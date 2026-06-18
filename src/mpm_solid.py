import math
import os

import numpy as np
import taichi as ti

try:
    from .mpm_config import MPMConfig
except ImportError:
    from mpm_config import MPMConfig


@ti.data_oriented
class MPMSolid3D:
    def __init__(self, config: MPMConfig, n_particles: int):
        if n_particles <= 0:
            raise ValueError("n_particles must be positive")

        self.config = config
        self.dim = 3
        self.n_grid = config.n_grid
        self.dx = config.dx
        self.inv_dx = 1.0 / config.dx
        self.dt = config.dt
        self.n_particles = n_particles
        self.bound = config.bound
        self.use_apic = config.use_apic

        self.gravity_x, self.gravity_y, self.gravity_z = config.gravity
        self.box_min_x, self.box_min_y, self.box_min_z = config.box_min
        self.box_max_x, self.box_max_y, self.box_max_z = config.box_max

        self.young_modulus = config.young_modulus
        self.poisson_ratio = config.poisson_ratio
        self.mu = config.young_modulus / (2.0 * (1.0 + config.poisson_ratio))
        self.la = (
            config.young_modulus
            * config.poisson_ratio
            / ((1.0 + config.poisson_ratio) * (1.0 - 2.0 * config.poisson_ratio))
        )

        box_volume = (
            (self.box_max_x - self.box_min_x)
            * (self.box_max_y - self.box_min_y)
            * (self.box_max_z - self.box_min_z)
        )
        self.p_vol0 = box_volume / float(n_particles)
        self.p_mass0 = self.p_vol0 * config.p_rho
        self.particles_per_axis = max(1, math.ceil(n_particles ** (1.0 / 3.0)))

        self.x = ti.Vector.field(3, ti.f32, shape=n_particles)
        self.v = ti.Vector.field(3, ti.f32, shape=n_particles)
        self.C = ti.Matrix.field(3, 3, ti.f32, shape=n_particles)
        self.F = ti.Matrix.field(3, 3, ti.f32, shape=n_particles)
        self.Jp = ti.field(ti.f32, shape=n_particles)
        self.mass = ti.field(ti.f32, shape=n_particles)
        self.vol0 = ti.field(ti.f32, shape=n_particles)

        self.grid_v = ti.Vector.field(3, ti.f32, shape=(self.n_grid, self.n_grid, self.n_grid))
        self.grid_m = ti.field(ti.f32, shape=(self.n_grid, self.n_grid, self.n_grid))
        self.grid_f_ext = ti.Vector.field(3, ti.f32, shape=(self.n_grid, self.n_grid, self.n_grid))

        self.min_x = ti.Vector.field(3, ti.f32, shape=())
        self.max_x = ti.Vector.field(3, ti.f32, shape=())
        self.max_speed = ti.field(ti.f32, shape=())
        self.min_J = ti.field(ti.f32, shape=())
        self.max_J = ti.field(ti.f32, shape=())
        self.total_mass = ti.field(ti.f32, shape=())

    @ti.func
    def inside_grid(self, I):
        return (
            0 <= I.x
            and I.x < self.n_grid
            and 0 <= I.y
            and I.y < self.n_grid
            and 0 <= I.z
            and I.z < self.n_grid
        )

    @ti.func
    def apply_boundary_at_node(self, I):
        if I.x < self.bound and self.grid_v[I].x < 0.0:
            self.grid_v[I].x = 0.0
        if I.x > self.n_grid - self.bound and self.grid_v[I].x > 0.0:
            self.grid_v[I].x = 0.0

        if I.y < self.bound and self.grid_v[I].y < 0.0:
            self.grid_v[I].y = 0.0
        if I.y > self.n_grid - self.bound and self.grid_v[I].y > 0.0:
            self.grid_v[I].y = 0.0

        if I.z < self.bound and self.grid_v[I].z < 0.0:
            self.grid_v[I].z = 0.0
        if I.z > self.n_grid - self.bound and self.grid_v[I].z > 0.0:
            self.grid_v[I].z = 0.0

    @ti.func
    def clamp_particle_to_domain(self, p):
        eps = self.dx
        for d in ti.static(range(3)):
            if self.x[p][d] < eps:
                self.x[p][d] = eps
                if self.v[p][d] < 0.0:
                    self.v[p][d] = 0.0
            if self.x[p][d] > 1.0 - eps:
                self.x[p][d] = 1.0 - eps
                if self.v[p][d] > 0.0:
                    self.v[p][d] = 0.0

    @ti.kernel
    def init_box(self):
        ppa = self.particles_per_axis
        span = ti.Vector(
            [
                self.box_max_x - self.box_min_x,
                self.box_max_y - self.box_min_y,
                self.box_max_z - self.box_min_z,
            ]
        )
        box_min = ti.Vector([self.box_min_x, self.box_min_y, self.box_min_z])

        for p in range(self.n_particles):
            ix = p % ppa
            iy = (p // ppa) % ppa
            iz = (p // (ppa * ppa)) % ppa
            denom = ti.max(1, ppa - 1)
            local = ti.Vector(
                [
                    (ti.cast(ix, ti.f32) + 0.5) / ti.cast(denom + 1, ti.f32),
                    (ti.cast(iy, ti.f32) + 0.5) / ti.cast(denom + 1, ti.f32),
                    (ti.cast(iz, ti.f32) + 0.5) / ti.cast(denom + 1, ti.f32),
                ]
            )

            self.x[p] = box_min + span * local
            self.v[p] = ti.Vector([0.0, 0.0, 0.0])
            self.C[p] = ti.Matrix.zero(ti.f32, 3, 3)
            self.F[p] = ti.Matrix.identity(ti.f32, 3)
            self.Jp[p] = 1.0
            self.mass[p] = self.p_mass0
            self.vol0[p] = self.p_vol0

    @ti.kernel
    def reset_deformation_state(self):
        for p in range(self.n_particles):
            self.C[p] = ti.Matrix.zero(ti.f32, 3, 3)
            self.F[p] = ti.Matrix.identity(ti.f32, 3)
            self.Jp[p] = 1.0

    def init_from_numpy(self, x_np, vol0_np, mass_np, v_np=None):
        x_arr = np.asarray(x_np, dtype=np.float32)
        vol_arr = np.asarray(vol0_np, dtype=np.float32)
        mass_arr = np.asarray(mass_np, dtype=np.float32)

        if x_arr.shape != (self.n_particles, 3):
            raise ValueError(f"x_np must have shape ({self.n_particles}, 3)")
        if vol_arr.shape != (self.n_particles,):
            raise ValueError(f"vol0_np must have shape ({self.n_particles},)")
        if mass_arr.shape != (self.n_particles,):
            raise ValueError(f"mass_np must have shape ({self.n_particles},)")
        if v_np is None:
            v_arr = np.zeros_like(x_arr, dtype=np.float32)
        else:
            v_arr = np.asarray(v_np, dtype=np.float32)
            if v_arr.shape != (self.n_particles, 3):
                raise ValueError(f"v_np must have shape ({self.n_particles}, 3)")

        if not np.all(np.isfinite(x_arr)):
            raise ValueError("x_np must be finite")
        if not np.all(np.isfinite(v_arr)):
            raise ValueError("v_np must be finite")
        if not np.all(np.isfinite(vol_arr)) or np.any(vol_arr <= 0.0):
            raise ValueError("vol0_np must be finite and positive")
        if not np.all(np.isfinite(mass_arr)) or np.any(mass_arr <= 0.0):
            raise ValueError("mass_np must be finite and positive")

        self.x.from_numpy(x_arr)
        self.v.from_numpy(v_arr)
        self.vol0.from_numpy(vol_arr)
        self.mass.from_numpy(mass_arr)
        self.reset_deformation_state()

    @ti.kernel
    def clear_grid(self):
        for I in ti.grouped(self.grid_m):
            self.grid_v[I] = ti.Vector([0.0, 0.0, 0.0])
            self.grid_m[I] = 0.0
            self.grid_f_ext[I] = ti.Vector([0.0, 0.0, 0.0])

    @ti.kernel
    def p2g(self):
        for p in range(self.n_particles):
            Xp = self.x[p] * self.inv_dx
            base = ti.cast(Xp - 0.5, ti.i32)
            fx = Xp - ti.cast(base, ti.f32)

            w = [
                0.5 * (1.5 - fx) ** 2,
                0.75 - (fx - 1.0) ** 2,
                0.5 * (fx - 0.5) ** 2,
            ]

            Fp = self.F[p]
            U, sig, V = ti.svd(Fp)
            R = U @ V.transpose()
            J = Fp.determinant()
            self.Jp[p] = J

            P = 2.0 * self.mu * (Fp - R) + self.la * (J - 1.0) * J * Fp.inverse().transpose()
            stress = -self.dt * self.vol0[p] * P @ Fp.transpose() * self.inv_dx * self.inv_dx
            affine = stress + self.mass[p] * self.C[p]

            for offset in ti.static(ti.grouped(ti.ndrange(3, 3, 3))):
                I = base + offset
                if self.inside_grid(I):
                    dpos = (ti.cast(offset, ti.f32) - fx) * self.dx
                    weight = w[offset.x].x * w[offset.y].y * w[offset.z].z
                    momentum = self.mass[p] * self.v[p] + affine @ dpos
                    ti.atomic_add(self.grid_v[I], weight * momentum)
                    ti.atomic_add(self.grid_m[I], weight * self.mass[p])

    @ti.kernel
    def grid_update(self):
        gravity = ti.Vector([self.gravity_x, self.gravity_y, self.gravity_z])
        for I in ti.grouped(self.grid_m):
            if self.grid_m[I] > 0.0:
                self.grid_v[I] = self.grid_v[I] / self.grid_m[I]
                self.grid_v[I] += self.dt * gravity
                self.grid_v[I] += self.dt * self.grid_f_ext[I] / self.grid_m[I]
                self.apply_boundary_at_node(I)

    @ti.kernel
    def g2p(self):
        for p in range(self.n_particles):
            Xp = self.x[p] * self.inv_dx
            base = ti.cast(Xp - 0.5, ti.i32)
            fx = Xp - ti.cast(base, ti.f32)

            w = [
                0.5 * (1.5 - fx) ** 2,
                0.75 - (fx - 1.0) ** 2,
                0.5 * (fx - 0.5) ** 2,
            ]

            new_v = ti.Vector([0.0, 0.0, 0.0])
            new_C = ti.Matrix.zero(ti.f32, 3, 3)

            for offset in ti.static(ti.grouped(ti.ndrange(3, 3, 3))):
                I = base + offset
                if self.inside_grid(I):
                    dpos = (ti.cast(offset, ti.f32) - fx) * self.dx
                    weight = w[offset.x].x * w[offset.y].y * w[offset.z].z
                    g_v = self.grid_v[I]

                    new_v += weight * g_v
                    new_C += 4.0 * weight * g_v.outer_product(dpos) * self.inv_dx * self.inv_dx

            self.v[p] = new_v
            self.x[p] += self.dt * new_v
            self.clamp_particle_to_domain(p)
            self.C[p] = new_C
            self.F[p] = (ti.Matrix.identity(ti.f32, 3) + self.dt * new_C) @ self.F[p]
            self.Jp[p] = self.F[p].determinant()

    def substep(self):
        self.clear_grid()
        self.p2g()
        self.grid_update()
        self.g2p()

    @ti.kernel
    def set_uniform_velocity(self, vx: ti.f32, vy: ti.f32, vz: ti.f32):
        for p in range(self.n_particles):
            self.v[p] = ti.Vector([vx, vy, vz])

    @ti.kernel
    def reduce_stats(self):
        self.min_x[None] = ti.Vector([1.0e9, 1.0e9, 1.0e9])
        self.max_x[None] = ti.Vector([-1.0e9, -1.0e9, -1.0e9])
        self.max_speed[None] = 0.0
        self.min_J[None] = 1.0e9
        self.max_J[None] = -1.0e9
        self.total_mass[None] = 0.0

        for p in range(self.n_particles):
            for d in ti.static(range(3)):
                ti.atomic_min(self.min_x[None][d], self.x[p][d])
                ti.atomic_max(self.max_x[None][d], self.x[p][d])
            ti.atomic_max(self.max_speed[None], self.v[p].norm())
            ti.atomic_min(self.min_J[None], self.Jp[p])
            ti.atomic_max(self.max_J[None], self.Jp[p])
            ti.atomic_add(self.total_mass[None], self.mass[p])

    def get_stats(self):
        """
        Diagnostic-only. This reads small reductions back to Python for baseline validation.
        """
        self.reduce_stats()
        min_x = self.min_x[None].to_numpy()
        max_x = self.max_x[None].to_numpy()
        return {
            "min_x": tuple(float(v) for v in min_x),
            "max_x": tuple(float(v) for v in max_x),
            "min_y": float(min_x[1]),
            "max_y": float(max_x[1]),
            "max_speed": float(self.max_speed[None]),
            "min_J": float(self.min_J[None]),
            "max_J": float(self.max_J[None]),
            "total_mass": float(self.total_mass[None]),
        }

    def export_particles(self, out_dir: str, prefix: str = "particles"):
        os.makedirs(out_dir, exist_ok=True)
        x_np = self.x.to_numpy()
        v_np = self.v.to_numpy()
        F_np = self.F.to_numpy()
        J_np = self.Jp.to_numpy()

        np.save(os.path.join(out_dir, f"{prefix}_x.npy"), x_np)
        np.save(os.path.join(out_dir, f"{prefix}_v.npy"), v_np)
        np.save(os.path.join(out_dir, f"{prefix}_F.npy"), F_np)
        np.save(os.path.join(out_dir, f"{prefix}_J.npy"), J_np)

    def export_particles_ply(self, frame: int, path: str):
        pos = self.x.to_numpy()
        writer = ti.tools.PLYWriter(num_vertices=self.n_particles)
        writer.add_vertex_pos(pos[:, 0], pos[:, 1], pos[:, 2])
        writer.export_frame(frame, path)
