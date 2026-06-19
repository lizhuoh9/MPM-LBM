# Step 16 Goal: Long-Run Validation and 64^3 Moving-Boundary Feasibility

## Paste-Ready `/goal`

```text
/goal
In D:\working\squid robot\LBM\MPM-LBM, execute Step 16: Long-run validation and 64^3 moving-boundary feasibility. The only authoritative execution contract is D:\working\squid robot\LBM\MPM-LBM\STEP16_LONG_RUN_VALIDATION_GOAL.md.

Goal: use the Step 15 calibrated moving_boundary settings to run longer 48^3 stability baselines and add a conservative 64^3 moving_boundary feasibility baseline, without adding new FSI physics. Produce long-run drift diagnostics, a 64^3 none/penalty/moving_boundary comparison, controlled artifacts, docs, report, pytest contract, and GitHub sync.

Hard boundaries: do not implement new FSI physics, do not change the Step 8 moving bounce-back formula, do not change the Step 9 MovingBoundaryFSICoupler3D transfer formula, do not change the Step 15 accounting convention, do not make moving_boundary the default, do not implement two-phase flow, contact angle physics, real squid validation, squid actuation, swimming locomotion, mesh import, sparse storage, ReducedSquidFSI, strict final momentum-conserving sharp-interface FSI, production-readiness claims, or edits to external/taichi_LBM3D. Required artifacts, configs, baselines, diagnostics, pytest contract, acceptance checklist, failure handling, and completion definition are all defined in STEP16_LONG_RUN_VALIDATION_GOAL.md. Finish only after required Step 16 baselines pass, pytest passes, external/taichi_LBM3D remains unchanged, and code/docs/logs/outputs/report are pushed to GitHub.
```

## 1. Current Baseline

Step 15 is accepted and is the starting point.

Current Step 15 final commit:

```text
1c97887d78cc6dc8bcf622323185654460769f89
```

Step 15 validated:

```text
1. MomentumAccounting3D diagnostic-only accounting.
2. Calibration helpers for stable/well_behaved/recommended rows.
3. 32^3 reaction_scale sweep.
4. 48^3 force_cap_norm sweep.
5. 48^3 squid_proxy calibrated window.
6. calibrated-vs-original comparison.
7. recommended moving_boundary configs:
   - box 48^3: reaction_scale=1.0, force_cap_norm=0.00001
   - squid_proxy 48^3: reaction_scale=0.5, force_cap_norm=0.000025
8. pytest passed with 93 tests.
9. external/taichi_LBM3D remained unchanged.
```

Step 15 still does not mean:

```text
1. strict final momentum-conserving sharp-interface FSI
2. real squid validation
3. validated squid swimming
4. two-phase LBM
5. contact angle physics
6. sparse storage
7. production-ready solver behavior
```

## 2. Step 16 Objective

Step 16 combines Step 14 larger-grid validation with Step 15 calibrated moving_boundary settings.

The goal is to add:

```text
1. 48^3 box moving_boundary long-run validation.
2. 48^3 squid_proxy moving_boundary long-run validation.
3. 64^3 box moving_boundary feasibility.
4. 64^3 none / penalty / moving_boundary short comparison.
5. long-run drift diagnostics.
6. controlled artifact manifest.
7. docs, report, logs, outputs, and pytest contract.
```

Step 16 is not a new solver method. It is:

```text
longer validation
64^3 moving_boundary feasibility
mode comparison
diagnostics drift summary
artifact governance
```

Allowed language:

```text
long-run validation
64^3 moving_boundary feasibility
engineering stability baseline
calibrated moving_boundary settings
diagnostic drift summary
```

Forbidden overclaims:

```text
real squid simulation is validated
validated squid swimming
biomechanically accurate squid
anatomically accurate squid
strict momentum-conserving FSI is complete
production-ready solver
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

GPU is required for the required final baselines. If Taichi GPU initialization fails, record the exact error and do not silently downgrade a required final acceptance run to CPU.

## 4. Strict Non-Goals

Do not implement these in Step 16:

```text
1. No new FSI physics.
2. No new coupling mode.
3. No changes to lbm.step() default behavior.
4. No changes to lbm.step_moving_bounceback().
5. No changes to the Step 8 moving bounce-back formula.
6. No changes to the Step 9 MovingBoundaryFSICoupler3D transfer formula.
7. No changes to the Step 15 accounting convention.
8. No changes to PenaltyFSICoupler3D formulas.
9. No replacement or deletion of PenaltyFSICoupler3D.
10. No replacement or deletion of MovingBoundaryFSICoupler3D.
11. No making moving_boundary the default driver path.
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
22. No production-readiness claim.
23. No deletion or weakening of Step 10/12/13/14/15 regression artifacts.
```

Allowed in Step 16:

```text
1. New validation configs.
2. New baseline runner scripts.
3. New long-run diagnostics summaries.
4. New 64^3 comparison tables.
5. CSV/NPZ/JSON/log outputs.
6. Docs, tests, report, artifact manifest.
7. Non-physics helper functions under baseline_tests/step16_common.py.
```

Any solver-adjacent edits must be limited to diagnostics, orchestration, configuration, and reporting. Do not alter collision, streaming, forcing, bounce-back, constitutive model, P2G/G2P, projection math, coupling formulas, or reaction-transfer formulas.

## 5. Required Final Structure

Create:

```text
configs/
  step16_long_box_48_moving_boundary.json
  step16_long_squid_proxy_48_moving_boundary.json
  step16_feasibility_64_moving_boundary_box.json
  step16_compare_64_modes.json

baseline_tests/
  step16_common.py
  run_step16_long_box_48_moving_boundary.py
  run_step16_long_squid_proxy_48_moving_boundary.py
  run_step16_feasibility_64_moving_boundary.py
  run_step16_64_mode_comparison.py
  run_step16_long_run_summary.py
  run_step16_artifact_manifest.py

outputs/
  step16_long_box_48_moving_boundary/
  step16_long_squid_proxy_48_moving_boundary/
  step16_feasibility_64_moving_boundary/
  step16_64_mode_comparison/
  step16_long_run_summary/
  step16_artifact_manifest/

logs/
  step16_long_box_48_moving_boundary.log
  step16_long_squid_proxy_48_moving_boundary.log
  step16_feasibility_64_moving_boundary.log
  step16_64_mode_comparison.log
  step16_long_run_summary.log
  step16_artifact_manifest.log
  step16_pytest.log

docs/
  15_long_run_validation.md

tests/
  test_step16_long_run_validation_contract.py

STEP16_LONG_RUN_VALIDATION_REPORT.md
```

Update:

```text
README.md
docs/08_roadmap.md
docs/10_performance_memory.md
docs/13_larger_grid_validation.md
docs/14_moving_boundary_calibration.md
```

Do not delete Step 1-15 reports, logs, outputs, configs, docs, or tests.

## 6. Required Configs

### `configs/step16_long_box_48_moving_boundary.json`

Use the Step 15 recommended 48^3 box moving_boundary values.

Required values:

```json
{
  "coupling_mode": "moving_boundary",
  "geometry_type": "box",
  "n_grid": 48,
  "n_particles": 13824,
  "n_lbm_steps": 50,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.00001,
  "output_interval": 10,
  "write_vtk": false,
  "write_particles": false
}
```

### `configs/step16_long_squid_proxy_48_moving_boundary.json`

Use the Step 15 recommended 48^3 squid_proxy moving_boundary values.

Required values:

```json
{
  "coupling_mode": "moving_boundary",
  "geometry_type": "squid_proxy",
  "geometry_config_path": "configs/step13_squid_proxy_geometry.json",
  "n_grid": 48,
  "n_particles": 4096,
  "n_lbm_steps": 30,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "mb_reaction_scale": 0.5,
  "mb_force_cap_norm": 0.000025,
  "output_interval": 10,
  "write_vtk": false,
  "write_particles": false
}
```

The squid_proxy run is shorter than the box long-run because procedural proxy geometry costs more and remains a proxy, not real squid validation.

### `configs/step16_feasibility_64_moving_boundary_box.json`

Use conservative moving_boundary settings for first 64^3 moving_boundary feasibility.

Required values:

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

This is feasibility, not full 64^3 validation.

### `configs/step16_compare_64_modes.json`

Create a JSON matrix config for the 64^3 mode comparison.

Required values:

```json
{
  "modes": ["none", "penalty", "moving_boundary"],
  "n_grid": 64,
  "n_particles": 32768,
  "n_lbm_steps": 5,
  "mpm_substeps_per_lbm_step": 5,
  "target_u_lbm": [0.0025, 0.0, 0.0],
  "write_vtk": false,
  "write_particles": false
}
```

The comparison runner may internally map mode-specific force settings:

```text
none:
  coupling_mode = none

penalty:
  coupling_mode = penalty
  beta_lbm = 0.001
  penalty_force_cap_lbm = 0.0001

moving_boundary:
  coupling_mode = moving_boundary
  mb_reaction_scale = 1.0
  mb_force_cap_norm = 0.000005
```

## 7. Long-Run Drift Diagnostics

Create:

```text
baseline_tests/step16_common.py
```

Required helper functions:

```python
def summarize_driver_timeseries(csv_path) -> dict:
    ...

def assert_long_run_stable(summary: dict) -> None:
    ...

def run_driver_case(config, out_dir):
    ...

def write_summary_csv(rows, path):
    ...

def load_final_row(driver_out_dir):
    ...
```

Required long-run summary fields:

```text
case
mode
geometry_type
n_grid
n_particles
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
stable
well_behaved
elapsed_seconds
```

Stability criteria:

```text
rho_min_global > 0.95
rho_max_global < 1.05
lbm_max_v_global < 0.1
mpm_min_J_global > 0.0
mpm_max_speed_global < 10.0
no NaN
no Inf
```

Moving_boundary-specific criteria:

```text
bb_link_count_min > 0
active_reaction_particle_count_min > 0
cell_force_max_norm == 0
```

Optional well-behaved marker:

```text
well_behaved =
  stable
  rho_min_global > 0.98
  rho_max_global < 1.02
  mpm_min_J_global > 0.90
  mpm_max_speed_global < 1.0
```

Do not make `well_behaved` a hard acceptance requirement unless the goal is explicitly revised.

## 8. Baseline 1: 48^3 Box Moving-Boundary Long-Run

Create:

```text
baseline_tests/run_step16_long_box_48_moving_boundary.py
```

Purpose:

```text
Validate the Step 15 recommended 48^3 box moving_boundary config over a longer window than Step 14/15.
```

Required config:

```text
configs/step16_long_box_48_moving_boundary.json
```

Required outputs:

```text
outputs/step16_long_box_48_moving_boundary/diagnostics_timeseries.csv
outputs/step16_long_box_48_moving_boundary/diagnostics_timeseries.npz
outputs/step16_long_box_48_moving_boundary/long_run_summary.json
logs/step16_long_box_48_moving_boundary.log
```

Acceptance:

```text
completed_lbm_steps = 50
total_mpm_substeps = 500
rho_min_global > 0.95
rho_max_global < 1.05
lbm_max_v_global < 0.1
mpm_min_J_global > 0
mpm_max_speed_global < 10
bb_link_count_min > 0
active_reaction_particle_count_min > 0
cell_force_max_norm == 0
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 16 48^3 box moving_boundary long-run finished
```

## 9. Baseline 2: 48^3 Squid Proxy Moving-Boundary Long-Run

Create:

```text
baseline_tests/run_step16_long_squid_proxy_48_moving_boundary.py
```

Purpose:

```text
Validate the Step 15 recommended 48^3 procedural squid_proxy moving_boundary config over a longer window than Step 14/15.
```

Required config:

```text
configs/step16_long_squid_proxy_48_moving_boundary.json
```

Required outputs:

```text
outputs/step16_long_squid_proxy_48_moving_boundary/diagnostics_timeseries.csv
outputs/step16_long_squid_proxy_48_moving_boundary/diagnostics_timeseries.npz
outputs/step16_long_squid_proxy_48_moving_boundary/long_run_summary.json
logs/step16_long_squid_proxy_48_moving_boundary.log
```

Acceptance:

```text
completed_lbm_steps = 30
total_mpm_substeps = 300
rho_min_global > 0.95
rho_max_global < 1.05
lbm_max_v_global < 0.1
mpm_min_J_global > 0
mpm_max_speed_global < 10
bb_link_count_min > 0
active_reaction_particle_count_min > 0
cell_force_max_norm == 0
no NaN
no Inf
squid_proxy remains procedural and not real squid validation
```

Required log marker:

```text
[OK] Step 16 48^3 squid_proxy moving_boundary long-run finished
```

## 10. Baseline 3: 64^3 Box Moving-Boundary Feasibility

Create:

```text
baseline_tests/run_step16_feasibility_64_moving_boundary.py
```

Purpose:

```text
Add the first conservative 64^3 moving_boundary feasibility row. Step 14 only validated 64^3 none/penalty feasibility.
```

Required config:

```text
configs/step16_feasibility_64_moving_boundary_box.json
```

Required outputs:

```text
outputs/step16_feasibility_64_moving_boundary/box_64_moving_boundary_results.csv
outputs/step16_feasibility_64_moving_boundary/box_64_moving_boundary_results.npz
outputs/step16_feasibility_64_moving_boundary/long_run_summary.json
logs/step16_feasibility_64_moving_boundary.log
```

Acceptance:

```text
n_grid = 64
coupling_mode = moving_boundary
stable = True
completed_lbm_steps = 5
total_mpm_substeps = 25
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
bb_link_count > 0
active_reaction_particle_count > 0
cell_force_max_norm == 0
write_vtk = false
write_particles = false
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 16 64^3 moving_boundary feasibility finished
```

## 11. Baseline 4: 64^3 Mode Comparison

Create:

```text
baseline_tests/run_step16_64_mode_comparison.py
```

Purpose:

```text
Create a short 64^3 none / penalty / moving_boundary comparison table using conservative Step 16 settings.
```

Required modes:

```text
none
penalty
moving_boundary
```

Required outputs:

```text
outputs/step16_64_mode_comparison/mode_64_results.csv
outputs/step16_64_mode_comparison/mode_64_results.npz
logs/step16_64_mode_comparison.log
```

Required output fields:

```text
mode
stable
n_grid
n_particles
completed_lbm_steps
total_mpm_substeps
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
cell_force_max_norm
hydro_force_max_norm
bb_link_count
active_reaction_particle_count
elapsed_seconds
notes
```

Acceptance:

```text
all three modes are present
all three modes are stable
all rows have n_grid = 64
none row: cell_force_max_norm == 0 and bb_link_count == 0
penalty row: cell_force_max_norm > 0 and bb_link_count == 0
moving_boundary row: cell_force_max_norm == 0 and bb_link_count > 0
rho bounds satisfied
MPM bounds satisfied
no NaN
no Inf
```

Do not require:

```text
moving_boundary response > penalty response
penalty response > none response
```

This is a feasibility comparison, not a physical accuracy ordering test.

Required log marker:

```text
[OK] Step 16 64^3 mode comparison finished
```

## 12. Baseline 5: Long-Run Summary

Create:

```text
baseline_tests/run_step16_long_run_summary.py
```

Purpose:

```text
Aggregate all Step 16 validation rows into one summary table and JSON.
```

Required inputs:

```text
outputs/step16_long_box_48_moving_boundary/long_run_summary.json
outputs/step16_long_squid_proxy_48_moving_boundary/long_run_summary.json
outputs/step16_feasibility_64_moving_boundary/box_64_moving_boundary_results.csv
outputs/step16_64_mode_comparison/mode_64_results.csv
```

Required outputs:

```text
outputs/step16_long_run_summary/step16_summary.csv
outputs/step16_long_run_summary/step16_summary.json
logs/step16_long_run_summary.log
```

Acceptance:

```text
summary contains 48^3 box long-run row
summary contains 48^3 squid_proxy long-run row
summary contains 64^3 moving_boundary feasibility row
summary contains 64^3 none / penalty / moving_boundary comparison rows
all required rows stable
all numeric fields finite
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 16 long-run summary finished
```

## 13. Artifact Manifest

Create:

```text
baseline_tests/run_step16_artifact_manifest.py
```

Purpose:

```text
Ensure Step 16 long-run and 64^3 artifacts remain controlled.
```

Required outputs:

```text
outputs/step16_artifact_manifest/artifact_manifest.csv
outputs/step16_artifact_manifest/artifact_summary.json
logs/step16_artifact_manifest.log
```

Acceptance:

```text
manifest exists
summary exists
file_count > 0
total_size_bytes > 0
large_file_count >= 0
large_file_count and total_size_mb are reported in STEP16_LONG_RUN_VALIDATION_REPORT.md
required Step 16 configs have write_vtk=false
required Step 16 configs have write_particles=false
no NaN
no Inf
```

Preferred artifact policy:

```text
write_vtk = false
write_particles = false
large_file_count = 0
```

Required log marker:

```text
[OK] Step 16 artifact manifest finished
```

## 14. Documentation Updates

Create:

```text
docs/15_long_run_validation.md
```

Must include:

```text
Step 16 scope
explicit statement that Step 16 does not add new FSI physics
explicit statement that Step 16 does not change moving bounce-back formula
explicit statement that Step 16 does not change MovingBoundaryFSICoupler3D formulas
48^3 box moving_boundary long-run
48^3 squid_proxy moving_boundary long-run
64^3 moving_boundary feasibility
64^3 mode comparison
long-run drift metrics
limitations and non-goals
```

Must state:

```text
The 64^3 moving_boundary row is a feasibility baseline.
squid_proxy is procedural and not real squid validation.
Strict link-area momentum-conserving coupling remains future work.
```

Update `README.md`:

```text
Add a concise Step 16 note that calibrated moving_boundary settings now have longer 48^3 baselines and a conservative 64^3 moving_boundary feasibility row.
Do not claim production readiness or real squid validation.
```

Update `docs/08_roadmap.md`:

```text
Mark Step 16 as completed after acceptance.
Set Step 17 to strict link-area momentum accounting prototype.
State that future physics must preserve Step 10 mode matrix, Step 13 geometry contracts, Step 14 scale baselines, and Step 15 calibration contracts.
```

Update `docs/10_performance_memory.md`:

```text
Add Step 16 runtime and artifact notes.
Keep timing language as environment-specific regression data, not hardware-independent benchmark data.
```

Update `docs/13_larger_grid_validation.md`:

```text
Add note that Step 16 adds 64^3 moving_boundary feasibility.
Keep 64^3 moving_boundary framed as feasibility, not full validation.
```

Update `docs/14_moving_boundary_calibration.md`:

```text
Add note that Step 16 uses the Step 15 recommended configs for long-run validation.
```

## 15. Step 16 Report Contract

Create:

```text
STEP16_LONG_RUN_VALIDATION_REPORT.md
```

Required sections:

```markdown
# Step 16 Long-Run Validation Report

## 1. Goal
## 2. Files
## 3. Explicit Non-Goals
## 4. 48^3 Box Moving-Boundary Long-Run
## 5. 48^3 Squid Proxy Moving-Boundary Long-Run
## 6. 64^3 Moving-Boundary Feasibility
## 7. 64^3 Mode Comparison
## 8. Long-Run Summary
## 9. Artifact Manifest
## 10. Documentation Updates
## 11. Verification
## 12. GitHub Sync
## 13. Acceptance Checklist
## 14. Decision
```

The report must include:

```text
commands run
config files used
summary tables
long-run drift values
64^3 mode comparison table
artifact summary
pytest command/result
confirmation that external/taichi_LBM3D was unchanged
confirmation that no FSI physics changed
confirmation that squid_proxy is not real squid validation
final commit hash or a note that final hash is reported after commit creation
remote branch after push
```

Before final verification, checklist items may be unchecked. They must be checked only after baselines and pytest pass.

## 16. Pytest Contract

Create:

```text
tests/test_step16_long_run_validation_contract.py
```

The test must check required paths:

```python
required_paths = [
    "configs/step16_long_box_48_moving_boundary.json",
    "configs/step16_long_squid_proxy_48_moving_boundary.json",
    "configs/step16_feasibility_64_moving_boundary_box.json",
    "configs/step16_compare_64_modes.json",
    "baseline_tests/step16_common.py",
    "baseline_tests/run_step16_long_box_48_moving_boundary.py",
    "baseline_tests/run_step16_long_squid_proxy_48_moving_boundary.py",
    "baseline_tests/run_step16_feasibility_64_moving_boundary.py",
    "baseline_tests/run_step16_64_mode_comparison.py",
    "baseline_tests/run_step16_long_run_summary.py",
    "baseline_tests/run_step16_artifact_manifest.py",
    "logs/step16_long_box_48_moving_boundary.log",
    "logs/step16_long_squid_proxy_48_moving_boundary.log",
    "logs/step16_feasibility_64_moving_boundary.log",
    "logs/step16_64_mode_comparison.log",
    "logs/step16_long_run_summary.log",
    "logs/step16_artifact_manifest.log",
    "logs/step16_pytest.log",
    "outputs/step16_long_box_48_moving_boundary/long_run_summary.json",
    "outputs/step16_long_squid_proxy_48_moving_boundary/long_run_summary.json",
    "outputs/step16_feasibility_64_moving_boundary/box_64_moving_boundary_results.csv",
    "outputs/step16_64_mode_comparison/mode_64_results.csv",
    "outputs/step16_long_run_summary/step16_summary.csv",
    "outputs/step16_long_run_summary/step16_summary.json",
    "outputs/step16_artifact_manifest/artifact_summary.json",
    "docs/15_long_run_validation.md",
    "STEP16_LONG_RUN_VALIDATION_REPORT.md",
]
```

The test must check source keywords:

```text
summarize_driver_timeseries
assert_long_run_stable
rho_min_global
rho_max_global
bb_link_count_min
active_reaction_particle_count_min
64^3 moving_boundary feasibility
```

The test must check log success markers:

```text
[OK] Step 16 48^3 box moving_boundary long-run finished
[OK] Step 16 48^3 squid_proxy moving_boundary long-run finished
[OK] Step 16 64^3 moving_boundary feasibility finished
[OK] Step 16 64^3 mode comparison finished
[OK] Step 16 long-run summary finished
[OK] Step 16 artifact manifest finished
```

The test must parse CSV/JSON/NPZ outputs and verify:

```text
box long summary completed_lbm_steps >= 50
box long summary total_mpm_substeps >= 500
box long summary rho_min_global > 0.95
box long summary rho_max_global < 1.05
box long summary bb_link_count_min > 0
squid_proxy long summary completed_lbm_steps >= 30
squid_proxy long summary total_mpm_substeps >= 300
squid_proxy long summary rho bounds valid
64 moving_boundary row n_grid == 64
64 moving_boundary row stable == True
64 moving_boundary row bb_link_count > 0
64 moving_boundary row cell_force_max_norm == 0
64 mode comparison contains none / penalty / moving_boundary
64 mode comparison all required rows stable
none row cell_force_max_norm == 0
penalty row cell_force_max_norm > 0
moving_boundary row bb_link_count > 0
recommended scale configs have write_vtk == false
recommended scale configs have write_particles == false
artifact summary file_count > 0
artifact summary total_size_bytes > 0
```

The test must check documentation/report do not contain overclaim phrases:

```text
real squid simulation is validated
validated squid swimming
biomechanically accurate squid
anatomically accurate squid
production-ready solver
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
not production-ready
strict link-area momentum-conserving coupling remains future work
```

The test must check `STEP16_LONG_RUN_VALIDATION_REPORT.md` acceptance checklist items are marked `[x]`.

## 17. Required Execution Order

Follow this order:

```text
1. Confirm git status, branch, remote, README, roadmap, and Step 15 baseline.
2. Read STEP16_LONG_RUN_VALIDATION_GOAL.md.
3. Read README.md, docs/08_roadmap.md, docs/10_performance_memory.md, docs/13_larger_grid_validation.md, docs/14_moving_boundary_calibration.md, STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md, src/fsi_driver.py, src/fsi_config.py, src/diagnostics.py, src/momentum_accounting.py, src/calibration.py.
4. Add tests/test_step16_long_run_validation_contract.py first.
5. Run pytest and confirm RED because Step 16 artifacts are missing.
6. Add Step 16 configs.
7. Implement baseline_tests/step16_common.py.
8. Add and run run_step16_long_box_48_moving_boundary.py, saving log.
9. Add and run run_step16_long_squid_proxy_48_moving_boundary.py, saving log.
10. Add and run run_step16_feasibility_64_moving_boundary.py, saving log.
11. Add and run run_step16_64_mode_comparison.py, saving log.
12. Add and run run_step16_long_run_summary.py, saving log.
13. Add and run run_step16_artifact_manifest.py, saving log.
14. Add docs/15_long_run_validation.md.
15. Update README.md, docs/08_roadmap.md, docs/10_performance_memory.md, docs/13_larger_grid_validation.md, docs/14_moving_boundary_calibration.md.
16. Add STEP16_LONG_RUN_VALIDATION_REPORT.md with unchecked checklist.
17. Run pytest -q.
18. Fix only Step 16 issues.
19. Save final pytest log as logs/step16_pytest.log.
20. Confirm src solver physics behavior is unchanged except diagnostics/config/orchestration additions.
21. Confirm external/taichi_LBM3D is unchanged.
22. Update STEP16_LONG_RUN_VALIDATION_REPORT.md checklist to checked.
23. Run final pytest -q.
24. Run git diff --check and git diff --cached --check.
25. Commit Step 16 artifacts.
26. Push to GitHub.
27. Verify local HEAD equals origin/main.
```

Do not report a short probe as Step 16 acceptance. Step 16 acceptance requires all required baselines, docs, report, pytest, artifact manifest, and GitHub push.

## 18. Verification Commands

Primary:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Baseline commands:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step16_long_box_48_moving_boundary.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step16_long_squid_proxy_48_moving_boundary.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step16_feasibility_64_moving_boundary.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step16_64_mode_comparison.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step16_long_run_summary.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step16_artifact_manifest.py
```

Log-saving form:

```powershell
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step16_long_box_48_moving_boundary.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step16_long_box_48_moving_boundary.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step16_long_squid_proxy_48_moving_boundary.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step16_long_squid_proxy_48_moving_boundary.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step16_feasibility_64_moving_boundary.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step16_feasibility_64_moving_boundary.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step16_64_mode_comparison.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step16_64_mode_comparison.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step16_long_run_summary.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step16_long_run_summary.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step16_artifact_manifest.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step16_artifact_manifest.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' -m pytest -q 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step16_pytest.log; $out; if ($code -ne 0) { exit $code }
```

Git hygiene:

```powershell
git status --short --branch
git status --short external
git diff --check
git diff --cached --check
```

## 19. Hard Acceptance Checklist

All must be true before Step 16 is complete:

```text
[ ] main is on the Step 16 final commit
[ ] configs/step16_long_box_48_moving_boundary.json exists
[ ] configs/step16_long_squid_proxy_48_moving_boundary.json exists
[ ] configs/step16_feasibility_64_moving_boundary_box.json exists
[ ] configs/step16_compare_64_modes.json exists
[ ] baseline_tests/step16_common.py exists
[ ] 48^3 box moving_boundary long-run passes
[ ] 48^3 squid_proxy moving_boundary long-run passes
[ ] 64^3 moving_boundary feasibility passes
[ ] 64^3 mode comparison passes
[ ] completed_lbm_steps box long-run >= 50
[ ] completed_lbm_steps squid_proxy long-run >= 30
[ ] 64^3 moving_boundary completed_lbm_steps >= 5
[ ] rho_min_global > 0.95 for required long-run rows
[ ] rho_max_global < 1.05 for required long-run rows
[ ] lbm_max_v_global < 0.1 for required long-run rows
[ ] mpm_min_J_global > 0 for required long-run rows
[ ] mpm_max_speed_global < 10 for required long-run rows
[ ] bb_link_count_min > 0 for moving_boundary long-runs
[ ] active_reaction_particle_count_min > 0 for moving_boundary long-runs
[ ] cell_force_max_norm == 0 for moving_boundary rows
[ ] penalty row cell_force_max_norm > 0
[ ] no NaN
[ ] no Inf
[ ] write_vtk=false in required Step 16 scale configs
[ ] write_particles=false in required Step 16 scale configs
[ ] artifact large_file_count controlled and reported
[ ] no new FSI physics
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no real squid validation claims
[ ] no sparse storage implementation
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] docs/15_long_run_validation.md exists
[ ] docs state 64^3 moving_boundary row is feasibility only
[ ] README.md updated conservatively
[ ] docs/08_roadmap.md updated
[ ] docs/10_performance_memory.md updated
[ ] docs/13_larger_grid_validation.md updated
[ ] docs/14_moving_boundary_calibration.md updated
[ ] STEP16_LONG_RUN_VALIDATION_REPORT.md complete
[ ] tests/test_step16_long_run_validation_contract.py exists
[ ] pytest -q passes
[ ] logs/step16_pytest.log exists
[ ] git diff --check passes
[ ] Step 16 artifacts are committed
[ ] Step 16 artifacts are pushed to GitHub
```

## 20. Failure Handling

If 48^3 box long-run fails:

```text
Record the exact failing step and diagnostic row.
Do not lower the completed_lbm_steps requirement without explicit goal revision.
Do not change moving-boundary formulas.
Investigate whether Step 15 recommended force cap is still too aggressive over longer runs.
```

If 48^3 squid_proxy long-run fails:

```text
Record whether the failure is density, MPM J, speed, or reaction-count related.
Keep squid_proxy as procedural proxy and do not claim real squid validation.
Do not report a shorter run as full acceptance unless the goal is explicitly revised.
```

If 64^3 moving_boundary feasibility fails:

```text
Keep the failure as evidence.
Try only config-level conservatism if needed: lower target_u_lbm, lower mb_force_cap_norm, or reduce reaction_scale.
Do not change solver physics or moving-boundary formulas.
If still failing, mark Step 16 blocked rather than claiming feasibility.
```

If 64^3 mode comparison fails:

```text
Identify which mode failed.
If none/penalty fail, inspect regression against Step 14.
If moving_boundary fails, inspect conservative settings and dynamic solid counts.
Do not weaken Step 14/15 tests.
```

If artifact manifest finds large files:

```text
Identify whether they were created by Step 16.
Move optional scratch outputs out of committed artifact paths if they are not required.
Do not delete user-created files without explicit approval.
Record large_file_count and total_size_mb in the report.
```

If pytest fails:

```text
Record the exact failing tests and error text.
Fix only issues caused by Step 16 unless the user explicitly broadens scope.
```

If GitHub push fails:

```text
Keep the local commit.
Record the exact push error.
Do not force-push unless explicitly requested.
```

## 21. Completion Definition

Step 16 is complete only when:

```text
1. all required Step 16 files exist
2. Step 16 configs are written and keep outputs lightweight
3. 48^3 box moving_boundary long-run passes
4. 48^3 squid_proxy moving_boundary long-run passes
5. 64^3 box moving_boundary feasibility passes
6. 64^3 none / penalty / moving_boundary comparison passes
7. long-run summary is generated
8. artifact manifest is generated and reported
9. docs and README updates are complete
10. Step 16 report has a completed checklist
11. pytest -q passes
12. logs/step16_pytest.log is saved
13. external/taichi_LBM3D remains unchanged
14. no FSI physics was changed
15. no real squid validation is claimed
16. final Step 16 commit is pushed to GitHub
17. local HEAD matches origin/main
```

Only after those conditions are satisfied may the report mark:

```text
Can proceed to Step 17?

- [x] Yes
- [ ] No
```

Suggested Step 17 title:

```text
Step 17: Strict link-area momentum accounting prototype
```
