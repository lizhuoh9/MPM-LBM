import os

from step96_common import ROOT, run_named_audit
from src.mpm_lbm.evidence.step96_taichi_ggui_10step_visualization_quality_audit import (
    build_step96_taichi_ggui_10step_visualization_quality_audit,
)


def main():
    os.chdir(ROOT)
    run_named_audit(
        build_step96_taichi_ggui_10step_visualization_quality_audit,
        "outputs/step96_taichi_ggui_10step_visualization_quality",
        "logs/step96_taichi_ggui_10step_visualization_quality.log",
        "step96_taichi_ggui_10step_visualization_quality_pass",
        "[OK] Step96 Taichi GGUI 10-step visualization quality audit finished",
        "taichi_ggui_10step_visualization_quality",
    )


if __name__ == "__main__":
    main()
