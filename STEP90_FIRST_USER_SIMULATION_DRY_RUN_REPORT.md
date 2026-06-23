# Step90 First User Simulation Dry Run Report

## Goal

Step90 executes exactly one first user simulation dry-run row authorized by
Step89:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run
```

Correct Step90 claim:

```text
first user simulation dry run completed for the bounded 32^3/1024-particle/5-step squid_proxy diagnostic envelope
```

Step90 does not claim production simulation readiness, physical validation,
real squid validation, squid swimming, squid actuation, grid convergence,
solver-formula improvement, or tau migration.

## Starting Point

Required starting commit:

```text
0a20bb93f784c707c5155fa5105d6cce40b47e6a
```

Step89 remains the accepted predecessor: it planned and guarded exactly one
future Step90 row without running `FSIDriver3D`.

## Executed Row

Step90 executed exactly one required row:

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
```

The row was executed through canonical `src.mpm_lbm.sim.drivers.fsi_driver`.
No legacy driver implementation was used.

## Evidence Summary

First user dry-run matrix:

```text
step90_first_user_simulation_dry_run_matrix_pass = true
row_count = 1
required_row_count = 1
required_stable_count = 1
optional_row_count = 0
driver_run_called_count = 1
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_count = 0
activation_feature_count = 3
squid_proxy_enabled_count = 1
runtime_geometry_enabled_count = 1
wall_velocity_enabled_count = 1
combined_runtime_geometry_wall_velocity_enabled_count = 1
min_completed_lbm_steps = 5
min_total_mpm_substeps = 5
min_diagnostics_row_count = 6
has_nan_count = 0
has_inf_count = 0
slowest_elapsed_seconds = 349.7978488999943
```

Stability counters:

```text
min_rho_min = 0.9943161606788635
max_rho_max = 1.000001072883606
max_lbm_max_v = 0.0036245593801140785
min_mpm_min_J = 0.999478816986084
max_mpm_max_speed = 0.009026913903653622
projected_mass_final = 0.02264910563826561
active_cell_count_final = 1759
bb_link_count_max = 2574
active_reaction_particle_count_final = 987
max_grid_reaction_norm_max = 4.2154577386099845e-05
```

Geometry, motion, and wall-velocity evidence:

```text
geometry_quality_report_pass_count = 1
geometry_motion_interface_report_pass_count = 1
boundary_motion_interface_report_pass_count = 1
wall_velocity_application_report_pass_count = 1
mutation_flag_enabled_count_max = 0
applied_cell_count = 648
max_applied_velocity_norm = 0.005866361313097195
wall_velocity_cap_lbm = 0.01
lbm_population_update_count = 0
```

Output guard:

```text
output_guard_pass = true
artifact_budget_pass = true
step90_required_driver_run_dir_count = 1
step90_optional_driver_run_dir_count = 0
step90_vtr_count = 0
step90_particle_npy_count = 0
step90_raw_geometry_output_count = 0
step90_real_geometry_candidate_output_count = 0
step90_dense_wall_velocity_output_count = 0
step90_sparse_wall_velocity_output_count = 0
step90_dense_displacement_output_count = 0
step90_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step90_total_size_mb = 0.6828508377075195
```

Artifact manifest:

```text
artifact_budget_pass = true
step90_file_count = 76
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step90_file_count = 0
protected_real_geometry_candidates_step90_file_count = 0
raw_geometry_file_count = 0
step90_required_driver_run_dir_count = 1
step90_particle_npy_count = 0
step90_vtr_count = 0
```

The exact self-referential Step90 byte total is recorded in
`outputs/step90_artifact_manifest/artifact_summary.json`.

Regression guards:

```text
step90_step89_regression_guard_pass = true
step89_activation_feature_count = 0
planned_step90_activation_feature_count = 3
step89_driver_run_dir_count = 0
step89_vtr_count = 0
step89_particle_npy_count = 0

step90_step88_regression_guard_pass = true
step88_activation_feature_count = 3
step88_squid_proxy_enabled_count = 1
step88_runtime_geometry_enabled_count = 1
step88_wall_velocity_enabled_count = 1
step88_vtr_count = 0
step88_particle_npy_count = 0

step90_step87_regression_guard_pass = true
step87_activation_feature_count = 0
planned_step88_activation_feature_count = 3
step87_driver_run_dir_count = 0
step87_vtr_count = 0
step87_particle_npy_count = 0
```

## Generated Driver Artifacts

The required driver run directory is:

```text
outputs/step90_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run/
```

It contains only the allowed lightweight files:

```text
boundary_motion_interface_report.json
diagnostics_timeseries.csv
diagnostics_timeseries.npz
driver_config.json
driver_timing.json
geo_all_fluid_32.dat
geometry_motion_interface_report.json
geometry_quality_report.json
wall_velocity_application_report.json
```

## Boundaries

Step90 does not edit runtime solver or diagnostics code. It does not change
LBM, MPM, coupling, moving-boundary, wall-velocity, geometry-motion, tau, or
bounce-back formulas.

Step90 keeps real geometry candidate data, link-area transfer, 48^3, 64^3, VTR
output, particle NPY output, dense wall-velocity output, dense displacement
output, physical-validation claims, real squid validation claims, squid
swimming claims, squid actuation claims, and production-readiness claims
closed.

## Verification

Expected red before artifacts:

```text
7 failed
```

Focused Step90 contract tests after evidence generation:

```text
7 passed in 1.34s
```

Full trusted Taichi pytest:

```text
1063 passed in 168.27s (0:02:48)
```

Full Anaconda pytest:

```text
1063 passed in 61.15s (0:01:01)
```

## Conclusion

Step90 accepted.

Step90 executed the first user simulation dry run exactly inside the Step89
authorization envelope. The run completed five LBM steps at 32^3 with 1024
particles, procedural `squid_proxy` geometry, runtime geometry diagnostic-only
reporting, wall velocity `solid_vel_experimental` reporting, and row-local zero
background target velocity.

The result is a bounded first user dry-run pass only. It is not physical
validation, real squid validation, squid swimming, squid actuation, grid
convergence, production readiness, or permission to enable real geometry,
link-area transfer, larger grids, VTR output, or particle NPY output.
