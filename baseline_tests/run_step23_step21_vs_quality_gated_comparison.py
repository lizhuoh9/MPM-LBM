import os

from step23_common import ROOT, read_csv_rows, write_json
from src.run_utils import save_csv_rows


STEP21_CSVS = [
    "outputs/step21_voxel_sphere_48_modes/voxel_sphere_48_results.csv",
    "outputs/step21_mesh_cube_48_modes/mesh_cube_48_results.csv",
    "outputs/step21_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_results.csv",
    "outputs/step21_imported_geometry_64_feasibility/imported_geometry_64_results.csv",
]

STEP23_CSVS = [
    "outputs/step23_quality_gated_voxel_sphere_48_modes/voxel_sphere_48_quality_gated_results.csv",
    "outputs/step23_quality_gated_mesh_cube_48_modes/mesh_cube_48_quality_gated_results.csv",
    "outputs/step23_quality_gated_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_quality_gated_results.csv",
    "outputs/step23_quality_gated_imported_geometry_64_feasibility/imported_geometry_64_quality_gated_results.csv",
]

COMPARISON_FIELDS = [
    "case",
    "mode",
    "reaction_transfer_mode",
    "n_grid",
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


def _key(row):
    return (
        row["case"],
        row["mode"],
        row["reaction_transfer_mode"],
        int(float(row["n_grid"])),
    )


def _load_rows(paths):
    rows = []
    for relative_path in paths:
        rows.extend(read_csv_rows(os.path.join(ROOT, relative_path)))
    return rows


def _compare_rows(step21_rows, step23_rows):
    step21_by_key = {_key(row): row for row in step21_rows}
    rows = []
    for step23 in step23_rows:
        key = _key(step23)
        if key not in step21_by_key:
            raise RuntimeError(f"missing Step 21 comparison row for {key}")
        step21 = step21_by_key[key]
        row = {
            "case": key[0],
            "mode": key[1],
            "reaction_transfer_mode": key[2],
            "n_grid": key[3],
            "rho_min_delta": float(step23["rho_min"]) - float(step21["rho_min"]),
            "rho_max_delta": float(step23["rho_max"]) - float(step21["rho_max"]),
            "lbm_max_v_delta": float(step23["lbm_max_v"]) - float(step21["lbm_max_v"]),
            "mpm_min_J_delta": float(step23["mpm_min_J"]) - float(step21["mpm_min_J"]),
            "projected_mass_delta": float(step23["projected_mass"]) - float(step21["projected_mass"]),
            "active_cell_count_delta": int(float(step23["active_cell_count"])) - int(float(step21["active_cell_count"])),
            "stable_both": bool(_as_bool(step21["stable"]) and _as_bool(step23["stable"])),
            "notes": "finite trend comparison only; bitwise identity is not required",
        }
        _assert_comparison_row(row)
        rows.append(row)
    rows.sort(key=lambda row: (row["n_grid"], row["case"], row["mode"], row["reaction_transfer_mode"]))
    return rows


def _assert_comparison_row(row):
    import math

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
        raise RuntimeError(f"Step 21/23 comparison is not stable in both rows: {row}")


def _summary(rows):
    return {
        "required_comparable_row_count": len(rows),
        "stable_both_count": sum(1 for row in rows if _as_bool(row["stable_both"])),
        "max_abs_rho_min_delta": max(abs(float(row["rho_min_delta"])) for row in rows),
        "max_abs_rho_max_delta": max(abs(float(row["rho_max_delta"])) for row in rows),
        "max_abs_lbm_max_v_delta": max(abs(float(row["lbm_max_v_delta"])) for row in rows),
        "max_abs_mpm_min_J_delta": max(abs(float(row["mpm_min_J_delta"])) for row in rows),
        "max_abs_projected_mass_delta": max(abs(float(row["projected_mass_delta"])) for row in rows),
        "max_abs_active_cell_count_delta": max(abs(float(row["active_cell_count_delta"])) for row in rows),
    }


def main():
    os.chdir(ROOT)
    rows = _compare_rows(_load_rows(STEP21_CSVS), _load_rows(STEP23_CSVS))
    summary = _summary(rows)
    if summary["required_comparable_row_count"] < 15:
        raise RuntimeError(f"not enough comparable rows: {summary}")
    if summary["stable_both_count"] != len(rows):
        raise RuntimeError(f"not all comparable rows are stable: {summary}")

    out_dir = os.path.join(ROOT, "outputs", "step23_step21_vs_quality_gated_comparison")
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "step21_vs_step23_comparison.csv")
    json_path = os.path.join(out_dir, "step21_vs_step23_comparison.json")
    save_csv_rows(rows, csv_path, fieldnames=COMPARISON_FIELDS)
    write_json(json_path, summary)

    print("Step 23 Step 21 vs quality-gated comparison")
    print(f"required_comparable_row_count={summary['required_comparable_row_count']}")
    print(f"stable_both_count={summary['stable_both_count']}")
    print(f"max_abs_rho_min_delta={summary['max_abs_rho_min_delta']:.9e}")
    print(f"max_abs_projected_mass_delta={summary['max_abs_projected_mass_delta']:.9e}")
    print("[OK] Step 23 Step 21 vs quality-gated comparison finished")


if __name__ == "__main__":
    main()
