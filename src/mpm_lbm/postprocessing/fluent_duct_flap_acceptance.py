from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from .fluent_duct_flap_io import parse_bool, parse_float, read_csv_rows, read_json, write_json


def load_step155_summary(solver_root: Path) -> dict[str, Any]:
    return read_json(Path(solver_root) / "solver_v1_summary.json")


def summarize_mass_flux(mass_flux_csv: Path, tail_fraction: float = 0.2) -> dict[str, Any]:
    rows = read_csv_rows(mass_flux_csv)
    if not rows:
        raise ValueError(f"mass flux csv has no rows: {mass_flux_csv}")
    tail_count = max(1, math.ceil(len(rows) * tail_fraction))
    tail_rows = rows[-tail_count:]
    inlet = _mean(tail_rows, "inlet_flux")
    outlet = _mean(tail_rows, "outlet_flux")
    midplane = _mean(tail_rows, "midplane_flux")
    imbalance = _mean(tail_rows, "flux_imbalance_rel")
    outlet_ratio = _mean(tail_rows, "outlet_to_inlet_flux_ratio")
    midplane_ratio = _mean(tail_rows, "midplane_to_inlet_flux_ratio")
    gate_pass = abs(outlet_ratio) >= 0.5 and abs(imbalance) <= 0.5
    return {
        "status": "mass_flux_summary_written",
        "mass_flux_rows": len(rows),
        "tail_fraction": tail_fraction,
        "tail_row_count": tail_count,
        "inlet_flux_tail_mean": inlet,
        "outlet_flux_tail_mean": outlet,
        "midplane_flux_tail_mean": midplane,
        "flux_imbalance_rel_tail_mean": imbalance,
        "outlet_to_inlet_flux_ratio_tail_mean": outlet_ratio,
        "midplane_to_inlet_flux_ratio_tail_mean": midplane_ratio,
        "flow_development_gate_pass": bool(gate_pass),
        "flow_development_gate_policy": "report_only_for_step156",
    }


def summarize_stability(stability_csv: Path) -> dict[str, Any]:
    rows = read_csv_rows(stability_csv)
    if not rows:
        raise ValueError(f"stability csv has no rows: {stability_csv}")
    density_pass = all(parse_bool(row.get("density_gate_pass_step")) for row in rows)
    mpm_j_pass = all(parse_bool(row.get("mpm_j_gate_pass_step")) for row in rows)
    finite_pass = all(parse_bool(row.get("finite_gate_pass_step")) for row in rows)
    velocity_finite = all(parse_bool(row.get("velocity_finite")) for row in rows)
    population_finite = all(parse_bool(row.get("population_finite")) for row in rows)
    rho_finite = all(parse_bool(row.get("rho_finite")) for row in rows)
    return {
        "status": "stability_summary_written",
        "stability_rows": len(rows),
        "density_gate_pass": bool(density_pass),
        "mpm_j_gate_pass": bool(mpm_j_pass),
        "finite_gate_pass": bool(finite_pass and velocity_finite and population_finite and rho_finite),
        "rho_min": min(parse_float(row.get("rho_min")) for row in rows),
        "rho_max": max(parse_float(row.get("rho_max")) for row in rows),
        "lbm_max_v": max(parse_float(row.get("lbm_max_v")) for row in rows),
        "mpm_min_J": min(parse_float(row.get("mpm_min_J")) for row in rows),
        "mpm_max_speed": max(parse_float(row.get("mpm_max_speed")) for row in rows),
    }


def build_solver_acceptance_report(
    step155_summary: dict,
    mass_flux_summary: dict,
    stability_summary: dict,
    output_path: Path,
) -> dict[str, Any]:
    step_window_pass = (
        step155_summary.get("n_steps_completed") == 50
        and abs(float(step155_summary.get("time_end_s", -1.0)) - 0.025) < 1.0e-12
    )
    solver_sanity = bool(
        step_window_pass
        and step155_summary.get("density_gate_pass") is True
        and step155_summary.get("finite_gate_pass") is True
        and step155_summary.get("mpm_j_gate_pass") is True
        and stability_summary.get("density_gate_pass") is True
        and stability_summary.get("finite_gate_pass") is True
        and stability_summary.get("mpm_j_gate_pass") is True
    )
    report = {
        "step": 156,
        "status": "solver_acceptance_report_written",
        "source_step155_status": step155_summary.get("status"),
        "postprocess_acceptance_pass": True,
        "solver_numerical_sanity_pass": solver_sanity,
        "step_window_pass": bool(step_window_pass),
        "density_gate_pass": bool(
            step155_summary.get("density_gate_pass") is True
            and stability_summary.get("density_gate_pass") is True
        ),
        "finite_gate_pass": bool(
            step155_summary.get("finite_gate_pass") is True
            and stability_summary.get("finite_gate_pass") is True
        ),
        "mpm_j_gate_pass": bool(
            step155_summary.get("mpm_j_gate_pass") is True
            and stability_summary.get("mpm_j_gate_pass") is True
        ),
        "flow_development_gate_pass": bool(mass_flux_summary["flow_development_gate_pass"]),
        "flow_development_gate_policy": "report_only_for_step156",
        "flow_development_not_required_for_postprocess_completion": True,
        "flow_development_gate_reported": True,
        "mass_flux_rows": mass_flux_summary["mass_flux_rows"],
        "tail_fraction": mass_flux_summary["tail_fraction"],
        "tail_row_count": mass_flux_summary["tail_row_count"],
        "inlet_flux_tail_mean": mass_flux_summary["inlet_flux_tail_mean"],
        "outlet_flux_tail_mean": mass_flux_summary["outlet_flux_tail_mean"],
        "midplane_flux_tail_mean": mass_flux_summary["midplane_flux_tail_mean"],
        "flux_imbalance_rel_tail_mean": mass_flux_summary["flux_imbalance_rel_tail_mean"],
        "outlet_to_inlet_flux_ratio_tail_mean": mass_flux_summary[
            "outlet_to_inlet_flux_ratio_tail_mean"
        ],
        "midplane_to_inlet_flux_ratio_tail_mean": mass_flux_summary[
            "midplane_to_inlet_flux_ratio_tail_mean"
        ],
        "official_monitor_loaded": False,
        "official_error_metrics_available": False,
        "validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    write_json(output_path, report)
    return report


def _mean(rows: list[dict[str, str]], field: str) -> float:
    values = [parse_float(row.get(field)) for row in rows]
    return float(sum(values) / len(values)) if values else 0.0
