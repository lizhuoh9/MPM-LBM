# Activation Preconditions

Step70 keeps all activation gates closed.

```text
activation_preconditions_audit_pass = true
activation_allowed_count = 0
activation_gate_count = 10
pending_gate_count = 5
```

Closed gates:

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

Pending gates:

```text
Step72 runtime geometry activation readiness pending
Step73 wall velocity activation readiness pending
Step74 real geometry data boundary pending
Step75 solver-complete campaign gate pending
```

Step71 resolves the tau convention decision without opening activation gates:

```text
tau_convention_decision = preserve_legacy_external_solver_parameter_for_now
default_solver_tau_formula = tau_from_legacy_external_solver_parameter
standard_lattice_viscosity_is_default = false
physical_viscosity_validation_claim = false
future_standard_tau_migration_requires_baseline_rerun = true
```

Activation remains closed after Step71. Runtime geometry, wall velocity, real
geometry, squid proxy activation, VTR output, and particle NPY output remain
blocked until later readiness steps explicitly open those gates.

Step72 adds runtime geometry activation readiness evidence without opening any
gate:

```text
runtime_geometry_readiness_audit_pass = true
readiness_claim = audit_ready_for_later_activation_decision_only
activation_allowed_after_step72 = false
```

The Step70 activation policy remains closed. Step72 only records that the
runtime geometry API, config schema, driver gates, state guards, output policy,
no-simulation guard, and Step71 regression guard are ready for a later activation
decision.

Step73 adds wall velocity activation readiness evidence without opening any gate:

```text
wall_velocity_readiness_audit_pass = true
readiness_claim = wall_velocity_audit_ready_for_later_activation_decision_only
activation_allowed_after_step73 = false
required_gate_count = 10
closed_gate_count = 10
activation_allowed_count = 0
```

Wall velocity remains opt-in and non-activated. LBM population updates, MPM
state updates, projector updates, moving bounce-back formula modification, jet
claims, and actuation claims remain forbidden.
