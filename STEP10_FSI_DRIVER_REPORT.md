# Step 10 Unified FSI Driver Report

## 1. Goal

Build a unified FSI driver that can run `none`, `penalty`, and `moving_boundary` modes with common config, diagnostics, and output handling.

Step 10 adds a unified engineering driver.
Step 10 does not add new FSI physics.
Step 10 does not replace `PenaltyFSICoupler3D`.
Step 10 does not replace `MovingBoundaryFSICoupler3D`.
Step 10 does not change the Step 8 moving bounce-back formula.
Step 10 does not make `moving_boundary` the default solver path.
Step 10 does not edit `external/taichi_LBM3D`.

## 2. Files

Created / updated:

- `src/fsi_config.py`
- `src/fsi_driver.py`
- `src/run_utils.py`
- `src/__init__.py`
- `configs/step10_penalty_default.json`
- `configs/step10_moving_boundary_default.json`
- `configs/step10_mode_matrix.json`
- `baseline_tests/run_step10_driver_penalty_mode.py`
- `baseline_tests/run_step10_driver_moving_boundary_mode.py`
- `baseline_tests/run_step10_driver_mode_matrix.py`
- `baseline_tests/run_step10_performance_profile.py`
- `tests/test_step10_fsi_driver_contract.py`
- `STEP10_FSI_DRIVER_REPORT.md`

Generated:

- `logs/step10_driver_penalty.log`
- `logs/step10_driver_moving_boundary.log`
- `logs/step10_mode_matrix.log`
- `logs/step10_performance_profile.log`
- `outputs/step10_driver_penalty/`
- `outputs/step10_driver_moving_boundary/`
- `outputs/step10_mode_matrix/`
- `outputs/step10_performance_profile/`

## 3. Driver modes

| mode | LBM path | MPM reaction | cell_force | dynamic solid |
| ---- | -------- | ------------ | ---------- | ------------- |
| none | `lbm.step()` | none | zero | no |
| penalty | `lbm.step()` | `PenaltyFSICoupler3D` | nonzero | no |
| moving_boundary | `lbm.step_moving_bounceback()` | `MovingBoundaryFSICoupler3D` | zero | yes |

## 4. Config schema and defaults

`FSIDriverConfig` validates the coupling mode and numeric bounds, then builds the shared `UnifiedSimConfig`.

Default full-driver settings:

- `n_grid = 32`
- `n_particles = 4096`
- `n_lbm_steps = 20`
- `mpm_substeps_per_lbm_step = 10`
- `mpm_dt = 4.0e-4`
- `target_u_lbm = (0.02, 0.0, 0.0)`
- `beta_lbm = 1.0e-3`
- `penalty_force_cap_lbm = 1.0e-4`
- `mb_reaction_scale = 1.0`
- `mb_force_cap_norm = 1.0e-4`

The moving-boundary default keeps the Step 9 stable full-coupled window, not the stronger isolated reaction field value.

## 5. Common diagnostics fields

Each driver run saves `diagnostics_timeseries.npz` and `diagnostics_timeseries.csv` with:

```text
step
total_mpm_substeps
coupling_mode
rho_min
rho_max
lbm_max_v
fluid_mean_ux
projection_zone_fluid_mean_ux
far_field_fluid_mean_ux
solid_mean_vx_norm
mpm_min_J
mpm_max_speed
projected_mass
active_cell_count
cell_force_max_norm
hydro_force_max_norm
bb_link_count
bb_max_correction
active_reaction_particle_count
max_grid_reaction_norm
elapsed_seconds
```

## 6. Penalty driver baseline

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_penalty_mode.py
```

Result:

- completed_lbm_steps: 20
- total_mpm_substeps: 200
- final_fluid_mean_ux: 1.452040578e-06
- final_projection_zone_ux: 3.118410314e-05
- final_solid_mean_vx_norm: 1.536530554e-01
- cell_force_max_norm: 1.964967487e-05
- hydro_force_max_norm: 1.964967487e-05
- rho_min: 9.999890327e-01
- rho_max: 1.000013351e+00
- lbm_max_v: 4.150630775e-05
- mpm_min_J: 9.999937415e-01
- mpm_max_speed: 1.536901593e-01
- Log marker: `[OK] Step 10 driver penalty mode finished`

## 7. Moving-boundary driver baseline

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_moving_boundary_mode.py
```

Result:

- completed_lbm_steps: 20
- total_mpm_substeps: 200
- final_projection_zone_ux: 1.293940120e-03
- final_solid_mean_vx_norm: 1.509043425e-01
- bb_link_count: 2322
- active_reaction_particle_count: 3520
- cell_force_max_norm: 0.000000000e+00
- hydro_force_max_norm: 4.021632075e-01
- rho_min: 9.851435423e-01
- rho_max: 1.014919519e+00
- lbm_max_v: 2.135862410e-02
- mpm_min_J: 9.723306894e-01
- mpm_max_speed: 2.192054689e-01
- Log marker: `[OK] Step 10 driver moving-boundary mode finished`

## 8. Mode matrix

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_mode_matrix.py
```

Result:

| mode | stable | projection_zone_ux_final | solid_vx_final | rho_min | rho_max | cell_force_max_norm | hydro_force_max_norm |
| ---- | ------ | -----------------------: | -------------: | ------: | ------: | ------------------: | -------------------: |
| none | True | 0.000000000e+00 | 1.562558860e-01 | 1.000000358e+00 | 1.000000358e+00 | 0.000000000e+00 | 0.000000000e+00 |
| penalty | True | 3.118396126e-05 | 1.536530405e-01 | 9.999890327e-01 | 1.000013232e+00 | 1.964970033e-05 | 1.964970033e-05 |
| moving_boundary | True | 1.293938956e-03 | 1.509043574e-01 | 9.851434231e-01 | 1.014919758e+00 | 0.000000000e+00 | 4.021631479e-01 |

Trend:

```text
projection_zone_ux_final(moving_boundary) > projection_zone_ux_final(penalty) > projection_zone_ux_final(none)
```

Log marker: `[OK] Step 10 driver mode matrix finished`

## 9. Performance profile

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_performance_profile.py
```

Result:

| mode | total_time | projection_time | coupling_time | lbm_time | mpm_time |
| ---- | ---------: | --------------: | ------------: | -------: | -------: |
| none | 4.373437290e+01 | 8.247374999e-01 | 0.000000000e+00 | 3.809378300e+00 | 2.849920500e+00 |
| penalty | 1.652768771e+02 | 7.281521100e+00 | 5.183930000e-01 | 4.336646700e+01 | 5.827792260e+01 |
| moving_boundary | 7.204992740e+01 | 8.267775000e-01 | 6.620363001e-01 | 4.862220000e+00 | 4.369796800e+00 |

Log marker: `[OK] Step 10 performance profile finished`

## 10. Explicit non-goals

Step 10 does not implement:

- new FSI physics
- two-phase flow
- contact angle physics
- squid geometry
- sparse storage
- ReducedSquidFSI
- external/taichi_LBM3D edits
- strict final momentum-conserving sharp-interface FSI
- production-grade high-performance solver work

## 11. Acceptance checklist

- [x] main is on the Step 10 final commit
- [x] src/fsi_config.py exists
- [x] src/fsi_driver.py exists
- [x] src/run_utils.py exists
- [x] src/__init__.py exports FSIDriverConfig
- [x] src/__init__.py exports FSIDriver3D
- [x] configs/step10_penalty_default.json exists
- [x] configs/step10_moving_boundary_default.json exists
- [x] configs/step10_mode_matrix.json exists
- [x] FSIDriverConfig validates coupling_mode
- [x] FSIDriver3D supports coupling_mode="none"
- [x] FSIDriver3D supports coupling_mode="penalty"
- [x] FSIDriver3D supports coupling_mode="moving_boundary"
- [x] penalty driver baseline completes 20 LBM steps
- [x] penalty driver baseline completes 200 MPM substeps
- [x] penalty driver baseline has cell_force_max_norm > 0
- [x] moving-boundary driver baseline completes 20 LBM steps
- [x] moving-boundary driver baseline completes 200 MPM substeps
- [x] moving-boundary driver baseline has bb_link_count > 0
- [x] moving-boundary driver baseline has active_reaction_particle_count > 0
- [x] moving-boundary driver baseline keeps cell_force_max_norm == 0
- [x] mode matrix baseline completes
- [x] mode matrix includes none, penalty, moving_boundary
- [x] performance profile baseline completes
- [x] common diagnostics_timeseries.npz is saved
- [x] common diagnostics_timeseries.csv is saved
- [x] mode_matrix_results.csv is saved
- [x] mode_matrix_results.npz is saved
- [x] performance_results.csv is saved
- [x] performance_results.npz is saved
- [x] no NaN
- [x] no Inf
- [x] rho_min > 0.95
- [x] rho_max < 1.05
- [x] lbm_max_v < 0.1
- [x] mpm_min_J > 0
- [x] mpm_max_speed < 10
- [x] no new FSI physics
- [x] no two-phase flow
- [x] no contact angle physics
- [x] no ReducedSquidFSI
- [x] no external/taichi_LBM3D edits
- [x] logs are saved under logs/
- [x] outputs are saved under outputs/
- [x] STEP10_FSI_DRIVER_REPORT.md is complete
- [x] pytest -q passes

## 12. Decision

Can proceed to Step 11?

- [x] Yes
- [ ] No
