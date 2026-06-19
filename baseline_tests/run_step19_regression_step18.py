import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step19_common import (  # noqa: E402
    STEP19_SUMMARY_FIELDS,
    assert_step19_stable,
    config_with,
    load_driver_config,
    print_step19_summary,
    run_driver_with_link_area_timeseries,
    summarize_step19_case,
    write_step19_rows_csv_npz,
)
from src import FSIDriverConfig  # noqa: E402


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step19_regression_step18")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 19 Step 18 regression")
    t0 = time.time()
    default_config = FSIDriverConfig(coupling_mode="moving_boundary")
    if default_config.reaction_transfer_mode != "engineering":
        raise RuntimeError("default reaction_transfer_mode must remain engineering")

    cases = [
        (
            "step18_sanity_regression",
            load_driver_config(ROOT, "configs/step18_link_area_transfer_sanity_32.json"),
            "link_area_experimental",
        ),
        (
            "step18_box_48_experimental_regression",
            config_with(
                load_driver_config(ROOT, "configs/step18_link_area_transfer_box_48.json"),
                n_lbm_steps=10,
                output_interval=10,
                write_vtk=False,
                write_particles=False,
            ),
            "link_area_experimental",
        ),
        (
            "engineering_default_regression",
            config_with(
                default_config,
                n_lbm_steps=5,
                mpm_substeps_per_lbm_step=5,
                target_u_lbm=(0.005, 0.0, 0.0),
                mb_force_cap_norm=1.0e-5,
                output_interval=5,
                write_vtk=False,
                write_particles=False,
            ),
            "engineering",
        ),
    ]
    rows = []
    for case, config, transfer_mode in cases:
        case_out_dir = os.path.join(out_dir, case)
        result = run_driver_with_link_area_timeseries(config, case_out_dir)
        summary = summarize_step19_case(
            result,
            case=case,
            transfer_mode=transfer_mode,
            notes="Step 19 Step 18 regression",
        )
        assert_step19_stable(summary, require_link_area=transfer_mode == "link_area_experimental")
        rows.append(summary)
        print_step19_summary(case, summary)

    write_step19_rows_csv_npz(
        rows,
        os.path.join(out_dir, "regression_results.csv"),
        os.path.join(out_dir, "regression_results.npz"),
        STEP19_SUMMARY_FIELDS,
    )
    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 19 Step 18 regression finished")


if __name__ == "__main__":
    main()
