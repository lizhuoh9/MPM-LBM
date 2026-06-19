import os
import statistics

from step24_common import ROOT, read_csv_rows, read_json, write_json, write_log
from src.run_utils import save_csv_rows


STEP24_CSVS = [
    "outputs/step24_strict_voxel_sphere_48_long/voxel_sphere_48_strict_long_results.csv",
    "outputs/step24_strict_mesh_cube_48_long/mesh_cube_48_strict_long_results.csv",
    "outputs/step24_strict_mesh_ellipsoid_48_long/mesh_ellipsoid_48_strict_long_results.csv",
    "outputs/step24_strict_imported_geometry_64_feasibility/imported_geometry_64_strict_feasibility_results.csv",
]

TIMING_FIELDS = [
    "case",
    "mode",
    "reaction_transfer_mode",
    "n_grid",
    "init_time",
    "projection_time",
    "coupling_time",
    "lbm_step_time",
    "mpm_substep_time",
    "diagnostics_time",
    "export_time",
    "total_time",
    "quality_report_size_bytes",
    "notes",
]


def _load_driver_rows():
    rows = []
    for relative_path in STEP24_CSVS:
        rows.extend(read_csv_rows(relative_path))
    return rows


def _timing_rows(driver_rows):
    rows = []
    for row in driver_rows:
        timing = read_json(row["driver_timing_path"])
        quality_report_path = os.path.join(ROOT, row["quality_report_path"])
        output = {
            "case": row["case"],
            "mode": row["mode"],
            "reaction_transfer_mode": row["reaction_transfer_mode"],
            "n_grid": int(float(row["n_grid"])),
            "init_time": float(timing.get("init_time", 0.0)),
            "projection_time": float(timing.get("projection_time", 0.0)),
            "coupling_time": float(timing.get("coupling_time", 0.0)),
            "lbm_step_time": float(timing.get("lbm_step_time", 0.0)),
            "mpm_substep_time": float(timing.get("mpm_substep_time", 0.0)),
            "diagnostics_time": float(timing.get("diagnostics_time", 0.0)),
            "export_time": float(timing.get("export_time", 0.0)),
            "total_time": float(timing.get("total_time", 0.0)),
            "quality_report_size_bytes": int(os.path.getsize(quality_report_path)),
            "notes": "workflow diagnostic only; not a production benchmark",
        }
        if output["total_time"] <= 0.0:
            raise RuntimeError(f"driver timing missing total_time: {row}")
        rows.append(output)
    rows.sort(key=lambda item: (item["n_grid"], item["case"], item["reaction_transfer_mode"]))
    return rows


def _summary(rows):
    total_times = [float(row["total_time"]) for row in rows]
    report_sizes = [int(row["quality_report_size_bytes"]) for row in rows]
    return {
        "row_count": len(rows),
        "median_total_time": statistics.median(total_times) if total_times else 0.0,
        "max_total_time": max(total_times) if total_times else 0.0,
        "quality_report_count": len(report_sizes),
        "quality_report_total_size_bytes": sum(report_sizes),
        "quality_report_max_size_bytes": max(report_sizes) if report_sizes else 0,
        "scope_note": "Timing is a workflow and artifact-budget diagnostic only, not a production benchmark.",
    }


def main():
    os.chdir(ROOT)
    rows = _timing_rows(_load_driver_rows())
    summary = _summary(rows)
    if summary["row_count"] != 9 or summary["quality_report_count"] != 9:
        raise RuntimeError(f"Step 24 timing summary expected 9 rows: {summary}")

    out_dir = os.path.join(ROOT, "outputs", "step24_timing_overhead_summary")
    os.makedirs(out_dir, exist_ok=True)
    save_csv_rows(rows, os.path.join(out_dir, "step24_timing_summary.csv"), fieldnames=TIMING_FIELDS)
    write_json(os.path.join(out_dir, "step24_timing_summary.json"), summary)

    marker = "[OK] Step 24 timing overhead summary finished"
    write_log(
        "logs/step24_timing_overhead_summary.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"median_total_time={summary['median_total_time']:.9e}",
            f"max_total_time={summary['max_total_time']:.9e}",
            f"quality_report_count={summary['quality_report_count']}",
        ],
    )
    print("Step 24 timing overhead summary")
    print(f"row_count={summary['row_count']}")
    print(f"median_total_time={summary['median_total_time']:.9e}")
    print(f"max_total_time={summary['max_total_time']:.9e}")
    print(marker)


if __name__ == "__main__":
    main()
