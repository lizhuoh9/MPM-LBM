import os

from step95_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step95_taichi_ggui_10step_visualization_guard import (
    build_step95_taichi_ggui_10step_visualization_guard,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step95_taichi_ggui_10step_visualization_guard,
        "outputs/step95_taichi_ggui_10step_visualization_guard",
        "logs/step95_taichi_ggui_10step_visualization_guard.log",
        "step95_taichi_ggui_10step_visualization_guard_pass",
        "[OK] Step95 Taichi GGUI 10-step visualization guard finished",
        "taichi_ggui_10step_visualization_guard",
    )


if __name__ == "__main__":
    main()
