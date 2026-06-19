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
    load_json,
    print_step19_summary,
    run_driver_with_link_area_timeseries,
    summarize_step19_case,
    write_step19_rows_csv_npz,
)
from src import FSIDriverConfig  # noqa: E402


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step19_compare_48_long_engineering_vs_link_area")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 19 48^3 long engineering vs link-area comparison")
    t0 = time.time()
    data = load_json(os.path.join(ROOT, "configs", "step19_compare_48_long_engineering_vs_link_area.json"))
    cases = [
        ("box_48", FSIDriverConfig(**data["box_48"]), 30, 300),
        ("squid_proxy_48", FSIDriverConfig(**data["squid_proxy_48"]), 20, 200),
    ]
    rows = []
    for case, base_config, min_steps, min_substeps in cases:
        variants = [
            ("engineering", base_config),
            (
                "link_area_experimental",
                config_with(
                    base_config,
                    reaction_transfer_mode="link_area_experimental",
                    link_area_policy="inverse_length",
                ),
            ),
        ]
        for transfer_mode, config in variants:
            case_out_dir = os.path.join(out_dir, f"{case}_{transfer_mode}")
            result = run_driver_with_link_area_timeseries(config, case_out_dir)
            summary = summarize_step19_case(
                result,
                case=case,
                transfer_mode=transfer_mode,
                notes="Step 19 48^3 long engineering vs link-area comparison",
            )
            assert int(summary["completed_lbm_steps"]) >= min_steps
            assert int(summary["total_mpm_substeps"]) >= min_substeps
            assert_step19_stable(summary, require_link_area=transfer_mode == "link_area_experimental")
            rows.append(summary)
            print_step19_summary(f"{case}_{transfer_mode}", summary)

    write_step19_rows_csv_npz(
        rows,
        os.path.join(out_dir, "comparison_48_long.csv"),
        os.path.join(out_dir, "comparison_48_long.npz"),
        STEP19_SUMMARY_FIELDS,
    )
    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 19 48^3 long engineering vs link-area comparison finished")


if __name__ == "__main__":
    main()
