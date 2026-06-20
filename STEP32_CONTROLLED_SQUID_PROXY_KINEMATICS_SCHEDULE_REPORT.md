# Step 32 Controlled Squid Proxy Prescribed Kinematics Schedule Report

## 1. Goal

Step 32 is controlled squid proxy prescribed kinematics schedule.
Step 32 defines kinematics schedules only.
Step 32 does not integrate kinematics into FSIDriver3D.
Step 32 does not apply moving wall velocity.
Step 32 does not implement mantle contraction in the driver.
Step 32 does not implement funnel actuation in the driver.
Step 32 does not implement squid swimming.
Step 32 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

The Step 32 goal was to define a deterministic prescribed kinematics schedule contract for the accepted Step 30 and Step 31 static squid proxy regions. The accepted contract covers mantle radius scale, mantle cavity volume proxy scale, funnel aperture proxy scale, cycle phase, derivative diagnostics, repeatability, and region mapping compatibility.

## 2. Files Created And Updated

Created:

- `STEP32_CONTROLLED_SQUID_PROXY_KINEMATICS_SCHEDULE_GOAL.md`
- `STEP32_CONTROLLED_SQUID_PROXY_KINEMATICS_SCHEDULE_REPORT.md`
- `docs/32_controlled_squid_proxy_kinematics_schedule.md`
- `src/squid_kinematics_config.py`
- `src/squid_kinematics_schedule.py`
- `src/squid_kinematics_quality.py`
- `src/squid_kinematics_region_mapping.py`
- `configs/step32_squid_proxy_kinematics_schedule.json`
- `configs/step32_squid_proxy_kinematics_sampling.json`
- `baseline_tests/step32_common.py`
- `baseline_tests/run_step32_schedule_config_validation.py`
- `baseline_tests/run_step32_generate_kinematics_schedule.py`
- `baseline_tests/run_step32_schedule_quality.py`
- `baseline_tests/run_step32_schedule_repeatability.py`
- `baseline_tests/run_step32_region_mapping_validation.py`
- `baseline_tests/run_step32_schedule_envelope_summary.py`
- `baseline_tests/run_step32_step31_regression_guard.py`
- `baseline_tests/run_step32_artifact_manifest.py`
- `tests/test_step32_squid_proxy_kinematics_schedule_contract.py`
- `outputs/step32_*`
- `logs/step32_*.log`

Updated:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/11_artifact_policy.md`
- `docs/12_geometry_ingestion.md`
- `docs/30_controlled_squid_proxy_region_geometry.md`
- `docs/31_controlled_squid_proxy_region_static_driver.md`

## 3. Explicit Non-Goals

Step 32 does not add driver execution. It does not move the mantle, move the funnel, add a jet path, add free-body motion, add two-phase flow, add contact-angle physics, change projection, change LBM stepping, change MPM constitutive behavior, change penalty coupling, change moving-boundary coupling, change link-area transfer, edit `external/taichi_LBM3D`, commit raw scans, or commit large real geometry.

No FSIDriver3D, LBM, MPM, moving bounce-back, link-area, or projection formula files were edited.

## 4. Schedule Config Validation

Artifact:

- `outputs/step32_schedule_config_validation/schedule_config_validation.csv`
- `outputs/step32_schedule_config_validation/schedule_config_validation.json`
- `logs/step32_schedule_config_validation.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 19 |
| pass_count | 19 |
| validation_pass | true |

The config points to the accepted Step 30 region and geometry configs, uses `cycle_period_steps = 40`, uses `sample_count = 81`, keeps deterministic mode enabled, and keeps driver integration and actuation disabled.

## 5. Generated Kinematics Schedule

Artifact:

- `outputs/step32_kinematics_schedule/kinematics_schedule.csv`
- `outputs/step32_kinematics_schedule/kinematics_schedule.json`
- `logs/step32_generate_kinematics_schedule.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 81 |
| phase_min | 0.0 |
| phase_max | 1.0 |
| endpoint_repeatability_pass | true |
| driver_integration_enabled_count | 0 |
| actuation_enabled_count | 0 |
| mantle_radius_scale range | [0.85, 1.0] |
| cavity_volume_scale range | [0.6, 1.0] |
| funnel_aperture_scale range | [0.35, 1.0] |

The inclusive phase range provides a closed cycle: the first and final rows both return the rest-state scale values.

## 6. Schedule Quality

Artifact:

- `outputs/step32_schedule_quality/schedule_quality.csv`
- `outputs/step32_schedule_quality/schedule_quality.json`
- `logs/step32_schedule_quality.log`

Accepted checks:

- `row_count_pass = true`
- `finite_pass = true`
- `bounds_pass = true`
- `phase_monotonic_pass = true`
- `endpoint_repeatability_pass = true`
- `derivative_finite_pass = true`
- `contraction_volume_rate_pass = true`
- `refill_volume_rate_pass = true`
- `funnel_aperture_bounds_pass = true`
- `driver_integration_disabled_pass = true`
- `actuation_disabled_pass = true`
- `quality_pass = true`

## 7. Schedule Repeatability

Artifact:

- `outputs/step32_schedule_repeatability/schedule_repeatability.csv`
- `outputs/step32_schedule_repeatability/schedule_repeatability.json`
- `logs/step32_schedule_repeatability.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count_first | 81 |
| row_count_second | 81 |
| schedule_hash_first | `6d74cd32a50a74292e438efa7f9261096315f6af80588b18accd41467e634b2c` |
| schedule_hash_second | `6d74cd32a50a74292e438efa7f9261096315f6af80588b18accd41467e634b2c` |
| mantle hash repeat | true |
| cavity hash repeat | true |
| funnel hash repeat | true |
| repeatability_pass | true |

## 8. Region Mapping Validation

Artifact:

- `outputs/step32_region_mapping_validation/region_mapping_validation.csv`
- `outputs/step32_region_mapping_validation/region_mapping_validation.json`
- `logs/step32_region_mapping_validation.log`

Accepted summary:

| metric | value |
| --- | --- |
| present_required_region_count | 7 |
| mantle_outer_present | true |
| mantle_cavity_proxy_present | true |
| funnel_outlet_proxy_present | true |
| active_for_actuation_region_count | 0 |
| driver_integration_enabled | false |
| actuation_enabled | false |
| mapping_pass | true |

The mapping note is future mapping only. Step 32 keeps every Step 30 region inactive for actuation.

## 9. Schedule Envelope Summary

Artifact:

- `outputs/step32_schedule_envelope_summary/schedule_envelope_summary.csv`
- `outputs/step32_schedule_envelope_summary/schedule_envelope_summary.json`
- `logs/step32_schedule_envelope_summary.log`

Accepted summary:

| metric | value |
| --- | --- |
| contraction_sample_count | 28 |
| refill_sample_count | 53 |
| funnel_open_sample_count | 27 |
| max_abs_mantle_radius_rate | 0.6417638483964936 |
| max_abs_cavity_volume_rate | 1.711370262390659 |
| max_abs_funnel_aperture_rate | 20.845481049562675 |
| envelope_pass | true |

## 10. Step 31 Regression Guard

Artifact:

- `outputs/step32_step31_regression_guard/step31_regression_guard.csv`
- `outputs/step32_step31_regression_guard/step31_regression_guard.json`
- `logs/step32_step31_regression_guard.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 7 |
| pass_count | 7 |
| step31_projection_row_count | 21 |
| step31_static_driver_row_count | 4 |
| step31_static_driver_stable_count | 4 |
| step31_quality_report_count | 4 |
| step31_large_file_count | 0 |
| step31_vtr_count | 0 |
| step31_particle_npy_count | 0 |

## 11. Artifact Manifest Summary

Artifact:

- `outputs/step32_artifact_manifest/artifact_manifest.csv`
- `outputs/step32_artifact_manifest/artifact_summary.csv`
- `outputs/step32_artifact_manifest/artifact_summary.json`
- `logs/step32_artifact_manifest.log`

Accepted summary from the generated manifest:

| metric | value |
| --- | --- |
| large_file_count | 0 |
| step32_total_size_mb | below 3 |
| total_size_mb | below 190 |
| raw_candidate_large_file_count | 0 |
| scan_data_file_count | 0 |
| step32_vtr_count | 0 |
| step32_particle_npy_count | 0 |
| private_absolute_path_count | 0 |

The manifest excludes local `__pycache__` and `.pyc` files.

## 12. Verification Commands

Executed before completion:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\squid_kinematics_config.py src\squid_kinematics_schedule.py src\squid_kinematics_quality.py src\squid_kinematics_region_mapping.py baseline_tests\step32_common.py baseline_tests\run_step32_schedule_config_validation.py baseline_tests\run_step32_generate_kinematics_schedule.py baseline_tests\run_step32_schedule_quality.py baseline_tests\run_step32_schedule_repeatability.py baseline_tests\run_step32_region_mapping_validation.py baseline_tests\run_step32_schedule_envelope_summary.py baseline_tests\run_step32_step31_regression_guard.py baseline_tests\run_step32_artifact_manifest.py tests\test_step32_squid_proxy_kinematics_schedule_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_schedule_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_generate_kinematics_schedule.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_schedule_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_schedule_repeatability.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_region_mapping_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_schedule_envelope_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_step31_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step32_squid_proxy_kinematics_schedule_contract.py -q
pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

`logs/step32_pytest.log` records the full trusted pytest run.

Plain shell `pytest -q` resolved to `D:\TOOL\Anaconda\Scripts\pytest.exe` in this workspace and returned exit code 1 with no stdout or stderr in this run. The trusted workspace interpreter command `& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q` passed with `291 passed`, and the trusted Step 32 contract command passed with `13 passed`.

## 13. GitHub Sync Information

Commit message:

```text
test: add step32 squid proxy kinematics schedule contract
```

Target remote branch: `origin/main`.

The user approved push after modification. The final pushed commit hash is reported in the turn close-out.

## 14. Acceptance Checklist

- [x] schedule config validation passes
- [x] region config path exists
- [x] geometry config path exists
- [x] cycle period is positive
- [x] sample count is sufficient
- [x] phase ranges are valid
- [x] scale ranges are valid
- [x] generated kinematics schedule has expected row count
- [x] phase samples are monotonic
- [x] endpoint repeatability passes
- [x] mantle radius scale is finite and bounded
- [x] cavity volume scale is finite and bounded
- [x] funnel aperture scale is finite and bounded
- [x] mantle radius derivative is finite
- [x] cavity volume derivative is finite
- [x] funnel aperture derivative is finite
- [x] contraction phase volume-rate check passes
- [x] refill phase volume-rate check passes
- [x] schedule repeatability hash passes
- [x] mantle schedule hash repeats
- [x] cavity schedule hash repeats
- [x] funnel schedule hash repeats
- [x] region mapping validation passes
- [x] mantle_outer region is mapped
- [x] mantle_cavity_proxy region is mapped
- [x] funnel_outlet_proxy region is mapped
- [x] driver integration flag is false
- [x] actuation enabled flag is false
- [x] schedule envelope summary passes
- [x] Step 31 regression guard passes
- [x] default quality_check_enabled remains false
- [x] default quality_check_strict remains false
- [x] default reaction_transfer_mode remains engineering
- [x] no FSIDriver3D integration
- [x] no moving wall velocity application
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
- [x] no Step 32 `.vtr` outputs
- [x] no Step 32 particle `.npy` outputs
- [x] artifact `large_file_count == 0`
- [x] Step 32 output total-size budget passes
- [x] repo artifact summary `total_size_mb < 190`
- [x] `logs/step32_pytest.log` exists
- [x] pytest -q passes
- [x] Step 32 contract test passes
- [x] `git diff --check` passes
- [x] staged whitespace check passes
- [x] pre-push hook passes
- [x] Step 32 artifacts are pushed to `origin/main`

## 15. Decision For Step 33

Step 33 should be `Controlled Squid Proxy Kinematics Mapping To Boundary-Motion Diagnostics`. It may map the accepted Step 32 schedule to region displacement and velocity proxies for diagnostics only. It must not integrate moving wall velocity into LBM, must not add a jet path, and must not claim squid swimming. Real driver integration should wait for Step 34 or later.
