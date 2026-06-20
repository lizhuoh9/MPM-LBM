import os

import taichi as ti

from step43_common import (
    ROOT,
    STEP43_DRIVER_FIELDS,
    STEP43_STATIC_DRIVER_CONFIGS,
    assert_driver_summary,
    case_name,
    driver_summary,
    run_step43_driver_case,
    write_json,
    write_log,
    write_rows_csv_npz,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.cpu, default_fp=ti.f32, random_seed=0, cpu_max_num_threads=1, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step43_static_driver_regression"
    rows = []
    for config_path in STEP43_STATIC_DRIVER_CONFIGS:
        case = case_name(config_path)
        case_dir = out_dir / case
        row_cache = case_dir / "step43_static_driver_row.json"
        row = run_step43_driver_case(config_path, case_dir)
        write_json(row_cache, row)
        rows.append(row)
    rows.sort(key=lambda row: row["reaction_transfer_mode"])
    summary = driver_summary(rows)
    assert_driver_summary(summary, expected_mode_class="static")
    write_rows_csv_npz(rows, out_dir / "static_driver_results.csv", out_dir / "static_driver_results.npz", STEP43_DRIVER_FIELDS)
    write_json(out_dir / "static_driver_results.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 43 static driver regression finished"
    write_log("logs/step43_static_driver_regression.log", [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
