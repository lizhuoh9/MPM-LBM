import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import FSIDriver3D, FSIDriverConfig  # noqa: E402
from src.run_utils import save_csv_rows  # noqa: E402


FIELDS = [
    "mode",
    "total_time",
    "init_time",
    "projection_time",
    "coupling_time",
    "lbm_step_time",
    "mpm_substep_time",
    "diagnostics_time",
    "export_time",
    "steps",
    "substeps",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
]


def config_for_mode(mode):
    return FSIDriverConfig.from_json(os.path.join(ROOT, "configs", f"step12_profile_{mode}.json"))


def validate_row(row):
    timing_values = [
        row["total_time"],
        row["init_time"],
        row["projection_time"],
        row["coupling_time"],
        row["lbm_step_time"],
        row["mpm_substep_time"],
        row["diagnostics_time"],
        row["export_time"],
    ]
    if not np.all(np.isfinite(timing_values)):
        raise RuntimeError(f"{row['mode']} timing contains NaN or Inf")
    if row["total_time"] <= 0.0:
        raise RuntimeError(f"{row['mode']} total_time must be positive")
    if row["rho_min"] <= 0.95 or row["rho_max"] >= 1.05:
        raise RuntimeError(f"{row['mode']} rho outside accepted range")
    if row["lbm_max_v"] >= 0.1:
        raise RuntimeError(f"{row['mode']} lbm_max_v exceeded threshold")
    if row["mpm_min_J"] <= 0.0:
        raise RuntimeError(f"{row['mode']} mpm_min_J became non-positive")


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    modes = ["none", "penalty", "moving_boundary"]
    out_dir = os.path.join(ROOT, "outputs", "step12_profile_matrix")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 12 driver profile matrix")
    print(f"modes={modes}")
    t0 = time.time()
    rows = []

    for mode in modes:
        config = config_for_mode(mode)
        driver = FSIDriver3D(config, os.path.join(out_dir, mode))
        diagnostics = driver.run()
        final = diagnostics[-1]
        timing = driver.performance_row()
        row = {
            "mode": mode,
            "total_time": timing["total_time"],
            "init_time": timing["init_time"],
            "projection_time": timing["projection_time"],
            "coupling_time": timing["coupling_time"],
            "lbm_step_time": timing["lbm_step_time"],
            "mpm_substep_time": timing["mpm_substep_time"],
            "diagnostics_time": timing["diagnostics_time"],
            "export_time": timing["export_time"],
            "steps": config.n_lbm_steps,
            "substeps": config.n_lbm_steps * config.mpm_substeps_per_lbm_step,
            "rho_min": final["rho_min"],
            "rho_max": final["rho_max"],
            "lbm_max_v": final["lbm_max_v"],
            "mpm_min_J": final["mpm_min_J"],
            "mpm_max_speed": final["mpm_max_speed"],
        }
        validate_row(row)
        rows.append(row)
        print(
            f"mode={mode}, total_time={row['total_time']:.9e}, "
            f"projection_time={row['projection_time']:.9e}, "
            f"coupling_time={row['coupling_time']:.9e}, "
            f"lbm_step_time={row['lbm_step_time']:.9e}, "
            f"mpm_substep_time={row['mpm_substep_time']:.9e}, "
            f"rho_min={row['rho_min']:.9e}, rho_max={row['rho_max']:.9e}, "
            f"lbm_max_v={row['lbm_max_v']:.9e}, mpm_min_J={row['mpm_min_J']:.9e}"
        )

    save_csv_rows(rows, os.path.join(out_dir, "profile_matrix.csv"), fieldnames=FIELDS)
    np.savez(
        os.path.join(out_dir, "profile_matrix.npz"),
        columns=np.asarray(FIELDS),
        modes=np.asarray([row["mode"] for row in rows]),
        rows=np.asarray([[row[field] for field in FIELDS[1:]] for row in rows], dtype=np.float64),
    )

    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 12 driver profile matrix finished")


if __name__ == "__main__":
    main()
