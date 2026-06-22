import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step86_step31_reference_guard_passes():
    payload = read_json("outputs/step86_step31_reference_guard/step31_reference_guard.json")
    summary = payload["summary"]

    assert summary["step86_step31_reference_guard_pass"] is True
    assert summary["step85_step31_reference_guard_pass"] is True
    assert summary["step30_squid_proxy_geometry_config_exists"] is True
    assert summary["step30_geometry_type"] == "squid_proxy"
    assert summary["step31_static_driver_reference_exists"] is True
    assert summary["step31_not_real_squid_validation_claim"] is True
    assert summary["step31_no_squid_swimming_claim"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
