import csv
import json
import math
import os
from pathlib import Path


CYCLE_PROXY_FIELDS = [
    "metric_scope",
    "cycle_period_steps",
    "schedule_row_count",
    "driver_row_count",
    "experimental_row_count",
    "cavity_rest_volume",
    "cavity_rest_volume_source",
    "cavity_volume_scale_min",
    "cavity_volume_scale_max",
    "contraction_sample_count",
    "refill_sample_count",
    "expelled_volume_proxy",
    "refill_volume_proxy",
    "net_cycle_volume_proxy",
    "closed_cycle_pass",
    "funnel_aperture_min",
    "funnel_aperture_max",
    "funnel_open_sample_count",
    "funnel_closed_or_rest_sample_count",
    "aperture_cycle_pass",
    "min_requested_phase",
    "max_requested_phase",
    "requested_phase_unique_count",
    "phase_alignment_pass",
    "cavity_volume_cycle_pass",
    "funnel_aperture_cycle_pass",
    "notes",
]

FORCE_IMPULSE_FIELDS = [
    "case",
    "mode_class",
    "reaction_transfer_mode",
    "hydro_force_max_norm_integral_proxy",
    "bb_correction_integral_proxy",
    "bb_link_count_integral_proxy",
    "max_hydro_force_max_norm",
    "max_bb_correction",
    "max_grid_reaction_norm",
    "impulse_proxy_finite_pass",
    "notes",
]


def load_step32_schedule(schedule_path) -> list[dict]:
    payload = _read_json(schedule_path)
    rows = payload.get("rows", [])
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"missing Step 32 schedule rows: {schedule_path}")
    return rows


def load_schedule_config(config_path) -> dict:
    payload = _read_json(config_path)
    if int(payload["cycle_period_steps"]) <= 0:
        raise ValueError(f"invalid cycle_period_steps in {config_path}")
    return payload


def estimate_cavity_rest_volume(geometry_config_path) -> tuple[float, str]:
    geometry = _read_json(geometry_config_path)
    radii = [float(value) for value in geometry["mantle_radii"]]
    ellipsoid_volume = (4.0 / 3.0) * math.pi * radii[0] * radii[1] * radii[2]
    cavity_fraction_proxy = 0.35
    return ellipsoid_volume * cavity_fraction_proxy, "mantle_ellipsoid_volume_times_fixed_cavity_proxy_fraction"


def compute_cavity_volume_cycle_proxy(schedule_rows: list[dict], cavity_rest_volume: float) -> dict:
    scales = [_as_float(row["cavity_volume_scale"]) for row in schedule_rows]
    rates = [_as_float(row["cavity_volume_rate"]) for row in schedule_rows]
    first_scale = scales[0]
    final_scale = scales[-1]
    min_scale = min(scales)
    max_scale = max(scales)
    expelled = float(cavity_rest_volume) * max(0.0, first_scale - min_scale)
    refill = float(cavity_rest_volume) * max(0.0, final_scale - min_scale)
    net = float(cavity_rest_volume) * (final_scale - first_scale)
    tolerance = max(1.0e-8, 1.0e-6 * float(cavity_rest_volume))
    row = {
        "cavity_rest_volume": float(cavity_rest_volume),
        "cavity_volume_scale_min": float(min_scale),
        "cavity_volume_scale_max": float(max_scale),
        "contraction_sample_count": sum(1 for rate in rates if rate < -1.0e-12),
        "refill_sample_count": sum(1 for rate in rates if rate > 1.0e-12),
        "expelled_volume_proxy": float(expelled),
        "refill_volume_proxy": float(refill),
        "net_cycle_volume_proxy": float(net),
        "closed_cycle_pass": abs(net) <= tolerance,
    }
    row["cavity_volume_cycle_pass"] = bool(
        _finite_values(row.values())
        and row["contraction_sample_count"] > 0
        and row["refill_sample_count"] > 0
        and row["expelled_volume_proxy"] > 0.0
        and row["refill_volume_proxy"] > 0.0
        and row["closed_cycle_pass"]
    )
    return row


def compute_funnel_aperture_cycle_proxy(schedule_rows: list[dict]) -> dict:
    apertures = [_as_float(row["funnel_aperture_scale"]) for row in schedule_rows]
    rest = apertures[0]
    row = {
        "funnel_aperture_min": float(min(apertures)),
        "funnel_aperture_max": float(max(apertures)),
        "funnel_open_sample_count": sum(1 for aperture in apertures if aperture > rest + 1.0e-12),
        "funnel_closed_or_rest_sample_count": sum(1 for aperture in apertures if aperture <= rest + 1.0e-12),
    }
    row["aperture_cycle_pass"] = bool(
        _finite_values(row.values())
        and row["funnel_aperture_max"] > row["funnel_aperture_min"]
        and row["funnel_open_sample_count"] > 0
        and row["funnel_closed_or_rest_sample_count"] > 0
    )
    row["funnel_aperture_cycle_pass"] = row["aperture_cycle_pass"]
    return row


def compute_cycle_phase_alignment(application_rows: list[dict], schedule_rows: list[dict], cycle_period_steps: int) -> dict:
    requested = [_as_float(row["requested_phase"]) for row in application_rows]
    unique_steps = {int(row["driver_lbm_step"]) for row in application_rows}
    if not requested:
        return {
            "min_requested_phase": 0.0,
            "max_requested_phase": 0.0,
            "requested_phase_unique_count": 0,
            "phase_alignment_pass": False,
        }
    expected_last_phase = (int(cycle_period_steps) - 1) / float(cycle_period_steps)
    row = {
        "min_requested_phase": min(requested),
        "max_requested_phase": max(requested),
        "requested_phase_unique_count": len(unique_steps),
    }
    row["phase_alignment_pass"] = bool(
        len(schedule_rows) >= int(cycle_period_steps) + 1
        and math.isclose(row["min_requested_phase"], 0.0, abs_tol=1.0e-12)
        and row["max_requested_phase"] >= expected_last_phase - 1.0e-12
        and row["max_requested_phase"] < 1.0
        and row["requested_phase_unique_count"] >= int(cycle_period_steps)
        and _finite_values(requested)
    )
    return row


def summarize_cycle_proxy(
    schedule_config: dict,
    schedule_rows: list[dict],
    driver_rows: list[dict],
    application_rows: list[dict],
    geometry_config_path,
) -> dict:
    cavity_rest_volume, rest_volume_source = estimate_cavity_rest_volume(geometry_config_path)
    summary = {
        "metric_scope": "Step 38 controlled tethered jet-cycle proxy diagnostics only",
        "cycle_period_steps": int(schedule_config["cycle_period_steps"]),
        "schedule_row_count": len(schedule_rows),
        "driver_row_count": len(driver_rows),
        "experimental_row_count": sum(1 for row in driver_rows if row.get("mode_class") == "experimental"),
        "cavity_rest_volume_source": rest_volume_source,
    }
    summary.update(compute_cavity_volume_cycle_proxy(schedule_rows, cavity_rest_volume))
    summary.update(compute_funnel_aperture_cycle_proxy(schedule_rows))
    summary.update(compute_cycle_phase_alignment(application_rows, schedule_rows, int(schedule_config["cycle_period_steps"])))
    summary["notes"] = "schedule-derived cavity/funnel proxy diagnostics; no internal-fluid volume solve and no jet validation claim"
    return summary


def wall_velocity_cycle_quality_row(driver_row: dict, timeseries_rows: list[dict], cycle_period_steps: int) -> dict:
    if not timeseries_rows:
        return {
            "case": driver_row["case"],
            "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
            "timeseries_row_count": 0,
            "quality_pass": False,
        }
    requested = [_as_float(row["requested_phase"]) for row in timeseries_rows]
    expected_last_phase = (int(cycle_period_steps) - 1) / float(cycle_period_steps)
    selected = [_as_float(row["selected_phase"]) for row in timeseries_rows]
    applied_counts = [_as_int(row["applied_cell_count"]) for row in timeseries_rows]
    max_applied = [_as_float(row["max_applied_velocity_norm"]) for row in timeseries_rows]
    mean_applied = [_as_float(row["mean_applied_velocity_norm"]) for row in timeseries_rows]
    cap_values = [_as_float(row["wall_velocity_cap_lbm"]) for row in timeseries_rows]
    row = {
        "case": driver_row["case"],
        "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
        "timeseries_row_count": len(timeseries_rows),
        "requested_phase_min": min(requested),
        "requested_phase_max": max(requested),
        "selected_phase_min": min(selected),
        "selected_phase_max": max(selected),
        "phase_sequence_covers_full_cycle": bool(min(requested) == 0.0 and max(requested) >= expected_last_phase - 1.0e-12),
        "repeatable_phase_sequence": _repeatable_requested_phase_sequence(requested, int(cycle_period_steps)),
        "applied_cell_count_min": min(applied_counts),
        "applied_cell_count_max": max(applied_counts),
        "max_applied_velocity_norm": max(max_applied),
        "mean_applied_velocity_norm_max": max(mean_applied),
        "wall_velocity_cap_lbm": max(cap_values),
        "cap_pass": all(_as_bool(row["cap_pass"]) for row in timeseries_rows),
        "finite_pass": all(_as_bool(row["finite_pass"]) for row in timeseries_rows) and _finite_values(requested + selected + max_applied + mean_applied),
        "lbm_population_update_count_max": max(_as_int(row["lbm_population_update_count"]) for row in timeseries_rows),
        "modify_bounceback_formula_any": any(_as_bool(row["modify_bounceback_formula"]) for row in timeseries_rows),
    }
    row["quality_pass"] = bool(
        row["timeseries_row_count"] >= int(cycle_period_steps)
        and row["phase_sequence_covers_full_cycle"]
        and row["repeatable_phase_sequence"]
        and row["applied_cell_count_min"] > 0
        and row["applied_cell_count_max"] >= row["applied_cell_count_min"]
        and row["max_applied_velocity_norm"] <= row["wall_velocity_cap_lbm"] + 1.0e-12
        and row["cap_pass"]
        and row["finite_pass"]
        and row["lbm_population_update_count_max"] == 0
        and not row["modify_bounceback_formula_any"]
    )
    return row


def compute_impulse_norm_proxy(diagnostics_rows: list[dict]) -> dict:
    post_rows = [row for row in diagnostics_rows if _as_int(row["step"]) > 0]
    if not post_rows:
        return {
            "hydro_force_max_norm_integral_proxy": 0.0,
            "bb_correction_integral_proxy": 0.0,
            "bb_link_count_integral_proxy": 0.0,
            "max_hydro_force_max_norm": 0.0,
            "max_bb_correction": 0.0,
            "max_grid_reaction_norm": 0.0,
            "impulse_proxy_finite_pass": False,
        }
    hydro = [_as_float(row["hydro_force_max_norm"]) for row in post_rows]
    bb_correction = [_as_float(row["bb_max_correction"]) for row in post_rows]
    bb_links = [_as_float(row["bb_link_count"]) for row in post_rows]
    grid_reaction = [_as_float(row["max_grid_reaction_norm"]) for row in post_rows]
    summary = {
        "hydro_force_max_norm_integral_proxy": float(sum(hydro)),
        "bb_correction_integral_proxy": float(sum(bb_correction)),
        "bb_link_count_integral_proxy": float(sum(bb_links)),
        "max_hydro_force_max_norm": float(max(hydro)),
        "max_bb_correction": float(max(bb_correction)),
        "max_grid_reaction_norm": float(max(grid_reaction)),
    }
    summary["impulse_proxy_finite_pass"] = bool(_finite_values(summary.values()) and summary["bb_link_count_integral_proxy"] > 0.0)
    return summary


def force_impulse_proxy_row(driver_row: dict, diagnostics_rows: list[dict]) -> dict:
    row = {
        "case": driver_row["case"],
        "mode_class": driver_row["mode_class"],
        "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
        "notes": "existing-diagnostics force and bounce-back proxy only; no real impulse validation claim",
    }
    row.update(compute_impulse_norm_proxy(diagnostics_rows))
    return row


def write_cycle_proxy_outputs(rows: list[dict], csv_path, json_path, summary: dict) -> None:
    write_csv_rows(csv_path, rows, CYCLE_PROXY_FIELDS)
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


def read_json(path):
    return _read_json(path)


def _repeatable_requested_phase_sequence(phases: list[float], cycle_period_steps: int) -> bool:
    if len(phases) < cycle_period_steps:
        return False
    for index, phase in enumerate(phases[:cycle_period_steps]):
        expected = index / float(cycle_period_steps)
        if not math.isclose(float(phase), expected, abs_tol=1.0e-12):
            return False
    return True


def _fieldnames(rows: list[dict]) -> list[str]:
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    return fields


def _read_json(path):
    with _resolve_path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return Path(__file__).resolve().parents[1] / path_obj


def _csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def _as_float(value) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite value: {value}")
    return number


def _as_int(value) -> int:
    return int(float(value))


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _finite_values(values) -> bool:
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                continue
        if isinstance(value, (int, float)) and not math.isfinite(float(value)):
            return False
    return True
