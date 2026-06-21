import json
from pathlib import Path

from src.mpm_lbm.evidence.behavior_preservation_audit import build_behavior_preservation_audit
from src.mpm_lbm.evidence.canonical_runtime_migration_audit import build_canonical_runtime_migration_audit
from src.mpm_lbm.evidence.import_execution_audit import build_import_execution_audit
from src.mpm_lbm.evidence.legacy_shim_audit import build_legacy_shim_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step57_step56_regression_guard_passes_current_source():
    _, migration_summary = build_canonical_runtime_migration_audit(ROOT)
    _, import_summary = build_import_execution_audit(ROOT)
    _, shim_summary = build_legacy_shim_audit(ROOT)
    behavior_rows, behavior_summary = build_behavior_preservation_audit(ROOT)
    assert migration_summary["canonical_runtime_migration_audit_pass"] is True
    assert import_summary["import_execution_audit_pass"] is True
    assert shim_summary["legacy_shim_audit_pass"] is True
    behavior_supersession = step56_behavior_pass_or_step57_support_supersession(behavior_rows, behavior_summary)
    assert behavior_supersession["pass"] is True
    assert behavior_supersession["unexpected_failures"] == []


def test_step57_step56_regression_guard_artifact_passes():
    payload = read_json("outputs/step57_step56_regression_guard/step56_regression_guard.json")
    summary = payload["summary"]
    assert summary["step56_regression_guard_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert all(row["pass"] is True for row in payload["rows"])


def test_step57_artifact_manifest_passes():
    manifest = read_json("outputs/step57_artifact_manifest/artifact_summary.json")
    assert manifest["artifact_budget_pass"] is True
    assert int(manifest["protected_external_taichi_lbm3d_step57_file_count"]) == 0
    assert int(manifest["protected_real_geometry_candidates_step57_file_count"]) == 0
    assert float(manifest["step57_total_size_mb"]) < 5.0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def step56_behavior_pass_or_step57_support_supersession(behavior_rows: list[dict], behavior_summary: dict) -> dict:
    if behavior_summary["behavior_preservation_audit_pass"]:
        return {"pass": True, "unexpected_failures": []}
    failing_rows = [item for item in behavior_rows if not item["pass"]]
    allowed_legacy_paths = {
        migration["legacy_path"]
        for migration in read_json("configs/step57_driver_support_migration_policy.json")["migrations"]
    }
    step58_policy_path = ROOT / "configs" / "step58_fsidriver_migration_policy.json"
    if step58_policy_path.is_file():
        allowed_legacy_paths.add(read_json("configs/step58_fsidriver_migration_policy.json")["migration"]["legacy_path"])
    unexpected_failures = []
    superseded_paths = []
    for item in failing_rows:
        actual = set(item.get("actual", []))
        if item.get("check") == "unmigrated_driver_and_coupling_paths_unchanged" and actual <= allowed_legacy_paths:
            superseded_paths.extend(sorted(actual))
        else:
            unexpected_failures.append(item)
    return {
        "pass": bool(failing_rows and not unexpected_failures and superseded_paths),
        "unexpected_failures": unexpected_failures,
    }
