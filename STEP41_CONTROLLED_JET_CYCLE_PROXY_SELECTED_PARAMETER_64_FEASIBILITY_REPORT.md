# Step 41 Controlled Jet-Cycle Proxy Selected-Parameter 64 Feasibility Report

## 1. Goal

Step 41 is controlled jet-cycle proxy selected-parameter 64^3 feasibility.
Step 41 selects one accepted wall velocity scale from Step 40.
Step 41 remains tethered and proxy-only.
Step 41 does not validate a real jet.
Step 41 does not validate jet propulsion.
Step 41 does not implement free-body motion.
Step 41 does not implement squid swimming.
Step 41 does not implement real squid validation.
Step 41 does not change moving bounce-back formulas.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

The detailed goal file is `STEP41_CONTROLLED_JET_CYCLE_PROXY_SELECTED_PARAMETER_64_FEASIBILITY_GOAL.md`.

## 2. Files Created And Updated

Created:

- `configs/step41_wall_velocity_application_scale_0050_64.json`
- `configs/step41_64_static_moving_boundary.json`
- `configs/step41_64_experimental_moving_boundary_scale_0050.json`
- `configs/step41_64_static_link_area.json`
- `configs/step41_64_experimental_link_area_scale_0050.json`
- `src/selected_parameter_64_feasibility.py`
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
- `tests/test_step41_selected_parameter_64_feasibility_contract.py`
- `docs/41_controlled_jet_cycle_proxy_selected_parameter_64_feasibility.md`

Updated:

- `README.md`

## 3. Explicit Non-Goals

Step 41 does not add propulsion physics, body-motion integration, swimming displacement, two-phase physics, contact-angle physics, solver formula changes, LBM population updates from the wall-velocity application, MPM forcing from the wall-velocity application, projection forcing from the wall-velocity application, or vendored `external/taichi_LBM3D` edits.

## 4. Selected Parameter Config Validation

Output: `outputs/step41_selected_parameter_config_validation/selected_parameter_config_validation.json`

Result:

- `application_config_count = 1`
- `driver_config_count = 4`
- `static_config_count = 2`
- `experimental_config_count = 2`
- `selected_wall_velocity_scale = 0.05`
- `wall_velocity_cap_lbm = 0.01`
- `all_driver_n_grid_64 = true`
- `all_driver_40_steps = true`
- `all_target_u_lbm_zero = true`
- `validation_pass = true`

## 5. 64^3 Selected Parameter Driver

Output: `outputs/step41_64_selected_parameter_driver/selected_parameter_64_results.json`

Result:

- `row_count = 4`
- `stable_count = 4`
- `quality_pass_count = 4`
- `static_row_count = 2`
- `experimental_row_count = 2`
- `engineering_row_count = 2`
- `link_area_row_count = 2`
- `min_completed_lbm_steps = 40`
- `min_total_mpm_substeps = 200`
- `min_rho_min_global = 0.9690961241722107`
- `max_rho_max_global = 1.0409393310546875`
- `max_lbm_max_v_global = 0.012116076424717903`
- `min_mpm_min_J_global = 0.9959453344345093`
- `min_projected_mass_min = 0.02294033206999302`
- `min_active_cell_count = 9837`
- `min_bb_link_count_max = 27540`
- `max_applied_velocity_norm = 0.00721642344030184`

Implementation note: the selected scale and cap remain `0.05` and `0.01`. The Step 41 64^3 driver configs use `dynamic_solid_threshold = 0.75` as a configuration-level boundary activation threshold to keep the one-cycle 64^3 density envelope bounded without changing solver formulas.

## 6. 64^3 Feasibility Summary

Output: `outputs/step41_64_feasibility_summary/feasibility_summary.json`

Result:

- `driver_row_count = 4`
- `stable_count = 4`
- `selected_scale = 0.05`
- `n_grid = 64`
- `one_cycle_pass = true`
- `feasibility_pass = true`
- `max_applied_velocity_norm = 0.00721642344030184`

## 7. Static Vs Experimental 64^3 Comparison

Output: `outputs/step41_static_vs_experimental_64_comparison/static_vs_experimental_64.json`

Result:

- `row_count = 2`
- `comparison_pass_count = 2`
- `comparison_pass = true`
- engineering `projected_mass_delta = 2.0489096641540527e-08`
- link-area `projected_mass_delta = -5.587935447692871e-09`

## 8. Engineering Vs Link-Area 64^3 Comparison

Output: `outputs/step41_engineering_vs_link_area_64_comparison/engineering_vs_link_area_64.json`

Result:

- `row_count = 1`
- `comparison_pass_count = 1`
- `comparison_pass = true`
- `wall_velocity_scale = 0.05`
- `link_area_scale_final = 0.8088821768760681`
- `max_applied_velocity_norm_delta = 0.0`

## 9. Wall Velocity 64^3 Quality

Output: `outputs/step41_wall_velocity_64_quality/wall_velocity_64_quality.json`

Result:

- `row_count = 2`
- `pass_count = 2`
- `quality_pass = true`
- `selected_scale = 0.05`
- `cap_value = 0.01`
- `min_timeseries_row_count = 40`
- `min_applied_cell_count = 5056`
- `max_applied_velocity_norm = 0.00721642344030184`
- `max_lbm_population_update_count = 0`

## 10. Cycle Proxy 64^3 Diagnostics

Output: `outputs/step41_cycle_proxy_64_diagnostics/cycle_proxy_64_diagnostics.json`

Result:

- `cycle_period_steps = 40`
- `cycle_count = 1`
- `cycle_proxy_64_pass = true`
- `phase_alignment_pass = true`
- `cavity_volume_cycle_pass = true`
- `funnel_aperture_cycle_pass = true`
- `expelled_volume_proxy = 0.0027022723369117957`
- `refill_volume_proxy = 0.0027022723369117957`
- `net_cycle_volume_proxy = 0.0`

## 11. Force And Impulse 64^3 Summary

Output: `outputs/step41_force_impulse_64_summary/force_impulse_64_summary.json`

Result:

- `row_count = 4`
- `response_finite_pass_count = 4`
- `force_impulse_64_pass = true`
- all hydro-force, bounce-back correction, link-count, and impulse proxy values are finite

## 12. Tethered No-Free-Body Guard

Output: `outputs/step41_tethered_no_free_body_guard/tethered_no_free_body_guard.json`

Result:

- `guard_pass = true`
- `config_count = 4`
- `free_body_state_file_count = 0`
- `body_trajectory_output_count = 0`
- `rigid_body_integrator_enabled = false`
- `body_position_state_enabled = false`
- `swimming_displacement_claim_enabled = false`
- `target_u_lbm_zero_for_cycle_configs = true`

## 13. Quality Report Aggregation

Output: `outputs/step41_quality_report_aggregation/quality_report_summary.json`

Result:

- `quality_report_count = 4`
- `pass_count = 4`
- `strict_count = 4`
- `warning_count = 0`
- `error_count = 0`

## 14. Step 40 Regression Guard

Output: `outputs/step41_step40_regression_guard/step40_regression_guard.json`

Result:

- `row_count = 10`
- `pass_count = 10`
- `regression_pass = true`
- Step 40 driver, parameter sensitivity, cap diagnostics, tethered guard, and artifact policy remain passing

## 15. Artifact Manifest Summary

Output: `outputs/step41_artifact_manifest/artifact_summary.json`

Result:

- `large_file_count = 0`
- `step41_file_count = 96`
- `step41_total_size_mb = 3.450411796569824`
- `total_size_mb = 161.83606433868408`
- `raw_candidate_large_file_count = 0`
- `scan_data_file_count = 0`
- `private_absolute_path_count = 0`
- `step41_vtr_count = 0`
- `step41_particle_npy_count = 0`

## 16. Verification Commands

Executed:

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
```

Final pytest logs:

- `logs/step41_pytest.log`: `425 passed in 4.56s`
- `logs/step41_contract_pytest.log`: `16 passed in 0.10s`

Whitespace and push checks are recorded in the final assistant response after this report is committed.

## 17. GitHub Sync Information

Target branch: `main`.

Target remote: `origin/main`.

The final pushed commit hash is reported after the GitHub push completes.

## 18. Acceptance Checklist

- [x] Step 41 detailed goal file exists
- [x] selected parameter config validation passes
- [x] selected wall_velocity_scale is 0.05
- [x] velocity cap is 0.01
- [x] driver config count is 4
- [x] all configs use n_grid=64
- [x] static configs keep wall_velocity_application_mode disabled
- [x] experimental configs use solid_vel_experimental
- [x] no config enables LBM population update
- [x] no config enables moving-bounceback formula edits
- [x] selected parameter driver runs 4 rows
- [x] all rows complete at least 40 LBM steps
- [x] all rows complete at least 200 MPM substeps
- [x] experimental rows write at least 40 wall velocity application reports
- [x] max applied velocity norm stays below the configured cap
- [x] rho_min is greater than 0.95
- [x] rho_max is less than 1.05
- [x] lbm_max_v is less than 0.1
- [x] mpm_min_J is greater than 0
- [x] projected_mass is greater than 0
- [x] active_cell_count is greater than 0
- [x] bb_link_count is greater than 0
- [x] no NaN is present
- [x] no Inf is present
- [x] 64^3 feasibility summary passes
- [x] static vs experimental 64^3 comparison passes
- [x] engineering vs link_area 64^3 comparison passes
- [x] wall velocity 64^3 quality passes
- [x] cycle proxy 64^3 diagnostics pass
- [x] force/impulse 64^3 summary passes
- [x] tethered no-free-body guard passes
- [x] no free-body state files exist
- [x] no body trajectory output exists
- [x] no swimming displacement claim exists
- [x] quality report aggregation passes
- [x] Step 40 regression guard passes
- [x] default boundary_motion_mode remains static
- [x] default wall_velocity_application_mode remains disabled
- [x] no default behavior changes
- [x] no solver formula changes
- [x] no external/taichi_LBM3D edits
- [x] no Step 41 VTR outputs
- [x] no Step 41 particle NPY outputs
- [x] artifact large_file_count is 0
- [x] Step 41 output total-size budget passes
- [x] repo artifact summary total_size_mb is below 300

## 19. Decision For Step 42

Step 41 is acceptable as a controlled 64^3 selected-parameter feasibility artifact.

Recommended Step 42: `Controlled Squid Proxy Prescribed Geometry Displacement Diagnostics`, still diagnostic-only and not driver-coupled.
