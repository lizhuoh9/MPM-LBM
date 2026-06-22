# Step82 Wall Velocity Solid-Vel Canonical Driver Smoke Goal

## Objective

Implement Step82 as the first post-gate wall-velocity single-feature canonical
driver smoke.

Step82 must run exactly one required canonical `FSIDriver3D.run()` row:

```text
canonical_driver_wall_velocity_solid_vel_32_3step_smoke
```

Step82 may activate exactly one feature:

```text
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
```

Step82 must not activate runtime geometry, combined runtime geometry plus wall
velocity, real geometry, squid proxy behavior, link-area transfer, larger grids,
VTR output, particle NPY output, solver formula changes, tau migration, or
physical-production claims.

## Current Anchor

The required previous state is Step81:

```text
origin/main = daec448a6e63af26caa776d5bb8c0143ef6d75bc
Step81 = Wall Velocity Single-Feature Activation Plan And Guard
Step81 report status = accepted
```

Step81 planned and guarded exactly one future Step82 row:

```text
canonical_driver_wall_velocity_solid_vel_32_3step_smoke
```

Step81 did not run `FSIDriver3D`, did not execute simulation, and had:

```text
step81_activation_feature_count = 0
planned_step82_activation_feature_count = 1
wall_velocity_application_mode_planned_for_step82 = solid_vel_experimental
target_lbm_field_planned_for_step82 = solid_vel
runtime_geometry_planned_for_step82 = false
combined_runtime_geometry_wall_velocity_planned_for_step82 = false
```

## Required Driver Row

Step82 must add and run:

```text
configs/step82_canonical_driver_wall_velocity_solid_vel_32_3step_smoke.json
```

The config must use:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json
boundary_motion_report_enabled = true
wall_velocity_application_mode = solid_vel_experimental
wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json
wall_velocity_application_report_enabled = true
geometry_motion_mode = static
geometry_motion_application_mode = disabled
output_interval = 1
quality_check_enabled = false
quality_check_strict = false
write_vtk = false
write_particles = false
```

Although the Step36 wall-velocity application config derives a synthetic squid
proxy wall-velocity field, the Step82 solver row itself must remain:

```text
geometry_type = box
real_geometry_enabled = false
squid_proxy_enabled = false
```

Step82 tests the canonical `solid_vel` application path only. It is not a squid
geometry run and not real squid validation.

## Runtime Scope

Step82 may:

- call canonical `src.mpm_lbm.sim.drivers.fsi_driver.FSIDriver3D`
- call `driver.run()` for the single required row
- write `diagnostics_timeseries.csv`
- write `diagnostics_timeseries.npz`
- write `driver_config.json`
- write `geo_all_fluid_32.dat`
- write `boundary_motion_interface_report.json`
- write `wall_velocity_application_report.json`
- write Step82 JSON/CSV/log/report/manifest evidence

Step82 must not:

- add optional rows
- run more than the single required row
- enable runtime geometry
- enable combined runtime geometry plus wall velocity
- enable real geometry
- enable squid proxy geometry
- enable link-area transfer
- enable 48^3 or 64^3 grids
- write VTR output
- write particle NPY output
- write dense or sparse wall-velocity NPY output
- write displaced particle output
- write dense displacement output
- modify solver formulas
- modify moving bounce-back formulas
- migrate tau semantics
- claim moving-wall physical validation
- claim real squid validation
- claim production readiness

## Protected Runtime Boundaries

Step82 should not modify:

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

If the Step82 driver row fails, prefer fixing Step82 config/evidence/guard
logic. Do not use Step82 as a reason to change solver runtime behavior.

## Required New Files

Step82 must add:

```text
STEP82_WALL_VELOCITY_SOLID_VEL_CANONICAL_DRIVER_SMOKE_GOAL.md
STEP82_WALL_VELOCITY_SOLID_VEL_CANONICAL_DRIVER_SMOKE_REPORT.md

configs/step82_wall_velocity_solid_vel_smoke_matrix.json
configs/step82_canonical_driver_wall_velocity_solid_vel_32_3step_smoke.json
configs/step82_wall_velocity_solid_vel_acceptance_policy.json
configs/step82_activation_guard_policy.json
configs/step82_output_guard_policy.json
configs/step82_step81_regression_policy.json
configs/step82_artifact_manifest_policy.json

src/mpm_lbm/evidence/step82_wall_velocity_solid_vel_smoke_runner.py
src/mpm_lbm/evidence/step82_wall_velocity_solid_vel_smoke_audit.py
src/mpm_lbm/evidence/step82_wall_velocity_solid_vel_quality_audit.py
src/mpm_lbm/evidence/step82_wall_velocity_solid_vel_activation_guard.py
src/mpm_lbm/evidence/step82_output_guard.py
src/mpm_lbm/evidence/step82_step81_regression_guard.py

baseline_tests/step82_common.py
baseline_tests/run_step82_wall_velocity_solid_vel_smoke_matrix.py
baseline_tests/run_step82_wall_velocity_solid_vel_quality.py
baseline_tests/run_step82_activation_guard.py
baseline_tests/run_step82_output_guard.py
baseline_tests/run_step82_step81_regression_guard.py
baseline_tests/run_step82_artifact_manifest.py

tests/test_step82_wall_velocity_solid_vel_smoke_matrix_contract.py
tests/test_step82_wall_velocity_solid_vel_quality_contract.py
tests/test_step82_activation_guard_contract.py
tests/test_step82_output_guard_contract.py
tests/test_step82_step81_regression_contract.py

docs/82_wall_velocity_solid_vel_canonical_driver_smoke.md
```

Step82 must generate and commit:

```text
outputs/step82_driver_runs/canonical_driver_wall_velocity_solid_vel_32_3step_smoke/
outputs/step82_wall_velocity_solid_vel_smoke_matrix/
outputs/step82_wall_velocity_solid_vel_quality/
outputs/step82_activation_guard/
outputs/step82_output_guard/
outputs/step82_step81_regression_guard/
outputs/step82_artifact_manifest/
logs/step82_*.log
```

Step82 may update:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

## Required Driver Outputs

The required driver run directory is:

```text
outputs/step82_driver_runs/canonical_driver_wall_velocity_solid_vel_32_3step_smoke/
```

Allowed files in that directory:

```text
driver_config.json
geo_all_fluid_32.dat
diagnostics_timeseries.csv
diagnostics_timeseries.npz
boundary_motion_interface_report.json
wall_velocity_application_report.json
```

Forbidden outputs include:

```text
*.vtr
particle*.npy
dense_wall_velocity*.npy
sparse_wall_velocity*.npy
displaced_particles*.npy
dense_displacement*.npy
raw real geometry output
optional driver run dirs
```

## Required Smoke Matrix Artifact

Create:

```text
outputs/step82_wall_velocity_solid_vel_smoke_matrix/wall_velocity_solid_vel_smoke_matrix.json
outputs/step82_wall_velocity_solid_vel_smoke_matrix/wall_velocity_solid_vel_smoke_matrix.csv
outputs/step82_wall_velocity_solid_vel_smoke_matrix/wall_velocity_solid_vel_smoke_matrix_summary.csv
```

The row must prove:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
row_name = canonical_driver_wall_velocity_solid_vel_32_3step_smoke
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
completed_lbm_steps = 3
total_mpm_substeps >= 3
diagnostics_row_count >= 4
has_nan = false
has_inf = false
stable = true
runtime_hard_fail = false
```

The row must prove wall-velocity application:

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

The row must prove boundary-motion report state:

```text
boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path_exists = true
boundary_motion_interface_report_exists = true
boundary_motion_interface_report_pass = true
boundary_motion_diagnostic_only = true
```

The row must prove forbidden features remain off:

```text
runtime_geometry_enabled = false
combined_runtime_geometry_wall_velocity_enabled = false
real_geometry_enabled = false
squid_proxy_enabled = false
link_area_enabled = false
grid_48_enabled = false
grid_64_enabled = false
write_vtk = false
write_particles = false
```

The matrix summary must include and pass:

```text
step82_wall_velocity_solid_vel_smoke_matrix_pass = true
required_row_count = 1
optional_row_count = 0
required_stable_count = 1
activation_feature_count = 1
wall_velocity_enabled_count = 1
runtime_geometry_enabled_count = 0
combined_runtime_geometry_wall_velocity_enabled_count = 0
real_geometry_enabled_count = 0
squid_proxy_enabled_count = 0
link_area_enabled_count = 0
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = wall_velocity_solid_vel_only
```

## Required Quality Artifact

Create:

```text
outputs/step82_wall_velocity_solid_vel_quality/wall_velocity_solid_vel_quality.json
outputs/step82_wall_velocity_solid_vel_quality/wall_velocity_solid_vel_quality.csv
outputs/step82_wall_velocity_solid_vel_quality/wall_velocity_solid_vel_quality_summary.csv
```

The quality summary must include and pass:

```text
step82_wall_velocity_solid_vel_quality_pass = true
wall_velocity_application_report_pass_count = 1
finite_wall_velocity_report_count = 1
capped_wall_velocity_report_count = 1
boundary_motion_interface_report_pass_count = 1
source_matrix_row_count = 1
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

## Required Activation Guard

Create:

```text
outputs/step82_activation_guard/activation_guard.json
outputs/step82_activation_guard/activation_guard.csv
outputs/step82_activation_guard/activation_guard_summary.csv
```

The summary must include and pass:

```text
step82_activation_guard_pass = true
activation_feature_count = 1
wall_velocity_enabled_count = 1
runtime_geometry_enabled_count = 0
combined_runtime_geometry_wall_velocity_enabled_count = 0
real_geometry_enabled_count = 0
squid_proxy_enabled_count = 0
link_area_enabled_count = 0
planned_step82_activation_feature_count = 1
```

## Required Step82 Output Guard

Create:

```text
outputs/step82_output_guard/output_guard.json
outputs/step82_output_guard/output_guard.csv
outputs/step82_output_guard/output_guard_summary.csv
```

The summary must include and pass:

```text
output_guard_pass = true
step82_required_driver_run_dir_count = 1
step82_optional_driver_run_dir_count = 0
step82_vtr_count = 0
step82_particle_npy_count = 0
step82_dense_wall_velocity_output_count = 0
step82_sparse_wall_velocity_output_count = 0
step82_raw_geometry_output_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
```

## Required Step81 Regression Guard

Create:

```text
outputs/step82_step81_regression_guard/step81_regression_guard.json
outputs/step82_step81_regression_guard/step81_regression_guard.csv
outputs/step82_step81_regression_guard/step81_regression_guard_summary.csv
```

The summary must prove:

```text
step82_step81_regression_guard_pass = true
step81_wall_velocity_single_feature_activation_plan_pass = true
step81_wall_velocity_single_feature_activation_guard_pass = true
step81_step80_regression_guard_pass = true
step81_output_guard_pass = true
step81_artifact_budget_pass = true
step81_activation_feature_count = 0
planned_step82_activation_feature_count = 1
step81_driver_run_dir_count = 0
step81_vtr_count = 0
step81_particle_npy_count = 0
```

## Required Artifact Manifest

Create:

```text
outputs/step82_artifact_manifest/artifact_manifest.csv
outputs/step82_artifact_manifest/artifact_summary.csv
outputs/step82_artifact_manifest/artifact_summary.json
```

The manifest summary must pass:

```text
artifact_budget_pass = true
step82_file_count <= configured max_step82_file_count
step82_total_size_mb < configured max_step82_total_size_mb
step82_required_driver_run_dir_count = 1
step82_optional_driver_run_dir_count = 0
step82_vtr_count = 0
step82_particle_npy_count = 0
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step82_file_count = 0
protected_real_geometry_candidates_step82_file_count = 0
raw_geometry_file_count = 0
```

## Required Tests

Add focused Step82 contract tests:

```text
tests/test_step82_wall_velocity_solid_vel_smoke_matrix_contract.py
tests/test_step82_wall_velocity_solid_vel_quality_contract.py
tests/test_step82_activation_guard_contract.py
tests/test_step82_output_guard_contract.py
tests/test_step82_step81_regression_contract.py
```

The tests must inspect committed artifacts and Step82 evidence surfaces. They
must verify the required row, wall-velocity report, quality artifact,
activation guard, output guard, Step81 regression guard, and artifact manifest.

## Required Verification Commands

Run the Step82 baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step82_wall_velocity_solid_vel_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step82_wall_velocity_solid_vel_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step82_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step82_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step82_step81_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step82_artifact_manifest.py
```

Run focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step82_wall_velocity_solid_vel_smoke_matrix_contract.py tests\test_step82_wall_velocity_solid_vel_quality_contract.py tests\test_step82_activation_guard_contract.py tests\test_step82_output_guard_contract.py tests\test_step82_step81_regression_contract.py -q
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

Refresh the Step82 artifact manifest after final verification logs exist.

## Required Report Conclusion

The Step82 report must state:

```text
Step82 accepted.

Step82 runs exactly one required canonical driver row:
canonical_driver_wall_velocity_solid_vel_32_3step_smoke

The row uses 32^3, 1024 particles, 3 LBM steps, 1 MPM substep per LBM step,
moving_boundary, engineering transfer, box geometry, boundary_motion_mode =
prescribed_kinematic, wall_velocity_application_mode = solid_vel_experimental,
and target_lbm_field = solid_vel.

Step82 enables only wall velocity solid_vel experimental application.
Step82 writes wall_velocity_application_report.json.
Step82 writes boundary_motion_interface_report.json.
Step82 applies only to LBM solid_vel.
Step82 does not write LBM populations directly.
Step82 does not modify moving bounce-back formulas.
Step82 does not update MPM state directly.
Step82 does not update projector state.
Step82 does not enable runtime geometry.
Step82 does not enable combined runtime geometry plus wall velocity.
Step82 does not enable real geometry.
Step82 does not enable squid proxy.
Step82 does not enable link-area transfer.
Step82 does not enable 48^3 or 64^3.
Step82 does not write VTR or particle NPY.
Step82 does not claim physical validation or production readiness.
```

## Done Criteria

Step82 is complete only when:

1. The detailed goal file exists and the active goal references it.
2. The single Step82 driver row runs successfully.
3. The smoke matrix, quality, activation guard, output guard, Step81 regression
   guard, artifact manifest, docs, report, logs, and tests exist.
4. Step82 evidence proves exactly one activation feature: wall velocity
   `solid_vel_experimental`.
5. Step82 evidence proves runtime geometry, combined activation, real geometry,
   squid proxy, link area, larger grids, VTR, and particle NPY remain off.
6. Step81 regression artifacts remain green.
7. Focused Step82 tests pass.
8. Full pytest passes with `D:\working\taichi\env\python.exe`.
9. Full pytest passes with `D:\TOOL\Anaconda\python.exe`, or any
   environment-specific failure is reported exactly.
10. `git diff --check` and staged diff checks pass.
11. `external/taichi_LBM3D` and `data/real_geometry_candidates` have no Step82
   edits.
12. The finished work is committed with:

```text
test: add step82 wall velocity solid-vel canonical driver smoke
```

13. The commit is pushed to `origin/main`.
14. The final response reports the commit hash, branch, validation commands,
    pre-push result, and artifact summary.
