from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.activation_preconditions_audit import build_step70_activation_preconditions_audit
from src.mpm_lbm.evidence.compatibility_surface_audit import build_step70_compatibility_surface_audit
from src.mpm_lbm.evidence.current_root_inventory_audit import read_json
from src.mpm_lbm.evidence.output_artifact_policy_audit import build_step70_output_artifact_policy_audit
from src.mpm_lbm.evidence.public_api_surface_audit import build_step70_public_api_surface_audit
from src.mpm_lbm.evidence.report_consistency_freeze_audit import build_step70_report_consistency_audit


def build_step71_step70_regression_guard(
    root: Path,
    policy_path: str = "configs/step71_step70_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    computed = {
        "public_api_surface": build_step70_public_api_surface_audit(root)[1],
        "compatibility_surface": build_step70_compatibility_surface_audit(root)[1],
        "activation_preconditions": build_step70_activation_preconditions_audit(root)[1],
        "output_artifact_policy": build_step70_output_artifact_policy_audit(root)[1],
        "report_consistency": build_step70_report_consistency_audit(root)[1],
    }
    rows = []
    for check in policy["required_step70_checks"]:
        if "artifact_path" in check:
            payload = read_json(root / check["artifact_path"])
            actual = payload.get(check["summary_key"])
        else:
            actual = computed[check["check"]].get(check["summary_key"])
        rows.append(
            {
                "check": check["check"],
                "summary_key": check["summary_key"],
                "expected": check["expected"],
                "actual": actual,
                "pass": actual == check["expected"],
            }
        )
    rows.append(
        {
            "check": "step70_config_schema_freeze_superseded",
            "summary_key": "schema_freeze_superseded_by_step71_delta",
            "expected": True,
            "actual": bool(policy["schema_freeze_superseded_by_step71_delta"]),
            "pass": bool(policy["schema_freeze_superseded_by_step71_delta"]),
        }
    )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "schema_freeze_superseded_by_step71_delta": bool(policy["schema_freeze_superseded_by_step71_delta"]),
        "step71_step70_regression_guard_pass": False,
    }
    summary["step71_step70_regression_guard_pass"] = bool(rows and summary["pass_count"] == summary["row_count"])
    return rows, summary
