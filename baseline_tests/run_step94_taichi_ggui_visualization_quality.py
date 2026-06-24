import os

from step94_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step94_taichi_ggui_visualization_quality_audit import (
    build_step94_taichi_ggui_visualization_quality_audit,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step94_taichi_ggui_visualization_quality_audit,
        "outputs/step94_taichi_ggui_visualization_quality",
        "logs/step94_taichi_ggui_visualization_quality.log",
        "step94_taichi_ggui_visualization_quality_pass",
        "[OK] Step94 Taichi GGUI visualization quality audit finished",
        "taichi_ggui_visualization_quality",
    )


if __name__ == "__main__":
    main()
