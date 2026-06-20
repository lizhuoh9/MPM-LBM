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

## Step 22 Follow-On

Step 22 adds diagnostic quality checks for imported mesh and voxel geometry.
Step 22 is a geometry QA and import robustness layer, not real squid validation.

The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 22 mesh path is not production mesh repair or automatic remeshing.

Primary Step 22 outputs:

- `outputs/step22_mesh_quality_sanity/mesh_quality_results.csv`
- `outputs/step22_voxel_quality_sanity/voxel_quality_results.csv`
- `outputs/step22_bad_geometry_failure_checks/bad_geometry_results.csv`
- `outputs/step22_sampling_resolution_sensitivity/resolution_sensitivity.csv`
- `outputs/step22_driver_quality_gate_smoke/quality_gate_driver_results.csv`
- `outputs/step22_artifact_manifest/artifact_summary.json`

## Step 23 Follow-On

Step 23 repeats imported geometry scale validation with quality_check_enabled=true.
Step 23 uses quality_check_strict=false for scale validation.
Step 23 is quality-gated synthetic imported geometry validation, not real squid validation.

The default quality_check_enabled remains false. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 23 mesh path is not production mesh repair or automatic remeshing.

Primary Step 23 outputs:

- `outputs/step23_quality_gated_voxel_sphere_48_modes/voxel_sphere_48_quality_gated_results.csv`
- `outputs/step23_quality_gated_mesh_cube_48_modes/mesh_cube_48_quality_gated_results.csv`
- `outputs/step23_quality_gated_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_quality_gated_results.csv`
- `outputs/step23_quality_gated_imported_geometry_64_feasibility/imported_geometry_64_quality_gated_results.csv`
- `outputs/step23_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step23_step21_vs_quality_gated_comparison/step21_vs_step23_comparison.csv`
- `outputs/step23_artifact_manifest/artifact_summary.json`

## Step 24 Follow-On

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

Primary Step 24 outputs:

- `outputs/step24_strict_voxel_sphere_48_long/voxel_sphere_48_strict_long_results.csv`
- `outputs/step24_strict_mesh_cube_48_long/mesh_cube_48_strict_long_results.csv`
- `outputs/step24_strict_mesh_ellipsoid_48_long/mesh_ellipsoid_48_strict_long_results.csv`
- `outputs/step24_strict_imported_geometry_64_feasibility/imported_geometry_64_strict_feasibility_results.csv`
- `outputs/step24_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step24_artifact_manifest/artifact_summary.json`

## Step 25 Follow-On

Step 25 is controlled real geometry intake, not real squid validation.
Step 25 performs geometry QA, normalization, fingerprinting, sampling reproducibility, and projection-only smoke diagnostics.
Step 25 does not implement squid swimming.
Step 25 does not implement squid actuation.
Step 25 does not implement new FSI physics.
Step 25 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Candidate intake does not perform production mesh repair or automatic remeshing.
Raw large real geometry files and scan data are not committed.

Primary Step 25 outputs:

- `outputs/step25_candidate_manifest/candidate_manifest.csv`
- `outputs/step25_real_geometry_intake_smoke/intake_smoke_summary.csv`
- `outputs/step25_projection_smoke/projection_smoke_results.csv`

## Step 26 Follow-On

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

Primary Step 26 outputs:

- `outputs/step26_candidate_fingerprint_guard/fingerprint_guard.csv`
- `outputs/step26_generated_geometry_configs/generated_geometry_configs.csv`
- `outputs/step26_projection_scale_diagnostics/projection_scale_results.csv`
- `outputs/step26_step25_projection_regression/step25_projection_regression.csv`
- `outputs/step26_short_driver_summary/short_driver_summary.json`
- `outputs/step26_quality_report_aggregation/quality_report_summary.json`
- `outputs/step26_artifact_manifest/artifact_summary.json`
- `outputs/step25_normalization_reports/normalization_summary.csv`
- `outputs/step25_sampling_reproducibility/sampling_reproducibility.csv`
- `outputs/step25_projection_smoke/projection_smoke_results.csv`
- `outputs/step25_artifact_manifest/artifact_summary.json`

## Step 27 Follow-On

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

Primary Step 27 outputs:

- `outputs/step27_candidate_fingerprint_guard/fingerprint_guard.csv`
- `outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.csv`
- `outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.csv`
- `outputs/step27_driver_projection_alignment/driver_projection_alignment.csv`
- `outputs/step27_64_driver_summary/driver_64_summary.json`
- `outputs/step27_quality_report_aggregation/quality_report_summary.json`
- `outputs/step27_artifact_manifest/artifact_summary.json`

## Step 28 Transfer Diagnostics

Step 28 is controlled real geometry 64^3 transfer diagnostics.
Step 28 compares engineering and link_area_experimental transfer diagnostically.
Step 28 is not real squid validation.
Step 28 does not implement squid actuation.
Step 28 does not implement squid swimming.
Step 28 does not implement new FSI physics.
Step 28 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Primary Step 28 outputs:

- `outputs/step28_candidate_fingerprint_guard/fingerprint_guard.csv`
- `outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.csv`
- `outputs/step28_engineering_vs_link_area_comparison/engineering_vs_link_area.csv`
- `outputs/step28_force_reaction_diagnostics/force_reaction_diagnostics.csv`
- `outputs/step28_area_scale_envelope/area_scale_envelope.csv`
- `outputs/step28_step27_prefix_regression/step27_prefix_regression.csv`
- `outputs/step28_quality_report_aggregation/quality_report_summary.json`
- `outputs/step28_artifact_manifest/artifact_summary.json`
