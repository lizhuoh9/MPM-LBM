import os

from step43_common import ROOT, STEP43_GEOMETRY_MOTION_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log
from src.geometry_motion_interface import write_geometry_motion_interface_report


SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    out_dir = ROOT / "outputs" / "step43_geometry_motion_interface_report"
    payload = write_geometry_motion_interface_report(
        STEP43_GEOMETRY_MOTION_CONFIG_PATH,
        out_dir / "geometry_motion_interface_report.json",
        geometry_motion_mode="prescribed_kinematic",
    )
    summary = payload["summary"]
    if not summary["no_op_pass"]:
        raise RuntimeError(f"Step 43 geometry motion interface report failed: {summary}")
    write_csv_rows(out_dir / "geometry_motion_interface_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    marker = "[OK] Step 43 geometry motion interface report finished"
    write_log("logs/step43_geometry_motion_interface_report.log", [marker, f"displacement_row_count={summary['displacement_row_count']}", f"no_op_pass={summary['no_op_pass']}"])
    print(f"displacement_row_count={summary['displacement_row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
