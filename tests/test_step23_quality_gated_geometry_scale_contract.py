import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


STEP23_CONFIGS = [
    "configs/step23_quality_gated_voxel_sphere_48_none.json",
    "configs/step23_quality_gated_voxel_sphere_48_penalty.json",
    "configs/step23_quality_gated_voxel_sphere_48_moving_boundary.json",
    "configs/step23_quality_gated_voxel_sphere_48_link_area.json",
    "configs/step23_quality_gated_mesh_cube_48_none.json",
    "configs/step23_quality_gated_mesh_cube_48_penalty.json",
    "configs/step23_quality_gated_mesh_cube_48_moving_boundary.json",
    "configs/step23_quality_gated_mesh_cube_48_link_area.json",
    "configs/step23_quality_gated_mesh_ellipsoid_48_none.json",
    "configs/step23_quality_gated_mesh_ellipsoid_48_penalty.json",
    "configs/step23_quality_gated_mesh_ellipsoid_48_moving_boundary.json",
    "configs/step23_quality_gated_mesh_ellipsoid_48_link_area.json",
    "configs/step23_quality_gated_voxel_sphere_64_penalty.json",
    "configs/step23_quality_gated_voxel_sphere_64_moving_boundary.json",
    "configs/step23_quality_gated_mesh_cube_64_penalty.json",
]


STEP23_REQUIRED_DRIVER_OUTPUTS = {
    "outputs/step23_quality_gated_voxel_sphere_48_modes/voxel_sphere_48_quality_gated_results.csv": 4,
    "outputs/step23_quality_gated_mesh_cube_48_modes/mesh_cube_48_quality_gated_results.csv": 4,
    "outputs/step23_quality_gated_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_quality_gated_results.csv": 4,
    "outputs/step23_quality_gated_imported_geometry_64_feasibility/imported_geometry_64_quality_gated_results.csv": 3,
}


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


def test_step23_required_artifacts_exist():
    required_paths = [
        "baseline_tests/step23_common.py",
        "baseline_tests/run_step23_quality_gated_voxel_sphere_48_modes.py",
        "baseline_tests/run_step23_quality_gated_mesh_cube_48_modes.py",
        "baseline_tests/run_step23_quality_gated_mesh_ellipsoid_48_modes.py",
        "baseline_tests/run_step23_quality_gated_imported_geometry_64_feasibility.py",
        "baseline_tests/run_step23_quality_report_aggregation.py",
        "baseline_tests/run_step23_step21_vs_quality_gated_comparison.py",
        "baseline_tests/run_step23_artifact_manifest.py",
        "docs/22_quality_gated_imported_geometry_validation.md",
        "STEP23_QUALITY_GATED_GEOMETRY_SCALE_REPORT.md",
        "STEP23_QUALITY_GATED_GEOMETRY_SCALE_GOAL.md",
    ]
    missing = [path for path in required_paths + STEP23_CONFIGS if not (ROOT / path).is_file()]
    assert missing == []


def test_step23_config_contract():
    for path in STEP23_CONFIGS:
        data = read_json(path)
        assert data["quality_check_enabled"] is True
        assert data["quality_check_strict"] is False
        assert data["write_vtk"] is False
        assert data["write_particles"] is False
        assert data["geometry_type"] in {"voxel", "mesh"}
        assert data["reaction_transfer_mode"] in {"engineering", "link_area_experimental"}
        assert int(data["n_particles"]) == 4096

    for path in STEP23_CONFIGS[:12]:
        assert int(read_json(path)["n_grid"]) == 48
        assert int(read_json(path)["n_lbm_steps"]) >= 10

    for path in STEP23_CONFIGS[12:]:
        assert int(read_json(path)["n_grid"]) == 64
        assert int(read_json(path)["n_lbm_steps"]) >= 5


def test_step23_default_quality_gate_remains_disabled():
    geometry_config = read_text("src/mpm_lbm/sim/geometry/config.py")
    fsi_config = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    assert "quality_check_enabled: bool = False" in geometry_config
    assert "quality_check_strict: bool = False" in geometry_config
    assert "quality_check_enabled: bool = False" in fsi_config
    assert "quality_check_strict: bool = False" in fsi_config


def test_step23_logs_record_success_markers():
    expected_markers = {
        "logs/step23_quality_gated_voxel_sphere_48_modes.log": "[OK] Step 23 quality-gated voxel_sphere 48 modes finished",
        "logs/step23_quality_gated_mesh_cube_48_modes.log": "[OK] Step 23 quality-gated mesh_cube 48 modes finished",
        "logs/step23_quality_gated_mesh_ellipsoid_48_modes.log": "[OK] Step 23 quality-gated mesh_ellipsoid 48 modes finished",
        "logs/step23_quality_gated_imported_geometry_64_feasibility.log": "[OK] Step 23 quality-gated imported geometry 64 feasibility finished",
        "logs/step23_quality_report_aggregation.log": "[OK] Step 23 quality report aggregation finished",
        "logs/step23_step21_vs_quality_gated_comparison.log": "[OK] Step 23 Step 21 vs quality-gated comparison finished",
        "logs/step23_artifact_manifest.log": "[OK] Step 23 artifact manifest finished",
    }
    missing = []
    for path, marker in expected_markers.items():
        if not (ROOT / path).is_file() or marker not in read_log(path):
            missing.append(f"{path}: {marker}")
    assert missing == []


def test_step23_quality_gated_driver_outputs_are_valid():
    total_rows = 0
    for csv_path, min_rows in STEP23_REQUIRED_DRIVER_OUTPUTS.items():
        rows = read_csv_rows(csv_path)
        assert len(rows) >= min_rows
        total_rows += len(rows)
        for row in rows:
            assert_finite_row(
                row,
                excluded=(
                    "case",
                    "geometry_type",
                    "geometry_source",
                    "quality_kind",
                    "mode",
                    "reaction_transfer_mode",
                    "quality_check_enabled",
                    "quality_check_strict",
                    "quality_pass",
                    "quality_severity",
                    "quality_report_path",
                    "stable",
                    "notes",
                ),
            )
            assert as_bool(row["stable"])
            assert as_bool(row["quality_check_enabled"])
            assert not as_bool(row["quality_check_strict"])
            assert as_bool(row["quality_pass"])
            assert row["quality_severity"] in {"ok", "warning"}
            assert as_float(row, "rho_min") > 0.95
            assert as_float(row, "rho_max") < 1.05
            assert as_float(row, "lbm_max_v") < 0.1
            assert as_float(row, "mpm_min_J") > 0.0
            assert as_float(row, "projected_mass") > 0.0
            assert as_int(row, "active_cell_count") > 0
            assert (ROOT / row["quality_report_path"]).is_file()

            if row["mode"] == "penalty":
                assert as_float(row, "cell_force_max_norm") > 0.0
            if row["mode"] == "moving_boundary":
                assert as_float(row, "cell_force_max_norm") == 0.0
                assert as_int(row, "bb_link_count") > 0

    assert total_rows >= 15


def test_step23_quality_report_aggregation_is_valid():
    rows = read_csv_rows("outputs/step23_quality_report_aggregation/quality_report_summary.csv")
    summary = read_json("outputs/step23_quality_report_aggregation/quality_report_summary.json")
    assert len(rows) >= 15
    assert int(summary["quality_report_count"]) >= 15
    assert int(summary["error_count"]) == 0
    assert int(summary["pass_count"]) == len(rows)

    for row in rows:
        assert row["severity"] in {"ok", "warning"}
        assert as_bool(row["pass"])
        assert as_int(row, "reasons_count") == 0
        if row["geometry_type"] == "mesh":
            assert as_int(row, "boundary_edge_count") == 0
            assert as_int(row, "degenerate_face_count") == 0
        if row["geometry_type"] == "voxel":
            assert as_int(row, "occupied_count") > 0
            assert as_int(row, "connected_component_count") >= 1


def test_step23_step21_comparison_is_valid():
    rows = read_csv_rows("outputs/step23_step21_vs_quality_gated_comparison/step21_vs_step23_comparison.csv")
    summary = read_json("outputs/step23_step21_vs_quality_gated_comparison/step21_vs_step23_comparison.json")
    assert len(rows) >= 15
    assert int(summary["required_comparable_row_count"]) >= 15
    assert int(summary["stable_both_count"]) == len(rows)

    for row in rows:
        assert_finite_row(row, excluded=("case", "mode", "reaction_transfer_mode", "stable_both", "notes"))
        assert as_bool(row["stable_both"])


def test_step23_docs_report_and_manifest_are_valid():
    artifact_summary = read_json("outputs/step23_artifact_manifest/artifact_summary.json")
    assert int(artifact_summary["file_count"]) > 0
    assert int(artifact_summary["total_size_bytes"]) > 0
    assert float(artifact_summary["total_size_mb"]) > 0.0
    assert int(artifact_summary["large_file_count"]) == 0
    assert (ROOT / "logs/step23_pytest.log").is_file()

    doc_paths = [
        "README.md",
        "docs/08_roadmap.md",
        "docs/09_api_reference.md",
        "docs/12_geometry_ingestion.md",
        "docs/19_geometry_import_pipeline.md",
        "docs/20_imported_geometry_scale_validation.md",
        "docs/21_geometry_quality_checks.md",
        "docs/22_quality_gated_imported_geometry_validation.md",
        "STEP23_QUALITY_GATED_GEOMETRY_SCALE_REPORT.md",
    ]
    combined = "\n".join(read_text(path) for path in doc_paths)
    required_scope = [
        "Step 23 repeats imported geometry scale validation with quality_check_enabled=true.",
        "Step 23 uses quality_check_strict=false for scale validation.",
        "Step 23 is quality-gated synthetic imported geometry validation, not real squid validation.",
        "The default quality_check_enabled remains false.",
        "The default reaction_transfer_mode remains engineering.",
        "The moving bounce-back formula is unchanged.",
        "PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.",
        "Imported geometry remains limited to small synthetic voxel and mesh fixtures.",
        "The Step 23 mesh path is not production mesh repair or automatic remeshing.",
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


def test_step23_report_acceptance_complete():
    report = read_text("STEP23_QUALITY_GATED_GEOMETRY_SCALE_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. 48^3 Voxel_Sphere Quality-Gated Modes",
        "## 5. 48^3 Mesh_Cube Quality-Gated Modes",
        "## 6. 48^3 Mesh_Ellipsoid Quality-Gated Modes",
        "## 7. 64^3 Quality-Gated Feasibility",
        "## 8. Quality Report Aggregation",
        "## 9. Step 21 Vs Step 23 Comparison",
        "## 10. Artifact Manifest Summary",
        "## 11. Verification Commands",
        "## 12. GitHub Sync Information",
        "## 13. Acceptance Checklist",
        "## 14. Decision For Step 24",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] quality-gated voxel_sphere 48^3 modes pass",
        "- [x] quality-gated mesh_cube 48^3 modes pass",
        "- [x] quality-gated mesh_ellipsoid 48^3 modes pass",
        "- [x] quality-gated imported geometry 64^3 feasibility passes",
        "- [x] every required driver row has geometry_quality_report.json",
        "- [x] all required quality reports pass",
        "- [x] no required quality report severity == error",
        "- [x] Step 21 vs Step 23 comparison passes",
        "- [x] quality report aggregation passes",
        "- [x] default quality_check_enabled remains false",
        "- [x] quality_check_strict remains false for scale validation",
        "- [x] no FSI formula changes",
        "- [x] default reaction_transfer_mode remains engineering",
        "- [x] no production mesh repair claims",
        "- [x] no automatic remeshing claims",
        "- [x] no real squid validation claims",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] artifact large_file_count == 0",
        "- [x] logs/step23_pytest.log exists",
        "- [x] pytest -q passes",
        "- [x] Git pre-push pytest hook passes",
        "- [x] git diff --check passes",
        "- [x] Step 23 artifacts are pushed to GitHub origin/main",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []
