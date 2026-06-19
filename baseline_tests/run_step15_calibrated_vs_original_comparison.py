import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step15_common import (  # noqa: E402
    COMPARISON_FIELDS,
    config_with,
    elapsed_label,
    load_driver_config,
    run_accounted_moving_boundary_case,
    save_rows_npz,
    stable_thresholds_ok,
    summarize_case_result,
)
from src.run_utils import save_csv_rows  # noqa: E402


def _comparison_row(label, config, result, recommendation):
    summary = summarize_case_result(result, geometry_type="box")
    return {
        "label": label,
        "target_u_lbm_x": float(config.target_u_lbm[0]),
        "reaction_scale": float(config.mb_reaction_scale),
        "force_cap_norm": float(config.mb_force_cap_norm),
        "stable": bool(summary["stable"]),
        "well_behaved": bool(summary["well_behaved"]),
        "sign_reversed": bool(summary["sign_reversed"]),
        "rho_min": float(summary["rho_min"]),
        "rho_max": float(summary["rho_max"]),
        "lbm_max_v": float(summary["lbm_max_v"]),
        "mpm_min_J": float(summary["mpm_min_J"]),
        "mpm_max_speed": float(summary["mpm_max_speed"]),
        "solid_slowdown": float(summary["solid_slowdown"]),
        "projection_zone_ux_final": float(summary["projection_zone_ux_final"]),
        "hydro_force_max_norm": float(summary["hydro_force_max_norm"]),
        "accounting_error_x": float(summary["accounting_error_x"]),
        "recommendation": recommendation,
    }


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step15_calibrated_vs_original")
    os.makedirs(out_dir, exist_ok=True)

    original = load_driver_config(ROOT, "configs/step15_mb_force_cap_box_48.json")
    recommended = load_driver_config(ROOT, "configs/step15_mb_recommended_box_48.json")

    print("Step 15 calibrated-vs-original moving_boundary comparison")
    t0 = time.time()
    rows = []

    original_result = run_accounted_moving_boundary_case(original, os.path.join(out_dir, "original_step14"))
    rows.append(
        _comparison_row(
            "original_step14",
            original,
            original_result,
            "Step 14 known-good comparison row",
        )
    )

    recommended_result = run_accounted_moving_boundary_case(recommended, os.path.join(out_dir, "recommended_step15"))
    rows.append(
        _comparison_row(
            "recommended_step15",
            recommended,
            recommended_result,
            "selected from Step 15 evidence",
        )
    )

    if (
        abs(float(original.mb_reaction_scale) - float(recommended.mb_reaction_scale)) < 1.0e-12
        and abs(float(original.mb_force_cap_norm) - float(recommended.mb_force_cap_norm)) < 1.0e-12
    ):
        conservative = config_with(recommended, mb_force_cap_norm=0.00001)
        conservative_result = run_accounted_moving_boundary_case(
            conservative,
            os.path.join(out_dir, "optional_conservative"),
        )
        rows.append(
            _comparison_row(
                "optional_conservative",
                conservative,
                conservative_result,
                "optional conservative stable row because recommended_step15 equals original_step14",
            )
        )

    for row in rows:
        numeric = [value for key, value in row.items() if key not in {"label", "stable", "well_behaved", "sign_reversed", "recommendation"}]
        if not all(float(value) == float(value) for value in numeric):
            raise RuntimeError(f"comparison row contains NaN: {row}")
        if bool(row["stable"]) and not stable_thresholds_ok(row):
            raise RuntimeError(f"stable comparison row failed thresholds: {row}")

    by_label = {row["label"]: row for row in rows}
    if not bool(by_label["recommended_step15"]["stable"]):
        raise RuntimeError("recommended_step15 comparison row must be stable")
    if bool(by_label["recommended_step15"]["sign_reversed"]):
        raise RuntimeError("recommended_step15 comparison row must not reverse solid velocity")

    csv_path = os.path.join(out_dir, "comparison.csv")
    npz_path = os.path.join(out_dir, "comparison.npz")
    save_csv_rows(rows, csv_path, fieldnames=COMPARISON_FIELDS)
    save_rows_npz(rows, npz_path, COMPARISON_FIELDS)

    for row in rows:
        print(
            f"comparison label={row['label']}, stable={row['stable']}, "
            f"reaction_scale={row['reaction_scale']:.6g}, force_cap_norm={row['force_cap_norm']:.9g}, "
            f"rho_min={row['rho_min']:.9e}, rho_max={row['rho_max']:.9e}, "
            f"lbm_max_v={row['lbm_max_v']:.9e}, mpm_min_J={row['mpm_min_J']:.9e}, "
            f"solid_slowdown={row['solid_slowdown']:.9e}"
        )

    print(f"csv={csv_path}")
    print(f"npz={npz_path}")
    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 15 calibrated vs original comparison finished")


if __name__ == "__main__":
    main()
