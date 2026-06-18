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
    "stable",
    "projection_zone_ux_final",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "bb_link_count",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
]


def config_for_mode(mode):
    return FSIDriverConfig(
        coupling_mode=mode,
        n_grid=32,
        n_particles=4096,
        n_lbm_steps=10,
        mpm_substeps_per_lbm_step=10,
        mpm_dt=4.0e-4,
        write_vtk=False,
        write_particles=False,
        output_interval=10,
    )


def validate_row(row):
    numeric_values = [value for key, value in row.items() if key not in ("mode", "stable")]
    if not np.all(np.isfinite(numeric_values)):
        raise RuntimeError(f"{row['mode']} regression result contains NaN or Inf")
    if row["rho_min"] <= 0.95 or row["rho_max"] >= 1.05:
        raise RuntimeError(f"{row['mode']} rho outside accepted range")
    if row["lbm_max_v"] >= 0.1:
        raise RuntimeError(f"{row['mode']} lbm_max_v exceeded threshold")
    if row["mpm_min_J"] <= 0.0:
        raise RuntimeError(f"{row['mode']} mpm_min_J became non-positive")


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    modes = ["none", "penalty", "moving_boundary"]
    out_dir = os.path.join(ROOT, "outputs", "step12_no_physics_regression")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 12 no-physics regression")
    t0 = time.time()
    rows = []
    for mode in modes:
        config = config_for_mode(mode)
        driver = FSIDriver3D(config, os.path.join(out_dir, mode))
        diagnostics = driver.run()
        final = diagnostics[-1]
        row = {
            "mode": mode,
            "stable": True,
            "projection_zone_ux_final": final["projection_zone_fluid_mean_ux"],
            "cell_force_max_norm": final["cell_force_max_norm"],
            "hydro_force_max_norm": final["hydro_force_max_norm"],
            "bb_link_count": final["bb_link_count"],
            "rho_min": final["rho_min"],
            "rho_max": final["rho_max"],
            "lbm_max_v": final["lbm_max_v"],
            "mpm_min_J": final["mpm_min_J"],
            "mpm_max_speed": final["mpm_max_speed"],
        }
        validate_row(row)
        rows.append(row)
        print(
            f"mode={mode}, stable=True, "
            f"projection_zone_ux_final={row['projection_zone_ux_final']:.9e}, "
            f"cell_force_max_norm={row['cell_force_max_norm']:.9e}, "
            f"hydro_force_max_norm={row['hydro_force_max_norm']:.9e}, "
            f"bb_link_count={int(row['bb_link_count'])}, "
            f"rho_min={row['rho_min']:.9e}, rho_max={row['rho_max']:.9e}, "
            f"lbm_max_v={row['lbm_max_v']:.9e}, mpm_min_J={row['mpm_min_J']:.9e}"
        )

    by_mode = {row["mode"]: row for row in rows}
    ux_none = by_mode["none"]["projection_zone_ux_final"]
    ux_penalty = by_mode["penalty"]["projection_zone_ux_final"]
    ux_moving = by_mode["moving_boundary"]["projection_zone_ux_final"]
    if not (ux_moving > ux_penalty > ux_none):
        raise RuntimeError(
            "Step 10 mode trend was not preserved: "
            f"moving_boundary={ux_moving}, penalty={ux_penalty}, none={ux_none}"
        )
    if by_mode["penalty"]["cell_force_max_norm"] <= 0.0:
        raise RuntimeError("penalty mode should keep nonzero cell_force")
    if by_mode["moving_boundary"]["cell_force_max_norm"] != 0.0:
        raise RuntimeError("moving_boundary mode should keep cell_force zero")
    if by_mode["moving_boundary"]["bb_link_count"] <= 0:
        raise RuntimeError("moving_boundary mode should keep nonzero bounce-back links")

    save_csv_rows(rows, os.path.join(out_dir, "no_physics_regression.csv"), fieldnames=FIELDS)
    np.savez(
        os.path.join(out_dir, "no_physics_regression.npz"),
        columns=np.asarray(FIELDS),
        modes=np.asarray([row["mode"] for row in rows]),
        rows=np.asarray([[row[field] for field in FIELDS[2:]] for row in rows], dtype=np.float64),
    )

    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 12 no-physics regression finished")


if __name__ == "__main__":
    main()
