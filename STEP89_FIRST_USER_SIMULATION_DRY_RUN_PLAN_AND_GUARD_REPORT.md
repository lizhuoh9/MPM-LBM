# Step89 First User Simulation Dry Run Plan And Guard Report

## Goal

Step89 is a plan-and-guard step only. It does not run `FSIDriver3D`, does not
call `driver.run()`, and does not execute simulation.

Correct Step89 claim:

```text
first user simulation dry run is planned and guarded for Step90
```

Step89 does not claim first user simulation passed, production simulation
readiness, physical validation, real squid validation, squid swimming, or squid
actuation.

## Starting Point

Required starting commit:

```text
f83ddcd1a0979ed6dbe41c6a9763d891e9c66b9f
```

Step88 remains the accepted predecessor: it executed the bounded three-feature
32^3/1024-particle/3-step smoke row combining procedural `squid_proxy`
geometry, runtime geometry diagnostic-only reporting, and wall velocity
`solid_vel_experimental` reporting.

## Planned Step90 Row

Step89 plans exactly one future Step90 required row:

```text
campaign_id = step89_first_user_simulation_dry_run_plan_and_guard
row_id = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run
n_grid = 32
n_particles = 1024
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
planned_for_step90 = true
executed_in_step89 = false
```

The zero `target_u_lbm` is a planned row-local choice for the first user dry
run. It keeps Step90 focused on the Step88 three-feature envelope rather than
adding background-flow variation in the same step.

## Evidence Summary

Dry-run plan:

```text
step89_first_user_simulation_dry_run_plan_pass = true
previous_step = Step88
previous_commit = f83ddcd1a0979ed6dbe41c6a9763d891e9c66b9f
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
step90_allowed = true
step90_allowed_n_grid = 32
step90_allowed_n_particles = 1024
step90_allowed_n_lbm_steps = 5
step89_activation_feature_count = 0
planned_step90_activation_feature_count = 3
```

Dry-run guard:

```text
step89_first_user_simulation_dry_run_guard_pass = true
guard_pass_count = 38
guard_row_count = 38
squid_proxy_planned_for_step90 = true
runtime_geometry_planned_for_step90 = true
wall_velocity_planned_for_step90 = true
combined_runtime_geometry_wall_velocity_planned_for_step90 = true
geometry_motion_application_mode_planned_for_step90 = diagnostic_only
wall_velocity_application_mode_planned_for_step90 = solid_vel_experimental
target_lbm_field_planned_for_step90 = solid_vel
real_geometry_planned_for_step90 = false
real_geometry_candidate_data_planned_for_step90 = false
link_area_planned_for_step90 = false
write_vtk_planned_for_step90 = false
write_particles_planned_for_step90 = false
```

Regression guards:

```text
step89_step88_regression_guard_pass = true
step88_activation_feature_count = 3
step88_squid_proxy_enabled_count = 1
step88_runtime_geometry_enabled_count = 1
step88_wall_velocity_enabled_count = 1
step88_combined_runtime_geometry_wall_velocity_enabled_count = 1
step88_real_geometry_candidate_enabled_count = 0
step88_link_area_enabled_count = 0
step88_vtr_count = 0
step88_particle_npy_count = 0

step89_step87_regression_guard_pass = true
step87_activation_feature_count = 0
planned_step88_activation_feature_count = 3
step87_driver_run_dir_count = 0
step87_vtr_count = 0
step87_particle_npy_count = 0

step89_step86_regression_guard_pass = true
step86_activation_feature_count = 1
step86_squid_proxy_enabled_count = 1
step86_runtime_geometry_enabled_count = 0
step86_wall_velocity_enabled_count = 0
step86_vtr_count = 0
step86_particle_npy_count = 0
```

Output guard:

```text
output_guard_pass = true
artifact_budget_pass = true
step89_driver_run_dir_count = 0
step89_vtr_count = 0
step89_particle_npy_count = 0
step89_raw_geometry_output_count = 0
step89_real_geometry_candidate_output_count = 0
step89_dense_wall_velocity_output_count = 0
step89_sparse_wall_velocity_output_count = 0
step89_dense_displacement_output_count = 0
step89_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
```

Artifact manifest:

```text
artifact_budget_pass = true
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step89_file_count = 0
protected_real_geometry_candidates_step89_file_count = 0
raw_geometry_file_count = 0
step89_driver_run_dir_count = 0
step89_particle_npy_count = 0
step89_vtr_count = 0
```

The exact Step89 file count and byte total are recorded in
`outputs/step89_artifact_manifest/artifact_summary.json`; this report avoids
duplicating those self-referential values.

## Boundaries

Step89 does not edit runtime solver or diagnostics code. It does not change
LBM, MPM, coupling, moving-boundary, wall-velocity, geometry-motion, tau, or
bounce-back formulas.

Step89 keeps real geometry candidate data, link-area transfer, 48^3, 64^3, VTR
output, particle NPY output, dense wall-velocity output, dense displacement
output, physical-validation claims, real squid validation claims, squid
swimming claims, squid actuation claims, and production-readiness claims
closed.

Step89 does not create a driver-run output directory. It only produces plan,
guard, regression, output-guard, artifact-manifest, log, report, and
documentation artifacts.

## Conclusion

Step89 accepted.

Step89 is a plan-and-guard step only. It does not run `FSIDriver3D`, does not
call `driver.run()`, does not execute simulation, and does not activate the
first user simulation dry run.

Step89 only plans and guards Step90:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run
```

Step90 may run exactly one 32^3 / 1024-particle / 5-step /
`moving_boundary` / engineering row with:

```text
geometry_type = squid_proxy
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
target_u_lbm = [0.0, 0.0, 0.0]
```

Step90 must not enable real geometry candidate data, link-area transfer, 48^3,
64^3, VTR output, or particle NPY output. Step90 must not change solver
formulas or claim physical validation, squid swimming, real squid validation,
or production readiness.

## Verification

Focused Step89 contract tests:

```text
6 passed in 0.98s
```

Full trusted Taichi pytest:

```text
1056 passed in 168.95s (0:02:48)
```

Full Anaconda pytest:

```text
1056 passed in 79.26s (0:01:19)
```

The final verification logs are:

```text
logs/step89_focused_pytest.log
logs/step89_full_pytest_taichi.log
logs/step89_full_pytest_anaconda.log
```
