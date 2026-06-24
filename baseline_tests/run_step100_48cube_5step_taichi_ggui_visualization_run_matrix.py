import os

import taichi as ti

from step100_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step100_48cube_5step_taichi_ggui_visualization_run_runner import (
    build_step100_48cube_5step_taichi_ggui_visualization_run_matrix,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    run_named_audit(
        build_step100_48cube_5step_taichi_ggui_visualization_run_matrix,
        "outputs/step100_48cube_5step_taichi_ggui_visualization_run_matrix",
        "logs/step100_48cube_5step_taichi_ggui_visualization_run_matrix.log",
        "step100_48cube_5step_taichi_ggui_visualization_run_matrix_pass",
        "[OK] Step100 48cube 5-step Taichi GGUI visualization run matrix finished",
        "48cube_5step_taichi_ggui_visualization_run_matrix",
    )


if __name__ == "__main__":
    main()
