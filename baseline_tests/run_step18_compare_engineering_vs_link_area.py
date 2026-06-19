import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step16_common import load_driver_config, run_driver_case  # noqa: E402
from baseline_tests.step18_common import config_with, print_transfer_summary, summarize_transfer_result, write_comparison_outputs  # noqa: E402


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step18_compare_engineering_vs_link_area")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 18 engineering vs link-area comparison")
    t0 = time.time()
    cases = [
        ("box_48", "configs/step18_compare_engineering_vs_link_area_box_48.json"),
        ("squid_proxy_48", "configs/step18_compare_engineering_vs_link_area_squid_proxy_48.json"),
    ]
    rows = []
    for case, config_path in cases:
        engineering_config = load_driver_config(ROOT, config_path)
        link_area_config = config_with(
            engineering_config,
            reaction_transfer_mode="link_area_experimental",
            link_area_policy="inverse_length",
        )
        variants = [
            ("engineering", engineering_config),
            ("link_area_experimental", link_area_config),
        ]
        for transfer_mode, config in variants:
            case_out_dir = os.path.join(out_dir, f"{case}_{transfer_mode}")
            result = run_driver_case(config, case_out_dir)
            row = summarize_transfer_result(result, case=case, transfer_mode=transfer_mode)
            rows.append(row)
            print_transfer_summary(f"{case}_{transfer_mode}", row)

    write_comparison_outputs(rows, out_dir)
    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 18 engineering vs link-area comparison finished")


if __name__ == "__main__":
    main()
