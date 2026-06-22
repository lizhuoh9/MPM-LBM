# Step78 Minimal Post-Gate Canonical Driver 5-Step Rebaseline Report

Step78 extends exactly one dimension from Step77: duration increases from three
LBM steps to five LBM steps. The run remains the same 32^3, 1024-particle,
moving-boundary engineering canonical `FSIDriver3D` row with one MPM substep per
LBM step.

Step78 keeps runtime geometry, wall velocity, real geometry, squid proxy,
link-area transfer, 48^3, 64^3, 10-step baseline, VTR output, particle NPY
output, tau migration, and solver formula changes disabled.

## Evidence

- `outputs/step78_post_gate_5step_rebaseline_matrix/post_gate_5step_rebaseline_matrix.json`
- `outputs/step78_post_gate_5step_rebaseline_quality/post_gate_5step_rebaseline_quality.json`
- `outputs/step78_activation_guard/activation_guard.json`
- `outputs/step78_output_guard/output_guard.json`
- `outputs/step78_step77_regression_guard/step77_regression_guard.json`
- `outputs/step78_artifact_manifest/artifact_summary.json`

## Required Run

```text
row_name = canonical_driver_moving_boundary_engineering_32_5step_rebaseline
campaign_id = step78_minimal_post_gate_canonical_driver_5step_rebaseline
n_grid = 32
n_particles = 1024
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
```

Expected driver-run files:

```text
outputs/step78_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_rebaseline/driver_config.json
outputs/step78_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_rebaseline/geo_all_fluid_32.dat
outputs/step78_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_rebaseline/diagnostics_timeseries.csv
outputs/step78_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_rebaseline/diagnostics_timeseries.npz
```

## Result

```text
post_gate_5step_rebaseline_matrix_pass = true
post_gate_5step_rebaseline_quality_pass = true
post_gate_5step_activation_guard_pass = true
output_guard_pass = true
step78_step77_regression_guard_pass = true
artifact_budget_pass = true
```

Required row summary:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
previous_rebaseline_step = Step77
completed_lbm_steps = 5
total_mpm_substeps = 5
diagnostics_row_count = 6
has_nan = false
has_inf = false
runtime_warning = false
runtime_hard_fail = false
stable = true
elapsed_seconds = 242.33026560000144
```

Key numeric diagnostics:

```text
rho_min_min = 0.9631504416465759
rho_max_max = 1.0382390022277832
lbm_max_v_max = 0.029648633673787117
mpm_min_J_min = 0.9996404051780701
mpm_max_speed_max = 1.5697649717330933
projected_mass_final = 0.027000000700354576
active_cell_count_final = 1210
bb_link_count_max = 2272
bb_max_correction_max = 0.006899189669638872
active_reaction_particle_count_final = 893
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

Step78 proves only a minimal post-gate canonical driver 5-step rebaseline. It
does not validate physical behavior, real squid behavior, grid convergence,
runtime geometry, wall velocity, real geometry, or production readiness.

Output guard summary:

```text
step78_required_driver_run_dir_count = 1
step78_optional_driver_run_dir_count = 0
step78_vtr_count = 0
step78_particle_npy_count = 0
step78_large_file_count = 0
step78_forbidden_file_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step78_total_size_mb = 0.13317489624023438
```

## Next Direction

After Step78, do not continue to a 10-step box baseline. The next phase should
start single-feature activation planning, beginning with runtime geometry
diagnostic-only plan and guard work.
