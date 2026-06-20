import os

from step31_common import ROOT, read_csv_rows, write_csv_rows, write_json, write_log
from src.squid_region_driver_diagnostics import (
    ENGINEERING_LINK_AREA_FIELDS,
    assert_engineering_vs_link_area_summary,
    compare_engineering_vs_link_area_static,
    summarize_engineering_vs_link_area_rows,
)


def main():
    os.chdir(ROOT)
    driver_rows = read_csv_rows("outputs/step31_static_driver_smoke/static_driver_results.csv")
    rows = compare_engineering_vs_link_area_static(driver_rows)
    summary = summarize_engineering_vs_link_area_rows(rows)
    assert_engineering_vs_link_area_summary(summary)

    out_dir = ROOT / "outputs" / "step31_engineering_vs_link_area_static_comparison"
    write_csv_rows(out_dir / "engineering_vs_link_area_static.csv", rows, ENGINEERING_LINK_AREA_FIELDS)
    write_json(out_dir / "engineering_vs_link_area_static.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 31 engineering vs link-area static comparison finished"
    write_log(
        "logs/step31_engineering_vs_link_area_static_comparison.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"pass_count={summary['pass_count']}",
            f"max_abs_projected_mass_delta={summary['max_abs_projected_mass_delta']}",
        ],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
