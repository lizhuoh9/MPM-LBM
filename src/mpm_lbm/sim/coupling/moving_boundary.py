import taichi as ti


@ti.data_oriented
class MovingBoundaryFSICoupler3D:
    def __init__(
        self,
        sim_config,
        reaction_scale: float = 1.0,
        force_cap_norm: float = 1.0e-2,
        phi_min: float = 1.0e-6,
    ):
        if reaction_scale <= 0.0:
            raise ValueError("reaction_scale must be positive")
        if force_cap_norm <= 0.0:
            raise ValueError("force_cap_norm must be positive")
        if phi_min < 0.0:
            raise ValueError("phi_min must be non-negative")

        self.n_grid = sim_config.n_grid
        self.dx_norm = sim_config.dx_norm
        self.inv_dx_norm = 1.0 / sim_config.dx_norm
        self.lbm_dt_phys = sim_config.lbm_dt_phys
        self.reaction_scale = float(reaction_scale)
        self.force_cap_norm = float(force_cap_norm)
        self.phi_min = float(phi_min)

        # Step 9 uses this engineering scale for the MVP reaction transfer.
        # It is not a final sharp-interface area/link integration.
        self.force_density_scale_lbm_to_norm = self.dx_norm / (self.lbm_dt_phys**2)

        self.active_reaction_particle_count = ti.field(ti.i32, shape=())
        self.max_particle_reaction_norm = ti.field(ti.f32, shape=())
        self.max_grid_reaction_norm = ti.field(ti.f32, shape=())
        self.net_particle_reaction_force = ti.Vector.field(3, ti.f32, shape=())
        self.net_grid_reaction_force = ti.Vector.field(3, ti.f32, shape=())

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

    @ti.kernel
    def clear_reaction_diagnostics(self):
        self.active_reaction_particle_count[None] = 0
        self.max_particle_reaction_norm[None] = 0.0
        self.max_grid_reaction_norm[None] = 0.0
        self.net_particle_reaction_force[None] = ti.Vector([0.0, 0.0, 0.0])
        self.net_grid_reaction_force[None] = ti.Vector([0.0, 0.0, 0.0])

    @ti.kernel
    def add_moving_boundary_reaction_to_mpm_grid(self, solid: ti.template(), lbm: ti.template()):
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
        return {
            "n_grid": self.n_grid,
            "dx_norm": self.dx_norm,
            "inv_dx_norm": self.inv_dx_norm,
            "lbm_dt_phys": self.lbm_dt_phys,
            "reaction_scale": self.reaction_scale,
            "force_cap_norm": self.force_cap_norm,
            "phi_min": self.phi_min,
            "force_density_scale_lbm_to_norm": self.force_density_scale_lbm_to_norm,
            "active_reaction_particle_count": int(self.active_reaction_particle_count[None]),
            "max_particle_reaction_norm": float(self.max_particle_reaction_norm[None]),
            "max_grid_reaction_norm": float(self.max_grid_reaction_norm[None]),
            "net_particle_reaction_force": tuple(float(v) for v in net_particle),
            "net_grid_reaction_force": tuple(float(v) for v in net_grid),
        }
