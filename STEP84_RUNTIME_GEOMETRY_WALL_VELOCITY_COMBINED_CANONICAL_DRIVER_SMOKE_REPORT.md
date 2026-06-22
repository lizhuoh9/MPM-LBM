# Step84 Runtime Geometry Wall Velocity Combined Canonical Driver Smoke Report

Status: accepted.

Step84 runs exactly one required canonical driver row:

```text
canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

The row uses:

```text
32^3
1024 particles
3 LBM steps
1 MPM substep per LBM step
moving_boundary
engineering
box geometry
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
target_u_lbm = [0.0, 0.0, 0.0]
```

`target_u_lbm = [0.0, 0.0, 0.0]` is a row-local config choice to isolate the
combined smoke from background flow. It is not a solver, tau, or runtime-formula
change.

## Evidence Summary

The expected committed evidence files are:

```text
outputs/step84_runtime_geometry_wall_velocity_combined_smoke_matrix/runtime_geometry_wall_velocity_combined_smoke_matrix.json
outputs/step84_runtime_geometry_wall_velocity_combined_quality/runtime_geometry_wall_velocity_combined_quality.json
outputs/step84_activation_guard/activation_guard.json
outputs/step84_output_guard/output_guard.json
outputs/step84_step83_regression_guard/step83_regression_guard.json
outputs/step84_step82_regression_guard/step82_regression_guard.json
outputs/step84_step80_regression_guard/step80_regression_guard.json
outputs/step84_artifact_manifest/artifact_summary.json
```

Verified evidence:

```text
step84_runtime_geometry_wall_velocity_combined_smoke_matrix_pass = true
step84_runtime_geometry_wall_velocity_combined_quality_pass = true
step84_activation_guard_pass = true
output_guard_pass = true
step84_step83_regression_guard_pass = true
step84_step82_regression_guard_pass = true
step84_step80_regression_guard_pass = true
artifact_budget_pass = true
```

Smoke matrix summary:

```text
required_row_count = 1
optional_row_count = 0
required_stable_count = 1
activation_feature_count = 2
runtime_geometry_enabled_count = 1
wall_velocity_enabled_count = 1
combined_runtime_geometry_wall_velocity_enabled_count = 1
real_geometry_enabled_count = 0
squid_proxy_enabled_count = 0
link_area_enabled_count = 0
grid_48_enabled_count = 0
grid_64_enabled_count = 0
has_nan_count = 0
has_inf_count = 0
runtime_hard_fail_count = 0
max_lbm_max_v = 0.00042992818634957075
min_mpm_min_J = 0.9998469948768616
max_mpm_max_speed = 0.004585250746458769
total_elapsed_seconds = 212.63031799998134
```

Output guard summary:

```text
output_guard_pass = true
step84_required_driver_run_dir_count = 1
step84_optional_driver_run_dir_count = 0
step84_vtr_count = 0
step84_particle_npy_count = 0
step84_dense_wall_velocity_output_count = 0
step84_sparse_wall_velocity_output_count = 0
step84_dense_displacement_output_count = 0
step84_displaced_particle_output_count = 0
step84_raw_geometry_output_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
```

Artifact manifest summary:

```text
artifact_budget_pass = true
step84_file_count = 80
step84_total_size_mb = 0.41820430755615234
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step84_file_count = 0
protected_real_geometry_candidates_step84_file_count = 0
raw_geometry_file_count = 0
step84_required_driver_run_dir_count = 1
step84_optional_driver_run_dir_count = 0
step84_vtr_count = 0
step84_particle_npy_count = 0
```

## Driver Reports

Step84 writes:

```text
geometry_motion_interface_report.json
boundary_motion_interface_report.json
wall_velocity_application_report.json
```

## Claim Boundary

Step84 enables only:

```text
runtime geometry diagnostic-only interface reporting
wall velocity solid_vel experimental application
```

Step84 does not mutate geometry. Step84 does not displace MPM particles.
Step84 does not update LBM `solid_phi` through runtime geometry. Step84 does
not directly write LBM populations through wall velocity. Step84 does not
modify moving bounce-back formulas. Step84 does not directly update MPM state
through wall velocity. Step84 does not directly update projector state through
wall velocity. Step84 does not enable real geometry. Step84 does not enable
squid proxy. Step84 does not enable link-area transfer. Step84 does not enable
48^3 or 64^3. Step84 does not write VTR or particle NPY.

Step84 does not claim physical validation, moving-geometry validation,
moving-wall physics validation, real squid validation, grid convergence, or
production readiness.

## Validation Commands

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_runtime_geometry_wall_velocity_combined_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_runtime_geometry_wall_velocity_combined_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_step83_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_step82_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_step80_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_artifact_manifest.py
```

Focused and full pytest verification:

```text
Step84 focused tests: 11 passed in 1.03s
Full pytest with D:\working\taichi\env\python.exe: 1021 passed in 128.46s
Full pytest with D:\TOOL\Anaconda\python.exe: 1021 passed in 57.80s
```
