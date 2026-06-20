import os

import taichi as ti

from step37_common import (
    ROOT,
    STEP37_DRIVER_CONFIGS,
    STEP37_DRIVER_FIELDS,
    assert_driver_summary,
    case_name,
    driver_summary,
    run_step37_driver_case,
    write_json,
    write_log,
    write_rows_csv_npz,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step37_application_window_driver"
    rows = [run_step37_driver_case(config_path, out_dir / case_name(config_path)) for config_path in STEP37_DRIVER_CONFIGS]
    rows.sort(key=lambda row: (row["reaction_transfer_mode"], row["mode_class"]))
    summary = driver_summary(rows)
    assert_driver_summary(summary)

    write_rows_csv_npz(
        rows,
        out_dir / "application_window_results.csv",
        out_dir / "application_window_results.npz",
        STEP37_DRIVER_FIELDS,
    )
    write_json(out_dir / "application_window_results.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 37 application window driver finished"
    write_log(
        "logs/step37_application_window_driver.log",
        [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
