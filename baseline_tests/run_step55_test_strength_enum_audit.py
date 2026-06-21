import os

from step55_common import ROOT, read_json, summary_rows, write_csv_rows, write_json, write_log


FIELDS = ["test_file", "step", "test_strength_level", "allowed"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    policy = read_json("configs/step55_test_strength_enum_policy.json")
    payload = read_json("outputs/step54_test_strength_audit/test_strength_audit.json")
    allowed = set(policy["allowed_test_strength_levels"])
    rows = [
        {
            "test_file": row["test_file"],
            "step": row["step"],
            "test_strength_level": row["test_strength_level"],
            "allowed": row["test_strength_level"] in allowed,
        }
        for row in payload["rows"]
    ]
    summary = {
        "row_count": len(rows),
        "allowed_count": sum(1 for row in rows if row["allowed"]),
        "out_of_policy_count": sum(1 for row in rows if not row["allowed"]),
        "allowed_test_strength_level_count": len(allowed),
        "pytest_result_interpretation": policy["pytest_result_interpretation"],
        "test_strength_enum_audit_pass": False,
    }
    summary["test_strength_enum_audit_pass"] = bool(summary["row_count"] == summary["allowed_count"] and summary["row_count"] > 0)
    if not summary["test_strength_enum_audit_pass"]:
        raise RuntimeError(f"Step 55 test strength enum audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step55_test_strength_enum_audit"
    write_csv_rows(out_dir / "test_strength_enum_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "test_strength_enum_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "test_strength_enum_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 55 test strength enum audit finished"
    write_log("logs/step55_test_strength_enum_audit.log", [marker, f"out_of_policy_count={summary['out_of_policy_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
