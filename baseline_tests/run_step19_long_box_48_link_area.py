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

    out_dir = os.path.join(ROOT, "outputs", "step19_long_box_48_link_area")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 19 48^3 box link-area long-run")
    t0 = time.time()
    config = load_driver_config(ROOT, "configs/step19_long_box_48_link_area.json")
    result = run_driver_with_link_area_timeseries(config, out_dir)
    summary = summarize_step19_case(
        result,
        case="box_48_link_area_long",
        transfer_mode="link_area_experimental",
        notes="Step 19 48^3 box link-area long-run",
    )
    assert int(summary["completed_lbm_steps"]) >= 50
    assert int(summary["total_mpm_substeps"]) >= 500
    assert_step19_stable(summary, require_link_area=True)

    write_step19_summary_json(summary, os.path.join(out_dir, "long_run_summary.json"))
    write_step19_rows_csv_npz(
        [summary],
        os.path.join(out_dir, "box_48_link_area_long_results.csv"),
        os.path.join(out_dir, "box_48_link_area_long_results.npz"),
        STEP19_SUMMARY_FIELDS,
    )
    print_step19_summary("box_48_link_area_long", summary)
    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 19 48^3 box link-area long-run finished")


if __name__ == "__main__":
    main()
