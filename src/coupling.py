import taichi as ti


@ti.data_oriented
class PenaltyFSICoupler3D:
    def __init__(
        self,
        sim_config,
        beta_lbm: float = 1.0e-3,
        phi_min: float = 1.0e-6,
        force_cap_lbm: float = 1.0e-4,
        reaction_scale: float = 1.0,
    ):
        if beta_lbm <= 0.0:
            raise ValueError("beta_lbm must be positive")
        if phi_min < 0.0:
            raise ValueError("phi_min must be non-negative")
        if force_cap_lbm <= 0.0:
            raise ValueError("force_cap_lbm must be positive")
        if reaction_scale <= 0.0:
            raise ValueError("reaction_scale must be positive")

        self.n_grid = sim_config.n_grid
        self.dx_norm = sim_config.dx_norm
        self.inv_dx_norm = 1.0 / sim_config.dx_norm
        self.lbm_dt_phys = sim_config.lbm_dt_phys
        self.beta_lbm = float(beta_lbm)
        self.phi_min = float(phi_min)
        self.force_cap_lbm = float(force_cap_lbm)
        self.reaction_scale = float(reaction_scale)
        self.force_density_scale_lbm_to_norm = self.dx_norm / (self.lbm_dt_phys**2)

        self.active_force_cell_count = ti.field(ti.i32, shape=())
        self.max_cell_force_norm = ti.field(ti.f32, shape=())
        self.max_hydro_force_norm = ti.field(ti.f32, shape=())
        self.net_cell_force = ti.Vector.field(3, ti.f32, shape=())
        self.net_hydro_force = ti.Vector.field(3, ti.f32, shape=())
        self.max_reaction_grid_force_norm = ti.field(ti.f32, shape=())
        self.net_reaction_grid_force = ti.Vector.field(3, ti.f32, shape=())

    @ti.kernel
    def clear_force_fields(self, lbm: ti.template()):
        for I in ti.grouped(lbm.rho):
            lbm.cell_force[I] = ti.Vector([0.0, 0.0, 0.0])
            lbm.hydro_force[I] = ti.Vector([0.0, 0.0, 0.0])

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
    def build_penalty_force(self, lbm: ti.template()):
        self.active_force_cell_count[None] = 0
        self.max_cell_force_norm[None] = 0.0
        self.max_hydro_force_norm[None] = 0.0
        self.net_cell_force[None] = ti.Vector([0.0, 0.0, 0.0])
        self.net_hydro_force[None] = ti.Vector([0.0, 0.0, 0.0])

        for I in ti.grouped(lbm.rho):
            force = ti.Vector([0.0, 0.0, 0.0])

            if lbm.solid[I] == 0:
                phi = lbm.solid_phi[I]
                if phi > self.phi_min:
                    force = self.beta_lbm * phi * lbm.rho[I] * (lbm.solid_vel[I] - lbm.v[I])
                    force_norm = force.norm()
                    if force_norm > self.force_cap_lbm:
                        force = force * (self.force_cap_lbm / force_norm)

                    ti.atomic_add(self.active_force_cell_count[None], 1)

            hydro_force = -force
            lbm.cell_force[I] = force
            lbm.hydro_force[I] = hydro_force

            ti.atomic_max(self.max_cell_force_norm[None], force.norm())
            ti.atomic_max(self.max_hydro_force_norm[None], hydro_force.norm())
            for d in ti.static(range(3)):
                ti.atomic_add(self.net_cell_force[None][d], force[d])
                ti.atomic_add(self.net_hydro_force[None][d], hydro_force[d])

    @ti.kernel
    def add_lbm_reaction_to_mpm_grid(self, solid: ti.template(), lbm: ti.template()):
        self.max_reaction_grid_force_norm[None] = 0.0
        self.net_reaction_grid_force[None] = ti.Vector([0.0, 0.0, 0.0])

        for p in range(solid.n_particles):
            Xp = solid.x[p] * self.inv_dx_norm
            base = ti.cast(Xp - 0.5, ti.i32)
            fx = Xp - ti.cast(base, ti.f32)

            w = [
                0.5 * (1.5 - fx) ** 2,
                0.75 - (fx - 1.0) ** 2,
                0.5 * (fx - 0.5) ** 2,
            ]
            hydro_density_lbm = ti.Vector([0.0, 0.0, 0.0])

            for offset in ti.static(ti.grouped(ti.ndrange(3, 3, 3))):
                I = base + offset
                if self.inside_lbm(I, lbm):
                    weight = w[offset.x].x * w[offset.y].y * w[offset.z].z
                    hydro_density_lbm += weight * lbm.hydro_force[I]

            J = ti.max(solid.Jp[p], 0.0)
            particle_volume = solid.vol0[p] * J
            particle_force_norm = (
                hydro_density_lbm
                * self.force_density_scale_lbm_to_norm
                * particle_volume
                * self.reaction_scale
            )

            for offset in ti.static(ti.grouped(ti.ndrange(3, 3, 3))):
                I = base + offset
                if solid.inside_grid(I):
                    weight = w[offset.x].x * w[offset.y].y * w[offset.z].z
                    contribution = weight * particle_force_norm
                    ti.atomic_add(solid.grid_f_ext[I], contribution)
                    ti.atomic_max(self.max_reaction_grid_force_norm[None], contribution.norm())
                    for d in ti.static(range(3)):
                        ti.atomic_add(self.net_reaction_grid_force[None][d], contribution[d])

    def get_stats(self):
        net_cell = self.net_cell_force[None].to_numpy()
        net_hydro = self.net_hydro_force[None].to_numpy()
        net_reaction = self.net_reaction_grid_force[None].to_numpy()
        return {
            "n_grid": self.n_grid,
            "dx_norm": self.dx_norm,
            "inv_dx_norm": self.inv_dx_norm,
            "lbm_dt_phys": self.lbm_dt_phys,
            "beta_lbm": self.beta_lbm,
            "phi_min": self.phi_min,
            "force_cap_lbm": self.force_cap_lbm,
            "reaction_scale": self.reaction_scale,
            "force_density_scale_lbm_to_norm": self.force_density_scale_lbm_to_norm,
            "active_force_cell_count": int(self.active_force_cell_count[None]),
            "max_cell_force_norm": float(self.max_cell_force_norm[None]),
            "max_hydro_force_norm": float(self.max_hydro_force_norm[None]),
            "net_cell_force": tuple(float(v) for v in net_cell),
            "net_hydro_force": tuple(float(v) for v in net_hydro),
            "max_reaction_grid_force_norm": float(self.max_reaction_grid_force_norm[None]),
            "net_reaction_grid_force": tuple(float(v) for v in net_reaction),
        }
