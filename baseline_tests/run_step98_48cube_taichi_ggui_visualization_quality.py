import os

from step98_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step98_48cube_taichi_ggui_visualization_quality_audit import (
    build_step98_48cube_taichi_ggui_visualization_quality_audit,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step98_48cube_taichi_ggui_visualization_quality_audit,
        "outputs/step98_48cube_taichi_ggui_visualization_quality",
        "logs/step98_48cube_taichi_ggui_visualization_quality.log",
        "step98_48cube_taichi_ggui_visualization_quality_pass",
        "[OK] Step98 48cube Taichi GGUI visualization quality audit finished",
        "48cube_taichi_ggui_visualization_quality",
    )


if __name__ == "__main__":
    main()
