import os

from step22_common import VOXEL_QUALITY_FIELDS, ROOT, load_geometry_config, quality_row, write_json, write_rows_csv_npz


def main():
    os.chdir(ROOT)
    out_dir = os.path.join(ROOT, "outputs", "step22_voxel_quality_sanity")
    row, report = quality_row("voxel_sphere", load_geometry_config("configs/step22_quality_voxel_sphere.json"))
    print(
        f"case=voxel_sphere, occupied_count={row['occupied_count']}, "
        f"components={row['connected_component_count']}, "
        f"largest_fraction={row['largest_component_fraction']:.9e}, pass={row['pass']}"
    )
    write_rows_csv_npz(
        [row],
        os.path.join(out_dir, "voxel_quality_results.csv"),
        os.path.join(out_dir, "voxel_quality_results.npz"),
        VOXEL_QUALITY_FIELDS,
    )
    write_json(os.path.join(out_dir, "voxel_quality_report.json"), report)
    print("[OK] Step 22 voxel quality sanity finished")


if __name__ == "__main__":
    main()
