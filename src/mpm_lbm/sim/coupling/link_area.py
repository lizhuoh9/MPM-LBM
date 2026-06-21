"""Experimental link-area reaction transfer for moving-boundary coupling."""

import numpy as np
import taichi as ti

from .link_area_accounting import LinkAreaMomentumAccounting3D, VALID_AREA_POLICIES


@ti.data_oriented
class LinkAreaMovingBoundaryCoupler3D:
    """
    Experimental opt-in moving-boundary reaction transfer.

    The LBM moving bounce-back path is unchanged. This class samples the
    existing lbm.hydro_force field and applies a bounded global area_scale
    derived from Step 17 link-area proxy accounting before writing reaction
    forces to MPMSolid3D.grid_f_ext.
    """

    def __init__(
        self,
        sim_config,
        area_policy: str = "inverse_length",
        reaction_scale: float = 1.0,
        force_cap_norm: float = 1.0e-5,
        phi_min: float = 1.0e-6,
        area_scale_min: float = 0.25,
        area_scale_max: float = 2.0,
    ):
        if area_policy not in VALID_AREA_POLICIES:
            raise ValueError(f"area_policy must be one of {VALID_AREA_POLICIES}")
        if reaction_scale <= 0.0:
            raise ValueError("reaction_scale must be positive")
        if force_cap_norm <= 0.0:
            raise ValueError("force_cap_norm must be positive")
        if phi_min < 0.0:
            raise ValueError("phi_min must be non-negative")
        if area_scale_min <= 0.0:
            raise ValueError("area_scale_min must be positive")
        if area_scale_max <= 0.0:
            raise ValueError("area_scale_max must be positive")
        if area_scale_min > area_scale_max:
            raise ValueError("area_scale_min must be <= area_scale_max")

        self.n_grid = sim_config.n_grid
        self.dx_norm = sim_config.dx_norm
        self.inv_dx_norm = 1.0 / sim_config.dx_norm
        self.lbm_dt_phys = sim_config.lbm_dt_phys
        self.area_policy = area_policy
        self.reaction_scale = float(reaction_scale)
        self.force_cap_norm = float(force_cap_norm)
        self.phi_min = float(phi_min)
        self.area_scale_min = float(area_scale_min)
        self.area_scale_max = float(area_scale_max)

        # Same engineering dimensional bridge as MovingBoundaryFSICoupler3D.
        # Step 18 only adds a bounded global proxy scale on top of it.
        self.force_density_scale_lbm_to_norm = self.dx_norm / (self.lbm_dt_phys**2)

        self.area_scale = ti.field(ti.f32, shape=())
        self.raw_area_scale = ti.field(ti.f32, shape=())
        self.area_proxy_total = ti.field(ti.f32, shape=())
        self.area_weighted_hydro_sum = ti.Vector.field(3, ti.f32, shape=())

        self.active_reaction_particle_count = ti.field(ti.i32, shape=())
        self.max_particle_reaction_norm = ti.field(ti.f32, shape=())
        self.max_grid_reaction_norm = ti.field(ti.f32, shape=())
        self.net_particle_reaction_force = ti.Vector.field(3, ti.f32, shape=())
        self.net_grid_reaction_force = ti.Vector.field(3, ti.f32, shape=())

        self.set_area_summary(1.0, 1.0, 0.0, 0.0, 0.0, 0.0)

    @ti.func
    def inside_lbm(self, I, lbm: ti.template()):
        return (
            0 <= I.x
            and I.x < lbm.nx
            and 0 <= I.y
            and I.y < lbm.ny
            and 0 <= I.z
            and I.z < lbm.nz
        )

    def update_area_scale_from_lbm(self, lbm):
        summary = LinkAreaMomentumAccounting3D.summarize_link_accounting(lbm, policy=self.area_policy)
        eps = 1.0e-12
        numerator = abs(float(summary["area_weighted_solid_force_x"]))
        denominator = abs(float(summary["bb_net_solid_force_x"])) + eps
        raw_area_scale = numerator / denominator
        area_scale = float(np.clip(raw_area_scale, self.area_scale_min, self.area_scale_max))
        if not np.isfinite(area_scale):
            area_scale = self.area_scale_min
        self.set_area_summary(
            raw_area_scale,
            area_scale,
            float(summary["area_proxy_total"]),
            float(summary["area_weighted_solid_force_x"]),
            float(summary["area_weighted_solid_force_y"]),
            float(summary["area_weighted_solid_force_z"]),
        )
        result = dict(summary)
        result.update(
            {
                "area_policy": self.area_policy,
                "raw_area_scale": float(raw_area_scale),
                "area_scale": float(area_scale),
            }
        )
        return result

    @ti.kernel
    def set_area_scale(self, value: ti.f32):
        self.area_scale[None] = value

    @ti.kernel
    def set_area_summary(
        self,
        raw_area_scale: ti.f32,
        area_scale: ti.f32,
        area_proxy_total: ti.f32,
        weighted_x: ti.f32,
        weighted_y: ti.f32,
        weighted_z: ti.f32,
    ):
        self.raw_area_scale[None] = raw_area_scale
        self.area_scale[None] = area_scale
        self.area_proxy_total[None] = area_proxy_total
        self.area_weighted_hydro_sum[None] = ti.Vector([weighted_x, weighted_y, weighted_z])

    @ti.kernel
    def clear_reaction_diagnostics(self):
        self.active_reaction_particle_count[None] = 0
        self.max_particle_reaction_norm[None] = 0.0
        self.max_grid_reaction_norm[None] = 0.0
        self.net_particle_reaction_force[None] = ti.Vector([0.0, 0.0, 0.0])
        self.net_grid_reaction_force[None] = ti.Vector([0.0, 0.0, 0.0])

    @ti.kernel
    def add_link_area_reaction_to_mpm_grid(self, solid: ti.template(), lbm: ti.template()):
        scale = self.area_scale[None]
        for p in range(solid.n_particles):
            Xp = solid.x[p] * self.inv_dx_norm
            base = ti.cast(Xp - 0.5, ti.i32)
            fx = Xp - ti.cast(base, ti.f32)

            w = [
                0.5 * (1.5 - fx) ** 2,
                0.75 - (fx - 1.0) ** 2,
                0.5 * (fx - 0.5) ** 2,
            ]

            sampled_hydro_lbm = ti.Vector([0.0, 0.0, 0.0])
            sampled_phi = 0.0

            for offset in ti.static(ti.grouped(ti.ndrange(3, 3, 3))):
                I = base + offset
                if self.inside_lbm(I, lbm):
                    weight = w[offset.x].x * w[offset.y].y * w[offset.z].z
                    sampled_hydro_lbm += weight * lbm.hydro_force[I]
                    sampled_phi += weight * lbm.solid_phi[I]

            if sampled_phi > self.phi_min:
                J = ti.max(solid.Jp[p], 0.0)
                particle_volume = solid.vol0[p] * J
                particle_force = (
                    sampled_hydro_lbm
                    * self.force_density_scale_lbm_to_norm
                    * particle_volume
                    * self.reaction_scale
                    * scale
                )

                particle_force_norm = particle_force.norm()
                if particle_force_norm > self.force_cap_norm:
                    particle_force = particle_force * (self.force_cap_norm / particle_force_norm)
                    particle_force_norm = self.force_cap_norm

                if particle_force_norm > 0.0:
                    ti.atomic_add(self.active_reaction_particle_count[None], 1)

                ti.atomic_max(self.max_particle_reaction_norm[None], particle_force_norm)

                for d in ti.static(range(3)):
                    ti.atomic_add(self.net_particle_reaction_force[None][d], particle_force[d])

                for offset in ti.static(ti.grouped(ti.ndrange(3, 3, 3))):
                    I = base + offset
                    if solid.inside_grid(I):
                        weight = w[offset.x].x * w[offset.y].y * w[offset.z].z
                        contribution = weight * particle_force
                        ti.atomic_add(solid.grid_f_ext[I], contribution)
                        ti.atomic_max(self.max_grid_reaction_norm[None], contribution.norm())
                        for d in ti.static(range(3)):
                            ti.atomic_add(self.net_grid_reaction_force[None][d], contribution[d])

    def get_stats(self):
        net_particle = self.net_particle_reaction_force[None].to_numpy()
        net_grid = self.net_grid_reaction_force[None].to_numpy()
        weighted = self.area_weighted_hydro_sum[None].to_numpy()
        return {
            "n_grid": self.n_grid,
            "dx_norm": self.dx_norm,
            "inv_dx_norm": self.inv_dx_norm,
            "lbm_dt_phys": self.lbm_dt_phys,
            "area_policy": self.area_policy,
            "reaction_scale": self.reaction_scale,
            "force_cap_norm": self.force_cap_norm,
            "phi_min": self.phi_min,
            "force_density_scale_lbm_to_norm": self.force_density_scale_lbm_to_norm,
            "area_scale_min": self.area_scale_min,
            "area_scale_max": self.area_scale_max,
            "raw_area_scale": float(self.raw_area_scale[None]),
            "area_scale": float(self.area_scale[None]),
            "area_proxy_total": float(self.area_proxy_total[None]),
            "area_weighted_hydro_sum": tuple(float(v) for v in weighted),
            "active_reaction_particle_count": int(self.active_reaction_particle_count[None]),
            "max_particle_reaction_norm": float(self.max_particle_reaction_norm[None]),
            "max_grid_reaction_norm": float(self.max_grid_reaction_norm[None]),
            "net_particle_reaction_force": tuple(float(v) for v in net_particle),
            "net_grid_reaction_force": tuple(float(v) for v in net_grid),
        }
