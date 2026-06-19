import os
import sys
import time

import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step15_common import (  # noqa: E402
    CALIBRATION_FIELDS,
    choose_and_mark_recommended,
    config_with,
    elapsed_label,
    load_driver_config,
    print_calibration_row,
    run_accounted_moving_boundary_case,
    summarize_case_result,
    validate_calibration_rows,
    write_calibration_outputs,
    write_json,
    write_recommended_config,
)


REACTION_SCALES = [0.5, 1.0]
FORCE_CAPS = [0.000025, 0.00005]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step15_squid_proxy_calibrated_window")
    os.makedirs(out_dir, exist_ok=True)
    base = load_driver_config(ROOT, "configs/step15_mb_calibration_squid_proxy_48.json")

    print("Step 15 squid_proxy calibrated moving_boundary window")
    t0 = time.time()
    rows = []
    for scale in REACTION_SCALES:
        for cap in FORCE_CAPS:
            config = config_with(
                base,
                mb_reaction_scale=float(scale),
                mb_force_cap_norm=float(cap),
                write_vtk=False,
                write_particles=False,
            )
            case_dir = os.path.join(out_dir, f"scale_{scale:g}_cap_{cap:.8f}".replace(".", "p"))
            result = run_accounted_moving_boundary_case(config, case_dir)
            row = summarize_case_result(result, geometry_type="squid_proxy")
            rows.append(row)
            print_calibration_row("squid_proxy_window", row)

    validate_calibration_rows(rows)
    if sum(1 for row in rows if bool(row["stable"])) < 2:
        raise RuntimeError("squid_proxy calibrated window requires at least two stable rows")
    for row in rows:
        if bool(row["stable"]) and float(row["cell_force_max_norm"]) != 0.0:
            raise RuntimeError("moving_boundary squid_proxy rows must keep cell_force_max_norm at zero")
        if bool(row["stable"]) and int(row["bb_link_count"]) <= 0:
            raise RuntimeError("moving_boundary squid_proxy rows must have bounce-back links")

    recommended, marked_rows = choose_and_mark_recommended(rows)
    if not bool(recommended["stable"]):
        raise RuntimeError("recommended squid_proxy row must be stable")

    csv_path = os.path.join(out_dir, "squid_proxy_calibration.csv")
    npz_path = os.path.join(out_dir, "squid_proxy_calibration.npz")
    write_calibration_outputs(marked_rows, csv_path, npz_path, fieldnames=CALIBRATION_FIELDS + ["recommended"])
    recommended_config = write_recommended_config(
        base,
        recommended,
        os.path.join(ROOT, "configs", "step15_mb_recommended_squid_proxy_48.json"),
    )
    write_json(
        {
            "recommended": recommended,
            "recommended_config": recommended_config.to_dict(),
            "stable_count": sum(1 for row in marked_rows if bool(row["stable"])),
            "scope_note": "squid_proxy is procedural and not real squid validation.",
        },
        os.path.join(out_dir, "squid_proxy_calibration_summary.json"),
    )

    print(
        f"recommended_reaction_scale={recommended['reaction_scale']}, "
        f"recommended_force_cap_norm={recommended['force_cap_norm']}"
    )
    print(f"recommended_config=configs/step15_mb_recommended_squid_proxy_48.json")
    print(f"csv={csv_path}")
    print(f"npz={npz_path}")
    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 15 squid proxy calibrated window finished")


if __name__ == "__main__":
    main()
