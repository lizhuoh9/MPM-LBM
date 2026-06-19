# Step 24 Strict Quality-Gated Imported Geometry Long-Run Report

## 1. Goal

Step 24 runs strict quality-gated synthetic imported geometry long-run validation.
Step 24 uses quality_check_enabled=true and quality_check_strict=true for selected imported geometry rows.
Step 24 is not real squid validation.
Step 24 does not implement new FSI physics.

The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 24 mesh path is not production mesh repair or automatic remeshing.

## 2. Files Created And Updated

Created:

- `STEP24_STRICT_QUALITY_GATED_IMPORTED_GEOMETRY_LONG_RUN_GOAL.md`
- `STEP24_STRICT_QUALITY_GATED_IMPORTED_GEOMETRY_LONG_RUN_REPORT.md`
- `baseline_tests/step24_common.py`
- `baseline_tests/run_step24_strict_voxel_sphere_48_long.py`
- `baseline_tests/run_step24_strict_mesh_cube_48_long.py`
- `baseline_tests/run_step24_strict_mesh_ellipsoid_48_long.py`
- `baseline_tests/run_step24_strict_imported_geometry_64_feasibility.py`
- `baseline_tests/run_step24_quality_report_aggregation.py`
- `baseline_tests/run_step24_step23_prefix_comparison.py`
- `baseline_tests/run_step24_strict_non_strict_report_comparison.py`
- `baseline_tests/run_step24_timing_overhead_summary.py`
- `baseline_tests/run_step24_artifact_manifest.py`
- `configs/step24_strict_*.json`
- `docs/23_strict_quality_gated_imported_geometry_long_run.md`
- `tests/test_step24_strict_quality_gated_imported_geometry_long_run_contract.py`

Updated:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/12_geometry_ingestion.md`
- `docs/19_geometry_import_pipeline.md`
- `docs/20_imported_geometry_scale_validation.md`
- `docs/21_geometry_quality_checks.md`
- `docs/22_quality_gated_imported_geometry_validation.md`

## 3. Explicit Non-Goals

- No new FSI physics.
- No change to `PenaltyFSICoupler3D`.
- No change to `MovingBoundaryFSICoupler3D`.
- No change to `LinkAreaMovingBoundaryCoupler3D`.
- No change to the moving bounce-back formula.
- No change to LBM step formulas.
- No change to MPM constitutive formulas.
- No change to projection formulas.
- No change to default `quality_check_enabled = false`.
- No change to default `quality_check_strict = false`.
- No change to default `reaction_transfer_mode = "engineering"`.
- No real squid validation.
- No squid actuation or swimming validation.
- No production mesh repair.
- No automatic remeshing.
- No two-phase flow.
- No contact angle physics.
- No sparse storage.
- No edits to `external/taichi_LBM3D`.

## 4. 48^3 Voxel_Sphere Strict Long-Run

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_voxel_sphere_48_long.py
```

Artifact: `outputs/step24_strict_voxel_sphere_48_long/voxel_sphere_48_strict_long_results.csv`.

| transfer | rho_min_global | rho_max_global | lbm_max_v_global | mpm_min_J_global | projected_mass | active_cell_count | area_scale_final | stable |
| -------- | -------------: | -------------: | ---------------: | ---------------: | -------------: | ----------------: | ---------------: | ------ |
| engineering | 0.984065831 | 1.017020106 | 0.008774790 | 0.999202549 | 0.099441111 | 14188 | 1.000000000 | true |
| link_area_experimental | 0.984065592 | 1.017020345 | 0.008774760 | 0.999202311 | 0.099441059 | 14188 | 0.794031024 | true |

Both rows wrote strict `geometry_quality_report.json` files with `quality_pass=true`, `quality_severity=ok`, zero warnings, and zero reasons.

## 5. 48^3 Mesh_Cube Strict Long-Run

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_mesh_cube_48_long.py
```

Artifact: `outputs/step24_strict_mesh_cube_48_long/mesh_cube_48_strict_long_results.csv`.

| transfer | rho_min_global | rho_max_global | lbm_max_v_global | mpm_min_J_global | projected_mass | active_cell_count | area_scale_final | stable |
| -------- | -------------: | -------------: | ---------------: | ---------------: | -------------: | ----------------: | ---------------: | ------ |
| engineering | 0.995331705 | 1.005136847 | 0.004038962 | 0.999739230 | 0.747853041 | 61747 | 1.000000000 | true |
| link_area_experimental | 0.995331645 | 1.005136490 | 0.004038712 | 0.999739051 | 0.747850716 | 61747 | 0.799531937 | true |

Both rows wrote strict `geometry_quality_report.json` files with `quality_pass=true`, `quality_severity=ok`, zero warnings, and zero reasons.

## 6. 48^3 Mesh_Ellipsoid Strict Long-Run

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_mesh_ellipsoid_48_long.py
```

Artifact: `outputs/step24_strict_mesh_ellipsoid_48_long/mesh_ellipsoid_48_strict_long_results.csv`.

| transfer | rho_min_global | rho_max_global | lbm_max_v_global | mpm_min_J_global | projected_mass | active_cell_count | area_scale_final | stable |
| -------- | -------------: | -------------: | ---------------: | ---------------: | -------------: | ----------------: | ---------------: | ------ |
| engineering | 0.988013506 | 1.015392065 | 0.009199067 | 0.995057464 | 0.133917078 | 18342 | 1.000000000 | true |
| link_area_experimental | 0.988013327 | 1.015392423 | 0.009198980 | 0.995057344 | 0.133917257 | 18342 | 0.799485147 | true |

Both rows wrote strict `geometry_quality_report.json` files with `quality_pass=true`, `quality_severity=ok`, zero warnings, and zero reasons.

## 7. 64^3 Strict Imported Geometry Feasibility

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_imported_geometry_64_feasibility.py
```

Artifact: `outputs/step24_strict_imported_geometry_64_feasibility/imported_geometry_64_strict_feasibility_results.csv`.

| case | transfer | rho_min_global | rho_max_global | lbm_max_v_global | mpm_min_J_global | projected_mass | active_cell_count | area_scale_final | stable |
| ---- | -------- | -------------: | -------------: | ---------------: | ---------------: | -------------: | ----------------: | ---------------: | ------ |
| voxel_sphere | engineering | 0.994373143 | 1.005661249 | 0.005045215 | 0.999895573 | 0.099441171 | 31116 | 1.000000000 | true |
| mesh_cube | engineering | 0.997110724 | 1.002923012 | 0.004664375 | 0.999982595 | 0.747852206 | 88946 | 1.000000000 | true |
| mesh_cube | link_area_experimental | 0.997110665 | 1.002922893 | 0.004664362 | 0.999982655 | 0.747852623 | 88946 | 0.772117198 | true |

All three rows wrote strict `geometry_quality_report.json` files with `quality_pass=true`, `quality_severity=ok`, zero warnings, and zero reasons.

## 8. Quality Report Aggregation

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_quality_report_aggregation.py
```

Artifacts:

- `outputs/step24_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step24_quality_report_aggregation/quality_report_summary.json`

| metric | value |
| ------ | ----: |
| quality_report_count | 9 |
| pass_count | 9 |
| error_count | 0 |
| warning_count | 0 |
| mesh_row_count | 6 |
| voxel_row_count | 3 |
| quality_report_total_size_bytes | 11047 |
| quality_report_max_size_bytes | 1352 |

## 9. Step 23 Prefix Comparison

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_step23_prefix_comparison.py
```

Artifacts:

- `outputs/step24_step23_prefix_comparison/step23_prefix_comparison.csv`
- `outputs/step24_step23_prefix_comparison/step23_prefix_comparison.json`

| metric | value |
| ------ | ----: |
| row_count | 9 |
| compared_row_count | 7 |
| missing_overlap_count | 2 |
| stable_both_count | 9 |
| max_abs_rho_min_delta | 0.000001132 |
| max_abs_rho_max_delta | 0.000000954 |
| max_abs_lbm_max_v_delta | 0.000000075 |
| max_abs_mpm_min_J_delta | 0.000000179 |
| max_abs_projected_mass_delta | 0.000003159 |
| max_abs_active_cell_count_delta | 0 |

The two missing-overlap rows are the Step 24-only 64^3 `mesh_cube moving_boundary` and `mesh_cube link_area_experimental` feasibility rows.

## 10. Strict Vs Non-Strict Report Comparison

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_non_strict_report_comparison.py
```

Artifacts:

- `outputs/step24_strict_non_strict_report_comparison/strict_non_strict_report_comparison.csv`
- `outputs/step24_strict_non_strict_report_comparison/strict_non_strict_report_comparison.json`

| metric | value |
| ------ | ----: |
| row_count | 9 |
| reports_match_count | 9 |
| step23_report_count | 7 |
| qa_only_nonstrict_report_count | 2 |

Strict mode changed gate policy only for the good synthetic imported geometry reports; diagnostic counts and clean pass status remained aligned.

## 11. Timing And Overhead Summary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_timing_overhead_summary.py
```

Artifacts:

- `outputs/step24_timing_overhead_summary/step24_timing_summary.csv`
- `outputs/step24_timing_overhead_summary/step24_timing_summary.json`

| metric | value |
| ------ | ----: |
| row_count | 9 |
| median_total_time | 136.732836200 |
| max_total_time | 215.125179500 |
| quality_report_count | 9 |
| quality_report_total_size_bytes | 11047 |
| quality_report_max_size_bytes | 1352 |

Timing is a workflow and artifact-budget diagnostic only, not a production benchmark.

## 12. Artifact Manifest Summary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_artifact_manifest.py
```

Artifact manifest results are recorded in:

- `outputs/step24_artifact_manifest/artifact_manifest.csv`
- `outputs/step24_artifact_manifest/artifact_summary.csv`
- `outputs/step24_artifact_manifest/artifact_summary.json`

The final manifest was regenerated after the report and pytest log were present.

| metric | value |
| ------ | ----: |
| file_count | 1230 |
| total_size_bytes | 127779482 |
| total_size_mb | 121.860010 |
| large_file_count | 0 |
| step24_file_count | 85 |
| step24_quality_report_count | 9 |
| step24_total_size_bytes | 4709953 |
| step24_total_size_mb | 4.491761 |

No Step 24 `.vtr` files were written. No Step 24 particle `.npy` outputs were written.

## 13. Verification Commands

Executed:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile baseline_tests\step24_common.py baseline_tests\run_step24_strict_voxel_sphere_48_long.py baseline_tests\run_step24_strict_mesh_cube_48_long.py baseline_tests\run_step24_strict_mesh_ellipsoid_48_long.py baseline_tests\run_step24_strict_imported_geometry_64_feasibility.py baseline_tests\run_step24_quality_report_aggregation.py baseline_tests\run_step24_step23_prefix_comparison.py baseline_tests\run_step24_strict_non_strict_report_comparison.py baseline_tests\run_step24_timing_overhead_summary.py baseline_tests\run_step24_artifact_manifest.py tests\test_step24_strict_quality_gated_imported_geometry_long_run_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_voxel_sphere_48_long.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_mesh_cube_48_long.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_mesh_ellipsoid_48_long.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_imported_geometry_64_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_step23_prefix_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_non_strict_report_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_timing_overhead_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step24_strict_quality_gated_imported_geometry_long_run_contract.py -q
git diff --check
git status --short external/taichi_LBM3D
```

Results:

- `pytest -q`: 184 passed in 4.28s.
- Step 24 contract test: 11 passed in 0.08s.
- `git diff --check`: passed. Git reported line-ending warnings only.
- `git status --short external/taichi_LBM3D`: no output.
- `logs/step24_pytest.log`: exists.

## 14. GitHub Sync Information

Target branch: `origin/main`.

This report is part of the Step 24 commit pushed after verification. The final commit hash is reported in the completion message.

## 15. Acceptance Checklist

- [x] strict voxel_sphere 48^3 long-run engineering passes
- [x] strict voxel_sphere 48^3 long-run link_area passes
- [x] strict mesh_cube 48^3 long-run engineering passes
- [x] strict mesh_cube 48^3 long-run link_area passes
- [x] strict mesh_ellipsoid 48^3 long-run engineering passes
- [x] strict mesh_ellipsoid 48^3 long-run link_area passes
- [x] strict voxel_sphere 64^3 moving_boundary feasibility passes
- [x] strict mesh_cube 64^3 moving_boundary feasibility passes
- [x] strict mesh_cube 64^3 link_area feasibility passes
- [x] every Step 24 row writes geometry_quality_report.json
- [x] every Step 24 gate.strict == true
- [x] every Step 24 quality_pass == true
- [x] every Step 24 quality_severity == ok
- [x] mesh reports have zero boundary/degen/nonmanifold errors
- [x] voxel reports are non-empty and connected
- [x] Step 23 prefix comparison passes for overlapping rows
- [x] Step 24-only rows are explicitly marked as lacking Step 23 overlap
- [x] strict vs non-strict report comparison passes
- [x] quality report aggregation count == 9
- [x] quality report warnings == 0
- [x] quality report errors == 0
- [x] rho_min_global > 0.95
- [x] rho_max_global < 1.05
- [x] lbm_max_v_global < 0.1
- [x] mpm_min_J_global > 0
- [x] mpm_max_speed_global < 10
- [x] moving_boundary rows keep cell_force_max_norm == 0
- [x] moving_boundary rows have bb_link_count_min > 0
- [x] moving_boundary rows have active_reaction_particle_count_max > 0
- [x] link_area rows have finite bounded area_scale
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
- [x] no external/taichi_LBM3D edits
- [x] no Step 24 .vtr outputs
- [x] no Step 24 particle .npy outputs
- [x] artifact large_file_count == 0
- [x] Step 24 output total size budget passes
- [x] repo artifact_summary total_size_mb < 150
- [x] timing summary exists and is framed as workflow diagnostics only
- [x] logs/step24_pytest.log exists
- [x] pytest -q passes
- [x] Step 24 contract test passes
- [x] git diff --check passes
- [x] pre-push hook passes if push is performed
- [x] Step 24 artifacts are pushed to GitHub origin/main unless user explicitly says not to push

## 16. Decision For Step 25

Step 25 should be a controlled real geometry intake contract, starting with geometry QA, normalization, and sampling reproducibility only.

Step 25 should not claim squid swimming, production sharp-interface FSI, or final solver readiness.
