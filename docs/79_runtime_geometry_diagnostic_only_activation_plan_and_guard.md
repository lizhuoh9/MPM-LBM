# Step79 Runtime Geometry Diagnostic-Only Activation Plan And Guard

Step79 is a plan-and-guard step for the future Step80 runtime geometry
diagnostic-only smoke. It does not run `FSIDriver3D`, does not execute a
simulation, does not apply runtime geometry to solver state, and does not mutate
geometry.

## Scope

Step79 may:

- record the Step80 runtime geometry diagnostic-only activation plan
- check the plan against a guard policy
- confirm Step78 evidence remains green
- prove Step79 outputs stay lightweight and contain no driver run artifacts
- write JSON, CSV, log, report, documentation, and manifest evidence

Step79 may not:

- call `FSIDriver3D.run()`
- execute a simulation
- activate runtime geometry simulation
- mutate geometry
- change solver formulas or tau semantics
- activate wall velocity
- activate real geometry
- activate squid proxy behavior
- use link-area transfer
- add 48^3 or 64^3 rows
- add a 10-step baseline
- write VTR or particle NPY outputs
- claim physical validation, real squid validation, or production readiness

## Planned Step80 Row

Step79 authorizes exactly one future Step80 row:

```text
row_name = canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
```

The Step80 plan keeps wall velocity, real geometry, squid proxy behavior,
link-area transfer, 48^3, 64^3, VTR output, and particle NPY output disabled.

## Interpretation

Passing Step79 means runtime geometry diagnostic-only single-feature activation
is planned and guarded for Step80. It does not mean runtime geometry simulation,
moving geometry, deforming geometry, real geometry, wall velocity, squid
swimming, physical validation, or production readiness works.

Evidence:

```text
outputs/step79_runtime_geometry_diagnostic_only_activation_plan/runtime_geometry_diagnostic_only_activation_plan.json
outputs/step79_runtime_geometry_diagnostic_only_activation_guard/runtime_geometry_diagnostic_only_activation_guard.json
outputs/step79_step78_regression_guard/step78_regression_guard.json
outputs/step79_output_guard/output_guard.json
outputs/step79_artifact_manifest/artifact_summary.json
```
