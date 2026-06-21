from __future__ import annotations

import json
from pathlib import Path

from src.mpm_lbm.evidence.canonical_driver_duration_ramp_audit import (
    build_canonical_driver_duration_ramp_audit,
)
from src.mpm_lbm.evidence.canonical_driver_duration_ramp_output_guard import (
    build_canonical_driver_duration_ramp_output_guard,
)
from src.mpm_lbm.evidence.step60_regression_guard import build_step60_step59_regression_guard


def build_step61_step60_regression_guard(root: Path) -> tuple[list[dict], dict]:
    root = Path(root)
    duration_matrix = read_json(root / "outputs/step60_duration_ramp_matrix/duration_ramp_matrix.json")["summary"]
    duration_rows, duration_quality = build_canonical_driver_duration_ramp_audit(root)
    _, output_summary = build_canonical_driver_duration_ramp_output_guard(root)
    _, step59_summary = build_step60_step59_regression_guard(root)
    artifact_summary = read_json(root / "outputs/step60_artifact_manifest/artifact_summary.json")
    rows = [
        row("step60_duration_ramp_matrix", duration_matrix["duration_ramp_matrix_pass"], duration_matrix),
        row("step60_duration_ramp_quality", duration_quality["duration_ramp_audit_pass"], duration_quality),
        row("step60_output_guard", output_summary["output_guard_pass"], output_summary),
        row("step60_step59_regression_guard", step59_summary["step59_regression_guard_pass"], step59_summary),
        row("step60_artifact_manifest", artifact_summary["artifact_budget_pass"], artifact_summary),
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for item in rows if item["pass"]),
        "step60_required_row_count": int(duration_quality["required_row_count"]),
        "step60_duration_quality_row_count": len(duration_rows),
        "step60_missing_required_rows": duration_quality["missing_required_rows"],
        "step60_legacy_driver_module_used_count": int(duration_quality["legacy_driver_module_used_count"]),
        "step60_runtime_code_changed": bool(duration_matrix["runtime_code_changed"]),
        "step60_solver_behavior_changed": bool(duration_matrix["solver_behavior_changed"]),
        "step60_physics_feature_expansion": bool(duration_matrix["physics_feature_expansion"]),
        "step60_regression_guard_pass": False,
    }
    summary["step60_regression_guard_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and summary["step60_missing_required_rows"] == []
        and summary["step60_legacy_driver_module_used_count"] == 0
        and not summary["step60_runtime_code_changed"]
        and not summary["step60_solver_behavior_changed"]
        and not summary["step60_physics_feature_expansion"]
    )
    return rows, summary


def row(check: str, passed: bool, details) -> dict:
    return {"check": check, "pass": bool(passed), "details": details}


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
