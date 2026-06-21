import os

import taichi as ti

from step59_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.canonical_driver_smoke_runner import (
    SMOKE_FIELDS,
    build_canonical_driver_smoke_matrix,
)


SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary = build_canonical_driver_smoke_matrix(ROOT)
    if not summary["canonical_driver_smoke_matrix_pass"]:
        raise RuntimeError(f"Step 59 canonical driver smoke matrix failed: {summary}")
    out_dir = ROOT / "outputs" / "step59_canonical_driver_smoke_matrix"
    write_csv_rows(out_dir / "smoke_matrix.csv", rows, SMOKE_FIELDS)
    write_csv_rows(out_dir / "smoke_matrix_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "smoke_matrix.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 59 canonical driver smoke matrix finished"
    log_lines = [
        marker,
        f"row_count={summary['row_count']}",
        f"stable_count={summary['stable_count']}",
        f"min_completed_lbm_steps={summary['min_completed_lbm_steps']}",
        f"min_total_mpm_substeps={summary['min_total_mpm_substeps']}",
    ]
    write_log("logs/step59_canonical_driver_smoke_matrix.log", log_lines)
    print(marker)


if __name__ == "__main__":
    main()
