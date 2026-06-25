import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_MONITORS = {
    "free_tip_proxy_mean",
    "free_tip_proxy_max_total_displacement",
    "nearest_public_monitor_point",
    "top_5_nearest_public_monitor_mean",
}


def test_step109_monitor_sensitivity_reports_mean_max_nearest_monitors():
    policy = read_json("configs/step109_monitor_sensitivity_policy.json")
    payload = read_json("outputs/step109_monitor_sensitivity/monitor_sensitivity_report.json")
    rows = payload["rows"]
    summary = payload["summary"]
    by_name = {row["monitor_name"]: row for row in rows}

    assert policy["public_monitor_x_m"] == 0.0505
    assert policy["public_monitor_y_m"] == 0.0095
    assert REQUIRED_MONITORS.issubset(set(policy["required_monitor_names"]))
    assert summary["monitor_sensitivity_pass"] is True
    assert summary["monitor_count"] >= 4
    assert summary["all_monitor_metrics_finite"] is True
    assert REQUIRED_MONITORS.issubset(by_name.keys())

    for monitor_name in REQUIRED_MONITORS:
        row = by_name[monitor_name]
        assert row["monitor_equivalence"] is False
        assert row["sample_count"] == 51
        assert row["time_end_s"] == 0.025
        assert row["peak_displacement_m"] >= 0.0
        assert finite_numeric_row(row)
        timeseries = read_csv(f"outputs/step109_monitor_sensitivity/monitor_timeseries_{monitor_name}.csv")
        assert len(timeseries) == 51
        assert math.isclose(float(timeseries[0]["time_s"]), 0.0, rel_tol=0.0, abs_tol=1.0e-15)
        assert math.isclose(float(timeseries[-1]["time_s"]), 0.025, rel_tol=0.0, abs_tol=1.0e-15)


def test_step109_force_and_structural_diagnostics_exist():
    force = read_json("outputs/step109_diagnostics/force_cap_diagnostics_report.json")
    structural = read_json("outputs/step109_diagnostics/structural_sensitivity_report.json")

    assert force["summary"]["force_cap_diagnostics_pass"] is True
    assert force["summary"]["row_count"] >= 6
    assert force["summary"]["best_peak_solver_m"] > 1.0e-5
    assert structural["summary"]["structural_sensitivity_report_pass"] is True
    assert structural["summary"]["structural_row_count"] >= 2
    assert "stiffness_reduction_order_of_magnitude_response" in structural["summary"]


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_csv(path):
    with (ROOT / path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def finite_numeric_row(row: dict) -> bool:
    for value in row.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if not math.isfinite(float(value)):
            return False
    return True
