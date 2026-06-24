# Step97 48^3 Taichi GGUI First User Visualization Expansion Plan And Guard Report

## Acceptance

Step97 is accepted as a plan-and-guard-only step.

Accepted claim:

```text
48^3 Taichi GGUI visualization smoke is planned and guarded for Step98.
```

Step97 did not run `FSIDriver3D`, did not call `driver.run()`, did not execute
simulation, did not open a GGUI window, and did not write screenshots, video,
VTR, or particle NPY output.

## Planned Step98 Row

Step97 plans exactly one future Step98 row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke
```

The planned row values are:

```text
n_grid = 48
n_particles = 1024
n_lbm_steps = 1
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
geometry_motion_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_application_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_report_enabled = true
geometry_motion_application_report_enabled = true
boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json
boundary_motion_report_enabled = true
wall_velocity_application_mode = solid_vel_experimental
wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json
wall_velocity_application_report_enabled = true
target_lbm_field = solid_vel
ggui_visualization_enabled = true
ggui_screenshot_enabled = true
ggui_video_enabled = false
write_vtk = false
write_particles = false
output_interval = 1
```

The only planned Step96-to-Step98 row changes are:

```text
n_grid = 32 -> 48
n_lbm_steps = 10 -> 1
```

The duration reduction is intentional 48^3 grid-expansion smoke isolation.

## Generated Evidence

```text
outputs/step97_48cube_taichi_ggui_visualization_expansion_plan/48cube_taichi_ggui_visualization_expansion_plan.json
outputs/step97_48cube_taichi_ggui_visualization_expansion_guard/48cube_taichi_ggui_visualization_expansion_guard.json
outputs/step97_step96_regression_guard/step96_regression_guard.json
outputs/step97_step94_regression_guard/step94_regression_guard.json
outputs/step97_step92_regression_guard/step92_regression_guard.json
outputs/step97_output_guard/output_guard.json
outputs/step97_artifact_manifest/artifact_summary.json
```

Key artifact summary values:

```text
step97_48cube_taichi_ggui_visualization_expansion_plan_pass = true
step97_48cube_taichi_ggui_visualization_expansion_guard_pass = true
step97_step96_regression_guard_pass = true
step97_step94_regression_guard_pass = true
step97_step92_regression_guard_pass = true
output_guard_pass = true
artifact_budget_pass = true
step97_driver_run_dir_count = 0
step97_ggui_screenshot_count = 0
step97_ggui_video_count = 0
step97_vtr_count = 0
step97_particle_npy_count = 0
step97_raw_geometry_output_count = 0
step97_real_geometry_candidate_output_count = 0
step97_dense_wall_velocity_output_count = 0
step97_sparse_wall_velocity_output_count = 0
step97_dense_displacement_output_count = 0
step97_displaced_particle_output_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
large_file_count = 0
```

## Verification

Baseline evidence runners passed:

```text
baseline_tests/run_step97_48cube_taichi_ggui_visualization_expansion_plan.py
baseline_tests/run_step97_48cube_taichi_ggui_visualization_expansion_guard.py
baseline_tests/run_step97_step96_regression_guard.py
baseline_tests/run_step97_step94_regression_guard.py
baseline_tests/run_step97_step92_regression_guard.py
baseline_tests/run_step97_output_guard.py
baseline_tests/run_step97_artifact_manifest.py
```

Focused Step97 tests:

```text
6 passed in 1.26s
```

Full pytest with the Taichi environment:

```text
1108 passed in 172.44s
```

Full pytest with the Anaconda environment:

```text
1108 passed in 78.19s
```

## Closed Scope

Step97 does not claim that a 48^3 run passed. It does not claim 48^3
readiness, production readiness, physical validation, real squid validation,
squid swimming, or actuation. Step97 keeps 64^3, real geometry candidates,
link-area transfer, video, VTR, particle NPY output, dense wall velocity
output, dense displacement output, tau migration, and solver formula changes
closed.
