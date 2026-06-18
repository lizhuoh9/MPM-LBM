# Step 4 Units, Grid, and Timestep Report

## 1. Goal

Step 4 implements the shared units, grid, and timestep scaffold for independent LBM and MPM solvers. It proves that `LBMFluid3D` and `MPMSolid3D` can be created from one cubic normalized-domain configuration and advanced in one dummy loop without MPM-to-LBM projection or FSI force coupling.

This is not an FSI implementation. It only prepares the coordinate, unit, and timestep convention required before Step 5 projection work.

## 2. Files Created Or Updated

Created:

```text
src/sim_config.py
src/units.py
baseline_tests/run_step4_units_consistency.py
baseline_tests/run_step4_shared_domain.py
baseline_tests/run_step4_time_sync_dummy.py
tests/test_step4_units_grid_timestep_contract.py
logs/step4_units_consistency.log
logs/step4_shared_domain.log
logs/step4_time_sync_dummy.log
outputs/step4_shared_domain/particle_lbm_indices.npy
outputs/step4_shared_domain/particles_x.npy
outputs/step4_time_sync_dummy/LBMFluid_20.vtr
outputs/step4_time_sync_dummy/particles_x.npy
outputs/step4_time_sync_dummy/particles_v.npy
outputs/step4_time_sync_dummy/particles_F.npy
outputs/step4_time_sync_dummy/particles_J.npy
```

Updated:

```text
src/__init__.py
src/mpm_solid.py
```

## 3. Chosen Convention

Step 4 uses a cubic normalized domain only:

```text
n_grid = 32
domain_length = 1.0
dx_norm = 0.03125
mpm_dt = 0.0004
mpm_substeps_per_lbm_step = 10
lbm_dt_phys = 0.004
lbm_niu = 0.1
lbm_rho0 = 1.0
```

`UnifiedSimConfig` enforces:

```text
nx = ny = nz = n_grid
dx_norm = domain_length / n_grid
lbm_dt_phys = mpm_substeps_per_lbm_step * mpm_dt
```

## 4. Conversion Formulas

Position:

```text
x_lbm = x_norm / dx_norm
x_norm = x_lbm * dx_norm
i = floor(x_norm / dx_norm)
x_center_norm = (i + 0.5) * dx_norm
```

Velocity:

```text
u_lbm = u_norm * lbm_dt_phys / dx_norm
u_norm = u_lbm * dx_norm / lbm_dt_phys
```

Acceleration:

```text
a_lbm = a_norm * lbm_dt_phys^2 / dx_norm
a_norm = a_lbm * dx_norm / lbm_dt_phys^2
```

Viscosity:

```text
nu_lbm = nu_norm * lbm_dt_phys / dx_norm^2
nu_norm = nu_lbm * dx_norm^2 / lbm_dt_phys
```

Default examples from `logs/step4_units_consistency.log`:

```text
u_lbm=0.03 -> u_norm=0.234375
a_norm=9.8 -> a_lbm=0.0050176
niu_lbm=0.1 -> nu_norm=0.02441406
```

## 5. Unit Consistency Command And Result

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step4_units_consistency.py
```

Log:

```text
logs/step4_units_consistency.log
```

Result:

```text
position_coord_round_trip: max_abs_error=0.000000e+00
velocity_round_trip: max_abs_error=0.000000e+00
acceleration_round_trip: max_abs_error=0.000000e+00
viscosity_round_trip: max_abs_error=0.000000e+00
[OK] Step 4 units consistency baseline finished
```

## 6. Shared Domain Command And Result

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step4_shared_domain.py
```

Log:

```text
logs/step4_shared_domain.log
```

Result:

```text
[Taichi] Starting on arch=cuda
lbm_shape=(32, 32, 32)
mpm_grid=32
dx_norm=0.03125000
lbm_dt_phys=0.00400000
particle_min=[0.2593750059604645, 0.359375, 0.2593750059604645]
particle_max=[0.5406250357627869, 0.640625, 0.5406250357627869]
index_min=[8, 11, 8]
index_max=[17, 20, 17]
[OK] Step 4 shared domain baseline finished
```

Outputs:

```text
outputs/step4_shared_domain/particle_lbm_indices.npy
outputs/step4_shared_domain/particles_x.npy
```

## 7. Time Sync Dummy Command And Result

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step4_time_sync_dummy.py
```

Log:

```text
logs/step4_time_sync_dummy.log
```

Result:

```text
[Taichi] Starting on arch=cuda
lbm_step=0020, total_mpm_substeps=200, rho_min=1.000000, rho_max=1.000000, lbm_max_v=0.000000e+00, mpm_min_J=1.000000, mpm_max_speed=0.000000e+00
[OK] Step 4 time sync dummy baseline finished. completed_lbm_steps=20, total_mpm_substeps=200, rho_min=1.000000, rho_max=1.000000, lbm_max_v=0.000000e+00, mpm_min_J=1.000000, mpm_max_speed=0.000000e+00
```

Outputs:

```text
outputs/step4_time_sync_dummy/LBMFluid_20.vtr
outputs/step4_time_sync_dummy/particles_x.npy
outputs/step4_time_sync_dummy/particles_v.npy
outputs/step4_time_sync_dummy/particles_F.npy
outputs/step4_time_sync_dummy/particles_J.npy
```

## 8. Explicit Non-Goal Confirmation

Step 4 does not implement:

```text
MPM -> LBM solid projection
solid velocity projection
LBM cell force computation from MPM
hydrodynamic force computation or use
penalty force
moving bounce-back
momentum exchange
immersed boundary
two-phase flow
ReducedSquidFSI
squid geometry or real squid case
edits to external/taichi_LBM3D
```

The Step 4 baseline scripts instantiate both solvers together, read MPM particle positions for diagnostic mapping, and save NumPy output. They do not write MPM data into LBM fields.

## 9. Hard Acceptance Checklist

- [x] main is on the Step 4 final commit
- [x] `src/sim_config.py` exists
- [x] `src/units.py` exists
- [x] `src/__init__.py` exports `UnifiedSimConfig` and `GridUnitMapper`
- [x] `MPMSolid3D` has `set_uniform_velocity()`
- [x] LBM and MPM use the same `n_grid`
- [x] `nx = ny = nz = n_grid`
- [x] `dx_norm = 1 / n_grid`
- [x] `lbm_dt_phys = mpm_substeps_per_lbm_step * mpm_dt`
- [x] position mapping works
- [x] velocity round trip works
- [x] acceleration round trip works
- [x] viscosity round trip works
- [x] `LBMFluid3D` and `MPMSolid3D` can initialize in one script
- [x] shared-domain particle indices are valid
- [x] synchronized dummy loop runs
- [x] `total_mpm_substeps = n_lbm_steps * mpm_substeps_per_lbm_step`
- [x] LBM rho remains stable
- [x] MPM `min_J > 0`
- [x] no NaN
- [x] no Inf
- [x] no MPM -> LBM projection is implemented
- [x] no FSI force coupling is implemented
- [x] logs are saved under `logs/`
- [x] outputs are saved under `outputs/`
- [x] `STEP4_UNITS_GRID_TIMESTEP_REPORT.md` is complete
- [x] `pytest -q` passes

## 10. Decision

Can proceed to Step 5?

- [x] Yes

Step 5 can add projection tests on top of this scaffold. It should not reinterpret Step 4 as already having FSI coupling.
