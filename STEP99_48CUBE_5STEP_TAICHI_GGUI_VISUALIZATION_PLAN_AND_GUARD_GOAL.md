# Step99 48cube 5-Step Taichi GGUI Visualization Plan And Guard Goal

## Objective

Implement Step99 as a plan-and-guard-only step for the next bounded visualization expansion:

`Step99 48^3 / 5-Step Taichi GGUI Visualization Plan And Guard`

Step99 must not run the solver, driver, simulation, or GGUI. Step99 must only create a checked, artifact-backed plan and guard for a future Step100 run.

## Current Baseline

- `origin/main` is expected to start from `3142aea8361fd67c4799143ee56f95b8a09b3286`.
- Step96 is accepted.
- Step97 is accepted.
- Step98 is accepted.
- Step99 is not started.

Step98 accepted exactly this bounded claim:

`48^3 / 1-step Taichi GGUI visualization smoke passed for the first-user envelope.`

Step99 must build on Step98 without re-running Step98 and without widening its claim.

## Step99 Accepted Claim

Step99 may claim only:

`48^3 / 5-step Taichi GGUI visualization run is planned and guarded for Step100.`

Step99 must not claim:

- `48^3 / 5-step run passed`.
- `48^3 stable`.
- `48^3 / 10-step ready`.
- `64^3 ready`.
- Production readiness.
- Physical validation.
- Real squid validation.
- Squid swimming validation.
- Squid actuation validation.

## Step99 Hard Runtime Boundary

Step99 is plan-and-guard only. It must not call or execute:

- `FSIDriver3D`.
- `driver.run()`.
- Simulation stepping.
- Taichi GGUI window creation.
- Screenshot generation.
- Video generation.
- VTK output.
- Particle dump output.

Step99 must not create any Step99 driver-run directory, GGUI screenshot, GGUI video, VTK, particle NPY, raw geometry output, dense wall velocity output, dense displacement output, displaced particle output, real geometry candidate output, or link-area output.

## Forbidden Edit Scope

Step99 must not modify:

- `src/mpm_lbm/sim/**`.
- `src/mpm_lbm/diagnostics/**`.
- `src/mpm_lbm/sim/drivers/**`.
- `src/mpm_lbm/sim/coupling/**`.
- `src/mpm_lbm/sim/lbm/**`.
- `src/mpm_lbm/sim/mpm/**`.
- `src/mpm_lbm/sim/geometry/**`.
- `src/mpm_lbm/sim/motion/**`.
- `src/mpm_lbm/sim/wall_velocity/**`.
- `external/taichi_LBM3D/**`.
- `data/real_geometry_candidates/**`.

Step99 must not add solver formula changes, tau migration, runtime driver behavior changes, physical validation claims, production-readiness claims, real squid validation claims, squid swimming claims, or squid actuation claims.

## Planned Step100 Row

Step99 must allow exactly one future Step100 required row:

`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run`

The planned Step100 row must be:

- `n_grid = 48`.
- `n_particles = 1024`.
- `n_lbm_steps = 5`.
- `mpm_substeps_per_lbm_step = 1`.
- `coupling_mode = moving_boundary`.
- `reaction_transfer_mode = engineering`.
- `target_u_lbm = [0.0, 0.0, 0.0]`.
- `geometry_type = squid_proxy`.
- `geometry_config_path = configs/step85_squid_proxy_geometry_1024.json`.
- `quality_check_enabled = true`.
- `quality_check_strict = false`.
- `geometry_motion_mode = prescribed_kinematic`.
- `geometry_motion_application_mode = diagnostic_only`.
- `geometry_motion_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json`.
- `geometry_motion_application_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json`.
- `geometry_motion_report_enabled = true`.
- `geometry_motion_application_report_enabled = true`.
- `boundary_motion_mode = prescribed_kinematic`.
- `boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json`.
- `boundary_motion_report_enabled = true`.
- `wall_velocity_application_mode = solid_vel_experimental`.
- `wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json`.
- `wall_velocity_application_report_enabled = true`.
- `target_lbm_field = solid_vel`.
- `ggui_visualization_enabled = true`.
- `ggui_screenshot_enabled = true`.
- `ggui_video_enabled = false`.
- `write_vtk = false`.
- `write_particles = false`.
- `output_interval = 1`.

The only intended expansion from Step98 is:

`n_lbm_steps = 1 -> 5`

Everything else must remain Step98-compatible:

- 48 grid, not 64 grid.
- 1024 particles.
- One MPM substep per LBM step.
- Zero background flow.
- Squid proxy geometry.
- Runtime geometry diagnostic-only.
- Solid velocity wall-velocity report path.
- Taichi GGUI planned with one screenshot for Step100 only.
- No video.
- No VTK.
- No particle dumps.
- No real geometry candidate data.
- No link-area transfer.

## Required Files

Add:

- `STEP99_48CUBE_5STEP_TAICHI_GGUI_VISUALIZATION_PLAN_AND_GUARD_GOAL.md`.
- `STEP99_48CUBE_5STEP_TAICHI_GGUI_VISUALIZATION_PLAN_AND_GUARD_REPORT.md`.
- `configs/step99_48cube_5step_taichi_ggui_visualization_plan.json`.
- `configs/step99_48cube_5step_taichi_ggui_visualization_guard_policy.json`.
- `configs/step99_step98_regression_policy.json`.
- `configs/step99_step97_regression_policy.json`.
- `configs/step99_step96_regression_policy.json`.
- `configs/step99_output_guard_policy.json`.
- `configs/step99_artifact_manifest_policy.json`.
- `src/mpm_lbm/evidence/step99_48cube_5step_taichi_ggui_visualization_plan.py`.
- `src/mpm_lbm/evidence/step99_48cube_5step_taichi_ggui_visualization_guard.py`.
- `src/mpm_lbm/evidence/step99_step98_regression_guard.py`.
- `src/mpm_lbm/evidence/step99_step97_regression_guard.py`.
- `src/mpm_lbm/evidence/step99_step96_regression_guard.py`.
- `src/mpm_lbm/evidence/step99_output_guard.py`.
- `baseline_tests/step99_common.py`.
- `baseline_tests/run_step99_48cube_5step_taichi_ggui_visualization_plan.py`.
- `baseline_tests/run_step99_48cube_5step_taichi_ggui_visualization_guard.py`.
- `baseline_tests/run_step99_step98_regression_guard.py`.
- `baseline_tests/run_step99_step97_regression_guard.py`.
- `baseline_tests/run_step99_step96_regression_guard.py`.
- `baseline_tests/run_step99_output_guard.py`.
- `baseline_tests/run_step99_artifact_manifest.py`.
- `tests/test_step99_48cube_5step_taichi_ggui_visualization_plan_contract.py`.
- `tests/test_step99_48cube_5step_taichi_ggui_visualization_guard_contract.py`.
- `tests/test_step99_step98_regression_contract.py`.
- `tests/test_step99_step97_regression_contract.py`.
- `tests/test_step99_step96_regression_contract.py`.
- `tests/test_step99_output_guard_contract.py`.
- `docs/99_48cube_5step_taichi_ggui_visualization_plan_and_guard.md`.
- `outputs/step99_48cube_5step_taichi_ggui_visualization_plan/**`.
- `outputs/step99_48cube_5step_taichi_ggui_visualization_guard/**`.
- `outputs/step99_step98_regression_guard/**`.
- `outputs/step99_step97_regression_guard/**`.
- `outputs/step99_step96_regression_guard/**`.
- `outputs/step99_output_guard/**`.
- `outputs/step99_artifact_manifest/**`.
- `logs/step99_*.log`.

Allowed documentation updates if needed:

- `README.md`.
- `docs/00_project_status.md`.
- `docs/ACTIVATION_PRECONDITIONS.md`.
- `docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md`.
- `docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md`.

Do not update these optional docs unless the existing repo pattern clearly requires it.

## Step99 Plan Config Contract

`configs/step99_48cube_5step_taichi_ggui_visualization_plan.json` must encode:

- `step = Step99`.
- `campaign_id = step99_48cube_5step_taichi_ggui_visualization_plan_and_guard`.
- `previous_step = Step98`.
- `previous_required_commit = 3142aea8361fd67c4799143ee56f95b8a09b3286`.
- `activation_kind = 48cube_5step_taichi_ggui_visualization_plan_only`.
- `driver_run_required = false`.
- `fsidriver_run_allowed = false`.
- `simulation_run_allowed = false`.
- `ggui_run_allowed = false`.
- `screenshot_output_allowed_in_step99 = false`.
- `step100_allowed = true`.
- `step100_allowed_row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run`.
- `step100_allowed_n_grid = 48`.
- `step100_allowed_n_particles = 1024`.
- `step100_allowed_n_lbm_steps = 5`.
- `step100_allowed_mpm_substeps_per_lbm_step = 1`.
- `step100_allowed_coupling_mode = moving_boundary`.
- `step100_allowed_reaction_transfer_mode = engineering`.
- `step100_allowed_output_interval = 1`.
- `from_step98_duration_expansion = true`.
- `previous_step98_n_grid = 48`.
- `previous_step98_n_lbm_steps = 1`.
- `planned_step100_n_grid = 48`.
- `planned_step100_n_lbm_steps = 5`.
- `only_new_dimension_from_step98 = n_lbm_steps_5`.
- `ggui_visualization_planned_for_step100 = true`.
- `ggui_interactive_window_allowed_for_step100 = true`.
- `ggui_screenshot_allowed_for_step100 = true`.
- `ggui_video_allowed_for_step100 = false`.
- `ggui_required_backend_policy = local_desktop_taichi_environment`.
- `ggui_screenshot_count_allowed_for_step100 = 1`.
- `squid_proxy_planned_for_step100 = true`.
- `geometry_type_allowed_for_step100 = squid_proxy`.
- `geometry_config_path_allowed_for_step100 = configs/step85_squid_proxy_geometry_1024.json`.
- `quality_check_enabled_allowed_for_step100 = true`.
- `quality_check_strict_allowed_for_step100 = false`.
- `geometry_quality_report_required_for_step100 = true`.
- `runtime_geometry_planned_for_step100 = true`.
- `geometry_motion_mode_allowed_for_step100 = prescribed_kinematic`.
- `geometry_motion_application_mode_allowed_for_step100 = diagnostic_only`.
- `geometry_motion_config_path_allowed_for_step100 = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json`.
- `geometry_motion_application_config_path_allowed_for_step100 = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json`.
- `geometry_motion_interface_report_required_for_step100 = true`.
- `geometry_motion_application_report_required_for_step100 = true`.
- `geometry_mutation_allowed = false`.
- `wall_velocity_planned_for_step100 = true`.
- `boundary_motion_mode_allowed_for_step100 = prescribed_kinematic`.
- `boundary_motion_config_path_allowed_for_step100 = configs/step34_boundary_motion_interface_prescribed_kinematic.json`.
- `boundary_motion_report_required_for_step100 = true`.
- `wall_velocity_application_mode_allowed_for_step100 = solid_vel_experimental`.
- `wall_velocity_application_config_path_allowed_for_step100 = configs/step36_wall_velocity_application_solid_vel_experimental.json`.
- `wall_velocity_application_report_required_for_step100 = true`.
- `target_lbm_field_planned_for_step100 = solid_vel`.
- `target_u_lbm_allowed_for_step100 = [0.0, 0.0, 0.0]`.
- `target_u_lbm_policy = same_zero_background_flow_as_step90_step92_step94_step96_step98`.
- `combined_runtime_geometry_wall_velocity_planned_for_step100 = true`.
- `planned_step100_activation_feature_count = 5`.
- `step99_activation_feature_count = 0`.
- All disallowed outputs and expansions set to `false`: VTK, particles, VTR, particle NPY, video, real geometry, real geometry candidate data, link-area, grid 64, dense wall velocity, dense displacement.
- Runtime code changed, solver behavior changed, solver formula change allowed, and tau migration allowed all set to `false`.
- Physical validation, production readiness, real squid validation, squid swimming, and squid actuation claims all set to `false`.

## Step99 Plan Artifact Contract

Generate:

- `outputs/step99_48cube_5step_taichi_ggui_visualization_plan/48cube_5step_taichi_ggui_visualization_plan.json`.
- `outputs/step99_48cube_5step_taichi_ggui_visualization_plan/48cube_5step_taichi_ggui_visualization_plan.csv`.
- `outputs/step99_48cube_5step_taichi_ggui_visualization_plan/48cube_5step_taichi_ggui_visualization_plan_summary.csv`.

The summary must include and pass:

- `step99_48cube_5step_taichi_ggui_visualization_plan_pass = true`.
- `previous_step = Step98`.
- `previous_commit = 3142aea8361fd67c4799143ee56f95b8a09b3286`.
- No driver/simulation/GGUI/screenshot execution in Step99.
- Step100 allowed row and exact values.
- Duration expansion from Step98: 1 to 5 LBM steps.
- GGUI planned for Step100 with screenshot allowed and video disallowed.
- No VTK, particles, VTR, particle NPY, video, real geometry, link-area, or 64 grid.
- `step99_activation_feature_count = 0`.
- `planned_step100_activation_feature_count = 5`.

## Step99 Guard Artifact Contract

Generate:

- `outputs/step99_48cube_5step_taichi_ggui_visualization_guard/48cube_5step_taichi_ggui_visualization_guard.json`.
- `outputs/step99_48cube_5step_taichi_ggui_visualization_guard/48cube_5step_taichi_ggui_visualization_guard.csv`.
- `outputs/step99_48cube_5step_taichi_ggui_visualization_guard/48cube_5step_taichi_ggui_visualization_guard_summary.csv`.

The summary must include and pass:

- `step99_48cube_5step_taichi_ggui_visualization_guard_pass = true`.
- `guard_row_count > 0`.
- `guard_pass_count = guard_row_count`.
- `step99_activation_feature_count = 0`.
- `planned_step100_activation_feature_count = 5`.
- Planned Step100 grid and duration: 48 grid and 5 LBM steps.
- GGUI planned for Step100, screenshot allowed for Step100, video disallowed.
- Squid proxy, runtime geometry, wall velocity, and combined runtime geometry wall velocity planned for Step100.
- VTR, particle NPY, video, real geometry, real geometry candidate data, link-area, and grid 64 all disallowed.

## Regression Guards

Add Step99 regression guards for Step98, Step97, and Step96.

### Step98 Regression Guard

Generate:

- `outputs/step99_step98_regression_guard/step98_regression_guard.json`.
- `outputs/step99_step98_regression_guard/step98_regression_guard.csv`.
- `outputs/step99_step98_regression_guard/step98_regression_guard_summary.csv`.

The summary must prove:

- `step98_48cube_taichi_ggui_visualization_smoke_matrix_pass = true`.
- `step98_48cube_taichi_ggui_visualization_quality_pass = true`.
- `step98_activation_guard_pass = true`.
- `step98_output_guard_pass = true`.
- `step98_step97_regression_guard_pass = true`.
- `step98_step96_regression_guard_pass = true`.
- `step98_step94_regression_guard_pass = true`.
- `step98_artifact_budget_pass = true`.
- `step98_activation_feature_count = 5`.
- `step98_completed_lbm_steps = 1`.
- `step98_n_grid = 48`.
- `step98_grid_48_enabled_count = 1`.
- `step98_grid_64_enabled_count = 0`.
- `step98_squid_proxy_enabled_count = 1`.
- `step98_runtime_geometry_enabled_count = 1`.
- `step98_wall_velocity_enabled_count = 1`.
- `step98_ggui_screenshot_count = 1`.
- `step98_ggui_video_count = 0`.
- `step98_vtr_count = 0`.
- `step98_particle_npy_count = 0`.

### Step97 Regression Guard

Generate:

- `outputs/step99_step97_regression_guard/step97_regression_guard.json`.
- `outputs/step99_step97_regression_guard/step97_regression_guard.csv`.
- `outputs/step99_step97_regression_guard/step97_regression_guard_summary.csv`.

The summary must prove:

- Step97 plan pass.
- Step97 guard pass.
- Step97 Step96 regression pass.
- Step97 Step94 regression pass.
- Step97 Step92 regression pass.
- Step97 output guard pass.
- Step97 artifact budget pass.
- `step97_activation_feature_count = 0`.
- `planned_step98_activation_feature_count = 5`.
- No Step97 driver run dir, screenshot, video, VTR, or particle NPY.

### Step96 Regression Guard

Generate:

- `outputs/step99_step96_regression_guard/step96_regression_guard.json`.
- `outputs/step99_step96_regression_guard/step96_regression_guard.csv`.
- `outputs/step99_step96_regression_guard/step96_regression_guard_summary.csv`.

The summary must prove:

- Step96 matrix pass.
- Step96 quality pass.
- Step96 activation guard pass.
- Step96 output guard pass.
- Step96 artifact budget pass.
- `step96_activation_feature_count = 4`.
- `step96_completed_lbm_steps = 10`.
- `step96_n_grid = 32`.
- Step96 squid proxy, runtime geometry, wall velocity, and screenshot counts remain accepted.
- No Step96 video, VTR, or particle NPY.

## Step99 Output Guard

Generate:

- `outputs/step99_output_guard/output_guard.json`.
- `outputs/step99_output_guard/output_guard.csv`.
- `outputs/step99_output_guard/output_guard_summary.csv`.

The summary must prove:

- `output_guard_pass = true`.
- `step99_driver_run_dir_count = 0`.
- `step99_ggui_screenshot_count = 0`.
- `step99_ggui_video_count = 0`.
- `step99_vtr_count = 0`.
- `step99_particle_npy_count = 0`.
- `step99_raw_geometry_output_count = 0`.
- `step99_real_geometry_candidate_output_count = 0`.
- `step99_dense_wall_velocity_output_count = 0`.
- `step99_sparse_wall_velocity_output_count = 0`.
- `step99_dense_displacement_output_count = 0`.
- `step99_displaced_particle_output_count = 0`.
- `private_absolute_path_count = 0`.
- `protected_sim_edit_count = 0`.
- `protected_diagnostics_edit_count = 0`.
- `protected_external_edit_count = 0`.
- `protected_real_geometry_candidate_edit_count = 0`.
- `step99_large_file_count = 0`.

## Step99 Artifact Manifest

Generate:

- `outputs/step99_artifact_manifest/artifact_manifest.csv`.
- `outputs/step99_artifact_manifest/artifact_summary.csv`.
- `outputs/step99_artifact_manifest/artifact_summary.json`.

The summary must prove:

- `artifact_budget_pass = true`.
- `step99_file_count <= 70`.
- `step99_total_size_mb < 5`.
- `step99_driver_run_dir_count = 0`.
- `step99_ggui_screenshot_count = 0`.
- `step99_ggui_video_count = 0`.
- `step99_vtr_count = 0`.
- `step99_particle_npy_count = 0`.
- `large_file_count = 0`.
- `private_absolute_path_count = 0`.
- `protected_external_taichi_lbm3d_step99_file_count = 0`.
- `protected_real_geometry_candidates_step99_file_count = 0`.
- `raw_geometry_file_count = 0`.

Do not hardcode exact manifest byte totals in the prose report because the report can change the manifest size. Keep exact totals in `artifact_summary.json`.

## Tests

Add contract tests:

- `tests/test_step99_48cube_5step_taichi_ggui_visualization_plan_contract.py`.
- `tests/test_step99_48cube_5step_taichi_ggui_visualization_guard_contract.py`.
- `tests/test_step99_step98_regression_contract.py`.
- `tests/test_step99_step97_regression_contract.py`.
- `tests/test_step99_step96_regression_contract.py`.
- `tests/test_step99_output_guard_contract.py`.

The tests must read committed Step99 output artifacts and assert the contract fields above. They must not import heavy solver modules or execute the driver.

## Report Requirements

`STEP99_48CUBE_5STEP_TAICHI_GGUI_VISUALIZATION_PLAN_AND_GUARD_REPORT.md` must clearly state:

- Step99 accepted.
- Step99 is plan-and-guard only.
- Step99 does not run `FSIDriver3D`.
- Step99 does not call `driver.run()`.
- Step99 does not execute simulation.
- Step99 does not open a GGUI window.
- Step99 does not write screenshots, video, VTK, or particle NPY.
- Step99 only plans and guards the future Step100 row.
- Step100 may run exactly one 48 grid, 1024-particle, 5-step, moving-boundary, engineering row with squid proxy, diagnostic-only runtime geometry, solid velocity wall velocity, GGUI screenshot, no video, no VTK, no particle dumps.
- The only intended expansion from Step98 is `n_lbm_steps = 1 -> 5`.
- Step100 must not enable 64 grid, VTK, particle NPY, video, real geometry candidate data, link-area transfer, solver formula changes, physical validation, production readiness, real squid validation, or squid swimming claims.

## Verification Commands

Run these with the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step99_48cube_5step_taichi_ggui_visualization_plan.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step99_48cube_5step_taichi_ggui_visualization_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step99_step98_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step99_step97_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step99_step96_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step99_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step99_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step99_48cube_5step_taichi_ggui_visualization_plan_contract.py tests\test_step99_48cube_5step_taichi_ggui_visualization_guard_contract.py tests\test_step99_step98_regression_contract.py tests\test_step99_step97_regression_contract.py tests\test_step99_step96_regression_contract.py tests\test_step99_output_guard_contract.py -q
```

Full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Git checks:

- `git diff --check`.
- `git diff --cached --check`.
- `git status --short external/taichi_LBM3D`.
- `git status --short data/real_geometry_candidates`.
- Run the existing legacy-output grep command from the task handoff; it must return no output. Do not write its literal legacy tokens into repo files.

## Done Criteria

Step99 is done only when:

- Goal file exists and the active goal references it.
- Step99 plan, guard, regression guards, output guard, artifact manifest, docs, report, tests, logs, and outputs are generated.
- Step99 has no driver run, no simulation run, no GGUI run, and no screenshot/video/VTK/particle outputs.
- Step99 does not edit forbidden solver, diagnostics, vendor, or real-geometry-candidate paths.
- Focused Step99 tests pass.
- Full tests pass with the trusted Taichi interpreter.
- Full tests pass with Anaconda Python.
- Git diff checks pass.
- Final commit message is `test: add step99 48cube 5step taichi ggui visualization plan and guard`.
- The validated commit is pushed to `origin/main`.
