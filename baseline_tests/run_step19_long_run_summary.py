import json
import os
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step19_common import (  # noqa: E402
    STEP19_AGGREGATE_FIELDS,
    aggregate_rows,
    read_csv_rows,
    write_step19_rows_csv_npz,
)


def _read_json_row(relative_path):
    path = os.path.join(ROOT, relative_path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    os.chdir(ROOT)
    out_dir = os.path.join(ROOT, "outputs", "step19_long_run_summary")
    os.makedirs(out_dir, exist_ok=True)

    rows = [
        aggregate_rows(
            "box_48_link_area_long",
            "outputs/step19_long_box_48_link_area/long_run_summary.json",
            [_read_json_row("outputs/step19_long_box_48_link_area/long_run_summary.json")],
            notes="48^3 box link-area long-run",
        ),
        aggregate_rows(
            "squid_proxy_48_link_area_long",
            "outputs/step19_long_squid_proxy_48_link_area/long_run_summary.json",
            [_read_json_row("outputs/step19_long_squid_proxy_48_link_area/long_run_summary.json")],
            notes="48^3 procedural squid_proxy link-area long-run",
        ),
        aggregate_rows(
            "box_64_link_area_feasibility",
            "outputs/step19_feasibility_64_link_area/long_run_summary.json",
            [_read_json_row("outputs/step19_feasibility_64_link_area/long_run_summary.json")],
            notes="64^3 box link-area feasibility",
        ),
        aggregate_rows(
            "engineering_vs_link_area_64",
            "outputs/step19_compare_64_engineering_vs_link_area/comparison_64.csv",
            read_csv_rows(os.path.join(ROOT, "outputs", "step19_compare_64_engineering_vs_link_area", "comparison_64.csv")),
            notes="64^3 engineering-vs-link-area comparison",
        ),
        aggregate_rows(
            "engineering_vs_link_area_48",
            "outputs/step19_compare_48_long_engineering_vs_link_area/comparison_48_long.csv",
            read_csv_rows(os.path.join(ROOT, "outputs", "step19_compare_48_long_engineering_vs_link_area", "comparison_48_long.csv")),
            notes="48^3 long engineering-vs-link-area comparison",
        ),
        aggregate_rows(
            "step18_regression",
            "outputs/step19_regression_step18/regression_results.csv",
            read_csv_rows(os.path.join(ROOT, "outputs", "step19_regression_step18", "regression_results.csv")),
            notes="Step 18 behavior regression",
        ),
    ]

    if not all(bool(row["stable"]) for row in rows):
        raise RuntimeError("Step 19 summary contains unstable aggregate rows")

    csv_path = os.path.join(out_dir, "step19_summary.csv")
    json_path = os.path.join(out_dir, "step19_summary.json")
    npz_path = os.path.join(out_dir, "step19_summary.npz")
    write_step19_rows_csv_npz(rows, csv_path, npz_path, STEP19_AGGREGATE_FIELDS)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, sort_keys=True)
        f.write("\n")

    for row in rows:
        print(
            f"{row['summary_case']} stable={row['stable']}, row_count={row['row_count']}, "
            f"rho_min={float(row['rho_min_global']):.9e}, rho_max={float(row['rho_max_global']):.9e}, "
            f"area_scale_range=[{float(row['area_scale_min']):.9e}, {float(row['area_scale_max']):.9e}]"
        )
    print("[OK] Step 19 long-run summary finished")


if __name__ == "__main__":
    main()
