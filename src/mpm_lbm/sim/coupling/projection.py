import taichi as ti


@ti.data_oriented
class MPMToLBMProjector3D:
    def __init__(self, sim_config):
        self.n_grid = sim_config.n_grid
        self.dx_norm = sim_config.dx_norm
        self.inv_dx_norm = 1.0 / sim_config.dx_norm
        self.cell_volume_norm = sim_config.dx_norm**3
        self.vel_scale_norm_to_lbm = sim_config.lbm_dt_phys / sim_config.dx_norm
        self.eps_mass = 1.0e-12

        self.projected_mass = ti.field(ti.f32, shape=())
        self.projected_volume_raw = ti.field(ti.f32, shape=())
        self.projected_volume_clamped = ti.field(ti.f32, shape=())
        self.max_phi_raw = ti.field(ti.f32, shape=())
        self.active_cell_count = ti.field(ti.i32, shape=())

    @ti.kernel
    def clear_projection(self, lbm: ti.template()):
        for I in ti.grouped(lbm.rho):
            lbm.solid_phi[I] = 0.0
            lbm.solid_mass[I] = 0.0
            lbm.solid_vel[I] = ti.Vector([0.0, 0.0, 0.0])

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
    def project_particles(self, solid: ti.template(), lbm: ti.template()):
        for p in range(solid.n_particles):
            Xp = solid.x[p] * self.inv_dx_norm
            base = ti.cast(Xp - 0.5, ti.i32)
            fx = Xp - ti.cast(base, ti.f32)

            w = [
                0.5 * (1.5 - fx) ** 2,
                0.75 - (fx - 1.0) ** 2,
                0.5 * (fx - 0.5) ** 2,
            ]

            J = ti.max(solid.Jp[p], 0.0)
            current_volume = solid.vol0[p] * J
            v_lbm = solid.v[p] * self.vel_scale_norm_to_lbm

            for offset in ti.static(ti.grouped(ti.ndrange(3, 3, 3))):
                I = base + offset
                if self.inside_lbm(I, lbm):
                    weight = w[offset.x].x * w[offset.y].y * w[offset.z].z
                    mass_contrib = weight * solid.mass[p]
                    volume_fraction_contrib = weight * current_volume / self.cell_volume_norm

                    ti.atomic_add(lbm.solid_phi[I], volume_fraction_contrib)
                    ti.atomic_add(lbm.solid_mass[I], mass_contrib)
                    ti.atomic_add(lbm.solid_vel[I], mass_contrib * v_lbm)

    @ti.kernel
    def normalize_projection(self, lbm: ti.template()):
        self.projected_mass[None] = 0.0
        self.projected_volume_raw[None] = 0.0
        self.projected_volume_clamped[None] = 0.0
        self.max_phi_raw[None] = 0.0
        self.active_cell_count[None] = 0

        for I in ti.grouped(lbm.rho):
            phi_raw = lbm.solid_phi[I]
            ti.atomic_max(self.max_phi_raw[None], phi_raw)

            if lbm.solid_mass[I] > self.eps_mass:
                lbm.solid_vel[I] = lbm.solid_vel[I] / lbm.solid_mass[I]
            else:
                lbm.solid_vel[I] = ti.Vector([0.0, 0.0, 0.0])

            phi_clamped = ti.min(1.0, ti.max(0.0, phi_raw))
            lbm.solid_phi[I] = phi_clamped

            if phi_clamped > 1.0e-8:
                ti.atomic_add(self.active_cell_count[None], 1)

            ti.atomic_add(self.projected_mass[None], lbm.solid_mass[I])
            ti.atomic_add(self.projected_volume_raw[None], phi_raw * self.cell_volume_norm)
            ti.atomic_add(self.projected_volume_clamped[None], phi_clamped * self.cell_volume_norm)

    def project(self, solid, lbm, clear=True):
        if clear:
            self.clear_projection(lbm)
        self.project_particles(solid, lbm)
        self.normalize_projection(lbm)

    def get_stats(self):
        """
        Diagnostic-only. Reads projection reductions back to Python for baseline validation.
        """
        return {
            "projected_mass": float(self.projected_mass[None]),
            "projected_volume_raw": float(self.projected_volume_raw[None]),
            "projected_volume_clamped": float(self.projected_volume_clamped[None]),
            "max_phi_raw": float(self.max_phi_raw[None]),
            "active_cell_count": int(self.active_cell_count[None]),
            "vel_scale_norm_to_lbm": float(self.vel_scale_norm_to_lbm),
            "cell_volume_norm": float(self.cell_volume_norm),
        }
