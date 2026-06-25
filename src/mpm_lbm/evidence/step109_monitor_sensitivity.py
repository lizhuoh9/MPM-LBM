from __future__ import annotations

import math
from pathlib import Path
import shutil

from src.mpm_lbm.evidence.step109_common import (
    numeric_values_finite,
    read_csv_rows,
    read_json,
    reset_output_dir,
    safe_ratio,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)
from src.mpm_lbm.evidence.step109_response_sensitivity_matrix_runner import MONITOR_FIELDS


MONITOR_REPORT_FIELDS = [
    "monitor_name",
    "source_row_name",
    "monitor_equivalence",
    "sample_count",
    "time_start_s",
    "time_end_s",
    "peak_displacement_m",
    "final_displacement_m",
    "peak_x_displacement_m",
    "peak_y_displacement_m",
    "validation_claim_allowed",
    "direct_quantitative_equivalence_allowed",
]


def build_step109_monitor_sensitivity(
    root: Path,
    policy_path: str = "configs/step109_monitor_sensitivity_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    matrix = read_json(root / "outputs" / "step109_response_sensitivity_matrix" / "response_matrix_report.json")
    best_row_name = matrix["summary"]["best_candidate_row_name"]
    if not best_row_name:
        raise RuntimeError("Step109 monitor sensitivity requires a selected response-matrix candidate")

    out_dir = root / "outputs" / "step109_monitor_sensitivity"
    reset_output_dir(out_dir, root / "outputs")
    rows = []
    for monitor_name in policy["required_monitor_names"]:
        source = (
            root
            / "outputs"
            / "step109_response_sensitivity_matrix"
            / "monitor_timeseries"
            / f"{best_row_name}__{monitor_name}.csv"
        )
        target = out_dir / f"monitor_timeseries_{monitor_name}.csv"
        shutil.copy2(source, target)
        rows.append(monitor_report_row(monitor_name, best_row_name, read_csv_rows(target)))
    summary = monitor_summary(rows, policy)
    write_json(out_dir / "monitor_sensitivity_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "monitor_sensitivity_report.csv", rows, MONITOR_REPORT_FIELDS)
    write_csv_rows(out_dir / "monitor_sensitivity_summary.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(
        out_dir / "monitor_sensitivity_report.md",
        "Step109 Monitor Sensitivity",
        rows,
        MONITOR_REPORT_FIELDS,
        note="These monitor variants are proxy reports; none is a direct official structural-point equivalent.",
    )
    if not summary["monitor_sensitivity_pass"]:
        raise RuntimeError(f"Step109 monitor sensitivity failed: {summary}")
    return rows, summary


def monitor_report_row(monitor_name: str, source_row_name: str, rows: list[dict]) -> dict:
    if not rows:
        raise RuntimeError(f"empty Step109 monitor timeseries for {monitor_name}")
    peaks = [(index, abs(float(row["total_displacement_m"]))) for index, row in enumerate(rows)]
    peak_index = max(peaks, key=lambda item: item[1])[0]
    peak_row = rows[peak_index]
    return {
        "direct_quantitative_equivalence_allowed": False,
        "final_displacement_m": float(rows[-1]["total_displacement_m"]),
        "monitor_equivalence": False,
        "monitor_name": monitor_name,
        "peak_displacement_m": float(peak_row["total_displacement_m"]),
        "peak_x_displacement_m": float(peak_row["x_displacement_m"]),
        "peak_y_displacement_m": float(peak_row["y_displacement_m"]),
        "sample_count": len(rows),
        "source_row_name": source_row_name,
        "time_end_s": float(rows[-1]["time_s"]),
        "time_start_s": float(rows[0]["time_s"]),
        "validation_claim_allowed": False,
    }


def monitor_summary(rows: list[dict], policy: dict) -> dict:
    peak_values = [float(row["peak_displacement_m"]) for row in rows]
    mean_peak = next((float(row["peak_displacement_m"]) for row in rows if row["monitor_name"] == "free_tip_proxy_mean"), 0.0)
    summary = {
        "all_monitor_metrics_finite": all(numeric_values_finite(row) for row in rows),
        "direct_quantitative_equivalence_allowed": False,
        "max_to_mean_peak_ratio": safe_ratio(max(peak_values, default=0.0), mean_peak),
        "monitor_count": len(rows),
        "monitor_sensitivity_pass": False,
        "validation_claim_allowed": False,
    }
    summary["monitor_sensitivity_pass"] = bool(
        len(rows) >= len(policy["required_monitor_names"])
        and all(row["monitor_name"] in set(policy["required_monitor_names"]) for row in rows)
        and all(int(row["sample_count"]) == 51 for row in rows)
        and all(math.isclose(float(row["time_start_s"]), 0.0, rel_tol=0.0, abs_tol=1.0e-15) for row in rows)
        and all(math.isclose(float(row["time_end_s"]), float(policy["time_end_s"]), rel_tol=0.0, abs_tol=1.0e-15) for row in rows)
        and all(not row["monitor_equivalence"] for row in rows)
        and summary["all_monitor_metrics_finite"]
        and not summary["validation_claim_allowed"]
        and not summary["direct_quantitative_equivalence_allowed"]
    )
    return summary
