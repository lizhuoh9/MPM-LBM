# Step 36 Controlled Moving-Wall Bounce-Back Velocity Application Smoke Report

## 1. Goal

Step 36 is controlled moving-wall bounce-back velocity application smoke. It adds an opt-in experimental bridge from Step 35 wall velocity diagnostics into the existing LBM `solid_vel` wall-velocity channel.

## 2. Files Created And Updated

- Added `src/wall_velocity_application_config.py`.
- Added `src/wall_velocity_application.py`.
- Updated `src/fsi_config.py` with default-disabled wall velocity application fields.
- Updated `src/fsi_driver.py` with a projection-after, bounce-back-before application hook.
- Added Step 36 configs, baseline runners, docs, contract tests, reports, logs, and output artifacts.
- Updated the Step 35 contract boundary so later driver orchestration work does not fail the old diagnostic-only test.

## 3. Explicit Non-Goals

Step 36 does not change moving bounce-back formulas. Step 36 does not update LBM populations outside the existing bounce-back step. Step 36 does not implement a jet model. Step 36 does not implement squid swimming. Step 36 does not implement real squid validation. Step 36 does not edit `external/taichi_LBM3D`.

## 4. Application Config Validation

`outputs/step36_wall_velocity_application_config_validation/application_config_validation.json` passes 19 of 19 checks.

Key guarded values:

- `application_mode = solid_vel_experimental`
- `target_lbm_field = solid_vel`
- `wall_velocity_scale = 0.05`
- `wall_velocity_cap_lbm = 0.01`
- `apply_to_lbm_populations = false`
- `modify_bounceback_formula = false`

## 5. Application Report

`outputs/step36_wall_velocity_application_report/application_report.json` passes with 63 Step 35 rows available, 2136 applied cells on the 48^3 sample, and max capped velocity norm 0.005849450792213756.

## 6. Static Regression Smoke

`outputs/step36_static_regression_smoke/static_regression_results.json` contains 3 stable default-disabled rows. Static rows write no wall velocity application report and have `applied_cell_count == 0`.

## 7. Experimental Application Smoke

`outputs/step36_experimental_application_smoke/experimental_application_results.json` contains 3 stable opt-in rows. Each experimental row writes a passing wall velocity application report. The maximum applied velocity norm is 0.005866361313097195 and direct LBM population update count is 0.

## 8. Static Vs Experimental Comparison

`outputs/step36_static_vs_experimental_comparison/static_vs_experimental.json` passes bounded comparison for matching grid and transfer modes. The comparison is a smoke check, not a claim of physical equivalence.

## 9. Mass Force Stability Diagnostics

`outputs/step36_mass_force_stability_diagnostics/mass_force_stability.json` passes for all experimental rows. Density stays in the accepted short-smoke range, bounce-back corrections remain measurable, and no direct population writes are reported.

## 10. Wall Velocity Application Quality

`outputs/step36_wall_velocity_application_quality/application_quality.json` passes for all 3 experimental reports. Each report is finite, capped, nonzero, `solid_vel`-only, and formula-preserving.

## 11. Quality Report Aggregation

`outputs/step36_quality_report_aggregation/quality_report_summary.json` aggregates 6 strict procedural squid proxy quality reports. All pass with severity `ok` and zero warnings/reasons.

## 12. Step 35 Regression Guard

`outputs/step36_step35_regression_guard/step35_regression_guard.json` passes. Step 35 remains diagnostic-only: 63 rows, no LBM application, no LBM population update, and no moving bounce-back update.

## 13. Artifact Manifest Summary

`outputs/step36_artifact_manifest/artifact_summary.json` records the Step 36 artifact budget. Step 36 writes no `.vtr` output and no particle `.npy` output.

## 14. Verification Commands

These commands are the Step 36 verification surface:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\wall_velocity_application_config.py src\wall_velocity_application.py src\fsi_config.py src\fsi_driver.py baseline_tests\step36_common.py baseline_tests\run_step36_wall_velocity_application_config_validation.py baseline_tests\run_step36_wall_velocity_application_report.py baseline_tests\run_step36_static_regression_smoke.py baseline_tests\run_step36_experimental_application_smoke.py baseline_tests\run_step36_static_vs_experimental_comparison.py baseline_tests\run_step36_mass_force_stability_diagnostics.py baseline_tests\run_step36_wall_velocity_application_quality.py baseline_tests\run_step36_quality_report_aggregation.py baseline_tests\run_step36_step35_regression_guard.py baseline_tests\run_step36_artifact_manifest.py tests\test_step36_moving_wall_bounceback_application_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_wall_velocity_application_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_wall_velocity_application_report.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_static_regression_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_experimental_application_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_static_vs_experimental_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_mass_force_stability_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_wall_velocity_application_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_step35_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q *> logs\step36_pytest.log
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step36_moving_wall_bounceback_application_contract.py -q
git diff --check
git status --short external/taichi_LBM3D
```

## 15. GitHub Sync Information

Branch: `main`.

Remote target: `origin/main`.

Final commit hash is reported in the Codex completion message after push.

## 16. Acceptance Checklist

- [x] Step 36 detailed goal file exists.
- [x] Default `boundary_motion_mode` remains static.
- [x] Default `wall_velocity_application_mode` remains disabled.
- [x] Default quality checks remain disabled.
- [x] Default reaction transfer remains engineering.
- [x] Application config validation passes.
- [x] Application report passes.
- [x] Static regression smoke passes.
- [x] Experimental application smoke passes.
- [x] Static vs experimental comparison passes.
- [x] Mass force stability diagnostics pass.
- [x] Wall velocity application quality passes.
- [x] Quality report aggregation passes.
- [x] Step 35 regression guard passes.
- [x] No `external/taichi_LBM3D` edits.
- [x] No Step 36 `.vtr` outputs.
- [x] No Step 36 particle `.npy` outputs.
- [x] `logs/step36_pytest.log` exists.
- [x] Full pytest passes.
- [x] Step 36 contract test passes.
- [x] Step 36 artifacts are pushed to `origin/main`.

## 17. Decision For Step 37

Step 36 can be accepted when the recorded verification commands pass and the commit is pushed. Step 37 should remain similarly bounded and must not turn this smoke into a propulsion or real-squid validation claim.
