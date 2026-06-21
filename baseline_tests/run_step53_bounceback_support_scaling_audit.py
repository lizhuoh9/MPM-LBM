import os

from step53_common import ROOT, STEP53_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log
from src.runtime_geometry_wall_velocity_support_scaling_audit import bounceback_support_rows


FIELDS = [
    "metric",
    "bb_link_count_32",
    "bb_link_count_48",
    "bb_link_count_ratio",
    "bb_link_growth_observed",
    "bb_link_non_decreasing",
    "bb_link_used_as_area_convergence_metric",
    "bb_link_support_status",
    "audit_pass",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = bounceback_support_rows(ROOT, STEP53_CONFIG_PATH)
    if not summary["bounceback_support_audit_pass"]:
        raise RuntimeError(f"Step 53 bounce-back support audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step53_bounceback_support_scaling_audit"
    write_csv_rows(out_dir / "bounceback_support_scaling.csv", rows, FIELDS)
    write_csv_rows(out_dir / "bounceback_support_scaling_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "bounceback_support_scaling.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 53 bounce-back support scaling audit finished"
    write_log("logs/step53_bounceback_support_scaling_audit.log", [marker, f"bb_link_count_ratio={summary['bb_link_count_ratio']}"])
    print(marker)


if __name__ == "__main__":
    main()
