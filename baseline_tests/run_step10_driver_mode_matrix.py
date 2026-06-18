import json
import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import FSIDriver3D, FSIDriverConfig  # noqa: E402
from src.run_utils import save_csv_rows  # noqa: E402


MATRIX_FIELDS = [
    "mode",
    "stable",
    "fluid_mean_ux_final",
    "projection_zone_ux_final",
    "solid_mean_vx_initial",
    "solid_mean_vx_final",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "bb_link_count",
    "active_reaction_particle_count",
]


def make_mode_config(base_config, mode):
    values = {
        "coupling_mode": mode,
        "n_grid": int(base_config["n_grid"]),
        "n_particles": int(base_config["n_particles"]),
        "n_lbm_steps": int(base_config["n_lbm_steps"]),
        "mpm_substeps_per_lbm_step": int(base_config["mpm_substeps_per_lbm_step"]),
        "target_u_lbm": tuple(float(v) for v in base_config["target_u_lbm"]),
    }
    if mode == "moving_boundary":
        values["mb_force_cap_norm"] = 1.0e-4
    return FSIDriverConfig(**values)


def validate_mode_result(result):
    values = [value for key, value in result.items() if key not in ("mode", "stable")]
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"{result['mode']} mode matrix result contains NaN or Inf")
    if not result["stable"]:
        raise RuntimeError(f"{result['mode']} mode matrix result is unstable")
    if result["rho_min"] <= 0.95 or result["rho_max"] >= 1.05:
        raise RuntimeError(f"{result['mode']} rho outside accepted range")
    if result["lbm_max_v"] >= 0.1:
        raise RuntimeError(f"{result['mode']} lbm max_v exceeded threshold")
    if result["mpm_min_J"] <= 0.0:
        raise RuntimeError(f"{result['mode']} mpm min_J became non-positive")
    if result["mpm_max_speed"] >= 10.0:
        raise RuntimeError(f"{result['mode']} mpm max_speed exceeded threshold")


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    config_path = os.path.join(ROOT, "configs", "step10_mode_matrix.json")
    with open(config_path, "r", encoding="utf-8") as f:
        matrix_config = json.load(f)

    out_dir = os.path.join(ROOT, "outputs", "step10_mode_matrix")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 10 driver mode matrix")
    print(f"modes={matrix_config['modes']}")
    print(f"n_grid={matrix_config['n_grid']}")
    print(f"n_particles={matrix_config['n_particles']}")
    print(f"n_lbm_steps={matrix_config['n_lbm_steps']}")
    print(f"target_u_lbm={matrix_config['target_u_lbm']}")
    t0 = time.time()

    results = []
    for mode in matrix_config["modes"]:
        mode_config = make_mode_config(matrix_config, mode)
        mode_out_dir = os.path.join(out_dir, mode)
        driver = FSIDriver3D(mode_config, mode_out_dir)
        rows = driver.run()
        initial_row = rows[0]
        final_row = rows[-1]
        result = {
            "mode": mode,
            "stable": True,
            "fluid_mean_ux_final": final_row["fluid_mean_ux"],
            "projection_zone_ux_final": final_row["projection_zone_fluid_mean_ux"],
            "solid_mean_vx_initial": initial_row["solid_mean_vx_norm"],
            "solid_mean_vx_final": final_row["solid_mean_vx_norm"],
            "rho_min": final_row["rho_min"],
            "rho_max": final_row["rho_max"],
            "lbm_max_v": final_row["lbm_max_v"],
            "mpm_min_J": final_row["mpm_min_J"],
            "mpm_max_speed": final_row["mpm_max_speed"],
            "cell_force_max_norm": final_row["cell_force_max_norm"],
            "hydro_force_max_norm": final_row["hydro_force_max_norm"],
            "bb_link_count": final_row["bb_link_count"],
            "active_reaction_particle_count": final_row["active_reaction_particle_count"],
        }
        validate_mode_result(result)
        results.append(result)
        print(
            f"mode={mode}, stable=True, "
            f"projection_zone_ux_final={result['projection_zone_ux_final']:.9e}, "
            f"solid_mean_vx_initial={result['solid_mean_vx_initial']:.9e}, "
            f"solid_mean_vx_final={result['solid_mean_vx_final']:.9e}, "
            f"cell_force_max_norm={result['cell_force_max_norm']:.9e}, "
            f"hydro_force_max_norm={result['hydro_force_max_norm']:.9e}, "
            f"bb_link_count={int(result['bb_link_count'])}, "
            f"active_reaction_particle_count={int(result['active_reaction_particle_count'])}, "
            f"rho_min={result['rho_min']:.9e}, rho_max={result['rho_max']:.9e}, "
            f"lbm_max_v={result['lbm_max_v']:.9e}, "
            f"mpm_min_J={result['mpm_min_J']:.9e}, "
            f"mpm_max_speed={result['mpm_max_speed']:.9e}"
        )

    by_mode = {result["mode"]: result for result in results}
    if by_mode["penalty"]["cell_force_max_norm"] <= 0.0:
        raise RuntimeError("penalty mode should have nonzero cell_force")
    if by_mode["moving_boundary"]["cell_force_max_norm"] != 0.0:
        raise RuntimeError("moving_boundary mode should keep cell_force zero")
    if by_mode["moving_boundary"]["bb_link_count"] <= 0:
        raise RuntimeError("moving_boundary mode should have bounce-back links")
    if by_mode["moving_boundary"]["active_reaction_particle_count"] <= 0:
        raise RuntimeError("moving_boundary mode should have active reaction particles")

    ux_none = by_mode["none"]["projection_zone_ux_final"]
    ux_penalty = by_mode["penalty"]["projection_zone_ux_final"]
    ux_moving = by_mode["moving_boundary"]["projection_zone_ux_final"]
    if not (ux_moving > ux_penalty > ux_none - 1.0e-12):
        raise RuntimeError(
            "projection-zone ux trend failed: "
            f"moving_boundary={ux_moving}, penalty={ux_penalty}, none={ux_none}"
        )

    save_csv_rows(results, os.path.join(out_dir, "mode_matrix_results.csv"), fieldnames=MATRIX_FIELDS)
    np.savez(
        os.path.join(out_dir, "mode_matrix_results.npz"),
        columns=np.asarray(MATRIX_FIELDS),
        modes=np.asarray([result["mode"] for result in results]),
        rows=np.asarray([[result[field] for field in MATRIX_FIELDS[2:]] for result in results], dtype=np.float64),
    )

    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 10 driver mode matrix finished")


if __name__ == "__main__":
    main()
