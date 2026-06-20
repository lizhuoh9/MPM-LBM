import os

from step37_common import ROOT, fieldnames_from_rows, read_json, write_csv_rows, write_json, write_log
from src.wall_velocity_application_envelope import summarize_application_envelope


def main():
    os.chdir(ROOT)
    driver_rows = read_json("outputs/step37_application_window_driver/application_window_results.json")["rows"]
    rows = [quality_row(row) for row in driver_rows if row["mode_class"] == "experimental"]
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
        raise RuntimeError(f"Step 37 wall velocity timeseries quality failed: {summary}")

    out_dir = ROOT / "outputs" / "step37_wall_velocity_timeseries_quality"
    write_csv_rows(out_dir / "wall_velocity_timeseries_quality.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "wall_velocity_timeseries_quality.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 37 wall velocity timeseries quality finished"
    write_log("logs/step37_wall_velocity_timeseries_quality.log", [marker, f"row_count={summary['row_count']}"])
    print(f"quality_pass={summary['quality_pass']}")
    print(marker)


def quality_row(driver_row):
    json_path = driver_row["wall_velocity_application_timeseries_path"].replace("\\", "/").replace(".csv", ".json")
    payload = read_json(json_path)
    summary = summarize_application_envelope(payload["rows"])
    row = {
        "case": driver_row["case"],
        "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
        "timeseries_row_count": int(summary["timeseries_row_count"]),
        "applied_cell_count_min": int(summary["applied_cell_count_min"]),
        "applied_cell_count_max": int(summary["applied_cell_count_max"]),
        "max_applied_velocity_norm": float(summary["max_applied_velocity_norm"]),
        "mean_applied_velocity_norm_max": float(summary["mean_applied_velocity_norm_max"]),
        "wall_velocity_cap_lbm": float(summary["wall_velocity_cap_lbm"]),
        "cap_pass": bool(summary["cap_pass"]),
        "finite_pass": bool(summary["finite_pass"]),
        "repeatable_phase_sequence": bool(summary["repeatable_phase_sequence"]),
        "lbm_population_update_count_max": int(summary["lbm_population_update_count_max"]),
        "modify_bounceback_formula_any": bool(summary["modify_bounceback_formula_any"]),
    }
    row["quality_pass"] = bool(
        row["timeseries_row_count"] >= 20
        and row["applied_cell_count_min"] > 0
        and row["applied_cell_count_max"] >= row["applied_cell_count_min"]
        and row["max_applied_velocity_norm"] <= row["wall_velocity_cap_lbm"] + 1.0e-12
        and row["cap_pass"]
        and row["finite_pass"]
        and row["repeatable_phase_sequence"]
        and row["lbm_population_update_count_max"] == 0
        and not row["modify_bounceback_formula_any"]
    )
    return row


if __name__ == "__main__":
    main()
