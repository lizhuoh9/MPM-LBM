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
)


REACTION_SCALES = [0.25, 0.5, 1.0, 2.0]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    out_dir = os.path.join(ROOT, "outputs", "step15_reaction_scale_sweep_box_32")
    os.makedirs(out_dir, exist_ok=True)
    base = load_driver_config(ROOT, "configs/step15_mb_calibration_box_32.json")

    print("Step 15 reaction_scale sweep box 32")
    t0 = time.time()
    rows = []
    for scale in REACTION_SCALES:
        config = config_with(base, mb_reaction_scale=float(scale), write_vtk=False, write_particles=False)
        case_dir = os.path.join(out_dir, f"reaction_scale_{scale:g}".replace(".", "p"))
        result = run_accounted_moving_boundary_case(config, case_dir)
        row = summarize_case_result(result, geometry_type="box")
        rows.append(row)
        print_calibration_row("reaction_scale_box_32", row)

    validate_calibration_rows(rows)
    stable_required = [row for row in rows if float(row["reaction_scale"]) in {0.25, 0.5, 1.0}]
    if sum(1 for row in stable_required if bool(row["stable"])) < 3:
        raise RuntimeError("reaction_scale 0.25, 0.5, and 1.0 must be stable")
    for row in stable_required:
        if bool(row["stable"]) and float(row["solid_slowdown"]) < 0.0:
            raise RuntimeError("stable recommended reaction_scale candidates must not accelerate the solid")

    recommended, marked_rows = choose_and_mark_recommended(rows)
    csv_path = os.path.join(out_dir, "reaction_scale_sweep.csv")
    npz_path = os.path.join(out_dir, "reaction_scale_sweep.npz")
    write_calibration_outputs(marked_rows, csv_path, npz_path, fieldnames=CALIBRATION_FIELDS + ["recommended"])
    write_json(
        {
            "recommended": recommended,
            "stable_count": sum(1 for row in marked_rows if bool(row["stable"])),
            "scope_note": "Step 15 reaction_scale sweep uses the existing moving_boundary engineering coupling scale.",
        },
        os.path.join(out_dir, "reaction_scale_sweep_summary.json"),
    )

    print(f"recommended_reaction_scale={recommended['reaction_scale']}")
    print(f"csv={csv_path}")
    print(f"npz={npz_path}")
    print(f"elapsed={elapsed_label(t0)}")
    print("[OK] Step 15 reaction scale sweep box 32 finished")


if __name__ == "__main__":
    main()
