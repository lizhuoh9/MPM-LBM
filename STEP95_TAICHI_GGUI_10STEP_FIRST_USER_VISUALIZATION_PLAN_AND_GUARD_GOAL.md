# Step95 Taichi GGUI 10-Step First User Visualization Plan And Guard Goal

## Source Baseline

- Current accepted upstream baseline: `origin/main = a255713f9148f8046b81595d6e2ce4152920d057`.
- Previous completed step: Step94, committed as `test: add step94 taichi ggui visualization smoke`.
- Step94 accepted route: Taichi GGUI screenshot-only visualization smoke, 32^3 grid, 1 LBM step.
- Deprecated route: the older Step93 VTR enablement route must remain replaced by the Step94 GGUI route.
- Step95 must be the next step. The repository must not already contain Step95 acceptance artifacts before this implementation.

## Goal

Implement Step95 as a plan-and-guard-only step for the next real run, Step96.

Step95 must produce repository-tracked plan, guard, regression, output, manifest, docs, and test artifacts proving:

- A future Step96 Taichi GGUI 10-step first-user visualization run is planned.
- The Step96 plan combines the Step92 10-step first-user dry-run envelope with the Step94 Taichi GGUI screenshot-only visualization path.
- Step95 itself does not execute the simulation, does not open a GGUI window, and does not create screenshots, videos, VTR, particle NPY, raw geometry, or dense field outputs.
- Step95 preserves the existing Step92, Step93, and Step94 evidence contracts.

The correct final Step95 claim is exactly:

`Taichi GGUI 10-step first-user visualization run is planned and guarded for Step96.`

## Step95 Scope

Step95 is strictly plan-and-guard only.

Allowed work:

- Add Step95 configuration JSON files.
- Add Step95 evidence scripts under `src/mpm_lbm/evidence/`.
- Add Step95 baseline runner scripts under `baseline_tests/`.
- Add Step95 contract tests under `tests/`.
- Add Step95 docs and reports.
- Generate Step95 plan, guard, regression, output guard, artifact manifest, and log artifacts.
- Update allowed project status docs if needed.
- Commit and push the verified Step95 implementation to `origin/main`.

Forbidden work:

- Do not run `FSIDriver3D`.
- Do not call `driver.run()`.
- Do not run any simulation.
- Do not open a Taichi GGUI window.
- Do not create a screenshot.
- Do not create video output.
- Do not create VTR output.
- Do not create particle NPY output.
- Do not activate real geometry candidates.
- Do not activate link-area logic.
- Do not activate 48^3 or 64^3 grids.
- Do not add dense wall velocity output.
- Do not add dense displacement output.
- Do not change solver formulas.
- Do not migrate tau behavior.
- Do not claim physical validation.
- Do not claim production readiness.
- Do not claim real squid validation.
- Do not claim squid swimming.
- Do not claim squid actuation.

## Protected Paths

Step95 must not edit these paths:

- `src/mpm_lbm/sim/**`
- `src/mpm_lbm/diagnostics/**`
- `src/mpm_lbm/sim/drivers/**`
- `src/mpm_lbm/sim/coupling/**`
- `src/mpm_lbm/sim/lbm/**`
- `src/mpm_lbm/sim/mpm/**`
- `src/mpm_lbm/sim/geometry/**`
- `src/mpm_lbm/sim/motion/**`
- `src/mpm_lbm/sim/wall_velocity/**`
- `external/taichi_LBM3D/**`
- `data/real_geometry_candidates/**`

Allowed documentation updates:

- `README.md`
- `docs/00_project_status.md`
- `docs/ACTIVATION_PRECONDITIONS.md`
- `docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md`
- `docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md`

## Planned Step96 Row

Step95 must plan and guard this future Step96 row:

`first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run`

Required Step96 planned fields:

```json
{
  "n_grid": 32,
  "n_particles": 1024,
  "n_lbm_steps": 10,
  "mpm_substeps_per_lbm_step": 1,
  "coupling_mode": "moving_boundary",
  "reaction_transfer_mode": "engineering",
  "target_u_lbm": [0.0, 0.0, 0.0],
  "geometry_type": "squid_proxy",
  "geometry_config_path": "configs/step85_squid_proxy_geometry_1024.json",
  "quality_check_enabled": true,
  "quality_check_strict": false,
  "geometry_motion_mode": "prescribed_kinematic",
  "geometry_motion_application_mode": "diagnostic_only",
  "geometry_motion_config_path": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
  "geometry_motion_application_config_path": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
  "geometry_motion_report_enabled": true,
  "geometry_motion_application_report_enabled": true,
  "boundary_motion_mode": "prescribed_kinematic",
  "boundary_motion_config_path": "configs/step34_boundary_motion_interface_prescribed_kinematic.json",
  "boundary_motion_report_enabled": true,
  "wall_velocity_application_mode": "solid_vel_experimental",
  "wall_velocity_application_config_path": "configs/step36_wall_velocity_application_solid_vel_experimental.json",
  "wall_velocity_application_report_enabled": true,
  "target_lbm_field": "solid_vel",
  "ggui_visualization_enabled": true,
  "ggui_screenshot_enabled": true,
  "ggui_video_enabled": false,
  "write_vtk": false,
  "write_particles": false,
  "output_interval": 1
}
```

Relationship to prior steps:

- From Step94 to Step96: expand duration from `n_lbm_steps = 1` to `n_lbm_steps = 10`, keep the same GGUI screenshot-only route, and keep video/VTR/particle NPY disabled.
- From Step92 to Step96: keep the 10-step first-user dry-run envelope and add Taichi GGUI visualization.
- Step95 activation feature count must remain `0`.
- Planned Step96 activation feature count must be `4`.

## Required Files

Root:

- `STEP95_TAICHI_GGUI_10STEP_FIRST_USER_VISUALIZATION_PLAN_AND_GUARD_GOAL.md`
- `STEP95_TAICHI_GGUI_10STEP_FIRST_USER_VISUALIZATION_PLAN_AND_GUARD_REPORT.md`

Configs:

- `configs/step95_taichi_ggui_10step_visualization_plan.json`
- `configs/step95_taichi_ggui_10step_visualization_guard_policy.json`
- `configs/step95_step94_regression_policy.json`
- `configs/step95_step93_regression_policy.json`
- `configs/step95_step92_regression_policy.json`
- `configs/step95_output_guard_policy.json`
- `configs/step95_artifact_manifest_policy.json`

Evidence scripts:

- `src/mpm_lbm/evidence/step95_taichi_ggui_10step_visualization_plan.py`
- `src/mpm_lbm/evidence/step95_taichi_ggui_10step_visualization_guard.py`
- `src/mpm_lbm/evidence/step95_step94_regression_guard.py`
- `src/mpm_lbm/evidence/step95_step93_regression_guard.py`
- `src/mpm_lbm/evidence/step95_step92_regression_guard.py`
- `src/mpm_lbm/evidence/step95_output_guard.py`

Baseline runners:

- `baseline_tests/step95_common.py`
- `baseline_tests/run_step95_taichi_ggui_10step_visualization_plan.py`
- `baseline_tests/run_step95_taichi_ggui_10step_visualization_guard.py`
- `baseline_tests/run_step95_step94_regression_guard.py`
- `baseline_tests/run_step95_step93_regression_guard.py`
- `baseline_tests/run_step95_step92_regression_guard.py`
- `baseline_tests/run_step95_output_guard.py`
- `baseline_tests/run_step95_artifact_manifest.py`

Tests:

- `tests/test_step95_taichi_ggui_10step_visualization_plan_contract.py`
- `tests/test_step95_taichi_ggui_10step_visualization_guard_contract.py`
- `tests/test_step95_step94_regression_contract.py`
- `tests/test_step95_step93_regression_contract.py`
- `tests/test_step95_step92_regression_contract.py`
- `tests/test_step95_output_guard_contract.py`

Docs:

- `docs/95_taichi_ggui_10step_first_user_visualization_plan_and_guard.md`

Output directories:

- `outputs/step95_taichi_ggui_10step_visualization_plan/`
- `outputs/step95_taichi_ggui_10step_visualization_guard/`
- `outputs/step95_step94_regression_guard/`
- `outputs/step95_step93_regression_guard/`
- `outputs/step95_step92_regression_guard/`
- `outputs/step95_output_guard/`
- `outputs/step95_artifact_manifest/`

Logs:

- `logs/step95_*.log`

## Plan Config Contract

`configs/step95_taichi_ggui_10step_visualization_plan.json` must include these contract fields:

- `step = "Step95"`
- `campaign_id = "step95_taichi_ggui_10step_first_user_visualization_plan_and_guard"`
- `previous_step = "Step94"`
- `previous_required_commit = "a255713f9148f8046b81595d6e2ce4152920d057"`
- `activation_kind = "taichi_ggui_10step_visualization_plan_only"`
- `driver_run_required = false`
- `fsidriver_run_allowed = false`
- `simulation_run_allowed = false`
- `ggui_run_allowed = false`
- `screenshot_output_allowed_in_step95 = false`
- `step96_allowed = true`
- `step96_allowed_row_name = "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run"`
- `step96_allowed_n_grid = 32`
- `step96_allowed_n_particles = 1024`
- `step96_allowed_n_lbm_steps = 10`
- `step96_allowed_mpm_substeps_per_lbm_step = 1`
- `step96_allowed_coupling_mode = "moving_boundary"`
- `step96_allowed_reaction_transfer_mode = "engineering"`
- `step96_allowed_output_interval = 1`
- `from_step94_duration_expansion = true`
- `previous_step94_n_lbm_steps = 1`
- `planned_step96_n_lbm_steps = 10`
- `from_step92_adds_ggui_visualization = true`
- `previous_step92_n_lbm_steps = 10`
- `ggui_visualization_planned_for_step96 = true`
- `ggui_interactive_window_allowed_for_step96 = true`
- `ggui_screenshot_allowed_for_step96 = true`
- `ggui_video_allowed_for_step96 = false`
- `ggui_required_backend_policy = "local_desktop_taichi_environment"`
- `ggui_screenshot_count_allowed_for_step96 = 1`
- `squid_proxy_planned_for_step96 = true`
- `geometry_type_allowed_for_step96 = "squid_proxy"`
- `geometry_config_path_allowed_for_step96 = "configs/step85_squid_proxy_geometry_1024.json"`
- `quality_check_enabled_allowed_for_step96 = true`
- `quality_check_strict_allowed_for_step96 = false`
- `geometry_quality_report_required_for_step96 = true`
- `runtime_geometry_planned_for_step96 = true`
- `geometry_motion_mode_allowed_for_step96 = "prescribed_kinematic"`
- `geometry_motion_application_mode_allowed_for_step96 = "diagnostic_only"`
- `geometry_motion_config_path_allowed_for_step96 = "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json"`
- `geometry_motion_application_config_path_allowed_for_step96 = "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json"`
- `geometry_motion_interface_report_required_for_step96 = true`
- `geometry_mutation_allowed = false`
- `wall_velocity_planned_for_step96 = true`
- `boundary_motion_mode_allowed_for_step96 = "prescribed_kinematic"`
- `boundary_motion_config_path_allowed_for_step96 = "configs/step34_boundary_motion_interface_prescribed_kinematic.json"`
- `boundary_motion_report_required_for_step96 = true`
- `wall_velocity_application_mode_allowed_for_step96 = "solid_vel_experimental"`
- `wall_velocity_application_config_path_allowed_for_step96 = "configs/step36_wall_velocity_application_solid_vel_experimental.json"`
- `wall_velocity_application_report_required_for_step96 = true`
- `target_lbm_field_planned_for_step96 = "solid_vel"`
- `target_u_lbm_allowed_for_step96 = [0.0, 0.0, 0.0]`
- `target_u_lbm_policy = "same_zero_background_flow_as_step90_step92_step94"`
- `combined_runtime_geometry_wall_velocity_planned_for_step96 = true`
- `planned_step96_activation_feature_count = 4`
- `step95_activation_feature_count = 0`
- `write_vtk_allowed = false`
- `write_particles_allowed = false`
- `vtr_output_allowed = false`
- `particle_npy_output_allowed = false`
- `video_output_allowed = false`
- `real_geometry_allowed = false`
- `real_geometry_candidate_data_allowed = false`
- `link_area_allowed = false`
- `grid_48_allowed = false`
- `grid_64_allowed = false`
- `dense_wall_velocity_output_allowed = false`
- `dense_displacement_output_allowed = false`
- `runtime_code_changed = false`
- `solver_behavior_changed = false`
- `solver_formula_change_allowed = false`
- `tau_migration_allowed = false`
- `physical_validation_claim_allowed = false`
- `production_readiness_claim_allowed = false`
- `real_squid_validation_claim_allowed = false`
- `squid_swimming_claim_allowed = false`
- `squid_actuation_claim_allowed = false`

## Evidence Output Contracts

The plan output summary must include:

- `step95_taichi_ggui_10step_visualization_plan_pass = true`
- `driver_run_required = false`
- `fsidriver_run_allowed = false`
- `simulation_run_allowed = false`
- `ggui_run_allowed = false`
- `screenshot_output_allowed_in_step95 = false`
- `step95_activation_feature_count = 0`
- `planned_step96_activation_feature_count = 4`

The visualization guard output summary must include:

- `step95_taichi_ggui_10step_visualization_guard_pass = true`
- `guard_row_count > 0`
- `guard_pass_count = guard_row_count`
- `step95_activation_feature_count = 0`
- `planned_step96_activation_feature_count = 4`
- GGUI planned for Step96: true
- Step96 screenshot planned: true
- Step96 video planned: false
- Step96 squid proxy planned: true
- Step96 runtime geometry planned: true
- Step96 wall velocity planned: true
- Step96 combined runtime geometry and wall velocity planned: true
- VTR, particle NPY, video, real geometry, real geometry candidate data, link-area, 48^3, and 64^3 planned: all false

Step94 regression guard must prove:

- Step94 matrix, quality, activation, output, Step93 regression, Step92 regression, Step90 regression, and artifact summary outputs pass.
- Step94 activation feature count is 4.
- Step94 GGUI visualization enabled count is 1.
- Step94 screenshot count is 1.
- Step94 video count is 0.
- Step94 VTR count is 0.
- Step94 particle NPY count is 0.
- Step94 completed LBM steps is 1.

Step93 regression guard must prove:

- Step93 plan, guard, output, artifact, and regression outputs pass.
- Step93 activation feature count is 0.
- Step93 planned Step94 activation feature count is 4.
- Step93 driver run directory count is 0.
- Step93 screenshot count is 0.
- Step93 VTR count is 0.
- Step93 particle NPY count is 0.

Step92 regression guard must prove:

- Step92 matrix, quality, activation, output, and artifact outputs pass.
- Step92 activation feature count is 3.
- Step92 completed LBM steps is 10.
- Step92 squid proxy count is 1.
- Step92 runtime geometry count is 1.
- Step92 wall velocity count is 1.
- Step92 VTR count is 0.
- Step92 particle NPY count is 0.

Output guard must prove:

- Step95 driver run directory count is 0.
- Step95 screenshot count is 0.
- Step95 video count is 0.
- Step95 VTR count is 0.
- Step95 particle NPY count is 0.
- Step95 raw geometry output count is 0.
- Step95 real geometry candidate output count is 0.
- Step95 dense wall velocity output count is 0.
- Step95 sparse wall velocity output count is 0.
- Step95 dense displacement output count is 0.
- Step95 displaced particle output count is 0.
- Step95 private path count is 0.
- Step95 protected sim/diagnostics/external/real-geometry candidate edit count is 0.
- Step95 large file count is 0.

Artifact manifest must prove:

- `artifact_budget_pass = true`
- `step95_file_count <= 70`
- `step95_total_size_mb < 5`
- `step95_driver_run_dir_count = 0`
- `step95_ggui_screenshot_count = 0`
- `step95_ggui_video_count = 0`
- `step95_vtr_count = 0`
- `step95_particle_npy_count = 0`
- Step95 large/private/protected/raw output counts are all 0.

## Verification Commands

Run these baseline commands with the trusted Taichi environment:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step95_taichi_ggui_10step_visualization_plan.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step95_taichi_ggui_10step_visualization_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step95_step94_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step95_step93_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step95_step92_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step95_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step95_artifact_manifest.py
```

Run focused Step95 tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step95_taichi_ggui_10step_visualization_plan_contract.py tests\test_step95_taichi_ggui_10step_visualization_guard_contract.py tests\test_step95_step94_regression_contract.py tests\test_step95_step93_regression_contract.py tests\test_step95_step92_regression_contract.py tests\test_step95_output_guard_contract.py -q
```

Run full test suites:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Run boundary and diff checks:

```powershell
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Run the legacy Step93 file-visualization route-token grep from the source
instructions. The final `git grep` must produce no matches.

## Report Requirements

`STEP95_TAICHI_GGUI_10STEP_FIRST_USER_VISUALIZATION_PLAN_AND_GUARD_REPORT.md` must state:

- Step95 is accepted.
- Step95 is plan-and-guard only.
- Step95 did not run `FSIDriver3D`.
- Step95 did not call `driver.run()`.
- Step95 did not run a simulation.
- Step95 did not open a GGUI window.
- Step95 did not create a screenshot.
- Step95 did not create video output.
- Step95 did not create VTR output.
- Step95 did not create particle NPY output.
- Step95 only plans the Step96 row.
- Step96 combines Step92 10-step first-user dry run and Step94 GGUI screenshot path.
- Step96 must not enable VTR, particle NPY, real geometry, link-area, 48^3, 64^3, solver formula changes, physical validation claims, or production readiness claims.

## Commit And Push

After all verification passes:

```powershell
git add .
git diff --cached --check
git commit -m "test: add step95 taichi ggui 10step visualization plan and guard"
git push origin main
```

After pushing, verify the remote main commit and report:

- Final local commit hash.
- Remote branch pushed: `origin/main`.
- Verification commands and results.
- Any skipped or failed checks, if applicable.
