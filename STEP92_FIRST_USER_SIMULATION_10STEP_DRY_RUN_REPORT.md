# Step92 First User Simulation 10-Step Dry Run Report

## Conclusion

Step92 accepted.

Step92 runs exactly one required first-user dry-run row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run
```

Correct Step92 claim:

```text
first user simulation dry run 32^3 / 10-step passed
```

Step92 is a duration-only expansion from the accepted Step90 dry run:

```text
Step90 n_lbm_steps = 5
Step92 n_lbm_steps = 10
only_duration_expansion_from_step90 = true
```

## Executed Row

The row used:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
```

The canonical driver was called:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
```

## Matrix Evidence

Artifact:

```text
outputs/step92_first_user_simulation_10step_dry_run_matrix/first_user_simulation_10step_dry_run_matrix.json
```

Summary:

```text
step92_first_user_simulation_10step_dry_run_matrix_pass = true
required_row_count = 1
optional_row_count = 0
required_stable_count = 1
activation_feature_count = 3
min_completed_lbm_steps = 10
min_diagnostics_row_count = 11
only_duration_expansion_from_step90 = true
previous_step90_n_lbm_steps = 5
step92_n_lbm_steps = 10
```

Observed dry-run numerics:

```text
completed_lbm_steps = 10
total_mpm_substeps = 10
diagnostics_row_count = 11
rho_min_min = 0.9936118125915527
rho_max_max = 1.0026592016220093
lbm_max_v_max = 0.005718602333217859
mpm_min_J_min = 0.998312771320343
mpm_max_speed_max = 0.01751340739428997
projected_mass_final = 0.022649124264717102
active_cell_count_final = 1759
bb_link_count_max = 2574
max_grid_reaction_norm_max = 4.21562253904995e-05
elapsed_seconds = 250.57026240000414
```

## Quality Evidence

Artifact:

```text
outputs/step92_first_user_simulation_10step_dry_run_quality/first_user_simulation_10step_dry_run_quality.json
```

Summary:

```text
step92_first_user_simulation_10step_dry_run_quality_pass = true
geometry_quality_report_pass_count = 1
geometry_motion_interface_report_pass_count = 1
wall_velocity_application_report_pass_count = 1
boundary_motion_interface_report_pass_count = 1
finite_wall_velocity_report_count = 1
capped_wall_velocity_report_count = 1
finite_max_grid_reaction_norm_count = 1
mutation_flag_enabled_count_max = 0
pass_count = 80
row_count = 80
```

## Driver Outputs

Step92 writes only the allowed driver-run files:

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

Step92 does not write:

```text
*.vtr
particle*.npy
dense_wall_velocity*.npy
sparse_wall_velocity*.npy
dense_displacement*.npy
displaced_particles*.npy
raw geometry output
real geometry candidate output
optional driver run dirs
```

## Output Guard Evidence

Artifact:

```text
outputs/step92_output_guard/output_guard.json
```

Summary:

```text
output_guard_pass = true
artifact_budget_pass = true
step92_required_driver_run_dir_count = 1
step92_optional_driver_run_dir_count = 0
step92_vtr_count = 0
step92_particle_npy_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step92_total_size_bytes = 734392
step92_total_size_mb = 0.7003707885742188
```

## Regression Evidence

Step91 regression guard:

```text
step92_step91_regression_guard_pass = true
artifact_pass_count = 7
artifact_check_count = 7
step91_first_user_simulation_10step_dry_run_plan_pass = true
step91_first_user_simulation_10step_dry_run_guard_pass = true
step91_activation_feature_count = 0
planned_step92_activation_feature_count = 3
step91_driver_run_dir_count = 0
step91_vtr_count = 0
step91_particle_npy_count = 0
step92_allowed_n_lbm_steps = 10
```

Step90 regression guard:

```text
step92_step90_regression_guard_pass = true
artifact_pass_count = 8
artifact_check_count = 8
step90_activation_feature_count = 3
step90_squid_proxy_enabled_count = 1
step90_runtime_geometry_enabled_count = 1
step90_wall_velocity_enabled_count = 1
step90_combined_runtime_geometry_wall_velocity_enabled_count = 1
step90_completed_lbm_steps = 5
step90_real_geometry_candidate_enabled_count = 0
step90_link_area_enabled_count = 0
step90_vtr_count = 0
step90_particle_npy_count = 0
```

Step89 regression guard:

```text
step92_step89_regression_guard_pass = true
artifact_pass_count = 7
artifact_check_count = 7
step89_activation_feature_count = 0
planned_step90_activation_feature_count = 3
step89_driver_run_dir_count = 0
step89_vtr_count = 0
step89_particle_npy_count = 0
```

## Artifact Manifest

Artifact:

```text
outputs/step92_artifact_manifest/artifact_summary.json
```

Final summary after verification-log refresh:

```text
artifact_budget_pass = true
step92_file_count = 77
step92_total_size_bytes = 358448
step92_total_size_mb = 0.3418426513671875
large_file_count = 0
private_absolute_path_count = 0
raw_geometry_file_count = 0
protected_external_taichi_lbm3d_step92_file_count = 0
protected_real_geometry_candidates_step92_file_count = 0
step92_required_driver_run_dir_count = 1
step92_vtr_count = 0
step92_particle_npy_count = 0
```

The manifest was refreshed after focused, Taichi full, and Anaconda full pytest
logs were written.

## Verification

Focused Step92 contract tests:

```text
7 passed in 1.42s
```

Full trusted Taichi pytest:

```text
1076 passed in 183.79s (0:03:03)
```

Full Anaconda pytest:

```text
1076 passed in 74.79s (0:01:14)
```

## Boundaries

Step92 does not mutate geometry.
Step92 does not displace MPM particles through runtime geometry.
Step92 does not update LBM `solid_phi` through runtime geometry.
Step92 does not directly write LBM populations through wall velocity.
Step92 does not modify moving bounce-back formulas.
Step92 does not directly update MPM state through wall velocity.
Step92 does not directly update projector state through wall velocity.
Step92 does not enable real geometry candidate data.
Step92 does not enable link-area transfer.
Step92 does not enable 48^3 or 64^3.
Step92 does not write VTR or particle NPY.
Step92 does not claim squid swimming.
Step92 does not claim real squid validation.
Step92 does not claim physical validation or production readiness.
