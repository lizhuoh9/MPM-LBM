import json
import subprocess
import sys
from pathlib import Path


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
    flux_max=0.08,
    inlet_flux=0.03,
    outlet_flux=0.03,
    outlet_ratio=None,
    midplane_ratio=1.0,
    outlet_cv=0.02,
    mass=0.001,
    mach=0.08,
    limiter=0.0,
    first_failure_reason=None,
    skipped_reason=None,
    solver_state_hash="candidate-config-hash",
    selected_source_hash=None,
):
    first_failure = None if complete and first_failure_reason is None else 10
    if outlet_ratio is None:
        outlet_ratio = abs(float(outlet_flux) / float(inlet_flux)) if inlet_flux else None
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
        "step120_validation_claimed": bool(validation and complete and first_failure_reason is None),
        "simulation_backed_artifact": bool(simulation),
        "not_used_for_validation": False,
        "finite_pass": True,
        "density_gate_pass": True,
        "mass_drift_gate_pass": abs(mass) < 0.005,
        "population_gate_pass": True,
        "mach_gate_pass": mach < 0.20,
        "first_failure_step": first_failure,
        "first_failure_reason": first_failure_reason,
        "skipped_reason": skipped_reason,
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
        "mach_proxy_observed_max": float(mach),
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
        "config_hash": solver_state_hash,
        "solver_state_hash": solver_state_hash,
        "selected_source_row_name": "duct_only_48_regularized_limited_boundary_500step_real"
        if role in {"selected_96_duct", "selected_96_static"}
        else None,
        "selected_source_config_hash": selected_source_hash
        if selected_source_hash is not None
        else (solver_state_hash if role in {"selected_96_duct", "selected_96_static"} else None),
        "selected_source_tau": 0.572 if role in {"selected_96_duct", "selected_96_static"} else None,
        "selected_source_lbm_relaxation_semantics": "legacy_external_solver_parameter"
        if role in {"selected_96_duct", "selected_96_static"}
        else None,
    }


def _write_finite(row_dir: Path, row: dict) -> None:
    row_dir.mkdir(parents=True, exist_ok=True)
    (row_dir / "finite_stability_report.json").write_text(
        json.dumps({"summary_row": row}, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _references(*, legacy_complete=True, regularized_complete=True, regularized_failure=None):
    return [
        _row(
            "duct_only_48_legacy_boundary_500step_reference_real",
            "equilibrium_all_population_reset",
            role="reference_48",
            complete=legacy_complete,
            validation=legacy_complete,
            first_failure_reason=None if legacy_complete else "rho_range",
            flux=0.08,
            solver_state_hash="legacy-reference-hash",
        ),
        _row(
            "duct_only_48_regularized_boundary_500step_reference_real",
            "regularized_velocity_pressure",
            role="reference_48",
            complete=regularized_complete,
            validation=regularized_complete,
            first_failure_reason=regularized_failure,
            flux=0.20,
            solver_state_hash="regularized-reference-hash",
        ),
    ]


def _passing_candidates():
    return [
        _row(
            "duct_only_48_regularized_limited_boundary_500step_real",
            "regularized_velocity_pressure_limited",
            role="candidate_48",
            flux=0.04,
            solver_state_hash="limited-candidate-hash",
        ),
        _row(
            "duct_only_48_convective_outlet_boundary_500step_real",
            "convective_pressure_outlet_experimental",
            role="candidate_48",
            flux=0.05,
            solver_state_hash="convective-candidate-hash",
        ),
    ]


def test_step124_legacy_reference_physical_failure_stops_campaign():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        select_step121_best_boundary,
    )

    selection = select_step121_best_boundary(_references(legacy_complete=False) + _passing_candidates())

    assert selection["campaign_state"] == "48_legacy_reference_failed"
    assert selection["final_classification"] == "boundary_repair_failed_revisit_lbm_solver"
    assert selection["campaign_should_stop_at_48"] is True
    assert selection["reference_status"]["failed_reference_semantics"] == ["equilibrium_all_population_reset"]


def test_step124_old_regularized_reference_failure_is_comparison_evidence():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        select_step121_best_boundary,
    )

    rows = _references(regularized_complete=False, regularized_failure="rho_range") + _passing_candidates()

    selection = select_step121_best_boundary(rows)

    assert selection["reference_comparison_ready"] is True
    assert selection["reference_status"]["failed_reference_semantics"] == ["regularized_velocity_pressure"]
    assert selection["campaign_state"] == "best_48_selected"
    assert selection["best_boundary_selected"] is True


def test_step124_zero_throughput_candidate_cannot_pass():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        select_step121_best_boundary,
    )

    zero_flow = _row(
        "duct_only_48_regularized_limited_boundary_500step_real",
        "regularized_velocity_pressure_limited",
        role="candidate_48",
        flux=0.0,
        flux_max=0.0,
        inlet_flux=0.0,
        outlet_flux=0.0,
        outlet_ratio=None,
        midplane_ratio=0.0,
        solver_state_hash="limited-candidate-hash",
    )
    rows = _references() + [zero_flow, _passing_candidates()[1]]

    selection = select_step121_best_boundary(rows)
    limited = next(row for row in selection["candidate_summaries"] if row["name"] == zero_flow["name"])

    assert limited["candidate_pass"] is False
    assert "inlet_flux_tail_mean" in limited["flow_development_rejection_reasons"]
    assert selection["selected_row_name"] == "duct_only_48_convective_outlet_boundary_500step_real"


def test_step124_average_correct_but_oscillating_candidate_cannot_pass():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        select_step121_best_boundary,
    )

    oscillating = _row(
        "duct_only_48_regularized_limited_boundary_500step_real",
        "regularized_velocity_pressure_limited",
        role="candidate_48",
        flux=0.04,
        flux_max=0.08,
        outlet_cv=0.45,
        solver_state_hash="limited-candidate-hash",
    )
    rows = _references() + [oscillating, _passing_candidates()[1]]

    selection = select_step121_best_boundary(rows)
    limited = next(row for row in selection["candidate_summaries"] if row["name"] == oscillating["name"])

    assert limited["candidate_pass"] is False
    assert "outlet_flux_tail_cv" in limited["flow_development_rejection_reasons"]
    assert selection["selected_row_name"] == "duct_only_48_convective_outlet_boundary_500step_real"


def test_step124_selected_96_requires_throughput_ratio_and_tail_stationarity():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        build_step121_gate_report,
        select_step121_best_boundary,
    )

    selection = select_step121_best_boundary(_references() + _passing_candidates())
    duct = _row(
        "duct_only_96_limited_1000step_real",
        "regularized_velocity_pressure_limited",
        role="selected_96_duct",
        nx=96,
        steps=1000,
        flux=0.04,
        inlet_flux=0.03,
        outlet_flux=0.006,
        outlet_ratio=0.20,
        midplane_ratio=1.0,
        outlet_cv=0.02,
        solver_state_hash="selected-duct-hash",
        selected_source_hash="limited-candidate-hash",
    )
    static = _row(
        "static_two_flap_96_limited_1000step_real",
        "regularized_velocity_pressure_limited",
        role="selected_96_static",
        nx=96,
        steps=1000,
        flux=0.04,
        inlet_flux=0.03,
        outlet_flux=0.03,
        outlet_ratio=1.0,
        midplane_ratio=1.0,
        outlet_cv=0.30,
        solver_state_hash="selected-static-hash",
        selected_source_hash="limited-candidate-hash",
    )

    gate = build_step121_gate_report(_references() + _passing_candidates() + [duct, static], selection)

    assert gate["campaign_state"] == "awaiting_selected_96_duct"
    assert gate["selected_96_flow_development_gate"]["duct_pass"] is False
    assert "outlet_to_inlet_flux_ratio_tail_mean" in gate["selected_96_flow_development_gate"]["duct_reasons"]
    assert gate["selected_96_flow_development_gate"]["static_pass"] is False
    assert "outlet_flux_tail_cv" in gate["selected_96_flow_development_gate"]["static_reasons"]


def test_step124_summary_ignores_stale_solver_state_and_wrong_selected_source(tmp_path):
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        collect_step121_rows,
    )

    good = _row(
        "duct_only_48_regularized_limited_boundary_500step_real",
        "regularized_velocity_pressure_limited",
        role="candidate_48",
        solver_state_hash="expected-hash",
    )
    stale = {**good, "name": "duct_only_48_convective_outlet_boundary_500step_real", "solver_state_hash": "old-hash"}
    wrong_source = _row(
        "duct_only_96_limited_1000step_real",
        "regularized_velocity_pressure_limited",
        role="selected_96_duct",
        nx=96,
        steps=1000,
        solver_state_hash="selected-hash",
        selected_source_hash="wrong-source",
    )
    _write_finite(tmp_path / good["name"], good)
    _write_finite(tmp_path / stale["name"], stale)
    _write_finite(tmp_path / wrong_source["name"], wrong_source)
    (tmp_path / "campaign_manifest.json").write_text(
        json.dumps(
            {
                "campaign_id": "step124-test",
                "git_commit": "516b1aaa4c71d5468ce5ea444a21ffa07741c8bc",
                "expected_rows": {
                    good["name"]: {"solver_state_hash": "expected-hash"},
                    stale["name"]: {"solver_state_hash": "expected-hash"},
                    wrong_source["name"]: {
                        "solver_state_hash": "selected-hash",
                        "selected_source_config_hash": "expected-source",
                    },
                },
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    collected = collect_step121_rows(tmp_path, return_ignored=True)

    assert [row["name"] for row in collected["rows"]] == [good["name"]]
    ignored = {row["name"]: row["ignored_reasons"] for row in collected["ignored_rows"]}
    assert ignored[stale["name"]] == ["solver_state_hash_mismatch"]
    assert ignored[wrong_source["name"]] == ["selected_source_config_hash_mismatch"]


def test_step124_current_docs_entry_is_bounded_and_consistent():
    active_path = ROOT / "docs" / "current" / "ACTIVE_CAMPAIGN.json"
    status_path = ROOT / "docs" / "current" / "STATUS.md"
    gates_path = ROOT / "docs" / "current" / "VALIDATION_GATES.md"
    reading_path = ROOT / "docs" / "current" / "READING_ORDER.md"
    gate_report_path = ROOT / "outputs" / "step121_lbm_boundary_real_campaign_and_gate_correction" / "step121_gate_report.json"

    for path in (active_path, status_path, gates_path, reading_path, gate_report_path):
        assert path.is_file(), path

    active = json.loads(active_path.read_text(encoding="utf-8"))
    gate = json.loads(gate_report_path.read_text(encoding="utf-8"))
    status = status_path.read_text(encoding="utf-8")

    assert active["state"] == gate["campaign_state"]
    assert active["final_classification"] == gate["final_classification"]
    assert len(active["read_first"]) <= 8
    for rel_path in active["read_first"]:
        assert (ROOT / rel_path).exists(), rel_path
    assert "quasi-2D" in status
    assert "FSI" in status
    assert "Fluent" in status
    assert "awaiting_48_references" in status
    assert active["base_commit"] == "516b1aaa4c71d5468ce5ea444a21ffa07741c8bc"
    subprocess.check_call(["git", "merge-base", "--is-ancestor", active["base_commit"], "HEAD"], cwd=ROOT)
