# Geometry Ingestion and Squid Proxy Geometry

Step 13 adds procedural geometry ingestion for MPM particle initialization and LBM projection diagnostics. Step 13 does not add new FSI physics.

## Scope

The geometry layer supports three deterministic geometry types:

- `box`
- `ellipsoid`
- `squid_proxy`

`GeometryConfig` stores normalized-domain geometry parameters. `GeometrySampler3D` turns those parameters into a deterministic MPM particle cloud and a diagnostic voxel occupancy mask.

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

## MPM Initialization

`MPMSolid3D.init_from_numpy()` initializes particle positions, reference volumes, masses, and optional velocities from NumPy arrays. It resets `C`, `F`, and `Jp` to the undeformed state.

This is an initialization entry point only. It does not change the MPM constitutive model, P2G/G2P, grid update, or boundary behavior.

## Driver Integration

`FSIDriverConfig.geometry_type` controls the initialization path:

- `box`: preserves the existing `MPMSolid3D.init_box()` default path.
- `ellipsoid`: samples an analytic ellipsoid and calls `MPMSolid3D.init_from_numpy()`.
- `squid_proxy`: samples the procedural squid proxy and calls `MPMSolid3D.init_from_numpy()`.

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

## Step 14 Reuse

Step 14 reuses `configs/step13_squid_proxy_geometry.json` for 48^3 squid_proxy scale validation. This keeps the procedural geometry fixed while increasing LBM grid resolution. The Step 14 squid_proxy rows remain not real squid validation, not swimming validation, and not anatomical squid geometry evidence.

## Artifact Policy

Step 13 commits small baseline geometry outputs for reproducibility:

- particle clouds
- voxel occupancy masks
- projection diagnostics
- driver mode diagnostics

Larger ad-hoc geometry experiments should be written under `outputs/experiments/` or `outputs/scratch/` and should not be committed unless they become a documented step baseline.

## Limitations

- no mesh import
- no real squid geometry validation
- no squid actuation
- no swimming locomotion
- no two-phase flow
- no contact angle physics
- no sparse storage implementation
- no new FSI physics
