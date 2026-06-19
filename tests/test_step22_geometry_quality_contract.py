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
        assert math.isfinite(float(value)), f"{key} is not finite in {row}"


def test_step22_required_artifacts_exist():
    required_paths = [
        "src/mesh_quality.py",
        "src/voxel_quality.py",
        "src/geometry_quality.py",
        "data/geometry_fixtures/bad_nonwatertight.obj",
        "data/geometry_fixtures/bad_degenerate.obj",
        "data/geometry_fixtures/bad_empty_voxel.npy",
        "data/geometry_fixtures/bad_empty_voxel_metadata.json",
        "configs/step22_quality_mesh_cube.json",
        "configs/step22_quality_mesh_ellipsoid.json",
        "configs/step22_quality_voxel_sphere.json",
        "configs/step22_quality_bad_nonwatertight.json",
        "configs/step22_quality_bad_degenerate.json",
        "configs/step22_quality_bad_empty_voxel.json",
        "configs/step22_resolution_sweep_voxel_sphere.json",
        "configs/step22_resolution_sweep_mesh_ellipsoid.json",
        "configs/step22_driver_quality_gate_voxel_penalty.json",
        "configs/step22_driver_quality_gate_mesh_moving_boundary.json",
        "baseline_tests/step22_common.py",
        "baseline_tests/run_step22_mesh_quality_sanity.py",
        "baseline_tests/run_step22_voxel_quality_sanity.py",
        "baseline_tests/run_step22_bad_geometry_failure_checks.py",
        "baseline_tests/run_step22_sampling_resolution_sensitivity.py",
        "baseline_tests/run_step22_driver_quality_gate_smoke.py",
        "baseline_tests/run_step22_artifact_manifest.py",
        "docs/21_geometry_quality_checks.md",
        "STEP22_GEOMETRY_QUALITY_REPORT.md",
    ]
    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    assert missing == []


def test_step22_geometry_config_defaults_and_exports():
    geometry_config = read_text("src/geometry_config.py")
    init_py = read_text("src/__init__.py")
    fsi_driver = read_text("src/fsi_driver.py")

    assert "quality_check_enabled: bool = False" in geometry_config
    assert "quality_check_strict: bool = False" in geometry_config
    assert "quality_report_path: Optional[str] = None" in geometry_config
    assert "analyze_geometry_config" in init_py
    assert "GeometryQualityGate" in init_py
    assert "geometry_quality_report.json" in fsi_driver
    assert "quality_check_enabled" in fsi_driver


def test_step22_config_contract():
    expected = {
        "configs/step22_quality_mesh_cube.json": ("mesh", "data/geometry_fixtures/cube.obj", False, False),
        "configs/step22_quality_mesh_ellipsoid.json": (
            "mesh",
            "data/geometry_fixtures/ellipsoid_proxy.obj",
            False,
            False,
        ),
        "configs/step22_quality_voxel_sphere.json": ("voxel", "data/geometry_fixtures/voxel_sphere.npy", False, False),
        "configs/step22_quality_bad_nonwatertight.json": (
            "mesh",
            "data/geometry_fixtures/bad_nonwatertight.obj",
            True,
            True,
        ),
        "configs/step22_quality_bad_degenerate.json": (
            "mesh",
            "data/geometry_fixtures/bad_degenerate.obj",
            True,
            True,
        ),
        "configs/step22_quality_bad_empty_voxel.json": (
            "voxel",
            "data/geometry_fixtures/bad_empty_voxel.npy",
            True,
            True,
        ),
    }

    for path, (geometry_type, geometry_file, enabled, strict) in expected.items():
        data = read_json(path)
        assert data["geometry_type"] == geometry_type
        assert data["geometry_file"] == geometry_file
        assert bool(data["quality_check_enabled"]) is enabled
        assert bool(data["quality_check_strict"]) is strict
        assert int(data["n_particles"]) == 4096

    for path in [
        "configs/step22_driver_quality_gate_voxel_penalty.json",
        "configs/step22_driver_quality_gate_mesh_moving_boundary.json",
    ]:
        data = read_json(path)
        assert data["quality_check_enabled"] is True
        assert data["quality_check_strict"] is False
        assert data["write_vtk"] is False
        assert data["write_particles"] is False
        assert int(data["n_grid"]) == 32
        assert int(data["n_lbm_steps"]) == 5


def test_step22_logs_record_success_markers():
    expected_markers = {
        "logs/step22_mesh_quality_sanity.log": "[OK] Step 22 mesh quality sanity finished",
        "logs/step22_voxel_quality_sanity.log": "[OK] Step 22 voxel quality sanity finished",
        "logs/step22_bad_geometry_failure_checks.log": "[OK] Step 22 bad geometry failure checks finished",
        "logs/step22_sampling_resolution_sensitivity.log": "[OK] Step 22 sampling resolution sensitivity finished",
        "logs/step22_driver_quality_gate_smoke.log": "[OK] Step 22 driver quality gate smoke finished",
        "logs/step22_artifact_manifest.log": "[OK] Step 22 artifact manifest finished",
    }
    missing = []
    for path, marker in expected_markers.items():
        if not (ROOT / path).is_file() or marker not in read_log(path):
            missing.append(f"{path}: {marker}")
    assert missing == []


def test_step22_mesh_quality_outputs_are_valid():
    rows = read_csv_rows("outputs/step22_mesh_quality_sanity/mesh_quality_results.csv")
    by_case = {row["case"]: row for row in rows}
    assert {"mesh_cube", "mesh_ellipsoid"}.issubset(by_case)

    cube = by_case["mesh_cube"]
    assert_finite_row(cube, excluded=("case", "geometry_type", "quality_kind", "pass", "severity", "stable", "notes"))
    assert as_int(cube, "vertices_count") == 8
    assert as_int(cube, "faces_count") == 12
    assert as_int(cube, "boundary_edge_count") == 0
    assert as_int(cube, "nonmanifold_edge_count") == 0
    assert as_int(cube, "degenerate_face_count") == 0
    assert as_bool(cube["is_watertight_proxy"])
    assert as_bool(cube["pass"])
    assert as_float(cube, "volume_abs") > 0.0

    ellipsoid = by_case["mesh_ellipsoid"]
    assert as_int(ellipsoid, "vertices_count") > 0
    assert as_int(ellipsoid, "faces_count") > 0
    assert as_int(ellipsoid, "degenerate_face_count") == 0
    assert as_float(ellipsoid, "volume_abs") > 0.0
    assert as_bool(ellipsoid["pass"])


def test_step22_voxel_quality_outputs_are_valid():
    rows = read_csv_rows("outputs/step22_voxel_quality_sanity/voxel_quality_results.csv")
    assert len(rows) >= 1
    row = rows[0]
    assert row["case"] == "voxel_sphere"
    assert_finite_row(row, excluded=("case", "geometry_type", "quality_kind", "empty", "pass", "severity", "stable", "notes"))
    assert not as_bool(row["empty"])
    assert as_int(row, "occupied_count") > 0
    assert as_int(row, "connected_component_count") >= 1
    assert as_float(row, "largest_component_fraction") > 0.95
    assert as_int(row, "surface_voxel_count") > 0
    assert as_int(row, "interior_voxel_count") > 0
    assert as_bool(row["pass"])


def test_step22_bad_geometry_failures_are_valid():
    rows = read_csv_rows("outputs/step22_bad_geometry_failure_checks/bad_geometry_results.csv")
    by_case = {row["case"]: row for row in rows}
    assert {"bad_nonwatertight", "bad_degenerate", "bad_empty_voxel"}.issubset(by_case)

    nonwatertight = by_case["bad_nonwatertight"]
    assert as_int(nonwatertight, "boundary_edge_count") > 0
    assert not as_bool(nonwatertight["strict_pass"])
    assert as_bool(nonwatertight["expected_failure"])

    degenerate = by_case["bad_degenerate"]
    assert as_int(degenerate, "degenerate_face_count") > 0
    assert not as_bool(degenerate["strict_pass"])
    assert as_bool(degenerate["expected_failure"])

    empty = by_case["bad_empty_voxel"]
    assert as_bool(empty["expected_failure"])
    assert not as_bool(empty["strict_pass"])
    assert as_int(empty, "occupied_count") == 0 or as_bool(empty["loader_expected_failure"])


def test_step22_resolution_sensitivity_outputs_are_valid():
    rows = read_csv_rows("outputs/step22_sampling_resolution_sensitivity/resolution_sensitivity.csv")
    assert len(rows) >= 6
    by_case = {}
    for row in rows:
        assert_finite_row(row, excluded=("case", "geometry_type", "stable", "notes"))
        assert as_bool(row["stable"])
        assert as_float(row, "geometry_volume") > 0.0
        assert as_float(row, "projected_mass") > 0.0
        assert math.isfinite(as_float(row, "relative_mass_error"))
        assert as_int(row, "active_cell_count") > 0
        by_case.setdefault(row["case"], []).append(as_float(row, "geometry_volume"))

    for case, volumes in by_case.items():
        ratio = max(volumes) / min(volumes)
        assert ratio < 2.0, f"{case} volume ratio too high: {ratio}"


def test_step22_driver_quality_gate_outputs_are_valid():
    rows = read_csv_rows("outputs/step22_driver_quality_gate_smoke/quality_gate_driver_results.csv")
    keys = {(row["case"], row["mode"]) for row in rows}
    assert ("voxel_sphere", "penalty") in keys
    assert ("mesh_cube", "moving_boundary") in keys
    for row in rows:
        assert_finite_row(
            row,
            excluded=(
                "case",
                "geometry_type",
                "geometry_source",
                "mode",
                "reaction_transfer_mode",
                "quality_gate_severity",
                "stable",
                "notes",
            ),
        )
        assert as_bool(row["stable"])
        assert as_bool(row["quality_gate_pass"])
        assert as_float(row, "rho_min") > 0.95
        assert as_float(row, "rho_max") < 1.05
        assert as_float(row, "lbm_max_v") < 0.1
        assert as_float(row, "mpm_min_J") > 0.0
        assert as_float(row, "projected_mass") > 0.0
        assert as_int(row, "active_cell_count") > 0

    expected_reports = [
        "outputs/step22_driver_quality_gate_smoke/voxel_sphere_penalty/geometry_quality_report.json",
        "outputs/step22_driver_quality_gate_smoke/mesh_cube_moving_boundary/geometry_quality_report.json",
    ]
    for path in expected_reports:
        report = read_json(path)
        assert report["gate"]["pass"] is True


def test_step22_docs_report_and_manifest_are_valid():
    artifact_summary = read_json("outputs/step22_artifact_manifest/artifact_summary.json")
    assert int(artifact_summary["file_count"]) > 0
    assert int(artifact_summary["total_size_bytes"]) > 0
    assert float(artifact_summary["total_size_mb"]) > 0.0
    assert int(artifact_summary["large_file_count"]) == 0
    assert (ROOT / "logs/step22_pytest.log").is_file()

    doc_paths = [
        "README.md",
        "docs/08_roadmap.md",
        "docs/09_api_reference.md",
        "docs/12_geometry_ingestion.md",
        "docs/19_geometry_import_pipeline.md",
        "docs/20_imported_geometry_scale_validation.md",
        "docs/21_geometry_quality_checks.md",
        "STEP22_GEOMETRY_QUALITY_REPORT.md",
    ]
    combined = "\n".join(read_text(path) for path in doc_paths)
    required_scope = [
        "Step 22 adds diagnostic quality checks for imported mesh and voxel geometry.",
        "Step 22 is a geometry QA and import robustness layer, not real squid validation.",
        "The default reaction_transfer_mode remains engineering.",
        "The moving bounce-back formula is unchanged.",
        "PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.",
        "Imported geometry remains limited to small synthetic voxel and mesh fixtures.",
        "The Step 22 mesh path is not production mesh repair or automatic remeshing.",
    ]
    missing = [phrase for phrase in required_scope if phrase not in combined]
    assert missing == []

    forbidden_claims = [
        "real squid simulation is validated",
        "validated squid swimming",
        "production mesh repair is complete",
        "automatic remeshing is implemented",
        "production-ready mesh import",
        "production-ready sharp-interface FSI",
        "strict momentum-conserving FSI is complete",
        "implements two_phase",
        "implements contact_angle",
    ]
    offenders = [claim for claim in forbidden_claims if claim in combined]
    assert offenders == []


def test_step22_report_acceptance_complete():
    report = read_text("STEP22_GEOMETRY_QUALITY_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Mesh Quality Sanity",
        "## 5. Voxel Quality Sanity",
        "## 6. Bad Geometry Failure Checks",
        "## 7. Sampling Resolution Sensitivity",
        "## 8. Driver Quality Gate Smoke",
        "## 9. Artifact Manifest Summary",
        "## 10. Verification Commands",
        "## 11. GitHub Sync Information",
        "## 12. Acceptance Checklist",
        "## 13. Decision For Step 23",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] mesh quality sanity passes",
        "- [x] voxel quality sanity passes",
        "- [x] bad geometry failure checks pass",
        "- [x] sampling resolution sensitivity passes",
        "- [x] driver quality gate smoke passes",
        "- [x] GeometryConfig quality_check_enabled defaults to false",
        "- [x] FSIDriver3D default behavior unchanged when quality_check_enabled is false",
        "- [x] no FSI formula changes",
        "- [x] default reaction_transfer_mode remains engineering",
        "- [x] no production mesh repair claims",
        "- [x] no automatic remeshing claims",
        "- [x] no real squid validation claims",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] artifact large_file_count == 0",
        "- [x] logs/step22_pytest.log exists",
        "- [x] pytest -q passes",
        "- [x] Git pre-push pytest hook passes",
        "- [x] git diff --check passes",
        "- [x] Step 22 artifacts are pushed to GitHub origin/main",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []
