import os

from step97_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step97_48cube_taichi_ggui_visualization_expansion_guard import (
    build_step97_48cube_taichi_ggui_visualization_expansion_guard,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step97_48cube_taichi_ggui_visualization_expansion_guard,
        "outputs/step97_48cube_taichi_ggui_visualization_expansion_guard",
        "logs/step97_48cube_taichi_ggui_visualization_expansion_guard.log",
        "step97_48cube_taichi_ggui_visualization_expansion_guard_pass",
        "[OK] Step97 48cube Taichi GGUI visualization expansion guard finished",
        "48cube_taichi_ggui_visualization_expansion_guard",
    )


if __name__ == "__main__":
    main()
