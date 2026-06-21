import math


def summarize_coupling_smoke_quality(rows: list[dict]) -> dict:
    by_name = {row["row_name"]: row for row in rows}
    row_count_pass = len(rows) == 4
    stability_pass = all(bool(row["stable"]) for row in rows)
    projection_pass = all(float(row["projected_mass"]) > 0.0 and int(row["active_cell_count"]) > 0 for row in rows)
    wall_velocity_rows = [row for row in rows if bool(row["wall_velocity_application_enabled"])]
    wall_velocity_pass = all(
        int(row["applied_cell_count"]) > 0
        and 0.0 < float(row["max_applied_velocity_norm"]) <= float(row["wall_velocity_cap_lbm"]) + 1.0e-12
        for row in wall_velocity_rows
    )
    combined = by_name.get("runtime_geometry_plus_wall_velocity_32_phase035_1step", {})
    combined_row_pass = bool(
        combined
        and combined["runtime_geometry_projection_enabled"]
        and combined["wall_velocity_application_enabled"]
        and int(combined["applied_cell_count"]) > 0
        and int(combined["projection_delta_active_cell_count"]) > 0
    )
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
        "stability_pass": bool(stability_pass),
        "projection_pass": bool(projection_pass),
        "wall_velocity_pass": bool(wall_velocity_pass),
        "combined_row_pass": bool(combined_row_pass),
        "diagnostic_only_pass": bool(diagnostic_only_pass),
        "no_persistent_state_pass": bool(no_persistent_state_pass),
        "quality_pass": bool(
            row_count_pass
            and stability_pass
            and projection_pass
            and wall_velocity_pass
            and combined_row_pass
            and diagnostic_only_pass
            and no_persistent_state_pass
        ),
    }


def compare_smoke_rows(rows: list[dict]) -> tuple[list[dict], dict]:
    by_name = {row["row_name"]: row for row in rows}
    pairs = [
        ("geometry_only_minus_original_static", "runtime_geometry_only_32_phase035_1step", "original_static_32_1step"),
        ("wall_velocity_only_minus_original_static", "wall_velocity_only_32_phase035_1step", "original_static_32_1step"),
        ("combined_minus_original_static", "runtime_geometry_plus_wall_velocity_32_phase035_1step", "original_static_32_1step"),
        ("combined_minus_geometry_only", "runtime_geometry_plus_wall_velocity_32_phase035_1step", "runtime_geometry_only_32_phase035_1step"),
        ("combined_minus_wall_velocity_only", "runtime_geometry_plus_wall_velocity_32_phase035_1step", "wall_velocity_only_32_phase035_1step"),
    ]
    comparison_rows = []
    for comparison, left_name, right_name in pairs:
        left = by_name[left_name]
        right = by_name[right_name]
        row = {
            "comparison": comparison,
            "left_row": left_name,
            "right_row": right_name,
            "projected_mass_delta": float(left["projected_mass"]) - float(right["projected_mass"]),
            "active_cell_delta": float(left["active_cell_count"]) - float(right["active_cell_count"]),
            "applied_velocity_delta": float(left["max_applied_velocity_norm"]) - float(right["max_applied_velocity_norm"]),
            "hydro_force_delta": float(left["hydro_force_max_norm"]) - float(right["hydro_force_max_norm"]),
            "bb_link_count_delta": float(left["bb_link_count"]) - float(right["bb_link_count"]),
        }
        row["comparison_pass"] = _finite_comparison(row) and abs(float(row["projected_mass_delta"])) <= 1.0e-9 and abs(float(row["active_cell_delta"])) <= 1024.0
        comparison_rows.append(row)
    summary = {
        "comparison_count": len(comparison_rows),
        "comparison_pass_count": sum(1 for row in comparison_rows if bool(row["comparison_pass"])),
        "comparison_pass": all(bool(row["comparison_pass"]) for row in comparison_rows),
        "geometry_only_projection_delta_nonzero": by_name["runtime_geometry_only_32_phase035_1step"]["projection_delta_active_cell_count"] > 0,
        "wall_velocity_only_applied_velocity_nonzero": by_name["wall_velocity_only_32_phase035_1step"]["max_applied_velocity_norm"] > 0.0,
        "combined_has_geometry_and_wall_velocity": bool(
            by_name["runtime_geometry_plus_wall_velocity_32_phase035_1step"]["runtime_geometry_projection_enabled"]
            and by_name["runtime_geometry_plus_wall_velocity_32_phase035_1step"]["wall_velocity_application_enabled"]
            and by_name["runtime_geometry_plus_wall_velocity_32_phase035_1step"]["max_applied_velocity_norm"] > 0.0
            and by_name["runtime_geometry_plus_wall_velocity_32_phase035_1step"]["projection_delta_active_cell_count"] > 0
        ),
    }
    summary["comparison_pass"] = bool(
        summary["comparison_pass"]
        and summary["geometry_only_projection_delta_nonzero"]
        and summary["wall_velocity_only_applied_velocity_nonzero"]
        and summary["combined_has_geometry_and_wall_velocity"]
    )
    return comparison_rows, summary


def mass_force_bounceback_diagnostics(rows: list[dict]) -> tuple[list[dict], dict]:
    diag_rows = []
    for row in rows:
        diag = {
            "row_name": row["row_name"],
            "runtime_geometry_projection_enabled": bool(row["runtime_geometry_projection_enabled"]),
            "wall_velocity_application_enabled": bool(row["wall_velocity_application_enabled"]),
            "rho_min": float(row["rho_min"]),
            "rho_max": float(row["rho_max"]),
            "lbm_max_v": float(row["lbm_max_v"]),
            "bb_link_count": int(row["bb_link_count"]),
            "bb_max_correction": float(row["bb_max_correction"]),
            "hydro_force_max_norm": float(row["hydro_force_max_norm"]),
            "max_applied_velocity_norm": float(row["max_applied_velocity_norm"]),
            "wall_velocity_cap_lbm": float(row["wall_velocity_cap_lbm"]),
            "has_nan": bool(row["has_nan"]),
            "has_inf": bool(row["has_inf"]),
        }
        diag["diagnostics_pass"] = bool(
            diag["rho_min"] > 0.95
            and diag["rho_max"] < 1.05
            and diag["bb_link_count"] > 0
            and math.isfinite(diag["bb_max_correction"])
            and math.isfinite(diag["hydro_force_max_norm"])
            and (not diag["wall_velocity_application_enabled"] or diag["max_applied_velocity_norm"] <= diag["wall_velocity_cap_lbm"] + 1.0e-12)
            and not diag["has_nan"]
            and not diag["has_inf"]
        )
        diag_rows.append(diag)
    summary = {
        "row_count": len(diag_rows),
        "diagnostics_pass_count": sum(1 for row in diag_rows if bool(row["diagnostics_pass"])),
        "rho_min_global": min(float(row["rho_min"]) for row in diag_rows) if diag_rows else 0.0,
        "rho_max_global": max(float(row["rho_max"]) for row in diag_rows) if diag_rows else 0.0,
        "bb_max_correction_global": max(float(row["bb_max_correction"]) for row in diag_rows) if diag_rows else 0.0,
        "bb_link_count_min": min(int(row["bb_link_count"]) for row in diag_rows) if diag_rows else 0,
        "hydro_force_max_norm_global": max(float(row["hydro_force_max_norm"]) for row in diag_rows) if diag_rows else 0.0,
        "has_nan_count": sum(1 for row in diag_rows if bool(row["has_nan"])),
        "has_inf_count": sum(1 for row in diag_rows if bool(row["has_inf"])),
    }
    summary["diagnostics_pass"] = bool(len(diag_rows) == 4 and all(bool(row["diagnostics_pass"]) for row in diag_rows))
    return diag_rows, summary


def summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


def _finite_comparison(row: dict) -> bool:
    return all(
        math.isfinite(float(row[field]))
        for field in (
            "projected_mass_delta",
            "active_cell_delta",
            "applied_velocity_delta",
            "hydro_force_delta",
            "bb_link_count_delta",
        )
    )
