# Step81 Wall Velocity Single-Feature Activation Plan And Guard

Step81 is a plan-and-guard step only. It prepares the single allowed Step82
wall-velocity smoke row and proves that Step81 itself does not run a simulation.

## Scope

Step81 may:

- record the Step82 wall-velocity-only canonical driver smoke plan
- validate the Step82 row name, grid size, particle count, and duration
- validate the existing Step36 `solid_vel_experimental` wall-velocity application contract
- prove Step81 has zero activated runtime features
- prove Step80 evidence remains green
- write lightweight JSON, CSV, log, report, and manifest evidence

Step81 may not:

- run `FSIDriver3D`
- call `driver.run()`
- initialize Taichi
- activate wall velocity in a driver run
- enable runtime geometry
- combine runtime geometry with wall velocity
- enable real geometry
- enable squid proxy behavior
- use link-area transfer
- add 48^3 or 64^3 rows
- write VTR or particle NPY output
- change solver formulas or tau semantics
- claim physical validation, real squid validation, or production readiness

## Planned Step82 Row

```text
row_name = canonical_driver_wall_velocity_solid_vel_32_3step_smoke
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

The Step82 plan allows wall velocity to target only `solid_vel`:

```text
apply_to_lbm_solid_vel = true
apply_to_lbm_populations = false
apply_to_mpm = false
apply_to_projector = false
modify_bounceback_formula = false
jet_model_enabled = false
actuation_claim_enabled = false
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
```

Passing Step81 means the repository has a committed plan and guard for a later
wall-velocity-only Step82 smoke. It does not mean wall velocity has already run
through the canonical driver in the post-gate campaign.
