import json
from pathlib import Path

from src.mpm_lbm.evidence.behavior_preservation_audit import build_behavior_preservation_audit
from src.mpm_lbm.evidence.driver_support_behavior_preservation_audit import (
    build_driver_support_behavior_preservation_audit,
)
from src.mpm_lbm.evidence.driver_support_import_execution_audit import (
    build_driver_support_import_execution_audit,
)
from src.mpm_lbm.evidence.driver_support_legacy_shim_audit import build_driver_support_legacy_shim_audit
from src.mpm_lbm.evidence.driver_support_migration_audit import build_driver_support_migration_audit
from src.mpm_lbm.evidence.src_init_export_audit import build_src_init_export_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step58_step57_regression_guard_passes_current_source():
    _, migration_summary = build_driver_support_migration_audit(ROOT)
    _, import_summary = build_driver_support_import_execution_audit(ROOT)
    _, shim_summary = build_driver_support_legacy_shim_audit(ROOT)
    _, behavior_summary = build_driver_support_behavior_preservation_audit(ROOT)
    _, export_summary = build_src_init_export_audit(ROOT)
    step56_rows, step56_summary = build_behavior_preservation_audit(ROOT)
    supersession = step56_behavior_pass_or_step57_step58_supersession(step56_rows, step56_summary)
    assert migration_summary["driver_support_migration_audit_pass"] is True
    assert import_summary["driver_support_import_execution_audit_pass"] is True
    assert shim_summary["driver_support_legacy_shim_audit_pass"] is True
    assert behavior_summary["driver_support_behavior_preservation_audit_pass"] is True
    assert export_summary["src_init_export_audit_pass"] is True
    assert supersession["pass"] is True
    assert supersession["unexpected_failures"] == []


def test_step58_step57_regression_guard_artifact_passes():
    payload = read_json("outputs/step58_step57_regression_guard/step57_regression_guard.json")
    summary = payload["summary"]
    assert summary["step57_regression_guard_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert all(row["pass"] is True for row in payload["rows"])


def test_step58_artifact_manifest_passes():
    manifest = read_json("outputs/step58_artifact_manifest/artifact_summary.json")
    assert manifest["artifact_budget_pass"] is True
    assert int(manifest["protected_external_taichi_lbm3d_step58_file_count"]) == 0
    assert int(manifest["protected_real_geometry_candidates_step58_file_count"]) == 0
    assert float(manifest["step58_total_size_mb"]) < 5.0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def step56_behavior_pass_or_step57_step58_supersession(step56_rows: list[dict], step56_summary: dict) -> dict:
    if step56_summary["behavior_preservation_audit_pass"]:
        return {"pass": True, "unexpected_failures": []}
    failing_rows = [item for item in step56_rows if not item["pass"]]
    allowed_paths = {
        migration["legacy_path"]
        for migration in read_json("configs/step57_driver_support_migration_policy.json")["migrations"]
    }
    allowed_paths.add(read_json("configs/step58_fsidriver_migration_policy.json")["migration"]["legacy_path"])
    unexpected_failures = []
    superseded_paths = []
    for item in failing_rows:
        actual = set(item.get("actual", []))
        if item.get("check") == "unmigrated_driver_and_coupling_paths_unchanged" and actual <= allowed_paths:
            superseded_paths.extend(sorted(actual))
        else:
            unexpected_failures.append(item)
    return {
        "pass": bool(failing_rows and not unexpected_failures and superseded_paths),
        "unexpected_failures": unexpected_failures,
    }
