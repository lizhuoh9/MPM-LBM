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


def assert_stable_bounds(row, rho_prefix=""):
    rho_min_key = f"{rho_prefix}rho_min" if rho_prefix else "rho_min"
    rho_max_key = f"{rho_prefix}rho_max" if rho_prefix else "rho_max"
    lbm_key = "lbm_max_v"
    assert as_float(row, rho_min_key) > 0.95
    assert as_float(row, rho_max_key) < 1.05
    assert as_float(row, lbm_key) < 0.1
    assert as_float(row, "mpm_min_J") > 0.0


def assert_area_scale_bounded(row, key="area_scale"):
    value = as_float(row, key)
    assert math.isfinite(value)
    assert 0.25 <= value <= 2.0


def test_step18_required_artifacts_exist():
    required_paths = [
        "STEP18_LINK_AREA_TRANSFER_GOAL.md",
        "src/mpm_lbm/sim/coupling/link_area.py",
        "configs/step18_link_area_transfer_sanity_32.json",
        "configs/step18_link_area_policy_sweep_box_32.json",
        "configs/step18_link_area_transfer_box_48.json",
        "configs/step18_link_area_transfer_squid_proxy_48.json",
        "configs/step18_compare_engineering_vs_link_area_box_48.json",
        "configs/step18_compare_engineering_vs_link_area_squid_proxy_48.json",
        "baseline_tests/step18_common.py",
        "baseline_tests/run_step18_link_area_transfer_sanity.py",
        "baseline_tests/run_step18_link_area_policy_sweep_box_32.py",
        "baseline_tests/run_step18_link_area_transfer_box_48.py",
        "baseline_tests/run_step18_link_area_transfer_squid_proxy_48.py",
        "baseline_tests/run_step18_compare_engineering_vs_link_area.py",
        "baseline_tests/run_step18_regression_existing_modes.py",
        "baseline_tests/run_step18_artifact_manifest.py",
        "logs/step18_link_area_transfer_sanity.log",
        "logs/step18_link_area_policy_sweep_box_32.log",
        "logs/step18_link_area_transfer_box_48.log",
        "logs/step18_link_area_transfer_squid_proxy_48.log",
        "logs/step18_compare_engineering_vs_link_area.log",
        "logs/step18_regression_existing_modes.log",
        "logs/step18_artifact_manifest.log",
        "logs/step18_pytest.log",
        "outputs/step18_link_area_transfer_sanity/sanity_results.csv",
        "outputs/step18_link_area_transfer_sanity/sanity_results.npz",
        "outputs/step18_link_area_policy_sweep_box_32/policy_sweep.csv",
        "outputs/step18_link_area_policy_sweep_box_32/policy_sweep.npz",
        "outputs/step18_link_area_transfer_box_48/box_48_link_area_results.csv",
        "outputs/step18_link_area_transfer_box_48/box_48_link_area_results.npz",
        "outputs/step18_link_area_transfer_box_48/diagnostics_timeseries.csv",
        "outputs/step18_link_area_transfer_squid_proxy_48/squid_proxy_48_link_area_results.csv",
        "outputs/step18_link_area_transfer_squid_proxy_48/squid_proxy_48_link_area_results.npz",
        "outputs/step18_link_area_transfer_squid_proxy_48/diagnostics_timeseries.csv",
        "outputs/step18_compare_engineering_vs_link_area/comparison.csv",
        "outputs/step18_compare_engineering_vs_link_area/comparison.npz",
        "outputs/step18_regression_existing_modes/regression_results.csv",
        "outputs/step18_regression_existing_modes/regression_results.npz",
        "outputs/step18_artifact_manifest/artifact_manifest.csv",
        "outputs/step18_artifact_manifest/artifact_summary.json",
        "docs/17_experimental_link_area_transfer.md",
        "STEP18_LINK_AREA_TRANSFER_REPORT.md",
    ]
    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step18_source_keywords_and_defaults_exist():
    source_paths = [
        "src/mpm_lbm/sim/drivers/fsi_config.py",
        "src/fsi_driver.py",
        "src/mpm_lbm/sim/coupling/link_area.py",
        "src/__init__.py",
    ]
    source = "\n".join(read_text(path) for path in source_paths if (ROOT / path).is_file())
    required_keywords = [
        "class LinkAreaMovingBoundaryCoupler3D",
        "reaction_transfer_mode",
        "engineering",
        "link_area_experimental",
        "area_scale",
        "link_area_policy",
        "link_area_scale_min",
        "link_area_scale_max",
        "add_link_area_reaction_to_mpm_grid",
        "update_area_scale_from_lbm",
        "solid.grid_f_ext",
    ]
    missing = [keyword for keyword in required_keywords if keyword not in source]
    assert missing == []

    config_source = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    assert 'reaction_transfer_mode: str = "engineering"' in config_source
    assert "reaction_transfer_mode == \"link_area_experimental\"" in config_source
    assert "coupling_mode != \"moving_boundary\"" in config_source


def test_step18_configs_match_contract_and_disable_heavy_exports():
    sanity = read_json("configs/step18_link_area_transfer_sanity_32.json")
    policy = read_json("configs/step18_link_area_policy_sweep_box_32.json")
    box48 = read_json("configs/step18_link_area_transfer_box_48.json")
    squid48 = read_json("configs/step18_link_area_transfer_squid_proxy_48.json")
    compare_box = read_json("configs/step18_compare_engineering_vs_link_area_box_48.json")
    compare_squid = read_json("configs/step18_compare_engineering_vs_link_area_squid_proxy_48.json")

    experimental = [sanity, policy, box48, squid48]
    for config in experimental:
        assert config["coupling_mode"] == "moving_boundary"
        assert config["reaction_transfer_mode"] == "link_area_experimental"
        assert float(config["link_area_scale_min"]) == 0.25
        assert float(config["link_area_scale_max"]) == 2.0
        assert config["write_vtk"] is False
        assert config["write_particles"] is False

    assert int(sanity["n_grid"]) == 32
    assert int(sanity["n_lbm_steps"]) == 5
    assert int(sanity["mpm_substeps_per_lbm_step"]) == 5

    assert int(policy["n_grid"]) == 32
    assert int(policy["n_lbm_steps"]) == 10
    assert int(policy["mpm_substeps_per_lbm_step"]) == 10

    assert int(box48["n_grid"]) == 48
    assert int(box48["n_particles"]) == 13824
    assert int(box48["n_lbm_steps"]) == 20
    assert box48["target_u_lbm"] == [0.005, 0.0, 0.0]

    assert squid48["geometry_type"] == "squid_proxy"
    assert squid48["geometry_config_path"] == "configs/step13_squid_proxy_geometry.json"
    assert int(squid48["n_grid"]) == 48
    assert int(squid48["n_particles"]) == 4096
    assert math.isclose(float(squid48["mb_reaction_scale"]), 0.5)

    for config in [compare_box, compare_squid]:
        assert config["coupling_mode"] == "moving_boundary"
        assert config["write_vtk"] is False
        assert config["write_particles"] is False


def test_step18_logs_record_success_markers():
    expected_markers = {
        "logs/step18_link_area_transfer_sanity.log": "[OK] Step 18 link-area transfer sanity finished",
        "logs/step18_link_area_policy_sweep_box_32.log": "[OK] Step 18 link-area policy sweep box 32 finished",
        "logs/step18_link_area_transfer_box_48.log": "[OK] Step 18 link-area transfer box 48 finished",
        "logs/step18_link_area_transfer_squid_proxy_48.log": "[OK] Step 18 link-area transfer squid proxy 48 finished",
        "logs/step18_compare_engineering_vs_link_area.log": "[OK] Step 18 engineering vs link-area comparison finished",
        "logs/step18_regression_existing_modes.log": "[OK] Step 18 existing mode regression finished",
        "logs/step18_artifact_manifest.log": "[OK] Step 18 artifact manifest finished",
    }
    missing = []
    for path, marker in expected_markers.items():
        if not (ROOT / path).is_file() or marker not in read_log(path):
            missing.append(f"{path}: {marker}")
    assert missing == []


def test_step18_sanity_baseline_is_valid():
    rows = read_csv_rows("outputs/step18_link_area_transfer_sanity/sanity_results.csv")
    assert len(rows) >= 1
    row = rows[-1]
    assert_finite_row(row, excluded=("area_policy", "stable"))
    assert as_bool(row["stable"])
    assert_area_scale_bounded(row)
    assert as_float(row, "raw_area_scale") > 0.0
    assert int(float(row["active_reaction_particle_count"])) > 0
    assert as_float(row, "max_grid_reaction_norm") > 0.0
    assert as_float(row, "cell_force_max_norm") == 0.0
    assert int(float(row["bb_link_count"])) > 0
    assert_stable_bounds(row)

    payload = np.load(ROOT / "outputs/step18_link_area_transfer_sanity/sanity_results.npz")
    assert "area_scale" in payload.files
    assert "active_reaction_particle_count" in payload.files


def test_step18_policy_sweep_is_valid():
    rows = read_csv_rows("outputs/step18_link_area_policy_sweep_box_32/policy_sweep.csv")
    by_policy = {row["policy"]: row for row in rows}
    assert set(by_policy) == {"uniform", "inverse_length", "length"}
    assert as_bool(by_policy["inverse_length"]["stable"])

    for row in rows:
        assert_finite_row(row, excluded=("policy", "stable"))
        assert as_float(row, "cell_force_max_norm") == 0.0
        assert int(float(row["bb_link_count"])) > 0
        if as_bool(row["stable"]):
            assert_area_scale_bounded(row, key="area_scale_final")
            assert_stable_bounds(row)

    payload = np.load(ROOT / "outputs/step18_link_area_policy_sweep_box_32/policy_sweep.npz")
    assert "policies" in payload.files
    assert "area_scale_final" in payload.files


def test_step18_48_cube_and_squid_proxy_baselines_are_valid():
    checks = [
        ("outputs/step18_link_area_transfer_box_48/box_48_link_area_results.csv", "box_48"),
        (
            "outputs/step18_link_area_transfer_squid_proxy_48/squid_proxy_48_link_area_results.csv",
            "squid_proxy_48",
        ),
    ]
    for path, case in checks:
        rows = read_csv_rows(path)
        assert len(rows) == 1
        row = rows[0]
        assert row["case"] == case
        assert row["transfer_mode"] == "link_area_experimental"
        assert_finite_row(row, excluded=("case", "transfer_mode", "policy", "stable"))
        assert as_bool(row["stable"])
        assert_area_scale_bounded(row, key="area_scale_final")
        assert int(float(row["bb_link_count"])) > 0
        assert int(float(row["active_reaction_particle_count"])) > 0
        assert as_float(row, "cell_force_max_norm") == 0.0
        assert_stable_bounds(row, rho_prefix="global_")


def test_step18_engineering_vs_link_area_comparison_is_valid():
    rows = read_csv_rows("outputs/step18_compare_engineering_vs_link_area/comparison.csv")
    keys = {(row["case"], row["transfer_mode"]) for row in rows}
    expected = {
        ("box_48", "engineering"),
        ("box_48", "link_area_experimental"),
        ("squid_proxy_48", "engineering"),
        ("squid_proxy_48", "link_area_experimental"),
    }
    assert expected.issubset(keys)

    for row in rows:
        assert_finite_row(row, excluded=("case", "transfer_mode", "policy", "stable"))
        assert as_bool(row["stable"])
        assert as_float(row, "cell_force_max_norm") == 0.0
        assert int(float(row["bb_link_count"])) > 0
        assert_stable_bounds(row, rho_prefix="global_")
        if row["transfer_mode"] == "link_area_experimental":
            assert_area_scale_bounded(row, key="area_scale_final")

    payload = np.load(ROOT / "outputs/step18_compare_engineering_vs_link_area/comparison.npz")
    assert "transfer_modes" in payload.files
    assert "area_scale_final" in payload.files


def test_step18_existing_mode_regression_and_artifacts_are_valid():
    rows = read_csv_rows("outputs/step18_regression_existing_modes/regression_results.csv")
    cases = {row["case"] for row in rows}
    assert {"engineering_box_48_regression", "step17_accounting_regression"}.issubset(cases)
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

    artifact_summary = read_json("outputs/step18_artifact_manifest/artifact_summary.json")
    assert int(artifact_summary["file_count"]) > 0
    assert int(artifact_summary["total_size_bytes"]) > 0
    assert float(artifact_summary["total_size_mb"]) > 0.0
    assert int(artifact_summary["large_file_count"]) == 0


def test_step18_docs_avoid_overclaims_and_document_scope():
    doc_paths = [
        "README.md",
        "docs/08_roadmap.md",
        "docs/09_api_reference.md",
        "docs/16_link_area_momentum_accounting.md",
        "docs/17_experimental_link_area_transfer.md",
        "STEP18_LINK_AREA_TRANSFER_REPORT.md",
    ]
    combined_docs = "\n".join(read_text(path) for path in doc_paths if (ROOT / path).is_file())
    required_scope = [
        "Step 18 adds an opt-in experimental link-area reaction transfer mode.",
        "The default moving_boundary reaction transfer remains engineering.",
        "The moving bounce-back formula is unchanged.",
        "MovingBoundaryFSICoupler3D is unchanged.",
        "The experimental transfer uses a bounded global area_scale from Step 17 link-area proxy accounting.",
        "This is not final strict momentum-conserving sharp-interface FSI.",
        "squid_proxy is procedural and not real squid validation.",
    ]
    missing = [token for token in required_scope if token not in combined_docs]
    assert missing == []

    forbidden_claims = [
        "strict momentum-conserving FSI is complete",
        "real squid simulation is validated",
        "validated squid swimming",
        "production-ready sharp-interface FSI",
        "is final surface-area reconstruction",
        "implements final surface-area reconstruction",
    ]
    offenders = [claim for claim in forbidden_claims if claim in combined_docs]
    assert offenders == []


def test_step18_report_acceptance_complete():
    report = read_text("STEP18_LINK_AREA_TRANSFER_REPORT.md")
    required_checks = [
        "- [x] main is on the Step 18 final commit",
        "- [x] src/link_area_coupling.py exists",
        "- [x] LinkAreaMovingBoundaryCoupler3D exists",
        "- [x] FSIDriverConfig has reaction_transfer_mode",
        "- [x] FSIDriverConfig default reaction_transfer_mode == engineering",
        "- [x] link_area_experimental is opt-in only",
        "- [x] engineering moving_boundary path remains available",
        "- [x] moving bounce-back formula unchanged",
        "- [x] MovingBoundaryFSICoupler3D unchanged",
        "- [x] PenaltyFSICoupler3D unchanged",
        "- [x] LBMFluid3D.step() default behavior unchanged",
        "- [x] experimental transfer writes MPM reaction through solid.grid_f_ext",
        "- [x] experimental transfer does not use lbm.cell_force",
        "- [x] area_scale is finite and bounded",
        "- [x] sanity baseline passes",
        "- [x] area policy sweep passes",
        "- [x] 48^3 box experimental transfer passes",
        "- [x] 48^3 procedural squid_proxy experimental transfer passes",
        "- [x] engineering vs link-area comparison passes",
        "- [x] existing-mode regression passes",
        "- [x] rho_min > 0.95 for required stable rows",
        "- [x] rho_max < 1.05 for required stable rows",
        "- [x] lbm_max_v < 0.1 for required stable rows",
        "- [x] mpm_min_J > 0 for required stable rows",
        "- [x] cell_force_max_norm == 0 for moving_boundary rows",
        "- [x] active_reaction_particle_count > 0 for experimental rows",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] no two-phase flow",
        "- [x] no contact angle physics",
        "- [x] no real squid validation claims",
        "- [x] no squid swimming validation claims",
        "- [x] no mesh import",
        "- [x] no sparse storage implementation",
        "- [x] no ReducedSquidFSI",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] artifact large_file_count == 0",
        "- [x] docs/17_experimental_link_area_transfer.md exists",
        "- [x] STEP18_LINK_AREA_TRANSFER_REPORT.md complete",
        "- [x] tests/test_step18_link_area_transfer_contract.py exists",
        "- [x] logs/step18_pytest.log exists",
        "- [x] pytest -q passes",
        "- [x] git diff --check passes",
        "- [x] Step 18 artifacts are committed",
        "- [x] Step 18 artifacts are pushed to GitHub origin/main",
    ]
    missing = [check for check in required_checks if check not in report]
    assert missing == []
