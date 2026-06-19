import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step16_common import (  # noqa: E402
    assert_long_run_stable,
    elapsed_label,
    load_driver_config,
    print_summary,
    run_driver_case,
    summarize_driver_result,
    write_long_run_summary,
)


CONFIG_PATH = "configs/step16_long_box_48_moving_boundary.json"
CASE = "long_box_48_moving_boundary"


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step16_long_box_48_moving_boundary")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 16 48^3 box moving_boundary long-run")
    t0 = time.time()
    config = load_driver_config(ROOT, CONFIG_PATH)
    result = run_driver_case(config, out_dir)
    summary = summarize_driver_result(
        result,
        CASE,
        notes="48^3 box moving_boundary long-run validation; no new FSI physics",
    )

    if int(summary["completed_lbm_steps"]) < 50:
        raise RuntimeError("48^3 box long-run did not complete 50 LBM steps")
    if int(summary["total_mpm_substeps"]) < 500:
        raise RuntimeError("48^3 box long-run did not complete 500 MPM substeps")
    assert_long_run_stable(summary, require_moving_boundary=True)

    write_long_run_summary(summary, os.path.join(out_dir, "long_run_summary.json"))
    print_summary("long_box_48", summary)
    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 16 48^3 box moving_boundary long-run finished")


if __name__ == "__main__":
    main()
