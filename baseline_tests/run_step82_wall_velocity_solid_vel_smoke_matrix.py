import os

import taichi as ti

from step82_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.step82_wall_velocity_solid_vel_smoke_runner import (
    STEP82_SMOKE_FIELDS,
    build_step82_wall_velocity_solid_vel_smoke_matrix,
)


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, random_seed=0, kernel_profiler=False, print_ir=False)
    rows, summary = build_step82_wall_velocity_solid_vel_smoke_matrix(ROOT)
    if not summary["step82_wall_velocity_solid_vel_smoke_matrix_pass"]:
        raise RuntimeError(f"Step82 wall velocity solid_vel smoke matrix failed: {summary}")
    out_dir = ROOT / "outputs" / "step82_wall_velocity_solid_vel_smoke_matrix"
    write_csv_rows(out_dir / "wall_velocity_solid_vel_smoke_matrix.csv", rows, STEP82_SMOKE_FIELDS)
    write_csv_rows(out_dir / "wall_velocity_solid_vel_smoke_matrix_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "wall_velocity_solid_vel_smoke_matrix.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step82 wall velocity solid_vel canonical driver smoke matrix finished"
    write_log(
        "logs/step82_wall_velocity_solid_vel_smoke_matrix.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"stable_count={summary['stable_count']}",
            f"total_elapsed_seconds={summary['total_elapsed_seconds']}",
            f"slowest_row_name={summary['slowest_row_name']}",
            f"slowest_elapsed_seconds={summary['slowest_elapsed_seconds']}",
        ],
    )
    print(marker)


if __name__ == "__main__":
    main()
