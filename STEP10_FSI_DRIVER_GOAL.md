# Step 10 Goal: Unified FSI Driver, Mode Matrix, and Production Scaffold

## Paste-Ready `/goal`

```text
/goal
In D:\working\squid robot\LBM\MPM-LBM, execute Step 10: Unified FSI driver, mode matrix, and production scaffold. The only authoritative execution contract is D:\working\squid robot\LBM\MPM-LBM\STEP10_FSI_DRIVER_GOAL.md.

Goal: wrap the existing Step 6/7 penalty-force two-way coupling path and the existing Step 8/9 moving-boundary two-way coupling path behind a common configurable FSIDriver3D. Add shared config, shared outputs, shared diagnostics timeseries, a mode matrix for none/penalty/moving_boundary, and lightweight performance profiling. This is engineering integration and regression scaffolding, not new FSI physics.

Hard boundaries: do not implement new FSI physics, do not change the Step 8 moving bounce-back formula, do not replace or delete PenaltyFSICoupler3D or MovingBoundaryFSICoupler3D, do not make moving_boundary the implicit default, do not implement two-phase flow, contact angle physics, squid geometry, sparse storage, ReducedSquidFSI, strict final momentum-conserving sharp-interface FSI, or edits to external/taichi_LBM3D. Required artifacts, execution order, baseline settings, pytest contract, Hard Acceptance Checklist, failure handling, and completion definition are all defined in STEP10_FSI_DRIVER_GOAL.md. Finish only after all Step 10 baselines pass, pytest passes, and code/logs/outputs/report are pushed to GitHub.
```

## 1. Current Baseline

Step 9 is accepted and is the starting point.

Current Step 9 final commit:

```text
94302b0363931e4e9f25e22eb0d4f596d5f5ef45
```

Step 9 validated:

```text
Penalty-force two-way coupling remains available through PenaltyFSICoupler3D.
Moving-boundary bounce-back remains opt-in through lbm.step_moving_bounceback().
Moving-boundary reaction is transferred to MPMSolid3D.grid_f_ext through MovingBoundaryFSICoupler3D.
Moving-boundary mode keeps lbm.cell_force at zero.
Penalty and moving-boundary comparison baselines both pass.
external/taichi_LBM3D is unchanged.
```

Step 9 means:

```text
The project has two independent MPM-LBM two-way coupling MVPs:
1. penalty-force two-way coupling
2. moving-boundary bounce-back two-way coupling
```

Step 9 still does not mean:

```text
strict final momentum-conserving sharp-interface FSI is complete
two-phase FSI exists
real squid geometry validation is complete
production-grade high-performance solver exists
```

## 2. Step 10 Objective

Step 10 turns the validated scripts from Steps 6-9 into a reusable engineering scaffold.

Implement a unified driver that can run:

```text
coupling_mode = "none"
coupling_mode = "penalty"
coupling_mode = "moving_boundary"
```

The driver must provide:

```text
1. a common configuration object
2. a common simulation initialization path
3. a common step_once() and run() loop
4. a common output directory layout
5. common diagnostics collection
6. diagnostics_timeseries.npz and diagnostics_timeseries.csv
7. standard driver baselines for penalty and moving_boundary
8. a three-mode matrix baseline
9. a lightweight performance profile baseline
10. a regression-test contract
```

This step is not about adding physics. It is about making the current physics paths reproducible, comparable, and easier to reuse.

## 3. Workspace And Environment

Work in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Known Python environment:

```powershell
& 'D:\working\taichi\env\python.exe' ...
```

Runtime baselines should use:

```python
ti.init(arch=ti.gpu, default_fp=ti.f32)
```

If a short diagnostic probe is needed, label it as a probe and then rerun the full required baseline. Do not report short probes as full acceptance.

## 4. Strict Non-Goals

Do not implement these in Step 10:

```text
1. No new FSI physics.
2. No new coupling model beyond none, penalty, moving_boundary.
3. No new moving bounce-back formula.
4. No replacement or deletion of PenaltyFSICoupler3D.
5. No replacement or deletion of MovingBoundaryFSICoupler3D.
6. No replacement of existing lbm.step() behavior.
7. No default switch from lbm.step() to lbm.step_moving_bounceback().
8. No two-phase LBM.
9. No contact angle physics.
10. No squid geometry or real squid case.
11. No sparse storage.
12. No ReducedSquidFSI.
13. No edits to external/taichi_LBM3D.
14. No claim that strict momentum-conserving sharp-interface FSI is complete.
15. No claim that real squid FSI is validated.
```

Allowed in Step 10:

```text
driver abstraction
mode selection
JSON config files
common benchmark baselines
common diagnostics aggregation
CSV and NPZ output
lightweight performance timing
mode comparison report
```

## 5. Required Final Structure

Create:

```text
src/
  fsi_config.py
  fsi_driver.py
  run_utils.py

configs/
  step10_penalty_default.json
  step10_moving_boundary_default.json
  step10_mode_matrix.json

baseline_tests/
  run_step10_driver_penalty_mode.py
  run_step10_driver_moving_boundary_mode.py
  run_step10_driver_mode_matrix.py
  run_step10_performance_profile.py

outputs/
  step10_driver_penalty/
  step10_driver_moving_boundary/
  step10_mode_matrix/
  step10_performance_profile/

logs/
  step10_driver_penalty.log
  step10_driver_moving_boundary.log
  step10_mode_matrix.log
  step10_performance_profile.log

tests/
  test_step10_fsi_driver_contract.py

STEP10_FSI_DRIVER_REPORT.md
```

Update:

```text
src/__init__.py
```

Export:

```python
FSIDriverConfig
FSIDriver3D
```

## 6. FSIDriverConfig Contract

Create:

```text
src/fsi_config.py
```

Required class:

```python
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class FSIDriverConfig:
    coupling_mode: str = "penalty"

    n_grid: int = 32
    n_particles: int = 4096
    n_lbm_steps: int = 20
    mpm_substeps_per_lbm_step: int = 10
    mpm_dt: float = 4.0e-4

    target_u_lbm: Tuple[float, float, float] = (0.02, 0.0, 0.0)
    gravity: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    box_min: Tuple[float, float, float] = (0.25, 0.35, 0.25)
    box_max: Tuple[float, float, float] = (0.55, 0.65, 0.55)

    dynamic_solid_threshold: float = 0.5

    beta_lbm: float = 1.0e-3
    penalty_force_cap_lbm: float = 1.0e-4

    mb_reaction_scale: float = 1.0
    mb_force_cap_norm: float = 1.0e-4

    output_interval: int = 10
    write_vtk: bool = True
    write_particles: bool = True
```

Validation requirements:

```text
coupling_mode must be one of: "none", "penalty", "moving_boundary"
n_grid > 0
n_particles > 0
n_lbm_steps > 0
mpm_substeps_per_lbm_step > 0
mpm_dt > 0
dynamic_solid_threshold >= 0
beta_lbm > 0
penalty_force_cap_lbm > 0
mb_reaction_scale > 0
mb_force_cap_norm > 0
output_interval > 0
```

Required helpers:

```text
from_json(path)
to_dict()
make_unified_sim_config()
```

Use Step 9's stable full-coupled moving-boundary setting as the default:

```text
mb_force_cap_norm = 1.0e-4
```

Do not use the stronger Step 9 isolated reaction value `1.0e-2` as the default for full driver runs.

## 7. FSIDriver3D Contract

Create:

```text
src/fsi_driver.py
```

Required class:

```python
class FSIDriver3D:
    def __init__(self, config: FSIDriverConfig, out_dir: str):
        ...

    def initialize(self):
        ...

    def step_once(self):
        ...

    def run(self):
        ...

    def collect_diagnostics(self, step: int):
        ...

    def export_outputs(self, step: int):
        ...

    def save_timeseries(self):
        ...
```

Responsibilities:

```text
1. Build UnifiedSimConfig from FSIDriverConfig.
2. Build GridUnitMapper.
3. Create all-fluid geometry for the driver case.
4. Create and initialize LBMFluid3D.
5. Create and initialize MPMSolid3D.
6. Set initial MPM velocity from target_u_lbm via GridUnitMapper.
7. Create MPMToLBMProjector3D.
8. Create PenaltyFSICoupler3D only for coupling_mode="penalty".
9. Create MovingBoundaryFSICoupler3D only for coupling_mode="moving_boundary".
10. Keep coupling_mode="none" free of penalty and moving-boundary reaction operations.
11. Track current_lbm_step and total_mpm_substeps.
12. Record common diagnostics into an internal list.
13. Save diagnostics to NPZ and CSV.
14. Export LBM VTK and particle arrays when configured.
```

## 8. Coupling Mode Loops

### 8.1 `coupling_mode = "none"`

Use this loop:

```python
projector.project(solid, lbm)
lbm.step()

for _ in range(substeps):
    solid.substep()
```

Do not call:

```text
PenaltyFSICoupler3D.build_penalty_force()
PenaltyFSICoupler3D.add_lbm_reaction_to_mpm_grid()
lbm.update_dynamic_solid()
lbm.reinitialize_new_fluid_cells()
lbm.step_moving_bounceback()
MovingBoundaryFSICoupler3D.add_moving_boundary_reaction_to_mpm_grid()
```

Expected diagnostics:

```text
cell_force_max_norm == 0
hydro_force_max_norm == 0
bb_link_count == 0
active_reaction_particle_count == 0
```

### 8.2 `coupling_mode = "penalty"`

Use the Step 6/7 loop:

```python
projector.project(solid, lbm)
penalty_coupler.clear_force_fields(lbm)
penalty_coupler.build_penalty_force(lbm)
lbm.step()

for _ in range(substeps):
    solid.clear_grid()
    solid.p2g()
    penalty_coupler.add_lbm_reaction_to_mpm_grid(solid, lbm)
    solid.grid_update()
    solid.g2p()
```

Do not call:

```text
lbm.update_dynamic_solid()
lbm.reinitialize_new_fluid_cells()
lbm.step_moving_bounceback()
MovingBoundaryFSICoupler3D.add_moving_boundary_reaction_to_mpm_grid()
```

Expected diagnostics:

```text
cell_force_max_norm > 0
hydro_force_max_norm > 0
bb_link_count == 0 or not used
```

### 8.3 `coupling_mode = "moving_boundary"`

Use the Step 9 loop:

```python
projector.project(solid, lbm)
lbm.update_dynamic_solid(dynamic_solid_threshold)
lbm.reinitialize_new_fluid_cells()
lbm.step_moving_bounceback()

for _ in range(substeps):
    solid.clear_grid()
    solid.p2g()
    mb_coupler.clear_reaction_diagnostics()
    mb_coupler.add_moving_boundary_reaction_to_mpm_grid(solid, lbm)
    solid.grid_update()
    solid.g2p()
```

Do not call:

```text
PenaltyFSICoupler3D.build_penalty_force()
PenaltyFSICoupler3D.add_lbm_reaction_to_mpm_grid()
lbm.set_uniform_cell_force()
lbm.set_spherical_cell_force()
```

Required per-step invariant:

```text
cell_force_max_norm == 0
```

Expected diagnostics:

```text
bb_link_count > 0
active_reaction_particle_count > 0
hydro_force_max_norm > 0
```

## 9. Common Diagnostics

`FSIDriver3D.collect_diagnostics(step)` must record one row per output interval and at final step.

Required columns:

```text
step
total_mpm_substeps
coupling_mode
rho_min
rho_max
lbm_max_v
fluid_mean_ux
projection_zone_fluid_mean_ux
far_field_fluid_mean_ux
solid_mean_vx_norm
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
elapsed_seconds
```

Required files:

```text
diagnostics_timeseries.npz
diagnostics_timeseries.csv
```

Diagnostics must distinguish unavailable metrics from zero metrics. Use zero for inactive mode counters only when the inactive path is intentionally unused.

## 10. run_utils.py Contract

Create:

```text
src/run_utils.py
```

Required helpers:

```text
make_all_fluid_geo(path, n_grid)
save_json_config(config, path)
save_csv_rows(rows, path, fieldnames=None)
assert_no_nan_inf_array(name, arr)
ensure_output_dir(path)
```

Do not make these helpers hide solver behavior. They are only for file IO, finite checks, and repeated baseline boilerplate.

## 11. Config Files

Create:

```text
configs/step10_penalty_default.json
configs/step10_moving_boundary_default.json
configs/step10_mode_matrix.json
```

### `configs/step10_penalty_default.json`

```json
{
  "coupling_mode": "penalty",
  "n_grid": 32,
  "n_particles": 4096,
  "n_lbm_steps": 20,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.02, 0.0, 0.0],
  "gravity": [0.0, 0.0, 0.0],
  "beta_lbm": 0.001,
  "penalty_force_cap_lbm": 0.0001
}
```

### `configs/step10_moving_boundary_default.json`

```json
{
  "coupling_mode": "moving_boundary",
  "n_grid": 32,
  "n_particles": 4096,
  "n_lbm_steps": 20,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.02, 0.0, 0.0],
  "gravity": [0.0, 0.0, 0.0],
  "dynamic_solid_threshold": 0.5,
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.0001
}
```

### `configs/step10_mode_matrix.json`

```json
{
  "modes": ["none", "penalty", "moving_boundary"],
  "n_grid": 32,
  "n_particles": 4096,
  "n_lbm_steps": 20,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.02, 0.0, 0.0]
}
```

## 12. Baseline 1: Driver Penalty Mode

Create:

```text
baseline_tests/run_step10_driver_penalty_mode.py
```

Purpose:

```text
Verify the unified driver reproduces the stable Step 6/7 penalty response.
```

Recommended settings:

```text
coupling_mode = "penalty"
n_grid = 32
n_particles = 4096
n_lbm_steps = 20
mpm_substeps_per_lbm_step = 10
target_u_lbm = (0.02, 0, 0)
beta_lbm = 1e-3
penalty_force_cap_lbm = 1e-4
```

Acceptance:

```text
completed_lbm_steps = 20
total_mpm_substeps = 200
fluid_mean_ux_final > 0
projection_zone_fluid_mean_ux_final > 0
solid_mean_vx_final < solid_mean_vx_initial
cell_force_max_norm > 0
hydro_force_max_norm > 0
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
no NaN
no Inf
```

Required outputs:

```text
outputs/step10_driver_penalty/LBMFluid_20.vtr
outputs/step10_driver_penalty/particles_x.npy
outputs/step10_driver_penalty/particles_v.npy
outputs/step10_driver_penalty/particles_F.npy
outputs/step10_driver_penalty/particles_J.npy
outputs/step10_driver_penalty/diagnostics_timeseries.npz
outputs/step10_driver_penalty/diagnostics_timeseries.csv
```

Required log:

```text
logs/step10_driver_penalty.log
```

Required log marker:

```text
[OK] Step 10 driver penalty mode finished
```

## 13. Baseline 2: Driver Moving-Boundary Mode

Create:

```text
baseline_tests/run_step10_driver_moving_boundary_mode.py
```

Purpose:

```text
Verify the unified driver reproduces the stable Step 9 moving-boundary response.
```

Recommended settings:

```text
coupling_mode = "moving_boundary"
n_grid = 32
n_particles = 4096
n_lbm_steps = 20
mpm_substeps_per_lbm_step = 10
target_u_lbm = (0.02, 0, 0)
dynamic_solid_threshold = 0.5
mb_reaction_scale = 1.0
mb_force_cap_norm = 1e-4
```

Acceptance:

```text
completed_lbm_steps = 20
total_mpm_substeps = 200
bb_link_count > 0
active_reaction_particle_count > 0
projection_zone_fluid_mean_ux_final > 0
solid_mean_vx_final < solid_mean_vx_initial
cell_force_max_norm == 0
hydro_force_max_norm > 0
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
no NaN
no Inf
```

Required outputs:

```text
outputs/step10_driver_moving_boundary/LBMFluid_20.vtr
outputs/step10_driver_moving_boundary/particles_x.npy
outputs/step10_driver_moving_boundary/particles_v.npy
outputs/step10_driver_moving_boundary/particles_F.npy
outputs/step10_driver_moving_boundary/particles_J.npy
outputs/step10_driver_moving_boundary/diagnostics_timeseries.npz
outputs/step10_driver_moving_boundary/diagnostics_timeseries.csv
```

Required log:

```text
logs/step10_driver_moving_boundary.log
```

Required log marker:

```text
[OK] Step 10 driver moving-boundary mode finished
```

## 14. Baseline 3: Driver Mode Matrix

Create:

```text
baseline_tests/run_step10_driver_mode_matrix.py
```

Purpose:

```text
Run none, penalty, and moving_boundary modes through the same FSIDriver3D and generate a comparison table.
```

Modes:

```text
none
penalty
moving_boundary
```

Recommended settings for each mode:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 20
mpm_substeps_per_lbm_step = 10
target_u_lbm = (0.02, 0, 0)
```

Required output:

```text
outputs/step10_mode_matrix/mode_matrix_results.csv
outputs/step10_mode_matrix/mode_matrix_results.npz
```

Required columns:

```text
mode
stable
fluid_mean_ux_final
projection_zone_ux_final
solid_mean_vx_initial
solid_mean_vx_final
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
cell_force_max_norm
hydro_force_max_norm
bb_link_count
active_reaction_particle_count
```

Acceptance:

```text
none mode stable
penalty mode stable
moving_boundary mode stable
penalty mode has cell_force_max_norm > 0
moving_boundary mode has cell_force_max_norm == 0
moving_boundary mode has bb_link_count > 0
moving_boundary mode has active_reaction_particle_count > 0
rho_min > 0.95 for all modes
rho_max < 1.05 for all modes
lbm_max_v < 0.1 for all modes
mpm_min_J > 0 for all modes
mpm_max_speed < 10 for all modes
no NaN
no Inf
```

Qualitative trend check:

```text
projection_zone_ux_final(moving_boundary) > projection_zone_ux_final(penalty) > projection_zone_ux_final(none)
```

Use a small tolerance if needed, but do not hide a reversed trend.

Required log:

```text
logs/step10_mode_matrix.log
```

Required log marker:

```text
[OK] Step 10 driver mode matrix finished
```

## 15. Baseline 4: Performance Profile

Create:

```text
baseline_tests/run_step10_performance_profile.py
```

Purpose:

```text
Record a lightweight engineering performance baseline for the unified driver. Do not optimize in Step 10.
```

Recommended settings:

```text
modes = ["none", "penalty", "moving_boundary"]
n_grid = 32
n_particles = 4096
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
target_u_lbm = (0.02, 0, 0)
```

Use:

```python
time.perf_counter()
```

Do not introduce heavyweight profilers.

Required timing fields:

```text
mode
init_time
projection_time
coupling_time
lbm_step_time
mpm_substep_time
diagnostics_time
export_time
total_time
```

Required output:

```text
outputs/step10_performance_profile/performance_results.csv
outputs/step10_performance_profile/performance_results.npz
```

Acceptance:

```text
all modes finish
timing values finite
total_time > 0 for each mode
performance CSV exists
performance NPZ exists
no NaN
no Inf
```

Required log:

```text
logs/step10_performance_profile.log
```

Required log marker:

```text
[OK] Step 10 performance profile finished
```

## 16. Required Report

Create:

```text
STEP10_FSI_DRIVER_REPORT.md
```

Report must include:

```text
1. Goal
2. Files created/updated
3. Driver modes
4. Config schema and defaults
5. Common diagnostics fields
6. Penalty driver baseline command/result
7. Moving-boundary driver baseline command/result
8. Mode matrix command/result
9. Performance profile command/result
10. Explicit non-goals
11. Hard Acceptance Checklist
12. Decision: can proceed to Step 11 or not
```

Report must explicitly state:

```text
Step 10 adds a unified engineering driver.
Step 10 does not add new FSI physics.
Step 10 does not replace PenaltyFSICoupler3D.
Step 10 does not replace MovingBoundaryFSICoupler3D.
Step 10 does not change the Step 8 moving bounce-back formula.
Step 10 does not make moving_boundary the default solver path.
Step 10 does not edit external/taichi_LBM3D.
```

Recommended report template:

````markdown
# Step 10 Unified FSI Driver Report

## 1. Goal

Build a unified FSI driver that can run none, penalty, and moving_boundary modes with common config, diagnostics, and output handling.

## 2. Files

Created / updated:

- src/fsi_config.py
- src/fsi_driver.py
- src/run_utils.py
- src/__init__.py
- configs/step10_penalty_default.json
- configs/step10_moving_boundary_default.json
- configs/step10_mode_matrix.json
- baseline_tests/run_step10_driver_penalty_mode.py
- baseline_tests/run_step10_driver_moving_boundary_mode.py
- baseline_tests/run_step10_driver_mode_matrix.py
- baseline_tests/run_step10_performance_profile.py
- tests/test_step10_fsi_driver_contract.py

## 3. Driver modes

| mode | LBM path | MPM reaction | cell_force | dynamic solid |
| ---- | -------- | ------------ | ---------- | ------------- |
| none | lbm.step() | none | zero | no |
| penalty | lbm.step() | PenaltyFSICoupler3D | nonzero | no |
| moving_boundary | lbm.step_moving_bounceback() | MovingBoundaryFSICoupler3D | zero | yes |

## 4. Penalty driver baseline

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_penalty_mode.py
```

Result:

- completed_lbm_steps:
- total_mpm_substeps:
- final_fluid_mean_ux:
- final_solid_mean_vx_norm:
- cell_force_max_norm:
- hydro_force_max_norm:
- rho_min:
- rho_max:

## 5. Moving-boundary driver baseline

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_moving_boundary_mode.py
```

Result:

- completed_lbm_steps:
- total_mpm_substeps:
- final_projection_zone_ux:
- final_solid_mean_vx_norm:
- bb_link_count:
- active_reaction_particle_count:
- cell_force_max_norm:
- rho_min:
- rho_max:

## 6. Mode matrix

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_mode_matrix.py
```

Result:

| mode | stable | projection_zone_ux_final | solid_vx_final | rho_min | rho_max |
| ---- | ------ | -----------------------: | -------------: | ------: | ------: |

## 7. Performance profile

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_performance_profile.py
```

Result:

| mode | total_time | projection_time | coupling_time | lbm_time | mpm_time |
| ---- | ---------: | --------------: | ------------: | -------: | -------: |

## 8. Explicit non-goals

Step 10 does not implement new FSI physics, two-phase flow, contact angle physics, squid geometry, sparse storage, ReducedSquidFSI, or external/taichi_LBM3D edits.

## 9. Acceptance checklist

- [ ] main is on the Step 10 final commit
- [ ] FSIDriverConfig exists
- [ ] FSIDriver3D exists
- [ ] run_utils helpers exist
- [ ] mode none runs
- [ ] mode penalty runs
- [ ] mode moving_boundary runs
- [ ] common diagnostics_timeseries.npz is saved
- [ ] common diagnostics_timeseries.csv is saved
- [ ] mode_matrix_results.csv exists
- [ ] performance_results.csv exists
- [ ] no new FSI physics
- [ ] no external/taichi_LBM3D edits
- [ ] pytest -q passes

## 10. Decision

Can proceed to Step 11?

- [ ] Yes
- [ ] No
````

## 17. Pytest Contract

Create:

```text
tests/test_step10_fsi_driver_contract.py
```

Recommended tests:

```text
test_step10_required_artifacts_exist
test_step10_source_contains_required_interfaces
test_step10_config_files_are_valid_json
test_step10_scripts_respect_mode_boundaries
test_step10_logs_record_successful_baselines
test_step10_report_acceptance_complete
```

Required artifact paths:

```text
src/fsi_config.py
src/fsi_driver.py
src/run_utils.py
configs/step10_penalty_default.json
configs/step10_moving_boundary_default.json
configs/step10_mode_matrix.json
baseline_tests/run_step10_driver_penalty_mode.py
baseline_tests/run_step10_driver_moving_boundary_mode.py
baseline_tests/run_step10_driver_mode_matrix.py
baseline_tests/run_step10_performance_profile.py
logs/step10_driver_penalty.log
logs/step10_driver_moving_boundary.log
logs/step10_mode_matrix.log
logs/step10_performance_profile.log
outputs/step10_driver_penalty/LBMFluid_20.vtr
outputs/step10_driver_penalty/particles_x.npy
outputs/step10_driver_penalty/particles_v.npy
outputs/step10_driver_penalty/particles_F.npy
outputs/step10_driver_penalty/particles_J.npy
outputs/step10_driver_penalty/diagnostics_timeseries.npz
outputs/step10_driver_penalty/diagnostics_timeseries.csv
outputs/step10_driver_moving_boundary/LBMFluid_20.vtr
outputs/step10_driver_moving_boundary/particles_x.npy
outputs/step10_driver_moving_boundary/particles_v.npy
outputs/step10_driver_moving_boundary/particles_F.npy
outputs/step10_driver_moving_boundary/particles_J.npy
outputs/step10_driver_moving_boundary/diagnostics_timeseries.npz
outputs/step10_driver_moving_boundary/diagnostics_timeseries.csv
outputs/step10_mode_matrix/mode_matrix_results.csv
outputs/step10_mode_matrix/mode_matrix_results.npz
outputs/step10_performance_profile/performance_results.csv
outputs/step10_performance_profile/performance_results.npz
STEP10_FSI_DRIVER_REPORT.md
```

Required source keywords:

```text
class FSIDriverConfig
class FSIDriver3D
coupling_mode
step_once
run
collect_diagnostics
export_outputs
save_timeseries
PenaltyFSICoupler3D
MovingBoundaryFSICoupler3D
MPMToLBMProjector3D
FSIDiagnostics3D
diagnostics_timeseries
```

Required log markers:

```text
[OK] Step 10 driver penalty mode finished
[OK] Step 10 driver moving-boundary mode finished
[OK] Step 10 driver mode matrix finished
[OK] Step 10 performance profile finished
```

Required log tokens:

```text
coupling_mode
completed_lbm_steps
total_mpm_substeps
cell_force_max_norm
hydro_force_max_norm
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
```

Forbidden tokens in Step 10 source and baselines:

```text
two_phase
contact_angle
ReducedSquidFSI
```

Do not forbid:

```text
PenaltyFSICoupler3D
MovingBoundaryFSICoupler3D
```

Reason: the unified driver must use both existing coupling implementations.

Mode-boundary test requirement:

```text
The none mode path must not call PenaltyFSICoupler3D or MovingBoundaryFSICoupler3D operations.
The penalty mode path must not call step_moving_bounceback().
The moving_boundary mode path must not call PenaltyFSICoupler3D build/add reaction methods.
```

## 18. Hard Acceptance Checklist

All must pass:

```text
[ ] main is on the Step 10 final commit
[ ] src/fsi_config.py exists
[ ] src/fsi_driver.py exists
[ ] src/run_utils.py exists
[ ] src/__init__.py exports FSIDriverConfig
[ ] src/__init__.py exports FSIDriver3D
[ ] configs/step10_penalty_default.json exists
[ ] configs/step10_moving_boundary_default.json exists
[ ] configs/step10_mode_matrix.json exists
[ ] FSIDriverConfig validates coupling_mode
[ ] FSIDriver3D supports coupling_mode="none"
[ ] FSIDriver3D supports coupling_mode="penalty"
[ ] FSIDriver3D supports coupling_mode="moving_boundary"
[ ] penalty driver baseline completes 20 LBM steps
[ ] penalty driver baseline completes 200 MPM substeps
[ ] penalty driver baseline has cell_force_max_norm > 0
[ ] moving-boundary driver baseline completes 20 LBM steps
[ ] moving-boundary driver baseline completes 200 MPM substeps
[ ] moving-boundary driver baseline has bb_link_count > 0
[ ] moving-boundary driver baseline has active_reaction_particle_count > 0
[ ] moving-boundary driver baseline keeps cell_force_max_norm == 0
[ ] mode matrix baseline completes
[ ] mode matrix includes none, penalty, moving_boundary
[ ] performance profile baseline completes
[ ] common diagnostics_timeseries.npz is saved
[ ] common diagnostics_timeseries.csv is saved
[ ] mode_matrix_results.csv is saved
[ ] mode_matrix_results.npz is saved
[ ] performance_results.csv is saved
[ ] performance_results.npz is saved
[ ] no NaN
[ ] no Inf
[ ] rho_min > 0.95
[ ] rho_max < 1.05
[ ] lbm_max_v < 0.1
[ ] mpm_min_J > 0
[ ] mpm_max_speed < 10
[ ] no new FSI physics
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] logs are saved under logs/
[ ] outputs are saved under outputs/
[ ] STEP10_FSI_DRIVER_REPORT.md is complete
[ ] pytest -q passes
```

## 19. Recommended Execution Order

Follow this order:

```text
1. Add Step 10 pytest contract/artifact checks.
2. Run pytest and confirm RED for missing Step 10 artifacts.
3. Create src/fsi_config.py.
4. Create src/run_utils.py.
5. Create src/fsi_driver.py.
6. Implement FSIDriverConfig validation and JSON loading.
7. Implement FSIDriver3D initialization.
8. Implement coupling_mode="none".
9. Implement coupling_mode="penalty".
10. Implement coupling_mode="moving_boundary".
11. Implement common diagnostics collection.
12. Implement common output export.
13. Export FSIDriverConfig and FSIDriver3D from src/__init__.py.
14. Add configs/*.json.
15. Add and run penalty driver baseline.
16. Add and run moving-boundary driver baseline.
17. Add and run mode matrix baseline.
18. Add and run performance profile baseline.
19. Write STEP10_FSI_DRIVER_REPORT.md.
20. Run final pytest -q.
21. Inspect git diff and git status.
22. Confirm external/taichi_LBM3D is unchanged.
23. Commit and push code, logs, outputs, tests, configs, and report to GitHub.
```

Suggested commits:

```text
test: add step 10 fsi driver contract
feat: add unified fsi driver
feat: add step 10 driver baselines
docs: add step 10 fsi driver report
```

It is acceptable to squash into one final implementation commit if that keeps review simpler.

## 20. Failure Handling

If any required baseline fails, stop and record:

```text
exact command
log path
first failing error
which acceptance item failed
whether failure is compile/import/runtime/numerical/output
next minimal fix
```

Do not weaken required baselines and call Step 10 complete.

If moving-boundary mode becomes unstable:

```text
1. Do not change the Step 8 moving bounce-back formula.
2. Do not switch moving-boundary mode to penalty force.
3. First verify mb_force_cap_norm is 1.0e-4.
4. If still unstable, reduce mb_reaction_scale or mb_force_cap_norm.
5. Keep the full 20-step and 200-substep baseline.
6. Document the stable window in STEP10_FSI_DRIVER_REPORT.md.
```

If mode matrix trend fails:

```text
1. Do not fake the trend in the report.
2. Check whether diagnostics are measuring projection-zone velocity consistently.
3. Check whether none mode is correctly free-running.
4. Check whether penalty and moving_boundary modes are using their expected couplers.
5. Use a small tolerance only for numerical noise, not for reversed behavior.
```

If performance timings are noisy:

```text
1. Keep the profile lightweight.
2. Do not optimize in Step 10.
3. Report timing as an engineering baseline.
```

## 21. Completion Definition

Step 10 is complete only when:

```text
1. FSIDriverConfig exists and validates configs.
2. FSIDriver3D exists and is exported.
3. FSIDriver3D runs none, penalty, and moving_boundary modes.
4. Penalty mode keeps using PenaltyFSICoupler3D.
5. Moving-boundary mode keeps using MovingBoundaryFSICoupler3D.
6. Moving-boundary mode keeps lbm.cell_force at zero.
7. Common diagnostics NPZ and CSV are saved.
8. Driver penalty baseline passes.
9. Driver moving-boundary baseline passes.
10. Mode matrix baseline passes.
11. Performance profile baseline passes.
12. No forbidden physics or external edits are introduced.
13. Logs, outputs, configs, and STEP10_FSI_DRIVER_REPORT.md record evidence.
14. pytest -q passes.
15. The completed code, configs, report, logs, and outputs are pushed to GitHub.
```

Completion means:

```text
The project has a unified configurable MPM-LBM FSI prototype framework that can run and compare none, penalty, and moving-boundary coupling modes.
```

Completion does not mean:

```text
strict final momentum-conserving sharp-interface FSI is complete
real squid validation is complete
two-phase FSI exists
production-grade high-performance solver is complete
```

Those belong to later steps.
