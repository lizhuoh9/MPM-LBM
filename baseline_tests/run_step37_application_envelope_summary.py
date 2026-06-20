import os
from pathlib import Path

from step37_common import ROOT, fieldnames_from_rows, read_json, write_csv_rows, write_json, write_log
from src.wall_velocity_application_envelope import collect_wall_velocity_application_reports, summarize_application_envelope


def main():
    os.chdir(ROOT)
    payload = read_json("outputs/step37_application_window_driver/application_window_results.json")
    rows = []
    for driver_row in payload["rows"]:
        if driver_row["mode_class"] != "experimental":
            continue
        case_dir = Path(ROOT / driver_row["wall_velocity_application_timeseries_path"]).parent
        reports = collect_wall_velocity_application_reports(case_dir)
        summary = summarize_application_envelope(reports)
        row = {
            "case": driver_row["case"],
            "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
            **summary,
        }
        rows.append(row)
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["application_envelope_pass"]),
        "application_envelope_pass": all(row["application_envelope_pass"] for row in rows),
        "max_applied_velocity_norm": max(float(row["max_applied_velocity_norm"]) for row in rows) if rows else 0.0,
    }
    if not summary["application_envelope_pass"] or int(summary["row_count"]) != 2:
        raise RuntimeError(f"Step 37 application envelope failed: {summary}")

    out_dir = ROOT / "outputs" / "step37_application_envelope_summary"
    write_csv_rows(out_dir / "application_envelope.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "application_envelope.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 37 application envelope summary finished"
    write_log("logs/step37_application_envelope_summary.log", [marker, f"row_count={summary['row_count']}"])
    print(f"application_envelope_pass={summary['application_envelope_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
