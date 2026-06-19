import os

import taichi as ti

from step26_common import ROOT, STEP26_PROJECTION_CONFIGS, load_json, write_json, write_log, write_rows_csv_npz
from src.real_geometry_feasibility import PROJECTION_FIELDS, run_projection_only_scale_case


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.cpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = ROOT / "outputs" / "step26_projection_scale_diagnostics"
    rows = []
    for config_path in STEP26_PROJECTION_CONFIGS:
        payload = load_json(config_path)
        rows.append(
            run_projection_only_scale_case(
                payload["geometry_config_path"],
                int(payload["n_grid"]),
                out_dir / f"{payload['candidate_id']}_{int(payload['n_grid'])}",
            )
        )
    rows.sort(key=lambda row: (row["candidate_id"], int(row["n_grid"])))
    summary = _summary(rows)
    _assert_summary(summary)

    write_rows_csv_npz(
        rows,
        out_dir / "projection_scale_results.csv",
        out_dir / "projection_scale_results.npz",
        PROJECTION_FIELDS,
    )
    write_json(out_dir / "projection_scale_results.json", {"row_count": len(rows), "summary": summary, "rows": rows})
    marker = "[OK] Step 26 projection scale diagnostics finished"
    write_log(
        "logs/step26_projection_scale_diagnostics.log",
        [
            marker,
            f"row_count={len(rows)}",
            f"pass_count={summary['pass_count']}",
            f"min_projected_mass={summary['min_projected_mass']:.12e}",
            "scope=projection_only_no_fsi_driver_long_run",
        ],
    )
    print(f"row_count={len(rows)}")
    print(marker)


def _summary(rows):
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if bool(row["projection_pass"])),
        "candidate_count": len({row["candidate_id"] for row in rows}),
        "grid_count": len({int(row["n_grid"]) for row in rows}),
        "min_projected_mass": min(float(row["projected_mass"]) for row in rows) if rows else 0.0,
        "max_projected_mass": max(float(row["projected_mass"]) for row in rows) if rows else 0.0,
        "min_active_cell_count": min(int(row["active_cell_count"]) for row in rows) if rows else 0,
        "max_active_cell_count": max(int(row["active_cell_count"]) for row in rows) if rows else 0,
        "has_nan_count": sum(1 for row in rows if bool(row["has_nan"])),
        "has_inf_count": sum(1 for row in rows if bool(row["has_inf"])),
    }


def _assert_summary(summary):
    if int(summary["row_count"]) != 6:
        raise RuntimeError(f"expected 6 Step 26 projection rows: {summary}")
    if int(summary["pass_count"]) != 6:
        raise RuntimeError(f"all Step 26 projection rows must pass: {summary}")
    if int(summary["candidate_count"]) != 2 or int(summary["grid_count"]) != 3:
        raise RuntimeError(f"Step 26 projection matrix shape is wrong: {summary}")
    if int(summary["has_nan_count"]) != 0 or int(summary["has_inf_count"]) != 0:
        raise RuntimeError(f"Step 26 projection rows contain NaN or Inf: {summary}")


if __name__ == "__main__":
    main()
