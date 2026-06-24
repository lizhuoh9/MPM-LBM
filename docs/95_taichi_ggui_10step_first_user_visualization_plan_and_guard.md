# Step95 Taichi GGUI 10-Step First User Visualization Plan And Guard

Step95 is a plan-and-guard-only step for the future Step96 10-step first-user
Taichi GGUI visualization run.

It plans this Step96 row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run
```

The planned row keeps the Step92 first-user 10-step dry-run envelope and adds
the Step94 Taichi GGUI screenshot path:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
ggui_visualization_enabled = true
ggui_screenshot_enabled = true
ggui_video_enabled = false
write_vtk = false
write_particles = false
```

## Acceptance

Step95 acceptance is artifact-backed by:

```text
outputs/step95_taichi_ggui_10step_visualization_plan/taichi_ggui_10step_visualization_plan.json
outputs/step95_taichi_ggui_10step_visualization_guard/taichi_ggui_10step_visualization_guard.json
outputs/step95_step94_regression_guard/step94_regression_guard.json
outputs/step95_step93_regression_guard/step93_regression_guard.json
outputs/step95_step92_regression_guard/step92_regression_guard.json
outputs/step95_output_guard/output_guard.json
outputs/step95_artifact_manifest/artifact_summary.json
```

The Step95 evidence reads existing Step92, Step93, and Step94 artifacts and
writes only Step95 plan, guard, regression, output, manifest, and log artifacts.

## Boundary

Step95 does not run `FSIDriver3D`, does not call `driver.run()`, does not run a
simulation, does not open a GGUI window, and does not write screenshots, videos,
VTR files, particle NPY files, raw geometry, real-geometry candidate output,
dense wall velocity output, or dense displacement output.

Step95 proves only this claim:

```text
Taichi GGUI 10-step first-user visualization run is planned and guarded for Step96.
```

Step95 does not claim physical validation, real squid validation, squid
swimming, squid actuation, grid convergence, production visualization readiness,
or production simulation readiness.
