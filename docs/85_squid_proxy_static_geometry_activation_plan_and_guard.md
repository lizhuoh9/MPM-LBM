# Step85 Squid Proxy Static Geometry Activation Plan And Guard

Step85 is a plan-and-guard step for exactly one future Step86 row:
`canonical_driver_squid_proxy_static_geometry_32_3step_smoke`.

Step85 does not run `FSIDriver3D`, does not call `driver.run()`, and does not
execute a simulation. It does not edit runtime solver code and does not change
LBM, MPM, coupling, moving-boundary, wall-velocity, geometry-motion, tau, or
bounce-back formulas.

## Planned Step86 Row

```text
row_id = canonical_driver_squid_proxy_static_geometry_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
boundary_motion_mode = static
geometry_motion_mode = static
geometry_motion_application_mode = disabled
wall_velocity_application_mode = disabled
write_vtk = false
write_particles = false
quality_check_enabled = true
quality_check_strict = false
executed_in_step85 = false
planned_for_step86 = true
```

The planned geometry config preserves the accepted Step30 procedural
`squid_proxy` shape semantics, lowers the planned smoke particle count to 1024,
and requires a future Step86 quality report while keeping strict quality checks
off for the planned smoke.

## Guarded Closures

Step85 keeps these features closed:

```text
runtime_geometry_allowed = false
wall_velocity_allowed = false
combined_runtime_geometry_wall_velocity_allowed = false
real_geometry_allowed = false
real_geometry_candidate_data_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
solver_formula_change_allowed = false
tau_migration_allowed = false
physical_validation_claim_allowed = false
production_readiness_claim_allowed = false
real_squid_validation_claim_allowed = false
squid_swimming_claim_allowed = false
squid_actuation_claim_allowed = false
```

## Evidence

Step85 records:

- activation plan evidence in
  `outputs/step85_squid_proxy_static_geometry_activation_plan/`;
- activation guard evidence in
  `outputs/step85_squid_proxy_static_geometry_activation_guard/`;
- Step84 regression evidence in
  `outputs/step85_step84_regression_guard/`;
- Step31/Step30 reference evidence in
  `outputs/step85_step31_reference_guard/`;
- output guard evidence in `outputs/step85_output_guard/`;
- artifact budget evidence in `outputs/step85_artifact_manifest/`.

The only positive Step85 claim is that squid-proxy static-geometry
single-feature smoke is planned and guarded for Step86. Step85 is not real squid
validation, does not validate swimming, and does not establish production
readiness.
