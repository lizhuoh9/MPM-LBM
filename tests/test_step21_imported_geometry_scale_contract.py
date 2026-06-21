import csv
import json
import math
from pathlib import Path


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


def read_json(relative_path):
    return json.loads(read_text(relative_path))


def read_csv_rows(relative_path):
    with (ROOT / relative_path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def as_float(row, key):
    return float(row[key])


def as_int(row, key):
    return int(float(row[key]))


def assert_finite_row(row, excluded=()):
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        assert math.isfinite(float(value)), f"{key} is not finite"


def assert_stable_driver_row(row):
    assert_finite_row(
        row,
        excluded=("case", "geometry_type", "geometry_source", "mode", "reaction_transfer_mode", "stable", "notes"),
    )
    assert as_bool(row["stable"])
    assert as_float(row, "rho_min") > 0.95
    assert as_float(row, "rho_max") < 1.05
    assert as_float(row, "lbm_max_v") < 0.1
    assert as_float(row, "mpm_min_J") > 0.0
    assert as_float(row, "mpm_max_speed") < 10.0
    assert as_float(row, "projected_mass") > 0.0
    assert as_int(row, "active_cell_count") > 0

    if row["mode"] == "none":
        assert as_float(row, "cell_force_max_norm") == 0.0
    if row["mode"] == "penalty":
        assert as_float(row, "cell_force_max_norm") > 0.0
    if row["mode"] == "moving_boundary":
        assert as_float(row, "cell_force_max_norm") == 0.0
        assert as_int(row, "bb_link_count") > 0
        assert as_float(row, "hydro_force_max_norm") > 0.0
    if row["reaction_transfer_mode"] == "link_area_experimental":
        assert math.isfinite(as_float(row, "area_scale_final"))


def test_step21_required_artifacts_exist():
    required_paths = [
        "configs/step21_voxel_sphere_48_none.json",
        "configs/step21_voxel_sphere_48_penalty.json",
        "configs/step21_voxel_sphere_48_moving_boundary.json",
        "configs/step21_voxel_sphere_48_link_area.json",
        "configs/step21_mesh_cube_48_none.json",
        "configs/step21_mesh_cube_48_penalty.json",
        "configs/step21_mesh_cube_48_moving_boundary.json",
        "configs/step21_mesh_cube_48_link_area.json",
        "configs/step21_mesh_ellipsoid_48_none.json",
        "configs/step21_mesh_ellipsoid_48_penalty.json",
        "configs/step21_mesh_ellipsoid_48_moving_boundary.json",
        "configs/step21_mesh_ellipsoid_48_link_area.json",
        "configs/step21_voxel_sphere_64_penalty.json",
        "configs/step21_voxel_sphere_64_moving_boundary.json",
        "configs/step21_mesh_cube_64_penalty.json",
        "baseline_tests/step21_common.py",
        "baseline_tests/run_step21_voxel_sphere_48_modes.py",
        "baseline_tests/run_step21_mesh_cube_48_modes.py",
        "baseline_tests/run_step21_mesh_ellipsoid_48_modes.py",
        "baseline_tests/run_step21_imported_geometry_64_feasibility.py",
        "baseline_tests/run_step21_imported_geometry_projection_quality.py",
        "baseline_tests/run_step21_imported_geometry_scale_summary.py",
        "baseline_tests/run_step21_artifact_manifest.py",
        "docs/20_imported_geometry_scale_validation.md",
        "STEP21_IMPORTED_GEOMETRY_SCALE_REPORT.md",
    ]
    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step21_config_matrix_matches_contract():
    config_expectations = {
        "configs/step21_voxel_sphere_48_none.json": ("voxel_sphere", "voxel", "none", "engineering", 48, 10, 10),
        "configs/step21_voxel_sphere_48_penalty.json": ("voxel_sphere", "voxel", "penalty", "engineering", 48, 10, 10),
        "configs/step21_voxel_sphere_48_moving_boundary.json": (
            "voxel_sphere",
            "voxel",
            "moving_boundary",
            "engineering",
            48,
            10,
            10,
        ),
        "configs/step21_voxel_sphere_48_link_area.json": (
            "voxel_sphere",
            "voxel",
            "moving_boundary",
            "link_area_experimental",
            48,
            10,
            10,
        ),
        "configs/step21_mesh_cube_48_none.json": ("mesh_cube", "mesh", "none", "engineering", 48, 10, 10),
        "configs/step21_mesh_cube_48_penalty.json": ("mesh_cube", "mesh", "penalty", "engineering", 48, 10, 10),
        "configs/step21_mesh_cube_48_moving_boundary.json": (
            "mesh_cube",
            "mesh",
            "moving_boundary",
            "engineering",
            48,
            10,
            10,
        ),
        "configs/step21_mesh_cube_48_link_area.json": (
            "mesh_cube",
            "mesh",
            "moving_boundary",
            "link_area_experimental",
            48,
            10,
            10,
        ),
        "configs/step21_mesh_ellipsoid_48_none.json": (
            "mesh_ellipsoid",
            "mesh",
            "none",
            "engineering",
            48,
            10,
            10,
        ),
        "configs/step21_mesh_ellipsoid_48_penalty.json": (
            "mesh_ellipsoid",
            "mesh",
            "penalty",
            "engineering",
            48,
            10,
            10,
        ),
        "configs/step21_mesh_ellipsoid_48_moving_boundary.json": (
            "mesh_ellipsoid",
            "mesh",
            "moving_boundary",
            "engineering",
            48,
            10,
            10,
        ),
        "configs/step21_mesh_ellipsoid_48_link_area.json": (
            "mesh_ellipsoid",
            "mesh",
            "moving_boundary",
            "link_area_experimental",
            48,
            10,
            10,
        ),
        "configs/step21_voxel_sphere_64_penalty.json": (
            "voxel_sphere",
            "voxel",
            "penalty",
            "engineering",
            64,
            5,
            5,
        ),
        "configs/step21_voxel_sphere_64_moving_boundary.json": (
            "voxel_sphere",
            "voxel",
            "moving_boundary",
            "engineering",
            64,
            5,
            5,
        ),
        "configs/step21_mesh_cube_64_penalty.json": ("mesh_cube", "mesh", "penalty", "engineering", 64, 5, 5),
    }

    for path, (case, geometry_type, mode, transfer, n_grid, steps, substeps) in config_expectations.items():
        data = read_json(path)
        assert data["coupling_mode"] == mode
        assert data["geometry_type"] == geometry_type
        assert data["reaction_transfer_mode"] == transfer
        assert int(data["n_grid"]) == n_grid
        assert int(data["n_particles"]) == 4096
        assert int(data["n_lbm_steps"]) == steps
        assert int(data["mpm_substeps_per_lbm_step"]) == substeps
        assert data["write_vtk"] is False
        assert data["write_particles"] is False
        if case == "voxel_sphere":
            assert data["geometry_config_path"] == "configs/step20_voxel_sphere_geometry.json"
        if case == "mesh_cube":
            assert data["geometry_config_path"] == "configs/step20_mesh_cube_geometry.json"
        if case == "mesh_ellipsoid":
            assert data["geometry_config_path"] == "configs/step20_mesh_ellipsoid_geometry.json"


def test_step21_source_contract_and_frozen_defaults():
    fsi_config = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    coupling_sources = "\n".join(
        read_text(path)
        for path in [
            "src/coupling.py",
            "src/moving_boundary_coupling.py",
            "src/mpm_lbm/sim/coupling/link_area.py",
        ]
    )

    assert 'reaction_transfer_mode: str = "engineering"' in fsi_config
    assert 'reaction_transfer_mode == "link_area_experimental"' in fsi_config
    assert 'coupling_mode != "moving_boundary"' in fsi_config

    forbidden_step21_tokens = [
        "Step 21 changes coupling formula",
        "real squid simulation is validated",
        "production mesh repair is complete",
    ]
    offenders = [token for token in forbidden_step21_tokens if token in coupling_sources]
    assert offenders == []


def test_step21_logs_record_success_markers():
    expected_markers = {
        "logs/step21_voxel_sphere_48_modes.log": "[OK] Step 21 voxel_sphere 48 modes finished",
        "logs/step21_mesh_cube_48_modes.log": "[OK] Step 21 mesh_cube 48 modes finished",
        "logs/step21_mesh_ellipsoid_48_modes.log": "[OK] Step 21 mesh_ellipsoid 48 modes finished",
        "logs/step21_imported_geometry_64_feasibility.log": "[OK] Step 21 imported geometry 64 feasibility finished",
        "logs/step21_imported_geometry_projection_quality.log": "[OK] Step 21 imported geometry projection quality finished",
        "logs/step21_imported_geometry_scale_summary.log": "[OK] Step 21 imported geometry scale summary finished",
        "logs/step21_artifact_manifest.log": "[OK] Step 21 artifact manifest finished",
    }
    missing = []
    for path, marker in expected_markers.items():
        if not (ROOT / path).is_file() or marker not in read_log(path):
            missing.append(f"{path}: {marker}")
    assert missing == []


def test_step21_48_mode_outputs_are_valid():
    outputs = {
        "outputs/step21_voxel_sphere_48_modes/voxel_sphere_48_results.csv": {
            ("voxel_sphere", "none", "engineering"),
            ("voxel_sphere", "penalty", "engineering"),
            ("voxel_sphere", "moving_boundary", "engineering"),
            ("voxel_sphere", "moving_boundary", "link_area_experimental"),
        },
        "outputs/step21_mesh_cube_48_modes/mesh_cube_48_results.csv": {
            ("mesh_cube", "none", "engineering"),
            ("mesh_cube", "penalty", "engineering"),
            ("mesh_cube", "moving_boundary", "engineering"),
            ("mesh_cube", "moving_boundary", "link_area_experimental"),
        },
        "outputs/step21_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_results.csv": {
            ("mesh_ellipsoid", "none", "engineering"),
            ("mesh_ellipsoid", "penalty", "engineering"),
            ("mesh_ellipsoid", "moving_boundary", "engineering"),
            ("mesh_ellipsoid", "moving_boundary", "link_area_experimental"),
        },
    }

    for path, expected_rows in outputs.items():
        rows = read_csv_rows(path)
        keys = {(row["case"], row["mode"], row["reaction_transfer_mode"]) for row in rows}
        assert expected_rows.issubset(keys)
        for row in rows:
            assert as_int(row, "n_grid") == 48
            assert as_int(row, "n_particles") == 4096
            assert as_int(row, "completed_lbm_steps") == 10
            assert_stable_driver_row(row)


def test_step21_64_feasibility_output_is_valid():
    rows = read_csv_rows("outputs/step21_imported_geometry_64_feasibility/imported_geometry_64_results.csv")
    required = {
        ("voxel_sphere", "penalty", "engineering"),
        ("voxel_sphere", "moving_boundary", "engineering"),
        ("mesh_cube", "penalty", "engineering"),
    }
    keys = {(row["case"], row["mode"], row["reaction_transfer_mode"]) for row in rows}
    assert required.issubset(keys)
    for row in rows:
        if (row["case"], row["mode"], row["reaction_transfer_mode"]) in required:
            assert as_int(row, "n_grid") == 64
            assert as_int(row, "n_particles") == 4096
            assert as_int(row, "completed_lbm_steps") == 5
            assert_stable_driver_row(row)


def test_step21_projection_quality_output_is_valid():
    rows = read_csv_rows("outputs/step21_imported_geometry_projection_quality/projection_quality.csv")
    expected = {"voxel_sphere", "mesh_cube", "mesh_ellipsoid"}
    assert expected.issubset({row["case"] for row in rows})
    for row in rows:
        assert_finite_row(row, excluded=("case", "geometry_type", "stable", "notes"))
        assert as_bool(row["stable"])
        assert as_int(row, "particle_count") == 4096
        assert as_float(row, "geometry_volume") > 0.0
        assert as_float(row, "particle_mass_sum") > 0.0
        assert as_float(row, "projected_mass") > 0.0
        assert abs(as_float(row, "relative_mass_error")) < 1.0e-4
        assert as_int(row, "active_cell_count") > 0
        assert as_float(row, "solid_phi_min") >= 0.0
        assert as_float(row, "solid_phi_max") <= 1.0
        assert as_float(row, "particle_bounds_min_x") >= 0.0
        assert as_float(row, "particle_bounds_min_y") >= 0.0
        assert as_float(row, "particle_bounds_min_z") >= 0.0
        assert as_float(row, "particle_bounds_max_x") <= 1.0
        assert as_float(row, "particle_bounds_max_y") <= 1.0
        assert as_float(row, "particle_bounds_max_z") <= 1.0


def test_step21_summary_and_artifact_manifest_are_valid():
    summary = read_json("outputs/step21_imported_geometry_scale_summary/step21_summary.json")
    assert summary["stable"] is True
    assert int(summary["required_row_count"]) >= 18
    assert float(summary["rho_min_global"]) > 0.95
    assert float(summary["rho_max_global"]) < 1.05
    assert float(summary["lbm_max_v_global"]) < 0.1
    assert float(summary["mpm_min_J_global"]) > 0.0
    assert int(summary["projection_quality_row_count"]) >= 3

    artifact_summary = read_json("outputs/step21_artifact_manifest/artifact_summary.json")
    assert int(artifact_summary["file_count"]) > 0
    assert int(artifact_summary["total_size_bytes"]) > 0
    assert float(artifact_summary["total_size_mb"]) > 0.0
    assert int(artifact_summary["large_file_count"]) == 0
    assert (ROOT / "logs/step21_pytest.log").is_file()


def test_step21_docs_report_scope_and_avoid_overclaims():
    doc_paths = [
        "README.md",
        "docs/08_roadmap.md",
        "docs/09_api_reference.md",
        "docs/10_performance_memory.md",
        "docs/12_geometry_ingestion.md",
        "docs/19_geometry_import_pipeline.md",
        "docs/20_imported_geometry_scale_validation.md",
        "STEP21_IMPORTED_GEOMETRY_SCALE_REPORT.md",
    ]
    combined = "\n".join(read_text(path) for path in doc_paths if (ROOT / path).is_file())
    required_scope = [
        "Step 21 carries Step 20 synthetic imported voxel and mesh geometries to 48^3 mode validation and 64^3 feasibility.",
        "Step 21 is synthetic imported geometry scale validation, not real squid validation.",
        "The default reaction_transfer_mode remains engineering.",
        "The moving bounce-back formula is unchanged.",
        "PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.",
        "Imported geometry remains limited to small synthetic voxel and mesh fixtures.",
        "The Step 21 mesh path is not production mesh repair.",
    ]
    missing = [phrase for phrase in required_scope if phrase not in combined]
    assert missing == []

    forbidden_claims = [
        "real squid simulation is validated",
        "validated squid swimming",
        "production mesh repair is complete",
        "production-ready mesh import",
        "production-ready sharp-interface FSI",
        "strict momentum-conserving FSI is complete",
    ]
    offenders = [claim for claim in forbidden_claims if claim in combined]
    assert offenders == []


def test_step21_report_acceptance_complete():
    report = read_text("STEP21_IMPORTED_GEOMETRY_SCALE_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Config Matrix",
        "## 5. 48^3 Voxel_Sphere Mode Validation",
        "## 6. 48^3 Mesh_Cube Mode Validation",
        "## 7. 48^3 Mesh_Ellipsoid Mode Validation",
        "## 8. 64^3 Imported Geometry Feasibility",
        "## 9. Projection Quality Diagnostics",
        "## 10. Scale Summary",
        "## 11. Artifact Manifest Summary",
        "## 12. Verification Commands",
        "## 13. GitHub Sync Information",
        "## 14. Acceptance Checklist",
        "## 15. Decision For Step 22",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] voxel_sphere 48^3 modes baseline passes",
        "- [x] mesh_cube 48^3 modes baseline passes",
        "- [x] mesh_ellipsoid 48^3 modes baseline passes",
        "- [x] imported geometry 64^3 feasibility passes",
        "- [x] imported geometry projection quality passes",
        "- [x] no FSI formula changes",
        "- [x] default reaction_transfer_mode remains engineering",
        "- [x] no real squid validation claims",
        "- [x] no production mesh repair claims",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] artifact large_file_count == 0",
        "- [x] logs/step21_pytest.log exists",
        "- [x] pytest -q passes",
        "- [x] Git pre-push pytest hook passes",
        "- [x] git diff --check passes",
        "- [x] Step 21 artifacts are pushed to GitHub origin/main",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []
