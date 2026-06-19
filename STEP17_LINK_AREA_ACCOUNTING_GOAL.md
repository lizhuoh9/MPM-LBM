# Step 17 Goal: Link-Area Momentum Accounting Prototype

This file is the authoritative execution contract for Step 17 in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Step 17 starts only when a `/goal` message explicitly references this file.

## 1. Status Before Step 17

Step 16 is accepted on GitHub at commit:

```text
366725e603ab72d3f0285c549c62ab852cf1857b
```

Step 16 established:

- 48^3 box moving_boundary long-run: 50 LBM steps / 500 MPM substeps.
- 48^3 procedural squid_proxy moving_boundary long-run: 30 LBM steps / 300 MPM substeps.
- 64^3 box moving_boundary feasibility: 5 LBM steps / 25 MPM substeps.
- 64^3 none/penalty/moving_boundary mode comparison.
- `pytest -q`: 102 passed.
- `external/taichi_LBM3D` unchanged.

Step 16 also documents that:

- the 64^3 moving_boundary row is a feasibility baseline;
- squid_proxy is procedural and not real squid validation;
- strict link-area momentum-conserving coupling remains future work.

Step 17 must preserve all of the above.

## 2. Step 17 Objective

Implement a diagnostic-only link-area momentum accounting prototype for the existing moving_boundary path.

The goal is to move from:

```text
moving_boundary has engineering-scale reaction transfer and scalar/vector momentum diagnostics
```

to:

```text
moving_boundary has per-D3Q19-direction link-wise accounting and link-area proxy momentum budgets
```

Step 17 must:

1. Record bounce-back link counts per D3Q19 direction.
2. Record fluid impulse per D3Q19 direction.
3. Record solid reaction force per D3Q19 direction.
4. Record correction absolute sum and max per D3Q19 direction.
5. Provide diagnostic-only link-area proxy weighting policies.
6. Compare `uniform`, `inverse_length`, and `length` area proxy policies.
7. Analyze 48^3 box, 48^3 procedural squid_proxy, and 64^3 box moving_boundary baselines.
8. Add Step 16 regression evidence showing existing behavior remains stable.
9. Keep the existing engineering-scale moving_boundary coupler unchanged.

Step 17 is accounting and evidence infrastructure. It is not a new production FSI method.

## 3. Hard Boundaries

Do not implement or change:

- no change to the Step 8 moving bounce-back formula;
- no change to the Step 9 `MovingBoundaryFSICoupler3D` reaction transfer formula;
- no change to `PenaltyFSICoupler3D`;
- no change to `FSIDriver3D` default behavior;
- no new production FSI mode;
- no replacement of the existing moving_boundary coupling path;
- no two-phase flow;
- no contact angle physics;
- no real squid validation claims;
- no squid actuation or swimming simulation;
- no mesh import;
- no sparse storage;
- no `ReducedSquidFSI`;
- no edits to `external/taichi_LBM3D`;
- no claim that strict momentum-conserving sharp-interface FSI is complete.

Allowed work:

- diagnostic-only per-direction accumulators;
- link-area proxy metrics;
- accounting tables;
- comparison reports;
- opt-in analysis scripts;
- future-work documentation.

## 4. Required Source Changes

### 4.1 `src/lbm_fluid.py`

Add small diagnostic fields to `LBMFluid3D`:

```python
self.bb_link_count_by_dir = ti.field(ti.i32, shape=(19,))
self.bb_fluid_impulse_by_dir = ti.Vector.field(3, ti.f32, shape=(19,))
self.bb_solid_force_by_dir = ti.Vector.field(3, ti.f32, shape=(19,))
self.bb_correction_abs_sum_by_dir = ti.field(ti.f32, shape=(19,))
self.bb_correction_abs_max_by_dir = ti.field(ti.f32, shape=(19,))
```

Update `clear_moving_boundary_diagnostics()` to clear these fields.

Update `streaming_moving_bounceback()` only by adding per-direction atomic diagnostics inside the existing bounce-back link block:

```python
ti.atomic_add(self.bb_link_count_by_dir[s], 1)
for d in ti.static(range(3)):
    ti.atomic_add(self.bb_fluid_impulse_by_dir[s][d], fluid_impulse[d])
    ti.atomic_add(self.bb_solid_force_by_dir[s][d], solid_force[d])
ti.atomic_add(self.bb_correction_abs_sum_by_dir[s], ti.abs(correction))
ti.atomic_max(self.bb_correction_abs_max_by_dir[s], ti.abs(correction))
```

Do not modify:

```python
correction = -6.0 * w[s] * rho * dot(e[s], u_wall)
bounced = f[i][s] + correction
```

Add:

```python
def get_moving_boundary_directional_stats(self):
    """
    Diagnostic-only. Returns per-D3Q19-direction bounce-back link counts,
    fluid impulses, solid forces, and correction statistics.
    """
```

The return dictionary must contain:

```text
link_count_by_dir: shape (19,)
fluid_impulse_by_dir: shape (19, 3)
solid_force_by_dir: shape (19, 3)
correction_abs_sum_by_dir: shape (19,)
correction_abs_max_by_dir: shape (19,)
```

### 4.2 `src/link_area_accounting.py`

Add:

```python
class LinkAreaMomentumAccounting3D:
    """
    Diagnostic-only link-area proxy accounting for moving-boundary bounce-back.
    Does not modify solver state.
    """
```

Required functions:

```python
direction_metadata(lbm)
area_weights(lbm, policy="inverse_length")
read_directional_stats(lbm)
area_weighted_impulse(lbm, policy="inverse_length")
summarize_link_accounting(lbm, policy="inverse_length")
```

Direction metadata must use the actual `lbm.e.to_numpy()` ordering. Direction classes:

```text
rest
axis
face_diagonal
```

D3Q19 has no body diagonal.

Area proxy policies:

```text
uniform:        area_weight = 1
inverse_length: area_weight = 1 / ||e||
length:         area_weight = ||e||
```

For `rest`, area weight must be `0`.

Required summary fields include:

```text
policy
total_link_count
axis_link_count
face_diagonal_link_count
area_proxy_total
bb_net_fluid_impulse_x
bb_net_solid_force_x
area_weighted_fluid_impulse_x
area_weighted_solid_force_x
area_weighted_balance_error_x
scalar_vs_directional_impulse_error_x
hydro_force_sum_x
hydro_vs_directional_solid_error_x
```

### 4.3 `src/__init__.py`

Export `LinkAreaMomentumAccounting3D`.

## 5. Required Config Files

Create:

```text
configs/step17_link_area_wall_32.json
configs/step17_link_area_box_48.json
configs/step17_link_area_squid_proxy_48.json
configs/step17_link_area_box_64.json
```

All Step 17 configs must set:

```text
write_vtk = false
write_particles = false
```

### 5.1 Wall / Sanity Config

```json
{
  "coupling_mode": "moving_boundary",
  "geometry_type": "box",
  "n_grid": 32,
  "n_particles": 4096,
  "n_lbm_steps": 100,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.02, 0.0, 0.0],
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.0001,
  "output_interval": 20,
  "write_vtk": false,
  "write_particles": false
}
```

### 5.2 48^3 Box Link Budget

```json
{
  "coupling_mode": "moving_boundary",
  "geometry_type": "box",
  "n_grid": 48,
  "n_particles": 13824,
  "n_lbm_steps": 20,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.00001,
  "output_interval": 10,
  "write_vtk": false,
  "write_particles": false
}
```

### 5.3 48^3 Procedural Squid Proxy Link Budget

```json
{
  "coupling_mode": "moving_boundary",
  "geometry_type": "squid_proxy",
  "geometry_config_path": "configs/step13_squid_proxy_geometry.json",
  "n_grid": 48,
  "n_particles": 4096,
  "n_lbm_steps": 20,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "mb_reaction_scale": 0.5,
  "mb_force_cap_norm": 0.000025,
  "output_interval": 10,
  "write_vtk": false,
  "write_particles": false
}
```

### 5.4 64^3 Box Link Budget Feasibility

```json
{
  "coupling_mode": "moving_boundary",
  "geometry_type": "box",
  "n_grid": 64,
  "n_particles": 32768,
  "n_lbm_steps": 5,
  "mpm_substeps_per_lbm_step": 5,
  "target_u_lbm": [0.0025, 0.0, 0.0],
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.000005,
  "output_interval": 5,
  "write_vtk": false,
  "write_particles": false
}
```

## 6. Required Baseline Scripts

Create:

```text
baseline_tests/run_step17_directional_link_sanity.py
baseline_tests/run_step17_link_area_wall_couette.py
baseline_tests/run_step17_box_48_link_budget.py
baseline_tests/run_step17_squid_proxy_48_link_budget.py
baseline_tests/run_step17_box_64_link_budget.py
baseline_tests/run_step17_step16_regression.py
baseline_tests/run_step17_artifact_manifest.py
```

Use the known workspace Python for validation commands:

```text
D:\working\taichi\env\python.exe
```

Prefer `ti.gpu` for baselines. If GPU initialization fails, stop and report the failure; do not silently downgrade a required Step 17 baseline to CPU.

All logs must be UTF-8.

## 7. Baseline Contracts

### 7.1 Directional Link Sanity

Script:

```text
baseline_tests/run_step17_directional_link_sanity.py
```

Outputs:

```text
outputs/step17_directional_link_sanity/directional_stats.csv
outputs/step17_directional_link_sanity/directional_stats.npz
logs/step17_directional_link_sanity.log
```

Required checks:

```text
sum(bb_link_count_by_dir) == bb_link_count
sum(bb_fluid_impulse_by_dir) matches bb_net_fluid_impulse within f32 tolerance
sum(bb_solid_force_by_dir) matches bb_net_solid_force within f32 tolerance
bb_net_fluid_impulse_x > 0
bb_net_solid_force_x < 0
cell_force_max_norm == 0
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
all arrays finite
```

Success marker:

```text
[OK] Step 17 directional link sanity finished
```

### 7.2 Link-Area Wall Couette

Script:

```text
baseline_tests/run_step17_link_area_wall_couette.py
```

Outputs:

```text
outputs/step17_link_area_wall_couette/area_policy_comparison.csv
outputs/step17_link_area_wall_couette/area_policy_comparison.npz
logs/step17_link_area_wall_couette.log
```

Compare policies:

```text
uniform
inverse_length
length
```

Required fields:

```text
policy
total_link_count
axis_link_count
face_diagonal_link_count
area_proxy_total
bb_net_fluid_impulse_x
area_weighted_fluid_impulse_x
area_weighted_solid_force_x
area_weighted_balance_error_x
rho_min
rho_max
lbm_max_v
cell_force_max_norm
```

Required checks:

```text
all policies finite
all policies have area_proxy_total > 0
bb_net_fluid_impulse_x > 0
area_weighted_solid_force_x < 0
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
cell_force_max_norm == 0
```

Success marker:

```text
[OK] Step 17 link-area wall Couette finished
```

### 7.3 48^3 Box Link Budget

Script:

```text
baseline_tests/run_step17_box_48_link_budget.py
```

Outputs:

```text
outputs/step17_box_48_link_budget/link_budget_timeseries.csv
outputs/step17_box_48_link_budget/link_budget_summary.json
outputs/step17_box_48_link_budget/directional_stats_final.npz
logs/step17_box_48_link_budget.log
```

Required checks:

```text
stable == true
completed_lbm_steps >= 20
total_mpm_substeps >= 200
rho_min_global > 0.95
rho_max_global < 1.05
lbm_max_v_global < 0.1
mpm_min_J_global > 0
bb_link_count_min > 0
scalar_vs_directional_impulse_error_x finite and small
hydro_vs_directional_solid_error_x finite and recorded
area_proxy_total > 0
cell_force_max_norm == 0
```

Success marker:

```text
[OK] Step 17 box 48 link budget finished
```

### 7.4 48^3 Procedural Squid Proxy Link Budget

Script:

```text
baseline_tests/run_step17_squid_proxy_48_link_budget.py
```

Outputs:

```text
outputs/step17_squid_proxy_48_link_budget/link_budget_timeseries.csv
outputs/step17_squid_proxy_48_link_budget/link_budget_summary.json
outputs/step17_squid_proxy_48_link_budget/directional_stats_final.npz
logs/step17_squid_proxy_48_link_budget.log
```

Required checks:

```text
stable == true
completed_lbm_steps >= 20
total_mpm_substeps >= 200
rho_min_global > 0.95
rho_max_global < 1.05
lbm_max_v_global < 0.1
mpm_min_J_global > 0
bb_link_count_min > 0
axis_link_count > 0
face_diagonal_link_count > 0
area_proxy_total > 0
cell_force_max_norm == 0
docs and report state squid_proxy is procedural and not real squid validation
```

Success marker:

```text
[OK] Step 17 squid proxy 48 link budget finished
```

### 7.5 64^3 Box Link Budget Feasibility

Script:

```text
baseline_tests/run_step17_box_64_link_budget.py
```

Outputs:

```text
outputs/step17_box_64_link_budget/link_budget_summary.json
outputs/step17_box_64_link_budget/directional_stats_final.npz
logs/step17_box_64_link_budget.log
```

Required checks:

```text
n_grid == 64
stable == true
completed_lbm_steps >= 5
total_mpm_substeps >= 25
bb_link_count > 0
area_proxy_total > 0
rho_min > 0.95
rho_max < 1.05
mpm_min_J > 0
cell_force_max_norm == 0
```

Success marker:

```text
[OK] Step 17 box 64 link budget finished
```

### 7.6 Step 16 Regression

Script:

```text
baseline_tests/run_step17_step16_regression.py
```

Purpose:

```text
Prove Step 17 diagnostic accumulators did not break Step 16 behavior.
```

Run lightweight versions of:

```text
48^3 box moving_boundary, 10 LBM steps
64^3 box moving_boundary, 5 LBM steps
```

Do not require bitwise identity. Require the same stability thresholds and mode boundaries.

Outputs:

```text
outputs/step17_step16_regression/regression_results.csv
outputs/step17_step16_regression/regression_results.npz
logs/step17_step16_regression.log
```

Success marker:

```text
[OK] Step 17 Step 16 regression finished
```

### 7.7 Artifact Manifest

Script:

```text
baseline_tests/run_step17_artifact_manifest.py
```

Outputs:

```text
outputs/step17_artifact_manifest/artifact_manifest.csv
outputs/step17_artifact_manifest/artifact_summary.json
logs/step17_artifact_manifest.log
```

Required checks:

```text
file_count > 0
total_size_mb recorded
large_file_count == 0
```

Success marker:

```text
[OK] Step 17 artifact manifest finished
```

## 8. Required Documentation

Create:

```text
docs/16_link_area_momentum_accounting.md
STEP17_LINK_AREA_ACCOUNTING_REPORT.md
```

Update:

```text
README.md
docs/08_roadmap.md
docs/09_api_reference.md
docs/14_moving_boundary_calibration.md
docs/15_long_run_validation.md
```

Required documentation phrases:

```text
Step 17 adds diagnostic-only direction-wise and link-area proxy accounting.
The moving bounce-back formula is unchanged.
MovingBoundaryFSICoupler3D is unchanged.
These are diagnostic proxy policies, not final surface-area reconstruction.
Strict link-area momentum-conserving coupling remains future work.
squid_proxy is procedural and not real squid validation.
```

Forbidden documentation/report claims:

```text
strict momentum-conserving FSI is complete
real squid simulation is validated
validated squid swimming
biomechanically accurate squid
anatomically accurate squid
production-ready solver
implements two_phase
implements contact_angle
implements ReducedSquidFSI
```

## 9. Required Contract Test

Create:

```text
tests/test_step17_link_area_accounting_contract.py
```

The test must check required paths, source keywords, logs, CSV/JSON/NPZ outputs, docs/report wording, and the acceptance checklist.

Required source keywords:

```text
bb_link_count_by_dir
bb_fluid_impulse_by_dir
bb_solid_force_by_dir
bb_correction_abs_sum_by_dir
bb_correction_abs_max_by_dir
get_moving_boundary_directional_stats
class LinkAreaMomentumAccounting3D
direction_metadata
area_weights
area_weighted_impulse
summarize_link_accounting
uniform
inverse_length
length
```

Required output checks:

```text
directional_stats.csv:
  sum_link_count_by_dir == bb_link_count
  scalar_vs_directional_impulse_error_x < tolerance

area_policy_comparison.csv:
  contains uniform, inverse_length, length
  all area_proxy_total > 0

box_48 / squid_proxy_48 / box_64 summaries:
  stable == true
  area_proxy_total > 0
  bb_link_count_min > 0
  cell_force_max_norm == 0
```

The contract test must first be run in RED state after being added, before implementation is complete.

## 10. Execution Order

Follow this order.

### Phase A: Contract Test First

1. Add `tests/test_step17_link_area_accounting_contract.py`.
2. Run it and confirm RED due to missing Step 17 files/artifacts.

### Phase B: Directional Diagnostics

1. Update `src/lbm_fluid.py` with per-direction diagnostic fields.
2. Update clear and accumulation kernels.
3. Add `get_moving_boundary_directional_stats()`.
4. Export `LinkAreaMomentumAccounting3D` later through `src/__init__.py`.
5. Run `run_step17_directional_link_sanity.py`.

### Phase C: Link-Area Accounting Tools

1. Add `src/link_area_accounting.py`.
2. Implement D3Q19 metadata from actual LBM direction ordering.
3. Implement `uniform`, `inverse_length`, and `length` policies.
4. Implement scalar-vs-directional consistency checks.
5. Run wall Couette area policy comparison.

### Phase D: Link Budget Baselines

1. Run 48^3 box link budget.
2. Run 48^3 procedural squid_proxy link budget.
3. Run 64^3 box link budget feasibility.
4. Run Step 16 regression.

### Phase E: Documentation And Report

1. Write `docs/16_link_area_momentum_accounting.md`.
2. Update README and docs listed above.
3. Write `STEP17_LINK_AREA_ACCOUNTING_REPORT.md` with actual results.
4. Run artifact manifest.
5. Run full `pytest -q`.

### Phase F: GitHub Sync

1. Confirm `external/taichi_LBM3D` unchanged.
2. Run `git diff --check`.
3. Commit all Step 17 code, docs, logs, outputs, tests, and report.
4. Push to `origin/main`.
5. Confirm local `HEAD` equals `origin/main`.

## 11. Hard Acceptance Checklist

The report must mark all of these complete:

```text
[ ] main is on the Step 17 final commit
[ ] LBMFluid3D has per-direction moving-boundary diagnostics
[ ] get_moving_boundary_directional_stats() exists
[ ] src/link_area_accounting.py exists
[ ] LinkAreaMomentumAccounting3D exists
[ ] configs/step17_link_area_wall_32.json exists
[ ] configs/step17_link_area_box_48.json exists
[ ] configs/step17_link_area_squid_proxy_48.json exists
[ ] configs/step17_link_area_box_64.json exists
[ ] directional sanity baseline passes
[ ] sum(direction counts) == scalar bb_link_count
[ ] sum(direction impulses) matches scalar impulse within tolerance
[ ] area proxy policies uniform / inverse_length / length run
[ ] 48^3 box link budget passes
[ ] 48^3 squid_proxy link budget passes
[ ] 64^3 box link budget passes
[ ] Step 16 regression passes
[ ] rho_min > 0.95
[ ] rho_max < 1.05
[ ] lbm_max_v < 0.1
[ ] mpm_min_J > 0
[ ] cell_force_max_norm == 0 for moving_boundary rows
[ ] no NaN
[ ] no Inf
[ ] no new bounce-back formula
[ ] no new reaction transfer formula
[ ] no new FSI mode
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no real squid validation claims
[ ] no sparse storage implementation
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] artifact large_file_count controlled
[ ] docs/16_link_area_momentum_accounting.md exists
[ ] STEP17_LINK_AREA_ACCOUNTING_REPORT.md complete
[ ] tests/test_step17_link_area_accounting_contract.py exists
[ ] pytest -q passes
[ ] logs/step17_pytest.log exists
[ ] git diff --check passes
[ ] Step 17 artifacts are committed
[ ] Step 17 artifacts are pushed to GitHub
```

## 12. Failure Handling

If a required baseline fails:

1. Stop and identify whether the failure is diagnostics-only, encoding/logging, Taichi runtime, or solver-state instability.
2. Do not weaken thresholds without documenting the reason.
3. Do not shorten required baselines and call them complete.
4. Do not replace a required 48^3 or 64^3 baseline with a short probe.
5. Do not hide instability by filtering rows.
6. Keep failed evidence if it is useful, but do not mark acceptance complete until the required baseline passes.

If per-direction sums do not match scalar diagnostics:

1. Inspect the bounce-back branch where scalar diagnostics are already updated.
2. Add only matching atomic diagnostic updates.
3. Do not change the bounce-back correction formula.
4. Re-run directional sanity immediately.

If `external/taichi_LBM3D` changes:

1. Stop.
2. Revert only the unintended external changes.
3. Continue only after `git status --short external/taichi_LBM3D` is clean.

## 13. Completion Definition

Step 17 is complete only when:

```text
1. All required files exist.
2. All Step 17 baselines pass.
3. All required logs and outputs are generated.
4. Artifact manifest exists and reports controlled artifacts.
5. STEP17_LINK_AREA_ACCOUNTING_REPORT.md is complete.
6. pytest -q passes.
7. external/taichi_LBM3D is unchanged.
8. git diff --check passes.
9. All Step 17 code/docs/logs/outputs/report are committed.
10. The commit is pushed to GitHub origin/main.
11. Local HEAD equals origin/main.
```

Only after these are true may the goal be marked complete.
