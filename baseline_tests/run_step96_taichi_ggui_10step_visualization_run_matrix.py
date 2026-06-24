import os

import taichi as ti

from step96_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step96_taichi_ggui_10step_visualization_run_runner import (
    build_step96_taichi_ggui_10step_visualization_run_matrix,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    run_named_audit(
        build_step96_taichi_ggui_10step_visualization_run_matrix,
        "outputs/step96_taichi_ggui_10step_visualization_run_matrix",
        "logs/step96_taichi_ggui_10step_visualization_run_matrix.log",
        "step96_taichi_ggui_10step_visualization_run_matrix_pass",
        "[OK] Step96 Taichi GGUI 10-step visualization run matrix finished",
        "taichi_ggui_10step_visualization_run_matrix",
    )


if __name__ == "__main__":
    main()
