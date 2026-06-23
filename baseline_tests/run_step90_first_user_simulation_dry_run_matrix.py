import os

import taichi as ti

from step90_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step90_first_user_simulation_dry_run_runner import (
    build_step90_first_user_simulation_dry_run_matrix,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    run_named_audit(
        build_step90_first_user_simulation_dry_run_matrix,
        "outputs/step90_first_user_simulation_dry_run_matrix",
        "logs/step90_first_user_simulation_dry_run_matrix.log",
        "step90_first_user_simulation_dry_run_matrix_pass",
        "[OK] Step90 first user simulation dry run matrix finished",
        "first_user_simulation_dry_run_matrix",
    )


if __name__ == "__main__":
    main()
