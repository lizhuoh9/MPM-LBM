import os

from step101_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step101_48cube_10step_taichi_ggui_visualization_plan import (
    build_step101_48cube_10step_taichi_ggui_visualization_plan,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step101_48cube_10step_taichi_ggui_visualization_plan,
        "outputs/step101_48cube_10step_taichi_ggui_visualization_plan",
        "logs/step101_48cube_10step_taichi_ggui_visualization_plan.log",
        "step101_48cube_10step_taichi_ggui_visualization_plan_pass",
        "[OK] Step101 48cube 10-step Taichi GGUI visualization plan finished",
        "48cube_10step_taichi_ggui_visualization_plan",
    )


if __name__ == "__main__":
    main()
