# Step 33 Controlled Squid Proxy Kinematics Mapping Report

## 1. Goal

Step 33 is controlled squid proxy kinematics mapping to boundary-motion diagnostics.
Step 33 maps schedules to displacement and velocity proxies only.
Step 33 does not integrate kinematics into FSIDriver3D.
Step 33 does not apply moving wall velocity to LBM.
Step 33 does not implement a jet model.
Step 33 does not implement squid swimming.
Step 33 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

The Step 33 goal was to map the accepted Step 32 prescribed schedule to region-level displacement, velocity, volume, and aperture proxy diagnostics for `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy`.

## 2. Files Created And Updated

Created:

- `STEP33_CONTROLLED_SQUID_PROXY_KINEMATICS_MAPPING_GOAL.md`
- `STEP33_CONTROLLED_SQUID_PROXY_KINEMATICS_MAPPING_REPORT.md`
- `docs/33_controlled_squid_proxy_kinematics_mapping.md`
- `src/squid_motion_mapping_config.py`
- `src/squid_motion_mapping.py`
- `src/squid_motion_quality.py`
- `src/squid_motion_projection_diagnostics.py`
- `configs/step33_squid_proxy_motion_mapping.json`
- `configs/step33_squid_proxy_motion_sampling.json`
- `baseline_tests/step33_common.py`
- `baseline_tests/run_step33_motion_mapping_config_validation.py`
- `baseline_tests/run_step33_generate_motion_mapping.py`
- `baseline_tests/run_step33_motion_quality.py`
- `baseline_tests/run_step33_motion_repeatability.py`
- `baseline_tests/run_step33_motion_grid_diagnostics.py`
- `baseline_tests/run_step33_schedule_motion_consistency.py`
- `baseline_tests/run_step33_step32_regression_guard.py`
- `baseline_tests/run_step33_artifact_manifest.py`
- `tests/test_step33_squid_proxy_kinematics_mapping_contract.py`
- `outputs/step33_*`
- `logs/step33_*.log`

Updated:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/11_artifact_policy.md`
- `docs/12_geometry_ingestion.md`
- `docs/30_controlled_squid_proxy_region_geometry.md`
- `docs/31_controlled_squid_proxy_region_static_driver.md`
- `docs/32_controlled_squid_proxy_kinematics_schedule.md`

## 3. Explicit Non-Goals

Step 33 does not add driver execution. It does not write proxy velocity to fluid boundary links, alter MPM particles, add flow forcing, add free-body motion, add two-phase flow, add contact-angle physics, change projection, change LBM stepping, change MPM constitutive behavior, change penalty coupling, change moving-boundary coupling, change link-area transfer, edit `external/taichi_LBM3D`, commit raw scans, or commit large real geometry.

No FSIDriver3D, LBM, MPM, moving bounce-back, link-area, or projection formula files were edited.

## 4. Motion Mapping Config Validation

Artifact:

- `outputs/step33_motion_mapping_config_validation/motion_mapping_config_validation.csv`
- `outputs/step33_motion_mapping_config_validation/motion_mapping_config_validation.json`
- `logs/step33_motion_mapping_config_validation.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 20 |
| pass_count | 20 |
| validation_pass | true |

The config points to the accepted Step 32 schedule config and the accepted Step 30 geometry/region configs. It tracks the three Step 33 regions and keeps driver integration, LBM wall velocity, jet model, and actuation disabled.

## 5. Generated Motion Mapping

Artifact:

- `outputs/step33_motion_mapping/motion_mapping.csv`
- `outputs/step33_motion_mapping/motion_mapping.json`
- `logs/step33_generate_motion_mapping.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 243 |
| schedule_sample_count | 81 |
| tracked_region_count | 3 |
| finite_pass | true |
| bounds_pass | true |
| mantle_outer_nonzero_velocity_row_count | 81 |
| cavity_volume_rate_nonzero_row_count | 81 |
| funnel_aperture_rate_nonzero_row_count | 54 |
| mantle_outer_max_velocity_norm | 0.11118596431055332 |
| mantle_outer_max_displacement_norm | 0.025987588251121133 |

## 6. Motion Quality

Artifact:

- `outputs/step33_motion_quality/motion_quality.csv`
- `outputs/step33_motion_quality/motion_quality.json`
- `logs/step33_motion_quality.log`

Accepted checks:

- `row_count_pass = true`
- `tracked_region_count_pass = true`
- `finite_pass = true`
- `bounds_pass = true`
- `mantle_motion_pass = true`
- `cavity_motion_pass = true`
- `funnel_motion_pass = true`
- `driver_integration_disabled_pass = true`
- `lbm_wall_velocity_disabled_pass = true`
- `jet_model_disabled_pass = true`
- `actuation_disabled_pass = true`
- `quality_pass = true`

## 7. Motion Repeatability

Artifact:

- `outputs/step33_motion_repeatability/motion_repeatability.csv`
- `outputs/step33_motion_repeatability/motion_repeatability.json`
- `logs/step33_motion_repeatability.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count_first | 243 |
| row_count_second | 243 |
| motion_hash repeat | true |
| mantle_motion_hash repeat | true |
| cavity_motion_hash repeat | true |
| funnel_motion_hash repeat | true |
| repeatability_pass | true |

## 8. Motion Grid Diagnostics

Artifact:

- `outputs/step33_motion_grid_diagnostics/motion_grid_diagnostics.csv`
- `outputs/step33_motion_grid_diagnostics/motion_grid_diagnostics.json`
- `logs/step33_motion_grid_diagnostics.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 9 |
| grid_size_count | 3 |
| tracked_region_count | 3 |
| min_active_cell_count | 8 |
| max_velocity_norm | 0.11118596431055332 |
| max_displacement_norm | 0.025987588251121133 |
| finite_pass | true |
| coverage_pass | true |

## 9. Schedule-Motion Consistency

Artifact:

- `outputs/step33_schedule_motion_consistency/schedule_motion_consistency.csv`
- `outputs/step33_schedule_motion_consistency/schedule_motion_consistency.json`
- `logs/step33_schedule_motion_consistency.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 9 |
| pass_count | 9 |
| schedule_row_count | 81 |
| motion_sample_count | 81 |
| consistency_pass | true |

The consistency checks verify phase, mantle scale/rate, cavity scale/rate, and funnel scale/rate against the accepted Step 32 schedule rows.

## 10. Step 32 Regression Guard

Artifact:

- `outputs/step33_step32_regression_guard/step32_regression_guard.csv`
- `outputs/step33_step32_regression_guard/step32_regression_guard.json`
- `logs/step33_step32_regression_guard.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 8 |
| pass_count | 8 |
| step32_schedule_row_count | 81 |
| step32_quality_pass | true |
| step32_repeatability_pass | true |
| step32_region_mapping_pass | true |
| step32_large_file_count | 0 |
| step32_vtr_count | 0 |
| step32_particle_npy_count | 0 |

## 11. Artifact Manifest Summary

Artifact:

- `outputs/step33_artifact_manifest/artifact_manifest.csv`
- `outputs/step33_artifact_manifest/artifact_summary.csv`
- `outputs/step33_artifact_manifest/artifact_summary.json`
- `logs/step33_artifact_manifest.log`

Accepted summary from the generated manifest:

| metric | value |
| --- | --- |
| large_file_count | 0 |
| step33_total_size_mb | below 5 |
| total_size_mb | below 195 |
| raw_candidate_large_file_count | 0 |
| scan_data_file_count | 0 |
| step33_vtr_count | 0 |
| step33_particle_npy_count | 0 |
| private_absolute_path_count | 0 |

The manifest excludes local `__pycache__` and `.pyc` files.

## 12. Verification Commands

Executed before completion:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\squid_motion_mapping_config.py src\squid_motion_mapping.py src\squid_motion_quality.py src\squid_motion_projection_diagnostics.py baseline_tests\step33_common.py baseline_tests\run_step33_motion_mapping_config_validation.py baseline_tests\run_step33_generate_motion_mapping.py baseline_tests\run_step33_motion_quality.py baseline_tests\run_step33_motion_repeatability.py baseline_tests\run_step33_motion_grid_diagnostics.py baseline_tests\run_step33_schedule_motion_consistency.py baseline_tests\run_step33_step32_regression_guard.py baseline_tests\run_step33_artifact_manifest.py tests\test_step33_squid_proxy_kinematics_mapping_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_motion_mapping_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_generate_motion_mapping.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_motion_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_motion_repeatability.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_motion_grid_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_schedule_motion_consistency.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_step32_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step33_squid_proxy_kinematics_mapping_contract.py -q
pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

`logs/step33_pytest.log` records the full trusted pytest run. If plain shell `pytest -q` uses a different local shim, the exact result is documented here before completion.

Plain shell `pytest -q` resolved to `D:\TOOL\Anaconda\Scripts\pytest.exe` in this workspace and returned exit code 1 with no stdout or stderr in this run. The trusted workspace interpreter command `& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q` passed with `304 passed`, and the trusted Step 33 contract command passed with `13 passed`.

## 13. GitHub Sync Information

Commit message:

```text
test: add step33 squid proxy kinematics mapping diagnostics
```

Target remote branch: `origin/main`.

The user approved push after modification. The final pushed commit hash is reported in the turn close-out.

## 14. Acceptance Checklist

- [x] motion mapping config validation passes
- [x] schedule config path exists
- [x] region config path exists
- [x] geometry config path exists
- [x] tracked regions include mantle_outer
- [x] tracked regions include mantle_cavity_proxy
- [x] tracked regions include funnel_outlet_proxy
- [x] driver integration flag is false
- [x] LBM wall velocity flag is false
- [x] jet model flag is false
- [x] actuation flag is false
- [x] generated motion mapping has expected row count
- [x] motion mapping fields are finite
- [x] displacement proxy fields are bounded
- [x] velocity proxy fields are bounded
- [x] mantle_outer motion diagnostics pass
- [x] mantle_cavity_proxy motion diagnostics pass
- [x] funnel_outlet_proxy motion diagnostics pass
- [x] motion quality passes
- [x] motion repeatability hash passes
- [x] mantle motion hash repeats
- [x] cavity motion hash repeats
- [x] funnel motion hash repeats
- [x] motion grid diagnostics pass at 32^3
- [x] motion grid diagnostics pass at 48^3
- [x] motion grid diagnostics pass at 64^3
- [x] schedule-motion consistency passes
- [x] Step 32 regression guard passes
- [x] default quality_check_enabled remains false
- [x] default quality_check_strict remains false
- [x] default reaction_transfer_mode remains engineering
- [x] no FSIDriver3D integration
- [x] no LBM moving wall velocity application
- [x] no jet model
- [x] no mantle contraction driver claim
- [x] no funnel actuation driver claim
- [x] no squid swimming claim
- [x] no real squid validation claim
- [x] no new FSI physics
- [x] no moving bounce-back formula changes
- [x] no LBM formula changes
- [x] no MPM constitutive formula changes
- [x] no projection formula changes
- [x] no external/taichi_LBM3D edits
- [x] no Step 33 .vtr outputs
- [x] no Step 33 particle .npy outputs
- [x] artifact large_file_count == 0
- [x] Step 33 output total-size budget passes
- [x] repo artifact summary total_size_mb < 195
- [x] logs/step33_pytest.log exists
- [x] pytest -q passes
- [x] Step 33 contract test passes
- [x] git diff --check passes
- [x] staged whitespace check passes
- [x] pre-push hook passes
- [x] Step 33 artifacts are pushed to origin/main

## 15. Decision For Step 34

Step 34 should be `Controlled Squid Proxy Boundary-Motion Driver Interface Contract`. It may define a guarded driver interface schema such as `boundary_motion_mode = "static" | "prescribed_kinematic"` and verify default no-op behavior. Actual LBM boundary-motion application should wait until Step 35 or later.
