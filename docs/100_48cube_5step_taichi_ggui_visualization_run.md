# Step100 48cube 5-Step Taichi GGUI Visualization Run

Step100 is the first real 48^3 / 5-step Taichi GGUI visualization run for the accepted first-user envelope. It runs exactly one required row:

`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run`

## Scope

- Grid: `n_grid=48`.
- Particles: `n_particles=1024`.
- Duration: `n_lbm_steps=5`, `mpm_substeps_per_lbm_step=1`.
- Geometry: `squid_proxy` using `configs/step85_squid_proxy_geometry_1024.json`.
- Coupling: `moving_boundary` with `engineering` reaction transfer.
- Motion application: prescribed kinematic, diagnostic-only geometry motion.
- Wall velocity application: `solid_vel_experimental`, targeting LBM `solid_vel`.
- Visualization: one Taichi GGUI PNG screenshot enabled, video disabled.
- Outputs: no VTK, no particle dumps, no raw geometry export, no real geometry candidate data.

The only intended expansion from Step98 is `n_lbm_steps = 1 -> 5`.

## Acceptance

The accepted Step100 claim is limited to:

`48^3 / 5-step Taichi GGUI visualization run passed for the first-user envelope.`

Step100 does not claim 48^3 10-step readiness, 64^3 readiness, production readiness, physical validation, real squid validation, squid swimming validation, or grid convergence.

## Evidence

- Goal: `STEP100_48CUBE_5STEP_TAICHI_GGUI_VISUALIZATION_RUN_GOAL.md`.
- Report: `STEP100_48CUBE_5STEP_TAICHI_GGUI_VISUALIZATION_RUN_REPORT.md`.
- Matrix config: `configs/step100_48cube_5step_taichi_ggui_visualization_run_matrix.json`.
- Driver config: `configs/step100_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run.json`.
- GGUI config: `configs/step100_taichi_ggui_visualization_config.json`.
- Matrix artifact: `outputs/step100_48cube_5step_taichi_ggui_visualization_run_matrix/48cube_5step_taichi_ggui_visualization_run_matrix.json`.
- Quality artifact: `outputs/step100_48cube_5step_taichi_ggui_visualization_quality/48cube_5step_taichi_ggui_visualization_quality.json`.
- Screenshot: `outputs/step100_ggui_visualization/step100_48cube_5step_ggui_visualization.png`.

## Result Snapshot

- Matrix pass: `true`.
- Quality pass: `true`.
- Activation guard pass: `true`.
- Output guard pass: `true`.
- Artifact budget pass: `true`.
- Completed LBM steps: `5`.
- Diagnostics rows: `6`.
- Screenshot count: `1`.
- VTR count: `0`.
- Particle NPY count: `0`.
- GGUI video count: `0`.

## Follow-up Boundary

Any later 48^3 longer-duration run, 64^3 run, real-geometry run, link-area transfer run, VTK/video/particle-output run, or physical validation claim must be a separate planned and guarded step.
