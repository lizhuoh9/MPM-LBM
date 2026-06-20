import os

import taichi as ti

from step28_common import (
    ROOT,
    STEP28_DRIVER_CONFIGS,
    assert_transfer_pair_summary,
    case_name,
    run_step28_transfer_driver_case,
    transfer_pair_summary,
    write_json,
    write_log,
    write_rows_csv_npz,
)
from src.real_geometry_feasibility import SHORT_DRIVER_FIELDS


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step28_64_transfer_pair_driver"
    rows = []
    for config_path in STEP28_DRIVER_CONFIGS:
        rows.append(run_step28_transfer_driver_case(config_path, out_dir / case_name(config_path)))
    rows.sort(key=lambda row: (row["candidate_id"], row["reaction_transfer_mode"]))
    summary = transfer_pair_summary(rows)
    assert_transfer_pair_summary(summary)

    write_rows_csv_npz(
        rows,
        out_dir / "transfer_pair_driver_results.csv",
        out_dir / "transfer_pair_driver_results.npz",
        SHORT_DRIVER_FIELDS,
    )
    write_json(out_dir / "transfer_pair_driver_results.json", {"row_count": len(rows), "summary": summary, "rows": rows})
    marker = "[OK] Step 28 64 transfer pair driver finished"
    write_log(
        "logs/step28_64_transfer_pair_driver.log",
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
