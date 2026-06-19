# Step 20 Geometry Import Report

## 1. Goal

Step 20 adds a small synthetic mesh and voxel geometry import pipeline.
Step 20 is a geometry-ingestion scaffold, not real squid validation.

The goal was to add artifact-controlled imported geometry support for small voxel and mesh fixtures, integrate it through the existing `GeometryConfig`, `GeometrySampler3D`, and `FSIDriver3D` paths, and validate 32^3 imported-geometry smoke baselines without adding new FSI physics.

## 2. Files Created And Updated

Created:

| path | purpose |
| ---- | ------- |
| `src/voxel_io.py` | small `.npy` voxel occupancy loading, saving, and stats |
| `src/mesh_io.py` | minimal ASCII OBJ loading, writing, triangulation, and normalization |
| `src/geometry_import.py` | `ImportedGeometrySampler3D` for voxel and mesh inputs |
| `data/geometry_fixtures/` | small synthetic voxel and OBJ fixtures |
| `configs/step20_*` | Step 20 geometry and driver configs |
| `baseline_tests/run_step20_*` | Step 20 baseline runners |
| `baseline_tests/step20_common.py` | shared Step 20 baseline helpers |
| `docs/19_geometry_import_pipeline.md` | Step 20 user-facing geometry import notes |
| `tests/test_step20_geometry_import_contract.py` | Step 20 artifact contract test |

Updated:

| path | update |
| ---- | ------ |
| `src/geometry_config.py` | adds `voxel` and `mesh` config fields and validation |
| `src/geometry.py` | delegates imported geometry to `ImportedGeometrySampler3D` |
| `src/__init__.py` | exports Step 20 import utilities |
| `README.md` | documents Step 20 scope and commands |
| `docs/08_roadmap.md` | marks Step 20 complete and Step 21 proposed |
| `docs/09_api_reference.md` | documents imported geometry API |
| `docs/12_geometry_ingestion.md` | extends geometry ingestion docs |
| `docs/18_link_area_long_run.md` | updates Step 19 decision now that Step 20 exists |

## 3. Explicit Non-Goals

Step 20 did not add or change FSI physics. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 20 does not implement two-phase flow, contact angle physics, squid actuation, squid swimming, sparse storage, ReducedSquidFSI, real squid validation, or final strict momentum-conserving sharp-interface FSI.

Imported geometry supports voxel and mesh inputs through GeometryConfig and GeometrySampler3D. The Step 20 mesh path is limited to small synthetic fixtures and is not production mesh repair.

## 4. GeometryConfig And Sampler Integration

`VALID_GEOMETRY_TYPES` now includes:

```text
box
ellipsoid
squid_proxy
voxel
mesh
```

`GeometryConfig` now supports:

```text
geometry_file
metadata_file
normalize_to_domain
preserve_aspect_ratio
padding
voxel_threshold
voxel_spacing
mesh_inside_method
mesh_voxel_resolution
```

`GeometrySampler3D` keeps the existing procedural paths and caches an `ImportedGeometrySampler3D` helper for `voxel` and `mesh`. Imported geometry still reaches MPM through `MPMSolid3D.init_from_numpy()` and reaches LBM through the existing `MPMToLBMProjector3D.project()` path.

`FSIDriver3D` still uses the existing `geometry_type` and `geometry_config_path` flow. No separate driver path was added.

## 5. Voxel Import Sanity Result

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_voxel_import_sanity.py
```

Result:

| case | geometry_type | particle_count | occupied_count | geometry_volume | stable |
| ---- | ------------- | -------------: | -------------: | --------------: | ------ |
| voxel_sphere | voxel | 4096 | 3016 | 0.099441056 | true |

Outputs:

- `outputs/step20_voxel_import_sanity/particles_x.npy`
- `outputs/step20_voxel_import_sanity/particle_vol0.npy`
- `outputs/step20_voxel_import_sanity/particle_mass.npy`
- `outputs/step20_voxel_import_sanity/geometry_occupancy.npy`
- `outputs/step20_voxel_import_sanity/import_stats.json`

## 6. Mesh Import Sanity Result

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_mesh_import_sanity.py
```

Result:

| case | geometry_type | vertices | faces | particle_count | occupied_count | geometry_volume | stable |
| ---- | ------------- | -------: | ----: | -------------: | -------------: | --------------: | ------ |
| mesh_cube | mesh | 8 | 12 | 4096 | 21952 | 0.747852526 | true |
| mesh_ellipsoid | mesh | 114 | 224 | 4096 | 4400 | 0.133917160 | true |

Outputs:

- `outputs/step20_mesh_import_sanity/cube_particles_x.npy`
- `outputs/step20_mesh_import_sanity/ellipsoid_particles_x.npy`
- `outputs/step20_mesh_import_sanity/mesh_import_stats.json`

## 7. Imported Geometry Projection Result

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_imported_geometry_projection.py
```

Result:

| case | geometry_type | particle_count | occupied_count | projected_mass | active_cell_count | rho_min | rho_max | lbm_max_v | mpm_min_J | cell_force_max_norm | stable |
| ---- | ------------- | -------------: | -------------: | -------------: | ----------------: | ------: | ------: | --------: | --------: | ------------------: | ------ |
| voxel_sphere | voxel | 4096 | 3016 | 0.099440910 | 5286 | n/a | n/a | n/a | n/a | 0.000000000 | true |
| mesh_cube | mesh | 4096 | 21952 | 0.747851968 | 28653 | n/a | n/a | n/a | n/a | 0.000000000 | true |
| mesh_ellipsoid | mesh | 4096 | 4400 | 0.133917108 | 6415 | n/a | n/a | n/a | n/a | 0.000000000 | true |

Projection rows are diagnostic-only. `cell_force_max_norm == 0` and `hydro_force_max_norm == 0` for all projection rows.

## 8. Driver Imported Geometry Modes Result

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_driver_imported_geometry_modes.py
```

Result:

| case | geometry_type | mode | particle_count | occupied_count | projected_mass | active_cell_count | rho_min | rho_max | lbm_max_v | mpm_min_J | cell_force_max_norm | stable |
| ---- | ------------- | ---- | -------------: | -------------: | -------------: | ----------------: | ------: | ------: | --------: | --------: | ------------------: | ------ |
| voxel_sphere | voxel | none | 4096 | 3016 | 0.099440977 | 5294 | 1.000000000 | 1.000000358 | 0.000000000 | 1.000000000 | 0.000000000 | true |
| voxel_sphere | voxel | penalty | 4096 | 3016 | 0.099441022 | 5294 | 0.999998152 | 1.000002742 | 0.000005304 | 0.999996006 | 0.000004981 | true |
| mesh_cube | mesh | none | 4096 | 21952 | 0.747852564 | 28646 | 1.000000000 | 1.000000358 | 0.000000000 | 0.993225098 | 0.000000000 | true |
| mesh_cube | mesh | penalty | 4096 | 21952 | 0.747853935 | 28647 | 0.999998987 | 1.000001669 | 0.000005048 | 0.993242681 | 0.000005030 | true |
| mesh_cube | mesh | moving_boundary | 4096 | 21952 | 0.747853220 | 28646 | 0.992932916 | 1.008372307 | 0.007739408 | 0.993218839 | 0.000000000 | true |

The moving_boundary row keeps `cell_force_max_norm == 0`. Penalty rows have finite nonzero `cell_force_max_norm`.

## 9. Artifact Manifest Summary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_artifact_manifest.py
```

Final result after `logs/step20_pytest.log` was generated:

| file_count | total_size_bytes | total_size_mb | large_file_count |
| ---------: | ---------------: | ------------: | ---------------: |
| 843 | 107374410 | 102.400217 | 0 |

## 10. Verification Commands

Baseline commands:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_voxel_import_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_mesh_import_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_imported_geometry_projection.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_driver_imported_geometry_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_artifact_manifest.py
```

Full validation commands:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
git diff --check
git status --short external/taichi_LBM3D
```

## 11. GitHub Sync Information

Target branch:

```text
origin/main
```

The Step 20 source, configs, fixtures, docs, logs, outputs, report, and contract test are included in the Step 20 final commit and pushed to GitHub `origin/main`.

## 12. Acceptance Checklist

- [x] geometry_type supports voxel
- [x] geometry_type supports mesh
- [x] src/voxel_io.py exists
- [x] src/mesh_io.py exists
- [x] src/geometry_import.py exists
- [x] voxel_sphere.npy exists and is small
- [x] cube.obj exists and is small
- [x] ellipsoid_proxy.obj exists and is small
- [x] voxel import sanity passes
- [x] mesh import sanity passes
- [x] imported geometry projection passes
- [x] driver imported geometry modes pass
- [x] imported geometry particle positions are finite
- [x] imported geometry particle positions are inside [0, 1]^3
- [x] imported geometry vol0 values are positive
- [x] imported geometry mass values are positive
- [x] projected_mass > 0 for projection rows
- [x] active_cell_count > 0 for projection rows
- [x] rho_min > 0.95 for required stable driver rows
- [x] rho_max < 1.05 for required stable driver rows
- [x] lbm_max_v < 0.1 for required stable driver rows
- [x] mpm_min_J > 0 for required stable driver rows
- [x] no NaN
- [x] no Inf
- [x] no FSI formula changes
- [x] default reaction_transfer_mode remains engineering
- [x] link_area_experimental remains opt-in
- [x] no two-phase flow
- [x] no contact angle physics
- [x] no real squid validation claims
- [x] no squid swimming validation claims
- [x] no production mesh repair claims
- [x] no sparse storage implementation
- [x] no ReducedSquidFSI
- [x] no external/taichi_LBM3D edits
- [x] artifact large_file_count == 0
- [x] docs/19_geometry_import_pipeline.md exists
- [x] STEP20_GEOMETRY_IMPORT_REPORT.md complete
- [x] tests/test_step20_geometry_import_contract.py exists
- [x] logs/step20_pytest.log exists
- [x] pytest -q passes
- [x] Git pre-push pytest hook passes
- [x] git diff --check passes
- [x] Step 20 artifacts are pushed to GitHub origin/main

## 13. Decision For Step 21

Step 20 supports proceeding to Step 21: imported geometry scale validation.

Recommended Step 21 scope:

- carry imported voxel/mesh cases to larger validation windows;
- compare none, penalty, moving_boundary engineering, and optional link_area_experimental modes;
- keep real squid geometry out of scope until imported geometry quality checks and artifact policy remain stable at larger scale.
