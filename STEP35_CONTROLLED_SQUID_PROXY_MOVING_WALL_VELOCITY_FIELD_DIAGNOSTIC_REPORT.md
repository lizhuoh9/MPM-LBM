# Step 35 Controlled Squid Proxy Moving-Wall Velocity Field Diagnostic Report

## 1. Goal

Step 35 is controlled squid proxy moving-wall velocity field diagnostics.
Step 35 generates diagnostic wall velocity fields only.
Step 35 does not apply moving wall velocity to LBM.
Step 35 does not update LBM populations.
Step 35 does not change moving bounce-back formulas.
Step 35 does not implement a jet model.
Step 35 does not implement squid swimming.
Step 35 does not implement new FSI physics.
The default boundary_motion_mode remains static.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.

The Step 35 goal was to generate and validate sparse moving-wall velocity diagnostic rows from the accepted Step 34 interface, without integrating those rows into the fluid, solid, projection, driver, or coupler execution paths.

## 2. Files Created And Updated

Created:

- `STEP35_CONTROLLED_SQUID_PROXY_MOVING_WALL_VELOCITY_FIELD_DIAGNOSTIC_GOAL.md`
- `STEP35_CONTROLLED_SQUID_PROXY_MOVING_WALL_VELOCITY_FIELD_DIAGNOSTIC_REPORT.md`
- `docs/35_controlled_squid_proxy_wall_velocity_field_diagnostics.md`
- `configs/step35_squid_proxy_wall_velocity_field.json`
- `configs/step35_squid_proxy_wall_velocity_sampling.json`
- `src/wall_velocity_config.py`
- `src/wall_velocity_field.py`
- `src/wall_velocity_quality.py`
- `src/wall_velocity_consistency.py`
- `baseline_tests/step35_common.py`
- `baseline_tests/run_step35_wall_velocity_config_validation.py`
- `baseline_tests/run_step35_generate_wall_velocity_field.py`
- `baseline_tests/run_step35_wall_velocity_quality.py`
- `baseline_tests/run_step35_wall_velocity_repeatability.py`
- `baseline_tests/run_step35_motion_velocity_consistency.py`
- `baseline_tests/run_step35_grid_coverage_diagnostics.py`
- `baseline_tests/run_step35_no_lbm_update_guard.py`
- `baseline_tests/run_step35_step34_regression_guard.py`
- `baseline_tests/run_step35_artifact_manifest.py`
- `tests/test_step35_wall_velocity_field_diagnostics_contract.py`
- `outputs/step35_*`
- `logs/step35_*.log`

Updated:

- No solver, driver, coupler, projection, LBM, MPM, or vendored external files were intentionally changed.

## 3. Explicit Non-Goals

Step 35 does not write wall velocity into LBM state, MPM state, dynamic solid state, projector state, moving links, penalty coupling, moving-boundary coupling, link-area transfer, driver execution, or external solver code.

Step 35 is limited to config validation, sparse diagnostic row generation, quality checks, consistency checks, safety guards, reports, and small artifacts.

## 4. Wall Velocity Config Validation

Artifacts:

- `outputs/step35_wall_velocity_config_validation/wall_velocity_config_validation.csv`
- `outputs/step35_wall_velocity_config_validation/wall_velocity_config_validation_summary.csv`
- `outputs/step35_wall_velocity_config_validation/wall_velocity_config_validation.json`
- `logs/step35_wall_velocity_config_validation.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 29 |
| pass_count | 29 |
| validation_pass | true |
| grid_size_count | 3 |
| phase_sample_count | 7 |
| tracked_region_count | 3 |
| execution_flag_enabled_count | 0 |

## 5. Generated Wall Velocity Field

Artifacts:

- `outputs/step35_wall_velocity_field/wall_velocity_field.csv`
- `outputs/step35_wall_velocity_field/wall_velocity_field.json`
- `logs/step35_generate_wall_velocity_field.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 63 |
| expected_row_count | 63 |
| finite_pass | true |
| bounds_pass | true |
| coverage_pass | true |
| min_active_cell_count | 8 |
| max_active_cell_count | 5056 |
| max_velocity_norm | 0.10895977240897987 |
| apply_to_lbm_count | 0 |
| lbm_population_update_enabled_count | 0 |
| moving_bounceback_update_enabled_count | 0 |
| driver_integration_enabled_count | 0 |

## 6. Wall Velocity Quality

Artifacts:

- `outputs/step35_wall_velocity_quality/wall_velocity_quality.csv`
- `outputs/step35_wall_velocity_quality/wall_velocity_quality.json`
- `logs/step35_wall_velocity_quality.log`

Accepted summary:

| metric | value |
| --- | --- |
| quality_pass | true |
| row_count_pass | true |
| finite_pass | true |
| bounds_pass | true |
| coverage_pass | true |
| max_velocity_norm_pass | true |
| diagnostic_only_pass | true |
| no_lbm_update_pass | true |
| no_bounceback_update_pass | true |
| no_driver_integration_pass | true |

## 7. Wall Velocity Repeatability

Artifacts:

- `outputs/step35_wall_velocity_repeatability/wall_velocity_repeatability.csv`
- `outputs/step35_wall_velocity_repeatability/wall_velocity_repeatability.json`
- `logs/step35_wall_velocity_repeatability.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count_first | 63 |
| row_count_second | 63 |
| velocity_field_hash_first | `23463573ceffc274364c9bc2742e8e0780de92eaeb5159c4ce982aa62f8d03f0` |
| velocity_field_hash_second | `23463573ceffc274364c9bc2742e8e0780de92eaeb5159c4ce982aa62f8d03f0` |
| repeatability_pass | true |

The mantle, cavity, and funnel region hashes each repeated exactly.

## 8. Motion-Velocity Consistency

Artifacts:

- `outputs/step35_motion_velocity_consistency/motion_velocity_consistency.csv`
- `outputs/step35_motion_velocity_consistency/motion_velocity_consistency.json`
- `logs/step35_motion_velocity_consistency.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 21 |
| pass_count | 21 |
| phase_match_pass | true |
| region_match_pass | true |
| mantle_velocity_consistency_pass | true |
| cavity_rate_sign_consistency_pass | true |
| funnel_rate_sign_consistency_pass | true |
| consistency_pass | true |

## 9. Grid Coverage Diagnostics

Artifacts:

- `outputs/step35_grid_coverage_diagnostics/grid_coverage_diagnostics.csv`
- `outputs/step35_grid_coverage_diagnostics/grid_coverage_diagnostics.json`
- `logs/step35_grid_coverage_diagnostics.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 9 |
| pass_count | 9 |
| coverage_pass | true |
| active_cell_count_min | 8 |
| active_cell_count_max | 5056 |

## 10. No LBM Update Guard

Artifacts:

- `outputs/step35_no_lbm_update_guard/no_lbm_update_guard.csv`
- `outputs/step35_no_lbm_update_guard/no_lbm_update_guard.json`
- `logs/step35_no_lbm_update_guard.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 8 |
| pass_count | 8 |
| guard_pass | true |
| lbm_population_update_count | 0 |
| moving_bounceback_update_count | 0 |
| driver_integration_enabled_count | 0 |
| apply_to_lbm_count | 0 |

## 11. Step 34 Regression Guard

Artifacts:

- `outputs/step35_step34_regression_guard/step34_regression_guard.csv`
- `outputs/step35_step34_regression_guard/step34_regression_guard.json`
- `logs/step35_step34_regression_guard.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 7 |
| pass_count | 7 |
| regression_pass | true |
| step34_no_op_pass | true |
| step34_noop_state_guard_pass_count | 2 |
| step34_quality_report_count | 6 |
| step34_large_file_count | 0 |
| step34_vtr_count | 0 |
| step34_particle_npy_count | 0 |

## 12. Artifact Manifest Summary

Artifacts:

- `outputs/step35_artifact_manifest/artifact_manifest.csv`
- `outputs/step35_artifact_manifest/artifact_summary.csv`
- `outputs/step35_artifact_manifest/artifact_summary.json`
- `logs/step35_artifact_manifest.log`

Accepted summary:

| metric | value |
| --- | --- |
| file_count | 2181 |
| large_file_count | 0 |
| step35_file_count | 47 |
| step35_total_size_mb | 0.2492694854736328 |
| total_size_mb | 146.50701522827148 |
| raw_candidate_large_file_count | 0 |
| scan_data_file_count | 0 |
| step35_vtr_count | 0 |
| step35_particle_npy_count | 0 |
| private_absolute_path_count | 0 |

## 13. Verification Commands

Executed before completion:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\wall_velocity_config.py src\wall_velocity_field.py src\wall_velocity_quality.py src\wall_velocity_consistency.py baseline_tests\step35_common.py baseline_tests\run_step35_wall_velocity_config_validation.py baseline_tests\run_step35_generate_wall_velocity_field.py baseline_tests\run_step35_wall_velocity_quality.py baseline_tests\run_step35_wall_velocity_repeatability.py baseline_tests\run_step35_motion_velocity_consistency.py baseline_tests\run_step35_grid_coverage_diagnostics.py baseline_tests\run_step35_no_lbm_update_guard.py baseline_tests\run_step35_step34_regression_guard.py baseline_tests\run_step35_artifact_manifest.py tests\test_step35_wall_velocity_field_diagnostics_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_wall_velocity_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_generate_wall_velocity_field.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_wall_velocity_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_wall_velocity_repeatability.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_motion_velocity_consistency.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_grid_coverage_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_no_lbm_update_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_step34_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q *> logs\step35_pytest.log
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step35_wall_velocity_field_diagnostics_contract.py -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

`logs/step35_pytest.log` records the trusted full pytest run.

## 14. GitHub Sync Information

Commit message:

```text
test: add step35 wall velocity field diagnostics
```

Target remote branch: `origin/main`.

The user approved push after modification. The final pushed commit hash is reported in the turn close-out.

## 15. Acceptance Checklist

- [x] Wall velocity config validation passes.
- [x] Grid sizes are exactly `32`, `48`, and `64`.
- [x] Phase samples are valid and exactly `0.0`, `0.1`, `0.2`, `0.35`, `0.5`, `0.75`, and `1.0`.
- [x] Tracked regions include `mantle_outer`.
- [x] Tracked regions include `mantle_cavity_proxy`.
- [x] Tracked regions include `funnel_outlet_proxy`.
- [x] `write_dense_field` is false.
- [x] `write_sparse_samples` is false.
- [x] `apply_to_lbm` is false.
- [x] `lbm_population_update_enabled` is false.
- [x] `moving_bounceback_update_enabled` is false.
- [x] `driver_integration_enabled` is false.
- [x] `jet_model_enabled` is false.
- [x] `actuation_enabled` is false.
- [x] Generated wall velocity field has 63 rows.
- [x] Velocity fields are finite.
- [x] Velocity fields are bounded.
- [x] Active cell coverage is positive.
- [x] `diagnostic_only` is true for all rows.
- [x] Wall velocity quality passes.
- [x] Wall velocity repeatability hash passes.
- [x] Mantle velocity hash repeats.
- [x] Cavity velocity hash repeats.
- [x] Funnel velocity hash repeats.
- [x] Motion-velocity consistency passes.
- [x] Grid coverage diagnostics pass.
- [x] No-LBM-update guard passes.
- [x] LBM population update count is 0.
- [x] Moving bounce-back update count is 0.
- [x] Step 34 regression guard passes.
- [x] Default `boundary_motion_mode` remains static.
- [x] Default `quality_check_enabled` remains false.
- [x] Default `quality_check_strict` remains false.
- [x] Default `reaction_transfer_mode` remains engineering.
- [x] No moving wall velocity application.
- [x] No LBM population update.
- [x] No moving bounce-back formula changes.
- [x] No jet model.
- [x] No mantle contraction driver behavior.
- [x] No funnel actuation driver behavior.
- [x] No squid swimming claim.
- [x] No real squid validation claim.
- [x] No new FSI physics.
- [x] No LBM formula changes.
- [x] No MPM constitutive formula changes.
- [x] No projection formula changes.
- [x] No `external/taichi_LBM3D` edits.
- [x] No Step 35 `.vtr` outputs.
- [x] No Step 35 particle `.npy` outputs.
- [x] Artifact `large_file_count == 0`.
- [x] Step 35 output total-size budget passes.
- [x] Repo artifact summary `total_size_mb < 210`.
- [x] `logs/step35_pytest.log` exists.
- [x] Full pytest passes.
- [x] Step 35 contract test passes.
- [x] `git diff --check` passes.
- [x] Staged whitespace check passes.
- [x] Pre-push hook passes.
- [x] Step 35 artifacts are pushed to `origin/main`.

## 16. Decision For Step 36

Step 36 may be `Controlled Moving-Wall Bounce-Back Velocity Application Smoke`, but only as a separate guarded experimental contract. It should be opt-in, short-step, 32 or 48 grid, and should carry static no-op regression, mass/force diagnostics, and strict artifact guards before any broader claims are made.
