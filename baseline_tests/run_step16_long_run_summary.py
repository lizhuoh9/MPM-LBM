import csv
import os
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step16_common import (  # noqa: E402
    LONG_SUMMARY_FIELDS,
    assert_long_run_stable,
    validate_mode_rows,
    write_json,
    write_summary_csv,
)


def read_csv_rows(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    import json

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_row(row):
    return {field: row.get(field, "") for field in LONG_SUMMARY_FIELDS}


def main():
    os.chdir(ROOT)
    out_dir = os.path.join(ROOT, "outputs", "step16_long_run_summary")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 16 long-run summary")
    rows = [
        normalize_row(read_json(os.path.join(ROOT, "outputs", "step16_long_box_48_moving_boundary", "long_run_summary.json"))),
        normalize_row(read_json(os.path.join(ROOT, "outputs", "step16_long_squid_proxy_48_moving_boundary", "long_run_summary.json"))),
        normalize_row(read_json(os.path.join(ROOT, "outputs", "step16_feasibility_64_moving_boundary", "long_run_summary.json"))),
    ]
    rows.extend(
        normalize_row(row)
        for row in read_csv_rows(os.path.join(ROOT, "outputs", "step16_64_mode_comparison", "mode_64_results.csv"))
    )

    for row in rows:
        assert_long_run_stable(row, require_moving_boundary=row["mode"] == "moving_boundary")
    validate_mode_rows([row for row in rows if row["case"].startswith("mode_compare_64_")])

    csv_path = os.path.join(out_dir, "step16_summary.csv")
    json_path = os.path.join(out_dir, "step16_summary.json")
    write_summary_csv(rows, csv_path)
    write_json(
        {
            "row_count": len(rows),
            "stable_rows": sum(1 for row in rows if str(row["stable"]).strip().lower() == "true"),
            "grid_references": sorted({int(float(row["n_grid"])) for row in rows}),
            "scope_note": "Step 16 long-run validation and 64^3 moving_boundary feasibility summary; not production validation.",
            "columns": LONG_SUMMARY_FIELDS,
            "rows": rows,
        },
        json_path,
    )

    print(f"row_count={len(rows)}")
    print(f"csv={csv_path}")
    print(f"json={json_path}")
    print("[OK] Step 16 long-run summary finished")


if __name__ == "__main__":
    main()
