import json
import os

import taichi as ti

from step41_common import (
    ROOT,
    STEP41_DRIVER_CONFIGS,
    STEP41_DRIVER_FIELDS,
    case_name,
    driver_summary,
    run_step41_driver_case,
    write_json,
    write_log,
    write_rows_csv_npz,
)
from src.selected_parameter_64_feasibility import assert_selected_parameter_driver_summary


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step41_64_selected_parameter_driver"
    rows = []
    for config_path in STEP41_DRIVER_CONFIGS:
        case = case_name(config_path)
        case_dir = out_dir / case
        row_cache = case_dir / "step41_driver_row.json"
        if row_cache.is_file():
            with row_cache.open("r", encoding="utf-8") as f:
                row = json.load(f)
        else:
            row = run_step41_driver_case(config_path, case_dir)
            write_json(row_cache, row)
        rows.append(row)
    rows.sort(key=lambda row: (row["reaction_transfer_mode"], row["mode_class"], float(row["wall_velocity_scale"])))
    summary = driver_summary(rows)
    assert_selected_parameter_driver_summary(summary)

    write_rows_csv_npz(
        rows,
        out_dir / "selected_parameter_64_results.csv",
        out_dir / "selected_parameter_64_results.npz",
        STEP41_DRIVER_FIELDS,
    )
    write_json(out_dir / "selected_parameter_64_results.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 41 64 selected parameter driver finished"
    write_log("logs/step41_64_selected_parameter_driver.log", [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
