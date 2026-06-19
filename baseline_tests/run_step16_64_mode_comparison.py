import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step16_common import (  # noqa: E402
    elapsed_label,
    load_mode_matrix,
    mode_matrix_config,
    print_summary,
    run_driver_case,
    summarize_driver_result,
    validate_mode_rows,
    validate_mode_summary,
    write_summary_csv,
    write_summary_npz,
)


CONFIG_PATH = "configs/step16_compare_64_modes.json"


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step16_64_mode_comparison")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 16 64^3 mode comparison")
    print("scope=none/penalty/moving_boundary short comparison; no new FSI physics")
    matrix = load_mode_matrix(os.path.join(ROOT, CONFIG_PATH))
    t0 = time.time()

    rows = []
    for mode in matrix["modes"]:
        config = mode_matrix_config(matrix, mode)
        result = run_driver_case(config, os.path.join(out_dir, mode))
        row = summarize_driver_result(
            result,
            f"mode_compare_64_{mode}",
            notes="64^3 mode comparison row; not full 64^3 validation",
        )
        validate_mode_summary(row)
        rows.append(row)
        print_summary("mode_compare_64", row)

    validate_mode_rows(rows)
    write_summary_csv(rows, os.path.join(out_dir, "mode_64_results.csv"))
    write_summary_npz(rows, os.path.join(out_dir, "mode_64_results.npz"))

    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 16 64^3 mode comparison finished")


if __name__ == "__main__":
    main()
