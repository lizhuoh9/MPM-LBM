import os

import taichi as ti

from step98_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step98_48cube_taichi_ggui_visualization_smoke_runner import (
    build_step98_48cube_taichi_ggui_visualization_smoke_matrix,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    run_named_audit(
        build_step98_48cube_taichi_ggui_visualization_smoke_matrix,
        "outputs/step98_48cube_taichi_ggui_visualization_smoke_matrix",
        "logs/step98_48cube_taichi_ggui_visualization_smoke_matrix.log",
        "step98_48cube_taichi_ggui_visualization_smoke_matrix_pass",
        "[OK] Step98 48cube Taichi GGUI visualization smoke matrix finished",
        "48cube_taichi_ggui_visualization_smoke_matrix",
    )


if __name__ == "__main__":
    main()
