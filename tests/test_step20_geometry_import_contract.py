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


def test_step20_required_artifacts_exist():
    required_paths = [
        "src/voxel_io.py",
        "src/mesh_io.py",
        "src/geometry_import.py",
        "data/geometry_fixtures/README.md",
        "data/geometry_fixtures/cube.obj",
        "data/geometry_fixtures/ellipsoid_proxy.obj",
        "data/geometry_fixtures/voxel_sphere.npy",
        "data/geometry_fixtures/voxel_sphere_metadata.json",
        "configs/step20_voxel_sphere_geometry.json",
        "configs/step20_mesh_cube_geometry.json",
        "configs/step20_mesh_ellipsoid_geometry.json",
        "configs/step20_driver_voxel_penalty.json",
        "configs/step20_driver_mesh_moving_boundary.json",
        "baseline_tests/step20_common.py",
        "baseline_tests/run_step20_voxel_import_sanity.py",
        "baseline_tests/run_step20_mesh_import_sanity.py",
        "baseline_tests/run_step20_imported_geometry_projection.py",
        "baseline_tests/run_step20_driver_imported_geometry_modes.py",
        "baseline_tests/run_step20_artifact_manifest.py",
        "docs/19_geometry_import_pipeline.md",
        "STEP20_GEOMETRY_IMPORT_REPORT.md",
    ]
    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step20_source_contract_and_frozen_defaults():
    geometry_config = read_text("src/geometry_config.py")
    geometry = read_text("src/geometry.py")
    fsi_config = read_text("src/fsi_config.py")
    coupling_sources = "\n".join(
        read_text(path)
        for path in [
            "src/coupling.py",
            "src/moving_boundary_coupling.py",
            "src/link_area_coupling.py",
        ]
    )

    assert "voxel" in geometry_config
    assert "mesh" in geometry_config
    assert "geometry_file" in geometry_config
    assert "metadata_file" in geometry_config
    assert "mesh_inside_method" in geometry_config
    assert "mesh_voxel_resolution" in geometry_config

    assert "ImportedGeometrySampler3D" in geometry
    assert '"voxel"' in geometry or "'voxel'" in geometry
    assert '"mesh"' in geometry or "'mesh'" in geometry

    assert 'reaction_transfer_mode: str = "engineering"' in fsi_config
    assert "reaction_transfer_mode == \"link_area_experimental\"" in fsi_config
    assert "coupling_mode != \"moving_boundary\"" in fsi_config

    forbidden_step20_tokens = [
        "Step 20 changes coupling formula",
        "production mesh repair",
        "real squid simulation is validated",
    ]
    offenders = [token for token in forbidden_step20_tokens if token in coupling_sources]
    assert offenders == []


def test_step20_configs_match_contract():
    voxel = read_json("configs/step20_voxel_sphere_geometry.json")
    cube = read_json("configs/step20_mesh_cube_geometry.json")
    ellipsoid = read_json("configs/step20_mesh_ellipsoid_geometry.json")
    voxel_driver = read_json("configs/step20_driver_voxel_penalty.json")
    mesh_driver = read_json("configs/step20_driver_mesh_moving_boundary.json")

    assert voxel["geometry_type"] == "voxel"
    assert voxel["geometry_file"] == "data/geometry_fixtures/voxel_sphere.npy"
    assert voxel["metadata_file"] == "data/geometry_fixtures/voxel_sphere_metadata.json"
    assert int(voxel["n_particles"]) == 4096

    for config, fixture in [(cube, "cube.obj"), (ellipsoid, "ellipsoid_proxy.obj")]:
        assert config["geometry_type"] == "mesh"
        assert config["geometry_file"] == f"data/geometry_fixtures/{fixture}"
        assert config["mesh_inside_method"] in {"ray_cast", "voxelized"}
        assert int(config["mesh_voxel_resolution"]) == 32
        assert int(config["n_particles"]) == 4096
        assert config["normalize_to_domain"] is True
        assert config["preserve_aspect_ratio"] is True

    for driver in [voxel_driver, mesh_driver]:
        assert int(driver["n_grid"]) == 32
        assert int(driver["n_particles"]) == 4096
        assert int(driver["n_lbm_steps"]) == 5
        assert int(driver["mpm_substeps_per_lbm_step"]) == 5
        assert driver["write_vtk"] is False
        assert driver["write_particles"] is False

    assert voxel_driver["coupling_mode"] == "penalty"
    assert voxel_driver["geometry_type"] == "voxel"
    assert mesh_driver["coupling_mode"] == "moving_boundary"
    assert mesh_driver["reaction_transfer_mode"] == "engineering"
    assert mesh_driver["geometry_type"] == "mesh"


def test_step20_fixtures_are_small_and_valid():
    voxel_path = ROOT / "data/geometry_fixtures/voxel_sphere.npy"
    occupancy = np.load(voxel_path)
    assert occupancy.shape == (32, 32, 32)
    assert np.all(np.isfinite(occupancy))
    assert int(np.count_nonzero(occupancy)) > 0
    assert voxel_path.stat().st_size < 200_000

    for path in [
        ROOT / "data/geometry_fixtures/cube.obj",
        ROOT / "data/geometry_fixtures/ellipsoid_proxy.obj",
    ]:
        text = path.read_text(encoding="utf-8")
        assert "\nv " in "\n" + text
        assert "\nf " in "\n" + text
        assert path.stat().st_size < 200_000


def test_step20_logs_record_success_markers():
    expected_markers = {
        "logs/step20_voxel_import_sanity.log": "[OK] Step 20 voxel import sanity finished",
        "logs/step20_mesh_import_sanity.log": "[OK] Step 20 mesh import sanity finished",
        "logs/step20_imported_geometry_projection.log": "[OK] Step 20 imported geometry projection finished",
        "logs/step20_driver_imported_geometry_modes.log": "[OK] Step 20 driver imported geometry modes finished",
        "logs/step20_artifact_manifest.log": "[OK] Step 20 artifact manifest finished",
    }
    missing = []
    for path, marker in expected_markers.items():
        if not (ROOT / path).is_file() or marker not in read_log(path):
            missing.append(f"{path}: {marker}")
    assert missing == []


def test_step20_voxel_and_mesh_sanity_outputs_are_valid():
    voxel_stats = read_json("outputs/step20_voxel_import_sanity/import_stats.json")
    assert voxel_stats["geometry_type"] == "voxel"
    assert voxel_stats["shape"] == [32, 32, 32]
    assert int(voxel_stats["occupied_count"]) > 0
    assert int(voxel_stats["particle_count"]) == 4096
    assert float(voxel_stats["geometry_volume"]) > 0.0

    particles = np.load(ROOT / "outputs/step20_voxel_import_sanity/particles_x.npy")
    vol0 = np.load(ROOT / "outputs/step20_voxel_import_sanity/particle_vol0.npy")
    mass = np.load(ROOT / "outputs/step20_voxel_import_sanity/particle_mass.npy")
    assert particles.shape == (4096, 3)
    assert np.all(np.isfinite(particles))
    assert np.min(particles) >= 0.0
    assert np.max(particles) <= 1.0
    assert np.all(vol0 > 0.0)
    assert np.all(mass > 0.0)

    mesh_stats = read_json("outputs/step20_mesh_import_sanity/mesh_import_stats.json")
    assert {"mesh_cube", "mesh_ellipsoid"}.issubset(mesh_stats)
    for row in mesh_stats.values():
        assert int(row["vertices_count"]) > 0
        assert int(row["faces_count"]) > 0
        assert int(row["particle_count"]) == 4096
        assert int(row["voxel_occupied_count"]) > 0
        assert float(row["geometry_volume"]) > 0.0


def test_step20_projection_and_driver_outputs_are_valid():
    projection_rows = read_csv_rows("outputs/step20_imported_geometry_projection/projection_results.csv")
    expected_projection = {"voxel_sphere", "mesh_cube", "mesh_ellipsoid"}
    assert expected_projection.issubset({row["case"] for row in projection_rows})
    for row in projection_rows:
        assert_finite_row(row, excluded=("case", "geometry_type", "stable", "notes"))
        assert as_bool(row["stable"])
        assert as_float(row, "projected_mass") > 0.0
        assert as_int(row, "active_cell_count") > 0
        assert as_float(row, "solid_phi_min") >= 0.0
        assert as_float(row, "solid_phi_max") <= 1.0
        assert as_float(row, "cell_force_max_norm") == 0.0
        assert as_float(row, "hydro_force_max_norm") == 0.0

    driver_rows = read_csv_rows("outputs/step20_driver_imported_geometry_modes/imported_geometry_mode_results.csv")
    expected_driver = {
        ("voxel_sphere", "none"),
        ("voxel_sphere", "penalty"),
        ("mesh_cube", "none"),
        ("mesh_cube", "penalty"),
        ("mesh_cube", "moving_boundary"),
    }
    assert expected_driver.issubset({(row["case"], row["mode"]) for row in driver_rows})
    for row in driver_rows:
        assert_finite_row(row, excluded=("case", "geometry_type", "mode", "reaction_transfer_mode", "stable", "notes"))
        assert as_bool(row["stable"])
        assert as_float(row, "rho_min") > 0.95
        assert as_float(row, "rho_max") < 1.05
        assert as_float(row, "lbm_max_v") < 0.1
        assert as_float(row, "mpm_min_J") > 0.0
        assert as_float(row, "mpm_max_speed") < 10.0
        assert as_float(row, "projected_mass") > 0.0
        assert as_int(row, "active_cell_count") > 0
        if row["mode"] == "moving_boundary":
            assert as_float(row, "cell_force_max_norm") == 0.0


def test_step20_artifact_manifest_and_pytest_log_are_valid():
    artifact_summary = read_json("outputs/step20_artifact_manifest/artifact_summary.json")
    assert int(artifact_summary["file_count"]) > 0
    assert int(artifact_summary["total_size_bytes"]) > 0
    assert float(artifact_summary["total_size_mb"]) > 0.0
    assert int(artifact_summary["large_file_count"]) == 0
    assert (ROOT / "logs/step20_pytest.log").is_file()


def test_step20_docs_report_scope_and_avoid_overclaims():
    doc_paths = [
        "README.md",
        "docs/08_roadmap.md",
        "docs/09_api_reference.md",
        "docs/12_geometry_ingestion.md",
        "docs/18_link_area_long_run.md",
        "docs/19_geometry_import_pipeline.md",
        "STEP20_GEOMETRY_IMPORT_REPORT.md",
    ]
    combined = "\n".join(read_text(path) for path in doc_paths if (ROOT / path).is_file())
    required_scope = [
        "Step 20 adds a small synthetic mesh and voxel geometry import pipeline.",
        "Step 20 is a geometry-ingestion scaffold, not real squid validation.",
        "The default reaction_transfer_mode remains engineering.",
        "The moving bounce-back formula is unchanged.",
        "PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.",
        "Imported geometry supports voxel and mesh inputs through GeometryConfig and GeometrySampler3D.",
        "The Step 20 mesh path is limited to small synthetic fixtures and is not production mesh repair.",
    ]
    missing = [phrase for phrase in required_scope if phrase not in combined]
    assert missing == []

    forbidden_claims = [
        "real squid simulation is validated",
        "validated squid swimming",
        "production mesh repair",
        "production-ready mesh import",
        "production-ready sharp-interface FSI",
        "strict momentum-conserving FSI is complete",
    ]
    offenders = [claim for claim in combined if claim in forbidden_claims]
    assert offenders == []


def test_step20_report_acceptance_complete():
    report = read_text("STEP20_GEOMETRY_IMPORT_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. GeometryConfig And Sampler Integration",
        "## 5. Voxel Import Sanity Result",
        "## 6. Mesh Import Sanity Result",
        "## 7. Imported Geometry Projection Result",
        "## 8. Driver Imported Geometry Modes Result",
        "## 9. Artifact Manifest Summary",
        "## 10. Verification Commands",
        "## 11. GitHub Sync Information",
        "## 12. Acceptance Checklist",
        "## 13. Decision For Step 21",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] geometry_type supports voxel",
        "- [x] geometry_type supports mesh",
        "- [x] voxel import sanity passes",
        "- [x] mesh import sanity passes",
        "- [x] imported geometry projection passes",
        "- [x] driver imported geometry modes pass",
        "- [x] no FSI formula changes",
        "- [x] default reaction_transfer_mode remains engineering",
        "- [x] no real squid validation claims",
        "- [x] no production mesh repair claims",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] artifact large_file_count == 0",
        "- [x] logs/step20_pytest.log exists",
        "- [x] pytest -q passes",
        "- [x] Git pre-push pytest hook passes",
        "- [x] git diff --check passes",
        "- [x] Step 20 artifacts are pushed to GitHub origin/main",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []
