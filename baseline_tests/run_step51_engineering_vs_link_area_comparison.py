import os

from step51_common import ROOT, transfer_comparison_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_transfer_diagnostics import summarize_engineering_link_area_comparison

    rows = transfer_comparison_rows()
    comparison_rows, summary = summarize_engineering_link_area_comparison(rows)
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 51 engineering vs link-area comparison failed: {summary}")
    out_dir = ROOT / "outputs" / "step51_engineering_vs_link_area_comparison"
    write_csv_rows(out_dir / "engineering_vs_link_area_comparison.csv", comparison_rows)
    write_json(out_dir / "engineering_vs_link_area_comparison.json", {"summary": summary, "rows": comparison_rows})
    marker = "[OK] Step 51 engineering vs link-area comparison finished"
    write_log("logs/step51_engineering_vs_link_area_comparison.log", [marker, f"comparison_count={summary['comparison_count']}", f"comparison_pass={summary['comparison_pass']}"])
    print(marker)


if __name__ == "__main__":
    main()
