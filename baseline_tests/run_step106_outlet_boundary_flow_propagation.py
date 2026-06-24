import os

import taichi as ti

from step106_common import ROOT, write_log
from src.mpm_lbm.evidence.step106_outlet_boundary_flow_propagation_runner import (
    build_step106_outlet_boundary_flow,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary, timeseries, semantics = build_step106_outlet_boundary_flow(ROOT)
    if not summary["duct_only_outlet_boundary_flow_pass"]:
        raise RuntimeError(f"Step106 duct-only outlet boundary flow failed: {summary}")
    if semantics["pressure_outlet_uses_boundary_self_velocity"]:
        raise RuntimeError(f"Step106 boundary semantics still use boundary-self velocity: {semantics}")
    marker = "[OK] Step106 duct-only outlet boundary flow propagation finished"
    write_log(
        "logs/step106_outlet_boundary_flow_propagation.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"timeseries_rows={len(timeseries)}",
            f"outlet_plane_mean_ux_final={rows[0]['outlet_plane_mean_ux_final']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
