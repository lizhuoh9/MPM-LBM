# Step80 Runtime Geometry Diagnostic-Only Canonical Driver Smoke

Step80 runs exactly one canonical driver row that enables only runtime geometry
diagnostic-only interface reporting.

## Scope

Step80 may:

- call canonical `FSIDriver3D.run()` for one 32^3 / 1024-particle / 3-step row
- enable `geometry_motion_mode = prescribed_kinematic`
- enable `geometry_motion_application_mode = diagnostic_only`
- write `geometry_motion_interface_report.json`
- verify the report is finite, diagnostic-only, no-op, and has zero mutation flags
- write lightweight JSON, CSV, NPZ, DAT, log, report, and manifest evidence

Step80 may not:

- mutate geometry
- displace MPM particles
- update LBM `solid_phi`
- update LBM `solid_vel`
- update `dynamic_solid`
- recompute boundary links
- change moving bounce-back formulas
- enable wall velocity
- enable real geometry
- enable squid proxy behavior
- use link-area transfer
- add 48^3 or 64^3 rows
- write VTR or particle NPY output
- claim physical validation, real squid validation, or production readiness

## Required Row

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

## Result

```text
step80_runtime_geometry_diagnostic_only_smoke_matrix_pass = true
step80_runtime_geometry_diagnostic_only_quality_pass = true
step80_runtime_geometry_diagnostic_only_activation_guard_pass = true
output_guard_pass = true
step80_step79_regression_guard_pass = true
artifact_budget_pass = true
```

Driver row summary:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
completed_lbm_steps = 3
total_mpm_substeps = 3
diagnostics_row_count = 4
runtime_geometry_enabled = true
geometry_motion_interface_report_exists = true
geometry_motion_interface_report_pass = true
no_op_pass = true
mutation_flag_enabled_count = 0
stable = true
```

Passing Step80 means the runtime geometry diagnostic-only driver path can run.
It does not mean runtime deforming geometry, moving geometry physics, real
geometry, wall velocity, squid swimming, physical validation, or production
readiness is validated.
