# Step91 First User Simulation 10-Step Dry Run Plan And Guard Report

## Goal

Step91 is a plan-and-guard step only. It does not run `FSIDriver3D`, does not
call `driver.run()`, and does not execute simulation.

Correct Step91 claim:

```text
first user simulation 10-step dry run is planned and guarded for Step92
```

Step91 does not claim 10-step dry-run success, production readiness, physical
validation, real squid validation, squid swimming, or squid actuation.

## Starting Point

Required starting commit:

```text
72503260933df8919826ef8fa7ed7cab12b96297
```

Step90 remains the accepted predecessor: it executed the bounded first user
simulation dry-run row at 32^3 with 1024 particles for five LBM steps.

## Planned Step92 Row

Step91 plans exactly one future Step92 required row:

```text
campaign_id = step91_first_user_simulation_10step_dry_run_plan_and_guard
row_id = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run
n_grid = 32
n_particles = 1024
n_lbm_steps = 10
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
planned_for_step92 = true
executed_in_step91 = false
```

The only intended expansion from Step90 to Step92 is:

```text
n_lbm_steps = 5 -> 10
```

Everything else stays fixed.

## Evidence Summary

10-step dry-run plan:

```text
step91_first_user_simulation_10step_dry_run_plan_pass = true
previous_step = Step90
previous_commit = 72503260933df8919826ef8fa7ed7cab12b96297
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
step92_allowed = true
step92_allowed_n_grid = 32
step92_allowed_n_particles = 1024
step92_allowed_n_lbm_steps = 10
only_duration_expansion_from_step90 = true
previous_step90_n_lbm_steps = 5
planned_step92_n_lbm_steps = 10
step91_activation_feature_count = 0
planned_step92_activation_feature_count = 3
pass_count = 67
row_count = 67
```

10-step dry-run guard:

```text
step91_first_user_simulation_10step_dry_run_guard_pass = true
guard_pass_count = 42
guard_row_count = 42
squid_proxy_planned_for_step92 = true
runtime_geometry_planned_for_step92 = true
wall_velocity_planned_for_step92 = true
combined_runtime_geometry_wall_velocity_planned_for_step92 = true
geometry_motion_application_mode_planned_for_step92 = diagnostic_only
wall_velocity_application_mode_planned_for_step92 = solid_vel_experimental
target_lbm_field_planned_for_step92 = solid_vel
real_geometry_planned_for_step92 = false
real_geometry_candidate_data_planned_for_step92 = false
link_area_planned_for_step92 = false
write_vtk_planned_for_step92 = false
write_particles_planned_for_step92 = false
```

Step90 regression guard:

```text
step91_step90_regression_guard_pass = true
artifact_pass_count = 8
artifact_check_count = 8
step90_activation_feature_count = 3
step90_squid_proxy_enabled_count = 1
step90_runtime_geometry_enabled_count = 1
step90_wall_velocity_enabled_count = 1
step90_combined_runtime_geometry_wall_velocity_enabled_count = 1
step90_completed_lbm_steps = 5
step90_real_geometry_candidate_enabled_count = 0
step90_link_area_enabled_count = 0
step90_vtr_count = 0
step90_particle_npy_count = 0
```

Step89 and Step88 regression guards:

```text
step91_step89_regression_guard_pass = true
step91_step88_regression_guard_pass = true
```

Output guard:

```text
output_guard_pass = true
artifact_budget_pass = true
step91_driver_run_dir_count = 0
step91_vtr_count = 0
step91_particle_npy_count = 0
step91_raw_geometry_output_count = 0
step91_real_geometry_candidate_output_count = 0
step91_dense_wall_velocity_output_count = 0
step91_sparse_wall_velocity_output_count = 0
step91_dense_displacement_output_count = 0
step91_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step91_large_file_count = 0
```

Artifact manifest:

```text
artifact_budget_pass = true
step91_file_count = 57
step91_driver_run_dir_count = 0
step91_vtr_count = 0
step91_particle_npy_count = 0
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step91_file_count = 0
protected_real_geometry_candidates_step91_file_count = 0
raw_geometry_file_count = 0
```

The exact self-referential Step91 byte total is recorded in
`outputs/step91_artifact_manifest/artifact_summary.json`.

## Boundaries

Step91 does not edit runtime solver or diagnostics code. It does not change
LBM, MPM, coupling, moving-boundary, wall-velocity, geometry-motion, tau, or
bounce-back formulas.

Step91 keeps real geometry candidate data, link-area transfer, 48^3, 64^3, VTR
output, particle NPY output, dense wall-velocity output, dense displacement
output, physical-validation claims, real squid validation claims, squid
swimming claims, squid actuation claims, and production-readiness claims
closed.

Step91 does not create a driver-run output directory. It only produces plan,
guard, regression, output-guard, artifact-manifest, log, report, and
documentation artifacts.

## Verification

Expected red before artifacts:

```text
6 failed
```

Focused Step91 contract tests after evidence generation:

```text
6 passed in 1.15s
```

Focused Step91 contract tests after final output-guard refresh:

```text
6 passed in 1.21s
```

Full trusted Taichi pytest:

```text
1069 passed in 181.20s (0:03:01)
```

Full Anaconda pytest:

```text
1069 passed in 82.71s (0:01:22)
```

## Conclusion

Step91 accepted.

Step91 is a plan-and-guard step only. It does not run `FSIDriver3D`, does not
call `driver.run()`, does not execute simulation, and does not activate the
10-step dry run.

Step91 only plans and guards Step92:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run
```

Step92 may run exactly one 32^3 / 1024-particle / 10-step /
`moving_boundary` / engineering row with:

```text
geometry_type = squid_proxy
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
target_u_lbm = [0.0, 0.0, 0.0]
```

The only intended expansion from Step90 to Step92 is duration:

```text
n_lbm_steps = 5 -> 10
```

Step92 must not enable real geometry candidate data, link-area transfer, 48^3,
64^3, VTR output, or particle NPY output. Step92 must not change solver
formulas or claim physical validation, squid swimming, real squid validation,
or production readiness.
