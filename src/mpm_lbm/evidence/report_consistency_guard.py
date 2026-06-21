from __future__ import annotations

import json
import math
import re
from pathlib import Path


def build_report_consistency_guard(
    root: Path,
    policy_path: str = "configs/step62_report_consistency_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    tolerance = float(policy.get("tolerance", 1e-12))
    rows = [check_report_metric(root, check, tolerance) for check in policy["checks"]]
    step61_rows = [row for row in rows if int(row["step"]) == 61]
    step62_rows = [row for row in rows if int(row["step"]) == 62]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "fail_count": sum(1 for row in rows if not row["pass"]),
        "step61_row_count": len(step61_rows),
        "step61_pass_count": sum(1 for row in step61_rows if row["pass"]),
        "step62_row_count": len(step62_rows),
        "step62_pass_count": sum(1 for row in step62_rows if row["pass"]),
        "step61_report_consistency_issue_fixed": False,
        "step62_report_consistency_checked": False,
        "report_consistency_guard_pass": False,
    }
    summary["step61_report_consistency_issue_fixed"] = bool(
        summary["step61_row_count"] > 0 and summary["step61_row_count"] == summary["step61_pass_count"]
    )
    summary["step62_report_consistency_checked"] = bool(
        summary["step62_row_count"] > 0 and summary["step62_row_count"] == summary["step62_pass_count"]
    )
    summary["report_consistency_guard_pass"] = bool(summary["row_count"] == summary["pass_count"])
    return rows, summary


def check_report_metric(root: Path, check: dict, tolerance: float) -> dict:
    report_path = root / check["report_path"]
    artifact_path = root / check["artifact_path"]
    metric = check["metric"]
    section = check["section"]
    report_value = extract_report_metric(report_path, section, metric)
    artifact_value = extract_artifact_value(read_json(artifact_path), check["artifact_key_path"])
    delta = abs(float(report_value) - float(artifact_value))
    passed = math.isfinite(delta) and delta <= tolerance
    return {
        "step": int(check["step"]),
        "report_path": check["report_path"],
        "artifact_path": check["artifact_path"],
        "section": section,
        "metric": metric,
        "report_value": float(report_value),
        "artifact_value": float(artifact_value),
        "delta": delta,
        "tolerance": tolerance,
        "pass": passed,
        "notes": "report metric matches artifact" if passed else "report metric differs from artifact",
    }


def extract_report_metric(report_path: Path, section: str, metric: str) -> float:
    text = report_path.read_text(encoding="utf-8")
    section_text = extract_markdown_section(text, section)
    pattern = re.compile(r"\|\s*`" + re.escape(metric) + r"`\s*\|\s*([^|]+?)\s*\|")
    match = pattern.search(section_text)
    if not match:
        raise RuntimeError(f"metric {metric!r} not found in section {section!r} of {report_path}")
    return float(match.group(1).strip())


def extract_markdown_section(text: str, section: str) -> str:
    header = f"## {section}"
    start = text.find(header)
    if start < 0:
        raise RuntimeError(f"section {section!r} not found")
    next_header = text.find("\n## ", start + len(header))
    if next_header < 0:
        return text[start:]
    return text[start:next_header]


def extract_artifact_value(payload: dict, key_path: str):
    value = payload
    for key in key_path.split("."):
        value = value[key]
    return value


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
