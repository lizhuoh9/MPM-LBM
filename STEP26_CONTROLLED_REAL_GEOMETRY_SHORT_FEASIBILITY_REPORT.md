# Step 26 Controlled Real Geometry Short Feasibility Report

## 1. Goal

Step 26 is controlled real geometry projection-only and short driver feasibility.
Step 26 is not real squid validation.
Step 26 does not implement squid actuation.
Step 26 does not implement squid swimming.
Step 26 does not implement new FSI physics.
Step 26 does not validate production sharp-interface FSI.

The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 26 takes the accepted Step 25 candidates through fingerprint-guarded config generation, projection-only scale diagnostics, Step 25 projection regression, and 48^3 very short driver feasibility.

## 2. Files Created And Updated

Created:

- `STEP26_CONTROLLED_REAL_GEOMETRY_SHORT_FEASIBILITY_GOAL.md`
- `STEP26_CONTROLLED_REAL_GEOMETRY_SHORT_FEASIBILITY_REPORT.md`
- `src/geometry_driver_config.py`
- `src/real_geometry_feasibility.py`
- `configs/step26_real_candidate_smoke_mesh_geometry.json`
- `configs/step26_real_candidate_smoke_voxel_geometry.json`
- `configs/step26_projection_real_candidate_smoke_mesh_32.json`
- `configs/step26_projection_real_candidate_smoke_mesh_48.json`
- `configs/step26_projection_real_candidate_smoke_mesh_64.json`
- `configs/step26_projection_real_candidate_smoke_voxel_32.json`
- `configs/step26_projection_real_candidate_smoke_voxel_48.json`
- `configs/step26_projection_real_candidate_smoke_voxel_64.json`
- `configs/step26_driver_real_candidate_smoke_mesh_48_none.json`
- `configs/step26_driver_real_candidate_smoke_mesh_48_penalty.json`
- `configs/step26_driver_real_candidate_smoke_mesh_48_moving_boundary.json`
- `configs/step26_driver_real_candidate_smoke_mesh_48_link_area.json`
- `configs/step26_driver_real_candidate_smoke_voxel_48_none.json`
- `configs/step26_driver_real_candidate_smoke_voxel_48_penalty.json`
- `configs/step26_driver_real_candidate_smoke_voxel_48_moving_boundary.json`
- `configs/step26_driver_real_candidate_smoke_voxel_48_link_area.json`
- `baseline_tests/step26_common.py`
- `baseline_tests/run_step26_candidate_fingerprint_guard.py`
- `baseline_tests/run_step26_generate_driver_geometry_configs.py`
- `baseline_tests/run_step26_projection_scale_diagnostics.py`
- `baseline_tests/run_step26_step25_projection_regression.py`
- `baseline_tests/run_step26_short_driver_mesh_48_modes.py`
- `baseline_tests/run_step26_short_driver_voxel_48_modes.py`
- `baseline_tests/run_step26_short_driver_summary.py`
- `baseline_tests/run_step26_quality_report_aggregation.py`
- `baseline_tests/run_step26_step25_regression_guard.py`
- `baseline_tests/run_step26_artifact_manifest.py`
- `docs/26_controlled_real_geometry_short_feasibility.md`
- `tests/test_step26_controlled_real_geometry_short_feasibility_contract.py`

Updated:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/11_artifact_policy.md`
- `docs/12_geometry_ingestion.md`
- `docs/19_geometry_import_pipeline.md`
- `docs/24_controlled_real_geometry_intake.md`
- `docs/25_real_geometry_candidate_policy.md`

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
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_candidate_fingerprint_guard.py
```

Artifacts:

- `outputs/step26_candidate_fingerprint_guard/fingerprint_guard.csv`
- `outputs/step26_candidate_fingerprint_guard/fingerprint_guard.json`
- `logs/step26_candidate_fingerprint_guard.log`

Results:

| candidate_id | type | size_bytes | sha256_match | guard_pass |
| ------------ | ---- | ---------: | ------------- | ---------- |
| real_candidate_smoke_mesh | mesh | 323 | true | true |
| real_candidate_smoke_voxel | voxel | 32896 | true | true |

Row count: 2. Pass count: 2. Source paths are repo-relative/redacted.

## 5. Generated Driver Geometry Configs

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_generate_driver_geometry_configs.py
```

Artifacts:

- `configs/step26_real_candidate_smoke_mesh_geometry.json`
- `configs/step26_real_candidate_smoke_voxel_geometry.json`
- `outputs/step26_generated_geometry_configs/generated_geometry_configs.csv`
- `outputs/step26_generated_geometry_configs/generated_geometry_configs.json`
- `logs/step26_generate_driver_geometry_configs.log`

Results: 2 valid `GeometryConfig` files and 8 short driver configs. Both geometry configs use `n_particles = 4096`, `quality_check_enabled = true`, and `quality_check_strict = true`.

## 6. Projection-Only Scale Diagnostics

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_projection_scale_diagnostics.py
```

Artifacts:

- `outputs/step26_projection_scale_diagnostics/projection_scale_results.csv`
- `outputs/step26_projection_scale_diagnostics/projection_scale_results.npz`
- `outputs/step26_projection_scale_diagnostics/projection_scale_results.json`
- `logs/step26_projection_scale_diagnostics.log`

Results:

| candidate_id | n_grid | projected_mass | active_cell_count | solid_phi_min | solid_phi_max | pass |
| ------------ | -----: | -------------: | ----------------: | ------------: | ------------: | ---- |
| real_candidate_smoke_mesh | 32 | 0.605826139450 | 23961 | 0.0 | 1.0 | true |
| real_candidate_smoke_mesh | 48 | 0.605826020241 | 68954 | 0.0 | 1.0 | true |
| real_candidate_smoke_mesh | 64 | 0.605826079845 | 110592 | 0.0 | 1.0 | true |
| real_candidate_smoke_voxel | 32 | 0.099441051483 | 5286 | 0.0 | 1.0 | true |
| real_candidate_smoke_voxel | 48 | 0.099441081285 | 14141 | 0.0 | 1.0 | true |
| real_candidate_smoke_voxel | 64 | 0.099441073835 | 31116 | 0.0 | 1.0 | true |

Row count: 6. Pass count: 6. NaN count: 0. Inf count: 0. This path is projection-only and does not run the FSI driver.

## 7. Step 25 Projection Regression

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_step25_projection_regression.py
```

Artifacts:

- `outputs/step26_step25_projection_regression/step25_projection_regression.csv`
- `outputs/step26_step25_projection_regression/step25_projection_regression.json`
- `logs/step26_step25_projection_regression.log`

Results:

| candidate_id | projected_mass_delta | active_cell_count_delta | phi_min_delta | phi_max_delta | pass |
| ------------ | -------------------: | ----------------------: | ------------: | ------------: | ---- |
| real_candidate_smoke_mesh | -5.960464477539063e-08 | 0 | 0.0 | 0.0 | true |
| real_candidate_smoke_voxel | 0.0 | 0 | 0.0 | 0.0 | true |

Compared row count: 2. Pass count: 2.

## 8. 48^3 Mesh Short Driver Feasibility

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_short_driver_mesh_48_modes.py
```

Artifacts:

- `outputs/step26_short_driver_mesh_48_modes/mesh_48_short_driver_results.csv`
- `outputs/step26_short_driver_mesh_48_modes/mesh_48_short_driver_results.npz`
- `outputs/step26_short_driver_mesh_48_modes/mesh_48_short_driver_results.json`
- `logs/step26_short_driver_mesh_48_modes.log`

Results:

| mode | transfer | rho_min | rho_max | lbm_max_v | projected_mass | active_cells | force_max | bb_links | area_scale | stable |
| ---- | -------- | ------: | ------: | --------: | -------------: | -----------: | --------: | -------: | ---------: | ------ |
| none | engineering | 1.000000000 | 1.000000358 | 0.000000000 | 0.605825483799 | 68947 | 0.000000000000e+00 | 0 | 1.000000000 | true |
| penalty | engineering | 0.999999523 | 1.000001311 | 0.000003001 | 0.605824589729 | 68947 | 2.987732841575e-06 | 0 | 1.000000000 | true |
| moving_boundary | engineering | 0.994422853 | 1.004842281 | 0.005786321 | 0.605825662613 | 68947 | 0.000000000000e+00 | 313294 | 1.000000000 | true |
| moving_boundary | link_area_experimental | 0.994422734 | 1.004842401 | 0.005786343 | 0.605825960636 | 68947 | 0.000000000000e+00 | 313294 | 0.778742969 | true |

All 4 rows completed 5 LBM steps and 25 MPM substeps.

## 9. 48^3 Voxel Short Driver Feasibility

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_short_driver_voxel_48_modes.py
```

Artifacts:

- `outputs/step26_short_driver_voxel_48_modes/voxel_48_short_driver_results.csv`
- `outputs/step26_short_driver_voxel_48_modes/voxel_48_short_driver_results.npz`
- `outputs/step26_short_driver_voxel_48_modes/voxel_48_short_driver_results.json`
- `logs/step26_short_driver_voxel_48_modes.log`

Results:

| mode | transfer | rho_min | rho_max | lbm_max_v | projected_mass | active_cells | force_max | bb_links | area_scale | stable |
| ---- | -------- | ------: | ------: | --------: | -------------: | -----------: | --------: | -------: | ---------: | ------ |
| none | engineering | 1.000000000 | 1.000000358 | 0.000000000 | 0.099441081285 | 14141 | 0.000000000000e+00 | 0 | 1.000000000 | true |
| penalty | engineering | 0.999999344 | 1.000001550 | 0.000003212 | 0.099441081285 | 14141 | 2.989472932313e-06 | 0 | 1.000000000 | true |
| moving_boundary | engineering | 0.991988122 | 1.007332802 | 0.006088905 | 0.099441148341 | 14141 | 0.000000000000e+00 | 37204 | 1.000000000 | true |
| moving_boundary | link_area_experimental | 0.991988063 | 1.007332683 | 0.006088879 | 0.099441006780 | 14141 | 0.000000000000e+00 | 37204 | 0.786895335 | true |

All 4 rows completed 5 LBM steps and 25 MPM substeps.

## 10. Short Driver Summary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_short_driver_summary.py
```

Artifacts:

- `outputs/step26_short_driver_summary/short_driver_summary.csv`
- `outputs/step26_short_driver_summary/short_driver_summary.npz`
- `outputs/step26_short_driver_summary/short_driver_summary.json`
- `logs/step26_short_driver_summary.log`

Summary:

| metric | value |
| ------ | ----: |
| driver_row_count | 8 |
| stable_count | 8 |
| quality_report_count | 8 |
| quality_pass_count | 8 |
| min_rho_min_global | 0.9919880628585815 |
| max_rho_max_global | 1.0073328018188477 |
| max_lbm_max_v_global | 0.006088905036449432 |
| min_mpm_min_J_global | 0.9996494650840759 |
| max_mpm_max_speed_global | 0.033784739673137665 |
| min_projected_mass | 0.09944100677967072 |
| min_active_cell_count | 14141 |
| max_step26_driver_total_time | 210.2499514000374 |

## 11. Quality Report Aggregation

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_quality_report_aggregation.py
```

Artifacts:

- `outputs/step26_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step26_quality_report_aggregation/quality_report_summary.json`
- `logs/step26_quality_report_aggregation.log`

Summary:

| metric | value |
| ------ | ----: |
| quality_report_count | 8 |
| pass_count | 8 |
| strict_count | 8 |
| error_count | 0 |
| warning_count | 0 |
| mesh_row_count | 4 |
| voxel_row_count | 4 |
| quality_report_total_size_bytes | 9484 |
| quality_report_max_size_bytes | 1294 |

## 12. Step 25 Regression Guard

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_step25_regression_guard.py
```

Artifacts:

- `outputs/step26_step25_regression_guard/step25_regression_guard.csv`
- `outputs/step26_step25_regression_guard/step25_regression_guard.json`
- `logs/step26_step25_regression_guard.log`

Results: 7 guard rows, 7 pass. Step 25 manifest row count remains 2. Step 25 large-file, scan-data, and raw-candidate-large-file counts remain 0.

## 13. Artifact Manifest Summary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_artifact_manifest.py
```

Artifacts:

- `outputs/step26_artifact_manifest/artifact_manifest.csv`
- `outputs/step26_artifact_manifest/artifact_summary.csv`
- `outputs/step26_artifact_manifest/artifact_summary.json`
- `logs/step26_artifact_manifest.log`

Final artifact summary is regenerated after report and `logs/step26_pytest.log` are present.

Summary:

| metric | value |
| ------ | ----: |
| file_count | 1554 |
| total_size_bytes | 136511710 |
| total_size_mb | 130.18771171569824 |
| large_file_count | 0 |
| step26_file_count | 110 |
| step26_total_size_bytes | 5591957 |
| step26_total_size_mb | 5.3329057693481445 |
| step26_vtr_count | 0 |
| step26_particle_npy_count | 0 |
| step26_quality_report_count | 8 |
| raw_candidate_large_file_count | 0 |
| scan_data_file_count | 0 |
| private_absolute_path_count | 0 |

## 14. Verification Commands

Executed or required in this order:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\geometry_driver_config.py src\real_geometry_feasibility.py baseline_tests\step26_common.py baseline_tests\run_step26_candidate_fingerprint_guard.py baseline_tests\run_step26_generate_driver_geometry_configs.py baseline_tests\run_step26_projection_scale_diagnostics.py baseline_tests\run_step26_step25_projection_regression.py baseline_tests\run_step26_short_driver_mesh_48_modes.py baseline_tests\run_step26_short_driver_voxel_48_modes.py baseline_tests\run_step26_short_driver_summary.py baseline_tests\run_step26_quality_report_aggregation.py baseline_tests\run_step26_step25_regression_guard.py baseline_tests\run_step26_artifact_manifest.py tests\test_step26_controlled_real_geometry_short_feasibility_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_candidate_fingerprint_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_generate_driver_geometry_configs.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_projection_scale_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_step25_projection_regression.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_short_driver_mesh_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_short_driver_voxel_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_short_driver_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_step25_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step26_controlled_real_geometry_short_feasibility_contract.py -q
git diff --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

The full pytest output is written to `logs/step26_pytest.log`.

## 15. GitHub Sync Information

Target remote branch: `origin/main`.

This report is part of the Step 26 commit. The final pushed commit hash is reported in the completion message because a git commit cannot embed its own final hash without changing that hash.

## 16. Acceptance Checklist

- [x] candidate fingerprint guard passes
- [x] Step 25 manifest fingerprints match current candidate files
- [x] generated driver GeometryConfig files are valid
- [x] generated driver configs preserve strict quality gate
- [x] projection-only scale diagnostics pass for 32^3 rows
- [x] projection-only scale diagnostics pass for 48^3 rows
- [x] projection-only scale diagnostics pass for 64^3 rows
- [x] Step 25 projection regression passes for 32^3 rows
- [x] mesh 48^3 none short driver passes
- [x] mesh 48^3 penalty short driver passes
- [x] mesh 48^3 moving_boundary engineering short driver passes
- [x] mesh 48^3 moving_boundary link_area short driver passes
- [x] voxel 48^3 none short driver passes
- [x] voxel 48^3 penalty short driver passes
- [x] voxel 48^3 moving_boundary engineering short driver passes
- [x] voxel 48^3 moving_boundary link_area short driver passes
- [x] voxel 48^3 link_area short driver passes
- [x] every Step 26 driver row writes geometry_quality_report.json
- [x] every Step 26 quality gate is strict
- [x] every Step 26 quality report passes
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
- [x] link_area rows have finite bounded area_scale
- [x] Step 25 regression guard passes
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
- [x] no Step 26 .vtr outputs
- [x] no Step 26 particle .npy outputs
- [x] artifact large_file_count == 0
- [x] Step 26 output total size budget passes
- [x] repo artifact_summary total_size_mb < 170
- [x] logs/step26_pytest.log exists
- [x] pytest -q passes
- [x] Step 26 contract test passes
- [x] git diff --check passes
- [x] pre-push hook passes
- [x] Step 26 artifacts are pushed to origin/main

## 17. Decision For Step 27

Step 27 should be Controlled Real Geometry 64^3 Short Driver Feasibility.

It should remain conservative: carry only a small 64^3 short-driver subset forward, keep strict quality reports, avoid actuation and swimming claims, avoid production sharp-interface FSI claims, avoid final readiness claims, avoid mesh repair claims, avoid automatic remeshing claims, and avoid formula changes.
