# Step83 Runtime Geometry Wall Velocity Combined Activation Plan And Guard Report

Status: accepted.

Step83 is a plan-and-guard step only.

Step83 does not run `FSIDriver3D`.
Step83 does not call `driver.run()`.
Step83 does not execute a simulation.
Step83 does not activate combined runtime geometry plus wall velocity in a
driver run.

## Planned Step84 Row

Step83 only plans and guards Step84:

```text
canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

Step84 may run exactly one 32^3 / 1024-particle / 3-step /
moving_boundary / engineering / box row with:

```text
geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
```

The planned Step84 config paths are:

```text
geometry_motion_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_application_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json
wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json
```

## Evidence Summary

```text
step83_runtime_geometry_wall_velocity_combined_activation_plan_pass = true
step83_runtime_geometry_wall_velocity_combined_activation_guard_pass = true
step83_step82_regression_guard_pass = true
step83_step80_regression_guard_pass = true
output_guard_pass = true
artifact_budget_pass = true
```

Plan evidence:

```text
previous_step = Step82
previous_commit = 3df6bb25b32d74f16300b8ba603c843eecc725c2
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
runtime_geometry_planned_for_step84 = true
geometry_motion_application_mode_allowed_for_step84 = diagnostic_only
geometry_mutation_allowed = false
wall_velocity_planned_for_step84 = true
wall_velocity_application_mode_allowed_for_step84 = solid_vel_experimental
target_lbm_field_planned_for_step84 = solid_vel
combined_runtime_geometry_wall_velocity_planned_for_step84 = true
step83_activation_feature_count = 0
planned_step84_activation_feature_count = 2
step84_allowed_row_name = canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

Guard evidence:

```text
guard_pass_count = 44
guard_row_count = 44
runtime_geometry_application_mode_planned_for_step84 = diagnostic_only
apply_to_lbm_solid_vel_planned_for_step84 = true
apply_to_lbm_populations_planned_for_step84 = false
apply_to_mpm_planned_for_step84 = false
apply_to_projector_planned_for_step84 = false
modify_bounceback_formula_planned_for_step84 = false
real_geometry_planned_for_step84 = false
squid_proxy_planned_for_step84 = false
link_area_planned_for_step84 = false
write_vtk_planned_for_step84 = false
write_particles_planned_for_step84 = false
```

Regression evidence:

```text
step83_step82_regression_guard_pass = true
step82_wall_velocity_enabled_count = 1
step82_runtime_geometry_enabled_count = 0
step82_vtr_count = 0
step82_particle_npy_count = 0

step83_step80_regression_guard_pass = true
step80_runtime_geometry_enabled_count = 1
step80_wall_velocity_enabled_count = 0
step80_vtr_count = 0
step80_particle_npy_count = 0
```

Output evidence:

```text
step83_driver_run_dir_count = 0
step83_vtr_count = 0
step83_particle_npy_count = 0
step83_dense_wall_velocity_output_count = 0
step83_sparse_wall_velocity_output_count = 0
step83_dense_displacement_output_count = 0
step83_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
```

Artifact budget:

```text
artifact_budget_pass = true
step83_file_count <= 55
step83_total_size_mb < 5
step83_driver_run_dir_count = 0
step83_vtr_count = 0
step83_particle_npy_count = 0
```

## Validation Commands

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step83_runtime_geometry_wall_velocity_combined_activation_plan.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step83_runtime_geometry_wall_velocity_combined_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step83_step82_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step83_step80_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step83_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step83_artifact_manifest.py
```

Focused and full pytest logs are stored under `logs/step83_*.log`.

## Claim Boundary

Step83 proves only this bounded claim:

```text
runtime geometry diagnostic-only + wall velocity solid_vel combined smoke is planned and guarded for Step84
```

Step83 does not prove the combined smoke has passed. Step83 does not prove
moving geometry, moving-wall physics, real squid validation, grid convergence,
or production readiness.
