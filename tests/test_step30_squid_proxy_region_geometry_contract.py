import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP30_REQUIRED_FILES = [
    "STEP30_CONTROLLED_SQUID_PROXY_REGION_GEOMETRY_GOAL.md",
    "STEP30_CONTROLLED_SQUID_PROXY_REGION_GEOMETRY_REPORT.md",
    "docs/30_controlled_squid_proxy_region_geometry.md",
    "src/squid_region_config.py",
    "src/squid_proxy_regions.py",
    "src/squid_region_quality.py",
    "src/squid_region_projection.py",
    "configs/step30_squid_proxy_geometry.json",
    "configs/step30_squid_proxy_region_config.json",
    "baseline_tests/step30_common.py",
    "baseline_tests/run_step30_region_schema_validation.py",
    "baseline_tests/run_step30_region_mask_sampling.py",
    "baseline_tests/run_step30_region_quality.py",
    "baseline_tests/run_step30_region_overlap_diagnostics.py",
    "baseline_tests/run_step30_region_projection_smoke.py",
    "baseline_tests/run_step30_step29_regression_guard.py",
    "baseline_tests/run_step30_artifact_manifest.py",
    "tests/test_step30_squid_proxy_region_geometry_contract.py",
]

STEP30_OUTPUT_FILES = [
    "outputs/step30_region_schema_validation/region_schema_validation.csv",
    "outputs/step30_region_schema_validation/region_schema_validation.json",
    "outputs/step30_region_mask_sampling/region_mask_summary.csv",
    "outputs/step30_region_mask_sampling/region_mask_summary.json",
    "outputs/step30_region_quality/region_quality.csv",
    "outputs/step30_region_quality/region_quality.json",
    "outputs/step30_region_overlap_diagnostics/region_overlap_matrix.csv",
    "outputs/step30_region_overlap_diagnostics/region_overlap_summary.json",
    "outputs/step30_region_projection_smoke/region_projection_results.csv",
    "outputs/step30_region_projection_smoke/region_projection_results.json",
    "outputs/step30_step29_regression_guard/step29_regression_guard.csv",
    "outputs/step30_step29_regression_guard/step29_regression_guard.json",
    "outputs/step30_artifact_manifest/artifact_manifest.csv",
    "outputs/step30_artifact_manifest/artifact_summary.csv",
    "outputs/step30_artifact_manifest/artifact_summary.json",
]

STEP30_LOG_MARKERS = {
    "logs/step30_region_schema_validation.log": "[OK] Step 30 region schema validation finished",
    "logs/step30_region_mask_sampling.log": "[OK] Step 30 region mask sampling finished",
    "logs/step30_region_quality.log": "[OK] Step 30 region quality finished",
    "logs/step30_region_overlap_diagnostics.log": "[OK] Step 30 region overlap diagnostics finished",
    "logs/step30_region_projection_smoke.log": "[OK] Step 30 region projection smoke finished",
    "logs/step30_step29_regression_guard.log": "[OK] Step 30 Step 29 regression guard finished",
    "logs/step30_artifact_manifest.log": "[OK] Step 30 artifact manifest finished",
}

REQUIRED_REGION_IDS = {
    "mantle_outer",
    "mantle_cavity_proxy",
    "funnel_outlet_proxy",
    "head_proxy",
    "arms_proxy",
    "left_fin_proxy",
    "right_fin_proxy",
}

REQUIRED_SCOPE = [
    "Step 30 is controlled squid proxy region geometry.",
    "Step 30 defines squid-like region semantics only.",
    "Step 30 is not real squid validation.",
    "Step 30 does not implement squid actuation.",
    "Step 30 does not implement squid swimming.",
    "Step 30 does not implement mantle contraction.",
    "Step 30 does not implement funnel actuation.",
    "Step 30 does not implement new FSI physics.",
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
    "mantle contraction is implemented",
    "funnel actuation is implemented",
    "implements two_phase",
    "implements contact_angle",
]


def test_step30_required_artifacts_exist():
    missing = [path for path in STEP30_REQUIRED_FILES + STEP30_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_step30_region_config_schema_is_valid():
    geometry_config = read_json("configs/step30_squid_proxy_geometry.json")
    region_config = read_json("configs/step30_squid_proxy_region_config.json")
    schema = read_json("outputs/step30_region_schema_validation/region_schema_validation.json")["summary"]
    assert geometry_config["geometry_type"] == "squid_proxy"
    assert int(geometry_config["n_particles"]) == 4096
    assert geometry_config["quality_check_enabled"] is True
    assert geometry_config["quality_check_strict"] is True
    assert geometry_config["deterministic"] is True
    assert region_config["geometry_type"] == "squid_proxy"
    assert region_config["body_axis"] == "+y"
    assert float(region_config["reference_length"]) > 0.0
    assert set(row["region_id"] for row in region_config["regions"]) == REQUIRED_REGION_IDS
    assert all(row["active_for_actuation"] is False for row in region_config["regions"])
    assert "not anatomical validation" in region_config["scope_note"]
    assert int(schema["required_region_count"]) == 7
    assert int(schema["present_required_region_count"]) == 7
    assert schema["region_ids_unique"] is True
    assert schema["body_axis_valid"] is True
    assert schema["reference_length_positive"] is True
    assert schema["body_frame_origin_finite"] is True
    assert schema["schema_pass"] is True


def test_step30_region_mask_sampling_is_deterministic():
    payload = read_json("outputs/step30_region_mask_sampling/region_mask_summary.json")
    summary = payload["summary"]
    rows = payload["rows"]
    csv_rows = read_csv_rows("outputs/step30_region_mask_sampling/region_mask_summary.csv")
    assert int(summary["row_count"]) == 7
    assert len(rows) == 7
    assert len(csv_rows) == 7
    assert int(summary["sample_count"]) == 32768
    for region_id in REQUIRED_REGION_IDS:
        assert int(summary[f"{region_id}_count"]) > 0
    assert summary["all_masks_boolean"] is True
    assert summary["deterministic_counts_pass"] is True
    assert summary["sampled_position_hash"] == summary["sampled_position_hash_repeat"]
    assert summary["region_assignment_hash"] == summary["region_assignment_hash_repeat"]
    assert summary["sampled_position_hash_repeatable"] is True
    assert summary["region_assignment_hash_repeatable"] is True
    assert summary["sampling_pass"] is True
    assert {row["region_id"] for row in rows} == REQUIRED_REGION_IDS
    assert all(row["bbox_finite"] is True for row in rows)
    assert all(row["diagnostics_finite"] is True for row in rows)


def test_step30_region_quality_is_valid():
    payload = read_json("outputs/step30_region_quality/region_quality.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 11
    assert int(summary["pass_count"]) == 11
    assert summary["region_quality_pass"] is True
    assert int(summary["missing_required_region_count"]) == 0
    assert int(summary["forbidden_claim_count"]) == 0
    for region_id in REQUIRED_REGION_IDS:
        assert int(summary[f"{region_id}_count"]) > 0
    assert all(row["pass"] is True for row in rows)
    assert any(row["check"] == "mantle_cavity_inside_mantle" and row["value"] == "recorded" for row in rows)
    assert any(row["check"] == "funnel_outlet_near_mantle_boundary" and row["value"] == "recorded" for row in rows)


def test_step30_region_overlap_diagnostics_are_valid():
    summary = read_json("outputs/step30_region_overlap_diagnostics/region_overlap_summary.json")
    rows = read_csv_rows("outputs/step30_region_overlap_diagnostics/region_overlap_matrix.csv")
    assert int(summary["row_count"]) == 49
    assert len(rows) == 49
    assert summary["matrix_finite"] is True
    assert int(summary["diagonal_match_count"]) == 7
    assert int(summary["diagonal_mismatch_count"]) == 0
    assert int(summary["intentional_overlap_count"]) > 0
    assert int(summary["unintended_overlap_count"]) == 0
    assert summary["overlap_pass"] is True
    assert not [row for row in rows if as_bool(row["unintended_overlap"])]


def test_step30_region_projection_smoke_is_valid():
    payload = read_json("outputs/step30_region_projection_smoke/region_projection_results.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 14
    assert int(summary["grid_size_count"]) == 2
    assert int(summary["required_region_count"]) == 7
    assert int(summary["pass_count"]) == 14
    assert float(summary["projected_mass_total"]) > 0.0
    assert int(summary["active_cell_count_total"]) > 0
    assert int(summary["has_nan_count"]) == 0
    assert int(summary["has_inf_count"]) == 0
    assert summary["projection_pass"] is True
    assert {int(row["grid_size"]) for row in rows} == {32, 48}
    for grid_size in (32, 48):
        assert {row["region_id"] for row in rows if int(row["grid_size"]) == grid_size} == REQUIRED_REGION_IDS
    for row in rows:
        assert int(row["particle_count"]) > 0
        assert float(row["projected_mass"]) > 0.0
        assert int(row["active_cell_count"]) > 0
        assert float(row["solid_phi_min"]) >= 0.0
        assert float(row["solid_phi_max"]) <= 1.0
        assert row["has_nan"] is False
        assert row["has_inf"] is False
        assert row["projection_pass"] is True


def test_step30_step29_regression_guard_is_valid():
    summary = read_json("outputs/step30_step29_regression_guard/step29_regression_guard.json")
    rows = read_csv_rows("outputs/step30_step29_regression_guard/step29_regression_guard.csv")
    assert int(summary["row_count"]) == 7
    assert int(summary["pass_count"]) == 7
    assert int(summary["step29_driver_row_count"]) == 4
    assert int(summary["step29_stable_count"]) == 4
    assert int(summary["step29_quality_report_count"]) == 4
    assert int(summary["step29_quality_pass_count"]) == 4
    assert int(summary["step29_large_file_count"]) == 0
    assert int(summary["step29_raw_candidate_large_file_count"]) == 0
    assert int(summary["step29_scan_data_file_count"]) == 0
    assert all(as_bool(row["pass"]) for row in rows)


def test_step30_default_modes_remain_unchanged():
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


def test_step30_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "README.md",
            "docs/08_roadmap.md",
            "docs/09_api_reference.md",
            "docs/11_artifact_policy.md",
            "docs/12_geometry_ingestion.md",
            "docs/29_controlled_real_geometry_64_stability_envelope.md",
            "docs/30_controlled_squid_proxy_region_geometry.md",
            "STEP30_CONTROLLED_SQUID_PROXY_REGION_GEOMETRY_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step30_artifact_budget_is_valid():
    summary = read_json("outputs/step30_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step30_total_size_mb"]) < 5.0
    assert float(summary["total_size_mb"]) < 180.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["step30_vtr_count"]) == 0
    assert int(summary["step30_particle_npy_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    manifest_rows = read_csv_rows("outputs/step30_artifact_manifest/artifact_manifest.csv")
    step30_paths = [row["path"] for row in manifest_rows if row["path"].startswith("outputs/step30")]
    assert not [path for path in step30_paths if path.endswith(".vtr")]
    assert not [path for path in step30_paths if path.endswith(".npy") and "particle" in path.lower()]


def test_step30_report_acceptance_complete():
    report = read_text("STEP30_CONTROLLED_SQUID_PROXY_REGION_GEOMETRY_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Region Schema Validation",
        "## 5. Region Mask Sampling",
        "## 6. Region Quality",
        "## 7. Region Overlap Diagnostics",
        "## 8. Region Projection Smoke",
        "## 9. Step 29 Regression Guard",
        "## 10. Artifact Manifest Summary",
        "## 11. Verification Commands",
        "## 12. GitHub Sync Information",
        "## 13. Acceptance Checklist",
        "## 14. Decision For Step 31",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] region schema validation passes",
        "- [x] required squid proxy regions exist",
        "- [x] region IDs are unique",
        "- [x] body axis is defined",
        "- [x] reference length is positive",
        "- [x] body-frame origin is finite",
        "- [x] mantle_outer region exists",
        "- [x] mantle_cavity_proxy region exists",
        "- [x] funnel_outlet_proxy region exists",
        "- [x] head_proxy region exists",
        "- [x] arms_proxy region exists",
        "- [x] fin proxy regions exist or are explicitly disabled",
        "- [x] region mask sampling is deterministic",
        "- [x] region-assignment hash is repeatable",
        "- [x] sampled-position hash is repeatable",
        "- [x] every required region has finite diagnostics",
        "- [x] solid regions have positive count",
        "- [x] cavity proxy has positive count",
        "- [x] funnel outlet proxy has positive count",
        "- [x] region overlap diagnostics pass",
        "- [x] intentional overlaps are documented",
        "- [x] projection-only smoke passes at 32^3",
        "- [x] projection-only smoke passes at 48^3",
        "- [x] region projected mass is finite",
        "- [x] region active cell count is finite",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] Step 29 regression guard passes",
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
        "- [x] no mantle contraction claims",
        "- [x] no funnel actuation claims",
        "- [x] no production sharp-interface FSI claims",
        "- [x] no final readiness claims",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] no committed large raw real geometry",
        "- [x] no committed scan data",
        "- [x] no private absolute paths in committed outputs",
        "- [x] no Step 30 .vtr outputs",
        "- [x] no Step 30 particle .npy outputs",
        "- [x] artifact large_file_count == 0",
        "- [x] Step 30 output total-size budget passes",
        "- [x] repo artifact summary total_size_mb < 180",
        "- [x] logs/step30_pytest.log exists",
        "- [x] full pytest passes",
        "- [x] Step 30 contract test passes",
        "- [x] git diff --check passes",
        "- [x] staged whitespace check passes",
        "- [x] pre-push hook passes",
        "- [x] Step 30 artifacts are pushed to origin/main",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []

    assert (ROOT / "logs/step30_pytest.log").is_file()
    for path, marker in STEP30_LOG_MARKERS.items():
        assert (ROOT / path).is_file(), path
        assert marker in read_text(path), path


def test_step30_no_solver_formula_changes_claimed():
    report = read_text("STEP30_CONTROLLED_SQUID_PROXY_REGION_GEOMETRY_REPORT.md")
    assert "No FSI, LBM, MPM, moving bounce-back, link-area, or projection formula files were edited." in report
    external_status = subprocess.run(
        ["git", "status", "--short", "external/taichi_LBM3D"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert external_status.stdout.strip() == ""


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
