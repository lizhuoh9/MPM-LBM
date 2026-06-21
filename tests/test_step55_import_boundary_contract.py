import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step55_import_boundary_audit_passes():
    payload = read_json("outputs/step55_import_boundary_audit/import_boundary_audit.json")
    summary = payload["summary"]
    assert summary["import_boundary_audit_pass"] is True
    assert int(summary["scanned_sim_file_count"]) > 0
    assert int(summary["sim_forbidden_import_count"]) == 0
    assert int(summary["sim_forbidden_path_count"]) == 0
    assert int(summary["sim_step_constant_count"]) == 0
    assert summary["solver_behavior_changed"] is False
    assert all(row["pass"] is True for row in payload["rows"])


def test_step55_import_boundary_policy_is_strict_for_sim_package():
    policy = read_json("configs/step55_import_boundary_policy.json")
    assert policy["sim_scan_root"] == "src/mpm_lbm/sim"
    assert "from experiments" in policy["sim_forbidden_import_tokens"]
    assert "from baseline_tests" in policy["sim_forbidden_import_tokens"]
    assert "from tests" in policy["sim_forbidden_import_tokens"]
    assert "outputs/" in policy["sim_forbidden_path_tokens"]
    assert "logs/" in policy["sim_forbidden_path_tokens"]
    assert "docs/" in policy["sim_forbidden_path_tokens"]
    for token in ["step50", "step51", "step52", "step53", "step54"]:
        assert token in policy["sim_forbidden_step_tokens"]
    assert policy["solver_behavior_changed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
