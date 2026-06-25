import os

import taichi as ti

from step110_common import ROOT
from src.mpm_lbm.evidence.step112_common import write_log
from src.mpm_lbm.evidence.step112_real_candidate_matrix_runner import build_step112_real_candidate_matrix


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary = build_step112_real_candidate_matrix(ROOT)
    if not summary["candidate_matrix_pass"]:
        raise RuntimeError(f"Step112 real candidate matrix failed: {summary}")
    marker = "[OK] Step112 real candidate matrix finished"
    write_log(
        ROOT,
        "logs/step112_real_candidate_matrix.log",
        [
            marker,
            f"best_candidate={summary['best_candidate_row_name']}",
            f"hard_gate_pass={summary['hard_gate_pass']}",
            f"best_normalized_rms_error={summary['best_normalized_rms_error']}",
            f"best_shape_correlation={summary['best_shape_correlation']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
