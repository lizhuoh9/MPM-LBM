from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step80_runtime_geometry_diagnostic_only_smoke_runner import (
    STEP80_SMOKE_FIELDS,
    build_step80_runtime_geometry_diagnostic_only_smoke_matrix,
)


def build_step80_smoke_matrix(root: Path) -> tuple[list[dict], dict]:
    return build_step80_runtime_geometry_diagnostic_only_smoke_matrix(root)
