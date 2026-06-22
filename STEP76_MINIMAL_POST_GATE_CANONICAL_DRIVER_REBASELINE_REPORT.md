# Step76 Minimal Post-Gate Canonical Driver Rebaseline Report

Step76 is the first simulation step allowed after the Step75 solver-complete
readiness gate. It runs exactly one minimal canonical `FSIDriver3D` row:
32^3, 1024 particles, moving-boundary engineering transfer, one LBM step, and
one MPM substep per LBM step.

Step76 keeps runtime geometry, wall velocity, real geometry, squid proxy,
link-area transfer, 48^3, 64^3, VTR output, particle NPY output, tau migration,
and solver formula changes disabled.

## Evidence

- `outputs/step76_post_gate_rebaseline_matrix/post_gate_rebaseline_matrix.json`
- `outputs/step76_post_gate_rebaseline_quality/post_gate_rebaseline_quality.json`
- `outputs/step76_activation_guard/activation_guard.json`
- `outputs/step76_output_guard/output_guard.json`
- `outputs/step76_step75_regression_guard/step75_regression_guard.json`
- `outputs/step76_artifact_manifest/artifact_summary.json`

## Required Run

```text
row_name = canonical_driver_moving_boundary_engineering_32_1step_rebaseline
campaign_id = step76_minimal_post_gate_real_driver_rebaseline
n_grid = 32
n_particles = 1024
n_lbm_steps = 1
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
```

Expected driver-run files:

```text
outputs/step76_driver_runs/canonical_driver_moving_boundary_engineering_32_1step_rebaseline/driver_config.json
outputs/step76_driver_runs/canonical_driver_moving_boundary_engineering_32_1step_rebaseline/geo_all_fluid_32.dat
outputs/step76_driver_runs/canonical_driver_moving_boundary_engineering_32_1step_rebaseline/diagnostics_timeseries.csv
outputs/step76_driver_runs/canonical_driver_moving_boundary_engineering_32_1step_rebaseline/diagnostics_timeseries.npz
```

## Result

```text
post_gate_rebaseline_matrix_pass = true
post_gate_rebaseline_quality_pass = true
post_gate_activation_guard_pass = true
output_guard_pass = true
step76_step75_regression_guard_pass = true
artifact_budget_pass = true
```

Required row summary:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
completed_lbm_steps = 1
total_mpm_substeps = 1
diagnostics_row_count = 2
has_nan = false
has_inf = false
stable = true
elapsed_seconds = 203.5551211000129
```

Key numeric diagnostics:

```text
rho_min_min = 0.980000376701355
rho_max_max = 1.0200003385543823
lbm_max_v_max = 0.020408157259225845
mpm_min_J_min = 0.9999732971191406
mpm_max_speed_max = 1.563986897468567
projected_mass_final = 0.027000008150935173
active_cell_count_final = 1320
bb_link_count_max = 2272
bb_max_correction_max = 0.006666668690741062
active_reaction_particle_count_final = 892
max_grid_reaction_norm_max = 4.051990254083648e-05
```

The required row proves only a minimal post-gate canonical driver rebaseline.
It does not validate physical behavior, real squid behavior, grid convergence,
runtime geometry, wall velocity, real geometry, or production readiness.

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

The optional 32^3/three-step rebaseline row remains disabled by default and is
not run by Step76.

Output guard:

```text
step76_required_driver_run_dir_count = 1
step76_optional_driver_run_dir_count = 0
step76_vtr_count = 0
step76_particle_npy_count = 0
step76_large_file_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step76_total_size_mb = 0.544865608215332
```

Artifact manifest:

```text
step76_file_count = 56
step76_total_size_mb = 0.2775897979736328
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step76_file_count = 0
protected_real_geometry_candidates_step76_file_count = 0
raw_geometry_file_count = 0
step76_required_driver_run_dir_count = 1
step76_optional_driver_run_dir_count = 0
step76_particle_npy_count = 0
step76_vtr_count = 0
```

## Validation

Completed validation:

```text
D:\working\taichi\env\python.exe -m py_compile <Step76 Python files>
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step76_post_gate_rebaseline_matrix.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step76_post_gate_rebaseline_quality.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step76_activation_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step76_output_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step76_step75_regression_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step76_artifact_manifest.py
D:\working\taichi\env\python.exe -W ignore -m pytest <Step76 focused tests> -q
14 passed

D:\working\taichi\env\python.exe -W ignore -m pytest -q
929 passed

D:\TOOL\Anaconda\python.exe -W ignore -m pytest -q
929 passed
```

The Step76 matrix runner emitted Taichi offline cache lock warnings on this
machine, but the required driver row completed and all Step76 audits and tests
passed.
