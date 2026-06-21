import os

from step54_common import ROOT, check_row, read_json, summary_rows, write_csv_rows, write_json, write_log
from src.proxy_diagnostic_truthfulness import PROXY_RECORD_METADATA, proxy_metadata_present


FIELDS = ["check", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]
PROXY_ARTIFACTS = {
    "step50": "outputs/step50_one_cycle_envelope_matrix/one_cycle_envelope_matrix.json",
    "step51": "outputs/step51_transfer_comparison_matrix/transfer_comparison_matrix.json",
    "step52": "outputs/step52_48_feasibility_matrix/feasibility_matrix.json",
}


def main():
    os.chdir(ROOT)
    rows = []
    for step, relative_path in PROXY_ARTIFACTS.items():
        payload = read_json(relative_path)
        artifact_rows = payload["rows"]
        step_records = [record for row in artifact_rows for record in row["step_records"]]
        rows.append(
            check_row(
                f"{step}_row_proxy_metadata_present",
                all(proxy_metadata_present(row) for row in artifact_rows),
                len(artifact_rows),
                "every top-level proxy row must disclose record/source metadata",
            )
        )
        rows.append(
            check_row(
                f"{step}_step_record_proxy_metadata_present",
                all(proxy_metadata_present(record) for record in step_records),
                len(step_records),
                "every per-step proxy record must disclose record/source metadata",
            )
        )
        rows.append(
            check_row(
                f"{step}_solver_time_integration_false",
                all(row["solver_time_integration_run"] is False for row in artifact_rows),
                PROXY_RECORD_METADATA["solver_time_integration_run"],
                "Step 50/51/52 artifacts are proxy diagnostics, not solver time integration records",
            )
        )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "audited_step_count": len(PROXY_ARTIFACTS),
        "proxy_record_metadata_field_count": len(PROXY_RECORD_METADATA),
        "proxy_truthfulness_audit_pass": False,
        "real_jet_validation_claim": False,
        "full_solver_validation_claim": False,
    }
    summary["proxy_truthfulness_audit_pass"] = bool(summary["row_count"] == summary["pass_count"])
    if not summary["proxy_truthfulness_audit_pass"]:
        raise RuntimeError(f"Step 54 proxy diagnostic truthfulness audit failed: {summary}")

    out_dir = ROOT / "outputs" / "step54_proxy_diagnostic_truthfulness_audit"
    write_csv_rows(out_dir / "proxy_diagnostic_truthfulness.csv", rows, FIELDS)
    write_csv_rows(out_dir / "proxy_diagnostic_truthfulness_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "proxy_diagnostic_truthfulness.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 54 proxy diagnostic truthfulness audit finished"
    write_log("logs/step54_proxy_diagnostic_truthfulness_audit.log", [marker, f"pass_count={summary['pass_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
