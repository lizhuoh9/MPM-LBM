from __future__ import annotations

from pathlib import Path

import numpy as np

from src.mpm_lbm.evidence.step111_common import read_csv_rows, read_json, safe_ratio, write_csv_rows, write_json
from src.mpm_lbm.sim.geometry.duct_flap_proxy import duct_flap_proxy_component_masks


MONITOR_FIELDS = [
    "step",
    "time_s",
    "total_displacement_m",
    "x_displacement_m",
    "y_displacement_m",
    "z_displacement_m",
]


def append_step111_monitors(driver, policy: dict, monitor_rows: dict[str, list[dict]], step: int) -> None:
    for name, row in compute_step111_monitor_rows(driver, policy, step).items():
        monitor_rows[name].append(row)


def compute_step111_monitor_rows(driver, policy: dict, step: int) -> dict[str, dict]:
    initial = np.asarray(driver.initial_particle_positions, dtype=np.float64)
    current = np.asarray(driver.solid.x.to_numpy(), dtype=np.float64)
    displacement_m = (current - initial) * float(driver._duct_length_scale_m())
    target = public_monitor_normalized_position(driver, policy)
    distances = np.linalg.norm(initial - target, axis=1)
    nearest_index = int(np.argmin(distances))
    top_indices = np.argsort(distances)[: min(5, len(distances))]
    radius_indices = np.nonzero(distances <= float(policy["public_monitor_radius_normalized"]))[0]
    if radius_indices.size == 0:
        radius_indices = top_indices
    time_s = float(step) * float(driver.config.official_fsi_dt_s)
    return {
        "nearest_public_monitor_point": monitor_row(step, time_s, displacement_m[nearest_index]),
        "top_5_nearest_public_monitor_mean": monitor_row(step, time_s, np.mean(displacement_m[top_indices], axis=0)),
        "radius_public_monitor_mean": monitor_row(step, time_s, np.mean(displacement_m[radius_indices], axis=0)),
    }


def public_monitor_normalized_position(driver, policy: dict) -> np.ndarray:
    geometry_config = driver._make_geometry_config()
    duct = geometry_config.duct or {}
    duct_x = [float(value) for value in duct.get("x", [0.0, 1.0])]
    duct_y = [float(value) for value in duct.get("y", [0.0, 1.0])]
    duct_z = [float(value) for value in duct.get("z", [0.0, 1.0])]
    x_norm = duct_x[0] + safe_ratio(float(policy["public_monitor_x_m"]), float(policy["duct_length_m"])) * (duct_x[1] - duct_x[0])
    y_norm = duct_y[0] + safe_ratio(float(policy["public_monitor_y_m"]), float(policy["duct_height_m"])) * (duct_y[1] - duct_y[0])
    z_norm = 0.5 * (duct_z[0] + duct_z[1])
    return np.asarray([x_norm, y_norm, z_norm], dtype=np.float64)


def monitor_row(step: int, time_s: float, displacement: np.ndarray) -> dict:
    vector = np.asarray(displacement, dtype=np.float64)
    return {
        "step": int(step),
        "time_s": float(time_s),
        "total_displacement_m": float(np.linalg.norm(vector)),
        "x_displacement_m": float(vector[0]),
        "y_displacement_m": float(vector[1]),
        "z_displacement_m": float(vector[2]),
    }


def write_step111_monitor_timeseries(out_dir: Path, monitor_rows: dict[str, list[dict]]) -> None:
    for name, rows in monitor_rows.items():
        write_csv_rows(out_dir / f"monitor_timeseries_{name}.csv", rows, MONITOR_FIELDS)


def fixed_base_stats(driver) -> dict:
    initial = np.asarray(driver.initial_particle_positions, dtype=np.float64)
    current = np.asarray(driver.solid.x.to_numpy(), dtype=np.float64)
    velocity = np.asarray(driver.solid.v.to_numpy(), dtype=np.float64)
    masks = duct_flap_proxy_component_masks(initial, driver._make_geometry_config())
    fixed = np.asarray(masks["fixed_base"], dtype=bool)
    if not np.any(fixed):
        return {
            "fixed_base_constraint_applied": False,
            "fixed_base_max_displacement_norm": 0.0,
            "fixed_base_max_velocity_norm": 0.0,
            "fixed_base_particle_count": 0,
        }
    displacement = (current - initial) * float(driver._duct_length_scale_m())
    return {
        "fixed_base_constraint_applied": True,
        "fixed_base_max_displacement_norm": float(np.max(np.linalg.norm(displacement[fixed], axis=1))),
        "fixed_base_max_velocity_norm": float(np.max(np.linalg.norm(velocity[fixed], axis=1))),
        "fixed_base_particle_count": int(np.count_nonzero(fixed)),
    }


def build_step111_monitor_report(
    root: Path,
    solver_dir: str = "outputs/step111_real_solver_candidate",
    policy_path: str = "configs/step111_monitor_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    out_dir = root / solver_dir
    policy = read_json(root / policy_path)
    rows = []
    for name in policy["required_monitor_names"]:
        monitor_rows = read_csv_rows(out_dir / f"monitor_timeseries_{name}.csv")
        rows.append(
            {
                "monitor_name": name,
                "monitor_source": "real_solver_particles",
                "row_count": len(monitor_rows),
                "time_start_s": float(monitor_rows[0]["time_s"]),
                "time_end_s": float(monitor_rows[-1]["time_s"]),
                "peak_displacement_m": max(abs(float(row["total_displacement_m"])) for row in monitor_rows),
                "validation_claim_allowed": False,
                "direct_quantitative_equivalence_allowed": False,
                "stable": len(monitor_rows) == int(policy["expected_monitor_rows"]),
            }
        )
    summary = {
        "direct_quantitative_equivalence_allowed": False,
        "monitor_alignment_pass": all(row["stable"] for row in rows),
        "monitor_source": "real_solver_particles",
        "required_monitor_count": len(policy["required_monitor_names"]),
        "row_count": len(rows),
        "validation_claim_allowed": False,
    }
    write_json(out_dir / "monitor_definition_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "monitor_definition_report.csv", rows)
    if not summary["monitor_alignment_pass"]:
        raise RuntimeError(f"Step111 monitor report failed: {summary}")
    return rows, summary
