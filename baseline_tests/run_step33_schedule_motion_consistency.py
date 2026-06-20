import os

from step33_common import ROOT, load_motion_inputs, write_csv_rows, write_json, write_log
from src.squid_motion_mapping import compute_region_motion_rows


FIELDS = ["check", "pass", "value", "notes"]


def main():
    os.chdir(ROOT)
    inputs = load_motion_inputs()
    schedule_rows = inputs["schedule_rows"]
    motion_rows = compute_region_motion_rows(
        inputs["mapping_config"],
        schedule_rows,
        inputs["geometry_config"],
        inputs["region_config"],
        inputs["points"],
        inputs["masks"],
    )
    rows, summary = consistency_rows(schedule_rows, motion_rows)
    if not summary["consistency_pass"]:
        raise RuntimeError(f"Step 33 schedule-motion consistency failed: {summary}")

    out_dir = ROOT / "outputs" / "step33_schedule_motion_consistency"
    write_csv_rows(out_dir / "schedule_motion_consistency.csv", rows, FIELDS)
    write_json(out_dir / "schedule_motion_consistency.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 33 schedule-motion consistency finished"
    write_log("logs/step33_schedule_motion_consistency.log", [marker, f"row_count={len(rows)}", f"consistency_pass={summary['consistency_pass']}"])
    print(f"row_count={len(rows)}")
    print(marker)


def consistency_rows(schedule_rows, motion_rows):
    schedule_by_index = {int(row["sample_index"]): row for row in schedule_rows}
    motion_by_index = {}
    for row in motion_rows:
        motion_by_index.setdefault(int(row["sample_index"]), []).append(row)
    checks = [
        _check("schedule_row_count", len(schedule_rows) == 81, len(schedule_rows), "Step 32 schedule row count must remain 81"),
        _check("motion_sample_count", len(motion_by_index) == len(schedule_rows), len(motion_by_index), "motion sample count must match schedule"),
        _check("phase_samples_match", _field_match(schedule_by_index, motion_by_index, "phase", "phase"), len(motion_rows), "motion phase must match schedule phase"),
        _check(
            "mantle_scale_match",
            _field_match(schedule_by_index, motion_by_index, "mantle_radius_scale", "mantle_radius_scale"),
            len(motion_rows),
            "motion mantle scale must match schedule",
        ),
        _check(
            "mantle_rate_match",
            _field_match(schedule_by_index, motion_by_index, "mantle_radius_rate", "mantle_radius_rate"),
            len(motion_rows),
            "motion mantle rate must match schedule",
        ),
        _check("cavity_scale_match", _field_match(schedule_by_index, motion_by_index, "cavity_volume_scale", "volume_scale"), len(motion_rows), "motion cavity scale must match schedule"),
        _check("cavity_rate_match", _field_match(schedule_by_index, motion_by_index, "cavity_volume_rate", "volume_rate"), len(motion_rows), "motion cavity rate must match schedule"),
        _check("funnel_scale_match", _field_match(schedule_by_index, motion_by_index, "funnel_aperture_scale", "aperture_scale"), len(motion_rows), "motion funnel scale must match schedule"),
        _check("funnel_rate_match", _field_match(schedule_by_index, motion_by_index, "funnel_aperture_rate", "aperture_rate"), len(motion_rows), "motion funnel rate must match schedule"),
    ]
    summary = {
        "schedule_row_count": len(schedule_rows),
        "motion_row_count": len(motion_rows),
        "motion_sample_count": len(motion_by_index),
        "pass_count": sum(1 for row in checks if row["pass"]),
        "row_count": len(checks),
    }
    summary["consistency_pass"] = all(row["pass"] for row in checks)
    return checks, summary


def _field_match(schedule_by_index, motion_by_index, schedule_field, motion_field) -> bool:
    for sample_index, schedule_row in schedule_by_index.items():
        for motion_row in motion_by_index.get(sample_index, []):
            if abs(float(schedule_row[schedule_field]) - float(motion_row[motion_field])) > 1.0e-12:
                return False
    return True


def _check(name, passed, value, notes):
    return {"check": name, "pass": bool(passed), "value": value, "notes": notes}


if __name__ == "__main__":
    main()
