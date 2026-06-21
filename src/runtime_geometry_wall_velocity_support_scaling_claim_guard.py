from __future__ import annotations

import json
from pathlib import Path


REQUIRED_FALSE_FLAGS = [
    "grid_convergence_claim",
    "physical_validation_claim",
    "production_readiness_claim",
    "active_cell_count_is_grid_convergence_metric",
    "applied_cell_growth_is_physical_validation",
    "bb_link_used_as_area_convergence_metric",
]


def claim_guard_rows(root: Path) -> tuple[list[dict], dict]:
    paths = list(step53_claim_surface_files(root))
    rows = []
    forbidden = forbidden_positive_claims()
    for path in paths:
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        hits = [claim for claim in forbidden if claim in lower]
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "forbidden_claim_count": len(hits),
                "forbidden_claims_absent": len(hits) == 0,
            }
        )
    flag_rows = required_flag_rows(root)
    rows.extend(flag_rows)
    summary = {
        "scanned_file_count": len(paths),
        "forbidden_claim_count": sum(int(row.get("forbidden_claim_count", 0)) for row in rows),
        "required_flag_count": len(flag_rows),
        "required_false_flag_pass_count": sum(1 for row in flag_rows if bool(row["forbidden_claims_absent"])),
        "force_impulse_interpretation": force_impulse_interpretation(root),
        "claim_guard_pass": False,
    }
    summary["claim_guard_pass"] = bool(
        summary["forbidden_claim_count"] == 0
        and summary["required_flag_count"] == summary["required_false_flag_pass_count"]
        and summary["force_impulse_interpretation"] == "diagnostic_proxy_only"
    )
    return rows, summary


def step53_claim_surface_files(root: Path):
    candidates = [
        root / "docs" / "53_controlled_48_support_scaling_active_cell_semantics.md",
        root / "STEP53_CONTROLLED_48_SUPPORT_SCALING_ACTIVE_CELL_SEMANTICS_REPORT.md",
    ]
    candidates.extend(sorted((root / "configs").glob("step53*.json")))
    candidates.extend(sorted((root / "baseline_tests").glob("*step53*.py")))
    candidates.extend(sorted((root / "tests").glob("*step53*.py")))
    for base in sorted((root / "outputs").glob("step53_*")):
        candidates.extend(sorted(path for path in base.rglob("*") if path.suffix.lower() in {".json", ".csv"}))
    return [path for path in candidates if path.is_file()]


def required_flag_rows(root: Path) -> list[dict]:
    rows = []
    for path in step53_json_outputs(root):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        flattened = flatten_dict(payload)
        for flag in REQUIRED_FALSE_FLAGS:
            if flag in flattened:
                rows.append(
                    {
                        "path": path.relative_to(root).as_posix(),
                        "flag": flag,
                        "forbidden_claim_count": 0,
                        "forbidden_claims_absent": flattened[flag] is False,
                    }
                )
    return rows


def step53_json_outputs(root: Path):
    for base in sorted((root / "outputs").glob("step53_*")):
        yield from sorted(base.rglob("*.json"))


def force_impulse_interpretation(root: Path) -> str:
    path = root / "outputs" / "step53_phasewise_support_scaling_audit" / "phasewise_support_scaling.json"
    if not path.is_file():
        return ""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return str(payload.get("summary", {}).get("force_impulse_interpretation", ""))


def forbidden_positive_claims() -> list[str]:
    return [
        "validates " + "real jet",
        "validates " + "jet propulsion",
        "implements " + "squid swimming",
        "validates " + "real squid",
        "proves " + "grid convergence",
        "validates " + "physical accuracy",
        "is " + "production ready",
        "implements " + "production moving geometry",
        "proves " + "link_area superiority",
        "validates " + "48^3 physical behavior",
    ]


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
