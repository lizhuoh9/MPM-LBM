import os
import time

import numpy as np
import taichi as ti


ti.init(arch=ti.gpu, default_fp=ti.f32)

DIM = 3
N_GRID = 32
STEPS = 50
DT = 4e-4

N_PARTICLES = N_GRID**DIM // 4
DX = 1.0 / N_GRID
INV_DX = 1.0 / DX

P_RHO = 1.0
P_VOL = (DX * 0.5) ** 3
P_MASS = P_VOL * P_RHO

GRAVITY = 9.8
BOUND = 3
E = 400.0

x = ti.Vector.field(DIM, ti.f32, shape=N_PARTICLES)
v = ti.Vector.field(DIM, ti.f32, shape=N_PARTICLES)
C = ti.Matrix.field(DIM, DIM, ti.f32, shape=N_PARTICLES)
J = ti.field(ti.f32, shape=N_PARTICLES)

grid_v = ti.Vector.field(DIM, ti.f32, shape=(N_GRID, N_GRID, N_GRID))
grid_m = ti.field(ti.f32, shape=(N_GRID, N_GRID, N_GRID))

min_y_stat = ti.field(ti.f32, shape=())
max_y_stat = ti.field(ti.f32, shape=())
max_speed_stat = ti.field(ti.f32, shape=())
min_j_stat = ti.field(ti.f32, shape=())


@ti.kernel
def init_particles():
    for p in range(N_PARTICLES):
        rx = ti.random(ti.f32)
        ry = ti.random(ti.f32)
        rz = ti.random(ti.f32)

        x[p] = ti.Vector(
            [
                0.25 + 0.3 * rx,
                0.35 + 0.3 * ry,
                0.25 + 0.3 * rz,
            ]
        )

        v[p] = ti.Vector([0.0, 0.0, 0.0])
        C[p] = ti.Matrix.zero(ti.f32, DIM, DIM)
        J[p] = 1.0


@ti.func
def inside_grid(I):
    return (
        0 <= I.x
        and I.x < N_GRID
        and 0 <= I.y
        and I.y < N_GRID
        and 0 <= I.z
        and I.z < N_GRID
    )


@ti.kernel
def substep():
    for I in ti.grouped(grid_m):
        grid_v[I] = ti.Vector([0.0, 0.0, 0.0])
        grid_m[I] = 0.0

    for p in x:
        Xp = x[p] * INV_DX
        base = ti.cast(Xp - 0.5, ti.i32)
        fx = Xp - ti.cast(base, ti.f32)

        w = [
            0.5 * (1.5 - fx) ** 2,
            0.75 - (fx - 1.0) ** 2,
            0.5 * (fx - 0.5) ** 2,
        ]

        stress = -DT * 4.0 * E * P_VOL * (J[p] - 1.0) * INV_DX * INV_DX
        affine = ti.Matrix.identity(ti.f32, DIM) * stress + P_MASS * C[p]

        for offset in ti.static(ti.grouped(ti.ndrange(3, 3, 3))):
            I = base + offset

            if inside_grid(I):
                dpos = (ti.cast(offset, ti.f32) - fx) * DX
                weight = w[offset.x].x * w[offset.y].y * w[offset.z].z

                ti.atomic_add(grid_v[I], weight * (P_MASS * v[p] + affine @ dpos))
                ti.atomic_add(grid_m[I], weight * P_MASS)

    for I in ti.grouped(grid_m):
        if grid_m[I] > 0.0:
            grid_v[I] = grid_v[I] / grid_m[I]
            grid_v[I].y -= DT * GRAVITY

            if I.x < BOUND and grid_v[I].x < 0:
                grid_v[I].x = 0
            if I.x > N_GRID - BOUND and grid_v[I].x > 0:
                grid_v[I].x = 0

            if I.y < BOUND and grid_v[I].y < 0:
                grid_v[I].y = 0
            if I.y > N_GRID - BOUND and grid_v[I].y > 0:
                grid_v[I].y = 0

            if I.z < BOUND and grid_v[I].z < 0:
                grid_v[I].z = 0
            if I.z > N_GRID - BOUND and grid_v[I].z > 0:
                grid_v[I].z = 0

    for p in x:
        Xp = x[p] * INV_DX
        base = ti.cast(Xp - 0.5, ti.i32)
        fx = Xp - ti.cast(base, ti.f32)

        w = [
            0.5 * (1.5 - fx) ** 2,
            0.75 - (fx - 1.0) ** 2,
            0.5 * (fx - 0.5) ** 2,
        ]

        new_v = ti.Vector([0.0, 0.0, 0.0])
        new_C = ti.Matrix.zero(ti.f32, DIM, DIM)

        for offset in ti.static(ti.grouped(ti.ndrange(3, 3, 3))):
            I = base + offset

            if inside_grid(I):
                dpos = (ti.cast(offset, ti.f32) - fx) * DX
                weight = w[offset.x].x * w[offset.y].y * w[offset.z].z
                g_v = grid_v[I]

                new_v += weight * g_v
                new_C += 4.0 * weight * g_v.outer_product(dpos) * INV_DX * INV_DX

        v[p] = new_v
        x[p] += DT * v[p]
        J[p] *= 1.0 + DT * new_C.trace()
        C[p] = new_C


@ti.kernel
def reduce_stats():
    min_y_stat[None] = 1e9
    max_y_stat[None] = -1e9
    max_speed_stat[None] = 0.0
    min_j_stat[None] = 1e9

    for p in x:
        ti.atomic_min(min_y_stat[None], x[p].y)
        ti.atomic_max(max_y_stat[None], x[p].y)
        ti.atomic_max(max_speed_stat[None], v[p].norm())
        ti.atomic_min(min_j_stat[None], J[p])


def main():
    out_dir = os.path.join("outputs", "mpm3d")
    os.makedirs(out_dir, exist_ok=True)

    init_particles()

    t0 = time.time()

    for step in range(STEPS + 1):
        substep()

        if step % 10 == 0:
            reduce_stats()
            min_y = float(min_y_stat[None])
            max_y = float(max_y_stat[None])
            max_speed = float(max_speed_stat[None])
            min_j = float(min_j_stat[None])

            print(
                f"step={step:04d}, "
                f"min_y={min_y:.6f}, max_y={max_y:.6f}, "
                f"max_speed={max_speed:.6e}, min_J={min_j:.6f}"
            )

            if not np.all(np.isfinite([min_y, max_y, max_speed, min_j])):
                raise RuntimeError("MPM stats contain NaN or Inf")

            if min_j <= 0.0:
                raise RuntimeError("MPM J became non-positive")

    pos = x.to_numpy()
    if not np.all(np.isfinite(pos)):
        raise RuntimeError("MPM particle positions contain NaN or Inf")

    output_path = os.path.join(out_dir, "mpm3d_positions.npy")
    np.save(output_path, pos)

    print(f"[OK] MPM 3D baseline finished in {time.time() - t0:.2f}s")
    print(f"[OK] particle positions saved to {output_path}")


if __name__ == "__main__":
    main()
