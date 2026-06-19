# Quality-Gated Imported Geometry Scale Validation

Step 23 repeats imported geometry scale validation with quality_check_enabled=true.
Step 23 uses quality_check_strict=false for scale validation.
Step 23 is quality-gated synthetic imported geometry validation, not real squid validation.

The default quality_check_enabled remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 23 mesh path is not production mesh repair or automatic remeshing.

## Scope

Step 23 reruns the Step 21 imported geometry scale cases with the Step 22 quality report path enabled. The quality gate is diagnostic and non-strict for these good synthetic fixtures.

Step 23 does not add new FSI physics, change solver formulas, change coupling formulas, validate real squid geometry, add squid actuation, add swimming validation, add two-phase flow, add contact angle physics, add sparse storage, or edit `external/taichi_LBM3D`.

## Quality Gate Mode

All Step 23 driver configs use:

```text
quality_check_enabled = true
quality_check_strict = false
write_vtk = false
write_particles = false
```

Strict failure behavior remains covered by Step 22 bad geometry fixtures. Step 23 checks that good synthetic imported geometry can run through the existing scale baselines while writing `geometry_quality_report.json` for every row.

## Geometry Cases

Step 23 covers:

- `voxel_sphere`
- `mesh_cube`
- `mesh_ellipsoid`

The 48^3 mode matrix includes:

- `none`
- `penalty`
- `moving_boundary` with engineering reaction transfer
- `moving_boundary` with opt-in `link_area_experimental`

The required 64^3 feasibility rows are:

- `voxel_sphere` penalty
- `voxel_sphere` moving_boundary engineering
- `mesh_cube` penalty

## Baselines

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_voxel_sphere_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_mesh_cube_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_mesh_ellipsoid_48_modes.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_gated_imported_geometry_64_feasibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_step21_vs_quality_gated_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step23_artifact_manifest.py
```

Primary outputs:

- `outputs/step23_quality_gated_voxel_sphere_48_modes/voxel_sphere_48_quality_gated_results.csv`
- `outputs/step23_quality_gated_mesh_cube_48_modes/mesh_cube_48_quality_gated_results.csv`
- `outputs/step23_quality_gated_mesh_ellipsoid_48_modes/mesh_ellipsoid_48_quality_gated_results.csv`
- `outputs/step23_quality_gated_imported_geometry_64_feasibility/imported_geometry_64_quality_gated_results.csv`
- `outputs/step23_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step23_step21_vs_quality_gated_comparison/step21_vs_step23_comparison.csv`
- `outputs/step23_artifact_manifest/artifact_summary.json`

## Results

Step 23 produced 15 driver rows. All rows were stable, all rows had `quality_pass = true`, all quality reports had severity `ok`, and the quality aggregation found 15 reports with zero errors.

The Step 21 vs Step 23 comparison produced 15 comparable rows with `stable_both = true`. The maximum absolute deltas were small and finite:

- `rho_min`: `1.072883606e-06`
- `rho_max`: `5.960464478e-07`
- `lbm_max_v`: `1.708976924e-07`
- `mpm_min_J`: `2.980232239e-07`
- `projected_mass`: `2.086162567e-06`
- `active_cell_count`: `0`

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

## Decision For Step 24

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

The Step 24 role is to verify that good synthetic imported geometry passes strict quality gating during selected longer moving_boundary windows before opening a controlled real geometry intake contract.
