import os

from step95_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step95_taichi_ggui_10step_visualization_plan import (
    build_step95_taichi_ggui_10step_visualization_plan,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step95_taichi_ggui_10step_visualization_plan,
        "outputs/step95_taichi_ggui_10step_visualization_plan",
        "logs/step95_taichi_ggui_10step_visualization_plan.log",
        "step95_taichi_ggui_10step_visualization_plan_pass",
        "[OK] Step95 Taichi GGUI 10-step visualization plan finished",
        "taichi_ggui_10step_visualization_plan",
    )


if __name__ == "__main__":
    main()
