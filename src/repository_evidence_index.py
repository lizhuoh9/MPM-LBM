from __future__ import annotations

import re
from pathlib import Path


STEP_CLASSIFICATIONS = {
    1: {
        "evidence_kind": "solver_smoke_baseline",
        "solver_time_integration_run": True,
        "record_kind": "solver_smoke_record",
        "scope_note": "early solver smoke baseline, not a full validation claim",
    },
    2: {
        "evidence_kind": "solver_smoke_baseline",
        "solver_time_integration_run": True,
        "record_kind": "solver_smoke_record",
        "scope_note": "early solver smoke baseline, not a full validation claim",
    },
    50: {
        "evidence_kind": "proxy_diagnostic",
        "solver_time_integration_run": False,
        "record_kind": "proxy_diagnostic_record",
        "scope_note": "config-declared one-cycle proxy diagnostics, no driver instance",
    },
    51: {
        "evidence_kind": "proxy_diagnostic",
        "solver_time_integration_run": False,
        "record_kind": "proxy_diagnostic_record",
        "scope_note": "config-declared transfer comparison proxy diagnostics, no driver instance",
    },
    52: {
        "evidence_kind": "proxy_diagnostic",
        "solver_time_integration_run": False,
        "record_kind": "proxy_diagnostic_record",
        "scope_note": "config-declared 48-grid proxy diagnostics, no driver instance",
    },
    53: {
        "evidence_kind": "post_processing_audit",
        "solver_time_integration_run": False,
        "record_kind": "post_processing_audit_record",
        "scope_note": "post-processing audit over committed Step 51 and Step 52 artifacts",
    },
    54: {
        "evidence_kind": "evidence_integrity_repair",
        "solver_time_integration_run": False,
        "record_kind": "repository_evidence_integrity_record",
        "scope_note": "repository evidence index, claim guard, and semantics repair",
    },
}


def build_repository_evidence_index(root: Path) -> tuple[list[dict], dict]:
    root = Path(root)
    rows = []
    for step in discovered_steps(root):
        classification = classify_step(step)
        primary_artifact = primary_step_artifact(root, step)
        row = {
            "step": step,
            "primary_artifact": primary_artifact,
            "primary_artifact_exists": bool(primary_artifact and (root / primary_artifact).is_file()),
            "evidence_kind": classification["evidence_kind"],
            "solver_time_integration_run": classification["solver_time_integration_run"],
            "record_kind": classification["record_kind"],
            "scope_note": classification["scope_note"],
            "claim_boundary": claim_boundary_for_kind(classification["evidence_kind"]),
        }
        rows.append(row)

    rows.sort(key=lambda row: int(row["step"]))
    step_map = {int(row["step"]): row for row in rows}
    summary = {
        "indexed_step_count": len(rows),
        "step50_51_52_proxy_diagnostic_count": sum(
            1 for step in (50, 51, 52) if step_map.get(step, {}).get("evidence_kind") == "proxy_diagnostic"
        ),
        "step53_post_processing_audit_count": int(step_map.get(53, {}).get("evidence_kind") == "post_processing_audit"),
        "step1_step2_solver_smoke_baseline_count": sum(
            1 for step in (1, 2) if step_map.get(step, {}).get("evidence_kind") == "solver_smoke_baseline"
        ),
        "proxy_steps_solver_time_integration_false": all(
            step_map.get(step, {}).get("solver_time_integration_run") is False for step in (50, 51, 52)
        ),
        "step53_solver_time_integration_false": step_map.get(53, {}).get("solver_time_integration_run") is False,
        "positive_physical_claim_allowed": False,
        "repository_evidence_index_pass": False,
    }
    summary["repository_evidence_index_pass"] = bool(
        summary["step50_51_52_proxy_diagnostic_count"] == 3
        and summary["step53_post_processing_audit_count"] == 1
        and summary["step1_step2_solver_smoke_baseline_count"] == 2
        and summary["proxy_steps_solver_time_integration_false"]
        and summary["step53_solver_time_integration_false"]
        and not summary["positive_physical_claim_allowed"]
    )
    return rows, summary


def discovered_steps(root: Path) -> list[int]:
    steps = set()
    patterns = [
        "STEP*_REPORT.md",
        "STEP*_GOAL.md",
        "tests/test_step*.py",
        "baseline_tests/run_step*.py",
    ]
    for pattern in patterns:
        for path in root.glob(pattern):
            match = re.search(r"[Ss][Tt][Ee][Pp](\d+)", path.name)
            if match:
                steps.add(int(match.group(1)))
    return sorted(steps)


def primary_step_artifact(root: Path, step: int) -> str:
    candidates = []
    candidates.extend(sorted(root.glob(f"STEP{step:02d}*_REPORT.md")))
    candidates.extend(sorted(root.glob(f"STEP{step}*_REPORT.md")))
    candidates.extend(sorted(root.glob(f"STEP{step:02d}*_GOAL.md")))
    candidates.extend(sorted(root.glob(f"STEP{step}*_GOAL.md")))
    for path in candidates:
        if path.is_file():
            return path.relative_to(root).as_posix()
    return ""


def classify_step(step: int) -> dict:
    if step in STEP_CLASSIFICATIONS:
        return dict(STEP_CLASSIFICATIONS[step])
    return {
        "evidence_kind": "contract_or_report_artifact",
        "solver_time_integration_run": "unknown_from_repository_index",
        "record_kind": "historical_step_record",
        "scope_note": "historical step kept under its original committed contract",
    }


def claim_boundary_for_kind(evidence_kind: str) -> str:
    if evidence_kind == "solver_smoke_baseline":
        return "solver smoke only, not production or physical validation"
    if evidence_kind == "proxy_diagnostic":
        return "proxy diagnostic only, not solver time integration"
    if evidence_kind == "post_processing_audit":
        return "artifact audit only, no new solver rows"
    if evidence_kind == "evidence_integrity_repair":
        return "evidence repair only, no new physics scope"
    return "defer to original step report"
