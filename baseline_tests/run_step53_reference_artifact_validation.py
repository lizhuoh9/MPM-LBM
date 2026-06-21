import os

from step53_common import ROOT, STEP53_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log
from src.runtime_geometry_wall_velocity_support_scaling_audit import reference_validation_rows


FIELDS = ["check", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = reference_validation_rows(ROOT, STEP53_CONFIG_PATH)
    if not summary["reference_validation_pass"]:
        raise RuntimeError(f"Step 53 reference artifact validation failed: {summary}")
    out_dir = ROOT / "outputs" / "step53_reference_artifact_validation"
    write_csv_rows(out_dir / "reference_artifact_validation.csv", rows, FIELDS)
    write_csv_rows(out_dir / "reference_artifact_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "reference_artifact_validation.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 53 reference artifact validation finished"
    write_log("logs/step53_reference_artifact_validation.log", [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
