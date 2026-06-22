# Step86 Squid Proxy Static Geometry Canonical Driver Smoke Report

## Goal

Step86 executes the single static `squid_proxy` canonical-driver smoke row
planned by Step85. It proves only that the procedural static squid proxy can run
through `FSIDriver3D.run()` for three LBM steps at 32^3 with 1024 particles,
write the required quality report, and keep the Step85/Step84/Step31
boundaries intact.

Correct Step86 claim:

```text
squid_proxy static geometry canonical driver 3-step smoke passed
```

Step86 is not real squid validation, squid swimming, squid actuation, physical
validation, grid convergence, or production readiness.

## Starting Point

Required starting commit:

```text
f74e44a540f00dd59d2f1b231c942a334bd0891b
```

Step85 remains the accepted predecessor: it planned and guarded one future
static `squid_proxy` row but did not run `FSIDriver3D`.

## Executed Row

```text
campaign_id = step86_squid_proxy_static_geometry_canonical_driver_smoke
row_id = canonical_driver_squid_proxy_static_geometry_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
boundary_motion_mode = static
geometry_motion_mode = static
geometry_motion_application_mode = disabled
wall_velocity_application_mode = disabled
write_vtk = false
write_particles = false
executed_in_step86 = true
```

No optional row was added or run.

## Evidence Summary

Smoke matrix:

```text
step86_squid_proxy_static_geometry_smoke_matrix_pass = true
required_row_count = 1
optional_row_count = 0
required_stable_count = 1
driver_run_called_count = 1
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_count = 0
activation_feature_count = 1
procedural_geometry_enabled_count = 1
squid_proxy_enabled_count = 1
real_geometry_candidate_enabled_count = 0
real_geometry_enabled_count = 0
runtime_geometry_enabled_count = 0
wall_velocity_enabled_count = 0
combined_runtime_geometry_wall_velocity_enabled_count = 0
link_area_enabled_count = 0
grid_48_enabled_count = 0
grid_64_enabled_count = 0
write_vtk_count = 0
write_particles_count = 0
```

Runtime smoke values:

```text
completed_lbm_steps = 3
total_mpm_substeps = 3
diagnostics_row_count = 4
rho_min_min = 0.9614667892456055
rho_max_max = 1.0393489599227905
lbm_max_v_max = 0.0288397129625082
mpm_min_J_min = 0.999782145023346
mpm_max_speed_max = 1.567559003829956
projected_mass_final = 0.02264912612736225
active_cell_count_final = 1763
bb_link_count_max = 2574
active_reaction_particle_count_final = 987
max_grid_reaction_norm_max = 4.2154038965236396e-05
```

Geometry quality:

```text
step86_squid_proxy_static_geometry_quality_pass = true
geometry_quality_report_pass_count = 1
quality_check_strict = false
quality_report_occupied_count = 774
quality_report_surface_voxel_count = 358
quality_report_touches_domain_boundary = false
sampling_particle_count = 1024
mantle_particle_count = 867
head_particle_count = 189
arms_particle_count = 52
left_fin_particle_count = 23
right_fin_particle_count = 22
```

Output guard:

```text
output_guard_pass = true
row_count = 37
pass_count = 37
step86_required_driver_run_dir_count = 1
step86_optional_driver_run_dir_count = 0
step86_vtr_count = 0
step86_particle_npy_count = 0
step86_dense_wall_velocity_output_count = 0
step86_dense_displacement_output_count = 0
step86_raw_geometry_output_count = 0
step86_real_geometry_candidate_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
```

Artifact manifest:

```text
artifact_budget_pass = true
step86_file_count = 79
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step86_file_count = 0
protected_real_geometry_candidates_step86_file_count = 0
raw_geometry_file_count = 0
step86_driver_run_dir_count = 1
step86_particle_npy_count = 0
step86_vtr_count = 0
```

Step85/Step84/Step31 guard evidence:

```text
step86_step85_regression_guard_pass = true
step86_step84_regression_guard_pass = true
step86_step31_reference_guard_pass = true
step85_activation_feature_count = 0
step84_activation_feature_count = 2
step30_geometry_type = squid_proxy
step31_static_driver_reference_exists = true
step31_not_real_squid_validation_claim = true
step31_no_squid_swimming_claim = true
```

## Driver Output

The required driver run directory is:

```text
outputs/step86_driver_runs/canonical_driver_squid_proxy_static_geometry_32_3step_smoke
```

It contains only the allowed run artifacts:

```text
diagnostics_timeseries.csv
diagnostics_timeseries.npz
driver_config.json
driver_timing.json
geo_all_fluid_32.dat
geometry_quality_report.json
```

No VTR, particle NPY, dense wall-velocity/displacement, displaced-particle,
raw real-geometry, or optional driver-run directory is produced.

## Files Added

Configs:

- `configs/step86_canonical_driver_squid_proxy_static_geometry_32_3step_smoke.json`
- `configs/step86_squid_proxy_static_geometry_smoke_matrix.json`
- `configs/step86_squid_proxy_static_geometry_acceptance_policy.json`
- `configs/step86_activation_guard_policy.json`
- `configs/step86_output_guard_policy.json`
- `configs/step86_step85_regression_policy.json`
- `configs/step86_step84_regression_policy.json`
- `configs/step86_step31_reference_policy.json`
- `configs/step86_artifact_manifest_policy.json`

Evidence modules:

- `src/mpm_lbm/evidence/step86_squid_proxy_static_geometry_smoke_runner.py`
- `src/mpm_lbm/evidence/step86_squid_proxy_static_geometry_smoke_audit.py`
- `src/mpm_lbm/evidence/step86_squid_proxy_static_geometry_quality_audit.py`
- `src/mpm_lbm/evidence/step86_squid_proxy_static_geometry_activation_guard.py`
- `src/mpm_lbm/evidence/step86_output_guard.py`
- `src/mpm_lbm/evidence/step86_step85_regression_guard.py`
- `src/mpm_lbm/evidence/step86_step84_regression_guard.py`
- `src/mpm_lbm/evidence/step86_step31_reference_guard.py`

Baseline runners:

- `baseline_tests/step86_common.py`
- `baseline_tests/run_step86_squid_proxy_static_geometry_smoke_matrix.py`
- `baseline_tests/run_step86_squid_proxy_static_geometry_quality.py`
- `baseline_tests/run_step86_activation_guard.py`
- `baseline_tests/run_step86_output_guard.py`
- `baseline_tests/run_step86_step85_regression_guard.py`
- `baseline_tests/run_step86_step84_regression_guard.py`
- `baseline_tests/run_step86_step31_reference_guard.py`
- `baseline_tests/run_step86_artifact_manifest.py`

Tests:

- `tests/test_step86_squid_proxy_static_geometry_smoke_matrix_contract.py`
- `tests/test_step86_squid_proxy_static_geometry_quality_contract.py`
- `tests/test_step86_activation_guard_contract.py`
- `tests/test_step86_output_guard_contract.py`
- `tests/test_step86_step85_regression_contract.py`
- `tests/test_step86_step84_regression_contract.py`
- `tests/test_step86_step31_reference_contract.py`

Docs:

- `docs/86_squid_proxy_static_geometry_canonical_driver_smoke.md`
- `STEP86_SQUID_PROXY_STATIC_GEOMETRY_CANONICAL_DRIVER_SMOKE_GOAL.md`
- `STEP86_SQUID_PROXY_STATIC_GEOMETRY_CANONICAL_DRIVER_SMOKE_REPORT.md`

## Boundaries

Step86 does not edit runtime solver or diagnostics code. It does not change
LBM, MPM, coupling, moving-boundary, wall-velocity, geometry-motion, tau, or
bounce-back formulas. It keeps runtime geometry, wall velocity, combined
runtime geometry plus wall velocity, real geometry candidates, link-area
transfer, 48^3, 64^3, VTR output, and particle NPY output closed.

The static `squid_proxy` geometry is a procedural proxy only. It is not real
squid geometry, does not represent squid actuation, and does not validate squid
swimming.

## Verification

Focused Step86 contract tests:

```text
trusted-taichi-python -W ignore -m pytest -q tests\test_step86_squid_proxy_static_geometry_smoke_matrix_contract.py tests\test_step86_squid_proxy_static_geometry_quality_contract.py tests\test_step86_activation_guard_contract.py tests\test_step86_output_guard_contract.py tests\test_step86_step85_regression_contract.py tests\test_step86_step84_regression_contract.py tests\test_step86_step31_reference_contract.py
7 passed in 1.01s
```

Full pytest with the trusted Taichi interpreter:

```text
trusted-taichi-python -W ignore -m pytest -q
1033 passed in 138.29s
```

Full pytest with the Anaconda interpreter:

```text
anaconda-python -W ignore -m pytest -q
1033 passed in 60.41s
```

Final Step86 output and artifact guards:

```text
baseline_tests/run_step86_output_guard.py
[OK] Step86 output guard finished

baseline_tests/run_step86_artifact_manifest.py
[OK] Step86 artifact manifest finished
```
