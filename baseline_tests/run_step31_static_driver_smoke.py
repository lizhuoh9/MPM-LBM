import os

import taichi as ti

from step31_common import (
    ROOT,
    STEP31_DRIVER_CONFIGS,
    STEP31_DRIVER_FIELDS,
    assert_static_driver_summary,
    can_reuse_existing_step31_case,
    case_name,
    load_existing_step31_static_driver_case,
    run_step31_static_driver_case,
    static_driver_summary,
    write_json,
    write_log,
    write_rows_csv_npz,
)


MODE_ORDER = {"none": 0, "penalty": 1, "moving_boundary": 2}
TRANSFER_ORDER = {"engineering": 0, "link_area_experimental": 1}


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step31_static_driver_smoke"
    rows = []
    for config_path in STEP31_DRIVER_CONFIGS:
        case_dir = out_dir / case_name(config_path)
        if can_reuse_existing_step31_case(config_path, case_dir):
            rows.append(load_existing_step31_static_driver_case(config_path, case_dir))
        else:
            rows.append(run_step31_static_driver_case(config_path, case_dir))
    rows.sort(key=lambda row: (MODE_ORDER[row["mode"]], TRANSFER_ORDER[row["reaction_transfer_mode"]]))
    summary = static_driver_summary(rows)
    assert_static_driver_summary(summary)

    write_rows_csv_npz(
        rows,
        out_dir / "static_driver_results.csv",
        out_dir / "static_driver_results.npz",
        STEP31_DRIVER_FIELDS,
    )
    write_json(out_dir / "static_driver_results.json", {"row_count": len(rows), "summary": summary, "rows": rows})
    marker = "[OK] Step 31 static driver smoke finished"
    write_log(
        "logs/step31_static_driver_smoke.log",
        [
            marker,
            f"row_count={len(rows)}",
            f"stable_count={summary['stable_count']}",
            f"quality_pass_count={summary['quality_pass_count']}",
        ],
    )
    print(f"row_count={len(rows)}")
    print(marker)


if __name__ == "__main__":
    main()
