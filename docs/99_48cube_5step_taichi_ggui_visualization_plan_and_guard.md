# Step99 48cube 5-Step Taichi GGUI Visualization Plan And Guard

Step99 is a plan-and-guard-only step. It does not run the driver, simulation, or Taichi GGUI. It only plans and guards a future Step100 48^3 / 5-step visualization run.

## Accepted Claim

`48^3 / 5-step Taichi GGUI visualization run is planned and guarded for Step100.`

Step99 does not claim that a 5-step run passed.

## Planned Step100 Row

`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run`

The planned Step100 row keeps the Step98 envelope and changes only duration:

- `n_grid=48`.
- `n_particles=1024`.
- `n_lbm_steps=5`.
- `mpm_substeps_per_lbm_step=1`.
- `coupling_mode=moving_boundary`.
- `reaction_transfer_mode=engineering`.
- `target_u_lbm=[0.0, 0.0, 0.0]`.
- `geometry_type=squid_proxy`.
- `geometry_motion_application_mode=diagnostic_only`.
- `wall_velocity_application_mode=solid_vel_experimental`.
- `target_lbm_field=solid_vel`.
- GGUI screenshot planned for Step100.
- GGUI video disabled.
- VTK and particle outputs disabled.

## Step99 Runtime Boundary

Step99 must leave these counts at zero:

- Driver run directories.
- GGUI screenshots.
- GGUI videos.
- VTK outputs.
- Particle NPY outputs.
- Raw geometry outputs.
- Real geometry candidate outputs.
- Dense wall velocity outputs.
- Dense displacement outputs.

## Artifacts

- Goal: `STEP99_48CUBE_5STEP_TAICHI_GGUI_VISUALIZATION_PLAN_AND_GUARD_GOAL.md`.
- Report: `STEP99_48CUBE_5STEP_TAICHI_GGUI_VISUALIZATION_PLAN_AND_GUARD_REPORT.md`.
- Plan config: `configs/step99_48cube_5step_taichi_ggui_visualization_plan.json`.
- Plan artifact: `outputs/step99_48cube_5step_taichi_ggui_visualization_plan/48cube_5step_taichi_ggui_visualization_plan.json`.
- Guard artifact: `outputs/step99_48cube_5step_taichi_ggui_visualization_guard/48cube_5step_taichi_ggui_visualization_guard.json`.
- Regression guards: `outputs/step99_step98_regression_guard`, `outputs/step99_step97_regression_guard`, and `outputs/step99_step96_regression_guard`.
- Output guard: `outputs/step99_output_guard/output_guard.json`.
- Artifact manifest: `outputs/step99_artifact_manifest/artifact_summary.json`.

## Follow-up Boundary

If Step99 is accepted, Step100 may run the single planned 48^3 / 5-step GGUI visualization row. Step100 still must not enable 64^3, video, VTK, particle dumps, real geometry candidate data, link-area transfer, solver formula changes, or broad physical validation claims.
