# Step92 First User Simulation 10-Step Dry Run Goal

## Starting Point

The required starting point is:

```text
origin/main = 459a55ce56c93d96db6843918fe8ecfb178d80f2
Step90 accepted
Step91 accepted
Step92 not started
```

Step91 is accepted as a plan-and-guard-only step. It did not run
`FSIDriver3D`, did not call `driver.run()`, and did not execute simulation.
Step91 only planned and guarded the Step92 10-step dry-run row.

Step90 is accepted as the predecessor driver run. It completed the same
first-user dry-run envelope at:

```text
32^3
1024 particles
5 LBM steps
1 MPM substep per LBM step
moving_boundary
engineering reaction transfer
squid_proxy procedural geometry
runtime geometry diagnostic_only
wall velocity solid_vel_experimental
target_u_lbm = [0.0, 0.0, 0.0]
```

## Step92 Name

```text
Step92 First User Simulation 10-Step Dry Run
```

Required commit message:

```text
test: add step92 first user simulation 10step dry run
```

## Purpose

Step92 is a real driver run, not a plan/guard step.

Step92 must do exactly one thing:

```text
extend the accepted Step90 first-user simulation dry run from 5 LBM steps to 10 LBM steps
```

The only intended change from Step90 is:

```text
n_lbm_steps: 5 -> 10
```

Everything else must stay inside the Step90 envelope:

```text
n_grid = 32
n_particles = 1024
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
runtime geometry application = diagnostic_only
wall velocity application = solid_vel_experimental
target_lbm_field = solid_vel
write_vtk = false
write_particles = false
```

Step92 may claim only:

```text
first user simulation dry run 32^3 / 10-step passed
```

Step92 must not claim:

```text
real squid validated
squid swimming validated
squid actuation validated
physical validation complete
production ready
grid convergence complete
48^3 ready
64^3 ready
VTR output ready
particle output ready
real geometry candidate data ready
```

## Required Row

Run exactly one required row and no optional rows:

```text
row_id = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run
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
boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json
boundary_motion_report_enabled = true
geometry_motion_mode = prescribed_kinematic
geometry_motion_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_report_enabled = true
geometry_motion_application_mode = diagnostic_only
geometry_motion_application_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_application_report_enabled = true
wall_velocity_application_mode = solid_vel_experimental
wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json
wall_velocity_application_report_enabled = true
target_lbm_field = solid_vel
output_interval = 1
write_vtk = false
write_particles = false
```

## Required Driver Config

Add:

```text
configs/step92_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run.json
```

The config must express the exact row above and must not add 48^3, 64^3, VTR,
particle NPY, link-area transfer, real geometry candidate data, real geometry,
or optional rows.

## Required Files

Step92 must add:

```text
STEP92_FIRST_USER_SIMULATION_10STEP_DRY_RUN_GOAL.md
STEP92_FIRST_USER_SIMULATION_10STEP_DRY_RUN_REPORT.md

configs/step92_first_user_simulation_10step_dry_run_matrix.json
configs/step92_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run.json
configs/step92_first_user_simulation_10step_dry_run_acceptance_policy.json
configs/step92_activation_guard_policy.json
configs/step92_output_guard_policy.json
configs/step92_step91_regression_policy.json
configs/step92_step90_regression_policy.json
configs/step92_step89_regression_policy.json
configs/step92_artifact_manifest_policy.json

src/mpm_lbm/evidence/step92_first_user_simulation_10step_dry_run_runner.py
src/mpm_lbm/evidence/step92_first_user_simulation_10step_dry_run_audit.py
src/mpm_lbm/evidence/step92_first_user_simulation_10step_dry_run_quality_audit.py
src/mpm_lbm/evidence/step92_activation_guard.py
src/mpm_lbm/evidence/step92_output_guard.py
src/mpm_lbm/evidence/step92_step91_regression_guard.py
src/mpm_lbm/evidence/step92_step90_regression_guard.py
src/mpm_lbm/evidence/step92_step89_regression_guard.py

baseline_tests/step92_common.py
baseline_tests/run_step92_first_user_simulation_10step_dry_run_matrix.py
baseline_tests/run_step92_first_user_simulation_10step_dry_run_quality.py
baseline_tests/run_step92_activation_guard.py
baseline_tests/run_step92_output_guard.py
baseline_tests/run_step92_step91_regression_guard.py
baseline_tests/run_step92_step90_regression_guard.py
baseline_tests/run_step92_step89_regression_guard.py
baseline_tests/run_step92_artifact_manifest.py

tests/test_step92_first_user_simulation_10step_dry_run_matrix_contract.py
tests/test_step92_first_user_simulation_10step_dry_run_quality_contract.py
tests/test_step92_activation_guard_contract.py
tests/test_step92_output_guard_contract.py
tests/test_step92_step91_regression_contract.py
tests/test_step92_step90_regression_contract.py
tests/test_step92_step89_regression_contract.py

docs/92_first_user_simulation_10step_dry_run.md

outputs/step92_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run/
outputs/step92_first_user_simulation_10step_dry_run_matrix/
outputs/step92_first_user_simulation_10step_dry_run_quality/
outputs/step92_activation_guard/
outputs/step92_output_guard/
outputs/step92_step91_regression_guard/
outputs/step92_step90_regression_guard/
outputs/step92_step89_regression_guard/
outputs/step92_artifact_manifest/

logs/step92_*.log
```

Step92 may update:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

## Forbidden Edits

Step92 must not modify:

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

If the Step92 run fails, inspect only Step92 config, evidence runner, report
extraction, acceptance bounds, output guard assumptions, and artifact manifest
assumptions first. Do not use Step92 as an excuse to change solver runtime
code or physics formulas.

## Driver Output Policy

Required run directory:

```text
outputs/step92_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run/
```

Allowed files in that run directory:

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

Forbidden outputs:

```text
*.vtr
particle*.npy
dense_wall_velocity*.npy
sparse_wall_velocity*.npy
dense_displacement*.npy
displaced_particles*.npy
raw geometry output
real geometry candidate output
optional driver run dirs
```

## Driver Acceptance Requirements

The executed row must satisfy:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run
n_grid = 32
n_particles = 1024
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
completed_lbm_steps = 10
total_mpm_substeps >= 10
diagnostics_row_count >= 11
has_nan = false
has_inf = false
stable = true
runtime_hard_fail = false
```

Duration-only expansion from Step90 must satisfy:

```text
only_duration_expansion_from_step90 = true
previous_step90_n_lbm_steps = 5
step92_n_lbm_steps = 10
n_grid unchanged from Step90 = 32
n_particles unchanged from Step90 = 1024
geometry_type unchanged from Step90 = squid_proxy
target_u_lbm unchanged from Step90 = [0.0, 0.0, 0.0]
write_vtk unchanged = false
write_particles unchanged = false
```

Squid proxy geometry must satisfy:

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

Runtime geometry diagnostic-only must satisfy:

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

Wall velocity `solid_vel` must satisfy:

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

Boundary motion reporting must satisfy:

```text
boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path_exists = true
boundary_motion_interface_report_exists = true
boundary_motion_interface_report_pass = true
boundary_motion_diagnostic_only = true
```

Combined feature summary must satisfy:

```text
activation_feature_count = 3
squid_proxy_enabled_count = 1
runtime_geometry_enabled_count = 1
wall_velocity_enabled_count = 1
combined_runtime_geometry_wall_velocity_enabled_count = 1
```

The combined count only means the runtime-geometry diagnostic path and
wall-velocity path are both enabled. It is not geometry mutation and is not
physical moving-geometry validation.

The following must remain closed:

```text
real_geometry_candidate_enabled = false
real_geometry_enabled = false
link_area_enabled = false
grid_48_enabled = false
grid_64_enabled = false
write_vtk = false
write_particles = false
```

Numeric dry-run bounds:

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

## Matrix Summary Requirements

The Step92 matrix summary must satisfy:

```text
step92_first_user_simulation_10step_dry_run_matrix_pass = true
required_row_count = 1
optional_row_count = 0
required_stable_count = 1
activation_feature_count = 3
squid_proxy_enabled_count = 1
procedural_geometry_enabled_count = 1
real_geometry_candidate_enabled_count = 0
real_geometry_enabled_count = 0
runtime_geometry_enabled_count = 1
wall_velocity_enabled_count = 1
combined_runtime_geometry_wall_velocity_enabled_count = 1
link_area_enabled_count = 0
min_completed_lbm_steps = 10
min_diagnostics_row_count >= 11
only_duration_expansion_from_step90 = true
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = first_user_10step_dry_run_duration_only
```

## Output Guard Requirements

The Step92 output guard must prove:

```text
output_guard_pass = true
step92_required_driver_run_dir_count = 1
step92_optional_driver_run_dir_count = 0
step92_vtr_count = 0
step92_particle_npy_count = 0
step92_dense_wall_velocity_output_count = 0
step92_sparse_wall_velocity_output_count = 0
step92_dense_displacement_output_count = 0
step92_displaced_particle_output_count = 0
step92_raw_geometry_output_count = 0
step92_real_geometry_candidate_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
artifact_budget_pass = true
```

## Regression Guard Requirements

Step91 regression guard must prove:

```text
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

Step89 regression guard must prove:

```text
step89_first_user_simulation_dry_run_plan_pass = true
step89_first_user_simulation_dry_run_guard_pass = true
step89_output_guard_pass = true
step89_artifact_budget_pass = true
step89_activation_feature_count = 0
planned_step90_activation_feature_count = 3
step89_driver_run_dir_count = 0
step89_vtr_count = 0
step89_particle_npy_count = 0
```

## Runner Requirement

`baseline_tests/run_step92_first_user_simulation_10step_dry_run_matrix.py`
must actually call the canonical driver:

```python
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

config = FSIDriverConfig.from_json(
    "configs/step92_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run.json"
)
driver = FSIDriver3D(
    config,
    "outputs/step92_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run",
)
diagnostics = driver.run()
```

The evidence row must at least record:

```text
driver_run_called
canonical_driver_module
legacy_driver_module_used_as_implementation
completed_lbm_steps
total_mpm_substeps
diagnostics_row_count
only_duration_expansion_from_step90
previous_step90_n_lbm_steps
step92_n_lbm_steps
geometry_type
geometry_config_path_exists
squid_proxy_enabled
procedural_geometry_enabled
real_geometry_candidate_enabled
geometry_quality_report_exists
geometry_quality_report_pass
sampling_particle_count
mantle_particle_count
head_particle_count
arms_particle_count
runtime_geometry_enabled
geometry_motion_application_mode
geometry_motion_interface_report_exists
geometry_motion_interface_report_pass
no_op_pass
mutation_flag_enabled_count
wall_velocity_enabled
wall_velocity_application_mode
wall_velocity_application_report_exists
wall_velocity_application_report_pass
applied_cell_count
max_applied_velocity_norm
cap_pass
finite_pass
lbm_population_update_count
modify_bounceback_formula
boundary_motion_interface_report_exists
boundary_motion_interface_report_pass
combined_runtime_geometry_wall_velocity_enabled
link_area_enabled
write_vtk
write_particles
rho_min_min
rho_max_max
lbm_max_v_max
mpm_min_J_min
mpm_max_speed_max
projected_mass_final
active_cell_count_final
bb_link_count_max
max_grid_reaction_norm_max
has_nan
has_inf
stable
elapsed_seconds
```

## Test Requirements

Step92 must add focused pytest contracts for:

- first user simulation 10-step dry-run matrix;
- first user simulation 10-step dry-run quality;
- activation guard;
- output guard;
- Step91 regression guard;
- Step90 regression guard;
- Step89 regression guard.

The tests should read committed artifacts from `outputs/step92_*` and validate
summary keys. Runtime-heavy imports should remain in baseline runner paths, not
in artifact contract tests.

## Verification Commands

Run Step92 baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step92_first_user_simulation_10step_dry_run_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step92_first_user_simulation_10step_dry_run_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step92_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step92_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step92_step91_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step92_step90_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step92_step89_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step92_artifact_manifest.py
```

Run focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step92_first_user_simulation_10step_dry_run_matrix_contract.py tests\test_step92_first_user_simulation_10step_dry_run_quality_contract.py tests\test_step92_activation_guard_contract.py tests\test_step92_output_guard_contract.py tests\test_step92_step91_regression_contract.py tests\test_step92_step90_regression_contract.py tests\test_step92_step89_regression_contract.py -q
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

`STEP92_FIRST_USER_SIMULATION_10STEP_DRY_RUN_REPORT.md` must state:

```text
Step92 accepted.

Step92 runs exactly one required first-user dry-run row:
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run

The row uses:
32^3
1024 particles
10 LBM steps
1 MPM substep per LBM step
moving_boundary
engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel

The only intended expansion from Step90 is:
n_lbm_steps = 5 -> 10

Step92 enables only:
procedural squid_proxy static geometry
runtime geometry diagnostic-only interface reporting
wall velocity solid_vel experimental application

Step92 writes:
geometry_quality_report.json
geometry_motion_interface_report.json
boundary_motion_interface_report.json
wall_velocity_application_report.json

Step92 does not mutate geometry.
Step92 does not displace MPM particles through runtime geometry.
Step92 does not update LBM solid_phi through runtime geometry.
Step92 does not directly write LBM populations through wall velocity.
Step92 does not modify moving bounce-back formulas.
Step92 does not directly update MPM state through wall velocity.
Step92 does not directly update projector state through wall velocity.
Step92 does not enable real geometry candidate data.
Step92 does not enable link-area transfer.
Step92 does not enable 48^3 or 64^3.
Step92 does not write VTR or particle NPY.
Step92 does not claim squid swimming.
Step92 does not claim real squid validation.
Step92 does not claim physical validation or production readiness.

Correct claim:
first user simulation dry run 32^3 / 10-step passed.
```

## Step93 Direction

If Step92 is green, the next recommended direction is output-path planning, not
another duration jump or a grid-size jump:

```text
Step93 VTR Output Enablement Plan And Guard
Step94 VTR Output Smoke
```

Step93 should still be plan/guard only. Step94 should be the smallest VTR
output smoke. Do not open VTR, particle NPY, 48^3, 64^3, real geometry, or
link-area in Step92.

## Completion Criteria

Step92 is complete only when:

- the active goal references this detailed goal file;
- all Step92 configs, evidence modules, baseline runners, tests, docs, report,
  logs, and output artifacts exist;
- the required Step92 driver row has actually run exactly once;
- no optional row exists or runs;
- Step92 matrix, quality, activation, output, artifact, and regression guards pass;
- focused Step92 pytest passes;
- full trusted Taichi pytest passes;
- full Anaconda pytest passes or an environment-specific failure is documented
  precisely;
- protected runtime/vendor/real-geometry paths remain unchanged;
- changes are committed with `test: add step92 first user simulation 10step dry run`;
- the commit is pushed to `origin/main`;
- the final response reports the pushed commit hash, remote branch,
  verification evidence, and artifact-manifest summary.
