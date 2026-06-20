import os

from step38_common import (
    ROOT,
    compare_engineering_link_area_cycle,
    fieldnames_from_rows,
    read_driver_rows,
    write_csv_rows,
    write_json,
    write_log,
)


def main():
    os.chdir(ROOT)
    source_rows = read_driver_rows()
    experimental = [row for row in source_rows if row["mode_class"] == "experimental"]
    by_transfer = {row["reaction_transfer_mode"]: row for row in experimental}
    rows = [compare_engineering_link_area_cycle(by_transfer["engineering"], by_transfer["link_area_experimental"])]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["comparison_pass"]),
        "comparison_pass": all(row["comparison_pass"] for row in rows),
    }
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 38 engineering-vs-link-area cycle comparison failed: {summary}")

    out_dir = ROOT / "outputs" / "step38_engineering_vs_link_area_cycle_comparison"
    write_csv_rows(out_dir / "engineering_vs_link_area_cycle.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "engineering_vs_link_area_cycle.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 38 engineering vs link-area cycle comparison finished"
    write_log("logs/step38_engineering_vs_link_area_cycle_comparison.log", [marker, f"row_count={summary['row_count']}"])
    print(f"comparison_pass={summary['comparison_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
