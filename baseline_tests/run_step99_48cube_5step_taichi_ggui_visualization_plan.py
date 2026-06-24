import os

from step99_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step99_48cube_5step_taichi_ggui_visualization_plan import (
    build_step99_48cube_5step_taichi_ggui_visualization_plan,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step99_48cube_5step_taichi_ggui_visualization_plan,
        "outputs/step99_48cube_5step_taichi_ggui_visualization_plan",
        "logs/step99_48cube_5step_taichi_ggui_visualization_plan.log",
        "step99_48cube_5step_taichi_ggui_visualization_plan_pass",
        "[OK] Step99 48cube 5-step Taichi GGUI visualization plan finished",
        "48cube_5step_taichi_ggui_visualization_plan",
    )


if __name__ == "__main__":
    main()
