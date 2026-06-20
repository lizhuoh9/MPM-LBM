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
    static_rows = read_csv_rows("outputs/step34_static_driver_regression/static_driver_results.csv")
    prescribed_rows = read_csv_rows("outputs/step34_prescribed_interface_noop_smoke/prescribed_interface_noop_results.csv")
    rows = compare_static_to_prescribed(static_rows, prescribed_rows)
    summary = compare_summary(rows)
    summary.update(
        {
            "prescribed_report_count": sum(1 for row in prescribed_rows if row["boundary_motion_report_written"].lower() == "true"),
            "prescribed_no_op_pass_count": sum(1 for row in prescribed_rows if row["boundary_motion_no_op_pass"].lower() == "true"),
        }
    )
    if not summary["comparison_pass"] or int(summary["prescribed_report_count"]) != 2 or int(summary["prescribed_no_op_pass_count"]) != 2:
        raise RuntimeError(f"Step 34 no-op state guard failed: {summary}")

    out_dir = ROOT / "outputs" / "step34_noop_state_guard"
    write_csv_rows(out_dir / "noop_state_guard.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "noop_state_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 34 no-op state guard finished"
    write_log(
        "logs/step34_noop_state_guard.log",
        [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


def compare_static_to_prescribed(static_rows, prescribed_rows):
    static_by_transfer = {
        row["reaction_transfer_mode"]: row
        for row in static_rows
        if row["mode"] == "moving_boundary" and row["boundary_motion_mode"] == "static"
    }
    rows = []
    for prescribed in prescribed_rows:
        transfer = prescribed["reaction_transfer_mode"]
        if transfer not in static_by_transfer:
            raise RuntimeError(f"missing static Step 34 row for transfer={transfer}")
        rows.append(compare_row_pair(static_by_transfer[transfer], prescribed, f"noop_guard_{transfer}"))
    return rows


if __name__ == "__main__":
    main()
