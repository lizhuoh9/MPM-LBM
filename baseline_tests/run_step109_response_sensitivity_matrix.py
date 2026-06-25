import os

import taichi as ti

from step109_common import ROOT, write_log
from src.mpm_lbm.evidence.step109_response_sensitivity_matrix_runner import (
    build_step109_response_sensitivity_matrix,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary = build_step109_response_sensitivity_matrix(ROOT)
    if not summary["response_matrix_pass"]:
        raise RuntimeError(f"Step109 response matrix failed: {summary}")
    marker = "[OK] Step109 response sensitivity matrix finished"
    write_log(
        "logs/step109_response_sensitivity_matrix.log",
        [
            marker,
            f"row_count={summary['response_matrix_row_count']}",
            f"successful_rows={summary['successful_response_matrix_rows']}",
            f"best_candidate={summary['best_candidate_row_name']}",
            f"best_peak_solver_m={summary['best_peak_solver_m']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
