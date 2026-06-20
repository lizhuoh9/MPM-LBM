import os

from step39_common import ROOT, compare_static_experimental_multicycle, fieldnames_from_rows, read_driver_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    source_rows = read_driver_rows()
    static_by_transfer = {row["reaction_transfer_mode"]: row for row in source_rows if row["mode_class"] == "static"}
    experimental_by_transfer = {row["reaction_transfer_mode"]: row for row in source_rows if row["mode_class"] == "experimental"}
    rows = [
        compare_static_experimental_multicycle(static_by_transfer[transfer], experimental_by_transfer[transfer])
        for transfer in ("engineering", "link_area_experimental")
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["comparison_pass"]),
        "comparison_pass": all(row["comparison_pass"] for row in rows),
    }
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 39 static-vs-experimental multicycle comparison failed: {summary}")

    out_dir = ROOT / "outputs" / "step39_static_vs_experimental_multicycle_comparison"
    write_csv_rows(out_dir / "static_vs_experimental_multicycle.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "static_vs_experimental_multicycle.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 39 static vs experimental multicycle comparison finished"
    write_log("logs/step39_static_vs_experimental_multicycle_comparison.log", [marker, f"row_count={summary['row_count']}"])
    print(f"comparison_pass={summary['comparison_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
