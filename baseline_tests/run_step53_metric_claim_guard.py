import os

from step53_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.runtime_geometry_wall_velocity_support_scaling_claim_guard import claim_guard_rows


FIELDS = ["path", "flag", "forbidden_claim_count", "forbidden_claims_absent"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = claim_guard_rows(ROOT)
    if not summary["claim_guard_pass"]:
        raise RuntimeError(f"Step 53 metric claim guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step53_metric_claim_guard"
    write_csv_rows(out_dir / "metric_claim_guard.csv", rows, FIELDS)
    write_csv_rows(out_dir / "metric_claim_guard_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "metric_claim_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 53 metric claim guard finished"
    write_log("logs/step53_metric_claim_guard.log", [marker, f"scanned_file_count={summary['scanned_file_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
