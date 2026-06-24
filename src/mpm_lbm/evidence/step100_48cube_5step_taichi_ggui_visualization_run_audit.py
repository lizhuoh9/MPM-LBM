from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step100_48cube_5step_taichi_ggui_visualization_run_runner import (
    build_step100_48cube_5step_taichi_ggui_visualization_run_matrix,
)


def build_step100_48cube_5step_taichi_ggui_visualization_run_audit(root: Path) -> tuple[list[dict], dict]:
    return build_step100_48cube_5step_taichi_ggui_visualization_run_matrix(root)
