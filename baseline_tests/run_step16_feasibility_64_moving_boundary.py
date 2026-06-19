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
    write_summary_csv,
    write_summary_npz,
)


CONFIG_PATH = "configs/step16_feasibility_64_moving_boundary_box.json"
CASE = "feasibility_64_moving_boundary"


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step16_feasibility_64_moving_boundary")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 16 64^3 moving_boundary feasibility")
    print("scope=64^3 moving_boundary feasibility; not full 64^3 validation")
    t0 = time.time()
    config = load_driver_config(ROOT, CONFIG_PATH)
    result = run_driver_case(config, out_dir)
    summary = summarize_driver_result(
        result,
        CASE,
        notes="64^3 moving_boundary feasibility baseline; not full validation",
    )

    if int(summary["completed_lbm_steps"]) < 5:
        raise RuntimeError("64^3 moving_boundary feasibility did not complete 5 LBM steps")
    if int(summary["total_mpm_substeps"]) < 25:
        raise RuntimeError("64^3 moving_boundary feasibility did not complete 25 MPM substeps")
    assert_long_run_stable(summary, require_moving_boundary=True)

    write_long_run_summary(summary, os.path.join(out_dir, "long_run_summary.json"))
    write_summary_csv([summary], os.path.join(out_dir, "box_64_moving_boundary_results.csv"))
    write_summary_npz([summary], os.path.join(out_dir, "box_64_moving_boundary_results.npz"))
    print_summary("feasibility_64_moving_boundary", summary)
    print("The 64^3 moving_boundary row is a feasibility baseline.")
    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 16 64^3 moving_boundary feasibility finished")


if __name__ == "__main__":
    main()
