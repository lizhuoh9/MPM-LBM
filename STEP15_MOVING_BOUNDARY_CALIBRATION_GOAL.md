# Step 15 Goal: Moving-Boundary Reaction Calibration and Momentum Accounting

## Paste-Ready `/goal`

```text
/goal
In D:\working\squid robot\LBM\MPM-LBM, execute Step 15: Moving-boundary reaction calibration and momentum accounting. The only authoritative execution contract is D:\working\squid robot\LBM\MPM-LBM\STEP15_MOVING_BOUNDARY_CALIBRATION_GOAL.md.

Goal: without changing FSI physics or Step 8/9/10/14 validated behavior, add diagnostic-only momentum accounting and calibration baselines for the existing moving_boundary reaction path. Track link-wise moving-boundary impulse, hydro_force sums, sampled particle/grid reaction transfer, and solid particle momentum. Run reaction_scale and force_cap sweeps, identify conservative recommended moving_boundary configs for 48^3 box and 48^3 squid_proxy, compare calibrated and original Step 14 settings, write docs/report/logs/outputs, and add a pytest contract.

Hard boundaries: do not implement new FSI physics, do not change the Step 8 moving bounce-back formula, do not change PenaltyFSICoupler3D, do not change MovingBoundaryFSICoupler3D reaction formulas, do not make moving_boundary the default, do not delete the Step 9 engineering-scale reaction path, do not implement two-phase flow, contact angle physics, real squid validation, squid actuation, swimming locomotion, mesh import, mesh collision/contact, sparse storage, ReducedSquidFSI, strict final momentum-conserving sharp-interface FSI, production benchmark claims, or edits to external/taichi_LBM3D. Required artifacts, execution order, accounting quantities, calibration sweep settings, pytest contract, Hard Acceptance Checklist, failure handling, and completion definition are all defined in STEP15_MOVING_BOUNDARY_CALIBRATION_GOAL.md. Finish only after all Step 15 baselines pass, pytest passes, external/taichi_LBM3D remains unchanged, and code/docs/logs/outputs/report are pushed to GitHub.
```

## 1. Current Baseline

Step 14 is accepted and is the starting point.

Current Step 14 final commit:

```text
fca824ae14b80e98d9df9fada265161eeae600aa
```

Step 14 validated:

```text
48^3 box none / penalty / moving_boundary baselines pass.
48^3 squid_proxy none / penalty / moving_boundary baselines pass.
64^3 none / penalty feasibility baselines pass.
scaling_summary.csv and scaling_summary.json exist.
artifact manifest reports controlled output size and large_file_count = 0.
tests/test_step14_larger_grid_contract.py exists and passes.
logs/step14_pytest.log reports 82 passed.
external/taichi_LBM3D remains unchanged.
No solver physics was changed by Step 14.
```

Important Step 14 observation:

```text
48^3 box moving_boundary at target_u_lbm = [0.01, 0.0, 0.0] exceeded density bounds.
The accepted Step 14 config used target_u_lbm = [0.005, 0.0, 0.0] and mb_force_cap_norm = 0.000025.
This was a configuration-level stabilization, not a solver formula change.
```

Step 14 means the repository currently has:

```text
1. a geometry-aware MPM-LBM FSI engineering prototype
2. penalty and moving_boundary two-way coupling paths
3. 32^3 regression baselines
4. 48^3 box and squid_proxy moving_boundary scale baselines
5. 64^3 none / penalty feasibility evidence
6. artifact and performance governance
```

Step 14 still does not mean:

```text
production-grade large-scale solver
strict final momentum-conserving sharp-interface FSI
real squid validation
validated squid swimming
complete 64^3 moving_boundary validation
two-phase LBM
contact angle physics
sparse storage
```

## 2. Step 15 Objective

Step 15 calibrates the existing moving_boundary reaction transfer path and adds sharper momentum accounting diagnostics.

Implement diagnostic and calibration infrastructure that provides:

```text
1. diagnostic-only momentum accounting for moving_boundary runs
2. per-step records for link-wise impulse, hydro_force, sampled reaction, MPM grid reaction, and solid momentum
3. reaction_scale sweep at 32^3 box
4. force_cap_norm sweep at 48^3 box
5. calibrated 48^3 squid_proxy window
6. calibrated-vs-original comparison
7. recommended moving_boundary configs for box 48^3 and squid_proxy 48^3
8. docs, report, logs, outputs, and pytest contract
```

Step 15 is not a new FSI method. It is:

```text
calibration
momentum accounting
diagnostics
recommended parameter window selection
```

Allowed language:

```text
moving-boundary calibration
momentum accounting diagnostics
engineering coupling scale
recommended stable window
reaction_scale sweep
force_cap_norm sweep
```

Forbidden overclaims:

```text
strict final momentum-conserving FSI is complete
production-grade sharp-interface FSI
real squid validation
validated squid swimming
biomechanically accurate squid
```

## 3. Workspace And Environment

Work in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Known Python environment:

```powershell
& 'D:\working\taichi\env\python.exe' ...
```

Primary verification command:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

If Taichi GPU initialization fails during a required baseline, record the exact error. Do not silently downgrade a required final acceptance run unless the report explicitly marks that run as failed and the contract is revised.

## 4. Strict Non-Goals

Do not implement these in Step 15:

```text
1. No new FSI physics.
2. No new coupling mode.
3. No changes to lbm.step() default behavior.
4. No changes to lbm.step_moving_bounceback() formula.
5. No changes to the Step 8 moving bounce-back correction formula.
6. No changes to the Step 9 moving-boundary reaction-transfer formula.
7. No changes to PenaltyFSICoupler3D formulas.
8. No replacement or deletion of PenaltyFSICoupler3D.
9. No replacement or deletion of MovingBoundaryFSICoupler3D.
10. No making moving_boundary the default driver path.
11. No deleting or hiding the Step 9 engineering-scale reaction path.
12. No two-phase flow.
13. No contact angle physics.
14. No real squid validation.
15. No squid actuation or muscle model.
16. No swimming locomotion model.
17. No mesh import.
18. No mesh collision/contact.
19. No sparse storage implementation.
20. No ReducedSquidFSI.
21. No edits to external/taichi_LBM3D.
22. No production benchmark or production-readiness claim.
23. No deletion or weakening of Step 10/12/13/14 regression artifacts.
```

Allowed in Step 15:

```text
diagnostic-only accounting helpers
NumPy reductions over existing fields
calibration classification helpers
calibration sweep scripts
recommended config presets
CSV/NPZ/JSON/log outputs
docs, tests, report
```

Any solver-adjacent edits must be limited to diagnostics, orchestration, configuration, and reporting. Do not alter collision, streaming, forcing, bounce-back, constitutive model, P2G/G2P, projection math, coupling formulas, or reaction-transfer formulas.

## 5. Required Final Structure

Create:

```text
src/
  momentum_accounting.py
  calibration.py

configs/
  step15_mb_calibration_box_32.json
  step15_mb_force_cap_box_48.json
  step15_mb_calibration_squid_proxy_48.json
  step15_mb_recommended_box_48.json
  step15_mb_recommended_squid_proxy_48.json

baseline_tests/
  run_step15_momentum_accounting_sanity.py
  run_step15_reaction_scale_sweep_box_32.py
  run_step15_force_cap_sweep_box_48.py
  run_step15_squid_proxy_calibrated_window.py
  run_step15_calibrated_vs_original_comparison.py

outputs/
  step15_momentum_accounting/
  step15_reaction_scale_sweep_box_32/
  step15_force_cap_sweep_box_48/
  step15_squid_proxy_calibrated_window/
  step15_calibrated_vs_original/
  step15_artifact_manifest/

logs/
  step15_momentum_accounting.log
  step15_reaction_scale_sweep_box_32.log
  step15_force_cap_sweep_box_48.log
  step15_squid_proxy_calibrated_window.log
  step15_calibrated_vs_original.log
  step15_artifact_manifest.log
  step15_pytest.log

docs/
  14_moving_boundary_calibration.md

tests/
  test_step15_moving_boundary_calibration_contract.py

STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md
```

Update:

```text
src/__init__.py
README.md
docs/08_roadmap.md
docs/09_api_reference.md
docs/10_performance_memory.md
docs/13_larger_grid_validation.md
```

Do not delete Step 1-14 reports, logs, outputs, configs, docs, or tests.

## 6. Momentum Accounting Concept

Step 8/9/14 moving_boundary mode currently exposes several related but distinct quantities:

```text
A. LBM link-wise impulse diagnostics
   bb_net_fluid_impulse
   bb_net_solid_force

B. LBM grid diagnostic field
   lbm.hydro_force

C. MovingBoundaryFSICoupler3D sampled particle reaction
   net_particle_reaction_force

D. MPM grid reaction force
   net_grid_reaction_force

E. MPM solid particle momentum
   sum(mass[p] * v[p])
```

Step 15 must record these quantities in a per-LBM-step accounting table.

Required accounting row fields:

```text
step
bb_link_count
bb_net_fluid_impulse_x
bb_net_solid_force_x
hydro_force_sum_x
cell_force_sum_x
net_particle_reaction_force_x
net_grid_reaction_force_x
solid_momentum_x
solid_momentum_delta_x
fluid_mean_ux
projection_zone_ux
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
cell_force_max_norm
hydro_force_max_norm
hydro_field_vs_bb_error_x
grid_vs_particle_reaction_error_x
solid_momentum_response_ratio_x
force_sign_consistent
```

Suggested accounting metrics:

```text
hydro_field_vs_bb_error_x =
  abs(hydro_force_sum_x - bb_net_solid_force_x)

grid_vs_particle_reaction_error_x =
  abs(net_grid_reaction_force_x - net_particle_reaction_force_x)

solid_momentum_response_ratio_x =
  abs(solid_momentum_delta_x) / (abs(cumulative_grid_reaction_impulse_x) + eps)

force_sign_consistent =
  sign(net_grid_reaction_force_x) == -sign(target_u_lbm_x)
```

Because the current moving-boundary reaction path remains an engineering coupling scale, Step 15 must not require strict ratio = 1. The goal is to record, compare, classify, and choose conservative stable windows.

## 7. `src/momentum_accounting.py` Contract

Create:

```text
src/momentum_accounting.py
```

Required public class:

```python
class MomentumAccounting3D:
    """
    Diagnostic-only accounting helpers for moving-boundary FSI.
    Does not modify solver state.
    """
```

Required static methods:

```python
@staticmethod
def hydro_force_sum(lbm) -> np.ndarray:
    ...

@staticmethod
def cell_force_sum(lbm) -> np.ndarray:
    ...

@staticmethod
def solid_particle_momentum(solid) -> np.ndarray:
    ...

@staticmethod
def moving_boundary_accounting_row(
    step: int,
    lbm,
    solid,
    mb_coupler,
    previous_solid_momentum=None,
    cumulative_grid_reaction_impulse=None,
    target_u_lbm_x: float = 0.0,
) -> dict:
    ...
```

Behavior:

```text
hydro_force_sum reads lbm.hydro_force and returns a shape (3,) float64 NumPy array.
cell_force_sum reads lbm.cell_force and returns a shape (3,) float64 NumPy array.
solid_particle_momentum reads solid.mass and solid.v and returns sum(mass * v).
moving_boundary_accounting_row returns finite scalar fields suitable for CSV output.
```

Rules:

```text
Diagnostic-only.
Must not write Taichi fields.
Must not change solver state.
Must not initialize Taichi.
Must not call lbm.step().
Must not call solid.substep(), p2g, grid_update, or g2p.
Must use NumPy reductions after data is copied out.
Must be usable from pytest without running a full simulation when synthetic arrays/mocks are provided.
```

Required consistency fields:

```text
hydro_field_vs_bb_error_x
grid_vs_particle_reaction_error_x
solid_momentum_response_ratio_x
force_sign_consistent
```

If a field is unavailable from a current stats API, add read-only diagnostic accessors to the existing class only if necessary. Do not change the underlying physics or update order.

## 8. `src/calibration.py` Contract

Create:

```text
src/calibration.py
```

Required public functions:

```python
def classify_calibration_row(row: dict) -> dict:
    ...

def choose_recommended_row(rows: list[dict]) -> dict:
    ...

def write_calibration_summary(rows, csv_path: str, json_path: str) -> dict:
    ...
```

Required row classification:

```text
stable:
  rho_min > 0.95
  rho_max < 1.05
  lbm_max_v < 0.1
  mpm_min_J > 0
  mpm_max_speed < 10
  no NaN
  no Inf

well_behaved:
  stable
  rho_min > 0.98
  rho_max < 1.02
  mpm_min_J > 0.90
  mpm_max_speed < 1.0
  no sign reversal
  final_solid_vx_norm > 0

over_damped:
  stable
  sign_reversed is True or final_solid_vx_norm < 0

recommended:
  well_behaved row chosen by choose_recommended_row
```

Required helper outputs:

```text
stable
well_behaved
over_damped
sign_reversed
reason
score
```

Selection policy:

```text
Prefer well_behaved rows.
Prefer lower rho span.
Prefer no sign reversal.
Prefer positive solid slowdown without over-damping.
Prefer conservative force cap when scores are close.
Do not choose unstable rows.
```

If no well_behaved row exists, choose the most stable row only if it satisfies the hard stability criteria, mark it as conservative fallback, and explain this in the report. Do not claim it is physically calibrated.

## 9. Config Contracts

Create:

```text
configs/step15_mb_calibration_box_32.json
configs/step15_mb_force_cap_box_48.json
configs/step15_mb_calibration_squid_proxy_48.json
configs/step15_mb_recommended_box_48.json
configs/step15_mb_recommended_squid_proxy_48.json
```

### `configs/step15_mb_calibration_box_32.json`

Required intent:

```text
32^3 reaction_scale sweep base config.
```

Required values:

```json
{
  "coupling_mode": "moving_boundary",
  "geometry_type": "box",
  "n_grid": 32,
  "n_particles": 4096,
  "n_lbm_steps": 20,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.01, 0.0, 0.0],
  "dynamic_solid_threshold": 0.5,
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.0001,
  "write_vtk": false,
  "write_particles": false
}
```

### `configs/step15_mb_force_cap_box_48.json`

Required intent:

```text
48^3 force_cap_norm sweep base config.
```

Required values:

```json
{
  "coupling_mode": "moving_boundary",
  "geometry_type": "box",
  "n_grid": 48,
  "n_particles": 13824,
  "n_lbm_steps": 10,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "dynamic_solid_threshold": 0.5,
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.000025,
  "write_vtk": false,
  "write_particles": false
}
```

### `configs/step15_mb_calibration_squid_proxy_48.json`

Required intent:

```text
48^3 squid_proxy calibrated window base config.
```

Required values:

```json
{
  "coupling_mode": "moving_boundary",
  "geometry_type": "squid_proxy",
  "geometry_config_path": "configs/step13_squid_proxy_geometry.json",
  "n_grid": 48,
  "n_particles": 4096,
  "n_lbm_steps": 10,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "dynamic_solid_threshold": 0.5,
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.000025,
  "write_vtk": false,
  "write_particles": false
}
```

### Recommended configs

Create:

```text
configs/step15_mb_recommended_box_48.json
configs/step15_mb_recommended_squid_proxy_48.json
```

Start from Step 14 known-good values:

```text
target_u_lbm = [0.005, 0.0, 0.0]
mb_reaction_scale = 1.0
mb_force_cap_norm = 0.000025
write_vtk = false
write_particles = false
```

After sweeps, update these configs only if the evidence supports a better stable and well_behaved row. The report must explain the selected values.

## 10. Baseline 1: Momentum Accounting Sanity

Create:

```text
baseline_tests/run_step15_momentum_accounting_sanity.py
```

Purpose:

```text
Verify that moving_boundary momentum-accounting quantities can be recorded and have consistent signs for a +x moving-boundary target.
```

Required settings:

```text
n_grid = 32
n_particles = 4096
geometry_type = box
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
target_u_lbm = [0.01, 0.0, 0.0]
mb_reaction_scale = 1.0
mb_force_cap_norm = 0.0001
write_vtk = false
write_particles = false
```

Required flow:

```text
1. Initialize FSIDriver3D or equivalent existing components in moving_boundary mode.
2. At each LBM step, project MPM to LBM.
3. Run update_dynamic_solid() and reinitialize_new_fluid_cells().
4. Run lbm.step_moving_bounceback().
5. Record previous solid particle momentum before MPM reaction substeps.
6. Run MPM substeps using the existing MovingBoundaryFSICoupler3D path.
7. Use MomentumAccounting3D.moving_boundary_accounting_row() to record diagnostics.
8. Save CSV and NPZ timeseries.
```

Required outputs:

```text
outputs/step15_momentum_accounting/accounting_timeseries.csv
outputs/step15_momentum_accounting/accounting_timeseries.npz
logs/step15_momentum_accounting.log
```

Acceptance:

```text
rows are finite
bb_link_count > 0
cell_force_sum_x == 0
bb_net_fluid_impulse_x > 0 for +x moving boundary
bb_net_solid_force_x < 0
hydro_force_sum_x < 0
net_grid_reaction_force_x < 0
force_sign_consistent is True
grid_vs_particle_reaction_error_x finite
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 15 momentum accounting sanity finished
```

## 11. Baseline 2: Reaction Scale Sweep At 32^3

Create:

```text
baseline_tests/run_step15_reaction_scale_sweep_box_32.py
```

Purpose:

```text
Scan mb_reaction_scale at 32^3 and record the effect on solid slowdown, sign reversal, density stability, and momentum accounting.
```

Fixed settings:

```text
n_grid = 32
n_particles = 4096
geometry_type = box
target_u_lbm = [0.01, 0.0, 0.0]
mb_force_cap_norm = 0.0001
n_lbm_steps = 20
mpm_substeps_per_lbm_step = 10
write_vtk = false
write_particles = false
```

Required sweep values:

```text
mb_reaction_scale = [0.25, 0.5, 1.0, 2.0]
```

Required output fields:

```text
reaction_scale
stable
well_behaved
over_damped
sign_reversed
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
initial_solid_vx
final_solid_vx
solid_slowdown
projection_zone_ux_final
hydro_force_max_norm
net_grid_reaction_force_x
solid_momentum_delta_x
classification_reason
score
```

Required outputs:

```text
outputs/step15_reaction_scale_sweep_box_32/reaction_scale_sweep.csv
outputs/step15_reaction_scale_sweep_box_32/reaction_scale_sweep.npz
logs/step15_reaction_scale_sweep_box_32.log
```

Acceptance:

```text
reaction_scale rows include 0.25, 0.5, 1.0, 2.0
at least 0.25, 0.5, and 1.0 are stable
solid_slowdown is non-negative for stable recommended candidates
sign_reversed rows are not recommended
rho_min > 0.95 for stable rows
rho_max < 1.05 for stable rows
mpm_min_J > 0 for stable rows
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 15 reaction scale sweep box 32 finished
```

## 12. Baseline 3: Force Cap Sweep At 48^3

Create:

```text
baseline_tests/run_step15_force_cap_sweep_box_48.py
```

Purpose:

```text
Scan mb_force_cap_norm at 48^3 box to calibrate the conservative moving_boundary settings introduced in Step 14.
```

Fixed settings:

```text
n_grid = 48
n_particles = 13824
geometry_type = box
target_u_lbm = [0.005, 0.0, 0.0]
mb_reaction_scale = 1.0
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
write_vtk = false
write_particles = false
```

Required sweep values:

```text
mb_force_cap_norm = [0.00001, 0.000025, 0.00005, 0.0001]
```

Required output fields:

```text
force_cap_norm
stable
well_behaved
over_damped
sign_reversed
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
initial_solid_vx
final_solid_vx
solid_slowdown
projection_zone_ux_final
hydro_force_max_norm
net_grid_reaction_force_x
classification_reason
score
```

Required outputs:

```text
outputs/step15_force_cap_sweep_box_48/force_cap_sweep.csv
outputs/step15_force_cap_sweep_box_48/force_cap_sweep.npz
logs/step15_force_cap_sweep_box_48.log
```

Acceptance:

```text
force_cap_norm rows include 0.00001, 0.000025, 0.00005, 0.0001
0.000025 row is stable because it is the Step 14 known-good value
at least two rows among 0.00001, 0.000025, 0.00005 are stable
rho_min > 0.95 for stable rows
rho_max < 1.05 for stable rows
mpm_min_J > 0 for stable rows
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 15 force cap sweep box 48 finished
```

## 13. Baseline 4: Squid Proxy Calibrated Window

Create:

```text
baseline_tests/run_step15_squid_proxy_calibrated_window.py
```

Purpose:

```text
Apply the moving_boundary calibration window to the Step 13 procedural squid_proxy at 48^3 and verify the recommended window remains stable.
```

Fixed settings:

```text
n_grid = 48
geometry_type = squid_proxy
geometry_config_path = configs/step13_squid_proxy_geometry.json
n_particles = 4096
target_u_lbm = [0.005, 0.0, 0.0]
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
write_vtk = false
write_particles = false
```

Required sweep grid:

```text
mb_reaction_scale = [0.5, 1.0]
mb_force_cap_norm = [0.000025, 0.00005]
```

Total required rows:

```text
4
```

Required outputs:

```text
outputs/step15_squid_proxy_calibrated_window/squid_proxy_calibration.csv
outputs/step15_squid_proxy_calibrated_window/squid_proxy_calibration.npz
logs/step15_squid_proxy_calibrated_window.log
```

Acceptance:

```text
at least two combinations are stable
recommended combination is stable
rho_min > 0.95 for stable rows
rho_max < 1.05 for stable rows
mpm_min_J > 0 for stable rows
mpm_max_speed < 10 for stable rows
moving_boundary cell_force_max_norm == 0
bb_link_count > 0
no NaN
no Inf
no real squid validation claims
```

Required log marker:

```text
[OK] Step 15 squid proxy calibrated window finished
```

## 14. Baseline 5: Calibrated Vs Original Comparison

Create:

```text
baseline_tests/run_step15_calibrated_vs_original_comparison.py
```

Purpose:

```text
Compare Step 14 original known-good moving_boundary settings against Step 15 recommended settings on 48^3 box.
```

Comparison rows:

```text
original_step14:
  target_u_lbm = [0.005, 0.0, 0.0]
  mb_reaction_scale = 1.0
  mb_force_cap_norm = 0.000025

recommended_step15:
  values selected from the Step 15 force_cap/reaction_scale evidence

optional_conservative:
  a more conservative stable row if recommended_step15 equals original_step14
```

Required output fields:

```text
label
target_u_lbm_x
reaction_scale
force_cap_norm
stable
well_behaved
sign_reversed
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
solid_slowdown
projection_zone_ux_final
hydro_force_max_norm
accounting_error_x
recommendation
```

Required outputs:

```text
outputs/step15_calibrated_vs_original/comparison.csv
outputs/step15_calibrated_vs_original/comparison.npz
logs/step15_calibrated_vs_original.log
```

Acceptance:

```text
comparison contains original_step14
comparison contains recommended_step15
recommended_step15 is stable
recommended_step15 has no sign reversal unless explicitly documented as a conservative fallback
rho_min > 0.95
rho_max < 1.05
mpm_min_J > 0
no NaN
no Inf
recommendation text explains selected config
```

Required log marker:

```text
[OK] Step 15 calibrated vs original comparison finished
```

## 15. Artifact Manifest

Create or reuse a Step 15-specific artifact manifest runner:

```text
baseline_tests/run_step15_artifact_manifest.py
```

If adding a new script, include it in tests and report. If reusing Step 14 artifact utilities through a Step 15 script, keep the output names Step 15-specific.

Required outputs:

```text
outputs/step15_artifact_manifest/artifact_manifest.csv
outputs/step15_artifact_manifest/artifact_summary.json
logs/step15_artifact_manifest.log
```

Acceptance:

```text
manifest exists
summary exists
file_count > 0
total_size_bytes > 0
large_file_count >= 0
large_file_count and total_size_mb are reported in STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md
required calibration baselines have write_vtk=false
required calibration baselines have write_particles=false
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 15 artifact manifest finished
```

## 16. Documentation Updates

Create:

```text
docs/14_moving_boundary_calibration.md
```

Must include:

```text
Step 15 scope
explicit statement that Step 15 does not change moving bounce-back formula
explicit statement that Step 15 does not add new FSI physics
quantities tracked by MomentumAccounting3D
reaction_scale calibration
force_cap_norm calibration
recommended box 48^3 config
recommended squid_proxy 48^3 config
limitations and non-goals
```

Must state:

```text
The transfer remains an engineering coupling scale.
Strict link-area momentum-conserving coupling is future work.
squid_proxy is procedural and not real squid validation.
```

Update `README.md`:

```text
Add a concise note that Step 15 adds moving-boundary reaction calibration diagnostics and recommended moving_boundary configs.
Do not claim strict final momentum conservation.
```

Update `docs/08_roadmap.md`:

```text
Mark Step 15 as current while in progress, and completed after acceptance.
Set Step 16 to long-run validation and 64^3 moving_boundary feasibility.
State that future physics must preserve Step 10 mode matrix, Step 13 geometry contracts, and Step 14 scale baselines.
```

Update `docs/13_larger_grid_validation.md`:

```text
Add a note that Step 15 calibrates the conservative moving_boundary settings introduced in Step 14.
```

Update `docs/09_api_reference.md`:

```text
Add MomentumAccounting3D.
Add calibration utility functions.
Add recommended Step 15 config names.
```

Update `docs/10_performance_memory.md`:

```text
Add a short Step 15 calibration runtime/artifact note if timing rows are generated.
Keep timing language as environment-specific regression data, not benchmarks.
```

## 17. Step 15 Report Contract

Create:

```text
STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md
```

Required sections:

```markdown
# Step 15 Moving-Boundary Calibration Report

## 1. Goal
## 2. Files
## 3. Explicit Non-Goals
## 4. Momentum Accounting Sanity
## 5. Reaction Scale Sweep
## 6. Force Cap Sweep At 48^3
## 7. Squid Proxy Calibrated Window
## 8. Calibrated Vs Original Comparison
## 9. Recommended Configs
## 10. Artifact Manifest
## 11. Documentation Updates
## 12. Verification
## 13. GitHub Sync
## 14. Acceptance Checklist
## 15. Decision
```

The report must include:

```text
commands run
config files used
accounting sanity key values
reaction_scale sweep table
force_cap sweep table
squid_proxy calibration table
calibrated-vs-original table
recommended config values and reasons
artifact summary
pytest command/result
confirmation that external/taichi_LBM3D was unchanged
confirmation that no FSI physics changed
confirmation that squid_proxy is not real squid validation
final commit hash or a note that the final hash is reported after commit creation
remote branch after push
```

Before final verification, checklist items may be unchecked. They must be checked only after baselines and pytest pass.

## 18. Pytest Contract

Create:

```text
tests/test_step15_moving_boundary_calibration_contract.py
```

The test must check required paths:

```python
required_paths = [
    "src/momentum_accounting.py",
    "src/calibration.py",
    "configs/step15_mb_calibration_box_32.json",
    "configs/step15_mb_force_cap_box_48.json",
    "configs/step15_mb_calibration_squid_proxy_48.json",
    "configs/step15_mb_recommended_box_48.json",
    "configs/step15_mb_recommended_squid_proxy_48.json",
    "baseline_tests/run_step15_momentum_accounting_sanity.py",
    "baseline_tests/run_step15_reaction_scale_sweep_box_32.py",
    "baseline_tests/run_step15_force_cap_sweep_box_48.py",
    "baseline_tests/run_step15_squid_proxy_calibrated_window.py",
    "baseline_tests/run_step15_calibrated_vs_original_comparison.py",
    "logs/step15_momentum_accounting.log",
    "logs/step15_reaction_scale_sweep_box_32.log",
    "logs/step15_force_cap_sweep_box_48.log",
    "logs/step15_squid_proxy_calibrated_window.log",
    "logs/step15_calibrated_vs_original.log",
    "outputs/step15_momentum_accounting/accounting_timeseries.csv",
    "outputs/step15_reaction_scale_sweep_box_32/reaction_scale_sweep.csv",
    "outputs/step15_force_cap_sweep_box_48/force_cap_sweep.csv",
    "outputs/step15_squid_proxy_calibrated_window/squid_proxy_calibration.csv",
    "outputs/step15_calibrated_vs_original/comparison.csv",
    "docs/14_moving_boundary_calibration.md",
    "STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md",
]
```

If Step 15 artifact manifest is required by implementation:

```python
required_paths.extend([
    "baseline_tests/run_step15_artifact_manifest.py",
    "logs/step15_artifact_manifest.log",
    "outputs/step15_artifact_manifest/artifact_summary.json",
])
```

The test must check source keywords:

```text
class MomentumAccounting3D
hydro_force_sum
cell_force_sum
solid_particle_momentum
moving_boundary_accounting_row
classify_calibration_row
choose_recommended_row
write_calibration_summary
reaction_scale
force_cap_norm
sign_reversed
solid_slowdown
```

The test must check log success markers:

```text
[OK] Step 15 momentum accounting sanity finished
[OK] Step 15 reaction scale sweep box 32 finished
[OK] Step 15 force cap sweep box 48 finished
[OK] Step 15 squid proxy calibrated window finished
[OK] Step 15 calibrated vs original comparison finished
```

If Step 15 artifact manifest is included:

```text
[OK] Step 15 artifact manifest finished
```

The test must parse CSV/JSON/NPZ outputs and verify:

```text
accounting_timeseries.csv has finite rows
accounting_timeseries.csv has bb_link_count > 0
accounting_timeseries.csv has cell_force_sum_x == 0
accounting_timeseries.csv has force_sign_consistent true rows
reaction_scale_sweep.csv contains reaction_scale 0.25, 0.5, 1.0, 2.0
reaction_scale_sweep.csv has at least 3 stable rows among 0.25, 0.5, 1.0
force_cap_sweep.csv contains force_cap_norm 0.000025
force_cap_sweep.csv has 0.000025 stable
force_cap_sweep.csv has at least two stable rows among 0.00001, 0.000025, 0.00005
squid_proxy_calibration.csv has at least two stable rows
comparison.csv contains original_step14 and recommended_step15
recommended configs have coupling_mode == moving_boundary
recommended configs have write_vtk == false
recommended configs have write_particles == false
all stable rows have rho_min > 0.95
all stable rows have rho_max < 1.05
all stable rows have lbm_max_v < 0.1
all stable rows have mpm_min_J > 0
all stable rows have mpm_max_speed < 10
```

The test must check documentation/report do not contain overclaim phrases:

```text
real squid simulation is validated
validated squid swimming
biomechanically accurate squid
anatomically accurate squid
production benchmark
strict momentum-conserving FSI is complete
```

The test must check forbidden implementation claims:

```text
implements two_phase
implements contact_angle
implements ReducedSquidFSI
```

Do not forbid explanatory non-goal phrases such as:

```text
no two-phase flow
no contact angle physics
not real squid validation
not a production benchmark
strict link-area momentum-conserving coupling is future work
```

The test must check `STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md` acceptance checklist items are marked `[x]`.

## 19. Required Execution Order

Follow this order:

```text
1. Confirm git status, branch, remote, README, roadmap, and Step 14 baseline.
2. Read STEP15_MOVING_BOUNDARY_CALIBRATION_GOAL.md.
3. Read README.md, docs/08_roadmap.md, docs/09_api_reference.md, docs/10_performance_memory.md, docs/13_larger_grid_validation.md, STEP14_LARGER_GRID_VALIDATION_REPORT.md, src/lbm_fluid.py, src/moving_boundary_coupling.py, src/fsi_driver.py, and src/diagnostics.py.
4. Add tests/test_step15_moving_boundary_calibration_contract.py first.
5. Run pytest and confirm RED because Step 15 artifacts are missing.
6. Implement src/momentum_accounting.py.
7. Add and run run_step15_momentum_accounting_sanity.py, saving log.
8. Implement src/calibration.py.
9. Add Step 15 base configs.
10. Add and run run_step15_reaction_scale_sweep_box_32.py, saving log.
11. Add and run run_step15_force_cap_sweep_box_48.py, saving log.
12. Add and run run_step15_squid_proxy_calibrated_window.py, saving log.
13. Generate recommended box and squid_proxy configs from evidence.
14. Add and run run_step15_calibrated_vs_original_comparison.py, saving log.
15. Add Step 15 artifact manifest runner or equivalent Step 15 manifest output, saving log.
16. Add docs/14_moving_boundary_calibration.md.
17. Update README.md, docs/08_roadmap.md, docs/09_api_reference.md, docs/10_performance_memory.md, and docs/13_larger_grid_validation.md.
18. Add STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md with unchecked checklist.
19. Run pytest -q.
20. Fix only Step 15 issues.
21. Save final pytest log as logs/step15_pytest.log.
22. Confirm src solver physics behavior is unchanged except diagnostics/config/orchestration additions.
23. Confirm external/taichi_LBM3D is unchanged.
24. Update STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md checklist to checked.
25. Run final pytest -q.
26. Run git diff --check and git diff --cached --check.
27. Commit Step 15 artifacts.
28. Push to GitHub.
29. Verify local HEAD equals origin/main.
```

Do not report a short probe as Step 15 acceptance. Step 15 acceptance requires all required baselines, recommended configs, docs, report, pytest, and GitHub push.

## 20. Verification Commands

Primary:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Baseline commands:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_momentum_accounting_sanity.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_reaction_scale_sweep_box_32.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_force_cap_sweep_box_48.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_squid_proxy_calibrated_window.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_calibrated_vs_original_comparison.py
```

If Step 15 artifact manifest script exists:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_artifact_manifest.py
```

Log-saving form:

```powershell
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_momentum_accounting_sanity.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step15_momentum_accounting.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_reaction_scale_sweep_box_32.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step15_reaction_scale_sweep_box_32.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_force_cap_sweep_box_48.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step15_force_cap_sweep_box_48.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_squid_proxy_calibrated_window.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step15_squid_proxy_calibrated_window.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_calibrated_vs_original_comparison.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step15_calibrated_vs_original.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' -m pytest -q 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step15_pytest.log; $out; if ($code -ne 0) { exit $code }
```

Git hygiene:

```powershell
git status --short --branch
git status --short external
git diff --check
git diff --cached --check
```

## 21. Hard Acceptance Checklist

All must be true before Step 15 is complete:

```text
[ ] main is on the Step 15 final commit
[ ] src/momentum_accounting.py exists
[ ] src/calibration.py exists
[ ] src/__init__.py exports MomentumAccounting3D and calibration helpers if appropriate
[ ] configs/step15_mb_calibration_box_32.json exists
[ ] configs/step15_mb_force_cap_box_48.json exists
[ ] configs/step15_mb_calibration_squid_proxy_48.json exists
[ ] configs/step15_mb_recommended_box_48.json exists
[ ] configs/step15_mb_recommended_squid_proxy_48.json exists
[ ] accounting sanity baseline passes
[ ] bb_link_count > 0 in accounting sanity
[ ] bb_net_fluid_impulse_x > 0 for +x moving boundary
[ ] bb_net_solid_force_x < 0
[ ] hydro_force_sum_x < 0
[ ] net_grid_reaction_force_x < 0
[ ] cell_force_sum_x == 0
[ ] force_sign_consistent is true for recommended rows
[ ] reaction_scale sweep passes
[ ] reaction_scale sweep includes 0.25, 0.5, 1.0, 2.0
[ ] force_cap sweep 48^3 passes
[ ] force_cap sweep includes 0.000025
[ ] Step 14 known-good 0.000025 force cap remains stable
[ ] squid_proxy calibrated window passes
[ ] calibrated vs original comparison passes
[ ] recommended box 48 config is stable
[ ] recommended squid_proxy 48 config is stable
[ ] no sign reversal in recommended configs unless explicitly documented as fallback
[ ] rho_min > 0.95 for all stable rows
[ ] rho_max < 1.05 for all stable rows
[ ] lbm_max_v < 0.1 for all stable rows
[ ] mpm_min_J > 0 for all stable rows
[ ] mpm_max_speed < 10 for all stable rows
[ ] no NaN
[ ] no Inf
[ ] no new FSI physics
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no real squid validation claims
[ ] no sparse storage implementation
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] artifact large_file_count controlled and reported
[ ] docs/14_moving_boundary_calibration.md exists
[ ] docs state engineering coupling scale and future strict momentum work
[ ] README.md updated conservatively
[ ] docs/08_roadmap.md updated
[ ] docs/09_api_reference.md updated
[ ] docs/13_larger_grid_validation.md updated
[ ] STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md complete
[ ] tests/test_step15_moving_boundary_calibration_contract.py exists
[ ] pytest -q passes
[ ] logs/step15_pytest.log exists
[ ] git diff --check passes
[ ] Step 15 artifacts are committed
[ ] Step 15 artifacts are pushed to GitHub
```

## 22. Failure Handling

If accounting signs are inconsistent:

```text
Inspect whether the sign convention is documented incorrectly.
Do not change solver physics to force a sign.
Fix diagnostic naming or report the convention explicitly if the code's convention differs.
```

If hydro_force sum and bb_net_solid_force disagree:

```text
Record the discrepancy.
Check whether one quantity is per-step impulse and the other is a force-like diagnostic.
Do not require strict equality unless the current implementation semantics prove they should match.
Do not alter moving bounce-back formulas.
```

If reaction_scale sweep creates sign reversal:

```text
Classify the row as over_damped or sign_reversed.
Do not recommend that row unless no other stable row exists and the report explicitly marks it as fallback.
```

If 48^3 force_cap sweep is unstable at high caps:

```text
Keep high-cap rows as failed evidence.
Do not lower the required Step 14 known-good row.
Recommend the stable conservative row.
Do not change moving-boundary formulas.
```

If squid_proxy calibrated window has fewer than two stable rows:

```text
Reduce only Step 15 config aggressiveness.
Keep squid_proxy as procedural proxy and do not claim real squid validation.
Do not report a shorter probe as full acceptance unless the goal is explicitly revised.
```

If Step 10, Step 12, Step 13, or Step 14 regression tests fail:

```text
Stop and inspect whether Step 15 changed existing behavior.
Fix diagnostics/config compatibility.
Do not weaken existing tests unless the failure is a demonstrably stale documentation-only assertion and the report explains why.
```

If artifact manifest finds large files:

```text
Identify whether they are required baseline artifacts.
Move optional scratch outputs out of the committed artifact path if created by the current task.
Record large_file_count and total_size_mb in the report.
Do not delete user-created files without explicit approval.
```

If pytest fails:

```text
Record the exact failing tests and error text.
Fix only issues caused by Step 15 unless the user explicitly broadens scope.
```

If GitHub push fails:

```text
Keep the local commit.
Record the exact push error.
Do not force-push unless explicitly requested.
```

## 23. Completion Definition

Step 15 is complete only when:

```text
1. all required Step 15 files exist
2. MomentumAccounting3D is implemented and diagnostic-only
3. calibration helpers are implemented
4. momentum accounting sanity baseline passes
5. reaction_scale sweep baseline passes
6. force_cap_norm sweep baseline passes
7. squid_proxy calibrated window baseline passes
8. calibrated-vs-original comparison baseline passes
9. recommended box 48^3 and squid_proxy 48^3 configs are written from evidence
10. artifact manifest is generated and reported
11. docs and README updates are complete
12. Step 15 report has a completed checklist
13. pytest -q passes
14. logs/step15_pytest.log is saved
15. external/taichi_LBM3D remains unchanged
16. no FSI physics was changed
17. no real squid validation is claimed
18. final Step 15 commit is pushed to GitHub
19. local HEAD matches origin/main
```

Only after those conditions are satisfied may the report mark:

```text
Can proceed to Step 16?

- [x] Yes
- [ ] No
```

Suggested Step 16 title:

```text
Step 16: Long-run validation and 64^3 moving_boundary feasibility
```
