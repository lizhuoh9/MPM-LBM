import csv
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_log(relative_path):
    raw = (ROOT / relative_path).read_bytes()
    for encoding in ("utf-8", "utf-16"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="ignore")


def read_csv_rows(relative_path):
    with (ROOT / relative_path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_json(relative_path):
    return json.loads(read_text(relative_path))


def as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def as_float(row, key):
    return float(row[key])


def assert_finite_row(row, excluded=()):
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        numeric = float(value)
        assert math.isfinite(numeric), f"{key} is not finite"


def assert_stable_bounds(row, prefix=""):
    rho_min = float(row[f"{prefix}rho_min"] if prefix else row.get("rho_min", row.get("rho_min_global")))
    rho_max = float(row[f"{prefix}rho_max"] if prefix else row.get("rho_max", row.get("rho_max_global")))
    lbm_max_v = float(row[f"{prefix}lbm_max_v"] if prefix else row.get("lbm_max_v", row.get("lbm_max_v_global")))
    assert rho_min > 0.95
    assert rho_max < 1.05
    assert lbm_max_v < 0.1


def test_step17_required_artifacts_exist():
    required_paths = [
        "STEP17_LINK_AREA_ACCOUNTING_GOAL.md",
        "src/link_area_accounting.py",
        "configs/step17_link_area_wall_32.json",
        "configs/step17_link_area_box_48.json",
        "configs/step17_link_area_squid_proxy_48.json",
        "configs/step17_link_area_box_64.json",
        "baseline_tests/run_step17_directional_link_sanity.py",
        "baseline_tests/run_step17_link_area_wall_couette.py",
        "baseline_tests/run_step17_box_48_link_budget.py",
        "baseline_tests/run_step17_squid_proxy_48_link_budget.py",
        "baseline_tests/run_step17_box_64_link_budget.py",
        "baseline_tests/run_step17_step16_regression.py",
        "baseline_tests/run_step17_artifact_manifest.py",
        "logs/step17_directional_link_sanity.log",
        "logs/step17_link_area_wall_couette.log",
        "logs/step17_box_48_link_budget.log",
        "logs/step17_squid_proxy_48_link_budget.log",
        "logs/step17_box_64_link_budget.log",
        "logs/step17_step16_regression.log",
        "logs/step17_artifact_manifest.log",
        "logs/step17_pytest.log",
        "outputs/step17_directional_link_sanity/directional_stats.csv",
        "outputs/step17_directional_link_sanity/directional_stats.npz",
        "outputs/step17_link_area_wall_couette/area_policy_comparison.csv",
        "outputs/step17_link_area_wall_couette/area_policy_comparison.npz",
        "outputs/step17_box_48_link_budget/link_budget_timeseries.csv",
        "outputs/step17_box_48_link_budget/link_budget_summary.json",
        "outputs/step17_box_48_link_budget/directional_stats_final.npz",
        "outputs/step17_squid_proxy_48_link_budget/link_budget_timeseries.csv",
        "outputs/step17_squid_proxy_48_link_budget/link_budget_summary.json",
        "outputs/step17_squid_proxy_48_link_budget/directional_stats_final.npz",
        "outputs/step17_box_64_link_budget/link_budget_summary.json",
        "outputs/step17_box_64_link_budget/directional_stats_final.npz",
        "outputs/step17_step16_regression/regression_results.csv",
        "outputs/step17_step16_regression/regression_results.npz",
        "outputs/step17_artifact_manifest/artifact_manifest.csv",
        "outputs/step17_artifact_manifest/artifact_summary.json",
        "docs/16_link_area_momentum_accounting.md",
        "STEP17_LINK_AREA_ACCOUNTING_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step17_source_keywords_exist():
    source_paths = [
        "src/lbm_fluid.py",
        "src/link_area_accounting.py",
        "src/__init__.py",
        "baseline_tests/run_step17_directional_link_sanity.py",
        "baseline_tests/run_step17_link_area_wall_couette.py",
        "baseline_tests/run_step17_box_48_link_budget.py",
        "baseline_tests/run_step17_squid_proxy_48_link_budget.py",
        "baseline_tests/run_step17_box_64_link_budget.py",
    ]
    source = "\n".join(read_text(path) for path in source_paths)

    required_keywords = [
        "bb_link_count_by_dir",
        "bb_fluid_impulse_by_dir",
        "bb_solid_force_by_dir",
        "bb_correction_abs_sum_by_dir",
        "bb_correction_abs_max_by_dir",
        "get_moving_boundary_directional_stats",
        "class LinkAreaMomentumAccounting3D",
        "direction_metadata",
        "area_weights",
        "area_weighted_impulse",
        "summarize_link_accounting",
        "uniform",
        "inverse_length",
        "length",
    ]
    missing = [keyword for keyword in required_keywords if keyword not in source]
    assert missing == []


def test_step17_configs_match_contract_and_disable_heavy_exports():
    wall = read_json("configs/step17_link_area_wall_32.json")
    box48 = read_json("configs/step17_link_area_box_48.json")
    squid48 = read_json("configs/step17_link_area_squid_proxy_48.json")
    box64 = read_json("configs/step17_link_area_box_64.json")

    assert wall["coupling_mode"] == "moving_boundary"
    assert wall["geometry_type"] == "box"
    assert int(wall["n_grid"]) == 32
    assert int(wall["n_particles"]) == 4096
    assert int(wall["n_lbm_steps"]) >= 100
    assert wall["target_u_lbm"] == [0.02, 0.0, 0.0]

    assert box48["coupling_mode"] == "moving_boundary"
    assert box48["geometry_type"] == "box"
    assert int(box48["n_grid"]) == 48
    assert int(box48["n_particles"]) == 13824
    assert int(box48["n_lbm_steps"]) >= 20
    assert int(box48["mpm_substeps_per_lbm_step"]) == 10
    assert box48["target_u_lbm"] == [0.005, 0.0, 0.0]
    assert math.isclose(float(box48["mb_force_cap_norm"]), 1.0e-5)

    assert squid48["coupling_mode"] == "moving_boundary"
    assert squid48["geometry_type"] == "squid_proxy"
    assert squid48["geometry_config_path"] == "configs/step13_squid_proxy_geometry.json"
    assert int(squid48["n_grid"]) == 48
    assert int(squid48["n_particles"]) == 4096
    assert int(squid48["n_lbm_steps"]) >= 20
    assert int(squid48["mpm_substeps_per_lbm_step"]) == 10
    assert squid48["target_u_lbm"] == [0.005, 0.0, 0.0]
    assert math.isclose(float(squid48["mb_reaction_scale"]), 0.5)
    assert math.isclose(float(squid48["mb_force_cap_norm"]), 2.5e-5)

    assert box64["coupling_mode"] == "moving_boundary"
    assert box64["geometry_type"] == "box"
    assert int(box64["n_grid"]) == 64
    assert int(box64["n_particles"]) == 32768
    assert int(box64["n_lbm_steps"]) >= 5
    assert int(box64["mpm_substeps_per_lbm_step"]) == 5
    assert box64["target_u_lbm"] == [0.0025, 0.0, 0.0]
    assert math.isclose(float(box64["mb_force_cap_norm"]), 5.0e-6)

    for config in [wall, box48, squid48, box64]:
        assert config["write_vtk"] is False
        assert config["write_particles"] is False


def test_step17_logs_record_success_markers():
    expected_markers = {
        "logs/step17_directional_link_sanity.log": "[OK] Step 17 directional link sanity finished",
        "logs/step17_link_area_wall_couette.log": "[OK] Step 17 link-area wall Couette finished",
        "logs/step17_box_48_link_budget.log": "[OK] Step 17 box 48 link budget finished",
        "logs/step17_squid_proxy_48_link_budget.log": "[OK] Step 17 squid proxy 48 link budget finished",
        "logs/step17_box_64_link_budget.log": "[OK] Step 17 box 64 link budget finished",
        "logs/step17_step16_regression.log": "[OK] Step 17 Step 16 regression finished",
        "logs/step17_artifact_manifest.log": "[OK] Step 17 artifact manifest finished",
    }

    missing = []
    for path, marker in expected_markers.items():
        if not (ROOT / path).is_file() or marker not in read_log(path):
            missing.append(f"{path}: {marker}")
    assert missing == []


def test_step17_directional_link_sanity_is_valid():
    rows = read_csv_rows("outputs/step17_directional_link_sanity/directional_stats.csv")
    assert len(rows) == 1
    row = rows[0]
    assert_finite_row(row, excluded=("case",))
    assert int(float(row["sum_link_count_by_dir"])) == int(float(row["bb_link_count"]))
    assert as_float(row, "link_count_sum_error") == 0.0
    assert as_float(row, "scalar_vs_directional_impulse_error_x") < 1.0e-4
    assert as_float(row, "scalar_vs_directional_solid_error_x") < 1.0e-4
    assert as_float(row, "bb_net_fluid_impulse_x") > 0.0
    assert as_float(row, "bb_net_solid_force_x") < 0.0
    assert as_float(row, "cell_force_max_norm") == 0.0
    assert_stable_bounds(row)

    payload = np.load(ROOT / "outputs/step17_directional_link_sanity/directional_stats.npz")
    assert "link_count_by_dir" in payload.files
    assert "fluid_impulse_by_dir" in payload.files
    assert "solid_force_by_dir" in payload.files


def test_step17_area_policy_comparison_is_valid():
    rows = read_csv_rows("outputs/step17_link_area_wall_couette/area_policy_comparison.csv")
    by_policy = {row["policy"]: row for row in rows}
    assert set(by_policy) == {"uniform", "inverse_length", "length"}

    for row in rows:
        assert_finite_row(row, excluded=("case", "policy"))
        assert int(float(row["total_link_count"])) > 0
        assert int(float(row["axis_link_count"])) > 0
        assert int(float(row["face_diagonal_link_count"])) > 0
        assert as_float(row, "area_proxy_total") > 0.0
        assert as_float(row, "bb_net_fluid_impulse_x") > 0.0
        assert as_float(row, "area_weighted_fluid_impulse_x") > 0.0
        assert as_float(row, "area_weighted_solid_force_x") < 0.0
        assert as_float(row, "cell_force_max_norm") == 0.0
        assert_stable_bounds(row)

    payload = np.load(ROOT / "outputs/step17_link_area_wall_couette/area_policy_comparison.npz")
    assert "policies" in payload.files
    assert "area_proxy_total" in payload.files


def assert_link_budget_summary(path, expected_grid, expected_steps, expected_substeps, geometry_type):
    summary = read_json(path)
    assert summary["geometry_type"] == geometry_type
    assert int(summary["n_grid"]) == expected_grid
    assert int(summary["completed_lbm_steps"]) >= expected_steps
    assert int(summary["total_mpm_substeps"]) >= expected_substeps
    assert as_bool(summary["stable"])
    assert float(summary["rho_min_global"]) > 0.95
    assert float(summary["rho_max_global"]) < 1.05
    assert float(summary["lbm_max_v_global"]) < 0.1
    assert float(summary["mpm_min_J_global"]) > 0.0
    assert int(summary["bb_link_count_min"]) > 0
    assert int(summary["axis_link_count"]) > 0
    assert int(summary["face_diagonal_link_count"]) > 0
    assert float(summary["area_proxy_total"]) > 0.0
    assert float(summary["cell_force_max_norm"]) == 0.0
    assert math.isfinite(float(summary["scalar_vs_directional_impulse_error_x"]))
    assert float(summary["scalar_vs_directional_impulse_error_x"]) < 1.0e-4
    assert math.isfinite(float(summary["hydro_vs_directional_solid_error_x"]))
    return summary


def test_step17_link_budget_summaries_are_valid():
    box48 = assert_link_budget_summary(
        "outputs/step17_box_48_link_budget/link_budget_summary.json",
        expected_grid=48,
        expected_steps=20,
        expected_substeps=200,
        geometry_type="box",
    )
    squid48 = assert_link_budget_summary(
        "outputs/step17_squid_proxy_48_link_budget/link_budget_summary.json",
        expected_grid=48,
        expected_steps=20,
        expected_substeps=200,
        geometry_type="squid_proxy",
    )
    box64 = assert_link_budget_summary(
        "outputs/step17_box_64_link_budget/link_budget_summary.json",
        expected_grid=64,
        expected_steps=5,
        expected_substeps=25,
        geometry_type="box",
    )
    assert box48["policy"] == "inverse_length"
    assert squid48["policy"] == "inverse_length"
    assert box64["policy"] == "inverse_length"

    for path in [
        "outputs/step17_box_48_link_budget/directional_stats_final.npz",
        "outputs/step17_squid_proxy_48_link_budget/directional_stats_final.npz",
        "outputs/step17_box_64_link_budget/directional_stats_final.npz",
    ]:
        payload = np.load(ROOT / path)
        assert "link_count_by_dir" in payload.files
        assert "fluid_impulse_by_dir" in payload.files
        assert "solid_force_by_dir" in payload.files


def test_step17_step16_regression_and_artifacts_are_valid():
    rows = read_csv_rows("outputs/step17_step16_regression/regression_results.csv")
    cases = {row["case"] for row in rows}
    assert {"step16_box_48_short", "step16_box_64_feasibility"}.issubset(cases)

    for row in rows:
        assert_finite_row(row, excluded=("case", "mode", "geometry_type", "stable", "notes"))
        assert as_bool(row["stable"])
        assert row["mode"] == "moving_boundary"
        assert as_float(row, "cell_force_max_norm") == 0.0
        assert int(float(row["bb_link_count_min"])) > 0
        assert as_float(row, "rho_min_global") > 0.95
        assert as_float(row, "rho_max_global") < 1.05
        assert as_float(row, "lbm_max_v_global") < 0.1
        assert as_float(row, "mpm_min_J_global") > 0.0

    payload = np.load(ROOT / "outputs/step17_step16_regression/regression_results.npz")
    assert "columns" in payload.files

    artifact_summary = read_json("outputs/step17_artifact_manifest/artifact_summary.json")
    assert int(artifact_summary["file_count"]) > 0
    assert int(artifact_summary["total_size_bytes"]) > 0
    assert float(artifact_summary["total_size_mb"]) > 0.0
    assert int(artifact_summary["large_file_count"]) == 0


def test_step17_docs_avoid_overclaims_and_document_scope():
    doc_paths = [
        "README.md",
        "docs/08_roadmap.md",
        "docs/09_api_reference.md",
        "docs/14_moving_boundary_calibration.md",
        "docs/15_long_run_validation.md",
        "docs/16_link_area_momentum_accounting.md",
        "STEP17_LINK_AREA_ACCOUNTING_REPORT.md",
    ]
    combined_docs = "\n".join(read_text(path) for path in doc_paths if (ROOT / path).is_file())

    required_scope = [
        "Step 17 adds diagnostic-only direction-wise and link-area proxy accounting.",
        "The moving bounce-back formula is unchanged.",
        "MovingBoundaryFSICoupler3D is unchanged.",
        "These are diagnostic proxy policies, not final surface-area reconstruction.",
        "Strict link-area momentum-conserving coupling remains future work.",
        "squid_proxy is procedural and not real squid validation.",
    ]
    missing = [token for token in required_scope if token not in combined_docs]
    assert missing == []

    forbidden_claims = [
        "strict momentum-conserving FSI is complete",
        "real squid simulation is validated",
        "validated squid swimming",
        "biomechanically accurate squid",
        "anatomically accurate squid",
        "production-ready solver",
        "implements two_phase",
        "implements contact_angle",
        "implements ReducedSquidFSI",
    ]
    offenders = [claim for claim in forbidden_claims if claim in combined_docs]
    assert offenders == []


def test_step17_report_acceptance_complete():
    report = read_text("STEP17_LINK_AREA_ACCOUNTING_REPORT.md")

    required_checks = [
        "- [x] main is on the Step 17 final commit",
        "- [x] LBMFluid3D has per-direction moving-boundary diagnostics",
        "- [x] get_moving_boundary_directional_stats() exists",
        "- [x] src/link_area_accounting.py exists",
        "- [x] LinkAreaMomentumAccounting3D exists",
        "- [x] configs/step17_link_area_wall_32.json exists",
        "- [x] configs/step17_link_area_box_48.json exists",
        "- [x] configs/step17_link_area_squid_proxy_48.json exists",
        "- [x] configs/step17_link_area_box_64.json exists",
        "- [x] directional sanity baseline passes",
        "- [x] sum(direction counts) == scalar bb_link_count",
        "- [x] sum(direction impulses) matches scalar impulse within tolerance",
        "- [x] area proxy policies uniform / inverse_length / length run",
        "- [x] 48^3 box link budget passes",
        "- [x] 48^3 squid_proxy link budget passes",
        "- [x] 64^3 box link budget passes",
        "- [x] Step 16 regression passes",
        "- [x] rho_min > 0.95",
        "- [x] rho_max < 1.05",
        "- [x] lbm_max_v < 0.1",
        "- [x] mpm_min_J > 0",
        "- [x] cell_force_max_norm == 0 for moving_boundary rows",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] no new bounce-back formula",
        "- [x] no new reaction transfer formula",
        "- [x] no new FSI mode",
        "- [x] no two-phase flow",
        "- [x] no contact angle physics",
        "- [x] no real squid validation claims",
        "- [x] no sparse storage implementation",
        "- [x] no ReducedSquidFSI",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] artifact large_file_count controlled",
        "- [x] docs/16_link_area_momentum_accounting.md exists",
        "- [x] STEP17_LINK_AREA_ACCOUNTING_REPORT.md complete",
        "- [x] tests/test_step17_link_area_accounting_contract.py exists",
        "- [x] pytest -q passes",
        "- [x] logs/step17_pytest.log exists",
        "- [x] git diff --check passes",
        "- [x] Step 17 artifacts are committed",
        "- [x] Step 17 artifacts are pushed to GitHub",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
