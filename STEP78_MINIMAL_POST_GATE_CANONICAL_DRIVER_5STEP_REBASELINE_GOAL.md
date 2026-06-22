# Step78 Minimal Post-Gate Canonical Driver 5-Step Rebaseline Goal

## Step Name

`Step78 Minimal Post-Gate Canonical Driver 5-Step Rebaseline`

## Required Commit Message

`test: add step78 minimal post-gate canonical driver 5step rebaseline`

## Repository And Baseline

Repository root:

`D:\working\squid robot\LBM\MPM-LBM`

Required starting point:

```text
origin/main = e3b6e444eb0326c572d4ce94b93a54554f1986e4
commit = test: add step77 minimal post-gate canonical driver 3step rebaseline
```

Step78 starts only after Step77 accepted the minimal post-gate three-step
canonical driver rebaseline:

```text
post_gate_3step_rebaseline_matrix_pass = true
post_gate_3step_rebaseline_quality_pass = true
post_gate_3step_activation_guard_pass = true
output_guard_pass = true
step77_step76_regression_guard_pass = true
artifact_budget_pass = true
```

Step77 ran exactly one required canonical driver row:

```text
row_name = canonical_driver_moving_boundary_engineering_32_3step_rebaseline
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
activation_feature_count = 0
```

## Core Objective

Step78 extends exactly one dimension from Step77:

```text
duration: 3 LBM steps -> 5 LBM steps
```

All other dimensions must remain equivalent to Step77:

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
rebaseline can extend from three LBM steps to five LBM steps without enabling
any advanced feature or changing solver formulas.

Step78 is the last pure duration-baseline extension in this ladder. Do not add
a Step78 10-step row. After Step78 is accepted, the next work should move to
single-feature activation planning, starting with runtime geometry
diagnostic-only plan and guard work.

## Explicit Non-Goals

Step78 is not:

```text
runtime geometry activation
wall velocity activation
combined runtime geometry plus wall velocity activation
real geometry activation
squid proxy activation
link-area activation
48^3 or 64^3 validation
10-step baseline
VTR output enablement
particle NPY output enablement
tau migration
solver formula migration
physical validation
real squid validation
grid convergence
production readiness
```

Step78 must not claim:

```text
real squid simulation can run
runtime geometry has been physically validated
wall velocity has been physically validated
real geometry has been validated
the solver is production-ready
```

## Required Row

The only required row is:

```text
canonical_driver_moving_boundary_engineering_32_5step_rebaseline
```

Required config:

```json
{
  "boundary_motion_mode": "static",
  "coupling_mode": "moving_boundary",
  "geometry_motion_application_mode": "disabled",
  "geometry_motion_mode": "static",
  "geometry_type": "box",
  "mpm_substeps_per_lbm_step": 1,
  "n_grid": 32,
  "n_lbm_steps": 5,
  "n_particles": 1024,
  "output_interval": 1,
  "quality_check_enabled": false,
  "quality_check_strict": false,
  "reaction_transfer_mode": "engineering",
  "wall_velocity_application_mode": "disabled",
  "write_particles": false,
  "write_vtk": false
}
```

Expected driver-run files only:

```text
outputs/step78_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_rebaseline/driver_config.json
outputs/step78_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_rebaseline/geo_all_fluid_32.dat
outputs/step78_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_rebaseline/diagnostics_timeseries.csv
outputs/step78_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_rebaseline/diagnostics_timeseries.npz
```

## Allowed Files And Surfaces

Step78 may add:

```text
STEP78_MINIMAL_POST_GATE_CANONICAL_DRIVER_5STEP_REBASELINE_GOAL.md
STEP78_MINIMAL_POST_GATE_CANONICAL_DRIVER_5STEP_REBASELINE_REPORT.md

configs/step78_minimal_post_gate_canonical_driver_5step_rebaseline.json
configs/step78_canonical_driver_moving_boundary_engineering_32_5step_rebaseline.json
configs/step78_rebaseline_acceptance_policy.json
configs/step78_activation_guard_policy.json
configs/step78_output_guard_policy.json
configs/step78_step77_regression_policy.json

src/mpm_lbm/evidence/post_gate_5step_rebaseline_runner.py
src/mpm_lbm/evidence/post_gate_5step_rebaseline_audit.py
src/mpm_lbm/evidence/post_gate_5step_rebaseline_quality_audit.py
src/mpm_lbm/evidence/post_gate_5step_activation_guard.py
src/mpm_lbm/evidence/post_gate_5step_output_guard.py
src/mpm_lbm/evidence/step78_regression_guard.py

baseline_tests/step78_common.py
baseline_tests/run_step78_post_gate_5step_rebaseline_matrix.py
baseline_tests/run_step78_post_gate_5step_rebaseline_quality.py
baseline_tests/run_step78_activation_guard.py
baseline_tests/run_step78_output_guard.py
baseline_tests/run_step78_step77_regression_guard.py
baseline_tests/run_step78_artifact_manifest.py

tests/test_step78_post_gate_5step_rebaseline_matrix_contract.py
tests/test_step78_post_gate_5step_rebaseline_quality_contract.py
tests/test_step78_activation_guard_contract.py
tests/test_step78_output_guard_contract.py
tests/test_step78_step77_regression_contract.py

docs/78_minimal_post_gate_canonical_driver_5step_rebaseline.md

outputs/step78_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_rebaseline/
outputs/step78_post_gate_5step_rebaseline_matrix/
outputs/step78_post_gate_5step_rebaseline_quality/
outputs/step78_activation_guard/
outputs/step78_output_guard/
outputs/step78_step77_regression_guard/
outputs/step78_artifact_manifest/

logs/step78_*.log
```

Step78 may update status documents that already track the step ladder:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md
```

## Forbidden Files And Surfaces

Step78 must not edit solver/runtime implementation surfaces:

```text
src/mpm_lbm/sim/**
src/mpm_lbm/diagnostics/**
src/mpm_lbm/geometry/**
src/mpm_lbm/coupling/**
external/taichi_LBM3D/**
data/real_geometry_candidates/**
```

Step78 must not change:

```text
LBM formulas
LBM tau convention
MPM update formulas
MPM material formulas
projector formulas
moving-boundary formulas
wall velocity formulas
geometry mutation formulas
```

## Acceptance Requirements

Driver identity:

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation = false
```

Duration:

```text
completed_lbm_steps = 5
total_mpm_substeps >= 5
diagnostics_row_count >= 6
```

Stability:

```text
has_nan = false
has_inf = false
stable = true
runtime_warning = false or explicitly reported
runtime_hard_fail = false
```

Numerical acceptance:

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
max_grid_reaction_norm_max finite
```

Scope guard:

```text
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
activation_feature_count = 0
```

Output guard:

```text
one required driver run dir
zero optional driver run dirs
no VTR
no particle NPY
no dense displacement output
no displaced particle output
no raw real geometry output
no private absolute paths
no protected external edits
no protected real geometry candidate edits
artifact budget pass
```

Regression guard:

```text
Step77 matrix pass remains true
Step77 quality pass remains true
Step77 activation guard pass remains true
Step77 output guard pass remains true
Step77 Step76 regression guard pass remains true
Step77 artifact manifest pass remains true
```

## Required Evidence Artifacts

Matrix:

```text
outputs/step78_post_gate_5step_rebaseline_matrix/post_gate_5step_rebaseline_matrix.json
outputs/step78_post_gate_5step_rebaseline_matrix/post_gate_5step_rebaseline_matrix.csv
outputs/step78_post_gate_5step_rebaseline_matrix/post_gate_5step_rebaseline_matrix_summary.csv
```

Quality:

```text
outputs/step78_post_gate_5step_rebaseline_quality/post_gate_5step_rebaseline_quality.json
outputs/step78_post_gate_5step_rebaseline_quality/post_gate_5step_rebaseline_quality.csv
outputs/step78_post_gate_5step_rebaseline_quality/post_gate_5step_rebaseline_quality_summary.csv
```

Activation guard:

```text
outputs/step78_activation_guard/activation_guard.json
outputs/step78_activation_guard/activation_guard.csv
outputs/step78_activation_guard/activation_guard_summary.csv
```

Output guard:

```text
outputs/step78_output_guard/output_guard.json
outputs/step78_output_guard/output_guard.csv
outputs/step78_output_guard/output_guard_summary.csv
```

Regression guard:

```text
outputs/step78_step77_regression_guard/step77_regression_guard.json
outputs/step78_step77_regression_guard/step77_regression_guard.csv
outputs/step78_step77_regression_guard/step77_regression_guard_summary.csv
```

Artifact manifest:

```text
outputs/step78_artifact_manifest/artifact_summary.json
outputs/step78_artifact_manifest/artifact_summary.csv
outputs/step78_artifact_manifest/artifact_manifest.csv
```

Logs:

```text
logs/step78_post_gate_5step_rebaseline_matrix.log
logs/step78_post_gate_5step_rebaseline_quality.log
logs/step78_activation_guard.log
logs/step78_output_guard.log
logs/step78_step77_regression_guard.log
logs/step78_artifact_manifest.log
```

## Required Commands

Evidence generation:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step78_post_gate_5step_rebaseline_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step78_post_gate_5step_rebaseline_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step78_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step78_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step78_step77_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step78_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step78_post_gate_5step_rebaseline_matrix_contract.py tests\test_step78_post_gate_5step_rebaseline_quality_contract.py tests\test_step78_activation_guard_contract.py tests\test_step78_output_guard_contract.py tests\test_step78_step77_regression_contract.py -q
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

Commit and push:

```powershell
git add <Step78 files>
git commit -m "test: add step78 minimal post-gate canonical driver 5step rebaseline"
git push origin main
```

## Documentation Requirements

The Step78 report must state exactly:

```text
Step78 is a minimal post-gate canonical driver 5-step rebaseline.
Step78 changes duration only.
Step78 does not activate runtime geometry, wall velocity, real geometry,
squid proxy, link-area transfer, larger grids, VTR output, or particle output.
Step78 does not validate physical behavior, real squid behavior, grid
convergence, runtime geometry, wall velocity, real geometry, or production
readiness.
```

The docs must also record the next direction:

```text
After Step78, do not continue to a 10-step box baseline. The next step should
start single-feature activation planning with runtime geometry diagnostic-only
plan and guard work.
```
