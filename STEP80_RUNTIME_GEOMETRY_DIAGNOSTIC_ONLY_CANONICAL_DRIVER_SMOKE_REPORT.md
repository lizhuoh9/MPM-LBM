# Step80 Runtime Geometry Diagnostic-Only Canonical Driver Smoke Report

Status: accepted.

Step80 runs exactly one required canonical driver row:

```text
canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke
```

The row uses:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
```

## Evidence

```text
outputs/step80_driver_runs/canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke/
outputs/step80_runtime_geometry_diagnostic_only_smoke_matrix/runtime_geometry_diagnostic_only_smoke_matrix.json
outputs/step80_runtime_geometry_diagnostic_only_quality/runtime_geometry_diagnostic_only_quality.json
outputs/step80_activation_guard/activation_guard.json
outputs/step80_output_guard/output_guard.json
outputs/step80_step79_regression_guard/step79_regression_guard.json
outputs/step80_artifact_manifest/artifact_summary.json
```

## Result

```text
step80_runtime_geometry_diagnostic_only_smoke_matrix_pass = true
step80_runtime_geometry_diagnostic_only_quality_pass = true
step80_runtime_geometry_diagnostic_only_activation_guard_pass = true
output_guard_pass = true
step80_step79_regression_guard_pass = true
artifact_budget_pass = true
```

Driver row summary:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
completed_lbm_steps = 3
total_mpm_substeps = 3
diagnostics_row_count = 4
stable = true
elapsed_seconds = 263.8073267000145
```

Runtime geometry diagnostic-only report summary:

```text
geometry_motion_interface_report_exists = true
geometry_motion_interface_report_pass = true
no_op_pass = true
config_validation_pass = true
diagnostic_only = true
mutation_flag_enabled_count = 0
apply_to_driver = false
apply_to_mpm_particles = false
apply_to_lbm_solid_phi = false
apply_to_lbm_solid_vel = false
apply_to_projection = false
update_dynamic_solid = false
recompute_boundary_links = false
mutate_geometry_state = false
```

Key numeric diagnostics:

```text
rho_min_min = 0.9631504416465759
rho_max_max = 1.037545919418335
lbm_max_v_max = 0.028745334595441818
mpm_min_J_min = 0.9998476505279541
mpm_max_speed_max = 1.5669373273849487
projected_mass_final = 0.02699997089803219
active_cell_count_final = 1320
bb_link_count_max = 2272
bb_max_correction_max = 0.0068721589632332325
active_reaction_particle_count_final = 892
max_grid_reaction_norm_max = 4.051990254083648e-05
```

Output and artifact guard summary:

```text
step80_required_driver_run_dir_count = 1
step80_optional_driver_run_dir_count = 0
step80_vtr_count = 0
step80_particle_npy_count = 0
step80_displaced_particle_output_count = 0
step80_dense_displacement_output_count = 0
step80_raw_geometry_output_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step80_file_count = 63
step80_total_size_mb < 20.0
```

Verification:

```text
focused Step80 pytest = 7 passed
trusted-environment full pytest = 976 passed
Anaconda full pytest = 976 passed
```

## Scope Guard

Step80 enables only runtime geometry diagnostic-only interface reporting.
Step80 writes `geometry_motion_interface_report.json`.
Step80 does not mutate geometry.
Step80 does not displace MPM particles.
Step80 does not update LBM `solid_phi`.
Step80 does not update LBM `solid_vel`.
Step80 does not update `dynamic_solid`.
Step80 does not recompute boundary links.
Step80 does not change moving bounce-back formulas.
Step80 does not enable wall velocity.
Step80 does not enable real geometry.
Step80 does not enable squid proxy.
Step80 does not enable link-area transfer.
Step80 does not enable VTR or particle NPY.
Step80 does not claim physical validation or production readiness.

## Next Direction

After Step80, the next step should be Step81 Wall Velocity Single-Feature
Activation Plan And Guard. Step81 should be plan-and-guard only, not a
simulation run.
