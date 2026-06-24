from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step98_48cube_taichi_ggui_visualization_smoke_runner import (
    build_step98_48cube_taichi_ggui_visualization_smoke_matrix,
)


def build_step98_48cube_taichi_ggui_visualization_smoke_audit(root: Path) -> tuple[list[dict], dict]:
    return build_step98_48cube_taichi_ggui_visualization_smoke_matrix(root)
