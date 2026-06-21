# Step 62 Controlled Canonical 32 Moving-Boundary 3-Step Duration Goal

## 1. Step Name

Step 62 Controlled Canonical 32^3 Moving-Boundary 3-Step Duration Probe.

## 2. Starting Point

The repository starts from Step 61:

```text
74cc17b77da0e281f7c2552d0d071f7befc38eae
test: add step61 canonical 32 moving boundary single step
```

Step 61 proved that the canonical `FSIDriver3D` moving-boundary engineering path can run the required 32^3 row for one LBM step:

```text
canonical_driver_moving_boundary_engineering_32_1step
```

The accepted Step 61 row:

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
boundary_motion_mode = static
wall_velocity_application_mode = disabled
geometry_motion_mode = static
geometry_motion_application_mode = disabled
```

Step 61 called the real canonical driver path:

```python
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

driver = FSIDriver3D(config, out_dir)
diagnostics = driver.run()
```

Step 61 also preserved:

```text
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = false
```

## 3. Step 61 Report Consistency Repair

Before expanding duration, Step 62 must repair a Step 61 report consistency issue.

The current `STEP61_CONTROLLED_CANONICAL_32_MOVING_BOUNDARY_SINGLE_STEP_REPORT.md` output-guard table records:

```text
step61_total_size_mb = 0.11867237091064453
```

The committed `outputs/step61_output_guard/output_guard.json` records:

```text
summary.step61_total_size_mb = 0.46668243408203125
```

The committed `outputs/step61_artifact_manifest/artifact_summary.json` records:

```text
step61_total_size_mb = 0.5198221206665039
```

This mismatch is a report-number consistency issue only. It is not a simulation failure, not a solver failure, and not a reason to rerun Step 61 unless Step 62 guards require regenerated Step 62 artifacts.

Step 62 must:

```text
update STEP61_CONTROLLED_CANONICAL_32_MOVING_BOUNDARY_SINGLE_STEP_REPORT.md
so the Output Guard table matches outputs/step61_output_guard/output_guard.json
```

Step 62 must also add a reusable report consistency guard that checks report numbers against JSON artifacts for both Step 61 and Step 62.

## 4. Core Objective

Step 62 expands exactly one dimension:

```text
duration: 1 LBM step -> 3 LBM steps
grid: stays 32^3
mode: stays moving_boundary engineering
```

The correct interpretation is:

```text
controlled canonical 32^3 moving-boundary engineering 3-step real-driver duration probe
finite/bounded duration feasibility smoke
```

The incorrect interpretations are:

```text
validation
grid convergence
production simulation
squid swimming
jet propulsion
real squid behavior validation
physical validation
```

Step 62 must not replace the real 32^3 / 3-step run with an import audit, constructor audit, proxy audit, artifact-only audit, or Step 61 artifact reuse. The required Step 62 row must actually call `driver.run()`.

## 5. Required Simulation Row

Step 62 must run exactly one required row:

```text
canonical_driver_moving_boundary_engineering_32_3step
```

Required configuration:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
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

## 6. Optional Rows

Step 62 may define, but must not run by default, these optional rows:

```text
canonical_driver_penalty_32_3step_optional
canonical_driver_moving_boundary_engineering_32_5step_optional
```

Default policy:

```text
run_optional_penalty_32_3step = false
run_optional_32_5step = false
```

Step 62 acceptance must not depend on optional rows. Do not combine the 3-step duration expansion with 5-step duration, link-area comparison, runtime geometry, wall velocity, or larger grid in this step.

## 7. Runtime Code Boundary

Step 62 must not change runtime solver code by default.

Expected flags:

```text
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = false
```

Do not modify runtime formulas or runtime state behavior in:

```text
src/mpm_lbm/sim/drivers/fsi_driver.py
src/mpm_lbm/sim/lbm/*
src/mpm_lbm/sim/mpm/*
src/mpm_lbm/sim/coupling/*
src/fsi_driver.py
```

Do not modify protected external or real-geometry candidate directories:

```text
external/taichi_LBM3D
data/real_geometry_candidates
```

If the 32^3 / 3-step row exposes a runtime solver bug, stop and report the failure rather than mixing a solver repair into Step 62 evidence. Only report, evidence, path, output, or guard consistency bugs may be fixed inside Step 62.

## 8. Explicit Non-Goals

Step 62 must not implement, run, or claim:

```text
48^3
64^3
5-step required row
longer cycle
link_area_experimental required row
runtime geometry
wall velocity application
geometry motion
prescribed boundary motion
real geometry
squid geometry
squid swimming
jet propulsion validation
real squid behavior validation
grid convergence
production readiness
LBM tau migration
standard viscosity migration
runtime solver code change
VTR output
particle NPY output
external/taichi_LBM3D edits
data/real_geometry_candidates edits
```

## 9. Required Config Files

Add:

```text
configs/step62_controlled_canonical_32_moving_boundary_3step_duration.json
configs/step62_canonical_driver_moving_boundary_engineering_32_3step.json
configs/step62_canonical_driver_penalty_32_3step_optional.json
configs/step62_canonical_driver_moving_boundary_engineering_32_5step_optional.json
configs/step62_duration_acceptance_policy.json
configs/step62_output_guard_policy.json
configs/step62_runtime_budget_policy.json
configs/step62_report_consistency_policy.json
```

The required config file must be explicit checked-in JSON. Optional config files must be checked in but disabled by default through the Step 62 matrix policy.

## 10. Required Evidence Source Files

Add:

```text
src/mpm_lbm/evidence/canonical_driver_32_duration_runner.py
src/mpm_lbm/evidence/canonical_driver_32_duration_audit.py
src/mpm_lbm/evidence/canonical_driver_32_duration_output_guard.py
src/mpm_lbm/evidence/report_consistency_guard.py
src/mpm_lbm/evidence/step62_regression_guard.py
```

These files must live under the canonical evidence package. Do not add root `src/*.py` implementation files.

## 11. Required Baseline Runners

Add:

```text
baseline_tests/step62_common.py
baseline_tests/run_step62_32_duration_matrix.py
baseline_tests/run_step62_32_duration_quality.py
baseline_tests/run_step62_output_guard.py
baseline_tests/run_step62_report_consistency_guard.py
baseline_tests/run_step62_step61_regression_guard.py
baseline_tests/run_step62_artifact_manifest.py
```

`run_step62_32_duration_matrix.py` must call the real canonical driver:

```python
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

config = FSIDriverConfig.from_json(
    "configs/step62_canonical_driver_moving_boundary_engineering_32_3step.json"
)
driver = FSIDriver3D(
    config,
    "outputs/step62_driver_runs/canonical_driver_moving_boundary_engineering_32_3step",
)
diagnostics = driver.run()
```

The quality runner may read matrix artifacts and enforce policy. It must not replace the real 32^3 / 3-step run.

## 12. Required Tests

Add:

```text
tests/test_step62_32_duration_contract.py
tests/test_step62_32_duration_quality_contract.py
tests/test_step62_output_guard_contract.py
tests/test_step62_report_consistency_contract.py
tests/test_step62_step61_regression_contract.py
```

Tests must check both current source/audit behavior and committed output artifacts.

## 13. Required Docs And Reports

Add:

```text
STEP62_CONTROLLED_CANONICAL_32_MOVING_BOUNDARY_3STEP_DURATION_REPORT.md
docs/62_controlled_canonical_32_moving_boundary_3step_duration.md
```

Update:

```text
README.md
docs/00_project_status.md
STEP61_CONTROLLED_CANONICAL_32_MOVING_BOUNDARY_SINGLE_STEP_REPORT.md
```

The Step 62 docs must state that this is a controlled canonical 32^3 moving-boundary 3-step duration probe only. The Step 61 report update must be limited to the report-number consistency repair unless a later consistency guard exposes another documented mismatch.

## 14. Required Outputs And Logs

Generate and commit:

```text
outputs/step62_driver_runs/canonical_driver_moving_boundary_engineering_32_3step/
outputs/step62_32_duration_matrix/
outputs/step62_32_duration_quality/
outputs/step62_output_guard/
outputs/step62_report_consistency_guard/
outputs/step62_step61_regression_guard/
outputs/step62_artifact_manifest/
logs/step62_*.log
```

Do not generate optional run directories unless explicitly enabled:

```text
outputs/step62_driver_runs/canonical_driver_penalty_32_3step_optional/
outputs/step62_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_optional/
```

The required driver run directory may contain only:

```text
driver_config.json
geo_all_fluid_32.dat
diagnostics_timeseries.csv
diagnostics_timeseries.npz
```

## 15. Required Matrix Row Schema

The Step 62 matrix row must include at least:

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

## 16. Required 32^3 / 3-Step Acceptance Criteria

For `canonical_driver_moving_boundary_engineering_32_3step`:

```text
driver_run_called == true
canonical_driver_module == src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation == false
initialized == true
n_grid == 32
n_particles == 1024
n_lbm_steps == 3
mpm_substeps_per_lbm_step == 1
completed_lbm_steps == 3
total_mpm_substeps >= 3
diagnostics_row_count >= 4
diagnostics_csv_exists == true
diagnostics_npz_exists == true
driver_config_exists == true
geo_path_name == geo_all_fluid_32.dat
has_nan == false
has_inf == false
stable == true
```

Numerical hard bounds:

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

Soft warning bounds:

```text
rho_min_min < 0.95 -> warning, not fail
rho_max_max > 1.05 -> warning, not fail
elapsed_seconds > 3600 -> warning, not fail
elapsed_seconds > 7200 -> hard fail unless manually overridden
```

## 17. Runtime Policy

Step 62 must record runtime:

```text
elapsed_seconds
runtime_warning
```

Runtime warning is a soft signal:

```text
runtime_warning == true only if elapsed_seconds > 3600
elapsed_seconds > 7200 must hard-fail unless an explicit manual override is added to the policy
```

If the 3-step runtime exceeds 3600 seconds but remains below 7200 seconds, Step 63 must not automatically expand both duration and feature scope. If it exceeds 7200 seconds, stop and report instead of pushing a green claim.

## 18. Output Guard Criteria

Allowed Step 62 required driver run files:

```text
driver_config.json
geo_all_fluid_32.dat
diagnostics_timeseries.csv
diagnostics_timeseries.npz
summary csv/json
logs
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
step62_required_driver_run_dir_count == 1
step62_optional_driver_run_dir_count == 0
step62_vtr_count == 0
step62_particle_npy_count == 0
step62_large_file_count == 0
step62_forbidden_file_count == 0
private_absolute_path_count == 0
external_edit_count == 0
real_geometry_candidates_edit_count == 0
step62_total_size_mb < 20
```

## 19. Report Consistency Guard Criteria

Add:

```text
outputs/step62_report_consistency_guard/report_consistency_guard.json
```

The report consistency guard must check:

```text
Step61 report output_guard size matches outputs/step61_output_guard/output_guard.json
Step61 report artifact_manifest size matches outputs/step61_artifact_manifest/artifact_summary.json
Step62 report output_guard size matches outputs/step62_output_guard/output_guard.json
Step62 report artifact_manifest size matches outputs/step62_artifact_manifest/artifact_summary.json
```

The guard should write rows with:

```text
step
report_path
artifact_path
metric
report_value
artifact_value
pass
notes
```

The guard summary should include:

```text
report_consistency_guard_pass
row_count
pass_count
fail_count
step61_report_consistency_issue_fixed
step62_report_consistency_checked
```

## 20. Step 61 Regression Guard Criteria

Step 62 must confirm Step 61 remains green:

```text
Step61 32 probe matrix pass
Step61 32 probe quality pass
Step61 output guard pass
Step61 Step60 regression guard pass
Step61 artifact manifest pass
Step61 required row still present
Step61 optional rows remain disabled
Step61 legacy driver implementation count == 0
Step61 runtime_code_changed == false
Step61 solver_behavior_changed == false
Step61 physics_feature_expansion == false
Step61 report consistency issue fixed or explicitly recorded
```

The Step 61 regression guard must not rerun Step 61's expensive 32^3 driver row unless the Step 62 implementation explicitly changes Step 61 artifacts. It may inspect committed JSON/CSV/report artifacts.

## 21. Required Report Content

The Step 62 report must include:

```text
Goal
Runtime vs diagnostic boundary
Step61 report consistency repair
Files created and updated
Explicit non-goals
Required configs
32^3 3-step duration matrix
32^3 duration quality
Runtime timing summary
Output guard
Report consistency guard
Step61 regression guard
Artifact manifest
Verification commands
Acceptance checklist
Decision for Step63
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
controlled canonical 32^3 moving-boundary 3-step duration probe
finite/bounded duration feasibility smoke
```

## 22. Artifact Manifest

Add a Step 62 artifact manifest generated by:

```text
baseline_tests/run_step62_artifact_manifest.py
```

The manifest must include Step 62 files and summary metrics:

```text
artifact_budget_pass
file_count
step62_file_count
step62_total_size_bytes
step62_total_size_mb
large_file_count
step62_vtr_count
step62_particle_npy_count
protected_external_taichi_lbm3d_step62_file_count
protected_real_geometry_candidates_step62_file_count
```

Hard requirements:

```text
artifact_budget_pass == true
large_file_count == 0
step62_vtr_count == 0
step62_particle_npy_count == 0
protected_external_taichi_lbm3d_step62_file_count == 0
protected_real_geometry_candidates_step62_file_count == 0
step62_total_size_mb < 20
```

## 23. README And Status Updates

Update `README.md` implemented list with:

```text
Step 62 controlled canonical 32^3 moving-boundary 3-step duration probe
```

Add a README boundary section explaining:

```text
Step 62 calls FSIDriver3D(...).run() through the canonical driver.
Step 62 runs one required 32^3, 1024-particle moving-boundary engineering row for 3 LBM steps.
Step 62 repairs the Step 61 report output-guard size mismatch and adds a report consistency guard.
Step 62 keeps runtime solver code unchanged.
Step 62 keeps optional 32^3 penalty 3-step and 32^3 moving-boundary 5-step configs disabled by default.
Step 62 keeps outputs lightweight and rejects VTR, particle NPY, large Step 62 files, private absolute paths, external edits, and real-geometry candidate edits.
Step 62 does not activate runtime geometry, wall velocity, link area, real geometry, or larger grids.
```

Update `docs/00_project_status.md` with the same concise Step 62 status.

## 24. Verification Commands

Compile:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\evidence\canonical_driver_32_duration_runner.py `
  src\mpm_lbm\evidence\canonical_driver_32_duration_audit.py `
  src\mpm_lbm\evidence\canonical_driver_32_duration_output_guard.py `
  src\mpm_lbm\evidence\report_consistency_guard.py `
  src\mpm_lbm\evidence\step62_regression_guard.py `
  baseline_tests\step62_common.py `
  baseline_tests\run_step62_32_duration_matrix.py `
  baseline_tests\run_step62_32_duration_quality.py `
  baseline_tests\run_step62_output_guard.py `
  baseline_tests\run_step62_report_consistency_guard.py `
  baseline_tests\run_step62_step61_regression_guard.py `
  baseline_tests\run_step62_artifact_manifest.py `
  tests\test_step62_32_duration_contract.py `
  tests\test_step62_32_duration_quality_contract.py `
  tests\test_step62_output_guard_contract.py `
  tests\test_step62_report_consistency_contract.py `
  tests\test_step62_step61_regression_contract.py
```

Generate Step 62 artifacts:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step62_32_duration_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step62_32_duration_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step62_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step62_report_consistency_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step62_step61_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step62_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step62_32_duration_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step62_32_duration_quality_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step62_output_guard_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step62_report_consistency_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step62_step61_regression_contract.py -q
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
git commit -m "test: add step62 canonical 32 moving boundary 3step duration"
git push origin main
```

## 25. Step 63 Decision Rule

If Step 62 passes and runtime remains manageable, Step 63 may choose one dimension only:

```text
A. 32^3 moving_boundary engineering 5-step duration probe
B. 32^3 moving_boundary link_area_experimental 1-step comparison
```

Recommended if Step 62 runtime stays below the soft warning threshold:

```text
Step 63 = 32^3 moving_boundary engineering 5-step duration probe
```

Only after stable 32^3 / 3-step and 5-step duration probes should the project consider:

```text
runtime geometry
wall velocity
link_area comparison
48^3
```

## 26. Done Criteria

Step 62 is complete only when:

```text
Detailed goal file exists and active goal references it.
Step 61 report output-guard size mismatch is repaired.
All required Step 62 configs, evidence modules, runners, tests, docs, report, logs, and artifacts are committed.
The required 32^3 / 3-step row has real FSIDriver3D.run() artifacts.
Duration quality audit passes.
Output guard passes.
Report consistency guard passes.
Step 61 regression guard passes.
Artifact manifest passes.
Focused Step 62 tests pass.
Full Taichi pytest passes.
Full Anaconda pytest passes.
Git checks pass.
Runtime solver code remains unchanged.
Protected external solver and real-geometry candidate directories remain unchanged.
Commit uses: test: add step62 canonical 32 moving boundary 3step duration
Commit is pushed to origin/main.
Final response reports commit hash, remote branch, validation pass counts, artifact summary, report consistency status, and runtime timing.
```
