import os

from step31_common import ROOT, read_csv_rows, read_json, write_csv_rows, write_json, write_log
from src.squid_region_driver_diagnostics import (
    ALIGNMENT_FIELDS,
    assert_alignment_summary,
    summarize_alignment_rows,
    summarize_region_projection_alignment,
)


def main():
    os.chdir(ROOT)
    projection_rows = read_json("outputs/step31_region_projection_scale/region_projection_scale.json")["rows"]
    driver_rows = read_csv_rows("outputs/step31_static_driver_smoke/static_driver_results.csv")
    rows = summarize_region_projection_alignment(projection_rows, driver_rows)
    summary = summarize_alignment_rows(rows)
    assert_alignment_summary(summary)

    out_dir = ROOT / "outputs" / "step31_region_driver_alignment"
    write_csv_rows(out_dir / "region_driver_alignment.csv", rows, ALIGNMENT_FIELDS)
    write_json(out_dir / "region_driver_alignment.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 31 region driver alignment finished"
    write_log(
        "logs/step31_region_driver_alignment.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"pass_count={summary['pass_count']}",
            f"semantic_overlap_note={summary['semantic_overlap_note']}",
        ],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
