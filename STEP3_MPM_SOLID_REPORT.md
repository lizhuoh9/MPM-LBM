# Step 3 MPM Solid Report

## 1. Goal

Implement an independent 3D MPM solid backend without connecting it to `LBMFluid3D` and without implementing FSI.

Step 3 result:

```text
src/mpm_config.py
src/mpm_solid.py
baseline_tests/run_mpm_rest_block.py
baseline_tests/run_mpm_falling_block.py
baseline_tests/run_mpm_elastic_block.py
```

This step proves that the solid solver alone can initialize a 3D block, execute P2G/grid update/G2P, update deformation gradient `F`, compute `J = det(F)`, apply gravity and boundaries, and export particle diagnostics.

## 2. Step 2 Preflight Cleanup

- [x] Step 2 i8 warning cleanup implemented
- [x] `LBMFluid3D.get_stats()` diagnostic-only comment/docstring added

Changes:

```text
src/lbm_fluid.py now casts dynamic-solid i8 assignments with ti.cast(..., ti.i8).
src/lbm_fluid.py documents get_stats() as diagnostic-only because it copies Taichi fields to NumPy.
```

Verification:

```powershell
cmd /c ""D:\working\taichi\env\python.exe" baseline_tests\run_lbm_refactored_dynamic_solid_dummy.py > logs\step2_lbm_refactor_dynamic_solid.log 2>&1"
```

Result:

```text
[OK] Step 2 dynamic-solid dummy baseline finished.
No "Assign may lose precision: i8 <- i32" warning remains in logs/step2_lbm_refactor_dynamic_solid.log.
```

## 3. MPMConfig Summary

`src/mpm_config.py` defines:

```text
n_grid, dx, dt
gravity
p_rho, particles_per_cell
young_modulus, poisson_ratio
bound, use_apic
box_min, box_max
output_interval
```

The default `dt=4.0e-4` and `n_grid=32` follow the Step 1 MPM smoke baseline scale.

## 4. MPMSolid3D Summary

`src/mpm_solid.py` defines `MPMSolid3D` with:

```text
particle fields:
  x, v, C, F, Jp, mass, vol0

grid fields:
  grid_v, grid_m, grid_f_ext

diagnostics:
  min_x, max_x, max_speed, min_J, max_J, total_mass
```

Implemented methods:

```text
init_box()
clear_grid()
p2g()
grid_update()
g2p()
substep()
get_stats()
export_particles()
export_particles_ply()
```

`grid_f_ext` is present only as a Step 3 placeholder. No LBM data is connected.

## 5. Material Model

Material model used:

```text
fixed-corotated elasticity
```

The P2G stress path uses:

```text
U, sig, V = ti.svd(F)
R = U @ V.transpose()
J = det(F)
P = 2 * mu * (F - R) + lambda * (J - 1) * J * F^{-T}
stress = -dt * vol0 * P @ F.transpose() * inv_dx^2
affine = stress + mass * C
```

No scalar-J fallback was used for the completed baselines.

## 6. Rest Block Baseline

Command:

```powershell
cmd /c ""D:\working\taichi\env\python.exe" baseline_tests\run_mpm_rest_block.py > logs\step3_mpm_rest_block.log 2>&1"
```

Settings:

```text
gravity = (0, 0, 0)
steps = 100
n_particles = 4096
```

Result:

```text
[OK] Step 3 MPM rest block baseline finished.
step=0100
initial_min_y = 0.359375
final_min_y = 0.359375
max_speed = 0.000000e+00
min_J = 1.000000
max_J = 1.000000
total_mass = 2.700039e-02
```

Outputs:

```text
outputs/mpm_rest_block/particles_x.npy
outputs/mpm_rest_block/particles_v.npy
outputs/mpm_rest_block/particles_F.npy
outputs/mpm_rest_block/particles_J.npy
```

## 7. Falling Block Baseline

Command:

```powershell
cmd /c ""D:\working\taichi\env\python.exe" baseline_tests\run_mpm_falling_block.py > logs\step3_mpm_falling_block.log 2>&1"
```

Settings:

```text
gravity = (0, -9.8, 0)
steps = 100
n_particles = 4096
```

Result:

```text
[OK] Step 3 MPM falling block baseline finished.
step=0100
initial_min_y = 0.359375
final_min_y = 0.351457
initial_max_speed = 0.000000e+00
final_max_speed = 3.920040e-01
min_J = 1.000000
max_J = 1.000000
total_mass = 2.700039e-02
```

Outputs:

```text
outputs/mpm_falling_block/particles_x.npy
outputs/mpm_falling_block/particles_v.npy
outputs/mpm_falling_block/particles_F.npy
outputs/mpm_falling_block/particles_J.npy
```

## 8. Elastic Block Baseline

Command:

```powershell
cmd /c ""D:\working\taichi\env\python.exe" baseline_tests\run_mpm_elastic_block.py > logs\step3_mpm_elastic_block.log 2>&1"
```

Settings:

```text
gravity = (0, -9.8, 0)
steps = 300
n_particles = 4096
box_min = (0.35, 0.12, 0.35)
box_max = (0.65, 0.42, 0.65)
```

Result:

```text
[OK] Step 3 MPM elastic block baseline finished.
step=0300
initial_min_y = 0.129375
final_min_y = 0.086393
min_y_seen = 0.086393
boundary_zone = 0.125000
final_max_speed = 3.946655e-01
min_J_seen = 0.778176
max_J_seen = 1.000039
final_min_J = 0.778176
final_max_J = 0.999240
total_mass = 2.700039e-02
```

Outputs:

```text
outputs/mpm_elastic_block/particles_x.npy
outputs/mpm_elastic_block/particles_v.npy
outputs/mpm_elastic_block/particles_F.npy
outputs/mpm_elastic_block/particles_J.npy
```

## 9. Known Issues

- The first MPM baseline in a fresh Python process spends most time compiling Taichi kernels. Subsequent MPM baselines run much faster in this environment.
- Particle initialization is deterministic lattice sampling inside the configured box, not mesh-based solid geometry. Real squid geometry remains out of scope for Step 3.
- `get_stats()` and `export_particles()` are diagnostic paths that copy data back to NumPy. They are acceptable for baselines and reports, but should not be called every production step in large coupled runs.
- `grid_f_ext` is a placeholder only; it is cleared to zero in Step 3 baselines and is not connected to LBM.

## 10. Hard Acceptance Checklist

- [x] Step 2 i8 warning cleanup implemented
- [x] `LBMFluid3D.get_stats()` diagnostic-only comment/docstring added
- [x] `src/mpm_config.py` exists
- [x] `src/mpm_solid.py` exists
- [x] `src/__init__.py` exports `MPMConfig` and `MPMSolid3D`
- [x] `MPMSolid3D` can initialize
- [x] `init_box()` generates a 3D solid block
- [x] `clear_grid()` runs
- [x] `p2g()` runs
- [x] `grid_update()` runs
- [x] `g2p()` runs
- [x] `substep()` runs
- [x] `F[p]` initializes to identity
- [x] `J = det(F)` is computed and exported/statistically reported
- [x] Gravity can be disabled for rest block
- [x] Gravity can be enabled for falling/elastic blocks
- [x] Grid boundary prevents unbounded domain escape
- [x] Rest block baseline completes
- [x] Falling block baseline completes
- [x] Elastic block baseline completes
- [x] Logs are saved under `logs/`
- [x] Outputs are saved under `outputs/`
- [x] Particle x/v/F/J `.npy` outputs exist for each baseline
- [x] `STEP3_MPM_SOLID_REPORT.md` is complete
- [x] `pytest` passes

Numerical hard limits:

- [x] no NaN
- [x] no Inf
- [x] `min_J > 0`
- [x] `max_speed < 10`
- [x] particle positions remain finite
- [x] particles remain inside `[0, 1]^3` or are boundary-limited with documented clamping

## 11. Decision

Can proceed to Step 4?

- [x] Yes
- [ ] No

Step 3 is complete as a standalone MPM solid backend. It does not claim real FSI.
