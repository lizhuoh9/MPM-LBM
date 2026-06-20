import os

from step34_common import ROOT, STEP34_BOUNDARY_MOTION_CONFIG_PATH, summary_rows, write_csv_rows, write_log
from src.boundary_motion_interface import write_boundary_motion_interface_report


SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    out_dir = ROOT / "outputs" / "step34_boundary_motion_interface_report"
    payload = write_boundary_motion_interface_report(
        STEP34_BOUNDARY_MOTION_CONFIG_PATH,
        out_dir / "boundary_motion_interface_report.json",
        boundary_motion_mode="prescribed_kinematic",
    )
    summary = payload["summary"]
    assert_summary(summary)
    write_csv_rows(out_dir / "boundary_motion_interface_report_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    marker = "[OK] Step 34 boundary motion interface report finished"
    write_log(
        "logs/step34_boundary_motion_interface_report.log",
        [
            marker,
            f"schedule_row_count={summary['schedule_row_count']}",
            f"motion_mapping_row_count={summary['motion_mapping_row_count']}",
            f"no_op_pass={summary['no_op_pass']}",
        ],
    )
    print(f"schedule_row_count={summary['schedule_row_count']}")
    print(marker)


def assert_summary(summary):
    if summary["boundary_motion_mode"] != "prescribed_kinematic":
        raise RuntimeError(f"wrong boundary motion mode: {summary}")
    if summary["diagnostic_only"] is not True or summary["no_op_pass"] is not True:
        raise RuntimeError(f"Step 34 report must be diagnostic-only no-op: {summary}")
    if int(summary["schedule_row_count"]) != 81 or int(summary["motion_mapping_row_count"]) != 243:
        raise RuntimeError(f"Step 34 report has wrong schedule or motion counts: {summary}")
    if int(summary["tracked_region_count"]) != 3:
        raise RuntimeError(f"Step 34 report has wrong tracked-region count: {summary}")
    if int(summary["execution_flag_enabled_count"]) != 0:
        raise RuntimeError(f"Step 34 report has enabled execution flags: {summary}")
    if not summary["schedule_finite_pass"] or not summary["motion_finite_pass"] or not summary["motion_bounds_pass"]:
        raise RuntimeError(f"Step 34 report has invalid finite/bounds state: {summary}")


if __name__ == "__main__":
    main()
