from __future__ import annotations

import math
import shutil
from pathlib import Path

from src.mpm_lbm.evidence.step109_common import (
    bool_count,
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


STEP110_NAME = "Step110 Fluent Public-Plot Error-Minimized Candidate With Preflow and Monitor Alignment"
ALLOWED_CLAIM = (
    "A Step110 public-plot error-minimized proxy candidate was selected using proxy preflow, "
    "public structural-point monitor alignment, and Step107 public-reference error metrics."
)

CANDIDATE_NAMES = [
    "cap_3e-2_E_1e6",
    "cap_5e-2_E_1e6",
    "cap_7e-2_E_1e6",
    "cap_1e-2_E_5e4",
    "cap_1e-2_E_2e4",
    "cap_1e-2_E_1e4",
    "cap_2e-2_E_5e4",
    "cap_2e-2_E_2e4",
    "cap_3e-2_E_5e4",
    "cap_3e-2_E_2e4",
    "replay_E_1e4",
    "replay_cap_1e-2",
]


def write_log(root: Path, path: str, lines: list[str]) -> None:
    log_path = root / path
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def finite_row(row: dict) -> bool:
    return numeric_values_finite(row)


def copy_if_exists(source: Path, target: Path) -> bool:
    if not source.is_file():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return True


def window_rms(reference: list[dict], solver: list[dict], start_s: float, end_s: float) -> float:
    pairs = [
        (
            float(ref["fluent_public_digitized_total_displacement_m"]),
            float(row["solver_total_displacement_m"]),
        )
        for ref, row in zip(reference, solver)
        if start_s <= float(ref["time_s"]) <= end_s
    ]
    if not pairs:
        return 0.0
    return math.sqrt(sum((solver_value - ref_value) ** 2 for ref_value, solver_value in pairs) / len(pairs))

