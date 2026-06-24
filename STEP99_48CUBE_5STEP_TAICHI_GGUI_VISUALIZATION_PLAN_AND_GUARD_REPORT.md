# Step99 48cube 5-Step Taichi GGUI Visualization Plan And Guard Report

## Result

Step99 accepted.

Accepted claim:

`48^3 / 5-step Taichi GGUI visualization run is planned and guarded for Step100.`

Step99 is a plan-and-guard step only. It does not claim that a 5-step run passed.

## Runtime Boundary

Step99 does not run `FSIDriver3D`.
Step99 does not call `driver.run()`.
Step99 does not execute simulation.
Step99 does not open a GGUI window.
Step99 does not write screenshots.
Step99 does not write video.
Step99 does not write VTK.
Step99 does not write particle NPY.

## Planned Step100 Row

Step99 only plans and guards Step100:

`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run`

Step100 may run exactly one 48^3 / 1024-particle / 5-step / moving-boundary / engineering row with:

- `geometry_type=squid_proxy`.
- `geometry_motion_application_mode=diagnostic_only`.
- `wall_velocity_application_mode=solid_vel_experimental`.
- `target_lbm_field=solid_vel`.
- `target_u_lbm=[0.0, 0.0, 0.0]`.
- `ggui_visualization_enabled=true`.
- `ggui_screenshot_enabled=true`.
- `ggui_video_enabled=false`.
- `write_vtk=false`.
- `write_particles=false`.

The only intended expansion from Step98 is:

`n_lbm_steps = 1 -> 5`

## Evidence

- Plan pass: `true`.
- Guard pass: `true`.
- Step98 regression guard pass: `true`.
- Step97 regression guard pass: `true`.
- Step96 regression guard pass: `true`.
- Output guard pass: `true`.
- Step99 activation feature count: `0`.
- Planned Step100 activation feature count: `5`.
- Planned Step100 grid: `48`.
- Planned Step100 LBM steps: `5`.

## Output Guard

- `step99_driver_run_dir_count=0`.
- `step99_ggui_screenshot_count=0`.
- `step99_ggui_video_count=0`.
- `step99_vtr_count=0`.
- `step99_particle_npy_count=0`.
- `step99_raw_geometry_output_count=0`.
- `step99_real_geometry_candidate_output_count=0`.
- `step99_dense_wall_velocity_output_count=0`.
- `step99_sparse_wall_velocity_output_count=0`.
- `step99_dense_displacement_output_count=0`.
- `step99_displaced_particle_output_count=0`.
- `private_absolute_path_count=0`.
- `protected_sim_edit_count=0`.
- `protected_diagnostics_edit_count=0`.
- `protected_external_edit_count=0`.
- `protected_real_geometry_candidate_edit_count=0`.

## Artifact Budget

The artifact budget passes when `step99_file_count <= 70`, `step99_total_size_mb < 5`, and no large/private/protected files are present. Exact latest values are recorded in `outputs/step99_artifact_manifest/artifact_summary.json`.

## Forbidden Follow-up Claims

Step100 must not enable 64^3.
Step100 must not enable VTK.
Step100 must not enable particle NPY.
Step100 must not enable video.
Step100 must not enable real geometry candidate data.
Step100 must not enable link-area transfer.
Step100 must not change solver formulas.
Step100 must not claim 48^3 production readiness, physical validation, squid swimming, or real squid validation.

## Verification

- `baseline_tests/run_step99_48cube_5step_taichi_ggui_visualization_plan.py`: pass.
- `baseline_tests/run_step99_48cube_5step_taichi_ggui_visualization_guard.py`: pass.
- `baseline_tests/run_step99_step98_regression_guard.py`: pass.
- `baseline_tests/run_step99_step97_regression_guard.py`: pass.
- `baseline_tests/run_step99_step96_regression_guard.py`: pass.
- `baseline_tests/run_step99_output_guard.py`: pass.
- `baseline_tests/run_step99_artifact_manifest.py`: pass.

Final artifact manifest, focused tests, full tests, git checks, and push proof are recorded by the generated artifacts and commit history for this step.
