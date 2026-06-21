from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


REQUIRED_STEP68_ARTIFACTS = [
    {
        "path": "outputs/step68_step_specific_proxy_policy_audit/audit.json",
        "summary_key": "step68_proxy_policy_audit_pass",
    },
    {
        "path": "outputs/step68_step_specific_proxy_migration_audit/audit.json",
        "summary_key": "step68_proxy_migration_audit_pass",
    },
    {
        "path": "outputs/step68_import_execution_audit/audit.json",
        "summary_key": "step68_import_execution_audit_pass",
    },
    {
        "path": "outputs/step68_legacy_shim_audit/audit.json",
        "summary_key": "step68_legacy_shim_audit_pass",
    },
    {
        "path": "outputs/step68_experiment_boundary_audit/audit.json",
        "summary_key": "experiment_boundary_audit_pass",
    },
    {
        "path": "outputs/step68_step63_67_regression_guard/audit.json",
        "summary_key": "step68_regression_guard_pass",
    },
    {
        "path": "outputs/step68_artifact_manifest/artifact_summary.json",
        "summary_key": "artifact_budget_pass",
        "payload_is_summary": True
    }
]


def build_step69_regression_guard(root: Path) -> tuple[list[dict], dict]:
    root = Path(root)
    rows = [artifact_row(root, artifact) for artifact in REQUIRED_STEP68_ARTIFACTS]
    summary = {
        "row_count": len(rows),
        "step68_required_artifact_count": len(REQUIRED_STEP68_ARTIFACTS),
        "step68_pass_count": sum(1 for row in rows if row["pass"]),
        "missing_artifact_count": sum(1 for row in rows if not row["artifact_exists"]),
        "step69_step68_regression_guard_pass": False,
    }
    summary["step69_step68_regression_guard_pass"] = bool(
        summary["row_count"] == summary["step68_required_artifact_count"]
        and summary["step68_pass_count"] == summary["step68_required_artifact_count"]
        and summary["missing_artifact_count"] == 0
    )
    return rows, summary


def artifact_row(root: Path, artifact: dict) -> dict:
    path = root / artifact["path"]
    exists = path.is_file()
    summary = {}
    key = artifact["summary_key"]
    value = False
    error = ""
    if exists:
        try:
            payload = read_json(path)
            summary = payload if artifact.get("payload_is_summary") else payload["summary"]
            value = bool(summary.get(key, False))
        except Exception as exc:  # pragma: no cover - artifact row captures details
            error = f"{type(exc).__name__}: {exc}"
    return {
        "path": artifact["path"],
        "summary_key": key,
        "artifact_exists": exists,
        "summary_value": value,
        "pass": bool(exists and value),
        "error": error,
    }
