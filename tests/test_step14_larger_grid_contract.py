import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_csv_rows(relative_path):
    with (ROOT / relative_path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_json(relative_path):
    return json.loads(read_text(relative_path))


def as_float(row, key):
    return float(row[key])


def assert_finite_row(row, excluded=("mode", "geometry_type", "stable", "notes")):
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        numeric = float(value)
        assert math.isfinite(numeric), f"{key} is not finite"


def test_step14_required_artifacts_exist():
    required_paths = [
        "configs/step14_scale_48_none.json",
        "configs/step14_scale_48_penalty.json",
        "configs/step14_scale_48_moving_boundary.json",
        "configs/step14_scale_48_squid_proxy_none.json",
        "configs/step14_scale_48_squid_proxy_penalty.json",
        "configs/step14_scale_48_squid_proxy_moving_boundary.json",
        "configs/step14_feasibility_64_none.json",
        "configs/step14_feasibility_64_penalty.json",
        "baseline_tests/run_step14_scale_box_48.py",
        "baseline_tests/run_step14_scale_squid_proxy_48.py",
        "baseline_tests/run_step14_feasibility_64.py",
        "baseline_tests/run_step14_scaling_summary.py",
        "baseline_tests/run_step14_artifact_manifest.py",
        "logs/step14_scale_box_48.log",
        "logs/step14_scale_squid_proxy_48.log",
        "logs/step14_feasibility_64.log",
        "logs/step14_scaling_summary.log",
        "logs/step14_artifact_manifest.log",
        "logs/step14_pytest.log",
        "outputs/step14_scale_box_48/box_48_results.csv",
        "outputs/step14_scale_squid_proxy_48/squid_proxy_48_results.csv",
        "outputs/step14_feasibility_64/feasibility_64_results.csv",
        "outputs/step14_scaling_summary/scaling_summary.csv",
        "outputs/step14_scaling_summary/scaling_summary.json",
        "outputs/step14_artifact_manifest/artifact_summary.json",
        "docs/13_larger_grid_validation.md",
        "STEP14_LARGER_GRID_VALIDATION_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step14_configs_keep_scale_outputs_lightweight():
    config_paths = [
        "configs/step14_scale_48_none.json",
        "configs/step14_scale_48_penalty.json",
        "configs/step14_scale_48_moving_boundary.json",
        "configs/step14_scale_48_squid_proxy_none.json",
        "configs/step14_scale_48_squid_proxy_penalty.json",
        "configs/step14_scale_48_squid_proxy_moving_boundary.json",
        "configs/step14_feasibility_64_none.json",
        "configs/step14_feasibility_64_penalty.json",
    ]

    for path in config_paths:
        config = read_json(path)
        assert config["write_vtk"] is False
        assert config["write_particles"] is False

        if "feasibility_64" in path:
            assert int(config["n_grid"]) == 64
            assert int(config["n_particles"]) == 32768
        else:
            assert int(config["n_grid"]) == 48

        if "squid_proxy" in path:
            assert config["geometry_type"] == "squid_proxy"
            assert int(config["n_particles"]) == 4096
        elif "scale_48" in path:
            assert config["geometry_type"] == "box"
            assert int(config["n_particles"]) == 13824


def test_step14_logs_record_success_markers():
    expected_markers = {
        "logs/step14_scale_box_48.log": "[OK] Step 14 48^3 box scale validation finished",
        "logs/step14_scale_squid_proxy_48.log": "[OK] Step 14 48^3 squid proxy scale validation finished",
        "logs/step14_feasibility_64.log": "[OK] Step 14 64^3 feasibility finished",
        "logs/step14_scaling_summary.log": "[OK] Step 14 scaling summary finished",
        "logs/step14_artifact_manifest.log": "[OK] Step 14 artifact manifest finished",
    }

    missing = []
    for path, marker in expected_markers.items():
        if not (ROOT / path).is_file() or marker not in read_text(path):
            missing.append(f"{path}: {marker}")

    assert missing == []


def test_step14_box_48_results_are_valid():
    rows = read_csv_rows("outputs/step14_scale_box_48/box_48_results.csv")
    by_mode = {row["mode"]: row for row in rows}
    assert set(by_mode) == {"none", "penalty", "moving_boundary"}

    for row in rows:
        assert_finite_row(row)
        assert row["stable"] == "True"
        assert int(float(row["n_grid"])) == 48
        assert int(float(row["n_particles"])) == 13824
        assert as_float(row, "rho_min") > 0.95
        assert as_float(row, "rho_max") < 1.05
        assert as_float(row, "lbm_max_v") < 0.1
        assert as_float(row, "mpm_min_J") > 0.0
        assert as_float(row, "mpm_max_speed") < 10.0
        assert as_float(row, "total_time_sec") > 0.0

    assert as_float(by_mode["penalty"], "cell_force_max_norm") > 0.0
    assert as_float(by_mode["moving_boundary"], "cell_force_max_norm") == 0.0
    assert int(float(by_mode["moving_boundary"]["bb_link_count"])) > 0


def test_step14_squid_proxy_48_results_are_valid():
    rows = read_csv_rows("outputs/step14_scale_squid_proxy_48/squid_proxy_48_results.csv")
    by_mode = {row["mode"]: row for row in rows}
    assert set(by_mode) == {"none", "penalty", "moving_boundary"}

    for row in rows:
        assert_finite_row(row)
        assert row["stable"] == "True"
        assert int(float(row["n_grid"])) == 48
        assert int(float(row["n_particles"])) == 4096
        assert row["geometry_type"] == "squid_proxy"
        assert as_float(row, "rho_min") > 0.95
        assert as_float(row, "rho_max") < 1.05
        assert as_float(row, "lbm_max_v") < 0.1
        assert as_float(row, "mpm_min_J") > 0.0
        assert as_float(row, "mpm_max_speed") < 10.0
        assert int(float(row["active_cell_count"])) > 0
        assert as_float(row, "projected_mass") > 0.0
        assert as_float(row, "total_time_sec") > 0.0

    assert as_float(by_mode["penalty"], "cell_force_max_norm") > 0.0
    assert as_float(by_mode["moving_boundary"], "cell_force_max_norm") == 0.0
    assert int(float(by_mode["moving_boundary"]["bb_link_count"])) > 0


def test_step14_feasibility_64_results_are_valid():
    rows = read_csv_rows("outputs/step14_feasibility_64/feasibility_64_results.csv")
    by_mode = {row["mode"]: row for row in rows}
    assert set(by_mode) == {"none", "penalty"}

    for row in rows:
        assert_finite_row(row)
        assert row["stable"] == "True"
        assert int(float(row["n_grid"])) == 64
        assert int(float(row["n_particles"])) == 32768
        assert as_float(row, "rho_min") > 0.95
        assert as_float(row, "rho_max") < 1.05
        assert as_float(row, "lbm_max_v") < 0.1
        assert as_float(row, "mpm_min_J") > 0.0
        assert as_float(row, "mpm_max_speed") < 10.0
        assert as_float(row, "estimated_memory_mb") > 0.0
        assert as_float(row, "total_time_sec") > 0.0

    assert as_float(by_mode["penalty"], "cell_force_max_norm") > 0.0


def test_step14_scaling_summary_and_artifacts_are_valid():
    rows = read_csv_rows("outputs/step14_scaling_summary/scaling_summary.csv")
    grids = {int(float(row["n_grid"])) for row in rows}
    assert {32, 48, 64}.issubset(grids)

    stable_rows = [row for row in rows if row.get("stable") == "True"]
    assert stable_rows
    for row in stable_rows:
        assert_finite_row(row)
        assert as_float(row, "estimated_memory_mb") > 0.0

    summary = read_json("outputs/step14_scaling_summary/scaling_summary.json")
    assert int(summary["row_count"]) == len(rows)
    assert "engineering scale baseline" in summary["scope_note"]

    artifact_summary = read_json("outputs/step14_artifact_manifest/artifact_summary.json")
    assert int(artifact_summary["file_count"]) > 0
    assert int(artifact_summary["total_size_bytes"]) > 0
    assert float(artifact_summary["total_size_mb"]) > 0.0
    assert int(artifact_summary["large_file_count"]) >= 0


def test_step14_docs_avoid_overclaims_and_document_scope():
    doc_paths = [
        "README.md",
        "docs/08_roadmap.md",
        "docs/10_performance_memory.md",
        "docs/12_geometry_ingestion.md",
        "docs/13_larger_grid_validation.md",
        "STEP14_LARGER_GRID_VALIDATION_REPORT.md",
    ]
    combined_docs = "\n".join(read_text(path) for path in doc_paths if (ROOT / path).is_file())

    required_scope = [
        "Step 14 does not add new FSI physics",
        "48^3",
        "64^3",
        "engineering scale baseline",
        "not production benchmark",
        "not real squid validation",
    ]
    missing = [token for token in required_scope if token not in combined_docs]
    assert missing == []

    forbidden_overclaims = [
        "real squid simulation is validated",
        "validated squid swimming",
        "biomechanically accurate squid",
        "anatomically accurate squid",
        "production-grade large-scale solver",
        "strict momentum-conserving FSI is complete",
    ]
    offenders = [claim for claim in forbidden_overclaims if claim in combined_docs]
    assert offenders == []

    forbidden_claims = ["implements two_phase", "implements contact_angle", "implements ReducedSquidFSI"]
    offenders = [claim for claim in forbidden_claims if claim in combined_docs]
    assert offenders == []


def test_step14_report_acceptance_complete():
    report = read_text("STEP14_LARGER_GRID_VALIDATION_REPORT.md")

    required_checks = [
        "- [x] main is on the Step 14 final commit",
        "- [x] configs/step14_scale_48_none.json exists",
        "- [x] configs/step14_scale_48_penalty.json exists",
        "- [x] configs/step14_scale_48_moving_boundary.json exists",
        "- [x] configs/step14_scale_48_squid_proxy_none.json exists",
        "- [x] configs/step14_scale_48_squid_proxy_penalty.json exists",
        "- [x] configs/step14_scale_48_squid_proxy_moving_boundary.json exists",
        "- [x] configs/step14_feasibility_64_none.json exists",
        "- [x] configs/step14_feasibility_64_penalty.json exists",
        "- [x] 48^3 box none baseline passes",
        "- [x] 48^3 box penalty baseline passes",
        "- [x] 48^3 box moving_boundary baseline passes",
        "- [x] 48^3 squid_proxy none baseline passes",
        "- [x] 48^3 squid_proxy penalty baseline passes",
        "- [x] 48^3 squid_proxy moving_boundary baseline passes",
        "- [x] 64^3 none feasibility baseline passes",
        "- [x] 64^3 penalty feasibility baseline passes",
        "- [x] rho_min > 0.95 for all stable rows",
        "- [x] rho_max < 1.05 for all stable rows",
        "- [x] lbm_max_v < 0.1 for all stable rows",
        "- [x] mpm_min_J > 0 for all stable rows",
        "- [x] mpm_max_speed < 10 for all stable rows",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] scaling_summary.csv exists",
        "- [x] scaling_summary.json exists",
        "- [x] artifact manifest exists",
        "- [x] write_vtk is false in required scale configs",
        "- [x] write_particles is false in required scale configs",
        "- [x] no new FSI physics",
        "- [x] no two-phase flow",
        "- [x] no contact angle physics",
        "- [x] no real squid validation claims",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] docs/13_larger_grid_validation.md exists",
        "- [x] README.md documents larger-grid validation conservatively",
        "- [x] STEP14_LARGER_GRID_VALIDATION_REPORT.md complete",
        "- [x] tests/test_step14_larger_grid_contract.py exists",
        "- [x] pytest -q passes",
        "- [x] logs/step14_pytest.log exists",
        "- [x] git diff --check passes",
        "- [x] Step 14 artifacts are committed",
        "- [x] Step 14 artifacts are pushed to GitHub",
        "- [x] Yes",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
