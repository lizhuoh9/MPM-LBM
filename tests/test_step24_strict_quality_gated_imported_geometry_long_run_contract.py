import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


STEP24_CONFIGS = [
    "configs/step24_strict_voxel_sphere_48_moving_boundary.json",
    "configs/step24_strict_voxel_sphere_48_link_area.json",
    "configs/step24_strict_mesh_cube_48_moving_boundary.json",
    "configs/step24_strict_mesh_cube_48_link_area.json",
    "configs/step24_strict_mesh_ellipsoid_48_moving_boundary.json",
    "configs/step24_strict_mesh_ellipsoid_48_link_area.json",
    "configs/step24_strict_voxel_sphere_64_moving_boundary.json",
    "configs/step24_strict_mesh_cube_64_moving_boundary.json",
    "configs/step24_strict_mesh_cube_64_link_area.json",
]


STEP24_REQUIRED_DRIVER_OUTPUTS = {
    "outputs/step24_strict_voxel_sphere_48_long/voxel_sphere_48_strict_long_results.csv": 2,
    "outputs/step24_strict_mesh_cube_48_long/mesh_cube_48_strict_long_results.csv": 2,
    "outputs/step24_strict_mesh_ellipsoid_48_long/mesh_ellipsoid_48_strict_long_results.csv": 2,
    "outputs/step24_strict_imported_geometry_64_feasibility/imported_geometry_64_strict_feasibility_results.csv": 3,
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


def test_step24_required_artifacts_exist():
    required_paths = [
        "baseline_tests/step24_common.py",
        "baseline_tests/run_step24_strict_voxel_sphere_48_long.py",
        "baseline_tests/run_step24_strict_mesh_cube_48_long.py",
        "baseline_tests/run_step24_strict_mesh_ellipsoid_48_long.py",
        "baseline_tests/run_step24_strict_imported_geometry_64_feasibility.py",
        "baseline_tests/run_step24_quality_report_aggregation.py",
        "baseline_tests/run_step24_step23_prefix_comparison.py",
        "baseline_tests/run_step24_strict_non_strict_report_comparison.py",
        "baseline_tests/run_step24_timing_overhead_summary.py",
        "baseline_tests/run_step24_artifact_manifest.py",
        "docs/23_strict_quality_gated_imported_geometry_long_run.md",
        "STEP24_STRICT_QUALITY_GATED_IMPORTED_GEOMETRY_LONG_RUN_GOAL.md",
        "STEP24_STRICT_QUALITY_GATED_IMPORTED_GEOMETRY_LONG_RUN_REPORT.md",
    ]
    missing = [path for path in required_paths + STEP24_CONFIGS if not (ROOT / path).is_file()]
    assert missing == []


def test_step24_config_contract():
    for path in STEP24_CONFIGS:
        data = read_json(path)
        assert data["quality_check_enabled"] is True
        assert data["quality_check_strict"] is True
        assert data["write_vtk"] is False
        assert data["write_particles"] is False
        assert data["coupling_mode"] == "moving_boundary"
        assert data["geometry_type"] in {"voxel", "mesh"}
        assert data["geometry_config_path"].startswith("configs/step20_")
        assert data["reaction_transfer_mode"] in {"engineering", "link_area_experimental"}
        assert int(data["n_particles"]) == 4096
        if data["reaction_transfer_mode"] == "link_area_experimental":
            assert data["link_area_policy"] == "inverse_length"
            assert float(data["link_area_scale_min"]) == 0.25
            assert float(data["link_area_scale_max"]) == 2.0

    for path in STEP24_CONFIGS[:6]:
        data = read_json(path)
        assert int(data["n_grid"]) == 48
        assert int(data["n_lbm_steps"]) >= 30
        assert int(data["mpm_substeps_per_lbm_step"]) >= 10

    for path in STEP24_CONFIGS[6:]:
        data = read_json(path)
        assert int(data["n_grid"]) == 64
        assert int(data["n_lbm_steps"]) >= 5
        assert int(data["mpm_substeps_per_lbm_step"]) >= 5


def test_step24_default_quality_gate_remains_disabled():
    geometry_config = read_text("src/mpm_lbm/sim/geometry/config.py")
    fsi_config = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    assert "quality_check_enabled: bool = False" in geometry_config
    assert "quality_check_strict: bool = False" in geometry_config
    assert "quality_check_enabled: bool = False" in fsi_config
    assert "quality_check_strict: bool = False" in fsi_config
    assert 'reaction_transfer_mode: str = "engineering"' in fsi_config


def test_step24_logs_record_success_markers():
    expected_markers = {
        "logs/step24_strict_voxel_sphere_48_long.log": "[OK] Step 24 strict voxel_sphere 48 long-run finished",
        "logs/step24_strict_mesh_cube_48_long.log": "[OK] Step 24 strict mesh_cube 48 long-run finished",
        "logs/step24_strict_mesh_ellipsoid_48_long.log": "[OK] Step 24 strict mesh_ellipsoid 48 long-run finished",
        "logs/step24_strict_imported_geometry_64_feasibility.log": "[OK] Step 24 strict imported geometry 64 feasibility finished",
        "logs/step24_quality_report_aggregation.log": "[OK] Step 24 quality report aggregation finished",
        "logs/step24_step23_prefix_comparison.log": "[OK] Step 24 Step 23 prefix comparison finished",
        "logs/step24_strict_non_strict_report_comparison.log": "[OK] Step 24 strict vs non-strict report comparison finished",
        "logs/step24_timing_overhead_summary.log": "[OK] Step 24 timing overhead summary finished",
        "logs/step24_artifact_manifest.log": "[OK] Step 24 artifact manifest finished",
    }
    missing = []
    for path, marker in expected_markers.items():
        if not (ROOT / path).is_file() or marker not in read_log(path):
            missing.append(f"{path}: {marker}")
    assert missing == []


def test_step24_driver_outputs_are_valid():
    total_rows = 0
    for csv_path, expected_rows in STEP24_REQUIRED_DRIVER_OUTPUTS.items():
        rows = read_csv_rows(csv_path)
        assert len(rows) == expected_rows
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
                    "quality_gate_strict",
                    "quality_report_path",
                    "driver_timing_path",
                    "stable",
                    "notes",
                ),
            )
            assert as_bool(row["stable"])
            assert as_bool(row["quality_check_enabled"])
            assert as_bool(row["quality_check_strict"])
            assert as_bool(row["quality_gate_strict"])
            assert as_bool(row["quality_pass"])
            assert row["quality_severity"] == "ok"
            assert as_int(row, "quality_warnings_count") == 0
            assert as_int(row, "quality_reasons_count") == 0
            assert as_float(row, "rho_min_global") > 0.95
            assert as_float(row, "rho_max_global") < 1.05
            assert as_float(row, "lbm_max_v_global") < 0.1
            assert as_float(row, "mpm_min_J_global") > 0.0
            assert as_float(row, "mpm_max_speed_global") < 10.0
            assert as_float(row, "projected_mass") > 0.0
            assert as_int(row, "active_cell_count") > 0
            assert as_float(row, "cell_force_max_norm") == 0.0
            assert as_int(row, "bb_link_count_min") > 0
            assert as_int(row, "bb_link_count_max") > 0
            assert as_int(row, "active_reaction_particle_count_max") > 0
            assert (ROOT / row["quality_report_path"]).is_file()
            assert (ROOT / row["driver_timing_path"]).is_file()
            if row["reaction_transfer_mode"] == "link_area_experimental":
                assert 0.25 <= as_float(row, "area_scale_final") <= 2.0

    assert total_rows == 9


def test_step24_quality_report_aggregation_is_valid():
    rows = read_csv_rows("outputs/step24_quality_report_aggregation/quality_report_summary.csv")
    summary = read_json("outputs/step24_quality_report_aggregation/quality_report_summary.json")
    assert len(rows) == 9
    assert int(summary["quality_report_count"]) == 9
    assert int(summary["pass_count"]) == 9
    assert int(summary["error_count"]) == 0
    assert int(summary["warning_count"]) == 0

    for row in rows:
        assert row["severity"] == "ok"
        assert as_bool(row["strict"])
        assert as_bool(row["pass"])
        assert as_int(row, "warnings_count") == 0
        assert as_int(row, "reasons_count") == 0
        assert as_int(row, "report_size_bytes") < 100_000
        if row["geometry_type"] == "mesh":
            assert as_int(row, "vertices_count") > 0
            assert as_int(row, "faces_count") > 0
            assert as_int(row, "boundary_edge_count") == 0
            assert as_int(row, "degenerate_face_count") == 0
            assert as_int(row, "nonmanifold_edge_count") == 0
        if row["geometry_type"] == "voxel":
            assert as_int(row, "occupied_count") > 0
            assert as_int(row, "connected_component_count") == 1
            assert as_float(row, "largest_component_fraction") == 1.0


def test_step24_step23_prefix_comparison_is_valid():
    rows = read_csv_rows("outputs/step24_step23_prefix_comparison/step23_prefix_comparison.csv")
    summary = read_json("outputs/step24_step23_prefix_comparison/step23_prefix_comparison.json")
    assert len(rows) == 9
    assert int(summary["row_count"]) == 9
    assert int(summary["compared_row_count"]) >= 7
    assert int(summary["missing_overlap_count"]) == 2
    assert int(summary["stable_both_count"]) == 9

    for row in rows:
        assert as_bool(row["stable_both"])
        if row["comparison_status"] == "compared":
            assert abs(as_float(row, "rho_min_delta")) <= 1.0e-5
            assert abs(as_float(row, "rho_max_delta")) <= 1.0e-5
            assert abs(as_float(row, "lbm_max_v_delta")) <= 1.0e-5
            assert abs(as_float(row, "mpm_min_J_delta")) <= 1.0e-5
            assert abs(as_float(row, "projected_mass_delta")) <= 1.0e-5
            assert as_int(row, "active_cell_count_delta") == 0
        else:
            assert row["comparison_status"] == "not_comparable_step23_overlap_missing"


def test_step24_strict_non_strict_report_comparison_is_valid():
    rows = read_csv_rows(
        "outputs/step24_strict_non_strict_report_comparison/strict_non_strict_report_comparison.csv"
    )
    summary = read_json(
        "outputs/step24_strict_non_strict_report_comparison/strict_non_strict_report_comparison.json"
    )
    assert len(rows) == 9
    assert int(summary["row_count"]) == 9
    assert int(summary["reports_match_count"]) == 9
    assert int(summary["step23_report_count"]) >= 7
    assert int(summary["qa_only_nonstrict_report_count"]) == 2
    for row in rows:
        assert as_bool(row["reports_match"])
        assert as_bool(row["same_quality_kind"])
        assert as_bool(row["same_geometry_type"])
        assert as_bool(row["same_pass"])
        assert as_bool(row["same_severity"])
        assert as_bool(row["mesh_counts_match"])
        assert as_bool(row["voxel_counts_match"])
        assert as_int(row, "strict_reasons_count") == 0
        assert as_int(row, "nonstrict_reasons_count") == 0
        assert as_int(row, "strict_warnings_count") == 0
        assert as_int(row, "nonstrict_warnings_count") == 0


def test_step24_timing_and_artifact_summaries_are_valid():
    timing_summary = read_json("outputs/step24_timing_overhead_summary/step24_timing_summary.json")
    assert int(timing_summary["row_count"]) == 9
    assert int(timing_summary["quality_report_count"]) == 9
    assert "not a production benchmark" in timing_summary["scope_note"]

    artifact_summary = read_json("outputs/step24_artifact_manifest/artifact_summary.json")
    assert int(artifact_summary["file_count"]) > 0
    assert int(artifact_summary["total_size_bytes"]) > 0
    assert float(artifact_summary["total_size_mb"]) < 150.0
    assert int(artifact_summary["large_file_count"]) == 0
    assert int(artifact_summary["step24_quality_report_count"]) == 9
    assert float(artifact_summary["step24_total_size_mb"]) < 25.0
    assert (ROOT / "outputs/step24_artifact_manifest/artifact_summary.csv").is_file()
    assert (ROOT / "logs/step24_pytest.log").is_file()

    manifest_rows = read_csv_rows("outputs/step24_artifact_manifest/artifact_manifest.csv")
    step24_paths = [row["path"] for row in manifest_rows if row["path"].startswith("outputs/step24")]
    assert not [path for path in step24_paths if path.endswith(".vtr")]
    assert not [path for path in step24_paths if path.endswith(".npy") and "particle" in path.lower()]


def test_step24_docs_report_and_manifest_are_valid():
    doc_paths = [
        "README.md",
        "docs/08_roadmap.md",
        "docs/09_api_reference.md",
        "docs/12_geometry_ingestion.md",
        "docs/19_geometry_import_pipeline.md",
        "docs/20_imported_geometry_scale_validation.md",
        "docs/21_geometry_quality_checks.md",
        "docs/22_quality_gated_imported_geometry_validation.md",
        "docs/23_strict_quality_gated_imported_geometry_long_run.md",
        "STEP24_STRICT_QUALITY_GATED_IMPORTED_GEOMETRY_LONG_RUN_REPORT.md",
    ]
    combined = "\n".join(read_text(path) for path in doc_paths)
    required_scope = [
        "Step 24 runs strict quality-gated synthetic imported geometry long-run validation.",
        "Step 24 uses quality_check_enabled=true and quality_check_strict=true for selected imported geometry rows.",
        "Step 24 is not real squid validation.",
        "Step 24 does not implement new FSI physics.",
        "The default quality_check_enabled remains false.",
        "The default quality_check_strict remains false.",
        "The default reaction_transfer_mode remains engineering.",
        "The moving bounce-back formula is unchanged.",
        "PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.",
        "Imported geometry remains limited to small synthetic voxel and mesh fixtures.",
        "The Step 24 mesh path is not production mesh repair or automatic remeshing.",
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


def test_step24_report_acceptance_complete():
    report = read_text("STEP24_STRICT_QUALITY_GATED_IMPORTED_GEOMETRY_LONG_RUN_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. 48^3 Voxel_Sphere Strict Long-Run",
        "## 5. 48^3 Mesh_Cube Strict Long-Run",
        "## 6. 48^3 Mesh_Ellipsoid Strict Long-Run",
        "## 7. 64^3 Strict Imported Geometry Feasibility",
        "## 8. Quality Report Aggregation",
        "## 9. Step 23 Prefix Comparison",
        "## 10. Strict Vs Non-Strict Report Comparison",
        "## 11. Timing And Overhead Summary",
        "## 12. Artifact Manifest Summary",
        "## 13. Verification Commands",
        "## 14. GitHub Sync Information",
        "## 15. Acceptance Checklist",
        "## 16. Decision For Step 25",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] strict voxel_sphere 48^3 long-run engineering passes",
        "- [x] strict voxel_sphere 48^3 long-run link_area passes",
        "- [x] strict mesh_cube 48^3 long-run engineering passes",
        "- [x] strict mesh_cube 48^3 long-run link_area passes",
        "- [x] strict mesh_ellipsoid 48^3 long-run engineering passes",
        "- [x] strict mesh_ellipsoid 48^3 long-run link_area passes",
        "- [x] strict voxel_sphere 64^3 moving_boundary feasibility passes",
        "- [x] strict mesh_cube 64^3 moving_boundary feasibility passes",
        "- [x] strict mesh_cube 64^3 link_area feasibility passes",
        "- [x] every Step 24 row writes geometry_quality_report.json",
        "- [x] every Step 24 gate.strict == true",
        "- [x] every Step 24 quality_pass == true",
        "- [x] every Step 24 quality_severity == ok",
        "- [x] Step 23 prefix comparison passes for overlapping rows",
        "- [x] strict vs non-strict report comparison passes",
        "- [x] default quality_check_enabled remains false",
        "- [x] default quality_check_strict remains false",
        "- [x] default reaction_transfer_mode remains engineering",
        "- [x] no FSI formula changes",
        "- [x] no moving bounce-back formula changes",
        "- [x] no real squid validation claims",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] artifact large_file_count == 0",
        "- [x] pytest -q passes",
        "- [x] Step 24 contract test passes",
        "- [x] git diff --check passes",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []
