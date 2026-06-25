from dataclasses import replace
import json
import os
from pathlib import Path
import time

import numpy as np

from ...diagnostics.fsi_diagnostics import FSIDiagnostics3D
from ..coupling.link_area import LinkAreaMovingBoundaryCoupler3D
from ..coupling.moving_boundary import MovingBoundaryFSICoupler3D
from ..coupling.penalty import PenaltyFSICoupler3D
from ..coupling.projection import MPMToLBMProjector3D
from ..geometry.config import GeometryConfig
from ..geometry.duct_flap_proxy import duct_flap_proxy_static_geometry
from ..geometry.quality import GeometryQualityGate, analyze_geometry_config
from ..geometry.sampler import GeometrySampler3D
from ..io.run_utils import assert_no_nan_inf_array, ensure_output_dir, make_all_fluid_geo, save_csv_rows, save_json_config
from ..lbm.fluid import LBMFluid3D
from ..mpm.solid import MPMSolid3D
from ..units.mapper import GridUnitMapper
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig


DIAGNOSTIC_FIELDS = [
    "step",
    "total_mpm_substeps",
    "coupling_mode",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "fluid_mean_ux",
    "projection_zone_fluid_mean_ux",
    "far_field_fluid_mean_ux",
    "solid_mean_vx_norm",
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
    "elapsed_seconds",
]


class FSIDriver3D:
    def __init__(self, config: FSIDriverConfig, out_dir: str):
        self.config = config
        self.out_dir = out_dir
        self.sim = config.make_unified_sim_config()
        self.mapper = GridUnitMapper.from_sim_config(self.sim)
        self.current_lbm_step = 0
        self.total_lbm_substeps = 0
        self.total_mpm_substeps = 0
        self.diagnostics_rows = []
        self.timing = {
            "init_time": 0.0,
            "projection_time": 0.0,
            "coupling_time": 0.0,
            "lbm_step_time": 0.0,
            "mpm_substep_time": 0.0,
            "diagnostics_time": 0.0,
            "export_time": 0.0,
            "wall_velocity_application_time": 0.0,
            "geometry_motion_interface_time": 0.0,
            "total_time": 0.0,
        }

        self.geo_path = os.path.join(self.out_dir, f"geo_all_fluid_{self.config.n_grid}.dat")
        self.initialized = False
        self.start_time = None

        self.lbm = None
        self.solid = None
        self.projector = None
        self.penalty_coupler = None
        self.mb_coupler = None
        self.link_area_coupler = None
        self.geometry_quality_report = None
        self.boundary_motion_interface_report = None
        self.duct_boundary_condition_report = None
        self.duct_static_geometry_report = None
        self.wall_velocity_application_report = None
        self.wall_velocity_application_reports = []
        self.geometry_motion_interface_report = None
        self.sampling_stats = None
        self.initial_particle_positions = None
        self.free_tip_proxy_mask = None
        self.flap_tip_monitor_rows = []
        self.material_reference_used_for_mpm_config = False

    def initialize(self):
        t0 = time.perf_counter()
        ensure_output_dir(self.out_dir)
        geometry_config = None
        if not (self.config.geometry_type == "box" and self.config.geometry_config_path is None):
            geometry_config = self._make_geometry_config()
        self._write_static_lbm_geometry(geometry_config)
        save_json_config(self.config, os.path.join(self.out_dir, "driver_config.json"))
        self._run_boundary_motion_interface_report()
        self._run_geometry_motion_interface_report()

        lbm_config = self._make_lbm_config()
        self._write_lbm_boundary_condition_report(lbm_config)
        self.lbm = LBMFluid3D(lbm_config)
        self.lbm.init_geo(self.geo_path)
        self.lbm.init_simulation()

        mpm_overrides = {
            "gravity": self.config.gravity,
            "box_min": self.config.box_min,
            "box_max": self.config.box_max,
        }
        mpm_overrides.update(self._mpm_material_overrides(geometry_config))
        self.solid = MPMSolid3D(
            self.sim.make_mpm_config(**mpm_overrides),
            n_particles=self.config.n_particles,
        )
        if self.config.geometry_type == "box" and self.config.geometry_config_path is None:
            self.solid.init_box()
        else:
            self._run_geometry_quality_check(geometry_config)
            cloud = GeometrySampler3D(geometry_config).sample_particles()
            self.sampling_stats = dict(cloud["sampling_stats"])
            self.initial_particle_positions = np.asarray(cloud["x"], dtype=np.float32).copy()
            self.free_tip_proxy_mask = np.asarray(
                cloud.get("free_tip_proxy_mask", np.zeros((self.config.n_particles,), dtype=np.int8)),
                dtype=bool,
            )
            self.solid.init_from_numpy(
                cloud["x"],
                cloud["vol0"],
                cloud["mass"],
                fixed_mask_np=cloud.get("fixed_base_mask"),
            )
        initial_solid_velocity = self.config.initial_solid_velocity_norm
        self.solid.set_uniform_velocity(
            float(initial_solid_velocity[0]),
            float(initial_solid_velocity[1]),
            float(initial_solid_velocity[2]),
        )

        self.projector = MPMToLBMProjector3D(self.sim)
        if self.config.coupling_mode == "penalty":
            self.penalty_coupler = PenaltyFSICoupler3D(
                self.sim,
                beta_lbm=self.config.beta_lbm,
                force_cap_lbm=self.config.penalty_force_cap_lbm,
            )
        if self.config.coupling_mode == "moving_boundary" and self.config.reaction_transfer_mode == "engineering":
            self.mb_coupler = MovingBoundaryFSICoupler3D(
                self.sim,
                reaction_scale=self.config.mb_reaction_scale,
                force_cap_norm=self.config.mb_force_cap_norm,
                phi_min=1.0e-6,
            )
        if self.config.coupling_mode == "moving_boundary" and self.config.reaction_transfer_mode == "link_area_experimental":
            self.link_area_coupler = LinkAreaMovingBoundaryCoupler3D(
                self.sim,
                area_policy=self.config.link_area_policy,
                reaction_scale=self.config.mb_reaction_scale,
                force_cap_norm=self.config.mb_force_cap_norm,
                phi_min=1.0e-6,
                area_scale_min=self.config.link_area_scale_min,
                area_scale_max=self.config.link_area_scale_max,
            )

        self.initialized = True
        self.start_time = time.perf_counter()
        self.timing["init_time"] += self.start_time - t0

    def _write_static_lbm_geometry(self, geometry_config):
        if self.config.lbm_boundary_condition_mode == "duct_velocity_inlet_pressure_outlet":
            if geometry_config is None or geometry_config.geometry_type != "duct_flap_proxy":
                raise ValueError("duct_velocity_inlet_pressure_outlet requires duct_flap_proxy geometry_config")
            self.geo_path = os.path.join(self.out_dir, f"geo_duct_flap_proxy_{self.config.n_grid}.dat")
            solid_geo, report = duct_flap_proxy_static_geometry(self.config.n_grid, geometry_config)
            np.savetxt(self.geo_path, solid_geo.reshape(-1, order="F"), fmt="%d")
            report = dict(report)
            report["geo_path"] = os.path.basename(self.geo_path)
            report["lbm_boundary_condition_mode"] = self.config.lbm_boundary_condition_mode
            self.duct_static_geometry_report = report
            with open(os.path.join(self.out_dir, "duct_static_geometry_report.json"), "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, sort_keys=True)
                f.write("\n")
            return report

        make_all_fluid_geo(self.geo_path, self.config.n_grid)
        return None

    def _make_lbm_config(self):
        if self.config.lbm_boundary_condition_mode == "default_periodic":
            return self.sim.make_lbm_config()
        if self.config.lbm_boundary_condition_mode != "duct_velocity_inlet_pressure_outlet":
            raise ValueError(f"unsupported lbm_boundary_condition_mode: {self.config.lbm_boundary_condition_mode}")

        target = tuple(float(value) for value in self.config.target_u_lbm)
        if self.config.velocity_inlet_side == "min":
            return self.sim.make_lbm_config(
                bc_x_left=2,
                bc_x_right=1,
                vel_bc_x_left=target,
                rho_bc_x_right=1.0,
            )
        return self.sim.make_lbm_config(
            bc_x_left=1,
            bc_x_right=2,
            rho_bc_x_left=1.0,
            vel_bc_x_right=target,
        )

    def _write_lbm_boundary_condition_report(self, lbm_config):
        if self.config.lbm_boundary_condition_mode == "default_periodic":
            return None
        static_report = self.duct_static_geometry_report or {}
        if self.config.velocity_inlet_side == "min":
            velocity_inlet_cell_count = int(static_report.get("inlet_fluid_cell_count", 0))
            pressure_outlet_cell_count = int(static_report.get("pressure_outlet_fluid_cell_count", 0))
        else:
            velocity_inlet_cell_count = int(static_report.get("pressure_outlet_fluid_cell_count", 0))
            pressure_outlet_cell_count = int(static_report.get("inlet_fluid_cell_count", 0))
        report = {
            "bc_x_left": int(lbm_config.bc_x_left),
            "bc_x_right": int(lbm_config.bc_x_right),
            "duct_wall_cell_count": int(static_report.get("duct_wall_cell_count", 0)),
            "lbm_boundary_condition_mode": self.config.lbm_boundary_condition_mode,
            "periodic_boundary_used": False,
            "pressure_outlet_cell_count": pressure_outlet_cell_count,
            "pressure_outlet_side": self.config.pressure_outlet_side,
            "target_u_lbm": list(self.config.target_u_lbm),
            "target_u_lbm_applied_to_inlet": True,
            "target_u_lbm_applied_to_solid_initial_velocity": False,
            "velocity_inlet_axis": self.config.velocity_inlet_axis,
            "velocity_inlet_cell_count": velocity_inlet_cell_count,
            "velocity_inlet_side": self.config.velocity_inlet_side,
            "vel_bc_x_left": list(lbm_config.vel_bc_x_left),
            "vel_bc_x_right": list(lbm_config.vel_bc_x_right),
        }
        self.duct_boundary_condition_report = report
        with open(os.path.join(self.out_dir, "duct_boundary_condition_report.json"), "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True)
            f.write("\n")
        return report

    def _mpm_material_overrides(self, geometry_config):
        if geometry_config is None or geometry_config.geometry_type != "duct_flap_proxy":
            self.material_reference_used_for_mpm_config = False
            return {}
        material = geometry_config.material_reference or {}
        if not bool(material.get("used_for_mpm_config", False)):
            self.material_reference_used_for_mpm_config = False
            return {}
        self.material_reference_used_for_mpm_config = True
        return {
            "p_rho": float(material["density"]),
            "young_modulus": float(material["youngs_modulus"]),
            "poisson_ratio": float(material["poisson_ratio"]),
        }

    def _make_geometry_config(self):
        if self.config.geometry_config_path is None:
            return GeometryConfig(
                geometry_type=self.config.geometry_type,
                n_particles=self.config.n_particles,
                box_min=self.config.box_min,
                box_max=self.config.box_max,
            )

        geometry_config = GeometryConfig.from_json(self.config.geometry_config_path)
        if geometry_config.geometry_type != self.config.geometry_type:
            raise ValueError(
                "geometry_config_path geometry_type does not match FSIDriverConfig.geometry_type: "
                f"{geometry_config.geometry_type} != {self.config.geometry_type}"
            )
        if geometry_config.n_particles != self.config.n_particles:
            raise ValueError(
                "geometry_config_path n_particles does not match FSIDriverConfig.n_particles: "
                f"{geometry_config.n_particles} != {self.config.n_particles}"
            )
        if self.config.quality_check_enabled or self.config.quality_check_strict or self.config.quality_report_path:
            geometry_config = replace(
                geometry_config,
                quality_check_enabled=bool(self.config.quality_check_enabled),
                quality_check_strict=bool(self.config.quality_check_strict),
                quality_report_path=self.config.quality_report_path,
            )
        return geometry_config

    def _run_geometry_quality_check(self, geometry_config):
        if not geometry_config.quality_check_enabled:
            return None

        report = analyze_geometry_config(geometry_config)
        gate = GeometryQualityGate(strict=geometry_config.quality_check_strict)
        gate_result = gate.evaluate(report)
        payload = {
            "report": report,
            "gate": gate_result,
        }
        self.geometry_quality_report = payload

        report_path = geometry_config.quality_report_path
        if report_path is None:
            report_path = os.path.join(self.out_dir, "geometry_quality_report.json")
        elif not os.path.isabs(report_path):
            report_path = os.fspath(_repo_root() / report_path)
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)
            f.write("\n")

        if not gate_result["pass"]:
            raise ValueError("Geometry quality gate failed: " + "; ".join(gate_result["reasons"]))
        return payload

    def _run_boundary_motion_interface_report(self):
        if not self.config.boundary_motion_report_enabled:
            return None

        report_path = os.path.join(self.out_dir, "boundary_motion_interface_report.json")
        if self.config.boundary_motion_mode == "static":
            from ..motion.boundary_motion_interface import write_static_boundary_motion_interface_report

            self.boundary_motion_interface_report = write_static_boundary_motion_interface_report(report_path)
            return self.boundary_motion_interface_report

        if self.config.boundary_motion_mode == "prescribed_kinematic":
            from ..motion.boundary_motion_interface import write_boundary_motion_interface_report

            self.boundary_motion_interface_report = write_boundary_motion_interface_report(
                self.config.boundary_motion_config_path,
                report_path,
                boundary_motion_mode=self.config.boundary_motion_mode,
            )
            return self.boundary_motion_interface_report

        raise ValueError(f"unsupported boundary_motion_mode: {self.config.boundary_motion_mode}")

    def _run_geometry_motion_interface_report(self):
        if self.config.geometry_motion_application_mode == "disabled":
            return None
        if self.config.geometry_motion_application_mode != "diagnostic_only":
            raise ValueError(f"unsupported geometry_motion_application_mode: {self.config.geometry_motion_application_mode}")
        if self.config.geometry_motion_mode != "prescribed_kinematic":
            raise ValueError("diagnostic_only geometry motion requires prescribed_kinematic geometry_motion_mode")

        from ..motion.geometry_motion_interface import write_geometry_motion_interface_report

        t0 = time.perf_counter()
        report_path = None
        if self.config.geometry_motion_report_enabled or self.config.geometry_motion_application_report_enabled:
            report_path = os.path.join(self.out_dir, "geometry_motion_interface_report.json")
        self.geometry_motion_interface_report = write_geometry_motion_interface_report(
            self.config.geometry_motion_application_config_path or self.config.geometry_motion_config_path,
            report_path,
            geometry_motion_mode=self.config.geometry_motion_mode,
        )
        self.timing["geometry_motion_interface_time"] += time.perf_counter() - t0
        return self.geometry_motion_interface_report

    def step_once(self):
        if not self.initialized:
            self.initialize()

        if self.config.fsi_exchange_mode == "lbm_subcycled_per_fsi_step":
            self._step_once_subcycled()
            self.current_lbm_step += 1
            return

        coupling_mode = self.config.coupling_mode
        if coupling_mode == "none":
            self._step_none()
        elif coupling_mode == "penalty":
            self._step_penalty()
        elif coupling_mode == "moving_boundary":
            self._step_moving_boundary()
        else:
            raise ValueError(f"unsupported coupling_mode: {coupling_mode}")

        self.current_lbm_step += 1
        self.total_lbm_substeps += 1

    def _step_once_subcycled(self):
        if self.config.coupling_mode != "moving_boundary":
            raise ValueError("subcycled FSI exchange currently supports only moving_boundary coupling")
        self._step_moving_boundary_subcycled()

    def _project(self):
        t0 = time.perf_counter()
        self.projector.project(self.solid, self.lbm)
        self.timing["projection_time"] += time.perf_counter() - t0
        self._apply_wall_velocity_application_if_enabled()

    def _apply_wall_velocity_application_if_enabled(self):
        if self.config.wall_velocity_application_mode == "disabled":
            return None
        if self.config.wall_velocity_application_mode != "solid_vel_experimental":
            raise ValueError(f"unsupported wall_velocity_application_mode: {self.config.wall_velocity_application_mode}")
        if self.config.boundary_motion_mode != "prescribed_kinematic":
            raise ValueError("solid_vel_experimental wall velocity application requires prescribed_kinematic boundary motion")

        from ..wall_velocity.application import apply_wall_velocity_application_to_lbm

        t0 = time.perf_counter()
        report_path = None
        if self.config.wall_velocity_application_report_enabled:
            report_path = os.path.join(self.out_dir, "wall_velocity_application_report.json")
        report = apply_wall_velocity_application_to_lbm(
            self.lbm,
            self.config.wall_velocity_application_config_path,
            self.config.n_grid,
            self.current_lbm_step,
            report_path=report_path,
        )
        self.wall_velocity_application_report = report
        self.wall_velocity_application_reports.append(report)
        self.timing["wall_velocity_application_time"] += time.perf_counter() - t0
        return report

    def _step_none(self):
        self._project()

        t0 = time.perf_counter()
        self.lbm.step()
        self.timing["lbm_step_time"] += time.perf_counter() - t0

        t0 = time.perf_counter()
        for _ in range(self.config.mpm_substeps_per_lbm_step):
            self.solid.substep()
            self.total_mpm_substeps += 1
        self.timing["mpm_substep_time"] += time.perf_counter() - t0

    def _step_penalty(self):
        self._project()

        t0 = time.perf_counter()
        self.penalty_coupler.clear_force_fields(self.lbm)
        self.penalty_coupler.build_penalty_force(self.lbm)
        self.timing["coupling_time"] += time.perf_counter() - t0

        t0 = time.perf_counter()
        self.lbm.step()
        self.timing["lbm_step_time"] += time.perf_counter() - t0

        t0 = time.perf_counter()
        for _ in range(self.config.mpm_substeps_per_lbm_step):
            self.solid.clear_grid()
            self.solid.p2g()
            self.penalty_coupler.add_lbm_reaction_to_mpm_grid(self.solid, self.lbm)
            self.solid.grid_update()
            self.solid.g2p()
            self.total_mpm_substeps += 1
        self.timing["mpm_substep_time"] += time.perf_counter() - t0

    def _step_moving_boundary(self):
        self._project()

        t0 = time.perf_counter()
        self.lbm.update_dynamic_solid(self.config.dynamic_solid_threshold)
        self.lbm.reinitialize_new_fluid_cells()
        self.timing["coupling_time"] += time.perf_counter() - t0

        t0 = time.perf_counter()
        self.lbm.step_moving_bounceback()
        self.timing["lbm_step_time"] += time.perf_counter() - t0

        self._advance_mpm_with_moving_boundary_reaction()

    def _step_moving_boundary_subcycled(self):
        self._project()

        for _ in range(self.config.lbm_substeps_per_fsi_step):
            t0 = time.perf_counter()
            self.lbm.update_dynamic_solid(self.config.dynamic_solid_threshold)
            self.lbm.reinitialize_new_fluid_cells()
            self.timing["coupling_time"] += time.perf_counter() - t0

            t0 = time.perf_counter()
            self.lbm.step_moving_bounceback()
            self.timing["lbm_step_time"] += time.perf_counter() - t0
            self.total_lbm_substeps += 1

        self._advance_mpm_with_moving_boundary_reaction()

    def _advance_mpm_with_moving_boundary_reaction(self):
        t0 = time.perf_counter()
        if self.config.reaction_transfer_mode == "engineering":
            for _ in range(self.config.mpm_substeps_per_lbm_step):
                self.solid.clear_grid()
                self.solid.p2g()
                self.mb_coupler.clear_reaction_diagnostics()
                self.mb_coupler.add_moving_boundary_reaction_to_mpm_grid(self.solid, self.lbm)
                self.solid.grid_update()
                self.solid.g2p()
                self.total_mpm_substeps += 1
        elif self.config.reaction_transfer_mode == "link_area_experimental":
            self.link_area_coupler.update_area_scale_from_lbm(self.lbm)
            for _ in range(self.config.mpm_substeps_per_lbm_step):
                self.solid.clear_grid()
                self.solid.p2g()
                self.link_area_coupler.clear_reaction_diagnostics()
                self.link_area_coupler.add_link_area_reaction_to_mpm_grid(self.solid, self.lbm)
                self.solid.grid_update()
                self.solid.g2p()
                self.total_mpm_substeps += 1
        else:
            raise ValueError(f"unsupported reaction_transfer_mode: {self.config.reaction_transfer_mode}")
        self.timing["mpm_substep_time"] += time.perf_counter() - t0

    def run(self):
        total_start = time.perf_counter()
        if not self.initialized:
            self.initialize()

        self.collect_diagnostics(0)
        for _ in range(self.config.n_lbm_steps):
            self.step_once()
            should_record = (
                self.current_lbm_step % self.config.output_interval == 0
                or self.current_lbm_step == self.config.n_lbm_steps
            )
            if should_record:
                self.collect_diagnostics(self.current_lbm_step)

        self.export_outputs(self.current_lbm_step)
        self.save_timeseries()
        self.timing["total_time"] = time.perf_counter() - total_start
        return self.diagnostics_rows

    def collect_diagnostics(self, step: int):
        t0 = time.perf_counter()
        lbm_stats = self.lbm.get_stats()
        mpm_stats = self.solid.get_stats()
        lbm_fluid_stats = FSIDiagnostics3D.lbm_fluid_stats(self.lbm)
        projection_zone_velocity = FSIDiagnostics3D.projection_zone_fluid_mean_velocity(self.lbm)
        far_field_velocity = FSIDiagnostics3D.far_field_fluid_mean_velocity(self.lbm)
        solid_mean_velocity = FSIDiagnostics3D.solid_mean_velocity_norm(self.solid)
        projection_stats = self.projector.get_stats()
        force_stats = FSIDiagnostics3D.force_stats(self.lbm)

        bb_link_count = 0
        bb_max_correction = 0.0
        if self.config.coupling_mode == "moving_boundary":
            moving_stats = self.lbm.get_moving_boundary_stats()
            bb_link_count = moving_stats["bb_link_count"]
            bb_max_correction = moving_stats["bb_max_correction"]

        active_reaction_particle_count = 0
        max_grid_reaction_norm = 0.0
        if self.config.coupling_mode == "moving_boundary" and self.mb_coupler is not None:
            mb_stats = self.mb_coupler.get_stats()
            active_reaction_particle_count = mb_stats["active_reaction_particle_count"]
            max_grid_reaction_norm = mb_stats["max_grid_reaction_norm"]
        elif self.config.coupling_mode == "moving_boundary" and self.link_area_coupler is not None:
            link_area_stats = self.link_area_coupler.get_stats()
            active_reaction_particle_count = link_area_stats["active_reaction_particle_count"]
            max_grid_reaction_norm = link_area_stats["max_grid_reaction_norm"]
        elif self.config.coupling_mode == "penalty" and self.penalty_coupler is not None:
            penalty_stats = self.penalty_coupler.get_stats()
            max_grid_reaction_norm = penalty_stats["max_reaction_grid_force_norm"]

        elapsed_seconds = 0.0 if self.start_time is None else time.perf_counter() - self.start_time
        row = {
            "step": int(step),
            "total_mpm_substeps": int(self.total_mpm_substeps),
            "coupling_mode": self.config.coupling_mode,
            "rho_min": lbm_stats["rho_min"],
            "rho_max": lbm_stats["rho_max"],
            "lbm_max_v": lbm_stats["max_v"],
            "fluid_mean_ux": float(lbm_fluid_stats["fluid_mean_velocity"][0]),
            "projection_zone_fluid_mean_ux": float(projection_zone_velocity[0]),
            "far_field_fluid_mean_ux": float(far_field_velocity[0]),
            "solid_mean_vx_norm": float(solid_mean_velocity[0]),
            "mpm_min_J": mpm_stats["min_J"],
            "mpm_max_speed": mpm_stats["max_speed"],
            "projected_mass": projection_stats["projected_mass"],
            "active_cell_count": projection_stats["active_cell_count"],
            "cell_force_max_norm": force_stats["max_cell_force_norm"],
            "hydro_force_max_norm": force_stats["max_hydro_force_norm"],
            "bb_link_count": int(bb_link_count),
            "bb_max_correction": float(bb_max_correction),
            "active_reaction_particle_count": int(active_reaction_particle_count),
            "max_grid_reaction_norm": float(max_grid_reaction_norm),
            "elapsed_seconds": elapsed_seconds,
        }
        self._assert_row_finite(row)
        self.diagnostics_rows.append(row)
        self.collect_flap_tip_monitor(step)
        self.timing["diagnostics_time"] += time.perf_counter() - t0
        return row

    def collect_flap_tip_monitor(self, step: int):
        if self.initial_particle_positions is None or self.free_tip_proxy_mask is None:
            return None
        if not np.any(self.free_tip_proxy_mask):
            return None
        x_np = self.solid.x.to_numpy()
        displacement_norm = x_np[self.free_tip_proxy_mask] - self.initial_particle_positions[self.free_tip_proxy_mask]
        displacement_mean = np.mean(displacement_norm, axis=0)
        scale_m = self._duct_length_scale_m()
        displacement_m = displacement_mean * scale_m
        row = {
            "step": int(step),
            "time_s": float(step) * self._monitor_time_step_s(),
            "flap_tip_total_displacement_m": float(np.linalg.norm(displacement_m)),
            "flap_tip_x_displacement_m": float(displacement_m[0]),
            "flap_tip_y_displacement_m": float(displacement_m[1]),
        }
        self.flap_tip_monitor_rows.append(row)
        return row

    def _monitor_time_step_s(self) -> float:
        geometry_config = self._make_geometry_config() if self.config.geometry_config_path else None
        metadata = getattr(geometry_config, "dimensional_reference", None) if geometry_config is not None else None
        if metadata and "transient_dt_s" in metadata:
            return float(metadata["transient_dt_s"])
        return float(self.sim.lbm_dt_phys)

    def _duct_length_scale_m(self) -> float:
        geometry_config = self._make_geometry_config() if self.config.geometry_config_path else None
        if geometry_config is None:
            return 1.0
        duct = geometry_config.duct or {}
        metadata = getattr(geometry_config, "dimensional_reference", None) or {}
        duct_x = duct.get("x", [0.0, 1.0])
        duct_span = max(float(duct_x[1]) - float(duct_x[0]), 1.0e-12)
        return float(metadata.get("duct_length_m", 1.0)) / duct_span

    def _assert_row_finite(self, row):
        numeric_values = [value for value in row.values() if isinstance(value, (int, float))]
        assert_no_nan_inf_array("driver diagnostics", numeric_values)

    def export_outputs(self, step: int):
        t0 = time.perf_counter()
        if self.config.write_particles:
            self.solid.export_particles(self.out_dir)
        if self.config.write_vtk:
            self.lbm.export_VTK(step, out_prefix=os.path.join(self.out_dir, "LBMFluid"))
        self.timing["export_time"] += time.perf_counter() - t0

    def save_timeseries(self):
        csv_path = os.path.join(self.out_dir, "diagnostics_timeseries.csv")
        save_csv_rows(self.diagnostics_rows, csv_path, fieldnames=DIAGNOSTIC_FIELDS)

        npz_payload = {
            "columns": np.asarray(DIAGNOSTIC_FIELDS),
            "modes": np.asarray([row["coupling_mode"] for row in self.diagnostics_rows]),
        }
        for field in DIAGNOSTIC_FIELDS:
            if field == "coupling_mode":
                continue
            npz_payload[field] = np.asarray([row[field] for row in self.diagnostics_rows], dtype=np.float64)

        np.savez(os.path.join(self.out_dir, "diagnostics_timeseries.npz"), **npz_payload)

        if self.flap_tip_monitor_rows:
            save_csv_rows(
                self.flap_tip_monitor_rows,
                os.path.join(self.out_dir, "flap_tip_displacement_timeseries.csv"),
                fieldnames=[
                    "step",
                    "time_s",
                    "flap_tip_total_displacement_m",
                    "flap_tip_x_displacement_m",
                    "flap_tip_y_displacement_m",
                ],
            )

    def final_diagnostics(self):
        if not self.diagnostics_rows:
            return None
        return self.diagnostics_rows[-1]

    def performance_row(self):
        row = {"mode": self.config.coupling_mode}
        row.update(self.timing)
        return row


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
