# Post-Gate Simulation Campaign Status

Step75 created the inactive Step76 campaign proposal. Step76 executed only the
required first row from that proposal. Step77 added a separate 3-step
post-gate rebaseline row after Step76 was accepted. Step78 added a separate
5-step post-gate rebaseline row after Step77 was accepted. Steps 79, 81, 83,
and 85 planned bounded single-feature rows; Steps 80, 82, 84, and 86 executed
those planned canonical driver smoke rows. Step87 planned the first
three-feature combined row, Step88 executed that bounded combined smoke, and
Step89 planned the first user simulation dry run for Step90 without executing
simulation. Step95 planned the 10-step first-user Taichi GGUI visualization
run, and Step96 executed that single bounded visualization row.

## Step76 Executed Row

```text
campaign_id = step76_minimal_post_gate_real_driver_rebaseline
row_id = canonical_driver_moving_boundary_engineering_32_1step_rebaseline
n_grid = 32
n_lbm_steps = 1
required = true
executed_in_step76 = true
```

## Step77 Executed Row

```text
campaign_id = step77_minimal_post_gate_canonical_driver_3step_rebaseline
row_id = canonical_driver_moving_boundary_engineering_32_3step_rebaseline
n_grid = 32
n_lbm_steps = 3
required = true
executed_in_step77 = true
```

## Step78 Executed Row

```text
campaign_id = step78_minimal_post_gate_canonical_driver_5step_rebaseline
row_id = canonical_driver_moving_boundary_engineering_32_5step_rebaseline
n_grid = 32
n_lbm_steps = 5
required = true
executed_in_step78 = true
```

## Feature State

All advanced activation features remain disabled:

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

Step78 is a minimal post-gate 5-step rebaseline only. It is not a
real-geometry, runtime-geometry, wall-velocity, squid-proxy, grid-convergence,
physical-validation, or production-readiness step. After Step78, the next
intended direction is runtime geometry diagnostic-only single-feature
activation planning, not another pure duration baseline.

## Step79 Planned Row

Step79 does not execute a driver row. It records and guards the only planned
Step80 row:

```text
campaign_id = step79_runtime_geometry_diagnostic_only_activation_plan_and_guard
row_id = canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
geometry_motion_application_mode = diagnostic_only
executed_in_step79 = false
planned_for_step80 = true
```

Step79 does not run `FSIDriver3D`, does not execute simulation, does not mutate
geometry, does not enable wall velocity, real geometry, squid proxy behavior,
link-area transfer, 48^3, 64^3, VTR output, or particle NPY output, and does
not claim physical validation or production readiness.

## Step80 Executed Row

```text
campaign_id = step80_runtime_geometry_diagnostic_only_canonical_driver_smoke
row_id = canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
geometry_motion_application_mode = diagnostic_only
executed_in_step80 = true
```

Step80 enables only runtime geometry diagnostic-only interface reporting and
writes `geometry_motion_interface_report.json`. It does not mutate geometry,
displace MPM particles, update LBM `solid_phi`, update LBM `solid_vel`, update
`dynamic_solid`, recompute boundary links, enable wall velocity, enable real
geometry, enable squid proxy behavior, use link-area transfer, write VTR, write
particle NPY, or claim physical validation or production readiness.

## Step81 Planned Row

Step81 does not execute a driver row. It records and guards the only planned
Step82 row:

```text
campaign_id = step81_wall_velocity_single_feature_activation_plan_and_guard
row_id = canonical_driver_wall_velocity_solid_vel_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
executed_in_step81 = false
planned_for_step82 = true
```

Step81 does not run `FSIDriver3D`, does not execute simulation, does not
activate wall velocity in runtime, does not enable runtime geometry, does not
combine runtime geometry with wall velocity, does not enable real geometry,
squid proxy behavior, link-area transfer, 48^3, 64^3, VTR output, or particle
NPY output, and does not claim physical validation or production readiness.

## Step82 Executed Row

```text
campaign_id = step82_wall_velocity_solid_vel_canonical_driver_smoke
row_id = canonical_driver_wall_velocity_solid_vel_32_3step_smoke
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
executed_in_step82 = true
```

Step82 enables only wall velocity application to LBM `solid_vel` and writes the
wall-velocity and boundary-motion reports for that single row. Runtime geometry,
combined runtime geometry plus wall velocity, real geometry, squid proxy
behavior, link-area transfer, 48^3, 64^3, VTR output, and particle NPY output
remain disabled. Step82 does not claim physical validation or production
readiness.

## Step83 Planned Row

Step83 does not execute a driver row. It records and guards the only planned
Step84 combined row:

```text
campaign_id = step83_runtime_geometry_wall_velocity_combined_activation_plan_and_guard
row_id = canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
executed_in_step83 = false
planned_for_step84 = true
```

Step83 does not run `FSIDriver3D`, does not execute simulation, does not
activate the combined path in runtime, does not enable real geometry, squid
proxy behavior, link-area transfer, 48^3, 64^3, VTR output, or particle NPY
output, and does not claim physical validation or production readiness.

## Step84 Executed Row

```text
campaign_id = step84_runtime_geometry_wall_velocity_combined_canonical_driver_smoke
row_id = canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
target_u_lbm = [0.0, 0.0, 0.0]
executed_in_step84 = true
```

Step84 enables only runtime geometry diagnostic-only reporting plus wall
velocity application to LBM `solid_vel` in the single planned canonical driver
row. Real geometry, squid proxy behavior, link-area transfer, 48^3, 64^3, VTR
output, and particle NPY output remain disabled. Step84 does not claim physical
validation, grid convergence, or production readiness.

## Step85 Planned Row

Step85 does not execute a driver row. It records and guards the only planned
Step86 row:

```text
campaign_id = step85_squid_proxy_static_geometry_activation_plan_and_guard
row_id = canonical_driver_squid_proxy_static_geometry_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
boundary_motion_mode = static
geometry_motion_mode = static
geometry_motion_application_mode = disabled
wall_velocity_application_mode = disabled
write_vtk = false
write_particles = false
executed_in_step85 = false
planned_for_step86 = true
```

Step85 does not run `FSIDriver3D`, does not execute simulation, does not enable
runtime geometry, wall velocity, combined runtime geometry plus wall velocity,
real geometry candidates, link-area transfer, 48^3, 64^3, VTR output, or
particle NPY output, and does not claim physical validation or production
readiness.

## Step86 Executed Row

```text
campaign_id = step86_squid_proxy_static_geometry_canonical_driver_smoke
row_id = canonical_driver_squid_proxy_static_geometry_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
boundary_motion_mode = static
geometry_motion_mode = static
geometry_motion_application_mode = disabled
wall_velocity_application_mode = disabled
write_vtk = false
write_particles = false
executed_in_step86 = true
```

Step86 executes only procedural static `squid_proxy` geometry in the single
planned canonical driver row and writes a non-strict geometry quality report.
Runtime geometry, wall velocity, combined runtime geometry plus wall velocity,
real geometry candidates, link-area transfer, 48^3, 64^3, VTR output, and
particle NPY output remain disabled. Step86 does not claim physical validation,
real squid validation, squid swimming, grid convergence, or production
readiness.

## Step87 Planned Row

Step87 does not execute a driver row. It records and guards the only planned
Step88 row:

```text
campaign_id = step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_and_guard
row_id = canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
executed_in_step87 = false
planned_for_step88 = true
```

Step87 does not run `FSIDriver3D`, does not execute simulation, does not enable
the three-feature combined row, real geometry candidates, link-area transfer,
48^3, 64^3, VTR output, or particle NPY output, and does not claim physical
validation, real squid validation, squid swimming, or production readiness.

## Step88 Executed Row

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
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
executed_in_step88 = true
```

Step88 enables only the bounded combination of procedural `squid_proxy`
geometry, runtime geometry diagnostic-only reporting, and wall velocity
`solid_vel_experimental` reporting. Real geometry candidates, link-area
transfer, 48^3, 64^3, VTR output, and particle NPY output remain disabled.
Step88 does not claim physical validation, real squid validation, squid
swimming, squid actuation, grid convergence, or production readiness.

## Step89 Planned Row

Step89 does not execute a driver row. It records and guards the only planned
Step90 first user simulation dry-run row:

```text
campaign_id = step89_first_user_simulation_dry_run_plan_and_guard
row_id = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run
n_grid = 32
n_particles = 1024
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
executed_in_step89 = false
planned_for_step90 = true
```

Step89 does not run `FSIDriver3D`, does not execute simulation, and does not
activate the first user dry run. Real geometry candidates, link-area transfer,
48^3, 64^3, VTR output, and particle NPY output remain disabled. Step89 does
not claim physical validation, real squid validation, squid swimming, squid
actuation, grid convergence, or production readiness.

## Step90 Executed Row

```text
campaign_id = step90_first_user_simulation_dry_run
row_id = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run
n_grid = 32
n_particles = 1024
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
executed_in_step90 = true
```

Step90 executes only the bounded first user simulation dry-run row planned by
Step89. Runtime geometry remains diagnostic-only, wall velocity targets LBM
`solid_vel` only, and the `squid_proxy` geometry remains procedural. Real
geometry candidates, link-area transfer, 48^3, 64^3, VTR output, and particle
NPY output remain disabled. Step90 does not claim physical validation, real
squid validation, squid swimming, squid actuation, grid convergence, or
production readiness.

## Step91 Planned Row

Step91 does not execute a driver row. It records and guards the only planned
Step92 ten-step first user simulation dry-run row:

```text
campaign_id = step91_first_user_simulation_10step_dry_run_plan_and_guard
row_id = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run
n_grid = 32
n_particles = 1024
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
executed_in_step91 = false
planned_for_step92 = true
```

The only planned expansion from Step90 to Step92 is `n_lbm_steps = 5 -> 10`.
Step91 does not run `FSIDriver3D`, does not execute simulation, and does not
activate the ten-step dry run. Real geometry candidates, link-area transfer,
48^3, 64^3, VTR output, and particle NPY output remain disabled. Step91 does
not claim physical validation, real squid validation, squid swimming, squid
actuation, grid convergence, or production readiness.

## Step92 Executed Row

```text
campaign_id = step92_first_user_simulation_10step_dry_run
row_id = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run
n_grid = 32
n_particles = 1024
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
executed_in_step92 = true
```

Step92 executes only the bounded first user simulation 10-step dry-run row
planned by Step91. Runtime geometry remains diagnostic-only, wall velocity
targets LBM `solid_vel` only, and the `squid_proxy` geometry remains
procedural. Real geometry candidates, link-area transfer, 48^3, 64^3,
file-based visualization output, and particle NPY output remain disabled.
Step92 does not claim physical validation, real squid validation, squid
swimming, squid actuation, grid convergence, or production readiness.

## Step93 Planned Row

Step93 does not execute a driver row. It records and guards the only planned
Step94 Taichi GGUI visualization smoke row:

```text
campaign_id = step93_taichi_ggui_visualization_enablement_plan_and_guard
row_id = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke
n_grid = 32
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
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
ggui_visualization_enabled = true
write_vtk = false
write_particles = false
executed_in_step93 = false
planned_for_step94 = true
```

The only planned expansion from Step92 to Step94 is Taichi GGUI visualization.
Step93 does not run `FSIDriver3D`, does not open a GGUI window, does not write
screenshots, does not execute simulation, and does not activate the visual
smoke. Real geometry candidates, link-area transfer, 48^3, 64^3, file-based
visualization output, and particle NPY output remain disabled. Step93 does not
claim physical validation, real squid validation, squid swimming, squid
actuation, grid convergence, or production readiness.

## Step94 Executed GGUI Smoke Row

Step94 executes the only planned Taichi GGUI visualization smoke row:

```text
campaign_id = step94_taichi_ggui_visualization_smoke
row_id = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke
n_grid = 32
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
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
ggui_visualization_enabled = true
write_vtk = false
write_particles = false
executed_in_step94 = true
```

The independent Step94 GGUI renderer writes exactly one PNG screenshot and no
video. Step94 keeps file-based visualization output, particle NPY output, real
geometry candidates, link-area transfer, 48^3, 64^3, solver formula changes,
physical validation, real squid validation, squid swimming, squid actuation,
grid convergence, production visualization readiness, and production simulation
readiness closed.
