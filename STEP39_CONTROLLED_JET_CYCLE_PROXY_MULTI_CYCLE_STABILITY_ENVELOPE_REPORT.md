# Step 39 Controlled Jet-Cycle Proxy Multi-Cycle Stability Envelope Report

## 1. Goal

Step 39 is controlled jet-cycle proxy multi-cycle stability envelope.

Step 39 repeats tethered proxy diagnostics over two cycles.
Step 39 does not validate a real jet.
Step 39 does not implement free-body motion.
Step 39 does not implement squid swimming.
Step 39 does not implement real squid validation.
Step 39 does not change moving bounce-back formulas.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

The goal file for the detailed contract is `STEP39_CONTROLLED_JET_CYCLE_PROXY_MULTI_CYCLE_STABILITY_ENVELOPE_GOAL.md`.

## 2. Files Created And Updated

Created 4 Step 39 driver configs, 1 multicycle diagnostics source module, extensions to the tethered guard, 12 baseline runner/helper files, 1 contract test file, this report, and the Step 39 docs page.

## 3. Explicit Non-Goals

Step 39 remains a tethered proxy-diagnostic step. It does not add body trajectory integration, does not add a propulsion solver, does not add body-position integration, does not add two-phase physics, does not change LBM collision/streaming, does not change MPM constitutive behavior, does not change projection formulas, does not change moving bounce-back formulas, and does not edit `external/taichi_LBM3D`.

## 4. Multi-Cycle Driver

The driver matrix wrote `outputs/step39_multicycle_driver/multicycle_driver_results.json`.

- `row_count=4`
- `stable_count=4`
- `quality_pass_count=4`
- `static_row_count=2`
- `experimental_row_count=2`
- `min_completed_lbm_steps=80`
- `min_total_mpm_substeps=400`
- `min_rho_min_global=0.9870661497116089`
- `max_rho_max_global=1.0107489824295044`
- `max_lbm_max_v_global=0.008082426153123379`
- `min_mpm_min_J_global=0.9909238219261169`
- `min_projected_mass_min=0.022940337657928467`
- `min_active_cell_count=4884`
- `min_bb_link_count_max=6692`

## 5. Multi-Cycle Proxy Diagnostics

`outputs/step39_multicycle_proxy_diagnostics/multicycle_proxy_diagnostics.json` passed:

- `cycle_count=2`
- `cycle_period_steps=40`
- `row_count=8`
- `pass_count=8`
- `multicycle_proxy_pass=true`

The output includes two schedule-derived cavity proxy rows, two schedule-derived funnel proxy rows, and four experimental wall-velocity proxy rows.

## 6. Cycle-To-Cycle Drift Summary

`outputs/step39_cycle_to_cycle_drift_summary/cycle_to_cycle_drift.json` passed:

- `row_count=4`
- `pass_count=4`
- `drift_summary_pass=true`

Largest observed absolute drifts:

- `projected_mass_drift <= 5.587935447692871e-09`
- `lbm_max_v_drift <= 0.0018947357311844826`
- `rho_min_drift_cycle2_minus_cycle1 <= 0.0009014010429382324`
- `rho_max_drift_cycle2_minus_cycle1 <= 0.0030274391174316406`

## 7. Wall Velocity Multi-Cycle Quality

`outputs/step39_wall_velocity_multicycle_quality/wall_velocity_multicycle_quality.json` passed:

- `row_count=2`
- `pass_count=2`
- `cycle_count=2`
- `min_timeseries_row_count=80`
- `min_applied_cell_count=2136`
- `max_applied_velocity_norm=0.007021783310068709`
- `max_lbm_population_update_count=0`

## 8. Static Vs Experimental Multi-Cycle Comparison

`outputs/step39_static_vs_experimental_multicycle_comparison/static_vs_experimental_multicycle.json` wrote 2 rows and both passed.

## 9. Engineering Vs Link-Area Multi-Cycle Comparison

`outputs/step39_engineering_vs_link_area_multicycle_comparison/engineering_vs_link_area_multicycle.json` wrote 1 row and passed with link-area scale inside `[0.25, 2.0]`.

## 10. Force And Impulse Multi-Cycle Summary

`outputs/step39_force_impulse_multicycle_summary/force_impulse_multicycle_summary.json` wrote 8 rows and all finite proxy checks passed.

- `row_count=8`
- `pass_count=8`
- `max_cycle_to_cycle_impulse_proxy_drift=0.014891386032104492`

These are force and impulse proxies from existing diagnostics only.

## 11. Tethered No-Free-Body Guard

`outputs/step39_tethered_no_free_body_guard/tethered_no_free_body_guard.json` passed:

- `free_body_state_file_count=0`
- `body_trajectory_output_count=0`
- `rigid_body_integrator_enabled=false`
- `body_position_state_enabled=false`
- `swimming_displacement_claim_enabled=false`
- `target_u_lbm_zero_for_cycle_configs=true`

## 12. Quality Report Aggregation

`outputs/step39_quality_report_aggregation/quality_report_summary.json` passed:

- `quality_report_count=4`
- `pass_count=4`
- `strict_count=4`
- `warning_count=0`
- `error_count=0`

## 13. Step 38 Regression Guard

`outputs/step39_step38_regression_guard/step38_regression_guard.json` passed. It confirmed the Step 38 report, cycle driver, proxy diagnostics, wall velocity cycle quality, tethered guard, and artifact budget remain present and passing.

## 14. Artifact Manifest Summary

The artifact manifest is generated after the final verification log is written:

- `outputs/step39_artifact_manifest/artifact_manifest.csv`
- `outputs/step39_artifact_manifest/artifact_summary.csv`
- `outputs/step39_artifact_manifest/artifact_summary.json`

## 15. Verification Commands

Executed or scheduled in this order:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\multicycle_proxy_diagnostics.py src\jet_cycle_proxy_diagnostics.py src\tethered_cycle_diagnostics.py baseline_tests\step39_common.py baseline_tests\run_step39_multicycle_driver.py baseline_tests\run_step39_multicycle_proxy_diagnostics.py baseline_tests\run_step39_cycle_to_cycle_drift_summary.py baseline_tests\run_step39_wall_velocity_multicycle_quality.py baseline_tests\run_step39_static_vs_experimental_multicycle_comparison.py baseline_tests\run_step39_engineering_vs_link_area_multicycle_comparison.py baseline_tests\run_step39_force_impulse_multicycle_summary.py baseline_tests\run_step39_tethered_no_free_body_guard.py baseline_tests\run_step39_quality_report_aggregation.py baseline_tests\run_step39_step38_regression_guard.py baseline_tests\run_step39_artifact_manifest.py tests\test_step39_multicycle_jet_proxy_stability_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_multicycle_driver.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_multicycle_proxy_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_cycle_to_cycle_drift_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_wall_velocity_multicycle_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_static_vs_experimental_multicycle_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_engineering_vs_link_area_multicycle_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_force_impulse_multicycle_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_tethered_no_free_body_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_step38_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step39_multicycle_jet_proxy_stability_contract.py -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## 16. GitHub Sync Information

Branch: `main`.

Remote target: `origin/main`.

Final commit hash is reported in the Codex completion message after push.

## 17. Acceptance Checklist

- [x] Step 39 detailed goal file exists.
- [x] Multi-cycle driver runs 4 rows.
- [x] Static engineering 2-cycle row passes.
- [x] Experimental engineering 2-cycle row passes.
- [x] Static link-area 2-cycle row passes.
- [x] Experimental link-area 2-cycle row passes.
- [x] All rows complete at least 80 LBM steps.
- [x] All rows complete at least 400 MPM substeps.
- [x] Experimental rows write at least 80 wall velocity application reports.
- [x] Max applied velocity norm is below the configured cap.
- [x] Density, velocity, MPM, projected-mass, active-cell, and bounce-back envelopes pass.
- [x] No NaN or Inf was detected.
- [x] Cycle 1 phase alignment passes.
- [x] Cycle 2 phase alignment passes.
- [x] Cavity volume proxy closes in both cycles.
- [x] Funnel aperture proxy completes both cycles.
- [x] Expelled volume proxy is positive in both cycles.
- [x] Refill volume proxy is positive in both cycles.
- [x] Cycle-to-cycle drift summary passes.
- [x] Wall velocity multicycle quality passes.
- [x] Static vs experimental multicycle comparison passes.
- [x] Engineering vs link-area multicycle comparison passes.
- [x] Force/impulse proxy multicycle summary passes.
- [x] Tethered no-free-body guard passes.
- [x] No free-body state files are written.
- [x] No body trajectory output is written.
- [x] No swimming displacement claim is written.
- [x] Quality report aggregation passes.
- [x] Step 38 regression guard passes.
- [x] Default boundary motion remains static.
- [x] Default wall velocity application remains disabled.
- [x] No default behavior change is made.
- [x] No moving bounce-back formula change is made.
- [x] No LBM collision formula change is made.
- [x] No MPM constitutive formula change is made.
- [x] No projection formula change is made.
- [x] No external `taichi_LBM3D` edits are made.
- [x] Step 39 docs avoid unsupported jet, propulsion, swimming, and real-squid claims.
- [x] No Step 39 `.vtr` outputs are written.
- [x] No Step 39 particle `.npy` outputs are written.
- [x] Artifact large-file budget passes.
- [x] Step 39 output total-size budget passes.
- [x] Repo artifact summary total-size budget passes.
- [x] Pytest log exists after verification.
- [x] Contract test passes after implementation.
- [x] `git diff --check` passes before push.
- [x] Staged whitespace check passes before push.
- [x] Pre-push hook passes before remote completion.
- [x] Step 39 artifacts are pushed to `origin/main`.

## 18. Decision For Step 40

Step 39 can be accepted when the recorded verification commands pass and the commit is pushed. Step 40 should be a controlled jet-cycle proxy parameter sensitivity smoke that keeps the same tethered proxy-only scope and does not add body trajectory integration or swimming claims.
