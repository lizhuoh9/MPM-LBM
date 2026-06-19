import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step18_common import regression_rows, write_regression_outputs  # noqa: E402


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step18_regression_existing_modes")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 18 existing mode regression")
    t0 = time.time()
    rows = regression_rows(ROOT, out_dir)
    write_regression_outputs(rows, out_dir)
    for row in rows:
        print(
            f"case={row['case']}, mode={row['mode']}, n_grid={row['n_grid']}, "
            f"completed_lbm_steps={row['completed_lbm_steps']}, total_mpm_substeps={row['total_mpm_substeps']}, "
            f"rho_min={float(row['rho_min_global']):.9e}, rho_max={float(row['rho_max_global']):.9e}, "
            f"lbm_max_v={float(row['lbm_max_v_global']):.9e}, mpm_min_J={float(row['mpm_min_J_global']):.9e}, "
            f"bb_link_count_min={row['bb_link_count_min']}, cell_force_max_norm={float(row['cell_force_max_norm']):.9e}, "
            f"stable={row['stable']}"
        )
    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 18 existing mode regression finished")


if __name__ == "__main__":
    main()
