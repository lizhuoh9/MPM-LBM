import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step86_squid_proxy_static_geometry_quality_passes():
    payload = read_json("outputs/step86_squid_proxy_static_geometry_quality/squid_proxy_static_geometry_quality.json")
    summary = payload["summary"]

    assert summary["step86_squid_proxy_static_geometry_quality_pass"] is True
    assert summary["geometry_quality_report_pass_count"] == 1
    assert summary["finite_max_grid_reaction_norm_count"] == 1
    assert summary["squid_proxy_enabled_count"] == 1


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
