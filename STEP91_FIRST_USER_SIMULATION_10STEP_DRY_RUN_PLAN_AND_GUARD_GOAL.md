# Step91 First User Simulation 10-Step Dry Run Plan And Guard Goal

## Source State

GitHub inspection states the current accepted head is:

```text
origin/main = 72503260933df8919826ef8fa7ed7cab12b96297
commit = test: add step90 first user simulation dry run
```

Step90 is accepted. Step91 is not started.

Step91 must start from the Step90 endpoint and preserve the accepted Step90
boundary:

```text
Step90 accepted row:
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run

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
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
```

Step90 proved only a bounded 32^3 / 1024-particle / 5-step first-user dry run.
It did not prove real squid validation, squid swimming, physical validation,
grid convergence, production readiness, real geometry readiness, VTR readiness,
particle-output readiness, 48^3 readiness, or 64^3 readiness.

## Step91 Name

```text
Step91 First User Simulation 10-Step Dry Run Plan And Guard
```

Commit message after successful implementation and verification:

```text
test: add step91 first user simulation 10step dry run plan and guard
```

## Step91 Objective

Step91 is a plan-and-guard step only.

Step91 must not run a simulation. Its only purpose is to plan and guard the
future Step92 dry run that extends the accepted Step90 envelope from five LBM
steps to ten LBM steps.

Correct Step91 claim:

```text
first user simulation 10-step dry run is planned and guarded for Step92
```

Incorrect Step91 claims:

```text
10-step dry run passed
production simulation ready
physical validation complete
real squid validated
squid swimming works
squid actuation works
grid convergence complete
real geometry ready
```

## Strict No-Simulation Boundary

Step91 must not call or execute:

```text
FSIDriver3D
driver.run()
any simulation
any canonical driver runtime row
```

Step91 must not create:

```text
outputs/step91_driver_runs/
any Step91 VTR output
any Step91 particle NPY output
any Step91 raw geometry output
any Step91 real geometry candidate output
any Step91 dense wall velocity output
any Step91 dense displacement output
```

## Protected Paths

Step91 must not edit:

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

Step91 may add only plan/guard evidence code under:

```text
src/mpm_lbm/evidence/
baseline_tests/
configs/
tests/
docs/
logs/
outputs/
```

and may update existing top-level/docs status files:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

## Explicit Feature Closure

Step91 must not enable:

```text
real geometry candidate data
real geometry mode
link_area transfer
48^3 grid rows
64^3 grid rows
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

## Planned Step92 Row

Step91 must plan exactly one required Step92 row:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run
```

No optional Step92 rows are allowed.

The future Step92 row must be:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 10
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

write_vtk = false
write_particles = false
output_interval = 1
```

The only intended expansion from Step90 to Step92 is:

```text
n_lbm_steps: 5 -> 10
```

Everything else must stay fixed.

## Required New Files

Step91 must add:

```text
STEP91_FIRST_USER_SIMULATION_10STEP_DRY_RUN_PLAN_AND_GUARD_GOAL.md
STEP91_FIRST_USER_SIMULATION_10STEP_DRY_RUN_PLAN_AND_GUARD_REPORT.md

configs/step91_first_user_simulation_10step_dry_run_plan.json
configs/step91_first_user_simulation_10step_dry_run_guard_policy.json
configs/step91_step90_regression_policy.json
configs/step91_step89_regression_policy.json
configs/step91_step88_regression_policy.json
configs/step91_output_guard_policy.json
configs/step91_artifact_manifest_policy.json

src/mpm_lbm/evidence/step91_first_user_simulation_10step_dry_run_plan.py
src/mpm_lbm/evidence/step91_first_user_simulation_10step_dry_run_guard.py
src/mpm_lbm/evidence/step91_step90_regression_guard.py
src/mpm_lbm/evidence/step91_step89_regression_guard.py
src/mpm_lbm/evidence/step91_step88_regression_guard.py
src/mpm_lbm/evidence/step91_output_guard.py

baseline_tests/step91_common.py
baseline_tests/run_step91_first_user_simulation_10step_dry_run_plan.py
baseline_tests/run_step91_first_user_simulation_10step_dry_run_guard.py
baseline_tests/run_step91_step90_regression_guard.py
baseline_tests/run_step91_step89_regression_guard.py
baseline_tests/run_step91_step88_regression_guard.py
baseline_tests/run_step91_output_guard.py
baseline_tests/run_step91_artifact_manifest.py

tests/test_step91_first_user_simulation_10step_dry_run_plan_contract.py
tests/test_step91_first_user_simulation_10step_dry_run_guard_contract.py
tests/test_step91_step90_regression_contract.py
tests/test_step91_step89_regression_contract.py
tests/test_step91_step88_regression_contract.py
tests/test_step91_output_guard_contract.py

docs/91_first_user_simulation_10step_dry_run_plan_and_guard.md

outputs/step91_first_user_simulation_10step_dry_run_plan/
outputs/step91_first_user_simulation_10step_dry_run_guard/
outputs/step91_step90_regression_guard/
outputs/step91_step89_regression_guard/
outputs/step91_step88_regression_guard/
outputs/step91_output_guard/
outputs/step91_artifact_manifest/

logs/step91_*.log
```

Step91 may update:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

## Plan Config Contract

Add:

```text
configs/step91_first_user_simulation_10step_dry_run_plan.json
```

It must encode:

```text
step = Step91
campaign_id = step91_first_user_simulation_10step_dry_run_plan_and_guard
previous_step = Step90
previous_required_commit = 72503260933df8919826ef8fa7ed7cab12b96297

activation_kind = first_user_simulation_10step_dry_run_plan_only
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false

step92_allowed = true
step92_allowed_row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run
step92_allowed_n_grid = 32
step92_allowed_n_particles = 1024
step92_allowed_n_lbm_steps = 10
step92_allowed_mpm_substeps_per_lbm_step = 1
step92_allowed_coupling_mode = moving_boundary
step92_allowed_reaction_transfer_mode = engineering
step92_allowed_output_interval = 1

only_duration_expansion_from_step90 = true
previous_step90_n_lbm_steps = 5
planned_step92_n_lbm_steps = 10

squid_proxy_planned_for_step92 = true
runtime_geometry_planned_for_step92 = true
wall_velocity_planned_for_step92 = true
combined_runtime_geometry_wall_velocity_planned_for_step92 = true
planned_step92_activation_feature_count = 3
step91_activation_feature_count = 0

target_u_lbm_allowed_for_step92 = [0.0, 0.0, 0.0]
target_u_lbm_policy = same_zero_background_flow_as_step90

write_vtk_allowed = false
write_particles_allowed = false
real_geometry_allowed = false
real_geometry_candidate_data_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
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

## Guard Policy Contract

Add:

```text
configs/step91_first_user_simulation_10step_dry_run_guard_policy.json
```

It must verify:

```text
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false

step91_activation_feature_count = 0
planned_step92_activation_feature_count = 3
planned_step92_duration_lbm_steps = 10

only_duration_expansion_from_step90 = true
previous_step90_n_lbm_steps = 5
planned_step92_n_lbm_steps = 10

squid_proxy_planned_for_step92 = true
runtime_geometry_planned_for_step92 = true
wall_velocity_planned_for_step92 = true
combined_runtime_geometry_wall_velocity_planned_for_step92 = true

geometry_motion_application_mode_planned_for_step92 = diagnostic_only
wall_velocity_application_mode_planned_for_step92 = solid_vel_experimental
target_lbm_field_planned_for_step92 = solid_vel
target_u_lbm_allowed_for_step92 = [0.0, 0.0, 0.0]

real_geometry_planned_for_step92 = false
real_geometry_candidate_data_planned_for_step92 = false
link_area_planned_for_step92 = false
write_vtk_planned_for_step92 = false
write_particles_planned_for_step92 = false
```

## Required Evidence Outputs

Plan evidence:

```text
outputs/step91_first_user_simulation_10step_dry_run_plan/first_user_simulation_10step_dry_run_plan.json
outputs/step91_first_user_simulation_10step_dry_run_plan/first_user_simulation_10step_dry_run_plan.csv
outputs/step91_first_user_simulation_10step_dry_run_plan/first_user_simulation_10step_dry_run_plan_summary.csv
```

Plan summary must contain:

```text
step91_first_user_simulation_10step_dry_run_plan_pass = true
previous_step = Step90
previous_commit = 72503260933df8919826ef8fa7ed7cab12b96297
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
step92_allowed = true
step92_allowed_row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run
step92_allowed_n_grid = 32
step92_allowed_n_particles = 1024
step92_allowed_n_lbm_steps = 10
only_duration_expansion_from_step90 = true
previous_step90_n_lbm_steps = 5
planned_step92_n_lbm_steps = 10
squid_proxy_planned_for_step92 = true
runtime_geometry_planned_for_step92 = true
wall_velocity_planned_for_step92 = true
combined_runtime_geometry_wall_velocity_planned_for_step92 = true
target_u_lbm_allowed_for_step92 = [0.0, 0.0, 0.0]
step91_activation_feature_count = 0
planned_step92_activation_feature_count = 3
real_geometry_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
```

Guard evidence:

```text
outputs/step91_first_user_simulation_10step_dry_run_guard/first_user_simulation_10step_dry_run_guard.json
outputs/step91_first_user_simulation_10step_dry_run_guard/first_user_simulation_10step_dry_run_guard.csv
outputs/step91_first_user_simulation_10step_dry_run_guard/first_user_simulation_10step_dry_run_guard_summary.csv
```

Guard summary must contain:

```text
step91_first_user_simulation_10step_dry_run_guard_pass = true
guard_row_count > 0
guard_pass_count = guard_row_count
step91_activation_feature_count = 0
planned_step92_activation_feature_count = 3
planned_step92_duration_lbm_steps = 10
only_duration_expansion_from_step90 = true
squid_proxy_planned_for_step92 = true
runtime_geometry_planned_for_step92 = true
wall_velocity_planned_for_step92 = true
combined_runtime_geometry_wall_velocity_planned_for_step92 = true
geometry_motion_application_mode_planned_for_step92 = diagnostic_only
wall_velocity_application_mode_planned_for_step92 = solid_vel_experimental
target_lbm_field_planned_for_step92 = solid_vel
real_geometry_planned_for_step92 = false
real_geometry_candidate_data_planned_for_step92 = false
link_area_planned_for_step92 = false
write_vtk_planned_for_step92 = false
write_particles_planned_for_step92 = false
```

## Regression Guards

Step91 must add Step90 regression evidence:

```text
outputs/step91_step90_regression_guard/step90_regression_guard.json
outputs/step91_step90_regression_guard/step90_regression_guard.csv
outputs/step91_step90_regression_guard/step90_regression_guard_summary.csv
```

It must confirm:

```text
step90_first_user_simulation_dry_run_matrix_pass = true
step90_first_user_simulation_dry_run_quality_pass = true
step90_activation_guard_pass = true
step90_output_guard_pass = true
step90_step89_regression_guard_pass = true
step90_step88_regression_guard_pass = true
step90_step87_regression_guard_pass = true
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

Step91 must add Step89 regression evidence:

```text
outputs/step91_step89_regression_guard/step89_regression_guard.json
outputs/step91_step89_regression_guard/step89_regression_guard.csv
outputs/step91_step89_regression_guard/step89_regression_guard_summary.csv
```

It must confirm:

```text
step89_first_user_simulation_dry_run_plan_pass = true
step89_first_user_simulation_dry_run_guard_pass = true
step89_step88_regression_guard_pass = true
step89_step87_regression_guard_pass = true
step89_step86_regression_guard_pass = true
step89_output_guard_pass = true
step89_artifact_budget_pass = true
step89_activation_feature_count = 0
planned_step90_activation_feature_count = 3
step89_driver_run_dir_count = 0
step89_vtr_count = 0
step89_particle_npy_count = 0
```

Step91 must add Step88 regression evidence:

```text
outputs/step91_step88_regression_guard/step88_regression_guard.json
outputs/step91_step88_regression_guard/step88_regression_guard.csv
outputs/step91_step88_regression_guard/step88_regression_guard_summary.csv
```

It must confirm:

```text
step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix_pass = true
step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality_pass = true
step88_activation_guard_pass = true
step88_output_guard_pass = true
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

## Output Guard

Step91 must add:

```text
outputs/step91_output_guard/output_guard.json
outputs/step91_output_guard/output_guard.csv
outputs/step91_output_guard/output_guard_summary.csv
```

It must prove:

```text
output_guard_pass = true
step91_driver_run_dir_count = 0
step91_vtr_count = 0
step91_particle_npy_count = 0
step91_raw_geometry_output_count = 0
step91_real_geometry_candidate_output_count = 0
step91_dense_wall_velocity_output_count = 0
step91_sparse_wall_velocity_output_count = 0
step91_dense_displacement_output_count = 0
step91_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step91_large_file_count = 0
```

## Artifact Manifest

Step91 must add:

```text
outputs/step91_artifact_manifest/artifact_manifest.csv
outputs/step91_artifact_manifest/artifact_summary.csv
outputs/step91_artifact_manifest/artifact_summary.json
```

It must prove:

```text
artifact_budget_pass = true
step91_file_count <= 70
step91_total_size_mb < 5
step91_driver_run_dir_count = 0
step91_vtr_count = 0
step91_particle_npy_count = 0
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step91_file_count = 0
protected_real_geometry_candidates_step91_file_count = 0
raw_geometry_file_count = 0
```

## Contract Tests

Add:

```text
tests/test_step91_first_user_simulation_10step_dry_run_plan_contract.py
tests/test_step91_first_user_simulation_10step_dry_run_guard_contract.py
tests/test_step91_step90_regression_contract.py
tests/test_step91_step89_regression_contract.py
tests/test_step91_step88_regression_contract.py
tests/test_step91_output_guard_contract.py
```

They must assert the plan pass, guard pass, Step90/89/88 regression passes,
and output guard pass from committed artifact JSON.

## Required Runners

Add and run:

```text
baseline_tests/run_step91_first_user_simulation_10step_dry_run_plan.py
baseline_tests/run_step91_first_user_simulation_10step_dry_run_guard.py
baseline_tests/run_step91_step90_regression_guard.py
baseline_tests/run_step91_step89_regression_guard.py
baseline_tests/run_step91_step88_regression_guard.py
baseline_tests/run_step91_output_guard.py
baseline_tests/run_step91_artifact_manifest.py
```

Use:

```text
D:\working\taichi\env\python.exe
```

as the trusted verification interpreter.

## Verification Commands

Focused Step91 tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step91_first_user_simulation_10step_dry_run_plan_contract.py tests\test_step91_first_user_simulation_10step_dry_run_guard_contract.py tests\test_step91_step90_regression_contract.py tests\test_step91_step89_regression_contract.py tests\test_step91_step88_regression_contract.py tests\test_step91_output_guard_contract.py -q
```

Full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Git checks:

```powershell
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
git status --short src/mpm_lbm/sim
git status --short src/mpm_lbm/diagnostics
```

## Report Requirements

`STEP91_FIRST_USER_SIMULATION_10STEP_DRY_RUN_PLAN_AND_GUARD_REPORT.md`
must state:

```text
Step91 accepted.

Step91 is a plan-and-guard step only.
Step91 does not run FSIDriver3D.
Step91 does not call driver.run().
Step91 does not execute simulation.
Step91 does not activate the 10-step dry run.

Step91 only plans and guards Step92:
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run

Step92 may run exactly one 32^3 / 1024-particle / 10-step /
moving_boundary / engineering row with:
geometry_type = squid_proxy
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
target_u_lbm = [0.0, 0.0, 0.0]

The only intended expansion from Step90 to Step92 is duration:
n_lbm_steps = 5 -> 10.

Step92 must not enable real geometry candidate data.
Step92 must not enable link-area transfer.
Step92 must not enable 48^3 or 64^3.
Step92 must not write VTR or particle NPY.
Step92 must not change solver formulas.
Step92 must not claim physical validation, squid swimming, real squid validation, or production readiness.
```

## Completion

After all required checks pass:

1. Commit with:

```text
test: add step91 first user simulation 10step dry run plan and guard
```

2. Push to:

```text
origin/main
```

3. Report the final commit hash, remote branch, key pass counts, and artifact
manifest summary.
