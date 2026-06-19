# Geometry Import Pipeline

Step 20 adds a small synthetic mesh and voxel geometry import pipeline.
Step 20 is a geometry-ingestion scaffold, not real squid validation.

Imported geometry supports voxel and mesh inputs through GeometryConfig and GeometrySampler3D. The Step 20 mesh path is limited to small synthetic fixtures and is not production mesh repair.

## Scope

Step 20 adds small fixture-controlled geometry import and 32^3 smoke baselines. It does not add new FSI physics, squid actuation, squid swimming, two-phase flow, contact angle physics, sparse storage, real squid geometry validation, or final strict momentum-conserving sharp-interface FSI.

The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

## Inputs

Fixtures live in `data/geometry_fixtures/`:

| fixture | type | purpose |
| ------- | ---- | ------- |
| `voxel_sphere.npy` | voxel | 32 x 32 x 32 synthetic occupancy sphere |
| `voxel_sphere_metadata.json` | metadata | voxel domain and order metadata |
| `cube.obj` | mesh | small watertight cube mesh with 8 vertices and 12 triangles |
| `ellipsoid_proxy.obj` | mesh | small watertight ellipsoid-like mesh with 114 vertices and 224 triangles |

The fixtures are deterministic and small. They are not anatomical squid geometry.

## Configs

Geometry configs:

- `configs/step20_voxel_sphere_geometry.json`
- `configs/step20_mesh_cube_geometry.json`
- `configs/step20_mesh_ellipsoid_geometry.json`

Driver configs:

- `configs/step20_driver_voxel_penalty.json`
- `configs/step20_driver_mesh_moving_boundary.json`

The driver configs use `n_grid = 32`, `n_particles = 4096`, `n_lbm_steps = 5`, `mpm_substeps_per_lbm_step = 5`, `target_u_lbm = [0.005, 0.0, 0.0]`, `write_vtk = false`, and `write_particles = false`.

## Baselines

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_voxel_import_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_mesh_import_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_imported_geometry_projection.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_driver_imported_geometry_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_artifact_manifest.py
```

Primary outputs:

- `outputs/step20_voxel_import_sanity/`
- `outputs/step20_mesh_import_sanity/`
- `outputs/step20_imported_geometry_projection/`
- `outputs/step20_driver_imported_geometry_modes/`
- `outputs/step20_artifact_manifest/`

## Results

| case | geometry_type | particle_count | projected_mass | active_cell_count | stable |
| ---- | ------------- | -------------: | -------------: | ----------------: | ------ |
| voxel_sphere | voxel | 4096 | 0.099440910 | 5286 | true |
| mesh_cube | mesh | 4096 | 0.747851968 | 28653 | true |
| mesh_ellipsoid | mesh | 4096 | 0.133917108 | 6415 | true |

| case | mode | rho_min | rho_max | lbm_max_v | mpm_min_J | cell_force_max_norm | stable |
| ---- | ---- | ------: | ------: | --------: | --------: | ------------------: | ------ |
| voxel_sphere | none | 1.000000000 | 1.000000358 | 0.000000000 | 1.000000000 | 0.000000000 | true |
| voxel_sphere | penalty | 0.999998152 | 1.000002742 | 0.000005304 | 0.999996006 | 0.000004981 | true |
| mesh_cube | none | 1.000000000 | 1.000000358 | 0.000000000 | 0.993225098 | 0.000000000 | true |
| mesh_cube | penalty | 0.999998987 | 1.000001669 | 0.000005048 | 0.993242681 | 0.000005030 | true |
| mesh_cube | moving_boundary | 0.992932916 | 1.008372307 | 0.007739408 | 0.993218839 | 0.000000000 | true |

## Decision

Step 20 supports proceeding to Step 21: imported geometry scale validation. Step 21 should carry imported voxel/mesh cases to larger validation windows before any real squid geometry work.

## Step 21 Follow-On

Step 21 carries Step 20 synthetic imported voxel and mesh geometries to 48^3 mode validation and 64^3 feasibility.
Step 21 is synthetic imported geometry scale validation, not real squid validation.

The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Imported geometry remains limited to small synthetic voxel and mesh fixtures. The Step 21 mesh path is not production mesh repair.

Primary Step 21 outputs:

- `outputs/step21_voxel_sphere_48_modes/voxel_sphere_48_results.csv`
- `outputs/step21_mesh_cube_48_modes/mesh_cube_48_results.csv`
- `outputs/step21_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_results.csv`
- `outputs/step21_imported_geometry_64_feasibility/imported_geometry_64_results.csv`
- `outputs/step21_imported_geometry_projection_quality/projection_quality.csv`
- `outputs/step21_imported_geometry_scale_summary/step21_summary.json`
