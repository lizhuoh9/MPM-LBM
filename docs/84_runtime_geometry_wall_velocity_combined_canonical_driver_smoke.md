# Step84 Runtime Geometry Wall Velocity Combined Canonical Driver Smoke

Step84 runs exactly one required canonical driver row:

```text
canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

The row is 32^3, uses 1024 particles, runs three LBM steps, performs one MPM
substep per LBM step, uses `moving_boundary` coupling, uses `engineering`
reaction transfer, and uses box geometry.

Step84 combines only:

```text
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
```

The row writes:

```text
geometry_motion_interface_report.json
boundary_motion_interface_report.json
wall_velocity_application_report.json
```

Step84 does not mutate geometry. It does not displace MPM particles through
runtime geometry. It does not update LBM `solid_phi` through runtime geometry.
It does not directly write LBM populations through wall velocity. It does not
modify moving bounce-back formulas. It does not directly update MPM or
projector state through wall velocity.

Step84 keeps real geometry, squid proxy behavior, link-area transfer, 48^3,
64^3, VTR output, particle NPY output, dense wall-velocity output, dense
displacement output, and raw geometry output disabled.

The row-local driver config sets:

```text
target_u_lbm = [0.0, 0.0, 0.0]
```

This isolates the combined smoke from default background flow. It is a config
choice only, not a solver, tau, or runtime-formula change.

Step84 is a combined canonical driver smoke. It is not moving-geometry physics
validation, moving-wall physics validation, real squid validation, grid
convergence, or production readiness.
