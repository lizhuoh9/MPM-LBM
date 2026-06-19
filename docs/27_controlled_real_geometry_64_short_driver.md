# Controlled Real Geometry 64 Short Driver Feasibility

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

## Scope

Step 27 reuses the accepted Step 25 candidate descriptors and the Step 26 strict driver-ready `GeometryConfig` files. It runs only a small 64^3 short-driver coupling subset:

- mesh candidate, penalty, engineering transfer;
- mesh candidate, moving_boundary, engineering transfer;
- mesh candidate, moving_boundary, link_area_experimental transfer;
- voxel candidate, penalty, engineering transfer;
- voxel candidate, moving_boundary, engineering transfer;
- voxel candidate, moving_boundary, link_area_experimental transfer.

The `none` driver row is intentionally excluded from Step 27. Step 26 already covered `none` at 48^3 and covered 64^3 projection-only diagnostics.

## Inputs

Step 27 reuses:

- `configs/step25_candidate_smoke_mesh_descriptor.json`
- `configs/step25_candidate_smoke_voxel_descriptor.json`
- `configs/step26_real_candidate_smoke_mesh_geometry.json`
- `configs/step26_real_candidate_smoke_voxel_geometry.json`
- `outputs/step26_projection_scale_diagnostics/projection_scale_results.json`

Step 27 driver configs use `n_grid = 64`, `n_lbm_steps = 5`, `mpm_substeps_per_lbm_step = 5`, `quality_check_enabled = true`, `quality_check_strict = true`, `write_vtk = false`, and `write_particles = false`.

## Baselines

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_candidate_fingerprint_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_64_driver_mesh_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_64_driver_voxel_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_driver_projection_alignment.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_64_driver_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_step26_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step27_artifact_manifest.py
```

Primary outputs:

- `outputs/step27_candidate_fingerprint_guard/fingerprint_guard.csv`
- `outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.csv`
- `outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.csv`
- `outputs/step27_driver_projection_alignment/driver_projection_alignment.csv`
- `outputs/step27_64_driver_summary/driver_64_summary.json`
- `outputs/step27_quality_report_aggregation/quality_report_summary.json`
- `outputs/step27_step26_regression_guard/step26_regression_guard.json`
- `outputs/step27_artifact_manifest/artifact_summary.json`

## Acceptance

Every Step 27 driver row must complete at least 5 LBM steps and 25 MPM substeps, pass strict geometry quality gates, remain finite, keep density and velocity within the Step 27 short-driver bounds, and write a `geometry_quality_report.json`.

The driver projection diagnostics are compared against the accepted Step 26 64^3 projection-only rows with these tolerances:

```text
abs(projected_mass_delta) <= 5e-5
abs(active_cell_count_delta) <= 32
```

## Limitations

- no squid actuation;
- no squid swimming;
- no new FSI physics;
- no production sharp-interface FSI validation;
- no production mesh repair;
- no automatic remeshing;
- no two-phase flow;
- no contact angle physics;
- no sparse-storage implementation;
- no edits to `external/taichi_LBM3D`;
- no large raw real geometry or scan data committed.

## Decision For Step 28

If Step 27 passes, Step 28 should stay conservative and compare engineering versus link-area transfer at 64^3 with additional force/reaction diagnostics and a stability envelope. It should not jump to actuation or swimming.
