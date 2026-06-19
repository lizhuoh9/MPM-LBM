# Step 21 Imported Geometry Scale Report

## 1. Goal

Step 21 carries Step 20 synthetic imported voxel and mesh geometries to 48^3 mode validation and 64^3 feasibility.
Step 21 is synthetic imported geometry scale validation, not real squid validation.

The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 21 mesh path is not production mesh repair.

## 2. Files Created And Updated

Created:

- `baseline_tests/step21_common.py`
- `baseline_tests/run_step21_voxel_sphere_48_modes.py`
- `baseline_tests/run_step21_mesh_cube_48_modes.py`
- `baseline_tests/run_step21_mesh_ellipsoid_48_modes.py`
- `baseline_tests/run_step21_imported_geometry_64_feasibility.py`
- `baseline_tests/run_step21_imported_geometry_projection_quality.py`
- `baseline_tests/run_step21_imported_geometry_scale_summary.py`
- `baseline_tests/run_step21_artifact_manifest.py`
- `configs/step21_*.json`
- `docs/20_imported_geometry_scale_validation.md`
- `tests/test_step21_imported_geometry_scale_contract.py`

Updated:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/10_performance_memory.md`
- `docs/12_geometry_ingestion.md`
- `docs/19_geometry_import_pipeline.md`

## 3. Explicit Non-Goals

- No new FSI physics.
- No change to `PenaltyFSICoupler3D`.
- No change to `MovingBoundaryFSICoupler3D`.
- No change to `LinkAreaMovingBoundaryCoupler3D`.
- No change to the moving bounce-back formula.
- No change to LBM step formulas.
- No change to default `reaction_transfer_mode = "engineering"`.
- No real squid validation.
- No production mesh repair.
- No sparse storage.
- No `ReducedSquidFSI`.

## 4. Config Matrix

| config group | rows | n_grid | n_particles | n_lbm_steps | mpm_substeps_per_lbm_step | output |
| ------------ | ---: | -----: | ----------: | ----------: | ------------------------: | ------ |
| voxel_sphere 48 modes | 4 | 48 | 4096 | 10 | 10 | VTK off, particles off |
| mesh_cube 48 modes | 4 | 48 | 4096 | 10 | 10 | VTK off, particles off |
| mesh_ellipsoid 48 modes | 4 | 48 | 4096 | 10 | 10 | VTK off, particles off |
| imported geometry 64 feasibility | 3 required | 64 | 4096 | 5 | 5 | VTK off, particles off |

## 5. 48^3 Voxel_Sphere Mode Validation

| case | geometry_type | mode | reaction_transfer_mode | n_grid | particle_count | completed_lbm_steps | projected_mass | active_cell_count | rho_min | rho_max | lbm_max_v | mpm_min_J | cell_force_max_norm | hydro_force_max_norm | area_scale_final | stable |
| ---- | ------------- | ---- | ---------------------- | -----: | -------------: | ------------------: | -------------: | ----------------: | ------: | ------: | --------: | --------: | ------------------: | -------------------: | ---------------: | ------ |
| voxel_sphere | voxel | none | engineering | 48 | 4096 | 10 | 0.099441007 | 14151 | 1.000000000 | 1.000000358 | 0.000000000 | 0.999999583 | 0.000000000 | 0.000000000 | 1.000000000 | true |
| voxel_sphere | voxel | penalty | engineering | 48 | 4096 | 10 | 0.099441059 | 14151 | 0.999996781 | 1.000004411 | 0.000008127 | 0.999999046 | 0.000004959 | 0.000004959 | 1.000000000 | true |
| voxel_sphere | voxel | moving_boundary | engineering | 48 | 4096 | 10 | 0.099441163 | 14151 | 0.984065711 | 1.017020345 | 0.008774806 | 0.999380827 | 0.000000000 | 0.417786568 | 1.000000000 | true |
| voxel_sphere | voxel | moving_boundary | link_area_experimental | 48 | 4096 | 10 | 0.099440962 | 14151 | 0.984065592 | 1.017020583 | 0.008774805 | 0.999380827 | 0.000000000 | 0.417786896 | 0.784033895 | true |

## 6. 48^3 Mesh_Cube Mode Validation

| case | geometry_type | mode | reaction_transfer_mode | n_grid | particle_count | completed_lbm_steps | projected_mass | active_cell_count | rho_min | rho_max | lbm_max_v | mpm_min_J | cell_force_max_norm | hydro_force_max_norm | area_scale_final | stable |
| ---- | ------------- | ---- | ---------------------- | -----: | -------------: | ------------------: | -------------: | ----------------: | ------: | ------: | --------: | --------: | ------------------: | -------------------: | ---------------: | ------ |
| mesh_cube | mesh | none | engineering | 48 | 4096 | 10 | 0.747849584 | 61750 | 1.000000000 | 1.000000358 | 0.000000000 | 0.999740303 | 0.000000000 | 0.000000000 | 1.000000000 | true |
| mesh_cube | mesh | penalty | engineering | 48 | 4096 | 10 | 0.747850716 | 61750 | 0.999998987 | 1.000001669 | 0.000004472 | 0.999742627 | 0.000002972 | 0.000002972 | 1.000000000 | true |
| mesh_cube | mesh | moving_boundary | engineering | 48 | 4096 | 10 | 0.747849703 | 61747 | 0.995331407 | 1.004702330 | 0.004038826 | 0.999739230 | 0.000000000 | 0.417498738 | 1.000000000 | true |
| mesh_cube | mesh | moving_boundary | link_area_experimental | 48 | 4096 | 10 | 0.747850418 | 61747 | 0.995330989 | 1.004702330 | 0.004038866 | 0.999739289 | 0.000000000 | 0.417499155 | 0.777030170 | true |

## 7. 48^3 Mesh_Ellipsoid Mode Validation

| case | geometry_type | mode | reaction_transfer_mode | n_grid | particle_count | completed_lbm_steps | projected_mass | active_cell_count | rho_min | rho_max | lbm_max_v | mpm_min_J | cell_force_max_norm | hydro_force_max_norm | area_scale_final | stable |
| ---- | ------------- | ---- | ---------------------- | -----: | -------------: | ------------------: | -------------: | ----------------: | ------: | ------: | --------: | --------: | ------------------: | -------------------: | ---------------: | ------ |
| mesh_ellipsoid | mesh | none | engineering | 48 | 4096 | 10 | 0.133917063 | 18342 | 1.000000000 | 1.000000358 | 0.000000000 | 0.995436490 | 0.000000000 | 0.000000000 | 1.000000000 | true |
| mesh_ellipsoid | mesh | penalty | engineering | 48 | 4096 | 10 | 0.133917063 | 18342 | 0.999997139 | 1.000003695 | 0.000008149 | 0.995465934 | 0.000004957 | 0.000004957 | 1.000000000 | true |
| mesh_ellipsoid | mesh | moving_boundary | engineering | 48 | 4096 | 10 | 0.133917272 | 18342 | 0.988651395 | 1.015392900 | 0.007571429 | 0.995670736 | 0.000000000 | 0.418528587 | 1.000000000 | true |
| mesh_ellipsoid | mesh | moving_boundary | link_area_experimental | 48 | 4096 | 10 | 0.133917198 | 18342 | 0.988651931 | 1.015392065 | 0.007571500 | 0.995670855 | 0.000000000 | 0.418528497 | 0.790933192 | true |

## 8. 64^3 Imported Geometry Feasibility

| case | geometry_type | mode | reaction_transfer_mode | n_grid | particle_count | completed_lbm_steps | projected_mass | active_cell_count | rho_min | rho_max | lbm_max_v | mpm_min_J | cell_force_max_norm | hydro_force_max_norm | area_scale_final | stable |
| ---- | ------------- | ---- | ---------------------- | -----: | -------------: | ------------------: | -------------: | ----------------: | ------: | ------: | --------: | --------: | ------------------: | -------------------: | ---------------: | ------ |
| voxel_sphere | voxel | penalty | engineering | 64 | 4096 | 5 | 0.099441014 | 31116 | 0.999999583 | 1.000001311 | 0.000002625 | 0.999999166 | 0.000002491 | 0.000002491 | 1.000000000 | true |
| voxel_sphere | voxel | moving_boundary | engineering | 64 | 4096 | 5 | 0.099441148 | 31116 | 0.994373202 | 1.005661130 | 0.005045182 | 0.999895632 | 0.000000000 | 0.418163091 | 1.000000000 | true |
| mesh_cube | mesh | penalty | engineering | 64 | 4096 | 5 | 0.747853160 | 88946 | 0.999999762 | 1.000001073 | 0.000002490 | 0.999983251 | 0.000002489 | 0.000002489 | 1.000000000 | true |

## 9. Projection Quality Diagnostics

| case | geometry_type | particle_count | geometry_volume | particle_mass_sum | projected_mass | relative_mass_error | active_cell_count | solid_phi_min | solid_phi_max | occupied_count_32 | stable |
| ---- | ------------- | -------------: | --------------: | ----------------: | -------------: | ------------------: | ----------------: | ------------: | ------------: | ----------------: | ------ |
| voxel_sphere | voxel | 4096 | 0.099441056 | 0.099441059 | 0.099440970 | 0.000000899 | 14141 | 0.000000000 | 1.000000000 | 3016 | true |
| mesh_cube | mesh | 4096 | 0.747852526 | 0.747852504 | 0.747850657 | 0.000002471 | 61744 | 0.000000000 | 1.000000000 | 21952 | true |
| mesh_ellipsoid | mesh | 4096 | 0.133917160 | 0.133917153 | 0.133917212 | 0.000000445 | 18330 | 0.000000000 | 1.000000000 | 4400 | true |

## 10. Scale Summary

| metric | value |
| ------ | ----: |
| required_row_count | 18 |
| driver_row_count | 15 |
| projection_quality_row_count | 3 |
| rho_min_global | 0.984065592 |
| rho_max_global | 1.017020583 |
| lbm_max_v_global | 0.008774806 |
| mpm_min_J_global | 0.995436490 |
| mpm_max_speed_global | 0.028837694 |
| max_relative_mass_error | 0.000002471 |

## 11. Artifact Manifest Summary

The final artifact manifest is generated after pytest so it includes `logs/step21_pytest.log`. The authoritative artifact counts are in `outputs/step21_artifact_manifest/artifact_summary.json`.

| metric | value |
| ------ | ----: |
| large_file_count | 0 |

## 12. Verification Commands

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_imported_geometry_projection_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_voxel_sphere_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_mesh_cube_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_mesh_ellipsoid_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_imported_geometry_64_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_imported_geometry_scale_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
git diff --check
```

## 13. GitHub Sync Information

Target branch: `origin/main`.

This report is part of the Step 21 commit pushed after verification. The final commit hash is reported in the completion message.

## 14. Acceptance Checklist

- [x] voxel_sphere 48^3 modes baseline passes
- [x] mesh_cube 48^3 modes baseline passes
- [x] mesh_ellipsoid 48^3 modes baseline passes
- [x] imported geometry 64^3 feasibility passes
- [x] imported geometry projection quality passes
- [x] no FSI formula changes
- [x] default reaction_transfer_mode remains engineering
- [x] no real squid validation claims
- [x] no production mesh repair claims
- [x] no external/taichi_LBM3D edits
- [x] artifact large_file_count == 0
- [x] logs/step21_pytest.log exists
- [x] pytest -q passes
- [x] Git pre-push pytest hook passes
- [x] git diff --check passes
- [x] Step 21 artifacts are pushed to GitHub origin/main

## 15. Decision For Step 22

Step 21 supports proceeding to Step 22 planning. The next step should keep the Step 20/21 synthetic imported-geometry scope explicit unless a separate goal introduces real geometry under a new validation contract.
