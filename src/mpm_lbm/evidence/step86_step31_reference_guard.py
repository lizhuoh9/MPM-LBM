from __future__ import annotations

import json
from pathlib import Path


def build_step86_step31_reference_guard(
    root: Path,
    policy_path: str = "configs/step86_step31_reference_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    step31_payload = read_json(root / policy["step85_step31_reference_artifact_path"])
    source_summary = step31_payload["summary"]
    checks = [
        ("step85_step31_reference_guard_pass", True),
        ("step30_squid_proxy_geometry_config_exists", True),
        ("step30_geometry_type", "squid_proxy"),
        ("step31_static_driver_reference_exists", True),
        ("step31_not_real_squid_validation_claim", True),
        ("step31_no_squid_swimming_claim", True),
    ]
    rows = [literal_row("step85_step31_reference", key, source_summary[key], expected) for key, expected in checks]
    summary = {
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "step30_geometry_type": source_summary["step30_geometry_type"],
        "step30_squid_proxy_geometry_config_exists": source_summary["step30_squid_proxy_geometry_config_exists"],
        "step31_no_squid_swimming_claim": source_summary["step31_no_squid_swimming_claim"],
        "step31_not_real_squid_validation_claim": source_summary["step31_not_real_squid_validation_claim"],
        "step31_static_driver_reference_exists": source_summary["step31_static_driver_reference_exists"],
        "step85_step31_reference_guard_pass": source_summary["step85_step31_reference_guard_pass"],
        "step86_step31_reference_guard_pass": False,
    }
    summary["step86_step31_reference_guard_pass"] = bool(rows and summary["pass_count"] == summary["row_count"])
    return rows, summary


def literal_row(row_name: str, check: str, actual, expected) -> dict:
    return {
        "actual": actual,
        "check": check,
        "expected": expected,
        "pass": actual == expected,
        "row_name": row_name,
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
