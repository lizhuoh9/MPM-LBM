from __future__ import annotations

import math
import shutil
import time
from pathlib import Path

import numpy as np

from src.mpm_lbm.evidence.step84_runtime_geometry_wall_velocity_combined_smoke_runner import (
    MUTATION_FLAG_FIELDS,
    boundary_report_pass,
    combined_report_repo_roots,
    diagnostics_have_nan_or_inf,
    geometry_report_pass,
    max_float,
    max_int,
    min_float,
    report_summary,
)
from src.mpm_lbm.evidence.step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_runner import (
    path_exists_from_repo_root,
    reset_generated_run_dir,
)
from src.mpm_lbm.evidence.step94_taichi_ggui_visualization_smoke_runner import (
    count_files_by_suffix,
    count_particle_npy,
    domain_box_lines,
    vector_field,
    wall_velocity_proxy_lines,
)
from src.mpm_lbm.evidence.step103_common import STEP103_ROW_NAME, read_json, rel_path, resolve_under_root, write_json


STRING_FIELDS = {
    "allowed_claim",
    "canonical_driver_module",
    "campaign_id",
    "comparison_status",
    "coupling_mode",
    "geo_path_name",
    "geometry_config_path",
    "geometry_motion_application_mode",
    "geometry_motion_mode",
    "geometry_type",
    "ggui_screenshot_path",
    "ggui_visualization_source",
    "notes",
    "official_case_dimensionality",
    "official_monitor_quantity",
    "official_structural_model",
    "reaction_transfer_mode",
    "row_name",
    "sampling_geometry_type",
    "target_lbm_field",
    "target_u_lbm",
    "wall_velocity_application_mode",
}


def build_step103_fluent_inspired_duct_flap_proxy_smoke_matrix(
    root: Path,
    run_config_path: str = "configs/step103_fluent_inspired_duct_flap_proxy_48_5step_ggui_comparison_smoke.json",
    acceptance_policy_path: str = "configs/step103_acceptance_policy.json",
    ggui_config_path: str = "configs/step103_taichi_ggui_visualization_config.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    acceptance_policy = read_json(root / acceptance_policy_path)
    row = run_step103_fluent_inspired_duct_flap_proxy_case(
        root,
        run_config_path,
        acceptance_policy,
        ggui_config_path,
    )
    rows = [row]
    summary = step103_smoke_summary(rows, acceptance_policy)
    return rows, summary


def run_step103_fluent_inspired_duct_flap_proxy_case(
    root: Path,
    config_path: str,
    acceptance_policy: dict,
    ggui_config_path: str,
) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D
    from src.mpm_lbm.sim.geometry.config import GeometryConfig
    from src.mpm_lbm.sim.geometry.sampler import GeometrySampler3D

    row_name = row_name_from_config(config_path)
    config = FSIDriverConfig.from_json(root / config_path)
    enforce_step103_config(root, config, row_name, acceptance_policy)
    geometry_config = GeometryConfig.from_json(str(root / config.geometry_config_path))
    sampling_stats = GeometrySampler3D(geometry_config).sample_particles()["sampling_stats"]

    run_root = root / "outputs" / "step103_driver_runs"
    out_dir = run_root / row_name
    reset_generated_run_dir(run_root, out_dir)

    ggui_output_dir = root / "outputs" / "step103_ggui_visualization"
    reset_step103_output_dir(ggui_output_dir, root / "outputs")

    driver = FSIDriver3D(config, str(out_dir))
    started = time.perf_counter()
    with combined_report_repo_roots(root):
        diagnostics = driver.run()
    elapsed_seconds = time.perf_counter() - started
    write_json(out_dir / "driver_timing.json", driver.performance_row())
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step103 row: {row_name}")

    ggui_report = render_step103_duct_flap_proxy_ggui_visual_smoke(
        driver_run_dir=out_dir,
        ggui_config_path=root / ggui_config_path,
        output_dir=ggui_output_dir,
        root=root,
    )

    final = diagnostics[-1]
    has_nan, has_inf = diagnostics_have_nan_or_inf(diagnostics)
    feature_flags = step103_feature_flags(config)
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
        "campaign_id": "step103_fluent_inspired_duct_flap_proxy_solver_comparison_smoke",
        "previous_step": "Step102",
        "allowed_claim": "Fluent-inspired duct-flap proxy comparison smoke ran and produced a solver gap report.",
        "driver_run_called": True,
        "canonical_driver_module": driver.__class__.__module__,
        "legacy_driver_module_used_as_implementation": driver.__class__.__module__
        != "src.mpm_lbm.sim.drivers.fsi_driver",
        "initialized": bool(driver.initialized),
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
        "official_case_dimensionality": "2D",
        "our_solver_dimensionality": "3D",
        "official_mesh_imported": False,
        "official_fluent_files_used_as_runtime_input": False,
        "direct_quantitative_equivalence_allowed": False,
        "validation_claim_allowed": False,
        "official_structural_model": "linear_elasticity_intrinsic_fsi",
        "our_structural_model_equivalent": False,
        "official_dynamic_mesh": True,
        "our_geometry_mutation_enabled": False,
        "official_monitor_quantity": "total_displacement",
        "our_equivalent_flap_tip_displacement_available": False,
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
        "fluent_inspired_geometry_ratios_recorded": bool(
            quality_report.get("fluent_inspired_geometry_ratios_recorded", False)
            and sampling_stats.get("fluent_inspired_geometry_ratios_recorded", False)
        ),
        "sampling_stats_exist": bool(sampling_stats),
        "sampling_geometry_type": sampling_stats.get("geometry_type", ""),
        "sampling_particle_count": int(sampling_stats.get("particle_count", 0)),
        "flap_particle_count": int(sampling_stats.get("flap_particle_count", 0)),
        "fixed_base_particle_count": int(sampling_stats.get("fixed_base_particle_count", 0)),
        "free_tip_proxy_particle_count": int(sampling_stats.get("free_tip_proxy_particle_count", 0)),
        "duct_context_particle_count": int(sampling_stats.get("duct_context_particle_count", 0)),
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
        "ggui_visualization_enabled": bool(ggui_report["ggui_visualization_enabled"]),
        "ggui_renderer_called": bool(ggui_report["ggui_renderer_called"]),
        "ggui_window_created": bool(ggui_report["ggui_window_created"]),
        "ggui_scene_created": bool(ggui_report["ggui_scene_created"]),
        "ggui_camera_configured": bool(ggui_report["ggui_camera_configured"]),
        "ggui_rendered_frame_count": int(ggui_report["ggui_rendered_frame_count"]),
        "ggui_screenshot_enabled": bool(ggui_report["ggui_screenshot_enabled"]),
        "ggui_screenshot_exists": bool(ggui_report["ggui_screenshot_exists"]),
        "ggui_screenshot_file_count": int(ggui_report["ggui_screenshot_file_count"]),
        "ggui_screenshot_size_bytes": int(ggui_report["ggui_screenshot_size_bytes"]),
        "ggui_screenshot_path": ggui_report["ggui_screenshot_path"],
        "ggui_video_enabled": bool(ggui_report["ggui_video_enabled"]),
        "ggui_video_file_count": int(ggui_report["ggui_video_file_count"]),
        "ggui_render_report_exists": (ggui_output_dir / "step103_ggui_visualization_report.json").is_file(),
        "ggui_render_report_pass": bool(ggui_report["ggui_render_report_pass"]),
        "ggui_visualization_source": ggui_report["visualization_source"],
        "ggui_visual_point_count": int(ggui_report["visual_point_count"]),
        "ggui_domain_box_line_vertex_count": int(ggui_report["domain_box_line_vertex_count"]),
        "ggui_wall_velocity_proxy_line_vertex_count": int(ggui_report["wall_velocity_proxy_line_vertex_count"]),
        "has_nan": bool(has_nan),
        "has_inf": bool(has_inf),
        "generated_file_count": len([path for path in out_dir.iterdir() if path.is_file()]),
        "geo_path_name": Path(driver.geo_path).name,
        "diagnostics_csv_exists": (out_dir / "diagnostics_timeseries.csv").is_file(),
        "diagnostics_npz_exists": (out_dir / "diagnostics_timeseries.npz").is_file(),
        "driver_config_exists": (out_dir / "driver_config.json").is_file(),
        "driver_timing_exists": (out_dir / "driver_timing.json").is_file(),
        "vtr_output_count": count_files_by_suffix((out_dir, ggui_output_dir), ".vtr"),
        "particle_npy_output_count": count_particle_npy((out_dir, ggui_output_dir)),
        "elapsed_seconds": elapsed_seconds,
        "runtime_warning": elapsed_seconds > float(acceptance_policy["runtime_warning_seconds"]),
        "runtime_hard_fail": elapsed_seconds > float(acceptance_policy["runtime_hard_fail_seconds"]),
        "stable": False,
        "notes": (
            "Step103 is a real solver smoke with a procedural Fluent-inspired duct-flap proxy and "
            "gap-only comparison reporting; it is not Fluent validation."
        ),
    }
    row["activation_feature_count"] = step103_activation_feature_count(row)
    row["stable"] = step103_smoke_row_pass(row, acceptance_policy)
    if not row["stable"]:
        raise RuntimeError(f"Step103 smoke row failed acceptance: {row}")
    return row


def render_step103_duct_flap_proxy_ggui_visual_smoke(
    driver_run_dir,
    ggui_config_path,
    output_dir,
    root: Path | None = None,
) -> dict:
    import taichi as ti

    root = Path(root or Path.cwd())
    driver_run_dir = resolve_under_root(root, driver_run_dir)
    output_dir = resolve_under_root(root, output_dir)
    ggui_config_path = resolve_under_root(root, ggui_config_path)
    ggui_config = read_json(ggui_config_path)
    driver_config = read_json(driver_run_dir / "driver_config.json")

    output_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = resolve_under_root(root, ggui_config["screenshot_path"])
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "domain_box_line_vertex_count": 0,
        "error": "",
        "ggui_camera_configured": False,
        "ggui_render_report_exists": True,
        "ggui_render_report_pass": False,
        "ggui_rendered_frame_count": 0,
        "ggui_renderer_called": True,
        "ggui_scene_created": False,
        "ggui_screenshot_enabled": bool(ggui_config["screenshot_enabled"]),
        "ggui_screenshot_exists": False,
        "ggui_screenshot_file_count": 0,
        "ggui_screenshot_size_bytes": 0,
        "ggui_screenshot_path": rel_path(root, screenshot_path),
        "ggui_video_enabled": bool(ggui_config["video_enabled"]),
        "ggui_video_file_count": 0,
        "ggui_visualization_enabled": bool(ggui_config["ggui_visualization_enabled"]),
        "ggui_window_created": False,
        "render_frames_requested": int(ggui_config["render_frames"]),
        "show_window": bool(ggui_config.get("show_window", False)),
        "taichi_version": ".".join(str(item) for item in ti.__version__),
        "visual_point_count": 0,
        "visualization_note": "procedural duct-flap proxy visualization only; not Fluent validation",
        "visualization_source": "procedural_duct_flap_proxy_points",
        "wall_velocity_proxy_line_vertex_count": 0,
        "window_resolution": list(ggui_config["window_resolution"]),
        "window_title": ggui_config["window_title"],
    }
    try:
        points, component_points = duct_flap_visual_points(root, driver_config, int(ggui_config["max_visual_points"]))
        domain_lines = domain_box_lines()
        wall_velocity_lines = wall_velocity_proxy_lines(points)
        window = ti.ui.Window(
            ggui_config["window_title"],
            tuple(int(v) for v in ggui_config["window_resolution"]),
            show_window=bool(ggui_config.get("show_window", False)),
        )
        report["ggui_window_created"] = True
        canvas = window.get_canvas()
        scene = window.get_scene()
        report["ggui_scene_created"] = True
        camera = ti.ui.Camera()
        camera.position(*[float(v) for v in ggui_config["camera_position"]])
        camera.lookat(*[float(v) for v in ggui_config["camera_lookat"]])
        camera.up(*[float(v) for v in ggui_config["camera_up"]])
        scene.set_camera(camera)
        report["ggui_camera_configured"] = True
        scene.ambient_light((0.65, 0.65, 0.65))
        scene.point_light(pos=(1.2, 1.2, 1.2), color=(1.0, 1.0, 1.0))

        retained_fields = []
        if bool(ggui_config["visualize_domain_box"]):
            domain_field = vector_field(domain_lines, ti)
            retained_fields.append(domain_field)
            scene.lines(domain_field, color=(0.28, 0.62, 0.95), width=1.8)
            report["domain_box_line_vertex_count"] = int(len(domain_lines))

        if bool(ggui_config["visualize_flap_proxy_points"]):
            retained_fields.extend(draw_step103_component_particles(scene, ti, component_points))
            report["visual_point_count"] = int(len(points))

        if bool(ggui_config["visualize_wall_velocity_proxy"]):
            wall_field = vector_field(wall_velocity_lines, ti)
            retained_fields.append(wall_field)
            scene.lines(wall_field, color=(0.98, 0.72, 0.22), width=1.4)
            report["wall_velocity_proxy_line_vertex_count"] = int(len(wall_velocity_lines))

        canvas.scene(scene)
        if report["ggui_screenshot_enabled"]:
            window.save_image(str(screenshot_path))
        report["ggui_rendered_frame_count"] = 1
    except Exception as exc:  # pragma: no cover - backend-specific.
        report["error"] = str(exc)

    report["ggui_screenshot_exists"] = screenshot_path.is_file()
    report["ggui_screenshot_file_count"] = int(screenshot_path.is_file())
    report["ggui_screenshot_size_bytes"] = int(screenshot_path.stat().st_size) if screenshot_path.is_file() else 0
    report["ggui_video_file_count"] = 0
    report["ggui_render_report_pass"] = bool(
        report["ggui_visualization_enabled"]
        and report["ggui_renderer_called"]
        and report["ggui_window_created"]
        and report["ggui_scene_created"]
        and report["ggui_camera_configured"]
        and report["ggui_rendered_frame_count"] >= int(ggui_config["render_frames"])
        and report["ggui_screenshot_enabled"]
        and report["ggui_screenshot_exists"]
        and report["ggui_screenshot_size_bytes"] > 0
        and not report["ggui_video_enabled"]
        and report["visual_point_count"] > 0
        and not report["error"]
    )
    metadata = {
        "driver_run_dir": rel_path(root, driver_run_dir),
        "ggui_config_path": rel_path(root, ggui_config_path),
        "render_report_path": "outputs/step103_ggui_visualization/step103_ggui_visualization_report.json",
        "screenshot_path": rel_path(root, screenshot_path),
        "visualization_source": report["visualization_source"],
    }
    write_json(output_dir / "step103_ggui_visualization_metadata.json", metadata)
    write_json(output_dir / "step103_ggui_visualization_report.json", report)
    return report


def duct_flap_visual_points(root: Path, driver_config: dict, max_visual_points: int):
    from src.mpm_lbm.sim.geometry.config import GeometryConfig
    from src.mpm_lbm.sim.geometry.sampler import GeometrySampler3D

    geometry_config = GeometryConfig.from_json(str(root / driver_config["geometry_config_path"]))
    sampler = GeometrySampler3D(geometry_config)
    points = sampler.sample_particles()["x"].astype(np.float32)
    if len(points) > max_visual_points:
        indices = np.linspace(0, len(points) - 1, max_visual_points, dtype=np.int64)
        points = points[indices]
    masks = sampler.component_masks(points)
    component_points = {
        name: np.ascontiguousarray(points[mask].astype(np.float32)) for name, mask in masks.items() if np.any(mask)
    }
    return np.ascontiguousarray(points), component_points


def draw_step103_component_particles(scene, ti, component_points: dict[str, np.ndarray]) -> list:
    colors = {
        "duct_context": (0.30, 0.55, 0.85),
        "fixed_base": (0.80, 0.22, 0.22),
        "flap": (0.80, 0.38, 0.18),
        "free_tip_proxy": (0.96, 0.62, 0.22),
    }
    fields = []
    for name, points in sorted(component_points.items()):
        if len(points) == 0:
            continue
        field = vector_field(points, ti)
        fields.append(field)
        scene.particles(field, color=colors.get(name, (0.80, 0.38, 0.18)), radius=0.006)
    return fields


def enforce_step103_config(root: Path, config, row_name: str, policy: dict) -> None:
    if row_name not in set(policy["required_row_names"]):
        raise RuntimeError(f"unexpected Step103 row: {row_name}")
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
        raise RuntimeError(f"Step103 config mismatch: {actual} != {expected}")
    if config.geometry_type != policy["required_geometry_type"]:
        raise RuntimeError("Step103 must use duct_flap_proxy geometry")
    if config.geometry_config_path != policy["required_geometry_config_path"]:
        raise RuntimeError("Step103 must use the required duct-flap proxy geometry config")
    if list(config.target_u_lbm) != list(policy["required_target_u_lbm"]):
        raise RuntimeError("Step103 target_u_lbm mismatch")
    if config.coupling_mode != "moving_boundary" or config.reaction_transfer_mode != "engineering":
        raise RuntimeError("Step103 must use moving_boundary with engineering reaction transfer")
    if config.write_vtk or config.write_particles:
        raise RuntimeError("Step103 must not write VTK or particle arrays")
    if not config.quality_check_enabled or config.quality_check_strict:
        raise RuntimeError("Step103 must enable non-strict geometry quality reporting")
    if config.geometry_motion_application_mode != "diagnostic_only":
        raise RuntimeError("Step103 geometry motion must remain diagnostic_only")
    if config.wall_velocity_application_mode != "solid_vel_experimental":
        raise RuntimeError("Step103 must use solid_vel_experimental wall velocity reporting")
    for label, relative_path in {
        "boundary_motion_config_path": config.boundary_motion_config_path,
        "geometry_config_path": config.geometry_config_path,
        "geometry_motion_config_path": config.geometry_motion_config_path,
        "geometry_motion_application_config_path": config.geometry_motion_application_config_path,
        "wall_velocity_application_config_path": config.wall_velocity_application_config_path,
    }.items():
        if not path_exists_from_repo_root(root, relative_path):
            raise RuntimeError(f"Step103 {label} is not resolvable: {relative_path}")


def step103_feature_flags(config) -> dict:
    runtime_geometry_enabled = bool(config.geometry_motion_mode != "static" or config.geometry_motion_application_mode != "disabled")
    wall_velocity_enabled = bool(config.wall_velocity_application_mode != "disabled")
    duct_flap_proxy_enabled = bool(config.geometry_type == "duct_flap_proxy")
    real_geometry_candidate_enabled = bool(config.geometry_type in {"mesh", "voxel"})
    return {
        "runtime_geometry_enabled": runtime_geometry_enabled,
        "wall_velocity_enabled": wall_velocity_enabled,
        "combined_runtime_geometry_wall_velocity_enabled": bool(runtime_geometry_enabled and wall_velocity_enabled),
        "procedural_geometry_enabled": duct_flap_proxy_enabled or bool(config.geometry_type in {"box", "ellipsoid", "squid_proxy"}),
        "duct_flap_proxy_enabled": duct_flap_proxy_enabled,
        "squid_proxy_enabled": bool(config.geometry_type == "squid_proxy"),
        "real_geometry_candidate_enabled": real_geometry_candidate_enabled,
        "real_geometry_enabled": real_geometry_candidate_enabled,
        "link_area_enabled": bool(config.reaction_transfer_mode == "link_area_experimental"),
        "grid_48_enabled": bool(int(config.n_grid) == 48),
        "grid_64_enabled": bool(int(config.n_grid) == 64),
        "write_vtk": bool(config.write_vtk),
        "write_particles": bool(config.write_particles),
    }


def step103_activation_feature_count(row: dict) -> int:
    keys = (
        "duct_flap_proxy_enabled",
        "runtime_geometry_enabled",
        "wall_velocity_enabled",
        "grid_48_enabled",
        "ggui_visualization_enabled",
    )
    return sum(1 for key in keys if bool(row[key]))


def step103_smoke_row_pass(row: dict, policy: dict) -> bool:
    expected_geo = f"geo_all_fluid_{int(row['n_grid'])}.dat"
    mode_pass = bool(
        int(row["bb_link_count_max"]) > 0
        and float(row["bb_max_correction_max"]) >= 0.0
        and int(row["active_reaction_particle_count_final"]) >= 0
        and math.isfinite(float(row["max_grid_reaction_norm_max"]))
    )
    feature_pass = bool(
        row["procedural_geometry_enabled"]
        and row["duct_flap_proxy_enabled"]
        and row["runtime_geometry_enabled"]
        and row["wall_velocity_enabled"]
        and row["combined_runtime_geometry_wall_velocity_enabled"]
        and row["ggui_visualization_enabled"]
        and row["grid_48_enabled"]
        and not row["squid_proxy_enabled"]
        and not row["real_geometry_candidate_enabled"]
        and not row["real_geometry_enabled"]
        and not row["link_area_enabled"]
        and not row["grid_64_enabled"]
        and not row["write_vtk"]
        and not row["write_particles"]
        and int(row["vtr_output_count"]) == 0
        and int(row["particle_npy_output_count"]) == 0
    )
    quality_pass = bool(
        row["geometry_quality_report_exists"]
        and row["geometry_quality_report_pass"]
        and row["geometry_quality_strict"] is False
        and row["quality_report_geometry_type"] == "duct_flap_proxy"
        and row["quality_report_empty"] is False
        and int(row["quality_report_occupied_count"]) > 0
        and int(row["quality_report_surface_voxel_count"]) > 0
        and row["fluent_inspired_geometry_ratios_recorded"]
    )
    sampling_pass = bool(
        row["sampling_stats_exist"]
        and row["sampling_geometry_type"] == "duct_flap_proxy"
        and int(row["sampling_particle_count"]) == int(row["n_particles"])
        and int(row["flap_particle_count"]) == int(row["n_particles"])
        and int(row["fixed_base_particle_count"]) > 0
        and int(row["free_tip_proxy_particle_count"]) > 0
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
    ggui_pass = bool(
        row["ggui_renderer_called"]
        and row["ggui_window_created"]
        and row["ggui_scene_created"]
        and row["ggui_camera_configured"]
        and int(row["ggui_rendered_frame_count"]) >= int(policy["expected_ggui_render_frames"])
        and row["ggui_screenshot_enabled"]
        and row["ggui_screenshot_exists"]
        and int(row["ggui_screenshot_file_count"]) == int(policy["expected_ggui_screenshot_file_count"])
        and int(row["ggui_screenshot_size_bytes"]) >= int(policy["min_screenshot_size_bytes"])
        and not row["ggui_video_enabled"]
        and int(row["ggui_video_file_count"]) == int(policy["expected_ggui_video_file_count"])
        and row["ggui_render_report_exists"]
        and row["ggui_render_report_pass"]
        and int(row["ggui_visual_point_count"]) > 0
        and int(row["ggui_domain_box_line_vertex_count"]) > 0
    )
    return bool(
        row["driver_run_called"]
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
        and not row["official_mesh_imported"]
        and not row["official_fluent_files_used_as_runtime_input"]
        and not row["direct_quantitative_equivalence_allowed"]
        and not row["validation_claim_allowed"]
        and mode_pass
        and feature_pass
        and quality_pass
        and sampling_pass
        and geometry_report_ok
        and wall_velocity_pass
        and boundary_pass
        and ggui_pass
        and numeric_values_finite(row)
    )


def step103_smoke_summary(rows: list[dict], policy: dict) -> dict:
    required_names = set(policy["required_row_names"])
    row_names = {row["row_name"] for row in rows}
    required_rows = [row for row in rows if row["row_name"] in required_names]
    summary = {
        "activation_feature_count": sum(int(row["activation_feature_count"]) for row in rows),
        "combined_runtime_geometry_wall_velocity_enabled_count": sum(
            1 for row in rows if row["combined_runtime_geometry_wall_velocity_enabled"]
        ),
        "driver_run_called_count": sum(1 for row in rows if row["driver_run_called"]),
        "duct_flap_proxy_enabled_count": sum(1 for row in rows if row["duct_flap_proxy_enabled"]),
        "geometry_quality_report_pass_count": sum(1 for row in rows if row["geometry_quality_report_pass"]),
        "geometry_motion_interface_report_pass_count": sum(1 for row in rows if row["geometry_motion_interface_report_pass"]),
        "ggui_render_report_pass_count": sum(1 for row in rows if row["ggui_render_report_pass"]),
        "ggui_renderer_called_count": sum(1 for row in rows if row["ggui_renderer_called"]),
        "ggui_screenshot_count": sum(int(row["ggui_screenshot_file_count"]) for row in rows),
        "ggui_video_file_count": sum(int(row["ggui_video_file_count"]) for row in rows),
        "ggui_visualization_enabled_count": sum(1 for row in rows if row["ggui_visualization_enabled"]),
        "grid_48_enabled_count": sum(1 for row in rows if row["grid_48_enabled"]),
        "grid_64_enabled_count": sum(1 for row in rows if row["grid_64_enabled"]),
        "has_inf_count": sum(1 for row in rows if row["has_inf"]),
        "has_nan_count": sum(1 for row in rows if row["has_nan"]),
        "legacy_driver_module_used_count": sum(1 for row in rows if row["legacy_driver_module_used_as_implementation"]),
        "link_area_enabled_count": sum(1 for row in rows if row["link_area_enabled"]),
        "min_completed_lbm_steps": min(int(row["completed_lbm_steps"]) for row in rows),
        "min_diagnostics_row_count": min(int(row["diagnostics_row_count"]) for row in rows),
        "missing_required_rows": sorted(required_names - row_names),
        "optional_row_count": sum(1 for row in rows if row["row_name"] not in required_names),
        "particle_npy_output_count": sum(int(row["particle_npy_output_count"]) for row in rows),
        "real_geometry_candidate_enabled_count": sum(1 for row in rows if row["real_geometry_candidate_enabled"]),
        "real_geometry_enabled_count": sum(1 for row in rows if row["real_geometry_enabled"]),
        "required_row_count": len(required_names),
        "required_rows_present": sorted(required_names & row_names),
        "required_stable_count": sum(1 for row in required_rows if row["stable"]),
        "row_count": len(rows),
        "runtime_geometry_enabled_count": sum(1 for row in rows if row["runtime_geometry_enabled"]),
        "runtime_code_changed": True,
        "runtime_hard_fail_count": sum(1 for row in rows if row["runtime_hard_fail"]),
        "solver_behavior_changed": False,
        "solver_formula_changed": False,
        "stable_count": sum(1 for row in rows if row["stable"]),
        "step103_fluent_inspired_duct_flap_proxy_smoke_matrix_pass": False,
        "total_elapsed_seconds": sum(float(row["elapsed_seconds"]) for row in rows),
        "vtr_output_count": sum(int(row["vtr_output_count"]) for row in rows),
        "wall_velocity_application_report_pass_count": sum(1 for row in rows if row["wall_velocity_application_report_pass"]),
        "wall_velocity_enabled_count": sum(1 for row in rows if row["wall_velocity_enabled"]),
        "write_particles_count": sum(1 for row in rows if row["write_particles"]),
        "write_vtk_count": sum(1 for row in rows if row["write_vtk"]),
    }
    summary["step103_fluent_inspired_duct_flap_proxy_smoke_matrix_pass"] = bool(
        summary["missing_required_rows"] == []
        and summary["required_stable_count"] == summary["required_row_count"]
        and summary["stable_count"] == summary["row_count"]
        and summary["driver_run_called_count"] == 1
        and summary["legacy_driver_module_used_count"] == 0
        and summary["duct_flap_proxy_enabled_count"] == 1
        and summary["ggui_screenshot_count"] == 1
        and summary["ggui_video_file_count"] == 0
        and summary["vtr_output_count"] == 0
        and summary["particle_npy_output_count"] == 0
        and summary["has_nan_count"] == 0
        and summary["has_inf_count"] == 0
        and summary["grid_48_enabled_count"] == 1
        and summary["grid_64_enabled_count"] == 0
        and summary["real_geometry_candidate_enabled_count"] == 0
        and summary["real_geometry_enabled_count"] == 0
        and summary["link_area_enabled_count"] == 0
        and summary["write_vtk_count"] == 0
        and summary["write_particles_count"] == 0
        and summary["min_completed_lbm_steps"] == 5
        and summary["min_diagnostics_row_count"] >= 6
        and summary["runtime_hard_fail_count"] == 0
        and summary["runtime_code_changed"] is True
        and summary["solver_formula_changed"] is False
    )
    return summary


def reset_step103_output_dir(out_dir: Path, required_parent: Path) -> None:
    resolved_out = out_dir.resolve()
    resolved_parent = required_parent.resolve()
    if resolved_parent not in resolved_out.parents:
        raise RuntimeError(f"refusing to reset unexpected Step103 output directory: {out_dir}")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)


def numeric_values_finite(row: dict) -> bool:
    for key, value in row.items():
        if key in STRING_FIELDS or isinstance(value, bool):
            continue
        if isinstance(value, (int, float)) and not math.isfinite(float(value)):
            return False
    return True


def row_name_from_config(config_path: str) -> str:
    return Path(config_path).stem.removeprefix("step103_")
