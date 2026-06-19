import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step17_common import elapsed_label, print_link_summary, run_link_budget_case  # noqa: E402


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step17_squid_proxy_48_link_budget")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 17 squid proxy 48 link budget")
    print("scope=squid_proxy is procedural and not real squid validation")
    t0 = time.time()
    summary = run_link_budget_case(
        ROOT,
        "configs/step17_link_area_squid_proxy_48.json",
        out_dir,
        case="squid_proxy_48_link_budget",
        notes="48^3 procedural squid_proxy link-area proxy accounting; not real squid validation",
    )
    print_link_summary("squid_proxy_48_link_budget", summary)
    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 17 squid proxy 48 link budget finished")


if __name__ == "__main__":
    main()
