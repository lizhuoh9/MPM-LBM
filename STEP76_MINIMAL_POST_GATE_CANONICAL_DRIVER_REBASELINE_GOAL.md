# Step76 Minimal Post-Gate Canonical Driver Rebaseline Goal

## Step Name

`Step76 Minimal Post-Gate Canonical Driver Rebaseline`

## Required Commit Message

`test: add step76 minimal post-gate canonical driver rebaseline`

## Repository And Baseline

Repository root:

`D:\working\squid robot\LBM\MPM-LBM`

Required starting point:

```text
origin/main = f92567273e8014800ade38e3e8962ee68b2e4714
commit = test: add step75 solver complete readiness gate
```

Step76 starts only after Step75 accepted the gate result:

```text
gate_status = ready_for_step76_rebaseline_only
post_gate_simulation_allowed = true
allowed_next_step = Step76
allowed_next_step_scope = minimal safe rebaseline only
activation_features_allowed_in_next_step = []
runtime_geometry_activation_allowed = false
wall_velocity_activation_allowed = false
real_geometry_activation_allowed = false
squid_proxy_activation_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
```

## Core Objective

Run exactly one minimal post-gate canonical `FSIDriver3D` rebaseline row through
the canonical driver implementation:

```text
row_name = canonical_driver_moving_boundary_engineering_32_1step_rebaseline
n_grid = 32
n_particles = 1024
n_lbm_steps = 1
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
output_interval = 1
write_vtk = false
write_particles = false
quality_check_enabled = false
quality_check_strict = false
boundary_motion_mode = static
wall_velocity_application_mode = disabled
geometry_motion_mode = static
geometry_motion_application_mode = disabled
```

The row exists to confirm that, after Step63 through Step75 structural and
evidence work, the canonical driver still completes a minimal real run under
the narrow Step75 post-gate allowance.

## Correct Claim

Step76 may claim:

```text
minimal post-gate canonical driver rebaseline passed
```

Step76 must not claim:

```text
physical validation
production readiness
real squid simulation
real squid validation
grid convergence
runtime geometry validation
wall velocity validation
real geometry validation
tau migration validation
```

## Hard Scope Boundaries

Step76 must not activate or add:

```text
runtime geometry activation
wall velocity activation
combined runtime geometry plus wall velocity activation
real geometry activation
squid proxy activation
link_area activation
48^3 row
64^3 row
long duration row
VTR output
particle NPY output
tau formula migration
solver formula change
grid convergence claim
production readiness claim
physical validation claim
real squid validation claim
external/taichi_LBM3D edit
data/real_geometry_candidates edit
```

Step76 may generate only lightweight run, audit, summary, log, report, and
manifest artifacts needed to prove the minimal rebaseline and its boundaries.

## Required Driver Run

Required run directory:

```text
outputs/step76_driver_runs/canonical_driver_moving_boundary_engineering_32_1step_rebaseline/
```

Allowed files inside the required driver run directory:

```text
driver_config.json
geo_all_fluid_32.dat
diagnostics_timeseries.csv
diagnostics_timeseries.npz
```

The runner must call the canonical driver:

```python
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

config = FSIDriverConfig.from_json(
    "configs/step76_canonical_driver_moving_boundary_engineering_32_1step_rebaseline.json"
)
driver = FSIDriver3D(
    config,
    "outputs/step76_driver_runs/canonical_driver_moving_boundary_engineering_32_1step_rebaseline",
)
diagnostics = driver.run()
```

This `driver.run()` call is allowed only for the one required Step76 row because
Step75 explicitly allowed Step76 minimal safe rebaseline.

## Optional Row Policy

Define but do not run the optional row:

```text
row_name = canonical_driver_moving_boundary_engineering_32_3step_rebaseline_optional
run_optional_32_3step = false
```

The optional run directory must not exist:

```text
outputs/step76_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_rebaseline_optional/
```

Step77 may consider the three-step rebaseline later. Step76 must not run it.

## Required Files

### Goal And Report

```text
STEP76_MINIMAL_POST_GATE_CANONICAL_DRIVER_REBASELINE_GOAL.md
STEP76_MINIMAL_POST_GATE_CANONICAL_DRIVER_REBASELINE_REPORT.md
```

### Configs

```text
configs/step76_minimal_post_gate_canonical_driver_rebaseline.json
configs/step76_canonical_driver_moving_boundary_engineering_32_1step_rebaseline.json
configs/step76_canonical_driver_moving_boundary_engineering_32_3step_rebaseline_optional.json
configs/step76_rebaseline_acceptance_policy.json
configs/step76_activation_guard_policy.json
configs/step76_output_guard_policy.json
configs/step76_step75_regression_policy.json
```

### Evidence Modules

```text
src/mpm_lbm/evidence/post_gate_rebaseline_runner.py
src/mpm_lbm/evidence/post_gate_rebaseline_audit.py
src/mpm_lbm/evidence/post_gate_rebaseline_quality_audit.py
src/mpm_lbm/evidence/post_gate_activation_guard.py
src/mpm_lbm/evidence/post_gate_output_guard.py
src/mpm_lbm/evidence/step76_regression_guard.py
```

Do not put Step76 evidence code under:

```text
src/mpm_lbm/sim/
experiments/steps/
```

### Baseline Runners

```text
baseline_tests/step76_common.py
baseline_tests/run_step76_post_gate_rebaseline_matrix.py
baseline_tests/run_step76_post_gate_rebaseline_quality.py
baseline_tests/run_step76_activation_guard.py
baseline_tests/run_step76_output_guard.py
baseline_tests/run_step76_step75_regression_guard.py
baseline_tests/run_step76_artifact_manifest.py
```

### Tests

```text
tests/test_step76_post_gate_rebaseline_matrix_contract.py
tests/test_step76_post_gate_rebaseline_quality_contract.py
tests/test_step76_activation_guard_contract.py
tests/test_step76_output_guard_contract.py
tests/test_step76_step75_regression_contract.py
```

### Docs

```text
docs/76_minimal_post_gate_canonical_driver_rebaseline.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

Update:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
```

Docs must state that Step76 is a minimal rebaseline only and does not authorize
runtime geometry, wall velocity, real geometry, squid proxy, 48^3, 64^3, VTR,
particle NPY, physical validation, or production readiness.

## Matrix Summary Requirements

The matrix artifact must include the required row and these fields, or a
compatible superset:

```text
row_name
campaign_id
gate_source_step
post_gate_simulation_allowed
allowed_next_step
allowed_next_step_scope
n_grid
n_particles
n_lbm_steps
mpm_substeps_per_lbm_step
coupling_mode
reaction_transfer_mode
geometry_type
runtime_geometry_enabled
wall_velocity_enabled
real_geometry_enabled
squid_proxy_enabled
link_area_enabled
grid_48_enabled
grid_64_enabled
write_vtk
write_particles
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
bb_link_count_max
bb_max_correction_max
active_reaction_particle_count_final
max_grid_reaction_norm_max
has_nan
has_inf
geo_path_name
diagnostics_csv_exists
diagnostics_npz_exists
driver_config_exists
elapsed_seconds
runtime_warning
stable
notes
```

## Acceptance Bounds

The required row must satisfy:

```text
row_name == canonical_driver_moving_boundary_engineering_32_1step_rebaseline
driver_run_called == true
canonical_driver_module == src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation == false
n_grid == 32
n_particles == 1024
n_lbm_steps == 1
mpm_substeps_per_lbm_step == 1
completed_lbm_steps == 1
total_mpm_substeps >= 1
diagnostics_row_count >= 2
runtime_geometry_enabled == false
wall_velocity_enabled == false
real_geometry_enabled == false
squid_proxy_enabled == false
link_area_enabled == false
grid_48_enabled == false
grid_64_enabled == false
write_vtk == false
write_particles == false
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
```

Runtime:

```text
elapsed_seconds recorded
runtime_warning = elapsed_seconds > 3600
runtime_warning does not fail by itself
```

## Activation Guard

Step76 must prove that the run did not exceed Step75 scope:

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
optional_32_3step_run == false
forbidden_campaign_item_count == 0
```

It must read Step75 campaign policy and confirm the required row matches the
allowed required Step76 row.

## Output Guard

Expected summary:

```text
step76_required_driver_run_dir_count == 1
step76_optional_driver_run_dir_count == 0
step76_vtr_count == 0
step76_particle_npy_count == 0
step76_large_file_count == 0
private_absolute_path_count == 0
protected_external_edit_count == 0
protected_real_geometry_candidate_edit_count == 0
step76_total_size_mb < 20
output_guard_pass == true
```

Forbidden Step76 files:

```text
*.vtr
particle *.npy
dense_displacement*
displaced_particle*
raw geometry files
private absolute paths in Step76 outputs/logs
large Step76 files above 5 MB
protected external files
protected real geometry candidate files
```

## Step75 Regression Guard

Step76 must confirm these committed Step75 artifacts are still green:

```text
outputs/step75_precondition_artifact_audit/precondition_artifact.json
outputs/step75_activation_gate_closure_audit/activation_gate_closure.json
outputs/step75_post_gate_campaign_policy_audit/post_gate_campaign_policy.json
outputs/step75_solver_complete_gate_audit/solver_complete_gate.json
outputs/step75_no_simulation_audit/no_simulation.json
outputs/step75_output_artifact_policy_audit/output_artifact_policy.json
outputs/step75_step74_regression_guard/step74_regression_guard.json
outputs/step75_artifact_manifest/artifact_summary.json
```

Required Step75 summary checks:

```text
precondition_artifact_audit_pass == true
activation_gate_closure_audit_pass == true
post_gate_campaign_policy_audit_pass == true
solver_complete_gate_audit_pass == true
no_simulation_audit_pass == true
output_artifact_policy_audit_pass == true
step75_step74_regression_guard_pass == true
artifact_budget_pass == true
gate_status == ready_for_step76_rebaseline_only
allowed_next_step == Step76
allowed_next_step_scope == minimal safe rebaseline only
activation_features_allowed_in_next_step == []
activation_allowed_count == 0
```

## Final Acceptance Criteria

Step76 passes only if:

```text
Step76 goal, report, docs, configs, runners, evidence modules, tests, logs, and artifacts exist.
The required rebaseline row runs through canonical FSIDriver3D.run().
Exactly one required Step76 driver run directory exists.
The optional 32^3/3-step row remains unrun.
The row completes one LBM step and at least one MPM substep.
Diagnostics have at least two rows and no NaN/Inf.
All numeric acceptance bounds pass.
All advanced activation features remain disabled.
No VTR, particle NPY, dense displacement, displaced particle, raw geometry, protected external, protected real geometry candidate, private absolute path, or large file output is introduced.
Step75 regression guard passes.
Focused Step76 pytest passes.
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
  src\mpm_lbm\evidence\post_gate_rebaseline_runner.py `
  src\mpm_lbm\evidence\post_gate_rebaseline_audit.py `
  src\mpm_lbm\evidence\post_gate_rebaseline_quality_audit.py `
  src\mpm_lbm\evidence\post_gate_activation_guard.py `
  src\mpm_lbm\evidence\post_gate_output_guard.py `
  src\mpm_lbm\evidence\step76_regression_guard.py `
  baseline_tests\step76_common.py `
  baseline_tests\run_step76_post_gate_rebaseline_matrix.py `
  baseline_tests\run_step76_post_gate_rebaseline_quality.py `
  baseline_tests\run_step76_activation_guard.py `
  baseline_tests\run_step76_output_guard.py `
  baseline_tests\run_step76_step75_regression_guard.py `
  baseline_tests\run_step76_artifact_manifest.py
```

Generate artifacts:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step76_post_gate_rebaseline_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step76_post_gate_rebaseline_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step76_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step76_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step76_step75_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step76_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest `
  tests\test_step76_post_gate_rebaseline_matrix_contract.py `
  tests\test_step76_post_gate_rebaseline_quality_contract.py `
  tests\test_step76_activation_guard_contract.py `
  tests\test_step76_output_guard_contract.py `
  tests\test_step76_step75_regression_contract.py `
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
git add <Step76 files>
git commit -m "test: add step76 minimal post-gate canonical driver rebaseline"
git push origin main
```
