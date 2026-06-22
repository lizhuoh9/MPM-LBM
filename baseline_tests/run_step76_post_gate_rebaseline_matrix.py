import os

import taichi as ti

from step76_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.post_gate_rebaseline_runner import (
    POST_GATE_REBASELINE_FIELDS,
    build_step76_post_gate_rebaseline_matrix,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary = build_step76_post_gate_rebaseline_matrix(ROOT)
    if not summary["post_gate_rebaseline_matrix_pass"]:
        raise RuntimeError(f"Step76 post-gate rebaseline matrix failed: {summary}")
    out_dir = ROOT / "outputs" / "step76_post_gate_rebaseline_matrix"
    write_csv_rows(out_dir / "post_gate_rebaseline_matrix.csv", rows, POST_GATE_REBASELINE_FIELDS)
    write_csv_rows(out_dir / "post_gate_rebaseline_matrix_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "post_gate_rebaseline_matrix.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step76 post-gate rebaseline matrix finished"
    write_log(
        "logs/step76_post_gate_rebaseline_matrix.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"stable_count={summary['stable_count']}",
            f"total_elapsed_seconds={summary['total_elapsed_seconds']}",
            f"slowest_row_name={summary['slowest_row_name']}",
            f"slowest_elapsed_seconds={summary['slowest_elapsed_seconds']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
