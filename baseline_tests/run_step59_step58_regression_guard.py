import os

from step59_common import ROOT, read_json, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.fsidriver_behavior_preservation_audit import (
    build_fsidriver_behavior_preservation_audit,
)
from src.mpm_lbm.evidence.fsidriver_import_execution_audit import build_fsidriver_import_execution_audit
from src.mpm_lbm.evidence.fsidriver_legacy_shim_audit import build_fsidriver_legacy_shim_audit
from src.mpm_lbm.evidence.fsidriver_migration_audit import build_fsidriver_migration_audit
from src.mpm_lbm.evidence.optional_bridge_audit import build_optional_bridge_audit


FIELDS = ["check", "pass", "details"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    migration_rows, migration_summary = build_fsidriver_migration_audit(ROOT)
    import_rows, import_summary = build_fsidriver_import_execution_audit(ROOT)
    shim_rows, shim_summary = build_fsidriver_legacy_shim_audit(ROOT)
    bridge_rows, bridge_summary = build_optional_bridge_audit(ROOT)
    behavior_rows, behavior_summary = build_fsidriver_behavior_preservation_audit(ROOT)
    artifact_summary = read_json("outputs/step58_artifact_manifest/artifact_summary.json")
    step57_summary = read_json("outputs/step58_step57_regression_guard/step57_regression_guard.json")["summary"]
    rows = [
        row("step58_fsidriver_migration_audit", migration_summary["fsidriver_migration_audit_pass"], migration_summary),
        row("step58_import_execution_audit", import_summary["fsidriver_import_execution_audit_pass"], import_summary),
        row("step58_legacy_shim_audit", shim_summary["fsidriver_legacy_shim_audit_pass"], shim_summary),
        row("step58_optional_bridge_audit", bridge_summary["optional_bridge_audit_pass"], bridge_summary),
        row("step58_behavior_preservation_audit", behavior_summary["fsidriver_behavior_preservation_audit_pass"], behavior_summary),
        row("step58_artifact_manifest", artifact_summary["artifact_budget_pass"], artifact_summary),
        row("step58_step57_regression_guard", step57_summary["step57_regression_guard_pass"], step57_summary),
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for item in rows if item["pass"]),
        "step58_migration_row_count": len(migration_rows),
        "step58_import_row_count": len(import_rows),
        "step58_shim_row_count": len(shim_rows),
        "step58_bridge_row_count": len(bridge_rows),
        "step58_behavior_row_count": len(behavior_rows),
        "step59_geo_path_naming_supersession": "geo_path filename now follows n_grid; default n_grid=32 remains Step58-compatible",
        "step58_regression_guard_pass": False,
    }
    summary["step58_regression_guard_pass"] = bool(summary["row_count"] == summary["pass_count"])
    if not summary["step58_regression_guard_pass"]:
        raise RuntimeError(f"Step 59 Step 58 regression guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step59_step58_regression_guard"
    write_csv_rows(out_dir / "step58_regression_guard.csv", rows, FIELDS)
    write_csv_rows(out_dir / "step58_regression_guard_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "step58_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 59 Step 58 regression guard finished"
    write_log("logs/step59_step58_regression_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


def row(check: str, passed: bool, details) -> dict:
    return {"check": check, "pass": bool(passed), "details": details}


if __name__ == "__main__":
    main()
