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
    "step26_geometry_config",
    ROOT / "src" / "geometry_config.py",
)
_GEOMETRY_CONFIG_MODULE = importlib.util.module_from_spec(_GEOMETRY_CONFIG_SPEC)
sys.modules[_GEOMETRY_CONFIG_SPEC.name] = _GEOMETRY_CONFIG_MODULE
_GEOMETRY_CONFIG_SPEC.loader.exec_module(_GEOMETRY_CONFIG_MODULE)
GeometryConfig = _GEOMETRY_CONFIG_MODULE.GeometryConfig

STEP26_REQUIRED_FILES = [
    "STEP26_CONTROLLED_REAL_GEOMETRY_SHORT_FEASIBILITY_GOAL.md",
    "STEP26_CONTROLLED_REAL_GEOMETRY_SHORT_FEASIBILITY_REPORT.md",
    "src/geometry_driver_config.py",
    "src/real_geometry_feasibility.py",
    "configs/step26_real_candidate_smoke_mesh_geometry.json",
    "configs/step26_real_candidate_smoke_voxel_geometry.json",
    "configs/step26_projection_real_candidate_smoke_mesh_32.json",
    "configs/step26_projection_real_candidate_smoke_mesh_48.json",
    "configs/step26_projection_real_candidate_smoke_mesh_64.json",
    "configs/step26_projection_real_candidate_smoke_voxel_32.json",
    "configs/step26_projection_real_candidate_smoke_voxel_48.json",
    "configs/step26_projection_real_candidate_smoke_voxel_64.json",
    "configs/step26_driver_real_candidate_smoke_mesh_48_none.json",
    "configs/step26_driver_real_candidate_smoke_mesh_48_penalty.json",
    "configs/step26_driver_real_candidate_smoke_mesh_48_moving_boundary.json",
    "configs/step26_driver_real_candidate_smoke_mesh_48_link_area.json",
    "configs/step26_driver_real_candidate_smoke_voxel_48_none.json",
    "configs/step26_driver_real_candidate_smoke_voxel_48_penalty.json",
    "configs/step26_driver_real_candidate_smoke_voxel_48_moving_boundary.json",
    "configs/step26_driver_real_candidate_smoke_voxel_48_link_area.json",
    "baseline_tests/step26_common.py",
    "baseline_tests/run_step26_candidate_fingerprint_guard.py",
    "baseline_tests/run_step26_generate_driver_geometry_configs.py",
    "baseline_tests/run_step26_projection_scale_diagnostics.py",
    "baseline_tests/run_step26_step25_projection_regression.py",
    "baseline_tests/run_step26_short_driver_mesh_48_modes.py",
    "baseline_tests/run_step26_short_driver_voxel_48_modes.py",
    "baseline_tests/run_step26_short_driver_summary.py",
    "baseline_tests/run_step26_quality_report_aggregation.py",
    "baseline_tests/run_step26_step25_regression_guard.py",
    "baseline_tests/run_step26_artifact_manifest.py",
    "docs/26_controlled_real_geometry_short_feasibility.md",
    "tests/test_step26_controlled_real_geometry_short_feasibility_contract.py",
]

STEP26_OUTPUT_FILES = [
    "outputs/step26_candidate_fingerprint_guard/fingerprint_guard.csv",
    "outputs/step26_candidate_fingerprint_guard/fingerprint_guard.json",
    "outputs/step26_generated_geometry_configs/generated_geometry_configs.csv",
    "outputs/step26_generated_geometry_configs/generated_geometry_configs.json",
    "outputs/step26_projection_scale_diagnostics/projection_scale_results.csv",
    "outputs/step26_projection_scale_diagnostics/projection_scale_results.json",
    "outputs/step26_step25_projection_regression/step25_projection_regression.csv",
    "outputs/step26_step25_projection_regression/step25_projection_regression.json",
    "outputs/step26_short_driver_mesh_48_modes/mesh_48_short_driver_results.csv",
    "outputs/step26_short_driver_mesh_48_modes/mesh_48_short_driver_results.npz",
    "outputs/step26_short_driver_voxel_48_modes/voxel_48_short_driver_results.csv",
    "outputs/step26_short_driver_voxel_48_modes/voxel_48_short_driver_results.npz",
    "outputs/step26_short_driver_summary/short_driver_summary.csv",
    "outputs/step26_short_driver_summary/short_driver_summary.json",
    "outputs/step26_quality_report_aggregation/quality_report_summary.csv",
    "outputs/step26_quality_report_aggregation/quality_report_summary.json",
    "outputs/step26_step25_regression_guard/step25_regression_guard.csv",
    "outputs/step26_step25_regression_guard/step25_regression_guard.json",
    "outputs/step26_artifact_manifest/artifact_manifest.csv",
    "outputs/step26_artifact_manifest/artifact_summary.csv",
    "outputs/step26_artifact_manifest/artifact_summary.json",
]

STEP26_GEOMETRY_CONFIGS = [
    "configs/step26_real_candidate_smoke_mesh_geometry.json",
    "configs/step26_real_candidate_smoke_voxel_geometry.json",
]

STEP26_DRIVER_CONFIGS = [
    "configs/step26_driver_real_candidate_smoke_mesh_48_none.json",
    "configs/step26_driver_real_candidate_smoke_mesh_48_penalty.json",
    "configs/step26_driver_real_candidate_smoke_mesh_48_moving_boundary.json",
    "configs/step26_driver_real_candidate_smoke_mesh_48_link_area.json",
    "configs/step26_driver_real_candidate_smoke_voxel_48_none.json",
    "configs/step26_driver_real_candidate_smoke_voxel_48_penalty.json",
    "configs/step26_driver_real_candidate_smoke_voxel_48_moving_boundary.json",
    "configs/step26_driver_real_candidate_smoke_voxel_48_link_area.json",
]

STEP26_LOG_MARKERS = {
    "logs/step26_candidate_fingerprint_guard.log": "[OK] Step 26 candidate fingerprint guard finished",
    "logs/step26_generate_driver_geometry_configs.log": "[OK] Step 26 generated driver geometry configs finished",
    "logs/step26_projection_scale_diagnostics.log": "[OK] Step 26 projection scale diagnostics finished",
    "logs/step26_step25_projection_regression.log": "[OK] Step 26 Step 25 projection regression finished",
    "logs/step26_short_driver_mesh_48_modes.log": "[OK] Step 26 mesh 48 short driver modes finished",
    "logs/step26_short_driver_voxel_48_modes.log": "[OK] Step 26 voxel 48 short driver modes finished",
    "logs/step26_short_driver_summary.log": "[OK] Step 26 short driver summary finished",
    "logs/step26_quality_report_aggregation.log": "[OK] Step 26 quality report aggregation finished",
    "logs/step26_step25_regression_guard.log": "[OK] Step 26 Step 25 regression guard finished",
    "logs/step26_artifact_manifest.log": "[OK] Step 26 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 26 is controlled real geometry projection-only and short driver feasibility.",
    "Step 26 is not real squid validation.",
    "Step 26 does not implement squid actuation.",
    "Step 26 does not implement squid swimming.",
    "Step 26 does not implement new FSI physics.",
    "Step 26 does not validate production sharp-interface FSI.",
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


def test_step26_required_artifacts_exist():
    missing = [path for path in STEP26_REQUIRED_FILES + STEP26_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_step26_candidate_fingerprint_guard_is_valid():
    summary = read_json("outputs/step26_candidate_fingerprint_guard/fingerprint_guard.json")
    rows = read_csv_rows("outputs/step26_candidate_fingerprint_guard/fingerprint_guard.csv")
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
        assert ":" not in row["source_file_redacted"]
        assert "\\Users\\" not in row["source_file_redacted"]


def test_step26_generated_geometry_configs_are_valid():
    summary = read_json("outputs/step26_generated_geometry_configs/generated_geometry_configs.json")
    assert int(summary["row_count"]) == 2
    assert int(summary["driver_config_count"]) == 8
    for path in STEP26_GEOMETRY_CONFIGS:
        config = GeometryConfig.from_json(ROOT / path)
        assert config.geometry_type in {"mesh", "voxel"}
        assert int(config.n_particles) == 4096
        assert config.quality_check_enabled is True
        assert config.quality_check_strict is True
        assert (ROOT / config.geometry_file).is_file()
    for path in STEP26_DRIVER_CONFIGS:
        payload = read_json(path)
        assert payload["quality_check_enabled"] is True
        assert payload["quality_check_strict"] is True
        assert payload["write_vtk"] is False
        assert payload["write_particles"] is False
        assert int(payload["n_grid"]) == 48
        assert int(payload["n_lbm_steps"]) == 5
        assert int(payload["mpm_substeps_per_lbm_step"]) == 5


def test_step26_projection_scale_diagnostics_are_valid():
    summary = read_json("outputs/step26_projection_scale_diagnostics/projection_scale_results.json")
    rows = summary["rows"]
    assert int(summary["row_count"]) == 6
    assert {int(row["n_grid"]) for row in rows} == {32, 48, 64}
    assert {row["candidate_id"] for row in rows} == {"real_candidate_smoke_mesh", "real_candidate_smoke_voxel"}
    for row in rows:
        assert row["projection_pass"] is True
        assert float(row["projected_mass"]) > 0.0
        assert int(row["active_cell_count"]) > 0
        assert 0.0 <= float(row["solid_phi_min"]) <= float(row["solid_phi_max"]) <= 1.0
        assert is_finite(row["projected_volume_raw"])
        assert is_finite(row["projected_volume_clamped"])
        assert is_finite(row["max_phi_raw"])
        assert row["has_nan"] is False
        assert row["has_inf"] is False
        assert "projection-only" in row["scope_note"]
        assert "real squid validation" in row["scope_note"]


def test_step26_step25_projection_regression_is_valid():
    summary = read_json("outputs/step26_step25_projection_regression/step25_projection_regression.json")
    rows = read_csv_rows("outputs/step26_step25_projection_regression/step25_projection_regression.csv")
    assert int(summary["compared_row_count"]) == 2
    assert int(summary["pass_count"]) == 2
    for row in rows:
        assert as_bool(row["regression_pass"])
        assert as_bool(row["projection_pass_both"])
        assert abs(float(row["projected_mass_delta"])) <= 1.0e-6
        assert int(float(row["active_cell_count_delta"])) == 0
        assert float(row["solid_phi_min_delta"]) == 0.0
        assert float(row["solid_phi_max_delta"]) == 0.0


def test_step26_mesh_short_driver_outputs_are_valid():
    rows = read_csv_rows("outputs/step26_short_driver_mesh_48_modes/mesh_48_short_driver_results.csv")
    assert len(rows) == 4
    for row in rows:
        assert row["geometry_type"] == "mesh"
        assert_short_driver_row(row)


def test_step26_voxel_short_driver_outputs_are_valid():
    rows = read_csv_rows("outputs/step26_short_driver_voxel_48_modes/voxel_48_short_driver_results.csv")
    assert len(rows) == 4
    for row in rows:
        assert row["geometry_type"] == "voxel"
        assert_short_driver_row(row)


def test_step26_short_driver_summary_is_valid():
    payload = read_json("outputs/step26_short_driver_summary/short_driver_summary.json")
    summary = payload["summary"]
    assert int(summary["driver_row_count"]) == 8
    assert int(summary["stable_count"]) == 8
    assert int(summary["quality_report_count"]) == 8
    assert int(summary["quality_pass_count"]) == 8
    assert float(summary["min_rho_min_global"]) > 0.95
    assert float(summary["max_rho_max_global"]) < 1.05
    assert float(summary["max_lbm_max_v_global"]) < 0.1
    assert float(summary["min_mpm_min_J_global"]) > 0.0
    assert float(summary["max_mpm_max_speed_global"]) < 10.0
    assert math.isfinite(float(summary["max_step26_driver_total_time"]))


def test_step26_quality_report_aggregation_is_valid():
    payload = read_json("outputs/step26_quality_report_aggregation/quality_report_summary.json")
    summary = payload["summary"]
    assert int(summary["quality_report_count"]) == 8
    assert int(summary["pass_count"]) == 8
    assert int(summary["strict_count"]) == 8
    assert int(summary["error_count"]) == 0
    assert int(summary["warning_count"]) == 0
    assert int(summary["mesh_row_count"]) == 4
    assert int(summary["voxel_row_count"]) == 4


def test_step26_step25_regression_guard_is_valid():
    summary = read_json("outputs/step26_step25_regression_guard/step25_regression_guard.json")
    rows = read_csv_rows("outputs/step26_step25_regression_guard/step25_regression_guard.csv")
    assert int(summary["row_count"]) == 7
    assert int(summary["pass_count"]) == 7
    assert int(summary["step25_manifest_row_count"]) == 2
    assert int(summary["step25_large_file_count"]) == 0
    assert int(summary["step25_scan_data_file_count"]) == 0
    assert int(summary["step25_raw_candidate_large_file_count"]) == 0
    assert all(as_bool(row["pass"]) for row in rows)


def test_step26_default_modes_remain_unchanged():
    geometry_config = read_text("src/mpm_lbm/sim/geometry/config.py")
    fsi_config = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    assert "quality_check_enabled: bool = False" in geometry_config
    assert "quality_check_strict: bool = False" in geometry_config
    assert "quality_check_enabled: bool = False" in fsi_config
    assert "quality_check_strict: bool = False" in fsi_config
    assert 'reaction_transfer_mode: str = "engineering"' in fsi_config

    formula_files = [
        "src/coupling.py",
        "src/moving_boundary_coupling.py",
        "src/mpm_lbm/sim/coupling/link_area.py",
        "src/lbm_fluid.py",
        "src/mpm_solid.py",
        "src/projection.py",
    ]
    status = subprocess.run(["git", "status", "--short", *formula_files], cwd=ROOT, check=True, capture_output=True, text=True)
    assert status.stdout.strip() == ""


def test_step26_docs_scope_and_forbidden_claims_are_valid():
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
            "STEP26_CONTROLLED_REAL_GEOMETRY_SHORT_FEASIBILITY_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step26_artifact_budget_is_valid():
    summary = read_json("outputs/step26_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step26_total_size_mb"]) < 8.0
    assert float(summary["total_size_mb"]) < 170.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["step26_vtr_count"]) == 0
    assert int(summary["step26_particle_npy_count"]) == 0
    assert int(summary["step26_quality_report_count"]) == 8
    assert int(summary["private_absolute_path_count"]) == 0
    manifest_rows = read_csv_rows("outputs/step26_artifact_manifest/artifact_manifest.csv")
    step26_paths = [row["path"] for row in manifest_rows if row["path"].startswith("outputs/step26")]
    assert not [path for path in step26_paths if path.endswith(".vtr")]
    assert not [path for path in step26_paths if path.endswith(".npy") and "particle" in path.lower()]


def test_step26_report_acceptance_complete():
    report = read_text("STEP26_CONTROLLED_REAL_GEOMETRY_SHORT_FEASIBILITY_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Candidate Fingerprint Guard",
        "## 5. Generated Driver Geometry Configs",
        "## 6. Projection-Only Scale Diagnostics",
        "## 7. Step 25 Projection Regression",
        "## 8. 48^3 Mesh Short Driver Feasibility",
        "## 9. 48^3 Voxel Short Driver Feasibility",
        "## 10. Short Driver Summary",
        "## 11. Quality Report Aggregation",
        "## 12. Step 25 Regression Guard",
        "## 13. Artifact Manifest Summary",
        "## 14. Verification Commands",
        "## 15. GitHub Sync Information",
        "## 16. Acceptance Checklist",
        "## 17. Decision For Step 27",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] candidate fingerprint guard passes",
        "- [x] Step 25 manifest fingerprints match current candidate files",
        "- [x] generated driver GeometryConfig files are valid",
        "- [x] projection-only scale diagnostics pass for 32^3 rows",
        "- [x] projection-only scale diagnostics pass for 48^3 rows",
        "- [x] projection-only scale diagnostics pass for 64^3 rows",
        "- [x] Step 25 projection regression passes for 32^3 rows",
        "- [x] mesh 48^3 none short driver passes",
        "- [x] voxel 48^3 link_area short driver passes",
        "- [x] every Step 26 driver row writes geometry_quality_report.json",
        "- [x] every Step 26 quality gate is strict",
        "- [x] all driver rows have completed_lbm_steps >= 5",
        "- [x] no FSI formula changes",
        "- [x] no moving bounce-back formula changes",
        "- [x] no real squid validation claims",
        "- [x] no squid swimming claims",
        "- [x] no squid actuation claims",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] artifact large_file_count == 0",
        "- [x] logs/step26_pytest.log exists",
        "- [x] pytest -q passes",
        "- [x] Step 26 contract test passes",
        "- [x] git diff --check passes",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []

    assert (ROOT / "logs/step26_pytest.log").is_file()
    for path, marker in STEP26_LOG_MARKERS.items():
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
    assert int(float(row["n_grid"])) == 48
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
    if mode == "none":
        assert float(row["cell_force_max_norm"]) == 0.0
        assert int(float(row["bb_link_count_max"])) == 0
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


def is_finite(value) -> bool:
    return math.isfinite(float(value))
