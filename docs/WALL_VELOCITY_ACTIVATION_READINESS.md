# Wall Velocity Activation Readiness

Wall velocity remains closed after Step73. The readiness status is:

```text
readiness_claim = wall_velocity_audit_ready_for_later_activation_decision_only
wall_velocity_activation_allowed = false
combined_runtime_geometry_wall_velocity_activation_allowed = false
runtime_geometry_activation_allowed = false
```

The Step73 readiness audit proves that the current wall velocity surface is
importable, schema-stable, opt-in only, closed by default at the driver config
boundary, and covered by output/no-simulation regression guards.

The opt-in application remains limited to `lbm.solid_vel`. It does not update
LBM populations, MPM state, projector state, moving bounce-back formulas, jet
claims, or actuation claims.

This is not a solver activation step. A later activation step must provide a
separate validated runtime coupling contract before changing driver behavior or
claiming physical validation.
