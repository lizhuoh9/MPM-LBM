# Controlled Real Geometry Short Feasibility

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

## Scope

Step 26 starts from the accepted Step 25 candidate descriptors and adds a guarded feasibility layer:

- fingerprint guard against the accepted Step 25 manifest;
- descriptor-to-driver `GeometryConfig` conversion;
- projection-only scale diagnostics at 32^3, 48^3, and 64^3;
- Step 25 projection regression for the 32^3 rows;
- very short 48^3 `FSIDriver3D` rows for `none`, `penalty`, `moving_boundary` engineering, and `moving_boundary` link-area transfer;
- strict `geometry_quality_report.json` generation for every driver row.

The driver rows are intentionally short: `n_lbm_steps = 5` and `mpm_substeps_per_lbm_step = 5`. They test whether the accepted controlled candidates can pass strict quality gates and enter existing driver modes without NaN, Inf, or obvious stability failures.

## Inputs

Step 26 reuses the Step 25 descriptors:

- `configs/step25_candidate_smoke_mesh_descriptor.json`
- `configs/step25_candidate_smoke_voxel_descriptor.json`

Generated driver-ready geometry configs:

- `configs/step26_real_candidate_smoke_mesh_geometry.json`
- `configs/step26_real_candidate_smoke_voxel_geometry.json`

Generated driver configs keep VTK and particle output disabled.

## APIs

Step 26 adds:

- `src/geometry_driver_config.py`
  - `geometry_config_payload_from_candidate_descriptor`
  - `write_geometry_config_from_descriptor`
  - `driver_config_payload_for_candidate`
- `src/real_geometry_feasibility.py`
  - `run_projection_only_scale_case`
  - `run_short_driver_case`
  - `summarize_short_driver_diagnostics`
  - `compare_step25_projection_smoke`

These helpers are orchestration and reporting helpers. They do not change solver, coupling, LBM, MPM, moving-boundary, or projection formulas.

## Baselines

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_candidate_fingerprint_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_generate_driver_geometry_configs.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_projection_scale_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_step25_projection_regression.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_short_driver_mesh_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_short_driver_voxel_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_short_driver_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_step25_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step26_artifact_manifest.py
```

Primary outputs:

- `outputs/step26_candidate_fingerprint_guard/fingerprint_guard.csv`
- `outputs/step26_generated_geometry_configs/generated_geometry_configs.csv`
- `outputs/step26_projection_scale_diagnostics/projection_scale_results.csv`
- `outputs/step26_step25_projection_regression/step25_projection_regression.csv`
- `outputs/step26_short_driver_mesh_48_modes/mesh_48_short_driver_results.csv`
- `outputs/step26_short_driver_voxel_48_modes/voxel_48_short_driver_results.csv`
- `outputs/step26_short_driver_summary/short_driver_summary.json`
- `outputs/step26_quality_report_aggregation/quality_report_summary.json`
- `outputs/step26_step25_regression_guard/step25_regression_guard.json`
- `outputs/step26_artifact_manifest/artifact_summary.json`

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

## Decision For Step 27

If Step 26 passes, Step 27 can conservatively try a 64^3 short-driver subset. It should keep the same scope boundaries and avoid actuation, swimming, production sharp-interface FSI claims, mesh repair claims, automatic remeshing claims, and formula changes.

## Step 27 Follow-Up

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

Step 27 runs only the 64^3 coupling subset for the accepted mesh and voxel candidates: penalty engineering, moving_boundary engineering, and moving_boundary link_area_experimental. It keeps VTK and particle outputs disabled.

## Step 28 Follow-Up Boundary

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

Step 28 keeps the Step 26 strict geometry configs and compares only four 64^3 moving_boundary transfer rows with per-step diagnostics enabled.
