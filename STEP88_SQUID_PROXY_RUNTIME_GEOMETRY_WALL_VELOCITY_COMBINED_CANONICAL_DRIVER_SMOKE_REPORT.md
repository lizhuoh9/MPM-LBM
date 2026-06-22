# Step88 Squid Proxy Runtime Geometry Wall Velocity Combined Canonical Driver Smoke Report

## Goal

Step88 executes the single three-feature canonical-driver smoke row planned by
Step87. It combines:

- procedural static `squid_proxy` geometry from Step86;
- runtime geometry `diagnostic_only` interface reporting from Step80/Step84;
- wall velocity `solid_vel_experimental` application reporting from Step82/Step84.

Correct Step88 claim:

```text
squid_proxy + runtime geometry diagnostic-only + wall velocity solid_vel combined canonical driver 3-step smoke passed
```

Step88 is not real squid validation, squid swimming, squid actuation, physical
validation, grid convergence, or production readiness.

## Starting Point

Required starting commit:

```text
082d3b0f89c2ca0591d65812b3b48ff4b26caf58
```

Step87 remains the accepted predecessor: it planned and guarded the future
Step88 row but did not run `FSIDriver3D`.

## Executed Row

```text
campaign_id = step88_squid_proxy_runtime_geometry_wall_velocity_combined_canonical_driver_smoke
row_id = canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
boundary_motion_mode = prescribed_kinematic
geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
executed_in_step88 = true
```

No optional row was added or run.

`target_u_lbm = [0.0, 0.0, 0.0]` is a Step88 row-local config choice. Step87
did not freeze `target_u_lbm`, and the zero background flow isolates the wall
velocity `solid_vel` cap/report contract from the default squid_proxy background
flow. This is not a runtime solver change.

## Evidence Summary

Smoke matrix:

```text
step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix_pass = true
required_row_count = 1
optional_row_count = 0
required_stable_count = 1
driver_run_called_count = 1
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_count = 0
activation_feature_count = 3
procedural_geometry_enabled_count = 1
squid_proxy_enabled_count = 1
runtime_geometry_enabled_count = 1
wall_velocity_enabled_count = 1
combined_runtime_geometry_wall_velocity_enabled_count = 1
real_geometry_candidate_enabled_count = 0
real_geometry_enabled_count = 0
link_area_enabled_count = 0
grid_48_enabled_count = 0
grid_64_enabled_count = 0
write_vtk_count = 0
write_particles_count = 0
runtime_code_changed = false
solver_behavior_changed = false
```

Runtime smoke values:

```text
completed_lbm_steps = 3
total_mpm_substeps = 3
diagnostics_row_count = 4
rho_min_min = 0.9994185566902161
rho_max_max = 1.000001072883606
lbm_max_v_max = 0.00046188393025659025
mpm_min_J_min = 0.9997814893722534
mpm_max_speed_max = 0.0054171099327504635
projected_mass_final = 0.02264912612736225
active_cell_count_final = 1759
bb_link_count_max = 2574
active_reaction_particle_count_final = 987
max_grid_reaction_norm_max = 4.215420631226152e-05
```

Geometry quality:

```text
geometry_quality_report_pass_count = 1
geometry_quality_strict = false
quality_report_occupied_count = 774
quality_report_surface_voxel_count = 358
quality_report_touches_domain_boundary = false
sampling_particle_count = 1024
mantle_particle_count = 867
head_particle_count = 189
arms_particle_count = 52
left_fin_particle_count = 23
right_fin_particle_count = 22
```

Runtime geometry and wall-velocity reports:

```text
geometry_motion_interface_report_pass_count = 1
mutation_flag_enabled_count_max = 0
boundary_motion_interface_report_pass_count = 1
wall_velocity_application_report_pass_count = 1
finite_wall_velocity_report_count = 1
capped_wall_velocity_report_count = 1
applied_cell_count = 648
max_applied_velocity_norm = 0.0005021311353590662
wall_velocity_cap_lbm = 0.01
lbm_population_update_count = 0
modify_bounceback_formula = false
```

Output guard:

```text
output_guard_pass = true
row_count = 48
pass_count = 48
step88_required_driver_run_dir_count = 1
step88_optional_driver_run_dir_count = 0
step88_vtr_count = 0
step88_particle_npy_count = 0
step88_raw_geometry_output_count = 0
step88_real_geometry_candidate_output_count = 0
step88_dense_wall_velocity_output_count = 0
step88_dense_displacement_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
```

Regression guards:

```text
step88_step87_regression_guard_pass = true
step87_activation_feature_count = 0
planned_step88_activation_feature_count = 3
step87_driver_run_dir_count = 0

step88_step86_regression_guard_pass = true
step86_activation_feature_count = 1
step86_squid_proxy_enabled_count = 1
step86_runtime_geometry_enabled_count = 0
step86_wall_velocity_enabled_count = 0
step86_combined_runtime_geometry_wall_velocity_enabled_count = 0

step88_step84_regression_guard_pass = true
step84_activation_feature_count = 2
step84_runtime_geometry_enabled_count = 1
step84_wall_velocity_enabled_count = 1
step84_combined_runtime_geometry_wall_velocity_enabled_count = 1
step84_squid_proxy_enabled_count = 0

step88_step82_regression_guard_pass = true
step82_wall_velocity_enabled_count = 1
step82_runtime_geometry_enabled_count = 0
step82_squid_proxy_enabled_count = 0

step88_step80_regression_guard_pass = true
step80_runtime_geometry_enabled_count = 1
step80_wall_velocity_enabled_count = 0
step80_squid_proxy_enabled_count = 0
```

Artifact manifest:

```text
artifact_budget_pass = true
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step88_file_count = 0
protected_real_geometry_candidates_step88_file_count = 0
raw_geometry_file_count = 0
step88_required_driver_run_dir_count = 1
step88_particle_npy_count = 0
step88_vtr_count = 0
```

The exact file count and byte total are recorded in
`outputs/step88_artifact_manifest/artifact_summary.json`; the report does not
duplicate those self-referential values.

## Driver Output

The required driver run directory is:

```text
outputs/step88_driver_runs/canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

It contains only the allowed run artifacts:

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

No VTR, particle NPY, dense wall-velocity/displacement, displaced-particle,
raw geometry, real-geometry-candidate, or optional driver-run directory is
produced.

## Boundaries

Step88 does not edit runtime solver or diagnostics code. It does not change
LBM, MPM, coupling, moving-boundary, wall-velocity, geometry-motion, tau, or
bounce-back formulas.

Step88 keeps real geometry candidate data, link-area transfer, 48^3, 64^3, VTR
output, particle NPY output, dense wall-velocity output, dense displacement
output, physical-validation claims, real squid validation claims, squid
swimming claims, squid actuation claims, and production-readiness claims closed.

The `squid_proxy` geometry remains a procedural proxy. The runtime geometry path
is diagnostic-only/no-op with zero mutation flags. The wall velocity path targets
LBM `solid_vel` only and does not write LBM populations or modify bounce-back
formulas.

## Verification

Focused Step88 contract tests:

```text
trusted-taichi-python -W ignore -m pytest -q tests\test_step88_*.py
10 passed in 1.46s
```

Full pytest with the trusted Taichi interpreter:

```text
trusted-taichi-python -W ignore -m pytest -q
1050 passed in 138.06s
```

Full pytest with the Anaconda interpreter:

```text
anaconda-python -W ignore -m pytest -q
1050 passed in 61.65s
```

Final Step88 output and artifact guards:

```text
baseline_tests/run_step88_output_guard.py
[OK] Step88 output guard finished

baseline_tests/run_step88_artifact_manifest.py
[OK] Step88 artifact manifest finished
```
