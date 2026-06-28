import csv
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_PLANE = "regularized_plane_flux_controlled_pressure_outlet"
STEP139_PHASE = "planeflux_final48"
STEP139_ROLE = "final_evidence_candidate_48"
SOURCE_ROW_NAME = (
    "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075"
    "_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70"
    "_ramp85_target0p80_out5_250step_high_authority"
)
SOURCE_SOLVER_STATE_HASH = "34437ee966ac063d03d80bd4a9c9dea30961897cbb87d41cc5c7de1571ef3ed8"
SOURCE_RUN_MANIFEST_HASH = "e689ad17b0de0f478d57ef9d419e2ed10579692cfb94866dbc1095b5c7239969"
SOURCE_CODE_COMMIT = "f0284d3f6207eb1c9341dfc9906293b651c6b0f7"


def _step139_spec(**overrides):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import Step120RunSpec

    base = {
        "name": (
            "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075"
            "_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70"
            "_ramp85_target0p80_500step_final"
        ),
        "nx": 48,
        "ny": 48,
        "nz": 48,
        "n_steps": 500,
        "output_interval": 10,
        "failure_check_interval": 5,
        "checkpoint_every": 50,
        "open_boundary_semantics": REGULARIZED_PLANE,
        "geometry_mode": "duct_only",
        "requested_nx": 48,
        "requested_n_steps": 500,
        "allow_large_real_run_without_flag": True,
        "row_role": STEP139_ROLE,
        "open_boundary_flux_feedback_gain_u": 0.75,
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_flux_filter_alpha": 0.02,
        "open_boundary_flux_correction_cap_u": 0.0075,
        "open_boundary_flux_feedback_delta_cap_u": 0.0005,
        "open_boundary_flux_feedback_slew_alpha": 0.5,
        "open_boundary_convective_blend_weight": 0.02,
        "open_boundary_flux_control_measure_plane_offset": 2,
        "open_boundary_flux_control_target_scale": 0.80,
        "open_boundary_outlet_flux_drop_guard_enabled": True,
        "open_boundary_outlet_flux_drop_guard_min_ratio": 0.70,
        "open_boundary_inlet_ramp_steps": 85,
        "open_boundary_inlet_ramp_profile": "linear",
        "niu": 0.10,
        "source_step": 138,
        "source_row_name": SOURCE_ROW_NAME,
        "source_solver_state_hash": SOURCE_SOLVER_STATE_HASH,
        "source_run_manifest_hash": SOURCE_RUN_MANIFEST_HASH,
        "source_code_commit": SOURCE_CODE_COMMIT,
        "artifact_scope_note": (
            "Step139 single 48^3 500-step final evidence for the Step138 "
            "passing row; not selected96, selected-static, FSI, or Fluent validation"
        ),
    }
    base.update(overrides)
    return Step120RunSpec(**base)


def _step139_row(name, semantics, **overrides):
    row = {
        "name": name,
        "row_role": STEP139_ROLE,
        "geometry_mode": "duct_only",
        "lbm_open_boundary_semantics": semantics,
        "requested_nx": 48,
        "executed_nx": 48,
        "requested_n_steps": 500,
        "steps_completed": 500,
        "requested_window_completed": True,
        "step120_validation_claimed": True,
        "simulation_backed_artifact": True,
        "not_used_for_validation": False,
        "finite_pass": True,
        "density_gate_pass": True,
        "mass_drift_gate_pass": True,
        "population_gate_pass": True,
        "mach_gate_pass": True,
        "first_failure_step": None,
        "first_failure_reason": None,
        "stop_reason": None,
        "flux_balance_reported": True,
        "flux_imbalance_rel_tail_mean": 0.088,
        "flux_imbalance_rel_tail_max": 0.180,
        "outlet_to_inlet_flux_ratio_tail_mean": 1.05,
        "midplane_to_inlet_flux_ratio_tail_mean": 0.94,
        "outlet_flux_tail_cv": 0.09,
        "flow_development_gate_pass": True,
        "candidate_mass_acceptance_observed_abs": 0.003,
        "candidate_mass_acceptance_gate_pass": True,
        "limiter_activation_fraction": 0.0,
        "limiter_activation_gate_pass": True,
        "runtime_s": 1.0,
        "open_boundary_flux_feedback_gain_u": 0.75,
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_flux_filter_alpha": 0.02,
        "open_boundary_flux_correction_cap_u": 0.0075,
        "open_boundary_flux_feedback_delta_cap_u": 0.0005,
        "open_boundary_flux_feedback_slew_alpha": 0.50,
        "open_boundary_convective_blend_weight": 0.02,
        "open_boundary_flux_control_measure_plane_offset": 2,
        "open_boundary_flux_control_target_scale": 0.80,
        "open_boundary_outlet_flux_drop_guard_enabled": True,
        "open_boundary_outlet_flux_drop_guard_min_ratio": 0.70,
        "open_boundary_inlet_ramp_steps": 85,
        "open_boundary_inlet_ramp_profile": "linear",
        "step138_high_authority_outlet_candidate": False,
        "step139_planeflux_final48_candidate": True,
        "source_step": 138,
        "source_row_name": SOURCE_ROW_NAME,
        "source_solver_state_hash": SOURCE_SOLVER_STATE_HASH,
        "source_run_manifest_hash": SOURCE_RUN_MANIFEST_HASH,
        "source_code_commit": SOURCE_CODE_COMMIT,
        "selected96_claim_allowed": False,
        "validation_claim_allowed": False,
        "lbm_niu": 0.10,
        "solver_state_hash": "step139-final-hash",
        "run_manifest_hash": "step139-run-hash",
    }
    row.update(overrides)
    return row


def test_step139_phase_is_single_exact_500_step_final_evidence_row(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        run_manifest_hash_for_spec,
        solver_state_hash_for_spec,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        CANDIDATE_SEMANTICS,
        REPAIRED_CANDIDATE_SEMANTICS,
        resolve_step121_phase_specs,
        step121_plane_flux_final_48_specs,
        step121_plane_flux_high_authority_48_specs,
        write_step121_campaign_manifest,
    )

    specs = step121_plane_flux_final_48_specs(output_interval=10)
    assert resolve_step121_phase_specs(STEP139_PHASE, output_interval=10) == specs
    assert len(specs) == 1

    spec = specs[0]
    assert spec.name == (
        "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075"
        "_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70"
        "_ramp85_target0p80_500step_final"
    )
    assert spec.row_role == STEP139_ROLE
    assert spec.open_boundary_semantics == REGULARIZED_PLANE
    assert REGULARIZED_PLANE not in CANDIDATE_SEMANTICS
    assert REGULARIZED_PLANE not in REPAIRED_CANDIDATE_SEMANTICS
    assert (spec.nx, spec.ny, spec.nz) == (48, 48, 48)
    assert spec.requested_nx == 48
    assert spec.n_steps == 500
    assert spec.requested_n_steps == 500
    assert spec.output_interval == 10
    assert spec.open_boundary_inlet_ramp_steps == 85
    assert spec.open_boundary_flux_control_target_scale == pytest.approx(0.80)
    assert spec.open_boundary_flux_feedback_gain_u == pytest.approx(0.75)
    assert spec.open_boundary_flux_feedback_gain_rho == pytest.approx(0.001)
    assert spec.open_boundary_flux_filter_alpha == pytest.approx(0.02)
    assert spec.open_boundary_flux_correction_cap_u == pytest.approx(0.0075)
    assert spec.open_boundary_flux_feedback_delta_cap_u == pytest.approx(0.0005)
    assert spec.open_boundary_flux_feedback_slew_alpha == pytest.approx(0.50)
    assert spec.open_boundary_flux_control_measure_plane_offset == 2
    assert spec.open_boundary_outlet_flux_drop_guard_enabled is True
    assert spec.open_boundary_outlet_flux_drop_guard_min_ratio == pytest.approx(0.70)
    assert spec.niu == pytest.approx(0.10)
    assert spec.source_step == 138
    assert spec.source_row_name == SOURCE_ROW_NAME
    assert spec.source_solver_state_hash == SOURCE_SOLVER_STATE_HASH
    assert spec.source_run_manifest_hash == SOURCE_RUN_MANIFEST_HASH
    assert spec.source_code_commit == SOURCE_CODE_COMMIT
    assert "selected96" in spec.artifact_scope_note
    assert "Fluent validation" in spec.artifact_scope_note

    step138_source = next(
        item
        for item in step121_plane_flux_high_authority_48_specs(output_interval=5)
        if int(item.open_boundary_inlet_ramp_steps) == 85
        and item.open_boundary_flux_control_target_scale == pytest.approx(0.80)
        and item.open_boundary_flux_feedback_gain_u == pytest.approx(0.75)
        and item.open_boundary_flux_correction_cap_u == pytest.approx(0.0075)
    )
    assert solver_state_hash_for_spec(step138_source) == SOURCE_SOLVER_STATE_HASH
    assert run_manifest_hash_for_spec(step138_source) == SOURCE_RUN_MANIFEST_HASH

    manifest = write_step121_campaign_manifest(tmp_path, specs, phase=STEP139_PHASE)
    expected = manifest["expected_rows"][spec.name]
    assert manifest["phase_history"][-1] == STEP139_PHASE
    assert expected["row_role"] == STEP139_ROLE
    assert expected["source_step"] == 138
    assert expected["source_solver_state_hash"] == SOURCE_SOLVER_STATE_HASH
    assert expected["source_run_manifest_hash"] == SOURCE_RUN_MANIFEST_HASH
    assert expected["source_code_commit"] == SOURCE_CODE_COMMIT


def test_step139_rows_do_not_enable_selected96_even_if_all_final_gates_pass():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    row = _step139_row(
        "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075"
        "_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70"
        "_ramp85_target0p80_500step_final",
        REGULARIZED_PLANE,
    )

    selection = select_step121_best_boundary([row])

    assert selection["best_boundary_selected"] is False
    assert selection["validation_claim_allowed"] is False
    assert row["selected96_claim_allowed"] is False
    assert row["validation_claim_allowed"] is False


def test_step139_report_fields_and_flow_diagnostics_preserve_provenance(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS,
        _boundary_report,
        _flow_development_diagnostic_record,
        _metadata,
        _write_flow_development_diagnostics,
    )

    spec = _step139_spec()
    tau_report = {
        "lbm_niu": 0.10,
        "tau": 0.8,
        "lbm_relaxation_semantics": "legacy_external_solver_parameter",
    }
    metadata = _metadata(spec, tau_report, skipped=False, runtime_s=1.0, stop_reason=None, restored_checkpoint=None)
    boundary = _boundary_report(spec)
    for report in [metadata, boundary]:
        assert report["step139_planeflux_final48_candidate"] is True
        assert report["source_step"] == 138
        assert report["source_row_name"] == SOURCE_ROW_NAME
        assert report["source_solver_state_hash"] == SOURCE_SOLVER_STATE_HASH
        assert report["source_run_manifest_hash"] == SOURCE_RUN_MANIFEST_HASH
        assert report["source_code_commit"] == SOURCE_CODE_COMMIT

    records = []
    for step, profile in [
        (400, {"24": 40.0, "36": 39.0, "47": 38.0}),
        (450, {"24": 39.0, "36": 38.0, "47": 37.0}),
        (500, {"24": 38.0, "36": 37.0, "47": 36.0}),
    ]:
        records.append(
            _flow_development_diagnostic_record(
                {
                    "step": step,
                    "inlet_flux": 100.0,
                    "outlet_flux": profile["47"],
                    "midplane_flux": profile["36"],
                    "mass_total_delta_rel": 0.001,
                    "sampled_x_profile_flux": json.dumps(profile, sort_keys=True),
                },
                spec,
                {
                    "flow_correction_gain_effective_step": 0.75,
                    "flow_correction_cap_u": 0.0075,
                    "controller_target_outlet_flux": 80.0,
                    "controller_measured_outlet_flux": profile["47"],
                    "controller_raw_flux_error": 80.0 - profile["47"],
                    "controller_filtered_flux_error": 0.20,
                    "controller_u_feedback": -0.00075,
                    "controller_density_feedback": -0.00001,
                    "controller_delta_cap_u": 0.0005,
                    "controller_saturation_active_step": 0,
                    "controller_saturation_count_run": 0,
                    "controller_saturation_fraction_run": 0.0,
                    "controller_drop_guard_activation_count_run": 0,
                    "controller_measure_plane_offset": 2,
                    "controller_target_scale": 0.80,
                },
            )
        )

    assert "step139_planeflux_final48_candidate" in FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS
    assert records[-1]["step139_planeflux_final48_candidate"] is True
    assert records[-1]["step138_high_authority_outlet_candidate"] is False
    assert records[-1]["source_step"] == 138
    assert records[-1]["source_row_name"] == SOURCE_ROW_NAME
    assert records[-1]["source_solver_state_hash"] == SOURCE_SOLVER_STATE_HASH
    assert records[-1]["source_run_manifest_hash"] == SOURCE_RUN_MANIFEST_HASH
    assert records[-1]["source_code_commit"] == SOURCE_CODE_COMMIT
    assert records[-1]["selected96_claim_allowed"] is False
    assert records[-1]["validation_claim_allowed"] is False

    _write_flow_development_diagnostics(tmp_path, records)

    with (tmp_path / "flow_development_diagnostics.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[-1]["step139_planeflux_final48_candidate"] == "True"
    assert rows[-1]["source_solver_state_hash"] == SOURCE_SOLVER_STATE_HASH
    assert rows[-1]["selected96_claim_allowed"] == "False"

    summary = json.loads((tmp_path / "flow_development_diagnostics_summary.json").read_text(encoding="utf-8"))
    assert summary["step"] == 139
    assert summary["final"]["step139_planeflux_final48_candidate"] is True
    assert summary["selected96_claim_allowed"] is False


def test_step139_artifact_gate_contract_accepts_only_full_final_evidence():
    row = _step139_row(
        "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075"
        "_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70"
        "_ramp85_target0p80_500step_final",
        REGULARIZED_PLANE,
    )

    assert row["steps_completed"] == 500
    assert row["requested_window_completed"] is True
    assert row["simulation_backed_artifact"] is True
    assert row["finite_pass"] is True
    assert row["density_gate_pass"] is True
    assert row["population_gate_pass"] is True
    assert row["mach_gate_pass"] is True
    assert row["mass_drift_gate_pass"] is True
    assert row["first_failure_step"] is None
    assert row["first_failure_reason"] is None
    assert row["candidate_mass_acceptance_gate_pass"] is True
    assert abs(float(row["candidate_mass_acceptance_observed_abs"])) < 0.005
    assert row["flow_development_gate_pass"] is True
    assert 0.80 <= float(row["outlet_to_inlet_flux_ratio_tail_mean"]) <= 1.20
    assert 0.80 <= float(row["midplane_to_inlet_flux_ratio_tail_mean"]) <= 1.20
    assert float(row["flux_imbalance_rel_tail_mean"]) < 0.10
    assert float(row["flux_imbalance_rel_tail_max"]) < 0.20
    assert float(row["outlet_flux_tail_cv"]) < 0.10
    assert float(row["limiter_activation_fraction"]) <= 0.05
    assert row["selected96_claim_allowed"] is False
    assert row["validation_claim_allowed"] is False
