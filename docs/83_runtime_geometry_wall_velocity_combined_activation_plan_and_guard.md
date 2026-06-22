# Step83 Runtime Geometry Wall Velocity Combined Activation Plan And Guard

Step83 is a plan-and-guard step only. It prepares the single allowed Step84
combined smoke row and proves that Step83 itself does not run a simulation.

## Scope

Step83 may:

- record the Step84 runtime geometry diagnostic-only plus wall velocity plan
- validate the Step84 row name, grid size, particle count, duration, modes, and configs
- prove Step83 has zero activated runtime features
- prove Step80 runtime geometry diagnostic-only evidence remains green
- prove Step82 wall velocity `solid_vel` evidence remains green
- write lightweight JSON, CSV, log, report, and manifest evidence

Step83 may not:

- run `FSIDriver3D`
- call `driver.run()`
- initialize Taichi
- execute a simulation
- activate the combined runtime geometry plus wall velocity path in a driver run
- enable real geometry
- enable squid proxy behavior
- use link-area transfer
- add 48^3 or 64^3 rows
- write VTR or particle NPY output
- change solver formulas or tau semantics
- claim physical validation, real squid validation, or production readiness

## Planned Step84 Row

```text
row_name = canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
boundary_motion_mode = prescribed_kinematic
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
```

The planned Step84 row reuses:

```text
geometry_motion_application_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json
wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json
```

## Evidence

```text
outputs/step83_runtime_geometry_wall_velocity_combined_activation_plan/runtime_geometry_wall_velocity_combined_activation_plan.json
outputs/step83_runtime_geometry_wall_velocity_combined_activation_guard/runtime_geometry_wall_velocity_combined_activation_guard.json
outputs/step83_step82_regression_guard/step82_regression_guard.json
outputs/step83_step80_regression_guard/step80_regression_guard.json
outputs/step83_output_guard/output_guard.json
outputs/step83_artifact_manifest/artifact_summary.json
```

## Result

```text
step83_runtime_geometry_wall_velocity_combined_activation_plan_pass = true
step83_runtime_geometry_wall_velocity_combined_activation_guard_pass = true
step83_step82_regression_guard_pass = true
step83_step80_regression_guard_pass = true
output_guard_pass = true
artifact_budget_pass = true
```

Passing Step83 means the combined runtime geometry diagnostic-only plus wall
velocity `solid_vel` smoke is planned and guarded for Step84. It does not mean
the combined smoke has run.
