import math


PHASE_SEQUENCE = [
    0.0, 0.025, 0.05, 0.075, 0.1,
    0.125, 0.15, 0.175, 0.2, 0.225,
    0.25, 0.275, 0.3, 0.325, 0.35,
    0.375, 0.4, 0.425, 0.45, 0.475,
    0.5, 0.525, 0.55, 0.575, 0.6,
    0.625, 0.65, 0.675, 0.7, 0.725,
    0.75, 0.775, 0.8, 0.825, 0.85,
    0.875, 0.9, 0.925, 0.95, 0.975,
]
WALL_VELOCITY_CLOSURE_TOLERANCE = 5.0e-4


def summarize_48_feasibility_quality(rows: list[dict], closure_rows: list[dict] | None = None) -> dict:
    by_name = {row["row_name"]: row for row in rows}
    static = by_name.get("engineering_static_48_40step", {})
    combined = by_name.get("engineering_runtime_geometry_plus_wall_velocity_48_40step", {})
    component_rows, component_summary = compare_48_static_combined(rows)
    closure_summary = summarize_48_cycle_closure(closure_rows or [])[1] if closure_rows is not None else {"closure_pass": True}
    row_count_pass = len(rows) == 2
    step_count_pass = all(len(row["step_records"]) == 40 for row in rows)
    stability_pass = all(bool(row["stable"]) for row in rows)
    projection_pass = all(float(row["projected_mass_min"]) > 0.0 and int(row["active_cell_count_min"]) > 0 for row in rows)
    transfer_mode_pass = all(row["reaction_transfer_mode"] == "engineering" for row in rows)
    diagnostic_only_pass = all(bool(row["diagnostic_only"]) for row in rows)
    no_persistent_state_pass = all(
        not bool(row["persist_projected_state"])
        and not bool(row["persist_displaced_geometry"])
        and not bool(row["persist_lbm_solid_vel"])
        for row in rows
    )
    combined_row_pass = bool(
        combined
        and combined["runtime_geometry_projection_enabled"]
        and combined["wall_velocity_application_enabled"]
        and int(combined["active_cell_count_delta_from_original_max"]) > 0
        and int(combined["applied_cell_count_max"]) > 0
    )
    static_row_pass = bool(static and not static["runtime_geometry_projection_enabled"] and not static["wall_velocity_application_enabled"])
    return {
        "row_count": len(rows),
        "row_count_pass": bool(row_count_pass),
        "static_row_pass": bool(static_row_pass),
        "combined_row_pass": bool(combined_row_pass),
        "step_count_pass": bool(step_count_pass),
        "stability_pass": bool(stability_pass),
        "projection_pass": bool(projection_pass),
        "transfer_mode_pass": bool(transfer_mode_pass),
        "component_effect_pass": bool(component_summary["comparison_pass"] and all(bool(row["comparison_pass"]) for row in component_rows)),
        "closure_pass": bool(closure_summary["closure_pass"]),
        "diagnostic_only_pass": bool(diagnostic_only_pass),
        "no_persistent_state_pass": bool(no_persistent_state_pass),
        "quality_pass": bool(
            row_count_pass
            and static_row_pass
            and combined_row_pass
            and step_count_pass
            and stability_pass
            and projection_pass
            and transfer_mode_pass
            and component_summary["comparison_pass"]
            and diagnostic_only_pass
            and no_persistent_state_pass
        ),
    }


def compare_48_static_combined(rows: list[dict]) -> tuple[list[dict], dict]:
    by_name = {row["row_name"]: row for row in rows}
    static = by_name["engineering_static_48_40step"]
    combined = by_name["engineering_runtime_geometry_plus_wall_velocity_48_40step"]
    row = {
        "comparison": "combined_minus_static_48",
        "left_row": combined["row_name"],
        "right_row": static["row_name"],
        "active_cell_delta_max_abs": _max_step_abs_delta(combined, static, "active_cell_count"),
        "applied_velocity_delta_max_abs": _max_step_abs_delta(combined, static, "max_applied_velocity_norm"),
        "hydro_force_delta_max_abs": _max_step_abs_delta(combined, static, "hydro_force_max_norm"),
        "bb_link_count_delta_max_abs": _max_step_abs_delta(combined, static, "bb_link_count"),
        "rho_min_delta_max_abs": _max_step_abs_delta(combined, static, "rho_min"),
        "rho_max_delta_max_abs": _max_step_abs_delta(combined, static, "rho_max"),
        "lbm_max_v_delta_max_abs": _max_step_abs_delta(combined, static, "lbm_max_v"),
        "hydro_force_max_norm": float(combined["hydro_force_max_norm_global"]),
        "impulse_proxy_max_norm": float(combined["impulse_proxy_max_norm"]),
    }
    row["comparison_pass"] = bool(
        _finite_comparison(row)
        and float(row["active_cell_delta_max_abs"]) > 0.0
        and float(row["applied_velocity_delta_max_abs"]) > 0.0
        and float(row["hydro_force_max_norm"]) < 0.05
        and float(row["impulse_proxy_max_norm"]) < 1.0
    )
    summary = {
        "comparison_count": 1,
        "comparison_pass_count": 1 if row["comparison_pass"] else 0,
        "runtime_geometry_effect_active_cell_delta_nonzero": float(row["active_cell_delta_max_abs"]) > 0.0,
        "wall_velocity_effect_applied_velocity_nonzero": float(row["applied_velocity_delta_max_abs"]) > 0.0,
        "hydro_force_max_norm_finite": math.isfinite(float(row["hydro_force_max_norm"])),
        "impulse_proxy_max_norm_finite": math.isfinite(float(row["impulse_proxy_max_norm"])),
        "bb_link_count_delta_finite": math.isfinite(float(row["bb_link_count_delta_max_abs"])),
        "rho_delta_finite": math.isfinite(float(row["rho_min_delta_max_abs"])) and math.isfinite(float(row["rho_max_delta_max_abs"])),
        "lbm_velocity_delta_finite": math.isfinite(float(row["lbm_max_v_delta_max_abs"])),
    }
    summary["comparison_pass"] = bool(
        row["comparison_pass"]
        and summary["runtime_geometry_effect_active_cell_delta_nonzero"]
        and summary["wall_velocity_effect_applied_velocity_nonzero"]
        and summary["hydro_force_max_norm_finite"]
        and summary["impulse_proxy_max_norm_finite"]
        and summary["bb_link_count_delta_finite"]
        and summary["rho_delta_finite"]
        and summary["lbm_velocity_delta_finite"]
    )
    return [row], summary


def compare_48_vs_step51_engineering(step51_rows: list[dict], step52_rows: list[dict], artifact_size_ratio: float = 1.0) -> tuple[list[dict], dict]:
    reference = next(row for row in step51_rows if row["row_name"] == "engineering_runtime_geometry_plus_wall_velocity_32_40step")
    combined = next(row for row in step52_rows if row["row_name"] == "engineering_runtime_geometry_plus_wall_velocity_48_40step")
    row = {
        "comparison": "step52_48_engineering_combined_vs_step51_32_engineering_combined",
        "step51_row": reference["row_name"],
        "step52_row": combined["row_name"],
        "active_cell_count_32": int(_row_max(reference, "active_cell_count_max", "active_cell_count")),
        "active_cell_count_48": int(_row_max(combined, "active_cell_count_max", "active_cell_count")),
        "applied_cell_count_32": int(_row_max(reference, "applied_cell_count_max", "applied_cell_count")),
        "applied_cell_count_48": int(_row_max(combined, "applied_cell_count_max", "applied_cell_count")),
        "bb_link_count_32": int(_row_max(reference, "bb_link_count_max", "bb_link_count")),
        "bb_link_count_48": int(_row_max(combined, "bb_link_count_max", "bb_link_count")),
        "rho_span_32": float(reference["rho_max_global"]) - float(reference["rho_min_global"]),
        "rho_span_48": float(combined["rho_span_global"]),
        "lbm_max_v_32": float(reference["lbm_max_v_global"]),
        "lbm_max_v_48": float(combined["lbm_max_v_global"]),
        "hydro_force_max_norm_32": float(reference["hydro_force_max_norm_global"]),
        "hydro_force_max_norm_48": float(combined["hydro_force_max_norm_global"]),
        "impulse_proxy_32": float(reference["impulse_proxy_max_norm"]),
        "impulse_proxy_48": float(combined["impulse_proxy_max_norm"]),
        "bb_max_correction_48": float(combined["bb_max_correction_global"]),
        "rho_min_48": float(combined["rho_min_global"]),
        "rho_max_48": float(combined["rho_max_global"]),
        "artifact_size_ratio_48_vs_32": float(artifact_size_ratio),
    }
    row["active_cell_count_ratio_48_vs_32"] = _ratio(row["active_cell_count_48"], row["active_cell_count_32"])
    row["applied_cell_count_ratio_48_vs_32"] = _ratio(row["applied_cell_count_48"], row["applied_cell_count_32"])
    row["bb_link_count_ratio_48_vs_32"] = _ratio(row["bb_link_count_48"], row["bb_link_count_32"])
    row["rho_span_ratio_48_vs_32"] = _ratio(row["rho_span_48"], row["rho_span_32"])
    row["lbm_max_v_ratio_48_vs_32"] = _ratio(row["lbm_max_v_48"], row["lbm_max_v_32"])
    row["hydro_force_max_norm_ratio_48_vs_32"] = _ratio(row["hydro_force_max_norm_48"], row["hydro_force_max_norm_32"])
    row["impulse_proxy_ratio_48_vs_32"] = _ratio(row["impulse_proxy_48"], row["impulse_proxy_32"])
    row["active_cell_count_growth_observed"] = bool(row["active_cell_count_48"] > row["active_cell_count_32"])
    row["active_cell_count_non_decreasing"] = bool(row["active_cell_count_48"] >= row["active_cell_count_32"])
    row["applied_cell_count_growth_observed"] = bool(row["applied_cell_count_48"] > row["applied_cell_count_32"])
    ratio_fields = [key for key in row if key.endswith("_ratio_48_vs_32")]
    row["all_ratios_finite"] = all(math.isfinite(float(row[field])) for field in ratio_fields) and math.isfinite(float(row["artifact_size_ratio_48_vs_32"]))
    row["scaling_pass"] = bool(
        row["rho_min_48"] > 0.95
        and row["rho_max_48"] < 1.05
        and row["lbm_max_v_48"] < 0.1
        and row["bb_max_correction_48"] < 0.1
        and row["hydro_force_max_norm_48"] < 0.05
        and row["impulse_proxy_48"] < 1.0
        and row["active_cell_count_non_decreasing"]
        and row["applied_cell_count_growth_observed"]
        and row["bb_link_count_48"] > 0
        and row["all_ratios_finite"]
    )
    summary = {
        "comparison_count": 1,
        "scaling_pass": bool(row["scaling_pass"]),
        "all_ratios_finite": bool(row["all_ratios_finite"]),
        "active_cell_count_ratio_48_vs_32": row["active_cell_count_ratio_48_vs_32"],
        "applied_cell_count_ratio_48_vs_32": row["applied_cell_count_ratio_48_vs_32"],
        "bb_link_count_ratio_48_vs_32": row["bb_link_count_ratio_48_vs_32"],
        "rho_span_ratio_48_vs_32": row["rho_span_ratio_48_vs_32"],
        "lbm_max_v_ratio_48_vs_32": row["lbm_max_v_ratio_48_vs_32"],
        "hydro_force_max_norm_ratio_48_vs_32": row["hydro_force_max_norm_ratio_48_vs_32"],
        "impulse_proxy_ratio_48_vs_32": row["impulse_proxy_ratio_48_vs_32"],
        "artifact_size_ratio_48_vs_32": row["artifact_size_ratio_48_vs_32"],
        "active_cell_count_growth_observed": bool(row["active_cell_count_growth_observed"]),
        "active_cell_count_non_decreasing": bool(row["active_cell_count_non_decreasing"]),
        "applied_cell_count_growth_observed": bool(row["applied_cell_count_growth_observed"]),
        "diagnostic_scaling_only": True,
        "grid_convergence_claim": False,
        "physical_validation_claim": False,
    }
    return [row], summary


def summarize_48_cycle_closure(closure_rows: list[dict]) -> tuple[list[dict], dict]:
    for row in closure_rows:
        row["geometry_projection_closure_pass"] = bool(
            math.isfinite(float(row["phase0_phase1_projected_mass_delta"]))
            and math.isfinite(float(row["phase0_phase1_active_cell_delta"]))
            and float(row["phase0_phase1_projected_mass_delta"]) <= 1.0e-8
            and int(row["phase0_phase1_active_cell_delta"]) <= 0
        )
        row["wall_velocity_closure_pass"] = bool(
            math.isfinite(float(row["phase0_phase1_applied_velocity_delta"]))
            and float(row["phase0_phase1_applied_velocity_delta"]) <= WALL_VELOCITY_CLOSURE_TOLERANCE
        )
        row["cycle_proxy_closure_pass"] = bool(row["geometry_projection_closure_pass"] and row["wall_velocity_closure_pass"] and bool(row["diagnostic_only"]))
        row["closure_pass"] = bool(row["closure_pass"] and row["cycle_proxy_closure_pass"])
    summary = {
        "row_count": len(closure_rows),
        "closure_phase": 1.0,
        "closure_pass_count": sum(1 for row in closure_rows if bool(row["closure_pass"])),
        "static_closure_pass": all(bool(row["closure_pass"]) for row in closure_rows if row["component_name"] == "static"),
        "combined_closure_pass": all(bool(row["closure_pass"]) for row in closure_rows if row["component_name"] == "runtime_geometry_plus_wall_velocity"),
        "geometry_projection_closure_pass": all(bool(row["geometry_projection_closure_pass"]) for row in closure_rows) if closure_rows else False,
        "wall_velocity_closure_pass": all(bool(row["wall_velocity_closure_pass"]) for row in closure_rows) if closure_rows else False,
        "cycle_proxy_closure_pass": all(bool(row["cycle_proxy_closure_pass"]) for row in closure_rows) if closure_rows else False,
        "phase0_phase1_projected_mass_delta_max": max((float(row["phase0_phase1_projected_mass_delta"]) for row in closure_rows), default=0.0),
        "phase0_phase1_active_cell_delta_max": max((int(row["phase0_phase1_active_cell_delta"]) for row in closure_rows), default=0),
        "phase0_phase1_applied_velocity_delta_max": max((float(row["phase0_phase1_applied_velocity_delta"]) for row in closure_rows), default=0.0),
        "wall_velocity_closure_tolerance": WALL_VELOCITY_CLOSURE_TOLERANCE,
    }
    summary["closure_pass"] = bool(
        len(closure_rows) == 2
        and int(summary["closure_pass_count"]) == 2
        and summary["static_closure_pass"]
        and summary["combined_closure_pass"]
        and summary["geometry_projection_closure_pass"]
        and summary["wall_velocity_closure_pass"]
        and summary["cycle_proxy_closure_pass"]
    )
    return closure_rows, summary


def mass_force_bounceback_48_envelope(rows: list[dict]) -> tuple[list[dict], dict]:
    diag_rows = []
    for row in rows:
        diag = {
            "row_name": row["row_name"],
            "component_name": row["component_name"],
            "rho_min_global": float(row["rho_min_global"]),
            "rho_max_global": float(row["rho_max_global"]),
            "rho_span_global": float(row["rho_span_global"]),
            "lbm_max_v_global": float(row["lbm_max_v_global"]),
            "bb_link_count_min": int(row["bb_link_count_min"]),
            "bb_link_count_max": int(row["bb_link_count_max"]),
            "bb_max_correction_global": float(row["bb_max_correction_global"]),
            "hydro_force_max_norm_global": float(row["hydro_force_max_norm_global"]),
            "impulse_proxy_max_norm": float(row["impulse_proxy_max_norm"]),
            "max_applied_velocity_norm": float(row["max_applied_velocity_norm"]),
            "wall_velocity_cap_lbm": float(row["wall_velocity_cap_lbm"]),
            "has_nan": bool(row["has_nan"]),
            "has_inf": bool(row["has_inf"]),
        }
        diag["envelope_pass"] = bool(
            diag["rho_min_global"] > 0.95
            and diag["rho_max_global"] < 1.05
            and diag["bb_link_count_min"] > 0
            and diag["bb_max_correction_global"] < 0.1
            and math.isfinite(diag["hydro_force_max_norm_global"])
            and math.isfinite(diag["impulse_proxy_max_norm"])
            and diag["hydro_force_max_norm_global"] < 0.05
            and diag["impulse_proxy_max_norm"] < 1.0
            and diag["max_applied_velocity_norm"] <= diag["wall_velocity_cap_lbm"] + 1.0e-12
            and not diag["has_nan"]
            and not diag["has_inf"]
        )
        diag_rows.append(diag)
    summary = {
        "row_count": len(diag_rows),
        "envelope_pass_count": sum(1 for row in diag_rows if bool(row["envelope_pass"])),
        "rho_min_global": min(float(row["rho_min_global"]) for row in diag_rows) if diag_rows else 0.0,
        "rho_max_global": max(float(row["rho_max_global"]) for row in diag_rows) if diag_rows else 0.0,
        "bb_max_correction_global": max(float(row["bb_max_correction_global"]) for row in diag_rows) if diag_rows else 0.0,
        "bb_link_count_min": min(int(row["bb_link_count_min"]) for row in diag_rows) if diag_rows else 0,
        "bb_link_count_max": max(int(row["bb_link_count_max"]) for row in diag_rows) if diag_rows else 0,
        "hydro_force_max_norm_global": max(float(row["hydro_force_max_norm_global"]) for row in diag_rows) if diag_rows else 0.0,
        "impulse_proxy_max_norm_global": max(float(row["impulse_proxy_max_norm"]) for row in diag_rows) if diag_rows else 0.0,
        "has_nan_count": sum(1 for row in diag_rows if bool(row["has_nan"])),
        "has_inf_count": sum(1 for row in diag_rows if bool(row["has_inf"])),
    }
    summary["envelope_pass"] = bool(len(diag_rows) == 2 and all(bool(row["envelope_pass"]) for row in diag_rows))
    return diag_rows, summary


def summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


def _ratio(left, right) -> float:
    denominator = float(right)
    if abs(denominator) <= 1.0e-15:
        return 1.0 if abs(float(left)) <= 1.0e-15 else math.inf
    return float(left) / denominator


def _row_max(row: dict, summary_field: str, step_field: str) -> float:
    if summary_field in row:
        return float(row[summary_field])
    return max(float(step[step_field]) for step in row["step_records"])


def _max_step_abs_delta(left, right, field) -> float:
    return max(abs(float(a[field]) - float(b[field])) for a, b in zip(left["step_records"], right["step_records"]))


def _finite_comparison(row: dict) -> bool:
    for key, value in row.items():
        if key.endswith("_abs") or key.endswith("_max_abs") or key.endswith("_delta") or key.endswith("_norm"):
            try:
                if not math.isfinite(float(value)):
                    return False
            except (TypeError, ValueError):
                continue
    return True
