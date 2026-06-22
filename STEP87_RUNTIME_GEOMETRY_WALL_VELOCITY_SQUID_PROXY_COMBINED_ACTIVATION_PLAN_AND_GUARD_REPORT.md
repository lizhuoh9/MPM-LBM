# Step87 Runtime Geometry Wall Velocity Squid Proxy Combined Activation Plan And Guard Report

## Goal

Step87 is a plan-and-guard step only. It does not run `FSIDriver3D`, does not
call `driver.run()`, and does not execute simulation. It plans and guards one
future Step88 canonical driver row that combines:

- Step86 procedural static `squid_proxy` geometry;
- Step80/Step84 runtime geometry diagnostic-only reporting;
- Step82/Step84 wall velocity `solid_vel_experimental` reporting.

Correct Step87 claim:

```text
runtime geometry diagnostic-only + wall velocity solid_vel + squid_proxy combined smoke is planned and guarded for Step88.
```

Step87 does not claim that the combined smoke passed. It does not claim squid
swimming, squid actuation, real squid validation, physical validation, grid
convergence, or production readiness.

## Starting Point

Required starting commit:

```text
e69e11971728a370465e54f753988d2b9ab228b5
```

Step86 remains the accepted predecessor: one static `squid_proxy` canonical
driver smoke row passed at 32^3 with 1024 particles and three LBM steps.

## Planned Step88 Row

Step87 plans exactly one future Step88 row:

```text
campaign_id = step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_and_guard
row_id = canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
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
geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
planned_for_step88 = true
executed_in_step87 = false
```

The planned runtime geometry remains diagnostic-only/no-op. The planned wall
velocity path targets LBM `solid_vel` only, not LBM populations, MPM state, or
projector state.

## Evidence Summary

Activation plan:

```text
step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_pass = true
previous_step = Step86
previous_commit = e69e11971728a370465e54f753988d2b9ab228b5
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
step87_activation_feature_count = 0
planned_step88_activation_feature_count = 3
squid_proxy_planned_for_step88 = true
runtime_geometry_planned_for_step88 = true
wall_velocity_planned_for_step88 = true
combined_runtime_geometry_wall_velocity_planned_for_step88 = true
geometry_type_allowed_for_step88 = squid_proxy
geometry_motion_application_mode_allowed_for_step88 = diagnostic_only
wall_velocity_application_mode_allowed_for_step88 = solid_vel_experimental
target_lbm_field_planned_for_step88 = solid_vel
real_geometry_allowed = false
real_geometry_candidate_data_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
```

Activation guard:

```text
step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard_pass = true
guard_row_count = 37
guard_pass_count = 37
step87_activation_feature_count = 0
planned_step88_activation_feature_count = 3
geometry_type_planned_for_step88 = squid_proxy
runtime_geometry_application_mode_planned_for_step88 = diagnostic_only
wall_velocity_application_mode_planned_for_step88 = solid_vel_experimental
apply_to_lbm_solid_vel_planned_for_step88 = true
apply_to_lbm_populations_planned_for_step88 = false
modify_bounceback_formula_planned_for_step88 = false
real_geometry_planned_for_step88 = false
real_geometry_candidate_data_planned_for_step88 = false
link_area_planned_for_step88 = false
write_vtk_planned_for_step88 = false
write_particles_planned_for_step88 = false
```

Regression guards:

```text
step87_step86_regression_guard_pass = true
step86_activation_feature_count = 1
step86_squid_proxy_enabled_count = 1
step86_runtime_geometry_enabled_count = 0
step86_wall_velocity_enabled_count = 0
step86_combined_runtime_geometry_wall_velocity_enabled_count = 0

step87_step84_regression_guard_pass = true
step84_activation_feature_count = 2
step84_runtime_geometry_enabled_count = 1
step84_wall_velocity_enabled_count = 1
step84_combined_runtime_geometry_wall_velocity_enabled_count = 1
step84_squid_proxy_enabled_count = 0

step87_step82_regression_guard_pass = true
step82_wall_velocity_enabled_count = 1
step82_runtime_geometry_enabled_count = 0
step82_squid_proxy_enabled_count = 0

step87_step80_regression_guard_pass = true
step80_runtime_geometry_enabled_count = 1
step80_wall_velocity_enabled_count = 0
step80_squid_proxy_enabled_count = 0
```

Output guard:

```text
output_guard_pass = true
row_count = 35
pass_count = 35
step87_driver_run_dir_count = 0
step87_vtr_count = 0
step87_particle_npy_count = 0
step87_raw_geometry_output_count = 0
step87_real_geometry_candidate_output_count = 0
step87_dense_wall_velocity_output_count = 0
step87_sparse_wall_velocity_output_count = 0
step87_dense_displacement_output_count = 0
step87_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
```

Artifact manifest:

```text
artifact_budget_pass = true
step87_file_count = 66
step87_driver_run_dir_count = 0
step87_vtr_count = 0
step87_particle_npy_count = 0
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step87_file_count = 0
protected_real_geometry_candidates_step87_file_count = 0
raw_geometry_file_count = 0
```

## Boundaries

Step87 does not edit runtime solver or diagnostics code. It does not change LBM,
MPM, coupling, moving-boundary, wall-velocity, geometry-motion, tau, or
bounce-back formulas.

Step87 keeps real geometry candidate data, link-area transfer, 48^3, 64^3, VTR
output, particle NPY output, dense wall-velocity output, dense displacement
output, physical-validation claims, real squid validation claims, squid
swimming claims, squid actuation claims, and production-readiness claims closed.

## Conclusion

Step87 accepted.

Step87 is a plan-and-guard step only. It does not run `FSIDriver3D`, does not
call `driver.run()`, does not execute simulation, and does not activate the
three-feature combined row.

Step87 only plans and guards Step88:

```text
canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

Step88 may run exactly one 32^3 / 1024-particle / 3-step /
`moving_boundary` / engineering row with:

```text
geometry_type = squid_proxy
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
```

Step88 must not enable real geometry candidate data, link-area transfer, 48^3,
64^3, VTR output, or particle NPY output. Step88 must not change solver formulas
or claim physical validation, squid swimming, real squid validation, or
production readiness.

## Verification

Focused Step87 contract tests:

```text
trusted-taichi-python -W ignore -m pytest -q tests/test_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_contract.py tests/test_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard_contract.py tests/test_step87_step86_regression_contract.py tests/test_step87_step84_regression_contract.py tests/test_step87_step82_regression_contract.py tests/test_step87_step80_regression_contract.py tests/test_step87_output_guard_contract.py
7 passed in 1.10s
```

Full pytest with the trusted Taichi interpreter:

```text
trusted-taichi-python -W ignore -m pytest -q
1040 passed in 161.41s
```

Full pytest with the Anaconda interpreter:

```text
anaconda-python -W ignore -m pytest -q
1040 passed in 62.81s
```

Final Step87 output and artifact guards:

```text
baseline_tests/run_step87_output_guard.py
[OK] Step87 output guard finished

baseline_tests/run_step87_artifact_manifest.py
[OK] Step87 artifact manifest finished
```
