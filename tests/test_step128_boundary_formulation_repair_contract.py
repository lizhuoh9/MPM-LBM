import json
import shutil
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_REPAIR = "regularized_mass_balanced_pressure_outlet"
CONVECTIVE_REPAIR = "convective_mass_balanced_pressure_outlet"
OLD_CANDIDATES = {
    "regularized_velocity_pressure_limited",
    "convective_pressure_outlet_experimental",
}
REPAIR_CANDIDATES = {REGULARIZED_REPAIR, CONVECTIVE_REPAIR}


def _row(
    name,
    semantics,
    *,
    role="candidate_48",
    complete=True,
    validation=True,
    flux=0.04,
    flux_max=0.08,
    inlet_flux=0.03,
    outlet_flux=0.03,
    outlet_ratio=None,
    midplane_ratio=1.0,
    outlet_cv=0.02,
    mass=0.001,
    limiter=0.0,
    first_failure_reason=None,
    solver_state_hash="hash",
):
    first_failure = None if complete and first_failure_reason is None else 10
    if outlet_ratio is None:
        outlet_ratio = abs(float(outlet_flux) / float(inlet_flux)) if inlet_flux else None
    return {
        "name": name,
        "row_role": role,
        "geometry_mode": "duct_only",
        "lbm_open_boundary_semantics": semantics,
        "requested_nx": 48,
        "executed_nx": 48,
        "requested_n_steps": 500,
        "steps_completed": 500 if complete else 200,
        "requested_window_completed": bool(complete),
        "step120_validation_claimed": bool(validation and complete and first_failure_reason is None),
        "simulation_backed_artifact": True,
        "not_used_for_validation": False,
        "finite_pass": True,
        "density_gate_pass": True,
        "mass_drift_gate_pass": abs(float(mass)) < 0.005,
        "population_gate_pass": True,
        "mach_gate_pass": True,
        "first_failure_step": first_failure,
        "first_failure_reason": first_failure_reason,
        "stop_reason": f"lightweight_failure:{first_failure_reason}" if first_failure_reason else None,
        "flux_balance_reported": True,
        "flux_imbalance_rel_tail_mean": float(flux),
        "flux_imbalance_rel_tail_max": float(flux_max),
        "inlet_flux_tail_mean": float(inlet_flux),
        "outlet_flux_tail_mean": float(outlet_flux),
        "outlet_to_inlet_flux_ratio_tail_mean": outlet_ratio,
        "midplane_to_inlet_flux_ratio_tail_mean": float(midplane_ratio),
        "outlet_flux_tail_cv": float(outlet_cv),
        "flow_development_gate_pass": True,
        "flow_development_rejection_reasons": [],
        "mass_total_delta_rel_final": float(mass),
        "mach_proxy_observed_max": 0.08,
        "limiter_activation_fraction": float(limiter),
        "limiter_activation_gate_pass": limiter <= 0.05,
        "runtime_s": 1.0,
        "open_boundary_limiter_enabled": False,
        "open_boundary_rho_min": 0.91,
        "open_boundary_rho_max": 1.09,
        "open_boundary_u_max": 0.08,
        "open_boundary_noneq_cap": 0.17,
        "open_boundary_population_floor": None,
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
        _row(
            "duct_only_48_legacy_boundary_500step_reference_real",
            "equilibrium_all_population_reset",
            role="reference_48",
            flux=0.04,
            solver_state_hash="legacy-reference-hash",
        ),
        _row(
            "duct_only_48_regularized_boundary_500step_reference_real",
            "regularized_velocity_pressure",
            role="reference_48",
            flux=0.51,
            flux_max=0.86,
            outlet_ratio=1.41,
            midplane_ratio=1.31,
            outlet_cv=0.45,
            mass=0.0029,
            solver_state_hash="regularized-reference-hash",
        ),
    ]


def _failed_step127_candidates():
    return [
        _row(
            "duct_only_48_regularized_limited_boundary_500step_real",
            "regularized_velocity_pressure_limited",
            flux=0.51165,
            flux_max=0.866,
            outlet_ratio=1.4127,
            midplane_ratio=1.306,
            outlet_cv=0.452,
            mass=0.0029,
            solver_state_hash="limited-step127-hash",
        ),
        _row(
            "duct_only_48_convective_outlet_boundary_500step_real",
            "convective_pressure_outlet_experimental",
            complete=False,
            validation=False,
            flux=0.261,
            flux_max=0.269,
            outlet_ratio=0.738,
            midplane_ratio=0.754,
            outlet_cv=0.0038,
            mass=0.046,
            first_failure_reason="mass_drift",
            solver_state_hash="convective-step127-hash",
        ),
    ]


def _write_finite(row_dir: Path, row: dict) -> None:
    row_dir.mkdir(parents=True, exist_ok=True)
    (row_dir / "finite_stability_report.json").write_text(
        json.dumps({"summary_row": row}, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def test_step128_new_semantics_are_valid_config_values_and_dispatched():
    from src.mpm_lbm.sim.lbm.config import LBMConfig, VALID_LBM_OPEN_BOUNDARY_SEMANTICS

    assert REPAIR_CANDIDATES.issubset(set(VALID_LBM_OPEN_BOUNDARY_SEMANTICS))
    for semantics in REPAIR_CANDIDATES:
        cfg = LBMConfig(nx=4, ny=3, nz=3, open_boundary_semantics=semantics)
        assert cfg.open_boundary_semantics == semantics

    source = (ROOT / "src/mpm_lbm/sim/lbm/fluid.py").read_text(encoding="utf-8")
    assert "apply_regularized_mass_balanced_pressure_outlet_x_open_boundaries" in source
    assert "apply_convective_mass_balanced_pressure_outlet_x_open_boundaries" in source
    assert REGULARIZED_REPAIR in source
    assert CONVECTIVE_REPAIR in source


def test_step128_repair_phase_is_separate_from_step127_candidates48():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        CANDIDATE_SEMANTICS,
        REPAIRED_CANDIDATE_SEMANTICS,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        resolve_step121_phase_specs,
        step121_candidate_48_specs,
        step121_repair_48_specs,
    )

    assert OLD_CANDIDATES.issubset(CANDIDATE_SEMANTICS)
    assert REPAIR_CANDIDATES.issubset(CANDIDATE_SEMANTICS)
    assert set(REPAIRED_CANDIDATE_SEMANTICS) == REPAIR_CANDIDATES

    old_specs = step121_candidate_48_specs(output_interval=25)
    repair_specs = step121_repair_48_specs(output_interval=25)

    assert {spec.open_boundary_semantics for spec in old_specs} == OLD_CANDIDATES
    assert {spec.open_boundary_semantics for spec in repair_specs} == REPAIR_CANDIDATES
    assert all(spec.row_role == "repair_candidate_48" for spec in repair_specs)
    assert {spec.open_boundary_semantics for spec in resolve_step121_phase_specs("repair48")} == REPAIR_CANDIDATES


def test_step128_solver_state_hash_separates_repaired_semantics():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        Step120RunSpec,
        solver_state_hash_for_spec,
    )

    base = {
        "name": "hash_row",
        "nx": 5,
        "ny": 4,
        "nz": 4,
        "n_steps": 3,
        "output_interval": 1,
        "failure_check_interval": 1,
        "geometry_mode": "duct_only",
        "requested_nx": 5,
        "requested_n_steps": 3,
        "allow_large_real_run_without_flag": True,
    }
    old = Step120RunSpec(**base, open_boundary_semantics="convective_pressure_outlet_experimental")
    repaired = Step120RunSpec(**base, open_boundary_semantics=CONVECTIVE_REPAIR, row_role="repair_candidate_48")

    assert solver_state_hash_for_spec(old) != solver_state_hash_for_spec(repaired)


@pytest.mark.parametrize("semantics", sorted(REPAIR_CANDIDATES))
def test_step128_repaired_semantics_run_tiny_real_smoke(tmp_path, semantics):
    from experiments.steps import step120_lbm_boundary_repair_large_real_execution as step120

    spec = step120.Step120RunSpec(
        name=f"tiny_{semantics}",
        nx=4,
        ny=3,
        nz=3,
        n_steps=1,
        output_interval=1,
        failure_check_interval=1,
        checkpoint_every=0,
        open_boundary_semantics=semantics,
        geometry_mode="duct_only",
        requested_nx=4,
        requested_n_steps=1,
        allow_large_real_run_without_flag=True,
        row_role="repair_candidate_48",
    )

    row = step120.run_step120_row(spec, tmp_path / spec.name, checkpoint_root=tmp_path / "checkpoints")

    assert row["simulation_backed_artifact"] is True
    assert row["finite_pass"] is True
    assert row["steps_completed"] == 1
    assert row["mass_balance_correction_count"] >= 0
    assert row["mass_balance_correction_abs_sum"] >= 0.0
    assert row["unknown_population_delta_abs_sum"] >= 0.0


def test_step128_hard_stop_mass_drift_telemetry_fields_are_explicit():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        _step120_lightweight_failure_detector,
    )

    failure = _step120_lightweight_failure_detector(
        {
            "step": 200,
            "stability_all_finite": True,
            "rho_min": 0.99,
            "rho_max": 1.01,
            "max_v": 0.05,
            "f_min": 0.0,
            "f_max": 0.1,
            "F_min": 0.0,
            "F_max": 0.1,
            "negative_population_fraction": 0.0,
            "mass_total_delta_rel": 0.051,
        },
        mass_drift_abs=0.05,
    )

    assert failure["first_failure_reason"] == "mass_drift"
    assert failure["hard_stop_failure_reason"] == "mass_drift"
    assert failure["hard_stop_failure_step"] == 200
    assert failure["hard_stop_mass_drift_abs_max"] == pytest.approx(0.05)
    assert failure["hard_stop_mass_drift_gate_pass"] is False


def test_step128_summary_rows_report_hard_stop_and_candidate_mass_gate_fields():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        Step120RunSpec,
        _finite_report,
        summarize_step120_limiter_activation,
    )

    spec = Step120RunSpec(
        name="step128_mass_stop",
        nx=4,
        ny=3,
        nz=3,
        n_steps=3,
        output_interval=1,
        failure_check_interval=1,
        open_boundary_semantics=CONVECTIVE_REPAIR,
        geometry_mode="duct_only",
        requested_nx=4,
        requested_n_steps=3,
        allow_large_real_run_without_flag=True,
        row_role="repair_candidate_48",
    )
    records = [
        {
            "step": 1,
            "all_finite": True,
            "rho_min": 0.99,
            "rho_max": 1.01,
            "mass_total_delta_rel": 0.006,
            "mach_proxy": 0.02,
            "flux_imbalance_rel": 0.2,
        }
    ]
    stability_records = [
        {
            "step": 1,
            "stability_all_finite": True,
            "negative_population_fraction": 0.0,
            "negative_population_count": 0,
        }
    ]
    finite = _finite_report(
        spec,
        steps_completed=1,
        records=records,
        stability_records=stability_records,
        combined_records=[{**records[0], **stability_records[0], "first_failure_reason": "mass_drift"}],
        tau_report={"tau_margin_pass": True, "lbm_niu": 0.1, "lbm_relaxation_semantics": "legacy_external_solver_parameter", "tau": 0.8},
        runtime_s=0.1,
        stop_reason="lightweight_failure:mass_drift",
        limiter_summary=summarize_step120_limiter_activation({}, spec),
        checkpoint_root=ROOT / "outputs/tmp/step128_boundary_contract/checkpoints",
        restored_checkpoint=None,
    )
    row = finite["summary_row"]

    assert row["hard_stop_failure_reason"] == "mass_drift"
    assert row["hard_stop_mass_drift_gate_pass"] is False
    assert row["candidate_mass_acceptance_abs_max"] == pytest.approx(0.005)
    assert row["candidate_mass_acceptance_gate_pass"] is False


def test_step128_repaired_candidate_can_be_selected_only_after_hard_gates():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        select_step121_best_boundary,
    )

    repaired = _row(
        "duct_only_48_regularized_mass_balanced_pressure_outlet_500step_real",
        REGULARIZED_REPAIR,
        role="repair_candidate_48",
        flux=0.04,
        flux_max=0.08,
        outlet_ratio=0.98,
        midplane_ratio=0.99,
        outlet_cv=0.02,
        mass=0.001,
        solver_state_hash="regularized-repair-hash",
    )
    selection = select_step121_best_boundary(_references() + _failed_step127_candidates() + [repaired])

    assert selection["best_boundary_selected"] is True
    assert selection["selected_boundary_semantics"] == REGULARIZED_REPAIR
    assert selection["selected_boundary_slug"] == "regularized_mass_balanced"


@pytest.mark.parametrize(
    "row, expected_reason",
    [
        (
            _row(
                "repair_first_failure",
                REGULARIZED_REPAIR,
                role="repair_candidate_48",
                complete=False,
                validation=False,
                first_failure_reason="mass_drift",
                mass=0.046,
            ),
            "first_failure",
        ),
        (
            _row(
                "repair_mass_gate",
                REGULARIZED_REPAIR,
                role="repair_candidate_48",
                mass=0.005,
            ),
            "mass_drift_gate",
        ),
        (
            _row(
                "repair_ratio_gate",
                REGULARIZED_REPAIR,
                role="repair_candidate_48",
                outlet_ratio=1.30,
                midplane_ratio=1.0,
                mass=0.001,
            ),
            "outlet_to_inlet_flux_ratio_tail_mean",
        ),
    ],
)
def test_step128_repaired_candidates_still_fail_hard_gates(row, expected_reason):
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        select_step121_best_boundary,
    )

    selection = select_step121_best_boundary(_references() + _failed_step127_candidates() + [row])
    summary = next(item for item in selection["candidate_summaries"] if item["name"] == row["name"])

    assert summary["candidate_pass"] is False
    assert expected_reason in set(summary["rejection_reasons"]) | set(summary["flow_development_rejection_reasons"])


def test_step128_stale_step127_artifact_cannot_reuse_repaired_row(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        Step120RunSpec,
        solver_state_hash_for_spec,
        step120_row_reusable_for_spec,
    )

    spec = Step120RunSpec(
        name="duct_only_48_convective_mass_balanced_pressure_outlet_500step_real",
        nx=48,
        ny=48,
        nz=48,
        n_steps=500,
        output_interval=25,
        failure_check_interval=5,
        checkpoint_every=100,
        open_boundary_semantics=CONVECTIVE_REPAIR,
        geometry_mode="duct_only",
        requested_nx=48,
        requested_n_steps=500,
        allow_large_real_run_without_flag=True,
        row_role="repair_candidate_48",
    )
    stale = {
        **_row(
            spec.name,
            "convective_pressure_outlet_experimental",
            role="candidate_48",
            solver_state_hash="step127-convective-hash",
        ),
        "requested_nx": 48,
        "requested_n_steps": 500,
        "config_hash": "step127-convective-hash",
        "solver_state_hash": "step127-convective-hash",
    }
    _write_finite(tmp_path / spec.name, stale)

    assert stale["solver_state_hash"] != solver_state_hash_for_spec(spec)
    assert step120_row_reusable_for_spec(tmp_path / spec.name, spec) is False


def teardown_module(module):
    path = ROOT / "outputs/tmp/step128_boundary_contract"
    if path.exists():
        shutil.rmtree(path)
