import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step110_monitor_alignment_uses_public_structural_point_proxy():
    policy = read_json("configs/step110_monitor_alignment_policy.json")
    payload = read_json("outputs/step110_monitor_alignment/monitor_definition_report.json")
    rows = payload["rows"]
    summary = payload["summary"]
    names = {row["monitor_name"] for row in rows}

    assert policy["public_monitor_x_m"] == 0.0505
    assert policy["public_monitor_y_m"] == 0.0095
    assert policy["normalized_monitor_point"] == [0.505, 0.395, 0.5]
    assert policy["monitor_equivalence"] is False
    assert summary["monitor_alignment_pass"] is True
    assert names == set(policy["required_monitor_names"])

    for monitor_name in policy["required_monitor_names"]:
        series = read_csv(f"outputs/step110_monitor_alignment/monitor_timeseries_{monitor_name}.csv")
        assert len(series) == 51
        assert float(series[-1]["time_s"]) == 0.025


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_csv(path):
    with (ROOT / path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

