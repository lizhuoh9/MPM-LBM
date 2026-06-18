import os
import time

import numpy as np

from .coupling import PenaltyFSICoupler3D
from .diagnostics import FSIDiagnostics3D
from .fsi_config import FSIDriverConfig
from .lbm_fluid import LBMFluid3D
from .moving_boundary_coupling import MovingBoundaryFSICoupler3D
from .mpm_solid import MPMSolid3D
from .projection import MPMToLBMProjector3D
from .run_utils import assert_no_nan_inf_array, ensure_output_dir, make_all_fluid_geo, save_csv_rows, save_json_config
from .units import GridUnitMapper


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
            "total_time": 0.0,
        }

        self.geo_path = os.path.join(self.out_dir, "geo_all_fluid_32.dat")
        self.initialized = False
        self.start_time = None

        self.lbm = None
        self.solid = None
        self.projector = None
        self.penalty_coupler = None
        self.mb_coupler = None

    def initialize(self):
        t0 = time.perf_counter()
        ensure_output_dir(self.out_dir)
        make_all_fluid_geo(self.geo_path, self.config.n_grid)
        save_json_config(self.config, os.path.join(self.out_dir, "driver_config.json"))

        self.lbm = LBMFluid3D(self.sim.make_lbm_config())
        self.lbm.init_geo(self.geo_path)
        self.lbm.init_simulation()

        self.solid = MPMSolid3D(
            self.sim.make_mpm_config(
                gravity=self.config.gravity,
                box_min=self.config.box_min,
                box_max=self.config.box_max,
            ),
            n_particles=self.config.n_particles,
        )
        self.solid.init_box()
        target_u_norm = self.mapper.velocity_lbm_to_norm(self.config.target_u_lbm)
        self.solid.set_uniform_velocity(float(target_u_norm[0]), float(target_u_norm[1]), float(target_u_norm[2]))

        self.projector = MPMToLBMProjector3D(self.sim)
        if self.config.coupling_mode == "penalty":
            self.penalty_coupler = PenaltyFSICoupler3D(
                self.sim,
                beta_lbm=self.config.beta_lbm,
                force_cap_lbm=self.config.penalty_force_cap_lbm,
            )
        if self.config.coupling_mode == "moving_boundary":
            self.mb_coupler = MovingBoundaryFSICoupler3D(
                self.sim,
                reaction_scale=self.config.mb_reaction_scale,
                force_cap_norm=self.config.mb_force_cap_norm,
                phi_min=1.0e-6,
            )

        self.initialized = True
        self.start_time = time.perf_counter()
        self.timing["init_time"] += self.start_time - t0

    def step_once(self):
        if not self.initialized:
            self.initialize()

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

    def _project(self):
        t0 = time.perf_counter()
        self.projector.project(self.solid, self.lbm)
        self.timing["projection_time"] += time.perf_counter() - t0

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

        t0 = time.perf_counter()
        for _ in range(self.config.mpm_substeps_per_lbm_step):
            self.solid.clear_grid()
            self.solid.p2g()
            self.mb_coupler.clear_reaction_diagnostics()
            self.mb_coupler.add_moving_boundary_reaction_to_mpm_grid(self.solid, self.lbm)
            self.solid.grid_update()
            self.solid.g2p()
            self.total_mpm_substeps += 1
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
        self.timing["diagnostics_time"] += time.perf_counter() - t0
        return row

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

    def final_diagnostics(self):
        if not self.diagnostics_rows:
            return None
        return self.diagnostics_rows[-1]

    def performance_row(self):
        row = {"mode": self.config.coupling_mode}
        row.update(self.timing)
        return row
