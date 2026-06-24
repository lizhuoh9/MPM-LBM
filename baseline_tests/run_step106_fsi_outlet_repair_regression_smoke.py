import os

import taichi as ti

from step106_common import ROOT, write_log
from src.mpm_lbm.evidence.step106_outlet_boundary_flow_propagation_runner import (
    build_step106_fsi_outlet_repair_regression,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary = build_step106_fsi_outlet_repair_regression(ROOT)
    if not summary["step106_fsi_outlet_repair_regression_pass"]:
        raise RuntimeError(f"Step106 FSI outlet repair regression failed: {summary}")
    marker = "[OK] Step106 FSI outlet repair regression smoke finished"
    write_log(
        "logs/step106_fsi_outlet_repair_regression_smoke.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"completed_lbm_steps={rows[0]['completed_lbm_steps']}",
            f"outlet_plane_mean_ux_final={rows[0]['outlet_plane_mean_ux_final']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
