import csv
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_PLANE = "regularized_plane_flux_controlled_pressure_outlet"
CONVECTIVE_PLANE = "convective_plane_flux_controlled_damped_outlet"
STEP133_SEMANTICS = {REGULARIZED_PLANE, CONVECTIVE_PLANE}


def _step133_row(name, semantics, *, solver_state_hash="step133-hash"):
    return {
        "name": name,
        "row_role": "plane_flux_control_candidate_48",
        "geometry_mode": "duct_only",
        "lbm_open_boundary_semantics": semantics,
        "requested_nx": 48,
        "executed_nx": 48,
        "requested_n_steps": 250,
        "steps_completed": 250,
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
        "flux_imbalance_rel_tail_mean": 0.04,
        "flux_imbalance_rel_tail_max": 0.08,
        "inlet_flux_tail_mean": 42.0,
        "outlet_flux_tail_mean": 41.5,
        "outlet_to_inlet_flux_ratio_tail_mean": 0.988,
        "midplane_to_inlet_flux_ratio_tail_mean": 0.99,
        "outlet_flux_tail_cv": 0.02,
        "flow_development_gate_pass": True,
        "flow_development_rejection_reasons": [],
        "mass_total_delta_rel_final": 0.001,
        "candidate_mass_acceptance_observed_abs": 0.001,
        "candidate_mass_acceptance_gate_pass": True,
        "mach_proxy_observed_max": 0.08,
        "limiter_activation_fraction": 0.0,
        "limiter_activation_gate_pass": True,
        "runtime_s": 1.0,
        "open_boundary_limiter_enabled": False,
        "open_boundary_rho_min": 0.91,
        "open_boundary_rho_max": 1.09,
        "open_boundary_u_max": 0.08,
        "open_boundary_noneq_cap": 0.17,
        "open_boundary_population_floor": None,
        "open_boundary_flux_feedback_gain_u": 0.25,
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_flux_filter_alpha": 0.02,
        "open_boundary_flux_correction_cap_u": 0.005,
        "open_boundary_flux_feedback_delta_cap_u": 0.0005,
        "open_boundary_flux_feedback_slew_alpha": 0.5,
        "open_boundary_convective_blend_weight": 0.02,
        "controller_u_feedback_tail_mean": 0.001,
        "controller_u_feedback_tail_std": 0.0001,
        "controller_saturation_fraction_tail": 0.0,
        "density_feedback_tail_abs_max": 0.00002,
        "inlet_u_lbm": 0.031,
        "outlet_rho": 0.997,
        "lbm_niu": 0.023,
        "lbm_viscosity_semantics": "legacy_external",
        "lbm_relaxation_semantics": "legacy_external_solver_parameter",
        "tau": 0.572,
        "config_hash": solver_state_hash,
        "solver_state_hash": solver_state_hash,
    }


def _references():
    return [
        _step133_row(
            "duct_only_48_legacy_boundary_500step_reference_real",
            "equilibrium_all_population_reset",
            solver_state_hash="legacy-reference-hash",
        )
        | {"row_role": "reference_48", "requested_n_steps": 500, "steps_completed": 500},
        _step133_row(
            "duct_only_48_regularized_boundary_500step_reference_real",
            "regularized_velocity_pressure",
            solver_state_hash="regularized-reference-hash",
        )
        | {"row_role": "reference_48", "requested_n_steps": 500, "steps_completed": 500},
    ]


def _failed_step127_candidates():
    failed_regularized = _step133_row(
        "duct_only_48_regularized_limited_boundary_500step_real",
        "regularized_velocity_pressure_limited",
        solver_state_hash="limited-step127-hash",
    )
    failed_regularized.update(
        {
            "row_role": "candidate_48",
            "requested_n_steps": 500,
            "steps_completed": 500,
            "flux_imbalance_rel_tail_mean": 0.51165,
            "flux_imbalance_rel_tail_max": 0.866,
            "outlet_to_inlet_flux_ratio_tail_mean": 1.4127,
            "midplane_to_inlet_flux_ratio_tail_mean": 1.306,
            "outlet_flux_tail_cv": 0.452,
            "flow_development_gate_pass": False,
        }
    )
    failed_convective = _step133_row(
        "duct_only_48_convective_outlet_boundary_500step_real",
        "convective_pressure_outlet_experimental",
        solver_state_hash="convective-step127-hash",
    )
    failed_convective.update(
        {
            "row_role": "candidate_48",
            "requested_n_steps": 500,
            "steps_completed": 200,
            "requested_window_completed": False,
            "step120_validation_claimed": False,
            "first_failure_step": 200,
            "first_failure_reason": "mass_drift",
            "stop_reason": "lightweight_failure:mass_drift",
            "mass_total_delta_rel_final": 0.046,
            "flow_development_gate_pass": False,
        }
    )
    return [failed_regularized, failed_convective]


def _step133_spec(**overrides):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import Step120RunSpec

    base = {
        "name": "duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_rho0p001_alpha0p02_du0p0005_slew0p50_250step_triage",
        "nx": 48,
        "ny": 48,
        "nz": 48,
        "n_steps": 250,
        "output_interval": 25,
        "failure_check_interval": 5,
        "checkpoint_every": 50,
        "open_boundary_semantics": REGULARIZED_PLANE,
        "geometry_mode": "duct_only",
        "requested_nx": 48,
        "requested_n_steps": 250,
        "allow_large_real_run_without_flag": True,
        "row_role": "plane_flux_control_candidate_48",
        "open_boundary_flux_feedback_gain_u": 0.25,
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_flux_filter_alpha": 0.02,
        "open_boundary_flux_correction_cap_u": 0.005,
        "open_boundary_flux_feedback_delta_cap_u": 0.0005,
        "open_boundary_flux_feedback_slew_alpha": 0.5,
        "open_boundary_convective_blend_weight": 0.02,
        "artifact_scope_note": "Step133 bounded 48^3 mass-damped plane-flux triage; not a selected96 enabling row",
    }
    base.update(overrides)
    return Step120RunSpec(**base)


def test_step133_mass_damped_phase_is_distinct_48_triage_surface():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        resolve_step121_phase_specs,
        step121_plane_flux_mass_damped_48_specs,
        step121_plane_flux_sweep_48_specs,
    )

    specs = step121_plane_flux_mass_damped_48_specs(output_interval=25)
    sweep_names = {spec.name for spec in step121_plane_flux_sweep_48_specs(output_interval=25)}

    assert resolve_step121_phase_specs("planeflux_mass_damped48", output_interval=25) == specs
    assert len(specs) == 6
    assert {spec.open_boundary_semantics for spec in specs} == STEP133_SEMANTICS
    assert all(spec.row_role == "plane_flux_control_candidate_48" for spec in specs)
    assert all(spec.requested_n_steps == 250 for spec in specs)
    assert all(spec.requested_nx == 48 for spec in specs)
    assert all("Step133" in spec.artifact_scope_note for spec in specs)
    assert all(spec.name not in sweep_names for spec in specs)
    assert all("rho" in spec.name and "alpha" in spec.name and "du" in spec.name and "slew" in spec.name for spec in specs)
    assert {spec.open_boundary_flux_feedback_gain_rho for spec in specs} == {0.0005, 0.001, 0.002}
    assert {spec.open_boundary_flux_feedback_delta_cap_u for spec in specs} == {0.00025, 0.0005}
    assert {spec.open_boundary_flux_feedback_slew_alpha for spec in specs} == {0.25, 0.5}


def test_step133_solver_hash_includes_density_and_stationarity_params():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import solver_state_hash_for_spec
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        step121_plane_flux_mass_damped_48_specs,
        step121_plane_flux_sweep_48_specs,
    )

    base = _step133_spec()
    density_changed = _step133_spec(open_boundary_flux_feedback_gain_rho=0.002)
    delta_changed = _step133_spec(open_boundary_flux_feedback_delta_cap_u=0.00025)
    slew_changed = _step133_spec(open_boundary_flux_feedback_slew_alpha=0.25)

    base_hash = solver_state_hash_for_spec(base)
    assert solver_state_hash_for_spec(density_changed) != base_hash
    assert solver_state_hash_for_spec(delta_changed) != base_hash
    assert solver_state_hash_for_spec(slew_changed) != base_hash

    step132_hashes = {solver_state_hash_for_spec(spec) for spec in step121_plane_flux_sweep_48_specs(output_interval=25)}
    step133_hashes = {solver_state_hash_for_spec(spec) for spec in step121_plane_flux_mass_damped_48_specs(output_interval=25)}
    assert len(step133_hashes) == 6
    assert step133_hashes.isdisjoint(step132_hashes)


def test_step133_manifest_rejects_stale_step132_rows_for_mass_damped_phase(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import solver_state_hash_for_spec
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        collect_step121_rows,
        step121_plane_flux_mass_damped_48_specs,
        step121_plane_flux_sweep_48_specs,
        write_step121_campaign_manifest,
    )

    out = tmp_path / "campaign"
    specs = step121_plane_flux_mass_damped_48_specs(output_interval=25)
    write_step121_campaign_manifest(out, specs, phase="planeflux_mass_damped48")
    spec = specs[0]
    stale_source = next(
        item
        for item in step121_plane_flux_sweep_48_specs(output_interval=25)
        if item.open_boundary_semantics == spec.open_boundary_semantics
    )
    stale = _step133_row(
        spec.name,
        spec.open_boundary_semantics,
        solver_state_hash=solver_state_hash_for_spec(stale_source),
    )
    _write_json(out / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(out, return_ignored=True)

    assert collected["rows"] == []
    assert collected["ignored_rows"][0]["name"] == spec.name
    assert "solver_state_hash_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]
    assert solver_state_hash_for_spec(spec) != stale["solver_state_hash"]


def test_step133_rows_do_not_enable_selected96_even_if_metrics_are_good():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    mass_damped_triage = _step133_row(
        "duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_rho0p001_alpha0p02_du0p0005_slew0p50_250step_triage",
        REGULARIZED_PLANE,
    )
    selection = select_step121_best_boundary(_references() + _failed_step127_candidates() + [mass_damped_triage])

    assert selection["best_boundary_selected"] is False
    assert selection["campaign_state"] == "48_candidates_failed"
    assert selection["validation_claim_allowed"] is False
    assert all(item["semantics"] not in STEP133_SEMANTICS for item in selection["candidate_summaries"])


def test_step133_density_and_stationarity_diagnostics_are_bounded(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS,
        _flow_development_diagnostic_record,
        _write_flow_development_diagnostics,
    )

    spec = _step133_spec()
    diagnostics = [
        _flow_development_diagnostic_record(
            {
                "step": 25,
                "inlet_flux": 42.0,
                "outlet_flux": 44.0,
                "midplane_flux": 43.0,
                "mass_total_delta_rel": 0.001,
                "outlet_plane_rho_mean": 1.001,
                "outlet_plane_rho_std": 0.002,
            },
            spec,
            {
                "flow_correction_cap_u": 0.005,
                "controller_target_outlet_flux": 42.0,
                "controller_measured_outlet_flux": 44.0,
                "controller_raw_flux_error": -2.0,
                "controller_filtered_flux_error": -0.04,
                "controller_u_feedback": -0.0005,
                "controller_density_feedback": -0.00001,
                "controller_delta_cap_u": 0.0005,
                "controller_slew_alpha": 0.5,
                "controller_saturation_fraction_run": 0.0,
            },
        ),
        _flow_development_diagnostic_record(
            {
                "step": 50,
                "inlet_flux": 42.0,
                "outlet_flux": 43.0,
                "midplane_flux": 42.5,
                "mass_total_delta_rel": -0.001,
                "outlet_plane_rho_mean": 0.999,
                "outlet_plane_rho_std": 0.003,
            },
            spec,
            {
                "flow_correction_cap_u": 0.005,
                "controller_target_outlet_flux": 42.0,
                "controller_measured_outlet_flux": 43.0,
                "controller_raw_flux_error": -1.0,
                "controller_filtered_flux_error": -0.03,
                "controller_u_feedback": 0.00025,
                "controller_density_feedback": -0.00002,
                "controller_delta_cap_u": 0.0005,
                "controller_slew_alpha": 0.5,
                "controller_saturation_fraction_run": 0.0,
            },
        ),
    ]
    _write_flow_development_diagnostics(tmp_path, diagnostics)

    required = {
        "step133_mass_damped_candidate",
        "controller_density_feedback",
        "controller_density_feedback_abs",
        "controller_delta_cap_u",
        "controller_slew_alpha",
        "outlet_plane_rho_mean",
        "outlet_plane_rho_std",
    }
    assert required.issubset(set(FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS))
    assert diagnostics[-1]["step133_mass_damped_candidate"] is True

    with (tmp_path / "flow_development_diagnostics.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["selected96_claim_allowed"] == "False"

    summary = json.loads((tmp_path / "flow_development_diagnostics_summary.json").read_text(encoding="utf-8"))
    assert summary["step"] == 133
    assert summary["density_feedback_tail_abs_max"] == pytest.approx(0.00002)
    assert summary["rho_outlet_tail_mean"] == pytest.approx(1.0)
    assert summary["rho_outlet_tail_std"] > 0.0
    assert summary["mass_drift_tail_slope"] == pytest.approx(-0.002)
    assert summary["outlet_flux_tail_slope"] == pytest.approx(-1.0)
    assert summary["controller_feedback_sign_change_count_tail"] == 1
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_claim_allowed"] is False


def test_step133_config_fields_validate_defaults_and_bounds():
    from src.mpm_lbm.sim.lbm.config import LBMConfig

    cfg = LBMConfig(
        nx=8,
        ny=6,
        nz=6,
        open_boundary_semantics=REGULARIZED_PLANE,
        open_boundary_flux_feedback_gain_rho=0.001,
        open_boundary_flux_feedback_delta_cap_u=0.0005,
        open_boundary_flux_feedback_slew_alpha=0.5,
    )
    assert cfg.open_boundary_flux_feedback_delta_cap_u == pytest.approx(0.0005)
    assert cfg.open_boundary_flux_feedback_slew_alpha == pytest.approx(0.5)

    with pytest.raises(ValueError, match="open_boundary_flux_feedback_delta_cap_u"):
        LBMConfig(nx=8, ny=6, nz=6, open_boundary_flux_feedback_delta_cap_u=-0.1)
    with pytest.raises(ValueError, match="open_boundary_flux_feedback_slew_alpha"):
        LBMConfig(nx=8, ny=6, nz=6, open_boundary_flux_feedback_slew_alpha=1.5)
