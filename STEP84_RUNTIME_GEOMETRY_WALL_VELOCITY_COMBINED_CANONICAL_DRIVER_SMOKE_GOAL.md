# Step84 Runtime Geometry Diagnostic-Only + Wall Velocity Solid-Vel Combined Canonical Driver 3-Step Smoke Goal

## Objective

Implement Step84 as the first combined-feature canonical driver smoke run after
accepted Step83.

Step84 must run exactly one required `FSIDriver3D.run()` row:

```text
canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

The row must combine only these two already-separately-accepted post-gate
features:

```text
runtime_geometry = diagnostic_only
wall_velocity = solid_vel_experimental
```

Step84 must prove that these two paths can coexist in the canonical driver for
one bounded 32^3 / 1024-particle / 3-LBM-step smoke run while remaining
stable, finite, and inside the Step83-planned activation envelope.

Step84 must not claim physical validation, real squid validation, moving
geometry validation, jet propulsion, grid convergence, or production readiness.

## Required Base State

The implementation must start from:

```text
origin/main = 42f4eafabf3c83490ce8a69aa3b34089a9bed08a
previous accepted step = Step83
```

Step83 is accepted as a plan-and-guard step. Step84 is the only planned next
row from Step83 and must honor Step83's row-level restrictions exactly.

Before committing, confirm the local `main` and `origin/main` are still based
on the Step83 commit, or fetch and resolve any remote movement without force
push.

## Required Commit Message

```text
test: add step84 runtime geometry wall velocity combined canonical driver smoke
```

## Required Driver Row

Only one required row is allowed:

```text
canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

No optional rows are allowed.

The required row must use:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
target_u_lbm = [0.0, 0.0, 0.0]
output_interval = 1
write_vtk = false
write_particles = false
quality_check_enabled = false
quality_check_strict = false
```

The zero `target_u_lbm` is a row-local config choice to isolate combined path
stability. It must be documented as a config choice, not a solver/tau/runtime
change.

## Required Step84 Driver Config

Add:

```text
configs/step84_canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke.json
```

The config must include:

```json
{
  "boundary_motion_mode": "prescribed_kinematic",
  "boundary_motion_config_path": "configs/step34_boundary_motion_interface_prescribed_kinematic.json",
  "boundary_motion_report_enabled": true,
  "coupling_mode": "moving_boundary",
  "geometry_motion_mode": "prescribed_kinematic",
  "geometry_motion_config_path": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
  "geometry_motion_report_enabled": true,
  "geometry_motion_application_mode": "diagnostic_only",
  "geometry_motion_application_config_path": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
  "geometry_motion_application_report_enabled": true,
  "geometry_type": "box",
  "wall_velocity_application_mode": "solid_vel_experimental",
  "wall_velocity_application_config_path": "configs/step36_wall_velocity_application_solid_vel_experimental.json",
  "wall_velocity_application_report_enabled": true,
  "mpm_substeps_per_lbm_step": 1,
  "n_grid": 32,
  "n_lbm_steps": 3,
  "n_particles": 1024,
  "output_interval": 1,
  "quality_check_enabled": false,
  "quality_check_strict": false,
  "reaction_transfer_mode": "engineering",
  "target_u_lbm": [0.0, 0.0, 0.0],
  "write_particles": false,
  "write_vtk": false
}
```

## Required New Files

Create the Step84 goal and report:

```text
STEP84_RUNTIME_GEOMETRY_WALL_VELOCITY_COMBINED_CANONICAL_DRIVER_SMOKE_GOAL.md
STEP84_RUNTIME_GEOMETRY_WALL_VELOCITY_COMBINED_CANONICAL_DRIVER_SMOKE_REPORT.md
```

Create configs:

```text
configs/step84_runtime_geometry_wall_velocity_combined_smoke_matrix.json
configs/step84_canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke.json
configs/step84_runtime_geometry_wall_velocity_combined_acceptance_policy.json
configs/step84_activation_guard_policy.json
configs/step84_output_guard_policy.json
configs/step84_step83_regression_policy.json
configs/step84_step82_regression_policy.json
configs/step84_step80_regression_policy.json
configs/step84_artifact_manifest_policy.json
```

Create evidence modules:

```text
src/mpm_lbm/evidence/step84_runtime_geometry_wall_velocity_combined_smoke_runner.py
src/mpm_lbm/evidence/step84_runtime_geometry_wall_velocity_combined_smoke_audit.py
src/mpm_lbm/evidence/step84_runtime_geometry_wall_velocity_combined_quality_audit.py
src/mpm_lbm/evidence/step84_runtime_geometry_wall_velocity_combined_activation_guard.py
src/mpm_lbm/evidence/step84_output_guard.py
src/mpm_lbm/evidence/step84_step83_regression_guard.py
src/mpm_lbm/evidence/step84_step82_regression_guard.py
src/mpm_lbm/evidence/step84_step80_regression_guard.py
```

Create baseline runners:

```text
baseline_tests/step84_common.py
baseline_tests/run_step84_runtime_geometry_wall_velocity_combined_smoke_matrix.py
baseline_tests/run_step84_runtime_geometry_wall_velocity_combined_quality.py
baseline_tests/run_step84_activation_guard.py
baseline_tests/run_step84_output_guard.py
baseline_tests/run_step84_step83_regression_guard.py
baseline_tests/run_step84_step82_regression_guard.py
baseline_tests/run_step84_step80_regression_guard.py
baseline_tests/run_step84_artifact_manifest.py
```

Create tests:

```text
tests/test_step84_runtime_geometry_wall_velocity_combined_smoke_matrix_contract.py
tests/test_step84_runtime_geometry_wall_velocity_combined_quality_contract.py
tests/test_step84_activation_guard_contract.py
tests/test_step84_output_guard_contract.py
tests/test_step84_step83_regression_contract.py
tests/test_step84_step82_regression_contract.py
tests/test_step84_step80_regression_contract.py
```

Create docs:

```text
docs/84_runtime_geometry_wall_velocity_combined_canonical_driver_smoke.md
```

Allowed documentation updates:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

Generated Step84 outputs and logs must be committed:

```text
outputs/step84_driver_runs/canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke/
outputs/step84_runtime_geometry_wall_velocity_combined_smoke_matrix/
outputs/step84_runtime_geometry_wall_velocity_combined_quality/
outputs/step84_activation_guard/
outputs/step84_output_guard/
outputs/step84_step83_regression_guard/
outputs/step84_step82_regression_guard/
outputs/step84_step80_regression_guard/
outputs/step84_artifact_manifest/
logs/step84_*.log
```

## Forbidden Modification Surface

Step84 must not edit:

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

If the Step84 driver run fails, first inspect Step84 config, Step84 evidence
runner logic, acceptance bounds, report-path handling, and output guard
assumptions. Do not use Step84 as a reason to modify solver runtime, vendored
external code, or real-geometry data.

## Required Driver Invocation

`baseline_tests/run_step84_runtime_geometry_wall_velocity_combined_smoke_matrix.py`
must run the canonical driver through the canonical import path:

```python
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

config = FSIDriverConfig.from_json(
    "configs/step84_canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke.json"
)

driver = FSIDriver3D(
    config,
    "outputs/step84_driver_runs/canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke",
)

diagnostics = driver.run()
```

The implementation may wrap this in a reusable evidence builder, but the smoke
must truly call `FSIDriver3D.run()` and must record that the canonical driver
module is `src.mpm_lbm.sim.drivers.fsi_driver`.

## Expected Driver Outputs

The required run directory is:

```text
outputs/step84_driver_runs/canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke/
```

Allowed files include:

```text
driver_config.json
geo_all_fluid_32.dat
diagnostics_timeseries.csv
diagnostics_timeseries.npz
geometry_motion_interface_report.json
boundary_motion_interface_report.json
wall_velocity_application_report.json
```

Forbidden generated outputs include:

```text
*.vtr
particle*.npy
dense_wall_velocity*.npy
sparse_wall_velocity*.npy
dense_displacement*.npy
displaced_particles*.npy
raw real geometry output
optional driver run dirs
```

## Smoke Matrix Acceptance

The smoke matrix summary must include:

```text
step84_runtime_geometry_wall_velocity_combined_smoke_matrix_pass = true
required_row_count = 1
optional_row_count = 0
required_stable_count = 1
activation_feature_count = 2
runtime_geometry_enabled_count = 1
wall_velocity_enabled_count = 1
combined_runtime_geometry_wall_velocity_enabled_count = 1
real_geometry_enabled_count = 0
squid_proxy_enabled_count = 0
link_area_enabled_count = 0
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = runtime_geometry_diagnostic_only_wall_velocity_solid_vel_only
```

The evidence row must include at least:

```text
driver_run_called
canonical_driver_module
legacy_driver_module_used_as_implementation
completed_lbm_steps
total_mpm_substeps
diagnostics_row_count
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
real_geometry_enabled
squid_proxy_enabled
link_area_enabled
has_nan
has_inf
stable
elapsed_seconds
```

## Driver Run Acceptance

The required row must satisfy:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
row_name = canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
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

## Runtime Geometry Diagnostic-Only Acceptance

The required row and report must satisfy:

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

## Wall Velocity Solid-Vel Acceptance

The required row and report must satisfy:

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

## Boundary Motion Acceptance

The required row and report must satisfy:

```text
boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path_exists = true
boundary_motion_interface_report_exists = true
boundary_motion_interface_report_pass = true
boundary_motion_diagnostic_only = true
```

## Combined Feature Acceptance

The required row must satisfy:

```text
combined_runtime_geometry_wall_velocity_enabled = true
activation_feature_count = 2
```

The following features must remain closed:

```text
real_geometry_enabled = false
squid_proxy_enabled = false
link_area_enabled = false
grid_48_enabled = false
grid_64_enabled = false
write_vtk = false
write_particles = false
```

## Numeric Smoke Bounds

Use bounded smoke thresholds:

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

## Quality Summary Acceptance

`outputs/step84_runtime_geometry_wall_velocity_combined_quality/runtime_geometry_wall_velocity_combined_quality.json`
must have:

```text
step84_runtime_geometry_wall_velocity_combined_quality_pass = true
geometry_motion_interface_report_pass_count = 1
wall_velocity_application_report_pass_count = 1
boundary_motion_interface_report_pass_count = 1
finite_wall_velocity_report_count = 1
capped_wall_velocity_report_count = 1
mutation_flag_enabled_count_max = 0
```

## Activation Guard Acceptance

`outputs/step84_activation_guard/activation_guard.json` must have:

```text
step84_activation_guard_pass = true
activation_feature_count = 2
runtime_geometry_enabled_count = 1
wall_velocity_enabled_count = 1
combined_runtime_geometry_wall_velocity_enabled_count = 1
real_geometry_enabled_count = 0
squid_proxy_enabled_count = 0
link_area_enabled_count = 0
```

## Output Guard Acceptance

`outputs/step84_output_guard/output_guard.json` must have:

```text
output_guard_pass = true
step84_required_driver_run_dir_count = 1
step84_optional_driver_run_dir_count = 0
step84_vtr_count = 0
step84_particle_npy_count = 0
step84_dense_wall_velocity_output_count = 0
step84_sparse_wall_velocity_output_count = 0
step84_dense_displacement_output_count = 0
step84_displaced_particle_output_count = 0
step84_raw_geometry_output_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
artifact_budget_pass = true
```

## Regression Guards

### Step83 Regression Guard

Step84 must prove the accepted Step83 evidence remains intact:

```text
step83_runtime_geometry_wall_velocity_combined_activation_plan_pass = true
step83_runtime_geometry_wall_velocity_combined_activation_guard_pass = true
step83_step82_regression_guard_pass = true
step83_step80_regression_guard_pass = true
step83_output_guard_pass = true
step83_artifact_budget_pass = true
step83_activation_feature_count = 0
planned_step84_activation_feature_count = 2
step83_driver_run_dir_count = 0
step83_vtr_count = 0
step83_particle_npy_count = 0
```

### Step82 Regression Guard

Step84 must prove accepted Step82 remains a wall-velocity-only smoke:

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
step82_vtr_count = 0
step82_particle_npy_count = 0
```

### Step80 Regression Guard

Step84 must prove accepted Step80 remains a runtime-geometry-only smoke:

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
step80_vtr_count = 0
step80_particle_npy_count = 0
```

## Required Contract Tests

Add focused contract tests for:

```text
Step84 smoke matrix artifact and row contract
Step84 combined quality artifact contract
Step84 activation guard contract
Step84 output guard contract
Step84 Step83 regression guard contract
Step84 Step82 regression guard contract
Step84 Step80 regression guard contract
```

The tests must read committed artifacts under `outputs/step84_*` and the
required Step84 driver run directory. They should avoid unnecessary heavy
imports so the pre-push hook remains reliable.

## Required Verification Commands

Run baseline artifact generators with the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_runtime_geometry_wall_velocity_combined_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_runtime_geometry_wall_velocity_combined_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_step83_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_step82_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_step80_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step84_artifact_manifest.py
```

Run focused Step84 tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step84_runtime_geometry_wall_velocity_combined_smoke_matrix_contract.py tests\test_step84_runtime_geometry_wall_velocity_combined_quality_contract.py tests\test_step84_activation_guard_contract.py tests\test_step84_output_guard_contract.py tests\test_step84_step83_regression_contract.py tests\test_step84_step82_regression_contract.py tests\test_step84_step80_regression_contract.py -q
```

Run full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Run git checks:

```powershell
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Refresh output guard and artifact manifest after final pytest logs exist.

## Required Report Conclusion

`STEP84_RUNTIME_GEOMETRY_WALL_VELOCITY_COMBINED_CANONICAL_DRIVER_SMOKE_REPORT.md`
must say, if verification passes:

```text
Step84 accepted.

Step84 runs exactly one required canonical driver row:
canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke

The row uses:
32^3
1024 particles
3 LBM steps
1 MPM substep per LBM step
moving_boundary
engineering
box geometry
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel

Step84 enables only:
runtime geometry diagnostic-only interface reporting
wall velocity solid_vel experimental application

Step84 writes:
geometry_motion_interface_report.json
boundary_motion_interface_report.json
wall_velocity_application_report.json

Step84 does not mutate geometry.
Step84 does not displace MPM particles.
Step84 does not update LBM solid_phi through runtime geometry.
Step84 does not directly write LBM populations through wall velocity.
Step84 does not modify moving bounce-back formulas.
Step84 does not directly update MPM state through wall velocity.
Step84 does not directly update projector state through wall velocity.
Step84 does not enable real geometry.
Step84 does not enable squid proxy.
Step84 does not enable link-area transfer.
Step84 does not enable 48^3 or 64^3.
Step84 does not write VTR or particle NPY.
Step84 does not claim physical validation or production readiness.
```

## Final Push Requirement

After implementation and verification:

1. Confirm worktree status.
2. Stage only Step84-related files and allowed docs.
3. Run cached diff checks.
4. Commit with the required commit message.
5. Push to `origin/main`.
6. Report final local and remote commit hashes, branch, pass counts, output guard
   status, artifact manifest summary, and any warnings.

Do not force-push.

## Step85 Reservation

If Step84 passes, reserve the next direction as a separate future step, not part
of Step84:

```text
Step85 Squid Proxy Static Geometry Single-Feature Activation Plan And Guard
Step86 Squid Proxy Static Geometry 32^3 / 3-step Smoke
Step87 Combined Runtime Geometry + Wall Velocity + Squid Proxy Plan And Guard
Step88 First User Simulation Dry Run
```

Do not open squid proxy or real geometry in Step84.
