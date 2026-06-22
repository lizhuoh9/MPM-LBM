# Step82 Wall Velocity Solid-Vel Canonical Driver Smoke

Step82 is the first post-gate wall-velocity single-feature driver run. It runs
exactly one canonical `FSIDriver3D` row:

```text
canonical_driver_wall_velocity_solid_vel_32_3step_smoke
```

## Scope

Step82 may:

- run one 32^3 / 1024-particle / 3-step moving-boundary engineering row
- enable `wall_velocity_application_mode = solid_vel_experimental`
- target only LBM `solid_vel`
- write `wall_velocity_application_report.json`
- write `boundary_motion_interface_report.json`
- write lightweight JSON, CSV, NPZ, DAT, and log evidence

Step82 may not:

- enable runtime geometry
- combine runtime geometry with wall velocity
- enable real geometry
- enable squid proxy behavior
- use link-area transfer
- add 48^3 or 64^3 rows
- write VTR or particle NPY output
- write dense or sparse wall velocity arrays
- change solver formulas or tau semantics
- claim moving-wall physics validation, real squid validation, or production readiness

## Executed Row

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
target_u_lbm = [0.0, 0.0, 0.0]
```

The zero `target_u_lbm` is a Step82 driver-row setting used to isolate the
wall-velocity cap smoke from the default background flow. It does not change
solver formulas or activate another feature.

## Evidence

```text
outputs/step82_driver_runs/canonical_driver_wall_velocity_solid_vel_32_3step_smoke/
outputs/step82_wall_velocity_solid_vel_smoke_matrix/wall_velocity_solid_vel_smoke_matrix.json
outputs/step82_wall_velocity_solid_vel_quality/wall_velocity_solid_vel_quality.json
outputs/step82_activation_guard/activation_guard.json
outputs/step82_step81_regression_guard/step81_regression_guard.json
outputs/step82_output_guard/output_guard.json
outputs/step82_artifact_manifest/artifact_summary.json
```

## Result

```text
step82_wall_velocity_solid_vel_smoke_matrix_pass = true
step82_wall_velocity_solid_vel_quality_pass = true
step82_activation_guard_pass = true
step82_step81_regression_guard_pass = true
output_guard_pass = true
artifact_budget_pass = true
```

Passing Step82 means the wall velocity `solid_vel_experimental` path completed
one bounded canonical driver smoke. It does not validate real moving-wall
physics, squid swimming, grid convergence, or production readiness.
