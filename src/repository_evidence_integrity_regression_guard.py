from __future__ import annotations

import json
from pathlib import Path


STEP53_REQUIRED_OUTPUTS = {
    "outputs/step53_reference_artifact_validation/reference_artifact_validation.json": ("reference_validation_pass", True),
    "outputs/step53_phasewise_support_scaling_audit/phasewise_support_scaling.json": ("phasewise_audit_pass", True),
    "outputs/step53_active_cell_semantics_audit/active_cell_semantics.json": ("semantics_pass", True),
    "outputs/step53_applied_wall_support_scaling_audit/applied_wall_support_scaling.json": ("applied_wall_support_audit_pass", True),
    "outputs/step53_bounceback_support_scaling_audit/bounceback_support_scaling.json": ("bounceback_support_audit_pass", True),
    "outputs/step53_metric_claim_guard/metric_claim_guard.json": ("claim_guard_pass", True),
    "outputs/step53_step52_regression_guard/step52_regression_guard.json": ("regression_pass", True),
    "outputs/step53_artifact_manifest/artifact_summary.json": ("artifact_budget_pass", True),
}


def step53_regression_rows(root: Path) -> tuple[list[dict], dict]:
    root = Path(root)
    rows = []
    for relative_path, (summary_key, expected) in STEP53_REQUIRED_OUTPUTS.items():
        path = root / relative_path
        if not path.is_file():
            rows.append(check_row(relative_path, False, "missing", f"{summary_key} must remain available"))
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        summary = payload.get("summary", payload)
        actual = summary.get(summary_key)
        rows.append(check_row(relative_path, actual == expected, actual, f"{summary_key} must remain {expected}"))
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "step53_regression_pass": False,
    }
    summary["step53_regression_pass"] = bool(summary["row_count"] == summary["pass_count"] == len(STEP53_REQUIRED_OUTPUTS))
    return rows, summary


def check_row(check: str, passed: bool, value, notes: str) -> dict:
    return {"check": check, "pass": bool(passed), "value": value, "notes": notes}
