"""Diagnostic-only momentum accounting for moving-boundary FSI runs."""

import numpy as np


def _field_to_numpy(field, name):
    if hasattr(field, "to_numpy"):
        return np.asarray(field.to_numpy())
    return np.asarray(field)


def _vector3(values, name):
    arr = np.asarray(values, dtype=np.float64).reshape(-1)
    if arr.size != 3:
        raise ValueError(f"{name} must contain exactly three values")
    return arr


def _sum_vector_field(field, name):
    arr = _field_to_numpy(field, name).astype(np.float64, copy=False)
    if arr.shape[-1] != 3:
        raise ValueError(f"{name} must have a final dimension of 3")
    return np.sum(arr.reshape(-1, 3), axis=0, dtype=np.float64)


def _max_vector_norm(field, name):
    arr = _field_to_numpy(field, name).astype(np.float64, copy=False)
    if arr.shape[-1] != 3:
        raise ValueError(f"{name} must have a final dimension of 3")
    if arr.size == 0:
        return 0.0
    return float(np.max(np.linalg.norm(arr.reshape(-1, 3), axis=1)))


class MomentumAccounting3D:
    """
    Diagnostic-only accounting helpers for moving-boundary FSI.
    Does not modify solver state.
    """

    @staticmethod
    def hydro_force_sum(lbm) -> np.ndarray:
        return _sum_vector_field(lbm.hydro_force, "lbm.hydro_force")

    @staticmethod
    def cell_force_sum(lbm) -> np.ndarray:
        return _sum_vector_field(lbm.cell_force, "lbm.cell_force")

    @staticmethod
    def solid_particle_momentum(solid) -> np.ndarray:
        mass = _field_to_numpy(solid.mass, "solid.mass").astype(np.float64, copy=False).reshape(-1)
        velocity = _field_to_numpy(solid.v, "solid.v").astype(np.float64, copy=False)
        if velocity.shape != (mass.size, 3):
            raise ValueError("solid.v must have shape (n_particles, 3)")
        return np.sum(velocity * mass[:, None], axis=0, dtype=np.float64)

    @staticmethod
    def moving_boundary_accounting_row(
        step: int,
        lbm,
        solid,
        mb_coupler,
        previous_solid_momentum=None,
        cumulative_grid_reaction_impulse=None,
        target_u_lbm_x: float = 0.0,
    ) -> dict:
        hydro_sum = MomentumAccounting3D.hydro_force_sum(lbm)
        cell_sum = MomentumAccounting3D.cell_force_sum(lbm)
        solid_momentum = MomentumAccounting3D.solid_particle_momentum(solid)

        previous_momentum = (
            solid_momentum
            if previous_solid_momentum is None
            else _vector3(previous_solid_momentum, "previous_solid_momentum")
        )
        cumulative_impulse = (
            np.zeros(3, dtype=np.float64)
            if cumulative_grid_reaction_impulse is None
            else _vector3(cumulative_grid_reaction_impulse, "cumulative_grid_reaction_impulse")
        )

        moving_stats = lbm.get_moving_boundary_stats()
        mb_stats = mb_coupler.get_stats()
        bb_net_fluid_impulse = _vector3(moving_stats["bb_net_fluid_impulse"], "bb_net_fluid_impulse")
        bb_net_solid_force = _vector3(moving_stats["bb_net_solid_force"], "bb_net_solid_force")
        applied_particle_reaction = _vector3(
            mb_stats["net_particle_reaction_force"], "net_particle_reaction_force"
        )
        applied_grid_reaction = _vector3(mb_stats["net_grid_reaction_force"], "net_grid_reaction_force")

        # The existing Step 9 engineering transfer applies the sampled force to the
        # MPM grid. Step 15 reports the contract's reaction convention as the
        # equal-and-opposite diagnostic while keeping the applied values explicit.
        net_particle_reaction = -applied_particle_reaction
        net_grid_reaction = -applied_grid_reaction

        rho = _field_to_numpy(lbm.rho, "lbm.rho").astype(np.float64, copy=False)
        velocity = _field_to_numpy(lbm.v, "lbm.v").astype(np.float64, copy=False)
        solid_mask = _field_to_numpy(lbm.solid, "lbm.solid") == 0
        if np.any(solid_mask):
            rho_fluid = rho[solid_mask]
            velocity_fluid = velocity[solid_mask]
        else:
            rho_fluid = rho.reshape(-1)
            velocity_fluid = velocity.reshape(-1, 3)

        solid_phi = _field_to_numpy(lbm.solid_phi, "lbm.solid_phi").astype(np.float64, copy=False)
        active_projection = solid_phi > 1.0e-6
        if np.any(active_projection):
            projection_zone_velocity = np.average(
                velocity[active_projection], axis=0, weights=solid_phi[active_projection]
            )
        else:
            projection_zone_velocity = np.zeros(3, dtype=np.float64)

        solid_j = _field_to_numpy(solid.Jp, "solid.Jp").astype(np.float64, copy=False).reshape(-1)
        solid_velocity = _field_to_numpy(solid.v, "solid.v").astype(np.float64, copy=False)
        mpm_speed = np.linalg.norm(solid_velocity, axis=1) if solid_velocity.size else np.zeros(1)

        solid_momentum_delta = solid_momentum - previous_momentum
        eps = 1.0e-30
        response_ratio_x = abs(float(solid_momentum_delta[0])) / (
            abs(float(cumulative_impulse[0])) + eps
        )

        target_sign = np.sign(float(target_u_lbm_x))
        if target_sign == 0.0:
            force_sign_consistent = True
        else:
            force_sign_consistent = np.sign(float(net_grid_reaction[0])) == -target_sign

        row = {
            "step": int(step),
            "bb_link_count": int(moving_stats["bb_link_count"]),
            "bb_net_fluid_impulse_x": float(bb_net_fluid_impulse[0]),
            "bb_net_solid_force_x": float(bb_net_solid_force[0]),
            "hydro_force_sum_x": float(hydro_sum[0]),
            "cell_force_sum_x": float(cell_sum[0]),
            "net_particle_reaction_force_x": float(net_particle_reaction[0]),
            "net_grid_reaction_force_x": float(net_grid_reaction[0]),
            "applied_particle_reaction_force_x": float(applied_particle_reaction[0]),
            "applied_grid_reaction_force_x": float(applied_grid_reaction[0]),
            "solid_momentum_x": float(solid_momentum[0]),
            "solid_momentum_delta_x": float(solid_momentum_delta[0]),
            "fluid_mean_ux": float(np.mean(velocity_fluid[:, 0])) if velocity_fluid.size else 0.0,
            "projection_zone_ux": float(projection_zone_velocity[0]),
            "rho_min": float(np.min(rho_fluid)),
            "rho_max": float(np.max(rho_fluid)),
            "lbm_max_v": float(np.max(np.linalg.norm(velocity_fluid, axis=1))) if velocity_fluid.size else 0.0,
            "mpm_min_J": float(np.min(solid_j)) if solid_j.size else 0.0,
            "mpm_max_speed": float(np.max(mpm_speed)) if mpm_speed.size else 0.0,
            "cell_force_max_norm": _max_vector_norm(lbm.cell_force, "lbm.cell_force"),
            "hydro_force_max_norm": _max_vector_norm(lbm.hydro_force, "lbm.hydro_force"),
            "hydro_field_vs_bb_error_x": float(abs(hydro_sum[0] - bb_net_solid_force[0])),
            "grid_vs_particle_reaction_error_x": float(
                abs(applied_grid_reaction[0] - applied_particle_reaction[0])
            ),
            "solid_momentum_response_ratio_x": float(response_ratio_x),
            "force_sign_consistent": bool(force_sign_consistent),
        }

        numeric_values = [value for value in row.values() if isinstance(value, (int, float))]
        if not np.all(np.isfinite(numeric_values)):
            raise RuntimeError("moving-boundary accounting row contains NaN or Inf")
        return row
