# Units, Grid, and Timestep

Step 4 introduced the shared normalized cubic domain and explicit unit conversion between MPM-normalized quantities and LBM lattice quantities.

## Domain

The domain is normalized to a cube of length:

```text
domain_length = 1.0
```

For a cubic grid:

```text
dx_norm = 1 / n_grid
```

The current small validation baseline uses:

```text
n_grid = 32
n_particles = 4096
```

## Timestep Synchronization

One LBM step corresponds to a fixed number of MPM substeps:

```text
lbm_dt_phys = mpm_substeps_per_lbm_step * mpm_dt
```

Current defaults:

```text
mpm_dt = 4.0e-4
mpm_substeps_per_lbm_step = 10
lbm_dt_phys = 0.004
```

## Velocity Conversion

Normalized velocity to LBM velocity:

```text
u_lbm = u_norm * lbm_dt_phys / dx_norm
```

LBM velocity to normalized velocity:

```text
u_norm = u_lbm * dx_norm / lbm_dt_phys
```

The current small validation cases use target_u_lbm around 0.02 to 0.03 in small validation cases.

## Acceleration Conversion

Normalized acceleration to LBM acceleration:

```text
a_lbm = a_norm * lbm_dt_phys^2 / dx_norm
```

LBM acceleration to normalized acceleration:

```text
a_norm = a_lbm * dx_norm / lbm_dt_phys^2
```

## Viscosity Conversion

Normalized kinematic viscosity to LBM viscosity:

```text
nu_lbm = nu_norm * lbm_dt_phys / dx_norm^2
```

LBM viscosity to normalized kinematic viscosity:

```text
nu_norm = nu_lbm * dx_norm^2 / lbm_dt_phys
```

## Practical Constraint

The current settings are conservative small-scale validation settings. Larger grids, larger velocities, or stronger coupling should be treated as new validation work, not as automatically covered by Step 10.
