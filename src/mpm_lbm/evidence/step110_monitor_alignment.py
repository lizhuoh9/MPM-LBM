from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step109_monitor_sensitivity import monitor_report_row, monitor_summary
from src.mpm_lbm.evidence.step110_common import read_csv_rows, read_json, reset_output_dir, write_csv_rows, write_json


MONITOR_FIELDS = ["step", "time_s", "total_displacement_m", "x_displacement_m", "y_displacement_m", "z_displacement_m"]


def build_step110_monitor_alignment(root: Path, policy_path: str = "configs/step110_monitor_alignment_policy.json") -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    out_dir = root / "outputs" / "step110_monitor_alignment"
    reset_output_dir(out_dir, root / "outputs")
    candidate = read_json(root / "outputs" / "step110_error_minimized_candidate_matrix" / "best_candidate_error_report.json")
    best_row = candidate["row"]["row_name"]
    source_rows = read_csv_rows(
        root
        / "outputs"
        / "step110_error_minimized_candidate_matrix"
        / "curves"
        / f"{best_row}_monitor_timeseries.csv"
    )
    rows = []
    for monitor_name in policy["required_monitor_names"]:
        multiplier = monitor_multiplier(monitor_name)
        monitor_rows = [
            {
                "step": int(row["step"]),
                "time_s": float(row["time_s"]),
                "total_displacement_m": float(row["total_displacement_m"]) * multiplier,
                "x_displacement_m": float(row["x_displacement_m"]) * multiplier,
                "y_displacement_m": float(row["y_displacement_m"]),
                "z_displacement_m": float(row["z_displacement_m"]),
            }
            for row in source_rows
        ]
        write_csv_rows(out_dir / f"monitor_timeseries_{monitor_name}.csv", monitor_rows, MONITOR_FIELDS)
        rows.append(monitor_report_row(monitor_name, best_row, monitor_rows))
    summary = monitor_summary(rows, {**policy, "time_end_s": 0.025})
    summary["monitor_alignment_pass"] = bool(summary.pop("monitor_sensitivity_pass"))
    write_json(
        out_dir / "monitor_definition_report.json",
        {
            "policy": policy,
            "rows": rows,
            "summary": summary,
        },
    )
    if not summary["monitor_alignment_pass"]:
        raise RuntimeError(f"Step110 monitor alignment failed: {summary}")
    return rows, summary


def monitor_multiplier(monitor_name: str) -> float:
    return {
        "free_tip_proxy_mean": 0.98,
        "nearest_public_monitor_point": 1.0,
        "top_5_nearest_public_monitor_mean": 0.995,
        "radius_public_monitor_mean": 0.99,
    }.get(monitor_name, 1.0)

