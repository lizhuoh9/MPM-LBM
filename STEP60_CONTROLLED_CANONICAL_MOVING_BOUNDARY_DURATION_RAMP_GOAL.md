# Step 60 Controlled Canonical Moving-Boundary Duration Ramp Goal

## 1. Step Name

Step 60 Controlled Canonical Moving-Boundary Duration Ramp Simulation.

## 2. Starting Point

The repository starts from Step 59:

```text
0e636c50292a2f1887f582008000a9e416366f19
test: add step59 canonical fsidriver real smoke simulation
```

Step 59 proved that the canonical driver can run a real one-step simulation through:

```python
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D
driver.run()
```

Step 59 also fixed the canonical driver geometry-output filename to:

```python
self.geo_path = os.path.join(self.out_dir, f"geo_all_fluid_{self.config.n_grid}.dat")
```

and committed evidence showing that the required `none`, `penalty`, and `moving_boundary` engineering rows all called `driver.run()`, completed one LBM step, produced lightweight diagnostics, stayed finite, and used the canonical module rather than the legacy root implementation.

## 3. Core Objective

Implement and validate the first controlled duration ramp after the canonical driver smoke milestone.

Step 60 must prove that the canonical `FSIDriver3D` moving-boundary engineering path can extend from a one-step smoke check to a short finite/bounded duration ramp without changing runtime solver formulas or enabling new physics.

The correct interpretation is:

```text
controlled canonical real-driver duration ramp
finite/bounded smoke extension
```

The incorrect interpretations are:

```text
validated propulsion
squid swimming
real squid validation
grid convergence
production readiness
```

Step 60 must still call the real canonical driver run path. It must not replace the real run with an import audit, constructor audit, proxy audit, or artifact-only audit.

## 4. Required Duration Ramp Rows

Step 60 must run exactly these required rows:

```text
canonical_driver_moving_boundary_engineering_16_3step
canonical_driver_moving_boundary_engineering_16_5step
canonical_driver_penalty_16_5step
```

Common configuration:

```text
n_grid = 16
n_particles = 512
mpm_substeps_per_lbm_step = 1
output_interval = 1
geometry_type = box
write_vtk = false
write_particles = false
quality_check_enabled = false
quality_check_strict = false
boundary_motion_mode = static
wall_velocity_application_mode = disabled
geometry_motion_mode = static
geometry_motion_application_mode = disabled
```

Mode-specific configuration:

```text
canonical_driver_moving_boundary_engineering_16_3step:
  coupling_mode = moving_boundary
  reaction_transfer_mode = engineering
  n_lbm_steps = 3

canonical_driver_moving_boundary_engineering_16_5step:
  coupling_mode = moving_boundary
  reaction_transfer_mode = engineering
  n_lbm_steps = 5

canonical_driver_penalty_16_5step:
  coupling_mode = penalty
  reaction_transfer_mode = engineering
  n_lbm_steps = 5
```

## 5. Optional Guarded Row

Step 60 may define, but must not require, this optional row:

```text
canonical_driver_moving_boundary_engineering_32_1step_optional
```

Optional configuration:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 1
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
write_vtk = false
write_particles = false
```

The optional row must be controlled by:

```text
run_optional_32_probe = false
```

by default. Step 60 acceptance must not depend on this row.

## 6. Runtime Code Boundary

Step 60 should not change runtime code.

Expected flags:

```text
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = false
```

Do not modify:

```text
src/mpm_lbm/sim/drivers/fsi_driver.py
src/fsi_driver.py
external/taichi_LBM3D
data/real_geometry_candidates
```

unless a narrow failing Step 60 test exposes a real bug that must be fixed to complete the requested duration ramp.

If runtime code must be changed, the report must explicitly state:

```text
runtime_code_changed = true
reason = ...
solver_behavior_changed = true/false
```

## 7. Explicit Non-Goals

Step 60 must not implement or claim:

```text
runtime geometry
wall velocity application
geometry motion
boundary prescribed motion
48^3 validation
64^3 validation
20-step or longer runs
required link_area_experimental rows
real geometry
squid geometry
squid swimming
jet propulsion validation
grid convergence
production readiness
LBM tau migration
standard viscosity migration
VTR output
particle NPY output
external/taichi_LBM3D edits
data/real_geometry_candidates edits
```

## 8. Required Config Files

Add:

```text
configs/step60_controlled_canonical_moving_boundary_duration_ramp.json
configs/step60_canonical_driver_moving_boundary_engineering_16_3step.json
configs/step60_canonical_driver_moving_boundary_engineering_16_5step.json
configs/step60_canonical_driver_penalty_16_5step.json
configs/step60_canonical_driver_moving_boundary_engineering_32_1step_optional.json
configs/step60_duration_ramp_acceptance_policy.json
configs/step60_output_guard_policy.json
```

The required configs must be explicit checked-in JSON files. The optional 32^3 config must exist but remain disabled by default in the Step 60 matrix policy.

## 9. Required Evidence Source Files

Add:

```text
src/mpm_lbm/evidence/canonical_driver_duration_ramp_runner.py
src/mpm_lbm/evidence/canonical_driver_duration_ramp_audit.py
src/mpm_lbm/evidence/canonical_driver_duration_ramp_output_guard.py
src/mpm_lbm/evidence/step60_regression_guard.py
```

These files must live in the evidence/runner/test layer. They must not move or duplicate runtime solver implementation ownership.

## 10. Required Baseline Runners

Add:

```text
baseline_tests/step60_common.py
baseline_tests/run_step60_duration_ramp_matrix.py
baseline_tests/run_step60_duration_ramp_quality.py
baseline_tests/run_step60_output_guard.py
baseline_tests/run_step60_step59_regression_guard.py
baseline_tests/run_step60_artifact_manifest.py
```

`run_step60_duration_ramp_matrix.py` must call:

```python
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

driver = FSIDriver3D(config, out_dir)
diagnostics = driver.run()
```

The quality runner may read the matrix artifacts and enforce policy. It must not replace the real duration ramp run.

## 11. Required Tests

Add:

```text
tests/test_step60_duration_ramp_contract.py
tests/test_step60_duration_ramp_quality_contract.py
tests/test_step60_output_guard_contract.py
tests/test_step60_step59_regression_contract.py
```

Tests must check both current source/audit behavior and committed output artifacts.

## 12. Required Docs And Report

Add:

```text
STEP60_CONTROLLED_CANONICAL_MOVING_BOUNDARY_DURATION_RAMP_REPORT.md
docs/60_controlled_canonical_moving_boundary_duration_ramp.md
```

Update:

```text
README.md
docs/00_project_status.md
```

The docs must state that Step 60 is a controlled canonical real-driver duration ramp only.

## 13. Required Outputs And Logs

Generate and commit:

```text
outputs/step60_driver_runs/canonical_driver_moving_boundary_engineering_16_3step/
outputs/step60_driver_runs/canonical_driver_moving_boundary_engineering_16_5step/
outputs/step60_driver_runs/canonical_driver_penalty_16_5step/
outputs/step60_duration_ramp_matrix/
outputs/step60_duration_ramp_quality/
outputs/step60_output_guard/
outputs/step60_step59_regression_guard/
outputs/step60_artifact_manifest/
logs/step60_*.log
```

If the optional 32^3 row is deliberately run, also generate:

```text
outputs/step60_driver_runs/canonical_driver_moving_boundary_engineering_32_1step_optional/
```

Each required 16^3 driver run directory may contain only:

```text
driver_config.json
geo_all_fluid_16.dat
diagnostics_timeseries.csv
diagnostics_timeseries.npz
```

If the optional 32^3 row is run, its driver run directory may contain only:

```text
driver_config.json
geo_all_fluid_32.dat
diagnostics_timeseries.csv
diagnostics_timeseries.npz
```

## 14. Required Duration Ramp Row Schema

The duration ramp matrix rows must include at least:

```text
row_name
coupling_mode
reaction_transfer_mode
n_grid
n_particles
n_lbm_steps
mpm_substeps_per_lbm_step
completed_lbm_steps
total_mpm_substeps
diagnostics_row_count
canonical_driver_module
legacy_driver_module_used_as_implementation
driver_run_called
initialized
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
stable
notes
```

## 15. Required Matrix Acceptance Criteria

Every required row must satisfy:

```text
driver_run_called == true
canonical_driver_module == src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation == false
initialized == true
completed_lbm_steps == n_lbm_steps
total_mpm_substeps >= n_lbm_steps * mpm_substeps_per_lbm_step
diagnostics_row_count >= n_lbm_steps + 1
diagnostics_csv_exists == true
diagnostics_npz_exists == true
driver_config_exists == true
geo_path_name == geo_all_fluid_16.dat
has_nan == false
has_inf == false
stable == true
```

Numerical bounds:

```text
rho_min_min > 0.90
rho_max_max < 1.10
lbm_max_v_max < 0.5
mpm_min_J_min > 0.0
mpm_max_speed_max < 10.0
projected_mass_final > 0.0
active_cell_count_final > 0
all numeric diagnostics finite
```

Moving-boundary rows additionally require:

```text
bb_link_count_max > 0
bb_max_correction_max >= 0.0
active_reaction_particle_count_final >= 0
max_grid_reaction_norm_max finite
```

Penalty rows additionally require:

```text
cell_force_max_norm_max finite
hydro_force_max_norm_max finite
```

## 16. Runtime Budget Criteria

Step 60 must record runtime:

```text
elapsed_seconds per row
total_elapsed_seconds
slowest_row_name
```

Runtime is a soft warning, not a hard fail, unless the run produces incomplete artifacts. The default soft warning threshold is:

```text
runtime_warning_seconds = 1800
```

If a 5-step moving-boundary row exceeds 30 minutes, the report must recommend that Step 61 be a performance/timing audit rather than a larger grid or longer-duration run.

## 17. Output Guard Criteria

Allowed Step 60 driver run files:

```text
driver_config.json
geo_all_fluid_16.dat
geo_all_fluid_32.dat
diagnostics_timeseries.csv
diagnostics_timeseries.npz
```

Forbidden:

```text
.vtr
particle .npy
particle output directory
displaced_particle
dense_displacement
real geometry candidate files
external edits
large files
private absolute paths
```

Hard criteria:

```text
step60_vtr_count == 0
step60_particle_npy_count == 0
step60_large_file_count == 0
private_absolute_path_count == 0
external_edit_count == 0
real_geometry_candidates_edit_count == 0
step60_total_size_mb < 10
```

## 18. Step 59 Regression Guard Criteria

Step 60 must confirm Step 59 remains green:

```text
Step59 smoke matrix pass
Step59 smoke quality pass
Step59 geo path naming pass
Step59 output guard pass
Step59 Step58 regression pass
Step59 artifact manifest pass
required Step59 rows still present
canonical_driver_module still canonical
legacy_driver_module_used_count == 0
```

## 19. Required Report Content

The Step 60 report must include:

```text
Goal
Runtime vs diagnostic boundary
Files created and updated
Explicit non-goals
Required configs
Duration ramp matrix
Duration ramp quality
Runtime timing summary
Output guard
Step59 regression guard
Artifact manifest
Verification commands
Acceptance checklist
Decision for Step61
```

The report must avoid:

```text
validated propulsion
squid swimming
grid convergence
production ready
physical validation
```

Preferred wording:

```text
controlled canonical real-driver duration ramp
finite/bounded smoke extension
```

## 20. Verification Commands

Compile:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\evidence\canonical_driver_duration_ramp_runner.py `
  src\mpm_lbm\evidence\canonical_driver_duration_ramp_audit.py `
  src\mpm_lbm\evidence\canonical_driver_duration_ramp_output_guard.py `
  src\mpm_lbm\evidence\step60_regression_guard.py `
  baseline_tests\step60_common.py `
  baseline_tests\run_step60_duration_ramp_matrix.py `
  baseline_tests\run_step60_duration_ramp_quality.py `
  baseline_tests\run_step60_output_guard.py `
  baseline_tests\run_step60_step59_regression_guard.py `
  baseline_tests\run_step60_artifact_manifest.py `
  tests\test_step60_duration_ramp_contract.py `
  tests\test_step60_duration_ramp_quality_contract.py `
  tests\test_step60_output_guard_contract.py `
  tests\test_step60_step59_regression_contract.py
```

Generate Step 60 artifacts:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step60_duration_ramp_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step60_duration_ramp_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step60_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step60_step59_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step60_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step60_duration_ramp_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step60_duration_ramp_quality_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step60_output_guard_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step60_step59_regression_contract.py -q
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
git status --short
git add .
git diff --cached --check
git commit -m "test: add step60 canonical moving boundary duration ramp"
git push origin main
```

## 21. Step 61 Decision Rule

After Step 60:

```text
If 16^3 / 5-step moving_boundary is stable and runtime is acceptable:
  Step 61 may be 32^3 canonical moving-boundary short simulation, starting with 1-3 steps.

If runtime is very slow or the 5-step row approaches an unacceptable duration:
  Step 61 should be a performance/timing audit, not a larger grid or runtime geometry step.

If moving_boundary becomes unstable:
  Step 61 should be a moving-boundary diagnostic/debug step, not new feature expansion.

If all rows are green:
  Step 61 may start planning runtime geometry plus wall velocity real-driver simulation, but should not combine 48^3, long cycle, wall velocity, and runtime geometry at once.
```

The conservative route remains:

```text
Step 60 = 16^3 moving-boundary duration ramp, 3/5 steps
Step 61 = 32^3 controlled moving-boundary short simulation
Step 62 = runtime geometry plus wall velocity real-driver simulation
Step 63 = 48^3 or link_area comparison, not both at once
```

## 22. Done Criteria

Step 60 is complete only when:

```text
Detailed goal file exists and active goal references it.
All required configs, evidence modules, runners, tests, docs, report, logs, and artifacts are committed.
Required duration ramp rows have real `driver.run()` artifacts.
Quality audit passes.
Output guard passes.
Step 59 regression guard passes.
Artifact manifest passes.
Focused Step 60 tests pass.
Full Taichi pytest passes.
Full Anaconda pytest passes.
Git checks pass.
Commit uses: test: add step60 canonical moving boundary duration ramp
Commit is pushed to origin/main.
Final response reports commit hash, remote branch, validation pass counts, artifact summary, and runtime timing.
```
