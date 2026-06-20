import os

from step30_common import ROOT, fieldnames_from_rows, make_step30_region_sample, write_csv_rows, write_json, write_log
from src.squid_region_quality import evaluate_region_quality


def main():
    os.chdir(ROOT)
    geometry_config, region_config, points, masks, region_rows = make_step30_region_sample()
    rows, summary = evaluate_region_quality(geometry_config, region_config, points, masks, region_rows)
    if not summary["region_quality_pass"]:
        raise RuntimeError(f"Step 30 region quality failed: {summary}")

    out_dir = ROOT / "outputs" / "step30_region_quality"
    write_csv_rows(out_dir / "region_quality.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "region_quality.json", {"rows": rows, "summary": summary})
    marker = "[OK] Step 30 region quality finished"
    write_log(
        "logs/step30_region_quality.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"region_quality_pass={summary['region_quality_pass']}",
        ],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
