# Step96 Taichi GGUI 10-Step First User Visualization Run

Step96 executes the single first-user 10-step visualization row planned by
Step95:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run
```

The row keeps the Step92 accepted 32^3 / 1024-particle / 10-step dry-run
envelope and adds the Step94 Taichi GGUI screenshot path at the same bounded
scale.

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

## Acceptance Evidence

Step96 acceptance is artifact-backed by:

```text
outputs/step96_taichi_ggui_10step_visualization_run_matrix/taichi_ggui_10step_visualization_run_matrix.json
outputs/step96_taichi_ggui_10step_visualization_quality/taichi_ggui_10step_visualization_quality.json
outputs/step96_activation_guard/activation_guard.json
outputs/step96_output_guard/output_guard.json
outputs/step96_step95_regression_guard/step95_regression_guard.json
outputs/step96_step94_regression_guard/step94_regression_guard.json
outputs/step96_step92_regression_guard/step92_regression_guard.json
outputs/step96_artifact_manifest/artifact_summary.json
```

The GGUI evidence writes exactly one screenshot:

```text
outputs/step96_ggui_visualization/step96_ggui_10step_visualization.png
```

## Boundary

Step96 proves only this bounded claim:

```text
Taichi GGUI visualization can render the accepted 32^3 / 10-step first-user dry-run envelope.
```

Step96 does not claim production visualization readiness, a full interactive
visualization campaign, physical validation, real squid validation, squid
swimming, real geometry readiness, or readiness for 48^3 / 64^3 visualization
runs.

Step96 does not write videos, VTR files, particle NPY files, raw geometry,
real-geometry candidate output, dense wall velocity output, sparse wall
velocity output, dense displacement output, or displaced-particle output.
