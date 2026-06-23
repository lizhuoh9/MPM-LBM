# Step90 First User Simulation Dry Run

Step90 executes exactly one bounded first user simulation dry-run row planned
and guarded by Step89:

```text
campaign_id = step90_first_user_simulation_dry_run
row_id = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run
n_grid = 32
n_particles = 1024
n_lbm_steps = 5
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
executed_in_step90 = true
```

This is the first bounded user-facing dry run of the three-feature Step88
envelope extended from three to five LBM steps. It is still a diagnostic dry
run, not a physical squid validation or production simulation campaign.

Step90 keeps runtime geometry diagnostic-only: the geometry-motion report must
show no geometry-state mutation, no MPM particle displacement through runtime
geometry, no LBM `solid_phi` update through runtime geometry, no dynamic-solid
update, and no boundary-link recomputation through the runtime geometry path.

Step90 keeps wall velocity limited to `solid_vel_experimental` reporting:
the wall-velocity report must target LBM `solid_vel`, avoid direct LBM
population writes, avoid direct MPM/projector state writes, avoid bounce-back
formula edits, and stay within the configured velocity cap.

Step90 does not enable real geometry candidate data, link-area transfer, 48^3
or 64^3 grids, VTR output, particle NPY output, dense wall-velocity outputs, or
dense displacement outputs. It does not edit solver, diagnostics, vendored
external code, or real geometry candidate data.

Evidence is recorded under:

```text
outputs/step90_driver_runs/
outputs/step90_first_user_simulation_dry_run_matrix/
outputs/step90_first_user_simulation_dry_run_quality/
outputs/step90_activation_guard/
outputs/step90_step89_regression_guard/
outputs/step90_step88_regression_guard/
outputs/step90_step87_regression_guard/
outputs/step90_output_guard/
outputs/step90_artifact_manifest/
```

The accepted Step90 claim is only:

```text
first user simulation dry run completed for the bounded 32^3/1024-particle/5-step squid_proxy diagnostic envelope
```

Step90 does not claim physical validation, real squid validation, squid
swimming, squid actuation, grid convergence, solver-formula improvement, tau
migration, or production readiness.
