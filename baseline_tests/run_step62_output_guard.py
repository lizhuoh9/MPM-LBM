import os

from step62_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.canonical_driver_32_duration_output_guard import (
    build_canonical_driver_32_duration_output_guard,
)


FIELDS = ["path", "size_bytes", "extension", "forbidden", "pass"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_canonical_driver_32_duration_output_guard(ROOT)
    if not summary["output_guard_pass"]:
        raise RuntimeError(f"Step 62 output guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step62_output_guard"
    write_csv_rows(out_dir / "output_guard.csv", rows, FIELDS)
    write_csv_rows(out_dir / "output_guard_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "output_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 62 output guard finished"
    write_log("logs/step62_output_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
