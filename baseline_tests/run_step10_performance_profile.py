import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import FSIDriver3D, FSIDriverConfig  # noqa: E402
from src.run_utils import save_csv_rows  # noqa: E402


PERF_FIELDS = [
    "mode",
    "init_time",
    "projection_time",
    "coupling_time",
    "lbm_step_time",
    "mpm_substep_time",
    "diagnostics_time",
    "export_time",
    "total_time",
]


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    modes = ["none", "penalty", "moving_boundary"]
    out_dir = os.path.join(ROOT, "outputs", "step10_performance_profile")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 10 performance profile")
    print(f"modes={modes}")
    print("n_grid=32")
    print("n_particles=4096")
    print("n_lbm_steps=10")
    print("mpm_substeps_per_lbm_step=10")
    t0 = time.time()

    results = []
    for mode in modes:
        config = FSIDriverConfig(
            coupling_mode=mode,
            n_lbm_steps=10,
            write_vtk=False,
            write_particles=False,
            output_interval=10,
        )
        driver = FSIDriver3D(config, os.path.join(out_dir, mode))
        driver.run()
        row = driver.performance_row()
        values = [row[field] for field in PERF_FIELDS if field != "mode"]
        if not np.all(np.isfinite(values)):
            raise RuntimeError(f"{mode} performance timing contains NaN or Inf")
        if row["total_time"] <= 0.0:
            raise RuntimeError(f"{mode} total_time must be positive")
        results.append(row)
        print(
            f"mode={mode}, "
            f"init_time={row['init_time']:.9e}, "
            f"projection_time={row['projection_time']:.9e}, "
            f"coupling_time={row['coupling_time']:.9e}, "
            f"lbm_step_time={row['lbm_step_time']:.9e}, "
            f"mpm_substep_time={row['mpm_substep_time']:.9e}, "
            f"diagnostics_time={row['diagnostics_time']:.9e}, "
            f"export_time={row['export_time']:.9e}, "
            f"total_time={row['total_time']:.9e}"
        )

    save_csv_rows(results, os.path.join(out_dir, "performance_results.csv"), fieldnames=PERF_FIELDS)
    np.savez(
        os.path.join(out_dir, "performance_results.npz"),
        columns=np.asarray(PERF_FIELDS),
        modes=np.asarray([row["mode"] for row in results]),
        rows=np.asarray([[row[field] for field in PERF_FIELDS[1:]] for row in results], dtype=np.float64),
    )

    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 10 performance profile finished")


if __name__ == "__main__":
    main()
