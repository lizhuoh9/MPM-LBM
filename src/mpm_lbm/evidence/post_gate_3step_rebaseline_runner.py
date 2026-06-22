from __future__ import annotations

import json
import math
import shutil
import time
from pathlib import Path


POST_GATE_3STEP_REBASELINE_FIELDS = [
    "row_name",
    "campaign_id",
    "gate_source_step",
    "previous_rebaseline_step",
    "post_gate_simulation_allowed",
    "allowed_next_step",
    "allowed_next_step_scope",
    "n_grid",
    "n_particles",
    "n_lbm_steps",
    "mpm_substeps_per_lbm_step",
    "coupling_mode",
    "reaction_transfer_mode",
    "geometry_type",
    "runtime_geometry_enabled",
    "wall_velocity_enabled",
    "combined_runtime_geometry_wall_velocity_enabled",
    "real_geometry_enabled",
    "squid_proxy_enabled",
    "link_area_enabled",
    "grid_48_enabled",
    "grid_64_enabled",
    "write_vtk",
    "write_particles",
    "activation_feature_count",
    "driver_run_called",
    "canonical_driver_module",
    "legacy_driver_module_used_as_implementation",
    "initialized",
    "completed_lbm_steps",
    "total_mpm_substeps",
    "diagnostics_row_count",
    "rho_min_final",
    "rho_max_final",
    "rho_min_min",
    "rho_max_max",
    "lbm_max_v_max",
    "mpm_min_J_min",
    "mpm_max_speed_max",
    "projected_mass_final",
    "active_cell_count_final",
    "cell_force_max_norm_max",
    "hydro_force_max_norm_max",
    "bb_link_count_final",
    "bb_link_count_max",
    "bb_max_correction_max",
    "active_reaction_particle_count_final",
    "max_grid_reaction_norm_max",
    "has_nan",
    "has_inf",
    "generated_file_count",
    "geo_path_name",
    "diagnostics_csv_exists",
    "diagnostics_npz_exists",
    "driver_config_exists",
    "elapsed_seconds",
    "runtime_warning",
    "runtime_hard_fail",
    "stable",
    "notes",
]


def build_step77_post_gate_3step_rebaseline_matrix(
    root: Path,
    matrix_policy_path: str = "configs/step77_minimal_post_gate_canonical_driver_3step_rebaseline.json",
    acceptance_policy_path: str = "configs/step77_rebaseline_acceptance_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    matrix_policy = read_json(root / matrix_policy_path)
    acceptance_policy = read_json(root / acceptance_policy_path)
    enforce_step77_policy(matrix_policy)

    rows = [
        run_step77_3step_rebaseline_case(root, config_path, matrix_policy, acceptance_policy)
        for config_path in matrix_policy["required_rebaseline_configs"]
    ]
    summary = step77_3step_rebaseline_summary(rows, matrix_policy, acceptance_policy)
    return rows, summary


def run_step77_3step_rebaseline_case(
    root: Path,
    config_path: str,
    matrix_policy: dict,
    acceptance_policy: dict,
) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

    config = FSIDriverConfig.from_json(root / config_path)
    row_name = row_name_from_config(config_path)
    enforce_step77_config(config, row_name, acceptance_policy)
    run_root = root / matrix_policy["driver_run_root"]
    out_dir = run_root / row_name
    reset_generated_run_dir(run_root, out_dir)

    driver = FSIDriver3D(config, str(out_dir))
    started = time.perf_counter()
    diagnostics = driver.run()
    elapsed_seconds = time.perf_counter() - started
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step77 3-step rebaseline row: {row_name}")

    final = diagnostics[-1]
    has_nan, has_inf = diagnostics_have_nan_or_inf(diagnostics)
    feature_flags = feature_flags_from_config(config)
    row = {
        "row_name": row_name,
        "campaign_id": matrix_policy["campaign_id"],
        "gate_source_step": matrix_policy["previous_rebaseline_step"],
        "previous_rebaseline_step": matrix_policy["previous_rebaseline_step"],
        "post_gate_simulation_allowed": bool(matrix_policy["post_gate_simulation_allowed"]),
        "allowed_next_step": matrix_policy["allowed_next_step"],
        "allowed_next_step_scope": matrix_policy["allowed_next_step_scope"],
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
        "coupling_mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "geometry_type": config.geometry_type,
        **feature_flags,
        "activation_feature_count": sum(1 for value in feature_flags.values() if bool(value)),
        "driver_run_called": True,
        "canonical_driver_module": driver.__class__.__module__,
        "legacy_driver_module_used_as_implementation": driver.__class__.__module__ != matrix_policy["canonical_driver_module"],
        "initialized": bool(driver.initialized),
        "completed_lbm_steps": int(driver.current_lbm_step),
        "total_mpm_substeps": int(driver.total_mpm_substeps),
        "diagnostics_row_count": len(diagnostics),
        "rho_min_final": float(final["rho_min"]),
        "rho_max_final": float(final["rho_max"]),
        "rho_min_min": min_float(diagnostics, "rho_min"),
        "rho_max_max": max_float(diagnostics, "rho_max"),
        "lbm_max_v_max": max_float(diagnostics, "lbm_max_v"),
        "mpm_min_J_min": min_float(diagnostics, "mpm_min_J"),
        "mpm_max_speed_max": max_float(diagnostics, "mpm_max_speed"),
        "projected_mass_final": float(final["projected_mass"]),
        "active_cell_count_final": int(final["active_cell_count"]),
        "cell_force_max_norm_max": max_float(diagnostics, "cell_force_max_norm"),
        "hydro_force_max_norm_max": max_float(diagnostics, "hydro_force_max_norm"),
        "bb_link_count_final": int(final["bb_link_count"]),
        "bb_link_count_max": max_int(diagnostics, "bb_link_count"),
        "bb_max_correction_max": max_float(diagnostics, "bb_max_correction"),
        "active_reaction_particle_count_final": int(final["active_reaction_particle_count"]),
        "max_grid_reaction_norm_max": max_float(diagnostics, "max_grid_reaction_norm"),
        "has_nan": bool(has_nan),
        "has_inf": bool(has_inf),
        "generated_file_count": len([path for path in out_dir.iterdir() if path.is_file()]),
        "geo_path_name": Path(driver.geo_path).name,
        "diagnostics_csv_exists": (out_dir / "diagnostics_timeseries.csv").is_file(),
        "diagnostics_npz_exists": (out_dir / "diagnostics_timeseries.npz").is_file(),
        "driver_config_exists": (out_dir / "driver_config.json").is_file(),
        "elapsed_seconds": elapsed_seconds,
        "runtime_warning": elapsed_seconds > float(acceptance_policy["runtime_warning_seconds"]),
        "runtime_hard_fail": elapsed_seconds > float(acceptance_policy["runtime_hard_fail_seconds"]),
        "stable": False,
        "notes": "minimal post-gate canonical driver 3-step rebaseline completed",
    }
    row["stable"] = step77_3step_rebaseline_row_pass(row, acceptance_policy)
    if not row["stable"]:
        raise RuntimeError(f"Step77 3-step rebaseline row failed acceptance: {row}")
    return row


def enforce_step77_policy(matrix_policy: dict) -> None:
    expected = {
        "post_gate_simulation_allowed": True,
        "allowed_next_step": "Step77",
        "allowed_next_step_scope": "minimal post-gate canonical driver 3-step rebaseline only",
        "gate_status": "ready_for_step77_3step_rebaseline_only",
        "previous_rebaseline_step": "Step76",
        "driver_run_required": True,
        "runtime_code_changed": False,
        "solver_behavior_changed": False,
        "physics_feature_expansion": False,
    }
    actual = {key: matrix_policy.get(key) for key in expected}
    if actual != expected:
        raise RuntimeError(f"Step77 policy does not authorize the 3-step rebaseline envelope: {actual} != {expected}")
    if matrix_policy.get("required_rebaseline_configs") != [
        "configs/step77_canonical_driver_moving_boundary_engineering_32_3step_rebaseline.json"
    ]:
        raise RuntimeError("Step77 must run exactly the canonical 32^3 3-step rebaseline config")


def enforce_step77_config(config, row_name: str, policy: dict) -> None:
    allowed = set(policy["required_row_names"])
    if row_name not in allowed:
        raise RuntimeError(f"unexpected Step77 3-step rebaseline row: {row_name}")
    expected = {
        "n_grid": int(policy["required_n_grid"]),
        "n_particles": int(policy["required_n_particles"]),
        "n_lbm_steps": int(policy["required_n_lbm_steps"]),
        "mpm_substeps_per_lbm_step": int(policy["mpm_substeps_per_lbm_step"]),
    }
    actual = {
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
    }
    if actual != expected:
        raise RuntimeError(f"Step77 config mismatch for {row_name}: {actual} != {expected}")
    if config.coupling_mode != "moving_boundary" or config.reaction_transfer_mode != "engineering":
        raise RuntimeError(f"Step77 row must use moving_boundary engineering transfer: {row_name}")
    if config.output_interval != 1 or config.write_vtk or config.write_particles:
        raise RuntimeError(f"Step77 row must use interval=1 and disable heavy outputs: {row_name}")
    if config.geometry_type != "box" or config.geometry_config_path is not None:
        raise RuntimeError(f"Step77 row must use default box geometry: {row_name}")
    if config.quality_check_enabled or config.quality_check_strict:
        raise RuntimeError(f"Step77 row must keep quality gates disabled: {row_name}")
    if config.boundary_motion_mode != "static" or config.boundary_motion_config_path is not None:
        raise RuntimeError(f"Step77 row must keep boundary motion static: {row_name}")
    if config.wall_velocity_application_mode != "disabled" or config.wall_velocity_application_config_path is not None:
        raise RuntimeError(f"Step77 row must keep wall velocity disabled: {row_name}")
    if config.geometry_motion_mode != "static" or config.geometry_motion_application_mode != "disabled":
        raise RuntimeError(f"Step77 row must keep geometry motion disabled: {row_name}")


def feature_flags_from_config(config) -> dict:
    runtime_geometry_enabled = bool(config.geometry_motion_mode != "static" or config.geometry_motion_application_mode != "disabled")
    wall_velocity_enabled = bool(config.wall_velocity_application_mode != "disabled")
    real_geometry_enabled = bool(config.geometry_type != "box" or config.geometry_config_path is not None)
    squid_proxy_enabled = bool(str(config.geometry_type).startswith("squid"))
    link_area_enabled = bool(config.reaction_transfer_mode == "link_area_experimental")
    return {
        "runtime_geometry_enabled": runtime_geometry_enabled,
        "wall_velocity_enabled": wall_velocity_enabled,
        "combined_runtime_geometry_wall_velocity_enabled": bool(runtime_geometry_enabled and wall_velocity_enabled),
        "real_geometry_enabled": real_geometry_enabled,
        "squid_proxy_enabled": squid_proxy_enabled,
        "link_area_enabled": link_area_enabled,
        "grid_48_enabled": bool(int(config.n_grid) == 48),
        "grid_64_enabled": bool(int(config.n_grid) == 64),
        "write_vtk": bool(config.write_vtk),
        "write_particles": bool(config.write_particles),
    }


def step77_3step_rebaseline_row_pass(row: dict, policy: dict) -> bool:
    expected_geo = f"geo_all_fluid_{int(row['n_grid'])}.dat"
    mode_pass = bool(
        int(row["bb_link_count_max"]) > 0
        and float(row["bb_max_correction_max"]) >= 0.0
        and int(row["active_reaction_particle_count_final"]) >= 0
        and math.isfinite(float(row["max_grid_reaction_norm_max"]))
    )
    feature_pass = bool(
        int(row["activation_feature_count"]) == 0
        and not row["runtime_geometry_enabled"]
        and not row["wall_velocity_enabled"]
        and not row["combined_runtime_geometry_wall_velocity_enabled"]
        and not row["real_geometry_enabled"]
        and not row["squid_proxy_enabled"]
        and not row["link_area_enabled"]
        and not row["grid_48_enabled"]
        and not row["grid_64_enabled"]
        and not row["write_vtk"]
        and not row["write_particles"]
    )
    return bool(
        row["post_gate_simulation_allowed"]
        and row["allowed_next_step"] == "Step77"
        and row["allowed_next_step_scope"] == "minimal post-gate canonical driver 3-step rebaseline only"
        and row["previous_rebaseline_step"] == "Step76"
        and row["driver_run_called"]
        and row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
        and not row["legacy_driver_module_used_as_implementation"]
        and row["initialized"]
        and int(row["n_grid"]) == int(policy["required_n_grid"])
        and int(row["n_particles"]) == int(policy["required_n_particles"])
        and int(row["n_lbm_steps"]) == int(policy["required_n_lbm_steps"])
        and int(row["completed_lbm_steps"]) == int(row["n_lbm_steps"])
        and int(row["total_mpm_substeps"]) >= int(policy["min_total_mpm_substeps"])
        and int(row["diagnostics_row_count"]) >= int(policy["min_diagnostics_row_count"])
        and row["diagnostics_csv_exists"]
        and row["diagnostics_npz_exists"]
        and row["driver_config_exists"]
        and row["geo_path_name"] == expected_geo
        and not row["has_nan"]
        and not row["has_inf"]
        and not row["runtime_hard_fail"]
        and float(row["rho_min_min"]) > float(policy["min_rho_min"])
        and float(row["rho_max_max"]) < float(policy["max_rho_max"])
        and float(row["lbm_max_v_max"]) < float(policy["max_lbm_max_v"])
        and float(row["mpm_min_J_min"]) > float(policy["min_mpm_min_J"])
        and float(row["mpm_max_speed_max"]) < float(policy["max_mpm_max_speed"])
        and float(row["projected_mass_final"]) > float(policy["min_projected_mass_final"])
        and int(row["active_cell_count_final"]) >= int(policy["min_active_cell_count_final"])
        and mode_pass
        and feature_pass
        and finite_values(row, excluded={"notes", "row_name", "campaign_id", "gate_source_step", "previous_rebaseline_step", "allowed_next_step", "allowed_next_step_scope", "coupling_mode", "reaction_transfer_mode", "geometry_type", "canonical_driver_module", "geo_path_name"})
    )


def step77_3step_rebaseline_summary(rows: list[dict], matrix_policy: dict, acceptance_policy: dict) -> dict:
    required_names = set(acceptance_policy["required_row_names"])
    optional_names = set(acceptance_policy.get("optional_row_names", []))
    row_names = {row["row_name"] for row in rows}
    required_rows = [row for row in rows if row["row_name"] in required_names]
    slowest = max(rows, key=lambda row: float(row["elapsed_seconds"])) if rows else {}
    summary = {
        "activation_feature_count": sum(int(row["activation_feature_count"]) for row in rows),
        "allowed_next_step": matrix_policy["allowed_next_step"],
        "allowed_next_step_scope": matrix_policy["allowed_next_step_scope"],
        "canonical_driver_module": matrix_policy["canonical_driver_module"],
        "driver_run_called_count": sum(1 for row in rows if row["driver_run_called"]),
        "driver_run_required": bool(matrix_policy["driver_run_required"]),
        "gate_status": matrix_policy["gate_status"],
        "has_inf_count": sum(1 for row in rows if row["has_inf"]),
        "has_nan_count": sum(1 for row in rows if row["has_nan"]),
        "legacy_driver_module_used_count": sum(1 for row in rows if row["legacy_driver_module_used_as_implementation"]),
        "max_lbm_max_v": max(float(row["lbm_max_v_max"]) for row in rows),
        "max_mpm_max_speed": max(float(row["mpm_max_speed_max"]) for row in rows),
        "max_rho_max": max(float(row["rho_max_max"]) for row in rows),
        "min_completed_lbm_steps": min(int(row["completed_lbm_steps"]) for row in rows),
        "min_diagnostics_row_count": min(int(row["diagnostics_row_count"]) for row in rows),
        "min_mpm_min_J": min(float(row["mpm_min_J_min"]) for row in rows),
        "min_rho_min": min(float(row["rho_min_min"]) for row in rows),
        "min_total_mpm_substeps": min(int(row["total_mpm_substeps"]) for row in rows),
        "missing_required_rows": sorted(required_names - row_names),
        "optional_row_count": sum(1 for row in rows if row["row_name"] in optional_names),
        "physics_feature_expansion": bool(matrix_policy["physics_feature_expansion"]),
        "post_gate_3step_rebaseline_matrix_pass": False,
        "post_gate_simulation_allowed": bool(matrix_policy["post_gate_simulation_allowed"]),
        "previous_rebaseline_step": matrix_policy["previous_rebaseline_step"],
        "required_row_count": len(required_names),
        "required_rows_present": sorted(required_names & row_names),
        "required_stable_count": sum(1 for row in required_rows if row["stable"]),
        "row_count": len(rows),
        "runtime_code_changed": bool(matrix_policy["runtime_code_changed"]),
        "runtime_hard_fail_count": sum(1 for row in rows if row["runtime_hard_fail"]),
        "runtime_warning_count": sum(1 for row in rows if row["runtime_warning"]),
        "slowest_elapsed_seconds": float(slowest.get("elapsed_seconds", 0.0)),
        "slowest_row_name": slowest.get("row_name", ""),
        "solver_behavior_changed": bool(matrix_policy["solver_behavior_changed"]),
        "stable_count": sum(1 for row in rows if row["stable"]),
        "total_elapsed_seconds": sum(float(row["elapsed_seconds"]) for row in rows),
    }
    summary["post_gate_3step_rebaseline_matrix_pass"] = bool(
        summary["gate_status"] == "ready_for_step77_3step_rebaseline_only"
        and summary["post_gate_simulation_allowed"] is True
        and summary["allowed_next_step"] == "Step77"
        and summary["allowed_next_step_scope"] == "minimal post-gate canonical driver 3-step rebaseline only"
        and summary["previous_rebaseline_step"] == "Step76"
        and summary["missing_required_rows"] == []
        and summary["required_stable_count"] == summary["required_row_count"]
        and summary["stable_count"] == summary["row_count"]
        and summary["driver_run_called_count"] == summary["row_count"]
        and summary["legacy_driver_module_used_count"] == 0
        and summary["has_nan_count"] == 0
        and summary["has_inf_count"] == 0
        and summary["optional_row_count"] == 0
        and summary["activation_feature_count"] == 0
        and summary["runtime_hard_fail_count"] == 0
        and not summary["runtime_code_changed"]
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
    )
    return summary


def reset_generated_run_dir(run_root: Path, out_dir: Path) -> None:
    run_root.mkdir(parents=True, exist_ok=True)
    resolved_run_root = run_root.resolve()
    resolved_out_dir = out_dir.resolve()
    if resolved_out_dir.parent != resolved_run_root:
        raise RuntimeError(f"refusing to reset unexpected Step77 run directory: {out_dir}")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)


def row_name_from_config(config_path: str) -> str:
    return Path(config_path).stem.removeprefix("step77_")


def min_float(rows: list[dict], key: str) -> float:
    return min(float(row[key]) for row in rows)


def max_float(rows: list[dict], key: str) -> float:
    return max(float(row[key]) for row in rows)


def max_int(rows: list[dict], key: str) -> int:
    return max(int(row[key]) for row in rows)


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
