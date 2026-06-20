import os

from step36_common import (
    ROOT,
    compare_static_experimental_rows,
    compare_summary,
    fieldnames_from_rows,
    read_csv_rows,
    write_csv_rows,
    write_json,
    write_log,
)


def main():
    os.chdir(ROOT)
    static_rows = read_csv_rows("outputs/step36_static_regression_smoke/static_regression_results.csv")
    experimental_rows = read_csv_rows("outputs/step36_experimental_application_smoke/experimental_application_results.csv")
    rows = compare_static_experimental_rows(static_rows, experimental_rows)
    summary = compare_summary(rows)
    if not bool(summary["comparison_pass"]):
        raise RuntimeError(f"Step 36 static-vs-experimental comparison failed: {summary}")

    out_dir = ROOT / "outputs" / "step36_static_vs_experimental_comparison"
    write_csv_rows(out_dir / "static_vs_experimental.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "static_vs_experimental.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 36 static vs experimental comparison finished"
    write_log(
        "logs/step36_static_vs_experimental_comparison.log",
        [marker, f"row_count={summary['row_count']}", f"comparison_pass={summary['comparison_pass']}"],
    )
    print(f"comparison_pass={summary['comparison_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
