from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


REQUIRED_STEP69_ARTIFACTS = [
    {
        "path": "outputs/step69_current_root_inventory_audit/audit.json",
        "checks": {
            "current_root_inventory_audit_pass": True,
            "current_migration_required_count": 0,
            "current_root_step_specific_implementation_count": 0,
            "current_unknown_requires_review_count": 0
        }
    },
    {
        "path": "outputs/step69_remaining_support_migration_audit/audit.json",
        "checks": {
            "remaining_support_migration_audit_pass": True,
            "remaining_migration_required_count": 0
        }
    },
    {
        "path": "outputs/step69_import_execution_audit/audit.json",
        "checks": {
            "step69_import_execution_audit_pass": True
        }
    },
    {
        "path": "outputs/step69_legacy_shim_audit/audit.json",
        "checks": {
            "step69_legacy_shim_audit_pass": True
        }
    },
    {
        "path": "outputs/step69_src_init_export_audit/audit.json",
        "checks": {
            "src_init_export_audit_pass": True
        }
    },
    {
        "path": "outputs/step69_no_simulation_audit/audit.json",
        "checks": {
            "no_simulation_audit_pass": True
        }
    },
    {
        "path": "outputs/step69_artifact_manifest/artifact_summary.json",
        "payload_is_summary": True,
        "checks": {
            "artifact_budget_pass": True
        }
    }
]


def build_step70_regression_guard(root: Path) -> tuple[list[dict], dict]:
    root = Path(root)
    rows = [
        check_row(root, artifact, key, expected)
        for artifact in REQUIRED_STEP69_ARTIFACTS
        for key, expected in artifact["checks"].items()
    ]
    summary = {
        "row_count": len(rows),
        "step69_required_check_count": len(rows),
        "step69_pass_count": sum(1 for row in rows if row["pass"]),
        "missing_artifact_count": len({row["path"] for row in rows if not row["artifact_exists"]}),
        "step70_step69_regression_guard_pass": False,
    }
    summary["step70_step69_regression_guard_pass"] = bool(
        rows
        and summary["step69_pass_count"] == summary["step69_required_check_count"]
        and summary["missing_artifact_count"] == 0
    )
    return rows, summary


def check_row(root: Path, artifact: dict, key: str, expected) -> dict:
    path = root / artifact["path"]
    exists = path.is_file()
    actual = None
    error = ""
    if exists:
        try:
            payload = read_json(path)
            summary = payload if artifact.get("payload_is_summary") else payload["summary"]
            actual = summary.get(key)
        except Exception as exc:  # pragma: no cover - artifact row captures details
            error = f"{type(exc).__name__}: {exc}"
    return {
        "path": artifact["path"],
        "summary_key": key,
        "expected": expected,
        "actual": actual,
        "artifact_exists": exists,
        "pass": bool(exists and actual == expected),
        "error": error,
    }
