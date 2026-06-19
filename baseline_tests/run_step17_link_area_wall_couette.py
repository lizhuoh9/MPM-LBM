import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step17_common import (  # noqa: E402
    area_policy_rows,
    elapsed_label,
    run_prescribed_wall_case,
    write_area_policy_outputs,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step17_link_area_wall_couette")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 17 link-area wall Couette")
    print("scope=diagnostic proxy policies, not final surface-area reconstruction")
    t0 = time.time()
    lbm = run_prescribed_wall_case(ROOT, out_dir, n_steps=1000, target_u_lbm_x=0.03)
    rows = area_policy_rows(lbm, case="link_area_wall_couette")
    write_area_policy_outputs(
        rows,
        os.path.join(out_dir, "area_policy_comparison.csv"),
        os.path.join(out_dir, "area_policy_comparison.npz"),
    )

    for row in rows:
        print(
            f"policy={row['policy']}, total_link_count={row['total_link_count']}, "
            f"axis_link_count={row['axis_link_count']}, "
            f"face_diagonal_link_count={row['face_diagonal_link_count']}, "
            f"area_proxy_total={float(row['area_proxy_total']):.9e}, "
            f"area_weighted_fluid_impulse_x={float(row['area_weighted_fluid_impulse_x']):.9e}, "
            f"area_weighted_solid_force_x={float(row['area_weighted_solid_force_x']):.9e}, "
            f"rho_min={float(row['rho_min']):.9e}, rho_max={float(row['rho_max']):.9e}, "
            f"lbm_max_v={float(row['lbm_max_v']):.9e}"
        )

    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 17 link-area wall Couette finished")


if __name__ == "__main__":
    main()
