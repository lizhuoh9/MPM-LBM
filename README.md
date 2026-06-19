# MPM-LBM FSI Prototype

A Taichi-based prototype framework for 3D MPM solid and LBM fluid coupling.

Current status: engineering prototype.

This repository is a small-scale engineering prototype for comparing MPM-LBM coupling paths. It is not production ready and should not be described as a completed sharp-interface FSI solver or a real squid simulation.

## Implemented

- 3D single-phase LBM backend based on taichi_LBM3D
- 3D MPM solid backend
- unified grid/unit/timestep scaffold
- MPM-to-LBM projection
- penalty-force two-way coupling
- moving-boundary bounce-back path
- moving-boundary reaction transfer to MPM
- unified FSIDriver3D with modes: none, penalty, moving_boundary
- shared diagnostics, CSV/NPZ outputs, logs, and small validation baselines
- larger-grid engineering baselines through 48^3 and 64^3 feasibility checks
- moving-boundary reaction calibration diagnostics and recommended moving_boundary configs
- Step 16 long-run validation for calibrated 48^3 moving_boundary cases and a conservative 64^3 moving_boundary feasibility row
- Step 17 diagnostic-only direction-wise and link-area proxy accounting for moving-boundary bounce-back
- Step 18 opt-in experimental link-area reaction transfer mode for moving_boundary comparison
- Step 19 long-window and 64^3 feasibility validation for the opt-in experimental link-area transfer
- Step 20 small synthetic mesh and voxel geometry import pipeline for 32^3 imported-geometry smoke validation
- Step 21 synthetic imported geometry scale validation for 48^3 imported-geometry mode rows and 64^3 feasibility rows
- Step 22 diagnostic mesh/voxel geometry quality checks and import robustness baselines

## Not Implemented

- two-phase flow
- contact angle physics
- sparse storage
- real squid geometry
- real squid validation
- production mesh repair
- final strict momentum-conserving sharp-interface FSI
- production-grade solver readiness

## Quick Start

Use the known Windows Python environment for this workspace:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Run the main Step 10 driver baselines:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_penalty_mode.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_moving_boundary_mode.py
```

The committed Step 10 artifacts are the current reproducibility baseline. Step 11 adds documentation and does not require rerunning heavy simulations when those artifacts are present and tests pass.

## Core Modes

| mode | LBM path | MPM reaction | cell_force | dynamic solid |
| ---- | -------- | ------------ | ---------- | ------------- |
| none | `lbm.step()` | none | zero | no |
| penalty | `lbm.step()` | `PenaltyFSICoupler3D` | nonzero | no |
| moving_boundary | `lbm.step_moving_bounceback()` | `MovingBoundaryFSICoupler3D` by default | zero | yes |

## Repository Layout

```text
src/
  lbm_fluid.py
  mpm_solid.py
  projection.py
  coupling.py
  moving_boundary_coupling.py
  fsi_config.py
  fsi_driver.py
  diagnostics.py

baseline_tests/
configs/
docs/
logs/
outputs/
paper/
tests/
```

## Reproducibility

All step reports and baseline logs are committed for reproducibility. The main validated driver entry points are the Step 10 baselines and the `FSIDriver3D` mode matrix.

Current validation includes small 32^3 regression cases, 48^3 engineering scale baseline cases, and 64^3 short feasibility checks. These runs are useful regression and comparison baselines, not final accuracy validation and not production benchmark data.

## Performance and Artifact Policy

See:

- docs/10_performance_memory.md
- docs/11_artifact_policy.md

## Geometry Support

Step 13 adds procedural geometry initialization:

- box
- ellipsoid
- squid_proxy

The squid_proxy is procedural and is not real squid validation.

Step 20 adds a small synthetic mesh and voxel geometry import pipeline.
Step 20 is a geometry-ingestion scaffold, not real squid validation.
Imported geometry supports voxel and mesh inputs through GeometryConfig and GeometrySampler3D.
The Step 20 mesh path is limited to small synthetic fixtures and is not production mesh repair.

Step 21 carries Step 20 synthetic imported voxel and mesh geometries to 48^3 mode validation and 64^3 feasibility.
Step 21 is synthetic imported geometry scale validation, not real squid validation.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 21 mesh path is not production mesh repair.

Supported geometry types are now:

- box
- ellipsoid
- squid_proxy
- voxel
- mesh

The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Run the Step 20 imported geometry baselines:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_voxel_import_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_mesh_import_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_imported_geometry_projection.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step20_driver_imported_geometry_modes.py
```

## Larger-Grid Validation

Step 14 adds 48^3 scale validation and 64^3 feasibility checks. These are engineering scale baselines, not production benchmark data or real squid validation. Step 14 does not add new FSI physics.

## Moving-Boundary Calibration

Step 15 adds `MomentumAccounting3D`, calibration helpers, reaction_scale and force_cap_norm sweeps, and recommended moving_boundary configs for 48^3 box and 48^3 procedural squid_proxy cases. Step 15 does not change the moving bounce-back formula and does not claim strict final momentum conservation.

## Long-Run Validation

Step 16 does not add new FSI physics. It uses the Step 15 calibrated moving_boundary settings for longer 48^3 box and procedural squid_proxy runs, then adds a conservative 64^3 moving_boundary feasibility row and a 64^3 none/penalty/moving_boundary mode comparison.

The 64^3 moving_boundary row is a feasibility baseline. squid_proxy is procedural and not real squid validation. Strict link-area momentum-conserving coupling remains future work.

## Link-Area Momentum Accounting

Step 17 adds diagnostic-only direction-wise and link-area proxy accounting. The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged.

The Step 17 area policies are `uniform`, `inverse_length`, and `length`. These are diagnostic proxy policies, not final surface-area reconstruction. Strict link-area momentum-conserving coupling remains future work. squid_proxy is procedural and not real squid validation.

## Experimental Link-Area Transfer

Step 18 adds an opt-in experimental link-area reaction transfer mode. The default moving_boundary reaction transfer remains engineering. The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged.

The experimental transfer uses a bounded global area_scale from Step 17 link-area proxy accounting. Enable it only with `coupling_mode = "moving_boundary"` and `reaction_transfer_mode = "link_area_experimental"`. This is not final strict momentum-conserving sharp-interface FSI. squid_proxy is procedural and not real squid validation.

## Link-Area Long-Run Validation

Step 19 validates the opt-in link_area_experimental transfer over longer windows and 64^3 feasibility. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. LinkAreaMovingBoundaryCoupler3D formula is unchanged. MovingBoundaryFSICoupler3D is unchanged.

The link-area transfer remains experimental and uses a bounded global area_scale. This is not final strict momentum-conserving sharp-interface FSI. squid_proxy is procedural and not real squid validation.

## Geometry Import Pipeline

Step 20 adds small synthetic voxel and OBJ fixtures, minimal import utilities, deterministic imported-geometry particle sampling, LBM projection diagnostics, and 32^3 driver smoke baselines for none, penalty, and moving_boundary modes. It prepares the repository for future real geometry ingestion without changing FSI physics.

Step 21 carries those small synthetic imported voxel and mesh fixtures to 48^3 mode validation and 64^3 feasibility without changing coupling formulas. See docs/20_imported_geometry_scale_validation.md.

Step 22 adds diagnostic quality checks for imported mesh and voxel geometry.
Step 22 is a geometry QA and import robustness layer, not real squid validation.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 22 mesh path is not production mesh repair or automatic remeshing.

The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
See docs/21_geometry_quality_checks.md.

## Upstream LBM Note

The LBM backend is derived from the vendored taichi_LBM3D single-phase solver under external/taichi_LBM3D. The external source is kept unmodified in this project workflow. For license details, see the upstream repository and vendored license files if present.
