# Step97 48-Cube Taichi GGUI Visualization Expansion Plan And Guard

Step97 is accepted as a plan-and-guard-only step. It does not run
`FSIDriver3D`, does not call `driver.run()`, does not execute simulation, does
not open a GGUI window, and does not write screenshots, video, VTR, or particle
NPY output.

Step97 plans exactly one future Step98 row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke
```

The planned row keeps the accepted first-user `squid_proxy` runtime-geometry
and wall-velocity envelope, keeps Taichi GGUI screenshot intent, and isolates
the grid expansion by changing only these two Step96 values:

```text
n_grid = 32 -> 48
n_lbm_steps = 10 -> 1
```

The duration reduction is intentional. Step98 is planned as a 48^3
grid-expansion smoke isolation step, not as a 10-step 48^3 readiness run.

## Planned Step98 Row

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

## Evidence

Step97 acceptance is artifact-backed by:

```text
outputs/step97_48cube_taichi_ggui_visualization_expansion_plan/48cube_taichi_ggui_visualization_expansion_plan.json
outputs/step97_48cube_taichi_ggui_visualization_expansion_guard/48cube_taichi_ggui_visualization_expansion_guard.json
outputs/step97_step96_regression_guard/step96_regression_guard.json
outputs/step97_step94_regression_guard/step94_regression_guard.json
outputs/step97_step92_regression_guard/step92_regression_guard.json
outputs/step97_output_guard/output_guard.json
outputs/step97_artifact_manifest/artifact_summary.json
```

The Step97 output guard requires zero driver-run directories, zero screenshots,
zero videos, zero VTR files, zero particle NPY files, zero raw or real-geometry
candidate files, zero dense/sparse wall-velocity files, zero dense displacement
files, and zero protected solver or vendored edits.

## Boundary

Step97 proves only this bounded claim:

```text
48^3 Taichi GGUI visualization smoke is planned and guarded for Step98.
```

Step97 does not prove that a 48^3 run passed. It does not claim 48^3
readiness, production readiness, physical validation, real squid validation,
squid swimming, or actuation. It does not enable 64^3, real geometry,
link-area transfer, video, VTR, particle NPY output, dense wall velocity output,
dense displacement output, tau migration, or solver formula changes.
