# Performance and Memory

Step 12 estimates dense-grid memory and records timing baselines.
Step 12 does not implement optimization or new solver physics.

## Scope

The purpose is resource governance:

- estimate memory lower bounds for dense LBM and MPM fields
- record a lightweight profile matrix for `none`, `penalty`, and `moving_boundary`
- preserve the Step 10 mode matrix while preparing for larger future cases

The estimates are not measured GPU allocation. They exclude Taichi runtime overhead, allocator overhead, kernel metadata, and temporary compiler/runtime buffers.

## Dense-Grid Memory Model

### LBM Estimate Fields

The LBM dense-field model counts:

```text
f: 19 floats / cell
F: 19 floats / cell
rho: 1 float / cell
v: 3 floats / cell
solid_phi: 1 float / cell
solid_mass: 1 float / cell
solid_vel: 3 floats / cell
cell_force: 3 floats / cell
hydro_force: 3 floats / cell
solid/static_solid/old_solid/reinit_flag: 4 int8 / cell
```

The lower-bound estimate is:

```text
LBM bytes = n_grid^3 * (53 * dtype_bytes + 4)
```

### MPM Particle Estimate Fields

The MPM particle model counts:

```text
x: 3 floats / particle
v: 3 floats / particle
C: 9 floats / particle
F: 9 floats / particle
Jp: 1 float / particle
mass: 1 float / particle
vol0: 1 float / particle
```

The lower-bound estimate is:

```text
MPM particle bytes = n_particles * 27 * dtype_bytes
```

### MPM Grid Estimate Fields

The MPM grid model counts:

```text
grid_v: 3 floats / node
grid_m: 1 float / node
grid_f_ext: 3 floats / node
```

The lower-bound estimate is:

```text
MPM grid bytes = n_grid^3 * 7 * dtype_bytes
```

### Coupling Estimate Assumptions

Projection fields are counted inside the LBM estimate. Current coupling diagnostics are scalar or reuse LBM/MPM fields, so additional coupling memory is treated as negligible relative to dense grid fields.

## Current Baseline Scale

Current Step 12 profile baselines use:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
```

## Scaling Warning

The 128^3 estimate is reported for planning. It is not a promise that the current GPU can run that case. At 128^3 and larger, dense-field memory, Taichi runtime overhead, and output volume should be reviewed before launching long simulations.

## Profile Matrix

The Step 12 profile matrix runs the same `FSIDriver3D` modes with VTK and particle exports disabled:

```text
none
penalty
moving_boundary
```

The profile matrix records total time, initialization, projection, coupling, LBM stepping, MPM substepping, diagnostics, and export overhead. These timings are environment-specific regression signals, not hardware-independent benchmarks.

## Step 14 Larger-Grid Results

Step 14 adds 48^3 engineering scale baseline rows and 64^3 short feasibility rows. Step 14 does not add new FSI physics, and these timings are not production benchmark data.

| case | mode | n_grid | n_particles | total_estimated_mb | total_time_s | rho_min | rho_max |
| ---- | ---- | -----: | ----------: | -----------------: | -----------: | ------: | ------: |
| box 48^3 | none | 48 | 13824 | 27.158203 | 44.333 | 1.000000358 | 1.000000358 |
| box 48^3 | penalty | 48 | 13824 | 27.158203 | 45.785 | 0.999991417 | 1.000009537 |
| box 48^3 | moving_boundary | 48 | 13824 | 27.158203 | 70.848 | 0.982743502 | 1.039551854 |
| squid_proxy 48^3 | none | 48 | 4096 | 26.156250 | 69.284 | 1.000000358 | 1.000000358 |
| squid_proxy 48^3 | penalty | 48 | 4096 | 26.156250 | 91.868 | 0.999996662 | 1.000004530 |
| squid_proxy 48^3 | moving_boundary | 48 | 4096 | 26.156250 | 95.615 | 0.990947962 | 1.012312770 |
| box 64^3 feasibility | none | 64 | 32768 | 64.375000 | 155.620 | 1.000000358 | 1.000000358 |
| box 64^3 feasibility | penalty | 64 | 32768 | 64.375000 | 178.103 | 0.999998331 | 1.000002623 |

The 64^3 rows are feasibility checks, not full validation. The lower-bound memory estimates still exclude Taichi runtime allocation, allocator overhead, temporary buffers, and optional visualization export.

## Step 15 Calibration Runtime Notes

Step 15 calibration rows are environment-specific regression data, not hardware-independent timing results. The committed Step 15 runs keep `write_vtk = false` and `write_particles = false` for required calibration configs.

Observed wall times in this Windows/Taichi GPU environment:

| case | rows | total time s | note |
| ---- | ---: | -----------: | ---- |
| momentum accounting sanity | 1 | 48.50 | 32^3 box, 10 LBM steps |
| reaction_scale sweep | 4 | 656.89 | 32^3 box, 20 LBM steps each |
| force_cap_norm sweep | 4 | 834.13 | 48^3 box, 10 LBM steps each |
| squid_proxy calibrated window | 4 | 423.49 | 48^3 procedural proxy, 10 LBM steps each |
| calibrated-vs-original comparison | 2 | 138.75 | 48^3 box comparison |
