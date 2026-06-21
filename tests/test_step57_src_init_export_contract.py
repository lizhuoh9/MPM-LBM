import json
from pathlib import Path

from src.mpm_lbm.evidence.src_init_export_audit import build_src_init_export_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step57_src_init_export_audit_passes_current_source():
    rows, summary = build_src_init_export_audit(ROOT)
    assert summary["src_init_export_audit_pass"] is True
    assert summary["export_count"] > 0
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert int(summary["missing_module_count"]) == 0
    assert int(summary["missing_symbol_count"]) == 0
    assert int(summary["migrated_target_mismatch_count"]) == 0
    assert int(summary["calibration_export_issue_count"]) == 0
    assert summary["lazy_import_enabled"] is True
    assert summary["solver_object_constructed"] is False
    assert all(row["pass"] is True for row in rows)


def test_step57_src_init_export_artifact_passes():
    payload = read_json("outputs/step57_src_init_export_audit/src_init_export_audit.json")
    summary = payload["summary"]
    assert summary["src_init_export_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert int(summary["migrated_target_mismatch_count"]) == 0
    assert int(summary["calibration_export_issue_count"]) == 0


def test_step57_migrated_src_init_exports_point_to_canonical_modules():
    from src import _EXPORT_MODULES

    policy = read_json("configs/step57_src_init_export_policy.json")
    for symbol, canonical_module in policy["migrated_symbol_targets"].items():
        assert _EXPORT_MODULES[symbol] == canonical_module
    for symbol in policy["calibration_symbols"]:
        assert _EXPORT_MODULES[symbol] == "src.calibration"


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
