import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step19_common import (  # noqa: E402
    STEP19_SUMMARY_FIELDS,
    assert_step19_stable,
    load_driver_config,
    print_step19_summary,
    run_driver_with_link_area_timeseries,
    summarize_step19_case,
    write_step19_rows_csv_npz,
    write_step19_summary_json,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step19_feasibility_64_link_area")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 19 64^3 link-area feasibility")
    t0 = time.time()
    config = load_driver_config(ROOT, "configs/step19_feasibility_64_link_area_box.json")
    result = run_driver_with_link_area_timeseries(config, out_dir)
    summary = summarize_step19_case(
        result,
        case="box_64_link_area_feasibility",
        transfer_mode="link_area_experimental",
        notes="Step 19 conservative 64^3 link-area feasibility",
    )
    assert int(summary["n_grid"]) == 64
    assert int(summary["n_particles"]) == 32768
    assert int(summary["completed_lbm_steps"]) >= 5
    assert int(summary["total_mpm_substeps"]) >= 25
    assert_step19_stable(summary, require_link_area=True)

    write_step19_summary_json(summary, os.path.join(out_dir, "long_run_summary.json"))
    write_step19_rows_csv_npz(
        [summary],
        os.path.join(out_dir, "box_64_link_area_results.csv"),
        os.path.join(out_dir, "box_64_link_area_results.npz"),
        STEP19_SUMMARY_FIELDS,
    )
    print_step19_summary("box_64_link_area_feasibility", summary)
    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 19 64^3 link-area feasibility finished")


if __name__ == "__main__":
    main()
