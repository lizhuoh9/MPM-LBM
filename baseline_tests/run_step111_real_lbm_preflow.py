import os

import taichi as ti

from step110_common import ROOT
from src.mpm_lbm.evidence.step111_common import write_log
from src.mpm_lbm.evidence.step111_real_lbm_preflow_runner import build_step111_real_lbm_preflow


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary, _timeseries = build_step111_real_lbm_preflow(ROOT)
    if not summary["preflow_pass"]:
        raise RuntimeError(f"Step111 real LBM preflow failed: {summary}")
    row = rows[0]
    marker = "[OK] Step111 real LBM preflow finished"
    write_log(
        ROOT,
        "logs/step111_real_lbm_preflow.log",
        [
            marker,
            f"completed_lbm_substeps={row['completed_lbm_substeps']}",
            f"outlet_plane_mean_ux_final={row['outlet_plane_mean_ux_final']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
