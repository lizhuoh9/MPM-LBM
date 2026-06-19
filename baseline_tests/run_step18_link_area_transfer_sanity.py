import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step16_common import load_driver_config, run_driver_case  # noqa: E402
from baseline_tests.step18_common import SANITY_FIELDS, sanity_row, save_rows_npz  # noqa: E402
from src.run_utils import save_csv_rows  # noqa: E402


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step18_link_area_transfer_sanity")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 18 link-area transfer sanity")
    t0 = time.time()
    config = load_driver_config(ROOT, "configs/step18_link_area_transfer_sanity_32.json")
    result = run_driver_case(config, out_dir)
    row = sanity_row(result)

    save_csv_rows([row], os.path.join(out_dir, "sanity_results.csv"), fieldnames=SANITY_FIELDS)
    save_rows_npz([row], os.path.join(out_dir, "sanity_results.npz"), SANITY_FIELDS)

    print(
        f"step={row['step']}, area_policy={row['area_policy']}, area_scale={float(row['area_scale']):.9e}, "
        f"raw_area_scale={float(row['raw_area_scale']):.9e}, bb_link_count={row['bb_link_count']}, "
        f"rho_min={float(row['rho_min']):.9e}, rho_max={float(row['rho_max']):.9e}, "
        f"lbm_max_v={float(row['lbm_max_v']):.9e}, mpm_min_J={float(row['mpm_min_J']):.9e}, "
        f"active_reaction_particle_count={row['active_reaction_particle_count']}, "
        f"cell_force_max_norm={float(row['cell_force_max_norm']):.9e}, stable={row['stable']}"
    )
    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 18 link-area transfer sanity finished")


if __name__ == "__main__":
    main()
