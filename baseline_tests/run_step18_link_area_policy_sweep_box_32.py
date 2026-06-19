import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step16_common import load_driver_config, run_driver_case  # noqa: E402
from baseline_tests.step18_common import POLICIES, config_with, policy_sweep_row, write_policy_outputs  # noqa: E402


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step18_link_area_policy_sweep_box_32")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 18 link-area policy sweep box 32")
    t0 = time.time()
    base_config = load_driver_config(ROOT, "configs/step18_link_area_policy_sweep_box_32.json")
    rows = []
    for policy in POLICIES:
        case_out_dir = os.path.join(out_dir, policy)
        config = config_with(base_config, link_area_policy=policy)
        result = run_driver_case(config, case_out_dir)
        row = policy_sweep_row(result, policy)
        rows.append(row)
        print(
            f"policy={policy}, stable={row['stable']}, area_scale={float(row['area_scale_final']):.9e}, "
            f"rho_min={float(row['rho_min']):.9e}, rho_max={float(row['rho_max']):.9e}, "
            f"lbm_max_v={float(row['lbm_max_v']):.9e}, mpm_min_J={float(row['mpm_min_J']):.9e}, "
            f"bb_link_count={row['bb_link_count']}, cell_force_max_norm={float(row['cell_force_max_norm']):.9e}"
        )

    write_policy_outputs(rows, out_dir)
    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 18 link-area policy sweep box 32 finished")


if __name__ == "__main__":
    main()
