import os

import taichi as ti

from step108_common import ROOT, write_log
from src.mpm_lbm.evidence.step108_low_mach_fsi_candidate_runner import build_step108_low_mach_fsi_candidate


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary = build_step108_low_mach_fsi_candidate(ROOT)
    if not summary["step108_low_mach_fsi_candidate_pass"]:
        raise RuntimeError(f"Step108 low-Mach FSI candidate failed: {summary}")
    row = rows[0]
    marker = "[OK] Step108 low-Mach FSI candidate finished"
    write_log(
        "logs/step108_low_mach_fsi_candidate.log",
        [
            marker,
            f"completed_official_fsi_steps={row['completed_official_fsi_steps']}",
            f"completed_lbm_substeps={row['completed_lbm_substeps']}",
            f"solver_curve_time_end_s={row['solver_curve_time_end_s']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
