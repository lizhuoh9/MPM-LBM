import math
import os

from step24_common import ROOT, read_csv_rows, row_key, write_json, write_log
from src.run_utils import save_csv_rows


STEP23_CSVS = [
    "outputs/step23_quality_gated_voxel_sphere_48_modes/voxel_sphere_48_quality_gated_results.csv",
    "outputs/step23_quality_gated_mesh_cube_48_modes/mesh_cube_48_quality_gated_results.csv",
    "outputs/step23_quality_gated_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_quality_gated_results.csv",
    "outputs/step23_quality_gated_imported_geometry_64_feasibility/imported_geometry_64_quality_gated_results.csv",
]

STEP24_CSVS = [
    "outputs/step24_strict_voxel_sphere_48_long/voxel_sphere_48_strict_long_results.csv",
    "outputs/step24_strict_mesh_cube_48_long/mesh_cube_48_strict_long_results.csv",
    "outputs/step24_strict_mesh_ellipsoid_48_long/mesh_ellipsoid_48_strict_long_results.csv",
    "outputs/step24_strict_imported_geometry_64_feasibility/imported_geometry_64_strict_feasibility_results.csv",
]

COMPARISON_FIELDS = [
    "case",
    "mode",
    "reaction_transfer_mode",
    "n_grid",
    "compare_step",
    "comparison_status",
    "rho_min_delta",
    "rho_max_delta",
    "lbm_max_v_delta",
    "mpm_min_J_delta",
    "projected_mass_delta",
    "active_cell_count_delta",
    "stable_both",
    "notes",
]


def _as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _load_rows(paths):
    rows = []
    for relative_path in paths:
        rows.extend(read_csv_rows(relative_path))
    return rows


def _diagnostics_row_from_report_path(report_path, compare_step):
    out_dir = os.path.dirname(os.path.join(ROOT, report_path))
    rows = read_csv_rows(os.path.join(out_dir, "diagnostics_timeseries.csv"))
    for row in rows:
        if int(float(row["step"])) == int(compare_step):
            return row
    raise RuntimeError(f"missing diagnostics step {compare_step} under {out_dir}")


def _compare(step24_rows, step23_rows):
    step23_by_key = {row_key(row): row for row in step23_rows}
    rows = []
    for step24 in step24_rows:
        key = row_key(step24)
        compare_step = 10 if int(float(step24["n_grid"])) == 48 else 5
        if key not in step23_by_key:
            rows.append(
                {
                    "case": key[0],
                    "mode": key[1],
                    "reaction_transfer_mode": key[2],
                    "n_grid": key[3],
                    "compare_step": compare_step,
                    "comparison_status": "not_comparable_step23_overlap_missing",
                    "rho_min_delta": 0.0,
                    "rho_max_delta": 0.0,
                    "lbm_max_v_delta": 0.0,
                    "mpm_min_J_delta": 0.0,
                    "projected_mass_delta": 0.0,
                    "active_cell_count_delta": 0,
                    "stable_both": bool(_as_bool(step24["stable"])),
                    "notes": "Step 24-only row; accepted through strict stability and quality report gates",
                }
            )
            continue

        step23 = step23_by_key[key]
        step24_diag = _diagnostics_row_from_report_path(step24["quality_report_path"], compare_step)
        step23_diag = _diagnostics_row_from_report_path(step23["quality_report_path"], compare_step)
        row = {
            "case": key[0],
            "mode": key[1],
            "reaction_transfer_mode": key[2],
            "n_grid": key[3],
            "compare_step": compare_step,
            "comparison_status": "compared",
            "rho_min_delta": float(step24_diag["rho_min"]) - float(step23_diag["rho_min"]),
            "rho_max_delta": float(step24_diag["rho_max"]) - float(step23_diag["rho_max"]),
            "lbm_max_v_delta": float(step24_diag["lbm_max_v"]) - float(step23_diag["lbm_max_v"]),
            "mpm_min_J_delta": float(step24_diag["mpm_min_J"]) - float(step23_diag["mpm_min_J"]),
            "projected_mass_delta": float(step24_diag["projected_mass"]) - float(step23_diag["projected_mass"]),
            "active_cell_count_delta": int(float(step24_diag["active_cell_count"]))
            - int(float(step23_diag["active_cell_count"])),
            "stable_both": bool(_as_bool(step23["stable"]) and _as_bool(step24["stable"])),
            "notes": "strict quality gate prefix comparison; bitwise identity is not required",
        }
        _assert_comparison_row(row)
        rows.append(row)
    rows.sort(key=lambda item: (int(item["n_grid"]), item["case"], item["reaction_transfer_mode"]))
    return rows


def _assert_comparison_row(row):
    for key in (
        "rho_min_delta",
        "rho_max_delta",
        "lbm_max_v_delta",
        "mpm_min_J_delta",
        "projected_mass_delta",
        "active_cell_count_delta",
    ):
        if not math.isfinite(float(row[key])):
            raise RuntimeError(f"non-finite comparison delta {key}: {row}")
    if not _as_bool(row["stable_both"]):
        raise RuntimeError(f"Step 23/24 comparison is not stable in both rows: {row}")
    thresholds = {
        "rho_min_delta": 1.0e-5,
        "rho_max_delta": 1.0e-5,
        "lbm_max_v_delta": 1.0e-5,
        "mpm_min_J_delta": 1.0e-5,
        "projected_mass_delta": 1.0e-5,
    }
    for key, threshold in thresholds.items():
        if abs(float(row[key])) > threshold:
            raise RuntimeError(f"{key} exceeds Step 24 prefix threshold: {row}")
    if int(row["active_cell_count_delta"]) != 0:
        raise RuntimeError(f"active_cell_count_delta must be zero: {row}")


def _summary(rows):
    compared = [row for row in rows if row["comparison_status"] == "compared"]
    missing = [row for row in rows if row["comparison_status"] != "compared"]
    return {
        "row_count": len(rows),
        "compared_row_count": len(compared),
        "missing_overlap_count": len(missing),
        "stable_both_count": sum(1 for row in rows if _as_bool(row["stable_both"])),
        "max_abs_rho_min_delta": max((abs(float(row["rho_min_delta"])) for row in compared), default=0.0),
        "max_abs_rho_max_delta": max((abs(float(row["rho_max_delta"])) for row in compared), default=0.0),
        "max_abs_lbm_max_v_delta": max((abs(float(row["lbm_max_v_delta"])) for row in compared), default=0.0),
        "max_abs_mpm_min_J_delta": max((abs(float(row["mpm_min_J_delta"])) for row in compared), default=0.0),
        "max_abs_projected_mass_delta": max(
            (abs(float(row["projected_mass_delta"])) for row in compared), default=0.0
        ),
        "max_abs_active_cell_count_delta": max(
            (abs(float(row["active_cell_count_delta"])) for row in compared), default=0.0
        ),
    }


def main():
    os.chdir(ROOT)
    rows = _compare(_load_rows(STEP24_CSVS), _load_rows(STEP23_CSVS))
    summary = _summary(rows)
    if summary["row_count"] != 9:
        raise RuntimeError(f"expected 9 Step 24 comparison rows, got {summary}")
    if summary["compared_row_count"] < 7:
        raise RuntimeError(f"expected at least 7 Step 23 overlaps, got {summary}")
    if summary["stable_both_count"] != len(rows):
        raise RuntimeError(f"not all comparison rows are stable: {summary}")

    out_dir = os.path.join(ROOT, "outputs", "step24_step23_prefix_comparison")
    os.makedirs(out_dir, exist_ok=True)
    save_csv_rows(rows, os.path.join(out_dir, "step23_prefix_comparison.csv"), fieldnames=COMPARISON_FIELDS)
    write_json(os.path.join(out_dir, "step23_prefix_comparison.json"), summary)

    marker = "[OK] Step 24 Step 23 prefix comparison finished"
    write_log(
        "logs/step24_step23_prefix_comparison.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"compared_row_count={summary['compared_row_count']}",
            f"missing_overlap_count={summary['missing_overlap_count']}",
        ],
    )
    print("Step 24 Step 23 prefix comparison")
    print(f"row_count={summary['row_count']}")
    print(f"compared_row_count={summary['compared_row_count']}")
    print(f"missing_overlap_count={summary['missing_overlap_count']}")
    print(f"max_abs_rho_min_delta={summary['max_abs_rho_min_delta']:.9e}")
    print(f"max_abs_projected_mass_delta={summary['max_abs_projected_mass_delta']:.9e}")
    print(marker)


if __name__ == "__main__":
    main()
