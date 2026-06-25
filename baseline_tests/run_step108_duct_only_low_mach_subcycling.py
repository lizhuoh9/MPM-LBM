import os

import taichi as ti

from step108_common import ROOT, write_log
from src.mpm_lbm.evidence.step108_duct_only_low_mach_subcycling_runner import (
    build_step108_duct_only_low_mach_subcycling,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary, _timeseries = build_step108_duct_only_low_mach_subcycling(ROOT)
    if not summary["duct_only_low_mach_subcycling_pass"]:
        raise RuntimeError(f"Step108 duct-only low-Mach subcycling failed: {summary}")
    row = rows[0]
    marker = "[OK] Step108 duct-only low-Mach subcycling finished"
    write_log(
        "logs/step108_duct_only_low_mach_subcycling.log",
        [
            marker,
            f"completed_official_steps={row['completed_official_steps']}",
            f"completed_lbm_substeps={row['completed_lbm_substeps']}",
            f"outlet_plane_mean_ux_final={row['outlet_plane_mean_ux_final']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
