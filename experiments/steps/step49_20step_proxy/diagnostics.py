import math


PREFIX_PHASES = [0.0, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35]
TRANSITION_PHASES = [0.35, 0.375, 0.4, 0.425, 0.45, 0.5]


def summarize_twenty_step_envelope_quality(rows: list[dict]) -> dict:
    by_name = {row["row_name"]: row for row in rows}
    row_count_pass = len(rows) == 4
    step_count_pass = all(len(row["step_records"]) == 20 for row in rows)
    stability_pass = all(bool(row["stable"]) for row in rows)
    projection_pass = all(float(row["projected_mass_min"]) > 0.0 and int(row["active_cell_count_min"]) > 0 for row in rows)
    wall_rows = [row for row in rows if bool(row["wall_velocity_application_enabled"])]
    wall_velocity_pass = all(
        int(row["applied_cell_count_max"]) > 0
        and 0.0 < float(row["max_applied_velocity_norm"]) <= float(row["wall_velocity_cap_lbm"]) + 1.0e-12
        for row in wall_rows
    )
    combined = by_name.get("runtime_geometry_plus_wall_velocity_32_20step", {})
    combined_row_pass = bool(
        combined
        and combined["runtime_geometry_projection_enabled"]
        and combined["wall_velocity_application_enabled"]
        and int(combined["applied_cell_count_max"]) > 0
        and int(combined["active_cell_count_delta_from_original_max"]) > 0
    )
    transition_rows, transition_summary = summarize_early_refill_transition(rows)
    diagnostic_only_pass = all(bool(row["diagnostic_only"]) for row in rows)
    no_persistent_state_pass = all(
        not bool(row["persist_projected_state"])
        and not bool(row["persist_displaced_geometry"])
        and not bool(row["persist_lbm_solid_vel"])
        for row in rows
    )
    return {
        "row_count": len(rows),
        "row_count_pass": bool(row_count_pass),
        "step_count_pass": bool(step_count_pass),
        "stability_pass": bool(stability_pass),
        "projection_pass": bool(projection_pass),
        "wall_velocity_pass": bool(wall_velocity_pass),
        "combined_row_pass": bool(combined_row_pass),
        "early_refill_pass": bool(transition_summary["transition_pass"] and all(bool(row["transition_pass"]) for row in transition_rows)),
        "diagnostic_only_pass": bool(diagnostic_only_pass),
        "no_persistent_state_pass": bool(no_persistent_state_pass),
        "quality_pass": bool(
            row_count_pass
            and step_count_pass
            and stability_pass
            and projection_pass
            and wall_velocity_pass
            and combined_row_pass
            and transition_summary["transition_pass"]
            and diagnostic_only_pass
            and no_persistent_state_pass
        ),
    }


def compare_twenty_step_components(rows: list[dict]) -> tuple[list[dict], dict]:
    by_name = {row["row_name"]: row for row in rows}
    pairs = [
        ("geometry_only_minus_original_static", "runtime_geometry_only_32_20step", "original_static_32_20step"),
        ("wall_velocity_only_minus_original_static", "wall_velocity_only_32_20step", "original_static_32_20step"),
        ("combined_minus_original_static", "runtime_geometry_plus_wall_velocity_32_20step", "original_static_32_20step"),
        ("combined_minus_geometry_only", "runtime_geometry_plus_wall_velocity_32_20step", "runtime_geometry_only_32_20step"),
        ("combined_minus_wall_velocity_only", "runtime_geometry_plus_wall_velocity_32_20step", "wall_velocity_only_32_20step"),
    ]
    comparison_rows = []
    for comparison, left_name, right_name in pairs:
        left = by_name[left_name]
        right = by_name[right_name]
        row = {
            "comparison": comparison,
            "left_row": left_name,
            "right_row": right_name,
            "projected_mass_delta_max_abs": _max_step_abs_delta(left, right, "projected_mass"),
            "active_cell_delta_max_abs": _max_step_abs_delta(left, right, "active_cell_count"),
            "applied_velocity_delta_max_abs": _max_step_abs_delta(left, right, "max_applied_velocity_norm"),
            "hydro_force_delta_max_abs": _max_step_abs_delta(left, right, "hydro_force_max_norm"),
            "bb_link_count_delta_max_abs": _max_step_abs_delta(left, right, "bb_link_count"),
        }
        row["comparison_pass"] = _finite_comparison(row) and float(row["projected_mass_delta_max_abs"]) <= 1.0e-9 and float(row["active_cell_delta_max_abs"]) <= 1024.0
        comparison_rows.append(row)
    summary = {
        "comparison_count": len(comparison_rows),
        "comparison_pass_count": sum(1 for row in comparison_rows if bool(row["comparison_pass"])),
        "comparison_pass": all(bool(row["comparison_pass"]) for row in comparison_rows),
        "geometry_effect_active_cell_delta_nonzero": by_name["runtime_geometry_only_32_20step"]["active_cell_count_delta_from_original_max"] > 0,
        "wall_velocity_effect_applied_velocity_nonzero": by_name["wall_velocity_only_32_20step"]["max_applied_velocity_norm"] > 0.0,
        "combined_has_geometry_and_wall_velocity": bool(
            by_name["runtime_geometry_plus_wall_velocity_32_20step"]["runtime_geometry_projection_enabled"]
            and by_name["runtime_geometry_plus_wall_velocity_32_20step"]["wall_velocity_application_enabled"]
            and by_name["runtime_geometry_plus_wall_velocity_32_20step"]["max_applied_velocity_norm"] > 0.0
            and by_name["runtime_geometry_plus_wall_velocity_32_20step"]["active_cell_count_delta_from_original_max"] > 0
        ),
    }
    summary["comparison_pass"] = bool(
        summary["comparison_pass"]
        and summary["geometry_effect_active_cell_delta_nonzero"]
        and summary["wall_velocity_effect_applied_velocity_nonzero"]
        and summary["combined_has_geometry_and_wall_velocity"]
    )
    return comparison_rows, summary


def summarize_twenty_step_phase_progression(rows: list[dict]) -> tuple[list[dict], dict]:
    progression_rows = []
    for row in rows:
        step_by_phase = {float(step["phase"]): step for step in row["step_records"]}
        phase0 = step_by_phase[0.0]
        phase035 = step_by_phase[0.35]
        phase05 = step_by_phase[0.5]
        active_delta = float(phase035["active_cell_count"]) - float(phase0["active_cell_count"])
        velocity_delta = float(phase05["max_applied_velocity_norm"]) - float(phase0["max_applied_velocity_norm"])
        progression = {
            "row_name": row["row_name"],
            "runtime_geometry_projection_enabled": bool(row["runtime_geometry_projection_enabled"]),
            "wall_velocity_application_enabled": bool(row["wall_velocity_application_enabled"]),
            "phase_sequence": row["phase_sequence"],
            "active_cell_count_phase0": int(phase0["active_cell_count"]),
            "active_cell_count_phase035": int(phase035["active_cell_count"]),
            "active_cell_count_delta_phase0_to_phase035": active_delta,
            "max_applied_velocity_phase0": float(phase0["max_applied_velocity_norm"]),
            "max_applied_velocity_phase05": float(phase05["max_applied_velocity_norm"]),
            "max_applied_velocity_delta_phase0_to_phase05": velocity_delta,
        }
        progression["progression_pass"] = bool(math.isfinite(active_delta) and math.isfinite(velocity_delta) and len(row["step_records"]) == 20)
        progression_rows.append(progression)
    by_name = {row["row_name"]: row for row in progression_rows}
    phase_sequence = progression_rows[0]["phase_sequence"] if progression_rows else []
    wall_velocity_delta = float(by_name["wall_velocity_only_32_20step"]["max_applied_velocity_delta_phase0_to_phase05"])
    combined_wall_velocity_delta = float(by_name["runtime_geometry_plus_wall_velocity_32_20step"]["max_applied_velocity_delta_phase0_to_phase05"])
    summary = {
        "phase_count": len(phase_sequence),
        "phase_sequence": phase_sequence,
        "phase_sequence_pass": phase_sequence == [0.0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.5],
        "runtime_geometry_phase_response_pass": abs(float(by_name["runtime_geometry_only_32_20step"]["active_cell_count_delta_phase0_to_phase035"])) > 0.0,
        "wall_velocity_phase_response_pass": bool(math.isfinite(wall_velocity_delta) and by_name["wall_velocity_only_32_20step"]["max_applied_velocity_phase05"] > 0.0),
        "combined_phase_response_pass": bool(
            abs(float(by_name["runtime_geometry_plus_wall_velocity_32_20step"]["active_cell_count_delta_phase0_to_phase035"])) > 0.0
            and math.isfinite(combined_wall_velocity_delta)
            and by_name["runtime_geometry_plus_wall_velocity_32_20step"]["max_applied_velocity_phase05"] > 0.0
        ),
        "phase0_to_phase035_projection_delta_nonzero": abs(float(by_name["runtime_geometry_only_32_20step"]["active_cell_count_delta_phase0_to_phase035"])) > 0.0,
        "phase0_to_phase05_wall_velocity_delta_finite": math.isfinite(wall_velocity_delta),
    }
    summary["phase_progression_pass"] = bool(
        summary["phase_sequence_pass"]
        and summary["runtime_geometry_phase_response_pass"]
        and summary["wall_velocity_phase_response_pass"]
        and summary["combined_phase_response_pass"]
        and summary["phase0_to_phase035_projection_delta_nonzero"]
        and summary["phase0_to_phase05_wall_velocity_delta_finite"]
        and all(bool(row["progression_pass"]) for row in progression_rows)
    )
    return progression_rows, summary


def summarize_early_refill_transition(rows: list[dict]) -> tuple[list[dict], dict]:
    transition_rows = []
    for row in rows:
        transition_steps = [step for step in row["step_records"] if 0.35 <= float(step["phase"]) <= 0.5]
        rho_min = min(float(step["rho_min"]) for step in transition_steps)
        rho_max = max(float(step["rho_max"]) for step in transition_steps)
        active_min = min(int(step["active_cell_count"]) for step in transition_steps)
        active_max = max(int(step["active_cell_count"]) for step in transition_steps)
        max_velocity = max(float(step["max_applied_velocity_norm"]) for step in transition_steps)
        cap = max(float(step["wall_velocity_cap_lbm"]) for step in transition_steps)
        applied_max = max(int(step["applied_cell_count"]) for step in transition_steps)
        row_payload = {
            "row_name": row["row_name"],
            "runtime_geometry_projection_enabled": bool(row["runtime_geometry_projection_enabled"]),
            "wall_velocity_application_enabled": bool(row["wall_velocity_application_enabled"]),
            "transition_phases": [float(step["phase"]) for step in transition_steps],
            "transition_phase_count": len(transition_steps),
            "rho_min_transition": rho_min,
            "rho_max_transition": rho_max,
            "active_cell_count_min_transition": active_min,
            "active_cell_count_max_transition": active_max,
            "active_cell_count_delta_transition": active_max - active_min,
            "applied_cell_count_max_transition": applied_max,
            "max_applied_velocity_norm_transition": max_velocity,
            "wall_velocity_cap_lbm": cap,
            "bb_link_count_min_transition": min(int(step["bb_link_count"]) for step in transition_steps),
            "has_nan": any(bool(step["has_nan"]) for step in transition_steps),
            "has_inf": any(bool(step["has_inf"]) for step in transition_steps),
        }
        row_payload["transition_pass"] = bool(
            len(transition_steps) >= 5
            and math.isfinite(rho_min)
            and math.isfinite(rho_max)
            and rho_min > 0.95
            and rho_max < 1.05
            and int(row_payload["bb_link_count_min_transition"]) > 0
            and int(row_payload["active_cell_count_delta_transition"]) <= 1024
            and (not row_payload["wall_velocity_application_enabled"] or applied_max > 0)
            and (not row_payload["wall_velocity_application_enabled"] or max_velocity <= cap + 1.0e-12)
            and not row_payload["has_nan"]
            and not row_payload["has_inf"]
        )
        transition_rows.append(row_payload)
    wall_rows = [row for row in transition_rows if bool(row["wall_velocity_application_enabled"])]
    summary = {
        "transition_phase_count": len(TRANSITION_PHASES),
        "transition_phases": list(TRANSITION_PHASES),
        "transition_pass_count": sum(1 for row in transition_rows if bool(row["transition_pass"])),
        "runtime_geometry_active_cell_count_bounded": all(int(row["active_cell_count_delta_transition"]) <= 1024 for row in transition_rows),
        "wall_velocity_applied_cell_count_positive": all(int(row["applied_cell_count_max_transition"]) > 0 for row in wall_rows),
        "wall_velocity_cap_pass": all(float(row["max_applied_velocity_norm_transition"]) <= float(row["wall_velocity_cap_lbm"]) + 1.0e-12 for row in wall_rows),
        "has_nan_count": sum(1 for row in transition_rows if bool(row["has_nan"])),
        "has_inf_count": sum(1 for row in transition_rows if bool(row["has_inf"])),
    }
    summary["transition_pass"] = bool(
        len(transition_rows) == 4
        and all(bool(row["transition_pass"]) for row in transition_rows)
        and summary["runtime_geometry_active_cell_count_bounded"]
        and summary["wall_velocity_applied_cell_count_positive"]
        and summary["wall_velocity_cap_pass"]
        and int(summary["has_nan_count"]) == 0
        and int(summary["has_inf_count"]) == 0
    )
    return transition_rows, summary


def mass_force_bounceback_twenty_step_envelope(rows: list[dict]) -> tuple[list[dict], dict]:
    diag_rows = []
    for row in rows:
        diag = {
            "row_name": row["row_name"],
            "runtime_geometry_projection_enabled": bool(row["runtime_geometry_projection_enabled"]),
            "wall_velocity_application_enabled": bool(row["wall_velocity_application_enabled"]),
            "rho_min_global": float(row["rho_min_global"]),
            "rho_max_global": float(row["rho_max_global"]),
            "lbm_max_v_global": float(row["lbm_max_v_global"]),
            "bb_link_count_min": int(row["bb_link_count_min"]),
            "bb_max_correction_global": float(row["bb_max_correction_global"]),
            "hydro_force_max_norm_global": float(row["hydro_force_max_norm_global"]),
            "max_applied_velocity_norm": float(row["max_applied_velocity_norm"]),
            "wall_velocity_cap_lbm": float(row["wall_velocity_cap_lbm"]),
            "has_nan": bool(row["has_nan"]),
            "has_inf": bool(row["has_inf"]),
        }
        diag["envelope_pass"] = bool(
            diag["rho_min_global"] > 0.95
            and diag["rho_max_global"] < 1.05
            and diag["bb_link_count_min"] > 0
            and math.isfinite(diag["bb_max_correction_global"])
            and math.isfinite(diag["hydro_force_max_norm_global"])
            and (not diag["wall_velocity_application_enabled"] or diag["max_applied_velocity_norm"] <= diag["wall_velocity_cap_lbm"] + 1.0e-12)
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
        "hydro_force_max_norm_global": max(float(row["hydro_force_max_norm_global"]) for row in diag_rows) if diag_rows else 0.0,
        "has_nan_count": sum(1 for row in diag_rows if bool(row["has_nan"])),
        "has_inf_count": sum(1 for row in diag_rows if bool(row["has_inf"])),
    }
    summary["envelope_pass"] = bool(len(diag_rows) == 4 and all(bool(row["envelope_pass"]) for row in diag_rows))
    return diag_rows, summary


def compare_step48_prefix(step48_rows: list[dict], step49_rows: list[dict]) -> tuple[list[dict], dict]:
    step48_by_name = {row["row_name"].replace("_10step", "_20step"): row for row in step48_rows}
    step49_by_name = {row["row_name"]: row for row in step49_rows}
    comparison_rows = []
    for row_name in sorted(step49_by_name):
        left = step49_by_name[row_name]
        right = step48_by_name[row_name]
        left_by_phase = {float(step["phase"]): step for step in left["step_records"]}
        right_by_phase = {float(step["phase"]): step for step in right["step_records"]}
        rows = []
        for phase in PREFIX_PHASES:
            rows.append(
                {
                    "phase": phase,
                    "projected_mass_delta_abs": abs(float(left_by_phase[phase]["projected_mass"]) - float(right_by_phase[phase]["projected_mass"])),
                    "active_cell_count_delta_abs": abs(float(left_by_phase[phase]["active_cell_count"]) - float(right_by_phase[phase]["active_cell_count"])),
                    "applied_velocity_delta_abs": abs(float(left_by_phase[phase]["max_applied_velocity_norm"]) - float(right_by_phase[phase]["max_applied_velocity_norm"])),
                }
            )
        comparison = {
            "row_pair": f"{row_name}_vs_step48_prefix",
            "step49_row": row_name,
            "step48_row": right["row_name"],
            "matched_phases": list(PREFIX_PHASES),
            "projected_mass_delta_max_abs": max(float(row["projected_mass_delta_abs"]) for row in rows),
            "active_cell_count_delta_max_abs": max(float(row["active_cell_count_delta_abs"]) for row in rows),
            "applied_velocity_delta_max_abs": max(float(row["applied_velocity_delta_abs"]) for row in rows),
        }
        comparison["comparison_pass"] = bool(
            math.isfinite(comparison["projected_mass_delta_max_abs"])
            and math.isfinite(comparison["active_cell_count_delta_max_abs"])
            and math.isfinite(comparison["applied_velocity_delta_max_abs"])
            and comparison["projected_mass_delta_max_abs"] <= 1.0e-9
            and comparison["active_cell_count_delta_max_abs"] <= 0.0
            and comparison["applied_velocity_delta_max_abs"] <= 1.0e-12
        )
        comparison_rows.append(comparison)
    summary = {
        "matched_phase_count": len(PREFIX_PHASES),
        "matched_phases": list(PREFIX_PHASES),
        "row_pair_count": len(comparison_rows),
        "comparison_pass_count": sum(1 for row in comparison_rows if bool(row["comparison_pass"])),
    }
    summary["comparison_pass"] = bool(summary["row_pair_count"] == 4 and summary["comparison_pass_count"] == summary["row_pair_count"])
    return comparison_rows, summary


def summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


def _max_step_abs_delta(left, right, field) -> float:
    return max(abs(float(a[field]) - float(b[field])) for a, b in zip(left["step_records"], right["step_records"]))


def _finite_comparison(row: dict) -> bool:
    return all(
        math.isfinite(float(row[field]))
        for field in (
            "projected_mass_delta_max_abs",
            "active_cell_delta_max_abs",
            "applied_velocity_delta_max_abs",
            "hydro_force_delta_max_abs",
            "bb_link_count_delta_max_abs",
        )
    )
