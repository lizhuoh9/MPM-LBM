import math


CONSISTENCY_FIELDS = ["check", "pass", "value", "notes"]
CYCLE_FIELDS = ["region_id", "phase0_phase1_displacement_delta", "closure_tolerance", "closure_pass"]


def compare_displacement_to_schedule(schedule_rows: list[dict], displacement_rows: list[dict]) -> tuple[list[dict], dict]:
    schedule_by_index = {int(row["sample_index"]): row for row in schedule_rows}
    displacement_by_index = {}
    for row in displacement_rows:
        displacement_by_index.setdefault(int(row["sample_index"]), []).append(row)
    checks = [
        _check("schedule_row_count", len(schedule_rows) == 81, len(schedule_rows), "Step 32 schedule row count must remain 81"),
        _check("displacement_sample_count", len(displacement_by_index) == len(schedule_rows), len(displacement_by_index), "displacement sample count must match schedule"),
        _check("phase_samples_match", _field_match(schedule_by_index, displacement_by_index, "phase", "phase"), len(displacement_rows), "displacement phases must match schedule phases"),
        _check("mantle_scale_consistency", _field_match(schedule_by_index, displacement_by_index, "mantle_radius_scale", "mantle_radius_scale") and _has_nonzero("mantle_outer", displacement_rows), len(displacement_rows), "mantle displacement rows must track mantle scale"),
        _check("cavity_volume_scale_consistency", _field_match(schedule_by_index, displacement_by_index, "cavity_volume_scale", "volume_scale") and _has_nonzero("mantle_cavity_proxy", displacement_rows), len(displacement_rows), "cavity displacement rows must track volume scale"),
        _check("funnel_aperture_scale_consistency", _field_match(schedule_by_index, displacement_by_index, "funnel_aperture_scale", "aperture_scale") and _has_nonzero("funnel_outlet_proxy", displacement_rows), len(displacement_rows), "funnel displacement rows must track aperture scale"),
    ]
    summary = {
        "schedule_row_count": len(schedule_rows),
        "displacement_row_count": len(displacement_rows),
        "displacement_sample_count": len(displacement_by_index),
        "phase_samples_match": bool(checks[2]["pass"]),
        "mantle_scale_consistency_pass": bool(checks[3]["pass"]),
        "cavity_volume_scale_consistency_pass": bool(checks[4]["pass"]),
        "funnel_aperture_scale_consistency_pass": bool(checks[5]["pass"]),
        "row_count": len(checks),
        "pass_count": sum(1 for row in checks if row["pass"]),
    }
    summary["consistency_pass"] = all(row["pass"] for row in checks)
    return checks, summary


def compare_displacement_to_motion_mapping(motion_rows: list[dict], displacement_rows: list[dict]) -> tuple[list[dict], dict]:
    motion_keys = {(int(row["sample_index"]), row["region_id"]) for row in motion_rows}
    displacement_keys = {(int(row["sample_index"]), row["region_id"]) for row in displacement_rows}
    checks = [
        _check("motion_mapping_row_count", len(motion_rows) == 243, len(motion_rows), "Step 33 motion row count must remain 243"),
        _check("displacement_row_count", len(displacement_rows) == 243, len(displacement_rows), "Step 42 displacement row count must be 243"),
        _check("phase_match", _paired_field_match(motion_rows, displacement_rows, "phase", "phase"), len(displacement_rows), "Step 42 phases must match Step 33 motion phases"),
        _check("region_match", motion_keys == displacement_keys, len(displacement_keys), "Step 42 regions must match Step 33 motion regions"),
        _check("velocity_displacement_sign", _velocity_displacement_sign_pass(motion_rows, displacement_rows), len(displacement_rows), "velocity and displacement diagnostics must remain finite and nonnegative"),
        _check("mantle_motion_displacement", _region_fields_match(motion_rows, displacement_rows, "mantle_outer", "mantle_radius_scale", "mantle_radius_scale") and _has_nonzero("mantle_outer", displacement_rows), "mantle_outer", "mantle displacement must align with Step 33 mantle motion scale"),
        _check("cavity_motion_displacement", _region_fields_match(motion_rows, displacement_rows, "mantle_cavity_proxy", "volume_scale", "volume_scale") and _has_nonzero("mantle_cavity_proxy", displacement_rows), "mantle_cavity_proxy", "cavity displacement must align with Step 33 cavity scale"),
        _check("funnel_motion_displacement", _region_fields_match(motion_rows, displacement_rows, "funnel_outlet_proxy", "aperture_scale", "aperture_scale") and _has_nonzero("funnel_outlet_proxy", displacement_rows), "funnel_outlet_proxy", "funnel displacement must align with Step 33 aperture scale"),
    ]
    summary = {
        "motion_mapping_row_count": len(motion_rows),
        "displacement_row_count": len(displacement_rows),
        "phase_match_pass": bool(checks[2]["pass"]),
        "region_match_pass": bool(checks[3]["pass"]),
        "velocity_displacement_sign_pass": bool(checks[4]["pass"]),
        "mantle_motion_displacement_pass": bool(checks[5]["pass"]),
        "cavity_motion_displacement_pass": bool(checks[6]["pass"]),
        "funnel_motion_displacement_pass": bool(checks[7]["pass"]),
        "row_count": len(checks),
        "pass_count": sum(1 for row in checks if row["pass"]),
    }
    summary["consistency_pass"] = all(row["pass"] for row in checks)
    return checks, summary


def cycle_closure_rows(displacement_rows: list[dict], tolerance=1.0e-10) -> tuple[list[dict], dict]:
    rows = []
    for region_id in ("mantle_outer", "mantle_cavity_proxy", "funnel_outlet_proxy"):
        region_rows = sorted([row for row in displacement_rows if row["region_id"] == region_id], key=lambda item: int(item["sample_index"]))
        if not region_rows:
            delta = float("inf")
        else:
            first = region_rows[0]
            last = region_rows[-1]
            deltas = [
                abs(float(first[field]) - float(last[field]))
                for field in (
                    "displacement_norm_min",
                    "displacement_norm_max",
                    "displacement_norm_mean",
                    "bbox_min_x",
                    "bbox_min_y",
                    "bbox_min_z",
                    "bbox_max_x",
                    "bbox_max_y",
                    "bbox_max_z",
                )
            ]
            delta = max(deltas)
        rows.append(
            {
                "region_id": region_id,
                "phase0_phase1_displacement_delta": float(delta),
                "closure_tolerance": float(tolerance),
                "closure_pass": bool(delta <= tolerance),
            }
        )
    summary = {
        "row_count": len(rows),
        "closure_tolerance": float(tolerance),
        "cycle_closure_pass": all(row["closure_pass"] for row in rows),
    }
    return rows, summary


def assert_consistency(summary: dict, label: str) -> None:
    if not bool(summary.get("consistency_pass", False)):
        raise RuntimeError(f"{label} failed: {summary}")


def assert_cycle_closure(summary: dict) -> None:
    if not bool(summary.get("cycle_closure_pass", False)):
        raise RuntimeError(f"Step 42 cycle closure diagnostics failed: {summary}")


def _field_match(schedule_by_index, displacement_by_index, schedule_field, displacement_field) -> bool:
    for sample_index, schedule_row in schedule_by_index.items():
        for displacement_row in displacement_by_index.get(sample_index, []):
            if abs(float(schedule_row[schedule_field]) - float(displacement_row[displacement_field])) > 1.0e-12:
                return False
    return True


def _paired_field_match(left_rows, right_rows, left_field, right_field) -> bool:
    right_by_key = {(int(row["sample_index"]), row["region_id"]): row for row in right_rows}
    for left_row in left_rows:
        right_row = right_by_key.get((int(left_row["sample_index"]), left_row["region_id"]))
        if right_row is None:
            return False
        if abs(float(left_row[left_field]) - float(right_row[right_field])) > 1.0e-12:
            return False
    return True


def _region_fields_match(left_rows, right_rows, region_id, left_field, right_field) -> bool:
    left_region = [row for row in left_rows if row["region_id"] == region_id]
    right_region = [row for row in right_rows if row["region_id"] == region_id]
    return bool(left_region) and bool(right_region) and _paired_field_match(left_region, right_region, left_field, right_field)


def _velocity_displacement_sign_pass(motion_rows, displacement_rows) -> bool:
    right_by_key = {(int(row["sample_index"]), row["region_id"]): row for row in displacement_rows}
    for motion_row in motion_rows:
        displacement_row = right_by_key.get((int(motion_row["sample_index"]), motion_row["region_id"]))
        if displacement_row is None:
            return False
        for field in ("velocity_norm_max", "displacement_norm_max"):
            source = motion_row if field == "velocity_norm_max" else displacement_row
            value = float(source[field])
            if not math.isfinite(value) or value < 0.0:
                return False
        if not bool(displacement_row["finite_pass"]) or not bool(displacement_row["bounds_pass"]):
            return False
    return True


def _has_nonzero(region_id: str, rows: list[dict]) -> bool:
    return any(row["region_id"] == region_id and float(row["displacement_norm_max"]) > 0.0 for row in rows)


def _check(name, passed, value, notes):
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}
