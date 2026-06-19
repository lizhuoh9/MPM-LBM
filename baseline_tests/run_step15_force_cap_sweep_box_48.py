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


FORCE_CAPS = [0.00001, 0.000025, 0.00005, 0.0001]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step15_force_cap_sweep_box_48")
    os.makedirs(out_dir, exist_ok=True)
    base = load_driver_config(ROOT, "configs/step15_mb_force_cap_box_48.json")

    print("Step 15 force_cap_norm sweep box 48")
    t0 = time.time()
    rows = []
    for cap in FORCE_CAPS:
        config = config_with(base, mb_force_cap_norm=float(cap), write_vtk=False, write_particles=False)
        case_dir = os.path.join(out_dir, f"force_cap_{cap:.8f}".replace(".", "p"))
        result = run_accounted_moving_boundary_case(config, case_dir)
        row = summarize_case_result(result, geometry_type="box")
        rows.append(row)
        print_calibration_row("force_cap_box_48", row)

    validate_calibration_rows(rows)
    known_good = [row for row in rows if abs(float(row["force_cap_norm"]) - 0.000025) < 1.0e-12]
    if len(known_good) != 1 or not bool(known_good[0]["stable"]):
        raise RuntimeError("Step 14 known-good force_cap_norm=0.000025 must remain stable")
    stable_required = [row for row in rows if round(float(row["force_cap_norm"]), 8) in {0.00001, 0.000025, 0.00005}]
    if sum(1 for row in stable_required if bool(row["stable"])) < 2:
        raise RuntimeError("at least two conservative force_cap rows must be stable")

    recommended, marked_rows = choose_and_mark_recommended(rows)
    csv_path = os.path.join(out_dir, "force_cap_sweep.csv")
    npz_path = os.path.join(out_dir, "force_cap_sweep.npz")
    write_calibration_outputs(marked_rows, csv_path, npz_path, fieldnames=CALIBRATION_FIELDS + ["recommended"])
    recommended_config = write_recommended_config(
        base,
        recommended,
        os.path.join(ROOT, "configs", "step15_mb_recommended_box_48.json"),
    )
    write_json(
        {
            "recommended": recommended,
            "recommended_config": recommended_config.to_dict(),
            "stable_count": sum(1 for row in marked_rows if bool(row["stable"])),
            "scope_note": "Step 15 force_cap_norm sweep calibrates existing moving_boundary settings.",
        },
        os.path.join(out_dir, "force_cap_sweep_summary.json"),
    )

    print(f"recommended_force_cap_norm={recommended['force_cap_norm']}")
    print(f"recommended_config=configs/step15_mb_recommended_box_48.json")
    print(f"csv={csv_path}")
    print(f"npz={npz_path}")
    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 15 force cap sweep box 48 finished")


if __name__ == "__main__":
    main()
