import os

from step54_common import ROOT, check_row, read_json, summary_rows, write_csv_rows, write_json, write_log
from src.state_guard_truthfulness import FIXED_ZERO_STATE_FIELDS, STATE_GUARD_METHOD_METADATA


FIELDS = ["check", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]
STATE_GUARD_ARTIFACTS = {
    "step50": "outputs/step50_state_mutation_guard/state_mutation_guard.json",
    "step51": "outputs/step51_state_mutation_guard/state_mutation_guard.json",
    "step52": "outputs/step52_state_mutation_guard/state_mutation_guard.json",
}


def main():
    os.chdir(ROOT)
    rows = []
    for step, relative_path in STATE_GUARD_ARTIFACTS.items():
        summary = read_json(relative_path)["summary"]
        for field in FIXED_ZERO_STATE_FIELDS:
            method_key = f"{field}_method"
            rows.append(
                check_row(
                    f"{step}_{method_key}",
                    method_key in summary and str(summary[method_key]).startswith(("not_applicable_proxy", "config_and_artifact_guard")),
                    summary.get(method_key, ""),
                    "fixed-zero state guard fields must disclose method/source",
                )
            )
        rows.append(
            check_row(
                f"{step}_state_guard_kind",
                summary.get("state_guard_kind") == STATE_GUARD_METHOD_METADATA["state_guard_kind"],
                summary.get("state_guard_kind", ""),
                "state guard must disclose hash plus artifact scan plus proxy fixed-zero fields",
            )
        )
        rows.append(
            check_row(
                f"{step}_fixed_zero_fields_disclosed",
                summary.get("fixed_zero_fields_disclosed") is True,
                summary.get("fixed_zero_fields_disclosed", ""),
                "fixed-zero fields must be explicitly disclosed",
            )
        )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "audited_step_count": len(STATE_GUARD_ARTIFACTS),
        "state_guard_truthfulness_audit_pass": False,
        "full_solver_validation_claim": False,
    }
    summary["state_guard_truthfulness_audit_pass"] = bool(summary["row_count"] == summary["pass_count"])
    if not summary["state_guard_truthfulness_audit_pass"]:
        raise RuntimeError(f"Step 54 state guard truthfulness audit failed: {summary}")

    out_dir = ROOT / "outputs" / "step54_state_guard_truthfulness_audit"
    write_csv_rows(out_dir / "state_guard_truthfulness.csv", rows, FIELDS)
    write_csv_rows(out_dir / "state_guard_truthfulness_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "state_guard_truthfulness.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 54 state guard truthfulness audit finished"
    write_log("logs/step54_state_guard_truthfulness_audit.log", [marker, f"pass_count={summary['pass_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
