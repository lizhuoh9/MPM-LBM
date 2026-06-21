import os

from step58_common import ROOT, read_json, summary_rows, write_csv_rows, write_json, write_log
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


FIELDS = ["check", "pass", "details"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    migration_rows, migration_summary = build_driver_support_migration_audit(ROOT)
    import_rows, import_summary = build_driver_support_import_execution_audit(ROOT)
    shim_rows, shim_summary = build_driver_support_legacy_shim_audit(ROOT)
    behavior_rows, behavior_summary = build_driver_support_behavior_preservation_audit(ROOT)
    export_rows, export_summary = build_src_init_export_audit(ROOT)
    step56_rows, step56_behavior_summary = build_behavior_preservation_audit(ROOT)
    step56_supersession = step56_behavior_pass_or_step57_step58_supersession(
        step56_rows, step56_behavior_summary
    )
    artifact_summary = read_json("outputs/step57_artifact_manifest/artifact_summary.json")
    rows = [
        row("step57_driver_support_migration_audit", migration_summary["driver_support_migration_audit_pass"], migration_summary),
        row("step57_import_execution_audit", import_summary["driver_support_import_execution_audit_pass"], import_summary),
        row("step57_legacy_shim_audit", shim_summary["driver_support_legacy_shim_audit_pass"], shim_summary),
        row("step57_behavior_preservation_audit", behavior_summary["driver_support_behavior_preservation_audit_pass"], behavior_summary),
        row("step57_src_init_export_audit", export_summary["src_init_export_audit_pass"], export_summary),
        row("step57_artifact_manifest", artifact_summary["artifact_budget_pass"], artifact_summary),
        row("step56_behavior_or_step57_step58_supersession", step56_supersession["pass"], step56_supersession),
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for item in rows if item["pass"]),
        "step57_migration_row_count": len(migration_rows),
        "step57_import_row_count": len(import_rows),
        "step57_shim_row_count": len(shim_rows),
        "step57_behavior_row_count": len(behavior_rows),
        "step57_export_row_count": len(export_rows),
        "step57_regression_guard_pass": False,
    }
    summary["step57_regression_guard_pass"] = bool(summary["row_count"] == summary["pass_count"])
    if not summary["step57_regression_guard_pass"]:
        raise RuntimeError(f"Step 58 Step 57 regression guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step58_step57_regression_guard"
    write_csv_rows(out_dir / "step57_regression_guard.csv", rows, FIELDS)
    write_csv_rows(out_dir / "step57_regression_guard_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "step57_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 58 Step 57 regression guard finished"
    write_log("logs/step58_step57_regression_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


def row(check: str, passed: bool, details) -> dict:
    return {"check": check, "pass": bool(passed), "details": details}


def step56_behavior_pass_or_step57_step58_supersession(step56_rows: list[dict], step56_summary: dict) -> dict:
    if step56_summary["behavior_preservation_audit_pass"]:
        return {
            "pass": True,
            "mode": "step56_behavior_preservation_pass",
            "behavior_summary": step56_summary,
            "superseded_paths": [],
            "unexpected_failures": [],
        }
    failing_rows = [item for item in step56_rows if not item["pass"]]
    allowed_paths = {
        migration["legacy_path"]
        for migration in read_json("configs/step57_driver_support_migration_policy.json")["migrations"]
    }
    allowed_paths.add(read_json("configs/step58_fsidriver_migration_policy.json")["migration"]["legacy_path"])
    superseded_paths = []
    unexpected_failures = []
    for item in failing_rows:
        actual = set(item.get("actual", []))
        if item.get("check") == "unmigrated_driver_and_coupling_paths_unchanged" and actual <= allowed_paths:
            superseded_paths.extend(sorted(actual))
        else:
            unexpected_failures.append(item)
    return {
        "pass": bool(failing_rows and not unexpected_failures and superseded_paths),
        "mode": "step57_step58_migrations_supersede_step56_protected_paths",
        "behavior_summary": step56_summary,
        "superseded_paths": superseded_paths,
        "unexpected_failures": unexpected_failures,
    }


if __name__ == "__main__":
    main()
