from __future__ import annotations

import json
from pathlib import Path


NEGATION_MARKERS = (" no ", " not ", " false", " forbidden", " disallowed", " does not ", " cannot ")


def claim_guard_rows(root: Path) -> tuple[list[dict], dict]:
    root = Path(root)
    rows = []
    for path in claim_surface_files(root):
        text = path.read_text(encoding="utf-8")
        hits = forbidden_positive_claim_hits(text)
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "forbidden_claim_count": len(hits),
                "forbidden_claims_absent": len(hits) == 0,
                "matched_claims": hits,
            }
        )
    rows.extend(required_false_claim_flag_rows(root))
    summary = {
        "scanned_file_count": sum(1 for row in rows if not row["path"].startswith("outputs/step54_required_false_flags")),
        "required_false_flag_count": sum(1 for row in rows if row["path"].startswith("outputs/step54_required_false_flags")),
        "forbidden_claim_count": sum(int(row["forbidden_claim_count"]) for row in rows),
        "claim_guard_pass": False,
    }
    summary["claim_guard_pass"] = bool(summary["scanned_file_count"] > 0 and summary["forbidden_claim_count"] == 0)
    return rows, summary


def claim_surface_files(root: Path) -> list[Path]:
    candidates = [
        root / "README.md",
        root / "docs" / "54_repository_evidence_integrity_repair.md",
        root / "docs" / "REPOSITORY_EVIDENCE_INDEX.md",
        root / "docs" / "REPOSITORY_EVIDENCE_INTEGRITY_ERRATA.md",
        root / "STEP54_REPOSITORY_EVIDENCE_INTEGRITY_REPAIR_REPORT.md",
    ]
    candidates.extend(sorted((root / "configs").glob("step54*.json")))
    candidates.extend(sorted((root / "baseline_tests").glob("*step54*.py")))
    candidates.extend(sorted((root / "tests").glob("*step54*.py")))
    candidates.extend(
        [
            root / "src" / "lbm_relaxation_semantics.py",
            root / "src" / "proxy_diagnostic_truthfulness.py",
            root / "src" / "state_guard_truthfulness.py",
            root / "src" / "repository_evidence_index.py",
            root / "src" / "repository_test_strength_audit.py",
        ]
    )
    for base in sorted((root / "outputs").glob("step54_*")):
        candidates.extend(path for path in sorted(base.rglob("*")) if path.suffix.lower() in {".json", ".csv"})
    return [path for path in candidates if path.is_file()]


def forbidden_positive_claim_hits(text: str) -> list[str]:
    hits = []
    for line in text.splitlines():
        lower_line = f" {line.lower()} "
        for claim in forbidden_positive_claims():
            if claim in lower_line and not any(marker in lower_line for marker in NEGATION_MARKERS):
                hits.append(claim.strip())
    return hits


def forbidden_positive_claims() -> list[str]:
    return [
        "validates " + "real jet",
        "validates " + "jet propulsion",
        "validates " + "real squid",
        "implements " + "squid swimming",
        "proves " + "grid convergence",
        "validates " + "physical accuracy",
        "is " + "production ready",
        "full solver validation " + "passed",
        "validates " + "standard viscosity",
        "standard viscosity " + "validation passed",
    ]


def required_false_claim_flag_rows(root: Path) -> list[dict]:
    rows = []
    for path in sorted((root / "outputs").glob("step54_*/*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        flattened = flatten_dict(payload)
        for key in [
            "real_jet_validation_claim",
            "jet_propulsion_validation_claim",
            "squid_swimming_claim",
            "grid_convergence_claim",
            "production_readiness_claim",
            "full_solver_validation_claim",
            "standard_viscosity_validation_claim",
            "physical_viscosity_validation_claim",
        ]:
            if key in flattened:
                passed = flattened[key] is False
                rows.append(
                    {
                        "path": f"outputs/step54_required_false_flags/{path.relative_to(root).as_posix()}::{key}",
                        "forbidden_claim_count": 0 if passed else 1,
                        "forbidden_claims_absent": passed,
                        "matched_claims": [] if passed else [key],
                    }
                )
    return rows


def flatten_dict(payload) -> dict:
    flattened = {}
    if isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, dict):
                flattened.update(flatten_dict(value))
            else:
                flattened[key] = value
    elif isinstance(payload, list):
        for item in payload:
            flattened.update(flatten_dict(item))
    return flattened
