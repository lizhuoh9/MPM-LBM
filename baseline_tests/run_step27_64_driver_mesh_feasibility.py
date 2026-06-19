import os

import taichi as ti

from step27_common import ROOT, STEP27_DRIVER_CONFIGS_BY_KIND, case_name, run_step27_short_driver_case, short_driver_summary
from step27_common import assert_step27_summary, write_json, write_log, write_rows_csv_npz
from src.real_geometry_feasibility import SHORT_DRIVER_FIELDS


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step27_64_driver_mesh_feasibility"
    rows = []
    for config_path in STEP27_DRIVER_CONFIGS_BY_KIND["mesh"]:
        rows.append(run_step27_short_driver_case(config_path, out_dir / case_name(config_path)))
    rows.sort(key=lambda row: (row["candidate_id"], row["mode"], row["reaction_transfer_mode"]))
    summary = short_driver_summary(rows)
    if int(summary["driver_row_count"]) != 3 or int(summary["mesh_row_count"]) != 3:
        raise RuntimeError(f"expected 3 Step 27 mesh rows: {summary}")
    if int(summary["stable_count"]) != 3 or int(summary["quality_pass_count"]) != 3 or int(summary["strict_count"]) != 3:
        raise RuntimeError(f"all Step 27 mesh rows must be stable strict quality-passing rows: {summary}")

    write_rows_csv_npz(
        rows,
        out_dir / "mesh_64_short_driver_results.csv",
        out_dir / "mesh_64_short_driver_results.npz",
        SHORT_DRIVER_FIELDS,
    )
    write_json(out_dir / "mesh_64_short_driver_results.json", {"row_count": len(rows), "summary": summary, "rows": rows})
    marker = "[OK] Step 27 mesh 64 short driver feasibility finished"
    write_log("logs/step27_64_driver_mesh_feasibility.log", [marker, f"row_count={len(rows)}", f"stable_count={summary['stable_count']}"])
    print(f"row_count={len(rows)}")
    print(marker)


if __name__ == "__main__":
    main()
