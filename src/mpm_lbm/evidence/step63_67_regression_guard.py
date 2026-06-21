from __future__ import annotations

import json
from pathlib import Path

from src.mpm_lbm.evidence.step62_regression_guard import build_step62_step61_regression_guard


def build_step63_67_step62_regression_guard(root: Path) -> tuple[list[dict], dict]:
    root = Path(root)
    _, step62_summary = build_step62_step61_regression_guard(root)
    artifact_summary = read_json(root / "outputs/step62_artifact_manifest/artifact_summary.json")
    report_guard = read_json(root / "outputs/step62_report_consistency_guard/report_consistency_guard.json")
    forbidden_dirs = [f"outputs/step{step}_driver_runs" for step in range(63, 68)]
    existing_forbidden_dirs = [path for path in forbidden_dirs if (root / path).exists()]
    rows = [
        row("step62_step61_regression_guard", step62_summary["step61_regression_guard_pass"], "outputs/step62_step61_regression_guard/step61_regression_guard.json"),
        row("step62_artifact_manifest", artifact_summary["artifact_budget_pass"], "outputs/step62_artifact_manifest/artifact_summary.json"),
        row("step62_report_consistency_guard", report_guard["summary"]["report_consistency_guard_pass"], "outputs/step62_report_consistency_guard/report_consistency_guard.json"),
        row("step63_67_driver_run_dirs_absent", not existing_forbidden_dirs, ",".join(existing_forbidden_dirs)),
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for item in rows if item["pass"]),
        "source_artifact_paths": [item["source_artifact_path"] for item in rows],
        "volatile_size_snapshot_embedded": False,
        "step62_regression_guard_pass": bool(step62_summary["step61_regression_guard_pass"]),
        "step63_67_regression_guard_pass": False,
    }
    summary["step63_67_regression_guard_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and summary["step62_regression_guard_pass"]
        and not summary["volatile_size_snapshot_embedded"]
    )
    return rows, summary


def row(check: str, passed: bool, source_artifact_path: str) -> dict:
    return {
        "check": check,
        "pass": bool(passed),
        "source_artifact_path": source_artifact_path,
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
