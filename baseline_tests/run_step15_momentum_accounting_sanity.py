import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step15_common import (  # noqa: E402
    ACCOUNTING_FIELDS,
    config_with,
    elapsed_label,
    load_driver_config,
    run_accounted_moving_boundary_case,
    save_rows_npz,
    validate_accounting_sanity,
)
from src.run_utils import save_csv_rows  # noqa: E402


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step15_momentum_accounting")
    os.makedirs(out_dir, exist_ok=True)

    base = load_driver_config(ROOT, "configs/step15_mb_calibration_box_32.json")
    config = config_with(base, n_lbm_steps=10, write_vtk=False, write_particles=False)

    csv_path = os.path.join(out_dir, "accounting_timeseries.csv")
    npz_path = os.path.join(out_dir, "accounting_timeseries.npz")

    print("Step 15 moving-boundary momentum accounting sanity")
    t0 = time.time()
    result = run_accounted_moving_boundary_case(
        config,
        os.path.join(out_dir, "case"),
        accounting_csv=csv_path,
        accounting_npz=npz_path,
    )
    rows = result["rows"]
    validate_accounting_sanity(rows)

    save_csv_rows(rows, csv_path, fieldnames=ACCOUNTING_FIELDS)
    save_rows_npz(rows, npz_path, ACCOUNTING_FIELDS)

    first = rows[0]
    final = rows[-1]
    print(
        "first_step "
        f"bb_link_count={first['bb_link_count']}, "
        f"bb_net_fluid_impulse_x={first['bb_net_fluid_impulse_x']:.9e}, "
        f"bb_net_solid_force_x={first['bb_net_solid_force_x']:.9e}, "
        f"hydro_force_sum_x={first['hydro_force_sum_x']:.9e}, "
        f"net_grid_reaction_force_x={first['net_grid_reaction_force_x']:.9e}"
    )
    print(
        "final_step "
        f"rho_min={final['rho_min']:.9e}, rho_max={final['rho_max']:.9e}, "
        f"lbm_max_v={final['lbm_max_v']:.9e}, mpm_min_J={final['mpm_min_J']:.9e}, "
        f"mpm_max_speed={final['mpm_max_speed']:.9e}, "
        f"solid_momentum_delta_x={final['solid_momentum_delta_x']:.9e}, "
        f"force_sign_consistent={final['force_sign_consistent']}"
    )
    print(f"csv={csv_path}")
    print(f"npz={npz_path}")
    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 15 momentum accounting sanity finished")


if __name__ == "__main__":
    main()
