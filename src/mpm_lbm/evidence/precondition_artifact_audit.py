from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


def build_step75_precondition_artifact_audit(
    root: Path,
    policy_path: str = "configs/step75_precondition_artifact_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["required_artifacts"]]
    rows.extend(step71_summary_row(root, check) for check in policy["required_step71_summary_values"])
    required_rows = [row for row in rows if row["check_kind"] == "required_artifact"]
    step_rows = {
        step: [row for row in required_rows if int(row["step"]) == step]
        for step in (71, 72, 73, 74)
    }
    summary = {
        "failed_artifact_count": sum(1 for row in required_rows if row["present"] and not row["pass"]),
        "green_artifact_count": sum(1 for row in required_rows if row["pass"]),
        "missing_artifact_count": sum(1 for row in required_rows if not row["present"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "precondition_artifact_audit_pass": False,
        "present_artifact_count": sum(1 for row in required_rows if row["present"]),
        "required_artifact_count": len(required_rows),
        "row_count": len(rows),
        "step71_extra_check_pass_count": sum(
            1 for row in rows if row["check_kind"] == "step71_required_summary_value" and row["pass"]
        ),
        "step71_extra_check_required_count": len(policy["required_step71_summary_values"]),
        "step71_pass": all(row["pass"] for row in step_rows[71]),
        "step72_pass": all(row["pass"] for row in step_rows[72]),
        "step73_pass": all(row["pass"] for row in step_rows[73]),
        "step74_pass": all(row["pass"] for row in step_rows[74]),
    }
    summary["precondition_artifact_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["required_artifact_count"] == 35
        and summary["present_artifact_count"] == summary["required_artifact_count"]
        and summary["green_artifact_count"] == summary["required_artifact_count"]
        and summary["missing_artifact_count"] == 0
        and summary["failed_artifact_count"] == 0
        and summary["step71_extra_check_pass_count"] == summary["step71_extra_check_required_count"]
        and summary["step71_pass"]
        and summary["step72_pass"]
        and summary["step73_pass"]
        and summary["step74_pass"]
    )
    return rows, summary


def artifact_row(root: Path, check: dict) -> dict:
    path = root / check["artifact_path"]
    present = path.is_file()
    actual = None
    if present:
        payload = read_json(path)
        actual = payload.get("summary", payload).get(check["summary_key"])
    return {
        "actual": actual,
        "artifact_path": check["artifact_path"],
        "check": check["check"],
        "check_kind": "required_artifact",
        "expected": check["expected"],
        "pass": bool(present and actual == check["expected"]),
        "present": present,
        "step": int(check["step"]),
        "summary_key": check["summary_key"],
    }


def step71_summary_row(root: Path, check: dict) -> dict:
    path = root / check["artifact_path"]
    present = path.is_file()
    actual = None
    if present:
        payload = read_json(path)
        actual = payload.get("summary", payload).get(check["summary_key"])
    return {
        "actual": actual,
        "artifact_path": check["artifact_path"],
        "check": check["check"],
        "check_kind": "step71_required_summary_value",
        "expected": check["expected"],
        "pass": bool(present and actual == check["expected"]),
        "present": present,
        "step": 71,
        "summary_key": check["summary_key"],
    }
