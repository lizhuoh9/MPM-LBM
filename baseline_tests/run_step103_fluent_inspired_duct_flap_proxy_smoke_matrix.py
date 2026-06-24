import os

import taichi as ti

from step103_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step103_fluent_inspired_duct_flap_proxy_runner import (
    build_step103_fluent_inspired_duct_flap_proxy_smoke_matrix,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    run_named_audit(
        build_step103_fluent_inspired_duct_flap_proxy_smoke_matrix,
        "outputs/step103_smoke_matrix",
        "logs/step103_fluent_inspired_duct_flap_proxy_smoke_matrix.log",
        "step103_fluent_inspired_duct_flap_proxy_smoke_matrix_pass",
        "[OK] Step103 Fluent-inspired duct-flap proxy smoke matrix finished",
        "fluent_inspired_duct_flap_proxy_smoke_matrix",
    )


if __name__ == "__main__":
    main()
