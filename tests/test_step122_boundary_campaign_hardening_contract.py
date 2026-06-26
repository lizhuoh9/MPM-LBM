import json
import sys
from types import SimpleNamespace
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _passing_row(name, semantics, *, role, nx=48, steps=500, flux=0.01, mass=0.001, limiter=0.0):
    return {
        "name": name,
        "row_role": role,
        "geometry_mode": "duct_only",
        "lbm_open_boundary_semantics": semantics,
        "requested_nx": int(nx),
        "executed_nx": int(nx),
        "requested_n_steps": int(steps),
        "steps_completed": int(steps),
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
        "flux_balance_reported": True,
        "flux_imbalance_rel_tail_mean": float(flux),
        "flux_imbalance_rel_tail_max": min(float(flux) * 1.5, 0.19),
        "inlet_flux_tail_mean": 0.031,
        "outlet_flux_tail_mean": 0.030,
        "outlet_flux_tail_cv": 0.02,
        "outlet_to_inlet_flux_ratio_tail_mean": 0.030 / 0.031,
        "midplane_to_inlet_flux_ratio_tail_mean": 1.0,
        "flow_development_gate_pass": flux < 0.1,
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


def _write_finite_report(row_dir: Path, row: dict) -> None:
    row_dir.mkdir(parents=True, exist_ok=True)
    (row_dir / "finite_stability_report.json").write_text(
        json.dumps({"summary_row": row}, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _selected_best_payload():
    return {
        "best_boundary_selected": True,
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


def test_step122_selected_static_requires_completed_selected_96_duct(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import solver_state_hash_for_spec
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import make_selected_96_specs, resolve_step121_phase_specs

    selection_path = tmp_path / "step121_best_boundary_selection.json"
    selection_path.write_text(json.dumps(_selected_best_payload()), encoding="utf-8")

    with pytest.raises(ValueError, match="selected 96.*duct"):
        resolve_step121_phase_specs("selected-static", best_selection_path=selection_path, output_dir=tmp_path)

    duct_row = _passing_row(
        "duct_only_96_limited_1000step_real",
        "regularized_velocity_pressure_limited",
        role="selected_96_duct",
        nx=96,
        steps=1000,
    )
    duct_spec, _static_spec = make_selected_96_specs(_selected_best_payload())
    duct_hash = solver_state_hash_for_spec(duct_spec)
    duct_row["config_hash"] = duct_hash
    duct_row["solver_state_hash"] = duct_hash
    _write_finite_report(tmp_path / duct_row["name"], duct_row)

    specs = resolve_step121_phase_specs("selected-static", best_selection_path=selection_path, output_dir=tmp_path)

    assert [spec.name for spec in specs] == ["static_two_flap_96_limited_1000step_real"]
    assert specs[0].geometry_mode == "static_two_flap"


def test_step122_selected_96_specs_inherit_selected_48_boundary_provenance():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import make_selected_96_specs

    duct, static = make_selected_96_specs(_selected_best_payload(), output_interval=25)

    for spec in (duct, static):
        assert spec.open_boundary_limiter_enabled is True
        assert spec.open_boundary_rho_min == pytest.approx(0.91)
        assert spec.open_boundary_rho_max == pytest.approx(1.09)
        assert spec.open_boundary_u_max == pytest.approx(0.08)
        assert spec.open_boundary_noneq_cap == pytest.approx(0.17)
        assert spec.open_boundary_population_floor == pytest.approx(-2.0e-8)
        assert spec.inlet_u_lbm == pytest.approx(0.031)
        assert spec.outlet_rho == pytest.approx(0.997)
        assert spec.niu == pytest.approx(0.023)
        assert spec.lbm_viscosity_semantics == "legacy_external"
        assert spec.output_interval == 25
    assert "not FSI" in static.artifact_scope_note


def test_step122_best_selection_records_full_boundary_provenance():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    rows = [
        _passing_row(
            "duct_only_48_legacy_boundary_500step_reference_real",
            "equilibrium_all_population_reset",
            role="reference_48",
            flux=0.08,
        ),
        _passing_row(
            "duct_only_48_regularized_boundary_500step_reference_real",
            "regularized_velocity_pressure",
            role="reference_48",
            flux=0.12,
        ),
        _passing_row(
            "duct_only_48_regularized_limited_boundary_500step_real",
            "regularized_velocity_pressure_limited",
            role="candidate_48",
            flux=0.01,
        ),
        _passing_row(
            "duct_only_48_convective_outlet_boundary_500step_real",
            "convective_pressure_outlet_experimental",
            role="candidate_48",
            flux=0.03,
        ),
    ]

    selection = select_step121_best_boundary(rows)
    provenance = selection["selected_boundary_provenance"]

    assert provenance["open_boundary_rho_min"] == pytest.approx(0.91)
    assert provenance["open_boundary_rho_max"] == pytest.approx(1.09)
    assert provenance["open_boundary_u_max"] == pytest.approx(0.08)
    assert provenance["open_boundary_noneq_cap"] == pytest.approx(0.17)
    assert provenance["open_boundary_population_floor"] == pytest.approx(-2.0e-8)
    assert provenance["inlet_u_lbm"] == pytest.approx(0.031)
    assert provenance["outlet_rho"] == pytest.approx(0.997)
    assert provenance["lbm_niu"] == pytest.approx(0.023)
    assert provenance["lbm_relaxation_semantics"] == "legacy_external_solver_parameter"
    assert provenance["config_hash"] == "candidate-config-hash"


class _FakeField:
    def __init__(self, value):
        self.value = np.asarray(value)

    def to_numpy(self):
        return np.asarray(self.value)

    def from_numpy(self, value):
        self.value = np.asarray(value)


class _FakeLbm:
    def __init__(self, nx=2, ny=2, nz=2):
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.f = _FakeField(np.full((nx, ny, nz, 19), 1.0 / 19.0, dtype=np.float32))
        self.F = _FakeField(np.full((nx, ny, nz, 19), 1.0 / 19.0, dtype=np.float32))
        self.rho = _FakeField(np.ones((nx, ny, nz), dtype=np.float32))
        self.v = _FakeField(np.zeros((nx, ny, nz, 3), dtype=np.float32))
        self.solid = _FakeField(np.zeros((nx, ny, nz), dtype=np.int8))
        self.static_solid = _FakeField(np.zeros((nx, ny, nz), dtype=np.int8))
        self.restored_counters = None

    def get_open_boundary_limiter_stats(self):
        return {
            "rho_clip_count_run": 1,
            "velocity_clip_count_run": 2,
            "noneq_clip_count_run": 3,
            "population_floor_count_run": 4,
            "reconstructed_population_count_run": 10,
            "limiter_activation_count": 10,
            "limiter_activation_denominator": 100,
        }

    def set_open_boundary_limiter_run_counters(self, rho, velocity, noneq, floor, reconstructed):
        self.restored_counters = (rho, velocity, noneq, floor, reconstructed)


class _FakeRuntimeLbm(_FakeLbm):
    def __init__(self, nx=2, ny=2, nz=2):
        super().__init__(nx=nx, ny=ny, nz=nz)
        self.config = SimpleNamespace(
            nx=nx,
            ny=ny,
            nz=nz,
            niu=0.1,
            rho0=1.0,
            relaxation_semantics="legacy_external_solver_parameter",
            open_boundary_semantics="regularized_velocity_pressure_limited",
            bc_x_left=2,
            bc_x_right=1,
            vel_bc_x_left=(0.02, 0.0, 0.0),
            rho_bc_x_right=1.0,
        )
        self.step_count = 0

    def clear_open_boundary_limiter_run_counters(self):
        return None

    def step(self):
        self.step_count += 1


def test_step122_checkpoint_restore_returns_npz_history_payload(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        Step120RunSpec,
        restore_latest_step120_checkpoint_with_history,
        write_step120_checkpoint,
    )

    spec = Step120RunSpec(
        name="step122_history_restore",
        nx=2,
        ny=2,
        nz=2,
        n_steps=2,
        output_interval=1,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=2,
        requested_n_steps=2,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
        allow_large_real_run_without_flag=True,
    )
    records = [{"step": 0, "mass_total": 8.0}, {"step": 2, "mass_total": 8.1}]
    stability = [{"step": 0, "rho_min": 1.0}, {"step": 2, "rho_min": 0.99}]
    write_step120_checkpoint(_FakeLbm(), spec, tmp_path, 2, 8.0, records, stability)

    restored_lbm = _FakeLbm()
    restored = restore_latest_step120_checkpoint_with_history(restored_lbm, spec, tmp_path)

    assert restored is not None
    step, mass_initial, checkpoint_path, restored_records, restored_stability = restored
    assert step == 2
    assert mass_initial == pytest.approx(8.0)
    assert Path(checkpoint_path).name == "checkpoint_step_000002.npz"
    assert restored_records == records
    assert restored_stability == stability
    assert restored_lbm.restored_counters == (1, 2, 3, 4, 10)


def test_step122_runner_stops_on_immediate_lightweight_mass_drift_and_writes_artifacts(tmp_path, monkeypatch):
    from experiments.steps import step120_lbm_boundary_repair_large_real_execution as step120

    spec = step120.Step120RunSpec(
        name="step122_immediate_mass_drift",
        nx=2,
        ny=2,
        nz=2,
        n_steps=3,
        output_interval=10,
        failure_check_interval=1,
        checkpoint_every=1,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=2,
        requested_n_steps=3,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
        allow_large_real_run_without_flag=True,
    )

    fake_lbm = _FakeRuntimeLbm()
    monkeypatch.setattr(step120, "create_step120_lbm", lambda spec, tau_report=None: (fake_lbm, tau_report))

    def fake_boundary_summary(lbm, step, mass_initial=None):
        mass = 100.0
        delta = 0.0 if mass_initial in (None, 0.0) else (mass - float(mass_initial)) / float(mass_initial)
        return {
            "step": int(step),
            "rho_min": 1.0,
            "rho_max": 1.0,
            "rho_mean": 1.0,
            "mass_total": mass,
            "mass_total_delta_from_initial": 0.0,
            "mass_total_delta_rel": delta,
            "inlet_mean_ux": 0.02,
            "outlet_mean_ux": 0.02,
            "midplane_mean_ux": 0.02,
            "inlet_flux": 0.02,
            "outlet_flux": 0.02,
            "flux_imbalance_abs": 0.0,
            "flux_imbalance_rel": 0.0,
            "flux_balance_reported": True,
            "max_v": 0.02,
            "mach_proxy_observed": 0.02,
            "centerline_ux_profile": [0.02],
            "outlet_reflection_proxy": {"negative_ux_fraction": 0.0, "rho_std": 0.0, "ux_std": 0.0},
            "all_finite": True,
        }

    def fake_lightweight_stability(lbm, step):
        return {
            "step": int(step),
            "diagnostic_mode": "lightweight_reduction",
            "f_all_finite": True,
            "F_all_finite": True,
            "all_finite": True,
            "rho_min": 1.0,
            "rho_max": 1.0,
            "max_v": 0.02,
            "f_min": 0.0,
            "f_max": 1.0,
            "F_min": 0.0,
            "F_max": 1.0,
            "negative_population_count": 0,
            "negative_population_fraction": 0.0,
            "population_entry_count": 304,
            "fluid_cell_count": 8,
            "mass_total": 100.0 if step == 0 else 106.0,
            "rho_below_low_count": 0,
            "rho_above_high_count": 0,
            "velocity_outlier_count": 0,
            "boundary_x_min_negative_population_count": 0,
            "boundary_x_max_negative_population_count": 0,
            "stability_all_finite": True,
        }

    monkeypatch.setattr(step120, "summarize_lbm_boundary_diagnostics", fake_boundary_summary)
    monkeypatch.setattr(step120, "summarize_step120_lightweight_stability", fake_lightweight_stability)

    row_dir = tmp_path / "row"
    checkpoint_root = tmp_path / "checkpoints"
    row = step120.run_step120_row(spec, row_dir, checkpoint_root=checkpoint_root)

    assert row["steps_completed"] == 1
    assert row["first_failure_step"] == 1
    assert row["first_failure_reason"] == "mass_drift"
    assert row["checkpoint_available"] is True
    assert (checkpoint_root / spec.name / "checkpoint_step_000001.npz").is_file()
    assert (row_dir / "population_snapshots" / "snapshot_step_000001_lightweight_failure.json").is_file()


def test_step122_lightweight_detector_uses_mass_total_delta():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import _step120_lightweight_failure_detector

    stability = {
        "step": 3,
        "stability_all_finite": True,
        "rho_min": 0.99,
        "rho_max": 1.01,
        "max_v": 0.02,
        "f_min": 0.0,
        "f_max": 1.0,
        "F_min": 0.0,
        "F_max": 1.0,
        "negative_population_fraction": 0.0,
        "mass_total": 106.0,
    }

    failure = _step120_lightweight_failure_detector(stability, mass_initial=100.0)

    assert failure["first_failure_step"] == 3
    assert failure["first_failure_reason"] == "mass_drift"
    assert failure["mass_total_delta_rel"] == pytest.approx(0.06)
    assert "mass_drift" in failure["lightweight_failure_reasons"]
