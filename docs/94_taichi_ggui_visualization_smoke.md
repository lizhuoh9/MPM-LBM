# Step94 Taichi GGUI Visualization Smoke

Step94 executes the first Taichi GGUI visualization smoke for the first-user
envelope. It runs exactly one 32^3 / 1024-particle / 1-LBM-step canonical
driver row and then renders one GGUI screenshot through an independent evidence
renderer.

The row is:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke
```

The driver config stays inside `FSIDriverConfig`'s existing schema. GGUI options
are read separately from:

```text
configs/step94_taichi_ggui_visualization_config.json
```

The renderer uses Taichi GGUI to create a window, scene, and camera, then draws
the unit domain box, deterministic procedural `squid_proxy` visualization proxy
points, and wall-velocity proxy line segments. The screenshot artifact is:

```text
outputs/step94_ggui_visualization/step94_ggui_visual_smoke.png
```

The renderer visualizes procedural `squid_proxy` visualization proxy points,
not exported physical particle trajectories.

## Acceptance

Step94 acceptance is artifact-backed by:

```text
outputs/step94_taichi_ggui_visualization_smoke_matrix/taichi_ggui_visualization_smoke_matrix.json
outputs/step94_taichi_ggui_visualization_quality/taichi_ggui_visualization_quality.json
outputs/step94_activation_guard/activation_guard.json
outputs/step94_output_guard/output_guard.json
outputs/step94_step93_regression_guard/step93_regression_guard.json
outputs/step94_step92_regression_guard/step92_regression_guard.json
outputs/step94_step90_regression_guard/step90_regression_guard.json
outputs/step94_artifact_manifest/artifact_summary.json
```

All Step94 guards pass. The run writes one screenshot and writes no VTR,
particle NPY, video, raw geometry, real-geometry candidate output, dense wall
velocity output, or dense displacement output.

## Boundary

Step94 proves only this claim:

```text
Taichi GGUI visualization path can render the first-user envelope in a minimal 32^3 / 1-step smoke.
```

Step94 does not claim physical validation, real squid validation, squid
swimming, squid actuation, grid convergence, production visualization readiness,
or production simulation readiness.
