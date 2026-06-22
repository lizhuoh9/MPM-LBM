# Step82 Wall Velocity Solid-Vel Canonical Driver Smoke Report

Status: accepted.

Step82 runs exactly one required canonical driver row:

```text
canonical_driver_wall_velocity_solid_vel_32_3step_smoke
```

## Driver Row

```text
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
target_u_lbm = [0.0, 0.0, 0.0]
completed_lbm_steps = 3
total_mpm_substeps = 3
diagnostics_row_count = 4
```

The zero background target velocity is a Step82 row-local config choice to
isolate the `solid_vel` application cap smoke. It does not change solver
formulas, tau semantics, or runtime code.

## Evidence Summary

```text
step82_wall_velocity_solid_vel_smoke_matrix_pass = true
step82_wall_velocity_solid_vel_quality_pass = true
step82_activation_guard_pass = true
step82_step81_regression_guard_pass = true
output_guard_pass = true
artifact_budget_pass = true
```

The smoke row produced:

```text
rho_min_min = 0.9995806813240051
rho_max_max = 1.0002126693725586
lbm_max_v_max = 0.00042992818634957075
mpm_min_J_min = 0.9998470544815063
mpm_max_speed_max = 0.004584999289363623
projected_mass_final = 0.02699996903538704
active_cell_count_final = 1320
bb_link_count_max = 2272
max_grid_reaction_norm_max = 4.052095755469054e-05
has_nan = false
has_inf = false
stable = true
```

Wall velocity report:

```text
wall_velocity_application_report_pass = true
target_lbm_field = solid_vel
application_policy = additive_capped
apply_to_lbm_solid_vel = true
apply_to_lbm_populations = false
apply_to_mpm = false
apply_to_projector = false
modify_bounceback_formula = false
jet_model_enabled = false
actuation_claim_enabled = false
applied_cell_count = 648
max_applied_velocity_norm = 0.0005021311353590662
wall_velocity_cap_lbm = 0.01
finite_pass = true
cap_pass = true
lbm_population_update_count = 0
```

Boundary motion report:

```text
boundary_motion_interface_report_pass = true
boundary_motion_diagnostic_only = true
boundary_motion_mode = prescribed_kinematic
```

Feature boundary:

```text
activation_feature_count = 1
wall_velocity_enabled_count = 1
runtime_geometry_enabled_count = 0
combined_runtime_geometry_wall_velocity_enabled_count = 0
real_geometry_enabled_count = 0
squid_proxy_enabled_count = 0
link_area_enabled_count = 0
grid_48_enabled_count = 0
grid_64_enabled_count = 0
write_vtk = false
write_particles = false
```

Output boundary:

```text
step82_required_driver_run_dir_count = 1
step82_optional_driver_run_dir_count = 0
step82_vtr_count = 0
step82_particle_npy_count = 0
step82_dense_wall_velocity_output_count = 0
step82_sparse_wall_velocity_output_count = 0
step82_raw_geometry_output_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step82_total_size_mb = 0.3398256301879883
```

## Validation Commands

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step82_wall_velocity_solid_vel_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step82_wall_velocity_solid_vel_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step82_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step82_step81_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step82_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step82_artifact_manifest.py
```

Focused and full pytest logs are stored under `logs/step82_*.log`.

## Claim Boundary

Step82 proves only this bounded claim:

```text
wall velocity solid_vel experimental canonical driver 3-step smoke passed
```

Step82 does not prove moving-wall physics validation, real squid swimming, grid
convergence, or production readiness.
