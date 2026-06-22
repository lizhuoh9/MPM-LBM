from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step82_wall_velocity_solid_vel_smoke_runner import (
    STEP82_SMOKE_FIELDS,
    build_step82_wall_velocity_solid_vel_smoke_matrix,
)


def build_step82_smoke_matrix(root: Path) -> tuple[list[dict], dict]:
    return build_step82_wall_velocity_solid_vel_smoke_matrix(root)
