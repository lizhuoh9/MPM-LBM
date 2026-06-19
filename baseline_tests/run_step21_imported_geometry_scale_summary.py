import os

from step21_common import (
    ROOT,
    STEP21_SUMMARY_FIELDS,
    assert_driver_row,
    assert_projection_quality_row,
    assert_summary_row,
    read_csv_rows,
    write_json,
    write_rows_csv_npz,
)


DRIVER_INPUTS = [
    "outputs/step21_voxel_sphere_48_modes/voxel_sphere_48_results.csv",
    "outputs/step21_mesh_cube_48_modes/mesh_cube_48_results.csv",
    "outputs/step21_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_results.csv",
    "outputs/step21_imported_geometry_64_feasibility/imported_geometry_64_results.csv",
]

PROJECTION_INPUT = "outputs/step21_imported_geometry_projection_quality/projection_quality.csv"


def main():
    os.chdir(ROOT)
    driver_rows = []
    for relative_path in DRIVER_INPUTS:
        path = os.path.join(ROOT, relative_path)
        if not os.path.isfile(path):
            raise RuntimeError(f"missing required summary input: {relative_path}")
        rows = read_csv_rows(path)
        for row in rows:
            assert_driver_row(row)
        driver_rows.extend(rows)

    projection_path = os.path.join(ROOT, PROJECTION_INPUT)
    if not os.path.isfile(projection_path):
        raise RuntimeError(f"missing required summary input: {PROJECTION_INPUT}")
    projection_rows = read_csv_rows(projection_path)
    for row in projection_rows:
        assert_projection_quality_row(row)

    summary = {
        "stable": True,
        "required_row_count": len(driver_rows) + len(projection_rows),
        "driver_row_count": len(driver_rows),
        "projection_quality_row_count": len(projection_rows),
        "rho_min_global": min(float(row["rho_min"]) for row in driver_rows),
        "rho_max_global": max(float(row["rho_max"]) for row in driver_rows),
        "lbm_max_v_global": max(float(row["lbm_max_v"]) for row in driver_rows),
        "mpm_min_J_global": min(float(row["mpm_min_J"]) for row in driver_rows),
        "mpm_max_speed_global": max(float(row["mpm_max_speed"]) for row in driver_rows),
        "max_relative_mass_error": max(abs(float(row["relative_mass_error"])) for row in projection_rows),
        "large_file_count": 0,
        "notes": "Step 21 scale summary for synthetic imported geometry validation",
    }
    assert_summary_row(summary)

    out_dir = os.path.join(ROOT, "outputs", "step21_imported_geometry_scale_summary")
    write_rows_csv_npz(
        [summary],
        os.path.join(out_dir, "step21_summary.csv"),
        os.path.join(out_dir, "step21_summary.npz"),
        STEP21_SUMMARY_FIELDS,
    )
    write_json(os.path.join(out_dir, "step21_summary.json"), summary)
    print(f"driver_row_count={summary['driver_row_count']}")
    print(f"projection_quality_row_count={summary['projection_quality_row_count']}")
    print(f"required_row_count={summary['required_row_count']}")
    print("[OK] Step 21 imported geometry scale summary finished")


if __name__ == "__main__":
    main()
