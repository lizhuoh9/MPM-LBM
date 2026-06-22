# Step81 Wall Velocity Single-Feature Activation Plan And Guard Report

Status: accepted.

Step81 is a plan-and-guard step only. Step81 does not run `FSIDriver3D`, does
not execute a simulation, and does not activate wall velocity in a driver run.

Step81 records and guards exactly one future Step82 row:

```text
canonical_driver_wall_velocity_solid_vel_32_3step_smoke
```

The planned Step82 row is limited to:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
boundary_motion_mode = prescribed_kinematic
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
```

## Evidence

```text
outputs/step81_wall_velocity_single_feature_activation_plan/wall_velocity_single_feature_activation_plan.json
outputs/step81_wall_velocity_single_feature_activation_guard/wall_velocity_single_feature_activation_guard.json
outputs/step81_step80_regression_guard/step80_regression_guard.json
outputs/step81_output_guard/output_guard.json
outputs/step81_artifact_manifest/artifact_summary.json
```

## Result

```text
step81_wall_velocity_single_feature_activation_plan_pass = true
step81_wall_velocity_single_feature_activation_guard_pass = true
step81_step80_regression_guard_pass = true
output_guard_pass = true
artifact_budget_pass = true
```

Activation plan summary:

```text
previous_step = Step80
previous_commit = a2fbdfa6a9af0f02901e16e92b276c2055755fe1
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
wall_velocity_activation_planned = true
wall_velocity_application_mode_planned_for_step82 = solid_vel_experimental
target_lbm_field_planned_for_step82 = solid_vel
step81_activation_feature_count = 0
planned_step82_activation_feature_count = 1
step82_allowed_row_name = canonical_driver_wall_velocity_solid_vel_32_3step_smoke
```

Activation guard summary:

```text
guard_row_count = 36
guard_pass_count = 36
apply_to_lbm_solid_vel_planned_for_step82 = true
apply_to_lbm_populations_planned_for_step82 = false
apply_to_mpm_planned_for_step82 = false
apply_to_projector_planned_for_step82 = false
modify_bounceback_formula_planned_for_step82 = false
jet_model_planned_for_step82 = false
actuation_claim_planned_for_step82 = false
runtime_geometry_planned_for_step82 = false
combined_runtime_geometry_wall_velocity_planned_for_step82 = false
real_geometry_planned_for_step82 = false
squid_proxy_planned_for_step82 = false
link_area_planned_for_step82 = false
write_vtk_planned_for_step82 = false
write_particles_planned_for_step82 = false
```

Step80 regression summary:

```text
artifact_check_count = 15
artifact_pass_count = 15
step80_activation_feature_count = 1
step80_runtime_geometry_enabled_count = 1
step80_wall_velocity_enabled_count = 0
step80_real_geometry_enabled_count = 0
step80_squid_proxy_enabled_count = 0
step80_link_area_enabled_count = 0
step80_vtr_count = 0
step80_particle_npy_count = 0
```

Output and artifact guard summary:

```text
step81_driver_run_dir_count = 0
step81_vtr_count = 0
step81_particle_npy_count = 0
step81_dense_wall_velocity_output_count = 0
step81_sparse_wall_velocity_output_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step81_file_count = 47
step81_total_size_mb = 0.20180511474609375
large_file_count = 0
protected_external_taichi_lbm3d_step81_file_count = 0
protected_real_geometry_candidates_step81_file_count = 0
```

Verification:

```text
focused Step81 pytest = 11 passed
trusted-environment full pytest = 987 passed
Anaconda full pytest = 987 passed
```

## Scope Guard

Step81 is a plan-and-guard step only.
Step81 does not run `FSIDriver3D`.
Step81 does not execute a simulation.
Step81 does not activate wall velocity in a driver run.
Step81 does not enable runtime geometry.
Step81 does not enable combined runtime geometry plus wall velocity.
Step81 does not enable real geometry.
Step81 does not enable squid proxy.
Step81 does not enable link-area transfer.
Step81 does not enable 48^3 or 64^3.
Step81 does not write VTR or particle NPY.
Step81 does not change solver formulas.
Step81 does not change tau semantics.
Step81 does not claim physical validation or production readiness.

## Next Direction

After Step81, the next step may be Step82 Wall Velocity Solid-Vel Canonical
Driver 3-Step Smoke. Step82 should run only:

```text
canonical_driver_wall_velocity_solid_vel_32_3step_smoke
```

Step82 must not enable runtime geometry, combined runtime geometry plus wall
velocity, real geometry, squid proxy behavior, link-area transfer, larger
grids, VTR output, particle NPY output, solver formula changes, tau migration,
or physical-production claims.
