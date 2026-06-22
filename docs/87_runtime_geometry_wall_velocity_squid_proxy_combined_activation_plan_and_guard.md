# Step87 Runtime Geometry Wall Velocity Squid Proxy Combined Activation Plan And Guard

Step87 is a plan-and-guard step for exactly one future Step88 row:
`canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke`.

Step87 does not run `FSIDriver3D`, does not call `driver.run()`, and does not
execute simulation.

## Planned Step88 Row

```text
row_id = canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
executed_in_step87 = false
planned_for_step88 = true
```

The planned row combines the Step86 `squid_proxy` static geometry path with the
Step80/84 runtime geometry diagnostic-only path and the Step82/84 wall velocity
`solid_vel_experimental` path. It remains diagnostic/report-bounded until
Step88 actually runs it.

## Guarded Closures

```text
step87_activation_feature_count = 0
planned_step88_activation_feature_count = 3
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
geometry_mutation_allowed = false
apply_to_lbm_solid_vel_allowed = true
apply_to_lbm_populations_allowed = false
apply_to_mpm_allowed = false
apply_to_projector_allowed = false
modify_bounceback_formula_allowed = false
real_geometry_allowed = false
real_geometry_candidate_data_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
```

Step87 does not validate the combined row. It does not validate squid swimming,
squid actuation, real squid geometry, physical correctness, grid convergence, or
production readiness.

## Evidence

Step87 records:

- activation plan evidence in `outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan/`;
- activation guard evidence in `outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard/`;
- Step86 regression evidence in `outputs/step87_step86_regression_guard/`;
- Step84 regression evidence in `outputs/step87_step84_regression_guard/`;
- Step82 regression evidence in `outputs/step87_step82_regression_guard/`;
- Step80 regression evidence in `outputs/step87_step80_regression_guard/`;
- output guard evidence in `outputs/step87_output_guard/`;
- artifact budget evidence in `outputs/step87_artifact_manifest/`.

The only positive Step87 claim is that the three-feature Step88 smoke is planned
and guarded.
