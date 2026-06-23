# Step91 First User Simulation 10-Step Dry Run Plan And Guard

Step91 is plan-and-guard only. It prepares a future Step92 ten-step dry run
without running a driver row in Step91.

Planned Step92 row:

```text
row_id = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run
n_grid = 32
n_particles = 1024
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
```

The only intended expansion from Step90 to Step92 is duration:

```text
n_lbm_steps = 5 -> 10
```

Step91 does not call `FSIDriver3D`, does not call `driver.run()`, and does not
execute simulation. Step91 also does not modify solver, diagnostics, vendored
external code, or real geometry candidate data.

Step92 remains bounded by this plan: no real geometry candidate data, no
link-area transfer, no 48^3 or 64^3 row, no VTR output, no particle NPY output,
no solver formula changes, and no physical-validation, real-squid-validation,
squid-swimming, squid-actuation, or production-readiness claim.

Evidence is recorded under:

```text
outputs/step91_first_user_simulation_10step_dry_run_plan/
outputs/step91_first_user_simulation_10step_dry_run_guard/
outputs/step91_step90_regression_guard/
outputs/step91_step89_regression_guard/
outputs/step91_step88_regression_guard/
outputs/step91_output_guard/
outputs/step91_artifact_manifest/
```
