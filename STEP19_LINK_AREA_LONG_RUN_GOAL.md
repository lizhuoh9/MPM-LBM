# Step 19 Goal: Experimental Link-Area Transfer Long-Run and 64^3 Feasibility

This file is the authoritative execution contract for Step 19 in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Step 19 starts only when a `/goal` message explicitly references this file.

## 1. Status Before Step 19

Step 18 is accepted on GitHub at commit:

```text
23eeb38d4ae343dcbd57f87ecbdf55f0e682a879
```

Step 18 established:

- `reaction_transfer_mode = "engineering" | "link_area_experimental"`;
- default `reaction_transfer_mode == "engineering"`;
- `reaction_transfer_mode = "link_area_experimental"` is valid only with `coupling_mode = "moving_boundary"`;
- `LinkAreaMovingBoundaryCoupler3D`;
- bounded global `area_scale` from Step 17 link-area proxy accounting;
- 32^3 link-area transfer sanity baseline;
- 32^3 policy sweep for `uniform`, `inverse_length`, and `length`;
- 48^3 box `link_area_experimental` baseline;
- 48^3 procedural squid_proxy `link_area_experimental` baseline;
- engineering-vs-link-area comparison for 48^3 box and 48^3 procedural squid_proxy;
- existing engineering moving_boundary regression;
- artifact manifest with `large_file_count = 0`;
- `pytest -q`: 123 passed;
- Git pre-push hook: 123 passed;
- `external/taichi_LBM3D` unchanged.

Step 18 documents that:

- the default moving_boundary reaction transfer remains engineering;
- the moving bounce-back formula is unchanged;
- `MovingBoundaryFSICoupler3D` is unchanged;
- the experimental transfer uses a bounded global `area_scale` from Step 17 link-area proxy accounting;
- the experimental transfer writes to `solid.grid_f_ext` and does not write to `lbm.cell_force`;
- this is not final strict momentum-conserving sharp-interface FSI;
- squid_proxy is procedural and not real squid validation.

Step 19 must preserve all of the above.

## 2. Step 19 Objective

Validate the Step 18 opt-in `link_area_experimental` reaction transfer over longer 48^3 windows and conservative 64^3 feasibility cases.

Step 19 moves from:

```text
short-window experimental link-area transfer evidence
```

to:

```text
longer-window 48^3 evidence + 64^3 feasibility evidence + direct engineering-vs-link-area comparisons
```

Step 19 must answer this question:

```text
Does the Step 18 experimental transfer remain finite, bounded, and stable over longer 48^3 windows and a conservative 64^3 feasibility check?
```

Step 19 must not introduce new FSI physics or a new transfer formula.

Step 19 must:

1. Run a 48^3 box `link_area_experimental` long-run.
2. Run a 48^3 procedural squid_proxy `link_area_experimental` long-run.
3. Run a 64^3 box `link_area_experimental` feasibility baseline.
4. Compare 64^3 box engineering vs `link_area_experimental`.
5. Compare 48^3 box and 48^3 procedural squid_proxy engineering vs `link_area_experimental` over longer windows than Step 18.
6. Record `area_scale` and `raw_area_scale` drift over time for experimental rows.
7. Preserve default engineering moving_boundary behavior.
8. Preserve Step 18 comparison evidence and add Step 18 regression.
9. Add Step 19 report, docs, logs, outputs, artifact manifest, and contract test.
10. Commit and push all Step 19 artifacts to GitHub `origin/main`.

## 3. Hard Boundaries

Do not implement or change:

- no change to the Step 8 moving bounce-back formula;
- no change to `LBMFluid3D.step()`;
- no change to `LBMFluid3D.step_moving_bounceback()` state update;
- no change to `LinkAreaMovingBoundaryCoupler3D` reaction transfer formula;
- no change to `MovingBoundaryFSICoupler3D`;
- no change to `PenaltyFSICoupler3D`;
- no new reaction transfer formula;
- no new production FSI mode;
- no replacement of the existing engineering moving_boundary path;
- no change to default `reaction_transfer_mode = "engineering"`;
- no implicit default use of `link_area_experimental`;
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

- long-run and feasibility configs;
- long-run and comparison baseline scripts;
- per-run `link_area_timeseries.csv`;
- `area_scale` drift diagnostics;
- long-run summary utilities;
- docs, reports, logs, outputs, and contract tests.

## 4. Required Design

Keep the Step 18 architecture:

```text
coupling_mode = "moving_boundary"
reaction_transfer_mode = "engineering" | "link_area_experimental"
```

`link_area_experimental` must remain opt-in.

Do not add:

```text
coupling_mode = "moving_boundary_link_area_experimental"
```

Do not alter the Step 18 formula:

```text
area_scale = clip(
    |area_weighted_solid_force_x| / (|bb_net_solid_force_x| + eps),
    area_scale_min,
    area_scale_max
)

particle_force =
    sampled_hydro_lbm
    * force_density_scale_lbm_to_norm
    * particle_volume
    * reaction_scale
    * area_scale
```

Step 19 may read `driver.link_area_coupler.get_stats()` after each recorded step to build timeseries diagnostics.

Do not modify common `FSIDriver3D.DIAGNOSTIC_FIELDS` unless there is no reasonable alternative. Prefer separate Step 19 files:

```text
link_area_timeseries.csv
link_area_timeseries.npz
long_run_summary.json
```

## 5. Required Diagnostics

Every Step 19 long-run or comparison row involving `link_area_experimental` must record:

```text
area_scale_initial
area_scale_final
area_scale_min
area_scale_max
area_scale_mean
raw_area_scale_initial
raw_area_scale_final
raw_area_scale_min
raw_area_scale_max
area_proxy_total_initial
area_proxy_total_final
area_proxy_total_min
area_proxy_total_max
```

Every Step 19 summary row must also record:

```text
case
transfer_mode
reaction_transfer_mode
geometry_type
n_grid
n_particles
n_lbm_steps
mpm_substeps_per_lbm_step
completed_lbm_steps
total_mpm_substeps
rho_min_global
rho_max_global
rho_span_global
lbm_max_v_global
mpm_min_J_global
mpm_max_speed_global
solid_vx_initial
solid_vx_final
solid_vx_drift
projection_zone_ux_initial
projection_zone_ux_final
bb_link_count_min
bb_link_count_max
active_reaction_particle_count_min
active_reaction_particle_count_max
cell_force_max_norm
hydro_force_max_norm
max_grid_reaction_norm
stable
well_behaved
elapsed_seconds
notes
```

For engineering rows, `area_scale_*` may be `1.0` and `raw_area_scale_*` may be `1.0`.

For `link_area_experimental` rows, `area_scale` must be finite and bounded:

```text
0.25 <= area_scale_min <= area_scale_max <= 2.0
```

The report must also state whether any `area_scale` row sits continuously on the min or max bound. Bound contact is not automatically failure, but it must be disclosed.

## 6. Required Config Files

Create:

```text
configs/step19_long_box_48_link_area.json
configs/step19_long_squid_proxy_48_link_area.json
configs/step19_feasibility_64_link_area_box.json
configs/step19_compare_64_engineering_vs_link_area.json
configs/step19_compare_48_long_engineering_vs_link_area.json
```

All Step 19 scale configs must disable heavy outputs:

```json
{
  "write_vtk": false,
  "write_particles": false
}
```

All Step 19 `link_area_experimental` configs must include:

```json
{
  "coupling_mode": "moving_boundary",
  "reaction_transfer_mode": "link_area_experimental",
  "link_area_policy": "inverse_length",
  "link_area_scale_min": 0.25,
  "link_area_scale_max": 2.0
}
```

### 6.1 `configs/step19_long_box_48_link_area.json`

Required settings:

```json
{
  "coupling_mode": "moving_boundary",
  "reaction_transfer_mode": "link_area_experimental",
  "link_area_policy": "inverse_length",
  "geometry_type": "box",
  "n_grid": 48,
  "n_particles": 13824,
  "n_lbm_steps": 50,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.00001,
  "link_area_scale_min": 0.25,
  "link_area_scale_max": 2.0,
  "output_interval": 10,
  "write_vtk": false,
  "write_particles": false
}
```

### 6.2 `configs/step19_long_squid_proxy_48_link_area.json`

Required settings:

```json
{
  "coupling_mode": "moving_boundary",
  "reaction_transfer_mode": "link_area_experimental",
  "link_area_policy": "inverse_length",
  "geometry_type": "squid_proxy",
  "geometry_config_path": "configs/step13_squid_proxy_geometry.json",
  "n_grid": 48,
  "n_particles": 4096,
  "n_lbm_steps": 30,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "mb_reaction_scale": 0.5,
  "mb_force_cap_norm": 0.000025,
  "link_area_scale_min": 0.25,
  "link_area_scale_max": 2.0,
  "output_interval": 10,
  "write_vtk": false,
  "write_particles": false
}
```

### 6.3 `configs/step19_feasibility_64_link_area_box.json`

Required settings:

```json
{
  "coupling_mode": "moving_boundary",
  "reaction_transfer_mode": "link_area_experimental",
  "link_area_policy": "inverse_length",
  "geometry_type": "box",
  "n_grid": 64,
  "n_particles": 32768,
  "n_lbm_steps": 5,
  "mpm_substeps_per_lbm_step": 5,
  "target_u_lbm": [0.0025, 0.0, 0.0],
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.000005,
  "link_area_scale_min": 0.25,
  "link_area_scale_max": 2.0,
  "output_interval": 5,
  "write_vtk": false,
  "write_particles": false
}
```

### 6.4 `configs/step19_compare_64_engineering_vs_link_area.json`

This config may be a shared base used by the runner to produce both rows.

Required base settings:

```json
{
  "coupling_mode": "moving_boundary",
  "reaction_transfer_mode": "engineering",
  "link_area_policy": "inverse_length",
  "geometry_type": "box",
  "n_grid": 64,
  "n_particles": 32768,
  "n_lbm_steps": 5,
  "mpm_substeps_per_lbm_step": 5,
  "target_u_lbm": [0.0025, 0.0, 0.0],
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.000005,
  "link_area_scale_min": 0.25,
  "link_area_scale_max": 2.0,
  "output_interval": 5,
  "write_vtk": false,
  "write_particles": false
}
```

The runner must run:

```text
engineering
link_area_experimental
```

### 6.5 `configs/step19_compare_48_long_engineering_vs_link_area.json`

This config may be a JSON object with `box_48` and `squid_proxy_48` sections, or it may be a base config plus runner-side overrides. The contract requires the effective runs to be:

```text
box_48 engineering: at least 30 LBM steps / 300 MPM substeps
box_48 link_area_experimental: at least 30 LBM steps / 300 MPM substeps
squid_proxy_48 engineering: at least 20 LBM steps / 200 MPM substeps
squid_proxy_48 link_area_experimental: at least 20 LBM steps / 200 MPM substeps
```

All rows must use:

```text
n_grid = 48
write_vtk = false
write_particles = false
```

## 7. Required Baseline Scripts

Create:

```text
baseline_tests/step19_common.py
baseline_tests/run_step19_long_box_48_link_area.py
baseline_tests/run_step19_long_squid_proxy_48_link_area.py
baseline_tests/run_step19_feasibility_64_link_area.py
baseline_tests/run_step19_compare_64_engineering_vs_link_area.py
baseline_tests/run_step19_compare_48_long_engineering_vs_link_area.py
baseline_tests/run_step19_regression_step18.py
baseline_tests/run_step19_long_run_summary.py
baseline_tests/run_step19_artifact_manifest.py
```

All scripts must:

- use deterministic config files;
- write under `outputs/step19_*`;
- save UTF-8 logs under `logs/step19_*.log` when run through acceptance commands;
- raise on NaN or Inf;
- raise on missing output files;
- raise when acceptance thresholds fail;
- print a final `[OK] ... finished` marker.

## 8. `baseline_tests/step19_common.py`

Implement common helpers rather than duplicating long-run logic in every runner.

Required helpers:

```python
def run_driver_with_link_area_timeseries(config, out_dir):
    ...

def collect_link_area_row(driver, step):
    ...

def summarize_link_area_timeseries(rows):
    ...

def summarize_step19_case(result, case, transfer_mode, notes=""):
    ...

def assert_step19_stable(summary, require_link_area=False):
    ...

def write_step19_summary_json(summary, path):
    ...

def write_step19_rows_csv_npz(rows, csv_path, npz_path, fieldnames):
    ...
```

`run_driver_with_link_area_timeseries()` should manually initialize and step `FSIDriver3D` so it can collect extra `link_area_coupler.get_stats()` values at step 0 and every configured output interval. It must still save the normal driver outputs:

```text
diagnostics_timeseries.csv
diagnostics_timeseries.npz
driver_config.json
```

It must also save:

```text
link_area_timeseries.csv
link_area_timeseries.npz
```

For engineering runs, the helper should write area-scale columns with stable comparison defaults:

```text
area_scale = 1.0
raw_area_scale = 1.0
area_proxy_total = 0.0
```

For `link_area_experimental` runs, the helper must read from:

```python
driver.link_area_coupler.get_stats()
```

Do not modify `FSIDriver3D.DIAGNOSTIC_FIELDS` only to satisfy Step 19 timeseries needs.

## 9. Baseline 1: 48^3 Box Link-Area Long-Run

Script:

```text
baseline_tests/run_step19_long_box_48_link_area.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_long_box_48_link_area.py
```

Output:

```text
outputs/step19_long_box_48_link_area/diagnostics_timeseries.csv
outputs/step19_long_box_48_link_area/diagnostics_timeseries.npz
outputs/step19_long_box_48_link_area/link_area_timeseries.csv
outputs/step19_long_box_48_link_area/link_area_timeseries.npz
outputs/step19_long_box_48_link_area/long_run_summary.json
logs/step19_long_box_48_link_area.log
```

Acceptance:

```text
reaction_transfer_mode == link_area_experimental
n_grid == 48
completed_lbm_steps >= 50
total_mpm_substeps >= 500
rho_min_global > 0.95
rho_max_global < 1.05
lbm_max_v_global < 0.1
mpm_min_J_global > 0
mpm_max_speed_global < 10
bb_link_count_min > 0
active_reaction_particle_count_min > 0
cell_force_max_norm == 0
hydro_force_max_norm > 0
area_scale finite
0.25 <= area_scale_min <= area_scale_max <= 2.0
no NaN
no Inf
```

Recommended `well_behaved` criteria:

```text
rho_min_global > 0.98
rho_max_global < 1.02
mpm_min_J_global > 0.90
```

Final marker:

```text
[OK] Step 19 48^3 box link-area long-run finished
```

## 10. Baseline 2: 48^3 Procedural Squid Proxy Link-Area Long-Run

Script:

```text
baseline_tests/run_step19_long_squid_proxy_48_link_area.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_long_squid_proxy_48_link_area.py
```

Output:

```text
outputs/step19_long_squid_proxy_48_link_area/diagnostics_timeseries.csv
outputs/step19_long_squid_proxy_48_link_area/diagnostics_timeseries.npz
outputs/step19_long_squid_proxy_48_link_area/link_area_timeseries.csv
outputs/step19_long_squid_proxy_48_link_area/link_area_timeseries.npz
outputs/step19_long_squid_proxy_48_link_area/long_run_summary.json
logs/step19_long_squid_proxy_48_link_area.log
```

Acceptance:

```text
reaction_transfer_mode == link_area_experimental
geometry_type == squid_proxy
n_grid == 48
completed_lbm_steps >= 30
total_mpm_substeps >= 300
rho_min_global > 0.95
rho_max_global < 1.05
lbm_max_v_global < 0.1
mpm_min_J_global > 0
mpm_max_speed_global < 10
bb_link_count_min > 0
active_reaction_particle_count_min > 0
cell_force_max_norm == 0
area_scale finite and bounded
no NaN
no Inf
```

The report and docs must say:

```text
squid_proxy is procedural and not real squid validation.
```

Final marker:

```text
[OK] Step 19 48^3 squid_proxy link-area long-run finished
```

## 11. Baseline 3: 64^3 Box Link-Area Feasibility

Script:

```text
baseline_tests/run_step19_feasibility_64_link_area.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_feasibility_64_link_area.py
```

Output:

```text
outputs/step19_feasibility_64_link_area/box_64_link_area_results.csv
outputs/step19_feasibility_64_link_area/box_64_link_area_results.npz
outputs/step19_feasibility_64_link_area/link_area_timeseries.csv
outputs/step19_feasibility_64_link_area/link_area_timeseries.npz
outputs/step19_feasibility_64_link_area/long_run_summary.json
logs/step19_feasibility_64_link_area.log
```

Acceptance:

```text
reaction_transfer_mode == link_area_experimental
n_grid == 64
n_particles == 32768
completed_lbm_steps >= 5
total_mpm_substeps >= 25
stable == True
rho_min_global > 0.95
rho_max_global < 1.05
lbm_max_v_global < 0.1
mpm_min_J_global > 0
mpm_max_speed_global < 10
bb_link_count_min > 0
active_reaction_particle_count_min > 0
area_scale finite and bounded
cell_force_max_norm == 0
```

Final marker:

```text
[OK] Step 19 64^3 link-area feasibility finished
```

## 12. Baseline 4: 64^3 Engineering vs Link-Area Comparison

Script:

```text
baseline_tests/run_step19_compare_64_engineering_vs_link_area.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_compare_64_engineering_vs_link_area.py
```

Rows:

```text
box_64 / engineering
box_64 / link_area_experimental
```

Output:

```text
outputs/step19_compare_64_engineering_vs_link_area/comparison_64.csv
outputs/step19_compare_64_engineering_vs_link_area/comparison_64.npz
logs/step19_compare_64_engineering_vs_link_area.log
```

Required fields:

```text
case
transfer_mode
stable
n_grid
n_particles
completed_lbm_steps
total_mpm_substeps
rho_min_global
rho_max_global
lbm_max_v_global
mpm_min_J_global
mpm_max_speed_global
projection_zone_ux_final
solid_vx_final
area_scale_final
area_scale_min
area_scale_max
bb_link_count_min
active_reaction_particle_count_min
cell_force_max_norm
hydro_force_max_norm
```

Acceptance:

```text
engineering row stable
link_area_experimental row stable
both rows have n_grid == 64
both rows have completed_lbm_steps >= 5
both rows have cell_force_max_norm == 0
both rows have bb_link_count_min > 0
link_area row has finite bounded area_scale
rho / velocity / MPM thresholds pass
```

Do not require the link-area row to outperform engineering.

Final marker:

```text
[OK] Step 19 64^3 engineering vs link-area comparison finished
```

## 13. Baseline 5: 48^3 Long Engineering vs Link-Area Comparison

Script:

```text
baseline_tests/run_step19_compare_48_long_engineering_vs_link_area.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_compare_48_long_engineering_vs_link_area.py
```

Rows:

```text
box_48 / engineering
box_48 / link_area_experimental
squid_proxy_48 / engineering
squid_proxy_48 / link_area_experimental
```

Minimum effective lengths:

```text
box_48 rows: completed_lbm_steps >= 30 and total_mpm_substeps >= 300
squid_proxy_48 rows: completed_lbm_steps >= 20 and total_mpm_substeps >= 200
```

Output:

```text
outputs/step19_compare_48_long_engineering_vs_link_area/comparison_48_long.csv
outputs/step19_compare_48_long_engineering_vs_link_area/comparison_48_long.npz
logs/step19_compare_48_long_engineering_vs_link_area.log
```

Acceptance:

```text
all four rows stable
box engineering row stable
box link_area_experimental row stable
squid_proxy engineering row stable
squid_proxy link_area_experimental row stable
link_area rows have finite bounded area_scale
engineering rows keep area_scale_final == 1.0
cell_force_max_norm == 0 for all moving_boundary rows
rho / velocity / MPM thresholds pass
```

Do not require experimental rows to outperform engineering rows.

Final marker:

```text
[OK] Step 19 48^3 long engineering vs link-area comparison finished
```

## 14. Baseline 6: Step 18 Regression

Script:

```text
baseline_tests/run_step19_regression_step18.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_regression_step18.py
```

Purpose:

```text
prove Step 19 did not break Step 18's short experimental transfer behavior or the engineering default
```

Required rows:

```text
step18_sanity_regression
step18_box_48_experimental_regression
engineering_default_regression
```

Output:

```text
outputs/step19_regression_step18/regression_results.csv
outputs/step19_regression_step18/regression_results.npz
logs/step19_regression_step18.log
```

Acceptance:

```text
all rows stable
default reaction_transfer_mode == engineering
experimental rows have finite bounded area_scale
cell_force_max_norm == 0
rho / velocity / MPM thresholds pass
```

Final marker:

```text
[OK] Step 19 Step 18 regression finished
```

## 15. Baseline 7: Long-Run Summary

Script:

```text
baseline_tests/run_step19_long_run_summary.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_long_run_summary.py
```

Output:

```text
outputs/step19_long_run_summary/step19_summary.csv
outputs/step19_long_run_summary/step19_summary.json
outputs/step19_long_run_summary/step19_summary.npz
logs/step19_long_run_summary.log
```

Required summary cases:

```text
box_48_link_area_long
squid_proxy_48_link_area_long
box_64_link_area_feasibility
engineering_vs_link_area_64
engineering_vs_link_area_48
step18_regression
```

Acceptance:

```text
summary files exist
all required cases present
all required stable rows marked stable
area_scale ranges recorded
artifact paths recorded
```

Final marker:

```text
[OK] Step 19 long-run summary finished
```

## 16. Baseline 8: Artifact Manifest

Script:

```text
baseline_tests/run_step19_artifact_manifest.py
```

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_artifact_manifest.py
```

Output:

```text
outputs/step19_artifact_manifest/artifact_manifest.csv
outputs/step19_artifact_manifest/artifact_summary.json
logs/step19_artifact_manifest.log
```

Acceptance:

```text
file_count recorded
total_size_bytes recorded
total_size_mb recorded
large_file_count == 0
Step 19 scale configs have write_vtk == false
Step 19 scale configs have write_particles == false
```

Final marker:

```text
[OK] Step 19 artifact manifest finished
```

## 17. Required Documentation

Create:

```text
docs/18_link_area_long_run.md
STEP19_LINK_AREA_LONG_RUN_REPORT.md
```

Update:

```text
README.md
docs/08_roadmap.md
docs/17_experimental_link_area_transfer.md
docs/16_link_area_momentum_accounting.md
docs/10_performance_memory.md
```

Required phrases in docs/report:

```text
Step 19 validates the opt-in link_area_experimental transfer over longer windows and 64^3 feasibility.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
LinkAreaMovingBoundaryCoupler3D formula is unchanged.
MovingBoundaryFSICoupler3D is unchanged.
The link-area transfer remains experimental and uses a bounded global area_scale.
This is not final strict momentum-conserving sharp-interface FSI.
squid_proxy is procedural and not real squid validation.
```

Forbidden overclaims:

```text
strict momentum-conserving FSI is complete
real squid simulation is validated
validated squid swimming
production-ready sharp-interface FSI
final local surface-area reconstruction
```

## 18. Step 19 Report Contract

`STEP19_LINK_AREA_LONG_RUN_REPORT.md` must contain:

```text
1. Goal
2. Files created and updated
3. Explicit non-goals
4. 48^3 box link-area long-run result
5. 48^3 procedural squid_proxy link-area long-run result
6. 64^3 link-area feasibility result
7. 64^3 engineering vs link-area comparison result
8. 48^3 long engineering vs link-area comparison result
9. Step 18 regression result
10. Long-run summary result
11. Artifact manifest summary
12. Verification commands
13. GitHub sync information
14. Acceptance checklist
15. Decision for Step 20
```

The report must include tables for:

```text
completed_lbm_steps
total_mpm_substeps
area_scale_initial
area_scale_final
area_scale_min
area_scale_max
rho_min_global
rho_max_global
lbm_max_v_global
mpm_min_J_global
cell_force_max_norm
stable
```

The report must explicitly state:

```text
The link-area transfer remains experimental.
Step 19 does not change the Step 18 transfer formula.
```

## 19. Required Contract Test

Create:

```text
tests/test_step19_link_area_long_run_contract.py
```

The contract test must avoid importing the full `src` package unless it also handles environments where optional runtime packages are unavailable. Prefer file/text and artifact checks.

The test must verify required files exist:

```python
required_paths = [
    "configs/step19_long_box_48_link_area.json",
    "configs/step19_long_squid_proxy_48_link_area.json",
    "configs/step19_feasibility_64_link_area_box.json",
    "configs/step19_compare_64_engineering_vs_link_area.json",
    "configs/step19_compare_48_long_engineering_vs_link_area.json",
    "baseline_tests/step19_common.py",
    "baseline_tests/run_step19_long_box_48_link_area.py",
    "baseline_tests/run_step19_long_squid_proxy_48_link_area.py",
    "baseline_tests/run_step19_feasibility_64_link_area.py",
    "baseline_tests/run_step19_compare_64_engineering_vs_link_area.py",
    "baseline_tests/run_step19_compare_48_long_engineering_vs_link_area.py",
    "baseline_tests/run_step19_regression_step18.py",
    "baseline_tests/run_step19_long_run_summary.py",
    "baseline_tests/run_step19_artifact_manifest.py",
    "docs/18_link_area_long_run.md",
    "STEP19_LINK_AREA_LONG_RUN_REPORT.md",
]
```

The test must verify logs contain:

```text
[OK] Step 19 48^3 box link-area long-run finished
[OK] Step 19 48^3 squid_proxy link-area long-run finished
[OK] Step 19 64^3 link-area feasibility finished
[OK] Step 19 64^3 engineering vs link-area comparison finished
[OK] Step 19 48^3 long engineering vs link-area comparison finished
[OK] Step 19 Step 18 regression finished
[OK] Step 19 long-run summary finished
[OK] Step 19 artifact manifest finished
```

The test must validate JSON/CSV outputs:

```text
box_48 long summary:
  completed_lbm_steps >= 50
  total_mpm_substeps >= 500
  reaction_transfer_mode == link_area_experimental
  area_scale finite and bounded

squid_proxy_48 long summary:
  completed_lbm_steps >= 30
  total_mpm_substeps >= 300
  reaction_transfer_mode == link_area_experimental
  area_scale finite and bounded

64 link-area feasibility:
  n_grid == 64
  completed_lbm_steps >= 5
  stable == True

64 comparison:
  engineering and link_area_experimental rows present
  all rows stable

48 long comparison:
  box_48 engineering/link_area rows present
  squid_proxy_48 engineering/link_area rows present
  all rows stable

artifact manifest:
  large_file_count == 0

logs:
  logs/step19_pytest.log exists
```

The test must verify docs/report avoid forbidden overclaims.

## 20. Required Execution Order

Follow this sequence:

1. Re-read this goal file and inspect current `main`.
2. Confirm `external/taichi_LBM3D` is clean.
3. Add `tests/test_step19_link_area_long_run_contract.py` first and run it to confirm RED.
4. Add Step 19 configs.
5. Add `baseline_tests/step19_common.py`.
6. Add Step 19 baseline runners.
7. Run 48^3 box link-area long-run.
8. Run 48^3 procedural squid_proxy link-area long-run.
9. Run 64^3 link-area feasibility.
10. Run 64^3 engineering-vs-link-area comparison.
11. Run 48^3 long engineering-vs-link-area comparison.
12. Run Step 18 regression.
13. Run long-run summary.
14. Run artifact manifest.
15. Update docs and `STEP19_LINK_AREA_LONG_RUN_REPORT.md`.
16. Run full `pytest -q` and save `logs/step19_pytest.log`.
17. Regenerate artifact manifest after pytest log exists.
18. Run final `pytest -q`.
19. Run `git diff --check`.
20. Confirm `git status --short external/taichi_LBM3D` is empty.
21. Commit all Step 19 code/docs/logs/outputs/report.
22. Push to GitHub `origin/main`.
23. Report commit hash, branch, verification commands, and key baseline numbers.

## 21. Required Commands

Use this interpreter unless unavailable:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore ...
```

Run baselines:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_long_box_48_link_area.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_long_squid_proxy_48_link_area.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_feasibility_64_link_area.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_compare_64_engineering_vs_link_area.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_compare_48_long_engineering_vs_link_area.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_regression_step18.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_long_run_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_artifact_manifest.py
```

Save logs with UTF-8 encoding. In Windows PowerShell, prefer:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_long_box_48_link_area.py 2>&1 | Out-File -FilePath logs\step19_long_box_48_link_area.log -Encoding utf8
```

Run pytest and save the required log:

```powershell
Set-Content -Path logs\step19_pytest.log -Value 'pytest started' -Encoding utf8
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q 2>&1 | Out-File -FilePath logs\step19_pytest.log -Encoding utf8
```

Also ensure Git pre-push hook compatibility. If the hook uses a different Python and fails due to test import environment, fix the contract test so it can run without importing optional runtime packages.

## 22. Hard Acceptance Checklist

All items must be true before Step 19 is complete:

```text
[ ] main is on the Step 19 final commit
[ ] configs/step19_long_box_48_link_area.json exists
[ ] configs/step19_long_squid_proxy_48_link_area.json exists
[ ] configs/step19_feasibility_64_link_area_box.json exists
[ ] configs/step19_compare_64_engineering_vs_link_area.json exists
[ ] configs/step19_compare_48_long_engineering_vs_link_area.json exists
[ ] baseline_tests/step19_common.py exists
[ ] 48^3 box link_area_experimental long-run completes
[ ] 48^3 box long-run completed_lbm_steps >= 50
[ ] 48^3 box long-run total_mpm_substeps >= 500
[ ] 48^3 squid_proxy link_area_experimental long-run completes
[ ] 48^3 squid_proxy long-run completed_lbm_steps >= 30
[ ] 48^3 squid_proxy long-run total_mpm_substeps >= 300
[ ] 64^3 link_area_experimental feasibility completes
[ ] 64^3 link-area feasibility completed_lbm_steps >= 5
[ ] 64^3 engineering vs link-area comparison completes
[ ] 48^3 long engineering vs link-area comparison completes
[ ] Step 18 regression completes
[ ] long-run summary completes
[ ] area_scale is finite for all experimental rows
[ ] area_scale stays within configured bounds
[ ] rho_min_global > 0.95 for required stable rows
[ ] rho_max_global < 1.05 for required stable rows
[ ] lbm_max_v_global < 0.1 for required stable rows
[ ] mpm_min_J_global > 0 for required stable rows
[ ] mpm_max_speed_global < 10 for required stable rows
[ ] cell_force_max_norm == 0 for moving_boundary rows
[ ] bb_link_count_min > 0 for moving_boundary rows
[ ] active_reaction_particle_count_min > 0 for required experimental rows
[ ] engineering transfer remains available
[ ] default reaction_transfer_mode remains engineering
[ ] link_area_experimental remains opt-in
[ ] no moving bounce-back formula changes
[ ] no LinkAreaMovingBoundaryCoupler3D formula changes
[ ] no MovingBoundaryFSICoupler3D changes
[ ] no PenaltyFSICoupler3D changes
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no real squid validation claims
[ ] no squid swimming validation claims
[ ] no mesh import
[ ] no sparse storage implementation
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] artifact large_file_count == 0
[ ] docs/18_link_area_long_run.md exists
[ ] STEP19_LINK_AREA_LONG_RUN_REPORT.md complete
[ ] tests/test_step19_link_area_long_run_contract.py exists
[ ] logs/step19_pytest.log exists
[ ] pytest -q passes
[ ] Git pre-push pytest hook passes
[ ] git diff --check passes
[ ] Step 19 artifacts are committed
[ ] Step 19 artifacts are pushed to GitHub origin/main
```

## 23. Failure Handling

If a long-run becomes unstable:

1. Do not silently reduce the acceptance target.
2. First inspect whether instability comes from `area_scale` hitting bounds.
3. Then reduce `mb_reaction_scale`.
4. Then reduce `mb_force_cap_norm`.
5. Then narrow `link_area_scale_min` / `link_area_scale_max`, for example to `[0.5, 1.5]`.
6. Only reduce step counts if the report clearly marks the run as a shorter smoke baseline and Step 19 remains incomplete.
7. Preserve engineering comparison rows.
8. Document every deviation in `STEP19_LINK_AREA_LONG_RUN_REPORT.md`.

If the 48^3 box long-run passes but 48^3 squid_proxy fails:

```text
Step 19 is not complete.
```

If 48^3 runs pass but 64^3 feasibility fails:

```text
Step 19 is not complete.
```

Either stabilize the 64^3 feasibility settings within the hard boundaries or mark the goal blocked after the blocked-audit threshold is met.

If `external/taichi_LBM3D` is modified:

```text
Step 19 is not complete.
```

Revert only unintended external edits made by this task. Never revert unrelated user changes without permission.

## 24. Completion Definition

Step 19 is complete only when:

1. All required config files exist.
2. All required baseline scripts exist.
3. All required Step 19 baselines pass.
4. `link_area_experimental` long-run and 64^3 feasibility evidence is saved.
5. Engineering comparison rows are saved.
6. Step 18 regression evidence is saved.
7. `area_scale` timeseries and summaries are saved.
8. `pytest -q` passes.
9. Git pre-push pytest hook passes.
10. `logs/step19_pytest.log` exists and records the passing pytest result.
11. Artifact manifest exists and reports `large_file_count == 0`.
12. Documentation and report are complete and avoid forbidden overclaims.
13. `external/taichi_LBM3D` remains unchanged.
14. Step 19 code/docs/logs/outputs/report are committed.
15. The commit is pushed to GitHub `origin/main`.
16. The final response reports the commit hash and remote branch.

## 25. Decision After Step 19

If Step 19 passes, the recommended Step 20 is:

```text
Step 20: Mesh/voxel geometry import pipeline
```

Reason: after Step 19, the project will have:

```text
engineering moving_boundary long-run evidence
link_area_experimental short-run evidence
link_area_experimental long-run evidence
64^3 link_area_experimental feasibility
direct engineering-vs-link-area comparison
```

The next bottleneck should be geometry ingestion for more realistic input, not claiming final strict momentum-conserving FSI.
