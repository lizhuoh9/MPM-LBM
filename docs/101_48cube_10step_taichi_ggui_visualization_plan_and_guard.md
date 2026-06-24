# Step101 48cube 10-Step Taichi GGUI Visualization Plan And Guard

Step101 is plan-and-guard only for the next 48^3 / 10-step Taichi GGUI visualization run. It does not run `FSIDriver3D`, does not call `driver.run()`, does not execute simulation, does not open a Taichi GGUI window, and does not write screenshots, video, VTR, or particle NPY output.

Step101 plans exactly one future Step102 row:

`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_10step_ggui_visual_run`

## Scope

- Future grid: `n_grid=48`.
- Future particles: `n_particles=1024`.
- Future duration: `n_lbm_steps=10`, `mpm_substeps_per_lbm_step=1`.
- Future geometry: `squid_proxy` using `configs/step85_squid_proxy_geometry_1024.json`.
- Future coupling: `moving_boundary` with `engineering` reaction transfer.
- Future motion application: prescribed kinematic, diagnostic-only geometry motion.
- Future wall velocity application: `solid_vel_experimental`, targeting LBM `solid_vel`.
- Future visualization: Taichi GGUI enabled with one screenshot allowed, video disabled.
- Future outputs: no VTK and no particle dumps.

The only intended expansion from Step100 is `n_lbm_steps = 5 -> 10`.

## Acceptance

The accepted Step101 claim is limited to:

`48^3 / 10-step Taichi GGUI visualization run is planned and guarded for Step102.`

Step101 does not claim a 48^3 / 10-step run passed, 48^3 production readiness, 64^3 readiness, physical validation, real squid validation, squid swimming validation, or grid convergence.

## Evidence

- Goal: `STEP101_48CUBE_10STEP_TAICHI_GGUI_VISUALIZATION_PLAN_AND_GUARD_GOAL.md`.
- Report: `STEP101_48CUBE_10STEP_TAICHI_GGUI_VISUALIZATION_PLAN_AND_GUARD_REPORT.md`.
- Plan config: `configs/step101_48cube_10step_taichi_ggui_visualization_plan.json`.
- Guard policy: `configs/step101_48cube_10step_taichi_ggui_visualization_guard_policy.json`.
- Output guard policy: `configs/step101_output_guard_policy.json`.
- Artifact manifest policy: `configs/step101_artifact_manifest_policy.json`.
- Plan artifact: `outputs/step101_48cube_10step_taichi_ggui_visualization_plan/48cube_10step_taichi_ggui_visualization_plan.json`.
- Guard artifact: `outputs/step101_48cube_10step_taichi_ggui_visualization_guard/48cube_10step_taichi_ggui_visualization_guard.json`.
- Output guard artifact: `outputs/step101_output_guard/output_guard.json`.
- Artifact manifest: `outputs/step101_artifact_manifest/artifact_summary.json`.

## Result Snapshot

- Plan pass: `true`.
- Guard pass: `true`.
- Step100 regression guard pass: `true`.
- Step99 regression guard pass: `true`.
- Step98 regression guard pass: `true`.
- Output guard pass: `true`.
- Driver run directory count: `0`.
- GGUI screenshot count: `0`.
- GGUI video count: `0`.
- VTR count: `0`.
- Particle NPY count: `0`.

## Follow-up Boundary

Step102 is the only planned place for the 48^3 / 10-step Taichi GGUI visual run. Any later 64^3 run, real-geometry run, link-area transfer run, VTK/video/particle-output run, or physical validation claim must be a separate planned and guarded step.
