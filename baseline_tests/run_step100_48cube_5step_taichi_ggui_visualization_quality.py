import os

from step100_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step100_48cube_5step_taichi_ggui_visualization_quality_audit import (
    build_step100_48cube_5step_taichi_ggui_visualization_quality_audit,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step100_48cube_5step_taichi_ggui_visualization_quality_audit,
        "outputs/step100_48cube_5step_taichi_ggui_visualization_quality",
        "logs/step100_48cube_5step_taichi_ggui_visualization_quality.log",
        "step100_48cube_5step_taichi_ggui_visualization_quality_pass",
        "[OK] Step100 48cube 5-step Taichi GGUI visualization quality audit finished",
        "48cube_5step_taichi_ggui_visualization_quality",
    )


if __name__ == "__main__":
    main()
