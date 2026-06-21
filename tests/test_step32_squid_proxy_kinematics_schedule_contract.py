import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP32_REQUIRED_FILES = [
    "STEP32_CONTROLLED_SQUID_PROXY_KINEMATICS_SCHEDULE_GOAL.md",
    "STEP32_CONTROLLED_SQUID_PROXY_KINEMATICS_SCHEDULE_REPORT.md",
    "docs/32_controlled_squid_proxy_kinematics_schedule.md",
    "src/squid_kinematics_config.py",
    "src/squid_kinematics_schedule.py",
    "src/squid_kinematics_quality.py",
    "src/squid_kinematics_region_mapping.py",
    "configs/step32_squid_proxy_kinematics_schedule.json",
    "configs/step32_squid_proxy_kinematics_sampling.json",
    "baseline_tests/step32_common.py",
    "baseline_tests/run_step32_schedule_config_validation.py",
    "baseline_tests/run_step32_generate_kinematics_schedule.py",
    "baseline_tests/run_step32_schedule_quality.py",
    "baseline_tests/run_step32_schedule_repeatability.py",
    "baseline_tests/run_step32_region_mapping_validation.py",
    "baseline_tests/run_step32_schedule_envelope_summary.py",
    "baseline_tests/run_step32_step31_regression_guard.py",
    "baseline_tests/run_step32_artifact_manifest.py",
    "tests/test_step32_squid_proxy_kinematics_schedule_contract.py",
]

STEP32_OUTPUT_FILES = [
    "outputs/step32_schedule_config_validation/schedule_config_validation.csv",
    "outputs/step32_schedule_config_validation/schedule_config_validation.json",
    "outputs/step32_kinematics_schedule/kinematics_schedule.csv",
    "outputs/step32_kinematics_schedule/kinematics_schedule.json",
    "outputs/step32_schedule_quality/schedule_quality.csv",
    "outputs/step32_schedule_quality/schedule_quality.json",
    "outputs/step32_schedule_repeatability/schedule_repeatability.csv",
    "outputs/step32_schedule_repeatability/schedule_repeatability.json",
    "outputs/step32_region_mapping_validation/region_mapping_validation.csv",
    "outputs/step32_region_mapping_validation/region_mapping_validation.json",
    "outputs/step32_schedule_envelope_summary/schedule_envelope_summary.csv",
    "outputs/step32_schedule_envelope_summary/schedule_envelope_summary.json",
    "outputs/step32_step31_regression_guard/step31_regression_guard.csv",
    "outputs/step32_step31_regression_guard/step31_regression_guard.json",
    "outputs/step32_artifact_manifest/artifact_manifest.csv",
    "outputs/step32_artifact_manifest/artifact_summary.csv",
    "outputs/step32_artifact_manifest/artifact_summary.json",
]

STEP32_LOG_MARKERS = {
    "logs/step32_schedule_config_validation.log": "[OK] Step 32 schedule config validation finished",
    "logs/step32_generate_kinematics_schedule.log": "[OK] Step 32 generate kinematics schedule finished",
    "logs/step32_schedule_quality.log": "[OK] Step 32 schedule quality finished",
    "logs/step32_schedule_repeatability.log": "[OK] Step 32 schedule repeatability finished",
    "logs/step32_region_mapping_validation.log": "[OK] Step 32 region mapping validation finished",
    "logs/step32_schedule_envelope_summary.log": "[OK] Step 32 schedule envelope summary finished",
    "logs/step32_step31_regression_guard.log": "[OK] Step 32 Step 31 regression guard finished",
    "logs/step32_artifact_manifest.log": "[OK] Step 32 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 32 is controlled squid proxy prescribed kinematics schedule.",
    "Step 32 defines kinematics schedules only.",
    "Step 32 does not integrate kinematics into FSIDriver3D.",
    "Step 32 does not apply moving wall velocity.",
    "Step 32 does not implement mantle contraction in the driver.",
    "Step 32 does not implement funnel actuation in the driver.",
    "Step 32 does not implement squid swimming.",
    "Step 32 does not implement new FSI physics.",
    "The default quality_check_enabled remains false.",
    "The default quality_check_strict remains false.",
    "The default reaction_transfer_mode remains engineering.",
    "The moving bounce-back formula is unchanged.",
    "PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.",
]

FORBIDDEN_CLAIMS = [
    "mantle contraction is integrated into the driver",
    "funnel actuation is integrated into the driver",
    "squid actuation is implemented",
    "squid swimming is implemented",
    "real squid simulation is validated",
    "production-ready sharp-interface FSI",
    "final solver readiness",
    "jet model is implemented",
    "free-body motion is implemented",
    "moving wall velocity is applied",
    "strict momentum-conserving FSI is complete",
    "implements two_phase",
    "implements contact_angle",
]


def test_step32_required_artifacts_exist():
    missing = [path for path in STEP32_REQUIRED_FILES + STEP32_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_step32_schedule_config_is_valid():
    config = read_json("configs/step32_squid_proxy_kinematics_schedule.json")
    sampling = read_json("configs/step32_squid_proxy_kinematics_sampling.json")
    validation = read_json("outputs/step32_schedule_config_validation/schedule_config_validation.json")
    assert config["schedule_id"] == "step32_squid_proxy_prescribed_cycle"
    assert config["region_config_path"] == "configs/step30_squid_proxy_region_config.json"
    assert config["geometry_config_path"] == "configs/step30_squid_proxy_geometry.json"
    assert int(config["cycle_period_steps"]) == 40
    assert int(config["sample_count"]) == 81
    assert float(config["contraction_start_phase"]) == 0.0
    assert float(config["contraction_end_phase"]) == 0.35
    assert float(config["refill_start_phase"]) == 0.35
    assert float(config["refill_end_phase"]) == 1.0
    assert float(config["mantle_radius_scale_min"]) == 0.85
    assert float(config["cavity_volume_scale_min"]) == 0.6
    assert float(config["funnel_aperture_scale_rest"]) == 0.35
    assert float(config["funnel_aperture_scale_max"]) == 1.0
    assert config["deterministic"] is True
    assert config["driver_integration_enabled"] is False
    assert config["actuation_enabled"] is False
    assert "schedule contract only" in config["scope_note"]
    assert "no driver integration" in config["scope_note"]
    assert sampling["schedule_config_path"] == "configs/step32_squid_proxy_kinematics_schedule.json"
    assert int(sampling["output_row_count"]) == int(config["sample_count"])
    assert sampling["driver_integration_enabled"] is False
    assert sampling["actuation_enabled"] is False
    assert "driver" not in {key for key in sampling if key not in {"driver_integration_enabled"}}
    summary = validation["summary"]
    assert int(summary["row_count"]) == 19
    assert int(summary["pass_count"]) == 19
    assert summary["validation_pass"] is True
    assert all(row["pass"] is True for row in validation["rows"])


def test_step32_kinematics_schedule_is_valid():
    config = read_json("configs/step32_squid_proxy_kinematics_schedule.json")
    payload = read_json("outputs/step32_kinematics_schedule/kinematics_schedule.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == int(config["sample_count"]) == 81
    assert float(summary["phase_min"]) == 0.0
    assert float(summary["phase_max"]) == 1.0
    assert summary["finite_pass"] is True
    assert summary["endpoint_repeatability_pass"] is True
    assert int(summary["driver_integration_enabled_count"]) == 0
    assert int(summary["actuation_enabled_count"]) == 0
    assert float(summary["mantle_radius_scale_min_observed"]) == float(config["mantle_radius_scale_min"])
    assert float(summary["mantle_radius_scale_max_observed"]) == float(config["mantle_radius_scale_rest"])
    assert float(summary["cavity_volume_scale_min_observed"]) == float(config["cavity_volume_scale_min"])
    assert float(summary["cavity_volume_scale_max_observed"]) == float(config["cavity_volume_scale_rest"])
    assert float(summary["funnel_aperture_scale_min_observed"]) == float(config["funnel_aperture_scale_rest"])
    assert float(summary["funnel_aperture_scale_max_observed"]) == float(config["funnel_aperture_scale_max"])
    assert [float(row["phase"]) for row in rows] == sorted(float(row["phase"]) for row in rows)
    assert rows[0]["phase_label"] == "cycle_endpoint"
    assert rows[-1]["phase_label"] == "cycle_endpoint"
    assert all(row["driver_integration_enabled"] is False for row in rows)
    assert all(row["actuation_enabled"] is False for row in rows)
    assert all("no driver integration" in row["scope_note"] for row in rows)


def test_step32_schedule_quality_is_valid():
    payload = read_json("outputs/step32_schedule_quality/schedule_quality.json")
    summary = payload["summary"]
    for key in (
        "row_count_pass",
        "finite_pass",
        "bounds_pass",
        "phase_monotonic_pass",
        "endpoint_repeatability_pass",
        "derivative_finite_pass",
        "contraction_volume_rate_pass",
        "refill_volume_rate_pass",
        "funnel_aperture_bounds_pass",
        "driver_integration_disabled_pass",
        "actuation_disabled_pass",
        "quality_pass",
    ):
        assert summary[key] is True
    assert int(summary["row_count"]) == 81
    assert all(row["pass"] is True for row in payload["rows"])


def test_step32_schedule_repeatability_is_valid():
    payload = read_json("outputs/step32_schedule_repeatability/schedule_repeatability.json")
    summary = payload["summary"]
    assert int(summary["row_count_first"]) == int(summary["row_count_second"]) == 81
    assert summary["schedule_hash_first"] == summary["schedule_hash_second"]
    assert summary["mantle_hash_first"] == summary["mantle_hash_second"]
    assert summary["cavity_hash_first"] == summary["cavity_hash_second"]
    assert summary["funnel_hash_first"] == summary["funnel_hash_second"]
    assert summary["repeatability_pass"] is True
    assert all(row["pass"] is True for row in payload["rows"])


def test_step32_region_mapping_validation_is_valid():
    payload = read_json("outputs/step32_region_mapping_validation/region_mapping_validation.json")
    summary = payload["summary"]
    assert summary["mantle_outer_present"] is True
    assert summary["mantle_cavity_proxy_present"] is True
    assert summary["funnel_outlet_proxy_present"] is True
    assert int(summary["present_required_region_count"]) == int(summary["required_region_count"]) == 7
    assert int(summary["active_for_actuation_region_count"]) == 0
    assert summary["driver_integration_enabled"] is False
    assert summary["actuation_enabled"] is False
    assert summary["mapping_pass"] is True
    assert "future mapping only" in summary["mapping_note"]
    assert all(row["pass"] is True for row in payload["rows"])


def test_step32_schedule_envelope_summary_is_valid():
    payload = read_json("outputs/step32_schedule_envelope_summary/schedule_envelope_summary.json")
    summary = payload["summary"]
    assert summary["envelope_pass"] is True
    assert int(summary["row_count"]) == 81
    assert int(summary["contraction_sample_count"]) > 0
    assert int(summary["refill_sample_count"]) > 0
    assert int(summary["funnel_open_sample_count"]) > 0
    assert float(summary["mantle_radius_scale_min_observed"]) == 0.85
    assert float(summary["mantle_radius_scale_max_observed"]) == 1.0
    assert float(summary["cavity_volume_scale_min_observed"]) == 0.6
    assert float(summary["cavity_volume_scale_max_observed"]) == 1.0
    assert float(summary["funnel_aperture_scale_min_observed"]) == 0.35
    assert float(summary["funnel_aperture_scale_max_observed"]) == 1.0
    assert float(summary["max_abs_mantle_radius_rate"]) > 0.0
    assert float(summary["max_abs_cavity_volume_rate"]) > 0.0
    assert float(summary["max_abs_funnel_aperture_rate"]) > 0.0


def test_step32_step31_regression_guard_is_valid():
    summary = read_json("outputs/step32_step31_regression_guard/step31_regression_guard.json")
    rows = read_csv_rows("outputs/step32_step31_regression_guard/step31_regression_guard.csv")
    assert int(summary["row_count"]) == 7
    assert int(summary["pass_count"]) == 7
    assert int(summary["step31_projection_row_count"]) == 21
    assert int(summary["step31_static_driver_row_count"]) == 4
    assert int(summary["step31_static_driver_stable_count"]) == 4
    assert int(summary["step31_quality_report_count"]) == 4
    assert int(summary["step31_large_file_count"]) == 0
    assert int(summary["step31_vtr_count"]) == 0
    assert int(summary["step31_particle_npy_count"]) == 0
    assert all(as_bool(row["pass"]) for row in rows)


def test_step32_default_modes_remain_unchanged():
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


def test_step32_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "README.md",
            "docs/08_roadmap.md",
            "docs/09_api_reference.md",
            "docs/11_artifact_policy.md",
            "docs/12_geometry_ingestion.md",
            "docs/30_controlled_squid_proxy_region_geometry.md",
            "docs/31_controlled_squid_proxy_region_static_driver.md",
            "docs/32_controlled_squid_proxy_kinematics_schedule.md",
            "STEP32_CONTROLLED_SQUID_PROXY_KINEMATICS_SCHEDULE_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step32_artifact_budget_is_valid():
    summary = read_json("outputs/step32_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step32_total_size_mb"]) < 3.0
    assert float(summary["total_size_mb"]) < 190.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["step32_vtr_count"]) == 0
    assert int(summary["step32_particle_npy_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    manifest_rows = read_csv_rows("outputs/step32_artifact_manifest/artifact_manifest.csv")
    step32_paths = [row["path"] for row in manifest_rows if row["path"].startswith("outputs/step32")]
    assert not [path for path in step32_paths if path.endswith(".vtr")]
    assert not [path for path in step32_paths if path.endswith(".npy") and "particle" in path.lower()]


def test_step32_report_acceptance_complete():
    report = read_text("STEP32_CONTROLLED_SQUID_PROXY_KINEMATICS_SCHEDULE_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Schedule Config Validation",
        "## 5. Generated Kinematics Schedule",
        "## 6. Schedule Quality",
        "## 7. Schedule Repeatability",
        "## 8. Region Mapping Validation",
        "## 9. Schedule Envelope Summary",
        "## 10. Step 31 Regression Guard",
        "## 11. Artifact Manifest Summary",
        "## 12. Verification Commands",
        "## 13. GitHub Sync Information",
        "## 14. Acceptance Checklist",
        "## 15. Decision For Step 33",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] schedule config validation passes",
        "- [x] region config path exists",
        "- [x] geometry config path exists",
        "- [x] cycle period is positive",
        "- [x] sample count is sufficient",
        "- [x] phase ranges are valid",
        "- [x] scale ranges are valid",
        "- [x] generated kinematics schedule has expected row count",
        "- [x] phase samples are monotonic",
        "- [x] endpoint repeatability passes",
        "- [x] mantle radius scale is finite and bounded",
        "- [x] cavity volume scale is finite and bounded",
        "- [x] funnel aperture scale is finite and bounded",
        "- [x] mantle radius derivative is finite",
        "- [x] cavity volume derivative is finite",
        "- [x] funnel aperture derivative is finite",
        "- [x] contraction phase volume-rate check passes",
        "- [x] refill phase volume-rate check passes",
        "- [x] schedule repeatability hash passes",
        "- [x] mantle schedule hash repeats",
        "- [x] cavity schedule hash repeats",
        "- [x] funnel schedule hash repeats",
        "- [x] region mapping validation passes",
        "- [x] mantle_outer region is mapped",
        "- [x] mantle_cavity_proxy region is mapped",
        "- [x] funnel_outlet_proxy region is mapped",
        "- [x] driver integration flag is false",
        "- [x] actuation enabled flag is false",
        "- [x] schedule envelope summary passes",
        "- [x] Step 31 regression guard passes",
        "- [x] default quality_check_enabled remains false",
        "- [x] default quality_check_strict remains false",
        "- [x] default reaction_transfer_mode remains engineering",
        "- [x] no FSIDriver3D integration",
        "- [x] no moving wall velocity application",
        "- [x] no mantle contraction driver claim",
        "- [x] no funnel actuation driver claim",
        "- [x] no squid swimming claim",
        "- [x] no real squid validation claim",
        "- [x] no new FSI physics",
        "- [x] no moving bounce-back formula changes",
        "- [x] no LBM formula changes",
        "- [x] no MPM constitutive formula changes",
        "- [x] no projection formula changes",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] no Step 32 `.vtr` outputs",
        "- [x] no Step 32 particle `.npy` outputs",
        "- [x] artifact `large_file_count == 0`",
        "- [x] Step 32 output total-size budget passes",
        "- [x] repo artifact summary `total_size_mb < 190`",
        "- [x] `logs/step32_pytest.log` exists",
        "- [x] pytest -q passes",
        "- [x] Step 32 contract test passes",
        "- [x] `git diff --check` passes",
        "- [x] staged whitespace check passes",
        "- [x] pre-push hook passes",
        "- [x] Step 32 artifacts are pushed to `origin/main`",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []

    assert (ROOT / "logs/step32_pytest.log").is_file()
    for path, marker in STEP32_LOG_MARKERS.items():
        assert (ROOT / path).is_file(), path
        assert marker in read_text(path), path


def test_step32_no_driver_integration_claims():
    report = read_text("STEP32_CONTROLLED_SQUID_PROXY_KINEMATICS_SCHEDULE_REPORT.md")
    assert "No FSIDriver3D, LBM, MPM, moving bounce-back, link-area, or projection formula files were edited." in report
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
