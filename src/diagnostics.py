"""diagnostic-only helpers for Step 7 penalty-coupled FSI validation."""

import numpy as np


class FSIDiagnostics3D:
    @staticmethod
    def lbm_fluid_stats(lbm):
        base_stats = lbm.get_stats()
        solid = lbm.solid.to_numpy()
        velocity = lbm.v.to_numpy()
        fluid = solid == 0

        if np.any(fluid):
            fluid_mean_velocity = np.mean(velocity[fluid], axis=0)
        else:
            fluid_mean_velocity = np.zeros(3, dtype=np.float64)

        return {
            **base_stats,
            "fluid_cell_count": int(np.count_nonzero(fluid)),
            "fluid_mean_velocity": tuple(float(v) for v in fluid_mean_velocity),
        }

    @staticmethod
    def mpm_particle_stats(solid):
        base_stats = solid.get_stats()
        x = solid.x.to_numpy()
        v = solid.v.to_numpy()
        mass = solid.mass.to_numpy()

        if mass.size > 0 and float(np.sum(mass)) > 0.0:
            mean_velocity = np.average(v, axis=0, weights=mass)
            momentum = np.sum(v * mass[:, None], axis=0)
        else:
            mean_velocity = np.zeros(3, dtype=np.float64)
            momentum = np.zeros(3, dtype=np.float64)

        return {
            **base_stats,
            "particle_count": int(x.shape[0]),
            "mean_velocity": tuple(float(a) for a in mean_velocity),
            "momentum": tuple(float(a) for a in momentum),
        }

    @staticmethod
    def projection_zone_fluid_mean_velocity(lbm, phi_threshold=1.0e-6):
        solid_phi = lbm.solid_phi.to_numpy()
        velocity = lbm.v.to_numpy()
        active = solid_phi > phi_threshold

        if not np.any(active):
            return np.zeros(3, dtype=np.float64)

        return np.average(velocity[active], axis=0, weights=solid_phi[active])

    @staticmethod
    def far_field_fluid_mean_velocity(lbm, phi_threshold=1.0e-6):
        solid = lbm.solid.to_numpy()
        solid_phi = lbm.solid_phi.to_numpy()
        velocity = lbm.v.to_numpy()
        far_field = (solid == 0) & (solid_phi <= phi_threshold)

        if not np.any(far_field):
            return np.zeros(3, dtype=np.float64)

        return np.mean(velocity[far_field], axis=0)

    @staticmethod
    def projected_solid_mean_velocity(lbm, eps_mass=1.0e-12):
        mass = lbm.solid_mass.to_numpy()
        velocity = lbm.solid_vel.to_numpy()
        active = mass > eps_mass

        if not np.any(active):
            return np.zeros(3, dtype=np.float64)

        return np.average(velocity[active], axis=0, weights=mass[active])

    @staticmethod
    def force_stats(lbm):
        cell_force = lbm.cell_force.to_numpy()
        hydro_force = lbm.hydro_force.to_numpy()
        cell_norm = np.linalg.norm(cell_force, axis=3)
        hydro_norm = np.linalg.norm(hydro_force, axis=3)
        net_cell_force = np.sum(cell_force.reshape(-1, 3), axis=0, dtype=np.float64)
        net_hydro_force = np.sum(hydro_force.reshape(-1, 3), axis=0, dtype=np.float64)
        force_balance = net_cell_force + net_hydro_force

        return {
            "active_force_cell_count": int(np.count_nonzero(cell_norm > 0.0)),
            "max_cell_force_norm": float(np.max(cell_norm)),
            "max_hydro_force_norm": float(np.max(hydro_norm)),
            "net_cell_force": tuple(float(a) for a in net_cell_force),
            "net_hydro_force": tuple(float(a) for a in net_hydro_force),
            "force_balance_error": float(np.linalg.norm(force_balance)),
        }

    @staticmethod
    def solid_mean_velocity_norm(solid):
        velocity = solid.v.to_numpy()
        mass = solid.mass.to_numpy()

        if mass.size == 0 or float(np.sum(mass)) <= 0.0:
            return np.zeros(3, dtype=np.float64)

        return np.average(velocity, axis=0, weights=mass)

    @staticmethod
    def solid_momentum_norm(solid):
        velocity = solid.v.to_numpy()
        mass = solid.mass.to_numpy()

        if mass.size == 0:
            return np.zeros(3, dtype=np.float64)

        return np.sum(velocity * mass[:, None], axis=0, dtype=np.float64)

    @staticmethod
    def lbm_velocity_profile_x_over_y(lbm, z_slice=None):
        velocity = lbm.v.to_numpy()
        ux = velocity[..., 0]

        if z_slice is None:
            return np.mean(ux, axis=(0, 2))

        z_index = int(np.clip(z_slice, 0, ux.shape[2] - 1))
        return np.mean(ux[:, :, z_index], axis=0)
