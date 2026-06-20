import os

from step30_common import ROOT, fieldnames_from_rows, make_step30_region_sample, write_csv_rows, write_json, write_log
from src.squid_region_quality import overlap_matrix_rows, summarize_overlap_diagnostics


def main():
    os.chdir(ROOT)
    _geometry_config, region_config, _points, masks, region_rows = make_step30_region_sample()
    rows = overlap_matrix_rows(masks, region_config)
    summary = summarize_overlap_diagnostics(rows, region_rows)
    if not summary["overlap_pass"]:
        raise RuntimeError(f"Step 30 overlap diagnostics failed: {summary}")

    out_dir = ROOT / "outputs" / "step30_region_overlap_diagnostics"
    write_csv_rows(out_dir / "region_overlap_matrix.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "region_overlap_summary.json", summary)
    marker = "[OK] Step 30 region overlap diagnostics finished"
    write_log(
        "logs/step30_region_overlap_diagnostics.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"intentional_overlap_count={summary['intentional_overlap_count']}",
            f"unintended_overlap_count={summary['unintended_overlap_count']}",
        ],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
