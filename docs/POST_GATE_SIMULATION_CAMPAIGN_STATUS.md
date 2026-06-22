# Post-Gate Simulation Campaign Status

Step75 created the inactive Step76 campaign proposal. Step76 executes only the
required first row from that proposal.

## Step76 Executed Row

```text
campaign_id = step76_minimal_post_gate_real_driver_rebaseline
row_id = canonical_driver_moving_boundary_engineering_32_1step_rebaseline
n_grid = 32
n_lbm_steps = 1
required = true
```

## Disabled Row

```text
row_id = canonical_driver_moving_boundary_engineering_32_3step_rebaseline_optional
n_grid = 32
n_lbm_steps = 3
required = false
run_by_default = false
executed_in_step76 = false
```

## Feature State

All advanced activation features remain disabled:

```text
runtime_geometry_enabled = false
wall_velocity_enabled = false
real_geometry_enabled = false
squid_proxy_enabled = false
link_area_enabled = false
grid_48_enabled = false
grid_64_enabled = false
write_vtk = false
write_particles = false
activation_feature_count = 0
```

Step76 is a minimal post-gate rebaseline only. It is not a real-geometry,
runtime-geometry, wall-velocity, squid-proxy, grid-convergence, physical
validation, or production-readiness step.
