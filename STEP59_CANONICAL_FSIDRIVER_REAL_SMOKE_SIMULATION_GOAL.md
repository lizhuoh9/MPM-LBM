# Step 59 Canonical FSIDriver Real Smoke Simulation Goal

## 1. Step Name

Step 59 Canonical FSIDriver Real Smoke Simulation.

## 2. Starting Point

The repository starts from Step 58:

```text
aa1b04c7261460b1c53bf80ff5414c1231e09f3b
test: add step58 canonical fsidriver implementation migration wave3
```

Step 58 migrated the real `FSIDriver3D` implementation to:

```text
src/mpm_lbm/sim/drivers/fsi_driver.py
```

and converted:

```text
src/fsi_driver.py
```

into a thin compatibility shim.

Step 58 also added temporary canonical bridge surfaces for optional motion and wall-velocity hooks. Those bridges are import surfaces only, still forwarding to the legacy implementations through `legacy_getattr`.

## 3. Core Objective

Implement and validate the first real canonical-driver smoke simulations after the Step 58 migration.

Step 59 must prove that the canonical driver implementation can:

```python
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D
driver.run()
```

and that this call performs a real initialization, real LBM/MPM stepping, and real lightweight diagnostics output.

Step 59 must not be only an import audit, constructor audit, proxy audit, or artifact audit.

## 4. Required Real Smoke Rows

Step 59 must run at least these three real canonical-driver rows:

```text
canonical_driver_none_16_1step
canonical_driver_penalty_16_1step
canonical_driver_moving_boundary_engineering_16_1step
```

Common configuration:

```text
n_grid = 16
n_particles = 512
n_lbm_steps = 1
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
none:
  coupling_mode = none

penalty:
  coupling_mode = penalty

moving_boundary_engineering:
  coupling_mode = moving_boundary
  reaction_transfer_mode = engineering
```

The optional Step 59 `link_area_experimental` row may be implemented and recorded as optional evidence, but it must not be required for Step 59 acceptance.

## 5. Required Geo Path Naming Fix

Fix the stale fixed geometry filename in:

```text
src/mpm_lbm/sim/drivers/fsi_driver.py
```

from:

```python
self.geo_path = os.path.join(self.out_dir, "geo_all_fluid_32.dat")
```

to:

```python
self.geo_path = os.path.join(self.out_dir, f"geo_all_fluid_{self.config.n_grid}.dat")
```

Acceptance requirements:

```text
FSIDriverConfig(n_grid=16) -> geo_all_fluid_16.dat
FSIDriverConfig(n_grid=32) -> geo_all_fluid_32.dat
FSIDriverConfig(n_grid=48) -> geo_all_fluid_48.dat
constructor does not create files
```

This is an output naming correction only. It must not change solver formulas or physics.

## 6. Required Config Files

Add:

```text
configs/step59_canonical_fsidriver_real_smoke_simulation.json
configs/step59_canonical_driver_none_16_1step.json
configs/step59_canonical_driver_penalty_16_1step.json
configs/step59_canonical_driver_moving_boundary_engineering_16_1step.json
configs/step59_geo_path_naming_policy.json
configs/step59_smoke_acceptance_policy.json
```

If the optional link-area row is included, add:

```text
configs/step59_canonical_driver_moving_boundary_link_area_16_1step.json
```

The required config files must be explicit checked-in JSON files, not implicit runner-only defaults.

## 7. Required Source Files

Add Step 59 evidence/smoke support under canonical evidence code:

```text
src/mpm_lbm/evidence/canonical_driver_smoke_runner.py
src/mpm_lbm/evidence/canonical_driver_smoke_audit.py
src/mpm_lbm/evidence/canonical_driver_output_guard.py
src/mpm_lbm/evidence/geo_path_naming_audit.py
```

Modify:

```text
src/mpm_lbm/sim/drivers/fsi_driver.py
```

only for the `geo_all_fluid_{n_grid}.dat` naming fix unless a narrow test-driven correction is required for Step 59 smoke execution.

Keep:

```text
src/fsi_driver.py
```

as a thin compatibility shim.

Do not migrate the real boundary-motion, geometry-motion, or wall-velocity implementations in Step 59.

## 8. Required Baseline Runners

Add:

```text
baseline_tests/step59_common.py
baseline_tests/run_step59_canonical_driver_smoke_matrix.py
baseline_tests/run_step59_canonical_driver_smoke_quality.py
baseline_tests/run_step59_geo_path_naming_audit.py
baseline_tests/run_step59_output_guard.py
baseline_tests/run_step59_step58_regression_guard.py
baseline_tests/run_step59_artifact_manifest.py
```

The smoke matrix runner must call `FSIDriver3D(...).run()` from:

```text
src.mpm_lbm.sim.drivers.fsi_driver
```

The smoke quality runner may read smoke matrix artifacts and enforce acceptance policy. It must not replace the real smoke run.

## 9. Required Tests

Add:

```text
tests/test_step59_canonical_driver_real_smoke_contract.py
tests/test_step59_geo_path_naming_contract.py
tests/test_step59_output_guard_contract.py
tests/test_step59_step58_regression_contract.py
```

Tests must check both current source/audit behavior and committed output artifacts.

## 10. Required Docs And Report

Add:

```text
STEP59_CANONICAL_FSIDRIVER_REAL_SMOKE_SIMULATION_REPORT.md
docs/59_canonical_fsidriver_real_smoke_simulation.md
```

Update:

```text
README.md
docs/00_project_status.md
```

The docs must state that Step 59 is a canonical-driver real smoke simulation only.

## 11. Required Outputs And Logs

Generate and commit:

```text
outputs/step59_driver_runs/canonical_driver_none_16_1step/
outputs/step59_driver_runs/canonical_driver_penalty_16_1step/
outputs/step59_driver_runs/canonical_driver_moving_boundary_engineering_16_1step/
outputs/step59_canonical_driver_smoke_matrix/
outputs/step59_canonical_driver_smoke_quality/
outputs/step59_geo_path_naming_audit/
outputs/step59_output_guard/
outputs/step59_step58_regression_guard/
outputs/step59_artifact_manifest/
logs/step59_*.log
```

Each driver run directory may contain only lightweight smoke artifacts:

```text
driver_config.json
geo_all_fluid_16.dat
diagnostics_timeseries.csv
diagnostics_timeseries.npz
```

No VTR or particle NPY output is allowed for Step 59.

## 12. Required Smoke Summary Schema

The smoke matrix summary rows must include at least:

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
initialized
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
projected_mass
active_cell_count
cell_force_max_norm
hydro_force_max_norm
bb_link_count
bb_max_correction
active_reaction_particle_count
max_grid_reaction_norm
has_nan
has_inf
driver_run_called
canonical_driver_module
legacy_driver_module_used_as_implementation
stable
notes
```

## 13. Required Smoke Acceptance Criteria

For every required smoke row:

```text
driver_run_called == true
canonical_driver_module == src.mpm_lbm.sim.drivers.fsi_driver
legacy_driver_module_used_as_implementation == false
completed_lbm_steps == 1
total_mpm_substeps >= 1
diagnostics_row_count >= 2
rho_min > 0.90
rho_max < 1.10
lbm_max_v < 0.5
mpm_min_J > 0.0
all numeric diagnostics finite
has_nan == false
has_inf == false
stable == true
```

Mode-specific criteria:

```text
none:
  cell_force_max_norm finite
  hydro_force_max_norm finite

penalty:
  penalty coupler exists during run
  cell_force_max_norm finite
  hydro_force_max_norm finite

moving_boundary_engineering:
  moving-boundary coupler exists during run
  bb_link_count >= 0
  bb_max_correction finite
  active_reaction_particle_count >= 0
  max_grid_reaction_norm finite
```

Do not require physical accuracy or validation beyond these smoke-level stability checks.

## 14. Required Output Guard Criteria

The output guard must pass:

```text
step59_driver_run_dir_count == 3
step59_vtr_count == 0
step59_particle_npy_count == 0
step59_large_file_count == 0
step59_total_size_mb < 5
external_edit_count == 0
real_geometry_candidates_edit_count == 0
private_absolute_path_count == 0
```

Allowed generated smoke files:

```text
driver_config.json
geo_all_fluid_16.dat
diagnostics_timeseries.csv
diagnostics_timeseries.npz
small summary CSV/JSON
logs
```

Forbidden:

```text
.vtr
particle .npy
displaced_particle
dense_displacement
real geometry candidate files
external solver edits
large files
private absolute user paths inside committed Step59 artifacts
```

## 15. Required Step 58 Regression Guard

Step 59 must keep Step 58 green:

```text
Step 58 FSIDriver migration audit green
Step 58 import execution audit green
Step 58 legacy shim audit green
Step 58 optional bridge audit green
Step 58 behavior preservation audit green
Step 58 artifact manifest green
Step 57 regression guard green
```

The Step 59 geo-path naming fix is allowed as a narrow supersession of the Step 58 constructor output-path assumption. No other solver-behavior or implementation-owner regression is allowed.

## 16. Explicit Non-Goals

Step 59 must not implement or claim:

```text
48^3 simulation
64^3 simulation
longer cycle
runtime geometry activation
wall velocity application activation
geometry motion activation
prescribed boundary motion activation
real geometry
squid swimming
jet propulsion validation
grid convergence
production readiness
LBM tau formula migration
standard viscosity migration
historical artifact rerun
VTR output
particle NPY output
external/taichi_LBM3D edits
data/real_geometry_candidates edits
real squid validation
new FSI physics
```

## 17. Verification Commands

Run syntax compilation:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\drivers\fsi_driver.py `
  src\mpm_lbm\evidence\canonical_driver_smoke_runner.py `
  src\mpm_lbm\evidence\canonical_driver_smoke_audit.py `
  src\mpm_lbm\evidence\canonical_driver_output_guard.py `
  src\mpm_lbm\evidence\geo_path_naming_audit.py `
  baseline_tests\step59_common.py `
  baseline_tests\run_step59_canonical_driver_smoke_matrix.py `
  baseline_tests\run_step59_canonical_driver_smoke_quality.py `
  baseline_tests\run_step59_geo_path_naming_audit.py `
  baseline_tests\run_step59_output_guard.py `
  baseline_tests\run_step59_step58_regression_guard.py `
  baseline_tests\run_step59_artifact_manifest.py `
  tests\test_step59_canonical_driver_real_smoke_contract.py `
  tests\test_step59_geo_path_naming_contract.py `
  tests\test_step59_output_guard_contract.py `
  tests\test_step59_step58_regression_contract.py
```

Generate Step 59 artifacts:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step59_geo_path_naming_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step59_canonical_driver_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step59_canonical_driver_smoke_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step59_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step59_step58_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step59_artifact_manifest.py
```

Run focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step59_canonical_driver_real_smoke_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step59_geo_path_naming_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step59_output_guard_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step59_step58_regression_contract.py -q
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
git diff --check HEAD~1 HEAD
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## 18. Commit And Push

Commit message:

```text
test: add step59 canonical fsidriver real smoke simulation
```

Push target:

```text
origin/main
```

The work is complete only after the commit is pushed and the final response reports:

```text
final commit hash
remote branch
focused test counts
full Taichi pytest count
full Anaconda pytest count
ECC pre-push hook result
artifact manifest summary
```
