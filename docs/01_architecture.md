# Architecture

The project is organized around a single Taichi runtime and a normalized cubic domain. `FSIDriver3D` is an engineering orchestration layer. It selects a mode, advances existing solver components, collects diagnostics, and writes outputs. It is not a new physical coupling model.

The benchmark and validation boundary is fixed by
`docs/GENERIC_SOLVER_ARCHITECTURE_CONTRACT.md`: solver-core packages remain
benchmark-agnostic, benchmark adapters may prepare inputs and comparisons
without changing solver equations, and official Fluent assets stay outside the
repository.

## Components

### LBMFluid3D

`LBMFluid3D` wraps the dense single-phase D3Q19 MRT LBM path. It owns distribution fields, density, velocity, static solid masks, dynamic solid masks, projection fields, `cell_force`, `hydro_force`, and VTK export.

### MPMSolid3D

`MPMSolid3D` owns particles, APIC affine fields, deformation gradients, particle volume/mass, and the MPM grid. It exposes `grid_f_ext` so coupling layers can add external reaction forces before grid update.

### GridUnitMapper

`GridUnitMapper` converts positions, velocities, accelerations, and viscosity between normalized MPM units and LBM lattice units.

### MPMToLBMProjector3D

`MPMToLBMProjector3D` transfers MPM particle volume, mass, and velocity to LBM grid fields:

```text
solid_phi
solid_mass
solid_vel
```

### PenaltyFSICoupler3D

`PenaltyFSICoupler3D` builds diffuse-interface `cell_force` on the LBM grid and transfers the opposite `hydro_force` back to the MPM grid.

### MovingBoundaryFSICoupler3D

`MovingBoundaryFSICoupler3D` samples link-wise moving-boundary `hydro_force` diagnostics and transfers an engineering-scale reaction to `MPMSolid3D.grid_f_ext`.

### FSIDriverConfig

`FSIDriverConfig` stores mode, grid, particle count, timestep, velocity, gravity, box, and coupling parameters. It can load JSON configs through `from_json()`.

### FSIDriver3D

`FSIDriver3D` constructs the LBM fluid, MPM solid, projector, optional coupler, diagnostics, outputs, and timing profile. It supports `none`, `penalty`, and `moving_boundary`.

## Data Flow

```text
MPMSolid3D particles
  -> MPMToLBMProjector3D
  -> LBMFluid3D solid_phi / solid_mass / solid_vel
  -> coupling mode
  -> LBM step
  -> hydro_force diagnostics or reaction
  -> MPMSolid3D grid_f_ext
```

## Mode-Specific Paths

```text
MPMSolid3D
  x, v, mass, vol0, Jp
       |
       v
MPMToLBMProjector3D
       |
       v
LBMFluid3D fields:
  solid_phi, solid_mass, solid_vel
       |
       +---- none mode ----> lbm.step()
       |
       +---- penalty mode ----> cell_force / hydro_force
       |
       +---- moving_boundary mode ----> dynamic solid + hydro_force
```

## Output Layer

Driver runs write:

```text
diagnostics_timeseries.csv
diagnostics_timeseries.npz
LBMFluid_*.vtr
particles_x.npy
particles_v.npy
particles_F.npy
particles_J.npy
```

The outputs are regression artifacts and inspection aids. They are not a production data format.
