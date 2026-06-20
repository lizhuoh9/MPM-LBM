# Step 34 Controlled Squid Proxy Boundary-Motion Driver Interface Report

## 1. Goal

Step 34 is controlled squid proxy boundary-motion driver interface.
Step 34 defines a guarded driver interface only.
Step 34 keeps prescribed kinematics diagnostic-only.
Step 34 does not apply moving wall velocity to LBM.
Step 34 does not implement a jet model.
Step 34 does not implement squid swimming.
Step 34 does not implement new FSI physics.
The default boundary_motion_mode remains static.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

The Step 34 goal was to define and validate a driver-side boundary-motion interface schema that remains report-only and no-op.

## 2. Files Created And Updated

Created:

- `STEP34_CONTROLLED_SQUID_PROXY_BOUNDARY_MOTION_DRIVER_INTERFACE_GOAL.md`
- `STEP34_CONTROLLED_SQUID_PROXY_BOUNDARY_MOTION_DRIVER_INTERFACE_REPORT.md`
- `docs/34_controlled_squid_proxy_boundary_motion_driver_interface.md`
- `src/boundary_motion_config.py`
- `src/boundary_motion_interface.py`
- `configs/step34_boundary_motion_interface_prescribed_kinematic.json`
- `configs/step34_squid_proxy_static_48_none.json`
- `configs/step34_squid_proxy_static_48_penalty.json`
- `configs/step34_squid_proxy_static_48_moving_boundary.json`
- `configs/step34_squid_proxy_static_48_link_area.json`
- `configs/step34_squid_proxy_prescribed_interface_48_moving_boundary.json`
- `configs/step34_squid_proxy_prescribed_interface_48_link_area.json`
- `baseline_tests/step34_common.py`
- `baseline_tests/run_step34_boundary_motion_config_validation.py`
- `baseline_tests/run_step34_boundary_motion_interface_report.py`
- `baseline_tests/run_step34_static_driver_regression.py`
- `baseline_tests/run_step34_prescribed_interface_noop_smoke.py`
- `baseline_tests/run_step34_step31_static_comparison.py`
- `baseline_tests/run_step34_noop_state_guard.py`
- `baseline_tests/run_step34_quality_report_aggregation.py`
- `baseline_tests/run_step34_step33_regression_guard.py`
- `baseline_tests/run_step34_artifact_manifest.py`
- `tests/test_step34_boundary_motion_driver_interface_contract.py`
- `outputs/step34_*`
- `logs/step34_*.log`

Updated:

- `src/fsi_config.py`
- `src/fsi_driver.py`
- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/11_artifact_policy.md`
- `docs/12_geometry_ingestion.md`
- `docs/33_controlled_squid_proxy_kinematics_mapping.md`

## 3. Explicit Non-Goals

Step 34 does not write prescribed kinematic values into LBM populations, MPM particles, MPM grid velocity, projector state, moving links, penalty coupling, moving-boundary coupling, link-area transfer, or external solver code.

The Step 34 driver change is limited to config validation and report writing.

## 4. Boundary-Motion Config Validation

Artifacts:

- `outputs/step34_boundary_motion_config_validation/boundary_motion_config_validation.csv`
- `outputs/step34_boundary_motion_config_validation/boundary_motion_config_validation.json`
- `outputs/step34_boundary_motion_config_validation/boundary_motion_config_validation_summary.csv`
- `logs/step34_boundary_motion_config_validation.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 21 |
| pass_count | 21 |
| validation_pass | true |

The validation checks source paths, expected row counts, diagnostic-only state, deterministic state, and every execution flag.

## 5. Boundary-Motion Interface Report

Artifacts:

- `outputs/step34_boundary_motion_interface_report/boundary_motion_interface_report.json`
- `outputs/step34_boundary_motion_interface_report/boundary_motion_interface_report_summary.csv`
- `logs/step34_boundary_motion_interface_report.log`

Accepted summary:

| metric | value |
| --- | --- |
| boundary_motion_mode | prescribed_kinematic |
| schedule_row_count | 81 |
| motion_mapping_row_count | 243 |
| tracked_region_count | 3 |
| execution_flag_enabled_count | 0 |
| no_op_pass | true |

## 6. Static Driver Regression

Artifacts:

- `outputs/step34_static_driver_regression/static_driver_results.csv`
- `outputs/step34_static_driver_regression/static_driver_results.npz`
- `outputs/step34_static_driver_regression/static_driver_results.json`
- `logs/step34_static_driver_regression.log`

Accepted summary:

| metric | value |
| --- | --- |
| driver_row_count | 4 |
| static_boundary_motion_row_count | 4 |
| boundary_report_count | 0 |
| boundary_no_op_pass_count | 4 |
| stable_count | 4 |
| quality_pass_count | 4 |
| strict_count | 4 |

## 7. Prescribed Interface No-Op Smoke

Artifacts:

- `outputs/step34_prescribed_interface_noop_smoke/prescribed_interface_noop_results.csv`
- `outputs/step34_prescribed_interface_noop_smoke/prescribed_interface_noop_results.npz`
- `outputs/step34_prescribed_interface_noop_smoke/prescribed_interface_noop_results.json`
- `outputs/step34_prescribed_interface_noop_smoke/prescribed_interface_noop_comparison.csv`
- `outputs/step34_prescribed_interface_noop_smoke/prescribed_interface_noop_comparison.json`
- `logs/step34_prescribed_interface_noop_smoke.log`

Accepted summary:

| metric | value |
| --- | --- |
| driver_row_count | 2 |
| prescribed_boundary_motion_row_count | 2 |
| boundary_report_count | 2 |
| boundary_no_op_pass_count | 2 |
| max_boundary_motion_execution_flag_enabled_count | 0 |

The prescribed rows write `boundary_motion_interface_report.json` and remain no-op relative to the matching Step 34 static moving_boundary rows.

## 8. Step 31 Static Comparison

Artifacts:

- `outputs/step34_step31_static_comparison/step31_static_comparison.csv`
- `outputs/step34_step31_static_comparison/step31_static_comparison.json`
- `logs/step34_step31_static_comparison.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 4 |
| pass_count | 4 |
| comparison_pass | true |
| max_abs_float_delta | <= 1e-5 |
| int_mismatch_count | 0 |

## 9. No-Op State Guard

Artifacts:

- `outputs/step34_noop_state_guard/noop_state_guard.csv`
- `outputs/step34_noop_state_guard/noop_state_guard.json`
- `logs/step34_noop_state_guard.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 2 |
| pass_count | 2 |
| comparison_pass | true |
| max_abs_float_delta | 9.5367431640625e-07 |
| int_mismatch_count | 0 |
| prescribed_report_count | 2 |
| prescribed_no_op_pass_count | 2 |

## 10. Quality Report Aggregation

Artifacts:

- `outputs/step34_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step34_quality_report_aggregation/quality_report_summary.json`
- `logs/step34_quality_report_aggregation.log`

Accepted summary:

| metric | value |
| --- | --- |
| quality_report_count | 6 |
| pass_count | 6 |
| strict_count | 6 |
| static_boundary_motion_report_count | 4 |
| prescribed_boundary_motion_report_count | 2 |
| warning_count | 0 |
| error_count | 0 |

## 11. Step 33 Regression Guard

Artifacts:

- `outputs/step34_step33_regression_guard/step33_regression_guard.csv`
- `outputs/step34_step33_regression_guard/step33_regression_guard.json`
- `logs/step34_step33_regression_guard.log`

Accepted summary:

| metric | value |
| --- | --- |
| row_count | 8 |
| pass_count | 8 |
| step33_motion_row_count | 243 |
| step33_motion_quality_pass | true |
| step33_repeatability_pass | true |
| step33_consistency_pass | true |
| step33_large_file_count | 0 |
| step33_vtr_count | 0 |
| step33_particle_npy_count | 0 |

## 12. Artifact Manifest Summary

Artifacts:

- `outputs/step34_artifact_manifest/artifact_manifest.csv`
- `outputs/step34_artifact_manifest/artifact_summary.csv`
- `outputs/step34_artifact_manifest/artifact_summary.json`
- `logs/step34_artifact_manifest.log`

Accepted summary:

| metric | value |
| --- | --- |
| large_file_count | 0 |
| step34_total_size_mb | 2.1969194412231445 |
| total_size_mb | 145.98759841918945 |
| raw_candidate_large_file_count | 0 |
| scan_data_file_count | 0 |
| step34_vtr_count | 0 |
| step34_particle_npy_count | 0 |
| private_absolute_path_count | 0 |

## 13. Verification Commands

Executed before completion:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\fsi_config.py src\fsi_driver.py src\boundary_motion_config.py src\boundary_motion_interface.py baseline_tests\step34_common.py baseline_tests\run_step34_boundary_motion_config_validation.py baseline_tests\run_step34_boundary_motion_interface_report.py baseline_tests\run_step34_static_driver_regression.py baseline_tests\run_step34_prescribed_interface_noop_smoke.py baseline_tests\run_step34_step31_static_comparison.py baseline_tests\run_step34_noop_state_guard.py baseline_tests\run_step34_quality_report_aggregation.py baseline_tests\run_step34_step33_regression_guard.py baseline_tests\run_step34_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step34_boundary_motion_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step34_boundary_motion_interface_report.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step34_static_driver_regression.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step34_prescribed_interface_noop_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step34_step31_static_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step34_noop_state_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step34_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step34_step33_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step34_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q *> logs\step34_pytest.log
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step34_boundary_motion_driver_interface_contract.py -q
pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

`logs/step34_pytest.log` records the full trusted pytest run.

Trusted full pytest result: `319 passed`.

Trusted Step 34 contract result: `15 passed`.

Plain shell `pytest -q` returned exit code 1 with no stdout or stderr in this workspace, matching the earlier local shim behavior. The trusted workspace interpreter command `& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q` passed and is the authoritative verification result for this repository.

## 14. GitHub Sync Information

Commit message:

```text
test: add step34 boundary motion driver interface contract
```

Target remote branch: `origin/main`.

The user approved push after modification. The final pushed commit hash is reported in the turn close-out.

## 15. Acceptance Checklist

- [x] boundary-motion config validation passes
- [x] diagnostic_only is true
- [x] all boundary-motion execution flags are false
- [x] interface report writes schedule_row_count == 81
- [x] interface report writes motion_mapping_row_count == 243
- [x] interface report writes tracked_region_count == 3
- [x] interface report no_op_pass is true
- [x] static none row passes
- [x] static penalty row passes
- [x] static moving_boundary engineering row passes
- [x] static moving_boundary link_area row passes
- [x] prescribed moving_boundary engineering row passes
- [x] prescribed moving_boundary link_area row passes
- [x] prescribed rows write boundary_motion_interface_report.json
- [x] prescribed rows remain no-op relative to Step 34 static rows
- [x] Step 31 static comparison passes
- [x] Step 33 regression guard passes
- [x] every Step 34 quality report passes strict gate
- [x] default boundary_motion_mode remains static
- [x] default quality_check_enabled remains false
- [x] default quality_check_strict remains false
- [x] default reaction_transfer_mode remains engineering
- [x] no LBM population update
- [x] no moving bounce-back formula changes
- [x] no coupler formula changes
- [x] no projection formula changes
- [x] no external/taichi_LBM3D edits
- [x] no Step 34 .vtr outputs
- [x] no Step 34 particle .npy outputs
- [x] artifact large_file_count == 0
- [x] Step 34 output total-size budget passes
- [x] repo artifact summary total_size_mb < 205
- [x] logs/step34_pytest.log exists
- [x] full pytest passes
- [x] Step 34 contract test passes
- [x] git diff --check passes
- [x] staged whitespace check passes
- [x] pre-push hook passes
- [x] Step 34 artifacts are pushed to origin/main

## 16. Decision For Step 35

Step 35 should be `Controlled Squid Proxy Moving-Wall Velocity Field Diagnostic Contract`. It may define and validate a velocity-field diagnostic generated from the accepted Step 34 interface, but it should still avoid LBM population updates until a later explicitly validated contract.
