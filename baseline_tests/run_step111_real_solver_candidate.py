import os

import taichi as ti

from step110_common import ROOT
from src.mpm_lbm.evidence.step111_common import write_log
from src.mpm_lbm.evidence.step111_real_solver_candidate_runner import build_step111_real_solver_candidate


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary = build_step111_real_solver_candidate(ROOT)
    if not summary["real_solver_candidate_pass"]:
        raise RuntimeError(f"Step111 real solver candidate failed: {summary}")
    row = rows[0]
    marker = "[OK] Step111 real solver candidate finished"
    write_log(
        ROOT,
        "logs/step111_real_solver_candidate.log",
        [
            marker,
            f"completed_official_fsi_steps={row['completed_official_fsi_steps']}",
            f"completed_lbm_substeps={row['completed_lbm_substeps']}",
            f"peak_nearest_monitor_m={row['peak_nearest_monitor_m']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
