# Strict Quality-Gated Imported Geometry Long-Run Validation

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

## Scope

Step 24 bridges Step 22 strict bad-geometry failure evidence and Step 23 non-strict good imported-geometry scale evidence. It checks that good synthetic imported voxel and mesh fixtures pass strict geometry quality gating before and during longer moving-boundary validation windows.

Step 24 does not add solver physics, modify coupling formulas, validate real squid geometry, add squid actuation, add swimming validation, add two-phase flow, add contact angle physics, add sparse storage, or edit `external/taichi_LBM3D`.

## Quality Gate Mode

All Step 24 driver configs use:

```text
quality_check_enabled = true
quality_check_strict = true
write_vtk = false
write_particles = false
```

The strict quality gate is applied only to the selected Step 24 synthetic imported geometry rows. Default configs and dataclass defaults remain non-strict and disabled unless explicitly enabled by a driver config.

## Geometry Cases

Step 24 covers six 48^3 long-run rows:

- `voxel_sphere` moving_boundary engineering
- `voxel_sphere` moving_boundary `link_area_experimental`
- `mesh_cube` moving_boundary engineering
- `mesh_cube` moving_boundary `link_area_experimental`
- `mesh_ellipsoid` moving_boundary engineering
- `mesh_ellipsoid` moving_boundary `link_area_experimental`

Step 24 also covers three 64^3 strict feasibility rows:

- `voxel_sphere` moving_boundary engineering
- `mesh_cube` moving_boundary engineering
- `mesh_cube` moving_boundary `link_area_experimental`

## Baselines

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_voxel_sphere_48_long.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_mesh_cube_48_long.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_mesh_ellipsoid_48_long.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_imported_geometry_64_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_step23_prefix_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_strict_non_strict_report_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_timing_overhead_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step24_artifact_manifest.py
```

Primary outputs:

- `outputs/step24_strict_voxel_sphere_48_long/voxel_sphere_48_strict_long_results.csv`
- `outputs/step24_strict_mesh_cube_48_long/mesh_cube_48_strict_long_results.csv`
- `outputs/step24_strict_mesh_ellipsoid_48_long/mesh_ellipsoid_48_strict_long_results.csv`
- `outputs/step24_strict_imported_geometry_64_feasibility/imported_geometry_64_strict_feasibility_results.csv`
- `outputs/step24_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step24_step23_prefix_comparison/step23_prefix_comparison.csv`
- `outputs/step24_strict_non_strict_report_comparison/strict_non_strict_report_comparison.csv`
- `outputs/step24_timing_overhead_summary/step24_timing_summary.csv`
- `outputs/step24_artifact_manifest/artifact_summary.json`

## Artifact Policy

Step 24 keeps VTK and particle export disabled. Step 24 commits only small CSV, JSON, NPZ, and log artifacts. The artifact manifest checks that Step 24 writes exactly nine quality reports, no Step 24 `.vtr` files, no Step 24 particle `.npy` outputs, and that Step 24 output size stays below the configured budget.

## Limitations

- no real squid geometry validation;
- no squid actuation;
- no swimming validation;
- no production mesh repair;
- no automatic remeshing;
- no two-phase flow;
- no contact angle physics;
- no sparse storage;
- no new FSI physics.

## Next Step

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

Step 25 starts with descriptor validation, fingerprinting, strict geometry QA, normalization reports, deterministic sampling reproducibility, and projection-only smoke diagnostics.
