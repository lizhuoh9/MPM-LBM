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
    "step28_geometry_config",
    ROOT / "src" / "geometry_config.py",
)
_GEOMETRY_CONFIG_MODULE = importlib.util.module_from_spec(_GEOMETRY_CONFIG_SPEC)
sys.modules[_GEOMETRY_CONFIG_SPEC.name] = _GEOMETRY_CONFIG_MODULE
_GEOMETRY_CONFIG_SPEC.loader.exec_module(_GEOMETRY_CONFIG_MODULE)
GeometryConfig = _GEOMETRY_CONFIG_MODULE.GeometryConfig

STEP28_REQUIRED_FILES = [
    "STEP28_CONTROLLED_REAL_GEOMETRY_64_TRANSFER_DIAGNOSTICS_GOAL.md",
    "STEP28_CONTROLLED_REAL_GEOMETRY_64_TRANSFER_DIAGNOSTICS_REPORT.md",
    "docs/28_controlled_real_geometry_64_transfer_diagnostics.md",
    "configs/step28_compare_real_candidate_smoke_mesh_64_moving_boundary.json",
    "configs/step28_compare_real_candidate_smoke_mesh_64_link_area.json",
    "configs/step28_compare_real_candidate_smoke_voxel_64_moving_boundary.json",
    "configs/step28_compare_real_candidate_smoke_voxel_64_link_area.json",
    "baseline_tests/step28_common.py",
    "baseline_tests/run_step28_candidate_fingerprint_guard.py",
    "baseline_tests/run_step28_64_transfer_pair_driver.py",
    "baseline_tests/run_step28_engineering_vs_link_area_comparison.py",
    "baseline_tests/run_step28_force_reaction_diagnostics.py",
    "baseline_tests/run_step28_area_scale_envelope.py",
    "baseline_tests/run_step28_step27_prefix_regression.py",
    "baseline_tests/run_step28_quality_report_aggregation.py",
    "baseline_tests/run_step28_step27_regression_guard.py",
    "baseline_tests/run_step28_artifact_manifest.py",
    "tests/test_step28_controlled_real_geometry_64_transfer_diagnostics_contract.py",
]

STEP28_OUTPUT_FILES = [
    "outputs/step28_candidate_fingerprint_guard/fingerprint_guard.csv",
    "outputs/step28_candidate_fingerprint_guard/fingerprint_guard.json",
    "outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.csv",
    "outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.npz",
    "outputs/step28_engineering_vs_link_area_comparison/engineering_vs_link_area.csv",
    "outputs/step28_engineering_vs_link_area_comparison/engineering_vs_link_area.json",
    "outputs/step28_force_reaction_diagnostics/force_reaction_diagnostics.csv",
    "outputs/step28_force_reaction_diagnostics/force_reaction_diagnostics.json",
    "outputs/step28_area_scale_envelope/area_scale_envelope.csv",
    "outputs/step28_area_scale_envelope/area_scale_envelope.json",
    "outputs/step28_step27_prefix_regression/step27_prefix_regression.csv",
    "outputs/step28_step27_prefix_regression/step27_prefix_regression.json",
    "outputs/step28_quality_report_aggregation/quality_report_summary.csv",
    "outputs/step28_quality_report_aggregation/quality_report_summary.json",
    "outputs/step28_step27_regression_guard/step27_regression_guard.csv",
    "outputs/step28_step27_regression_guard/step27_regression_guard.json",
    "outputs/step28_artifact_manifest/artifact_manifest.csv",
    "outputs/step28_artifact_manifest/artifact_summary.csv",
    "outputs/step28_artifact_manifest/artifact_summary.json",
]

STEP28_DRIVER_CONFIGS = [
    "configs/step28_compare_real_candidate_smoke_mesh_64_moving_boundary.json",
    "configs/step28_compare_real_candidate_smoke_mesh_64_link_area.json",
    "configs/step28_compare_real_candidate_smoke_voxel_64_moving_boundary.json",
    "configs/step28_compare_real_candidate_smoke_voxel_64_link_area.json",
]

STEP28_LOG_MARKERS = {
    "logs/step28_candidate_fingerprint_guard.log": "[OK] Step 28 candidate fingerprint guard finished",
    "logs/step28_64_transfer_pair_driver.log": "[OK] Step 28 64 transfer pair driver finished",
    "logs/step28_engineering_vs_link_area_comparison.log": "[OK] Step 28 engineering vs link-area comparison finished",
    "logs/step28_force_reaction_diagnostics.log": "[OK] Step 28 force reaction diagnostics finished",
    "logs/step28_area_scale_envelope.log": "[OK] Step 28 area-scale envelope finished",
    "logs/step28_step27_prefix_regression.log": "[OK] Step 28 Step 27 prefix regression finished",
    "logs/step28_quality_report_aggregation.log": "[OK] Step 28 quality report aggregation finished",
    "logs/step28_step27_regression_guard.log": "[OK] Step 28 Step 27 regression guard finished",
    "logs/step28_artifact_manifest.log": "[OK] Step 28 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 28 is controlled real geometry 64^3 transfer diagnostics.",
    "Step 28 compares engineering and link_area_experimental transfer diagnostically.",
    "Step 28 is not real squid validation.",
    "Step 28 does not implement squid actuation.",
    "Step 28 does not implement squid swimming.",
    "Step 28 does not implement new FSI physics.",
    "Step 28 does not validate production sharp-interface FSI.",
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
    "link_area_experimental is physically superior",
    "engineering transfer is physically validated",
    "implements two_phase",
    "implements contact_angle",
]


def test_step28_required_artifacts_exist():
    missing = [path for path in STEP28_REQUIRED_FILES + STEP28_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_step28_driver_configs_are_valid():
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

    assert len(STEP28_DRIVER_CONFIGS) == 4
    modes = []
    transfers = []
    for path in STEP28_DRIVER_CONFIGS:
        payload = read_json(path)
        assert payload["quality_check_enabled"] is True
        assert payload["quality_check_strict"] is True
        assert payload["write_vtk"] is False
        assert payload["write_particles"] is False
        assert int(payload["n_grid"]) == 64
        assert int(payload["n_particles"]) == 4096
        assert int(payload["n_lbm_steps"]) == 10
        assert int(payload["mpm_substeps_per_lbm_step"]) == 5
        assert int(payload["output_interval"]) == 1
        assert payload["coupling_mode"] == "moving_boundary"
        assert payload["geometry_config_path"].startswith("configs/step26_real_candidate_smoke_")
        assert payload["reaction_transfer_mode"] in {"engineering", "link_area_experimental"}
        modes.append(payload["coupling_mode"])
        transfers.append(payload["reaction_transfer_mode"])
        if payload["reaction_transfer_mode"] == "link_area_experimental":
            assert payload["link_area_policy"] == "inverse_length"
            assert float(payload["link_area_scale_min"]) == 0.25
            assert float(payload["link_area_scale_max"]) == 2.0
    assert modes == ["moving_boundary"] * 4
    assert transfers.count("engineering") == 2
    assert transfers.count("link_area_experimental") == 2


def test_step28_candidate_fingerprint_guard_is_valid():
    summary = read_json("outputs/step28_candidate_fingerprint_guard/fingerprint_guard.json")
    rows = read_csv_rows("outputs/step28_candidate_fingerprint_guard/fingerprint_guard.csv")
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


def test_step28_transfer_pair_driver_outputs_are_valid():
    payload = read_json("outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.json")
    summary = payload["summary"]
    rows = read_csv_rows("outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.csv")
    assert int(summary["driver_row_count"]) == 4
    assert int(summary["stable_count"]) == 4
    assert int(summary["quality_report_count"]) == 4
    assert int(summary["quality_pass_count"]) == 4
    assert int(summary["strict_count"]) == 4
    assert int(summary["mesh_row_count"]) == 2
    assert int(summary["voxel_row_count"]) == 2
    assert int(summary["engineering_row_count"]) == 2
    assert int(summary["link_area_row_count"]) == 2
    assert len(rows) == 4
    for row in rows:
        assert_transfer_driver_row(row)
        diagnostics_path = ROOT / Path(row["driver_timing_path"]).parent / "diagnostics_timeseries.csv"
        assert diagnostics_path.is_file()


def test_step28_engineering_vs_link_area_comparison_is_valid():
    payload = read_json("outputs/step28_engineering_vs_link_area_comparison/engineering_vs_link_area.json")
    rows = read_csv_rows("outputs/step28_engineering_vs_link_area_comparison/engineering_vs_link_area.csv")
    assert int(payload["summary"]["row_count"]) == 2
    assert int(payload["summary"]["pass_count"]) == 2
    assert len(rows) == 2
    for row in rows:
        assert as_bool(row["comparison_pass"])
        assert abs(float(row["rho_min_delta"])) <= 5.0e-4
        assert abs(float(row["rho_max_delta"])) <= 5.0e-4
        assert abs(float(row["lbm_max_v_delta"])) <= 5.0e-4
        assert abs(float(row["mpm_min_J_delta"])) <= 5.0e-4
        assert abs(float(row["projected_mass_delta"])) <= 5.0e-5
        assert 0.25 <= float(row["link_area_area_scale_final"]) <= 2.0


def test_step28_force_reaction_diagnostics_are_valid():
    payload = read_json("outputs/step28_force_reaction_diagnostics/force_reaction_diagnostics.json")
    rows = read_csv_rows("outputs/step28_force_reaction_diagnostics/force_reaction_diagnostics.csv")
    assert int(payload["summary"]["row_count"]) == 4
    assert int(payload["summary"]["pass_count"]) == 4
    assert len(rows) == 4
    for row in rows:
        assert int(float(row["row_count"])) >= 10
        assert int(float(row["post_step_positive_rows"])) >= 10
        assert float(row["hydro_force_max_norm_min"]) > 0.0
        assert float(row["hydro_force_max_norm_max"]) > 0.0
        assert math.isfinite(float(row["max_grid_reaction_norm_min"]))
        assert math.isfinite(float(row["max_grid_reaction_norm_max"]))
        assert int(float(row["active_reaction_particle_count_max"])) > 0
        assert int(float(row["bb_link_count_max"])) > 0
        assert math.isfinite(float(row["bb_max_correction_max"]))
        assert as_bool(row["finite_pass"])
        assert as_bool(row["diagnostic_pass"])


def test_step28_area_scale_envelope_is_valid():
    payload = read_json("outputs/step28_area_scale_envelope/area_scale_envelope.json")
    rows = read_csv_rows("outputs/step28_area_scale_envelope/area_scale_envelope.csv")
    assert int(payload["summary"]["row_count"]) == 2
    assert int(payload["summary"]["pass_count"]) == 2
    assert len(rows) == 2
    for row in rows:
        assert as_bool(row["finite_pass"])
        assert as_bool(row["bounded_pass"])
        assert 0.25 <= float(row["area_scale_min_observed"]) <= float(row["area_scale_max_observed"]) <= 2.0
        assert math.isfinite(float(row["area_scale_final"]))
        assert math.isfinite(float(row["raw_area_scale_min"]))
        assert math.isfinite(float(row["raw_area_scale_max"]))


def test_step28_step27_prefix_regression_is_valid():
    payload = read_json("outputs/step28_step27_prefix_regression/step27_prefix_regression.json")
    rows = read_csv_rows("outputs/step28_step27_prefix_regression/step27_prefix_regression.csv")
    assert int(payload["summary"]["row_count"]) == 4
    assert int(payload["summary"]["pass_count"]) == 4
    assert len(rows) == 4
    for row in rows:
        assert as_bool(row["prefix_pass"])
        assert abs(float(row["rho_min_delta"])) <= 1.0e-5
        assert abs(float(row["rho_max_delta"])) <= 1.0e-5
        assert abs(float(row["lbm_max_v_delta"])) <= 1.0e-5
        assert abs(float(row["mpm_min_J_delta"])) <= 1.0e-5
        assert abs(float(row["projected_mass_delta"])) <= 5.0e-5
        assert int(float(row["active_cell_count_delta"])) == 0
        assert int(float(row["bb_link_count_delta"])) == 0


def test_step28_quality_report_aggregation_is_valid():
    payload = read_json("outputs/step28_quality_report_aggregation/quality_report_summary.json")
    summary = payload["summary"]
    assert int(summary["quality_report_count"]) == 4
    assert int(summary["pass_count"]) == 4
    assert int(summary["strict_count"]) == 4
    assert int(summary["error_count"]) == 0
    assert int(summary["warning_count"]) == 0
    assert int(summary["mesh_row_count"]) == 2
    assert int(summary["voxel_row_count"]) == 2


def test_step28_step27_regression_guard_is_valid():
    summary = read_json("outputs/step28_step27_regression_guard/step27_regression_guard.json")
    rows = read_csv_rows("outputs/step28_step27_regression_guard/step27_regression_guard.csv")
    assert int(summary["row_count"]) == 7
    assert int(summary["pass_count"]) == 7
    assert int(summary["step27_driver_row_count"]) == 6
    assert int(summary["step27_stable_count"]) == 6
    assert int(summary["step27_quality_report_count"]) == 6
    assert int(summary["step27_quality_pass_count"]) == 6
    assert int(summary["step27_large_file_count"]) == 0
    assert all(as_bool(row["pass"]) for row in rows)


def test_step28_default_modes_remain_unchanged():
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


def test_step28_docs_scope_and_forbidden_claims_are_valid():
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
            "docs/28_controlled_real_geometry_64_transfer_diagnostics.md",
            "STEP28_CONTROLLED_REAL_GEOMETRY_64_TRANSFER_DIAGNOSTICS_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step28_artifact_budget_is_valid():
    summary = read_json("outputs/step28_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step28_total_size_mb"]) < 15.0
    assert float(summary["total_size_mb"]) < 165.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["step28_vtr_count"]) == 0
    assert int(summary["step28_particle_npy_count"]) == 0
    assert int(summary["step28_quality_report_count"]) == 4
    assert int(summary["private_absolute_path_count"]) == 0
    manifest_rows = read_csv_rows("outputs/step28_artifact_manifest/artifact_manifest.csv")
    step28_paths = [row["path"] for row in manifest_rows if row["path"].startswith("outputs/step28")]
    assert not [path for path in step28_paths if path.endswith(".vtr")]
    assert not [path for path in step28_paths if path.endswith(".npy") and "particle" in path.lower()]


def test_step28_report_acceptance_complete():
    report = read_text("STEP28_CONTROLLED_REAL_GEOMETRY_64_TRANSFER_DIAGNOSTICS_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Candidate Fingerprint Guard",
        "## 5. 64^3 Transfer Pair Driver",
        "## 6. Engineering Vs Link-Area Comparison",
        "## 7. Force And Reaction Diagnostics",
        "## 8. Area-Scale Envelope",
        "## 9. Step 27 Prefix Regression",
        "## 10. Quality Report Aggregation",
        "## 11. Step 27 Regression Guard",
        "## 12. Artifact Manifest Summary",
        "## 13. Verification Commands",
        "## 14. GitHub Sync Information",
        "## 15. Acceptance Checklist",
        "## 16. Decision For Step 29",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] candidate fingerprint guard passes",
        "- [x] Step 25 manifest fingerprints match current candidate files",
        "- [x] Step 26 generated GeometryConfig files remain valid",
        "- [x] mesh 64^3 moving_boundary engineering 10-step row passes",
        "- [x] mesh 64^3 moving_boundary link_area 10-step row passes",
        "- [x] voxel 64^3 moving_boundary engineering 10-step row passes",
        "- [x] voxel 64^3 moving_boundary link_area 10-step row passes",
        "- [x] every Step 28 driver row writes geometry_quality_report.json",
        "- [x] every Step 28 quality gate is strict",
        "- [x] every Step 28 quality report passes",
        "- [x] quality warning count == 0",
        "- [x] quality error count == 0",
        "- [x] all driver rows have completed_lbm_steps >= 10",
        "- [x] all driver rows have total_mpm_substeps >= 50",
        "- [x] rho_min > 0.95",
        "- [x] rho_max < 1.05",
        "- [x] lbm_max_v < 0.1",
        "- [x] mpm_min_J > 0",
        "- [x] mpm_max_speed < 10",
        "- [x] projected_mass > 0",
        "- [x] active_cell_count > 0",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] moving_boundary rows keep cell_force_max_norm == 0",
        "- [x] moving_boundary rows have bb_link_count > 0",
        "- [x] moving_boundary rows have active_reaction_particle_count_max > 0",
        "- [x] hydro_force_max_norm is finite and positive after nonzero steps",
        "- [x] max_grid_reaction_norm is finite",
        "- [x] engineering vs link_area comparison passes for mesh",
        "- [x] engineering vs link_area comparison passes for voxel",
        "- [x] link_area rows have finite bounded area_scale",
        "- [x] area_scale envelope summary passes",
        "- [x] Step 27 prefix regression passes at step=5",
        "- [x] Step 27 regression guard passes",
        "- [x] default quality_check_enabled remains false",
        "- [x] default quality_check_strict remains false",
        "- [x] default reaction_transfer_mode remains engineering",
        "- [x] no FSI formula changes",
        "- [x] no moving bounce-back formula changes",
        "- [x] no LBM formula changes",
        "- [x] no MPM constitutive formula changes",
        "- [x] no projection formula changes",
        "- [x] no production mesh repair claims",
        "- [x] no automatic remeshing claims",
        "- [x] no real squid validation claims",
        "- [x] no squid swimming claims",
        "- [x] no squid actuation claims",
        "- [x] no production sharp-interface FSI claims",
        "- [x] no final readiness claims",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] no committed large raw real geometry",
        "- [x] no committed scan data",
        "- [x] no private absolute paths in committed outputs",
        "- [x] no Step 28 .vtr outputs",
        "- [x] no Step 28 particle .npy outputs",
        "- [x] artifact large_file_count == 0",
        "- [x] Step 28 output total size budget passes",
        "- [x] repo artifact_summary total_size_mb < 165",
        "- [x] logs/step28_pytest.log exists",
        "- [x] pytest -q passes",
        "- [x] Step 28 contract test passes",
        "- [x] git diff --check passes",
        "- [x] staged whitespace check passes",
        "- [x] pre-push hook passes",
        "- [x] Step 28 artifacts are pushed to origin/main",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []

    assert (ROOT / "logs/step28_pytest.log").is_file()
    for path, marker in STEP28_LOG_MARKERS.items():
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


def assert_transfer_driver_row(row):
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
    assert int(float(row["n_lbm_steps"])) == 10
    assert int(float(row["mpm_substeps_per_lbm_step"])) == 5
    assert int(float(row["completed_lbm_steps"])) >= 10
    assert int(float(row["total_mpm_substeps"])) >= 50
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
    assert row["mode"] == "moving_boundary"
    assert float(row["cell_force_max_norm"]) == 0.0
    assert float(row["hydro_force_max_norm"]) > 0.0
    assert int(float(row["bb_link_count_min"])) > 0
    assert int(float(row["bb_link_count_max"])) > 0
    assert int(float(row["active_reaction_particle_count_max"])) > 0
    if row["reaction_transfer_mode"] == "link_area_experimental":
        assert 0.25 <= float(row["area_scale_final"]) <= 2.0
        assert 0.25 <= float(row["area_scale_min"]) <= float(row["area_scale_max"]) <= 2.0
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
