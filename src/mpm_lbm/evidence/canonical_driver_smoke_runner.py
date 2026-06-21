from __future__ import annotations

import json
import math
import shutil
import time
from pathlib import Path


SMOKE_FIELDS = [
    "row_name",
    "coupling_mode",
    "reaction_transfer_mode",
    "n_grid",
    "n_particles",
    "n_lbm_steps",
    "mpm_substeps_per_lbm_step",
    "completed_lbm_steps",
    "total_mpm_substeps",
    "diagnostics_row_count",
    "initialized",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "projected_mass",
    "active_cell_count",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "bb_link_count",
    "bb_max_correction",
    "active_reaction_particle_count",
    "max_grid_reaction_norm",
    "has_nan",
    "has_inf",
    "driver_run_called",
    "canonical_driver_module",
    "legacy_driver_module_used_as_implementation",
    "penalty_coupler_exists",
    "moving_boundary_coupler_exists",
    "link_area_coupler_exists",
    "geo_path_name",
    "generated_file_count",
    "elapsed_seconds",
    "stable",
    "notes",
]


def build_canonical_driver_smoke_matrix(
    root: Path,
    matrix_policy_path: str = "configs/step59_canonical_fsidriver_real_smoke_simulation.json",
    acceptance_policy_path: str = "configs/step59_smoke_acceptance_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    matrix_policy = read_json(root / matrix_policy_path)
    acceptance_policy = read_json(root / acceptance_policy_path)
    rows = [
        run_smoke_case(root, config_path, matrix_policy, acceptance_policy)
        for config_path in matrix_policy["required_smoke_configs"]
    ]
    summary = smoke_summary(rows, matrix_policy, acceptance_policy)
    return rows, summary


def run_smoke_case(root: Path, config_path: str, matrix_policy: dict, acceptance_policy: dict) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

    config = FSIDriverConfig.from_json(root / config_path)
    row_name = row_name_from_config(config_path)
    enforce_smoke_config(config, row_name, acceptance_policy)
    run_root = root / matrix_policy["driver_run_root"]
    out_dir = run_root / row_name
    reset_generated_run_dir(run_root, out_dir)

    driver = FSIDriver3D(config, str(out_dir))
    started = time.perf_counter()
    diagnostics = driver.run()
    elapsed_seconds = time.perf_counter() - started
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step 59 smoke row: {row_name}")

    final = diagnostics[-1]
    has_nan, has_inf = diagnostics_have_nan_or_inf(diagnostics)
    canonical_module = matrix_policy["canonical_driver_module"]
    row = {
        "row_name": row_name,
        "coupling_mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
        "completed_lbm_steps": int(driver.current_lbm_step),
        "total_mpm_substeps": int(driver.total_mpm_substeps),
        "diagnostics_row_count": len(diagnostics),
        "initialized": bool(driver.initialized),
        "rho_min": float(final["rho_min"]),
        "rho_max": float(final["rho_max"]),
        "lbm_max_v": float(final["lbm_max_v"]),
        "mpm_min_J": float(final["mpm_min_J"]),
        "mpm_max_speed": float(final["mpm_max_speed"]),
        "projected_mass": float(final["projected_mass"]),
        "active_cell_count": int(final["active_cell_count"]),
        "cell_force_max_norm": float(final["cell_force_max_norm"]),
        "hydro_force_max_norm": float(final["hydro_force_max_norm"]),
        "bb_link_count": int(final["bb_link_count"]),
        "bb_max_correction": float(final["bb_max_correction"]),
        "active_reaction_particle_count": int(final["active_reaction_particle_count"]),
        "max_grid_reaction_norm": float(final["max_grid_reaction_norm"]),
        "has_nan": bool(has_nan),
        "has_inf": bool(has_inf),
        "driver_run_called": True,
        "canonical_driver_module": driver.__class__.__module__,
        "legacy_driver_module_used_as_implementation": driver.__class__.__module__ != canonical_module,
        "penalty_coupler_exists": driver.penalty_coupler is not None,
        "moving_boundary_coupler_exists": driver.mb_coupler is not None,
        "link_area_coupler_exists": driver.link_area_coupler is not None,
        "geo_path_name": Path(driver.geo_path).name,
        "generated_file_count": len([path for path in out_dir.iterdir() if path.is_file()]),
        "elapsed_seconds": elapsed_seconds,
        "stable": False,
        "notes": "canonical driver real smoke completed",
    }
    row["stable"] = smoke_row_pass(row, acceptance_policy)
    if not row["stable"]:
        raise RuntimeError(f"Step 59 smoke row failed acceptance: {row}")
    return row


def enforce_smoke_config(config, row_name: str, policy: dict) -> None:
    if row_name not in policy["required_row_names"]:
        raise RuntimeError(f"unexpected Step 59 smoke row: {row_name}")
    expected = {
        "n_grid": int(policy["n_grid"]),
        "n_particles": int(policy["n_particles"]),
        "n_lbm_steps": int(policy["n_lbm_steps"]),
        "mpm_substeps_per_lbm_step": int(policy["mpm_substeps_per_lbm_step"]),
    }
    actual = {
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
    }
    if actual != expected:
        raise RuntimeError(f"Step 59 config mismatch for {row_name}: {actual} != {expected}")
    if config.output_interval != 1 or config.write_vtk or config.write_particles:
        raise RuntimeError(f"Step 59 smoke rows must use interval=1 and disable heavy outputs: {row_name}")
    if config.geometry_type != "box" or config.geometry_config_path is not None:
        raise RuntimeError(f"Step 59 smoke rows must use default box geometry: {row_name}")
    if config.quality_check_enabled or config.quality_check_strict:
        raise RuntimeError(f"Step 59 smoke rows must keep quality gates disabled: {row_name}")
    if config.boundary_motion_mode != "static" or config.boundary_motion_config_path is not None:
        raise RuntimeError(f"Step 59 smoke rows must keep boundary motion static: {row_name}")
    if config.wall_velocity_application_mode != "disabled" or config.wall_velocity_application_config_path is not None:
        raise RuntimeError(f"Step 59 smoke rows must keep wall velocity disabled: {row_name}")
    if config.geometry_motion_mode != "static" or config.geometry_motion_application_mode != "disabled":
        raise RuntimeError(f"Step 59 smoke rows must keep geometry motion disabled: {row_name}")


def smoke_row_pass(row: dict, policy: dict) -> bool:
    mode_pass = True
    if row["coupling_mode"] == "penalty":
        mode_pass = bool(row["penalty_coupler_exists"])
    if row["coupling_mode"] == "moving_boundary":
        mode_pass = bool(row["moving_boundary_coupler_exists"])
    return bool(
        row["driver_run_called"]
        and row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
        and not row["legacy_driver_module_used_as_implementation"]
        and int(row["completed_lbm_steps"]) == int(policy["n_lbm_steps"])
        and int(row["total_mpm_substeps"]) >= int(policy["min_total_mpm_substeps"])
        and int(row["diagnostics_row_count"]) >= int(policy["min_diagnostics_row_count"])
        and float(row["rho_min"]) > float(policy["rho_min_lower_bound"])
        and float(row["rho_max"]) < float(policy["rho_max_upper_bound"])
        and float(row["lbm_max_v"]) < float(policy["lbm_max_v_upper_bound"])
        and float(row["mpm_min_J"]) > float(policy["mpm_min_J_lower_bound"])
        and int(row["active_cell_count"]) >= 0
        and int(row["bb_link_count"]) >= 0
        and int(row["active_reaction_particle_count"]) >= 0
        and row["geo_path_name"] == "geo_all_fluid_16.dat"
        and not row["has_nan"]
        and not row["has_inf"]
        and mode_pass
        and finite_values(row, excluded={"notes", "row_name", "coupling_mode", "reaction_transfer_mode", "canonical_driver_module", "geo_path_name"})
    )


def smoke_summary(rows: list[dict], matrix_policy: dict, acceptance_policy: dict) -> dict:
    required_names = set(acceptance_policy["required_row_names"])
    row_names = {row["row_name"] for row in rows}
    summary = {
        "row_count": len(rows),
        "required_row_count": len(required_names),
        "required_rows_present": sorted(required_names & row_names),
        "missing_required_rows": sorted(required_names - row_names),
        "stable_count": sum(1 for row in rows if row["stable"]),
        "driver_run_called_count": sum(1 for row in rows if row["driver_run_called"]),
        "legacy_driver_module_used_count": sum(1 for row in rows if row["legacy_driver_module_used_as_implementation"]),
        "min_completed_lbm_steps": min(int(row["completed_lbm_steps"]) for row in rows),
        "min_total_mpm_substeps": min(int(row["total_mpm_substeps"]) for row in rows),
        "min_diagnostics_row_count": min(int(row["diagnostics_row_count"]) for row in rows),
        "min_rho_min": min(float(row["rho_min"]) for row in rows),
        "max_rho_max": max(float(row["rho_max"]) for row in rows),
        "max_lbm_max_v": max(float(row["lbm_max_v"]) for row in rows),
        "min_mpm_min_J": min(float(row["mpm_min_J"]) for row in rows),
        "max_mpm_max_speed": max(float(row["mpm_max_speed"]) for row in rows),
        "has_nan_count": sum(1 for row in rows if row["has_nan"]),
        "has_inf_count": sum(1 for row in rows if row["has_inf"]),
        "canonical_driver_module": matrix_policy["canonical_driver_module"],
        "driver_run_required": bool(matrix_policy["driver_run_required"]),
        "solver_behavior_changed": bool(matrix_policy["solver_behavior_changed"]),
        "physics_feature_expansion": bool(matrix_policy["physics_feature_expansion"]),
        "canonical_driver_smoke_matrix_pass": False,
    }
    summary["canonical_driver_smoke_matrix_pass"] = bool(
        summary["row_count"] == summary["required_row_count"]
        and summary["missing_required_rows"] == []
        and summary["stable_count"] == summary["row_count"]
        and summary["driver_run_called_count"] == summary["row_count"]
        and summary["legacy_driver_module_used_count"] == 0
        and summary["has_nan_count"] == 0
        and summary["has_inf_count"] == 0
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
    )
    return summary


def reset_generated_run_dir(run_root: Path, out_dir: Path) -> None:
    run_root.mkdir(parents=True, exist_ok=True)
    resolved_run_root = run_root.resolve()
    resolved_out_dir = out_dir.resolve()
    if resolved_out_dir.parent != resolved_run_root:
        raise RuntimeError(f"refusing to reset unexpected Step 59 run directory: {out_dir}")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)


def row_name_from_config(config_path: str) -> str:
    return Path(config_path).stem.removeprefix("step59_")


def diagnostics_have_nan_or_inf(rows: list[dict]) -> tuple[bool, bool]:
    has_nan = False
    has_inf = False
    for row in rows:
        for value in row.values():
            if isinstance(value, (int, float)):
                has_nan = has_nan or math.isnan(float(value))
                has_inf = has_inf or math.isinf(float(value))
    return has_nan, has_inf


def finite_values(row, excluded=()) -> bool:
    values = row.values() if isinstance(row, dict) else row
    iterable = (
        ((key, value) for key, value in row.items() if key not in excluded)
        if isinstance(row, dict)
        else ((None, value) for value in values)
    )
    for _, value in iterable:
        if isinstance(value, bool) or value == "":
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number):
            return False
    return True


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
