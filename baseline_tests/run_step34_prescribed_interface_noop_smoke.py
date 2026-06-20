import os

import taichi as ti

from step34_common import (
    ROOT,
    STEP34_DRIVER_FIELDS,
    STEP34_PRESCRIBED_DRIVER_CONFIGS,
    assert_driver_summary,
    case_name,
    compare_row_pair,
    compare_summary,
    driver_summary,
    fieldnames_from_rows,
    read_csv_rows,
    run_step34_driver_case,
    write_csv_rows,
    write_json,
    write_log,
    write_rows_csv_npz,
)


TRANSFER_ORDER = {"engineering": 0, "link_area_experimental": 1}


def main():
    os.chdir(ROOT)
    static_csv = ROOT / "outputs" / "step34_static_driver_regression" / "static_driver_results.csv"
    if not static_csv.is_file():
        raise RuntimeError("run Step 34 static driver regression before prescribed interface no-op smoke")
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step34_prescribed_interface_noop_smoke"
    rows = [run_step34_driver_case(config_path, out_dir / case_name(config_path)) for config_path in STEP34_PRESCRIBED_DRIVER_CONFIGS]
    rows.sort(key=lambda row: TRANSFER_ORDER[row["reaction_transfer_mode"]])
    summary = driver_summary(rows)
    assert_driver_summary(summary, expected_rows=2, expected_boundary_reports=2)
    if int(summary["prescribed_boundary_motion_row_count"]) != 2:
        raise RuntimeError(f"Step 34 prescribed smoke has wrong boundary mode split: {summary}")

    static_rows = read_csv_rows(static_csv)
    comparison_rows = compare_to_static(static_rows, rows)
    comparison_summary = compare_summary(comparison_rows)
    if not comparison_summary["comparison_pass"]:
        raise RuntimeError(f"Step 34 prescribed no-op comparison failed: {comparison_summary}")

    write_rows_csv_npz(
        rows,
        out_dir / "prescribed_interface_noop_results.csv",
        out_dir / "prescribed_interface_noop_results.npz",
        STEP34_DRIVER_FIELDS,
    )
    write_json(out_dir / "prescribed_interface_noop_results.json", {"row_count": len(rows), "summary": summary, "rows": rows})
    write_csv_rows(out_dir / "prescribed_interface_noop_comparison.csv", comparison_rows, fieldnames_from_rows(comparison_rows))
    write_json(out_dir / "prescribed_interface_noop_comparison.json", {"summary": comparison_summary, "rows": comparison_rows})
    marker = "[OK] Step 34 prescribed interface no-op smoke finished"
    write_log(
        "logs/step34_prescribed_interface_noop_smoke.log",
        [marker, f"row_count={len(rows)}", f"boundary_report_count={summary['boundary_report_count']}"],
    )
    print(f"row_count={len(rows)}")
    print(marker)


def compare_to_static(static_rows, prescribed_rows):
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
        rows.append(compare_row_pair(static_by_transfer[transfer], prescribed, f"static_vs_prescribed_{transfer}"))
    return rows


if __name__ == "__main__":
    main()
