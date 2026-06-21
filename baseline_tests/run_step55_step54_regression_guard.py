import os

from step55_common import ROOT, read_json, read_text, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["check", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    policy = read_json("configs/step55_test_strength_enum_policy.json")
    allowed = set(policy["allowed_test_strength_levels"])
    strength = read_json("outputs/step54_test_strength_audit/test_strength_audit.json")
    rows = [
        check("step54_lbm_relaxation_semantics_pass", read_json("outputs/step54_lbm_relaxation_semantics_audit/lbm_relaxation_semantics.json")["summary"]["lbm_relaxation_semantics_audit_pass"], True, "Step 54 LBM semantics audit remains green"),
        check("step54_proxy_truthfulness_pass", read_json("outputs/step54_proxy_diagnostic_truthfulness_audit/proxy_diagnostic_truthfulness.json")["summary"]["proxy_truthfulness_audit_pass"], True, "Step 54 proxy truthfulness audit remains green"),
        check("step54_state_guard_truthfulness_pass", read_json("outputs/step54_state_guard_truthfulness_audit/state_guard_truthfulness.json")["summary"]["state_guard_truthfulness_audit_pass"], True, "Step 54 state guard truthfulness audit remains green"),
        check("step54_repository_evidence_index_pass", read_json("outputs/step54_repository_evidence_index/repository_evidence_index.json")["summary"]["repository_evidence_index_pass"], True, "Step 54 repository evidence index remains green"),
        check("step54_claim_guard_pass", read_json("outputs/step54_claim_guard/claim_guard.json")["summary"]["claim_guard_pass"], True, "Step 54 claim guard remains green"),
        check("step54_artifact_manifest_pass", read_json("outputs/step54_artifact_manifest/artifact_summary.json")["artifact_budget_pass"], True, "Step 54 artifact manifest remains green"),
        check("step54_test_strength_audit_pass", strength["summary"]["test_strength_audit_pass"], True, "Step 54 test strength audit remains green"),
        check("step54_test_strength_enum_policy", all(row["test_strength_level"] in allowed for row in strength["rows"]), True, "Step 54 test strength rows use Step 55 policy enum"),
        check("step54_pytest_interpretation_updated", strength["summary"]["test_suite_result_interpretation"] == policy["pytest_result_interpretation"], True, "Step 54 pytest interpretation must be durable"),
        check("step54_report_no_stale_pytest_count", "604/614" not in read_text("STEP54_REPOSITORY_EVIDENCE_INTEGRITY_REPAIR_REPORT.md"), True, "Step 54 report must not contain stale pytest count"),
        check("step54_config_no_stale_pytest_count", "604/614" not in read_text("configs/step54_evidence_classification_policy.json"), True, "Step 54 policy config must not contain stale pytest count"),
        check("step54_tests_no_stale_pytest_count", "604/614" not in read_text("tests/test_step54_repository_evidence_integrity_repair_contract.py"), True, "Step 54 tests must not contain stale pytest count"),
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "step54_regression_guard_pass": False,
    }
    summary["step54_regression_guard_pass"] = bool(summary["row_count"] == summary["pass_count"])
    if not summary["step54_regression_guard_pass"]:
        raise RuntimeError(f"Step 55 Step 54 regression guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step55_step54_regression_guard"
    write_csv_rows(out_dir / "step54_regression_guard.csv", rows, FIELDS)
    write_csv_rows(out_dir / "step54_regression_guard_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "step54_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 55 Step 54 regression guard finished"
    write_log("logs/step55_step54_regression_guard.log", [marker, f"pass_count={summary['pass_count']}"])
    print(marker)


def check(name, value, expected, notes):
    return {"check": name, "pass": value == expected, "value": value, "notes": notes}


if __name__ == "__main__":
    main()
