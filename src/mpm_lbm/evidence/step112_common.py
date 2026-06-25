from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step109_common import (
    has_nan_or_inf,
    max_numeric,
    numeric_values_finite,
    read_csv_rows,
    read_json,
    reset_output_dir,
    safe_ratio,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)


STEP112_NAME = "Step112 Fluent Public-Plot Real Solver Dynamics Repair Matrix"
ALLOWED_CLAIM = (
    "A real-solver dynamics repair matrix was run, and the best real FSIDriver3D candidate improved "
    "public-plot comparison metrics without synthetic/replay curves."
)


def write_log(root: Path, path: str, lines: list[str]) -> None:
    log_path = Path(root) / path
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
