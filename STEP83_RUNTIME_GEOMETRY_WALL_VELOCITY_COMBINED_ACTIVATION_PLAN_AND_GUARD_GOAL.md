# Step83 Runtime Geometry Wall Velocity Combined Activation Plan And Guard Goal

## Objective

Implement Step83 as a plan-and-guard step only:

```text
Step83 Runtime Geometry Diagnostic-Only + Wall Velocity Combined Activation Plan And Guard
```

Step83 must not run `FSIDriver3D`, must not call `driver.run()`, and must not
execute a simulation. Step83 exists only to plan and guard the future Step84
combined runtime-geometry diagnostic-only plus wall-velocity `solid_vel`
canonical driver smoke.

## Current Anchor

The starting repository state is:

```text
origin/main = 3df6bb25b32d74f16300b8ba603c843eecc725c2
Step80 = accepted
Step81 = accepted
Step82 = accepted
Step83 = not started
```

Step82 is accepted and proves only:

```text
wall velocity solid_vel experimental canonical driver 3-step smoke passed
```

Step82 does not prove combined runtime geometry plus wall velocity, moving-wall
physics, squid swimming, real squid validation, grid convergence, or production
readiness.

## Correct Step83 Claim

Step83 may claim only:

```text
runtime geometry diagnostic-only + wall velocity solid_vel combined smoke is planned and guarded for Step84
```

Step83 must not claim:

```text
combined smoke passed
combined runtime geometry + wall velocity works
moving geometry works
moving-wall physics validated
squid swimming validated
production ready
```

## Strictly Forbidden In Step83

Step83 must not run:

```text
FSIDriver3D
driver.run()
any simulation
```

Step83 must not modify:

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

Step83 must not enable:

```text
real geometry
squid proxy
link_area
48^3
64^3
VTR
particle NPY
dense wall velocity output
dense displacement output
solver formula changes
tau migration
physical validation claims
production readiness claims
```

## Planned Step84 Row

Step83 must plan and guard exactly one future required Step84 row:

```text
canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

The planned Step84 row must have:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
boundary_motion_mode = prescribed_kinematic
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
quality_check_enabled = false
quality_check_strict = false
```

The planned Step84 config paths must be:

```text
geometry_motion_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_application_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json
wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json
```

Step83 should reuse the accepted Step80 diagnostic-only runtime geometry config
and the accepted Step36 `solid_vel_experimental` wall velocity application
config. Step83 must not introduce a new runtime solver config surface.

## Required Files

Add:

```text
STEP83_RUNTIME_GEOMETRY_WALL_VELOCITY_COMBINED_ACTIVATION_PLAN_AND_GUARD_REPORT.md

configs/step83_runtime_geometry_wall_velocity_combined_activation_plan.json
configs/step83_runtime_geometry_wall_velocity_combined_guard_policy.json
configs/step83_step82_regression_policy.json
configs/step83_step80_regression_policy.json
configs/step83_output_guard_policy.json
configs/step83_artifact_manifest_policy.json

src/mpm_lbm/evidence/step83_runtime_geometry_wall_velocity_combined_activation_plan.py
src/mpm_lbm/evidence/step83_runtime_geometry_wall_velocity_combined_activation_guard.py
src/mpm_lbm/evidence/step83_step82_regression_guard.py
src/mpm_lbm/evidence/step83_step80_regression_guard.py
src/mpm_lbm/evidence/step83_output_guard.py

baseline_tests/step83_common.py
baseline_tests/run_step83_runtime_geometry_wall_velocity_combined_activation_plan.py
baseline_tests/run_step83_runtime_geometry_wall_velocity_combined_activation_guard.py
baseline_tests/run_step83_step82_regression_guard.py
baseline_tests/run_step83_step80_regression_guard.py
baseline_tests/run_step83_output_guard.py
baseline_tests/run_step83_artifact_manifest.py

tests/test_step83_runtime_geometry_wall_velocity_combined_activation_plan_contract.py
tests/test_step83_runtime_geometry_wall_velocity_combined_activation_guard_contract.py
tests/test_step83_step82_regression_contract.py
tests/test_step83_step80_regression_contract.py
tests/test_step83_output_guard_contract.py

docs/83_runtime_geometry_wall_velocity_combined_activation_plan_and_guard.md

outputs/step83_runtime_geometry_wall_velocity_combined_activation_plan/
outputs/step83_runtime_geometry_wall_velocity_combined_activation_guard/
outputs/step83_step82_regression_guard/
outputs/step83_step80_regression_guard/
outputs/step83_output_guard/
outputs/step83_artifact_manifest/

logs/step83_*.log
```

Allowed updates:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

## Activation Plan Contract

`configs/step83_runtime_geometry_wall_velocity_combined_activation_plan.json`
must encode:

```text
step = Step83
campaign_id = step83_runtime_geometry_wall_velocity_combined_activation_plan_and_guard
previous_step = Step82
previous_required_commit = 3df6bb25b32d74f16300b8ba603c843eecc725c2
activation_kind = combined_feature_plan_only
features_under_plan = [runtime_geometry_diagnostic_only, wall_velocity_solid_vel]
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
step84_allowed = true
step84_allowed_row_name = canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
step84_allowed_n_grid = 32
step84_allowed_n_particles = 1024
step84_allowed_n_lbm_steps = 3
step84_allowed_mpm_substeps_per_lbm_step = 1
step84_allowed_coupling_mode = moving_boundary
step84_allowed_reaction_transfer_mode = engineering
step84_allowed_geometry_type = box
runtime_geometry_planned_for_step84 = true
geometry_motion_mode_allowed_for_step84 = prescribed_kinematic
geometry_motion_application_mode_allowed_for_step84 = diagnostic_only
geometry_motion_config_path_allowed_for_step84 = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_application_config_path_allowed_for_step84 = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_interface_report_required_for_step84 = true
geometry_mutation_allowed = false
wall_velocity_planned_for_step84 = true
boundary_motion_mode_allowed_for_step84 = prescribed_kinematic
boundary_motion_config_path_allowed_for_step84 = configs/step34_boundary_motion_interface_prescribed_kinematic.json
wall_velocity_application_mode_allowed_for_step84 = solid_vel_experimental
wall_velocity_application_config_path_allowed_for_step84 = configs/step36_wall_velocity_application_solid_vel_experimental.json
wall_velocity_application_report_required_for_step84 = true
target_lbm_field_planned_for_step84 = solid_vel
combined_runtime_geometry_wall_velocity_planned_for_step84 = true
planned_step84_activation_feature_count = 2
step83_activation_feature_count = 0
apply_to_lbm_solid_vel_allowed = true
apply_to_lbm_populations_allowed = false
apply_to_mpm_allowed = false
apply_to_projector_allowed = false
modify_bounceback_formula_allowed = false
jet_model_allowed = false
actuation_claim_allowed = false
real_geometry_allowed = false
squid_proxy_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
runtime_code_changed = false
solver_behavior_changed = false
solver_formula_change_allowed = false
tau_migration_allowed = false
physical_validation_claim_allowed = false
production_readiness_claim_allowed = false
real_squid_validation_claim_allowed = false
```

## Required Evidence Outputs

The activation plan output must be:

```text
outputs/step83_runtime_geometry_wall_velocity_combined_activation_plan/runtime_geometry_wall_velocity_combined_activation_plan.json
outputs/step83_runtime_geometry_wall_velocity_combined_activation_plan/runtime_geometry_wall_velocity_combined_activation_plan.csv
outputs/step83_runtime_geometry_wall_velocity_combined_activation_plan/runtime_geometry_wall_velocity_combined_activation_plan_summary.csv
```

Its summary must include:

```text
step83_runtime_geometry_wall_velocity_combined_activation_plan_pass = true
previous_step = Step82
previous_commit = 3df6bb25b32d74f16300b8ba603c843eecc725c2
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
runtime_geometry_planned_for_step84 = true
geometry_motion_application_mode_allowed_for_step84 = diagnostic_only
geometry_mutation_allowed = false
wall_velocity_planned_for_step84 = true
wall_velocity_application_mode_allowed_for_step84 = solid_vel_experimental
target_lbm_field_planned_for_step84 = solid_vel
combined_runtime_geometry_wall_velocity_planned_for_step84 = true
step83_activation_feature_count = 0
planned_step84_activation_feature_count = 2
real_geometry_allowed = false
squid_proxy_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
step84_allowed = true
step84_allowed_row_name = canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

The activation guard output must be:

```text
outputs/step83_runtime_geometry_wall_velocity_combined_activation_guard/runtime_geometry_wall_velocity_combined_activation_guard.json
outputs/step83_runtime_geometry_wall_velocity_combined_activation_guard/runtime_geometry_wall_velocity_combined_activation_guard.csv
outputs/step83_runtime_geometry_wall_velocity_combined_activation_guard/runtime_geometry_wall_velocity_combined_activation_guard_summary.csv
```

Its summary must include:

```text
step83_runtime_geometry_wall_velocity_combined_activation_guard_pass = true
guard_row_count > 0
guard_pass_count = guard_row_count
step83_activation_feature_count = 0
planned_step84_activation_feature_count = 2
runtime_geometry_planned_for_step84 = true
runtime_geometry_application_mode_planned_for_step84 = diagnostic_only
geometry_mutation_allowed = false
wall_velocity_planned_for_step84 = true
wall_velocity_application_mode_planned_for_step84 = solid_vel_experimental
apply_to_lbm_solid_vel_planned_for_step84 = true
apply_to_lbm_populations_planned_for_step84 = false
modify_bounceback_formula_planned_for_step84 = false
combined_runtime_geometry_wall_velocity_planned_for_step84 = true
real_geometry_planned_for_step84 = false
squid_proxy_planned_for_step84 = false
link_area_planned_for_step84 = false
write_vtk_planned_for_step84 = false
write_particles_planned_for_step84 = false
```

The Step82 regression guard must prove:

```text
step82_wall_velocity_solid_vel_smoke_matrix_pass = true
step82_wall_velocity_solid_vel_quality_pass = true
step82_activation_guard_pass = true
step82_step81_regression_guard_pass = true
step82_output_guard_pass = true
step82_artifact_budget_pass = true
step82_activation_feature_count = 1
step82_wall_velocity_enabled_count = 1
step82_runtime_geometry_enabled_count = 0
step82_combined_runtime_geometry_wall_velocity_enabled_count = 0
step82_real_geometry_enabled_count = 0
step82_squid_proxy_enabled_count = 0
step82_link_area_enabled_count = 0
step82_vtr_count = 0
step82_particle_npy_count = 0
```

The Step80 regression guard must prove:

```text
step80_runtime_geometry_diagnostic_only_smoke_matrix_pass = true
step80_runtime_geometry_diagnostic_only_quality_pass = true
step80_activation_guard_pass = true
step80_output_guard_pass = true
step80_step79_regression_guard_pass = true
step80_artifact_budget_pass = true
step80_activation_feature_count = 1
step80_runtime_geometry_enabled_count = 1
step80_wall_velocity_enabled_count = 0
step80_combined_runtime_geometry_wall_velocity_enabled_count = 0
step80_real_geometry_enabled_count = 0
step80_squid_proxy_enabled_count = 0
step80_link_area_enabled_count = 0
step80_vtr_count = 0
step80_particle_npy_count = 0
```

The output guard must prove:

```text
output_guard_pass = true
step83_driver_run_dir_count = 0
step83_vtr_count = 0
step83_particle_npy_count = 0
step83_dense_wall_velocity_output_count = 0
step83_sparse_wall_velocity_output_count = 0
step83_dense_displacement_output_count = 0
step83_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step83_large_file_count = 0
```

The artifact manifest must prove:

```text
artifact_budget_pass = true
step83_file_count <= 55
step83_total_size_mb < 5
step83_driver_run_dir_count = 0
step83_vtr_count = 0
step83_particle_npy_count = 0
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step83_file_count = 0
protected_real_geometry_candidates_step83_file_count = 0
raw_geometry_file_count = 0
```

## Required Tests

Add focused contract tests:

```text
tests/test_step83_runtime_geometry_wall_velocity_combined_activation_plan_contract.py
tests/test_step83_runtime_geometry_wall_velocity_combined_activation_guard_contract.py
tests/test_step83_step82_regression_contract.py
tests/test_step83_step80_regression_contract.py
tests/test_step83_output_guard_contract.py
```

These tests must assert the artifact summaries, plan boundaries, no-driver
source boundaries, regression guard pass counts, and output/artifact budgets.

## Required Verification

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step83_runtime_geometry_wall_velocity_combined_activation_plan.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step83_runtime_geometry_wall_velocity_combined_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step83_step82_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step83_step80_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step83_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step83_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step83_runtime_geometry_wall_velocity_combined_activation_plan_contract.py tests\test_step83_runtime_geometry_wall_velocity_combined_activation_guard_contract.py tests\test_step83_step82_regression_contract.py tests\test_step83_step80_regression_contract.py tests\test_step83_output_guard_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Refresh Step83 output guard and artifact manifest after final pytest logs exist.

## Commit And Push

Commit message:

```text
test: add step83 runtime geometry wall velocity combined activation plan and guard
```

Push to:

```text
origin main
```

The final response must report the final commit hash, remote branch, key
verification results, and the fact that Step83 remains plan-and-guard only.

## Done Criteria

Step83 is complete only when:

```text
step83_runtime_geometry_wall_velocity_combined_activation_plan_pass = true
step83_runtime_geometry_wall_velocity_combined_activation_guard_pass = true
step83_step82_regression_guard_pass = true
step83_step80_regression_guard_pass = true
output_guard_pass = true
artifact_budget_pass = true
focused Step83 pytest passes
full pytest passes with D:\working\taichi\env\python.exe
full pytest passes with D:\TOOL\Anaconda\python.exe
git diff --check passes
git diff --cached --check passes
protected external and real-geometry paths are clean
commit is pushed to origin/main
local HEAD matches origin/main
```

Step83 must remain strictly bounded as plan-and-guard evidence for Step84.
