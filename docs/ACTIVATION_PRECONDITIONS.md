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

Original Step70 pending gates:

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

Step74 adds real geometry data-boundary evidence without opening any gate:

```text
real_geometry_data_boundary_audit_pass = true
readiness_claim = real_geometry_boundary_audit_ready_for_later_data_decision_only
activation_allowed_after_step74 = false
required_gate_count = 10
closed_gate_count = 10
activation_allowed_count = 0
```

Real geometry remains non-activated. `data/real_geometry_candidates` remains
protected, no real geometry data was added, `real_geometry_feasibility` remains
quarantined experiment code, and Step74 does not execute projection smoke or
`FSIDriver3D`.

Step75 adds a solver-complete campaign readiness gate without opening any
advanced activation gate:

```text
solver_complete_gate_audit_pass = true
gate_status = ready_for_step76_rebaseline_only
post_gate_simulation_allowed = true
allowed_next_step = Step76
allowed_next_step_scope = minimal safe rebaseline only
activation_features_allowed_in_next_step = []
activation_allowed_count = 0
```

The Step75 `post_gate_simulation_allowed` flag is limited to the Step76
minimal safe rebaseline proposal. Runtime geometry, wall velocity, combined
runtime geometry plus wall velocity, real geometry, squid proxy, link-area
activation, 48^3, 64^3, VTR output, and particle NPY output remain closed.

Step76 executes only the required minimal rebaseline row allowed by Step75 and
does not open any advanced activation gate:

```text
post_gate_rebaseline_matrix_pass = true
post_gate_activation_guard_pass = true
activation_feature_count = 0
runtime_geometry_enabled = false
wall_velocity_enabled = false
real_geometry_enabled = false
squid_proxy_enabled = false
link_area_enabled = false
grid_48_enabled = false
grid_64_enabled = false
write_vtk = false
write_particles = false
```

The optional 32^3/three-step rebaseline remains disabled after Step76.

Step77 adds a separate post-gate canonical driver 3-step rebaseline after
Step76 acceptance and still does not open any advanced activation gate:

```text
post_gate_3step_rebaseline_matrix_pass = true
post_gate_3step_activation_guard_pass = true
activation_feature_count = 0
runtime_geometry_enabled = false
wall_velocity_enabled = false
combined_runtime_geometry_wall_velocity_enabled = false
real_geometry_enabled = false
squid_proxy_enabled = false
link_area_enabled = false
grid_48_enabled = false
grid_64_enabled = false
write_vtk = false
write_particles = false
```

Step77 does not authorize runtime geometry, wall velocity, real geometry,
squid proxy behavior, link-area transfer, larger grids, VTR output, particle
NPY output, or physical-production claims.

Step78 adds a separate post-gate canonical driver 5-step rebaseline after
Step77 acceptance and still does not open any advanced activation gate:

```text
post_gate_5step_rebaseline_matrix_pass = true
post_gate_5step_activation_guard_pass = true
activation_feature_count = 0
runtime_geometry_enabled = false
wall_velocity_enabled = false
combined_runtime_geometry_wall_velocity_enabled = false
real_geometry_enabled = false
squid_proxy_enabled = false
link_area_enabled = false
grid_48_enabled = false
grid_64_enabled = false
write_vtk = false
write_particles = false
```

Step78 does not authorize runtime geometry, wall velocity, real geometry,
squid proxy behavior, link-area transfer, larger grids, VTR output, particle
NPY output, 10-step baselines, or physical-production claims. The next intended
direction is runtime geometry diagnostic-only single-feature activation
planning and guard work.

Step79 plans and guards that next runtime geometry diagnostic-only
single-feature activation without opening runtime simulation:

```text
runtime_geometry_activation_planned = true
runtime_geometry_application_mode_planned_for_step80 = diagnostic_only
step79_activation_feature_count = 0
planned_step80_activation_feature_count = 1
fsidriver_run_allowed = false
simulation_run_allowed = false
geometry_mutation_allowed = false
```

Step79 authorizes only the future Step80 row
`canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke`. Wall
velocity, real geometry, squid proxy behavior, link-area transfer, 48^3, 64^3,
VTR output, particle NPY output, solver formula changes, tau migration, and
physical-production claims remain closed.

Step80 executes the authorized runtime geometry diagnostic-only row:

```text
step80_runtime_geometry_diagnostic_only_smoke_matrix_pass = true
activation_feature_count = 1
runtime_geometry_enabled_count = 1
geometry_motion_interface_report_pass_count = 1
wall_velocity_enabled_count = 0
combined_runtime_geometry_wall_velocity_enabled_count = 0
real_geometry_enabled_count = 0
squid_proxy_enabled_count = 0
link_area_enabled_count = 0
```

Step80 opens only the diagnostic-only runtime geometry interface path. Geometry
mutation, MPM particle displacement, LBM `solid_phi` updates, LBM `solid_vel`
updates, `dynamic_solid` updates, boundary-link recomputation, wall velocity,
real geometry, squid proxy behavior, link-area transfer, larger grids, VTR
output, particle NPY output, solver formula changes, tau migration, and
physical-production claims remain closed after Step80.

Step81 plans and guards a future wall-velocity-only Step82 row without opening
runtime simulation in Step81:

```text
wall_velocity_activation_planned = true
wall_velocity_application_mode_planned_for_step82 = solid_vel_experimental
target_lbm_field_planned_for_step82 = solid_vel
step81_activation_feature_count = 0
planned_step82_activation_feature_count = 1
fsidriver_run_allowed = false
simulation_run_allowed = false
runtime_geometry_allowed = false
combined_runtime_geometry_wall_velocity_allowed = false
```

Step81 authorizes only the future Step82 row
`canonical_driver_wall_velocity_solid_vel_32_3step_smoke`. Runtime geometry,
combined runtime geometry plus wall velocity, real geometry, squid proxy
behavior, link-area transfer, 48^3, 64^3, VTR output, particle NPY output,
solver formula changes, tau migration, and physical-production claims remain
closed in Step81.

Step82 executes the authorized wall-velocity-only row:

```text
step82_wall_velocity_solid_vel_smoke_matrix_pass = true
activation_feature_count = 1
wall_velocity_enabled_count = 1
wall_velocity_application_report_pass_count = 1
boundary_motion_interface_report_pass_count = 1
runtime_geometry_enabled_count = 0
combined_runtime_geometry_wall_velocity_enabled_count = 0
real_geometry_enabled_count = 0
squid_proxy_enabled_count = 0
link_area_enabled_count = 0
grid_48_enabled_count = 0
grid_64_enabled_count = 0
```

Step82 opens only the `solid_vel_experimental` wall-velocity application smoke
for the single planned canonical driver row. It targets only LBM `solid_vel`,
does not write LBM populations directly, does not update MPM or projector
state, does not modify moving bounce-back formulas, does not enable runtime
geometry, real geometry, squid proxy behavior, link-area transfer, larger grids,
VTR output, particle NPY output, solver formula changes, tau migration, or
physical-production claims.

Step83 then plans and guards exactly one future combined Step84 row without
running a simulation:

```text
combined_runtime_geometry_wall_velocity_planned_for_step84 = true
step83_activation_feature_count = 0
planned_step84_activation_feature_count = 2
fsidriver_run_allowed = false
simulation_run_allowed = false
```

Step83 authorizes only the future row
`canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke`.
It does not authorize real geometry, squid proxy behavior, link-area transfer,
larger grids, VTR output, particle NPY output, solver formula changes, tau
migration, or physical-production claims.

Step84 executes that authorized combined row:

```text
step84_runtime_geometry_wall_velocity_combined_smoke_matrix_pass = true
activation_feature_count = 2
runtime_geometry_enabled_count = 1
wall_velocity_enabled_count = 1
combined_runtime_geometry_wall_velocity_enabled_count = 1
real_geometry_enabled_count = 0
squid_proxy_enabled_count = 0
link_area_enabled_count = 0
grid_48_enabled_count = 0
grid_64_enabled_count = 0
```

Step84 opens only the bounded combination of runtime geometry diagnostic-only
interface reporting and wall velocity `solid_vel_experimental` application for
the single planned canonical driver row. Real geometry, squid proxy behavior,
link-area transfer, larger grids, VTR output, particle NPY output, solver
formula changes, tau migration, and physical-production claims remain closed.

Step85 plans and guards a future squid-proxy static-geometry single-feature
activation without running simulation:

```text
squid_proxy_planned_for_step86 = true
step85_activation_feature_count = 0
planned_step86_activation_feature_count = 1
fsidriver_run_allowed = false
simulation_run_allowed = false
runtime_geometry_allowed = false
wall_velocity_allowed = false
combined_runtime_geometry_wall_velocity_allowed = false
real_geometry_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
```

Step85 authorizes only the future row
`canonical_driver_squid_proxy_static_geometry_32_3step_smoke`. It does not
authorize real geometry candidates, runtime geometry, wall velocity, link-area
transfer, larger grids, solver formula changes, tau migration, squid swimming,
physical-validation claims, or production-readiness claims.
