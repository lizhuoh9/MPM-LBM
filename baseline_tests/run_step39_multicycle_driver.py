import os

import taichi as ti

from step39_common import (
    ROOT,
    STEP39_DRIVER_CONFIGS,
    STEP39_DRIVER_FIELDS,
    assert_driver_summary,
    case_name,
    driver_summary,
    run_step39_driver_case,
    write_json,
    write_log,
    write_rows_csv_npz,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step39_multicycle_driver"
    rows = [run_step39_driver_case(config_path, out_dir / case_name(config_path)) for config_path in STEP39_DRIVER_CONFIGS]
    rows.sort(key=lambda row: (row["reaction_transfer_mode"], row["mode_class"]))
    summary = driver_summary(rows)
    assert_driver_summary(summary)

    write_rows_csv_npz(
        rows,
        out_dir / "multicycle_driver_results.csv",
        out_dir / "multicycle_driver_results.npz",
        STEP39_DRIVER_FIELDS,
    )
    write_json(out_dir / "multicycle_driver_results.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 39 multicycle driver finished"
    write_log("logs/step39_multicycle_driver.log", [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
