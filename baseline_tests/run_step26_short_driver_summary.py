import math
import os

from step26_common import ROOT, read_csv_rows, write_json, write_log, write_rows_csv_npz
from src.real_geometry_feasibility import SHORT_DRIVER_FIELDS


CSV_PATHS = [
    "outputs/step26_short_driver_mesh_48_modes/mesh_48_short_driver_results.csv",
    "outputs/step26_short_driver_voxel_48_modes/voxel_48_short_driver_results.csv",
]


def main():
    os.chdir(ROOT)
    rows = []
    for path in CSV_PATHS:
        rows.extend(read_csv_rows(path))
    rows.sort(key=lambda row: (row["candidate_id"], row["mode"], row["reaction_transfer_mode"]))
    summary = _summary(rows)
    _assert_summary(summary)

    out_dir = ROOT / "outputs" / "step26_short_driver_summary"
    write_rows_csv_npz(rows, out_dir / "short_driver_summary.csv", out_dir / "short_driver_summary.npz", SHORT_DRIVER_FIELDS)
    write_json(out_dir / "short_driver_summary.json", {"driver_row_count": len(rows), "summary": summary, "rows": rows})
    marker = "[OK] Step 26 short driver summary finished"
    write_log(
        "logs/step26_short_driver_summary.log",
        [
            marker,
            f"driver_row_count={summary['driver_row_count']}",
            f"stable_count={summary['stable_count']}",
            f"quality_report_count={summary['quality_report_count']}",
            f"max_step26_driver_total_time={summary['max_step26_driver_total_time']:.9e}",
        ],
    )
    print(f"driver_row_count={summary['driver_row_count']}")
    print(marker)


def _summary(rows):
    timings = [_read_timing(row["driver_timing_path"]) for row in rows]
    total_times = [float(item.get("total_time", 0.0)) for item in timings]
    return {
        "driver_row_count": len(rows),
        "candidate_count": len({row["candidate_id"] for row in rows}),
        "mode_transfer_count": len({(row["mode"], row["reaction_transfer_mode"]) for row in rows}),
        "stable_count": sum(1 for row in rows if _as_bool(row["stable"])),
        "quality_report_count": sum(1 for row in rows if (ROOT / row["quality_report_path"]).is_file()),
        "quality_pass_count": sum(1 for row in rows if _as_bool(row["quality_pass"])),
        "strict_count": sum(1 for row in rows if _as_bool(row["quality_gate_strict"])),
        "min_rho_min_global": min(float(row["rho_min_global"]) for row in rows),
        "max_rho_max_global": max(float(row["rho_max_global"]) for row in rows),
        "max_lbm_max_v_global": max(float(row["lbm_max_v_global"]) for row in rows),
        "min_mpm_min_J_global": min(float(row["mpm_min_J_global"]) for row in rows),
        "max_mpm_max_speed_global": max(float(row["mpm_max_speed_global"]) for row in rows),
        "min_projected_mass": min(float(row["projected_mass"]) for row in rows),
        "min_active_cell_count": min(int(float(row["active_cell_count"])) for row in rows),
        "max_step26_driver_total_time": max(total_times) if total_times else 0.0,
        "scope_note": "Step 26 short driver feasibility only; not real squid validation.",
    }


def _assert_summary(summary):
    if int(summary["driver_row_count"]) != 8:
        raise RuntimeError(f"expected 8 Step 26 driver rows: {summary}")
    if int(summary["candidate_count"]) != 2 or int(summary["mode_transfer_count"]) != 4:
        raise RuntimeError(f"Step 26 short driver matrix shape is wrong: {summary}")
    if int(summary["stable_count"]) != 8 or int(summary["quality_report_count"]) != 8:
        raise RuntimeError(f"all Step 26 short driver rows must be stable and report-backed: {summary}")
    if int(summary["quality_pass_count"]) != 8 or int(summary["strict_count"]) != 8:
        raise RuntimeError(f"all Step 26 short driver rows must pass strict quality gates: {summary}")
    if float(summary["min_rho_min_global"]) <= 0.95 or float(summary["max_rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 26 density summary is out of range: {summary}")
    if float(summary["max_lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 26 velocity summary is out of range: {summary}")
    if float(summary["min_mpm_min_J_global"]) <= 0.0 or float(summary["max_mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"Step 26 MPM summary is out of range: {summary}")
    if float(summary["min_projected_mass"]) <= 0.0 or int(summary["min_active_cell_count"]) <= 0:
        raise RuntimeError(f"Step 26 projection summary is invalid: {summary}")
    if not math.isfinite(float(summary["max_step26_driver_total_time"])) or float(summary["max_step26_driver_total_time"]) <= 0.0:
        raise RuntimeError(f"Step 26 driver timing summary is invalid: {summary}")


def _read_timing(path):
    import json

    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


if __name__ == "__main__":
    main()
