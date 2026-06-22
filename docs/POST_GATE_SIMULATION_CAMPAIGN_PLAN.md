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

## Step76 Execution Status

Step76 executes only the required first row from this proposal:

```text
row_id = canonical_driver_moving_boundary_engineering_32_1step_rebaseline
executed_in_step76 = true
```

The optional row remains disabled:

```text
row_id = canonical_driver_moving_boundary_engineering_32_3step_rebaseline_optional
executed_in_step76 = false
```

Step76 does not expand the campaign beyond the Step75 plan. Runtime geometry,
wall velocity, real geometry, squid proxy, link-area transfer, 48^3, 64^3, VTR,
and particle NPY remain disabled.

## Step77 Follow-Up Rebaseline

After Step76 acceptance, Step77 runs a separate required 3-step rebaseline row:

```text
campaign_id = step77_minimal_post_gate_canonical_driver_3step_rebaseline
row_id = canonical_driver_moving_boundary_engineering_32_3step_rebaseline
n_grid = 32
n_lbm_steps = 3
required = true
executed_in_step77 = true
```

Step77 changes duration only. It does not activate runtime geometry, wall
velocity, real geometry, squid proxy behavior, link-area transfer, 48^3, 64^3,
VTR output, particle NPY output, solver formula changes, or tau migration.
