# Step 40 Controlled Jet-Cycle Proxy Parameter Sensitivity Smoke Report

## 1. Goal

Step 40 is controlled jet-cycle proxy parameter sensitivity smoke.
Step 40 varies wall velocity scale only.
Step 40 remains tethered and proxy-only.
Step 40 does not validate a real jet.
Step 40 does not validate jet propulsion.
Step 40 does not implement free-body motion.
Step 40 does not implement squid swimming.
Step 40 does not implement real squid validation.
Step 40 does not change moving bounce-back formulas.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

The detailed goal file is `STEP40_CONTROLLED_JET_CYCLE_PROXY_PARAMETER_SENSITIVITY_SMOKE_GOAL.md`.

## 2. Files Created And Updated

Created:

- `configs/step40_wall_velocity_application_scale_0025.json`
- `configs/step40_wall_velocity_application_scale_0050.json`
- `configs/step40_wall_velocity_application_scale_0075.json`
- `configs/step40_static_48_moving_boundary.json`
- `configs/step40_static_48_link_area.json`
- `configs/step40_experimental_48_moving_boundary_scale_0025.json`
- `configs/step40_experimental_48_moving_boundary_scale_0050.json`
- `configs/step40_experimental_48_moving_boundary_scale_0075.json`
- `configs/step40_experimental_48_link_area_scale_0025.json`
- `configs/step40_experimental_48_link_area_scale_0050.json`
- `configs/step40_experimental_48_link_area_scale_0075.json`
- `src/jet_cycle_parameter_sensitivity.py`
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
- `tests/test_step40_jet_cycle_parameter_sensitivity_contract.py`
- `docs/40_controlled_jet_cycle_proxy_parameter_sensitivity_smoke.md`

Updated:

- `README.md`

## 3. Explicit Non-Goals

Step 40 does not add a propulsion model, body-motion integration, swimming motion, two-phase physics, contact-angle physics, solver formula changes, moving-bounceback formula changes, LBM population updates from the wall-velocity application, MPM forcing from the wall-velocity application, projection forcing from the wall-velocity application, or vendored `external/taichi_LBM3D` edits.

## 4. Parameter Config Validation

Output: `outputs/step40_parameter_config_validation/parameter_config_validation.json`

Result:

- `application_config_count = 3`
- `driver_config_count = 8`
- `scale_values = [0.025, 0.05, 0.075]`
- all caps are `0.01`
- `static_disabled_count = 2`
- `experimental_config_count = 6`
- `validation_pass = true`

## 5. Parameter Sweep Driver

Output: `outputs/step40_parameter_sweep_driver/parameter_sweep_results.json`

Result:

- `row_count = 8`
- `stable_count = 8`
- `quality_pass_count = 8`
- `static_row_count = 2`
- `experimental_row_count = 6`
- `scale_count = 3`
- `transfer_mode_count = 2`
- `min_completed_lbm_steps = 40`
- `min_total_mpm_substeps = 200`
- `min_rho_min_global = 0.9828528761863708`
- `max_rho_max_global = 1.0134063959121704`
- `max_lbm_max_v_global = 0.01099871564656496`
- `min_mpm_min_J_global = 0.9909236431121826`
- `min_projected_mass_min = 0.02294032648205757`
- `min_active_cell_count = 4856`
- `min_bb_link_count_max = 6652`
- `max_applied_velocity_norm = 0.00967813097947864`

## 6. Parameter Sensitivity Summary

Output: `outputs/step40_parameter_sensitivity_summary/parameter_sensitivity_summary.json`

Result:

- `experimental_row_count = 6`
- `scale_count = 3`
- `engineering_row_count = 3`
- `link_area_row_count = 3`
- `all_experimental_rows_stable = true`
- `cap_value = 0.01`
- `max_applied_velocity_norm = 0.00967813097947864`
- `applied_velocity_response_pass = true`
- `parameter_sensitivity_pass = true`
- `cap_saturation_observed = false`

## 7. Static Vs Parameter Comparison

Output: `outputs/step40_static_vs_parameter_comparison/static_vs_parameter_comparison.json`

Result:

- `row_count = 6`
- `comparison_pass_count = 6`
- `comparison_pass = true`
- maximum projected mass delta magnitude was below `1e-3`
- all experimental rows had positive applied velocity

## 8. Engineering Vs Link-Area Parameter Comparison

Output: `outputs/step40_engineering_vs_link_area_parameter_comparison/engineering_vs_link_area_parameter.json`

Result:

- `row_count = 3`
- `comparison_pass_count = 3`
- `comparison_pass = true`
- `link_area_scale_final` stayed between `0.7795953750610352` and `0.8936212062835693`
- projected mass deltas stayed finite and bounded

## 9. Cap Saturation Diagnostics

Output: `outputs/step40_cap_saturation_diagnostics/cap_saturation_diagnostics.json`

Result:

- `row_count = 6`
- `cap_value = 0.01`
- `cap_hit_count = 0`
- `cap_hit_observed = false`
- `cap_pass = true`
- `cap_saturation_diagnostics_pass = true`

## 10. Force And Impulse Parameter Response

Output: `outputs/step40_force_impulse_parameter_response/force_impulse_parameter_response.json`

Result:

- `row_count = 8`
- `response_finite_pass_count = 8`
- `force_impulse_parameter_response_pass = true`
- force, bounce-back correction integral, bounce-back link-count integral, and impulse proxy values were finite
- bounce-back link-count integral proxy stayed positive for every row

These are existing-diagnostics proxy summaries only.

## 11. Tethered No-Free-Body Guard

Output: `outputs/step40_tethered_no_free_body_guard/tethered_no_free_body_guard.json`

Result:

- `config_count = 8`
- `free_body_state_file_count = 0`
- `body_trajectory_output_count = 0`
- `rigid_body_integrator_enabled = false`
- `body_position_state_enabled = false`
- `swimming_displacement_claim_enabled = false`
- `target_u_lbm_zero_for_cycle_configs = true`
- `guard_pass = true`

## 12. Quality Report Aggregation

Output: `outputs/step40_quality_report_aggregation/quality_report_summary.json`

Result:

- `quality_report_count = 8`
- `pass_count = 8`
- `strict_count = 8`
- `warning_count = 0`
- `error_count = 0`

## 13. Step 39 Regression Guard

Output: `outputs/step40_step39_regression_guard/step39_regression_guard.json`

Result:

- `row_count = 10`
- `pass_count = 10`
- `regression_pass = true`

The guard confirms that the accepted Step 39 report, multicycle driver, proxy diagnostics, drift summary, wall-velocity quality, tethered guard, and artifact budget evidence remain present and passing.

## 14. Artifact Manifest Summary

Output: `outputs/step40_artifact_manifest/artifact_summary.json`

Result:

- `file_count = 2672`
- `large_file_count = 0`
- `step40_file_count = 142`
- `step40_total_size_mb = 3.368701934814453`
- `total_size_mb = 158.09438514709473`
- `step40_vtr_count = 0`
- `step40_particle_npy_count = 0`
- `raw_candidate_large_file_count = 0`
- `scan_data_file_count = 0`
- `private_absolute_path_count = 0`

## 15. Verification Commands

Executed:

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
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step40_jet_cycle_parameter_sensitivity_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step40_artifact_manifest.py
```

Final results:

- `logs/step40_pytest.log`: `409 passed in 4.55s`
- `logs/step40_contract_pytest.log`: `16 passed in 0.10s`
- final artifact manifest passed after pytest logs were generated

## 16. GitHub Sync Information

Branch: `main`

Remote: `origin`

Final commit hash is reported with the push result.

## 17. Acceptance Checklist

- [x] Step 40 detailed goal file exists
- [x] parameter config validation passes
- [x] application config count is 3
- [x] driver config count is 8
- [x] wall_velocity_scale values are 0.025, 0.05, 0.075
- [x] velocity cap is 0.01 for all experimental configs
- [x] static configs keep wall_velocity_application_mode disabled
- [x] experimental configs use solid_vel_experimental
- [x] no config enables LBM population update
- [x] no config enables moving bounce-back formula changes
- [x] parameter sweep driver runs 8 rows
- [x] static engineering baseline passes
- [x] static link_area baseline passes
- [x] experimental engineering scale 0.025 passes
- [x] experimental engineering scale 0.05 passes
- [x] experimental engineering scale 0.075 passes
- [x] experimental link_area scale 0.025 passes
- [x] experimental link_area scale 0.05 passes
- [x] experimental link_area scale 0.075 passes
- [x] all rows complete at least 40 LBM steps
- [x] all rows complete at least 200 MPM substeps
- [x] experimental rows write at least 40 wall-velocity application reports
- [x] max applied velocity norm stays below the configured cap
- [x] applied velocity response summary passes
- [x] cap saturation diagnostics pass
- [x] rho_min is greater than 0.95
- [x] rho_max is less than 1.05
- [x] lbm_max_v is less than 0.1
- [x] mpm_min_J is greater than 0
- [x] projected_mass is greater than 0
- [x] active_cell_count is greater than 0
- [x] bb_link_count is greater than 0
- [x] no NaN is present
- [x] no Inf is present
- [x] static vs parameter comparison passes
- [x] engineering vs link_area parameter comparison passes
- [x] force/impulse parameter response passes
- [x] tethered no-free-body guard passes
- [x] no free-body state files exist
- [x] no body trajectory output exists
- [x] no swimming displacement claim exists
- [x] quality report aggregation passes
- [x] Step 39 regression guard passes
- [x] default boundary_motion_mode remains static
- [x] default wall_velocity_application_mode remains disabled
- [x] no default behavior changes
- [x] no moving bounce-back formula changes
- [x] no LBM collision formula changes
- [x] no MPM constitutive formula changes
- [x] no projection formula changes
- [x] no external/taichi_LBM3D edits
- [x] no physical jet-validation claim
- [x] no propulsion-validation claim
- [x] no squid swimming claim
- [x] no real-squid-validation claim
- [x] no Step 40 VTR outputs
- [x] no Step 40 particle NPY outputs
- [x] artifact large_file_count is 0 after final manifest
- [x] Step 40 output total-size budget passes after final manifest
- [x] repo artifact summary total_size_mb is below 280 after final manifest
- [x] logs/step40_pytest.log exists after final pytest
- [x] full pytest passes after final pytest
- [x] Step 40 contract test passes after final pytest
- [x] git diff --check passes after final diff check
- [x] staged whitespace check passes after final staging
- [x] pre-push hook passes after push
- [x] Step 40 artifacts are pushed to origin/main after push

## 18. Decision For Step 41

Step 40 passes its controlled parameter sensitivity smoke criteria. Step 41 should select a conservative accepted scale, such as `0.05` or `0.025`, and run `Controlled Jet-Cycle Proxy Selected-Parameter 64^3 Feasibility`. Step 41 should remain tethered and proxy-only.
