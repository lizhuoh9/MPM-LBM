from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json
from src.mpm_lbm.sim.geometry.candidate_manifest import validate_candidate_descriptor


def build_step74_candidate_descriptor_schema_audit(
    root: Path,
    policy_path: str = "configs/step74_candidate_descriptor_schema_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    valid_descriptor = deepcopy(policy["base_valid_descriptor"])
    rows = [valid_descriptor_row(valid_descriptor)]
    rows.extend(invalid_descriptor_row(valid_descriptor, case) for case in policy["invalid_descriptor_cases"])
    summary = {
        "candidate_descriptor_schema_audit_pass": False,
        "external_path_rejected": any(
            row["case_id"] == "external_taichi_lbm3d_source_rejected" and row["pass"] for row in rows
        ),
        "identity_claim_terms_rejected": all(
            row["pass"]
            for row in rows
            if row["case_id"]
            in {
                "candidate_id_contains_validated",
                "candidate_id_contains_swimming",
                "candidate_id_contains_actuation",
                "candidate_id_contains_anatomical",
            }
        ),
        "invalid_descriptor_rejected_count": sum(
            1 for row in rows if row["check"] == "invalid_descriptor_rejected" and row["pass"]
        ),
        "invalid_descriptor_required_count": len(policy["invalid_descriptor_cases"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "private_absolute_path_policy_enforced": any(
            row["case_id"] == "private_absolute_path_requires_local_only" and row["pass"] for row in rows
        ),
        "row_count": len(rows),
        "valid_descriptor_pass_count": sum(
            1 for row in rows if row["check"] == "valid_descriptor_accepted" and row["pass"]
        ),
    }
    summary["candidate_descriptor_schema_audit_pass"] = bool(
        summary["pass_count"] == summary["row_count"]
        and summary["valid_descriptor_pass_count"] == 1
        and summary["invalid_descriptor_rejected_count"] == summary["invalid_descriptor_required_count"]
        and summary["private_absolute_path_policy_enforced"]
        and summary["external_path_rejected"]
        and summary["identity_claim_terms_rejected"]
    )
    return rows, summary


def valid_descriptor_row(descriptor: dict) -> dict:
    error = ""
    passed = False
    try:
        validated = validate_candidate_descriptor(descriptor)
        passed = bool(validated["candidate_id"] == descriptor["candidate_id"])
    except Exception as exc:  # pragma: no cover - artifact row captures details
        error = f"{type(exc).__name__}: {exc}"
    return {
        "case_id": "valid_synthetic_descriptor",
        "check": "valid_descriptor_accepted",
        "error": error,
        "expected": "accepted",
        "pass": passed,
    }


def invalid_descriptor_row(base: dict, case: dict) -> dict:
    descriptor = deepcopy(base)
    descriptor.update(case["updates"])
    error = ""
    passed = False
    try:
        validate_candidate_descriptor(descriptor)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        passed = True
    return {
        "case_id": case["case_id"],
        "check": "invalid_descriptor_rejected",
        "error": error,
        "expected": "rejected",
        "pass": passed,
    }
