import os

import taichi as ti

from step40_common import (
    ROOT,
    STEP40_DRIVER_CONFIGS,
    STEP40_DRIVER_FIELDS,
    case_name,
    driver_summary,
    run_step40_driver_case,
    write_json,
    write_log,
    write_rows_csv_npz,
)
from src.jet_cycle_parameter_sensitivity import assert_parameter_driver_summary


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step40_parameter_sweep_driver"
    rows = []
    for config_path in STEP40_DRIVER_CONFIGS:
        case = case_name(config_path)
        case_dir = out_dir / case
        row_cache = case_dir / "step40_driver_row.json"
        if row_cache.is_file():
            with row_cache.open("r", encoding="utf-8") as f:
                import json

                row = json.load(f)
        else:
            row = run_step40_driver_case(config_path, case_dir)
            write_json(row_cache, row)
        rows.append(row)
    rows.sort(key=lambda row: (row["reaction_transfer_mode"], row["mode_class"], float(row["wall_velocity_scale"])))
    summary = driver_summary(rows)
    assert_parameter_driver_summary(summary)

    write_rows_csv_npz(
        rows,
        out_dir / "parameter_sweep_results.csv",
        out_dir / "parameter_sweep_results.npz",
        STEP40_DRIVER_FIELDS,
    )
    write_json(out_dir / "parameter_sweep_results.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 40 parameter sweep driver finished"
    write_log("logs/step40_parameter_sweep_driver.log", [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
