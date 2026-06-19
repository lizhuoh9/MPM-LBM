import os

from step22_common import MESH_QUALITY_FIELDS, ROOT, load_geometry_config, quality_row, write_json, write_rows_csv_npz


CASES = [
    ("mesh_cube", "configs/step22_quality_mesh_cube.json"),
    ("mesh_ellipsoid", "configs/step22_quality_mesh_ellipsoid.json"),
]


def main():
    os.chdir(ROOT)
    out_dir = os.path.join(ROOT, "outputs", "step22_mesh_quality_sanity")
    rows = []
    reports = {}
    for case, config_path in CASES:
        row, report = quality_row(case, load_geometry_config(config_path), strict=False)
        rows.append(row)
        reports[case] = report
        print(
            f"case={case}, vertices={row['vertices_count']}, faces={row['faces_count']}, "
            f"boundary_edges={row['boundary_edge_count']}, degenerate_faces={row['degenerate_face_count']}, "
            f"pass={row['pass']}"
        )

    write_rows_csv_npz(
        rows,
        os.path.join(out_dir, "mesh_quality_results.csv"),
        os.path.join(out_dir, "mesh_quality_results.npz"),
        MESH_QUALITY_FIELDS,
    )
    write_json(os.path.join(out_dir, "mesh_quality_reports.json"), reports)
    print("[OK] Step 22 mesh quality sanity finished")


if __name__ == "__main__":
    main()
