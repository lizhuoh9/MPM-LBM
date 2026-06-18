import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step14_common import (  # noqa: E402
    elapsed_label,
    print_row,
    run_config,
    validate_rows,
    write_result_table,
)


CONFIGS = [
    "configs/step14_scale_48_none.json",
    "configs/step14_scale_48_penalty.json",
    "configs/step14_scale_48_moving_boundary.json",
]


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step14_scale_box_48")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 14 48^3 box scale validation")
    t0 = time.time()
    rows = []
    for config_path in CONFIGS:
        mode = os.path.splitext(os.path.basename(config_path))[0].replace("step14_scale_48_", "")
        row = run_config(
            ROOT,
            config_path,
            os.path.join(out_dir, mode),
            notes="48^3 box engineering scale baseline; not production benchmark",
        )
        rows.append(row)
        print_row("box_48", row)

    validate_rows(
        rows,
        required_modes=["none", "penalty", "moving_boundary"],
        expected_grid=48,
        expected_particles_by_mode={"none": 13824, "penalty": 13824, "moving_boundary": 13824},
    )
    write_result_table(
        rows,
        os.path.join(out_dir, "box_48_results.csv"),
        os.path.join(out_dir, "box_48_results.npz"),
    )

    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 14 48^3 box scale validation finished")


if __name__ == "__main__":
    main()
