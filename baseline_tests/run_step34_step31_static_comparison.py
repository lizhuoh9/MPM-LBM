import os

from step34_common import (
    ROOT,
    compare_row_pair,
    compare_summary,
    fieldnames_from_rows,
    read_csv_rows,
    write_csv_rows,
    write_json,
    write_log,
)


def main():
    os.chdir(ROOT)
    step31_rows = read_csv_rows("outputs/step31_static_driver_smoke/static_driver_results.csv")
    step34_rows = read_csv_rows("outputs/step34_static_driver_regression/static_driver_results.csv")
    rows = compare_step31_to_step34(step31_rows, step34_rows)
    summary = compare_summary(rows)
    if not summary["comparison_pass"]:
        raise RuntimeError(f"Step 34 Step 31 static comparison failed: {summary}")

    out_dir = ROOT / "outputs" / "step34_step31_static_comparison"
    write_csv_rows(out_dir / "step31_static_comparison.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "step31_static_comparison.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 34 Step 31 static comparison finished"
    write_log(
        "logs/step34_step31_static_comparison.log",
        [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


def compare_step31_to_step34(step31_rows, step34_rows):
    step31_by_key = {(row["mode"], row["reaction_transfer_mode"]): row for row in step31_rows}
    step34_by_key = {(row["mode"], row["reaction_transfer_mode"]): row for row in step34_rows}
    rows = []
    for key in sorted(step31_by_key):
        if key not in step34_by_key:
            raise RuntimeError(f"missing Step 34 static row for {key}")
        rows.append(
            compare_row_pair(
                step31_by_key[key],
                step34_by_key[key],
                f"step31_vs_step34_{key[0]}_{key[1]}",
                tolerance=1.0e-5,
            )
        )
    return rows


if __name__ == "__main__":
    main()
