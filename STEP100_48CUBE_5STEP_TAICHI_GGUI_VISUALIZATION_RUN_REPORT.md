# Step100 48cube 5-Step Taichi GGUI Visualization Run Report

## Result

Step100 accepted.

Accepted claim:

`48^3 / 5-step Taichi GGUI visualization run passed for the first-user envelope.`

Step100 is a real run, not a plan-only guard. It runs exactly one required row:

`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run`

## Runtime Boundary

- `n_grid=48`.
- `n_particles=1024`.
- `n_lbm_steps=5`.
- `mpm_substeps_per_lbm_step=1`.
- `geometry_type=squid_proxy`.
- `geometry_motion_application_mode=diagnostic_only`.
- `wall_velocity_application_mode=solid_vel_experimental`.
- `target_u_lbm=[0.0, 0.0, 0.0]`.
- `write_vtk=false`.
- `write_particles=false`.
- GGUI screenshot enabled.
- GGUI video disabled.

The only expansion from Step98 is `n_lbm_steps = 1 -> 5`.

## Evidence

- Matrix pass: `true`.
- Quality pass: `true`.
- Activation guard pass: `true`.
- Step99 regression guard pass: `true`.
- Step98 regression guard pass: `true`.
- Step96 regression guard pass: `true`.
- Output guard pass: `true`.
- Artifact budget pass: `true`.

## Matrix Summary

- Required row count: `1`.
- Optional row count: `0`.
- Required stable count: `1`.
- Activation feature count: `5`.
- Completed LBM steps: `5`.
- Diagnostics rows: `6`.
- Total MPM substeps: `5`.
- Slowest row elapsed seconds: `61.89948790000926`.
- Screenshot size bytes: `132386`.
- `rho_min_min=0.9929272532463074`.
- `rho_max_max=1.0133136510849`.
- `max_lbm_max_v=0.008381160907447338`.
- `max_grid_reaction_norm_max=4.2187501094304025e-05`.
- `max_applied_velocity_norm=0.005849450792213756`.

## Output Guard

- `step100_required_driver_run_dir_count=1`.
- `step100_optional_driver_run_dir_count=0`.
- `step100_ggui_screenshot_count=1`.
- `step100_ggui_video_count=0`.
- `step100_vtr_count=0`.
- `step100_particle_npy_count=0`.
- `step100_raw_geometry_output_count=0`.
- `step100_real_geometry_candidate_output_count=0`.
- `step100_dense_wall_velocity_output_count=0`.
- `step100_sparse_wall_velocity_output_count=0`.
- `step100_dense_displacement_output_count=0`.
- `step100_displaced_particle_output_count=0`.
- `private_absolute_path_count=0`.
- `protected_sim_edit_count=0`.
- `protected_diagnostics_edit_count=0`.
- `protected_external_edit_count=0`.
- `protected_real_geometry_candidate_edit_count=0`.

## Artifact Budget

The artifact manifest passes with no large files, no private absolute paths, no protected-path files, one screenshot, no VTR, and no particle NPY. Exact latest file-count and size values are recorded in `outputs/step100_artifact_manifest/artifact_summary.json`.

## Artifact Paths

- Matrix artifact: `outputs/step100_48cube_5step_taichi_ggui_visualization_run_matrix/48cube_5step_taichi_ggui_visualization_run_matrix.json`.
- Quality artifact: `outputs/step100_48cube_5step_taichi_ggui_visualization_quality/48cube_5step_taichi_ggui_visualization_quality.json`.
- Activation guard: `outputs/step100_activation_guard/activation_guard.json`.
- Output guard: `outputs/step100_output_guard/output_guard.json`.
- Artifact manifest: `outputs/step100_artifact_manifest/artifact_summary.json`.
- Screenshot: `outputs/step100_ggui_visualization/step100_48cube_5step_ggui_visualization.png`.

## Verification

- `baseline_tests/run_step100_48cube_5step_taichi_ggui_visualization_run_matrix.py`: pass.
- `baseline_tests/run_step100_48cube_5step_taichi_ggui_visualization_quality.py`: pass.
- `baseline_tests/run_step100_activation_guard.py`: pass.
- `baseline_tests/run_step100_step99_regression_guard.py`: pass.
- `baseline_tests/run_step100_step98_regression_guard.py`: pass.
- `baseline_tests/run_step100_step96_regression_guard.py`: pass.
- `baseline_tests/run_step100_artifact_manifest.py`: pass.
- `baseline_tests/run_step100_output_guard.py`: pass.

Focused tests, full tests, git checks, and push proof are recorded by the final verification and commit history for this step.

## Forbidden Claims

Step100 does not claim 48^3 10-step readiness, 64^3 readiness, production readiness, physical validation, real squid validation, squid swimming validation, or grid convergence.
