# Step 61 Controlled Canonical 32 Moving-Boundary Single-Step Goal

## 1. Step Name

Step 61 Controlled Canonical 32^3 Moving-Boundary Single-Step Probe.

## 2. Starting Point

The repository starts from Step 60:

```text
60c2e916c5f5079f05c0f436b35c2083b83cfe28
test: add step60 canonical moving boundary duration ramp
```

Step 60 proved that the canonical `FSIDriver3D` moving-boundary engineering path can run a short finite/bounded duration ramp at 16^3:

```text
canonical_driver_moving_boundary_engineering_16_3step
canonical_driver_moving_boundary_engineering_16_5step
canonical_driver_penalty_16_5step
```

All Step 60 required rows called the real canonical driver run path, stayed finite, produced lightweight artifacts, and preserved:

```text
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = false
```

## 3. Core Objective

Step 61 expands exactly one dimension:

```text
grid: 16^3 -> 32^3
duration: stays at 1 LBM step
mode: moving_boundary engineering
```

The correct interpretation is:

```text
controlled canonical 32^3 real-driver single-step feasibility probe
finite/bounded feasibility smoke
```

The incorrect interpretations are:

```text
32^3 validation
grid convergence
production solver
physical propulsion validation
real squid validation
```

Step 61 must still call the real canonical driver run path:

```python
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

driver = FSIDriver3D(config, out_dir)
diagnostics = driver.run()
```

Step 61 must not replace the real 32^3 run with an import audit, constructor audit, proxy audit, or artifact-only audit.

## 4. Required Simulation Row

Step 61 must run exactly one required row:

```text
canonical_driver_moving_boundary_engineering_32_1step
```

Required configuration:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 1
mpm_substeps_per_lbm_step = 1
output_interval = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
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

## 5. Optional Rows

Step 61 may define, but must not run by default, these optional rows:

```text
canonical_driver_penalty_32_1step_optional
canonical_driver_moving_boundary_engineering_32_3step_optional
```

Default policy:

```text
run_optional_penalty_32_probe = false
run_optional_32_3step_probe = false
```

Step 61 acceptance must not depend on either optional row. Do not combine the grid increase with duration expansion in this step.

## 6. Runtime Code Boundary

Step 61 must not change runtime solver code by default.

Expected flags:

```text
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = false
```

Do not modify:

```text
src/mpm_lbm/sim/drivers/fsi_driver.py
src/mpm_lbm/sim/lbm/*
src/mpm_lbm/sim/mpm/*
src/mpm_lbm/sim/coupling/*
src/fsi_driver.py
external/taichi_LBM3D
data/real_geometry_candidates
```

If the 32^3 single-step run exposes a runtime solver bug, stop and report the failure rather than mixing a solver repair into Step 61 evidence. Only pure output, path, evidence, or guard bugs may be fixed inside Step 61.

## 7. Explicit Non-Goals

Step 61 must not implement or claim:

```text
runtime geometry
wall velocity application
geometry motion
prescribed boundary motion
48^3 rows
64^3 rows
3-step required row
5-step required row
20-step or longer row
required link_area_experimental row
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
runtime solver code changes
```

## 8. Required Config Files

Add:

```text
configs/step61_controlled_canonical_32_moving_boundary_single_step.json
configs/step61_canonical_driver_moving_boundary_engineering_32_1step.json
configs/step61_canonical_driver_penalty_32_1step_optional.json
configs/step61_canonical_driver_moving_boundary_engineering_32_3step_optional.json
configs/step61_single_step_acceptance_policy.json
configs/step61_output_guard_policy.json
configs/step61_runtime_budget_policy.json
```

The required config file must be explicit checked-in JSON. Optional config files must be checked in but disabled by default.

## 9. Required Evidence Source Files

Add:

```text
src/mpm_lbm/evidence/canonical_driver_32_probe_runner.py
src/mpm_lbm/evidence/canonical_driver_32_probe_audit.py
src/mpm_lbm/evidence/canonical_driver_32_probe_output_guard.py
src/mpm_lbm/evidence/step61_regression_guard.py
```

These files must live under the canonical evidence package. Do not add root `src/*.py` implementation files.

## 10. Required Baseline Runners

Add:

```text
baseline_tests/step61_common.py
baseline_tests/run_step61_32_probe_matrix.py
baseline_tests/run_step61_32_probe_quality.py
baseline_tests/run_step61_output_guard.py
baseline_tests/run_step61_step60_regression_guard.py
baseline_tests/run_step61_artifact_manifest.py
```

`run_step61_32_probe_matrix.py` must call:

```python
config = FSIDriverConfig.from_json("configs/step61_canonical_driver_moving_boundary_engineering_32_1step.json")
driver = FSIDriver3D(config, "outputs/step61_driver_runs/canonical_driver_moving_boundary_engineering_32_1step")
diagnostics = driver.run()
```

The quality runner may read matrix artifacts and enforce policy. It must not replace the real 32^3 run.

## 11. Required Tests

Add:

```text
tests/test_step61_32_probe_contract.py
tests/test_step61_32_probe_quality_contract.py
tests/test_step61_output_guard_contract.py
tests/test_step61_step60_regression_contract.py
```

Tests must check both current source/audit behavior and committed output artifacts.

## 12. Required Docs And Report

Add:

```text
STEP61_CONTROLLED_CANONICAL_32_MOVING_BOUNDARY_SINGLE_STEP_REPORT.md
docs/61_controlled_canonical_32_moving_boundary_single_step.md
```

Update:

```text
README.md
docs/00_project_status.md
```

The docs must state that Step 61 is a controlled canonical 32^3 real-driver single-step probe only.

## 13. Required Outputs And Logs

Generate and commit:

```text
outputs/step61_driver_runs/canonical_driver_moving_boundary_engineering_32_1step/
outputs/step61_32_probe_matrix/
outputs/step61_32_probe_quality/
outputs/step61_output_guard/
outputs/step61_step60_regression_guard/
outputs/step61_artifact_manifest/
logs/step61_*.log
```

Do not generate optional run directories unless explicitly enabled:

```text
outputs/step61_driver_runs/canonical_driver_penalty_32_1step_optional/
outputs/step61_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_optional/
```

The required run directory may contain only:

```text
driver_config.json
geo_all_fluid_32.dat
diagnostics_timeseries.csv
diagnostics_timeseries.npz
```

## 14. Required Matrix Row Schema

The Step 61 matrix row must include at least:

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

## 15. Required 32^3 Row Acceptance Criteria

For `canonical_driver_moving_boundary_engineering_32_1step`:

```text
driver_run_called == true
canonical_driver_module == src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation == false
initialized == true
n_grid == 32
n_particles == 1024
n_lbm_steps == 1
mpm_substeps_per_lbm_step == 1
completed_lbm_steps == 1
total_mpm_substeps >= 1
diagnostics_row_count >= 2
diagnostics_csv_exists == true
diagnostics_npz_exists == true
driver_config_exists == true
geo_path_name == geo_all_fluid_32.dat
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
bb_link_count_max > 0
bb_max_correction_max >= 0.0
active_reaction_particle_count_final >= 0
max_grid_reaction_norm_max finite
all numeric diagnostics finite
```

## 16. Runtime Policy

Step 61 must record runtime:

```text
elapsed_seconds
runtime_warning
```

Runtime warning is a soft signal, not a direct row failure:

```text
runtime_warning == true only if elapsed_seconds > 3600
```

If elapsed runtime exceeds 3600 seconds, Step 62 must not expand duration or grid and should become a performance/timing audit.

## 17. Output Guard Criteria

Allowed required driver run files:

```text
driver_config.json
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
step61_required_driver_run_dir_count == 1
step61_optional_driver_run_dir_count == 0 unless explicitly enabled
step61_vtr_count == 0
step61_particle_npy_count == 0
step61_large_file_count == 0
private_absolute_path_count == 0
external_edit_count == 0
real_geometry_candidates_edit_count == 0
step61_total_size_mb < 20
```

## 18. Step 60 Regression Guard Criteria

Step 61 must confirm Step 60 remains green:

```text
Step60 duration ramp matrix pass
Step60 duration ramp quality pass
Step60 output guard pass
Step60 Step59 regression guard pass
Step60 artifact manifest pass
Step60 required rows still present
Step60 legacy driver implementation count == 0
Step60 runtime_code_changed == false
Step60 solver_behavior_changed == false
Step60 physics_feature_expansion == false
```

## 19. Required Report Content

The Step 61 report must include:

```text
Goal
Runtime vs diagnostic boundary
Files created and updated
Explicit non-goals
Required configs
32^3 single-step matrix
32^3 probe quality
Runtime timing summary
Output guard
Step60 regression guard
Artifact manifest
Verification commands
Acceptance checklist
Decision for Step62
```

The report must avoid:

```text
validated propulsion
real squid validation
squid swimming
grid convergence
production ready
physical validation
```

Preferred wording:

```text
controlled canonical 32^3 real-driver single-step probe
finite/bounded feasibility smoke
```

## 20. Verification Commands

Compile:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\evidence\canonical_driver_32_probe_runner.py `
  src\mpm_lbm\evidence\canonical_driver_32_probe_audit.py `
  src\mpm_lbm\evidence\canonical_driver_32_probe_output_guard.py `
  src\mpm_lbm\evidence\step61_regression_guard.py `
  baseline_tests\step61_common.py `
  baseline_tests\run_step61_32_probe_matrix.py `
  baseline_tests\run_step61_32_probe_quality.py `
  baseline_tests\run_step61_output_guard.py `
  baseline_tests\run_step61_step60_regression_guard.py `
  baseline_tests\run_step61_artifact_manifest.py `
  tests\test_step61_32_probe_contract.py `
  tests\test_step61_32_probe_quality_contract.py `
  tests\test_step61_output_guard_contract.py `
  tests\test_step61_step60_regression_contract.py
```

Generate Step 61 artifacts:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step61_32_probe_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step61_32_probe_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step61_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step61_step60_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step61_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step61_32_probe_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step61_32_probe_quality_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step61_output_guard_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step61_step60_regression_contract.py -q
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
git commit -m "test: add step61 canonical 32 moving boundary single step"
git push origin main
```

## 21. Step 62 Decision Rule

After Step 61:

```text
If the 32^3 / 1-step moving-boundary row passes and runtime is manageable:
  Step 62 may be canonical 32^3 moving-boundary 3-step duration probe.

If Step 61 passes but runtime is very high:
  Step 62 should be a performance/timing audit, not duration or grid expansion.

If Step 61 fails numerically:
  Step 62 should be a 32^3 moving-boundary diagnostic/debug step.
```

Do not jump directly to:

```text
runtime geometry + wall velocity + 48^3 + longer cycle
```

Stable route:

```text
Step 61 = 32^3 moving_boundary engineering 1-step
Step 62 = 32^3 moving_boundary engineering 3-step, if runtime allows
Step 63 = optional 32^3 link_area or controlled runtime-geometry smoke, one feature only
Step 64 = runtime geometry plus wall velocity real-driver simulation, if previous gates stay green
```

## 22. Done Criteria

Step 61 is complete only when:

```text
Detailed goal file exists and active goal references it.
All required configs, evidence modules, runners, tests, docs, report, logs, and artifacts are committed.
The required 32^3 single-step row has real `driver.run()` artifacts.
Quality audit passes.
Output guard passes.
Step 60 regression guard passes.
Artifact manifest passes.
Focused Step 61 tests pass.
Full Taichi pytest passes.
Full Anaconda pytest passes.
Git checks pass.
Commit uses: test: add step61 canonical 32 moving boundary single step
Commit is pushed to origin/main.
Final response reports commit hash, remote branch, validation pass counts, artifact summary, and runtime timing.
```
