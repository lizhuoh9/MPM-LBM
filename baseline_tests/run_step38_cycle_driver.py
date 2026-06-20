import os

import taichi as ti

from step38_common import (
    ROOT,
    STEP38_DRIVER_CONFIGS,
    STEP38_DRIVER_FIELDS,
    assert_driver_summary,
    case_name,
    driver_summary,
    run_step38_driver_case,
    write_json,
    write_log,
    write_rows_csv_npz,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step38_cycle_driver"
    rows = [run_step38_driver_case(config_path, out_dir / case_name(config_path)) for config_path in STEP38_DRIVER_CONFIGS]
    rows.sort(key=lambda row: (row["reaction_transfer_mode"], row["mode_class"]))
    summary = driver_summary(rows)
    assert_driver_summary(summary)

    write_rows_csv_npz(
        rows,
        out_dir / "cycle_driver_results.csv",
        out_dir / "cycle_driver_results.npz",
        STEP38_DRIVER_FIELDS,
    )
    write_json(out_dir / "cycle_driver_results.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 38 cycle driver finished"
    write_log("logs/step38_cycle_driver.log", [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
