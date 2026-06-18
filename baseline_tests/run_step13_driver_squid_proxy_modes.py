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
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "active_cell_count",
    "projected_mass",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "bb_link_count",
    "active_reaction_particle_count",
    "max_grid_reaction_norm",
]


def load_config(mode):
    return FSIDriverConfig.from_json(os.path.join(ROOT, "configs", f"step13_squid_proxy_{mode}.json"))


def validate_row(row):
    numeric = [value for key, value in row.items() if key not in ("mode", "stable")]
    if not np.all(np.isfinite(numeric)):
        raise RuntimeError(f"{row['mode']} contains NaN or Inf")
    if not row["stable"]:
        raise RuntimeError(f"{row['mode']} is unstable")
    if row["rho_min"] <= 0.95 or row["rho_max"] >= 1.05:
        raise RuntimeError(f"{row['mode']} rho outside accepted range")
    if row["lbm_max_v"] >= 0.1:
        raise RuntimeError(f"{row['mode']} lbm_max_v exceeded threshold")
    if row["mpm_min_J"] <= 0.0:
        raise RuntimeError(f"{row['mode']} mpm_min_J became non-positive")
    if row["mpm_max_speed"] >= 10.0:
        raise RuntimeError(f"{row['mode']} mpm_max_speed exceeded threshold")
    if row["active_cell_count"] <= 0 or row["projected_mass"] <= 0.0:
        raise RuntimeError(f"{row['mode']} projection did not activate cells")


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    modes = ["none", "penalty", "moving_boundary"]
    out_dir = os.path.join(ROOT, "outputs", "step13_squid_proxy_modes")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 13 squid proxy driver modes")
    print(f"modes={modes}")
    t0 = time.time()
    rows = []

    for mode in modes:
        config = load_config(mode)
        driver = FSIDriver3D(config, os.path.join(out_dir, mode))
        diagnostics = driver.run()
        final = diagnostics[-1]
        row = {
            "mode": mode,
            "stable": True,
            "rho_min": final["rho_min"],
            "rho_max": final["rho_max"],
            "lbm_max_v": final["lbm_max_v"],
            "mpm_min_J": final["mpm_min_J"],
            "mpm_max_speed": final["mpm_max_speed"],
            "active_cell_count": final["active_cell_count"],
            "projected_mass": final["projected_mass"],
            "cell_force_max_norm": final["cell_force_max_norm"],
            "hydro_force_max_norm": final["hydro_force_max_norm"],
            "bb_link_count": final["bb_link_count"],
            "active_reaction_particle_count": final["active_reaction_particle_count"],
            "max_grid_reaction_norm": final["max_grid_reaction_norm"],
        }
        validate_row(row)
        rows.append(row)
        print(
            f"mode={mode}, stable=True, rho_min={row['rho_min']:.9e}, "
            f"rho_max={row['rho_max']:.9e}, lbm_max_v={row['lbm_max_v']:.9e}, "
            f"mpm_min_J={row['mpm_min_J']:.9e}, mpm_max_speed={row['mpm_max_speed']:.9e}, "
            f"active_cell_count={row['active_cell_count']}, projected_mass={row['projected_mass']:.9e}, "
            f"cell_force_max_norm={row['cell_force_max_norm']:.9e}, "
            f"hydro_force_max_norm={row['hydro_force_max_norm']:.9e}, "
            f"bb_link_count={row['bb_link_count']}"
        )

    by_mode = {row["mode"]: row for row in rows}
    if by_mode["penalty"]["cell_force_max_norm"] <= 0.0:
        raise RuntimeError("penalty mode should have nonzero cell_force")
    if by_mode["moving_boundary"]["cell_force_max_norm"] != 0.0:
        raise RuntimeError("moving_boundary mode should keep cell_force zero")
    if by_mode["moving_boundary"]["bb_link_count"] <= 0:
        raise RuntimeError("moving_boundary mode should have bounce-back links")
    if by_mode["moving_boundary"]["hydro_force_max_norm"] <= 0.0:
        raise RuntimeError("moving_boundary mode should have nonzero hydro_force response")

    save_csv_rows(rows, os.path.join(out_dir, "mode_results.csv"), fieldnames=FIELDS)
    np.savez(
        os.path.join(out_dir, "mode_results.npz"),
        columns=np.asarray(FIELDS),
        modes=np.asarray([row["mode"] for row in rows]),
        rows=np.asarray([[row[field] for field in FIELDS[2:]] for row in rows], dtype=np.float64),
    )

    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 13 squid proxy driver modes finished")


if __name__ == "__main__":
    main()
