import os

from step99_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step99_48cube_5step_taichi_ggui_visualization_guard import (
    build_step99_48cube_5step_taichi_ggui_visualization_guard,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step99_48cube_5step_taichi_ggui_visualization_guard,
        "outputs/step99_48cube_5step_taichi_ggui_visualization_guard",
        "logs/step99_48cube_5step_taichi_ggui_visualization_guard.log",
        "step99_48cube_5step_taichi_ggui_visualization_guard_pass",
        "[OK] Step99 48cube 5-step Taichi GGUI visualization guard finished",
        "48cube_5step_taichi_ggui_visualization_guard",
    )


if __name__ == "__main__":
    main()
