import csv
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_GEOMETRY_CONFIG_SPEC = importlib.util.spec_from_file_location(
    "step27_geometry_config",
    ROOT / "src" / "geometry_config.py",
)
_GEOMETRY_CONFIG_MODULE = importlib.util.module_from_spec(_GEOMETRY_CONFIG_SPEC)
sys.modules[_GEOMETRY_CONFIG_SPEC.name] = _GEOMETRY_CONFIG_MODULE
_GEOMETRY_CONFIG_SPEC.loader.exec_module(_GEOMETRY_CONFIG_MODULE)
GeometryConfig = _GEOMETRY_CONFIG_MODULE.GeometryConfig

STEP27_REQUIRED_FILES = [
    "STEP27_CONTROLLED_REAL_GEOMETRY_64_SHORT_DRIVER_GOAL.md",
    "STEP27_CONTROLLED_REAL_GEOMETRY_64_SHORT_DRIVER_REPORT.md",
    "docs/27_controlled_real_geometry_64_short_driver.md",
    "configs/step27_driver_real_candidate_smoke_mesh_64_penalty.json",
    "configs/step27_driver_real_candidate_smoke_mesh_64_moving_boundary.json",
    "configs/step27_driver_real_candidate_smoke_mesh_64_link_area.json",
    "configs/step27_driver_real_candidate_smoke_voxel_64_penalty.json",
    "configs/step27_driver_real_candidate_smoke_voxel_64_moving_boundary.json",
    "configs/step27_driver_real_candidate_smoke_voxel_64_link_area.json",
    "baseline_tests/step27_common.py",
    "baseline_tests/run_step27_candidate_fingerprint_guard.py",
    "baseline_tests/run_step27_64_driver_mesh_feasibility.py",
    "baseline_tests/run_step27_64_driver_voxel_feasibility.py",
    "baseline_tests/run_step27_driver_projection_alignment.py",
    "baseline_tests/run_step27_64_driver_summary.py",
    "baseline_tests/run_step27_quality_report_aggregation.py",
    "baseline_tests/run_step27_step26_regression_guard.py",
    "baseline_tests/run_step27_artifact_manifest.py",
    "tests/test_step27_controlled_real_geometry_64_short_driver_contract.py",
]

STEP27_OUTPUT_FILES = [
    "outputs/step27_candidate_fingerprint_guard/fingerprint_guard.csv",
    "outputs/step27_candidate_fingerprint_guard/fingerprint_guard.json",
    "outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.csv",
    "outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.npz",
    "outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.csv",
    "outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.npz",
    "outputs/step27_driver_projection_alignment/driver_projection_alignment.csv",
    "outputs/step27_driver_projection_alignment/driver_projection_alignment.json",
    "outputs/step27_64_driver_summary/driver_64_summary.csv",
    "outputs/step27_64_driver_summary/driver_64_summary.json",
    "outputs/step27_quality_report_aggregation/quality_report_summary.csv",
    "outputs/step27_quality_report_aggregation/quality_report_summary.json",
    "outputs/step27_step26_regression_guard/step26_regression_guard.csv",
    "outputs/step27_step26_regression_guard/step26_regression_guard.json",
    "outputs/step27_artifact_manifest/artifact_manifest.csv",
    "outputs/step27_artifact_manifest/artifact_summary.csv",
    "outputs/step27_artifact_manifest/artifact_summary.json",
]

STEP27_DRIVER_CONFIGS = [
    "configs/step27_driver_real_candidate_smoke_mesh_64_penalty.json",
    "configs/step27_driver_real_candidate_smoke_mesh_64_moving_boundary.json",
    "configs/step27_driver_real_candidate_smoke_mesh_64_link_area.json",
    "configs/step27_driver_real_candidate_smoke_voxel_64_penalty.json",
    "configs/step27_driver_real_candidate_smoke_voxel_64_moving_boundary.json",
    "configs/step27_driver_real_candidate_smoke_voxel_64_link_area.json",
]

STEP27_LOG_MARKERS = {
    "logs/step27_candidate_fingerprint_guard.log": "[OK] Step 27 candidate fingerprint guard finished",
    "logs/step27_64_driver_mesh_feasibility.log": "[OK] Step 27 mesh 64 short driver feasibility finished",
    "logs/step27_64_driver_voxel_feasibility.log": "[OK] Step 27 voxel 64 short driver feasibility finished",
    "logs/step27_driver_projection_alignment.log": "[OK] Step 27 driver projection alignment finished",
    "logs/step27_64_driver_summary.log": "[OK] Step 27 64 driver summary finished",
    "logs/step27_quality_report_aggregation.log": "[OK] Step 27 quality report aggregation finished",
    "logs/step27_step26_regression_guard.log": "[OK] Step 27 Step 26 regression guard finished",
    "logs/step27_artifact_manifest.log": "[OK] Step 27 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 27 is controlled real geometry 64^3 short driver feasibility.",
    "Step 27 is not real squid validation.",
    "Step 27 does not implement squid actuation.",
    "Step 27 does not implement squid swimming.",
    "Step 27 does not implement new FSI physics.",
    "Step 27 does not validate production sharp-interface FSI.",
    "The default quality_check_enabled remains false.",
    "The default quality_check_strict remains false.",
    "The default reaction_transfer_mode remains engineering.",
    "The moving bounce-back formula is unchanged.",
    "PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.",
]

FORBIDDEN_CLAIMS = [
    "real squid simulation is validated",
    "validated squid swimming",
    "squid actuation is implemented",
    "production-ready sharp-interface FSI",
    "final solver readiness",
    "production mesh repair is complete",
    "automatic remeshing is implemented",
    "strict momentum-conserving FSI is complete",
    "implements two_phase",
    "implements contact_angle",
]


def test_step27_required_artifacts_exist():
    missing = [path for path in STEP27_REQUIRED_FILES + STEP27_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_step27_driver_configs_are_valid():
    geometry_configs = [
        GeometryConfig.from_json(ROOT / "configs/step26_real_candidate_smoke_mesh_geometry.json"),
        GeometryConfig.from_json(ROOT / "configs/step26_real_candidate_smoke_voxel_geometry.json"),
    ]
    assert {config.geometry_type for config in geometry_configs} == {"mesh", "voxel"}
    for config in geometry_configs:
        assert int(config.n_particles) == 4096
        assert config.quality_check_enabled is True
        assert config.quality_check_strict is True
        assert (ROOT / config.geometry_file).is_file()

    for path in STEP27_DRIVER_CONFIGS:
        payload = read_json(path)
        assert payload["quality_check_enabled"] is True
        assert payload["quality_check_strict"] is True
        assert payload["write_vtk"] is False
        assert payload["write_particles"] is False
        assert int(payload["n_grid"]) == 64
        assert int(payload["n_particles"]) == 4096
        assert int(payload["n_lbm_steps"]) == 5
        assert int(payload["mpm_substeps_per_lbm_step"]) == 5
        assert payload["coupling_mode"] in {"penalty", "moving_boundary"}
        assert payload["geometry_config_path"].startswith("configs/step26_real_candidate_smoke_")
        if payload["coupling_mode"] == "penalty":
            assert payload["reaction_transfer_mode"] == "engineering"
        if payload["reaction_transfer_mode"] == "link_area_experimental":
            assert payload["coupling_mode"] == "moving_boundary"
            assert payload["link_area_policy"] == "inverse_length"
            assert float(payload["link_area_scale_min"]) == 0.25
            assert float(payload["link_area_scale_max"]) == 2.0


def test_step27_candidate_fingerprint_guard_is_valid():
    summary = read_json("outputs/step27_candidate_fingerprint_guard/fingerprint_guard.json")
    rows = read_csv_rows("outputs/step27_candidate_fingerprint_guard/fingerprint_guard.csv")
    assert int(summary["row_count"]) == 2
    assert int(summary["pass_count"]) == 2
    assert len(rows) == 2
    for row in rows:
        assert as_bool(row["guard_pass"])
        assert row["candidate_id"] in {"real_candidate_smoke_mesh", "real_candidate_smoke_voxel"}
        assert row["sha256_matches_step25"].lower() == "true"
        assert row["size_matches_step25"].lower() == "true"
        assert row["validation_scope"] == "intake_qa_normalization_sampling_projection_only"
        assert as_bool(row["quality_check_enabled"])
        assert as_bool(row["quality_check_strict"])
        assert as_bool(row["geometry_config_quality_check_enabled"])
        assert as_bool(row["geometry_config_quality_check_strict"])
        assert ":" not in row["source_file_redacted"]
        assert "\\Users\\" not in row["source_file_redacted"]


def test_step27_mesh_64_driver_outputs_are_valid():
    rows = read_csv_rows("outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.csv")
    assert len(rows) == 3
    assert {row["geometry_type"] for row in rows} == {"mesh"}
    assert {row["mode"] for row in rows} == {"penalty", "moving_boundary"}
    assert {row["reaction_transfer_mode"] for row in rows} == {"engineering", "link_area_experimental"}
    for row in rows:
        assert_short_driver_row(row)


def test_step27_voxel_64_driver_outputs_are_valid():
    rows = read_csv_rows("outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.csv")
    assert len(rows) == 3
    assert {row["geometry_type"] for row in rows} == {"voxel"}
    assert {row["mode"] for row in rows} == {"penalty", "moving_boundary"}
    assert {row["reaction_transfer_mode"] for row in rows} == {"engineering", "link_area_experimental"}
    for row in rows:
        assert_short_driver_row(row)


def test_step27_driver_projection_alignment_is_valid():
    payload = read_json("outputs/step27_driver_projection_alignment/driver_projection_alignment.json")
    rows = read_csv_rows("outputs/step27_driver_projection_alignment/driver_projection_alignment.csv")
    assert int(payload["row_count"]) == 6
    assert int(payload["pass_count"]) == 6
    assert len(rows) == 6
    for row in rows:
        assert as_bool(row["alignment_pass"])
        assert int(float(row["n_grid"])) == 64
        assert abs(float(row["projected_mass_delta"])) <= 5.0e-5
        assert abs(int(float(row["active_cell_count_delta"]))) <= 32


def test_step27_64_driver_summary_is_valid():
    payload = read_json("outputs/step27_64_driver_summary/driver_64_summary.json")
    summary = payload["summary"]
    assert int(summary["driver_row_count"]) == 6
    assert int(summary["mesh_row_count"]) == 3
    assert int(summary["voxel_row_count"]) == 3
    assert int(summary["penalty_row_count"]) == 2
    assert int(summary["moving_boundary_row_count"]) == 4
    assert int(summary["link_area_row_count"]) == 2
    assert int(summary["stable_count"]) == 6
    assert int(summary["quality_report_count"]) == 6
    assert int(summary["quality_pass_count"]) == 6
    assert float(summary["min_rho_min_global"]) > 0.95
    assert float(summary["max_rho_max_global"]) < 1.05
    assert float(summary["max_lbm_max_v_global"]) < 0.1
    assert float(summary["min_mpm_min_J_global"]) > 0.0
    assert float(summary["max_mpm_max_speed_global"]) < 10.0
    assert float(summary["min_projected_mass"]) > 0.0
    assert int(summary["min_active_cell_count"]) > 0
    assert math.isfinite(float(summary["max_driver_total_time"]))


def test_step27_quality_report_aggregation_is_valid():
    payload = read_json("outputs/step27_quality_report_aggregation/quality_report_summary.json")
    summary = payload["summary"]
    assert int(summary["quality_report_count"]) == 6
    assert int(summary["pass_count"]) == 6
    assert int(summary["strict_count"]) == 6
    assert int(summary["error_count"]) == 0
    assert int(summary["warning_count"]) == 0
    assert int(summary["mesh_row_count"]) == 3
    assert int(summary["voxel_row_count"]) == 3


def test_step27_step26_regression_guard_is_valid():
    summary = read_json("outputs/step27_step26_regression_guard/step26_regression_guard.json")
    rows = read_csv_rows("outputs/step27_step26_regression_guard/step26_regression_guard.csv")
    assert int(summary["row_count"]) == 8
    assert int(summary["pass_count"]) == 8
    assert int(summary["step26_projection_row_count"]) == 6
    assert int(summary["step26_driver_row_count"]) == 8
    assert int(summary["step26_stable_count"]) == 8
    assert int(summary["step26_quality_report_count"]) == 8
    assert int(summary["step26_large_file_count"]) == 0
    assert all(as_bool(row["pass"]) for row in rows)


def test_step27_default_modes_remain_unchanged():
    geometry_config = read_text("src/geometry_config.py")
    fsi_config = read_text("src/fsi_config.py")
    assert "quality_check_enabled: bool = False" in geometry_config
    assert "quality_check_strict: bool = False" in geometry_config
    assert "quality_check_enabled: bool = False" in fsi_config
    assert "quality_check_strict: bool = False" in fsi_config
    assert 'reaction_transfer_mode: str = "engineering"' in fsi_config

    formula_files = [
        "src/coupling.py",
        "src/moving_boundary_coupling.py",
        "src/link_area_coupling.py",
        "src/lbm_fluid.py",
        "src/mpm_solid.py",
        "src/projection.py",
    ]
    status = subprocess.run(["git", "status", "--short", *formula_files], cwd=ROOT, check=True, capture_output=True, text=True)
    assert status.stdout.strip() == ""


def test_step27_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "README.md",
            "docs/08_roadmap.md",
            "docs/09_api_reference.md",
            "docs/11_artifact_policy.md",
            "docs/12_geometry_ingestion.md",
            "docs/19_geometry_import_pipeline.md",
            "docs/24_controlled_real_geometry_intake.md",
            "docs/25_real_geometry_candidate_policy.md",
            "docs/26_controlled_real_geometry_short_feasibility.md",
            "docs/27_controlled_real_geometry_64_short_driver.md",
            "STEP27_CONTROLLED_REAL_GEOMETRY_64_SHORT_DRIVER_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step27_artifact_budget_is_valid():
    summary = read_json("outputs/step27_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step27_total_size_mb"]) < 15.0
    assert float(summary["total_size_mb"]) < 155.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["step27_vtr_count"]) == 0
    assert int(summary["step27_particle_npy_count"]) == 0
    assert int(summary["step27_quality_report_count"]) == 6
    assert int(summary["private_absolute_path_count"]) == 0
    manifest_rows = read_csv_rows("outputs/step27_artifact_manifest/artifact_manifest.csv")
    step27_paths = [row["path"] for row in manifest_rows if row["path"].startswith("outputs/step27")]
    assert not [path for path in step27_paths if path.endswith(".vtr")]
    assert not [path for path in step27_paths if path.endswith(".npy") and "particle" in path.lower()]


def test_step27_report_acceptance_complete():
    report = read_text("STEP27_CONTROLLED_REAL_GEOMETRY_64_SHORT_DRIVER_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Candidate Fingerprint Guard",
        "## 5. 64^3 Mesh Short Driver Feasibility",
        "## 6. 64^3 Voxel Short Driver Feasibility",
        "## 7. Driver Projection Alignment",
        "## 8. 64^3 Driver Summary",
        "## 9. Quality Report Aggregation",
        "## 10. Step 26 Regression Guard",
        "## 11. Artifact Manifest Summary",
        "## 12. Verification Commands",
        "## 13. GitHub Sync Information",
        "## 14. Acceptance Checklist",
        "## 15. Decision For Step 28",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] candidate fingerprint guard passes",
        "- [x] Step 25 manifest fingerprints match current candidate files",
        "- [x] Step 26 generated GeometryConfig files remain valid",
        "- [x] mesh 64^3 penalty short driver passes",
        "- [x] voxel 64^3 moving_boundary link_area short driver passes",
        "- [x] every Step 27 driver row writes geometry_quality_report.json",
        "- [x] every Step 27 quality gate is strict",
        "- [x] all driver rows have completed_lbm_steps >= 5",
        "- [x] driver/projection alignment passes against Step 26 64^3 projection-only rows",
        "- [x] Step 26 regression guard passes",
        "- [x] no FSI formula changes",
        "- [x] no moving bounce-back formula changes",
        "- [x] no real squid validation claims",
        "- [x] no squid swimming claims",
        "- [x] no squid actuation claims",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] artifact large_file_count == 0",
        "- [x] logs/step27_pytest.log exists",
        "- [x] pytest -q passes",
        "- [x] Step 27 contract test passes",
        "- [x] git diff --check passes",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []

    assert (ROOT / "logs/step27_pytest.log").is_file()
    for path, marker in STEP27_LOG_MARKERS.items():
        assert (ROOT / path).is_file(), path
        assert marker in read_text(path), path

    external_status = subprocess.run(
        ["git", "status", "--short", "external/taichi_LBM3D"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert external_status.stdout.strip() == ""


def assert_short_driver_row(row):
    assert as_bool(row["stable"])
    assert as_bool(row["quality_check_enabled"])
    assert as_bool(row["quality_check_strict"])
    assert as_bool(row["quality_pass"])
    assert as_bool(row["quality_gate_strict"])
    assert row["quality_severity"] == "ok"
    assert int(float(row["quality_warnings_count"])) == 0
    assert int(float(row["quality_reasons_count"])) == 0
    assert (ROOT / row["quality_report_path"]).is_file()
    assert (ROOT / row["driver_timing_path"]).is_file()
    assert int(float(row["n_grid"])) == 64
    assert int(float(row["n_particles"])) == 4096
    assert int(float(row["n_lbm_steps"])) == 5
    assert int(float(row["mpm_substeps_per_lbm_step"])) == 5
    assert int(float(row["completed_lbm_steps"])) >= 5
    assert int(float(row["total_mpm_substeps"])) >= 25
    assert float(row["rho_min_global"]) > 0.95
    assert float(row["rho_max_global"]) < 1.05
    assert float(row["lbm_max_v_global"]) < 0.1
    assert float(row["mpm_min_J_global"]) > 0.0
    assert float(row["mpm_max_speed_global"]) < 10.0
    assert float(row["projected_mass"]) > 0.0
    assert int(float(row["active_cell_count"])) > 0
    assert not as_bool(row["has_nan"])
    assert not as_bool(row["has_inf"])
    assert "not real squid validation" in row["notes"]
    assert_mode_specific(row)


def assert_mode_specific(row):
    mode = row["mode"]
    transfer = row["reaction_transfer_mode"]
    if mode == "penalty":
        assert float(row["cell_force_max_norm"]) > 0.0
        assert float(row["hydro_force_max_norm"]) > 0.0
        assert int(float(row["bb_link_count_max"])) == 0
    if mode == "moving_boundary":
        assert float(row["cell_force_max_norm"]) == 0.0
        assert float(row["hydro_force_max_norm"]) > 0.0
        assert int(float(row["bb_link_count_max"])) > 0
        assert int(float(row["active_reaction_particle_count_max"])) > 0
        if transfer == "link_area_experimental":
            assert 0.25 <= float(row["area_scale_final"]) <= 2.0
            assert math.isfinite(float(row["raw_area_scale_final"]))


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_json(relative_path: str):
    return json.loads(read_text(relative_path))


def read_csv_rows(relative_path: str) -> list[dict]:
    with (ROOT / relative_path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}
