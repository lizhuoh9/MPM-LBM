import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP31_REQUIRED_FILES = [
    "STEP31_CONTROLLED_SQUID_PROXY_REGION_STATIC_DRIVER_GOAL.md",
    "STEP31_CONTROLLED_SQUID_PROXY_REGION_STATIC_DRIVER_REPORT.md",
    "docs/31_controlled_squid_proxy_region_static_driver.md",
    "src/squid_region_driver_diagnostics.py",
    "configs/step31_squid_proxy_region_48_none.json",
    "configs/step31_squid_proxy_region_48_penalty.json",
    "configs/step31_squid_proxy_region_48_moving_boundary.json",
    "configs/step31_squid_proxy_region_48_link_area.json",
    "baseline_tests/step31_common.py",
    "baseline_tests/run_step31_region_projection_scale.py",
    "baseline_tests/run_step31_static_driver_smoke.py",
    "baseline_tests/run_step31_region_driver_alignment.py",
    "baseline_tests/run_step31_engineering_vs_link_area_static_comparison.py",
    "baseline_tests/run_step31_quality_report_aggregation.py",
    "baseline_tests/run_step31_step30_regression_guard.py",
    "baseline_tests/run_step31_artifact_manifest.py",
    "tests/test_step31_squid_proxy_region_static_driver_contract.py",
]

STEP31_OUTPUT_FILES = [
    "outputs/step31_region_projection_scale/region_projection_scale.csv",
    "outputs/step31_region_projection_scale/region_projection_scale.json",
    "outputs/step31_static_driver_smoke/static_driver_results.csv",
    "outputs/step31_static_driver_smoke/static_driver_results.npz",
    "outputs/step31_static_driver_smoke/static_driver_results.json",
    "outputs/step31_region_driver_alignment/region_driver_alignment.csv",
    "outputs/step31_region_driver_alignment/region_driver_alignment.json",
    "outputs/step31_engineering_vs_link_area_static_comparison/engineering_vs_link_area_static.csv",
    "outputs/step31_engineering_vs_link_area_static_comparison/engineering_vs_link_area_static.json",
    "outputs/step31_quality_report_aggregation/quality_report_summary.csv",
    "outputs/step31_quality_report_aggregation/quality_report_summary.json",
    "outputs/step31_step30_regression_guard/step30_regression_guard.csv",
    "outputs/step31_step30_regression_guard/step30_regression_guard.json",
    "outputs/step31_artifact_manifest/artifact_manifest.csv",
    "outputs/step31_artifact_manifest/artifact_summary.csv",
    "outputs/step31_artifact_manifest/artifact_summary.json",
]

STEP31_LOG_MARKERS = {
    "logs/step31_region_projection_scale.log": "[OK] Step 31 region projection scale finished",
    "logs/step31_static_driver_smoke.log": "[OK] Step 31 static driver smoke finished",
    "logs/step31_region_driver_alignment.log": "[OK] Step 31 region driver alignment finished",
    "logs/step31_engineering_vs_link_area_static_comparison.log": "[OK] Step 31 engineering vs link-area static comparison finished",
    "logs/step31_quality_report_aggregation.log": "[OK] Step 31 quality report aggregation finished",
    "logs/step31_step30_regression_guard.log": "[OK] Step 31 Step 30 regression guard finished",
    "logs/step31_artifact_manifest.log": "[OK] Step 31 artifact manifest finished",
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
    "Step 31 is controlled squid proxy region projection and static driver smoke.",
    "Step 31 uses static squid proxy region semantics only.",
    "Step 31 is not real squid validation.",
    "Step 31 does not implement squid actuation.",
    "Step 31 does not implement squid swimming.",
    "Step 31 does not implement mantle contraction.",
    "Step 31 does not implement funnel actuation.",
    "Step 31 does not implement new FSI physics.",
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
    "mantle contraction is implemented",
    "funnel actuation is implemented",
    "production-ready sharp-interface FSI",
    "final solver readiness",
    "production mesh repair is complete",
    "automatic remeshing is implemented",
    "strict momentum-conserving FSI is complete",
    "implements two_phase",
    "implements contact_angle",
]


def test_step31_required_artifacts_exist():
    missing = [path for path in STEP31_REQUIRED_FILES + STEP31_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_step31_driver_configs_are_valid():
    configs = [read_json(path) for path in STEP31_REQUIRED_FILES if path.startswith("configs/step31_")]
    assert len(configs) == 4
    modes = {(item["coupling_mode"], item["reaction_transfer_mode"]) for item in configs}
    assert modes == {
        ("none", "engineering"),
        ("penalty", "engineering"),
        ("moving_boundary", "engineering"),
        ("moving_boundary", "link_area_experimental"),
    }
    for item in configs:
        assert item["geometry_type"] == "squid_proxy"
        assert item["geometry_config_path"] == "configs/step30_squid_proxy_geometry.json"
        assert int(item["n_grid"]) == 48
        assert int(item["n_particles"]) == 4096
        assert int(item["n_lbm_steps"]) == 5
        assert int(item["mpm_substeps_per_lbm_step"]) == 5
        assert int(item["output_interval"]) == 1
        assert item["quality_check_enabled"] is True
        assert item["quality_check_strict"] is True
        assert item["write_vtk"] is False
        assert item["write_particles"] is False
    link_area = [item for item in configs if item["reaction_transfer_mode"] == "link_area_experimental"][0]
    assert link_area["link_area_policy"] == "inverse_length"
    assert float(link_area["link_area_scale_min"]) == 0.25
    assert float(link_area["link_area_scale_max"]) == 2.0


def test_step31_region_projection_scale_is_valid():
    payload = read_json("outputs/step31_region_projection_scale/region_projection_scale.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 21
    assert int(summary["grid_size_count"]) == 3
    assert int(summary["required_region_count"]) == 7
    assert int(summary["pass_count"]) == 21
    assert float(summary["projected_mass_total"]) > 0.0
    assert int(summary["active_cell_count_total"]) > 0
    assert int(summary["has_nan_count"]) == 0
    assert int(summary["has_inf_count"]) == 0
    assert summary["projection_pass"] is True
    assert {int(row["grid_size"]) for row in rows} == {32, 48, 64}
    for grid_size in (32, 48, 64):
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


def test_step31_static_driver_smoke_is_valid():
    payload = read_json("outputs/step31_static_driver_smoke/static_driver_results.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["driver_row_count"]) == 4
    assert int(summary["stable_count"]) == 4
    assert int(summary["quality_report_count"]) == 4
    assert int(summary["quality_pass_count"]) == 4
    assert int(summary["strict_count"]) == 4
    assert int(summary["min_completed_lbm_steps"]) >= 5
    assert int(summary["min_total_mpm_substeps"]) >= 25
    assert float(summary["min_rho_min_global"]) > 0.95
    assert float(summary["max_rho_max_global"]) < 1.05
    assert float(summary["max_lbm_max_v_global"]) < 0.1
    assert float(summary["min_mpm_min_J_global"]) > 0.0
    assert float(summary["max_mpm_max_speed_global"]) < 10.0
    assert float(summary["min_projected_mass"]) > 0.0
    assert int(summary["min_active_cell_count"]) > 0
    assert int(summary["min_moving_bb_link_count_max"]) > 0
    assert int(summary["min_moving_active_reaction_particle_count_max"]) > 0
    by_mode = {(row["mode"], row["reaction_transfer_mode"]): row for row in rows}
    assert float(by_mode[("none", "engineering")]["cell_force_max_norm"]) == 0.0
    assert int(by_mode[("none", "engineering")]["bb_link_count_max"]) == 0
    assert float(by_mode[("penalty", "engineering")]["cell_force_max_norm"]) > 0.0
    assert int(by_mode[("penalty", "engineering")]["bb_link_count_max"]) == 0
    for transfer in ("engineering", "link_area_experimental"):
        row = by_mode[("moving_boundary", transfer)]
        assert float(row["cell_force_max_norm"]) == 0.0
        assert int(row["bb_link_count_max"]) > 0
        assert int(row["active_reaction_particle_count_max"]) > 0
    link_area = by_mode[("moving_boundary", "link_area_experimental")]
    assert 0.25 <= float(link_area["area_scale_final"]) <= 2.0
    assert all(row["quality_severity"] == "ok" for row in rows)
    assert all(row["quality_warnings_count"] == 0 for row in rows)
    assert all(row["quality_reasons_count"] == 0 for row in rows)
    assert all(row["has_nan"] is False and row["has_inf"] is False for row in rows)


def test_step31_region_driver_alignment_is_valid():
    payload = read_json("outputs/step31_region_driver_alignment/region_driver_alignment.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 4
    assert int(summary["pass_count"]) == 4
    assert float(summary["min_driver_projected_mass"]) > 0.0
    assert float(summary["min_region_context_projected_mass_total"]) > 0.0
    assert int(summary["min_driver_active_cell_count"]) > 0
    assert int(summary["min_region_context_active_cell_count_total"]) > 0
    assert "not a mass partition" in summary["semantic_overlap_note"]
    for row in rows:
        assert row["alignment_pass"] is True
        assert float(row["driver_projected_mass"]) > 0.0
        assert float(row["region_context_projected_mass_total"]) > 0.0
        assert int(row["driver_active_cell_count"]) > 0
        assert int(row["region_context_active_cell_count_total"]) > 0
        assert "not a mass partition" in row["semantic_overlap_note"]


def test_step31_engineering_vs_link_area_static_comparison_is_valid():
    payload = read_json("outputs/step31_engineering_vs_link_area_static_comparison/engineering_vs_link_area_static.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 1
    assert int(summary["pass_count"]) == 1
    row = rows[0]
    assert row["comparison_pass"] is True
    assert abs(float(row["rho_min_delta"])) <= 1.0e-3
    assert abs(float(row["rho_max_delta"])) <= 1.0e-3
    assert abs(float(row["lbm_max_v_delta"])) <= 1.0e-3
    assert abs(float(row["mpm_min_J_delta"])) <= 1.0e-3
    assert abs(float(row["projected_mass_delta"])) <= 1.0e-4
    assert 0.25 <= float(row["link_area_area_scale_final"]) <= 2.0


def test_step31_quality_report_aggregation_is_valid():
    payload = read_json("outputs/step31_quality_report_aggregation/quality_report_summary.json")
    summary = payload["summary"]
    assert int(summary["quality_report_count"]) == 4
    assert int(summary["strict_count"]) == 4
    assert int(summary["pass_count"]) == 4
    assert int(summary["error_count"]) == 0
    assert int(summary["warning_count"]) == 0
    assert int(summary["quality_report_max_size_bytes"]) < 100_000
    assert int(summary["procedural_row_count"]) == 4


def test_step31_step30_regression_guard_is_valid():
    summary = read_json("outputs/step31_step30_regression_guard/step30_regression_guard.json")
    rows = read_csv_rows("outputs/step31_step30_regression_guard/step30_regression_guard.csv")
    assert int(summary["row_count"]) == 7
    assert int(summary["pass_count"]) == 7
    assert int(summary["step30_required_region_count"]) == 7
    assert summary["step30_sampling_hash_repeatable"] is True
    assert summary["step30_projection_pass"] is True
    assert int(summary["step30_large_file_count"]) == 0
    assert int(summary["step30_vtr_count"]) == 0
    assert int(summary["step30_particle_npy_count"]) == 0
    assert all(as_bool(row["pass"]) for row in rows)


def test_step31_default_modes_remain_unchanged():
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


def test_step31_docs_scope_and_forbidden_claims_are_valid():
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
            "docs/31_controlled_squid_proxy_region_static_driver.md",
            "STEP31_CONTROLLED_SQUID_PROXY_REGION_STATIC_DRIVER_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step31_artifact_budget_is_valid():
    summary = read_json("outputs/step31_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step31_total_size_mb"]) < 10.0
    assert float(summary["total_size_mb"]) < 185.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["step31_vtr_count"]) == 0
    assert int(summary["step31_particle_npy_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    manifest_rows = read_csv_rows("outputs/step31_artifact_manifest/artifact_manifest.csv")
    step31_paths = [row["path"] for row in manifest_rows if row["path"].startswith("outputs/step31")]
    assert not [path for path in step31_paths if path.endswith(".vtr")]
    assert not [path for path in step31_paths if path.endswith(".npy") and "particle" in path.lower()]


def test_step31_report_acceptance_complete():
    report = read_text("STEP31_CONTROLLED_SQUID_PROXY_REGION_STATIC_DRIVER_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Region Projection Scale",
        "## 5. Static Driver Smoke",
        "## 6. Region Driver Alignment",
        "## 7. Engineering Vs Link-Area Static Comparison",
        "## 8. Quality Report Aggregation",
        "## 9. Step 30 Regression Guard",
        "## 10. Artifact Manifest Summary",
        "## 11. Verification Commands",
        "## 12. GitHub Sync Information",
        "## 13. Acceptance Checklist",
        "## 14. Decision For Step 32",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] region projection scale passes at 32^3",
        "- [x] region projection scale passes at 48^3",
        "- [x] region projection scale passes at 64^3",
        "- [x] all required Step 30 regions are present",
        "- [x] region projected mass is finite",
        "- [x] region active cell count is finite",
        "- [x] static driver none row passes",
        "- [x] static driver penalty row passes",
        "- [x] static driver moving_boundary engineering row passes",
        "- [x] static driver moving_boundary link_area row passes",
        "- [x] every Step 31 driver row writes geometry_quality_report.json",
        "- [x] every Step 31 quality gate is strict",
        "- [x] every Step 31 quality report passes",
        "- [x] quality warning count == 0",
        "- [x] quality error count == 0",
        "- [x] all driver rows have completed_lbm_steps >= 5",
        "- [x] all driver rows have total_mpm_substeps >= 25",
        "- [x] rho_min > 0.95",
        "- [x] rho_max < 1.05",
        "- [x] lbm_max_v < 0.1",
        "- [x] mpm_min_J > 0",
        "- [x] mpm_max_speed < 10",
        "- [x] projected_mass > 0",
        "- [x] active_cell_count > 0",
        "- [x] no NaN",
        "- [x] no Inf",
        "- [x] none row has zero cell force",
        "- [x] penalty row has positive cell force",
        "- [x] moving_boundary rows have positive bb_link_count",
        "- [x] moving_boundary rows have active reaction particles",
        "- [x] link_area row has finite bounded area_scale",
        "- [x] region-driver alignment passes",
        "- [x] semantic overlap note is present",
        "- [x] engineering vs link_area static comparison passes",
        "- [x] Step 30 regression guard passes",
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
        "- [x] no Step 31 `.vtr` outputs",
        "- [x] no Step 31 particle `.npy` outputs",
        "- [x] artifact `large_file_count == 0`",
        "- [x] Step 31 output total-size budget passes",
        "- [x] repo artifact summary `total_size_mb < 185`",
        "- [x] `logs/step31_pytest.log` exists",
        "- [x] full pytest passes",
        "- [x] Step 31 contract test passes",
        "- [x] `git diff --check` passes",
        "- [x] staged whitespace check passes",
        "- [x] pre-push hook passes",
        "- [x] Step 31 artifacts are pushed to `origin/main`",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []

    assert (ROOT / "logs/step31_pytest.log").is_file()
    for path, marker in STEP31_LOG_MARKERS.items():
        assert (ROOT / path).is_file(), path
        assert marker in read_text(path), path


def test_step31_no_solver_formula_changes_claimed():
    report = read_text("STEP31_CONTROLLED_SQUID_PROXY_REGION_STATIC_DRIVER_REPORT.md")
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
