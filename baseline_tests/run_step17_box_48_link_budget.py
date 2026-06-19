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

    out_dir = os.path.join(ROOT, "outputs", "step17_box_48_link_budget")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 17 box 48 link budget")
    t0 = time.time()
    summary = run_link_budget_case(
        ROOT,
        "configs/step17_link_area_box_48.json",
        out_dir,
        case="box_48_link_budget",
        notes="48^3 box moving_boundary link-area proxy accounting; diagnostic-only",
    )
    print_link_summary("box_48_link_budget", summary)
    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 17 box 48 link budget finished")


if __name__ == "__main__":
    main()
