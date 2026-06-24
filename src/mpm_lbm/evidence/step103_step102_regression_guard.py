from __future__ import annotations

import json
from pathlib import Path


def build_step103_step102_regression_guard(
    root: Path,
    policy_path: str = "configs/step103_step102_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    intake = read_json(root / "outputs/step102_fluent_official_2way_fsi_benchmark_intake/fluent_official_2way_fsi_benchmark_intake.json")["summary"]
    output_summary = read_json(root / "outputs/step102_output_guard/output_guard.json")["summary"]
    artifact_summary = read_json(root / "outputs/step102_artifact_manifest/artifact_summary.json")
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "step102_artifact_budget_pass": artifact_summary["artifact_budget_pass"],
        "step102_benchmark_comparison_allowed": intake["step102_benchmark_comparison_allowed"],
        "step102_driver_run_dir_count": output_summary["step102_driver_run_dir_count"],
        "step102_fluent_official_2way_fsi_benchmark_intake_pass": intake[
            "step102_fluent_official_2way_fsi_benchmark_intake_pass"
        ],
        "step102_output_guard_pass": output_summary["output_guard_pass"],
        "step102_validation_claim_allowed": intake["step102_validation_claim_allowed"],
        "step103_step102_regression_guard_pass": False,
    }
    summary["step103_step102_regression_guard_pass"] = bool(
        rows
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["step102_fluent_official_2way_fsi_benchmark_intake_pass"] is True
        and summary["step102_output_guard_pass"] is True
        and summary["step102_artifact_budget_pass"] is True
        and summary["step102_driver_run_dir_count"] == int(policy["expected_step102_driver_run_dir_count"])
        and summary["step102_validation_claim_allowed"] is policy["expected_step102_validation_claim_allowed"]
        and summary["step102_benchmark_comparison_allowed"] is policy["expected_step102_benchmark_comparison_allowed"]
    )
    return rows, summary


def artifact_row(root: Path, check: dict) -> dict:
    actual = artifact_value(root, check["artifact_path"], check["summary_key"])
    return {
        "actual": actual,
        "artifact_path": check["artifact_path"],
        "check": check["check"],
        "expected": check["expected"],
        "pass": actual == check["expected"],
        "summary_key": check["summary_key"],
    }


def artifact_value(root: Path, artifact_path: str, summary_key: str):
    payload = read_json(Path(root) / artifact_path)
    return payload.get("summary", payload).get(summary_key)


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
