import os

from step101_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step101_48cube_10step_taichi_ggui_visualization_guard import (
    build_step101_48cube_10step_taichi_ggui_visualization_guard,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step101_48cube_10step_taichi_ggui_visualization_guard,
        "outputs/step101_48cube_10step_taichi_ggui_visualization_guard",
        "logs/step101_48cube_10step_taichi_ggui_visualization_guard.log",
        "step101_48cube_10step_taichi_ggui_visualization_guard_pass",
        "[OK] Step101 48cube 10-step Taichi GGUI visualization guard finished",
        "48cube_10step_taichi_ggui_visualization_guard",
    )


if __name__ == "__main__":
    main()
