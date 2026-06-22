# Step80 Runtime Geometry Diagnostic-Only Canonical Driver Smoke Goal

## Current Baseline

GitHub `origin/main` is already past Step78 and includes accepted Step79:

```text
268097498fab74645bf563dad89bdee9d08b900c
test: add step79 runtime geometry diagnostic-only activation plan and guard
```

Step79 is accepted and authorizes exactly one future Step80 runtime geometry
diagnostic-only row:

```text
canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke
```

Step79 remains a plan-and-guard step only. It did not run `FSIDriver3D`, did not
execute simulation, did not mutate geometry, and did not change solver formulas.

## Step80 Name

```text
Step80 Runtime Geometry Diagnostic-Only Canonical Driver 3-Step Smoke
```

Commit message:

```text
test: add step80 runtime geometry diagnostic-only canonical driver smoke
```

## Objective

Step80 must run exactly one canonical driver row that enables only the runtime
geometry diagnostic-only interface path. The run must prove the canonical driver
can load the geometry motion diagnostic-only config, write
`geometry_motion_interface_report.json`, complete three LBM steps, and keep the
diagnostic-only no-op/mutation contract intact.

The correct Step80 claim is:

```text
runtime geometry diagnostic-only driver path smoke passed
```

Step80 must not claim:

```text
runtime deforming geometry works
moving geometry physically validated
squid geometry motion validated
real geometry validated
wall velocity validated
physical validation
production readiness
```

## Required Row

Step80 must run one required row and no optional rows:

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
boundary_motion_mode = static
wall_velocity_application_mode = disabled
write_vtk = false
write_particles = false
quality_check_enabled = false
quality_check_strict = false
```

## Diagnostic-Only Geometry Motion Contract

Step80 uses the accepted Step43 geometry motion interface semantics:

```text
application_mode = diagnostic_only
diagnostic_only = true
apply_to_driver = false
apply_to_mpm_particles = false
apply_to_lbm_solid_phi = false
apply_to_lbm_solid_vel = false
apply_to_projection = false
update_dynamic_solid = false
recompute_boundary_links = false
mutate_geometry_state = false
mutation_flag_enabled_count = 0
no_op_pass = true
```

The driver output must include:

```text
outputs/step80_driver_runs/canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke/geometry_motion_interface_report.json
```

The report proves interface loading and no-op validation only. It must not be
interpreted as geometry mutation, moving mesh validation, or physical runtime
geometry simulation.

## Implementation Boundary

Step80 may add Step80 configs, evidence modules, baseline runners, contract
tests, docs, reports, logs, and evidence artifacts.

Step80 must not modify:

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

If Step80 fails because a config or evidence runner is wrong, fix the
config/evidence layer. Do not change solver runtime or formulas.

## Required New Files

Top-level goal/report:

```text
STEP80_RUNTIME_GEOMETRY_DIAGNOSTIC_ONLY_CANONICAL_DRIVER_SMOKE_GOAL.md
STEP80_RUNTIME_GEOMETRY_DIAGNOSTIC_ONLY_CANONICAL_DRIVER_SMOKE_REPORT.md
```

Configs:

```text
configs/step80_runtime_geometry_diagnostic_only_smoke_matrix.json
configs/step80_canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke.json
configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
configs/step80_runtime_geometry_diagnostic_only_acceptance_policy.json
configs/step80_activation_guard_policy.json
configs/step80_output_guard_policy.json
configs/step80_step79_regression_policy.json
configs/step80_artifact_manifest_policy.json
```

The `step80_geometry_motion_interface_prescribed_diagnostic_only.json` config
must preserve the Step43 no-op flags and use repository-rooted relative paths
without private absolute paths.

Evidence modules:

```text
src/mpm_lbm/evidence/step80_runtime_geometry_diagnostic_only_smoke_runner.py
src/mpm_lbm/evidence/step80_runtime_geometry_diagnostic_only_smoke_audit.py
src/mpm_lbm/evidence/step80_runtime_geometry_diagnostic_only_quality_audit.py
src/mpm_lbm/evidence/step80_runtime_geometry_diagnostic_only_activation_guard.py
src/mpm_lbm/evidence/step80_output_guard.py
src/mpm_lbm/evidence/step80_step79_regression_guard.py
```

Baseline runners:

```text
baseline_tests/step80_common.py
baseline_tests/run_step80_runtime_geometry_diagnostic_only_smoke_matrix.py
baseline_tests/run_step80_runtime_geometry_diagnostic_only_quality.py
baseline_tests/run_step80_activation_guard.py
baseline_tests/run_step80_output_guard.py
baseline_tests/run_step80_step79_regression_guard.py
baseline_tests/run_step80_artifact_manifest.py
```

Tests:

```text
tests/test_step80_runtime_geometry_diagnostic_only_smoke_matrix_contract.py
tests/test_step80_runtime_geometry_diagnostic_only_quality_contract.py
tests/test_step80_activation_guard_contract.py
tests/test_step80_output_guard_contract.py
tests/test_step80_step79_regression_contract.py
```

Docs:

```text
docs/80_runtime_geometry_diagnostic_only_canonical_driver_smoke.md
```

Generated outputs:

```text
outputs/step80_driver_runs/canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke/
outputs/step80_runtime_geometry_diagnostic_only_smoke_matrix/
outputs/step80_runtime_geometry_diagnostic_only_quality/
outputs/step80_activation_guard/
outputs/step80_output_guard/
outputs/step80_step79_regression_guard/
outputs/step80_artifact_manifest/
logs/step80_*.log
```

Allowed existing docs updates:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

## Matrix Acceptance Contract

The Step80 matrix artifact must include:

```text
step80_runtime_geometry_diagnostic_only_smoke_matrix_pass = true
required_row_count = 1
optional_row_count = 0
required_stable_count = 1
activation_feature_count = 1
runtime_geometry_enabled_count = 1
wall_velocity_enabled_count = 0
combined_runtime_geometry_wall_velocity_enabled_count = 0
real_geometry_enabled_count = 0
squid_proxy_enabled_count = 0
link_area_enabled_count = 0
grid_48_enabled_count = 0
grid_64_enabled_count = 0
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = diagnostic_only_only
```

The required row must include:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
completed_lbm_steps = 3
total_mpm_substeps >= 3
diagnostics_row_count >= 4
has_nan = false
has_inf = false
stable = true
runtime_hard_fail = false
geometry_motion_interface_report_exists = true
geometry_motion_interface_report_pass = true
no_op_pass = true
config_validation_pass = true
diagnostic_only = true
mutation_flag_enabled_count = 0
```

## Numeric Quality Contract

Step80 quality must use the same broad smoke/rebaseline numeric envelope as
Step78:

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

The quality artifact must pass:

```text
step80_runtime_geometry_diagnostic_only_quality_pass = true
```

## Output Guard Contract

The required driver run directory is:

```text
outputs/step80_driver_runs/canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke/
```

Allowed driver-run files:

```text
driver_config.json
geo_all_fluid_32.dat
diagnostics_timeseries.csv
diagnostics_timeseries.npz
geometry_motion_interface_report.json
```

Forbidden outputs:

```text
*.vtr
particle*.npy
displaced_particles*.npy
dense_displacement*.npy
raw geometry outputs
optional driver run dirs
private absolute paths
external/taichi_LBM3D edits
data/real_geometry_candidates edits
```

The output guard must pass:

```text
output_guard_pass = true
step80_required_driver_run_dir_count = 1
step80_optional_driver_run_dir_count = 0
step80_vtr_count = 0
step80_particle_npy_count = 0
step80_displaced_particle_output_count = 0
step80_dense_displacement_output_count = 0
step80_raw_geometry_output_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
```

## Step79 Regression Contract

The Step80 Step79 regression guard must prove:

```text
step79_runtime_geometry_diagnostic_only_activation_plan_pass = true
step79_runtime_geometry_diagnostic_only_activation_guard_pass = true
step79_step78_regression_guard_pass = true
step79_output_guard_pass = true
step79_artifact_budget_pass = true
step79_activation_feature_count = 0
planned_step80_activation_feature_count = 1
step79_driver_run_dir_count = 0
step79_vtr_count = 0
step79_particle_npy_count = 0
```

## Required Commands

Baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step80_runtime_geometry_diagnostic_only_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step80_runtime_geometry_diagnostic_only_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step80_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step80_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step80_step79_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step80_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step80_runtime_geometry_diagnostic_only_smoke_matrix_contract.py tests\test_step80_runtime_geometry_diagnostic_only_quality_contract.py tests\test_step80_activation_guard_contract.py tests\test_step80_output_guard_contract.py tests\test_step80_step79_regression_contract.py -q
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
```

## Required Report Conclusion

The Step80 report must state:

```text
Step80 accepted.
Step80 runs exactly one required canonical driver row:
canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke
Step80 enables only runtime geometry diagnostic-only interface reporting.
Step80 writes geometry_motion_interface_report.json.
Step80 does not mutate geometry.
Step80 does not displace MPM particles.
Step80 does not update LBM solid_phi.
Step80 does not update LBM solid_vel.
Step80 does not update dynamic_solid.
Step80 does not recompute boundary links.
Step80 does not change moving bounce-back formulas.
Step80 does not enable wall velocity.
Step80 does not enable real geometry.
Step80 does not enable squid proxy.
Step80 does not enable link-area transfer.
Step80 does not enable VTR or particle NPY.
Step80 does not claim physical validation or production readiness.
```

## Completion Criteria

Step80 is complete only when:

1. The detailed goal file is checked in and referenced by the active goal.
2. The required configs, evidence modules, baseline runners, docs, tests,
   report, outputs, logs, and manifest exist.
3. The one required canonical driver row runs and passes acceptance.
4. Runtime geometry diagnostic-only report generation passes with zero mutation
   flags.
5. Quality, activation guard, output guard, Step79 regression guard, and
   artifact manifest all pass.
6. Focused Step80 tests pass.
7. Full pytest passes with the trusted interpreter and Anaconda interpreter
   when available.
8. `git diff --check` and `git diff --cached --check` pass.
9. Protected external and real geometry candidate directories remain unchanged.
10. The completed commit is pushed to `origin/main`.
