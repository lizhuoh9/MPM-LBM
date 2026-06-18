# Numerical Methods

This document summarizes the implemented numerical methods at the level needed for project review. It does not claim final physical fidelity beyond the committed baselines.

## LBM

The fluid side uses a D3Q19 MRT single-phase LBM backend derived from the vendored taichi_LBM3D solver. The local wrapper keeps dense storage and provides:

- D3Q19 velocity set and weights
- MRT collision
- single-phase density and velocity fields
- static bounce-back for solid cells
- Guo-style forcing path for grid-local `cell_force`
- opt-in moving bounce-back through `step_moving_bounceback()`
- VTK export for ParaView-style inspection

The default `lbm.step()` path remains the penalty-compatible path. Moving bounce-back is opt-in and is not the implicit default.

## MPM

The solid side is a 3D MPM solver with:

- particles in a normalized cubic domain
- quadratic B-spline stencil
- APIC affine velocity field `C`
- deformation gradient `F`
- `Jp` volume-change diagnostic
- fixed-corotated elasticity
- grid mass, velocity, and external force fields

`MPMSolid3D.grid_f_ext` is the entry point used by coupling layers to apply reaction forces before the MPM grid update.

## Projection

`MPMToLBMProjector3D` projects MPM particle data to the LBM lattice:

```text
solid_phi  <- particle volume fraction
solid_mass <- particle mass
solid_vel  <- mass-weighted particle velocity converted to LBM units
```

The projection uses the same local stencil style as MPM particle-grid transfers and clamps `solid_phi` to a bounded grid field for coupling.

## Penalty Coupling

The penalty mode is a diffuse-interface MVP. After projection, `PenaltyFSICoupler3D` builds a local force on LBM fluid cells:

```text
cell_force = beta_lbm * solid_phi * rho * (solid_vel - fluid_vel)
```

The force is capped for small-scale stability. The equal/opposite `hydro_force` is sampled back to MPM particles and accumulated on `grid_f_ext`.

This mode is useful for comparing coupled response trends, but it is not a final sharp-interface method.

## Moving-Boundary Coupling

The moving-boundary mode is a sharper-interface MVP. The driver:

```text
projector.project()
lbm.update_dynamic_solid()
lbm.reinitialize_new_fluid_cells()
lbm.step_moving_bounceback()
MovingBoundaryFSICoupler3D reaction transfer -> MPM grid
```

`LBMFluid3D` computes link-wise moving-boundary diagnostics during `step_moving_bounceback()`. `MovingBoundaryFSICoupler3D` samples `hydro_force` and transfers an engineering-scale reaction to the MPM grid.

The moving-boundary reaction currently uses engineering scaling, not final strict link-area momentum integration. The current implementation is not a strict final momentum-conserving sharp-interface FSI solver.
