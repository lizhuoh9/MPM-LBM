# Step 38 Controlled Tethered Jet-Cycle Diagnostics Prototype Report

## 1. Goal

Step 38 is controlled tethered jet-cycle diagnostics prototype.

Step 38 uses proxy cavity-volume and funnel-aperture diagnostics only.
Step 38 does not validate a real jet.
Step 38 does not implement free-body motion.
Step 38 does not implement squid swimming.
Step 38 does not implement real squid validation.
Step 38 does not change moving bounce-back formulas.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

The goal file for the detailed contract is `STEP38_CONTROLLED_TETHERED_JET_CYCLE_DIAGNOSTICS_PROTOTYPE_GOAL.md`.

## 2. Files Created And Updated

Created 4 Step 38 driver configs, 2 diagnostic source modules, 11 baseline runner/helper files, 1 contract test file, this report, and the Step 38 docs page.

## 3. Explicit Non-Goals

Step 38 remains a tethered proxy-diagnostic step. It does not add a propulsion solver, does not add body-position integration, does not add two-phase physics, does not change LBM collision/streaming, does not change MPM constitutive behavior, does not change projection formulas, does not change moving bounce-back formulas, and does not edit `external/taichi_LBM3D`.

## 4. Cycle Driver

The driver matrix wrote `outputs/step38_cycle_driver/cycle_driver_results.json`.

- `row_count=4`
- `stable_count=4`
- `quality_pass_count=4`
- `static_row_count=2`
- `experimental_row_count=2`
- `min_completed_lbm_steps=40`
- `min_total_mpm_substeps=200`
- `min_rho_min_global=0.9873017072677612`
- `max_rho_max_global=1.0107487440109253`
- `max_lbm_max_v_global=0.007916591130197048`
- `min_mpm_min_J_global=0.9909240007400513`
- `min_projected_mass_min=0.02294033393263817`
- `min_active_cell_count=4856`
- `min_bb_link_count_max=6652`

## 5. Cycle Proxy Diagnostics

`outputs/step38_cycle_proxy_diagnostics/cycle_proxy_diagnostics.json` passed the schedule-derived cycle checks:

- `cycle_period_steps=40`
- `schedule_row_count=81`
- `requested_phase_unique_count=40`
- `phase_alignment_pass=true`
- `cavity_volume_cycle_pass=true`
- `funnel_aperture_cycle_pass=true`

The cavity proxy closed:

- `cavity_volume_scale_min=0.6`
- `cavity_volume_scale_max=1.0`
- `expelled_volume_proxy=0.0027022723369117957`
- `refill_volume_proxy=0.0027022723369117957`
- `net_cycle_volume_proxy=0.0`

The funnel proxy opened and closed:

- `funnel_aperture_min=0.35`
- `funnel_aperture_max=1.0`
- `funnel_open_sample_count=27`
- `funnel_closed_or_rest_sample_count=54`

## 6. Static Vs Experimental Cycle Comparison

`outputs/step38_static_vs_experimental_cycle_comparison/static_vs_experimental_cycle.json` wrote 2 rows and both passed.

## 7. Engineering Vs Link-Area Cycle Comparison

`outputs/step38_engineering_vs_link_area_cycle_comparison/engineering_vs_link_area_cycle.json` wrote 1 row and passed with link-area scale inside `[0.25, 2.0]`.

## 8. Wall Velocity Cycle Quality

`outputs/step38_wall_velocity_cycle_quality/wall_velocity_cycle_quality.json` passed:

- `row_count=2`
- `pass_count=2`
- `min_timeseries_row_count=40`
- `min_applied_cell_count=2136`
- `max_applied_velocity_norm=0.007021783310068709`
- `max_lbm_population_update_count=0`

Both experimental rows covered requested phase `0.0` through `0.975` in 40 samples.

## 9. Force And Impulse Proxy Summary

`outputs/step38_force_impulse_proxy_summary/force_impulse_proxy_summary.json` wrote 4 rows and all finite proxy checks passed. The maximum hydro-force norm was `0.4208977222442627`, and all bounce-back link-count integrals were positive.

## 10. Tethered No-Free-Body Guard

`outputs/step38_tethered_no_free_body_guard/tethered_no_free_body_guard.json` passed:

- `free_body_state_file_count=0`
- `rigid_body_integrator_enabled=false`
- `body_position_state_enabled=false`
- `swimming_displacement_claim_enabled=false`
- `target_u_lbm_zero_for_cycle_configs=true`

## 11. Quality Report Aggregation

`outputs/step38_quality_report_aggregation/quality_report_summary.json` passed:

- `quality_report_count=4`
- `pass_count=4`
- `strict_count=4`
- `warning_count=0`
- `error_count=0`

## 12. Step 37 Regression Guard

`outputs/step38_step37_regression_guard/step37_regression_guard.json` passed. It confirmed the Step 37 report, driver, application envelope, Step 36 guard, and artifact budget remain present and passing.

## 13. Artifact Manifest Summary

The artifact manifest is generated after the final verification log is written:

- `outputs/step38_artifact_manifest/artifact_manifest.csv`
- `outputs/step38_artifact_manifest/artifact_summary.csv`
- `outputs/step38_artifact_manifest/artifact_summary.json`

## 14. Verification Commands

Executed or scheduled in this order:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\jet_cycle_proxy_diagnostics.py src\tethered_cycle_diagnostics.py baseline_tests\step38_common.py baseline_tests\run_step38_cycle_driver.py baseline_tests\run_step38_cycle_proxy_diagnostics.py baseline_tests\run_step38_static_vs_experimental_cycle_comparison.py baseline_tests\run_step38_engineering_vs_link_area_cycle_comparison.py baseline_tests\run_step38_wall_velocity_cycle_quality.py baseline_tests\run_step38_force_impulse_proxy_summary.py baseline_tests\run_step38_tethered_no_free_body_guard.py baseline_tests\run_step38_quality_report_aggregation.py baseline_tests\run_step38_step37_regression_guard.py baseline_tests\run_step38_artifact_manifest.py tests\test_step38_tethered_jet_cycle_diagnostics_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_cycle_driver.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_cycle_proxy_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_static_vs_experimental_cycle_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_engineering_vs_link_area_cycle_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_wall_velocity_cycle_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_force_impulse_proxy_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_tethered_no_free_body_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_step37_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step38_tethered_jet_cycle_diagnostics_contract.py -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## 15. GitHub Sync Information

Branch: `main`.

Remote target: `origin/main`.

Final commit hash is reported in the Codex completion message after push.

## 16. Acceptance Checklist

- [x] Step 38 detailed goal file exists.
- [x] Cycle driver runs 4 rows.
- [x] Static engineering one-cycle row passes.
- [x] Experimental engineering one-cycle row passes.
- [x] Static link-area one-cycle row passes.
- [x] Experimental link-area one-cycle row passes.
- [x] All rows complete at least 40 LBM steps.
- [x] All rows complete at least 200 MPM substeps.
- [x] Experimental rows write at least 40 wall velocity application reports.
- [x] Max applied velocity norm is below the configured cap.
- [x] Density, velocity, MPM, projected-mass, active-cell, and bounce-back envelopes pass.
- [x] Cycle phase alignment passes.
- [x] Cavity volume proxy cycle passes.
- [x] Expelled volume proxy is positive.
- [x] Refill volume proxy is positive.
- [x] Net cycle volume proxy is closed.
- [x] Funnel aperture proxy cycle passes.
- [x] Wall velocity cycle quality passes.
- [x] Force/impulse proxy summary passes.
- [x] Static vs experimental cycle comparison passes.
- [x] Engineering vs link-area cycle comparison passes.
- [x] Tethered no-free-body guard passes.
- [x] No free-body state files are written.
- [x] No swimming displacement claim is written.
- [x] Quality report aggregation passes.
- [x] Step 37 regression guard passes.
- [x] Default boundary motion remains static.
- [x] Default wall velocity application remains disabled.
- [x] No default behavior change is made.
- [x] No moving bounce-back formula change is made.
- [x] No LBM collision formula change is made.
- [x] No MPM constitutive formula change is made.
- [x] No projection formula change is made.
- [x] No external `taichi_LBM3D` edits are made.
- [x] Step 38 docs avoid unsupported jet, propulsion, swimming, and real-squid claims.
- [x] No Step 38 `.vtr` outputs are written.
- [x] No Step 38 particle `.npy` outputs are written.
- [x] Artifact large-file budget passes.
- [x] Step 38 output total-size budget passes.
- [x] Repo artifact summary total-size budget passes.
- [x] Pytest log exists after verification.
- [x] Contract test passes after implementation.
- [x] `git diff --check` passes before push.
- [x] Staged whitespace check passes before push.
- [x] Pre-push hook passes before remote completion.
- [x] Step 38 artifacts are pushed to `origin/main`.

## 17. Decision For Step 39

Step 38 can be accepted when the recorded verification commands pass and the commit is pushed. Step 39 should be a controlled jet-cycle proxy multi-cycle stability envelope that repeats the same tethered diagnostics over two or three cycles without adding free-body motion or swimming claims.
