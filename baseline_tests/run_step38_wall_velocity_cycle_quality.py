import os

from step38_common import (
    CYCLE_PERIOD_STEPS,
    ROOT,
    fieldnames_from_rows,
    read_driver_rows,
    read_timeseries_rows,
    write_csv_rows,
    write_json,
    write_log,
)
from src.jet_cycle_proxy_diagnostics import wall_velocity_cycle_quality_row


def main():
    os.chdir(ROOT)
    driver_rows = read_driver_rows()
    rows = [
        wall_velocity_cycle_quality_row(row, read_timeseries_rows(row), CYCLE_PERIOD_STEPS)
        for row in driver_rows
        if row["mode_class"] == "experimental"
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["quality_pass"]),
        "quality_pass": all(row["quality_pass"] for row in rows),
        "min_timeseries_row_count": min(int(row["timeseries_row_count"]) for row in rows) if rows else 0,
        "min_applied_cell_count": min(int(row["applied_cell_count_min"]) for row in rows) if rows else 0,
        "max_applied_velocity_norm": max(float(row["max_applied_velocity_norm"]) for row in rows) if rows else 0.0,
        "max_lbm_population_update_count": max(int(row["lbm_population_update_count_max"]) for row in rows) if rows else 0,
    }
    if not summary["quality_pass"] or int(summary["row_count"]) != 2:
        raise RuntimeError(f"Step 38 wall velocity cycle quality failed: {summary}")

    out_dir = ROOT / "outputs" / "step38_wall_velocity_cycle_quality"
    write_csv_rows(out_dir / "wall_velocity_cycle_quality.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "wall_velocity_cycle_quality.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 38 wall velocity cycle quality finished"
    write_log("logs/step38_wall_velocity_cycle_quality.log", [marker, f"row_count={summary['row_count']}"])
    print(f"quality_pass={summary['quality_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
