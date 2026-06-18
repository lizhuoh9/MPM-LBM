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


def test_step12_required_artifacts_exist():
    required_paths = [
        "src/performance.py",
        "src/artifact_utils.py",
        "docs/10_performance_memory.md",
        "docs/11_artifact_policy.md",
        "configs/step12_profile_none.json",
        "configs/step12_profile_penalty.json",
        "configs/step12_profile_moving_boundary.json",
        "baseline_tests/run_step12_memory_estimate.py",
        "baseline_tests/run_step12_driver_profile_matrix.py",
        "baseline_tests/run_step12_artifact_manifest.py",
        "baseline_tests/run_step12_no_physics_regression.py",
        "logs/step12_memory_estimate.log",
        "logs/step12_profile_matrix.log",
        "logs/step12_artifact_manifest.log",
        "logs/step12_no_physics_regression.log",
        "outputs/step12_memory_estimate/memory_estimate.csv",
        "outputs/step12_memory_estimate/memory_estimate.npz",
        "outputs/step12_profile_matrix/profile_matrix.csv",
        "outputs/step12_profile_matrix/profile_matrix.npz",
        "outputs/step12_artifact_manifest/artifact_manifest.csv",
        "outputs/step12_artifact_manifest/artifact_summary.json",
        "outputs/step12_no_physics_regression/no_physics_regression.csv",
        "outputs/step12_no_physics_regression/no_physics_regression.npz",
        "STEP12_PERFORMANCE_MEMORY_REPORT.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step12_source_contract_keywords():
    source_paths = [
        "src/performance.py",
        "src/artifact_utils.py",
        "baseline_tests/run_step12_memory_estimate.py",
        "baseline_tests/run_step12_driver_profile_matrix.py",
        "baseline_tests/run_step12_artifact_manifest.py",
        "baseline_tests/run_step12_no_physics_regression.py",
    ]
    combined = "\n".join(read_text(path) for path in source_paths)

    required_keywords = [
        "estimate_lbm_memory_bytes",
        "estimate_mpm_memory_bytes",
        "estimate_total_memory_bytes",
        "scan_artifacts",
        "write_artifact_manifest",
        "summarize_artifacts",
        "FSIDriver3D",
        "coupling_mode",
    ]
    missing = [keyword for keyword in required_keywords if keyword not in combined]
    assert missing == []

    forbidden_tokens = ["two_phase", "contact_angle", "ReducedSquidFSI"]
    offenders = [token for token in forbidden_tokens if token in combined]
    assert offenders == []


def test_step12_logs_record_success_markers():
    expected_markers = {
        "logs/step12_memory_estimate.log": "[OK] Step 12 memory estimate finished",
        "logs/step12_profile_matrix.log": "[OK] Step 12 driver profile matrix finished",
        "logs/step12_artifact_manifest.log": "[OK] Step 12 artifact manifest finished",
        "logs/step12_no_physics_regression.log": "[OK] Step 12 no-physics regression finished",
    }

    missing = []
    for path, marker in expected_markers.items():
        text = read_text(path)
        if marker not in text:
            missing.append(f"{path}: {marker}")

    assert missing == []


def test_step12_memory_estimate_outputs_are_valid():
    rows = read_csv_rows("outputs/step12_memory_estimate/memory_estimate.csv")
    assert [int(row["n_grid"]) for row in rows] == [32, 64, 96, 128]

    totals = [float(row["total_estimated_mb"]) for row in rows]
    assert all(math.isfinite(value) for value in totals)
    assert all(value > 0.0 for value in totals)
    assert all(a < b for a, b in zip(totals, totals[1:]))
    assert totals[0] < 1024.0


def test_step12_profile_matrix_outputs_are_valid():
    rows = read_csv_rows("outputs/step12_profile_matrix/profile_matrix.csv")
    modes = {row["mode"] for row in rows}
    assert modes == {"none", "penalty", "moving_boundary"}

    for row in rows:
        assert float(row["total_time"]) > 0.0
        for field in (
            "init_time",
            "projection_time",
            "coupling_time",
            "lbm_step_time",
            "mpm_substep_time",
            "diagnostics_time",
            "export_time",
        ):
            value = float(row[field])
            assert math.isfinite(value)
            assert value >= 0.0
        assert int(row["steps"]) == 10
        assert int(row["substeps"]) == 100
        assert float(row["rho_min"]) > 0.95
        assert float(row["rho_max"]) < 1.05
        assert float(row["lbm_max_v"]) < 0.1
        assert float(row["mpm_min_J"]) > 0.0


def test_step12_artifact_summary_is_valid():
    summary_path = ROOT / "outputs/step12_artifact_manifest/artifact_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert int(summary["file_count"]) > 0
    assert int(summary["total_size_bytes"]) > 0
    assert float(summary["total_size_mb"]) > 0.0
    assert int(summary["large_file_count"]) >= 0
    assert isinstance(summary["by_extension"], dict)


def test_step12_no_physics_regression_outputs_are_valid():
    rows = read_csv_rows("outputs/step12_no_physics_regression/no_physics_regression.csv")
    by_mode = {row["mode"]: row for row in rows}
    assert set(by_mode) == {"none", "penalty", "moving_boundary"}

    none_ux = float(by_mode["none"]["projection_zone_ux_final"])
    penalty_ux = float(by_mode["penalty"]["projection_zone_ux_final"])
    moving_ux = float(by_mode["moving_boundary"]["projection_zone_ux_final"])
    assert moving_ux > penalty_ux > none_ux
    assert float(by_mode["penalty"]["cell_force_max_norm"]) > 0.0
    assert float(by_mode["moving_boundary"]["cell_force_max_norm"]) == 0.0
    assert int(float(by_mode["moving_boundary"]["bb_link_count"])) > 0

    for row in rows:
        assert float(row["rho_min"]) > 0.95
        assert float(row["rho_max"]) < 1.05
        assert float(row["lbm_max_v"]) < 0.1
        assert float(row["mpm_min_J"]) > 0.0


def test_step12_docs_and_gitignore_contract():
    readme = read_text("README.md")
    performance_doc = read_text("docs/10_performance_memory.md")
    artifact_doc = read_text("docs/11_artifact_policy.md")
    roadmap = read_text("docs/08_roadmap.md")
    gitignore = read_text(".gitignore")

    required_readme = ["docs/10_performance_memory.md", "docs/11_artifact_policy.md"]
    assert [token for token in required_readme if token not in readme] == []

    required_performance_doc = [
        "Step 12 estimates dense-grid memory and records timing baselines.",
        "Step 12 does not implement optimization or new solver physics.",
        "n_grid = 32",
        "n_particles = 4096",
        "128^3",
        "profile matrix",
    ]
    assert [token for token in required_performance_doc if token not in performance_doc] == []

    required_artifact_doc = [
        "outputs/tmp/",
        "outputs/scratch/",
        "logs/tmp/",
        "logs/scratch/",
        "outputs/experiments/",
        "logs/experiments/",
        "large-file threshold",
    ]
    assert [token for token in required_artifact_doc if token not in artifact_doc] == []

    assert "Step 12" in roadmap
    assert "completed" in roadmap
    assert "geometry ingestion / squid proxy geometry" in roadmap

    required_gitignore = [
        "outputs/tmp/",
        "outputs/scratch/",
        "logs/tmp/",
        "logs/scratch/",
        "outputs/experiments/",
        "logs/experiments/",
    ]
    assert [token for token in required_gitignore if token not in gitignore] == []
    assert "outputs/step*" not in gitignore
    assert "logs/step*" not in gitignore


def test_step12_report_acceptance_complete():
    report = read_text("STEP12_PERFORMANCE_MEMORY_REPORT.md")

    required_checks = [
        "- [x] main is on the Step 12 final commit",
        "- [x] src/performance.py exists",
        "- [x] src/artifact_utils.py exists",
        "- [x] docs/10_performance_memory.md exists",
        "- [x] docs/11_artifact_policy.md exists",
        "- [x] .gitignore exists and ignores tmp/scratch/experiments",
        "- [x] configs/step12_profile_none.json exists",
        "- [x] configs/step12_profile_penalty.json exists",
        "- [x] configs/step12_profile_moving_boundary.json exists",
        "- [x] baseline_tests/run_step12_memory_estimate.py exists",
        "- [x] baseline_tests/run_step12_driver_profile_matrix.py exists",
        "- [x] baseline_tests/run_step12_artifact_manifest.py exists",
        "- [x] baseline_tests/run_step12_no_physics_regression.py exists",
        "- [x] memory_estimate.csv exists",
        "- [x] memory_estimate.npz exists",
        "- [x] memory estimate values are finite",
        "- [x] memory estimate total increases monotonically with n_grid",
        "- [x] profile_matrix.csv exists",
        "- [x] profile_matrix.npz exists",
        "- [x] none / penalty / moving_boundary profiles complete",
        "- [x] artifact_manifest.csv exists",
        "- [x] artifact_summary.json exists",
        "- [x] no-physics regression passes",
        "- [x] Step 10 mode trend is preserved",
        "- [x] rho_min > 0.95",
        "- [x] rho_max < 1.05",
        "- [x] lbm_max_v < 0.1",
        "- [x] mpm_min_J > 0",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] no new FSI physics",
        "- [x] no two-phase flow",
        "- [x] no contact angle physics",
        "- [x] no ReducedSquidFSI",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] README links Step 12 docs",
        "- [x] docs/08_roadmap.md updated",
        "- [x] STEP12_PERFORMANCE_MEMORY_REPORT.md complete",
        "- [x] tests/test_step12_performance_memory_contract.py exists",
        "- [x] pytest -q passes",
        "- [x] logs/step12_pytest.log exists",
        "- [x] Step 12 artifacts are committed",
        "- [x] Step 12 artifacts are pushed to GitHub",
        "- [x] Yes",
    ]

    missing = [check for check in required_checks if check not in report]
    assert missing == []
