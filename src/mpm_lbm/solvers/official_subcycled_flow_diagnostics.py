from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

from .official_duct_flap_io import write_json


STEP = 157
FLOW_GATE_POLICY = (
    "flow gate requires abs(outlet_to_inlet_flux_ratio_tail_mean) >= 0.5 and "
    "abs(flux_imbalance_rel_tail_mean) <= 0.5"
)


def compute_required_lbm_substeps(
    compiled_case: dict,
    target_u_lbm: tuple[float, float, float],
) -> dict[str, Any]:
    setup = compiled_case["official_tutorial_setup"]
    grid = compiled_case["solver_grid"]
    n_grid = int(grid["nx"])
    duct_length_m = float(setup["duct_length_m"])
    target_inlet_velocity_mps = float(setup["inlet_air_velocity_mps"])
    target_u_x = float(target_u_lbm[0])
    official_dt_s = float(setup["official_tutorial_dt_s"])
    official_steps = int(setup["official_tutorial_time_steps"])
    dx_phys_m = duct_length_m / float(n_grid)
    lbm_dt_phys_s = target_u_x * dx_phys_m / target_inlet_velocity_mps
    required_substeps = int(round(official_dt_s / lbm_dt_phys_s))
    return {
        "step": STEP,
        "status": "lbm_substeps_required_computed",
        "duct_length_m": duct_length_m,
        "n_grid": n_grid,
        "dx_phys_m": dx_phys_m,
        "target_u_lbm": target_u_x,
        "target_inlet_velocity_mps": target_inlet_velocity_mps,
        "lbm_dt_phys_s": lbm_dt_phys_s,
        "official_fsi_dt_s": official_dt_s,
        "required_lbm_substeps_per_fsi_step": required_substeps,
        "required_total_lbm_substeps_for_50_official_steps": required_substeps * official_steps,
        "official_steps": official_steps,
        "validation_claim_allowed": False,
    }


def diagnose_step155_time_scale(
    step155_summary: dict,
    step156_acceptance: dict,
    compiled_case: dict,
) -> dict[str, Any]:
    required = compute_required_lbm_substeps(compiled_case, (0.02, 0.0, 0.0))
    step155_substeps_per_step = int(step155_summary.get("lbm_substeps_per_fsi_step", 1))
    step155_total_substeps = int(step155_summary.get("n_steps_completed", 0)) * step155_substeps_per_step
    report = {
        **required,
        "status": "time_scale_mismatch_diagnosed",
        "source_step155_status": step155_summary.get("status"),
        "source_step156_status": "official_tutorial_postprocess_complete",
        "step155_lbm_substeps_per_fsi_step": step155_substeps_per_step,
        "step155_total_lbm_substeps": step155_total_substeps,
        "step155_subcycling_deficit_factor": int(
            required["required_lbm_substeps_per_fsi_step"] / max(step155_substeps_per_step, 1)
        ),
        "step156_flow_development_gate_pass": bool(
            step156_acceptance.get("flow_development_gate_pass")
        ),
        "step156_inlet_flux_tail_mean": float(step156_acceptance.get("inlet_flux_tail_mean", 0.0)),
        "step156_outlet_flux_tail_mean": float(step156_acceptance.get("outlet_flux_tail_mean", 0.0)),
        "step156_outlet_to_inlet_flux_ratio_tail_mean": float(
            step156_acceptance.get("outlet_to_inlet_flux_ratio_tail_mean", 0.0)
        ),
        "step156_flux_imbalance_rel_tail_mean": float(
            step156_acceptance.get("flux_imbalance_rel_tail_mean", 0.0)
        ),
        "repair_hypothesis": (
            "one LBM step per official FSI step under-advects the flow; use "
            "lbm_subcycled_per_fsi_step with 120 LBM substeps per official step"
        ),
        "validation_claim_allowed": False,
    }
    return report


def summarize_step156_flux_failure(
    step156_x_flux_csv: Path,
    step156_acceptance: dict,
) -> dict[str, Any]:
    rows = _read_csv_rows(step156_x_flux_csv)
    mass_flux = [_parse_float(row.get("mass_flux_lbm")) for row in rows]
    max_abs = max((abs(value) for value in mass_flux), default=0.0)
    cutoff_index = None
    if max_abs > 0.0:
        for row, value in zip(rows, mass_flux):
            if abs(value) <= 0.1 * max_abs:
                cutoff_index = int(row.get("x_index", 0))
                break
    return {
        "step": STEP,
        "status": "step156_flux_failure_summarized",
        "row_count": len(rows),
        "first_x_index_below_10pct_max_abs_flux": cutoff_index,
        "step156_flow_development_gate_pass": bool(
            step156_acceptance.get("flow_development_gate_pass")
        ),
        "step156_outlet_to_inlet_flux_ratio_tail_mean": float(
            step156_acceptance.get("outlet_to_inlet_flux_ratio_tail_mean", 0.0)
        ),
        "validation_claim_allowed": False,
    }


def summarize_mass_flux_tail(mass_flux_csv: Path, tail_fraction: float = 0.2) -> dict[str, Any]:
    rows = _read_csv_rows(mass_flux_csv)
    if not rows:
        raise ValueError(f"mass flux csv has no rows: {mass_flux_csv}")
    tail_count = max(1, math.ceil(len(rows) * tail_fraction))
    tail_rows = rows[-tail_count:]
    tail_first_step = int(_parse_float(tail_rows[0].get("official_step", tail_rows[0].get("step"))))
    tail_last_step = int(_parse_float(tail_rows[-1].get("official_step", tail_rows[-1].get("step"))))
    inlet = _mean(tail_rows, "inlet_flux")
    outlet = _mean(tail_rows, "outlet_flux")
    midplane = _mean(tail_rows, "midplane_flux")
    imbalance = _mean(tail_rows, "flux_imbalance_rel")
    outlet_ratio = _mean(tail_rows, "outlet_to_inlet_flux_ratio")
    midplane_ratio = _mean(tail_rows, "midplane_to_inlet_flux_ratio")
    gate_pass = abs(outlet_ratio) >= 0.5 and abs(imbalance) <= 0.5
    return {
        "mass_flux_rows": len(rows),
        "tail_fraction": tail_fraction,
        "tail_row_count": tail_count,
        "tail_first_official_step": tail_first_step,
        "tail_last_official_step": tail_last_step,
        "inlet_flux_tail_mean": inlet,
        "outlet_flux_tail_mean": outlet,
        "midplane_flux_tail_mean": midplane,
        "flux_imbalance_rel_tail_mean": imbalance,
        "outlet_to_inlet_flux_ratio_tail_mean": outlet_ratio,
        "midplane_to_inlet_flux_ratio_tail_mean": midplane_ratio,
        "flow_development_gate_pass": bool(gate_pass),
    }


def summarize_stability_gate(stability_csv: Path | None) -> dict[str, Any]:
    if stability_csv is None:
        return {
            "stability_rows": 0,
            "density_gate_pass": True,
            "finite_gate_pass": True,
            "first_density_gate_failure_step": None,
            "first_finite_gate_failure_step": None,
        }

    rows = _read_csv_rows(stability_csv)
    first_density_failure = None
    first_finite_failure = None
    first_density_row: dict[str, str] | None = None
    first_finite_row: dict[str, str] | None = None
    density_pass = True
    finite_pass = True

    for row in rows:
        step = int(_parse_float(row.get("official_step", row.get("step", 0))))
        if not _parse_bool(row.get("density_gate_pass_step"), default=True):
            density_pass = False
            if first_density_failure is None:
                first_density_failure = step
                first_density_row = row
        if not _parse_bool(row.get("finite_gate_pass_step"), default=True):
            finite_pass = False
            if first_finite_failure is None:
                first_finite_failure = step
                first_finite_row = row

    return {
        "stability_rows": len(rows),
        "density_gate_pass": bool(density_pass),
        "finite_gate_pass": bool(finite_pass),
        "first_density_gate_failure_step": first_density_failure,
        "first_finite_gate_failure_step": first_finite_failure,
        "first_density_gate_failure_rho_min": (
            None if first_density_row is None else _parse_float(first_density_row.get("rho_min"))
        ),
        "first_density_gate_failure_rho_max": (
            None if first_density_row is None else _parse_float(first_density_row.get("rho_max"))
        ),
        "first_density_gate_failure_lbm_max_v": (
            None if first_density_row is None else _parse_float(first_density_row.get("lbm_max_v"))
        ),
        "first_finite_gate_failure_lbm_max_v": (
            None if first_finite_row is None else _parse_float(first_finite_row.get("lbm_max_v"))
        ),
    }


def build_flow_development_comparison_report(
    step156_acceptance: dict,
    subcycled_mass_flux_csv: Path,
    output_path: Path,
    tail_fraction: float = 0.2,
    stability_csv: Path | None = None,
) -> dict[str, Any]:
    baseline = {
        "flow_development_gate_pass": bool(step156_acceptance.get("flow_development_gate_pass")),
        "inlet_flux_tail_mean": float(step156_acceptance.get("inlet_flux_tail_mean", 0.0)),
        "outlet_flux_tail_mean": float(step156_acceptance.get("outlet_flux_tail_mean", 0.0)),
        "outlet_to_inlet_flux_ratio_tail_mean": float(
            step156_acceptance.get("outlet_to_inlet_flux_ratio_tail_mean", 0.0)
        ),
        "flux_imbalance_rel_tail_mean": float(
            step156_acceptance.get("flux_imbalance_rel_tail_mean", 0.0)
        ),
    }
    subcycled = summarize_mass_flux_tail(subcycled_mass_flux_csv, tail_fraction)
    stability = summarize_stability_gate(stability_csv)
    raw_outlet_improved = abs(subcycled["outlet_to_inlet_flux_ratio_tail_mean"]) > abs(
        baseline["outlet_to_inlet_flux_ratio_tail_mean"]
    )
    raw_imbalance_improved = abs(subcycled["flux_imbalance_rel_tail_mean"]) < abs(
        baseline["flux_imbalance_rel_tail_mean"]
    )
    flow_metrics_valid = bool(stability["density_gate_pass"] and stability["finite_gate_pass"])
    invalid_reason = None
    if not stability["density_gate_pass"]:
        invalid_reason = _stability_failure_reason(
            "density_gate_failed",
            stability["first_density_gate_failure_step"],
            subcycled["tail_first_official_step"],
            subcycled["tail_last_official_step"],
        )
    elif not stability["finite_gate_pass"]:
        invalid_reason = _stability_failure_reason(
            "finite_gate_failed",
            stability["first_finite_gate_failure_step"],
            subcycled["tail_first_official_step"],
            subcycled["tail_last_official_step"],
        )

    subcycled = {
        **subcycled,
        "density_gate_pass": bool(stability["density_gate_pass"]),
        "finite_gate_pass": bool(stability["finite_gate_pass"]),
        "first_density_gate_failure_step": stability["first_density_gate_failure_step"],
        "first_finite_gate_failure_step": stability["first_finite_gate_failure_step"],
        "flow_metrics_valid_for_gate": flow_metrics_valid,
        "flow_metrics_invalid_reason": invalid_reason,
    }
    report = {
        "step": STEP,
        "status": "flow_development_comparison_written",
        "baseline_step155_step156": baseline,
        "subcycled_step157": subcycled,
        "raw_outlet_flux_ratio_improved": bool(raw_outlet_improved),
        "raw_flux_imbalance_improved": bool(raw_imbalance_improved),
        "outlet_flux_ratio_improved": bool(flow_metrics_valid and raw_outlet_improved),
        "flux_imbalance_improved": bool(flow_metrics_valid and raw_imbalance_improved),
        "flow_metrics_valid_for_gate": flow_metrics_valid,
        "flow_metrics_invalid_reason": invalid_reason,
        "first_density_gate_failure_step": stability["first_density_gate_failure_step"],
        "first_finite_gate_failure_step": stability["first_finite_gate_failure_step"],
        "stability_gate_summary": stability,
        "subcycling_repair_success": bool(flow_metrics_valid and subcycled["flow_development_gate_pass"]),
        "subcycling_repair_success_policy": FLOW_GATE_POLICY,
        "validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
    }
    write_json(output_path, report)
    return report


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _mean(rows: list[dict[str, str]], field: str) -> float:
    values = [_parse_float(row.get(field)) for row in rows]
    return float(sum(values) / len(values)) if values else 0.0


def _parse_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _parse_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return default


def _stability_failure_reason(
    prefix: str,
    failure_step: int | None,
    tail_first_step: int,
    tail_last_step: int,
) -> str:
    if failure_step is None:
        return f"{prefix}_unknown_step"
    if failure_step < tail_first_step:
        return f"{prefix}_before_tail_window"
    if failure_step <= tail_last_step:
        return f"{prefix}_during_tail_window"
    return f"{prefix}_after_tail_window"
