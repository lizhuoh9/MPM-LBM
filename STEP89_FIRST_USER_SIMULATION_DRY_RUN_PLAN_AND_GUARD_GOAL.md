# Step89 First User Simulation Dry Run Plan And Guard Goal

## Starting Point

The required starting point is:

```text
origin/main = f83ddcd1a0979ed6dbe41c6a9763d891e9c66b9f
Step88 accepted
Step89 not started
```

Step88 accepted the first three-feature canonical-driver smoke row:

```text
canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

Step88 proved only this bounded claim:

```text
squid_proxy + runtime geometry diagnostic-only + wall velocity solid_vel combined canonical driver 3-step smoke passed
```

Step88 did not prove real squid validation, squid swimming, squid actuation,
physical validation, grid convergence, production readiness, longer dry-run
stability, 48^3/64^3 readiness, VTR readiness, or particle-output readiness.

## Step89 Name

```text
Step89 First User Simulation Dry Run Plan And Guard
```

Commit message:

```text
test: add step89 first user simulation dry run plan and guard
```

## Step89 Purpose

Step89 is a plan-and-guard step only. It must not run a simulation.

The purpose of Step89 is to prepare Step90, the first bounded user simulation
dry run, by locking down:

- the single future Step90 row;
- the duration and grid/particle envelope;
- the feature envelope inherited from Step88;
- the output policy;
- the forbidden activations;
- the claim boundary;
- Step88, Step87, and Step86 regression evidence;
- output and artifact-budget guards.

Step89 should convert the Step88 feature-activation smoke result into a
guarded Step90 dry-run plan. It should not execute that plan.

## Correct Step89 Claim

Step89 may claim:

```text
first user simulation dry run is planned and guarded for Step90
```

Step89 must not claim:

```text
first user simulation passed
production simulation ready
physical validation complete
real squid validated
squid swimming works
squid actuation works
```

## Hard Runtime Boundary

Step89 must not run:

```text
FSIDriver3D
driver.run()
any simulation
```

Step89 must not modify:

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

Step89 must not enable:

```text
real geometry candidate data
real geometry validation
link_area transfer
48^3
64^3
VTR output
particle NPY output
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

## Planned Step90 Row

Step89 should allow exactly one future Step90 required row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run
```

The planned Step90 row must be:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]

geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
geometry_quality_report_required = true

geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
geometry_motion_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_application_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_report_enabled = true
geometry_motion_application_report_enabled = true
geometry_mutation_allowed = false

boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json
boundary_motion_report_enabled = true

wall_velocity_application_mode = solid_vel_experimental
wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json
wall_velocity_application_report_enabled = true
target_lbm_field = solid_vel

write_vtk = false
write_particles = false
output_interval = 1
```

`target_u_lbm = [0.0, 0.0, 0.0]` is intentional for Step90 planning. It keeps
the first user dry run focused on the three-feature envelope rather than adding
background-flow or forcing variation in the same step.

## Required Files

Step89 must add:

```text
STEP89_FIRST_USER_SIMULATION_DRY_RUN_PLAN_AND_GUARD_GOAL.md
STEP89_FIRST_USER_SIMULATION_DRY_RUN_PLAN_AND_GUARD_REPORT.md

configs/step89_first_user_simulation_dry_run_plan.json
configs/step89_first_user_simulation_dry_run_guard_policy.json
configs/step89_step88_regression_policy.json
configs/step89_step87_regression_policy.json
configs/step89_step86_regression_policy.json
configs/step89_output_guard_policy.json
configs/step89_artifact_manifest_policy.json

src/mpm_lbm/evidence/step89_first_user_simulation_dry_run_plan.py
src/mpm_lbm/evidence/step89_first_user_simulation_dry_run_guard.py
src/mpm_lbm/evidence/step89_step88_regression_guard.py
src/mpm_lbm/evidence/step89_step87_regression_guard.py
src/mpm_lbm/evidence/step89_step86_regression_guard.py
src/mpm_lbm/evidence/step89_output_guard.py

baseline_tests/step89_common.py
baseline_tests/run_step89_first_user_simulation_dry_run_plan.py
baseline_tests/run_step89_first_user_simulation_dry_run_guard.py
baseline_tests/run_step89_step88_regression_guard.py
baseline_tests/run_step89_step87_regression_guard.py
baseline_tests/run_step89_step86_regression_guard.py
baseline_tests/run_step89_output_guard.py
baseline_tests/run_step89_artifact_manifest.py

tests/test_step89_first_user_simulation_dry_run_plan_contract.py
tests/test_step89_first_user_simulation_dry_run_guard_contract.py
tests/test_step89_step88_regression_contract.py
tests/test_step89_step87_regression_contract.py
tests/test_step89_step86_regression_contract.py
tests/test_step89_output_guard_contract.py

docs/89_first_user_simulation_dry_run_plan_and_guard.md

outputs/step89_first_user_simulation_dry_run_plan/
outputs/step89_first_user_simulation_dry_run_guard/
outputs/step89_step88_regression_guard/
outputs/step89_step87_regression_guard/
outputs/step89_step86_regression_guard/
outputs/step89_output_guard/
outputs/step89_artifact_manifest/

logs/step89_*.log
```

Step89 may update:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

## Plan Config Requirements

`configs/step89_first_user_simulation_dry_run_plan.json` must encode:

```text
step = Step89
campaign_id = step89_first_user_simulation_dry_run_plan_and_guard
previous_step = Step88
previous_required_commit = f83ddcd1a0979ed6dbe41c6a9763d891e9c66b9f
activation_kind = first_user_simulation_dry_run_plan_only
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false

step90_allowed = true
step90_allowed_row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run
step90_allowed_n_grid = 32
step90_allowed_n_particles = 1024
step90_allowed_n_lbm_steps = 5
step90_allowed_mpm_substeps_per_lbm_step = 1
step90_allowed_coupling_mode = moving_boundary
step90_allowed_reaction_transfer_mode = engineering
step90_allowed_output_interval = 1

squid_proxy_planned_for_step90 = true
runtime_geometry_planned_for_step90 = true
wall_velocity_planned_for_step90 = true
combined_runtime_geometry_wall_velocity_planned_for_step90 = true
step89_activation_feature_count = 0
planned_step90_activation_feature_count = 3

target_u_lbm_allowed_for_step90 = [0.0, 0.0, 0.0]
target_u_lbm_policy = row_local_zero_background_flow_for_first_user_dry_run
```

It must also encode every closed boundary:

```text
real_geometry_allowed = false
real_geometry_candidate_data_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
write_vtk_allowed = false
write_particles_allowed = false
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

## Evidence Output Requirements

Step89 must produce:

```text
outputs/step89_first_user_simulation_dry_run_plan/first_user_simulation_dry_run_plan.json
outputs/step89_first_user_simulation_dry_run_plan/first_user_simulation_dry_run_plan.csv
outputs/step89_first_user_simulation_dry_run_plan/first_user_simulation_dry_run_plan_summary.csv

outputs/step89_first_user_simulation_dry_run_guard/first_user_simulation_dry_run_guard.json
outputs/step89_first_user_simulation_dry_run_guard/first_user_simulation_dry_run_guard.csv
outputs/step89_first_user_simulation_dry_run_guard/first_user_simulation_dry_run_guard_summary.csv

outputs/step89_step88_regression_guard/step88_regression_guard.json
outputs/step89_step88_regression_guard/step88_regression_guard.csv
outputs/step89_step88_regression_guard/step88_regression_guard_summary.csv

outputs/step89_step87_regression_guard/step87_regression_guard.json
outputs/step89_step87_regression_guard/step87_regression_guard.csv
outputs/step89_step87_regression_guard/step87_regression_guard_summary.csv

outputs/step89_step86_regression_guard/step86_regression_guard.json
outputs/step89_step86_regression_guard/step86_regression_guard.csv
outputs/step89_step86_regression_guard/step86_regression_guard_summary.csv

outputs/step89_output_guard/output_guard.json
outputs/step89_output_guard/output_guard.csv
outputs/step89_output_guard/output_guard_summary.csv

outputs/step89_artifact_manifest/artifact_manifest.csv
outputs/step89_artifact_manifest/artifact_summary.csv
outputs/step89_artifact_manifest/artifact_summary.json
```

The plan output summary must include:

```text
step89_first_user_simulation_dry_run_plan_pass = true
previous_step = Step88
previous_commit = f83ddcd1a0979ed6dbe41c6a9763d891e9c66b9f
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
step90_allowed = true
step90_allowed_row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run
step90_allowed_n_grid = 32
step90_allowed_n_particles = 1024
step90_allowed_n_lbm_steps = 5
squid_proxy_planned_for_step90 = true
runtime_geometry_planned_for_step90 = true
wall_velocity_planned_for_step90 = true
combined_runtime_geometry_wall_velocity_planned_for_step90 = true
target_u_lbm_allowed_for_step90 = [0.0, 0.0, 0.0]
step89_activation_feature_count = 0
planned_step90_activation_feature_count = 3
real_geometry_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
```

The guard output summary must include:

```text
step89_first_user_simulation_dry_run_guard_pass = true
guard_row_count > 0
guard_pass_count = guard_row_count
step89_activation_feature_count = 0
planned_step90_activation_feature_count = 3
planned_step90_duration_lbm_steps = 5
squid_proxy_planned_for_step90 = true
runtime_geometry_planned_for_step90 = true
wall_velocity_planned_for_step90 = true
combined_runtime_geometry_wall_velocity_planned_for_step90 = true
geometry_motion_application_mode_planned_for_step90 = diagnostic_only
wall_velocity_application_mode_planned_for_step90 = solid_vel_experimental
target_lbm_field_planned_for_step90 = solid_vel
real_geometry_planned_for_step90 = false
real_geometry_candidate_data_planned_for_step90 = false
link_area_planned_for_step90 = false
write_vtk_planned_for_step90 = false
write_particles_planned_for_step90 = false
```

## Regression Guard Requirements

Step89 must verify Step88 remains accepted:

```text
step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix_pass = true
step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality_pass = true
step88_activation_guard_pass = true
step88_output_guard_pass = true
step88_step87_regression_guard_pass = true
step88_step86_regression_guard_pass = true
step88_step84_regression_guard_pass = true
step88_step82_regression_guard_pass = true
step88_step80_regression_guard_pass = true
step88_artifact_budget_pass = true
step88_activation_feature_count = 3
step88_squid_proxy_enabled_count = 1
step88_runtime_geometry_enabled_count = 1
step88_wall_velocity_enabled_count = 1
step88_combined_runtime_geometry_wall_velocity_enabled_count = 1
step88_real_geometry_candidate_enabled_count = 0
step88_link_area_enabled_count = 0
step88_vtr_count = 0
step88_particle_npy_count = 0
```

Step89 must verify Step87 remains accepted:

```text
step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_pass = true
step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard_pass = true
step87_step86_regression_guard_pass = true
step87_step84_regression_guard_pass = true
step87_step82_regression_guard_pass = true
step87_step80_regression_guard_pass = true
step87_output_guard_pass = true
step87_artifact_budget_pass = true
step87_activation_feature_count = 0
planned_step88_activation_feature_count = 3
step87_driver_run_dir_count = 0
step87_vtr_count = 0
step87_particle_npy_count = 0
```

Step89 must verify Step86 remains accepted:

```text
step86_squid_proxy_static_geometry_smoke_matrix_pass = true
step86_squid_proxy_static_geometry_quality_pass = true
step86_activation_guard_pass = true
step86_output_guard_pass = true
step86_artifact_budget_pass = true
step86_activation_feature_count = 1
step86_squid_proxy_enabled_count = 1
step86_runtime_geometry_enabled_count = 0
step86_wall_velocity_enabled_count = 0
step86_vtr_count = 0
step86_particle_npy_count = 0
```

## Output Guard Requirements

Step89 output guard must prove:

```text
output_guard_pass = true
step89_driver_run_dir_count = 0
step89_vtr_count = 0
step89_particle_npy_count = 0
step89_raw_geometry_output_count = 0
step89_real_geometry_candidate_output_count = 0
step89_dense_wall_velocity_output_count = 0
step89_sparse_wall_velocity_output_count = 0
step89_dense_displacement_output_count = 0
step89_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step89_large_file_count = 0
```

Artifact manifest must prove:

```text
artifact_budget_pass = true
step89_file_count <= 70
step89_total_size_mb < 5
step89_driver_run_dir_count = 0
step89_vtr_count = 0
step89_particle_npy_count = 0
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step89_file_count = 0
protected_real_geometry_candidates_step89_file_count = 0
raw_geometry_file_count = 0
```

## Test Requirements

Step89 must add focused pytest contracts for:

- first user simulation dry-run plan;
- first user simulation dry-run guard;
- Step88 regression guard;
- Step87 regression guard;
- Step86 regression guard;
- output guard.

The tests must read committed artifacts from `outputs/step89_*` and validate
the summary keys rather than importing heavy runtime simulation paths.

## Verification Commands

Run Step89 baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step89_first_user_simulation_dry_run_plan.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step89_first_user_simulation_dry_run_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step89_step88_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step89_step87_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step89_step86_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step89_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step89_artifact_manifest.py
```

Run focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step89_first_user_simulation_dry_run_plan_contract.py tests\test_step89_first_user_simulation_dry_run_guard_contract.py tests\test_step89_step88_regression_contract.py tests\test_step89_step87_regression_contract.py tests\test_step89_step86_regression_contract.py tests\test_step89_output_guard_contract.py -q
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

`STEP89_FIRST_USER_SIMULATION_DRY_RUN_PLAN_AND_GUARD_REPORT.md` must state:

```text
Step89 accepted.

Step89 is a plan-and-guard step only.
Step89 does not run FSIDriver3D.
Step89 does not call driver.run().
Step89 does not execute simulation.
Step89 does not activate the first user simulation dry run.

Step89 only plans and guards Step90:
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run

Step90 may run exactly one 32^3 / 1024-particle / 5-step /
moving_boundary / engineering row with:
geometry_type = squid_proxy
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
target_u_lbm = [0.0, 0.0, 0.0]

Step90 must not enable real geometry candidate data.
Step90 must not enable link-area transfer.
Step90 must not enable 48^3 or 64^3.
Step90 must not write VTR or particle NPY.
Step90 must not change solver formulas.
Step90 must not claim physical validation, squid swimming, real squid validation, or production readiness.
```

## Completion Criteria

Step89 is complete only when:

- the active goal references this detailed goal file;
- all Step89 configs, evidence modules, baseline runners, tests, docs, report,
  logs, and output artifacts exist;
- no Step89 code path runs a simulation;
- Step88, Step87, and Step86 regression guards pass;
- output guard and artifact manifest pass;
- focused Step89 pytest passes;
- full trusted Taichi pytest passes;
- full Anaconda pytest passes or an environment-specific failure is documented
  precisely;
- protected runtime/vendor/real-geometry paths remain unchanged;
- changes are committed with the required commit message;
- the commit is pushed to `origin/main`;
- final response reports the pushed commit hash and verification evidence.
