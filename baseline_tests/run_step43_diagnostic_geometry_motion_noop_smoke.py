import os

import taichi as ti

from step43_common import (
    ROOT,
    STEP43_DIAGNOSTIC_DRIVER_CONFIGS,
    STEP43_DRIVER_FIELDS,
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
    out_dir = ROOT / "outputs" / "step43_diagnostic_geometry_motion_noop_smoke"
    rows = []
    for config_path in STEP43_DIAGNOSTIC_DRIVER_CONFIGS:
        case = case_name(config_path)
        case_dir = out_dir / case
        row_cache = case_dir / "step43_diagnostic_driver_row.json"
        row = run_step43_driver_case(config_path, case_dir)
        write_json(row_cache, row)
        rows.append(row)
    rows.sort(key=lambda row: row["reaction_transfer_mode"])
    summary = driver_summary(rows)
    assert_driver_summary(summary, expected_mode_class="diagnostic")
    write_rows_csv_npz(rows, out_dir / "diagnostic_noop_results.csv", out_dir / "diagnostic_noop_results.npz", STEP43_DRIVER_FIELDS)
    write_json(out_dir / "diagnostic_noop_results.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 43 diagnostic geometry motion no-op smoke finished"
    write_log("logs/step43_diagnostic_geometry_motion_noop_smoke.log", [marker, f"row_count={summary['row_count']}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
