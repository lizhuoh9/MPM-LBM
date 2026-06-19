import os

import taichi as ti

from step26_common import ROOT, STEP26_DRIVER_CONFIGS_BY_KIND, write_json, write_log, write_rows_csv_npz
from src.real_geometry_feasibility import SHORT_DRIVER_FIELDS, run_short_driver_case


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step26_short_driver_voxel_48_modes"
    rows = []
    for config_path in STEP26_DRIVER_CONFIGS_BY_KIND["voxel"]:
        case_dir = out_dir / _case_name(config_path)
        rows.append(run_short_driver_case(config_path, case_dir))
    rows.sort(key=lambda row: (row["candidate_id"], row["mode"], row["reaction_transfer_mode"]))
    summary = _summary(rows)
    _assert_summary(summary)

    write_rows_csv_npz(rows, out_dir / "voxel_48_short_driver_results.csv", out_dir / "voxel_48_short_driver_results.npz", SHORT_DRIVER_FIELDS)
    write_json(out_dir / "voxel_48_short_driver_results.json", {"row_count": len(rows), "summary": summary, "rows": rows})
    marker = "[OK] Step 26 voxel 48 short driver modes finished"
    write_log(
        "logs/step26_short_driver_voxel_48_modes.log",
        [marker, f"row_count={len(rows)}", f"stable_count={summary['stable_count']}"],
    )
    print(f"row_count={len(rows)}")
    print(marker)


def _case_name(config_path):
    return os.path.splitext(os.path.basename(config_path))[0].removeprefix("step26_driver_")


def _summary(rows):
    return {
        "row_count": len(rows),
        "stable_count": sum(1 for row in rows if bool(row["stable"])),
        "quality_pass_count": sum(1 for row in rows if bool(row["quality_pass"])),
        "strict_count": sum(1 for row in rows if bool(row["quality_gate_strict"])),
        "mode_count": len({(row["mode"], row["reaction_transfer_mode"]) for row in rows}),
        "min_rho_min_global": min(float(row["rho_min_global"]) for row in rows),
        "max_rho_max_global": max(float(row["rho_max_global"]) for row in rows),
        "max_lbm_max_v_global": max(float(row["lbm_max_v_global"]) for row in rows),
        "min_mpm_min_J_global": min(float(row["mpm_min_J_global"]) for row in rows),
        "max_mpm_max_speed_global": max(float(row["mpm_max_speed_global"]) for row in rows),
    }


def _assert_summary(summary):
    if int(summary["row_count"]) != 4 or int(summary["mode_count"]) != 4:
        raise RuntimeError(f"expected 4 voxel short driver rows: {summary}")
    if int(summary["stable_count"]) != 4 or int(summary["quality_pass_count"]) != 4 or int(summary["strict_count"]) != 4:
        raise RuntimeError(f"voxel short driver rows must all be stable and strict quality-passing: {summary}")


if __name__ == "__main__":
    main()
