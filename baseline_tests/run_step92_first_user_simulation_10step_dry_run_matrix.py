import os

import taichi as ti

from step92_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step92_first_user_simulation_10step_dry_run_runner import (
    build_step92_first_user_simulation_10step_dry_run_matrix,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    run_named_audit(
        build_step92_first_user_simulation_10step_dry_run_matrix,
        "outputs/step92_first_user_simulation_10step_dry_run_matrix",
        "logs/step92_first_user_simulation_10step_dry_run_matrix.log",
        "step92_first_user_simulation_10step_dry_run_matrix_pass",
        "[OK] Step92 first user simulation 10-step dry run matrix finished",
        "first_user_simulation_10step_dry_run_matrix",
    )


if __name__ == "__main__":
    main()
