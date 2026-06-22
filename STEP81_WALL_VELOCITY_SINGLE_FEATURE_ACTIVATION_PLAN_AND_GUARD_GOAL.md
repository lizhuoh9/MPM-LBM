# Step81 Wall Velocity Single-Feature Activation Plan And Guard Goal

## Objective

Implement Step81 as a plan-and-guard step only.

Step81 must establish the exact evidence, guard, artifact, documentation, and regression contract that permits Step82 to run one wall-velocity-only canonical driver smoke row later:

```text
canonical_driver_wall_velocity_solid_vel_32_3step_smoke
```

Step81 must not run a simulation. Step81 must not call `FSIDriver3D`, `driver.run()`, Taichi initialization, or any canonical driver. Step81 must not activate wall velocity in runtime. Step81 only records that Step82 may activate wall velocity as one single feature under a bounded 32^3 / 1024-particle / 3-step smoke envelope.

## Current Anchor

The required previous state is Step80:

```text
origin/main = a2fbdfa6a9af0f02901e16e92b276c2055755fe1
Step80 = Runtime Geometry Diagnostic-Only Canonical Driver 3-Step Smoke
Step80 report status = accepted
```

Step80 ran exactly one required canonical driver row:

```text
canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke
```

Step80 proved only runtime geometry diagnostic-only interface reporting. It did not mutate geometry, did not enable wall velocity, did not enable real geometry, did not enable squid proxy, did not enable link-area transfer, did not write VTR, and did not write particle NPY.

## Step81 Scope

Step81 is plan-and-guard only. It may add:

- a Step81 goal file
- a Step81 report file
- Step81 JSON configs
- Step81 evidence builders
- Step81 thin baseline runners
- Step81 contract tests
- Step81 committed outputs
- Step81 committed logs
- Step81 documentation
- status documentation updates

Step81 must not add, remove, or alter solver behavior.

## Explicit Non-Simulation Boundary

Step81 must prove:

```text
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
step81_activation_feature_count = 0
planned_step82_activation_feature_count = 1
```

Step81 source and runner files must not contain:

```text
FSIDriver3D
driver.run(
ti.init(
taichi.init(
```

## Protected Runtime Boundaries

Step81 must not modify:

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

Step81 must not enable:

```text
runtime geometry
combined runtime geometry plus wall velocity
real geometry
squid proxy
link_area
48^3
64^3
VTR
particle NPY
dense wall velocity output
sparse wall velocity output
solver formula changes
tau migration
physical validation claim
production readiness claim
real squid validation claim
```

## Planned Step82 Envelope

Step81 may plan exactly one Step82 row:

```text
row_name = canonical_driver_wall_velocity_solid_vel_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json
wall_velocity_application_mode = solid_vel_experimental
wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json
target_lbm_field = solid_vel
```

Step82 may apply wall velocity only to the LBM `solid_vel` field through the existing experimental wall-velocity application surface:

```text
apply_to_lbm_solid_vel = true
apply_to_lbm_populations = false
apply_to_mpm = false
apply_to_projector = false
modify_bounceback_formula = false
jet_model_enabled = false
actuation_claim_enabled = false
```

Step82 must not combine wall velocity with runtime geometry. Step82 must not enable real geometry, squid proxy, link area, 48^3, 64^3, VTR, particle NPY, solver formula changes, tau migration, or physical/production readiness claims.

## Required New Files

Step81 must add:

```text
STEP81_WALL_VELOCITY_SINGLE_FEATURE_ACTIVATION_PLAN_AND_GUARD_GOAL.md
STEP81_WALL_VELOCITY_SINGLE_FEATURE_ACTIVATION_PLAN_AND_GUARD_REPORT.md

configs/step81_wall_velocity_single_feature_activation_plan.json
configs/step81_wall_velocity_single_feature_guard_policy.json
configs/step81_step80_regression_policy.json
configs/step81_output_guard_policy.json
configs/step81_artifact_manifest_policy.json

src/mpm_lbm/evidence/step81_wall_velocity_single_feature_activation_plan.py
src/mpm_lbm/evidence/step81_wall_velocity_single_feature_activation_guard.py
src/mpm_lbm/evidence/step81_step80_regression_guard.py
src/mpm_lbm/evidence/step81_output_guard.py

baseline_tests/step81_common.py
baseline_tests/run_step81_wall_velocity_single_feature_activation_plan.py
baseline_tests/run_step81_wall_velocity_single_feature_activation_guard.py
baseline_tests/run_step81_step80_regression_guard.py
baseline_tests/run_step81_output_guard.py
baseline_tests/run_step81_artifact_manifest.py

tests/test_step81_wall_velocity_single_feature_activation_plan_contract.py
tests/test_step81_wall_velocity_single_feature_activation_guard_contract.py
tests/test_step81_step80_regression_contract.py
tests/test_step81_output_guard_contract.py

docs/81_wall_velocity_single_feature_activation_plan_and_guard.md
```

Step81 must generate and commit:

```text
outputs/step81_wall_velocity_single_feature_activation_plan/
outputs/step81_wall_velocity_single_feature_activation_guard/
outputs/step81_step80_regression_guard/
outputs/step81_output_guard/
outputs/step81_artifact_manifest/
logs/step81_*.log
```

Step81 may update:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

## Required Activation Plan Artifact

Create:

```text
outputs/step81_wall_velocity_single_feature_activation_plan/wall_velocity_single_feature_activation_plan.json
outputs/step81_wall_velocity_single_feature_activation_plan/wall_velocity_single_feature_activation_plan.csv
outputs/step81_wall_velocity_single_feature_activation_plan/wall_velocity_single_feature_activation_plan_summary.csv
```

The JSON summary must include and pass:

```text
step81_wall_velocity_single_feature_activation_plan_pass = true
previous_step = Step80
previous_commit = a2fbdfa6a9af0f02901e16e92b276c2055755fe1
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
wall_velocity_activation_planned = true
wall_velocity_application_mode_planned_for_step82 = solid_vel_experimental
target_lbm_field_planned_for_step82 = solid_vel
step81_activation_feature_count = 0
planned_step82_activation_feature_count = 1
runtime_geometry_allowed = false
combined_runtime_geometry_wall_velocity_allowed = false
real_geometry_allowed = false
squid_proxy_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
step82_allowed = true
step82_allowed_row_name = canonical_driver_wall_velocity_solid_vel_32_3step_smoke
```

## Required Activation Guard Artifact

Create:

```text
outputs/step81_wall_velocity_single_feature_activation_guard/wall_velocity_single_feature_activation_guard.json
outputs/step81_wall_velocity_single_feature_activation_guard/wall_velocity_single_feature_activation_guard.csv
outputs/step81_wall_velocity_single_feature_activation_guard/wall_velocity_single_feature_activation_guard_summary.csv
```

The JSON summary must include and pass:

```text
step81_wall_velocity_single_feature_activation_guard_pass = true
guard_row_count > 0
guard_pass_count = guard_row_count
step81_activation_feature_count = 0
planned_step82_activation_feature_count = 1
wall_velocity_planned_for_step82 = true
wall_velocity_application_mode_planned_for_step82 = solid_vel_experimental
target_lbm_field_planned_for_step82 = solid_vel
apply_to_lbm_solid_vel_planned_for_step82 = true
apply_to_lbm_populations_planned_for_step82 = false
apply_to_mpm_planned_for_step82 = false
apply_to_projector_planned_for_step82 = false
modify_bounceback_formula_planned_for_step82 = false
jet_model_planned_for_step82 = false
actuation_claim_planned_for_step82 = false
runtime_geometry_planned_for_step82 = false
combined_runtime_geometry_wall_velocity_planned_for_step82 = false
real_geometry_planned_for_step82 = false
squid_proxy_planned_for_step82 = false
link_area_planned_for_step82 = false
write_vtk_planned_for_step82 = false
write_particles_planned_for_step82 = false
```

## Required Step80 Regression Artifact

Create:

```text
outputs/step81_step80_regression_guard/step80_regression_guard.json
outputs/step81_step80_regression_guard/step80_regression_guard.csv
outputs/step81_step80_regression_guard/step80_regression_guard_summary.csv
```

The guard must prove that the accepted Step80 artifacts remain green:

```text
step80_runtime_geometry_diagnostic_only_smoke_matrix_pass = true
step80_runtime_geometry_diagnostic_only_quality_pass = true
step80_runtime_geometry_diagnostic_only_activation_guard_pass = true
step80_output_guard_pass = true
step80_step79_regression_guard_pass = true
step80_artifact_budget_pass = true
step80 activation_feature_count = 1
step80 runtime_geometry_enabled_count = 1
step80 wall_velocity_enabled_count = 0
step80 real_geometry_enabled_count = 0
step80 squid_proxy_enabled_count = 0
step80 link_area_enabled_count = 0
step80 vtr_count = 0
step80 particle_npy_count = 0
```

## Required Step81 Output Guard

Create:

```text
outputs/step81_output_guard/output_guard.json
outputs/step81_output_guard/output_guard.csv
outputs/step81_output_guard/output_guard_summary.csv
```

The output guard summary must prove:

```text
output_guard_pass = true
step81_driver_run_dir_count = 0
step81_vtr_count = 0
step81_particle_npy_count = 0
step81_dense_wall_velocity_output_count = 0
step81_sparse_wall_velocity_output_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step81_large_file_count = 0
```

## Required Artifact Manifest

Create:

```text
outputs/step81_artifact_manifest/artifact_manifest.csv
outputs/step81_artifact_manifest/artifact_summary.csv
outputs/step81_artifact_manifest/artifact_summary.json
```

The artifact manifest summary must pass:

```text
artifact_budget_pass = true
step81_file_count <= configured max_step81_file_count
step81_total_size_mb < configured max_step81_total_size_mb
step81_driver_run_dir_count = 0
step81_vtr_count = 0
step81_particle_npy_count = 0
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step81_file_count = 0
protected_real_geometry_candidates_step81_file_count = 0
```

## Required Tests

Add focused Step81 contract tests that cover:

- activation plan artifact and builder
- activation guard artifact and builder
- Step80 regression guard artifact
- Step81 output guard and artifact manifest
- no Step81 runner/evidence source contains driver or Taichi runtime tokens

The tests must inspect committed artifacts and lightweight evidence builders only. They must not import heavy runtime driver paths unless unavoidable.

## Required Verification Commands

Run the Step81 baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step81_wall_velocity_single_feature_activation_plan.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step81_wall_velocity_single_feature_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step81_step80_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step81_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step81_artifact_manifest.py
```

Run focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step81_wall_velocity_single_feature_activation_plan_contract.py tests\test_step81_wall_velocity_single_feature_activation_guard_contract.py tests\test_step81_step80_regression_contract.py tests\test_step81_output_guard_contract.py -q
```

Run full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Run git safety checks:

```powershell
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Refresh the Step81 artifact manifest after final verification logs exist so the manifest includes the final logs.

## Required Report Conclusion

The Step81 report must state:

```text
Step81 accepted.

Step81 is a plan-and-guard step only.
Step81 does not run FSIDriver3D.
Step81 does not execute a simulation.
Step81 does not activate wall velocity in a driver run.
Step81 does not enable runtime geometry.
Step81 does not enable combined runtime geometry plus wall velocity.
Step81 does not enable real geometry.
Step81 does not enable squid proxy.
Step81 does not enable link-area transfer.
Step81 does not enable 48^3 or 64^3.
Step81 does not write VTR or particle NPY.
Step81 does not change solver formulas.
Step81 does not change tau semantics.
Step81 does not claim physical validation or production readiness.

Step81 only plans and guards Step82:
canonical_driver_wall_velocity_solid_vel_32_3step_smoke
```

## Done Criteria

Step81 is complete only when:

1. The detailed goal file exists and the active goal references it.
2. All required Step81 configs, evidence builders, runners, docs, tests, outputs, logs, and report artifacts exist.
3. Step81 evidence artifacts pass and prove no simulation was run.
4. Step80 regression artifacts remain green.
5. Step81 output and artifact guards pass.
6. README/status docs mention Step81 with the same boundaries as the report.
7. Focused Step81 tests pass.
8. Full pytest passes with `D:\working\taichi\env\python.exe`.
9. Full pytest passes with `D:\TOOL\Anaconda\python.exe`, or any environment-specific failure is reported exactly.
10. `git diff --check` and staged diff checks pass.
11. `external/taichi_LBM3D` and `data/real_geometry_candidates` have no Step81 edits.
12. The finished work is committed with:

```text
test: add step81 wall velocity single-feature activation plan and guard
```

13. The commit is pushed to `origin/main`.
14. The final response reports the commit hash, branch, validation commands, and artifact summary.
