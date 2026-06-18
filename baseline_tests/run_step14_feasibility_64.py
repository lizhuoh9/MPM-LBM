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
    "configs/step14_feasibility_64_none.json",
    "configs/step14_feasibility_64_penalty.json",
]


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step14_feasibility_64")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 14 64^3 feasibility")
    print("scope=short none/penalty feasibility, not full 64^3 validation")
    t0 = time.time()
    rows = []
    for config_path in CONFIGS:
        mode = os.path.splitext(os.path.basename(config_path))[0].replace("step14_feasibility_64_", "")
        row = run_config(
            ROOT,
            config_path,
            os.path.join(out_dir, mode),
            notes="64^3 short feasibility check; not full validation",
        )
        rows.append(row)
        print_row("feasibility_64", row)

    validate_rows(
        rows,
        required_modes=["none", "penalty"],
        expected_grid=64,
        expected_particles_by_mode={"none": 32768, "penalty": 32768},
    )
    write_result_table(
        rows,
        os.path.join(out_dir, "feasibility_64_results.csv"),
        os.path.join(out_dir, "feasibility_64_results.npz"),
    )

    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 14 64^3 feasibility finished")


if __name__ == "__main__":
    main()
