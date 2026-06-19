import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step18_common import print_transfer_summary, run_transfer_case, write_single_transfer_outputs  # noqa: E402


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step18_link_area_transfer_squid_proxy_48")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 18 link-area transfer squid proxy 48")
    print("scope=squid_proxy is procedural and not real squid validation")
    t0 = time.time()
    _, row = run_transfer_case(
        ROOT,
        "configs/step18_link_area_transfer_squid_proxy_48.json",
        out_dir,
        case="squid_proxy_48",
    )
    write_single_transfer_outputs(
        row,
        out_dir,
        "squid_proxy_48_link_area_results.csv",
        "squid_proxy_48_link_area_results.npz",
    )
    print_transfer_summary("squid_proxy_48", row)
    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 18 link-area transfer squid proxy 48 finished")


if __name__ == "__main__":
    main()
