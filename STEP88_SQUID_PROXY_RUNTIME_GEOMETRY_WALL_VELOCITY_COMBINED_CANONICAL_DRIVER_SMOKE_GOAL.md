# Step88 Squid Proxy + Runtime Geometry Diagnostic-Only + Wall Velocity Solid-Vel Combined Canonical Driver Smoke Goal

## Objective

Implement Step88 as the first bounded three-feature canonical driver smoke that
combines:

- `geometry_type = squid_proxy` procedural static geometry from Step86.
- runtime geometry `diagnostic_only` interface reporting from Step80/Step84.
- wall velocity `solid_vel_experimental` application reporting from Step82/Step84.

Step88 must run exactly one required `FSIDriver3D.run()` row:

```text
canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

The only valid Step88 claim is:

```text
squid_proxy + runtime geometry diagnostic-only + wall velocity solid_vel combined canonical driver 3-step smoke passed
```

Step88 is not real squid validation, not squid swimming, not physical validation,
not grid convergence, and not production readiness.

## Required Driver Row

The required row must use:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json
geometry_motion_mode = prescribed_kinematic
geometry_motion_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_application_mode = diagnostic_only
geometry_motion_application_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
wall_velocity_application_mode = solid_vel_experimental
wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json
target_lbm_field = solid_vel
output_interval = 1
write_vtk = false
write_particles = false
```

Do not add optional rows.

`target_u_lbm = [0.0, 0.0, 0.0]` is a Step88 row-local choice that isolates the
wall-velocity `solid_vel` application from the default squid_proxy background
flow. Step87 did not freeze `target_u_lbm`; Step88 keeps this as config-only
scope and does not change solver runtime behavior.

## Required New Step Surface

Create or update the Step88 files needed for the same artifact-backed contract
shape used by Step84/Step86/Step87:

```text
STEP88_SQUID_PROXY_RUNTIME_GEOMETRY_WALL_VELOCITY_COMBINED_CANONICAL_DRIVER_SMOKE_GOAL.md
STEP88_SQUID_PROXY_RUNTIME_GEOMETRY_WALL_VELOCITY_COMBINED_CANONICAL_DRIVER_SMOKE_REPORT.md
configs/step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix.json
configs/step88_canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke.json
configs/step88_squid_proxy_runtime_geometry_wall_velocity_combined_acceptance_policy.json
configs/step88_activation_guard_policy.json
configs/step88_output_guard_policy.json
configs/step88_step87_regression_policy.json
configs/step88_step86_regression_policy.json
configs/step88_step84_regression_policy.json
configs/step88_step82_regression_policy.json
configs/step88_step80_regression_policy.json
configs/step88_artifact_manifest_policy.json
src/mpm_lbm/evidence/step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_runner.py
src/mpm_lbm/evidence/step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_audit.py
src/mpm_lbm/evidence/step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality_audit.py
src/mpm_lbm/evidence/step88_squid_proxy_runtime_geometry_wall_velocity_combined_activation_guard.py
src/mpm_lbm/evidence/step88_output_guard.py
src/mpm_lbm/evidence/step88_step87_regression_guard.py
src/mpm_lbm/evidence/step88_step86_regression_guard.py
src/mpm_lbm/evidence/step88_step84_regression_guard.py
src/mpm_lbm/evidence/step88_step82_regression_guard.py
src/mpm_lbm/evidence/step88_step80_regression_guard.py
baseline_tests/step88_common.py
baseline_tests/run_step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix.py
baseline_tests/run_step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality.py
baseline_tests/run_step88_activation_guard.py
baseline_tests/run_step88_output_guard.py
baseline_tests/run_step88_step87_regression_guard.py
baseline_tests/run_step88_step86_regression_guard.py
baseline_tests/run_step88_step84_regression_guard.py
baseline_tests/run_step88_step82_regression_guard.py
baseline_tests/run_step88_step80_regression_guard.py
baseline_tests/run_step88_artifact_manifest.py
tests/test_step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix_contract.py
tests/test_step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality_contract.py
tests/test_step88_activation_guard_contract.py
tests/test_step88_output_guard_contract.py
tests/test_step88_step87_regression_contract.py
tests/test_step88_step86_regression_contract.py
tests/test_step88_step84_regression_contract.py
tests/test_step88_step82_regression_contract.py
tests/test_step88_step80_regression_contract.py
docs/88_squid_proxy_runtime_geometry_wall_velocity_combined_canonical_driver_smoke.md
outputs/step88_driver_runs/canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke/
outputs/step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix/
outputs/step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality/
outputs/step88_activation_guard/
outputs/step88_output_guard/
outputs/step88_step87_regression_guard/
outputs/step88_step86_regression_guard/
outputs/step88_step84_regression_guard/
outputs/step88_step82_regression_guard/
outputs/step88_step80_regression_guard/
outputs/step88_artifact_manifest/
logs/step88_*.log
```

README and status docs may be updated only to describe the accepted Step88
boundary and point at the Step88 report/doc.

## Forbidden Scope

Step88 must not modify solver runtime or diagnostic implementation modules:

```text
src/mpm_lbm/sim/**
src/mpm_lbm/diagnostics/**
src/mpm_lbm/sim/drivers/**
src/mpm_lbm/sim/coupling/**
src/mpm_lbm/sim/lbm/**
src/mpm_lbm/sim/mpm/**
src/mpm_lbm/sim/geometry/**
src/mpm_lbm/sim/motion/**
src/mpm_lbm/sim/wall_velocity/**
external/taichi_LBM3D/**
data/real_geometry_candidates/**
```

If the Step88 run fails, inspect the Step88 config, policy, audit extraction, or
artifact assumptions before considering any runtime solver change. Runtime
solver changes are out of scope for this step.

## Expected Driver Outputs

The required run directory is:

```text
outputs/step88_driver_runs/canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke/
```

Allowed driver-run files are:

```text
boundary_motion_interface_report.json
diagnostics_timeseries.csv
diagnostics_timeseries.npz
driver_config.json
driver_timing.json
geo_all_fluid_32.dat
geometry_motion_interface_report.json
geometry_quality_report.json
wall_velocity_application_report.json
```

The Step88 output guard must reject VTR, particle NPY, dense wall velocity,
sparse wall velocity, dense displacement, displaced-particle, raw geometry,
real-geometry-candidate, private absolute path, protected sim edit, protected
diagnostics edit, protected external edit, and protected real-geometry-candidate
edit outputs.

## Acceptance Requirements

The smoke matrix must pass all of the following:

```text
step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix_pass = true
required_row_count = 1
optional_row_count = 0
required_stable_count = 1
activation_feature_count = 3
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
completed_lbm_steps = 3
total_mpm_substeps >= 3
diagnostics_row_count >= 4
has_nan = false
has_inf = false
runtime_hard_fail = false
stable = true
```

Squid proxy geometry checks:

```text
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
geometry_config_path_exists = true
squid_proxy_enabled = true
procedural_geometry_enabled = true
real_geometry_candidate_enabled = false
real_geometry_enabled = false
geometry_quality_report_exists = true
geometry_quality_report_pass = true
geometry_quality_strict = false
sampling_stats_exist = true
sampling_geometry_type = squid_proxy
sampling_particle_count = 1024
mantle_particle_count > 0
head_particle_count > 0
arms_particle_count > 0
```

Runtime geometry diagnostic-only checks:

```text
runtime_geometry_enabled = true
geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
geometry_motion_config_path_exists = true
geometry_motion_application_config_path_exists = true
geometry_motion_interface_report_exists = true
geometry_motion_interface_report_pass = true
diagnostic_only = true
no_op_pass = true
config_validation_pass = true
mutation_flag_enabled_count = 0
apply_to_driver = false
apply_to_mpm_particles = false
apply_to_lbm_solid_phi = false
apply_to_lbm_solid_vel = false
apply_to_projection = false
update_dynamic_solid = false
recompute_boundary_links = false
mutate_geometry_state = false
```

Wall velocity solid_vel checks:

```text
wall_velocity_enabled = true
wall_velocity_application_mode = solid_vel_experimental
wall_velocity_application_config_path_exists = true
wall_velocity_application_report_exists = true
wall_velocity_application_report_pass = true
target_lbm_field = solid_vel
application_policy = additive_capped
apply_to_lbm_solid_vel = true
apply_to_lbm_populations = false
apply_to_mpm = false
apply_to_projector = false
modify_bounceback_formula = false
jet_model_enabled = false
actuation_claim_enabled = false
applied_cell_count > 0
max_applied_velocity_norm <= wall_velocity_cap_lbm
finite_pass = true
cap_pass = true
lbm_population_update_count = 0
```

Boundary motion checks:

```text
boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path_exists = true
boundary_motion_interface_report_exists = true
boundary_motion_interface_report_pass = true
boundary_motion_diagnostic_only = true
```

Feature closure checks:

```text
squid_proxy_enabled_count = 1
procedural_geometry_enabled_count = 1
runtime_geometry_enabled_count = 1
wall_velocity_enabled_count = 1
combined_runtime_geometry_wall_velocity_enabled_count = 1
real_geometry_candidate_enabled_count = 0
real_geometry_enabled_count = 0
link_area_enabled_count = 0
grid_48_enabled_count = 0
grid_64_enabled_count = 0
write_vtk_count = 0
write_particles_count = 0
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_only
```

Numerical smoke bounds:

```text
rho_min_min > 0.90
rho_max_max < 1.10
lbm_max_v_max < 0.5
mpm_min_J_min > 0.0
mpm_max_speed_max < 10.0
projected_mass_final > 0.0
active_cell_count_final > 0
bb_link_count_max > 0
max_grid_reaction_norm_max finite
```

## Regression Guards

Add Step88 regression guards for Step87, Step86, Step84, Step82, and Step80.
They must confirm that the prior committed artifacts remain in their accepted
roles:

- Step87 remains plan-and-guard only, with zero driver-run directories and
  `planned_step88_activation_feature_count = 3`.
- Step86 remains squid_proxy-only static geometry, with no runtime geometry or
  wall velocity activation.
- Step84 remains runtime geometry plus wall velocity only, with no squid_proxy.
- Step82 remains wall-velocity-only, with no runtime geometry or squid_proxy.
- Step80 remains runtime-geometry-only, with no wall velocity or squid_proxy.

## Verification Commands

Run the Step88 baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step88_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step88_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step88_step87_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step88_step86_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step88_step84_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step88_step82_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step88_step80_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step88_artifact_manifest.py
```

Run focused Step88 tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix_contract.py tests\test_step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality_contract.py tests\test_step88_activation_guard_contract.py tests\test_step88_output_guard_contract.py tests\test_step88_step87_regression_contract.py tests\test_step88_step86_regression_contract.py tests\test_step88_step84_regression_contract.py tests\test_step88_step82_regression_contract.py tests\test_step88_step80_regression_contract.py -q
```

Run full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Run git checks:

```powershell
git diff --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## Report Requirements

The Step88 report must explicitly say that Step88:

- runs exactly one required canonical driver row;
- enables only procedural squid_proxy static geometry, runtime geometry
  diagnostic-only reporting, and wall velocity solid_vel reporting;
- writes geometry quality, geometry motion, boundary motion, and wall velocity
  reports;
- does not mutate geometry;
- does not displace MPM particles through runtime geometry;
- does not update LBM `solid_phi` through runtime geometry;
- does not write LBM populations through wall velocity;
- does not modify moving bounce-back formulas;
- does not directly update MPM or projector state through wall velocity;
- does not enable real geometry candidate data;
- does not enable link-area transfer;
- does not enable 48^3 or 64^3 rows;
- does not write VTR or particle NPY;
- does not claim squid swimming, real squid validation, physical validation, or
  production readiness.

## Completion Criteria

Step88 is complete only when:

- the goal file is checked in;
- the Step88 driver row actually ran through `src.mpm_lbm.sim.drivers.fsi_driver.FSIDriver3D`;
- Step88 matrix, quality, activation, output, regression, and artifact-manifest
  artifacts are generated;
- focused Step88 tests pass;
- full pytest passes with the trusted Taichi interpreter;
- Anaconda full pytest is attempted and passes unless the environment blocks it;
- README/status docs are aligned with Step88;
- protected paths remain clean;
- the final artifact manifest includes the final logs;
- the commit uses:

```text
test: add step88 squid proxy runtime geometry wall velocity combined canonical driver smoke
```

- the commit is pushed to `origin/main`.
