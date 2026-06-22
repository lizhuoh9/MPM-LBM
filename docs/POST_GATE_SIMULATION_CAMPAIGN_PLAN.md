# Post-Gate Simulation Campaign Plan

This document records the inactive campaign proposal created by Step75 for
Step76. It is not executed by Step75.

## Allowed Step76 Campaign

```text
campaign_id = step76_minimal_post_gate_real_driver_rebaseline
campaign_kind = inactive_policy_proposal
```

Required first row:

```text
row_id = canonical_driver_moving_boundary_engineering_32_1step_rebaseline
n_grid = 32
n_lbm_steps = 1
required = true
```

Optional row, disabled by default:

```text
row_id = canonical_driver_moving_boundary_engineering_32_3step_rebaseline_optional
n_grid = 32
n_lbm_steps = 3
required = false
run_by_default = false
```

## Required Feature State

All advanced features remain disabled:

```text
runtime_geometry_enabled = false
wall_velocity_enabled = false
real_geometry_enabled = false
squid_proxy_enabled = false
write_vtk = false
write_particles = false
activation_features = []
```

## Forbidden Campaign Items

The Step76 starter campaign must not include runtime geometry plus wall
velocity coupling, real geometry candidates, squid motion, 48^3 or 64^3 rows,
VTR output, particle NPY output, required link-area rows, or long-duration
runs.

Step75 validates this proposal through
`outputs/step75_post_gate_campaign_policy_audit/post_gate_campaign_policy.json`.
