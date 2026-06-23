# Step89 First User Simulation Dry Run Plan And Guard

Step89 is plan-and-guard only. It prepares the first bounded user simulation
dry run for Step90 without running a driver row in Step89.

Planned Step90 row:

```text
row_id = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run
n_grid = 32
n_particles = 1024
n_lbm_steps = 5
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

Step89 does not call `FSIDriver3D`, does not call `driver.run()`, and does not
execute simulation. Step89 also does not modify solver, diagnostics, vendored
external code, or real geometry candidate data.

Step90 remains bounded by the Step89 plan: no real geometry candidate data, no
link-area transfer, no 48^3 or 64^3 row, no VTR output, no particle NPY output,
no solver formula changes, and no physical-validation, real-squid-validation,
squid-swimming, squid-actuation, or production-readiness claim.

Evidence is recorded under:

```text
outputs/step89_first_user_simulation_dry_run_plan/
outputs/step89_first_user_simulation_dry_run_guard/
outputs/step89_step88_regression_guard/
outputs/step89_step87_regression_guard/
outputs/step89_step86_regression_guard/
outputs/step89_output_guard/
outputs/step89_artifact_manifest/
```
