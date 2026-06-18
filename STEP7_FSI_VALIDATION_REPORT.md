# Step 7 FSI Validation Report

## 1. Goal

Validate the Step 6 penalty-force MPM-LBM coupling using trend, stability, and diagnostic baselines. No new FSI model is implemented.

Step 7 validates Step 6 penalty coupling. Step 7 does not implement a new coupling method. Step 7 evidence is qualitative/trend/stability evidence, not sharp-interface validation.

## 2. Files Created Or Updated

```text
src/diagnostics.py
src/__init__.py
baseline_tests/run_step7_couette_like_validation.py
baseline_tests/run_step7_momentum_impulse_diagnostics.py
baseline_tests/run_step7_beta_sweep.py
baseline_tests/run_step7_long_coupled_stability.py
tests/test_step7_validation_contract.py
logs/step7_couette_like.log
logs/step7_momentum_impulse.log
logs/step7_beta_sweep.log
logs/step7_long_stability.log
outputs/step7_couette_like/
outputs/step7_momentum_impulse/
outputs/step7_beta_sweep/
outputs/step7_long_stability/
STEP7_FSI_VALIDATION_REPORT.md
```

## 3. Explicit Non-Goals

Step 7 does not implement:

```text
moving bounce-back
momentum exchange
sharp-interface FSI
new immersed-boundary model
two-phase flow
contact angle physics
squid geometry
sparse storage
ReducedSquidFSI
external/taichi_LBM3D edits
```

Momentum and impulse are used only as diagnostics. They are not a momentum-exchange coupling method.

## 4. Diagnostics Definitions

`FSIDiagnostics3D` is a diagnostic-only NumPy helper. It reads Taichi fields to produce baseline evidence and does not modify solver state.

Implemented diagnostics:

```text
lbm_fluid_stats(lbm)
mpm_particle_stats(solid)
projection_zone_fluid_mean_velocity(lbm)
far_field_fluid_mean_velocity(lbm)
projected_solid_mean_velocity(lbm)
force_stats(lbm)
solid_mean_velocity_norm(solid)
solid_momentum_norm(solid)
lbm_velocity_profile_x_over_y(lbm)
```

Key statistics:

```text
projection-zone velocity: weighted average over solid_phi > 1.0e-6
far-field velocity: mean over fluid cells with solid_phi <= 1.0e-6
force balance error: norm(sum(cell_force) + sum(hydro_force))
solid mean velocity: particle-mass weighted average in normalized MPM units
ux profile over y: mean LBM ux across x-z planes
```

## 5. Couette-Like Validation

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step7_couette_like_validation.py
```

Log:

```text
logs/step7_couette_like.log
```

Result:

```text
[Taichi] Starting on arch=cuda
n_grid=32
n_lbm_steps=100
mpm_substeps_per_lbm_step=10
target_u_lbm=(0.03, 0.0, 0.0)
target_u_norm=(0.234375, 0.0, 0.0)
initial_projection_zone_fluid_mean_ux=0.000000000e+00
final_projection_zone_fluid_mean_ux=1.579456293e-04
far_field_fluid_mean_ux=2.134014039e-06
final_global_fluid_mean_ux=6.000273061e-06
initial_solid_mean_vx_norm=2.343821377e-01
final_solid_mean_vx_norm=2.161261886e-01
active_force_cell_count=1296
rho_min=9.999880791e-01
rho_max=1.000015020e+00
lbm_max_v=2.438331430e-04
mpm_min_J=9.999933243e-01
mpm_max_speed=2.162137628e-01
[OK] Step 7 Couette-like validation finished
```

Outputs:

```text
outputs/step7_couette_like/LBMFluid_100.vtr
outputs/step7_couette_like/particles_x.npy
outputs/step7_couette_like/particles_v.npy
outputs/step7_couette_like/ux_profile_y.npy
outputs/step7_couette_like/diagnostics.npz
```

## 6. Momentum / Impulse Diagnostics

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step7_momentum_impulse_diagnostics.py
```

Log:

```text
logs/step7_momentum_impulse.log
```

Result:

```text
[Taichi] Starting on arch=cuda
n_grid=32
n_lbm_steps=100
mpm_substeps_per_lbm_step=10
target_u_lbm=(0.03, 0.0, 0.0)
target_u_norm=(0.234375, 0.0, 0.0)
initial_fluid_mean_ux=0.000000000e+00
initial_solid_mean_vx_norm=2.343865037e-01
max_force_balance_error=0.000000000e+00
mean_force_balance_error=0.000000000e+00
cumulative_cell_impulse_x=2.534365149e+00
cumulative_hydro_impulse_x=-2.534365149e+00
final_fluid_mean_ux=8.978327969e-06
final_solid_mean_vx_norm=2.155670971e-01
rho_min=9.999854565e-01
rho_max=1.000018001e+00
lbm_max_v=2.276640007e-04
mpm_min_J=9.999896288e-01
mpm_max_speed=2.156339735e-01
[OK] Step 7 momentum impulse diagnostics finished
```

Outputs:

```text
outputs/step7_momentum_impulse/diagnostics_timeseries.npz
outputs/step7_momentum_impulse/LBMFluid_100.vtr
```

## 7. Beta Sweep

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step7_beta_sweep.py
```

Log:

```text
logs/step7_beta_sweep.log
```

Result:

| beta_lbm | stable | rho_min | rho_max | lbm_max_v | mpm_min_J | final_fluid_mean_ux | final_solid_mean_vx_norm | solid_slowdown_norm |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3.0e-4 | true | 0.9999976158 | 1.0000039339 | 2.636343197e-05 | 0.9999848008 | 9.762655964e-07 | 0.1542929411 | 0.0019618273 |
| 1.0e-3 | true | 0.9999912381 | 1.0000110865 | 8.615820843e-05 | 0.9999908209 | 3.191017640e-06 | 0.1498417407 | 0.0064130276 |
| 3.0e-3 | true | 0.9999746680 | 1.0000280142 | 2.457897644e-04 | 0.9999875426 | 9.120005416e-06 | 0.1378519535 | 0.0184028149 |

Summary:

```text
stable_beta_count=3
fluid_response=[9.76265596364101e-07, 3.191017640347127e-06, 9.12000541575253e-06]
solid_slowdown=[0.001961827278137207, 0.00641302764415741, 0.018402814865112305]
[OK] Step 7 beta sweep finished
```

Outputs:

```text
outputs/step7_beta_sweep/beta_sweep_results.csv
outputs/step7_beta_sweep/beta_sweep_results.npz
```

## 8. Long Coupled Stability

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step7_long_coupled_stability.py
```

Log:

```text
logs/step7_long_stability.log
```

Result:

```text
[Taichi] Starting on arch=cuda
n_grid=32
n_lbm_steps=100
mpm_substeps_per_lbm_step=10
target_u_lbm=(0.02, 0.0, 0.0)
target_u_norm=(0.15625, 0.0, 0.0)
completed_lbm_steps=100
total_mpm_substeps=1000
initial_fluid_mean_ux=0.000000000e+00
final_fluid_mean_ux=5.990422324e-06
initial_solid_mean_vx_norm=1.562547684e-01
final_solid_mean_vx_norm=1.437114030e-01
active_force_cell_count=1584
rho_min=9.999907017e-01
rho_max=1.000012636e+00
lbm_max_v=1.526288688e-04
mpm_min_J=9.999910593e-01
mpm_max_speed=1.437596679e-01
[OK] Step 7 long coupled stability finished
```

Outputs:

```text
outputs/step7_long_stability/LBMFluid_100.vtr
outputs/step7_long_stability/particles_x.npy
outputs/step7_long_stability/particles_v.npy
outputs/step7_long_stability/particles_F.npy
outputs/step7_long_stability/particles_J.npy
outputs/step7_long_stability/diagnostics_timeseries.npz
```

## 9. Stability Window Summary

The Step 7 baseline window is stable for:

```text
n_grid = 32
n_particles = 4096
mpm_dt = 4.0e-4
mpm_substeps_per_lbm_step = 10
force_cap_lbm = 1.0e-4
target_u_lbm in [(0.02, 0, 0), (0.03, 0, 0)]
beta_lbm in [3.0e-4, 1.0e-3, 3.0e-3]
```

Within this window:

```text
fluid response is non-decreasing with beta
solid slowdown is non-decreasing with beta
rho remains in [0.95, 1.05]
lbm_max_v remains far below 0.1
mpm_min_J remains positive
mpm_max_speed remains far below 10
```

## 10. Hard Acceptance Checklist

- [x] main is on the Step 7 final commit
- [x] `src/diagnostics.py` exists
- [x] `src/__init__.py` exports `FSIDiagnostics3D`
- [x] `FSIDiagnostics3D.lbm_fluid_stats()` exists
- [x] `FSIDiagnostics3D.mpm_particle_stats()` exists
- [x] `FSIDiagnostics3D.projection_zone_fluid_mean_velocity()` exists
- [x] `FSIDiagnostics3D.far_field_fluid_mean_velocity()` exists
- [x] `FSIDiagnostics3D.projected_solid_mean_velocity()` exists
- [x] `FSIDiagnostics3D.force_stats()` exists
- [x] `FSIDiagnostics3D.solid_mean_velocity_norm()` exists
- [x] `FSIDiagnostics3D.solid_momentum_norm()` exists
- [x] `FSIDiagnostics3D.lbm_velocity_profile_x_over_y()` exists
- [x] Couette-like validation passes
- [x] projection zone fluid ux increases
- [x] projection zone fluid ux > far-field ux
- [x] global fluid ux > 0
- [x] solid mean vx decreases
- [x] momentum / impulse diagnostics pass
- [x] force balance error is small
- [x] cumulative cell impulse x > 0
- [x] cumulative hydro impulse x < 0
- [x] beta sweep passes
- [x] beta sweep has stable 3.0e-4 row
- [x] beta sweep has stable 1.0e-3 row
- [x] fluid response is non-decreasing with beta within tolerance
- [x] solid slowdown is non-decreasing with beta within tolerance
- [x] long coupled stability completes 100 LBM steps
- [x] long coupled stability completes 1000 MPM substeps
- [x] active_force_cell_count > 0
- [x] `rho_min > 0.95`
- [x] `rho_max < 1.05`
- [x] `lbm_max_v < 0.1`
- [x] `mpm_min_J > 0`
- [x] `mpm_max_speed < 10`
- [x] no NaN
- [x] no Inf
- [x] no moving bounce-back
- [x] no momentum exchange
- [x] no sharp-interface FSI
- [x] no two-phase flow
- [x] no contact angle physics
- [x] no ReducedSquidFSI
- [x] no `external/taichi_LBM3D` edits
- [x] logs are saved under `logs/`
- [x] outputs are saved under `outputs/`
- [x] `STEP7_FSI_VALIDATION_REPORT.md` is complete
- [x] `pytest -q` passes

## 11. Decision

Can proceed to Step 8?

- [x] Yes

Step 7 provides reproducible qualitative FSI response and a documented small-scale stability window for the current penalty-force MPM-LBM prototype. It is now reasonable to plan Step 8 moving-boundary or sharper interface work as a new physics stage, using Step 7 as the comparison baseline.
