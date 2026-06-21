import os

from step56_common import ROOT, read_json, read_text, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.code_layout_audit import build_code_layout_audit
from src.mpm_lbm.evidence.compatibility_shim_audit import build_compatibility_shim_audit
from src.mpm_lbm.evidence.import_boundary_audit import build_import_boundary_audit


FIELDS = ["check", "pass", "details"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    code_rows, code_summary = build_code_layout_audit(ROOT)
    import_rows, import_summary = build_import_boundary_audit(ROOT)
    shim_rows, shim_summary = build_compatibility_shim_audit(ROOT)
    test_strength_summary = read_json("outputs/step55_test_strength_enum_audit/test_strength_enum_audit.json")["summary"]
    artifact_summary = read_json("outputs/step55_artifact_manifest/artifact_summary.json")
    step56_import_summary = read_json("outputs/step56_import_execution_audit/import_execution_audit.json")["summary"]
    readme_docs_boundary = docs_still_contain_layout_boundary()
    rows = [
        row("step55_code_layout_audit", code_summary["code_layout_audit_pass"], code_summary),
        row("step55_import_boundary_audit", import_summary["import_boundary_audit_pass"], import_summary),
        row(
            "step55_compatibility_shim_audit_or_step56_import_supersession",
            shim_summary["compatibility_shim_audit_pass"] and step56_import_summary["import_execution_audit_pass"],
            {"step55": shim_summary, "step56_import_execution": step56_import_summary},
        ),
        row("step55_test_strength_enum_audit", test_strength_summary["test_strength_enum_audit_pass"], test_strength_summary),
        row("step55_artifact_manifest", artifact_summary["artifact_budget_pass"], artifact_summary),
        row("readme_docs_layout_boundary", readme_docs_boundary, {"readme_docs_layout_boundary": readme_docs_boundary}),
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for item in rows if item["pass"]),
        "code_layout_row_count": len(code_rows),
        "import_boundary_row_count": len(import_rows),
        "compatibility_shim_row_count": len(shim_rows),
        "step55_regression_guard_pass": False,
    }
    summary["step55_regression_guard_pass"] = bool(summary["row_count"] == summary["pass_count"])
    if not summary["step55_regression_guard_pass"]:
        raise RuntimeError(f"Step 56 Step 55 regression guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step56_step55_regression_guard"
    write_csv_rows(out_dir / "step55_regression_guard.csv", rows, FIELDS)
    write_csv_rows(out_dir / "step55_regression_guard_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "step55_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 56 Step 55 regression guard finished"
    write_log("logs/step56_step55_regression_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


def row(check: str, passed: bool, details) -> dict:
    return {"check": check, "pass": bool(passed), "details": details}


def docs_still_contain_layout_boundary() -> bool:
    joined = "\n".join(
        [
            read_text("README.md"),
            read_text("docs/55_repository_code_layout_separation_import_boundary.md"),
            read_text("docs/REPOSITORY_CODE_LAYOUT_POLICY.md"),
        ]
    )
    return all(
        phrase in joined
        for phrase in [
            "Step 55 does not change solver behavior.",
            "Root `src/*.py` remains a compatibility and approved legacy surface",
        ]
    )


if __name__ == "__main__":
    main()
