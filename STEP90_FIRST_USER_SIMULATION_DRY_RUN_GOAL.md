# Step90 First User Simulation Dry Run Goal

## Starting Point

The required starting point is:

```text
origin/main = 0a20bb93f784c707c5155fa5105d6cce40b47e6a
Step89 accepted
Step90 not started
```

Step89 planned and guarded the first user simulation dry run for Step90. It did
not run `FSIDriver3D`, did not call `driver.run()`, and did not execute
simulation.

Step90 is the first step after the Step88 three-feature smoke and Step89
plan/guard that should actually execute the planned first-user dry-run row.

## Step90 Name

```text
Step90 First User Simulation Dry Run
```

Commit message:

```text
test: add step90 first user simulation dry run
```

## Step90 Purpose

Step90 must run exactly the one required row planned by Step89:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run
```

Step90's purpose is narrow:

```text
verify that the Step88 three-feature envelope can run as a 32^3 / 1024-particle / 5-LBM-step first user dry run
```

Step90 may claim:

```text
first user simulation dry run 32^3 / 5-step passed
```

Step90 must not claim:

```text
real squid validated
squid swimming validated
squid actuation validated
physical validation complete
production ready
grid convergence complete
real geometry ready
```

## Required Row

Step90 must run exactly one required row and no optional row:

```text
row_id = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run
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

The zero `target_u_lbm` is a Step90 row-local choice inherited from Step89.
It keeps the first user dry run focused on the three-feature envelope instead
of mixing in background-flow or forcing variation.

## Required Driver Config

Add:

```text
configs/step90_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run.json
```

The config must express the exact row above. It must not add 48^3, 64^3, VTR,
particle NPY, link-area transfer, real geometry candidate data, or optional
rows.

## Required Files

Step90 must add:

```text
STEP90_FIRST_USER_SIMULATION_DRY_RUN_GOAL.md
STEP90_FIRST_USER_SIMULATION_DRY_RUN_REPORT.md

configs/step90_first_user_simulation_dry_run_matrix.json
configs/step90_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run.json
configs/step90_first_user_simulation_dry_run_acceptance_policy.json
configs/step90_activation_guard_policy.json
configs/step90_output_guard_policy.json
configs/step90_step89_regression_policy.json
configs/step90_step88_regression_policy.json
configs/step90_step87_regression_policy.json
configs/step90_artifact_manifest_policy.json

src/mpm_lbm/evidence/step90_first_user_simulation_dry_run_runner.py
src/mpm_lbm/evidence/step90_first_user_simulation_dry_run_audit.py
src/mpm_lbm/evidence/step90_first_user_simulation_dry_run_quality_audit.py
src/mpm_lbm/evidence/step90_activation_guard.py
src/mpm_lbm/evidence/step90_output_guard.py
src/mpm_lbm/evidence/step90_step89_regression_guard.py
src/mpm_lbm/evidence/step90_step88_regression_guard.py
src/mpm_lbm/evidence/step90_step87_regression_guard.py

baseline_tests/step90_common.py
baseline_tests/run_step90_first_user_simulation_dry_run_matrix.py
baseline_tests/run_step90_first_user_simulation_dry_run_quality.py
baseline_tests/run_step90_activation_guard.py
baseline_tests/run_step90_output_guard.py
baseline_tests/run_step90_step89_regression_guard.py
baseline_tests/run_step90_step88_regression_guard.py
baseline_tests/run_step90_step87_regression_guard.py
baseline_tests/run_step90_artifact_manifest.py

tests/test_step90_first_user_simulation_dry_run_matrix_contract.py
tests/test_step90_first_user_simulation_dry_run_quality_contract.py
tests/test_step90_activation_guard_contract.py
tests/test_step90_output_guard_contract.py
tests/test_step90_step89_regression_contract.py
tests/test_step90_step88_regression_contract.py
tests/test_step90_step87_regression_contract.py

docs/90_first_user_simulation_dry_run.md

outputs/step90_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run/
outputs/step90_first_user_simulation_dry_run_matrix/
outputs/step90_first_user_simulation_dry_run_quality/
outputs/step90_activation_guard/
outputs/step90_output_guard/
outputs/step90_step89_regression_guard/
outputs/step90_step88_regression_guard/
outputs/step90_step87_regression_guard/
outputs/step90_artifact_manifest/

logs/step90_*.log
```

Step90 may update:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

## Forbidden Edits

Step90 must not modify:

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

If the run fails, inspect the Step90 config, evidence runner, report extraction,
acceptance bounds, output guard assumptions, and artifact manifest assumptions
first. Do not use Step90 as an excuse to change solver runtime code.

## Driver Output Policy

Required run directory:

```text
outputs/step90_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run/
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
row_name = first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run
n_grid = 32
n_particles = 1024
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0.0, 0.0, 0.0]
completed_lbm_steps = 5
total_mpm_substeps >= 5
diagnostics_row_count >= 6
has_nan = false
has_inf = false
stable = true
runtime_hard_fail = false
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

Numeric smoke/dry-run bounds:

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

The matrix summary must satisfy:

```text
step90_first_user_simulation_dry_run_matrix_pass = true
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
min_completed_lbm_steps = 5
min_diagnostics_row_count >= 6
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = first_user_dry_run_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel
```

## Output Guard Requirements

The Step90 output guard must prove:

```text
output_guard_pass = true
step90_required_driver_run_dir_count = 1
step90_optional_driver_run_dir_count = 0
step90_vtr_count = 0
step90_particle_npy_count = 0
step90_dense_wall_velocity_output_count = 0
step90_sparse_wall_velocity_output_count = 0
step90_dense_displacement_output_count = 0
step90_displaced_particle_output_count = 0
step90_raw_geometry_output_count = 0
step90_real_geometry_candidate_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
artifact_budget_pass = true
```

## Regression Guard Requirements

Step89 regression guard must prove:

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

Step88 regression guard must prove:

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

Step87 regression guard must prove:

```text
step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_pass = true
step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard_pass = true
step87_output_guard_pass = true
step87_artifact_budget_pass = true
step87_activation_feature_count = 0
planned_step88_activation_feature_count = 3
step87_driver_run_dir_count = 0
step87_vtr_count = 0
step87_particle_npy_count = 0
```

## Runner Requirement

`baseline_tests/run_step90_first_user_simulation_dry_run_matrix.py` must
actually call the canonical driver:

```python
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

config = FSIDriverConfig.from_json(
    "configs/step90_first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run.json"
)
driver = FSIDriver3D(
    config,
    "outputs/step90_driver_runs/first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run",
)
diagnostics = driver.run()
```

## Test Requirements

Step90 must add focused pytest contracts for:

- first user simulation dry-run matrix;
- first user simulation dry-run quality;
- activation guard;
- output guard;
- Step89 regression guard;
- Step88 regression guard;
- Step87 regression guard.

The tests should read committed artifacts from `outputs/step90_*` and validate
summary keys. Runtime-heavy imports should remain in baseline runner paths, not
in artifact contract tests.

## Verification Commands

Run Step90 baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step90_first_user_simulation_dry_run_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step90_first_user_simulation_dry_run_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step90_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step90_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step90_step89_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step90_step88_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step90_step87_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step90_artifact_manifest.py
```

Run focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step90_first_user_simulation_dry_run_matrix_contract.py tests\test_step90_first_user_simulation_dry_run_quality_contract.py tests\test_step90_activation_guard_contract.py tests\test_step90_output_guard_contract.py tests\test_step90_step89_regression_contract.py tests\test_step90_step88_regression_contract.py tests\test_step90_step87_regression_contract.py -q
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

`STEP90_FIRST_USER_SIMULATION_DRY_RUN_REPORT.md` must state:

```text
Step90 accepted.

Step90 runs exactly one required first-user dry-run row:
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run

The row uses:
32^3
1024 particles
5 LBM steps
1 MPM substep per LBM step
moving_boundary
engineering
target_u_lbm = [0.0, 0.0, 0.0]
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel

Step90 enables only:
procedural squid_proxy static geometry
runtime geometry diagnostic-only interface reporting
wall velocity solid_vel experimental application

Step90 writes:
geometry_quality_report.json
geometry_motion_interface_report.json
boundary_motion_interface_report.json
wall_velocity_application_report.json

Step90 does not mutate geometry.
Step90 does not displace MPM particles through runtime geometry.
Step90 does not update LBM solid_phi through runtime geometry.
Step90 does not directly write LBM populations through wall velocity.
Step90 does not modify moving bounce-back formulas.
Step90 does not directly update MPM state through wall velocity.
Step90 does not directly update projector state through wall velocity.
Step90 does not enable real geometry candidate data.
Step90 does not enable link-area transfer.
Step90 does not enable 48^3 or 64^3.
Step90 does not write VTR or particle NPY.
Step90 does not claim squid swimming.
Step90 does not claim real squid validation.
Step90 does not claim physical validation or production readiness.

Correct claim:
first user simulation dry run 32^3 / 5-step passed.
```

## Completion Criteria

Step90 is complete only when:

- the active goal references this detailed goal file;
- all Step90 configs, evidence modules, baseline runners, tests, docs, report,
  logs, and output artifacts exist;
- the required Step90 driver row has actually run exactly once;
- no optional row exists or runs;
- Step90 matrix, quality, activation, output, artifact, and regression guards pass;
- focused Step90 pytest passes;
- full trusted Taichi pytest passes;
- full Anaconda pytest passes or an environment-specific failure is documented
  precisely;
- protected runtime/vendor/real-geometry paths remain unchanged;
- changes are committed with the required commit message;
- the commit is pushed to `origin/main`;
- final response reports the pushed commit hash and verification evidence.
