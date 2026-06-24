import os

import taichi as ti

from step94_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step94_taichi_ggui_visualization_smoke_runner import (
    build_step94_taichi_ggui_visualization_smoke_matrix,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    run_named_audit(
        build_step94_taichi_ggui_visualization_smoke_matrix,
        "outputs/step94_taichi_ggui_visualization_smoke_matrix",
        "logs/step94_taichi_ggui_visualization_smoke_matrix.log",
        "step94_taichi_ggui_visualization_smoke_matrix_pass",
        "[OK] Step94 Taichi GGUI visualization smoke matrix finished",
        "taichi_ggui_visualization_smoke_matrix",
    )


if __name__ == "__main__":
    main()
