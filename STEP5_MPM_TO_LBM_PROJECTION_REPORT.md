# Step 5 MPM-to-LBM Projection Report

## 1. Goal

Step 5 projects MPM solid particles into LBM grid fields:

```text
solid_phi
solid_mass
solid_vel
```

This step does not implement FSI. It does not compute fluid response, `cell_force`, `hydro_force`, penalty force, momentum exchange, moving bounce-back, or immersed boundary coupling.

## 2. Files Created Or Updated

Created:

```text
src/projection.py
baseline_tests/run_step5_projection_static_block.py
baseline_tests/run_step5_projection_moving_block.py
baseline_tests/run_step5_projection_after_mpm_motion.py
baseline_tests/run_step5_dynamic_solid_mask_dryrun.py
tests/test_step5_projection_contract.py
logs/step5_projection_static.log
logs/step5_projection_moving.log
logs/step5_projection_motion.log
logs/step5_dynamic_solid_mask.log
outputs/step5_projection_static/LBMProjection_0.vtr
outputs/step5_projection_static/solid_phi.npy
outputs/step5_projection_static/solid_mass.npy
outputs/step5_projection_static/solid_vel.npy
outputs/step5_projection_static/particles_x.npy
outputs/step5_projection_moving/LBMProjection_0.vtr
outputs/step5_projection_moving/solid_phi.npy
outputs/step5_projection_moving/solid_mass.npy
outputs/step5_projection_moving/solid_vel.npy
outputs/step5_projection_moving/particles_x.npy
outputs/step5_projection_motion/LBMProjection_0.vtr
outputs/step5_projection_motion/LBMProjection_1.vtr
outputs/step5_projection_motion/solid_phi_0.npy
outputs/step5_projection_motion/solid_phi_1.npy
outputs/step5_projection_motion/solid_mass_0.npy
outputs/step5_projection_motion/solid_mass_1.npy
outputs/step5_projection_motion/solid_vel_0.npy
outputs/step5_projection_motion/solid_vel_1.npy
outputs/step5_dynamic_solid_mask/LBMProjection_mask_on.vtr
outputs/step5_dynamic_solid_mask/LBMProjection_mask_off.vtr
outputs/step5_dynamic_solid_mask/solid_on.npy
outputs/step5_dynamic_solid_mask/solid_off.npy
```

Updated:

```text
src/__init__.py
src/lbm_fluid.py
```

## 3. Projection Convention

The projector uses the same normalized cubic domain as Step 4:

```text
n_grid = 32
dx_norm = 0.03125
mpm_dt = 0.0004
mpm_substeps_per_lbm_step = 10
lbm_dt_phys = 0.004
vel_scale_norm_to_lbm = 0.128
```

Spatial projection uses the MPM-style quadratic 3x3x3 stencil:

```text
Xp = x_norm / dx_norm
base = int(Xp - 0.5)
fx = Xp - base
weight = wx * wy * wz
```

Volume fraction:

```text
current_volume = vol0 * max(Jp, 0)
solid_phi += weight * current_volume / dx_norm^3
solid_phi is clamped to [0, 1]
```

Mass:

```text
solid_mass += weight * mass
```

Velocity:

```text
solid_vel += weight * mass * v_lbm
solid_vel /= solid_mass
```

Diagnostics recorded:

```text
projected_mass
projected_volume_raw
projected_volume_clamped
max_phi_raw
active_cell_count
```

## 4. Velocity Unit Conversion

MPM velocity is normalized velocity. LBM `solid_vel` must be lattice velocity.

Formula:

```text
v_lbm = v_norm * lbm_dt_phys / dx_norm
v_norm = v_lbm * dx_norm / lbm_dt_phys
```

Moving baseline values:

```text
target_u_lbm = (0.03, 0.0, 0.0)
target_u_norm = (0.234375, 0.0, 0.0)
vel_scale_norm_to_lbm = 0.128
projected_mean_solid_vel = [0.03000006452202797, 0.0, 0.0]
```

## 5. Static Block Projection

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step5_projection_static_block.py
```

Log:

```text
logs/step5_projection_static.log
```

Result:

```text
[Taichi] Starting on arch=cuda
projected_mass=2.699997649e-02
total_particle_mass=2.700000256e-02
relative_mass_error=9.658159116e-07
projected_volume_raw=2.699996531e-02
projected_volume_clamped=2.696326375e-02
max_phi_raw=1.024193168e+00
active_cell_count=1584
solid_phi_min=0.000000000e+00
solid_phi_max=1.000000000e+00
max_solid_speed_lbm=0.000000000e+00
cell_force_max_norm=0.000000e+00
hydro_force_max_norm=0.000000e+00
[OK] Step 5 static block projection baseline finished
```

## 6. Moving Block Velocity Projection

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step5_projection_moving_block.py
```

Log:

```text
logs/step5_projection_moving.log
```

Result:

```text
[Taichi] Starting on arch=cuda
target_u_lbm=(0.03, 0.0, 0.0)
target_u_norm=(0.234375, 0.0, 0.0)
projected_mean_solid_vel=[0.03000006452202797, 0.0, 0.0]
velocity_error=[6.452202797047057e-08, 0.0, 0.0]
relative_mass_error=6.898685083e-07
active_cell_count=1584
cell_force_max_norm=0.000000e+00
hydro_force_max_norm=0.000000e+00
[OK] Step 5 moving block velocity projection baseline finished
```

## 7. Projection After MPM Motion

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step5_projection_after_mpm_motion.py
```

Log:

```text
logs/step5_projection_motion.log
```

Result:

```text
[Taichi] Starting on arch=cuda
target_u_lbm=(0.02, 0.0, 0.0)
target_u_norm=(0.15625, 0.0, 0.0)
mpm_substeps=50
center_x_initial=4.000000358e-01
center_x_final=4.031250775e-01
index_min_initial=[8, 11, 8]
index_max_initial=[17, 20, 17]
index_min_final=[8, 11, 8]
index_max_final=[17, 20, 17]
active_cell_count_initial=1584
active_cell_count_final=1584
relative_mass_error_initial=9.658159116e-07
relative_mass_error_final=6.898685083e-08
cell_force_max_norm=0.000000e+00
hydro_force_max_norm=0.000000e+00
[OK] Step 5 projection after MPM motion baseline finished
```

## 8. Dynamic Solid Mask Dry Run

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step5_dynamic_solid_mask_dryrun.py
```

Log:

```text
logs/step5_dynamic_solid_mask.log
```

Result:

```text
[Taichi] Starting on arch=cuda
threshold=0.500000
active_cell_count=1584
solid_on_count=787
solid_off_count=0
reinit_after_on_count=0
reinit_count=787
rho_min=1.000000000e+00
rho_max=1.000000000e+00
velocity_max=0.000000000e+00
cell_force_max_norm=0.000000e+00
hydro_force_max_norm=0.000000e+00
[OK] Step 5 dynamic solid mask dry run finished
```

This dry run calls only:

```text
lbm.update_dynamic_solid()
lbm.reinitialize_new_fluid_cells()
```

It does not call `lbm.step()`.

## 9. Explicit Non-Goal Confirmation

Step 5 does not implement:

```text
cell_force from MPM
hydro_force
penalty force
momentum exchange
moving bounce-back
immersed boundary
LBM fluid response to solid
two-phase flow
ReducedSquidFSI
real squid geometry
edits to external/taichi_LBM3D
```

`cell_force` and `hydro_force` are read only to verify that they remain zero.

## 10. Hard Acceptance Checklist

- [x] main is on the Step 5 final commit
- [x] `src/projection.py` exists
- [x] `src/__init__.py` exports `MPMToLBMProjector3D`
- [x] `LBMFluid3D.init_geo()` dtype cleanup is applied
- [x] `MPMToLBMProjector3D.clear_projection()` clears `solid_phi`, `solid_mass`, `solid_vel`
- [x] `MPMToLBMProjector3D.project_particles()` writes `solid_phi`
- [x] `MPMToLBMProjector3D.project_particles()` writes `solid_mass`
- [x] `MPMToLBMProjector3D.project_particles()` writes `solid_vel`
- [x] solid velocity uses normalized-to-LBM lattice velocity scaling
- [x] volume fraction uses `current_volume = vol0 * Jp`
- [x] `solid_phi` is clamped to `[0, 1]`
- [x] projected raw/clamped volume diagnostics are recorded
- [x] static block projection baseline passes
- [x] moving block velocity projection baseline passes
- [x] projection after MPM motion baseline passes
- [x] dynamic solid mask dry-run baseline passes
- [x] projected_mass relative error < 1e-5 in required baselines
- [x] static block projected `solid_vel` is approximately zero
- [x] moving block projected `solid_vel` matches `target_u_lbm`
- [x] particle `center_x` increases after motion baseline
- [x] active_cell_count > 0
- [x] `solid_phi` finite
- [x] `solid_mass` finite
- [x] `solid_vel` finite
- [x] no NaN
- [x] no Inf
- [x] `cell_force` remains zero
- [x] `hydro_force` remains zero
- [x] no penalty force is implemented
- [x] no momentum exchange is implemented
- [x] no moving bounce-back is implemented
- [x] no FSI force coupling is implemented
- [x] logs are saved under `logs/`
- [x] outputs are saved under `outputs/`
- [x] `STEP5_MPM_TO_LBM_PROJECTION_REPORT.md` is complete
- [x] `pytest -q` passes

## 11. Decision

Can proceed to Step 6?

- [x] Yes

Step 6 may build force coupling on top of the validated projection fields. It should continue to treat Step 5 as projection-only evidence, not as proof of FSI.
