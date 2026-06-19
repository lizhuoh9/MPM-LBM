# Step 27 Controlled Real Geometry 64 Short Driver Report

## 1. Goal

Step 27 is controlled real geometry 64^3 short driver feasibility.
Step 27 is not real squid validation.
Step 27 does not implement squid actuation.
Step 27 does not implement squid swimming.
Step 27 does not implement new FSI physics.
Step 27 does not validate production sharp-interface FSI.

The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 27 carries the accepted Step 25 controlled candidates from Step 26 projection-only and 48^3 short-driver feasibility into a six-row 64^3 coupling subset.

## 2. Files Created And Updated

Created:

- `STEP27_CONTROLLED_REAL_GEOMETRY_64_SHORT_DRIVER_GOAL.md`
- `STEP27_CONTROLLED_REAL_GEOMETRY_64_SHORT_DRIVER_REPORT.md`
- `docs/27_controlled_real_geometry_64_short_driver.md`
- `configs/step27_driver_real_candidate_smoke_mesh_64_penalty.json`
- `configs/step27_driver_real_candidate_smoke_mesh_64_moving_boundary.json`
- `configs/step27_driver_real_candidate_smoke_mesh_64_link_area.json`
- `configs/step27_driver_real_candidate_smoke_voxel_64_penalty.json`
- `configs/step27_driver_real_candidate_smoke_voxel_64_moving_boundary.json`
- `configs/step27_driver_real_candidate_smoke_voxel_64_link_area.json`
- `baseline_tests/step27_common.py`
- `baseline_tests/run_step27_candidate_fingerprint_guard.py`
- `baseline_tests/run_step27_64_driver_mesh_feasibility.py`
- `baseline_tests/run_step27_64_driver_voxel_feasibility.py`
- `baseline_tests/run_step27_driver_projection_alignment.py`
- `baseline_tests/run_step27_64_driver_summary.py`
- `baseline_tests/run_step27_quality_report_aggregation.py`
- `baseline_tests/run_step27_step26_regression_guard.py`
- `baseline_tests/run_step27_artifact_manifest.py`
- `tests/test_step27_controlled_real_geometry_64_short_driver_contract.py`

Updated:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/11_artifact_policy.md`
- `docs/12_geometry_ingestion.md`
- `docs/19_geometry_import_pipeline.md`
- `docs/24_controlled_real_geometry_intake.md`
- `docs/25_real_geometry_candidate_policy.md`
- `docs/26_controlled_real_geometry_short_feasibility.md`

## 3. Explicit Non-Goals

- No squid actuation.
- No squid swimming.
- No new FSI physics.
- No production sharp-interface FSI validation.
- No change to `PenaltyFSICoupler3D`.
- No change to `MovingBoundaryFSICoupler3D`.
- No change to `LinkAreaMovingBoundaryCoupler3D`.
- No change to the moving bounce-back formula.
- No change to LBM step formulas.
- No change to MPM constitutive formulas.
- No change to projection formulas.
- No production mesh repair.
- No automatic remeshing.
- No two-phase flow.
- No contact angle physics.
- No sparse-storage implementation.
- No edits to `external/taichi_LBM3D`.
- No committed raw large real geometry or scan data.

## 4. Candidate Fingerprint Guard

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_candidate_fingerprint_guard.py
```

Artifacts:

- `outputs/step27_candidate_fingerprint_guard/fingerprint_guard.csv`
- `outputs/step27_candidate_fingerprint_guard/fingerprint_guard.json`
- `logs/step27_candidate_fingerprint_guard.log`

Results:

| candidate_id | type | size_bytes | sha256_match | guard_pass |
| ------------ | ---- | ---------: | ------------- | ---------- |
| real_candidate_smoke_mesh | mesh | 323 | true | true |
| real_candidate_smoke_voxel | voxel | 32896 | true | true |

Row count: 2. Pass count: 2. Source paths are repo-relative/redacted. The Step 26 generated `GeometryConfig` source paths still match the accepted descriptors.

## 5. 64^3 Mesh Short Driver Feasibility

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_64_driver_mesh_feasibility.py
```

Artifacts:

- `outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.csv`
- `outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.npz`
- `outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.json`
- `logs/step27_64_driver_mesh_feasibility.log`

Results:

| mode | transfer | rho_min | rho_max | lbm_max_v | projected_mass | active_cells | force_max | bb_links | area_scale | stable |
| ---- | -------- | ------: | ------: | --------: | -------------: | -----------: | --------: | -------: | ---------: | ------ |
| moving_boundary | engineering | 0.996100783 | 1.003526330 | 0.005611053 | 0.605824947357 | 110592 | 0.000000000000e+00 | 498690 | 1.000000000 | true |
| moving_boundary | link_area_experimental | 0.996100783 | 1.003526330 | 0.005611053 | 0.605826795101 | 110592 | 0.000000000000e+00 | 498690 | 0.783299506 | true |
| penalty | engineering | 0.999999762 | 1.000001192 | 0.000002964 | 0.605826497078 | 110592 | 2.986912022607e-06 | 0 | 1.000000000 | true |

All 3 mesh rows completed 5 LBM steps and 25 MPM substeps.

## 6. 64^3 Voxel Short Driver Feasibility

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_64_driver_voxel_feasibility.py
```

Artifacts:

- `outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.csv`
- `outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.npz`
- `outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.json`
- `logs/step27_64_driver_voxel_feasibility.log`

Results:

| mode | transfer | rho_min | rho_max | lbm_max_v | projected_mass | active_cells | force_max | bb_links | area_scale | stable |
| ---- | -------- | ------: | ------: | --------: | -------------: | -----------: | --------: | -------: | ---------: | ------ |
| moving_boundary | engineering | 0.993246675 | 1.006780982 | 0.006081224 | 0.099440991879 | 31116 | 0.000000000000e+00 | 102014 | 1.000000000 | true |
| moving_boundary | link_area_experimental | 0.993246675 | 1.006780982 | 0.006081224 | 0.099440932274 | 31116 | 0.000000000000e+00 | 102014 | 0.791170597 | true |
| penalty | engineering | 0.999999344 | 1.000001431 | 0.000003160 | 0.099441051483 | 31116 | 2.989396762132e-06 | 0 | 1.000000000 | true |

All 3 voxel rows completed 5 LBM steps and 25 MPM substeps.

## 7. Driver Projection Alignment

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_driver_projection_alignment.py
```

Artifacts:

- `outputs/step27_driver_projection_alignment/driver_projection_alignment.csv`
- `outputs/step27_driver_projection_alignment/driver_projection_alignment.json`
- `logs/step27_driver_projection_alignment.log`

Results:

| candidate_id | mode | transfer | mass_delta | active_cell_delta | pass |
| ------------ | ---- | -------- | ---------: | ----------------: | ---- |
| real_candidate_smoke_mesh | moving_boundary | engineering | -1.1324882507324219e-06 | 0 | true |
| real_candidate_smoke_mesh | moving_boundary | link_area_experimental | 7.152557373046875e-07 | 0 | true |
| real_candidate_smoke_mesh | penalty | engineering | 4.172325134277344e-07 | 0 | true |
| real_candidate_smoke_voxel | moving_boundary | engineering | -8.195638656616211e-08 | 0 | true |
| real_candidate_smoke_voxel | moving_boundary | link_area_experimental | -1.4156103134155273e-07 | 0 | true |
| real_candidate_smoke_voxel | penalty | engineering | -2.2351741790771484e-08 | 0 | true |

Row count: 6. Pass count: 6. The active-cell delta is 0 for every row.

## 8. 64^3 Driver Summary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_64_driver_summary.py
```

Artifacts:

- `outputs/step27_64_driver_summary/driver_64_summary.csv`
- `outputs/step27_64_driver_summary/driver_64_summary.npz`
- `outputs/step27_64_driver_summary/driver_64_summary.json`
- `logs/step27_64_driver_summary.log`

Summary:

| metric | value |
| ------ | ----: |
| driver_row_count | 6 |
| stable_count | 6 |
| quality_report_count | 6 |
| quality_pass_count | 6 |
| mesh_row_count | 3 |
| voxel_row_count | 3 |
| penalty_row_count | 2 |
| moving_boundary_row_count | 4 |
| link_area_row_count | 2 |
| min_rho_min_global | 0.9932466745376587 |
| max_rho_max_global | 1.006780982017517 |
| max_lbm_max_v_global | 0.0060812244191765785 |
| min_mpm_min_J_global | 0.9997908473014832 |
| max_mpm_max_speed_global | 0.026037687435746193 |
| min_projected_mass | 0.09944093227386475 |
| min_active_cell_count | 31116 |
| max_driver_total_time | 216.0315125999623 |

## 9. Quality Report Aggregation

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_quality_report_aggregation.py
```

Artifacts:

- `outputs/step27_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step27_quality_report_aggregation/quality_report_summary.json`
- `logs/step27_quality_report_aggregation.log`

Summary:

| metric | value |
| ------ | ----: |
| quality_report_count | 6 |
| pass_count | 6 |
| strict_count | 6 |
| error_count | 0 |
| warning_count | 0 |
| mesh_row_count | 3 |
| voxel_row_count | 3 |
| quality_report_total_size_bytes | 7113 |
| quality_report_max_size_bytes | 1294 |

## 10. Step 26 Regression Guard

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_step26_regression_guard.py
```

Artifacts:

- `outputs/step27_step26_regression_guard/step26_regression_guard.csv`
- `outputs/step27_step26_regression_guard/step26_regression_guard.json`
- `logs/step27_step26_regression_guard.log`

Results: 8 guard rows, 8 pass. Step 26 projection row count remains 6, Step 26 short driver row count remains 8, Step 26 stable count remains 8, Step 26 quality report count remains 8, and Step 26 artifact large-file count remains 0.

## 11. Artifact Manifest Summary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_artifact_manifest.py
```

Artifacts:

- `outputs/step27_artifact_manifest/artifact_manifest.csv`
- `outputs/step27_artifact_manifest/artifact_summary.csv`
- `outputs/step27_artifact_manifest/artifact_summary.json`
- `logs/step27_artifact_manifest.log`

Final artifact summary is regenerated after report and `logs/step27_pytest.log` are present.

Current summary:

| metric | value |
| ------ | ----: |
| file_count | 1628 |
| total_size_bytes | 141567403 |
| total_size_mb | 135.00919628143310 |
| large_file_count | 0 |
| step27_file_count | 72 |
| step27_total_size_bytes | 4986139 |
| step27_total_size_mb | 4.7551527023315430 |
| step27_vtr_count | 0 |
| step27_particle_npy_count | 0 |
| step27_quality_report_count | 6 |
| raw_candidate_large_file_count | 0 |
| scan_data_file_count | 0 |
| private_absolute_path_count | 0 |

## 12. Verification Commands

Executed or required in this order:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile baseline_tests\step27_common.py baseline_tests\run_step27_candidate_fingerprint_guard.py baseline_tests\run_step27_64_driver_mesh_feasibility.py baseline_tests\run_step27_64_driver_voxel_feasibility.py baseline_tests\run_step27_driver_projection_alignment.py baseline_tests\run_step27_64_driver_summary.py baseline_tests\run_step27_quality_report_aggregation.py baseline_tests\run_step27_step26_regression_guard.py baseline_tests\run_step27_artifact_manifest.py tests\test_step27_controlled_real_geometry_64_short_driver_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_candidate_fingerprint_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_64_driver_mesh_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_64_driver_voxel_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_driver_projection_alignment.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_64_driver_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_step26_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step27_controlled_real_geometry_64_short_driver_contract.py -q
pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

The full pytest output is written to `logs/step27_pytest.log`.

## 13. GitHub Sync Information

Target remote branch: `origin/main`.

This report is part of the Step 27 commit. The final pushed commit hash is reported in the completion message because a git commit cannot embed its own final hash without changing that hash.

## 14. Acceptance Checklist

- [x] candidate fingerprint guard passes
- [x] Step 25 manifest fingerprints match current candidate files
- [x] Step 26 generated GeometryConfig files remain valid
- [x] mesh 64^3 penalty short driver passes
- [x] mesh 64^3 moving_boundary engineering short driver passes
- [x] mesh 64^3 moving_boundary link_area short driver passes
- [x] voxel 64^3 penalty short driver passes
- [x] voxel 64^3 moving_boundary engineering short driver passes
- [x] voxel 64^3 moving_boundary link_area short driver passes
- [x] every Step 27 driver row writes geometry_quality_report.json
- [x] every Step 27 quality gate is strict
- [x] every Step 27 quality report passes
- [x] quality warning count == 0
- [x] quality error count == 0
- [x] all driver rows have completed_lbm_steps >= 5
- [x] all driver rows have total_mpm_substeps >= 25
- [x] rho_min > 0.95
- [x] rho_max < 1.05
- [x] lbm_max_v < 0.1
- [x] mpm_min_J > 0
- [x] mpm_max_speed < 10
- [x] projected_mass > 0
- [x] active_cell_count > 0
- [x] no NaN
- [x] no Inf
- [x] penalty rows have positive cell_force_max_norm
- [x] moving_boundary rows keep cell_force_max_norm == 0
- [x] moving_boundary rows have bb_link_count > 0
- [x] moving_boundary rows have active_reaction_particle_count_max > 0
- [x] link_area rows have finite bounded area_scale
- [x] driver/projection alignment passes against Step 26 64^3 projection-only rows
- [x] Step 26 regression guard passes
- [x] default quality_check_enabled remains false
- [x] default quality_check_strict remains false
- [x] default reaction_transfer_mode remains engineering
- [x] no FSI formula changes
- [x] no moving bounce-back formula changes
- [x] no LBM formula changes
- [x] no MPM constitutive formula changes
- [x] no projection formula changes
- [x] no production mesh repair claims
- [x] no automatic remeshing claims
- [x] no real squid validation claims
- [x] no squid swimming claims
- [x] no squid actuation claims
- [x] no production sharp-interface FSI claims
- [x] no final readiness claims
- [x] no external/taichi_LBM3D edits
- [x] no committed large raw real geometry
- [x] no committed scan data
- [x] no private absolute paths in committed outputs
- [x] no Step 27 .vtr outputs
- [x] no Step 27 particle .npy outputs
- [x] artifact large_file_count == 0
- [x] Step 27 output total size budget passes
- [x] repo artifact_summary total_size_mb < 155
- [x] logs/step27_pytest.log exists
- [x] pytest -q passes
- [x] Step 27 contract test passes
- [x] git diff --check passes
- [x] staged whitespace check passes
- [x] pre-push hook passes
- [x] Step 27 artifacts are pushed to origin/main

## 15. Decision For Step 28

If Step 27 passes, Step 28 should stay conservative: compare engineering and link-area transfer at 64^3, add force/reaction diagnostics, summarize the area-scale envelope, and continue to avoid actuation, swimming, production sharp-interface FSI claims, final readiness claims, production mesh repair, automatic remeshing, and solver formula changes.
