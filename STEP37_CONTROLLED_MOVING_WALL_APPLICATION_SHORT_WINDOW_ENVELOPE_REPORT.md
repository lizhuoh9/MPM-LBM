# Step 37 Controlled Moving-Wall Application Short-Window Envelope Report

## 1. Goal

Step 37 is controlled moving-wall application short-window envelope. It extends the accepted Step 36 opt-in `solid_vel_experimental` wall-velocity application path from 5-step smoke to a 48^3, 20-step stability envelope.

## 2. Files Created And Updated

- Added `STEP37_CONTROLLED_MOVING_WALL_APPLICATION_SHORT_WINDOW_ENVELOPE_GOAL.md`.
- Added four Step 37 driver configs.
- Added `src/wall_velocity_application_envelope.py`.
- Added Step 37 baseline runners, logs, output artifacts, docs, and contract tests.
- Updated `src/wall_velocity_application.py` with an in-process wall velocity grid cache. This is a reporting/runtime optimization only and does not change the wall velocity formula or moving bounce-back formula.

## 3. Explicit Non-Goals

Step 37 does not change moving bounce-back formulas. Step 37 does not change LBM collision, streaming, projection, coupling, or MPM constitutive formulas. Step 37 does not implement a jet model. Step 37 does not validate jet propulsion. Step 37 does not implement free-body motion. Step 37 does not implement squid swimming. Step 37 does not implement real squid validation. Step 37 does not edit `external/taichi_LBM3D`.

## 4. Application Window Driver

`outputs/step37_application_window_driver/application_window_results.json` passes with 4 rows:

- `static_48_moving_boundary`
- `experimental_48_moving_boundary`
- `static_48_link_area`
- `experimental_48_link_area`

All rows completed 20 LBM steps and 100 MPM substeps. All rows are stable and strict quality-passing. The experimental rows each wrote 20 wall velocity application reports.

Key envelope values:

- `min_rho_min_global = 0.9811668395996094`
- `max_rho_max_global = 1.01199471950531`
- `max_lbm_max_v_global = 0.012898633256554604`
- `min_mpm_min_J_global = 0.990933895111084`
- `max_applied_velocity_norm = 0.007021783310068709`

## 5. Application Envelope Summary

`outputs/step37_application_envelope_summary/application_envelope.json` passes for 2 experimental rows. Each experimental row has 20 reports, applied cell count 2136, and max applied velocity norm 0.007021783310068709 under the 0.01 cap.

## 6. Static Vs Experimental Envelope

`outputs/step37_static_vs_experimental_envelope/static_vs_experimental_envelope.json` passes 2 bounded comparisons. Static and experimental rows are not required to match exactly; they only need to remain stable and bounded.

The largest observed `lbm_max_v_delta` is about 0.002529.

## 7. Engineering Vs Link-Area Envelope

`outputs/step37_engineering_vs_link_area_envelope/engineering_vs_link_area_envelope.json` passes the experimental engineering-vs-link-area comparison.

The link-area final scale is 0.7982993721961975, within `[0.25, 2.0]`.

## 8. Mass Force Bounce-Back Envelope

`outputs/step37_mass_force_bounceback_envelope/mass_force_bounceback_envelope.json` passes all 4 rows.

Key values:

- `max_bb_correction_max = 0.003309197025373578`
- `max_hydro_force_max_norm = 0.4212471842765808`
- `max_applied_velocity_norm = 0.007021783310068709`

## 9. Wall Velocity Timeseries Quality

`outputs/step37_wall_velocity_timeseries_quality/wall_velocity_timeseries_quality.json` passes for 2 experimental rows. Each row has 20 timeseries entries, positive applied-cell counts, finite applied velocity norms, cap pass, repeatable phase sequence, and zero direct LBM population updates.

## 10. Quality Report Aggregation

`outputs/step37_quality_report_aggregation/quality_report_summary.json` aggregates 4 strict procedural squid proxy quality reports. All pass with severity `ok` and zero warnings/reasons.

## 11. Step 36 Regression Guard

`outputs/step37_step36_regression_guard/step36_regression_guard.json` passes 8 of 8 checks. Step 36 report, Step 36 experimental smoke, Step 36 application quality, Step 36 Step 35 guard, and Step 36 artifact budget remain intact.

## 12. Artifact Manifest Summary

`outputs/step37_artifact_manifest/artifact_summary.json` records the Step 37 artifact budget. Step 37 writes no `.vtr` output and no particle `.npy` output.

## 13. Verification Commands

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\wall_velocity_application.py src\wall_velocity_application_envelope.py baseline_tests\step37_common.py baseline_tests\run_step37_application_window_driver.py baseline_tests\run_step37_application_envelope_summary.py baseline_tests\run_step37_static_vs_experimental_envelope.py baseline_tests\run_step37_engineering_vs_link_area_envelope.py baseline_tests\run_step37_mass_force_bounceback_envelope.py baseline_tests\run_step37_wall_velocity_timeseries_quality.py baseline_tests\run_step37_quality_report_aggregation.py baseline_tests\run_step37_step36_regression_guard.py baseline_tests\run_step37_artifact_manifest.py tests\test_step37_wall_velocity_application_envelope_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_application_window_driver.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_application_envelope_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_static_vs_experimental_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_engineering_vs_link_area_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_mass_force_bounceback_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_wall_velocity_timeseries_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_step36_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q *> logs\step37_pytest.log
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step37_wall_velocity_application_envelope_contract.py -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## 14. GitHub Sync Information

Branch: `main`.

Remote target: `origin/main`.

Final commit hash is reported in the Codex completion message after push.

## 15. Acceptance Checklist

- [x] Step 37 detailed goal file exists.
- [x] Application window driver runs 4 rows.
- [x] Static engineering row passes.
- [x] Experimental engineering row passes.
- [x] Static link-area row passes.
- [x] Experimental link-area row passes.
- [x] All rows complete at least 20 LBM steps.
- [x] All rows complete at least 100 MPM substeps.
- [x] Experimental rows write wall velocity application timeseries.
- [x] Experimental applied cell count is positive.
- [x] Max applied velocity norm is within the configured cap.
- [x] `rho_min_global > 0.95`.
- [x] `rho_max_global < 1.05`.
- [x] `lbm_max_v_global < 0.1`.
- [x] `mpm_min_J_global > 0`.
- [x] `projected_mass_min > 0`.
- [x] `projected_mass_max > 0`.
- [x] `active_cell_count > 0`.
- [x] `bb_link_count_max > 0`.
- [x] Hydro force diagnostics are finite.
- [x] Bounce-back correction diagnostics are finite.
- [x] No NaN.
- [x] No Inf.
- [x] Static vs experimental envelope passes.
- [x] Engineering vs link-area envelope passes.
- [x] Mass/force/bounce-back envelope passes.
- [x] Wall velocity timeseries quality passes.
- [x] Quality report aggregation passes.
- [x] Step 36 regression guard passes.
- [x] Default `boundary_motion_mode` remains static.
- [x] Default `wall_velocity_application_mode` remains disabled.
- [x] Default `quality_check_enabled` remains false.
- [x] Default `quality_check_strict` remains false.
- [x] Default `reaction_transfer_mode` remains engineering.
- [x] No default behavior change.
- [x] No moving bounce-back formula changes.
- [x] No LBM collision formula changes.
- [x] No MPM constitutive formula changes.
- [x] No projection formula changes.
- [x] No `external/taichi_LBM3D` edits.
- [x] No jet model claim.
- [x] No squid swimming claim.
- [x] No real squid validation claim.
- [x] No Step 37 `.vtr` outputs.
- [x] No Step 37 particle `.npy` outputs.
- [x] Artifact large file count is 0.
- [x] Step 37 output total-size budget passes.
- [x] Repo artifact summary `total_size_mb < 230`.
- [x] `logs/step37_pytest.log` exists.
- [x] Full pytest passes.
- [x] Step 37 contract test passes.
- [x] `git diff --check` passes.
- [x] Staged whitespace check passes.
- [x] Pre-push hook passes.
- [x] Step 37 artifacts are pushed to `origin/main`.

## 16. Decision For Step 38

Step 37 can be accepted when the recorded verification commands pass and the commit is pushed. Step 38 may start a controlled tethered jet-cycle diagnostics prototype, but it must still avoid real jet validation, free-body motion, squid swimming, and real squid validation claims.
