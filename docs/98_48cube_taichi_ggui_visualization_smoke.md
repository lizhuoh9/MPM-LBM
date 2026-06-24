# Step98 48cube Taichi GGUI Visualization Smoke

Step98 is the first real 48^3 Taichi GGUI visualization smoke after the Step97 expansion plan/guard. It runs exactly one required first-user envelope row:

`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke`

## Scope

- Grid: `n_grid=48`.
- Particles: `n_particles=1024`.
- Duration: `n_lbm_steps=1`, `mpm_substeps_per_lbm_step=1`.
- Geometry: `squid_proxy` using `configs/step85_squid_proxy_geometry_1024.json`.
- Coupling: `moving_boundary` with `engineering` reaction transfer.
- Motion application: prescribed kinematic, diagnostic-only geometry motion.
- Wall velocity application: `solid_vel_experimental`, targeting LBM `solid_vel`.
- Visualization: Taichi GGUI screenshot enabled, video disabled.
- Outputs: no VTK, no particle dumps, no raw geometry export, no real geometry candidate data.

## Acceptance

The accepted Step98 claim is limited to:

`48^3 / 1-step Taichi GGUI visualization smoke passed for the first-user envelope.`

Step98 does not claim 48^3 10-step readiness, 64^3 readiness, production readiness, physical validation, real squid validation, or squid swimming validation.

## Artifacts

- Goal: `STEP98_48CUBE_TAICHI_GGUI_VISUALIZATION_SMOKE_GOAL.md`.
- Report: `STEP98_48CUBE_TAICHI_GGUI_VISUALIZATION_SMOKE_REPORT.md`.
- Matrix config: `configs/step98_48cube_taichi_ggui_visualization_smoke_matrix.json`.
- Driver config: `configs/step98_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke.json`.
- GGUI config: `configs/step98_taichi_ggui_visualization_config.json`.
- Matrix artifact: `outputs/step98_48cube_taichi_ggui_visualization_smoke_matrix/48cube_taichi_ggui_visualization_smoke_matrix.json`.
- Quality artifact: `outputs/step98_48cube_taichi_ggui_visualization_quality/48cube_taichi_ggui_visualization_quality.json`.
- Screenshot: `outputs/step98_ggui_visualization/step98_48cube_ggui_visual_smoke.png`.

## Follow-up Boundary

The next step may plan and guard a 48^3 5-step expansion, but Step98 itself only accepts the bounded one-step visualization smoke.
