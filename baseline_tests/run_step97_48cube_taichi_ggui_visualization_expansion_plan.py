import os

from step97_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step97_48cube_taichi_ggui_visualization_expansion_plan import (
    build_step97_48cube_taichi_ggui_visualization_expansion_plan,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step97_48cube_taichi_ggui_visualization_expansion_plan,
        "outputs/step97_48cube_taichi_ggui_visualization_expansion_plan",
        "logs/step97_48cube_taichi_ggui_visualization_expansion_plan.log",
        "step97_48cube_taichi_ggui_visualization_expansion_plan_pass",
        "[OK] Step97 48cube Taichi GGUI visualization expansion plan finished",
        "48cube_taichi_ggui_visualization_expansion_plan",
    )


if __name__ == "__main__":
    main()
