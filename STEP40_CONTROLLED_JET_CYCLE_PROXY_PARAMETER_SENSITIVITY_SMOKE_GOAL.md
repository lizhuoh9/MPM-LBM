# Step 40 Controlled Jet-Cycle Proxy Parameter Sensitivity Smoke Goal

## Objective

Implement Step 40 as a small, controlled, tethered, proxy-only parameter sensitivity smoke for the existing jet-cycle proxy path. Step 40 varies only `wall_velocity_scale` over a fixed one-cycle 48^3 driver matrix, then verifies that wall-velocity application, cycle proxy diagnostics, moving-boundary bounce-back diagnostics, force/impulse proxies, static comparisons, link-area comparisons, artifact budgets, and prior Step 39 acceptance evidence remain stable, bounded, and honestly described.

The Step 40 deliverable must include explicit configs, source-level aggregation helpers, baseline runners, committed output artifacts, contract tests, documentation, a final report, verification logs, and a pushed GitHub commit on `origin/main`.

## Scope Statement

Step 40 is controlled jet-cycle proxy parameter sensitivity smoke.

Step 40 varies wall velocity scale only.

Step 40 remains tethered and proxy-only.

Step 40 does not validate a real jet.

Step 40 does not validate jet propulsion.

Step 40 does not implement free-body motion.

Step 40 does not implement squid swimming.

Step 40 does not implement real squid validation.

Step 40 does not change moving bounce-back formulas.

The default `boundary_motion_mode` remains `static`.

The default `wall_velocity_application_mode` remains `disabled`.

## Non-Goals And Hard Boundaries

Do not implement or claim any of the following:

- real jet validation
- jet propulsion validation
- free-body motion
- rigid-body integration
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

- explicit Step 40 wall-velocity scale configs
- explicit Step 40 one-cycle driver configs
- static baseline comparison
- `engineering` vs `link_area_experimental` comparison
- cap/saturation diagnostics
- force, bounce-back, and impulse proxy response summaries
- parameter response envelope summaries
- Step 39 regression guards
- small CSV/JSON/NPZ/log artifacts

## Driver Matrix

Use a one-cycle 40-LBM-step parameter smoke, not a longer multi-cycle run. Step 39 already covered two-cycle stability; Step 40 answers a narrower scale-response question.

Common driver parameters:

- `n_grid = 48`
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

The main matrix has eight rows:

- static moving_boundary engineering, 40 steps
- static moving_boundary link_area_experimental, 40 steps
- experimental moving_boundary engineering, `wall_velocity_scale = 0.025`
- experimental moving_boundary engineering, `wall_velocity_scale = 0.050`
- experimental moving_boundary engineering, `wall_velocity_scale = 0.075`
- experimental moving_boundary link_area_experimental, `wall_velocity_scale = 0.025`
- experimental moving_boundary link_area_experimental, `wall_velocity_scale = 0.050`
- experimental moving_boundary link_area_experimental, `wall_velocity_scale = 0.075`

The fixed velocity cap is:

- `wall_velocity_cap_lbm = 0.01`

## Required Configs

Add three wall-velocity application configs:

- `configs/step40_wall_velocity_application_scale_0025.json`
- `configs/step40_wall_velocity_application_scale_0050.json`
- `configs/step40_wall_velocity_application_scale_0075.json`

Each application config must keep:

- `application_mode = solid_vel_experimental`
- `target_lbm_field = solid_vel`
- `application_policy = additive_capped`
- `wall_velocity_cap_lbm = 0.01`
- `apply_to_lbm_solid_vel = true`
- `apply_to_lbm_populations = false`
- `apply_to_mpm = false`
- `apply_to_projector = false`
- `modify_bounceback_formula = false`
- `jet_model_enabled = false`
- `actuation_claim_enabled = false`
- `diagnostic_report_enabled = true`

Only `wall_velocity_scale` changes across those configs.

Add eight driver configs:

- `configs/step40_static_48_moving_boundary.json`
- `configs/step40_static_48_link_area.json`
- `configs/step40_experimental_48_moving_boundary_scale_0025.json`
- `configs/step40_experimental_48_moving_boundary_scale_0050.json`
- `configs/step40_experimental_48_moving_boundary_scale_0075.json`
- `configs/step40_experimental_48_link_area_scale_0025.json`
- `configs/step40_experimental_48_link_area_scale_0050.json`
- `configs/step40_experimental_48_link_area_scale_0075.json`

Static configs must use:

- `boundary_motion_mode = static`
- `wall_velocity_application_mode = disabled`
- no application config path
- no boundary-motion config path

Experimental configs must use:

- `boundary_motion_mode = prescribed_kinematic`
- `boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json`
- `boundary_motion_report_enabled = true`
- `wall_velocity_application_mode = solid_vel_experimental`
- the corresponding Step 40 scale config path
- `wall_velocity_application_report_enabled = true`

## Source Additions

Add `src/jet_cycle_parameter_sensitivity.py`.

This source module must aggregate and validate Step 40 parameter-sweep artifacts only. It must not change solver, coupler, LBM, MPM, projection, or moving-bounceback formulas.

Required helper responsibilities:

- parse and normalize Step 40 scale labels
- summarize parameter driver rows
- summarize applied-velocity scale response
- summarize cap/saturation behavior
- compare static baselines with each experimental parameter row
- compare `engineering` and `link_area_experimental` rows by scale
- summarize force, bounce-back, and impulse proxy responses
- write small CSV/JSON outputs
- expose finite/bounded checks reusable by baseline runners and tests

The implementation must not require hydro-force or impulse proxy monotonicity. Step 40 only requires finite, bounded, stable, cap-respecting responses.

## Required Baseline Runners

Add:

- `baseline_tests/step40_common.py`
- `baseline_tests/run_step40_parameter_config_validation.py`
- `baseline_tests/run_step40_parameter_sweep_driver.py`
- `baseline_tests/run_step40_parameter_sensitivity_summary.py`
- `baseline_tests/run_step40_static_vs_parameter_comparison.py`
- `baseline_tests/run_step40_engineering_vs_link_area_parameter_comparison.py`
- `baseline_tests/run_step40_cap_saturation_diagnostics.py`
- `baseline_tests/run_step40_force_impulse_parameter_response.py`
- `baseline_tests/run_step40_tethered_no_free_body_guard.py`
- `baseline_tests/run_step40_quality_report_aggregation.py`
- `baseline_tests/run_step40_step39_regression_guard.py`
- `baseline_tests/run_step40_artifact_manifest.py`

### Parameter Config Validation

Outputs:

- `outputs/step40_parameter_config_validation/parameter_config_validation.csv`
- `outputs/step40_parameter_config_validation/parameter_config_validation.json`
- `logs/step40_parameter_config_validation.log`

Acceptance:

- application config count is 3
- driver config count is 8
- scale values are `[0.025, 0.05, 0.075]`
- every cap is `0.01`
- experimental configs apply only to `lbm.solid_vel`
- no config applies to LBM populations
- no config changes moving-bounceback formulas
- no config enables jet-model or actuation claims
- static configs keep wall-velocity application disabled
- validation pass is true

### Parameter Sweep Driver

Outputs:

- `outputs/step40_parameter_sweep_driver/parameter_sweep_results.csv`
- `outputs/step40_parameter_sweep_driver/parameter_sweep_results.json`
- `outputs/step40_parameter_sweep_driver/parameter_sweep_results.npz`
- per-case `diagnostics_timeseries.csv`
- per-experimental-case `wall_velocity_application_timeseries.csv`
- per-case `geometry_quality_report.json`
- `logs/step40_parameter_sweep_driver.log`

Acceptance:

- `row_count == 8`
- `stable_count == 8`
- `static_row_count == 2`
- `experimental_row_count == 6`
- `scale_count == 3`
- `transfer_mode_count == 2`
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

- `application_report_count >= 40`
- `applied_cell_count_min > 0`
- `max_applied_velocity_norm <= 0.01`
- `lbm_population_update_count == 0`
- `modify_bounceback_formula == false`

### Parameter Sensitivity Summary

Outputs:

- `outputs/step40_parameter_sensitivity_summary/parameter_sensitivity_summary.csv`
- `outputs/step40_parameter_sensitivity_summary/parameter_sensitivity_summary.json`
- `logs/step40_parameter_sensitivity_summary.log`

Acceptance:

- `experimental_row_count == 6`
- `scale_count == 3`
- `engineering_row_count == 3`
- `link_area_row_count == 3`
- all experimental rows are stable
- max applied velocity stays below cap
- applied velocity response passes
- parameter sensitivity passes

For each transfer mode, `max_applied_velocity_norm` must be nondecreasing with scale within tolerance, or capped. Cap saturation is recorded but is not a failure.

### Static Vs Parameter Comparison

Outputs:

- `outputs/step40_static_vs_parameter_comparison/static_vs_parameter_comparison.csv`
- `outputs/step40_static_vs_parameter_comparison/static_vs_parameter_comparison.json`
- `logs/step40_static_vs_parameter_comparison.log`

Acceptance:

- `row_count == 6`
- every comparison passes
- static and experimental rows are stable
- density, velocity, MPM, projected mass, active cell, and bounce-back deltas are finite and bounded
- experimental applied velocity is positive

### Engineering Vs Link-Area Parameter Comparison

Outputs:

- `outputs/step40_engineering_vs_link_area_parameter_comparison/engineering_vs_link_area_parameter.csv`
- `outputs/step40_engineering_vs_link_area_parameter_comparison/engineering_vs_link_area_parameter.json`
- `logs/step40_engineering_vs_link_area_parameter_comparison.log`

Acceptance:

- `row_count == 3`
- every scale comparison passes
- both transfer rows are stable
- `0.25 <= link_area_scale_final <= 2.0`
- projected-mass deltas are finite and bounded

### Cap Saturation Diagnostics

Outputs:

- `outputs/step40_cap_saturation_diagnostics/cap_saturation_diagnostics.csv`
- `outputs/step40_cap_saturation_diagnostics/cap_saturation_diagnostics.json`
- `logs/step40_cap_saturation_diagnostics.log`

Acceptance:

- `row_count == 6`
- `cap_value == 0.01`
- every row satisfies max applied velocity <= cap
- cap-hit count is finite
- cap saturation diagnostics pass

If `scale = 0.075` hits the cap, record it as an observation, not a failure.

### Force And Impulse Parameter Response

Outputs:

- `outputs/step40_force_impulse_parameter_response/force_impulse_parameter_response.csv`
- `outputs/step40_force_impulse_parameter_response/force_impulse_parameter_response.json`
- `logs/step40_force_impulse_parameter_response.log`

Acceptance:

- `row_count == 8`
- hydro-force proxy is finite
- bounce-back correction integral proxy is finite
- bounce-back link-count integral proxy is positive for moving-boundary rows
- impulse proxy is finite
- no physical monotonicity claim is required

### Tethered No-Free-Body Guard

Outputs:

- `outputs/step40_tethered_no_free_body_guard/tethered_no_free_body_guard.csv`
- `outputs/step40_tethered_no_free_body_guard/tethered_no_free_body_guard.json`
- `logs/step40_tethered_no_free_body_guard.log`

Acceptance:

- guard passes
- no free-body state files
- no body trajectory outputs
- no rigid-body integrator enabled
- no body-position state enabled
- no swimming displacement claim
- all Step 40 configs keep `target_u_lbm` zero

### Quality Report Aggregation

Outputs:

- `outputs/step40_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step40_quality_report_aggregation/quality_report_summary.json`
- `logs/step40_quality_report_aggregation.log`

Acceptance:

- `quality_report_count == 8`
- `pass_count == 8`
- `strict_count == 8`
- `warning_count == 0`
- `error_count == 0`

### Step 39 Regression Guard

Outputs:

- `outputs/step40_step39_regression_guard/step39_regression_guard.csv`
- `outputs/step40_step39_regression_guard/step39_regression_guard.json`
- `logs/step40_step39_regression_guard.log`

Acceptance:

- Step 39 report exists
- Step 39 multicycle driver row count remains 4
- Step 39 stable count remains 4
- Step 39 multicycle proxy pass remains true
- Step 39 drift summary pass remains true
- Step 39 wall velocity quality pass remains true
- Step 39 tethered guard pass remains true
- Step 39 large-file count remains 0
- Step 39 VTR count remains 0
- Step 39 particle NPY count remains 0

### Artifact Manifest

Outputs:

- `outputs/step40_artifact_manifest/artifact_manifest.csv`
- `outputs/step40_artifact_manifest/artifact_summary.csv`
- `outputs/step40_artifact_manifest/artifact_summary.json`
- `logs/step40_artifact_manifest.log`

Acceptance:

- `large_file_count == 0`
- `step40_total_size_mb < 25`
- `total_size_mb < 280`
- `step40_vtr_count == 0`
- `step40_particle_npy_count == 0`
- `raw_candidate_large_file_count == 0`
- `scan_data_file_count == 0`
- `private_absolute_path_count == 0`

## Contract Test

Add `tests/test_step40_jet_cycle_parameter_sensitivity_contract.py`.

The contract must include tests for:

- required artifacts exist
- parameter configs are valid
- parameter sweep driver output is valid
- parameter sensitivity summary is valid
- static vs parameter comparison is valid
- engineering vs link-area comparison is valid
- cap saturation diagnostics are valid
- force/impulse response is valid
- tethered no-free-body guard is valid
- quality report aggregation is valid
- Step 39 regression guard is valid
- default modes remain unchanged
- docs scope and forbidden claims are valid
- artifact budget is valid
- final report acceptance is complete
- no physical validation claims are made

Forbidden phrases must include:

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
- `wall velocity scale physically validates propulsion`

## Documentation And Report

Add:

- `docs/40_controlled_jet_cycle_proxy_parameter_sensitivity_smoke.md`
- `STEP40_CONTROLLED_JET_CYCLE_PROXY_PARAMETER_SENSITIVITY_SMOKE_REPORT.md`

The report must include:

1. Goal
2. Files Created And Updated
3. Explicit Non-Goals
4. Parameter Config Validation
5. Parameter Sweep Driver
6. Parameter Sensitivity Summary
7. Static Vs Parameter Comparison
8. Engineering Vs Link-Area Parameter Comparison
9. Cap Saturation Diagnostics
10. Force And Impulse Parameter Response
11. Tethered No-Free-Body Guard
12. Quality Report Aggregation
13. Step 39 Regression Guard
14. Artifact Manifest Summary
15. Verification Commands
16. GitHub Sync Information
17. Acceptance Checklist
18. Decision For Step 41

If Step 40 passes, the report should recommend Step 41 as `Controlled Jet-Cycle Proxy Selected-Parameter 64^3 Feasibility`, still tethered and proxy-only.

## Verification Commands

Use the workspace Taichi Python:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\jet_cycle_parameter_sensitivity.py baseline_tests\step40_common.py baseline_tests\run_step40_parameter_config_validation.py baseline_tests\run_step40_parameter_sweep_driver.py baseline_tests\run_step40_parameter_sensitivity_summary.py baseline_tests\run_step40_static_vs_parameter_comparison.py baseline_tests\run_step40_engineering_vs_link_area_parameter_comparison.py baseline_tests\run_step40_cap_saturation_diagnostics.py baseline_tests\run_step40_force_impulse_parameter_response.py baseline_tests\run_step40_tethered_no_free_body_guard.py baseline_tests\run_step40_quality_report_aggregation.py baseline_tests\run_step40_step39_regression_guard.py baseline_tests\run_step40_artifact_manifest.py tests\test_step40_jet_cycle_parameter_sensitivity_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step40_parameter_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step40_parameter_sweep_driver.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step40_parameter_sensitivity_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step40_static_vs_parameter_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step40_engineering_vs_link_area_parameter_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step40_cap_saturation_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step40_force_impulse_parameter_response.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step40_tethered_no_free_body_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step40_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step40_step39_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step40_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step40_jet_cycle_parameter_sensitivity_contract.py -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Write final pytest logs to:

- `logs/step40_pytest.log`
- `logs/step40_contract_pytest.log`

Regenerate the Step 40 artifact manifest after final pytest logs exist.

## GitHub Delivery

After implementation and verification:

- stage only Step 40-relevant files plus required README/doc/report updates
- verify `external/taichi_LBM3D` is unchanged
- verify `data/real_geometry_candidates` is unchanged except allowed small metadata if any
- commit with `test: add step40 jet cycle parameter sensitivity smoke`
- push to `origin/main`
- report final commit hash, remote branch, and verification results

## Acceptance Checklist

- [ ] Step 40 detailed goal file exists
- [ ] parameter config validation passes
- [ ] application config count is 3
- [ ] driver config count is 8
- [ ] wall_velocity_scale values are 0.025, 0.05, 0.075
- [ ] velocity cap is 0.01 for all experimental configs
- [ ] static configs keep wall_velocity_application_mode disabled
- [ ] experimental configs use solid_vel_experimental
- [ ] no config enables LBM population update
- [ ] no config enables moving bounce-back formula changes
- [ ] parameter sweep driver runs 8 rows
- [ ] static engineering baseline passes
- [ ] static link_area baseline passes
- [ ] experimental engineering scale 0.025 passes
- [ ] experimental engineering scale 0.05 passes
- [ ] experimental engineering scale 0.075 passes
- [ ] experimental link_area scale 0.025 passes
- [ ] experimental link_area scale 0.05 passes
- [ ] experimental link_area scale 0.075 passes
- [ ] all rows complete at least 40 LBM steps
- [ ] all rows complete at least 200 MPM substeps
- [ ] experimental rows write at least 40 wall-velocity application reports
- [ ] max applied velocity norm stays below the configured cap
- [ ] applied velocity response summary passes
- [ ] cap saturation diagnostics pass
- [ ] rho_min is greater than 0.95
- [ ] rho_max is less than 1.05
- [ ] lbm_max_v is less than 0.1
- [ ] mpm_min_J is greater than 0
- [ ] projected_mass is greater than 0
- [ ] active_cell_count is greater than 0
- [ ] bb_link_count is greater than 0
- [ ] no NaN is present
- [ ] no Inf is present
- [ ] static vs parameter comparison passes
- [ ] engineering vs link_area parameter comparison passes
- [ ] force/impulse parameter response passes
- [ ] tethered no-free-body guard passes
- [ ] no free-body state files exist
- [ ] no body trajectory output exists
- [ ] no swimming displacement claim exists
- [ ] quality report aggregation passes
- [ ] Step 39 regression guard passes
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
- [ ] no Step 40 VTR outputs
- [ ] no Step 40 particle NPY outputs
- [ ] artifact large_file_count is 0
- [ ] Step 40 output total-size budget passes
- [ ] repo artifact summary total_size_mb is below 280
- [ ] logs/step40_pytest.log exists
- [ ] full pytest passes
- [ ] Step 40 contract test passes
- [ ] git diff --check passes
- [ ] staged whitespace check passes
- [ ] pre-push hook passes
- [ ] Step 40 artifacts are pushed to origin/main
