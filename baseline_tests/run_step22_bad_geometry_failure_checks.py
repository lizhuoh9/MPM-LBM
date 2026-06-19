import os

from step22_common import BAD_GEOMETRY_FIELDS, ROOT, bad_geometry_row, load_geometry_config, write_json, write_rows_csv_npz


CASES = [
    ("bad_nonwatertight", "configs/step22_quality_bad_nonwatertight.json"),
    ("bad_degenerate", "configs/step22_quality_bad_degenerate.json"),
    ("bad_empty_voxel", "configs/step22_quality_bad_empty_voxel.json"),
]


def main():
    os.chdir(ROOT)
    out_dir = os.path.join(ROOT, "outputs", "step22_bad_geometry_failure_checks")
    rows = []
    reports = {}
    for case, config_path in CASES:
        row, report = bad_geometry_row(case, load_geometry_config(config_path))
        rows.append(row)
        reports[case] = report
        print(
            f"case={case}, strict_pass={row['strict_pass']}, expected_failure={row['expected_failure']}, "
            f"severity={row['severity']}, reasons={row['reasons']}"
        )
        if not row["expected_failure"]:
            raise RuntimeError(f"{case} did not produce an expected failure")

    write_rows_csv_npz(
        rows,
        os.path.join(out_dir, "bad_geometry_results.csv"),
        os.path.join(out_dir, "bad_geometry_results.npz"),
        BAD_GEOMETRY_FIELDS,
    )
    write_json(os.path.join(out_dir, "bad_geometry_reports.json"), reports)
    print("[OK] Step 22 bad geometry failure checks finished")


if __name__ == "__main__":
    main()
