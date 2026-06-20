import os

from step43_common import ROOT, read_json, write_csv_rows, write_json, write_log


FIELDS = ["case", "mode_class", "reaction_transfer_mode", "quality_pass", "strict", "severity", "warning_count", "error_count", "quality_report_path"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    driver_rows = []
    driver_rows.extend(read_json("outputs/step43_static_driver_regression/static_driver_results.json")["rows"])
    driver_rows.extend(read_json("outputs/step43_diagnostic_geometry_motion_noop_smoke/diagnostic_noop_results.json")["rows"])
    rows = [quality_row(row) for row in driver_rows]
    summary = {
        "quality_report_count": len(rows),
        "pass_count": sum(1 for row in rows if row["quality_pass"]),
        "strict_count": sum(1 for row in rows if row["strict"]),
        "warning_count": sum(int(row["warning_count"]) for row in rows),
        "error_count": sum(int(row["error_count"]) for row in rows),
    }
    summary["quality_report_aggregation_pass"] = bool(
        summary["quality_report_count"] == 4
        and summary["pass_count"] == 4
        and summary["strict_count"] == 4
        and summary["warning_count"] == 0
        and summary["error_count"] == 0
    )
    if not summary["quality_report_aggregation_pass"]:
        raise RuntimeError(f"Step 43 quality aggregation failed: {summary}")
    out_dir = ROOT / "outputs" / "step43_quality_report_aggregation"
    write_csv_rows(out_dir / "quality_report_summary.csv", rows, FIELDS)
    write_csv_rows(out_dir / "quality_report_summary_metrics.csv", [{"metric": key, "value": value} for key, value in sorted(summary.items())], SUMMARY_FIELDS)
    write_json(out_dir / "quality_report_summary.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 43 quality report aggregation finished"
    write_log("logs/step43_quality_report_aggregation.log", [marker, f"quality_report_count={summary['quality_report_count']}", f"pass_count={summary['pass_count']}"])
    print(f"quality_report_count={summary['quality_report_count']}")
    print(marker)


def quality_row(driver_row):
    quality = read_json(driver_row["quality_report_path"])
    gate = quality["gate"]
    return {
        "case": driver_row["case"],
        "mode_class": driver_row["mode_class"],
        "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
        "quality_pass": bool(gate["pass"]),
        "strict": bool(gate["strict"]),
        "severity": gate["severity"],
        "warning_count": len(gate.get("warnings", [])),
        "error_count": len(gate.get("reasons", [])),
        "quality_report_path": driver_row["quality_report_path"],
    }


if __name__ == "__main__":
    main()
