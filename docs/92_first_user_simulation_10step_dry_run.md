# Step92 First User Simulation 10-Step Dry Run

Step92 executes exactly one bounded first user simulation 10-step dry-run row planned
and guarded by Step91:

```text
campaign_id = step92_first_user_simulation_10step_dry_run
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
executed_in_step92 = true
```

This is the accepted Step90 first-user dry-run envelope extended from five to
ten LBM steps. It is still a diagnostic dry run, not a physical squid
validation or production simulation campaign.

Step92 keeps runtime geometry diagnostic-only: the geometry-motion report must
show no geometry-state mutation, no MPM particle displacement through runtime
geometry, no LBM `solid_phi` update through runtime geometry, no dynamic-solid
update, and no boundary-link recomputation through the runtime geometry path.

Step92 keeps wall velocity limited to `solid_vel_experimental` reporting:
the wall-velocity report must target LBM `solid_vel`, avoid direct LBM
population writes, avoid direct MPM/projector state writes, avoid bounce-back
formula edits, and stay within the configured velocity cap.

Step92 does not enable real geometry candidate data, link-area transfer, 48^3
or 64^3 grids, VTR output, particle NPY output, dense wall-velocity outputs, or
dense displacement outputs. It does not edit solver, diagnostics, vendored
external code, or real geometry candidate data.

Evidence is recorded under:

```text
outputs/step92_driver_runs/
outputs/step92_first_user_simulation_10step_dry_run_matrix/
outputs/step92_first_user_simulation_10step_dry_run_quality/
outputs/step92_activation_guard/
outputs/step92_step91_regression_guard/
outputs/step92_step90_regression_guard/
outputs/step92_step89_regression_guard/
outputs/step92_output_guard/
outputs/step92_artifact_manifest/
```

The accepted Step92 claim is only:

```text
first user simulation 10-step dry run completed for the bounded 32^3/1024-particle/10-step squid_proxy diagnostic envelope
```

Step92 does not claim physical validation, real squid validation, squid
swimming, squid actuation, grid convergence, solver-formula improvement, tau
migration, or production readiness.
