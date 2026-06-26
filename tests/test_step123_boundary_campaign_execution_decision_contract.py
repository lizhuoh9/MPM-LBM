import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _row(
    name,
    semantics,
    *,
    role,
    nx=48,
    steps=500,
    complete=True,
    validation=True,
    simulation=True,
    flux=0.04,
    outlet_flux=0.03,
    inlet_flux=0.03,
    midplane_ratio=1.0,
    mass=0.001,
    limiter=0.0,
    first_failure_reason=None,
    skipped_reason=None,
):
    first_failure = None if complete and first_failure_reason is None else 10
    reason = first_failure_reason
    return {
        "name": name,
        "row_role": role,
        "geometry_mode": "duct_only",
        "lbm_open_boundary_semantics": semantics,
        "requested_nx": int(nx),
        "executed_nx": int(nx),
        "requested_n_steps": int(steps),
        "steps_completed": int(steps if complete else max(1, min(10, steps - 1))),
        "requested_window_completed": bool(complete),
        "step120_validation_claimed": bool(validation and complete and reason is None),
        "simulation_backed_artifact": bool(simulation),
        "not_used_for_validation": False,
        "finite_pass": True,
        "density_gate_pass": True,
        "mass_drift_gate_pass": abs(mass) < 0.005,
        "population_gate_pass": True,
        "mach_gate_pass": True,
        "first_failure_step": first_failure,
        "first_failure_reason": reason,
        "skipped_reason": skipped_reason,
        "flux_balance_reported": True,
        "flux_imbalance_rel_tail_mean": float(flux),
        "outlet_flux_tail_mean": float(outlet_flux),
        "inlet_flux_tail_mean": float(inlet_flux),
        "outlet_to_inlet_flux_ratio_tail_mean": float(outlet_flux / inlet_flux) if inlet_flux else None,
        "midplane_to_inlet_flux_ratio_tail_mean": float(midplane_ratio),
        "flow_development_gate_pass": bool(abs(outlet_flux) > 1.0e-12 and flux < 0.1),
        "mass_total_delta_rel_final": float(mass),
        "limiter_activation_fraction": float(limiter),
        "limiter_activation_gate_pass": limiter <= 0.05,
        "runtime_s": 1.0,
        "open_boundary_limiter_enabled": semantics == "regularized_velocity_pressure_limited",
        "open_boundary_rho_min": 0.91,
        "open_boundary_rho_max": 1.09,
        "open_boundary_u_max": 0.08,
        "open_boundary_noneq_cap": 0.17,
        "open_boundary_population_floor": -2.0e-8,
        "inlet_u_lbm": 0.031,
        "outlet_rho": 0.997,
        "lbm_niu": 0.023,
        "lbm_viscosity_semantics": "legacy_external",
        "lbm_relaxation_semantics": "legacy_external_solver_parameter",
        "tau": 0.572,
        "config_hash": "candidate-config-hash",
        "solver_state_hash": "candidate-config-hash",
        "selected_source_row_name": "duct_only_48_regularized_limited_boundary_500step_real" if role in {"selected_96_duct", "selected_96_static"} else None,
        "selected_source_config_hash": "candidate-config-hash" if role in {"selected_96_duct", "selected_96_static"} else None,
        "selected_source_tau": 0.572 if role in {"selected_96_duct", "selected_96_static"} else None,
        "selected_source_lbm_relaxation_semantics": "legacy_external_solver_parameter" if role in {"selected_96_duct", "selected_96_static"} else None,
    }


def _references():
    return [
        _row(
            "duct_only_48_legacy_boundary_500step_reference_real",
            "equilibrium_all_population_reset",
            role="reference_48",
            flux=0.08,
        ),
        _row(
            "duct_only_48_regularized_boundary_500step_reference_real",
            "regularized_velocity_pressure",
            role="reference_48",
            flux=0.12,
        ),
    ]


def _selected_payload():
    return {
        "best_boundary_selected": True,
        "campaign_state": "best_48_selected",
        "final_classification": "boundary_repair_partial_continue_lbm",
        "selected_boundary_semantics": "regularized_velocity_pressure_limited",
        "selected_boundary_slug": "limited",
        "selected_row_name": "duct_only_48_regularized_limited_boundary_500step_real",
        "selected_boundary_provenance": {
            "open_boundary_limiter_enabled": True,
            "open_boundary_rho_min": 0.91,
            "open_boundary_rho_max": 1.09,
            "open_boundary_u_max": 0.08,
            "open_boundary_noneq_cap": 0.17,
            "open_boundary_population_floor": -2.0e-8,
            "inlet_u_lbm": 0.031,
            "outlet_rho": 0.997,
            "lbm_niu": 0.023,
            "lbm_viscosity_semantics": "legacy_external",
            "lbm_relaxation_semantics": "legacy_external_solver_parameter",
            "tau": 0.572,
            "config_hash": "candidate-config-hash",
            "solver_state_hash": "candidate-config-hash",
        },
    }


def _write_finite(row_dir: Path, summary_row: dict) -> None:
    row_dir.mkdir(parents=True, exist_ok=True)
    (row_dir / "finite_stability_report.json").write_text(
        json.dumps({"summary_row": summary_row}, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def test_step123_physical_early_stop_candidates_are_terminal_failure():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    rows = _references() + [
        _row(
            "duct_only_48_regularized_limited_boundary_500step_real",
            "regularized_velocity_pressure_limited",
            role="candidate_48",
            complete=False,
            validation=False,
            flux=0.50,
            mass=0.02,
            first_failure_reason="mass_drift",
        ),
        _row(
            "duct_only_48_convective_outlet_boundary_500step_real",
            "convective_pressure_outlet_experimental",
            role="candidate_48",
            complete=False,
            validation=False,
            flux=0.45,
            mass=0.02,
            first_failure_reason="rho_range",
        ),
    ]

    selection = select_step121_best_boundary(rows)

    assert selection["campaign_state"] == "48_candidates_failed"
    assert selection["final_classification"] == "boundary_repair_failed_revisit_lbm_solver"
    assert selection["campaign_should_stop_at_48"] is True


def test_step123_walltime_candidate_is_not_terminal_evidence():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    rows = _references() + [
        _row(
            "duct_only_48_regularized_limited_boundary_500step_real",
            "regularized_velocity_pressure_limited",
            role="candidate_48",
            complete=False,
            validation=False,
            first_failure_reason="max_wall_seconds",
            skipped_reason="max_wall_seconds",
        ),
        _row(
            "duct_only_48_convective_outlet_boundary_500step_real",
            "convective_pressure_outlet_experimental",
            role="candidate_48",
            complete=False,
            validation=False,
            first_failure_reason="rho_range",
        ),
    ]

    selection = select_step121_best_boundary(rows)

    assert selection["campaign_state"] == "awaiting_48_candidates"
    assert selection["final_classification"] == "boundary_repair_partial_continue_lbm"


def test_step123_selected_96_gate_requires_flow_development_fields():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import build_step121_gate_report

    selection = _selected_payload()
    rows = _references() + [
        _row(
            "duct_only_48_regularized_limited_boundary_500step_real",
            "regularized_velocity_pressure_limited",
            role="candidate_48",
        ),
        {
            **_row(
                "duct_only_96_limited_1000step_real",
                "regularized_velocity_pressure_limited",
                role="selected_96_duct",
                nx=96,
                steps=1000,
                flux=0.01,
                outlet_flux=0.0,
            ),
            "flow_development_gate_pass": False,
        },
    ]

    gate = build_step121_gate_report(rows, selection)

    assert gate["campaign_state"] == "awaiting_selected_96_duct"
    assert gate["failed_selected_rows"] == ["duct_only_96_limited_1000step_real"]
    assert gate["selected_96_flow_development_gate"]["duct_pass"] is False


def test_step123_selected_96_gate_reports_flow_development_success():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import build_step121_gate_report

    selection = _selected_payload()
    rows = _references() + [
        _row(
            "duct_only_48_regularized_limited_boundary_500step_real",
            "regularized_velocity_pressure_limited",
            role="candidate_48",
        ),
        _row(
            "duct_only_96_limited_1000step_real",
            "regularized_velocity_pressure_limited",
            role="selected_96_duct",
            nx=96,
            steps=1000,
            flux=0.02,
            outlet_flux=0.03,
            inlet_flux=0.031,
        ),
        _row(
            "static_two_flap_96_limited_1000step_real",
            "regularized_velocity_pressure_limited",
            role="selected_96_static",
            nx=96,
            steps=1000,
            flux=0.02,
            outlet_flux=0.03,
            inlet_flux=0.031,
        ),
    ]

    gate = build_step121_gate_report(rows, selection)

    assert gate["campaign_state"] == "complete"
    assert gate["selected_96_flow_development_gate"]["duct_pass"] is True
    assert gate["selected_96_flow_development_gate"]["outlet_to_inlet_flux_ratio_tail_mean"] == pytest.approx(0.03 / 0.031)


def test_step123_row_reuse_rejects_same_name_mismatched_solver_hash(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        Step120RunSpec,
        solver_state_hash_for_spec,
        step120_row_reusable_for_spec,
    )

    spec = Step120RunSpec(
        name="same_name_row",
        nx=5,
        ny=4,
        nz=4,
        n_steps=1,
        output_interval=1,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=5,
        requested_n_steps=1,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
        allow_large_real_run_without_flag=True,
    )
    row = {
        "name": spec.name,
        "row_role": spec.row_role,
        "geometry_mode": spec.geometry_mode,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "requested_nx": spec.requested_nx,
        "requested_n_steps": spec.requested_n_steps,
        "requested_window_completed": True,
        "simulation_backed_artifact": True,
        "step120_validation_claimed": True,
        "config_hash": "old-hash",
        "solver_state_hash": "old-hash",
    }
    _write_finite(tmp_path / spec.name, row)

    assert step120_row_reusable_for_spec(tmp_path / spec.name, spec) is False

    row["config_hash"] = solver_state_hash_for_spec(spec)
    row["solver_state_hash"] = solver_state_hash_for_spec(spec)
    _write_finite(tmp_path / spec.name, row)

    assert step120_row_reusable_for_spec(tmp_path / spec.name, spec) is True


def test_step123_row_reuse_rejects_selected_source_mismatch(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        Step120RunSpec,
        solver_state_hash_for_spec,
        step120_row_reusable_for_spec,
    )

    spec = Step120RunSpec(
        name="selected_row",
        nx=5,
        ny=4,
        nz=4,
        n_steps=1,
        output_interval=1,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=5,
        requested_n_steps=1,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
        selected_source_row_name="new_source",
        selected_source_config_hash="new-source-hash",
        selected_source_tau=0.572,
        selected_source_lbm_relaxation_semantics="legacy_external_solver_parameter",
        allow_large_real_run_without_flag=True,
    )
    row = {
        "name": spec.name,
        "row_role": spec.row_role,
        "geometry_mode": spec.geometry_mode,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "requested_nx": spec.requested_nx,
        "requested_n_steps": spec.requested_n_steps,
        "requested_window_completed": True,
        "simulation_backed_artifact": True,
        "step120_validation_claimed": True,
        "config_hash": solver_state_hash_for_spec(spec),
        "solver_state_hash": solver_state_hash_for_spec(spec),
        "selected_source_row_name": "old_source",
        "selected_source_config_hash": "new-source-hash",
        "selected_source_tau": 0.572,
        "selected_source_lbm_relaxation_semantics": "legacy_external_solver_parameter",
    }
    _write_finite(tmp_path / spec.name, row)

    assert step120_row_reusable_for_spec(tmp_path / spec.name, spec) is False


def test_step123_solver_state_hash_ignores_run_manifest_fields():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        Step120RunSpec,
        run_manifest_hash_for_spec,
        solver_state_hash_for_spec,
    )

    base = Step120RunSpec(
        name="hash_split",
        nx=5,
        ny=4,
        nz=4,
        n_steps=3,
        output_interval=1,
        failure_check_interval=1,
        checkpoint_every=1,
        full_population_snapshot_interval=0,
        snapshot_on_failure=True,
        snapshot_on_final=True,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=5,
        requested_n_steps=3,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
        allow_large_real_run_without_flag=True,
    )
    changed_manifest = Step120RunSpec(
        **{
            **base.__dict__,
            "output_interval": 3,
            "failure_check_interval": 2,
            "checkpoint_every": 3,
            "full_population_snapshot_interval": 2,
            "snapshot_on_failure": False,
            "snapshot_on_final": False,
        }
    )

    assert solver_state_hash_for_spec(base) == solver_state_hash_for_spec(changed_manifest)
    assert run_manifest_hash_for_spec(base) != run_manifest_hash_for_spec(changed_manifest)


def test_step123_checkpoint_restore_allows_manifest_only_change(tmp_path):
    from tests.test_step122_boundary_campaign_hardening_contract import _FakeLbm
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        Step120RunSpec,
        restore_latest_step120_checkpoint_with_history,
        write_step120_checkpoint,
    )

    base = Step120RunSpec(
        name="manifest_only_checkpoint",
        nx=2,
        ny=2,
        nz=2,
        n_steps=2,
        output_interval=1,
        failure_check_interval=1,
        checkpoint_every=1,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=2,
        requested_n_steps=2,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
        allow_large_real_run_without_flag=True,
    )
    manifest_changed = Step120RunSpec(
        **{
            **base.__dict__,
            "output_interval": 2,
            "failure_check_interval": 2,
            "checkpoint_every": 2,
        }
    )

    write_step120_checkpoint(_FakeLbm(), base, tmp_path, 2, 8.0, [{"step": 2}], [{"step": 2}])
    restored = restore_latest_step120_checkpoint_with_history(_FakeLbm(), manifest_changed, tmp_path)

    assert restored is not None
    assert restored[0] == 2


def test_step123_selected_96_specs_require_formal_provenance_by_default():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import make_selected_96_specs

    selection = {
        "best_boundary_selected": True,
        "selected_boundary_semantics": "regularized_velocity_pressure_limited",
        "selected_boundary_slug": "limited",
        "selected_row_name": "duct_only_48_regularized_limited_boundary_500step_real",
    }

    with pytest.raises(ValueError, match="selected_boundary_provenance"):
        make_selected_96_specs(selection)


def test_step123_selected_96_specs_allow_explicit_legacy_provenance_mode():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import make_selected_96_specs

    selection = {
        "best_boundary_selected": True,
        "selected_boundary_semantics": "regularized_velocity_pressure_limited",
        "selected_boundary_slug": "limited",
        "selected_row_name": "duct_only_48_regularized_limited_boundary_500step_real",
        "allow_legacy_provenance_defaults": True,
    }

    duct, static = make_selected_96_specs(selection)

    assert duct.name == "duct_only_96_limited_1000step_real"
    assert static.name == "static_two_flap_96_limited_1000step_real"


def test_step123_real_taichi_lightweight_mass_matches_fluid_rho_sum():
    from experiments.steps import step120_lbm_boundary_repair_large_real_execution as step120

    spec = step120.Step120RunSpec(
        name="step123_real_mass_reduction",
        nx=4,
        ny=3,
        nz=3,
        n_steps=1,
        output_interval=1,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=4,
        requested_n_steps=1,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
        allow_large_real_run_without_flag=True,
    )
    lbm, _tau = step120.create_step120_lbm(spec)
    rho = lbm.rho.to_numpy()
    solid = lbm.solid.to_numpy()
    rho[solid == 0] = np.linspace(0.95, 1.05, int(np.count_nonzero(solid == 0)), dtype=np.float32)
    lbm.rho.from_numpy(rho.astype(np.float32))

    stats = lbm.get_lightweight_stability_stats()
    expected = float(np.sum(rho[solid == 0]))

    assert stats["mass_total"] == pytest.approx(expected, rel=1.0e-6, abs=1.0e-5)


def test_step123_real_lbm_runner_stops_on_lightweight_mass_drift(tmp_path, monkeypatch):
    from experiments.steps import step120_lbm_boundary_repair_large_real_execution as step120

    spec = step120.Step120RunSpec(
        name="step123_real_runner_mass_drift",
        nx=4,
        ny=3,
        nz=3,
        n_steps=3,
        output_interval=10,
        failure_check_interval=1,
        checkpoint_every=1,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=4,
        requested_n_steps=3,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
        allow_large_real_run_without_flag=True,
    )
    real_lbm, real_tau_report = step120.create_step120_lbm(spec)
    original_step = real_lbm.step

    def perturbing_real_step():
        original_step()
        rho = real_lbm.rho.to_numpy()
        solid = real_lbm.solid.to_numpy()
        rho[solid == 0] *= 1.10
        real_lbm.rho.from_numpy(rho.astype(np.float32))

    monkeypatch.setattr(
        step120,
        "create_step120_lbm",
        lambda spec, tau_report=None: (real_lbm, tau_report or real_tau_report),
    )
    monkeypatch.setattr(real_lbm, "step", perturbing_real_step)

    row = step120.run_step120_row(spec, tmp_path / "row", checkpoint_root=tmp_path / "checkpoints")

    assert row["steps_completed"] == 1
    assert row["first_failure_step"] == 1
    assert row["first_failure_reason"] == "mass_drift"


def teardown_module(module):
    path = ROOT / "outputs/tmp/step123_boundary_campaign_contract"
    if path.exists():
        shutil.rmtree(path)
