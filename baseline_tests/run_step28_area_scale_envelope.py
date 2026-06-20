import math
import os

from step28_common import (
    ROOT,
    diagnostics_path_from_driver_row,
    read_csv_rows,
    write_csv_rows,
    write_json,
    write_log,
)


FIELDS = [
    "candidate_id",
    "geometry_type",
    "n_grid",
    "area_scale_initial",
    "area_scale_min_observed",
    "area_scale_max_observed",
    "area_scale_final",
    "area_scale_config_min",
    "area_scale_config_max",
    "raw_area_scale_min",
    "raw_area_scale_max",
    "hit_lower_bound",
    "hit_upper_bound",
    "finite_pass",
    "bounded_pass",
]


def main():
    os.chdir(ROOT)
    driver_rows = [
        row
        for row in read_csv_rows("outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.csv")
        if row["reaction_transfer_mode"] == "link_area_experimental"
    ]
    rows = [_area_row(row) for row in driver_rows]
    rows.sort(key=lambda row: row["candidate_id"])
    summary = {"row_count": len(rows), "pass_count": sum(1 for row in rows if row["finite_pass"] and row["bounded_pass"])}
    if int(summary["row_count"]) != 2 or int(summary["pass_count"]) != 2:
        raise RuntimeError(f"Step 28 area-scale envelope failed: {rows}")

    out_dir = ROOT / "outputs" / "step28_area_scale_envelope"
    write_csv_rows(out_dir / "area_scale_envelope.csv", rows, FIELDS)
    write_json(out_dir / "area_scale_envelope.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 28 area-scale envelope finished"
    write_log("logs/step28_area_scale_envelope.log", [marker, f"row_count={summary['row_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def _area_row(driver_row):
    diagnostics_path = ROOT / diagnostics_path_from_driver_row(driver_row)
    if not diagnostics_path.is_file():
        raise RuntimeError(f"missing Step 28 link-area diagnostics series: {diagnostics_path}")
    initial = 1.0
    final = float(driver_row["area_scale_final"])
    config_min = float(driver_row["area_scale_min"])
    config_max = float(driver_row["area_scale_max"])
    raw_final = float(driver_row["raw_area_scale_final"])
    observed_min = min(initial, final)
    observed_max = max(initial, final)
    raw_min = min(initial, raw_final)
    raw_max = max(initial, raw_final)
    finite_pass = all(math.isfinite(value) for value in [initial, final, config_min, config_max, raw_min, raw_max])
    bounded_pass = bool(finite_pass and config_min <= observed_min <= observed_max <= config_max)
    return {
        "candidate_id": driver_row["candidate_id"],
        "geometry_type": driver_row["geometry_type"],
        "n_grid": int(float(driver_row["n_grid"])),
        "area_scale_initial": initial,
        "area_scale_min_observed": observed_min,
        "area_scale_max_observed": observed_max,
        "area_scale_final": final,
        "area_scale_config_min": config_min,
        "area_scale_config_max": config_max,
        "raw_area_scale_min": raw_min,
        "raw_area_scale_max": raw_max,
        "hit_lower_bound": observed_min <= config_min,
        "hit_upper_bound": observed_max >= config_max,
        "finite_pass": finite_pass,
        "bounded_pass": bounded_pass,
    }


if __name__ == "__main__":
    main()
