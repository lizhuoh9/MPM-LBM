import os

import taichi as ti

from step36_common import (
    ROOT,
    STEP36_DRIVER_FIELDS,
    STEP36_EXPERIMENTAL_DRIVER_CONFIGS,
    assert_driver_summary,
    can_reuse_step36_case,
    case_name,
    driver_summary,
    load_existing_step36_driver_case,
    run_step36_driver_case,
    write_json,
    write_log,
    write_rows_csv_npz,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step36_experimental_application_smoke"
    rows = []
    for config_path in STEP36_EXPERIMENTAL_DRIVER_CONFIGS:
        case_dir = out_dir / case_name(config_path)
        if can_reuse_step36_case(config_path, case_dir):
            rows.append(load_existing_step36_driver_case(config_path, case_dir))
        else:
            rows.append(run_step36_driver_case(config_path, case_dir))
    rows.sort(key=lambda row: (int(row["n_grid"]), row["reaction_transfer_mode"]))
    summary = driver_summary(rows)
    assert_driver_summary(summary, expected_rows=3, expected_reports=3)
    if int(summary["static_application_row_count"]) != 0 or int(summary["experimental_application_row_count"]) != 3:
        raise RuntimeError(f"Step 36 experimental smoke has wrong application split: {summary}")
    if int(summary["min_applied_cell_count"]) <= 0 or float(summary["max_applied_velocity_norm"]) > 0.01 + 1.0e-12:
        raise RuntimeError(f"Step 36 experimental application summary is invalid: {summary}")

    write_rows_csv_npz(
        rows,
        out_dir / "experimental_application_results.csv",
        out_dir / "experimental_application_results.npz",
        STEP36_DRIVER_FIELDS,
    )
    write_json(out_dir / "experimental_application_results.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 36 experimental application smoke finished"
    write_log(
        "logs/step36_experimental_application_smoke.log",
        [marker, f"row_count={len(rows)}", f"application_report_count={summary['application_report_count']}"],
    )
    print(f"row_count={len(rows)}")
    print(marker)


if __name__ == "__main__":
    main()
