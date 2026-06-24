# Step93 VTR Output Enablement Plan And Guard Goal

## Starting Point

The required starting point is:

```text
origin/main = 40a67ece3b6e8d77fb6356fe5e97dc25a3037372
Step90 accepted
Step91 accepted
Step92 accepted
Step93 not started
```

Step92 is accepted as the current strongest user-facing dry run. It executed
exactly one required first-user row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run
```

Step92's correct claim is only:

```text
first user simulation dry run 32^3 / 10-step passed
```

Step92 did not enable VTR, particle NPY, real geometry candidate data,
link-area transfer, 48^3, 64^3, physical validation, real squid validation,
squid swimming, squid actuation, or production readiness.

## Step93 Name

```text
Step93 VTR Output Enablement Plan And Guard
```

Required commit message:

```text
test: add step93 vtr output enablement plan and guard
```

## Purpose

Step93 is a plan-and-guard-only step. It must not run simulation.

Step93 has exactly one purpose:

```text
establish the plan, boundaries, guard, regression evidence, output guard, and artifact manifest for Step94's minimal VTR output smoke
```

Step93 may claim only:

```text
VTR output enablement is planned and guarded for Step94.
```

Step93 must not claim:

```text
VTR output works
visualization output passed
production output ready
physical validation complete
real squid validated
squid swimming works
squid actuation works
```

## Strict No-Run Boundary

Step93 must not call:

```text
FSIDriver3D
driver.run()
any simulation execution path
```

Step93 must not create a Step93 driver-run directory.

Step93 must not edit:

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

Step93 must not enable:

```text
particle NPY
real geometry candidate data
link_area
48^3
64^3
dense wall velocity output
dense displacement output
solver formula changes
tau migration
physical validation claims
production readiness claims
real squid validation claims
squid swimming claims
squid actuation claims
```

## Planned Step94 Row

Step93 may plan exactly one future Step94 required row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_vtr_smoke
```

Step94 should use one LBM step, not ten. Step92 already proved the
32^3/1024-particle/10-step dry-run duration for this first-user envelope.
Step94's purpose is isolated VTR output-path enablement, so runtime and
artifact size must be minimized.

The planned Step94 row is:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 1
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
geometry_motion_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_application_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_report_enabled = true
geometry_motion_application_report_enabled = true
boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json
boundary_motion_report_enabled = true
wall_velocity_application_mode = solid_vel_experimental
wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json
wall_velocity_application_report_enabled = true
target_lbm_field = solid_vel
write_vtk = true
write_particles = false
output_interval = 1
```

The only intended new feature from Step92 to Step94 is:

```text
write_vtk: false -> true
```

The duration reduction is intentional output-path isolation:

```text
previous_step92_n_lbm_steps = 10
planned_step94_n_lbm_steps = 1
duration_reduction_for_output_isolation = true
vtr_output_smoke_isolation = true
```

This is not a duration regression and not a new physical validation claim.

## Required Files

Step93 must add:

```text
STEP93_VTR_OUTPUT_ENABLEMENT_PLAN_AND_GUARD_GOAL.md
STEP93_VTR_OUTPUT_ENABLEMENT_PLAN_AND_GUARD_REPORT.md

configs/step93_vtr_output_enablement_plan.json
configs/step93_vtr_output_enablement_guard_policy.json
configs/step93_step92_regression_policy.json
configs/step93_step91_regression_policy.json
configs/step93_step90_regression_policy.json
configs/step93_output_guard_policy.json
configs/step93_artifact_manifest_policy.json

src/mpm_lbm/evidence/step93_vtr_output_enablement_plan.py
src/mpm_lbm/evidence/step93_vtr_output_enablement_guard.py
src/mpm_lbm/evidence/step93_step92_regression_guard.py
src/mpm_lbm/evidence/step93_step91_regression_guard.py
src/mpm_lbm/evidence/step93_step90_regression_guard.py
src/mpm_lbm/evidence/step93_output_guard.py

baseline_tests/step93_common.py
baseline_tests/run_step93_vtr_output_enablement_plan.py
baseline_tests/run_step93_vtr_output_enablement_guard.py
baseline_tests/run_step93_step92_regression_guard.py
baseline_tests/run_step93_step91_regression_guard.py
baseline_tests/run_step93_step90_regression_guard.py
baseline_tests/run_step93_output_guard.py
baseline_tests/run_step93_artifact_manifest.py

tests/test_step93_vtr_output_enablement_plan_contract.py
tests/test_step93_vtr_output_enablement_guard_contract.py
tests/test_step93_step92_regression_contract.py
tests/test_step93_step91_regression_contract.py
tests/test_step93_step90_regression_contract.py
tests/test_step93_output_guard_contract.py

docs/93_vtr_output_enablement_plan_and_guard.md

outputs/step93_vtr_output_enablement_plan/
outputs/step93_vtr_output_enablement_guard/
outputs/step93_step92_regression_guard/
outputs/step93_step91_regression_guard/
outputs/step93_step90_regression_guard/
outputs/step93_output_guard/
outputs/step93_artifact_manifest/

logs/step93_*.log
```

Step93 may update:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

## Plan Config Requirements

Add:

```text
configs/step93_vtr_output_enablement_plan.json
```

The plan must include:

```text
step = Step93
campaign_id = step93_vtr_output_enablement_plan_and_guard
previous_step = Step92
previous_required_commit = 40a67ece3b6e8d77fb6356fe5e97dc25a3037372
activation_kind = vtr_output_enablement_plan_only
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
step94_allowed = true
step94_allowed_row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_vtr_smoke
step94_allowed_n_grid = 32
step94_allowed_n_particles = 1024
step94_allowed_n_lbm_steps = 1
step94_allowed_mpm_substeps_per_lbm_step = 1
step94_allowed_coupling_mode = moving_boundary
step94_allowed_reaction_transfer_mode = engineering
step94_allowed_output_interval = 1
vtr_output_planned_for_step94 = true
write_vtk_allowed_for_step94 = true
write_particles_allowed_for_step94 = false
particle_npy_output_allowed = false
vtr_output_smoke_isolation = true
previous_step92_n_lbm_steps = 10
planned_step94_n_lbm_steps = 1
duration_reduction_for_output_isolation = true
only_new_feature_from_step92 = write_vtk
squid_proxy_planned_for_step94 = true
geometry_type_allowed_for_step94 = squid_proxy
geometry_config_path_allowed_for_step94 = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled_allowed_for_step94 = true
quality_check_strict_allowed_for_step94 = false
runtime_geometry_planned_for_step94 = true
geometry_motion_application_mode_allowed_for_step94 = diagnostic_only
wall_velocity_planned_for_step94 = true
wall_velocity_application_mode_allowed_for_step94 = solid_vel_experimental
target_lbm_field_planned_for_step94 = solid_vel
target_u_lbm_allowed_for_step94 = [0.0, 0.0, 0.0]
combined_runtime_geometry_wall_velocity_planned_for_step94 = true
planned_step94_activation_feature_count = 4
step93_activation_feature_count = 0
real_geometry_allowed = false
real_geometry_candidate_data_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
dense_wall_velocity_output_allowed = false
dense_displacement_output_allowed = false
runtime_code_changed = false
solver_behavior_changed = false
solver_formula_change_allowed = false
tau_migration_allowed = false
physical_validation_claim_allowed = false
production_readiness_claim_allowed = false
real_squid_validation_claim_allowed = false
squid_swimming_claim_allowed = false
squid_actuation_claim_allowed = false
```

## Guard Requirements

The guard must prove:

```text
step93_vtr_output_enablement_guard_pass = true
guard_row_count > 0
guard_pass_count = guard_row_count
step93_activation_feature_count = 0
planned_step94_activation_feature_count = 4
vtr_output_planned_for_step94 = true
write_vtk_allowed_for_step94 = true
write_particles_allowed_for_step94 = false
particle_npy_output_allowed = false
squid_proxy_planned_for_step94 = true
runtime_geometry_planned_for_step94 = true
wall_velocity_planned_for_step94 = true
combined_runtime_geometry_wall_velocity_planned_for_step94 = true
real_geometry_planned_for_step94 = false
real_geometry_candidate_data_planned_for_step94 = false
link_area_planned_for_step94 = false
grid_48_planned_for_step94 = false
grid_64_planned_for_step94 = false
```

## Regression Guard Requirements

Step92 regression guard must prove:

```text
step93_step92_regression_guard_pass = true
step92_first_user_simulation_10step_dry_run_matrix_pass = true
step92_first_user_simulation_10step_dry_run_quality_pass = true
step92_activation_guard_pass = true
step92_output_guard_pass = true
step92_step91_regression_guard_pass = true
step92_step90_regression_guard_pass = true
step92_step89_regression_guard_pass = true
step92_artifact_budget_pass = true
step92_activation_feature_count = 3
step92_squid_proxy_enabled_count = 1
step92_runtime_geometry_enabled_count = 1
step92_wall_velocity_enabled_count = 1
step92_combined_runtime_geometry_wall_velocity_enabled_count = 1
step92_real_geometry_candidate_enabled_count = 0
step92_link_area_enabled_count = 0
step92_vtr_count = 0
step92_particle_npy_count = 0
step92_completed_lbm_steps = 10
```

Step91 regression guard must prove:

```text
step93_step91_regression_guard_pass = true
step91_first_user_simulation_10step_dry_run_plan_pass = true
step91_first_user_simulation_10step_dry_run_guard_pass = true
step91_step90_regression_guard_pass = true
step91_step89_regression_guard_pass = true
step91_step88_regression_guard_pass = true
step91_output_guard_pass = true
step91_artifact_budget_pass = true
step91_activation_feature_count = 0
planned_step92_activation_feature_count = 3
step91_driver_run_dir_count = 0
step91_vtr_count = 0
step91_particle_npy_count = 0
```

Step90 regression guard must prove:

```text
step93_step90_regression_guard_pass = true
step90_first_user_simulation_dry_run_matrix_pass = true
step90_first_user_simulation_dry_run_quality_pass = true
step90_activation_guard_pass = true
step90_output_guard_pass = true
step90_artifact_budget_pass = true
step90_activation_feature_count = 3
step90_squid_proxy_enabled_count = 1
step90_runtime_geometry_enabled_count = 1
step90_wall_velocity_enabled_count = 1
step90_combined_runtime_geometry_wall_velocity_enabled_count = 1
step90_real_geometry_candidate_enabled_count = 0
step90_link_area_enabled_count = 0
step90_vtr_count = 0
step90_particle_npy_count = 0
step90_completed_lbm_steps = 5
```

## Output Guard Requirements

Step93 output guard must prove:

```text
output_guard_pass = true
step93_driver_run_dir_count = 0
step93_vtr_count = 0
step93_particle_npy_count = 0
step93_raw_geometry_output_count = 0
step93_real_geometry_candidate_output_count = 0
step93_dense_wall_velocity_output_count = 0
step93_sparse_wall_velocity_output_count = 0
step93_dense_displacement_output_count = 0
step93_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step93_large_file_count = 0
```

## Artifact Manifest Requirements

Step93 artifact manifest must prove:

```text
artifact_budget_pass = true
step93_file_count <= 70
step93_total_size_mb < 5
step93_driver_run_dir_count = 0
step93_vtr_count = 0
step93_particle_npy_count = 0
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step93_file_count = 0
protected_real_geometry_candidates_step93_file_count = 0
raw_geometry_file_count = 0
```

## Test Requirements

Add focused pytest contracts for:

- VTR output enablement plan;
- VTR output enablement guard;
- Step92 regression guard;
- Step91 regression guard;
- Step90 regression guard;
- output guard.

The tests must read committed Step93 artifacts from `outputs/step93_*`. They
must not import heavy runtime packages or call simulation.

## Verification Commands

Run Step93 baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step93_vtr_output_enablement_plan.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step93_vtr_output_enablement_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step93_step92_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step93_step91_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step93_step90_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step93_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step93_artifact_manifest.py
```

Run focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step93_vtr_output_enablement_plan_contract.py tests\test_step93_vtr_output_enablement_guard_contract.py tests\test_step93_step92_regression_contract.py tests\test_step93_step91_regression_contract.py tests\test_step93_step90_regression_contract.py tests\test_step93_output_guard_contract.py -q
```

Run full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Run final git checks:

```powershell
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
git status --short src/mpm_lbm/sim src/mpm_lbm/diagnostics
```

## Report Requirements

`STEP93_VTR_OUTPUT_ENABLEMENT_PLAN_AND_GUARD_REPORT.md` must state:

```text
Step93 accepted.

Step93 is a plan-and-guard step only.
Step93 does not run FSIDriver3D.
Step93 does not call driver.run().
Step93 does not execute simulation.
Step93 does not write VTR output.

Step93 only plans and guards Step94:
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_vtr_smoke

Step94 may run exactly one 32^3 / 1024-particle / 1-step / moving_boundary / engineering row with:
geometry_type = squid_proxy
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
target_u_lbm = [0.0, 0.0, 0.0]
write_vtk = true
write_particles = false

The only new feature from Step92 to Step94 is:
write_vtk = false -> true

The duration reduction from 10 steps to 1 step is intentional VTR-output smoke isolation.
```

The report must also state that Step94 must not enable real geometry candidate
data, link-area transfer, 48^3, 64^3, particle NPY, solver formula changes,
physical validation claims, squid swimming claims, real squid validation
claims, or production readiness claims.

## Step94 Direction

If Step93 is green, Step94 may run:

```text
Step94 VTR Output Smoke
```

Step94's required row is:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_vtr_smoke
```

After Step94, the maximum allowed claim is:

```text
VTR output path can write minimal 32^3 / 1-step visualization artifacts for the first-user envelope.
```

Step94 must still not claim production output readiness, full visualization
campaign readiness, particle output readiness, 48^3/64^3 readiness, or
physical validation completion.

## Completion Criteria

Step93 is complete only when:

- the active goal references this detailed goal file;
- all Step93 configs, evidence modules, baseline runners, tests, docs, report,
  logs, and output artifacts exist;
- no Step93 simulation or driver run exists;
- Step93 plan, guard, output guard, artifact manifest, and regression guards pass;
- focused Step93 pytest passes;
- full trusted Taichi pytest passes;
- full Anaconda pytest passes or an environment-specific failure is documented
  precisely;
- protected runtime/vendor/real-geometry paths remain unchanged;
- changes are committed with `test: add step93 vtr output enablement plan and guard`;
- the commit is pushed to `origin/main`;
- the final response reports the pushed commit hash, remote branch,
  verification evidence, and artifact-manifest summary.
