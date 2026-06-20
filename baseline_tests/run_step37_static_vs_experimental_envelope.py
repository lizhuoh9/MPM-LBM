import os

from step37_common import ROOT, fieldnames_from_rows, read_json, write_csv_rows, write_json, write_log
from src.wall_velocity_application_envelope import compare_static_experimental_envelopes


def main():
    os.chdir(ROOT)
    source_rows = read_json("outputs/step37_application_window_driver/application_window_results.json")["rows"]
    static_by_transfer = {row["reaction_transfer_mode"]: row for row in source_rows if row["mode_class"] == "static"}
    experimental_by_transfer = {row["reaction_transfer_mode"]: row for row in source_rows if row["mode_class"] == "experimental"}
    rows = [
        compare_static_experimental_envelopes(static_by_transfer[transfer], experimental_by_transfer[transfer])
        for transfer in ("engineering", "link_area_experimental")
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["comparison_pass"]),
        "comparison_pass": all(row["comparison_pass"] for row in rows),
    }
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 37 static-vs-experimental envelope failed: {summary}")

    out_dir = ROOT / "outputs" / "step37_static_vs_experimental_envelope"
    write_csv_rows(out_dir / "static_vs_experimental_envelope.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "static_vs_experimental_envelope.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 37 static vs experimental envelope finished"
    write_log("logs/step37_static_vs_experimental_envelope.log", [marker, f"row_count={summary['row_count']}"])
    print(f"comparison_pass={summary['comparison_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
