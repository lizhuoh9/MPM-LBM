import os

from step27_common import ROOT, assert_step27_summary, read_csv_rows, short_driver_summary, write_json, write_log, write_rows_csv_npz
from src.real_geometry_feasibility import SHORT_DRIVER_FIELDS


CSV_PATHS = [
    "outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.csv",
    "outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.csv",
]


def main():
    os.chdir(ROOT)
    rows = []
    for path in CSV_PATHS:
        rows.extend(read_csv_rows(path))
    rows.sort(key=lambda row: (row["candidate_id"], row["mode"], row["reaction_transfer_mode"]))
    summary = short_driver_summary(rows)
    assert_step27_summary(summary)

    out_dir = ROOT / "outputs" / "step27_64_driver_summary"
    write_rows_csv_npz(rows, out_dir / "driver_64_summary.csv", out_dir / "driver_64_summary.npz", SHORT_DRIVER_FIELDS)
    write_json(out_dir / "driver_64_summary.json", {"driver_row_count": len(rows), "summary": summary, "rows": rows})
    marker = "[OK] Step 27 64 driver summary finished"
    write_log(
        "logs/step27_64_driver_summary.log",
        [
            marker,
            f"driver_row_count={summary['driver_row_count']}",
            f"stable_count={summary['stable_count']}",
            f"quality_report_count={summary['quality_report_count']}",
            f"max_driver_total_time={summary['max_driver_total_time']:.9e}",
        ],
    )
    print(f"driver_row_count={summary['driver_row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
