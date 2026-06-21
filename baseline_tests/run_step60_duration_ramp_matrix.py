import os

import taichi as ti

from step60_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.canonical_driver_duration_ramp_runner import (
    DURATION_RAMP_FIELDS,
    build_canonical_driver_duration_ramp_matrix,
)


SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary = build_canonical_driver_duration_ramp_matrix(ROOT)
    if not summary["duration_ramp_matrix_pass"]:
        raise RuntimeError(f"Step 60 duration ramp matrix failed: {summary}")
    out_dir = ROOT / "outputs" / "step60_duration_ramp_matrix"
    write_csv_rows(out_dir / "duration_ramp_matrix.csv", rows, DURATION_RAMP_FIELDS)
    write_csv_rows(out_dir / "duration_ramp_matrix_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "duration_ramp_matrix.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 60 duration ramp matrix finished"
    log_lines = [
        marker,
        f"row_count={summary['row_count']}",
        f"stable_count={summary['stable_count']}",
        f"total_elapsed_seconds={summary['total_elapsed_seconds']}",
        f"slowest_row_name={summary['slowest_row_name']}",
        f"slowest_elapsed_seconds={summary['slowest_elapsed_seconds']}",
    ]
    write_log("logs/step60_duration_ramp_matrix.log", log_lines)
    print(marker)


if __name__ == "__main__":
    main()
