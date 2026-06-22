from __future__ import annotations

import json
from pathlib import Path


def build_step85_step31_reference_guard(
    root: Path,
    policy_path: str = "configs/step85_step31_reference_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    step30_config_path = root / policy["step30_geometry_config_path"]
    step31_report_path = root / policy["step31_report_path"]
    readme_path = root / policy["step31_readme_path"]
    step30_config = read_json(step30_config_path) if step30_config_path.exists() else {}
    report_text = step31_report_path.read_text(encoding="utf-8") if step31_report_path.exists() else ""
    readme_text = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

    rows = [
        literal_row("step30", "step30_squid_proxy_geometry_config_exists", step30_config_path.exists(), True),
        literal_row("step30", "step30_geometry_type", step30_config.get("geometry_type"), policy["expected_step30_geometry_type"]),
        literal_row("step30", "step30_deterministic", step30_config.get("deterministic"), policy["expected_step30_deterministic"]),
        literal_row("step31", "step31_static_driver_reference_exists", step31_report_path.exists(), True),
    ]
    rows.extend(
        literal_row("step31_report", phrase, phrase in report_text, True)
        for phrase in policy["required_report_phrases"]
    )
    rows.extend(
        literal_row("readme_step31_boundary", phrase, phrase in readme_text, True)
        for phrase in policy["required_readme_phrases"]
    )

    summary = {
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "step30_deterministic": bool(step30_config.get("deterministic")),
        "step30_geometry_type": step30_config.get("geometry_type", ""),
        "step30_squid_proxy_geometry_config_exists": step30_config_path.exists(),
        "step31_no_squid_swimming_claim": "Step 31 does not implement squid swimming." in report_text
        and "Step 31 does not implement squid swimming." in readme_text,
        "step31_not_real_squid_validation_claim": "Step 31 is not real squid validation." in report_text
        and "Step 31 is not real squid validation." in readme_text,
        "step31_static_driver_reference_exists": step31_report_path.exists(),
        "step85_step31_reference_guard_pass": False,
    }
    summary["step85_step31_reference_guard_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["step30_squid_proxy_geometry_config_exists"] is True
        and summary["step30_geometry_type"] == "squid_proxy"
        and summary["step30_deterministic"] is True
        and summary["step31_static_driver_reference_exists"] is True
        and summary["step31_not_real_squid_validation_claim"] is True
        and summary["step31_no_squid_swimming_claim"] is True
    )
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
