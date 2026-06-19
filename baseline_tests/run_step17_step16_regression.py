import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step16_common import (  # noqa: E402
    assert_long_run_stable,
    load_driver_config,
    run_driver_case,
    summarize_driver_result,
)
from baseline_tests.step17_common import config_with, elapsed_label, write_regression_outputs  # noqa: E402


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step17_step16_regression")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 17 Step 16 regression")
    print("scope=threshold regression after adding diagnostic-only direction accumulators")
    t0 = time.time()

    box48 = config_with(
        load_driver_config(ROOT, "configs/step16_long_box_48_moving_boundary.json"),
        n_lbm_steps=10,
        output_interval=10,
        write_vtk=False,
        write_particles=False,
    )
    box64 = config_with(
        load_driver_config(ROOT, "configs/step16_feasibility_64_moving_boundary_box.json"),
        n_lbm_steps=5,
        output_interval=5,
        write_vtk=False,
        write_particles=False,
    )

    cases = [
        ("step16_box_48_short", box48, os.path.join(out_dir, "step16_box_48_short")),
        ("step16_box_64_feasibility", box64, os.path.join(out_dir, "step16_box_64_feasibility")),
    ]
    rows = []
    for case, config, case_out_dir in cases:
        result = run_driver_case(config, case_out_dir)
        row = summarize_driver_result(
            result,
            case,
            notes="Step 16 threshold regression after Step 17 diagnostics",
        )
        assert_long_run_stable(row, require_moving_boundary=True)
        rows.append(row)
        print(
            f"case={case}, n_grid={row['n_grid']}, completed_lbm_steps={row['completed_lbm_steps']}, "
            f"total_mpm_substeps={row['total_mpm_substeps']}, rho_min={float(row['rho_min_global']):.9e}, "
            f"rho_max={float(row['rho_max_global']):.9e}, lbm_max_v={float(row['lbm_max_v_global']):.9e}, "
            f"mpm_min_J={float(row['mpm_min_J_global']):.9e}, bb_link_count_min={row['bb_link_count_min']}, "
            f"cell_force_max_norm={float(row['cell_force_max_norm']):.9e}, stable={row['stable']}"
        )

    write_regression_outputs(
        rows,
        os.path.join(out_dir, "regression_results.csv"),
        os.path.join(out_dir, "regression_results.npz"),
    )

    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 17 Step 16 regression finished")


if __name__ == "__main__":
    main()
