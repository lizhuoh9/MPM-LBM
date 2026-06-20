import os

import taichi as ti

from step29_common import (
    ROOT,
    STEP29_DRIVER_CONFIGS,
    assert_stability_driver_summary,
    case_name,
    run_step29_stability_driver_case,
    stability_driver_summary,
    write_json,
    write_log,
    write_rows_csv_npz,
)
from src.real_geometry_feasibility import SHORT_DRIVER_FIELDS


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step29_64_stability_driver"
    rows = []
    for config_path in STEP29_DRIVER_CONFIGS:
        rows.append(run_step29_stability_driver_case(config_path, out_dir / case_name(config_path)))
    rows.sort(key=lambda row: (row["candidate_id"], row["reaction_transfer_mode"]))
    summary = stability_driver_summary(rows)
    assert_stability_driver_summary(summary)

    write_rows_csv_npz(
        rows,
        out_dir / "stability_driver_results.csv",
        out_dir / "stability_driver_results.npz",
        SHORT_DRIVER_FIELDS,
    )
    write_json(out_dir / "stability_driver_results.json", {"row_count": len(rows), "summary": summary, "rows": rows})
    marker = "[OK] Step 29 64 stability driver finished"
    write_log(
        "logs/step29_64_stability_driver.log",
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
