# Geometry Ingestion and Squid Proxy Geometry

Step 13 adds procedural geometry ingestion for MPM particle initialization and LBM projection diagnostics. Step 13 does not add new FSI physics. Step 20 adds a small synthetic mesh and voxel geometry import pipeline. Step 20 does not add new FSI physics. Step 21 carries the Step 20 imported geometry fixtures to larger validation windows without adding new FSI physics. Step 22 adds diagnostic quality checks for imported mesh and voxel geometry. Step 23 repeats imported geometry scale validation with quality_check_enabled=true.

Step 20 is a geometry-ingestion scaffold, not real squid validation. The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 21 carries Step 20 synthetic imported voxel and mesh geometries to 48^3 mode validation and 64^3 feasibility. Step 21 is synthetic imported geometry scale validation, not real squid validation. Imported geometry remains limited to small synthetic voxel and mesh fixtures. The Step 21 mesh path is not production mesh repair.

Step 22 is a geometry QA and import robustness layer, not real squid validation. Imported geometry remains limited to small synthetic voxel and mesh fixtures. The Step 22 mesh path is not production mesh repair or automatic remeshing.
The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 23 uses quality_check_strict=false for scale validation. Step 23 is quality-gated synthetic imported geometry validation, not real squid validation. The default quality_check_enabled remains false. Imported geometry remains limited to small synthetic voxel and mesh fixtures. The Step 23 mesh path is not production mesh repair or automatic remeshing.

## Scope

The geometry layer supports deterministic geometry types:

- `box`
- `ellipsoid`
- `squid_proxy`
- `voxel`
- `mesh`

`GeometryConfig` stores normalized-domain geometry parameters. `GeometrySampler3D` turns those parameters into a deterministic MPM particle cloud and a diagnostic voxel occupancy mask.

Imported geometry supports voxel and mesh inputs through GeometryConfig and GeometrySampler3D. Voxel input is a small `.npy` occupancy array with optional JSON metadata. Mesh input is a small ASCII OBJ fixture with deterministic normalization into the normalized cubic domain.

## Sampling

The sampler uses structured candidate points in normalized `[0, 1]^3`, filters points by analytic inside tests, and selects a deterministic subset of exactly `n_particles` points. Each accepted particle receives:

- `x`: normalized particle position
- `vol0`: reference particle volume
- `mass`: reference particle mass using `p_rho`

This keeps the Step 13 baselines reproducible across runs.

## Voxel Diagnostics

`GeometrySampler3D.voxelize(n_grid)` evaluates the same inside test at cell centers and returns:

- `occupancy`
- `phi`
- `occupied_count`
- `geometry_volume_estimate`

The voxel output is diagnostic only. LBM coupling still uses the existing `MPMToLBMProjector3D` path.

## Imported Geometry

Step 20 adds:

- `src/voxel_io.py` for small `.npy` occupancy loading and metadata stats.
- `src/mesh_io.py` for minimal ASCII OBJ parsing, face triangulation, and normalization.
- `src/geometry_import.py` for `ImportedGeometrySampler3D`.
- `data/geometry_fixtures/` for small synthetic voxel and mesh fixtures.

The Step 20 mesh path is limited to small synthetic fixtures and is not production mesh repair. It supports the Step 20 cube and ellipsoid proxy fixtures; it does not claim non-manifold repair, arbitrary mesh cleanup, material/texture support, or anatomical squid import.

## Step 22 Quality Checks

Step 22 adds:

- mesh diagnostics for counts, bounds, degenerate faces, boundary edges, nonmanifold edges, watertightness proxy, and volume proxy;
- voxel diagnostics for occupied count, occupied fraction, bounds, connected components, surface voxels, and interior voxels;
- `GeometryQualityGate` with non-strict diagnostic mode and strict expected-failure mode;
- small bad fixtures for non-watertight mesh, degenerate mesh, and empty voxel occupancy;
- optional `FSIDriver3D` quality report writing through `geometry_quality_report.json`.

The quality checks run before imported-geometry sampling when explicitly enabled. They do not modify `LBMFluid3D`, `MPMSolid3D`, projector formulas, or coupler formulas.

## MPM Initialization

`MPMSolid3D.init_from_numpy()` initializes particle positions, reference volumes, masses, and optional velocities from NumPy arrays. It resets `C`, `F`, and `Jp` to the undeformed state.

This is an initialization entry point only. It does not change the MPM constitutive model, P2G/G2P, grid update, or boundary behavior.

## Driver Integration

`FSIDriverConfig.geometry_type` controls the initialization path:

- `box`: preserves the existing `MPMSolid3D.init_box()` default path.
- `ellipsoid`: samples an analytic ellipsoid and calls `MPMSolid3D.init_from_numpy()`.
- `squid_proxy`: samples the procedural squid proxy and calls `MPMSolid3D.init_from_numpy()`.
- `voxel`: imports a `.npy` occupancy field, samples particles, and calls `MPMSolid3D.init_from_numpy()`.
- `mesh`: imports a small synthetic OBJ fixture, samples particles, and calls `MPMSolid3D.init_from_numpy()`.

The coupling modes remain unchanged:

- `none`
- `penalty`
- `moving_boundary`

## Squid Proxy Definition

The `squid_proxy` is a procedural union of analytic primitives:

- mantle ellipsoid
- head ellipsoid
- left and right fin ellipsoid-like primitives
- six arm capsules

The squid_proxy is procedural and is not real squid validation. It is not anatomical geometry, does not validate swimming, and is not a biomechanical model.

## Step 30 Squid Proxy Region Semantics

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

Step 30 adds static semantic region descriptors on top of the existing procedural squid proxy:

- `mantle_outer`
- `mantle_cavity_proxy`
- `funnel_outlet_proxy`
- `head_proxy`
- `arms_proxy`
- `left_fin_proxy`
- `right_fin_proxy`

The mantle cavity proxy and funnel outlet proxy are static semantic descriptors. They do not change `GeometrySampler3D`, the MPM initialization path, the LBM projection formula, or any coupler formula.

## Step 31 Squid Proxy Region Static Driver

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

Step 31 reuses `configs/step30_squid_proxy_geometry.json` and `configs/step30_squid_proxy_region_config.json`. It adds projection-only region diagnostics at 32^3, 48^3, and 64^3, then runs four short static 48^3 driver rows with existing coupling modes. It does not add new geometry import behavior, mesh cleanup, remeshing, or raw scan-data handling.

The procedural `squid_proxy` quality report now records that appendage and fin proxy components may be disconnected in coarse diagnostic voxelization. This keeps strict quality reports warning-free for the accepted static proxy semantics without changing `GeometrySampler3D`, `MPMToLBMProjector3D`, LBM, MPM, or coupler formulas.

## Step 32 Squid Proxy Kinematics Schedule

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

Step 32 reuses `configs/step30_squid_proxy_geometry.json` and `configs/step30_squid_proxy_region_config.json` as immutable semantic context. It adds deterministic schedule artifacts for the mantle radius scale, mantle cavity volume proxy scale, and funnel aperture proxy scale. It does not alter `GeometryConfig`, `GeometrySampler3D`, imported geometry loading, MPM initialization, LBM projection, or driver mode dispatch.

## Step 33 Squid Proxy Kinematics Mapping

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

Step 33 reuses `configs/step30_squid_proxy_geometry.json`, `configs/step30_squid_proxy_region_config.json`, and `configs/step32_squid_proxy_kinematics_schedule.json`. It maps schedule rows to region-level proxy diagnostics and grid coverage summaries. It does not alter `GeometryConfig`, `GeometrySampler3D`, imported geometry loading, MPM initialization, LBM projection, or driver mode dispatch.

## Step 14 Reuse

Step 14 reuses `configs/step13_squid_proxy_geometry.json` for 48^3 squid_proxy scale validation. This keeps the procedural geometry fixed while increasing LBM grid resolution. The Step 14 squid_proxy rows remain not real squid validation, not swimming validation, and not anatomical squid geometry evidence.

## Artifact Policy

Step 13 commits small baseline geometry outputs for reproducibility:

- particle clouds
- voxel occupancy masks
- projection diagnostics
- driver mode diagnostics

Larger ad-hoc geometry experiments should be written under `outputs/experiments/` or `outputs/scratch/` and should not be committed unless they become a documented step baseline.

Step 20 commits only small synthetic fixtures and small 32^3 validation artifacts. It does not commit large real geometry, large scans, or large Step 20 VTK exports.

Step 21 commits CSV/NPZ diagnostics for the 48^3 and 64^3 imported-geometry scale baselines with VTK and particle export disabled. It does not commit large real geometry, large scans, or large Step 21 VTK outputs.

Step 22 commits small CSV/JSON/NPZ geometry QA diagnostics, small bad fixtures, and quality gate smoke logs with VTK and particle export disabled. It does not commit large real geometry, large scans, production repair outputs, or automatic remeshing artifacts.

Step 23 commits quality-gated scale validation CSV/JSON/NPZ diagnostics and quality reports with VTK and particle export disabled. It does not commit large real geometry, large scans, production repair outputs, or automatic remeshing artifacts.

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
Step 24 commits small strict long-run CSV/JSON/NPZ diagnostics and quality reports with VTK and particle export disabled. It does not commit large real geometry, large scans, production repair outputs, or automatic remeshing artifacts.

## Step 25 Controlled Candidate Intake

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

Step 25 descriptors live under `configs/step25_candidate_*_descriptor.json`. Local candidate payloads belong under `data/real_geometry_candidates/`, which is ignored by default except for README, `.gitkeep`, and descriptor files.

## Step 26 Controlled Projection And Short Driver Feasibility

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

Step 26 converts the accepted Step 25 descriptors into strict driver-ready geometry configs, runs projection-only scale diagnostics, and then runs 48^3 very short driver feasibility rows with VTK and particle outputs disabled.

## Step 27 Controlled 64 Short Driver Feasibility

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

Step 27 reuses the Step 26 strict driver-ready geometry configs and runs only a six-row 64^3 coupling subset with VTK and particle outputs disabled.

## Limitations

- no real squid geometry validation
- no squid actuation
- no swimming locomotion
- no two-phase flow
- no contact angle physics
- no sparse storage implementation
- no new FSI physics
- no production mesh repair

## Step 28 Geometry Boundary

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

Step 28 reuses the accepted Step 25 candidate descriptors and Step 26 strict driver-ready GeometryConfig files. It does not add mesh cleanup, mesh fixing, or new geometry ingestion behavior.

## Step 29 Geometry Boundary

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

Step 29 reuses the accepted Step 25 candidate descriptors and Step 26 strict driver-ready GeometryConfig files. It does not add mesh cleanup, mesh fixing, or new geometry ingestion behavior.

## Step 34 Boundary-Motion Interface Boundary

Step 34 is controlled squid proxy boundary-motion driver interface.
Step 34 defines a guarded driver interface only.
Step 34 keeps prescribed kinematics diagnostic-only.
Step 34 does not apply moving wall velocity to LBM.
Step 34 does not implement a jet model.
Step 34 does not implement squid swimming.
Step 34 does not implement new FSI physics.
The default boundary_motion_mode remains static.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 34 reuses the accepted Step 30 squid proxy geometry, Step 32 schedule, and Step 33 motion mapping artifacts. It does not add mesh cleanup, mesh fixing, new geometry ingestion behavior, or real geometry validation.
