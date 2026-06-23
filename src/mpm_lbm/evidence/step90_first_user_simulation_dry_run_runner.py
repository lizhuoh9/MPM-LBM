from __future__ import annotations

import math
import time
from pathlib import Path

from src.mpm_lbm.evidence.step84_runtime_geometry_wall_velocity_combined_smoke_runner import (
    MUTATION_FLAG_FIELDS,
    boundary_report_pass,
    combined_report_repo_roots,
    diagnostics_have_nan_or_inf,
    finite_values,
    geometry_report_pass,
    max_float,
    max_int,
    min_float,
    report_summary,
)
from src.mpm_lbm.evidence.step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_runner import (
    STRING_FIELDS,
    activation_feature_count,
    feature_flags_from_config,
    path_exists_from_repo_root,
    read_json,
    reset_generated_run_dir,
    write_json,
)


def build_step90_first_user_simulation_dry_run_matrix(
    root: Path,
    matrix_policy_path: str = "configs/step90_first_user_simulation_dry_run_matrix.json",
    acceptance_policy_path: str = "configs/step90_first_user_simulation_dry_run_acceptance_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    matrix_policy = read_json(root / matrix_policy_path)
    acceptance_policy = read_json(root / acceptance_policy_path)
    enforce_step90_policy(matrix_policy)
    rows = [
        run_step90_first_user_simulation_dry_run_case(root, config_path, matrix_policy, acceptance_policy)
        for config_path in matrix_policy["required_smoke_configs"]
    ]
    summary = step90_first_user_simulation_dry_run_summary(rows, matrix_policy, acceptance_policy)
    return rows, summary


def run_step90_first_user_simulation_dry_run_case(
    root: Path,
    config_path: str,
    matrix_policy: dict,
    acceptance_policy: dict,
) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D
    from src.mpm_lbm.sim.geometry.config import GeometryConfig
    from src.mpm_lbm.sim.geometry.sampler import GeometrySampler3D

    row_name = row_name_from_config(config_path)
    config = FSIDriverConfig.from_json(root / config_path)
    enforce_step90_config(root, config, row_name, acceptance_policy)
    geometry_config = GeometryConfig.from_json(config.geometry_config_path)
    sampling_stats = GeometrySampler3D(geometry_config).sample_particles()["sampling_stats"]

    run_root = root / matrix_policy["driver_run_root"]
    out_dir = run_root / row_name
    reset_generated_run_dir(run_root, out_dir)

    driver = FSIDriver3D(config, str(out_dir))
    started = time.perf_counter()
    with combined_report_repo_roots(root):
        diagnostics = driver.run()
    elapsed_seconds = time.perf_counter() - started
    write_json(out_dir / "driver_timing.json", driver.performance_row())
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step90 first user dry-run row: {row_name}")

    final = diagnostics[-1]
    has_nan, has_inf = diagnostics_have_nan_or_inf(diagnostics)
    feature_flags = feature_flags_from_config(config)
    quality_report_path = out_dir / "geometry_quality_report.json"
    quality_payload = read_json(quality_report_path) if quality_report_path.is_file() else {}
    quality_gate = quality_payload.get("gate", {})
    quality_report = quality_payload.get("report", {})
    geometry_report_path = out_dir / "geometry_motion_interface_report.json"
    geometry_summary = report_summary(geometry_report_path)
    boundary_report_path = out_dir / "boundary_motion_interface_report.json"
    boundary_summary = report_summary(boundary_report_path)
    wall_report_path = out_dir / "wall_velocity_application_report.json"
    wall_summary = report_summary(wall_report_path)

    row = {
        "row_name": row_name,
        "campaign_id": matrix_policy["campaign_id"],
        "gate_source_step": matrix_policy["gate_source_step"],
        "previous_step": matrix_policy["previous_step"],
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
        "geometry_config_path": config.geometry_config_path,
        "geometry_config_path_exists": path_exists_from_repo_root(root, config.geometry_config_path),
        "target_u_lbm": list(config.target_u_lbm),
        "boundary_motion_mode": config.boundary_motion_mode,
        "geometry_motion_mode": config.geometry_motion_mode,
        "geometry_motion_application_mode": config.geometry_motion_application_mode,
        "wall_velocity_application_mode": config.wall_velocity_application_mode,
        **feature_flags,
        "activation_feature_count": activation_feature_count(feature_flags),
        "driver_run_called": True,
        "canonical_driver_module": driver.__class__.__module__,
        "legacy_driver_module_used_as_implementation": driver.__class__.__module__
        != matrix_policy["canonical_driver_module"],
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
        "geometry_quality_report_exists": quality_report_path.is_file(),
        "geometry_quality_report_pass": bool(quality_gate.get("pass", False)),
        "geometry_quality_strict": bool(quality_gate.get("strict", True)),
        "geometry_quality_warning_count": len(quality_gate.get("warnings", [])),
        "geometry_quality_reason_count": len(quality_gate.get("reasons", [])),
        "quality_report_geometry_type": quality_report.get("geometry_type", ""),
        "quality_report_empty": bool(quality_report.get("empty", True)),
        "quality_report_occupied_count": int(quality_report.get("occupied_count", 0)),
        "quality_report_surface_voxel_count": int(quality_report.get("surface_voxel_count", 0)),
        "quality_report_touches_domain_boundary": bool(quality_report.get("touches_domain_boundary", True)),
        "sampling_stats_exist": bool(sampling_stats),
        "sampling_geometry_type": sampling_stats.get("geometry_type", ""),
        "sampling_particle_count": int(sampling_stats.get("particle_count", 0)),
        "mantle_particle_count": int(sampling_stats.get("mantle_particle_count", 0)),
        "head_particle_count": int(sampling_stats.get("head_particle_count", 0)),
        "arms_particle_count": int(sampling_stats.get("arms_particle_count", 0)),
        "left_fin_particle_count": int(sampling_stats.get("left_fin_particle_count", 0)),
        "right_fin_particle_count": int(sampling_stats.get("right_fin_particle_count", 0)),
        "geometry_motion_config_path_exists": path_exists_from_repo_root(root, config.geometry_motion_config_path),
        "geometry_motion_application_config_path_exists": path_exists_from_repo_root(
            root, config.geometry_motion_application_config_path
        ),
        "geometry_motion_interface_report_exists": geometry_report_path.is_file(),
        "geometry_motion_interface_report_pass": geometry_report_pass(geometry_report_path, geometry_summary),
        "no_op_pass": bool(geometry_summary.get("no_op_pass", False)),
        "config_validation_pass": bool(geometry_summary.get("config_validation_pass", False)),
        "diagnostic_only": bool(geometry_summary.get("diagnostic_only", False)),
        "mutation_flag_enabled_count": int(geometry_summary.get("mutation_flag_enabled_count", -1)),
        **{field: bool(geometry_summary.get(field, True)) for field in MUTATION_FLAG_FIELDS},
        "boundary_motion_config_path_exists": path_exists_from_repo_root(root, config.boundary_motion_config_path),
        "boundary_motion_interface_report_exists": boundary_report_path.is_file(),
        "boundary_motion_interface_report_pass": boundary_report_pass(boundary_report_path, boundary_summary),
        "boundary_motion_diagnostic_only": bool(boundary_summary.get("diagnostic_only", False)),
        "wall_velocity_application_config_path_exists": path_exists_from_repo_root(
            root, config.wall_velocity_application_config_path
        ),
        "wall_velocity_application_report_exists": wall_report_path.is_file(),
        "wall_velocity_application_report_pass": bool(wall_summary.get("report_pass", False)),
        "target_lbm_field": wall_summary.get("target_lbm_field", ""),
        "application_policy": wall_summary.get("application_policy", ""),
        "apply_to_lbm_solid_vel_wall_velocity": bool(wall_summary.get("apply_to_lbm_solid_vel", False)),
        "apply_to_lbm_populations": bool(wall_summary.get("apply_to_lbm_populations", True)),
        "apply_to_mpm": bool(wall_summary.get("apply_to_mpm", True)),
        "apply_to_projector": bool(wall_summary.get("apply_to_projector", True)),
        "modify_bounceback_formula": bool(wall_summary.get("modify_bounceback_formula", True)),
        "jet_model_enabled": bool(wall_summary.get("jet_model_enabled", True)),
        "actuation_claim_enabled": bool(wall_summary.get("actuation_claim_enabled", True)),
        "applied_cell_count": int(wall_summary.get("applied_cell_count", 0)),
        "max_applied_velocity_norm": float(wall_summary.get("max_applied_velocity_norm", math.inf)),
        "wall_velocity_cap_lbm": float(wall_summary.get("wall_velocity_cap_lbm", 0.0)),
        "finite_pass": bool(wall_summary.get("finite_pass", False)),
        "cap_pass": bool(wall_summary.get("cap_pass", False)),
        "lbm_population_update_count": int(wall_summary.get("lbm_population_update_count", -1)),
        "has_nan": bool(has_nan),
        "has_inf": bool(has_inf),
        "generated_file_count": len([path for path in out_dir.iterdir() if path.is_file()]),
        "geo_path_name": Path(driver.geo_path).name,
        "diagnostics_csv_exists": (out_dir / "diagnostics_timeseries.csv").is_file(),
        "diagnostics_npz_exists": (out_dir / "diagnostics_timeseries.npz").is_file(),
        "driver_config_exists": (out_dir / "driver_config.json").is_file(),
        "driver_timing_exists": (out_dir / "driver_timing.json").is_file(),
        "elapsed_seconds": elapsed_seconds,
        "runtime_warning": elapsed_seconds > float(acceptance_policy["runtime_warning_seconds"]),
        "runtime_hard_fail": elapsed_seconds > float(acceptance_policy["runtime_hard_fail_seconds"]),
        "stable": False,
        "notes": (
            "first user simulation dry run with squid_proxy, runtime geometry diagnostic-only, "
            "and wall velocity solid_vel completed"
        ),
    }
    row["stable"] = step90_first_user_simulation_dry_run_row_pass(row, acceptance_policy)
    if not row["stable"]:
        raise RuntimeError(f"Step90 first user simulation dry-run row failed acceptance: {row}")
    return row


def enforce_step90_policy(matrix_policy: dict) -> None:
    expected = {
        "post_gate_simulation_allowed": True,
        "allowed_next_step": "Step90",
        "allowed_next_step_scope": (
            "first user simulation dry run 32^3 5-step squid_proxy runtime geometry "
            "diagnostic-only wall velocity solid_vel only"
        ),
        "gate_source_step": "Step89",
        "previous_step": "Step89",
        "driver_run_required": True,
        "runtime_code_changed": False,
        "solver_behavior_changed": False,
        "physics_feature_expansion": (
            "first_user_dry_run_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel"
        ),
    }
    actual = {key: matrix_policy.get(key) for key in expected}
    if actual != expected:
        raise RuntimeError(f"Step90 policy mismatch: {actual} != {expected}")
    if matrix_policy.get("required_smoke_configs") != [
        "configs/step90_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run.json"
    ]:
        raise RuntimeError("Step90 must run exactly one first user simulation dry-run config")


def enforce_step90_config(root: Path, config, row_name: str, policy: dict) -> None:
    if row_name not in set(policy["required_row_names"]):
        raise RuntimeError(f"unexpected Step90 first user dry-run row: {row_name}")
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
        raise RuntimeError(f"Step90 config mismatch for {row_name}: {actual} != {expected}")
    if config.coupling_mode != "moving_boundary" or config.reaction_transfer_mode != "engineering":
        raise RuntimeError(f"Step90 row must use moving_boundary engineering transfer: {row_name}")
    if list(config.target_u_lbm) != list(policy["required_target_u_lbm"]):
        raise RuntimeError(f"Step90 row must use row-local zero background target_u_lbm: {row_name}")
    if config.geometry_type != policy["required_geometry_type"]:
        raise RuntimeError(f"Step90 row must use squid_proxy geometry: {row_name}")
    if config.geometry_config_path != policy["required_geometry_config_path"]:
        raise RuntimeError(f"Step90 row must use the Step85 squid_proxy geometry config: {row_name}")
    if config.output_interval != 1 or config.write_vtk or config.write_particles:
        raise RuntimeError(f"Step90 row must use interval=1 and disable heavy outputs: {row_name}")
    if not config.quality_check_enabled or config.quality_check_strict:
        raise RuntimeError(f"Step90 row must enable non-strict geometry quality reporting: {row_name}")
    if config.boundary_motion_mode != "prescribed_kinematic" or not config.boundary_motion_report_enabled:
        raise RuntimeError(f"Step90 row must write prescribed_kinematic boundary motion report: {row_name}")
    if config.geometry_motion_mode != "prescribed_kinematic":
        raise RuntimeError(f"Step90 row must use prescribed_kinematic geometry motion: {row_name}")
    if config.geometry_motion_application_mode != "diagnostic_only":
        raise RuntimeError(f"Step90 row must use diagnostic_only geometry motion application: {row_name}")
    if not config.geometry_motion_report_enabled or not config.geometry_motion_application_report_enabled:
        raise RuntimeError(f"Step90 row must write geometry motion reports: {row_name}")
    if config.wall_velocity_application_mode != "solid_vel_experimental":
        raise RuntimeError(f"Step90 row must use solid_vel_experimental wall velocity: {row_name}")
    if not config.wall_velocity_application_report_enabled:
        raise RuntimeError(f"Step90 row must write wall velocity application report: {row_name}")
    for label, relative_path in {
        "boundary_motion_config_path": config.boundary_motion_config_path,
        "geometry_config_path": config.geometry_config_path,
        "geometry_motion_config_path": config.geometry_motion_config_path,
        "geometry_motion_application_config_path": config.geometry_motion_application_config_path,
        "wall_velocity_application_config_path": config.wall_velocity_application_config_path,
    }.items():
        if not path_exists_from_repo_root(root, relative_path):
            raise RuntimeError(f"Step90 {label} is not resolvable: {relative_path}")


def step90_first_user_simulation_dry_run_row_pass(row: dict, policy: dict) -> bool:
    expected_geo = f"geo_all_fluid_{int(row['n_grid'])}.dat"
    mode_pass = bool(
        int(row["bb_link_count_max"]) > 0
        and float(row["bb_max_correction_max"]) >= 0.0
        and int(row["active_reaction_particle_count_final"]) >= 0
        and math.isfinite(float(row["max_grid_reaction_norm_max"]))
    )
    feature_pass = bool(
        int(row["activation_feature_count"]) == 3
        and row["procedural_geometry_enabled"]
        and row["squid_proxy_enabled"]
        and row["runtime_geometry_enabled"]
        and row["wall_velocity_enabled"]
        and row["combined_runtime_geometry_wall_velocity_enabled"]
        and not row["real_geometry_candidate_enabled"]
        and not row["real_geometry_enabled"]
        and not row["link_area_enabled"]
        and not row["grid_48_enabled"]
        and not row["grid_64_enabled"]
        and not row["write_vtk"]
        and not row["write_particles"]
    )
    quality_pass = bool(
        row["geometry_quality_report_exists"]
        and row["geometry_quality_report_pass"]
        and row["geometry_quality_strict"] is False
        and row["quality_report_geometry_type"] == "squid_proxy"
        and row["quality_report_empty"] is False
        and int(row["quality_report_occupied_count"]) > 0
        and int(row["quality_report_surface_voxel_count"]) > 0
        and row["quality_report_touches_domain_boundary"] is False
    )
    sampling_pass = bool(
        row["sampling_stats_exist"]
        and row["sampling_geometry_type"] == "squid_proxy"
        and int(row["sampling_particle_count"]) == int(row["n_particles"])
        and int(row["mantle_particle_count"]) > 0
        and int(row["head_particle_count"]) > 0
        and int(row["arms_particle_count"]) > 0
    )
    geometry_report_ok = bool(
        row["geometry_motion_config_path_exists"]
        and row["geometry_motion_application_config_path_exists"]
        and row["geometry_motion_interface_report_exists"]
        and row["geometry_motion_interface_report_pass"]
        and row["no_op_pass"]
        and row["config_validation_pass"]
        and row["diagnostic_only"]
        and int(row["mutation_flag_enabled_count"]) == 0
        and all(row[field] is False for field in MUTATION_FLAG_FIELDS)
    )
    wall_velocity_pass = bool(
        row["wall_velocity_application_config_path_exists"]
        and row["wall_velocity_application_report_exists"]
        and row["wall_velocity_application_report_pass"]
        and row["target_lbm_field"] == "solid_vel"
        and row["application_policy"] == "additive_capped"
        and row["apply_to_lbm_solid_vel_wall_velocity"]
        and not row["apply_to_lbm_populations"]
        and not row["apply_to_mpm"]
        and not row["apply_to_projector"]
        and not row["modify_bounceback_formula"]
        and not row["jet_model_enabled"]
        and not row["actuation_claim_enabled"]
        and int(row["applied_cell_count"]) >= int(policy["min_applied_cell_count"])
        and float(row["max_applied_velocity_norm"]) <= float(row["wall_velocity_cap_lbm"]) + 1.0e-12
        and row["finite_pass"]
        and row["cap_pass"]
        and int(row["lbm_population_update_count"]) == 0
    )
    boundary_pass = bool(
        row["boundary_motion_config_path_exists"]
        and row["boundary_motion_interface_report_exists"]
        and row["boundary_motion_interface_report_pass"]
        and row["boundary_motion_diagnostic_only"]
    )
    return bool(
        row["post_gate_simulation_allowed"]
        and row["allowed_next_step"] == "Step90"
        and row["previous_step"] == "Step89"
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
        and row["geometry_config_path"] == policy["required_geometry_config_path"]
        and row["geometry_config_path_exists"]
        and row["diagnostics_csv_exists"]
        and row["diagnostics_npz_exists"]
        and row["driver_config_exists"]
        and row["driver_timing_exists"]
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
        and quality_pass
        and sampling_pass
        and geometry_report_ok
        and wall_velocity_pass
        and boundary_pass
        and finite_values(row, excluded=STRING_FIELDS)
    )


def step90_first_user_simulation_dry_run_summary(
    rows: list[dict], matrix_policy: dict, acceptance_policy: dict
) -> dict:
    required_names = set(acceptance_policy["required_row_names"])
    optional_names = set(acceptance_policy.get("optional_row_names", []))
    row_names = {row["row_name"] for row in rows}
    required_rows = [row for row in rows if row["row_name"] in required_names]
    slowest = max(rows, key=lambda row: float(row["elapsed_seconds"])) if rows else {}
    summary = {
        "activation_feature_count": sum(int(row["activation_feature_count"]) for row in rows),
        "allowed_next_step": matrix_policy["allowed_next_step"],
        "allowed_next_step_scope": matrix_policy["allowed_next_step_scope"],
        "boundary_motion_interface_report_pass_count": sum(
            1 for row in rows if row["boundary_motion_interface_report_pass"]
        ),
        "canonical_driver_module": matrix_policy["canonical_driver_module"],
        "combined_runtime_geometry_wall_velocity_enabled_count": sum(
            1 for row in rows if row["combined_runtime_geometry_wall_velocity_enabled"]
        ),
        "driver_run_called_count": sum(1 for row in rows if row["driver_run_called"]),
        "driver_run_required": bool(matrix_policy["driver_run_required"]),
        "gate_source_step": matrix_policy["gate_source_step"],
        "geometry_motion_interface_report_pass_count": sum(
            1 for row in rows if row["geometry_motion_interface_report_pass"]
        ),
        "geometry_quality_report_pass_count": sum(1 for row in rows if row["geometry_quality_report_pass"]),
        "grid_48_enabled_count": sum(1 for row in rows if row["grid_48_enabled"]),
        "grid_64_enabled_count": sum(1 for row in rows if row["grid_64_enabled"]),
        "has_inf_count": sum(1 for row in rows if row["has_inf"]),
        "has_nan_count": sum(1 for row in rows if row["has_nan"]),
        "legacy_driver_module_used_count": sum(1 for row in rows if row["legacy_driver_module_used_as_implementation"]),
        "link_area_enabled_count": sum(1 for row in rows if row["link_area_enabled"]),
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
        "physics_feature_expansion": matrix_policy["physics_feature_expansion"],
        "post_gate_simulation_allowed": bool(matrix_policy["post_gate_simulation_allowed"]),
        "previous_step": matrix_policy["previous_step"],
        "procedural_geometry_enabled_count": sum(1 for row in rows if row["procedural_geometry_enabled"]),
        "real_geometry_candidate_enabled_count": sum(1 for row in rows if row["real_geometry_candidate_enabled"]),
        "real_geometry_enabled_count": sum(1 for row in rows if row["real_geometry_enabled"]),
        "required_row_count": len(required_names),
        "required_rows_present": sorted(required_names & row_names),
        "required_stable_count": sum(1 for row in required_rows if row["stable"]),
        "row_count": len(rows),
        "runtime_code_changed": bool(matrix_policy["runtime_code_changed"]),
        "runtime_geometry_enabled_count": sum(1 for row in rows if row["runtime_geometry_enabled"]),
        "runtime_hard_fail_count": sum(1 for row in rows if row["runtime_hard_fail"]),
        "runtime_warning_count": sum(1 for row in rows if row["runtime_warning"]),
        "slowest_elapsed_seconds": float(slowest.get("elapsed_seconds", 0.0)),
        "slowest_row_name": slowest.get("row_name", ""),
        "solver_behavior_changed": bool(matrix_policy["solver_behavior_changed"]),
        "squid_proxy_enabled_count": sum(1 for row in rows if row["squid_proxy_enabled"]),
        "stable_count": sum(1 for row in rows if row["stable"]),
        "step90_first_user_simulation_dry_run_matrix_pass": False,
        "total_elapsed_seconds": sum(float(row["elapsed_seconds"]) for row in rows),
        "wall_velocity_application_report_pass_count": sum(
            1 for row in rows if row["wall_velocity_application_report_pass"]
        ),
        "wall_velocity_enabled_count": sum(1 for row in rows if row["wall_velocity_enabled"]),
        "write_particles_count": sum(1 for row in rows if row["write_particles"]),
        "write_vtk_count": sum(1 for row in rows if row["write_vtk"]),
    }
    summary["step90_first_user_simulation_dry_run_matrix_pass"] = bool(
        summary["post_gate_simulation_allowed"] is True
        and summary["allowed_next_step"] == "Step90"
        and summary["previous_step"] == "Step89"
        and summary["missing_required_rows"] == []
        and summary["required_stable_count"] == summary["required_row_count"]
        and summary["stable_count"] == summary["row_count"]
        and summary["driver_run_called_count"] == summary["row_count"]
        and summary["legacy_driver_module_used_count"] == 0
        and summary["has_nan_count"] == 0
        and summary["has_inf_count"] == 0
        and summary["optional_row_count"] == 0
        and summary["activation_feature_count"] == 3
        and summary["procedural_geometry_enabled_count"] == 1
        and summary["squid_proxy_enabled_count"] == 1
        and summary["runtime_geometry_enabled_count"] == 1
        and summary["wall_velocity_enabled_count"] == 1
        and summary["combined_runtime_geometry_wall_velocity_enabled_count"] == 1
        and summary["geometry_quality_report_pass_count"] == 1
        and summary["geometry_motion_interface_report_pass_count"] == 1
        and summary["wall_velocity_application_report_pass_count"] == 1
        and summary["boundary_motion_interface_report_pass_count"] == 1
        and summary["real_geometry_candidate_enabled_count"] == 0
        and summary["real_geometry_enabled_count"] == 0
        and summary["link_area_enabled_count"] == 0
        and summary["grid_48_enabled_count"] == 0
        and summary["grid_64_enabled_count"] == 0
        and summary["write_vtk_count"] == 0
        and summary["write_particles_count"] == 0
        and summary["min_completed_lbm_steps"] == 5
        and summary["min_diagnostics_row_count"] >= 6
        and summary["runtime_hard_fail_count"] == 0
        and not summary["runtime_code_changed"]
        and not summary["solver_behavior_changed"]
        and summary["physics_feature_expansion"]
        == "first_user_dry_run_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel"
    )
    return summary


def row_name_from_config(config_path: str) -> str:
    return Path(config_path).stem.removeprefix("step90_")
