# Step77 Minimal Post-Gate Canonical Driver 3-Step Rebaseline Report

Step77 extends exactly one dimension from Step76: duration increases from one
LBM step to three LBM steps. The run remains the same 32^3, 1024-particle,
moving-boundary engineering canonical `FSIDriver3D` row with one MPM substep per
LBM step.

Step77 keeps runtime geometry, wall velocity, real geometry, squid proxy,
link-area transfer, 48^3, 64^3, VTR output, particle NPY output, tau migration,
and solver formula changes disabled.

## Evidence

- `outputs/step77_post_gate_3step_rebaseline_matrix/post_gate_3step_rebaseline_matrix.json`
- `outputs/step77_post_gate_3step_rebaseline_quality/post_gate_3step_rebaseline_quality.json`
- `outputs/step77_activation_guard/activation_guard.json`
- `outputs/step77_output_guard/output_guard.json`
- `outputs/step77_step76_regression_guard/step76_regression_guard.json`
- `outputs/step77_artifact_manifest/artifact_summary.json`

## Required Run

```text
row_name = canonical_driver_moving_boundary_engineering_32_3step_rebaseline
campaign_id = step77_minimal_post_gate_canonical_driver_3step_rebaseline
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
```

Expected driver-run files:

```text
outputs/step77_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_rebaseline/driver_config.json
outputs/step77_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_rebaseline/geo_all_fluid_32.dat
outputs/step77_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_rebaseline/diagnostics_timeseries.csv
outputs/step77_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_rebaseline/diagnostics_timeseries.npz
```

## Result

```text
post_gate_3step_rebaseline_matrix_pass = true
post_gate_3step_rebaseline_quality_pass = true
post_gate_3step_activation_guard_pass = true
output_guard_pass = true
step77_step76_regression_guard_pass = true
artifact_budget_pass = true
```

Required row summary:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
previous_rebaseline_step = Step76
completed_lbm_steps = 3
total_mpm_substeps = 3
diagnostics_row_count = 4
has_nan = false
has_inf = false
runtime_warning = false
runtime_hard_fail = false
stable = true
elapsed_seconds = 239.11242480002693
```

Key numeric diagnostics:

```text
rho_min_min = 0.9631504416465759
rho_max_max = 1.037545919418335
lbm_max_v_max = 0.028745334595441818
mpm_min_J_min = 0.9998476505279541
mpm_max_speed_max = 1.5669373273849487
projected_mass_final = 0.02699998766183853
active_cell_count_final = 1320
bb_link_count_max = 2272
bb_max_correction_max = 0.006872159894555807
active_reaction_particle_count_final = 892
max_grid_reaction_norm_max = 4.0519902540836483e-05
```

## Scope Guard

```text
runtime_geometry_enabled = false
wall_velocity_enabled = false
combined_runtime_geometry_wall_velocity_enabled = false
real_geometry_enabled = false
squid_proxy_enabled = false
link_area_enabled = false
grid_48_enabled = false
grid_64_enabled = false
write_vtk = false
write_particles = false
activation_feature_count = 0
```

Step77 proves only a minimal post-gate canonical driver 3-step rebaseline. It
does not validate physical behavior, real squid behavior, grid convergence,
runtime geometry, wall velocity, real geometry, or production readiness.

Output guard summary:

```text
step77_required_driver_run_dir_count = 1
step77_optional_driver_run_dir_count = 0
step77_vtr_count = 0
step77_particle_npy_count = 0
step77_large_file_count = 0
step77_forbidden_file_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step77_total_size_mb = 0.13200092315673828
```
