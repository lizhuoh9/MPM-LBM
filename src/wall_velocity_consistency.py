import math


def compare_wall_velocity_to_motion_mapping(wall_velocity_rows: list[dict], motion_mapping_rows: list[dict]) -> dict:
    motion_by_key = {
        (_phase_key(row["phase"]), row["region_id"]): row
        for row in motion_mapping_rows
        if _phase_is_sampled(float(row["phase"]))
    }
    rows = []
    grouped = _group_wall_rows(wall_velocity_rows)
    for key in sorted(grouped):
        phase, region_id = key
        motion_row = motion_by_key.get((phase, region_id))
        wall_rows = grouped[key]
        if motion_row is None:
            rows.append(_missing_row(phase, region_id))
            continue
        row = _compare_phase_region(phase, region_id, wall_rows, motion_row)
        rows.append(row)

    phase_match_pass = _phase_set(wall_velocity_rows) == _phase_set(motion_mapping_rows)
    region_match_pass = _region_set(wall_velocity_rows) == _region_set(motion_mapping_rows)
    mantle_rows = [row for row in rows if row["region_id"] == "mantle_outer"]
    cavity_rows = [row for row in rows if row["region_id"] == "mantle_cavity_proxy"]
    funnel_rows = [row for row in rows if row["region_id"] == "funnel_outlet_proxy"]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["consistency_pass"])),
        "phase_match_pass": phase_match_pass,
        "region_match_pass": region_match_pass,
        "mantle_velocity_consistency_pass": all(bool(row["mantle_velocity_consistency_pass"]) for row in mantle_rows),
        "cavity_rate_sign_consistency_pass": all(bool(row["cavity_rate_sign_consistency_pass"]) for row in cavity_rows),
        "funnel_rate_sign_consistency_pass": all(bool(row["funnel_rate_sign_consistency_pass"]) for row in funnel_rows),
        "max_wall_velocity_norm": max((float(row["wall_velocity_norm_max"]) for row in rows), default=0.0),
        "max_motion_velocity_norm": max((float(row["motion_velocity_norm_max"]) for row in rows), default=0.0),
    }
    summary["consistency_pass"] = (
        summary["row_count"] >= 21
        and summary["pass_count"] == summary["row_count"]
        and bool(summary["phase_match_pass"])
        and bool(summary["region_match_pass"])
        and bool(summary["mantle_velocity_consistency_pass"])
        and bool(summary["cavity_rate_sign_consistency_pass"])
        and bool(summary["funnel_rate_sign_consistency_pass"])
    )
    return {"summary": summary, "rows": rows}


def _compare_phase_region(phase: float, region_id: str, wall_rows: list[dict], motion_row: dict) -> dict:
    wall_velocity_norm_max = max(float(row["velocity_norm_max"]) for row in wall_rows)
    wall_velocity_norm_mean = sum(float(row["velocity_norm_mean"]) for row in wall_rows) / float(len(wall_rows))
    motion_velocity_norm_max = float(motion_row["velocity_norm_max"])
    motion_velocity_norm_mean = float(motion_row["velocity_norm_mean"])
    finite_pass = all(
        math.isfinite(value)
        for value in (
            phase,
            wall_velocity_norm_max,
            wall_velocity_norm_mean,
            motion_velocity_norm_max,
            motion_velocity_norm_mean,
            float(motion_row["mantle_radius_rate"]),
            float(motion_row["volume_rate"]),
            float(motion_row["aperture_rate"]),
        )
    )
    mantle_pass = True
    cavity_pass = True
    funnel_pass = True
    if region_id == "mantle_outer":
        mantle_pass = _nonzero_agrees(wall_velocity_norm_max, motion_velocity_norm_max)
    if region_id == "mantle_cavity_proxy":
        cavity_pass = _sign_matches(_mean_field(wall_rows, "velocity_y_mean"), float(motion_row["volume_rate"]))
    if region_id == "funnel_outlet_proxy":
        funnel_pass = _sign_matches(_mean_field(wall_rows, "velocity_y_mean"), float(motion_row["aperture_rate"]))
    row = {
        "phase": phase,
        "region_id": region_id,
        "wall_grid_row_count": len(wall_rows),
        "motion_row_present": True,
        "wall_velocity_norm_max": wall_velocity_norm_max,
        "wall_velocity_norm_mean": wall_velocity_norm_mean,
        "motion_velocity_norm_max": motion_velocity_norm_max,
        "motion_velocity_norm_mean": motion_velocity_norm_mean,
        "mantle_radius_rate": float(motion_row["mantle_radius_rate"]),
        "volume_rate": float(motion_row["volume_rate"]),
        "aperture_rate": float(motion_row["aperture_rate"]),
        "finite_pass": finite_pass,
        "phase_match_pass": True,
        "region_match_pass": True,
        "mantle_velocity_consistency_pass": mantle_pass,
        "cavity_rate_sign_consistency_pass": cavity_pass,
        "funnel_rate_sign_consistency_pass": funnel_pass,
    }
    row["consistency_pass"] = all(
        bool(row[key])
        for key in (
            "motion_row_present",
            "finite_pass",
            "phase_match_pass",
            "region_match_pass",
            "mantle_velocity_consistency_pass",
            "cavity_rate_sign_consistency_pass",
            "funnel_rate_sign_consistency_pass",
        )
    )
    return row


def _missing_row(phase: float, region_id: str) -> dict:
    return {
        "phase": phase,
        "region_id": region_id,
        "wall_grid_row_count": 0,
        "motion_row_present": False,
        "wall_velocity_norm_max": 0.0,
        "wall_velocity_norm_mean": 0.0,
        "motion_velocity_norm_max": 0.0,
        "motion_velocity_norm_mean": 0.0,
        "mantle_radius_rate": 0.0,
        "volume_rate": 0.0,
        "aperture_rate": 0.0,
        "finite_pass": False,
        "phase_match_pass": False,
        "region_match_pass": False,
        "mantle_velocity_consistency_pass": False,
        "cavity_rate_sign_consistency_pass": False,
        "funnel_rate_sign_consistency_pass": False,
        "consistency_pass": False,
    }


def _group_wall_rows(rows: list[dict]) -> dict[tuple[float, str], list[dict]]:
    grouped = {}
    for row in rows:
        key = (_phase_key(row["phase"]), row["region_id"])
        grouped.setdefault(key, []).append(row)
    return grouped


def _phase_set(rows: list[dict]) -> set[float]:
    return {_phase_key(row["phase"]) for row in rows if _phase_is_sampled(float(row["phase"]))}


def _region_set(rows: list[dict]) -> set[str]:
    return {row["region_id"] for row in rows}


def _phase_is_sampled(phase: float) -> bool:
    return any(math.isclose(float(phase), sample, abs_tol=1.0e-12) for sample in (0.0, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0))


def _phase_key(phase) -> float:
    return round(float(phase), 12)


def _nonzero_agrees(wall_value: float, motion_value: float, tolerance=1.0e-12) -> bool:
    if abs(float(motion_value)) <= tolerance:
        return abs(float(wall_value)) <= tolerance
    return abs(float(wall_value)) > tolerance


def _sign_matches(wall_value: float, source_rate: float, tolerance=1.0e-12) -> bool:
    if abs(float(source_rate)) <= tolerance:
        return abs(float(wall_value)) <= tolerance
    return math.copysign(1.0, float(wall_value)) == math.copysign(1.0, float(source_rate))


def _mean_field(rows: list[dict], field: str) -> float:
    return sum(float(row[field]) for row in rows) / float(len(rows)) if rows else 0.0
