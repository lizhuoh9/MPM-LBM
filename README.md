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
- Step 23 quality-gated synthetic imported geometry scale validation with quality reports for every driver row
- Step 24 strict quality-gated synthetic imported geometry long-run validation for selected moving_boundary rows
- Step 25 controlled real geometry candidate intake with manifest, fingerprinting, normalization reports, deterministic sampling reproducibility, and projection-only smoke diagnostics
- Step 26 controlled real geometry projection-only and short driver feasibility with strict quality reports for every very short driver row
- Step 27 controlled real geometry 64^3 short driver feasibility for a six-row coupling subset with strict quality reports
- Step 28 controlled real geometry 64^3 transfer diagnostics comparing engineering and link_area_experimental moving_boundary transfer rows
- Step 29 controlled real geometry 64^3 short-window stability envelope for the Step 28 transfer matrix
- Step 30 controlled squid proxy region geometry contract for static squid-like region semantics
- Step 31 controlled squid proxy region projection and static driver smoke for existing coupling modes only
- Step 32 controlled squid proxy prescribed kinematics schedule contract for artifact-only mantle, cavity, and funnel proxy schedules
- Step 33 controlled squid proxy kinematics mapping to boundary-motion diagnostics for artifact-only displacement and velocity proxies

## Not Implemented

- two-phase flow
- contact angle physics
- sparse storage
- real squid geometry
- real squid validation
- production mesh repair
- final strict momentum-conserving sharp-interface FSI
- production-grade solver readiness

## Step 30 Squid Proxy Region Boundary

Step 30 is controlled squid proxy region geometry.
Step 30 defines squid-like region semantics only.
Step 30 is not real squid validation.
Step 30 does not implement squid actuation.
Step 30 does not implement squid swimming.
Step 30 does not implement mantle contraction.
Step 30 does not implement funnel actuation.
Step 30 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 30 adds stable proxy region IDs for `mantle_outer`, `mantle_cavity_proxy`, `funnel_outlet_proxy`, `head_proxy`, `arms_proxy`, `left_fin_proxy`, and `right_fin_proxy`. The cavity and outlet regions are static geometry semantics only.

## Step 31 Squid Proxy Static Driver Boundary

Step 31 is controlled squid proxy region projection and static driver smoke.
Step 31 uses static squid proxy region semantics only.
Step 31 is not real squid validation.
Step 31 does not implement squid actuation.
Step 31 does not implement squid swimming.
Step 31 does not implement mantle contraction.
Step 31 does not implement funnel actuation.
Step 31 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 31 adds 32^3/48^3/64^3 projection-only region diagnostics, four 48^3 static driver smoke rows, region-driver alignment, engineering vs link_area_experimental static comparison, strict quality report aggregation, and a Step 30 regression guard.

## Step 32 Squid Proxy Kinematics Schedule Boundary

Step 32 is controlled squid proxy prescribed kinematics schedule.
Step 32 defines kinematics schedules only.
Step 32 does not integrate kinematics into FSIDriver3D.
Step 32 does not apply moving wall velocity.
Step 32 does not implement mantle contraction in the driver.
Step 32 does not implement funnel actuation in the driver.
Step 32 does not implement squid swimming.
Step 32 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 32 adds deterministic phase samples, mantle radius scale, mantle cavity volume proxy scale, funnel aperture proxy scale, derivative diagnostics, repeatability hashes, region mapping validation, a Step 31 regression guard, and artifact budget checks. These are schedule artifacts only.

## Step 33 Squid Proxy Kinematics Mapping Boundary

Step 33 is controlled squid proxy kinematics mapping to boundary-motion diagnostics.
Step 33 maps schedules to displacement and velocity proxies only.
Step 33 does not integrate kinematics into FSIDriver3D.
Step 33 does not apply moving wall velocity to LBM.
Step 33 does not implement a jet model.
Step 33 does not implement squid swimming.
Step 33 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 33 maps the accepted Step 32 schedule to region-level proxy diagnostics for `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy`, then summarizes coverage at 32^3, 48^3, and 64^3. These diagnostics are not written into a coupled simulation state.

## Step 25 Intake Boundary

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

## Step 26 Short Feasibility Boundary

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

Step 26 reuses the accepted Step 25 candidates, checks their fingerprints, creates driver-ready geometry configs, runs projection-only diagnostics at 32^3/48^3/64^3, and runs 48^3 very short driver rows for existing modes only.

## Step 27 64 Short Driver Boundary

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

Step 27 reuses the accepted Step 25 candidates and Step 26 strict driver-ready geometry configs, then runs only six 64^3 short coupling rows: penalty engineering, moving_boundary engineering, and moving_boundary link_area_experimental for both mesh and voxel candidates.

## Step 28 Transfer Diagnostics Boundary

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

Step 28 reuses the accepted Step 25 candidates and Step 26 strict driver-ready geometry configs, then runs four 64^3 moving_boundary rows: engineering and link_area_experimental transfer for both mesh and voxel candidates.

## Step 29 Stability Envelope Boundary

Step 29 is controlled real geometry 64^3 short-window stability envelope.
Step 29 extends Step 28 transfer diagnostics conservatively.
Step 29 is not real squid validation.
Step 29 does not implement squid actuation.
Step 29 does not implement squid swimming.
Step 29 does not implement new FSI physics.
Step 29 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 29 reuses the accepted Step 28 transfer matrix, then runs four 64^3 moving_boundary 20-step rows to summarize stability, force/reaction, transfer, area-scale, and Step 28 prefix envelopes.

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

Step 23 repeats imported geometry scale validation with quality_check_enabled=true.
Step 23 uses quality_check_strict=false for scale validation.
Step 23 is quality-gated synthetic imported geometry validation, not real squid validation.
The default quality_check_enabled remains false.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 23 mesh path is not production mesh repair or automatic remeshing.
See docs/22_quality_gated_imported_geometry_validation.md.

## Upstream LBM Note

The LBM backend is derived from the vendored taichi_LBM3D single-phase solver under external/taichi_LBM3D. The external source is kept unmodified in this project workflow. For license details, see the upstream repository and vendored license files if present.
