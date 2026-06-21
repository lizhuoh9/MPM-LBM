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
COMPONENT_NAMES = [
    "original_static",
    "runtime_geometry_only",
    "wall_velocity_only",
    "runtime_geometry_plus_wall_velocity",
]


def summarize_transfer_comparison(rows: list[dict]) -> dict:
    engineering = [row for row in rows if row["transfer_mode"] == "engineering"]
    link_area = [row for row in rows if row["transfer_mode"] == "link_area_experimental"]
    return {
        "row_count": len(rows),
        "engineering_row_count": len(engineering),
        "link_area_row_count": len(link_area),
        "stable_count": sum(1 for row in rows if bool(row["stable"])),
        "step_count_per_row": min((len(row["step_records"]) for row in rows), default=0),
        "completed_lbm_steps_min": min((int(row["completed_lbm_steps"]) for row in rows), default=0),
        "total_mpm_substeps_min": min((int(row["total_mpm_substeps"]) for row in rows), default=0),
        "rho_min_global": min((float(row["rho_min_global"]) for row in rows), default=0.0),
        "rho_max_global": max((float(row["rho_max_global"]) for row in rows), default=0.0),
        "lbm_max_v_global": max((float(row["lbm_max_v_global"]) for row in rows), default=0.0),
        "projected_mass_min": min((float(row["projected_mass_min"]) for row in rows), default=0.0),
        "active_cell_count_min": min((int(row["active_cell_count_min"]) for row in rows), default=0),
        "bb_link_count_min": min((int(row["bb_link_count_min"]) for row in rows), default=0),
        "area_scale_min_observed": min((float(row["area_scale_min_observed"]) for row in rows), default=0.0),
        "area_scale_max_observed": max((float(row["area_scale_max_observed"]) for row in rows), default=0.0),
        "has_nan_count": sum(1 for row in rows if bool(row["has_nan"])),
        "has_inf_count": sum(1 for row in rows if bool(row["has_inf"])),
        "comparison_matrix_pass": bool(
            len(rows) == 8
            and len(engineering) == 4
            and len(link_area) == 4
            and all(bool(row["stable"]) for row in rows)
            and all(len(row["step_records"]) == 40 for row in rows)
        ),
    }


def summarize_transfer_envelope_quality(rows: list[dict], closure_rows: list[dict] | None = None) -> dict:
    by_transfer = _by_transfer_component(rows)
    row_count_pass = len(rows) == 8
    step_count_pass = all(len(row["step_records"]) == 40 for row in rows)
    stability_pass = all(bool(row["stable"]) for row in rows)
    projection_pass = all(float(row["projected_mass_min"]) > 0.0 and int(row["active_cell_count_min"]) > 0 for row in rows)
    wall_rows = [row for row in rows if bool(row["wall_velocity_application_enabled"])]
    wall_velocity_pass = all(
        int(row["applied_cell_count_max"]) > 0
        and 0.0 < float(row["max_applied_velocity_norm"]) <= float(row["wall_velocity_cap_lbm"]) + 1.0e-12
        for row in wall_rows
    )
    transfer_mode_pass = set(by_transfer) == {"engineering", "link_area_experimental"} and all(set(components) == set(COMPONENT_NAMES) for components in by_transfer.values())
    link_area_pass = summarize_link_area_envelope(rows)[1]["link_area_envelope_pass"]
    component_rows, component_summary = summarize_transfer_component_effects(rows)
    closure_summary = summarize_transfer_cycle_closure(rows, closure_rows or [])[1] if closure_rows is not None else {"closure_pass": True}
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
        "transfer_mode_pass": bool(transfer_mode_pass),
        "link_area_pass": bool(link_area_pass),
        "component_effect_pass": bool(component_summary["comparison_pass"] and all(bool(row["comparison_pass"]) for row in component_rows)),
        "closure_pass": bool(closure_summary["closure_pass"]),
        "diagnostic_only_pass": bool(diagnostic_only_pass),
        "no_persistent_state_pass": bool(no_persistent_state_pass),
        "quality_pass": bool(
            row_count_pass
            and step_count_pass
            and stability_pass
            and projection_pass
            and wall_velocity_pass
            and transfer_mode_pass
            and link_area_pass
            and component_summary["comparison_pass"]
            and diagnostic_only_pass
            and no_persistent_state_pass
        ),
    }


def compare_engineering_link_area(rows) -> list[dict]:
    by_key = {(row["transfer_mode"], row["component_name"]): row for row in rows}
    comparison_rows = []
    for component in COMPONENT_NAMES:
        engineering = by_key[("engineering", component)]
        link_area = by_key[("link_area_experimental", component)]
        row = {
            "comparison": f"engineering_vs_link_area_{component}",
            "component_name": component,
            "engineering_row": engineering["row_name"],
            "link_area_row": link_area["row_name"],
            "both_transfer_modes_stable": bool(engineering["stable"] and link_area["stable"]),
            "rho_min_delta_abs": abs(float(engineering["rho_min_global"]) - float(link_area["rho_min_global"])),
            "rho_max_delta_abs": abs(float(engineering["rho_max_global"]) - float(link_area["rho_max_global"])),
            "lbm_max_v_delta_abs": abs(float(engineering["lbm_max_v_global"]) - float(link_area["lbm_max_v_global"])),
            "projected_mass_delta_max_abs": _max_step_abs_delta(engineering, link_area, "projected_mass"),
            "active_cell_count_delta_max_abs": _max_step_abs_delta(engineering, link_area, "active_cell_count"),
            "bb_link_count_delta_max_abs": _max_step_abs_delta(engineering, link_area, "bb_link_count"),
            "hydro_force_delta_max_abs": _max_step_abs_delta(engineering, link_area, "hydro_force_max_norm"),
            "impulse_proxy_delta_abs": abs(float(engineering["impulse_proxy_max_norm"]) - float(link_area["impulse_proxy_max_norm"])),
            "area_scale_delta_abs": abs(float(engineering["area_scale_final"]) - float(link_area["area_scale_final"])),
            "link_area_scale_final": float(link_area["area_scale_final"]),
        }
        row["comparison_pass"] = bool(
            row["both_transfer_modes_stable"]
            and _finite_comparison(row)
            and float(row["rho_min_delta_abs"]) <= 0.05
            and float(row["rho_max_delta_abs"]) <= 0.05
            and float(row["lbm_max_v_delta_abs"]) <= 0.1
            and float(row["projected_mass_delta_max_abs"]) <= 1.0e-8
            and float(row["active_cell_count_delta_max_abs"]) <= 0.0
            and float(row["bb_link_count_delta_max_abs"]) <= 0.0
            and float(row["hydro_force_delta_max_abs"]) <= 0.1
            and float(row["impulse_proxy_delta_abs"]) <= 4.0
            and 0.25 <= float(row["link_area_scale_final"]) <= 2.0
        )
        comparison_rows.append(row)
    return comparison_rows


def summarize_engineering_link_area_comparison(rows: list[dict]) -> tuple[list[dict], dict]:
    comparison_rows = compare_engineering_link_area(rows)
    summary = {
        "comparison_count": len(comparison_rows),
        "comparison_pass_count": sum(1 for row in comparison_rows if bool(row["comparison_pass"])),
        "both_transfer_modes_stable": all(bool(row["both_transfer_modes_stable"]) for row in comparison_rows),
        "projected_mass_delta_max_abs": max((float(row["projected_mass_delta_max_abs"]) for row in comparison_rows), default=0.0),
        "active_cell_count_delta_max_abs": max((float(row["active_cell_count_delta_max_abs"]) for row in comparison_rows), default=0.0),
        "bb_link_count_delta_max_abs": max((float(row["bb_link_count_delta_max_abs"]) for row in comparison_rows), default=0.0),
        "hydro_force_delta_max_abs": max((float(row["hydro_force_delta_max_abs"]) for row in comparison_rows), default=0.0),
        "impulse_proxy_delta_max_abs": max((float(row["impulse_proxy_delta_abs"]) for row in comparison_rows), default=0.0),
    }
    summary["comparison_pass"] = bool(summary["comparison_count"] == 4 and summary["comparison_pass_count"] == 4 and summary["both_transfer_modes_stable"])
    return comparison_rows, summary


def summarize_link_area_envelope(rows: list[dict]) -> tuple[list[dict], dict]:
    link_rows = [row for row in rows if row["transfer_mode"] == "link_area_experimental"]
    envelope_rows = []
    for row in link_rows:
        envelope = {
            "row_name": row["row_name"],
            "component_name": row["component_name"],
            "area_scale_min_observed": float(row["area_scale_min_observed"]),
            "area_scale_max_observed": float(row["area_scale_max_observed"]),
            "area_scale_final": float(row["area_scale_final"]),
            "raw_area_scale_final": float(row["raw_area_scale_final"]),
            "stable": bool(row["stable"]),
        }
        envelope["area_scale_finite_pass"] = all(math.isfinite(float(envelope[field])) for field in ("area_scale_min_observed", "area_scale_max_observed", "area_scale_final", "raw_area_scale_final"))
        envelope["area_scale_bounds_pass"] = bool(0.25 <= envelope["area_scale_min_observed"] <= 2.0 and 0.25 <= envelope["area_scale_max_observed"] <= 2.0 and 0.25 <= envelope["area_scale_final"] <= 2.0)
        envelope["link_area_row_pass"] = bool(envelope["stable"] and envelope["area_scale_finite_pass"] and envelope["area_scale_bounds_pass"])
        envelope_rows.append(envelope)
    summary = {
        "link_area_row_count": len(envelope_rows),
        "area_scale_finite_pass": all(bool(row["area_scale_finite_pass"]) for row in envelope_rows),
        "area_scale_min_observed": min((float(row["area_scale_min_observed"]) for row in envelope_rows), default=0.0),
        "area_scale_max_observed": max((float(row["area_scale_max_observed"]) for row in envelope_rows), default=0.0),
        "area_scale_final_min": min((float(row["area_scale_final"]) for row in envelope_rows), default=0.0),
        "area_scale_final_max": max((float(row["area_scale_final"]) for row in envelope_rows), default=0.0),
        "link_area_pass_count": sum(1 for row in envelope_rows if bool(row["link_area_row_pass"])),
    }
    summary["link_area_envelope_pass"] = bool(
        summary["link_area_row_count"] == 4
        and summary["area_scale_finite_pass"]
        and 0.25 <= float(summary["area_scale_min_observed"]) <= 2.0
        and 0.25 <= float(summary["area_scale_max_observed"]) <= 2.0
        and int(summary["link_area_pass_count"]) == 4
    )
    return envelope_rows, summary


def summarize_transfer_component_effects(rows: list[dict]) -> tuple[list[dict], dict]:
    by_key = {(row["transfer_mode"], row["component_name"]): row for row in rows}
    pairs = [
        ("geometry_only_minus_original_static", "runtime_geometry_only", "original_static"),
        ("wall_velocity_only_minus_original_static", "wall_velocity_only", "original_static"),
        ("combined_minus_original_static", "runtime_geometry_plus_wall_velocity", "original_static"),
        ("combined_minus_geometry_only", "runtime_geometry_plus_wall_velocity", "runtime_geometry_only"),
        ("combined_minus_wall_velocity_only", "runtime_geometry_plus_wall_velocity", "wall_velocity_only"),
    ]
    comparison_rows = []
    for transfer_mode in ("engineering", "link_area_experimental"):
        for comparison, left_component, right_component in pairs:
            left = by_key[(transfer_mode, left_component)]
            right = by_key[(transfer_mode, right_component)]
            row = {
                "comparison": f"{transfer_mode}_{comparison}",
                "transfer_mode": transfer_mode,
                "left_row": left["row_name"],
                "right_row": right["row_name"],
                "projected_mass_delta_max_abs": _max_step_abs_delta(left, right, "projected_mass"),
                "active_cell_delta_max_abs": _max_step_abs_delta(left, right, "active_cell_count"),
                "applied_velocity_delta_max_abs": _max_step_abs_delta(left, right, "max_applied_velocity_norm"),
                "hydro_force_delta_max_abs": _max_step_abs_delta(left, right, "hydro_force_max_norm"),
                "bb_link_count_delta_max_abs": _max_step_abs_delta(left, right, "bb_link_count"),
                "area_scale_delta_max_abs": _max_step_abs_delta(left, right, "area_scale"),
            }
            row["comparison_pass"] = _finite_comparison(row) and float(row["projected_mass_delta_max_abs"]) <= 1.0e-8 and float(row["active_cell_delta_max_abs"]) <= 1024.0
            comparison_rows.append(row)
    summary = {
        "transfer_mode_count": len({row["transfer_mode"] for row in comparison_rows}),
        "comparison_count": len(comparison_rows),
        "comparison_pass_count": sum(1 for row in comparison_rows if bool(row["comparison_pass"])),
    }
    for transfer_mode in ("engineering", "link_area_experimental"):
        summary[f"{transfer_mode}_geometry_effect_active_cell_delta_nonzero"] = by_key[(transfer_mode, "runtime_geometry_only")]["active_cell_count_delta_from_original_max"] > 0
        summary[f"{transfer_mode}_wall_velocity_effect_applied_velocity_nonzero"] = by_key[(transfer_mode, "wall_velocity_only")]["max_applied_velocity_norm"] > 0.0
        combined = by_key[(transfer_mode, "runtime_geometry_plus_wall_velocity")]
        summary[f"{transfer_mode}_combined_has_geometry_and_wall_velocity"] = bool(
            combined["runtime_geometry_projection_enabled"]
            and combined["wall_velocity_application_enabled"]
            and combined["max_applied_velocity_norm"] > 0.0
            and combined["active_cell_count_delta_from_original_max"] > 0
        )
    summary["geometry_effect_active_cell_delta_nonzero"] = bool(summary["engineering_geometry_effect_active_cell_delta_nonzero"] and summary["link_area_experimental_geometry_effect_active_cell_delta_nonzero"])
    summary["wall_velocity_effect_applied_velocity_nonzero"] = bool(summary["engineering_wall_velocity_effect_applied_velocity_nonzero"] and summary["link_area_experimental_wall_velocity_effect_applied_velocity_nonzero"])
    summary["combined_has_geometry_and_wall_velocity"] = bool(summary["engineering_combined_has_geometry_and_wall_velocity"] and summary["link_area_experimental_combined_has_geometry_and_wall_velocity"])
    summary["comparison_pass"] = bool(
        summary["transfer_mode_count"] == 2
        and summary["comparison_count"] >= 10
        and summary["comparison_pass_count"] == summary["comparison_count"]
        and summary["geometry_effect_active_cell_delta_nonzero"]
        and summary["wall_velocity_effect_applied_velocity_nonzero"]
        and summary["combined_has_geometry_and_wall_velocity"]
    )
    return comparison_rows, summary


def summarize_transfer_cycle_closure(rows: list[dict], closure_rows: list[dict]) -> tuple[list[dict], dict]:
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
        row["area_scale_closure_pass"] = bool(math.isfinite(float(row["phase0_phase1_area_scale_delta"])) and 0.25 <= float(row["phase0_area_scale"]) <= 2.0 and 0.25 <= float(row["closure_area_scale"]) <= 2.0)
        row["closure_pass"] = bool(row["closure_pass"] and row["cycle_proxy_closure_pass"] and row["area_scale_closure_pass"])
    summary = {
        "row_count": len(closure_rows),
        "transfer_mode_count": len({row["transfer_mode"] for row in closure_rows}),
        "closure_phase": 1.0,
        "closure_pass_count": sum(1 for row in closure_rows if bool(row["closure_pass"])),
        "engineering_closure_pass": all(bool(row["closure_pass"]) for row in closure_rows if row["transfer_mode"] == "engineering"),
        "link_area_closure_pass": all(bool(row["closure_pass"]) for row in closure_rows if row["transfer_mode"] == "link_area_experimental"),
        "geometry_projection_closure_pass": all(bool(row["geometry_projection_closure_pass"]) for row in closure_rows) if closure_rows else False,
        "wall_velocity_closure_pass": all(bool(row["wall_velocity_closure_pass"]) for row in closure_rows) if closure_rows else False,
        "cycle_proxy_closure_pass": all(bool(row["cycle_proxy_closure_pass"]) for row in closure_rows) if closure_rows else False,
        "area_scale_closure_pass": all(bool(row["area_scale_closure_pass"]) for row in closure_rows) if closure_rows else False,
        "phase0_phase1_projected_mass_delta_max": max((float(row["phase0_phase1_projected_mass_delta"]) for row in closure_rows), default=0.0),
        "phase0_phase1_active_cell_delta_max": max((int(row["phase0_phase1_active_cell_delta"]) for row in closure_rows), default=0),
        "phase0_phase1_applied_velocity_delta_max": max((float(row["phase0_phase1_applied_velocity_delta"]) for row in closure_rows), default=0.0),
        "phase0_phase1_area_scale_delta_max": max((float(row["phase0_phase1_area_scale_delta"]) for row in closure_rows), default=0.0),
        "wall_velocity_closure_tolerance": WALL_VELOCITY_CLOSURE_TOLERANCE,
    }
    summary["closure_pass"] = bool(
        len(closure_rows) == 8
        and int(summary["transfer_mode_count"]) == 2
        and int(summary["closure_pass_count"]) == 8
        and summary["engineering_closure_pass"]
        and summary["link_area_closure_pass"]
        and summary["geometry_projection_closure_pass"]
        and summary["wall_velocity_closure_pass"]
        and summary["cycle_proxy_closure_pass"]
        and summary["area_scale_closure_pass"]
    )
    return closure_rows, summary


def compare_step50_engineering_prefix(rows_step50: list[dict], rows_step51: list[dict]) -> tuple[list[dict], dict]:
    step50_by_component = {_step50_component(row["row_name"]): row for row in rows_step50}
    step51_engineering = {row["component_name"]: row for row in rows_step51 if row["transfer_mode"] == "engineering"}
    comparison_rows = []
    for component in COMPONENT_NAMES:
        left = step51_engineering[component]
        right = step50_by_component[component]
        left_by_phase = {float(step["phase"]): step for step in left["step_records"]}
        right_by_phase = {float(step["phase"]): step for step in right["step_records"]}
        per_phase_rows = []
        for phase in PHASE_SEQUENCE:
            per_phase_rows.append(
                {
                    "phase": phase,
                    "projected_mass_delta_abs": abs(float(left_by_phase[phase]["projected_mass"]) - float(right_by_phase[phase]["projected_mass"])),
                    "active_cell_count_delta_abs": abs(float(left_by_phase[phase]["active_cell_count"]) - float(right_by_phase[phase]["active_cell_count"])),
                    "applied_velocity_delta_abs": abs(float(left_by_phase[phase]["max_applied_velocity_norm"]) - float(right_by_phase[phase]["max_applied_velocity_norm"])),
                    "rho_min_delta_abs": abs(float(left_by_phase[phase]["rho_min"]) - float(right_by_phase[phase]["rho_min"])),
                    "rho_max_delta_abs": abs(float(left_by_phase[phase]["rho_max"]) - float(right_by_phase[phase]["rho_max"])),
                }
            )
        comparison = {
            "row_pair": f"step51_engineering_{component}_vs_step50",
            "step51_row": left["row_name"],
            "step50_row": right["row_name"],
            "matched_phase_count": len(PHASE_SEQUENCE),
            "matched_phases": list(PHASE_SEQUENCE),
            "projected_mass_delta_max_abs": max(float(row["projected_mass_delta_abs"]) for row in per_phase_rows),
            "active_cell_count_delta_max_abs": max(float(row["active_cell_count_delta_abs"]) for row in per_phase_rows),
            "applied_velocity_delta_max_abs": max(float(row["applied_velocity_delta_abs"]) for row in per_phase_rows),
            "rho_min_delta_max_abs": max(float(row["rho_min_delta_abs"]) for row in per_phase_rows),
            "rho_max_delta_max_abs": max(float(row["rho_max_delta_abs"]) for row in per_phase_rows),
        }
        comparison["comparison_pass"] = bool(
            math.isfinite(comparison["projected_mass_delta_max_abs"])
            and math.isfinite(comparison["active_cell_count_delta_max_abs"])
            and math.isfinite(comparison["applied_velocity_delta_max_abs"])
            and math.isfinite(comparison["rho_min_delta_max_abs"])
            and math.isfinite(comparison["rho_max_delta_max_abs"])
            and comparison["projected_mass_delta_max_abs"] <= 1.0e-8
            and comparison["active_cell_count_delta_max_abs"] <= 0.0
            and comparison["applied_velocity_delta_max_abs"] <= 1.0e-8
            and comparison["rho_min_delta_max_abs"] <= 1.0e-12
            and comparison["rho_max_delta_max_abs"] <= 1.0e-12
        )
        comparison_rows.append(comparison)
    summary = {
        "engineering_row_pair_count": len(comparison_rows),
        "matched_phase_count": len(PHASE_SEQUENCE),
        "matched_phases": list(PHASE_SEQUENCE),
        "comparison_pass_count": sum(1 for row in comparison_rows if bool(row["comparison_pass"])),
        "max_projected_mass_delta": max((float(row["projected_mass_delta_max_abs"]) for row in comparison_rows), default=0.0),
        "max_active_cell_count_delta": max((float(row["active_cell_count_delta_max_abs"]) for row in comparison_rows), default=0.0),
        "max_applied_velocity_delta": max((float(row["applied_velocity_delta_max_abs"]) for row in comparison_rows), default=0.0),
    }
    summary["comparison_pass"] = bool(summary["engineering_row_pair_count"] == 4 and summary["comparison_pass_count"] == 4)
    return comparison_rows, summary


def mass_force_bounceback_transfer_envelope(rows: list[dict]) -> tuple[list[dict], dict]:
    diag_rows = []
    for row in rows:
        diag = {
            "row_name": row["row_name"],
            "transfer_mode": row["transfer_mode"],
            "component_name": row["component_name"],
            "runtime_geometry_projection_enabled": bool(row["runtime_geometry_projection_enabled"]),
            "wall_velocity_application_enabled": bool(row["wall_velocity_application_enabled"]),
            "rho_min_global": float(row["rho_min_global"]),
            "rho_max_global": float(row["rho_max_global"]),
            "lbm_max_v_global": float(row["lbm_max_v_global"]),
            "bb_link_count_min": int(row["bb_link_count_min"]),
            "bb_max_correction_global": float(row["bb_max_correction_global"]),
            "hydro_force_max_norm_global": float(row["hydro_force_max_norm_global"]),
            "impulse_proxy_max_norm": float(row["impulse_proxy_max_norm"]),
            "max_applied_velocity_norm": float(row["max_applied_velocity_norm"]),
            "wall_velocity_cap_lbm": float(row["wall_velocity_cap_lbm"]),
            "area_scale_final": float(row["area_scale_final"]),
            "has_nan": bool(row["has_nan"]),
            "has_inf": bool(row["has_inf"]),
        }
        diag["envelope_pass"] = bool(
            diag["rho_min_global"] > 0.95
            and diag["rho_max_global"] < 1.05
            and diag["bb_link_count_min"] > 0
            and math.isfinite(diag["bb_max_correction_global"])
            and math.isfinite(diag["hydro_force_max_norm_global"])
            and math.isfinite(diag["impulse_proxy_max_norm"])
            and 0.25 <= diag["area_scale_final"] <= 2.0
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
        "impulse_proxy_max_norm_global": max(float(row["impulse_proxy_max_norm"]) for row in diag_rows) if diag_rows else 0.0,
        "has_nan_count": sum(1 for row in diag_rows if bool(row["has_nan"])),
        "has_inf_count": sum(1 for row in diag_rows if bool(row["has_inf"])),
    }
    summary["envelope_pass"] = bool(len(diag_rows) == 8 and all(bool(row["envelope_pass"]) for row in diag_rows))
    return diag_rows, summary


def summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


def _by_transfer_component(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["transfer_mode"], {})[row["component_name"]] = row
    return grouped


def _step50_component(row_name: str) -> str:
    if row_name == "original_static_32_40step":
        return "original_static"
    if row_name == "runtime_geometry_only_32_40step":
        return "runtime_geometry_only"
    if row_name == "wall_velocity_only_32_40step":
        return "wall_velocity_only"
    if row_name == "runtime_geometry_plus_wall_velocity_32_40step":
        return "runtime_geometry_plus_wall_velocity"
    raise KeyError(row_name)


def _max_step_abs_delta(left, right, field) -> float:
    return max(abs(float(a[field]) - float(b[field])) for a, b in zip(left["step_records"], right["step_records"]))


def _finite_comparison(row: dict) -> bool:
    for key, value in row.items():
        if key.endswith("_abs") or key.endswith("_max_abs") or key.endswith("_delta_abs") or key.endswith("_delta_max_abs"):
            if not math.isfinite(float(value)):
                return False
    return True
