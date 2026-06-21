from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json, read_text


def build_step70_report_consistency_audit(
    root: Path,
    policy_path: str = "configs/step70_report_consistency_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [report_row(root, report) for report in policy["reports"]]
    fail_count = sum(1 for row in rows if not row["pass"])
    step69_rows = [row for row in rows if row["step_label"] == "Step69"]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "fail_count": fail_count,
        "deferred_count": sum(1 for row in rows if row["deferred"]),
        "step69_report_consistency_fixed": bool(step69_rows and all(row["pass"] and not row["deferred"] for row in step69_rows)),
        "report_consistency_freeze_audit_pass": False,
    }
    summary["report_consistency_freeze_audit_pass"] = bool(
        rows
        and fail_count == 0
        and summary["step69_report_consistency_fixed"]
    )
    return rows, summary


def report_row(root: Path, report: dict) -> dict:
    report_path = root / report["report_path"]
    artifact_path = root / report["artifact_summary_path"]
    deferred = False
    error = ""
    report_text = read_text(report_path)
    if not artifact_path.is_file():
        deferred = report["step_label"] == "Step70"
        return {
            "step_label": report["step_label"],
            "report_path": report["report_path"],
            "artifact_summary_path": report["artifact_summary_path"],
            "artifact_exists": False,
            "report_exists": report_path.is_file(),
            "expected_file_count": "",
            "expected_total_size_mb": "",
            "file_count_match": deferred,
            "total_size_mb_match": deferred,
            "deferred": deferred,
            "pass": deferred,
            "error": "" if deferred else "artifact summary missing",
        }
    try:
        artifact = read_json(artifact_path)
        file_count = artifact[report["file_count_key"]]
        total_size_mb = artifact[report["total_size_mb_key"]]
        file_count_match = str(file_count) in report_text
        total_size_mb_match = str(total_size_mb) in report_text
        passed = bool(report_path.is_file() and file_count_match and total_size_mb_match)
    except Exception as exc:  # pragma: no cover - artifact row captures details
        file_count = ""
        total_size_mb = ""
        file_count_match = False
        total_size_mb_match = False
        passed = False
        error = f"{type(exc).__name__}: {exc}"
    return {
        "step_label": report["step_label"],
        "report_path": report["report_path"],
        "artifact_summary_path": report["artifact_summary_path"],
        "artifact_exists": artifact_path.is_file(),
        "report_exists": report_path.is_file(),
        "expected_file_count": file_count,
        "expected_total_size_mb": total_size_mb,
        "file_count_match": file_count_match,
        "total_size_mb_match": total_size_mb_match,
        "deferred": False,
        "pass": passed,
        "error": error,
    }
