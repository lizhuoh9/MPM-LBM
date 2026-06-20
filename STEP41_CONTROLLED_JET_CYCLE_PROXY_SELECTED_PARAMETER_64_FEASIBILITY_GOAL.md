# Step 41 Controlled Jet-Cycle Proxy Selected-Parameter 64^3 Feasibility Goal

## Objective

Implement Step 41 as a controlled, tethered, proxy-only 64^3 feasibility check for one selected wall-velocity parameter accepted by Step 40. Step 41 selects `wall_velocity_scale = 0.05` with `wall_velocity_cap_lbm = 0.01`, runs a one-cycle 64^3 matrix, and verifies that the existing moving-wall jet-cycle proxy path remains stable, finite, cap-safe, and bounded at the larger grid size.

The deliverable must include explicit configs, source-level postprocessing helpers, baseline runners, committed output artifacts, contract tests, documentation, a final report, verification logs, a clean artifact manifest, and a pushed GitHub commit on `origin/main`.

## Scope Statement

Step 41 is controlled jet-cycle proxy selected-parameter 64^3 feasibility.

Step 41 selects one accepted wall velocity scale from Step 40.

Step 41 remains tethered and proxy-only.

Step 41 does not validate a real jet.

Step 41 does not validate jet propulsion.

Step 41 does not implement free-body motion.

Step 41 does not implement squid swimming.

Step 41 does not implement real squid validation.

Step 41 does not change moving bounce-back formulas.

The default `boundary_motion_mode` remains `static`.

The default `wall_velocity_application_mode` remains `disabled`.

## Selected Parameter

Use:

- `wall_velocity_scale = 0.05`
- `wall_velocity_cap_lbm = 0.01`

Rationale:

- `0.05` is the accepted baseline scale used through the earlier moving-wall work.
- Step 40 showed `0.025`, `0.05`, and `0.075` were stable at 48^3.
- `0.05` is more conservative than `0.075` while remaining representative of the existing baseline response.
- `0.025` remains a future fallback if a later 64^3 expansion requires lower actuation magnitude.

## Non-Goals And Hard Boundaries

Do not implement or claim any of the following:

- real jet validation
- jet propulsion validation
- free-body motion
- rigid-body integration
- body trajectory integration
- squid swimming
- swimming displacement
- real squid validation
- production sharp-interface FSI
- two-phase flow
- contact angle physics
- new coupling formulas
- moving bounce-back formula changes
- LBM collision formula changes
- LBM streaming formula changes
- MPM constitutive formula changes
- projection formula changes
- default wall-velocity application
- default boundary motion
- edits under `external/taichi_LBM3D`
- raw real-geometry files or scan-data artifacts

Allowed work is limited to:

- explicit Step 41 selected-parameter application config
- explicit Step 41 64^3 one-cycle driver configs
- static-vs-experimental 64^3 comparison
- `engineering` vs `link_area_experimental` 64^3 comparison
- wall-velocity application quality at 64^3
- cycle proxy diagnostics at 64^3
- force, bounce-back, and impulse proxy summaries at 64^3
- tethered no-free-body guard
- Step 40 regression guard
- small CSV/JSON/NPZ/log artifacts

## Driver Matrix

Run a one-cycle 64^3 selected-parameter feasibility matrix with four rows:

- 64^3 static moving_boundary engineering, 40 steps
- 64^3 experimental moving_boundary engineering, scale 0.05, 40 steps
- 64^3 static moving_boundary link_area_experimental, 40 steps
- 64^3 experimental moving_boundary link_area_experimental, scale 0.05, 40 steps

Common driver parameters:

- `n_grid = 64`
- `n_particles = 4096`
- `n_lbm_steps = 40`
- `mpm_substeps_per_lbm_step = 5`
- `output_interval = 1`
- `target_u_lbm = [0.0, 0.0, 0.0]`
- `quality_check_enabled = true`
- `quality_check_strict = true`
- `write_vtk = false`
- `write_particles = false`
- `geometry_type = squid_proxy`
- `geometry_config_path = configs/step30_squid_proxy_geometry.json`
- `coupling_mode = moving_boundary`
- `link_area_policy = inverse_length`

Static rows must use:

- `boundary_motion_mode = static`
- `wall_velocity_application_mode = disabled`
- no boundary-motion config path
- no wall-velocity application config path

Experimental rows must use:

- `boundary_motion_mode = prescribed_kinematic`
- `boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json`
- `boundary_motion_report_enabled = true`
- `wall_velocity_application_mode = solid_vel_experimental`
- `wall_velocity_application_config_path = configs/step41_wall_velocity_application_scale_0050_64.json`
- `wall_velocity_application_report_enabled = true`

## Required Configs

Add one application config:

- `configs/step41_wall_velocity_application_scale_0050_64.json`

It must keep:

- `application_mode = solid_vel_experimental`
- `target_lbm_field = solid_vel`
- `application_policy = additive_capped`
- `wall_velocity_scale = 0.05`
- `wall_velocity_cap_lbm = 0.01`
- `apply_to_lbm_solid_vel = true`
- `apply_to_lbm_populations = false`
- `apply_to_mpm = false`
- `apply_to_projector = false`
- `modify_bounceback_formula = false`
- `jet_model_enabled = false`
- `actuation_claim_enabled = false`
- `diagnostic_report_enabled = true`

Add four driver configs:

- `configs/step41_64_static_moving_boundary.json`
- `configs/step41_64_experimental_moving_boundary_scale_0050.json`
- `configs/step41_64_static_link_area.json`
- `configs/step41_64_experimental_link_area_scale_0050.json`

## Source Additions

Add `src/selected_parameter_64_feasibility.py`.

This source module must aggregate and validate Step 41 artifacts only. It must not change solver, coupler, LBM, MPM, projection, or moving-bounceback formulas.

Required responsibilities:

- load Step 41 driver rows
- summarize selected-parameter 64^3 feasibility
- compare 64^3 static vs experimental rows
- compare 64^3 experimental engineering vs link-area rows
- summarize 64^3 wall-velocity quality
- summarize one-cycle cavity, funnel, and phase proxy diagnostics
- summarize force, bounce-back, and impulse proxy response
- write small CSV/JSON outputs
- expose finite and bounded checks reusable by baseline runners and tests

No hydro-force, bounce-back, or impulse proxy monotonicity is required.

## Required Baseline Runners

Add:

- `baseline_tests/step41_common.py`
- `baseline_tests/run_step41_selected_parameter_config_validation.py`
- `baseline_tests/run_step41_64_selected_parameter_driver.py`
- `baseline_tests/run_step41_64_feasibility_summary.py`
- `baseline_tests/run_step41_static_vs_experimental_64_comparison.py`
- `baseline_tests/run_step41_engineering_vs_link_area_64_comparison.py`
- `baseline_tests/run_step41_wall_velocity_64_quality.py`
- `baseline_tests/run_step41_cycle_proxy_64_diagnostics.py`
- `baseline_tests/run_step41_force_impulse_64_summary.py`
- `baseline_tests/run_step41_tethered_no_free_body_guard.py`
- `baseline_tests/run_step41_quality_report_aggregation.py`
- `baseline_tests/run_step41_step40_regression_guard.py`
- `baseline_tests/run_step41_artifact_manifest.py`

### Selected Parameter Config Validation

Outputs:

- `outputs/step41_selected_parameter_config_validation/selected_parameter_config_validation.csv`
- `outputs/step41_selected_parameter_config_validation/selected_parameter_config_validation.json`
- `logs/step41_selected_parameter_config_validation.log`

Acceptance:

- `driver_config_count == 4`
- `static_config_count == 2`
- `experimental_config_count == 2`
- `selected_wall_velocity_scale == 0.05`
- `wall_velocity_cap_lbm == 0.01`
- all driver configs use `n_grid == 64`
- all driver configs use `n_lbm_steps == 40`
- all driver configs use `target_u_lbm == [0.0, 0.0, 0.0]`
- static configs use `wall_velocity_application_mode == disabled`
- experimental configs use `wall_velocity_application_mode == solid_vel_experimental`
- `apply_to_lbm_populations == false`
- `modify_bounceback_formula == false`
- `jet_model_enabled == false`
- `validation_pass == true`

### 64^3 Selected Parameter Driver

Outputs:

- `outputs/step41_64_selected_parameter_driver/selected_parameter_64_results.csv`
- `outputs/step41_64_selected_parameter_driver/selected_parameter_64_results.json`
- `outputs/step41_64_selected_parameter_driver/selected_parameter_64_results.npz`
- per-case `diagnostics_timeseries.csv`
- per-experimental-case `wall_velocity_application_timeseries.csv`
- per-case `geometry_quality_report.json`
- `logs/step41_64_selected_parameter_driver.log`

Acceptance:

- `row_count == 4`
- `stable_count == 4`
- `static_row_count == 2`
- `experimental_row_count == 2`
- `engineering_row_count == 2`
- `link_area_row_count == 2`
- `min_completed_lbm_steps >= 40`
- `min_total_mpm_substeps >= 200`
- `rho_min_global > 0.95`
- `rho_max_global < 1.05`
- `lbm_max_v_global < 0.1`
- `mpm_min_J_global > 0`
- `projected_mass_min > 0`
- `active_cell_count > 0`
- `bb_link_count_max > 0`
- no NaN
- no Inf

Experimental row acceptance:

- `wall_velocity_application_report_count >= 40`
- `applied_cell_count_min > 0`
- `max_applied_velocity_norm <= 0.01`
- `lbm_population_update_count == 0`
- `modify_bounceback_formula == false`

### 64^3 Feasibility Summary

Outputs:

- `outputs/step41_64_feasibility_summary/feasibility_summary.csv`
- `outputs/step41_64_feasibility_summary/feasibility_summary.json`
- `logs/step41_64_feasibility_summary.log`

Acceptance:

- `driver_row_count == 4`
- `stable_count == 4`
- `selected_scale == 0.05`
- `n_grid == 64`
- `one_cycle_pass == true`
- `feasibility_pass == true`
- `min_rho_min_global > 0.95`
- `max_rho_max_global < 1.05`
- `max_lbm_max_v_global < 0.1`
- `min_mpm_min_J_global > 0`
- `min_projected_mass_min > 0`
- `min_active_cell_count > 0`
- `max_applied_velocity_norm <= 0.01`

### Static Vs Experimental 64^3 Comparison

Outputs:

- `outputs/step41_static_vs_experimental_64_comparison/static_vs_experimental_64.csv`
- `outputs/step41_static_vs_experimental_64_comparison/static_vs_experimental_64.json`
- `logs/step41_static_vs_experimental_64_comparison.log`

Acceptance:

- `row_count == 2`
- `comparison_pass_count == 2`
- both rows stable
- density, velocity, MPM, projected mass, active-cell, and bounce-back deltas are finite
- `abs(projected_mass_delta) <= 2e-3`
- active-cell and bounce-back deltas are bounded
- experimental applied velocity is positive

### Engineering Vs Link-Area 64^3 Comparison

Outputs:

- `outputs/step41_engineering_vs_link_area_64_comparison/engineering_vs_link_area_64.csv`
- `outputs/step41_engineering_vs_link_area_64_comparison/engineering_vs_link_area_64.json`
- `logs/step41_engineering_vs_link_area_64_comparison.log`

Acceptance:

- `row_count == 1`
- `comparison_pass == true`
- both rows stable
- `link_area_scale_final` finite
- `0.25 <= link_area_scale_final <= 2.0`
- density, velocity, MPM, projected mass, and applied velocity deltas are finite

### Wall Velocity 64^3 Quality

Outputs:

- `outputs/step41_wall_velocity_64_quality/wall_velocity_64_quality.csv`
- `outputs/step41_wall_velocity_64_quality/wall_velocity_64_quality.json`
- `logs/step41_wall_velocity_64_quality.log`

Acceptance:

- `row_count == 2`
- each row has at least 40 timeseries rows
- `selected_scale == 0.05`
- `cap == 0.01`
- `applied_cell_count_min > 0`
- `max_applied_velocity_norm <= cap`
- `cap_pass == true`
- `lbm_population_update_count == 0`
- `repeatable_phase_sequence == true`
- `quality_pass == true`

### Cycle Proxy 64^3 Diagnostics

Outputs:

- `outputs/step41_cycle_proxy_64_diagnostics/cycle_proxy_64_diagnostics.csv`
- `outputs/step41_cycle_proxy_64_diagnostics/cycle_proxy_64_diagnostics.json`
- `logs/step41_cycle_proxy_64_diagnostics.log`

Acceptance:

- `cycle_period_steps == 40`
- `cycle_count == 1`
- `phase_alignment_pass == true`
- `cavity_volume_cycle_pass == true`
- `funnel_aperture_cycle_pass == true`
- `expelled_volume_proxy > 0`
- `refill_volume_proxy > 0`
- `abs(net_cycle_volume_proxy)` is within tolerance

### Force And Impulse 64^3 Summary

Outputs:

- `outputs/step41_force_impulse_64_summary/force_impulse_64_summary.csv`
- `outputs/step41_force_impulse_64_summary/force_impulse_64_summary.json`
- `logs/step41_force_impulse_64_summary.log`

Acceptance:

- `row_count == 4`
- `response_finite_pass_count == 4`
- hydro-force proxy is finite
- bounce-back correction integral proxy is finite
- bounce-back link-count integral proxy is positive
- impulse proxy is finite
- `force_impulse_64_pass == true`
- no physical impulse validation claim

### Tethered No-Free-Body Guard

Outputs:

- `outputs/step41_tethered_no_free_body_guard/tethered_no_free_body_guard.csv`
- `outputs/step41_tethered_no_free_body_guard/tethered_no_free_body_guard.json`
- `logs/step41_tethered_no_free_body_guard.log`

Acceptance:

- `guard_pass == true`
- `config_count == 4`
- `free_body_state_file_count == 0`
- `body_trajectory_output_count == 0`
- `rigid_body_integrator_enabled == false`
- `body_position_state_enabled == false`
- `swimming_displacement_claim_enabled == false`
- `target_u_lbm_zero_for_cycle_configs == true`

### Quality Report Aggregation

Outputs:

- `outputs/step41_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step41_quality_report_aggregation/quality_report_summary.json`
- `logs/step41_quality_report_aggregation.log`

Acceptance:

- `quality_report_count == 4`
- `pass_count == 4`
- `strict_count == 4`
- `warning_count == 0`
- `error_count == 0`

### Step 40 Regression Guard

Outputs:

- `outputs/step41_step40_regression_guard/step40_regression_guard.csv`
- `outputs/step41_step40_regression_guard/step40_regression_guard.json`
- `logs/step41_step40_regression_guard.log`

Acceptance:

- Step 40 report exists
- Step 40 driver `row_count == 8`
- Step 40 driver `stable_count == 8`
- Step 40 `scale_count == 3`
- Step 40 `parameter_sensitivity_pass == true`
- Step 40 `cap_pass == true`
- Step 40 tethered guard pass remains true
- Step 40 large-file count remains 0
- Step 40 VTR count remains 0
- Step 40 particle NPY count remains 0

### Artifact Manifest

Outputs:

- `outputs/step41_artifact_manifest/artifact_manifest.csv`
- `outputs/step41_artifact_manifest/artifact_summary.csv`
- `outputs/step41_artifact_manifest/artifact_summary.json`
- `logs/step41_artifact_manifest.log`

Acceptance:

- `large_file_count == 0`
- `step41_total_size_mb < 20`
- `total_size_mb < 300`
- `step41_vtr_count == 0`
- `step41_particle_npy_count == 0`
- `raw_candidate_large_file_count == 0`
- `scan_data_file_count == 0`
- `private_absolute_path_count == 0`

## Contract Test

Add `tests/test_step41_selected_parameter_64_feasibility_contract.py`.

The contract must include tests for:

- required artifacts exist
- selected parameter configs are valid
- 64^3 selected-parameter driver output is valid
- 64^3 feasibility summary is valid
- static vs experimental 64^3 comparison is valid
- engineering vs link-area 64^3 comparison is valid
- wall velocity 64^3 quality is valid
- cycle proxy 64^3 diagnostics are valid
- force/impulse 64^3 summary is valid
- tethered no-free-body guard is valid
- quality report aggregation is valid
- Step 40 regression guard is valid
- default modes remain unchanged
- docs scope and forbidden claims are valid
- artifact budget is valid
- final report acceptance is complete

Forbidden phrases for user-facing docs/report:

- `real jet validation`
- `jet propulsion is validated`
- `squid swimming is implemented`
- `free-body motion is implemented`
- `real squid simulation is validated`
- `production-ready sharp-interface FSI`
- `final solver readiness`
- `two-phase flow is implemented`
- `contact angle physics is implemented`
- `moving bounce-back formula is changed`
- `default wall velocity application is enabled`
- `64^3 validates propulsion`

## Documentation And Report

Add:

- `docs/41_controlled_jet_cycle_proxy_selected_parameter_64_feasibility.md`
- `STEP41_CONTROLLED_JET_CYCLE_PROXY_SELECTED_PARAMETER_64_FEASIBILITY_REPORT.md`

The report must include:

1. Goal
2. Files Created And Updated
3. Explicit Non-Goals
4. Selected Parameter Config Validation
5. 64^3 Selected Parameter Driver
6. 64^3 Feasibility Summary
7. Static Vs Experimental 64^3 Comparison
8. Engineering Vs Link-Area 64^3 Comparison
9. Wall Velocity 64^3 Quality
10. Cycle Proxy 64^3 Diagnostics
11. Force And Impulse 64^3 Summary
12. Tethered No-Free-Body Guard
13. Quality Report Aggregation
14. Step 40 Regression Guard
15. Artifact Manifest Summary
16. Verification Commands
17. GitHub Sync Information
18. Acceptance Checklist
19. Decision For Step 42

If Step 41 passes, the report should recommend Step 42 as `Controlled Squid Proxy Prescribed Geometry Displacement Diagnostics`, still diagnostic-only and not driver-coupled.

## Verification Commands

Use the workspace Taichi Python:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\selected_parameter_64_feasibility.py baseline_tests\step41_common.py baseline_tests\run_step41_selected_parameter_config_validation.py baseline_tests\run_step41_64_selected_parameter_driver.py baseline_tests\run_step41_64_feasibility_summary.py baseline_tests\run_step41_static_vs_experimental_64_comparison.py baseline_tests\run_step41_engineering_vs_link_area_64_comparison.py baseline_tests\run_step41_wall_velocity_64_quality.py baseline_tests\run_step41_cycle_proxy_64_diagnostics.py baseline_tests\run_step41_force_impulse_64_summary.py baseline_tests\run_step41_tethered_no_free_body_guard.py baseline_tests\run_step41_quality_report_aggregation.py baseline_tests\run_step41_step40_regression_guard.py baseline_tests\run_step41_artifact_manifest.py tests\test_step41_selected_parameter_64_feasibility_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step41_selected_parameter_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step41_64_selected_parameter_driver.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step41_64_feasibility_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step41_static_vs_experimental_64_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step41_engineering_vs_link_area_64_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step41_wall_velocity_64_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step41_cycle_proxy_64_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step41_force_impulse_64_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step41_tethered_no_free_body_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step41_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step41_step40_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step41_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step41_selected_parameter_64_feasibility_contract.py -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Write final pytest logs to:

- `logs/step41_pytest.log`
- `logs/step41_contract_pytest.log`

Regenerate the Step 41 artifact manifest after final pytest logs exist.

## GitHub Delivery

After implementation and verification:

- stage only Step 41-relevant files plus required README/doc/report updates
- verify `external/taichi_LBM3D` is unchanged
- verify `data/real_geometry_candidates` is unchanged except allowed small metadata if any
- commit with `test: add step41 selected parameter 64 feasibility`
- push to `origin/main`
- report final commit hash, remote branch, and verification results

## Acceptance Checklist

- [ ] Step 41 detailed goal file exists
- [ ] selected parameter config validation passes
- [ ] selected wall_velocity_scale is 0.05
- [ ] velocity cap is 0.01
- [ ] driver config count is 4
- [ ] all configs use n_grid=64
- [ ] static configs keep wall_velocity_application_mode disabled
- [ ] experimental configs use solid_vel_experimental
- [ ] no config enables LBM population update
- [ ] no config enables moving bounce-back formula changes
- [ ] selected parameter driver runs 4 rows
- [ ] static engineering 64^3 row passes
- [ ] experimental engineering 64^3 row passes
- [ ] static link_area 64^3 row passes
- [ ] experimental link_area 64^3 row passes
- [ ] all rows complete at least 40 LBM steps
- [ ] all rows complete at least 200 MPM substeps
- [ ] experimental rows write at least 40 wall velocity application reports
- [ ] max applied velocity norm stays below the configured cap
- [ ] rho_min is greater than 0.95
- [ ] rho_max is less than 1.05
- [ ] lbm_max_v is less than 0.1
- [ ] mpm_min_J is greater than 0
- [ ] projected_mass is greater than 0
- [ ] active_cell_count is greater than 0
- [ ] bb_link_count is greater than 0
- [ ] no NaN is present
- [ ] no Inf is present
- [ ] 64^3 feasibility summary passes
- [ ] static vs experimental 64^3 comparison passes
- [ ] engineering vs link_area 64^3 comparison passes
- [ ] wall velocity 64^3 quality passes
- [ ] cycle proxy 64^3 diagnostics pass
- [ ] force/impulse 64^3 summary passes
- [ ] tethered no-free-body guard passes
- [ ] no free-body state files exist
- [ ] no body trajectory output exists
- [ ] no swimming displacement claim exists
- [ ] quality report aggregation passes
- [ ] Step 40 regression guard passes
- [ ] default boundary_motion_mode remains static
- [ ] default wall_velocity_application_mode remains disabled
- [ ] no default behavior changes
- [ ] no moving bounce-back formula changes
- [ ] no LBM collision formula changes
- [ ] no MPM constitutive formula changes
- [ ] no projection formula changes
- [ ] no external/taichi_LBM3D edits
- [ ] no real jet validation claim
- [ ] no jet propulsion validation claim
- [ ] no squid swimming claim
- [ ] no real squid validation claim
- [ ] no Step 41 VTR outputs
- [ ] no Step 41 particle NPY outputs
- [ ] artifact large_file_count is 0
- [ ] Step 41 output total-size budget passes
- [ ] repo artifact summary total_size_mb is below 300
- [ ] logs/step41_pytest.log exists
- [ ] full pytest passes
- [ ] Step 41 contract test passes
- [ ] git diff --check passes
- [ ] staged whitespace check passes
- [ ] pre-push hook passes
- [ ] Step 41 artifacts are pushed to origin/main
