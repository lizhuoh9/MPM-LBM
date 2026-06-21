from __future__ import annotations

import json
from pathlib import Path

from src.mpm_lbm.evidence.canonical_driver_32_probe_audit import build_canonical_driver_32_probe_audit
from src.mpm_lbm.evidence.canonical_driver_32_probe_output_guard import (
    build_canonical_driver_32_probe_output_guard,
)
from src.mpm_lbm.evidence.report_consistency_guard import build_report_consistency_guard
from src.mpm_lbm.evidence.step61_regression_guard import build_step61_step60_regression_guard


def build_step62_step61_regression_guard(root: Path) -> tuple[list[dict], dict]:
    root = Path(root)
    step61_matrix = read_json(root / "outputs/step61_32_probe_matrix/probe_32_matrix.json")["summary"]
    step61_rows, step61_quality = build_canonical_driver_32_probe_audit(root)
    _, step61_output = build_canonical_driver_32_probe_output_guard(root)
    _, step60_summary = build_step61_step60_regression_guard(root)
    artifact_summary = read_json(root / "outputs/step61_artifact_manifest/artifact_summary.json")
    _, consistency_summary = build_report_consistency_guard(root)
    rows = [
        row("step61_32_probe_matrix", step61_matrix["probe_32_matrix_pass"], step61_matrix),
        row("step61_32_probe_quality", step61_quality["probe_32_audit_pass"], step61_quality),
        row("step61_output_guard", step61_output["output_guard_pass"], step61_output),
        row("step61_step60_regression_guard", step60_summary["step60_regression_guard_pass"], step60_summary),
        row("step61_artifact_manifest", artifact_summary["artifact_budget_pass"], artifact_summary),
        row(
            "step61_report_consistency_issue_fixed",
            consistency_summary["step61_report_consistency_issue_fixed"],
            consistency_summary,
        ),
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for item in rows if item["pass"]),
        "step61_required_row_count": int(step61_quality["required_row_count"]),
        "step61_quality_row_count": len(step61_rows),
        "step61_missing_required_rows": step61_quality["missing_required_rows"],
        "step61_optional_row_count": int(step61_matrix["optional_row_count"]),
        "step61_legacy_driver_module_used_count": int(step61_quality["legacy_driver_module_used_count"]),
        "step61_runtime_code_changed": bool(step61_matrix["runtime_code_changed"]),
        "step61_solver_behavior_changed": bool(step61_matrix["solver_behavior_changed"]),
        "step61_physics_feature_expansion": bool(step61_matrix["physics_feature_expansion"]),
        "step61_report_consistency_issue_fixed": bool(
            consistency_summary["step61_report_consistency_issue_fixed"]
        ),
        "step61_regression_guard_pass": False,
    }
    summary["step61_regression_guard_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and summary["step61_missing_required_rows"] == []
        and summary["step61_optional_row_count"] == 0
        and summary["step61_legacy_driver_module_used_count"] == 0
        and not summary["step61_runtime_code_changed"]
        and not summary["step61_solver_behavior_changed"]
        and not summary["step61_physics_feature_expansion"]
        and summary["step61_report_consistency_issue_fixed"]
    )
    return rows, summary


def row(check: str, passed: bool, details) -> dict:
    return {"check": check, "pass": bool(passed), "details": details}


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
