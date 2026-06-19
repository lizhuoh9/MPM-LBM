import csv
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


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


def assert_stable_summary(summary, expected_steps, expected_substeps, require_moving_boundary=True):
    assert int(summary["completed_lbm_steps"]) >= expected_steps
    assert int(summary["total_mpm_substeps"]) >= expected_substeps
    assert float(summary["rho_min_global"]) > 0.95
    assert float(summary["rho_max_global"]) < 1.05
    assert float(summary["rho_span_global"]) < 0.10
    assert float(summary["lbm_max_v_global"]) < 0.1
    assert float(summary["mpm_min_J_global"]) > 0.0
    assert float(summary["mpm_max_speed_global"]) < 10.0
    assert as_bool(summary["stable"])
    assert as_bool(summary["well_behaved"])
    assert float(summary["elapsed_seconds"]) > 0.0
    if require_moving_boundary:
        assert int(summary["bb_link_count_min"]) > 0
        assert int(summary["bb_link_count_max"]) >= int(summary["bb_link_count_min"])
        assert int(summary["active_reaction_particle_count_min"]) > 0
        assert int(summary["active_reaction_particle_count_max"]) >= int(
            summary["active_reaction_particle_count_min"]
        )
        assert float(summary["cell_force_max_norm"]) == 0.0
        assert float(summary["hydro_force_max_norm"]) > 0.0


def test_step16_required_artifacts_exist():
    required_paths = [
        "configs/step16_long_box_48_moving_boundary.json",
        "configs/step16_long_squid_proxy_48_moving_boundary.json",
        "configs/step16_feasibility_64_moving_boundary_box.json",
        "configs/step16_compare_64_modes.json",
        "baseline_tests/step16_common.py",
        "baseline_tests/run_step16_long_box_48_moving_boundary.py",
        "baseline_tests/run_step16_long_squid_proxy_48_moving_boundary.py",
        "baseline_tests/run_step16_feasibility_64_moving_boundary.py",
        "baseline_tests/run_step16_64_mode_comparison.py",
        "baseline_tests/run_step16_long_run_summary.py",
        "baseline_tests/run_step16_artifact_manifest.py",
        "logs/step16_long_box_48_moving_boundary.log",
        "logs/step16_long_squid_proxy_48_moving_boundary.log",
        "logs/step16_feasibility_64_moving_boundary.log",
        "logs/step16_64_mode_comparison.log",
        "logs/step16_long_run_summary.log",
        "logs/step16_artifact_manifest.log",
        "logs/step16_pytest.log",
        "outputs/step16_long_box_48_moving_boundary/diagnostics_timeseries.csv",
        "outputs/step16_long_box_48_moving_boundary/diagnostics_timeseries.npz",
        "outputs/step16_long_box_48_moving_boundary/long_run_summary.json",
        "outputs/step16_long_squid_proxy_48_moving_boundary/diagnostics_timeseries.csv",
        "outputs/step16_long_squid_proxy_48_moving_boundary/diagnostics_timeseries.npz",
        "outputs/step16_long_squid_proxy_48_moving_boundary/long_run_summary.json",
        "outputs/step16_feasibility_64_moving_boundary/box_64_moving_boundary_results.csv",
        "outputs/step16_feasibility_64_moving_boundary/box_64_moving_boundary_results.npz",
        "outputs/step16_feasibility_64_moving_boundary/diagnostics_timeseries.csv",
        "outputs/step16_feasibility_64_moving_boundary/diagnostics_timeseries.npz",
        "outputs/step16_feasibility_64_moving_boundary/long_run_summary.json",
        "outputs/step16_64_mode_comparison/mode_64_results.csv",
        "outputs/step16_64_mode_comparison/mode_64_results.npz",
        "outputs/step16_long_run_summary/step16_summary.csv",
        "outputs/step16_long_run_summary/step16_summary.json",
        "outputs/step16_artifact_manifest/artifact_manifest.csv",
        "outputs/step16_artifact_manifest/artifact_summary.json",
        "docs/15_long_run_validation.md",
        "STEP16_LONG_RUN_VALIDATION_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step16_source_keywords_exist():
    source_paths = [
        "baseline_tests/step16_common.py",
        "baseline_tests/run_step16_long_box_48_moving_boundary.py",
        "baseline_tests/run_step16_long_squid_proxy_48_moving_boundary.py",
        "baseline_tests/run_step16_feasibility_64_moving_boundary.py",
        "baseline_tests/run_step16_64_mode_comparison.py",
        "baseline_tests/run_step16_long_run_summary.py",
    ]
    source = "\n".join(read_text(path) for path in source_paths)

    required_keywords = [
        "summarize_driver_timeseries",
        "assert_long_run_stable",
        "run_driver_case",
        "write_summary_csv",
        "load_final_row",
        "completed_lbm_steps",
        "rho_min_global",
        "bb_link_count_min",
        "active_reaction_particle_count_min",
        "cell_force_max_norm",
        "moving_boundary",
        "penalty",
        "none",
        "64^3 moving_boundary feasibility",
    ]
    missing = [keyword for keyword in required_keywords if keyword not in source]
    assert missing == []


def test_step16_configs_match_contract_and_disable_heavy_exports():
    box = read_json("configs/step16_long_box_48_moving_boundary.json")
    squid = read_json("configs/step16_long_squid_proxy_48_moving_boundary.json")
    moving64 = read_json("configs/step16_feasibility_64_moving_boundary_box.json")
    matrix = read_json("configs/step16_compare_64_modes.json")

    assert box["coupling_mode"] == "moving_boundary"
    assert box["geometry_type"] == "box"
    assert int(box["n_grid"]) == 48
    assert int(box["n_particles"]) == 13824
    assert int(box["n_lbm_steps"]) >= 50
    assert int(box["mpm_substeps_per_lbm_step"]) == 10
    assert box["target_u_lbm"] == [0.005, 0.0, 0.0]
    assert float(box["mb_reaction_scale"]) == 1.0
    assert math.isclose(float(box["mb_force_cap_norm"]), 1.0e-5)

    assert squid["coupling_mode"] == "moving_boundary"
    assert squid["geometry_type"] == "squid_proxy"
    assert squid["geometry_config_path"] == "configs/step13_squid_proxy_geometry.json"
    assert int(squid["n_grid"]) == 48
    assert int(squid["n_particles"]) == 4096
    assert int(squid["n_lbm_steps"]) >= 30
    assert int(squid["mpm_substeps_per_lbm_step"]) == 10
    assert squid["target_u_lbm"] == [0.005, 0.0, 0.0]
    assert float(squid["mb_reaction_scale"]) == 0.5
    assert math.isclose(float(squid["mb_force_cap_norm"]), 2.5e-5)

    assert moving64["coupling_mode"] == "moving_boundary"
    assert moving64["geometry_type"] == "box"
    assert int(moving64["n_grid"]) == 64
    assert int(moving64["n_particles"]) == 32768
    assert int(moving64["n_lbm_steps"]) >= 5
    assert int(moving64["mpm_substeps_per_lbm_step"]) == 5
    assert moving64["target_u_lbm"] == [0.0025, 0.0, 0.0]
    assert float(moving64["mb_reaction_scale"]) == 1.0
    assert math.isclose(float(moving64["mb_force_cap_norm"]), 5.0e-6)

    assert matrix["modes"] == ["none", "penalty", "moving_boundary"]
    assert int(matrix["n_grid"]) == 64
    assert int(matrix["n_particles"]) == 32768
    assert int(matrix["n_lbm_steps"]) >= 5
    assert int(matrix["mpm_substeps_per_lbm_step"]) == 5

    for config in [box, squid, moving64]:
        assert config["write_vtk"] is False
        assert config["write_particles"] is False
    assert matrix["write_vtk"] is False
    assert matrix["write_particles"] is False


def test_step16_logs_record_success_markers():
    expected_markers = {
        "logs/step16_long_box_48_moving_boundary.log": (
            "[OK] Step 16 48^3 box moving_boundary long-run finished"
        ),
        "logs/step16_long_squid_proxy_48_moving_boundary.log": (
            "[OK] Step 16 48^3 squid_proxy moving_boundary long-run finished"
        ),
        "logs/step16_feasibility_64_moving_boundary.log": (
            "[OK] Step 16 64^3 moving_boundary feasibility finished"
        ),
        "logs/step16_64_mode_comparison.log": "[OK] Step 16 64^3 mode comparison finished",
        "logs/step16_long_run_summary.log": "[OK] Step 16 long-run summary finished",
        "logs/step16_artifact_manifest.log": "[OK] Step 16 artifact manifest finished",
    }

    missing = []
    for path, marker in expected_markers.items():
        if not (ROOT / path).is_file() or marker not in read_text(path):
            missing.append(f"{path}: {marker}")

    assert missing == []


def test_step16_long_run_summaries_are_valid():
    box = read_json("outputs/step16_long_box_48_moving_boundary/long_run_summary.json")
    squid = read_json("outputs/step16_long_squid_proxy_48_moving_boundary/long_run_summary.json")
    moving64 = read_json("outputs/step16_feasibility_64_moving_boundary/long_run_summary.json")

    assert box["case"] == "long_box_48_moving_boundary"
    assert box["mode"] == "moving_boundary"
    assert box["geometry_type"] == "box"
    assert int(box["n_grid"]) == 48
    assert int(box["n_particles"]) == 13824
    assert_stable_summary(box, expected_steps=50, expected_substeps=500)

    assert squid["case"] == "long_squid_proxy_48_moving_boundary"
    assert squid["mode"] == "moving_boundary"
    assert squid["geometry_type"] == "squid_proxy"
    assert int(squid["n_grid"]) == 48
    assert int(squid["n_particles"]) == 4096
    assert_stable_summary(squid, expected_steps=30, expected_substeps=300)

    assert moving64["case"] == "feasibility_64_moving_boundary"
    assert moving64["mode"] == "moving_boundary"
    assert moving64["geometry_type"] == "box"
    assert int(moving64["n_grid"]) == 64
    assert int(moving64["n_particles"]) == 32768
    assert_stable_summary(moving64, expected_steps=5, expected_substeps=25)


def test_step16_64_outputs_and_mode_matrix_are_valid():
    moving_rows = read_csv_rows("outputs/step16_feasibility_64_moving_boundary/box_64_moving_boundary_results.csv")
    assert len(moving_rows) == 1
    moving = moving_rows[0]
    assert_finite_row(moving, excluded=("case", "mode", "geometry_type", "stable", "well_behaved", "notes"))
    assert moving["mode"] == "moving_boundary"
    assert int(float(moving["n_grid"])) == 64
    assert int(float(moving["n_particles"])) == 32768
    assert as_bool(moving["stable"])
    assert as_bool(moving["well_behaved"])
    assert as_float(moving, "rho_min_global") > 0.95
    assert as_float(moving, "rho_max_global") < 1.05
    assert as_float(moving, "lbm_max_v_global") < 0.1
    assert as_float(moving, "mpm_min_J_global") > 0.0
    assert as_float(moving, "mpm_max_speed_global") < 10.0
    assert as_float(moving, "cell_force_max_norm") == 0.0
    assert int(float(moving["bb_link_count_min"])) > 0

    payload = np.load(ROOT / "outputs/step16_feasibility_64_moving_boundary/box_64_moving_boundary_results.npz")
    assert "columns" in payload.files
    assert "rho_min_global" in payload.files

    rows = read_csv_rows("outputs/step16_64_mode_comparison/mode_64_results.csv")
    by_mode = {row["mode"]: row for row in rows}
    assert set(by_mode) == {"none", "penalty", "moving_boundary"}

    for row in rows:
        assert_finite_row(row, excluded=("case", "mode", "geometry_type", "stable", "well_behaved", "notes"))
        assert int(float(row["n_grid"])) == 64
        assert int(float(row["n_particles"])) == 32768
        assert as_bool(row["stable"])
        assert as_float(row, "rho_min_global") > 0.95
        assert as_float(row, "rho_max_global") < 1.05
        assert as_float(row, "lbm_max_v_global") < 0.1
        assert as_float(row, "mpm_min_J_global") > 0.0
        assert as_float(row, "mpm_max_speed_global") < 10.0

    assert as_float(by_mode["none"], "cell_force_max_norm") == 0.0
    assert int(float(by_mode["none"]["bb_link_count_min"])) == 0
    assert as_float(by_mode["penalty"], "cell_force_max_norm") > 0.0
    assert int(float(by_mode["penalty"]["bb_link_count_min"])) == 0
    assert as_float(by_mode["moving_boundary"], "cell_force_max_norm") == 0.0
    assert int(float(by_mode["moving_boundary"]["bb_link_count_min"])) > 0

    payload = np.load(ROOT / "outputs/step16_64_mode_comparison/mode_64_results.npz")
    assert "columns" in payload.files
    assert "modes" in payload.files


def test_step16_summary_and_artifacts_are_valid():
    rows = read_csv_rows("outputs/step16_long_run_summary/step16_summary.csv")
    cases = {row["case"] for row in rows}
    required_cases = {
        "long_box_48_moving_boundary",
        "long_squid_proxy_48_moving_boundary",
        "feasibility_64_moving_boundary",
        "mode_compare_64_none",
        "mode_compare_64_penalty",
        "mode_compare_64_moving_boundary",
    }
    assert required_cases.issubset(cases)

    for row in rows:
        assert_finite_row(row, excluded=("case", "mode", "geometry_type", "stable", "well_behaved", "notes"))
        assert as_bool(row["stable"])

    summary = read_json("outputs/step16_long_run_summary/step16_summary.json")
    assert int(summary["row_count"]) == len(rows)
    assert "long-run validation" in summary["scope_note"]
    assert "64^3 moving_boundary feasibility" in summary["scope_note"]

    artifact_summary = read_json("outputs/step16_artifact_manifest/artifact_summary.json")
    assert int(artifact_summary["file_count"]) > 0
    assert int(artifact_summary["total_size_bytes"]) > 0
    assert float(artifact_summary["total_size_mb"]) > 0.0
    assert int(artifact_summary["large_file_count"]) >= 0


def test_step16_docs_avoid_overclaims_and_document_scope():
    doc_paths = [
        "README.md",
        "docs/08_roadmap.md",
        "docs/10_performance_memory.md",
        "docs/13_larger_grid_validation.md",
        "docs/14_moving_boundary_calibration.md",
        "docs/15_long_run_validation.md",
        "STEP16_LONG_RUN_VALIDATION_REPORT.md",
    ]
    combined_docs = "\n".join(read_text(path) for path in doc_paths if (ROOT / path).is_file())

    required_scope = [
        "Step 16 does not add new FSI physics",
        "The 64^3 moving_boundary row is a feasibility baseline.",
        "squid_proxy is procedural and not real squid validation.",
        "Strict link-area momentum-conserving coupling remains future work.",
        "48^3",
        "64^3",
        "long-run validation",
    ]
    missing = [token for token in required_scope if token not in combined_docs]
    assert missing == []

    forbidden_claims = [
        "real squid simulation is validated",
        "validated squid swimming",
        "biomechanically accurate squid",
        "anatomically accurate squid",
        "production-ready solver",
        "strict momentum-conserving FSI is complete",
        "implements two_phase",
        "implements contact_angle",
        "implements ReducedSquidFSI",
    ]
    offenders = [claim for claim in forbidden_claims if claim in combined_docs]
    assert offenders == []


def test_step16_report_acceptance_complete():
    report = read_text("STEP16_LONG_RUN_VALIDATION_REPORT.md")

    required_checks = [
        "- [x] main is on the Step 16 final commit",
        "- [x] configs/step16_long_box_48_moving_boundary.json exists",
        "- [x] configs/step16_long_squid_proxy_48_moving_boundary.json exists",
        "- [x] configs/step16_feasibility_64_moving_boundary_box.json exists",
        "- [x] configs/step16_compare_64_modes.json exists",
        "- [x] baseline_tests/step16_common.py exists",
        "- [x] 48^3 box moving_boundary long-run passes",
        "- [x] 48^3 squid_proxy moving_boundary long-run passes",
        "- [x] 64^3 moving_boundary feasibility passes",
        "- [x] 64^3 mode comparison passes",
        "- [x] step16_summary.csv exists",
        "- [x] step16_summary.json exists",
        "- [x] artifact manifest exists",
        "- [x] rho_min_global > 0.95 for all stable rows",
        "- [x] rho_max_global < 1.05 for all stable rows",
        "- [x] lbm_max_v_global < 0.1 for all stable rows",
        "- [x] mpm_min_J_global > 0 for all stable rows",
        "- [x] mpm_max_speed_global < 10 for all stable rows",
        "- [x] moving_boundary rows have bb_link_count_min > 0",
        "- [x] moving_boundary rows keep cell_force_max_norm == 0",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] write_vtk is false in required Step 16 configs",
        "- [x] write_particles is false in required Step 16 configs",
        "- [x] no new FSI physics",
        "- [x] no two-phase flow",
        "- [x] no contact angle physics",
        "- [x] no real squid validation claims",
        "- [x] no sparse storage implementation",
        "- [x] no ReducedSquidFSI",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] docs/15_long_run_validation.md exists",
        "- [x] README.md updated conservatively",
        "- [x] docs/08_roadmap.md updated",
        "- [x] docs/10_performance_memory.md updated",
        "- [x] docs/13_larger_grid_validation.md updated",
        "- [x] docs/14_moving_boundary_calibration.md updated",
        "- [x] STEP16_LONG_RUN_VALIDATION_REPORT.md complete",
        "- [x] tests/test_step16_long_run_validation_contract.py exists",
        "- [x] pytest -q passes",
        "- [x] logs/step16_pytest.log exists",
        "- [x] git diff --check passes",
        "- [x] Step 16 artifacts are committed",
        "- [x] Step 16 artifacts are pushed to GitHub",
        "- [x] Yes",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
