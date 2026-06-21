import os

from step57_common import ROOT, read_json, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.behavior_preservation_audit import build_behavior_preservation_audit
from src.mpm_lbm.evidence.canonical_runtime_migration_audit import build_canonical_runtime_migration_audit
from src.mpm_lbm.evidence.import_execution_audit import build_import_execution_audit
from src.mpm_lbm.evidence.legacy_shim_audit import build_legacy_shim_audit


FIELDS = ["check", "pass", "details"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    migration_rows, migration_summary = build_canonical_runtime_migration_audit(ROOT)
    import_rows, import_summary = build_import_execution_audit(ROOT)
    shim_rows, shim_summary = build_legacy_shim_audit(ROOT)
    behavior_rows, behavior_summary = build_behavior_preservation_audit(ROOT)
    artifact_summary = read_json("outputs/step56_artifact_manifest/artifact_summary.json")
    step55_summary = read_json("outputs/step56_step55_regression_guard/step55_regression_guard.json")["summary"]
    behavior_supersession = step56_behavior_pass_or_step57_support_supersession(behavior_rows, behavior_summary)
    rows = [
        row("step56_canonical_runtime_migration_audit", migration_summary["canonical_runtime_migration_audit_pass"], migration_summary),
        row("step56_import_execution_audit", import_summary["import_execution_audit_pass"], import_summary),
        row("step56_legacy_shim_audit", shim_summary["legacy_shim_audit_pass"], shim_summary),
        row("step56_behavior_preservation_or_step57_support_supersession", behavior_supersession["pass"], behavior_supersession),
        row("step56_artifact_manifest", artifact_summary["artifact_budget_pass"], artifact_summary),
        row("step56_step55_regression_guard", step55_summary["step55_regression_guard_pass"], step55_summary),
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for item in rows if item["pass"]),
        "step56_migration_row_count": len(migration_rows),
        "step56_import_row_count": len(import_rows),
        "step56_shim_row_count": len(shim_rows),
        "step56_behavior_row_count": len(behavior_rows),
        "step56_regression_guard_pass": False,
    }
    summary["step56_regression_guard_pass"] = bool(summary["row_count"] == summary["pass_count"])
    if not summary["step56_regression_guard_pass"]:
        raise RuntimeError(f"Step 57 Step 56 regression guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step57_step56_regression_guard"
    write_csv_rows(out_dir / "step56_regression_guard.csv", rows, FIELDS)
    write_csv_rows(out_dir / "step56_regression_guard_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "step56_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 57 Step 56 regression guard finished"
    write_log("logs/step57_step56_regression_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


def row(check: str, passed: bool, details) -> dict:
    return {"check": check, "pass": bool(passed), "details": details}


def step56_behavior_pass_or_step57_support_supersession(behavior_rows: list[dict], behavior_summary: dict) -> dict:
    if behavior_summary["behavior_preservation_audit_pass"]:
        return {
            "pass": True,
            "mode": "step56_behavior_preservation_pass",
            "behavior_summary": behavior_summary,
            "superseded_paths": [],
        }
    failing_rows = [item for item in behavior_rows if not item["pass"]]
    allowed_legacy_paths = {
        migration["legacy_path"]
        for migration in read_json("configs/step57_driver_support_migration_policy.json")["migrations"]
    }
    step58_policy_path = ROOT / "configs" / "step58_fsidriver_migration_policy.json"
    if step58_policy_path.is_file():
        allowed_legacy_paths.add(read_json("configs/step58_fsidriver_migration_policy.json")["migration"]["legacy_path"])
    superseded_paths = []
    unexpected_failures = []
    for item in failing_rows:
        actual = set(item.get("actual", []))
        if item.get("check") == "unmigrated_driver_and_coupling_paths_unchanged" and actual <= allowed_legacy_paths:
            superseded_paths.extend(sorted(actual))
        else:
            unexpected_failures.append(item)
    return {
        "pass": bool(failing_rows and not unexpected_failures and superseded_paths),
        "mode": "step57_support_migration_supersedes_step56_protected_paths",
        "behavior_summary": behavior_summary,
        "superseded_paths": superseded_paths,
        "unexpected_failures": unexpected_failures,
    }


if __name__ == "__main__":
    main()
