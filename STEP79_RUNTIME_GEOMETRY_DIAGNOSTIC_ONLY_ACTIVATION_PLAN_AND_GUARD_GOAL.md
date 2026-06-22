# Step79 Runtime Geometry Diagnostic-Only Activation Plan And Guard Goal

## Current Baseline

Step78 is accepted on `origin/main` at:

```text
d226b1fc679f7d5592629a359c56f0b83372a393
test: add step78 minimal post-gate canonical driver 5step rebaseline
```

Step78 established only the minimal post-gate canonical driver 5-step rebaseline:

```text
row_name = canonical_driver_moving_boundary_engineering_32_5step_rebaseline
n_grid = 32
n_particles = 1024
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
```

Step78 did not enable runtime geometry, wall velocity, real geometry, squid proxy, link-area transfer, larger grids, 10-step baseline, VTR output, particle NPY output, tau migration, solver formula changes, physical validation, or production readiness.

## Step79 Name

```text
Step79 Runtime Geometry Diagnostic-Only Single-Feature Activation Plan And Guard
```

Commit message:

```text
test: add step79 runtime geometry diagnostic-only activation plan and guard
```

## Step79 Objective

Step79 must establish the plan, policy, guard, regression evidence, output guard, artifact manifest, tests, and documentation needed to authorize exactly one future Step80 runtime geometry diagnostic-only smoke row.

Step79 is a plan-and-guard step only. It must not run `FSIDriver3D`, must not execute a simulation, must not apply runtime geometry in a solver, must not mutate geometry, and must not change solver behavior.

The only allowed Step79 claim is:

```text
runtime geometry diagnostic-only single-feature activation is planned and guarded for Step80
```

## Forbidden Step79 Claims

Step79 must not claim any of the following:

```text
runtime geometry simulation works
moving geometry works
deforming geometry works
real geometry works
wall velocity works
squid swimming works
physical validation
production readiness
```

## Required Scope Boundaries

Step79 must keep all of the following disabled or forbidden:

```text
FSIDriver3D.run
simulation run
runtime geometry simulation
geometry mutation
solver formula changes
tau migration
wall velocity
combined runtime geometry plus wall velocity
real geometry
squid proxy
link-area transfer
48^3 grid
64^3 grid
10-step baseline
VTR output
particle NPY output
raw geometry artifacts
private absolute paths in artifacts
external/taichi_LBM3D edits
data/real_geometry_candidates edits
```

## Allowed Step80 Plan

Step79 may authorize exactly one future Step80 row:

```text
row_name = canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
geometry_motion_report_required = true
geometry_motion_interface_report_required = true
wall_velocity_application_mode = disabled
boundary_motion_mode = static
write_vtk = false
write_particles = false
```

This future Step80 row is diagnostic-only. Even after Step80, the valid claim must remain limited to the diagnostic driver path, not physical moving-geometry validation.

## Required New Files

Step79 must add these top-level goal/report files:

```text
STEP79_RUNTIME_GEOMETRY_DIAGNOSTIC_ONLY_ACTIVATION_PLAN_AND_GUARD_GOAL.md
STEP79_RUNTIME_GEOMETRY_DIAGNOSTIC_ONLY_ACTIVATION_PLAN_AND_GUARD_REPORT.md
```

Step79 must add these config files:

```text
configs/step79_runtime_geometry_diagnostic_only_activation_plan.json
configs/step79_runtime_geometry_diagnostic_only_guard_policy.json
configs/step79_step78_regression_policy.json
configs/step79_output_guard_policy.json
configs/step79_artifact_manifest_policy.json
```

Step79 must add these evidence modules:

```text
src/mpm_lbm/evidence/step79_runtime_geometry_diagnostic_only_activation_plan.py
src/mpm_lbm/evidence/step79_runtime_geometry_diagnostic_only_activation_guard.py
src/mpm_lbm/evidence/step79_step78_regression_guard.py
src/mpm_lbm/evidence/step79_output_guard.py
```

Step79 must add these baseline runners:

```text
baseline_tests/step79_common.py
baseline_tests/run_step79_runtime_geometry_diagnostic_only_activation_plan.py
baseline_tests/run_step79_runtime_geometry_diagnostic_only_activation_guard.py
baseline_tests/run_step79_step78_regression_guard.py
baseline_tests/run_step79_output_guard.py
baseline_tests/run_step79_artifact_manifest.py
```

Step79 must add these tests:

```text
tests/test_step79_runtime_geometry_diagnostic_only_activation_plan_contract.py
tests/test_step79_runtime_geometry_diagnostic_only_activation_guard_contract.py
tests/test_step79_step78_regression_contract.py
tests/test_step79_output_guard_contract.py
```

Step79 must add this documentation page:

```text
docs/79_runtime_geometry_diagnostic_only_activation_plan_and_guard.md
```

Step79 must generate these evidence output folders:

```text
outputs/step79_runtime_geometry_diagnostic_only_activation_plan/
outputs/step79_runtime_geometry_diagnostic_only_activation_guard/
outputs/step79_step78_regression_guard/
outputs/step79_output_guard/
outputs/step79_artifact_manifest/
```

Step79 must generate `logs/step79_*.log` files for the baseline runners and verification commands that are part of this step.

## Allowed Documentation Updates

Step79 may update only these existing documentation files:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

These documents must state that Step79 does not run `FSIDriver3D`, does not execute runtime geometry simulation, and only plans/guards the future Step80 diagnostic-only runtime geometry smoke.

## Forbidden Modifications

Step79 must not modify:

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

## Activation Plan Contract

`configs/step79_runtime_geometry_diagnostic_only_activation_plan.json` must include the Step78 baseline identity, declare `activation_kind` as `single_feature_plan_only`, declare `feature_under_plan` as `runtime_geometry`, and set:

```text
runtime_geometry_activation_planned = true
runtime_geometry_application_mode_planned_for_step80 = diagnostic_only
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
step80_allowed = true
geometry_motion_mode_allowed_for_step80 = prescribed_kinematic
geometry_motion_application_mode_allowed_for_step80 = diagnostic_only
geometry_mutation_allowed = false
runtime_code_changed = false
solver_behavior_changed = false
solver_formula_change_allowed = false
tau_migration_allowed = false
wall_velocity_allowed = false
combined_runtime_geometry_wall_velocity_allowed = false
real_geometry_allowed = false
squid_proxy_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
physical_validation_claim_allowed = false
production_readiness_claim_allowed = false
real_squid_validation_claim_allowed = false
```

## Guard Policy Contract

`configs/step79_runtime_geometry_diagnostic_only_guard_policy.json` must require the Step78 commit and Step78 evidence passes, then check:

```text
expected_step79_driver_run_required = false
expected_step79_fsidriver_run_allowed = false
expected_step79_simulation_run_allowed = false
expected_runtime_geometry_activation_planned = true
expected_runtime_geometry_application_mode_for_step80 = diagnostic_only
expected_geometry_mutation_allowed = false
expected_solver_formula_change_allowed = false
expected_wall_velocity_allowed = false
expected_combined_runtime_geometry_wall_velocity_allowed = false
expected_real_geometry_allowed = false
expected_squid_proxy_allowed = false
expected_link_area_allowed = false
expected_grid_48_allowed = false
expected_grid_64_allowed = false
expected_vtr_output_allowed = false
expected_particle_npy_output_allowed = false
expected_activation_feature_count_in_step79 = 0
expected_planned_activation_feature_count_for_step80 = 1
```

## Evidence Output Contract

The activation plan output must include:

```text
step79_runtime_geometry_diagnostic_only_activation_plan_pass = true
previous_step = Step78
previous_commit = d226b1fc679f7d5592629a359c56f0b83372a393
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
runtime_geometry_activation_planned = true
runtime_geometry_application_mode_planned_for_step80 = diagnostic_only
geometry_mutation_allowed = false
solver_formula_change_allowed = false
all non-runtime-geometry features disabled
step80_allowed = true
step80_allowed_row_count = 1
step80_allowed_row_name = canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke
```

The activation guard output must include:

```text
step79_runtime_geometry_diagnostic_only_activation_guard_pass = true
guard_pass_count = guard_row_count
step79_activation_feature_count = 0
planned_step80_activation_feature_count = 1
runtime_geometry_planned_for_step80 = true
runtime_geometry_application_mode_planned_for_step80 = diagnostic_only
geometry_mutation_allowed = false
all other feature plans disabled
```

The Step78 regression guard must prove the Step78 matrix, quality, activation guard, output guard, Step77 regression guard, and artifact budget remain accepted, with Step78 activation feature count, optional row count, VTR count, particle NPY count, protected external edit count, and protected real-geometry-candidate edit count all zero.

The output guard must prove Step79 created no driver run directory, VTR, particle NPY, dense displacement output, displaced particles output, raw geometry output, private absolute path, protected external edit, or protected real-geometry-candidate edit.

The artifact manifest must prove:

```text
artifact_budget_pass = true
step79_file_count <= 50
step79_total_size_mb < 5
step79_vtr_count = 0
step79_particle_npy_count = 0
step79_driver_run_dir_count = 0
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step79_file_count = 0
protected_real_geometry_candidates_step79_file_count = 0
raw_geometry_file_count = 0
```

## Required Verification

Run the Step79 baseline runners with the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step79_runtime_geometry_diagnostic_only_activation_plan.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step79_runtime_geometry_diagnostic_only_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step79_step78_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step79_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step79_artifact_manifest.py
```

Run focused Step79 tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step79_runtime_geometry_diagnostic_only_activation_plan_contract.py tests\test_step79_runtime_geometry_diagnostic_only_activation_guard_contract.py tests\test_step79_step78_regression_contract.py tests\test_step79_output_guard_contract.py -q
```

Run full tests with both interpreters when available:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Run git/output checks:

```powershell
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## Required Report Conclusion

The Step79 report must state:

```text
Step79 accepted.
Step79 does not run FSIDriver3D.
Step79 does not execute a simulation.
Step79 does not open runtime geometry simulation.
Step79 does not mutate geometry.
Step79 does not change solver formulas.
Step79 does not enable wall velocity.
Step79 does not enable real geometry.
Step79 does not enable squid proxy.
Step79 does not enable link-area transfer.
Step79 does not enable 48^3 or 64^3.
Step79 does not enable VTR or particle NPY.
Step79 only plans and guards Step80:
canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke
```

## Completion Criteria

Step79 is complete only when:

1. The required config, evidence, runner, test, docs, report, output, and log artifacts exist.
2. The Step79 activation plan and guard pass.
3. The Step78 regression guard passes.
4. The Step79 output guard passes.
5. The Step79 artifact manifest passes within the stated budget.
6. Focused Step79 tests pass.
7. Full pytest passes with the trusted interpreter and the Anaconda interpreter, unless a missing interpreter is reported explicitly.
8. `git diff --check` and `git diff --cached --check` pass.
9. Protected external and real geometry candidate trees remain unchanged.
10. The completed commit is pushed to `origin/main`.
