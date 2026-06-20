import os

from step36_common import ROOT, fieldnames_from_rows, read_json, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    payload = read_json("outputs/step36_experimental_application_smoke/experimental_application_results.json")
    rows = [quality_row(row) for row in payload["rows"]]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["quality_pass"]),
        "quality_pass": all(row["quality_pass"] for row in rows),
        "min_applied_cell_count": min(int(row["applied_cell_count"]) for row in rows),
        "max_applied_velocity_norm": max(float(row["max_applied_velocity_norm"]) for row in rows),
        "max_lbm_population_update_count": max(int(row["lbm_population_update_count"]) for row in rows),
    }
    if not summary["quality_pass"]:
        raise RuntimeError(f"Step 36 application quality failed: {summary}")

    out_dir = ROOT / "outputs" / "step36_wall_velocity_application_quality"
    write_csv_rows(out_dir / "application_quality.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "application_quality.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 36 wall velocity application quality finished"
    write_log(
        "logs/step36_wall_velocity_application_quality.log",
        [marker, f"row_count={summary['row_count']}", f"quality_pass={summary['quality_pass']}"],
    )
    print(f"quality_pass={summary['quality_pass']}")
    print(marker)


def quality_row(driver_row):
    report = read_json(driver_row["wall_velocity_application_report_path"])
    summary = report["summary"]
    row = {
        "case": driver_row["case"],
        "source_report_path": driver_row["wall_velocity_application_report_path"],
        "report_pass": bool(summary["report_pass"]),
        "finite_pass": bool(summary["finite_pass"]),
        "cap_pass": bool(summary["cap_pass"]),
        "apply_to_lbm_solid_vel": bool(summary["apply_to_lbm_solid_vel"]),
        "apply_to_lbm_populations": bool(summary["apply_to_lbm_populations"]),
        "modify_bounceback_formula": bool(summary["modify_bounceback_formula"]),
        "applied_cell_count": int(summary["applied_cell_count"]),
        "max_applied_velocity_norm": float(summary["max_applied_velocity_norm"]),
        "wall_velocity_cap_lbm": float(summary["wall_velocity_cap_lbm"]),
        "lbm_population_update_count": int(summary["lbm_population_update_count"]),
    }
    row["quality_pass"] = bool(
        row["report_pass"]
        and row["finite_pass"]
        and row["cap_pass"]
        and row["apply_to_lbm_solid_vel"]
        and not row["apply_to_lbm_populations"]
        and not row["modify_bounceback_formula"]
        and row["applied_cell_count"] > 0
        and row["max_applied_velocity_norm"] <= row["wall_velocity_cap_lbm"] + 1.0e-12
        and row["lbm_population_update_count"] == 0
    )
    return row


if __name__ == "__main__":
    main()
