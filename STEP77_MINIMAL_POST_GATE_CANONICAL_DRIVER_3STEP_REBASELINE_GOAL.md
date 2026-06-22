# Step77 Minimal Post-Gate Canonical Driver 3-Step Rebaseline Goal

## Step Name

`Step77 Minimal Post-Gate Canonical Driver 3-Step Rebaseline`

## Required Commit Message

`test: add step77 minimal post-gate canonical driver 3step rebaseline`

## Repository And Baseline

Repository root:

`D:\working\squid robot\LBM\MPM-LBM`

Required starting point:

```text
origin/main = a574d17703494e8146f8513056a52bfe92884d44
commit = test: add step76 minimal post-gate canonical driver rebaseline
```

Step77 starts only after Step76 accepted the minimal post-gate one-step
canonical driver rebaseline:

```text
post_gate_rebaseline_matrix_pass = true
post_gate_rebaseline_quality_pass = true
post_gate_activation_guard_pass = true
output_guard_pass = true
step76_step75_regression_guard_pass = true
artifact_budget_pass = true
```

Step76 ran exactly one required canonical driver row:

```text
row_name = canonical_driver_moving_boundary_engineering_32_1step_rebaseline
n_grid = 32
n_particles = 1024
n_lbm_steps = 1
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
activation_feature_count = 0
```

## Core Objective

Step77 extends exactly one dimension from Step76:

```text
duration: 1 LBM step -> 3 LBM steps
```

All other dimensions must remain equivalent to Step76:

```text
n_grid = 32
n_particles = 1024
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
runtime_geometry_enabled = false
wall_velocity_enabled = false
combined_runtime_geometry_wall_velocity_enabled = false
real_geometry_enabled = false
squid_proxy_enabled = false
link_area_enabled = false
grid_48_enabled = false
grid_64_enabled = false
write_vtk = false
write_particles = false
```

The row exists to confirm that the post-gate safe-default canonical driver
rebaseline can extend from one LBM step to three LBM steps without enabling any
advanced feature or changing solver formulas.

## Correct Claim

Step77 may claim:

```text
minimal post-gate 3-step canonical driver rebaseline passed
```

Step77 must not claim:

```text
physical validation
runtime geometry validation
wall velocity validation
real geometry validation
squid behavior validation
real squid validation
grid convergence
production readiness
tau migration validation
```

## Hard Scope Boundaries

Step77 must not activate or add:

```text
runtime geometry activation
wall velocity activation
combined runtime geometry plus wall velocity activation
real geometry activation
squid proxy activation
link_area activation
48^3 row
64^3 row
duration beyond 3 LBM steps
VTR output
particle NPY output
tau formula migration
solver formula change
new real geometry data
data/real_geometry_candidates edit
external/taichi_LBM3D edit
physical validation claim
production readiness claim
```

Step77 may generate only lightweight run, audit, summary, log, report, and
manifest artifacts needed to prove the three-step rebaseline and its boundaries.

## Required Driver Run

Required row:

```text
canonical_driver_moving_boundary_engineering_32_3step_rebaseline
```

Required run directory:

```text
outputs/step77_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_rebaseline/
```

Allowed files inside the driver run directory:

```text
driver_config.json
geo_all_fluid_32.dat
diagnostics_timeseries.csv
diagnostics_timeseries.npz
```

Required config:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
output_interval = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
quality_check_enabled = false
quality_check_strict = false
boundary_motion_mode = static
wall_velocity_application_mode = disabled
geometry_motion_mode = static
geometry_motion_application_mode = disabled
write_vtk = false
write_particles = false
```

The runner must call the real canonical driver:

```python
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

config = FSIDriverConfig.from_json(
    "configs/step77_canonical_driver_moving_boundary_engineering_32_3step_rebaseline.json"
)
driver = FSIDriver3D(
    config,
    "outputs/step77_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_rebaseline",
)
diagnostics = driver.run()
```

## Optional Rows

Step77 must not define or run optional rows.

If a future five-step row is desired, it belongs to Step78. Step77 is only a
single required three-step row.

## Required Files

### Goal And Report

```text
STEP77_MINIMAL_POST_GATE_CANONICAL_DRIVER_3STEP_REBASELINE_GOAL.md
STEP77_MINIMAL_POST_GATE_CANONICAL_DRIVER_3STEP_REBASELINE_REPORT.md
```

### Configs

```text
configs/step77_minimal_post_gate_canonical_driver_3step_rebaseline.json
configs/step77_canonical_driver_moving_boundary_engineering_32_3step_rebaseline.json
configs/step77_rebaseline_acceptance_policy.json
configs/step77_activation_guard_policy.json
configs/step77_output_guard_policy.json
configs/step77_step76_regression_policy.json
```

### Evidence Modules

```text
src/mpm_lbm/evidence/post_gate_3step_rebaseline_runner.py
src/mpm_lbm/evidence/post_gate_3step_rebaseline_audit.py
src/mpm_lbm/evidence/post_gate_3step_rebaseline_quality_audit.py
src/mpm_lbm/evidence/post_gate_3step_activation_guard.py
src/mpm_lbm/evidence/post_gate_3step_output_guard.py
src/mpm_lbm/evidence/step77_regression_guard.py
```

All Step77 evidence code must stay under:

```text
src/mpm_lbm/evidence/
```

Do not put Step77 evidence or runners under:

```text
src/mpm_lbm/sim/
experiments/steps/
```

### Baseline Runners

```text
baseline_tests/step77_common.py
baseline_tests/run_step77_post_gate_3step_rebaseline_matrix.py
baseline_tests/run_step77_post_gate_3step_rebaseline_quality.py
baseline_tests/run_step77_activation_guard.py
baseline_tests/run_step77_output_guard.py
baseline_tests/run_step77_step76_regression_guard.py
baseline_tests/run_step77_artifact_manifest.py
```

### Tests

```text
tests/test_step77_post_gate_3step_rebaseline_matrix_contract.py
tests/test_step77_post_gate_3step_rebaseline_quality_contract.py
tests/test_step77_activation_guard_contract.py
tests/test_step77_output_guard_contract.py
tests/test_step77_step76_regression_contract.py
```

### Docs

```text
docs/77_minimal_post_gate_canonical_driver_3step_rebaseline.md
```

Update:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

Docs must say that Step77 is only a three-step rebaseline and does not
authorize runtime geometry, wall velocity, real geometry, squid proxy,
link-area transfer, 48^3, 64^3, VTR, particle NPY, physical validation, or
production readiness.

## Matrix Summary Requirements

The matrix artifact must include the required row and these fields, or a
compatible superset:

```text
row_name
campaign_id
gate_source_step
previous_rebaseline_step
n_grid
n_particles
n_lbm_steps
mpm_substeps_per_lbm_step
coupling_mode
reaction_transfer_mode
geometry_type
runtime_geometry_enabled
wall_velocity_enabled
combined_runtime_geometry_wall_velocity_enabled
real_geometry_enabled
squid_proxy_enabled
link_area_enabled
grid_48_enabled
grid_64_enabled
write_vtk
write_particles
activation_feature_count
driver_run_called
canonical_driver_module
legacy_driver_module_used_as_implementation
initialized
completed_lbm_steps
total_mpm_substeps
diagnostics_row_count
rho_min_final
rho_max_final
rho_min_min
rho_max_max
lbm_max_v_max
mpm_min_J_min
mpm_max_speed_max
projected_mass_final
active_cell_count_final
cell_force_max_norm_max
hydro_force_max_norm_max
bb_link_count_final
bb_link_count_max
bb_max_correction_max
active_reaction_particle_count_final
max_grid_reaction_norm_max
has_nan
has_inf
generated_file_count
geo_path_name
diagnostics_csv_exists
diagnostics_npz_exists
driver_config_exists
elapsed_seconds
runtime_warning
runtime_hard_fail
stable
notes
```

## Acceptance Bounds

The required row must satisfy:

```text
row_name == canonical_driver_moving_boundary_engineering_32_3step_rebaseline
driver_run_called == true
canonical_driver_module == src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation == false
n_grid == 32
n_particles == 1024
n_lbm_steps == 3
mpm_substeps_per_lbm_step == 1
completed_lbm_steps == 3
total_mpm_substeps >= 3
diagnostics_row_count >= 4
runtime_geometry_enabled == false
wall_velocity_enabled == false
combined_runtime_geometry_wall_velocity_enabled == false
real_geometry_enabled == false
squid_proxy_enabled == false
link_area_enabled == false
grid_48_enabled == false
grid_64_enabled == false
write_vtk == false
write_particles == false
activation_feature_count == 0
geo_path_name == geo_all_fluid_32.dat
diagnostics_csv_exists == true
diagnostics_npz_exists == true
driver_config_exists == true
has_nan == false
has_inf == false
stable == true
```

Numeric bounds:

```text
rho_min_min > 0.90
rho_max_max < 1.10
lbm_max_v_max < 0.5
mpm_min_J_min > 0.0
mpm_max_speed_max < 10.0
projected_mass_final > 0.0
active_cell_count_final > 0
bb_link_count_max > 0
bb_max_correction_max >= 0.0
active_reaction_particle_count_final >= 0
max_grid_reaction_norm_max is finite
all numeric diagnostics finite
```

Runtime:

```text
elapsed_seconds recorded
runtime_warning = elapsed_seconds > 3600
runtime_warning does not fail by itself
runtime_hard_fail = elapsed_seconds > 7200
runtime_hard_fail must be false
```

## Activation Guard

Step77 must prove it did not expand activation:

```text
runtime_geometry_enabled == false
wall_velocity_enabled == false
combined_runtime_geometry_wall_velocity_enabled == false
real_geometry_enabled == false
squid_proxy_enabled == false
link_area_enabled == false
grid_48_enabled == false
grid_64_enabled == false
write_vtk == false
write_particles == false
activation_feature_count == 0
```

Step77 must also compare against Step76:

```text
step76_activation_feature_count == 0
step77_activation_feature_count == 0
activation_feature_delta == 0
```

## Output Guard

Expected summary:

```text
step77_required_driver_run_dir_count == 1
step77_optional_driver_run_dir_count == 0
step77_vtr_count == 0
step77_particle_npy_count == 0
step77_large_file_count == 0
private_absolute_path_count == 0
protected_external_edit_count == 0
protected_real_geometry_candidate_edit_count == 0
step77_total_size_mb < 20
output_guard_pass == true
```

Forbidden Step77 files:

```text
*.vtr
particle *.npy
dense_displacement*
displaced_particle*
raw geometry files
private absolute paths in Step77 outputs/logs
large Step77 files above 5 MB
protected external files
protected real geometry candidate files
```

## Step76 Regression Guard

Step77 must confirm these committed Step76 artifacts are still green:

```text
outputs/step76_post_gate_rebaseline_matrix/post_gate_rebaseline_matrix.json
outputs/step76_post_gate_rebaseline_quality/post_gate_rebaseline_quality.json
outputs/step76_activation_guard/activation_guard.json
outputs/step76_output_guard/output_guard.json
outputs/step76_step75_regression_guard/step75_regression_guard.json
outputs/step76_artifact_manifest/artifact_summary.json
```

Required Step76 checks:

```text
post_gate_rebaseline_matrix_pass == true
post_gate_rebaseline_quality_pass == true
post_gate_activation_guard_pass == true
output_guard_pass == true
step76_step75_regression_guard_pass == true
artifact_budget_pass == true
optional_row_count == 0
activation_feature_count == 0
step76_vtr_count == 0
step76_particle_npy_count == 0
protected_external_edit_count == 0
protected_real_geometry_candidate_edit_count == 0
```

## Final Acceptance Criteria

Step77 passes only if:

```text
Step77 goal, report, docs, configs, runners, evidence modules, tests, logs, and artifacts exist.
The required 3-step rebaseline row runs through canonical FSIDriver3D.run().
Exactly one required Step77 driver run directory exists.
No optional Step77 driver run directory exists.
The row completes three LBM steps and at least three MPM substeps.
Diagnostics have at least four rows and no NaN/Inf.
All numeric acceptance bounds pass.
All advanced activation features remain disabled.
No VTR, particle NPY, dense displacement, displaced particle, raw geometry, protected external, protected real geometry candidate, private absolute path, or large file output is introduced.
Step76 regression guard passes.
Focused Step77 pytest passes.
Full trusted Python pytest passes.
Full Anaconda Python pytest passes when available.
Pre-push hook passes.
git diff checks pass.
Commit is pushed to origin/main.
```

## Verification Commands

Compile:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\evidence\post_gate_3step_rebaseline_runner.py `
  src\mpm_lbm\evidence\post_gate_3step_rebaseline_audit.py `
  src\mpm_lbm\evidence\post_gate_3step_rebaseline_quality_audit.py `
  src\mpm_lbm\evidence\post_gate_3step_activation_guard.py `
  src\mpm_lbm\evidence\post_gate_3step_output_guard.py `
  src\mpm_lbm\evidence\step77_regression_guard.py `
  baseline_tests\step77_common.py `
  baseline_tests\run_step77_post_gate_3step_rebaseline_matrix.py `
  baseline_tests\run_step77_post_gate_3step_rebaseline_quality.py `
  baseline_tests\run_step77_activation_guard.py `
  baseline_tests\run_step77_output_guard.py `
  baseline_tests\run_step77_step76_regression_guard.py `
  baseline_tests\run_step77_artifact_manifest.py
```

Generate artifacts:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step77_post_gate_3step_rebaseline_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step77_post_gate_3step_rebaseline_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step77_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step77_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step77_step76_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step77_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest `
  tests\test_step77_post_gate_3step_rebaseline_matrix_contract.py `
  tests\test_step77_post_gate_3step_rebaseline_quality_contract.py `
  tests\test_step77_activation_guard_contract.py `
  tests\test_step77_output_guard_contract.py `
  tests\test_step77_step76_regression_contract.py `
  -q
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
git diff --check HEAD~1 HEAD
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Commit and push:

```powershell
git add <Step77 files>
git commit -m "test: add step77 minimal post-gate canonical driver 3step rebaseline"
git push origin main
```

## Step78 Direction

If Step77 passes, the preferred next step is:

```text
Step78 Minimal Post-Gate Canonical Driver 5-Step Rebaseline
```

Step78 should still keep runtime geometry, wall velocity, real geometry, squid
proxy, link-area transfer, VTR, and particle outputs disabled. Single-feature
activation should wait until after the safe post-gate baseline ladder is
explicitly accepted.
