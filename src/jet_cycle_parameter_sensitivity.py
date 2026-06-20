import csv
import json
import math
import os
from pathlib import Path

from .jet_cycle_proxy_diagnostics import compute_impulse_norm_proxy


SCALE_TOL = 1.0e-12


def scale_label(scale: float) -> str:
    return f"{int(round(float(scale) * 1000.0)):04d}"


def parse_wall_velocity_scale_from_case(value) -> float:
    text = str(value)
    marker = "scale_"
    if marker not in text:
        return 0.0
    suffix = text.split(marker, 1)[1].split(".", 1)[0].split("/", 1)[0].split("\\", 1)[0]
    return float(int(suffix[:4])) / 1000.0


def summarize_parameter_driver_rows(rows: list[dict]) -> dict:
    experimental = [row for row in rows if row["mode_class"] == "experimental"]
    scale_values = sorted({round(_as_float(row["wall_velocity_scale"]), 12) for row in experimental})
    transfer_modes = sorted({row["reaction_transfer_mode"] for row in rows})
    summary = {
        "row_count": len(rows),
        "static_row_count": sum(1 for row in rows if row["mode_class"] == "static"),
        "experimental_row_count": len(experimental),
        "engineering_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "engineering"),
        "link_area_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "link_area_experimental"),
        "stable_count": sum(1 for row in rows if _as_bool(row["stable"])),
        "quality_pass_count": sum(1 for row in rows if _as_bool(row["quality_pass"])),
        "scale_count": len(scale_values),
        "scale_values": scale_values,
        "transfer_mode_count": len(transfer_modes),
        "transfer_modes": transfer_modes,
        "min_completed_lbm_steps": min(_as_int(row["completed_lbm_steps"]) for row in rows),
        "min_total_mpm_substeps": min(_as_int(row["total_mpm_substeps"]) for row in rows),
        "min_rho_min_global": min(_as_float(row["rho_min_global"]) for row in rows),
        "max_rho_max_global": max(_as_float(row["rho_max_global"]) for row in rows),
        "max_lbm_max_v_global": max(_as_float(row["lbm_max_v_global"]) for row in rows),
        "min_mpm_min_J_global": min(_as_float(row["mpm_min_J_global"]) for row in rows),
        "max_mpm_max_speed_global": max(_as_float(row["mpm_max_speed_global"]) for row in rows),
        "min_projected_mass_min": min(_as_float(row["projected_mass_min"]) for row in rows),
        "max_projected_mass_max": max(_as_float(row["projected_mass_max"]) for row in rows),
        "min_active_cell_count": min(_as_int(row["active_cell_count"]) for row in rows),
        "min_bb_link_count_max": min(_as_int(row["bb_link_count_max"]) for row in rows),
        "max_application_report_count": max(_as_int(row["application_report_count"]) for row in rows),
        "max_applied_velocity_norm": max(_as_float(row["max_applied_velocity_norm"]) for row in rows),
        "max_lbm_population_update_count": max(_as_int(row["lbm_population_update_count_max"]) for row in rows),
        "scope_note": "Step 40 controlled jet-cycle proxy parameter sensitivity smoke; tethered proxy diagnostics only.",
    }
    summary["driver_pass"] = bool(
        summary["row_count"] == 8
        and summary["static_row_count"] == 2
        and summary["experimental_row_count"] == 6
        and summary["scale_count"] == 3
        and summary["transfer_mode_count"] == 2
        and summary["stable_count"] == 8
        and summary["quality_pass_count"] == 8
        and summary["min_completed_lbm_steps"] >= 40
        and summary["min_total_mpm_substeps"] >= 200
        and summary["min_rho_min_global"] > 0.95
        and summary["max_rho_max_global"] < 1.05
        and summary["max_lbm_max_v_global"] < 0.1
        and summary["min_mpm_min_J_global"] > 0.0
        and summary["min_projected_mass_min"] > 0.0
        and summary["min_active_cell_count"] > 0
        and summary["min_bb_link_count_max"] > 0
        and summary["max_lbm_population_update_count"] == 0
        and finite_values(summary)
    )
    return summary


def assert_parameter_driver_summary(summary: dict) -> None:
    if not _as_bool(summary["driver_pass"]):
        raise RuntimeError(f"Step 40 parameter driver summary failed: {summary}")


def summarize_scale_response(rows: list[dict]) -> tuple[list[dict], dict]:
    experimental = sorted(
        [row for row in rows if row["mode_class"] == "experimental"],
        key=lambda row: (row["reaction_transfer_mode"], _as_float(row["wall_velocity_scale"])),
    )
    by_mode: dict[str, list[dict]] = {}
    for row in experimental:
        by_mode.setdefault(row["reaction_transfer_mode"], []).append(row)

    response_rows = []
    mode_passes = {}
    for mode, mode_rows in sorted(by_mode.items()):
        sequence = [_as_float(row["max_applied_velocity_norm"]) for row in mode_rows]
        caps = [_as_float(row["wall_velocity_cap_lbm"]) for row in mode_rows]
        mode_pass = _nondecreasing_or_capped(sequence, caps)
        mode_passes[mode] = mode_pass
        for row in mode_rows:
            cap = _as_float(row["wall_velocity_cap_lbm"])
            max_applied = _as_float(row["max_applied_velocity_norm"])
            response_rows.append(
                {
                    "case": row["case"],
                    "transfer_mode": mode,
                    "reaction_transfer_mode": mode,
                    "wall_velocity_scale": _as_float(row["wall_velocity_scale"]),
                    "wall_velocity_cap_lbm": cap,
                    "max_applied_velocity_norm": max_applied,
                    "applied_cell_count_min": _as_int(row["applied_cell_count_min"]),
                    "application_report_count": _as_int(row["application_report_count"]),
                    "stable": _as_bool(row["stable"]),
                    "cap_saturation_observed": max_applied >= cap - 1.0e-9,
                    "response_pass": bool(
                        mode_pass
                        and _as_bool(row["stable"])
                        and _as_int(row["applied_cell_count_min"]) > 0
                        and _as_int(row["application_report_count"]) >= 40
                        and max_applied <= cap + SCALE_TOL
                        and finite_values(row, excluded=_driver_string_fields())
                    ),
                    "notes": "applied velocity response is bounded by the configured cap; this is a proxy diagnostic",
                }
            )

    cap_value = max((_as_float(row["wall_velocity_cap_lbm"]) for row in experimental), default=0.0)
    summary = {
        "experimental_row_count": len(experimental),
        "scale_count": len({round(_as_float(row["wall_velocity_scale"]), 12) for row in experimental}),
        "engineering_row_count": sum(1 for row in experimental if row["reaction_transfer_mode"] == "engineering"),
        "link_area_row_count": sum(1 for row in experimental if row["reaction_transfer_mode"] == "link_area_experimental"),
        "all_experimental_rows_stable": all(_as_bool(row["stable"]) for row in experimental),
        "cap_value": cap_value,
        "max_applied_velocity_norm": max((_as_float(row["max_applied_velocity_norm"]) for row in experimental), default=0.0),
        "cap_saturation_observed": any(row["cap_saturation_observed"] for row in response_rows),
        "applied_velocity_response_pass": all(mode_passes.values()) if mode_passes else False,
        "parameter_sensitivity_pass": all(row["response_pass"] for row in response_rows) and len(response_rows) == 6,
    }
    return response_rows, summary


def compare_static_vs_parameter_rows(static_rows: list[dict], experimental_rows: list[dict]) -> list[dict]:
    by_transfer = {row["reaction_transfer_mode"]: row for row in static_rows}
    rows = []
    for experimental in sorted(experimental_rows, key=lambda row: (row["reaction_transfer_mode"], _as_float(row["wall_velocity_scale"]))):
        static = by_transfer[experimental["reaction_transfer_mode"]]
        row = {
            "comparison": f"static_vs_parameter_{experimental['reaction_transfer_mode']}_{scale_label(experimental['wall_velocity_scale'])}",
            "static_case": static["case"],
            "experimental_case": experimental["case"],
            "reaction_transfer_mode": experimental["reaction_transfer_mode"],
            "wall_velocity_scale": _as_float(experimental["wall_velocity_scale"]),
            "both_stable": _as_bool(static["stable"]) and _as_bool(experimental["stable"]),
            "rho_min_delta": _as_float(experimental["rho_min_global"]) - _as_float(static["rho_min_global"]),
            "rho_max_delta": _as_float(experimental["rho_max_global"]) - _as_float(static["rho_max_global"]),
            "lbm_max_v_delta": _as_float(experimental["lbm_max_v_global"]) - _as_float(static["lbm_max_v_global"]),
            "mpm_min_J_delta": _as_float(experimental["mpm_min_J_global"]) - _as_float(static["mpm_min_J_global"]),
            "projected_mass_delta": _as_float(experimental["projected_mass_max"]) - _as_float(static["projected_mass_max"]),
            "active_cell_count_delta": _as_int(experimental["active_cell_count"]) - _as_int(static["active_cell_count"]),
            "bb_link_count_delta": _as_int(experimental["bb_link_count_max"]) - _as_int(static["bb_link_count_max"]),
            "experimental_applied_velocity_max": _as_float(experimental["max_applied_velocity_norm"]),
            "notes": "bounded static-vs-parameter proxy comparison",
        }
        row["comparison_pass"] = bool(
            row["both_stable"]
            and finite_values(row)
            and abs(row["rho_min_delta"]) <= 0.05
            and abs(row["rho_max_delta"]) <= 0.05
            and abs(row["lbm_max_v_delta"]) <= 0.08
            and abs(row["mpm_min_J_delta"]) <= 0.05
            and abs(row["projected_mass_delta"]) <= 1.0e-3
            and abs(row["active_cell_count_delta"]) <= 500
            and abs(row["bb_link_count_delta"]) <= 500
            and row["experimental_applied_velocity_max"] > 0.0
        )
        rows.append(row)
    return rows


def compare_transfer_modes_by_scale(experimental_rows: list[dict]) -> list[dict]:
    by_scale: dict[float, dict[str, dict]] = {}
    for row in experimental_rows:
        by_scale.setdefault(round(_as_float(row["wall_velocity_scale"]), 12), {})[row["reaction_transfer_mode"]] = row

    rows = []
    for scale, scale_rows in sorted(by_scale.items()):
        engineering = scale_rows["engineering"]
        link_area = scale_rows["link_area_experimental"]
        row = {
            "comparison": f"engineering_vs_link_area_scale_{scale_label(scale)}",
            "engineering_case": engineering["case"],
            "link_area_case": link_area["case"],
            "wall_velocity_scale": float(scale),
            "both_stable": _as_bool(engineering["stable"]) and _as_bool(link_area["stable"]),
            "link_area_scale_final": _as_float(link_area["area_scale_final"]),
            "rho_min_delta": _as_float(link_area["rho_min_global"]) - _as_float(engineering["rho_min_global"]),
            "rho_max_delta": _as_float(link_area["rho_max_global"]) - _as_float(engineering["rho_max_global"]),
            "lbm_max_v_delta": _as_float(link_area["lbm_max_v_global"]) - _as_float(engineering["lbm_max_v_global"]),
            "mpm_min_J_delta": _as_float(link_area["mpm_min_J_global"]) - _as_float(engineering["mpm_min_J_global"]),
            "projected_mass_delta": _as_float(link_area["projected_mass_max"]) - _as_float(engineering["projected_mass_max"]),
            "notes": "bounded engineering-vs-link-area parameter proxy comparison",
        }
        row["comparison_pass"] = bool(
            row["both_stable"]
            and finite_values(row)
            and 0.25 <= row["link_area_scale_final"] <= 2.0
            and abs(row["projected_mass_delta"]) <= 1.0e-3
            and abs(row["rho_min_delta"]) <= 0.05
            and abs(row["rho_max_delta"]) <= 0.05
            and abs(row["lbm_max_v_delta"]) <= 0.08
            and abs(row["mpm_min_J_delta"]) <= 0.05
        )
        rows.append(row)
    return rows


def summarize_cap_saturation(application_rows_by_case: dict[str, list[dict]], driver_rows: list[dict]) -> tuple[list[dict], dict]:
    rows = []
    for driver_row in sorted([row for row in driver_rows if row["mode_class"] == "experimental"], key=lambda row: (row["reaction_transfer_mode"], _as_float(row["wall_velocity_scale"]))):
        app_rows = application_rows_by_case.get(driver_row["case"], [])
        cap = _as_float(driver_row["wall_velocity_cap_lbm"])
        max_values = [_as_float(row["max_applied_velocity_norm"]) for row in app_rows]
        cap_hit_count = sum(1 for value in max_values if value >= cap - 1.0e-9)
        row = {
            "case": driver_row["case"],
            "transfer_mode": driver_row["reaction_transfer_mode"],
            "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
            "wall_velocity_scale": _as_float(driver_row["wall_velocity_scale"]),
            "wall_velocity_cap_lbm": cap,
            "timeseries_row_count": len(app_rows),
            "max_applied_velocity_norm": max(max_values) if max_values else 0.0,
            "cap_hit_count": cap_hit_count,
            "cap_hit_observed": cap_hit_count > 0,
            "finite_pass": finite_values({"values": 0.0}) and all(math.isfinite(value) for value in max_values),
        }
        row["cap_pass"] = bool(
            row["timeseries_row_count"] >= 40
            and row["max_applied_velocity_norm"] <= cap + SCALE_TOL
            and row["finite_pass"]
        )
        rows.append(row)
    summary = {
        "row_count": len(rows),
        "cap_value": max((_as_float(row["wall_velocity_cap_lbm"]) for row in rows), default=0.0),
        "cap_hit_count": sum(_as_int(row["cap_hit_count"]) for row in rows),
        "cap_hit_observed": any(_as_bool(row["cap_hit_observed"]) for row in rows),
        "cap_pass": all(_as_bool(row["cap_pass"]) for row in rows),
        "cap_saturation_diagnostics_pass": len(rows) == 6 and all(_as_bool(row["cap_pass"]) for row in rows),
    }
    return rows, summary


def force_impulse_parameter_response_row(driver_row: dict, diagnostics_rows: list[dict]) -> dict:
    impulse = compute_impulse_norm_proxy(diagnostics_rows)
    row = {
        "case": driver_row["case"],
        "mode_class": driver_row["mode_class"],
        "transfer_mode": driver_row["reaction_transfer_mode"],
        "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
        "wall_velocity_scale": _as_float(driver_row["wall_velocity_scale"]),
        "hydro_force_max_norm": _as_float(driver_row["hydro_force_max_norm"]),
        "bb_correction_integral_proxy": _as_float(impulse["bb_correction_integral_proxy"]),
        "bb_link_count_integral_proxy": _as_float(impulse["bb_link_count_integral_proxy"]),
        "impulse_proxy": _as_float(impulse["hydro_force_max_norm_integral_proxy"]),
        "notes": "existing-diagnostics force and bounce-back proxy only; no real-impulse claim",
    }
    row["response_finite_pass"] = bool(
        finite_values(row)
        and _as_float(row["bb_link_count_integral_proxy"]) > 0.0
        and _as_bool(impulse["impulse_proxy_finite_pass"])
    )
    return row


def summarize_response_rows(rows: list[dict], pass_key: str) -> dict:
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if _as_bool(row[pass_key])),
        "comparison_pass_count": sum(1 for row in rows if _as_bool(row[pass_key])),
        "response_finite_pass_count": sum(1 for row in rows if _as_bool(row[pass_key])),
        "comparison_pass": all(_as_bool(row[pass_key]) for row in rows),
        "force_impulse_parameter_response_pass": all(_as_bool(row[pass_key]) for row in rows),
    }


def write_parameter_sensitivity_outputs(rows: list[dict], csv_path, json_path, summary: dict) -> None:
    write_csv_rows(csv_path, rows)
    write_json(json_path, {"summary": summary, "rows": rows})


def write_csv_rows(path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    fields = _fieldnames(rows) if fieldnames is None else fieldnames
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(row.get(field, "")) for field in fields})


def write_json(path, data) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def finite_values(row, excluded=()) -> bool:
    values = row.values() if isinstance(row, dict) else row
    if isinstance(row, dict):
        iterable = ((key, value) for key, value in row.items() if key not in excluded)
    else:
        iterable = ((None, value) for value in values)
    for _, value in iterable:
        if isinstance(value, bool) or value == "":
            continue
        if isinstance(value, (list, tuple)):
            if not finite_values(value):
                return False
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number):
            return False
    return True


def _nondecreasing_or_capped(values: list[float], caps: list[float]) -> bool:
    if len(values) < 2:
        return False
    for prev, current, prev_cap, current_cap in zip(values, values[1:], caps, caps[1:]):
        if current + 1.0e-12 >= prev:
            continue
        if prev >= prev_cap - 1.0e-9 and current >= current_cap - 1.0e-9:
            continue
        return False
    return all(value <= cap + SCALE_TOL for value, cap in zip(values, caps))


def _fieldnames(rows: list[dict]) -> list[str]:
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    return fields


def _csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def _driver_string_fields():
    return {
        "case",
        "candidate_id",
        "mode_class",
        "geometry_type",
        "geometry_source",
        "mode",
        "reaction_transfer_mode",
        "boundary_motion_mode",
        "boundary_motion_config_path",
        "boundary_motion_report_enabled",
        "boundary_motion_report_written",
        "boundary_motion_interface_report_path",
        "wall_velocity_application_mode",
        "wall_velocity_application_config_path",
        "wall_velocity_application_report_enabled",
        "wall_velocity_application_report_written",
        "wall_velocity_application_report_path",
        "wall_velocity_application_timeseries_path",
        "application_envelope_pass",
        "modify_bounceback_formula_any",
        "quality_check_enabled",
        "quality_check_strict",
        "quality_pass",
        "quality_severity",
        "quality_gate_strict",
        "quality_report_path",
        "driver_timing_path",
        "has_nan",
        "has_inf",
        "stable",
        "notes",
    }


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _as_int(value) -> int:
    return int(float(value))


def _as_float(value) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite value: {value}")
    return number


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return Path(__file__).resolve().parents[1] / path_obj
