# Solver-Complete Readiness Gate

The solver-complete readiness gate is a campaign-planning gate, not a claim
that the solver is complete in a physical or production sense.

## Required Inputs

The gate requires green committed evidence from:

- Step71 output default safety alignment and tau convention decision
- Step72 runtime geometry readiness audit
- Step73 wall velocity readiness audit
- Step74 real geometry data boundary audit

Step75 validates these inputs through
`outputs/step75_precondition_artifact_audit/precondition_artifact.json`.

## Required Gate State

All activation gates must remain closed:

```text
runtime_geometry_activation_allowed = false
wall_velocity_activation_allowed = false
combined_runtime_geometry_wall_velocity_activation_allowed = false
real_geometry_activation_allowed = false
squid_proxy_activation_allowed = false
link_area_activation_allowed = false
grid_48_activation_allowed = false
grid_64_activation_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
```

Step75 validates this state through
`outputs/step75_activation_gate_closure_audit/activation_gate_closure.json`.

## Pass Decision

A passing gate has this status:

```text
gate_status = ready_for_step76_rebaseline_only
allowed_next_step = Step76
allowed_next_step_scope = minimal safe rebaseline only
```

The gate does not open advanced activation features. The only permitted next
work is a Step76 minimal safe rebaseline proposal with safe outputs and all
runtime geometry, wall velocity, real geometry, and squid proxy features off.
