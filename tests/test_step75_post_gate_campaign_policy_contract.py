import json
from pathlib import Path

from src.mpm_lbm.evidence.post_gate_campaign_policy_audit import build_step75_post_gate_campaign_policy_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step75_post_gate_campaign_policy_audit(ROOT)
    assert rows
    assert summary["post_gate_campaign_policy_audit_pass"] is True
    assert summary["allowed_campaign_count"] == 1
    assert summary["first_campaign_is_rebaseline_only"] is True
    assert summary["activation_feature_count_in_first_campaign"] == 0
    assert summary["runtime_geometry_enabled"] is False
    assert summary["wall_velocity_enabled"] is False
    assert summary["real_geometry_enabled"] is False
    assert summary["squid_proxy_enabled"] is False
    assert summary["write_vtk"] is False
    assert summary["write_particles"] is False


def test_artifact_passes():
    payload = read_json("outputs/step75_post_gate_campaign_policy_audit/post_gate_campaign_policy.json")
    assert payload["rows"]
    assert payload["summary"]["post_gate_campaign_policy_audit_pass"] is True
    assert payload["summary"]["run_optional_32_3step"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
