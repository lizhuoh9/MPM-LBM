# Imported Geometry Scale Validation

Step 21 carries Step 20 synthetic imported voxel and mesh geometries to 48^3 mode validation and 64^3 feasibility.
Step 21 is synthetic imported geometry scale validation, not real squid validation.

The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 21 mesh path is not production mesh repair.

## Scope

Step 21 validates the Step 20 imported geometry scaffold at larger dense-grid sizes. It does not add FSI physics, squid actuation, squid swimming, two-phase flow, contact angle physics, sparse storage, real squid geometry validation, production mesh repair, or final strict momentum-conserving sharp-interface FSI.

## Config Matrix

| group | configs | n_grid | steps | substeps | output policy |
| ----- | ------- | -----: | ----: | -------: | ------------- |
| voxel_sphere 48 modes | none, penalty, moving_boundary engineering, moving_boundary link_area_experimental | 48 | 10 | 10 | no VTK, no particles |
| mesh_cube 48 modes | none, penalty, moving_boundary engineering, moving_boundary link_area_experimental | 48 | 10 | 10 | no VTK, no particles |
| mesh_ellipsoid 48 modes | none, penalty, moving_boundary engineering, moving_boundary link_area_experimental | 48 | 10 | 10 | no VTK, no particles |
| imported geometry 64 feasibility | voxel_sphere penalty, voxel_sphere moving_boundary engineering, mesh_cube penalty | 64 | 5 | 5 | no VTK, no particles |

## Baselines

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_voxel_sphere_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_mesh_cube_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_mesh_ellipsoid_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_imported_geometry_64_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_imported_geometry_projection_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_imported_geometry_scale_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step21_artifact_manifest.py
```

Primary outputs:

- `outputs/step21_voxel_sphere_48_modes/voxel_sphere_48_results.csv`
- `outputs/step21_mesh_cube_48_modes/mesh_cube_48_results.csv`
- `outputs/step21_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_results.csv`
- `outputs/step21_imported_geometry_64_feasibility/imported_geometry_64_results.csv`
- `outputs/step21_imported_geometry_projection_quality/projection_quality.csv`
- `outputs/step21_imported_geometry_scale_summary/step21_summary.json`
- `outputs/step21_artifact_manifest/artifact_summary.json`

## 48^3 Mode Results

| case | mode | transfer | rho_min | rho_max | lbm_max_v | mpm_min_J | projected_mass | active_cell_count | area_scale_final | stable |
| ---- | ---- | -------- | ------: | ------: | --------: | --------: | -------------: | ----------------: | ---------------: | ------ |
| voxel_sphere | none | engineering | 1.000000000 | 1.000000358 | 0.000000000 | 0.999999583 | 0.099441007 | 14151 | 1.000000000 | true |
| voxel_sphere | penalty | engineering | 0.999996781 | 1.000004411 | 0.000008127 | 0.999999046 | 0.099441059 | 14151 | 1.000000000 | true |
| voxel_sphere | moving_boundary | engineering | 0.984065711 | 1.017020345 | 0.008774806 | 0.999380827 | 0.099441163 | 14151 | 1.000000000 | true |
| voxel_sphere | moving_boundary | link_area_experimental | 0.984065592 | 1.017020583 | 0.008774805 | 0.999380827 | 0.099440962 | 14151 | 0.784033895 | true |
| mesh_cube | none | engineering | 1.000000000 | 1.000000358 | 0.000000000 | 0.999740303 | 0.747849584 | 61750 | 1.000000000 | true |
| mesh_cube | penalty | engineering | 0.999998987 | 1.000001669 | 0.000004472 | 0.999742627 | 0.747850716 | 61750 | 1.000000000 | true |
| mesh_cube | moving_boundary | engineering | 0.995331407 | 1.004702330 | 0.004038826 | 0.999739230 | 0.747849703 | 61747 | 1.000000000 | true |
| mesh_cube | moving_boundary | link_area_experimental | 0.995330989 | 1.004702330 | 0.004038866 | 0.999739289 | 0.747850418 | 61747 | 0.777030170 | true |
| mesh_ellipsoid | none | engineering | 1.000000000 | 1.000000358 | 0.000000000 | 0.995436490 | 0.133917063 | 18342 | 1.000000000 | true |
| mesh_ellipsoid | penalty | engineering | 0.999997139 | 1.000003695 | 0.000008149 | 0.995465934 | 0.133917063 | 18342 | 1.000000000 | true |
| mesh_ellipsoid | moving_boundary | engineering | 0.988651395 | 1.015392900 | 0.007571429 | 0.995670736 | 0.133917272 | 18342 | 1.000000000 | true |
| mesh_ellipsoid | moving_boundary | link_area_experimental | 0.988651931 | 1.015392065 | 0.007571500 | 0.995670855 | 0.133917198 | 18342 | 0.790933192 | true |

## 64^3 Feasibility Results

| case | mode | transfer | rho_min | rho_max | lbm_max_v | mpm_min_J | projected_mass | active_cell_count | stable |
| ---- | ---- | -------- | ------: | ------: | --------: | --------: | -------------: | ----------------: | ------ |
| voxel_sphere | penalty | engineering | 0.999999583 | 1.000001311 | 0.000002625 | 0.999999166 | 0.099441014 | 31116 | true |
| voxel_sphere | moving_boundary | engineering | 0.994373202 | 1.005661130 | 0.005045182 | 0.999895632 | 0.099441148 | 31116 | true |
| mesh_cube | penalty | engineering | 0.999999762 | 1.000001073 | 0.000002490 | 0.999983251 | 0.747853160 | 88946 | true |

## Projection Quality

| case | geometry_type | geometry_volume | projected_mass | relative_mass_error | active_cell_count | occupied_fraction_32 | stable |
| ---- | ------------- | --------------: | -------------: | ------------------: | ----------------: | -------------------: | ------ |
| voxel_sphere | voxel | 0.099441056 | 0.099440970 | 0.000000899 | 14141 | 0.092041016 | true |
| mesh_cube | mesh | 0.747852526 | 0.747850657 | 0.000002471 | 61744 | 0.669921875 | true |
| mesh_ellipsoid | mesh | 0.133917160 | 0.133917212 | 0.000000445 | 18330 | 0.134277344 | true |

## Decision

Step 21 supports proceeding to Step 22 planning with the same constraints: no real squid validation claim, no production mesh repair claim, and no final strict momentum-conserving sharp-interface FSI claim.

## Step 22 Follow-On

Step 22 adds diagnostic quality checks for imported mesh and voxel geometry.
Step 22 is a geometry QA and import robustness layer, not real squid validation.

The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 22 mesh path is not production mesh repair or automatic remeshing.

Step 22 validates the import path with mesh quality sanity, voxel quality sanity, strict expected-failure bad fixtures, sampling resolution sensitivity diagnostics, and optional `FSIDriver3D` geometry quality reports. It does not add new FSI physics or change Step 21 coupling behavior.
