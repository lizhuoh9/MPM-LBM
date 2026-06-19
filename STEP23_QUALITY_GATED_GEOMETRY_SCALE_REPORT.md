# Step 23 Quality-Gated Imported Geometry Scale Report

## 1. Goal

Step 23 repeats imported geometry scale validation with quality_check_enabled=true.
Step 23 uses quality_check_strict=false for scale validation.
Step 23 is quality-gated synthetic imported geometry validation, not real squid validation.

The default quality_check_enabled remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 23 mesh path is not production mesh repair or automatic remeshing.

Step 23 reruns the Step 21 imported geometry scale matrix with Step 22 quality report generation enabled. Every required driver row must write `geometry_quality_report.json`, pass the non-strict quality gate, and remain stable.

## 2. Files Created And Updated

Created:

- `STEP23_QUALITY_GATED_GEOMETRY_SCALE_GOAL.md`
- `baseline_tests/step23_common.py`
- `baseline_tests/run_step23_quality_gated_voxel_sphere_48_modes.py`
- `baseline_tests/run_step23_quality_gated_mesh_cube_48_modes.py`
- `baseline_tests/run_step23_quality_gated_mesh_ellipsoid_48_modes.py`
- `baseline_tests/run_step23_quality_gated_imported_geometry_64_feasibility.py`
- `baseline_tests/run_step23_quality_report_aggregation.py`
- `baseline_tests/run_step23_step21_vs_quality_gated_comparison.py`
- `baseline_tests/run_step23_artifact_manifest.py`
- `configs/step23_quality_gated_*.json`
- `docs/22_quality_gated_imported_geometry_validation.md`
- `tests/test_step23_quality_gated_geometry_scale_contract.py`

Updated:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/12_geometry_ingestion.md`
- `docs/19_geometry_import_pipeline.md`
- `docs/20_imported_geometry_scale_validation.md`
- `docs/21_geometry_quality_checks.md`

## 3. Explicit Non-Goals

- No new FSI physics.
- No change to `PenaltyFSICoupler3D`.
- No change to `MovingBoundaryFSICoupler3D`.
- No change to `LinkAreaMovingBoundaryCoupler3D`.
- No change to the moving bounce-back formula.
- No change to LBM step formulas.
- No change to default `reaction_transfer_mode = "engineering"`.
- No change to default `quality_check_enabled = false`.
- No strict quality gate for scale validation.
- No real squid validation.
- No squid actuation or swimming validation.
- No production mesh repair.
- No automatic remeshing.
- No two-phase flow.
- No contact angle physics.
- No sparse storage.
- No `ReducedSquidFSI`.
- No edits to `external/taichi_LBM3D`.

## 4. 48^3 Voxel_Sphere Quality-Gated Modes

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_voxel_sphere_48_modes.py
```

Artifact: `outputs/step23_quality_gated_voxel_sphere_48_modes/voxel_sphere_48_quality_gated_results.csv`.

| case | geometry_type | mode | reaction_transfer_mode | n_grid | quality_check_enabled | quality_check_strict | quality_pass | quality_severity | rho_min | rho_max | lbm_max_v | mpm_min_J | projected_mass | active_cell_count | stable |
| ---- | ------------- | ---- | ---------------------- | -----: | --------------------- | -------------------- | ------------ | ---------------- | ------: | ------: | --------: | --------: | -------------: | ----------------: | ------ |
| voxel_sphere | voxel | none | engineering | 48 | true | false | true | ok | 1.000000000 | 1.000000358 | 0.000000000 | 0.999999583 | 0.099441089 | 14151 | true |
| voxel_sphere | voxel | penalty | engineering | 48 | true | false | true | ok | 0.999996781 | 1.000004411 | 0.000008081 | 0.999999166 | 0.099441059 | 14151 | true |
| voxel_sphere | voxel | moving_boundary | engineering | 48 | true | false | true | ok | 0.984066367 | 1.017020345 | 0.008774810 | 0.999380767 | 0.099441111 | 14151 | true |
| voxel_sphere | voxel | moving_boundary | link_area_experimental | 48 | true | false | true | ok | 0.984065890 | 1.017020583 | 0.008774685 | 0.999380648 | 0.099441066 | 14151 | true |

Every row wrote `geometry_quality_report.json` and passed the non-strict voxel quality gate.

## 5. 48^3 Mesh_Cube Quality-Gated Modes

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_mesh_cube_48_modes.py
```

Artifact: `outputs/step23_quality_gated_mesh_cube_48_modes/mesh_cube_48_quality_gated_results.csv`.

| case | geometry_type | mode | reaction_transfer_mode | n_grid | quality_check_enabled | quality_check_strict | quality_pass | quality_severity | rho_min | rho_max | lbm_max_v | mpm_min_J | projected_mass | active_cell_count | stable |
| ---- | ------------- | ---- | ---------------------- | -----: | --------------------- | -------------------- | ------------ | ---------------- | ------: | ------: | --------: | --------: | -------------: | ----------------: | ------ |
| mesh_cube | mesh | none | engineering | 48 | true | false | true | ok | 1.000000000 | 1.000000358 | 0.000000000 | 0.999740541 | 0.747850001 | 61750 | true |
| mesh_cube | mesh | penalty | engineering | 48 | true | false | true | ok | 0.999999106 | 1.000001550 | 0.000004455 | 0.999742746 | 0.747851074 | 61750 | true |
| mesh_cube | mesh | moving_boundary | engineering | 48 | true | false | true | ok | 0.995331049 | 1.004702449 | 0.004038997 | 0.999739170 | 0.747850180 | 61747 | true |
| mesh_cube | mesh | moving_boundary | link_area_experimental | 48 | true | false | true | ok | 0.995330513 | 1.004701972 | 0.004038705 | 0.999739230 | 0.747852504 | 61747 | true |

Every mesh_cube quality report passed and had no quality-gate errors.

## 6. 48^3 Mesh_Ellipsoid Quality-Gated Modes

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_mesh_ellipsoid_48_modes.py
```

Artifact: `outputs/step23_quality_gated_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_quality_gated_results.csv`.

| case | geometry_type | mode | reaction_transfer_mode | n_grid | quality_check_enabled | quality_check_strict | quality_pass | quality_severity | rho_min | rho_max | lbm_max_v | mpm_min_J | projected_mass | active_cell_count | stable |
| ---- | ------------- | ---- | ---------------------- | -----: | --------------------- | -------------------- | ------------ | ---------------- | ------: | ------: | --------: | --------: | -------------: | ----------------: | ------ |
| mesh_ellipsoid | mesh | none | engineering | 48 | true | false | true | ok | 1.000000000 | 1.000000358 | 0.000000000 | 0.995436192 | 0.133917123 | 18342 | true |
| mesh_ellipsoid | mesh | penalty | engineering | 48 | true | false | true | ok | 0.999997258 | 1.000003695 | 0.000008122 | 0.995465934 | 0.133917108 | 18342 | true |
| mesh_ellipsoid | mesh | moving_boundary | engineering | 48 | true | false | true | ok | 0.988651514 | 1.015393019 | 0.007571541 | 0.995670676 | 0.133917063 | 18342 | true |
| mesh_ellipsoid | mesh | moving_boundary | link_area_experimental | 48 | true | false | true | ok | 0.988650858 | 1.015392661 | 0.007571492 | 0.995670736 | 0.133917049 | 18342 | true |

Every mesh_ellipsoid quality report passed and had no quality-gate errors.

## 7. 64^3 Quality-Gated Feasibility

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_imported_geometry_64_feasibility.py
```

Artifact: `outputs/step23_quality_gated_imported_geometry_64_feasibility/imported_geometry_64_quality_gated_results.csv`.

| case | geometry_type | mode | reaction_transfer_mode | n_grid | quality_check_enabled | quality_check_strict | quality_pass | quality_severity | rho_min | rho_max | lbm_max_v | mpm_min_J | projected_mass | active_cell_count | stable |
| ---- | ------------- | ---- | ---------------------- | -----: | --------------------- | -------------------- | ------------ | ---------------- | ------: | ------: | --------: | --------: | -------------: | ----------------: | ------ |
| voxel_sphere | voxel | penalty | engineering | 64 | true | false | true | ok | 0.999999583 | 1.000001311 | 0.000002618 | 0.999999344 | 0.099441171 | 31116 | true |
| voxel_sphere | voxel | moving_boundary | engineering | 64 | true | false | true | ok | 0.994373262 | 1.005661130 | 0.005045207 | 0.999895573 | 0.099441014 | 31116 | true |
| mesh_cube | mesh | penalty | engineering | 64 | true | false | true | ok | 0.999999762 | 1.000001073 | 0.000002490 | 0.999983251 | 0.747851431 | 88946 | true |

All required 64^3 rows were stable and wrote quality reports.

## 8. Quality Report Aggregation

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_report_aggregation.py
```

Artifacts:

- `outputs/step23_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step23_quality_report_aggregation/quality_report_summary.json`

| metric | value |
| ------ | ----: |
| quality_report_count | 15 |
| pass_count | 15 |
| error_count | 0 |
| warning_count | 0 |
| mesh_row_count | 9 |
| voxel_row_count | 6 |

## 9. Step 21 Vs Step 23 Comparison

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_step21_vs_quality_gated_comparison.py
```

Artifacts:

- `outputs/step23_step21_vs_quality_gated_comparison/step21_vs_step23_comparison.csv`
- `outputs/step23_step21_vs_quality_gated_comparison/step21_vs_step23_comparison.json`

| metric | value |
| ------ | ----: |
| required_comparable_row_count | 15 |
| stable_both_count | 15 |
| max_abs_rho_min_delta | 0.000001073 |
| max_abs_rho_max_delta | 0.000000596 |
| max_abs_lbm_max_v_delta | 0.000000171 |
| max_abs_mpm_min_J_delta | 0.000000298 |
| max_abs_projected_mass_delta | 0.000002086 |
| max_abs_active_cell_count_delta | 0 |

The comparison is finite and stable. Bitwise identity is not required.

## 10. Artifact Manifest Summary

The final artifact manifest is generated after pytest so it includes `logs/step23_pytest.log`. The authoritative artifact counts are in `outputs/step23_artifact_manifest/artifact_summary.json`.

| metric | value |
| ------ | ----: |
| large_file_count | 0 |

## 11. Verification Commands

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_voxel_sphere_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_mesh_cube_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_mesh_ellipsoid_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_imported_geometry_64_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_step21_vs_quality_gated_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step23_quality_gated_geometry_scale_contract.py -q
git diff --check
```

## 12. GitHub Sync Information

Target branch: `origin/main`.

This report is part of the Step 23 commit pushed after verification. The final commit hash is reported in the completion message.

## 13. Acceptance Checklist

- [x] quality-gated voxel_sphere 48^3 modes pass
- [x] quality-gated mesh_cube 48^3 modes pass
- [x] quality-gated mesh_ellipsoid 48^3 modes pass
- [x] quality-gated imported geometry 64^3 feasibility passes
- [x] every required driver row has geometry_quality_report.json
- [x] all required quality reports pass
- [x] no required quality report severity == error
- [x] Step 21 vs Step 23 comparison passes
- [x] quality report aggregation passes
- [x] default quality_check_enabled remains false
- [x] quality_check_strict remains false for scale validation
- [x] no FSI formula changes
- [x] default reaction_transfer_mode remains engineering
- [x] no production mesh repair claims
- [x] no automatic remeshing claims
- [x] no real squid validation claims
- [x] no external/taichi_LBM3D edits
- [x] artifact large_file_count == 0
- [x] logs/step23_pytest.log exists
- [x] pytest -q passes
- [x] Git pre-push pytest hook passes
- [x] git diff --check passes
- [x] Step 23 artifacts are pushed to GitHub origin/main

## 14. Decision For Step 24

Step 23 supports proceeding to Step 24 planning. The next step should keep the synthetic imported-geometry scope explicit unless a separate contract introduces real geometry intake, and strict quality-gated long-run validation should remain a safer bridge before real geometry work.
