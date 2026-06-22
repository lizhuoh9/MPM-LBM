# Step85 Squid Proxy Static Geometry Activation Plan And Guard Report

## Goal

Step85 adds a plan-and-guard layer for one future Step86 static `squid_proxy`
canonical-driver smoke. Step85 does not run `FSIDriver3D`, does not call
`driver.run()`, does not execute simulation, and does not edit runtime solver or
diagnostics code.

## Starting Point

Required starting commit:

```text
29a130ccef93f095deeaa941b44003720f2291c5
```

Step84 remains the accepted predecessor: one combined runtime-geometry
diagnostic-only plus wall-velocity `solid_vel_experimental` 32^3 canonical
driver smoke. Step85 reads committed Step84 evidence only for regression.

## Files Added

Configs:

- `configs/step85_squid_proxy_static_geometry_activation_plan.json`
- `configs/step85_squid_proxy_static_geometry_guard_policy.json`
- `configs/step85_step84_regression_policy.json`
- `configs/step85_step31_reference_policy.json`
- `configs/step85_output_guard_policy.json`
- `configs/step85_artifact_manifest_policy.json`
- `configs/step85_squid_proxy_geometry_1024.json`

Evidence modules:

- `src/mpm_lbm/evidence/step85_squid_proxy_static_geometry_activation_plan.py`
- `src/mpm_lbm/evidence/step85_squid_proxy_static_geometry_activation_guard.py`
- `src/mpm_lbm/evidence/step85_step84_regression_guard.py`
- `src/mpm_lbm/evidence/step85_step31_reference_guard.py`
- `src/mpm_lbm/evidence/step85_output_guard.py`

Baseline runners:

- `baseline_tests/step85_common.py`
- `baseline_tests/run_step85_squid_proxy_static_geometry_activation_plan.py`
- `baseline_tests/run_step85_squid_proxy_static_geometry_activation_guard.py`
- `baseline_tests/run_step85_step84_regression_guard.py`
- `baseline_tests/run_step85_step31_reference_guard.py`
- `baseline_tests/run_step85_output_guard.py`
- `baseline_tests/run_step85_artifact_manifest.py`

Tests:

- `tests/test_step85_squid_proxy_static_geometry_activation_plan_contract.py`
- `tests/test_step85_squid_proxy_static_geometry_activation_guard_contract.py`
- `tests/test_step85_step84_regression_contract.py`
- `tests/test_step85_step31_reference_contract.py`
- `tests/test_step85_output_guard_contract.py`

Docs:

- `docs/85_squid_proxy_static_geometry_activation_plan_and_guard.md`
- `STEP85_SQUID_PROXY_STATIC_GEOMETRY_ACTIVATION_PLAN_AND_GUARD_GOAL.md`

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
```

The row is planned only. Step85 did not run it.

## Evidence Summary

Activation plan:

- `step85_squid_proxy_static_geometry_activation_plan_pass = true`
- `step85_activation_feature_count = 0`
- `planned_step86_activation_feature_count = 1`
- `driver_run_required = false`
- `fsidriver_run_allowed = false`
- `simulation_run_allowed = false`

Activation guard:

- `step85_squid_proxy_static_geometry_activation_guard_pass = true`
- `planned_step86_feature = squid_proxy_static_geometry`
- `geometry_config_path_allowed_for_step86 = configs/step85_squid_proxy_geometry_1024.json`
- `geometry_quality_report_required_for_step86 = true`

Step84 regression guard:

- `step85_step84_regression_guard_pass = true`
- `step84_activation_feature_count = 2`
- `step84_runtime_geometry_enabled_count = 1`
- `step84_wall_velocity_enabled_count = 1`
- `step84_combined_runtime_geometry_wall_velocity_enabled_count = 1`
- `step84_real_geometry_enabled_count = 0`
- `step84_squid_proxy_enabled_count = 0`
- `step84_link_area_enabled_count = 0`
- `step84_vtr_count = 0`
- `step84_particle_npy_count = 0`

Step31 reference guard:

- `step85_step31_reference_guard_pass = true`
- `step30_geometry_type = squid_proxy`
- `step30_deterministic = true`
- `step31_static_driver_reference_exists = true`
- `step31_not_real_squid_validation_claim = true`
- `step31_no_squid_swimming_claim = true`

Output guard:

- `output_guard_pass = true`
- `step85_driver_run_dir_count = 0`
- `step85_vtr_count = 0`
- `step85_particle_npy_count = 0`
- `step85_raw_geometry_output_count = 0`
- `private_absolute_path_count = 0`
- protected runtime, diagnostics, external, and real-geometry edit counts are 0

## Boundaries

Step85 does not validate real squid geometry, squid swimming, squid actuation,
physical correctness, grid convergence, or production readiness. It only plans
and guards one future static `squid_proxy` smoke row for Step86.
