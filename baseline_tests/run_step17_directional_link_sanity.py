import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step17_common import (  # noqa: E402
    directional_sanity_row,
    elapsed_label,
    run_prescribed_wall_case,
    write_directional_sanity_outputs,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step17_directional_link_sanity")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 17 directional link sanity")
    t0 = time.time()
    lbm = run_prescribed_wall_case(ROOT, out_dir, n_steps=100, target_u_lbm_x=0.02)
    row = directional_sanity_row(lbm, case="directional_link_sanity")
    write_directional_sanity_outputs(
        lbm,
        row,
        os.path.join(out_dir, "directional_stats.csv"),
        os.path.join(out_dir, "directional_stats.npz"),
    )

    print(
        f"bb_link_count={row['bb_link_count']}, sum_link_count_by_dir={row['sum_link_count_by_dir']}, "
        f"scalar_vs_directional_impulse_error_x={row['scalar_vs_directional_impulse_error_x']:.9e}, "
        f"bb_net_fluid_impulse_x={row['bb_net_fluid_impulse_x']:.9e}, "
        f"bb_net_solid_force_x={row['bb_net_solid_force_x']:.9e}, "
        f"rho_min={row['rho_min']:.9e}, rho_max={row['rho_max']:.9e}, "
        f"lbm_max_v={row['lbm_max_v']:.9e}"
    )
    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 17 directional link sanity finished")


if __name__ == "__main__":
    main()
