import hashlib
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


STEP141_DECISION = ROOT / "outputs" / "step141_density_feedback_isolation" / "step141_decision_summary.json"
STEP142_OUTPUT_ROOT = ROOT / "outputs" / "step142_mass_neutral_plane_flux_design"
STEP142_SUMMARY = STEP142_OUTPUT_ROOT / "step142_design_readiness_report.json"
STEP142_MARKDOWN = STEP142_OUTPUT_ROOT / "step142_design_readiness_report.md"
STEP142_GOAL = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "142" / "goal.md"
STEP142_REPORT = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "142" / "report.md"
STEP142_DESIGN = (
    ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "142" / "mass_neutral_plane_flux_design.md"
)
STEP121_DRIVER = ROOT / "experiments" / "steps" / "step121_lbm_boundary_real_campaign_and_gate_correction.py"

MASS_NEUTRAL_FIELDS = [
    "open_boundary_mass_neutral_flux_control_enabled",
    "open_boundary_mass_neutral_flux_control_mode",
    "open_boundary_mass_neutral_mass_error_gain",
    "open_boundary_mass_neutral_mass_error_cap",
    "open_boundary_mass_neutral_correction_blend",
    "open_boundary_mass_neutral_reference_mass_mode",
]


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_lbm_config_declares_default_disabled_mass_neutral_surface():
    from src.mpm_lbm.sim.lbm.config import (
        LBMConfig,
        VALID_OPEN_BOUNDARY_MASS_NEUTRAL_FLUX_CONTROL_MODES,
        VALID_OPEN_BOUNDARY_MASS_NEUTRAL_REFERENCE_MASS_MODES,
    )

    cfg = LBMConfig(nx=4, ny=4, nz=4)

    assert VALID_OPEN_BOUNDARY_MASS_NEUTRAL_FLUX_CONTROL_MODES == (
        "disabled",
        "global_mass_error_density_offset",
        "outlet_population_projection_report_only",
    )
    assert VALID_OPEN_BOUNDARY_MASS_NEUTRAL_REFERENCE_MASS_MODES == ("initial",)
    assert cfg.open_boundary_mass_neutral_flux_control_enabled is False
    assert cfg.open_boundary_mass_neutral_flux_control_mode == "disabled"
    assert cfg.open_boundary_mass_neutral_mass_error_gain == 0.0
    assert cfg.open_boundary_mass_neutral_mass_error_cap == 0.0
    assert cfg.open_boundary_mass_neutral_correction_blend == 0.0
    assert cfg.open_boundary_mass_neutral_reference_mass_mode == "initial"

    with pytest.raises(ValueError, match="mass_neutral_flux_control_mode"):
        LBMConfig(nx=4, ny=4, nz=4, open_boundary_mass_neutral_flux_control_mode="bad")
    with pytest.raises(ValueError, match="mass_neutral_reference_mass_mode"):
        LBMConfig(nx=4, ny=4, nz=4, open_boundary_mass_neutral_reference_mass_mode="runtime_initial")
    with pytest.raises(ValueError, match="mass_neutral_mass_error_gain"):
        LBMConfig(nx=4, ny=4, nz=4, open_boundary_mass_neutral_mass_error_gain=-1.0)
    with pytest.raises(ValueError, match="mass_neutral_mass_error_cap"):
        LBMConfig(nx=4, ny=4, nz=4, open_boundary_mass_neutral_mass_error_cap=-1.0)
    with pytest.raises(ValueError, match="mass_neutral_correction_blend"):
        LBMConfig(nx=4, ny=4, nz=4, open_boundary_mass_neutral_correction_blend=1.5)
    with pytest.raises(ValueError, match="disabled"):
        LBMConfig(nx=4, ny=4, nz=4, open_boundary_mass_neutral_flux_control_enabled=True)


def test_step120_reports_mass_neutral_surface_without_changing_solver_state_hash_fields():
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _lbm_config_report
    from experiments.steps.step118_lbm_open_boundary_stability_repair import _make_lbm_config
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        SOLVER_STATE_HASH_FIELDS,
        Step120RunSpec,
        _boundary_report,
        _metadata,
        _summary_row,
        _tau_feasibility_report,
    )

    spec = Step120RunSpec(
        name="tiny_step142_mass_neutral_contract",
        nx=5,
        ny=4,
        nz=4,
        n_steps=1,
        output_interval=1,
        open_boundary_semantics="regularized_plane_flux_controlled_pressure_outlet",
        geometry_mode="duct_only",
        checkpoint_every=0,
        requested_nx=5,
        requested_n_steps=1,
        allow_large_real_run_without_flag=True,
        not_used_for_validation=True,
        step119_required_row=False,
        step120_required_row=False,
        open_boundary_mass_neutral_flux_control_mode="outlet_population_projection_report_only",
    )
    tau_report = _tau_feasibility_report(spec)
    config = _make_lbm_config(spec, tau_report)
    config_report = _lbm_config_report(config, spec, tau_report)["lbm_config"]
    boundary = _boundary_report(spec)
    metadata = _metadata(spec, tau_report, skipped=True, runtime_s=0.0, stop_reason="test", restored_checkpoint=None)
    summary = _summary_row(
        spec,
        steps_completed=0,
        requested_window_completed=False,
        finite_pass=True,
        density_gate_pass=True,
        mass_drift_gate_pass=False,
        population_gate_pass=True,
        mach_gate_pass=True,
        first_failure_step=None,
        first_failure_reason=None,
        flux_imbalance_rel_final=None,
        flux_imbalance_rel_tail_mean=None,
        flux_imbalance_rel_tail_max=None,
        inlet_flux_tail_mean=None,
        outlet_flux_tail_mean=None,
        outlet_flux_tail_cv=None,
        outlet_to_inlet_flux_ratio_tail_mean=None,
        midplane_to_inlet_flux_ratio_tail_mean=None,
        flow_development_gate_pass=False,
        mass_total_delta_rel_final=None,
        mach_proxy_observed_max=None,
        tau_margin_pass=tau_report["tau_margin_pass"],
        skipped_due_to_tau_margin=True,
        stop_reason="test",
        row_source="unit_test",
        step120_validation_claimed=False,
        runtime_s=0.0,
        limiter_summary={},
        simulation_backed_artifact=False,
        flux_balance_reported=False,
        checkpoint_available=False,
        hard_stop_fields={},
        candidate_mass_fields={},
    )

    assert not any(field in SOLVER_STATE_HASH_FIELDS for field in MASS_NEUTRAL_FIELDS)
    for field in MASS_NEUTRAL_FIELDS:
        assert getattr(spec, field) == boundary[field]
        assert getattr(spec, field) == metadata[field]
        assert getattr(spec, field) == summary[field]
        assert getattr(config, field) == config_report[field]

    assert boundary["mass_neutral_runtime_behavior_active"] is False
    assert summary["step142_mass_neutral_plane_flux_design_surface"] is True
    assert metadata["step142_mass_neutral_plane_flux_design_surface"] is True


def test_fluid_mass_neutral_surface_is_report_only_for_step142():
    source = (ROOT / "src" / "mpm_lbm" / "sim" / "lbm" / "fluid.py").read_text(encoding="utf-8")

    assert "open_boundary_mass_neutral_flux_control_enabled" in source
    assert "mass_neutral_runtime_behavior_active" in source
    assert "mass_neutral_projection_report_only" in source

    population_start = source.index("def _regularized_plane_flux_controlled_population")
    population_end = source.index("def _convective_plane_flux_controlled_damped_population", population_start)
    population_block = source[population_start:population_end]
    assert "open_boundary_mass_neutral_mass_error_gain" not in population_block
    assert "open_boundary_mass_neutral_mass_error_cap" not in population_block


def test_step121_does_not_expose_step142_real_run_phase():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        SELECTED_CHAIN_ROLES,
        resolve_step121_phase_specs,
    )

    source = STEP121_DRIVER.read_text(encoding="utf-8")
    forbidden_phases = [
        "planeflux_mass_neutral_design48",
        "step142_mass_neutral48",
        "mass_neutral_design_diagnostic_48",
    ]
    for forbidden in forbidden_phases:
        assert forbidden not in source
        assert forbidden not in SELECTED_CHAIN_ROLES
        with pytest.raises(ValueError, match="unknown Step121 phase"):
            resolve_step121_phase_specs(forbidden)


def test_step142_report_generator_reads_step141_and_blocks_500_and_selected96(tmp_path):
    from experiments.steps.step142_mass_neutral_plane_flux_design_report import (
        run_step142_mass_neutral_design_report,
    )

    summary = run_step142_mass_neutral_design_report(
        step141_decision=STEP141_DECISION,
        output_dir=tmp_path,
        force=True,
    )

    assert summary["step"] == 142
    assert summary["source_step"] == 141
    assert summary["status"] == "design_ready"
    assert summary["source_step141_decision_hash"] == _sha256(STEP141_DECISION)
    assert summary["source_step141_decision_case"] == "density_feedback_isolation_insufficient"
    assert summary["step142_real_48_run_executed"] is False
    assert summary["step142_single_500step_final_evidence_proposal_allowed"] is False
    assert summary["selected96_execution_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["step143_250step_diagnostic_proposal_allowed"] is True
    assert summary["recommended_next_phase_name"] == "planeflux_mass_neutral_design48"
    assert summary["recommended_design"]["primary_mode"] == "global_mass_error_density_offset"
    assert (tmp_path / "step142_design_readiness_report.json").is_file()
    assert (tmp_path / "step142_design_readiness_report.md").is_file()


def test_step142_report_generator_blocks_missing_or_wrong_step141_decision(tmp_path):
    from experiments.steps.step142_mass_neutral_plane_flux_design_report import (
        run_step142_mass_neutral_design_report,
    )

    missing = run_step142_mass_neutral_design_report(
        step141_decision=tmp_path / "missing.json",
        output_dir=tmp_path / "missing_out",
        force=True,
    )
    assert missing["status"] == "missing_input"
    assert missing["step143_250step_diagnostic_proposal_allowed"] is False
    assert missing["selected96_execution_allowed"] is False

    wrong_decision = tmp_path / "wrong.json"
    wrong_decision.write_text(
        json.dumps(
            {
                "step": 141,
                "status": "decision_ready",
                "decision_case": "density_feedback_contributes_to_mass_stationarity_drift",
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    wrong = run_step142_mass_neutral_design_report(
        step141_decision=wrong_decision,
        output_dir=tmp_path / "wrong_out",
        force=True,
    )
    assert wrong["status"] == "blocked_by_step141_decision"
    assert wrong["step143_250step_diagnostic_proposal_allowed"] is False
    assert wrong["selected96_execution_allowed"] is False


def test_committed_step142_artifacts_and_current_docs_are_design_only():
    summary = _read_json(STEP142_SUMMARY)
    markdown = STEP142_MARKDOWN.read_text(encoding="utf-8")
    report = STEP142_REPORT.read_text(encoding="utf-8")
    design = STEP142_DESIGN.read_text(encoding="utf-8")
    active_campaign = _read_json(ROOT / "docs" / "current" / "ACTIVE_CAMPAIGN.json")
    reading_order = (ROOT / "docs" / "current" / "READING_ORDER.md").read_text(encoding="utf-8")
    status = (ROOT / "docs" / "current" / "STATUS.md").read_text(encoding="utf-8")
    gates = (ROOT / "docs" / "current" / "VALIDATION_GATES.md").read_text(encoding="utf-8")

    assert STEP142_GOAL.is_file()
    assert summary["status"] == "design_ready"
    assert summary["source_step141_decision_hash"] == _sha256(STEP141_DECISION)
    assert summary["step142_real_48_run_executed"] is False
    assert summary["step142_single_500step_final_evidence_proposal_allowed"] is False
    assert summary["selected96_execution_allowed"] is False
    assert "no real Step142 48^3 row was run" in markdown
    assert "Design A" in design
    assert "Step142 did not run a 500-step row" in report
    assert active_campaign["state"] == "48_candidates_failed"
    assert active_campaign["step142_design_artifact_root"] == "outputs/step142_mass_neutral_plane_flux_design"
    assert "24f5bef3d10e6102fbc2a1cd28c383df81ad7bf3" in active_campaign["final_repository_head_after_step141_push"]
    assert "steps/142/report.md" in reading_order
    assert "Step142" in status
    assert "Step142" in gates
    assert "selected 96^3 execution remains blocked" in gates
