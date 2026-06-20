import os

import taichi as ti

from step34_common import (
    ROOT,
    STEP34_DRIVER_FIELDS,
    STEP34_STATIC_DRIVER_CONFIGS,
    assert_driver_summary,
    can_reuse_existing_step34_case,
    driver_summary,
    load_existing_step34_driver_case,
    run_step34_driver_case,
    write_json,
    write_log,
    write_rows_csv_npz,
)


MODE_ORDER = {"none": 0, "penalty": 1, "moving_boundary": 2}
TRANSFER_ORDER = {"engineering": 0, "link_area_experimental": 1}


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step34_static_driver_regression"
    rows = []
    for config_path in STEP34_STATIC_DRIVER_CONFIGS:
        case_path = out_dir / case_dir(config_path)
        if can_reuse_existing_step34_case(config_path, case_path):
            rows.append(load_existing_step34_driver_case(config_path, case_path))
        else:
            rows.append(run_step34_driver_case(config_path, case_path))
    rows.sort(key=lambda row: (MODE_ORDER[row["mode"]], TRANSFER_ORDER[row["reaction_transfer_mode"]]))
    summary = driver_summary(rows)
    assert_driver_summary(summary, expected_rows=4, expected_boundary_reports=0)
    if int(summary["static_boundary_motion_row_count"]) != 4 or int(summary["prescribed_boundary_motion_row_count"]) != 0:
        raise RuntimeError(f"Step 34 static regression has wrong boundary mode split: {summary}")

    write_rows_csv_npz(
        rows,
        out_dir / "static_driver_results.csv",
        out_dir / "static_driver_results.npz",
        STEP34_DRIVER_FIELDS,
    )
    write_json(out_dir / "static_driver_results.json", {"row_count": len(rows), "summary": summary, "rows": rows})
    marker = "[OK] Step 34 static driver regression finished"
    write_log(
        "logs/step34_static_driver_regression.log",
        [marker, f"row_count={len(rows)}", f"stable_count={summary['stable_count']}"],
    )
    print(f"row_count={len(rows)}")
    print(marker)


def case_dir(config_path):
    from step34_common import case_name

    return case_name(config_path)


if __name__ == "__main__":
    main()
