from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step89_step87_regression_guard import build_step89_step87_regression_guard


def build_step90_step87_regression_guard(
    root: Path,
    policy_path: str = "configs/step90_step87_regression_policy.json",
) -> tuple[list[dict], dict]:
    rows, summary = build_step89_step87_regression_guard(root, policy_path)
    summary = dict(summary)
    summary["step90_step87_regression_guard_pass"] = bool(summary["step89_step87_regression_guard_pass"])
    return rows, summary
