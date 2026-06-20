import os

from step37_common import ROOT, fieldnames_from_rows, read_json, write_csv_rows, write_json, write_log
from src.wall_velocity_application_envelope import compare_engineering_link_area_envelopes


def main():
    os.chdir(ROOT)
    source_rows = read_json("outputs/step37_application_window_driver/application_window_results.json")["rows"]
    experimental = {row["reaction_transfer_mode"]: row for row in source_rows if row["mode_class"] == "experimental"}
    rows = [compare_engineering_link_area_envelopes(experimental["engineering"], experimental["link_area_experimental"])]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["comparison_pass"]),
        "comparison_pass": all(row["comparison_pass"] for row in rows),
    }
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 37 engineering-vs-link-area envelope failed: {summary}")

    out_dir = ROOT / "outputs" / "step37_engineering_vs_link_area_envelope"
    write_csv_rows(out_dir / "engineering_vs_link_area_envelope.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "engineering_vs_link_area_envelope.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 37 engineering vs link-area envelope finished"
    write_log("logs/step37_engineering_vs_link_area_envelope.log", [marker, f"row_count={summary['row_count']}"])
    print(f"comparison_pass={summary['comparison_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
