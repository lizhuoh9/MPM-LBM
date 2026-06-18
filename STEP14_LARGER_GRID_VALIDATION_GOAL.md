# Step 14 Goal: Larger-Grid Validation and Scaling Baseline

## Paste-Ready `/goal`

```text
/goal
In D:\working\squid robot\LBM\MPM-LBM, execute Step 14: Larger-grid validation and scaling baseline. The only authoritative execution contract is D:\working\squid robot\LBM\MPM-LBM\STEP14_LARGER_GRID_VALIDATION_GOAL.md.

Goal: without changing FSI physics or Step 10/13 validated behavior, extend the current MPM-LBM FSI prototype from 32^3 small-scale validation to 48^3 scale baselines and 64^3 feasibility checks. Add larger-grid configs, box and squid_proxy scale baselines, 64^3 feasibility baselines, scaling summary utilities, artifact hygiene checks, docs, report, logs, outputs, and a pytest contract. Preserve the none/penalty/moving_boundary mode matrix and keep all performance claims conservative.

Hard boundaries: do not implement new FSI physics, do not change lbm.step() default behavior, do not change penalty or moving_boundary formulas, do not replace PenaltyFSICoupler3D or MovingBoundaryFSICoupler3D, do not implement two-phase flow, contact angle physics, real squid validation, squid actuation, swimming locomotion, mesh import, mesh collision/contact, sparse storage, ReducedSquidFSI, production benchmark claims, or edits to external/taichi_LBM3D. Required artifacts, execution order, scale settings, baseline contracts, artifact policy, pytest contract, Hard Acceptance Checklist, failure handling, and completion definition are all defined in STEP14_LARGER_GRID_VALIDATION_GOAL.md. Finish only after all Step 14 baselines pass, pytest passes, external/taichi_LBM3D remains unchanged, and code/docs/logs/outputs/report are pushed to GitHub.
```

## 1. Current Baseline

Step 13 is accepted and is the starting point.

Current Step 13 final commit:

```text
adab90f69847f804edf25c941ca345a108ef0e83
```

Step 13 validated:

```text
src/geometry_config.py exists and supports box, ellipsoid, and squid_proxy.
src/geometry.py implements GeometrySampler3D with deterministic particle sampling and voxelization.
src/geometry_utils.py contains NumPy-only geometry helpers.
MPMSolid3D supports init_from_numpy() and resets deformation state.
FSIDriverConfig supports geometry_type and geometry_config_path.
FSIDriver3D can initialize squid_proxy geometry without changing coupling physics.
box / ellipsoid / squid_proxy geometry baselines pass.
squid_proxy none / penalty / moving_boundary driver modes pass.
Step 13 artifact manifest reports controlled artifacts.
tests/test_step13_geometry_ingestion_contract.py passes.
logs/step13_pytest.log reports 73 passed.
external/taichi_LBM3D remains unchanged.
```

Step 13 means the repository currently has:

```text
1. a geometry-aware MPM-LBM FSI engineering prototype
2. procedural analytic geometry ingestion
3. deterministic particle-cloud initialization for MPM
4. LBM projection diagnostics for box, ellipsoid, and squid_proxy
5. a unified FSIDriver3D mode matrix for none / penalty / moving_boundary
6. small 32^3 validation baselines
7. resource and artifact hygiene tools from Step 12
```

Step 13 still does not mean:

```text
production-grade solver
large-grid readiness
strict final momentum-conserving sharp-interface FSI
real squid geometry simulation
validated squid swimming
two-phase LBM
contact angle physics
sparse storage
```

## 2. Step 14 Objective

Step 14 upgrades the project from 32^3 small validation cases to larger-grid engineering baselines.

Implement reproducible scale validation that provides:

```text
1. 48^3 box validation for none / penalty / moving_boundary
2. 48^3 squid_proxy validation for none / penalty / moving_boundary
3. 64^3 feasibility validation for none / penalty
4. conservative timing and stability diagnostics
5. scaling summary across 32^3, 48^3, and 64^3 references
6. artifact hygiene checks for larger-grid outputs
7. documentation and report updates that avoid production or real-squid overclaims
```

This step is larger-grid validation and scaling evidence. It is not solver optimization, new coupling physics, or real squid validation.

Allowed language:

```text
larger-grid validation
48^3 scale baseline
64^3 feasibility check
engineering scaling baseline
geometry-aware scale testing
artifact-controlled larger-grid workflow
```

Forbidden overclaims:

```text
production benchmark
production-grade large-scale solver
real squid validation
validated squid swimming simulation
strict final momentum-conserving sharp-interface FSI
high-accuracy sharp-interface benchmark
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

If Taichi GPU initialization fails during a required baseline, record the exact error. Do not silently downgrade a required final acceptance run unless the report explicitly marks the run as a failed feasibility item and the contract is revised.

## 4. Strict Non-Goals

Do not implement these in Step 14:

```text
1. No new FSI physics.
2. No new coupling mode.
3. No changes to lbm.step() default behavior.
4. No changes to the Step 8 moving bounce-back formula.
5. No changes to the Step 6/7 penalty-force formula.
6. No changes to the Step 9 moving-boundary reaction formula.
7. No replacement or deletion of PenaltyFSICoupler3D.
8. No replacement or deletion of MovingBoundaryFSICoupler3D.
9. No two-phase flow.
10. No contact angle physics.
11. No real squid validation.
12. No squid actuation or muscle model.
13. No swimming locomotion model.
14. No mesh import.
15. No mesh collision/contact.
16. No sparse storage implementation.
17. No ReducedSquidFSI.
18. No edits to external/taichi_LBM3D.
19. No production benchmark or production-readiness claim.
20. No deletion or weakening of Step 10/12/13 regression artifacts.
```

Allowed in Step 14:

```text
larger-grid JSON configs
larger-grid baseline scripts
conservative timing diagnostics
memory estimate references
CSV/NPZ/JSON/log outputs
artifact manifest checks
docs, tests, logs, outputs, and report
```

Any solver-adjacent edits must be limited to orchestration, configuration, diagnostics, and artifact policy. Do not alter collision, streaming, forcing, bounce-back, constitutive model, P2G/G2P, projection math, coupling formulas, or reaction-transfer physics.

## 5. Required Final Structure

Create:

```text
configs/
  step14_scale_48_none.json
  step14_scale_48_penalty.json
  step14_scale_48_moving_boundary.json
  step14_scale_48_squid_proxy_none.json
  step14_scale_48_squid_proxy_penalty.json
  step14_scale_48_squid_proxy_moving_boundary.json
  step14_feasibility_64_none.json
  step14_feasibility_64_penalty.json

baseline_tests/
  run_step14_scale_box_48.py
  run_step14_scale_squid_proxy_48.py
  run_step14_feasibility_64.py
  run_step14_scaling_summary.py
  run_step14_artifact_manifest.py

outputs/
  step14_scale_box_48/
  step14_scale_squid_proxy_48/
  step14_feasibility_64/
  step14_scaling_summary/
  step14_artifact_manifest/

logs/
  step14_scale_box_48.log
  step14_scale_squid_proxy_48.log
  step14_feasibility_64.log
  step14_scaling_summary.log
  step14_artifact_manifest.log
  step14_pytest.log

docs/
  13_larger_grid_validation.md

tests/
  test_step14_larger_grid_contract.py

STEP14_LARGER_GRID_VALIDATION_REPORT.md
```

Update:

```text
README.md
docs/08_roadmap.md
docs/10_performance_memory.md
docs/12_geometry_ingestion.md
```

Do not delete Step 1-13 reports, logs, outputs, configs, docs, or tests.

## 6. Scale Design

### 6.1 Why Step 14 Should Not Jump To 128^3

Step 12 lower-bound dense-field memory estimates were:

```text
32^3  = 8.046875 MB
64^3  = 64.375000 MB
96^3  = 217.265625 MB
128^3 = 515.000000 MB
```

These are lower-bound estimates. They do not include:

```text
Taichi runtime memory
allocator overhead
temporary kernel buffers
Python and NumPy copies
CSV/NPZ serialization overhead
VTK export overhead
GPU driver/runtime overhead
```

Therefore Step 14 must validate:

```text
48^3 as the main scale baseline
64^3 as a short feasibility window
```

Do not jump directly to 96^3 or 128^3 in the required acceptance path.

### 6.2 48^3 Main Scale

Required 48^3 box settings:

```text
n_grid = 48
n_particles = 13824
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
target_u_lbm = [0.01, 0.0, 0.0]
gravity = [0.0, 0.0, 0.0]
write_vtk = false
write_particles = false
```

Reason for `n_particles = 13824`:

```text
24^3 = 13824
```

This is 3.375x the Step 13 4096-particle baseline while remaining small enough for reproducible short validation.

Required 48^3 squid_proxy settings:

```text
n_grid = 48
n_particles = 4096
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 10
target_u_lbm = [0.005, 0.0, 0.0]
geometry_type = "squid_proxy"
geometry_config_path = "configs/step13_squid_proxy_geometry.json"
write_vtk = false
write_particles = false
```

Reason for keeping squid_proxy at 4096 particles:

```text
Step 14 is testing finer LBM resolution around an existing procedural proxy.
Using the Step 13 squid_proxy geometry config avoids a second geometry change while isolating grid-scale behavior.
```

If Step 14 later chooses to increase squid_proxy particles, create a new explicit geometry config such as:

```text
configs/step14_squid_proxy_geometry_48.json
```

Do not silently override `n_particles` between `FSIDriverConfig` and `GeometryConfig`.

### 6.3 64^3 Feasibility Scale

Required 64^3 feasibility settings:

```text
n_grid = 64
n_particles = 32768
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 5
target_u_lbm = [0.005, 0.0, 0.0]
gravity = [0.0, 0.0, 0.0]
write_vtk = false
write_particles = false
```

Required modes:

```text
none
penalty
```

Do not require 64^3 moving_boundary in Step 14. It may be added as an optional probe only after all required Step 14 acceptance runs pass, and it must not be reported as required acceptance evidence unless the goal is explicitly revised.

## 7. Config Contracts

### 7.1 `configs/step14_scale_48_none.json`

```json
{
  "coupling_mode": "none",
  "geometry_type": "box",
  "n_grid": 48,
  "n_particles": 13824,
  "n_lbm_steps": 10,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.01, 0.0, 0.0],
  "gravity": [0.0, 0.0, 0.0],
  "output_interval": 5,
  "write_vtk": false,
  "write_particles": false
}
```

### 7.2 `configs/step14_scale_48_penalty.json`

```json
{
  "coupling_mode": "penalty",
  "geometry_type": "box",
  "n_grid": 48,
  "n_particles": 13824,
  "n_lbm_steps": 10,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.01, 0.0, 0.0],
  "gravity": [0.0, 0.0, 0.0],
  "beta_lbm": 0.001,
  "penalty_force_cap_lbm": 0.00005,
  "output_interval": 5,
  "write_vtk": false,
  "write_particles": false
}
```

### 7.3 `configs/step14_scale_48_moving_boundary.json`

```json
{
  "coupling_mode": "moving_boundary",
  "geometry_type": "box",
  "n_grid": 48,
  "n_particles": 13824,
  "n_lbm_steps": 10,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.01, 0.0, 0.0],
  "gravity": [0.0, 0.0, 0.0],
  "dynamic_solid_threshold": 0.5,
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.00005,
  "output_interval": 5,
  "write_vtk": false,
  "write_particles": false
}
```

### 7.4 `configs/step14_scale_48_squid_proxy_none.json`

```json
{
  "coupling_mode": "none",
  "geometry_type": "squid_proxy",
  "geometry_config_path": "configs/step13_squid_proxy_geometry.json",
  "n_grid": 48,
  "n_particles": 4096,
  "n_lbm_steps": 10,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "gravity": [0.0, 0.0, 0.0],
  "output_interval": 5,
  "write_vtk": false,
  "write_particles": false
}
```

### 7.5 `configs/step14_scale_48_squid_proxy_penalty.json`

```json
{
  "coupling_mode": "penalty",
  "geometry_type": "squid_proxy",
  "geometry_config_path": "configs/step13_squid_proxy_geometry.json",
  "n_grid": 48,
  "n_particles": 4096,
  "n_lbm_steps": 10,
  "mpm_substeps_per_lbm_step": 10,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "gravity": [0.0, 0.0, 0.0],
  "beta_lbm": 0.001,
  "penalty_force_cap_lbm": 0.00005,
  "output_interval": 5,
  "write_vtk": false,
  "write_particles": false
}
```

### 7.6 `configs/step14_scale_48_squid_proxy_moving_boundary.json`

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
  "gravity": [0.0, 0.0, 0.0],
  "dynamic_solid_threshold": 0.5,
  "mb_reaction_scale": 1.0,
  "mb_force_cap_norm": 0.000025,
  "output_interval": 5,
  "write_vtk": false,
  "write_particles": false
}
```

### 7.7 `configs/step14_feasibility_64_none.json`

```json
{
  "coupling_mode": "none",
  "geometry_type": "box",
  "n_grid": 64,
  "n_particles": 32768,
  "n_lbm_steps": 5,
  "mpm_substeps_per_lbm_step": 5,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "gravity": [0.0, 0.0, 0.0],
  "output_interval": 5,
  "write_vtk": false,
  "write_particles": false
}
```

### 7.8 `configs/step14_feasibility_64_penalty.json`

```json
{
  "coupling_mode": "penalty",
  "geometry_type": "box",
  "n_grid": 64,
  "n_particles": 32768,
  "n_lbm_steps": 5,
  "mpm_substeps_per_lbm_step": 5,
  "target_u_lbm": [0.005, 0.0, 0.0],
  "gravity": [0.0, 0.0, 0.0],
  "beta_lbm": 0.001,
  "penalty_force_cap_lbm": 0.00005,
  "output_interval": 5,
  "write_vtk": false,
  "write_particles": false
}
```

## 8. Shared Result Fields

Each Step 14 baseline CSV should include as many of these fields as practical:

```text
mode
geometry_type
stable
n_grid
n_particles
n_lbm_steps
mpm_substeps_per_lbm_step
total_mpm_substeps
target_u_lbm_x
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
projection_zone_ux_final
solid_mean_vx_final
active_cell_count
projected_mass
cell_force_max_norm
hydro_force_max_norm
bb_link_count
active_reaction_particle_count
max_grid_reaction_norm
estimated_memory_mb
total_time_sec
steps_per_sec
notes
```

All numerical values must be finite for stable rows.

## 9. Baseline 1: 48^3 Box Scale Validation

Create:

```text
baseline_tests/run_step14_scale_box_48.py
```

Purpose:

```text
Verify that the existing box geometry can run at 48^3 in none, penalty, and moving_boundary modes without changing coupling physics.
```

Required configs:

```text
configs/step14_scale_48_none.json
configs/step14_scale_48_penalty.json
configs/step14_scale_48_moving_boundary.json
```

Required flow:

```text
1. Load each config through the same config path used by existing driver baselines.
2. Run FSIDriver3D for the configured n_lbm_steps.
3. Record final diagnostics and total runtime per mode.
4. Save one CSV row per mode.
5. Save a compact NPZ summary.
6. Do not write VTK or particle dumps for required acceptance.
```

Required outputs:

```text
outputs/step14_scale_box_48/box_48_results.csv
outputs/step14_scale_box_48/box_48_results.npz
logs/step14_scale_box_48.log
```

Acceptance:

```text
none stable
penalty stable
moving_boundary stable
n_grid == 48
n_particles == 13824
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
penalty cell_force_max_norm > 0
moving_boundary cell_force_max_norm == 0
moving_boundary bb_link_count > 0
all values finite
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 14 48^3 box scale validation finished
```

## 10. Baseline 2: 48^3 Squid Proxy Scale Validation

Create:

```text
baseline_tests/run_step14_scale_squid_proxy_48.py
```

Purpose:

```text
Verify that the procedural squid_proxy geometry from Step 13 can run on a 48^3 LBM grid in none, penalty, and moving_boundary modes.
```

Required configs:

```text
configs/step14_scale_48_squid_proxy_none.json
configs/step14_scale_48_squid_proxy_penalty.json
configs/step14_scale_48_squid_proxy_moving_boundary.json
```

Required flow:

```text
1. Use geometry_config_path = configs/step13_squid_proxy_geometry.json.
2. Keep n_particles consistent with the geometry config.
3. Run none, penalty, and moving_boundary modes.
4. Use target_u_lbm = [0.005, 0.0, 0.0] unless the goal is explicitly revised.
5. Record final diagnostics and total runtime per mode.
6. Save one CSV row per mode.
7. Save a compact NPZ summary.
8. Do not write VTK or particle dumps for required acceptance.
```

Required outputs:

```text
outputs/step14_scale_squid_proxy_48/squid_proxy_48_results.csv
outputs/step14_scale_squid_proxy_48/squid_proxy_48_results.npz
logs/step14_scale_squid_proxy_48.log
```

Acceptance:

```text
none stable
penalty stable
moving_boundary stable
n_grid == 48
n_particles == 4096
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
active_cell_count > 0
projected_mass > 0
penalty cell_force_max_norm > 0
moving_boundary cell_force_max_norm == 0
moving_boundary bb_link_count > 0
all values finite
no NaN
no Inf
```

If moving_boundary is unstable, do not claim Step 14 acceptance. First reduce only Step 14 config aggressiveness, for example:

```text
target_u_lbm = [0.0025, 0.0, 0.0]
mb_force_cap_norm = 0.0000125
n_lbm_steps remains 10 unless explicitly revised
```

Any such reduction must be recorded in the report and in the config files. Do not change moving-boundary formulas to pass this baseline.

Required log marker:

```text
[OK] Step 14 48^3 squid proxy scale validation finished
```

## 11. Baseline 3: 64^3 Feasibility

Create:

```text
baseline_tests/run_step14_feasibility_64.py
```

Purpose:

```text
Run a short 64^3 feasibility check for none and penalty modes. This is not a full 64^3 validation suite.
```

Required configs:

```text
configs/step14_feasibility_64_none.json
configs/step14_feasibility_64_penalty.json
```

Required flow:

```text
1. Run none and penalty only.
2. Use n_grid = 64 and n_particles = 32768.
3. Use n_lbm_steps = 5 and mpm_substeps_per_lbm_step = 5.
4. Use target_u_lbm = [0.005, 0.0, 0.0].
5. Record timing and memory estimate fields.
6. Save one CSV row per mode.
7. Save a compact NPZ summary.
8. Do not write VTK or particle dumps for required acceptance.
```

Required outputs:

```text
outputs/step14_feasibility_64/feasibility_64_results.csv
outputs/step14_feasibility_64/feasibility_64_results.npz
logs/step14_feasibility_64.log
```

Acceptance:

```text
none stable
penalty stable
n_grid == 64
n_particles == 32768
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
penalty cell_force_max_norm > 0
estimated_memory_mb finite and positive
total_time_sec finite and positive
all values finite
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 14 64^3 feasibility finished
```

## 12. Baseline 4: Scaling Summary

Create:

```text
baseline_tests/run_step14_scaling_summary.py
```

Purpose:

```text
Combine Step 12 memory estimates and Step 14 run results into one conservative scaling summary.
```

Inputs:

```text
outputs/step12_memory_estimate/memory_estimate.csv
outputs/step14_scale_box_48/box_48_results.csv
outputs/step14_scale_squid_proxy_48/squid_proxy_48_results.csv
outputs/step14_feasibility_64/feasibility_64_results.csv
```

Required outputs:

```text
outputs/step14_scaling_summary/scaling_summary.csv
outputs/step14_scaling_summary/scaling_summary.json
logs/step14_scaling_summary.log
```

Required summary fields:

```text
n_grid
geometry_type
mode
n_particles
stable
total_time_sec
estimated_memory_mb
rho_min
rho_max
lbm_max_v
mpm_min_J
notes
```

Acceptance:

```text
scaling_summary.csv exists
scaling_summary.json exists
summary references 32^3, 48^3, and 64^3 scales
48^3 stable rows are included
64^3 feasibility rows are included
all stable rows have finite numerical values
notes distinguish validation baselines from production benchmarks
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 14 scaling summary finished
```

## 13. Baseline 5: Step 14 Artifact Manifest

Create:

```text
baseline_tests/run_step14_artifact_manifest.py
```

Purpose:

```text
Use the Step 12 artifact utilities to verify that larger-grid baselines did not create uncontrolled large artifacts.
```

Scan roots:

```text
logs/
outputs/
STEP*_REPORT.md
docs/
paper/
configs/
```

Required outputs:

```text
outputs/step14_artifact_manifest/artifact_manifest.csv
outputs/step14_artifact_manifest/artifact_summary.json
logs/step14_artifact_manifest.log
```

Acceptance:

```text
manifest exists
summary exists
file_count > 0
total_size_bytes > 0
large_file_count >= 0
large_file_count and total_size_mb are reported in STEP14_LARGER_GRID_VALIDATION_REPORT.md
required scale baselines have write_vtk=false
required scale baselines have write_particles=false
no NaN
no Inf
```

Required log marker:

```text
[OK] Step 14 artifact manifest finished
```

## 14. Artifact Policy

Step 14 must avoid large visualization outputs in accepted baselines.

Required default for scale configs:

```text
write_vtk = false
write_particles = false
```

Allowed committed outputs:

```text
CSV
NPZ
small JSON
logs
artifact manifest summaries
```

Disallowed in required Step 14 acceptance artifacts unless explicitly justified in the report:

```text
large VTK/VTR files
large particle dumps
large animation files
scratch/experimental outputs
```

Any optional visualization probe must be clearly marked optional and must not be used as required Step 14 acceptance evidence.

## 15. Documentation Updates

Create:

```text
docs/13_larger_grid_validation.md
```

Must include:

```text
Step 14 scope
48^3 main validation design
64^3 feasibility design
box and squid_proxy scale baselines
none / penalty / moving_boundary mode matrix at 48^3
none / penalty feasibility at 64^3
artifact policy for larger-grid runs
memory estimate references from Step 12
timing and stability summary
limitations and non-goals
```

Must state:

```text
Step 14 does not add new FSI physics.
Step 14 does not validate real squid swimming.
48^3 results are engineering scale baselines, not production benchmarks.
64^3 results are feasibility checks, not full validation.
```

Update `README.md` with a concise note:

```markdown
## Larger-Grid Validation

Step 14 adds 48^3 scale validation and 64^3 feasibility checks. These are engineering scale baselines, not production benchmarks or real squid validation.
```

Update `docs/08_roadmap.md`:

```text
Mark Step 14 as current while in progress, and completed after acceptance.
Set Step 15 to moving-boundary reaction calibration and sharper momentum accounting.
State that future work must preserve the Step 10 mode matrix, Step 12 resource checks, and Step 13 geometry contracts.
```

Update `docs/10_performance_memory.md`:

```text
Add Step 14 actual timing rows for 48^3 and 64^3 runs.
Keep memory estimates conservative and describe them as lower bounds.
Do not present Step 14 timing as a production benchmark.
```

Update `docs/12_geometry_ingestion.md`:

```text
Add a note that squid_proxy was reused in Step 14 at 48^3 for scale validation.
Clarify again that squid_proxy is procedural and not real squid validation.
```

## 16. Step 14 Report Contract

Create:

```text
STEP14_LARGER_GRID_VALIDATION_REPORT.md
```

Required sections:

```markdown
# Step 14 Larger Grid Validation Report

## 1. Goal
## 2. Files
## 3. Explicit Non-Goals
## 4. Scale Settings
## 5. 48^3 Box Validation
## 6. 48^3 Squid Proxy Validation
## 7. 64^3 Feasibility
## 8. Scaling Summary
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
mode results tables
key rho / velocity / MPM stability stats
timing summary
memory estimate references
artifact summary
pytest command/result
confirmation that external/taichi_LBM3D was unchanged
confirmation that no FSI physics changed
confirmation that squid_proxy is not real squid validation
final commit hash
remote branch after push
```

Before final verification, checklist items may be unchecked. They must be checked only after baselines and pytest pass.

## 17. Pytest Contract

Create:

```text
tests/test_step14_larger_grid_contract.py
```

The test must check required paths:

```python
required_paths = [
    "configs/step14_scale_48_none.json",
    "configs/step14_scale_48_penalty.json",
    "configs/step14_scale_48_moving_boundary.json",
    "configs/step14_scale_48_squid_proxy_none.json",
    "configs/step14_scale_48_squid_proxy_penalty.json",
    "configs/step14_scale_48_squid_proxy_moving_boundary.json",
    "configs/step14_feasibility_64_none.json",
    "configs/step14_feasibility_64_penalty.json",
    "baseline_tests/run_step14_scale_box_48.py",
    "baseline_tests/run_step14_scale_squid_proxy_48.py",
    "baseline_tests/run_step14_feasibility_64.py",
    "baseline_tests/run_step14_scaling_summary.py",
    "baseline_tests/run_step14_artifact_manifest.py",
    "logs/step14_scale_box_48.log",
    "logs/step14_scale_squid_proxy_48.log",
    "logs/step14_feasibility_64.log",
    "logs/step14_scaling_summary.log",
    "logs/step14_artifact_manifest.log",
    "logs/step14_pytest.log",
    "outputs/step14_scale_box_48/box_48_results.csv",
    "outputs/step14_scale_squid_proxy_48/squid_proxy_48_results.csv",
    "outputs/step14_feasibility_64/feasibility_64_results.csv",
    "outputs/step14_scaling_summary/scaling_summary.csv",
    "outputs/step14_scaling_summary/scaling_summary.json",
    "outputs/step14_artifact_manifest/artifact_summary.json",
    "docs/13_larger_grid_validation.md",
    "STEP14_LARGER_GRID_VALIDATION_REPORT.md",
]
```

The test must check log success markers:

```text
[OK] Step 14 48^3 box scale validation finished
[OK] Step 14 48^3 squid proxy scale validation finished
[OK] Step 14 64^3 feasibility finished
[OK] Step 14 scaling summary finished
[OK] Step 14 artifact manifest finished
```

The test must parse CSV/JSON/NPZ outputs and verify:

```text
box_48_results.csv contains none, penalty, moving_boundary
box_48_results.csv has n_grid == 48
box_48_results.csv has n_particles == 13824
box_48_results.csv has all stable == True
squid_proxy_48_results.csv contains none, penalty, moving_boundary
squid_proxy_48_results.csv has n_grid == 48
squid_proxy_48_results.csv has n_particles == 4096
squid_proxy_48_results.csv has all stable == True
feasibility_64_results.csv contains none and penalty
feasibility_64_results.csv has n_grid == 64
feasibility_64_results.csv has n_particles == 32768
feasibility_64_results.csv has all stable == True
all stable rows have rho_min > 0.95
all stable rows have rho_max < 1.05
all stable rows have lbm_max_v < 0.1
all stable rows have mpm_min_J > 0
all stable rows have mpm_max_speed < 10
all stable rows have finite total_time_sec
scaling_summary.csv references 32, 48, and 64 grid scales
artifact summary file_count > 0
artifact summary total_size_bytes > 0
```

The test must check configs:

```text
required Step 14 configs have write_vtk == false
required Step 14 configs have write_particles == false
48^3 configs use n_grid == 48
64^3 configs use n_grid == 64
squid_proxy configs use geometry_type == "squid_proxy"
```

The test must check documentation/report do not contain overclaim phrases:

```text
real squid simulation is validated
validated squid swimming
biomechanically accurate squid
anatomically accurate squid
production benchmark
production-grade large-scale solver
strict momentum-conserving FSI is complete
```

The test must check forbidden implementation claims:

```text
implements two_phase
implements contact_angle
ReducedSquidFSI
```

Do not forbid explanatory non-goal phrases such as:

```text
no two-phase flow
no contact angle physics
not real squid validation
not a production benchmark
```

The test must check `STEP14_LARGER_GRID_VALIDATION_REPORT.md` acceptance checklist items are marked `[x]`.

## 18. Required Execution Order

Follow this order:

```text
1. Confirm git status, branch, remote, README, roadmap, and Step 13 baseline.
2. Read STEP14_LARGER_GRID_VALIDATION_GOAL.md.
3. Read README.md, docs/08_roadmap.md, docs/10_performance_memory.md, docs/12_geometry_ingestion.md, STEP13_GEOMETRY_INGESTION_REPORT.md, src/fsi_config.py, src/fsi_driver.py, src/performance.py, and src/artifact_utils.py.
4. Add tests/test_step14_larger_grid_contract.py first.
5. Run pytest and confirm RED because Step 14 artifacts are missing.
6. Add Step 14 configs.
7. Add run_step14_scale_box_48.py.
8. Run 48^3 box scale baseline and save log.
9. Add run_step14_scale_squid_proxy_48.py.
10. Run 48^3 squid_proxy scale baseline and save log.
11. Add run_step14_feasibility_64.py.
12. Run 64^3 feasibility baseline and save log.
13. Add run_step14_scaling_summary.py.
14. Run scaling summary baseline and save log.
15. Add run_step14_artifact_manifest.py.
16. Run artifact manifest baseline and save log.
17. Add docs/13_larger_grid_validation.md.
18. Update README.md, docs/08_roadmap.md, docs/10_performance_memory.md, and docs/12_geometry_ingestion.md.
19. Add STEP14_LARGER_GRID_VALIDATION_REPORT.md with unchecked checklist.
20. Run pytest -q.
21. Fix only Step 14 issues.
22. Save final pytest log as logs/step14_pytest.log.
23. Confirm src solver physics behavior is unchanged except orchestration/config/diagnostic additions.
24. Confirm external/taichi_LBM3D is unchanged.
25. Update STEP14_LARGER_GRID_VALIDATION_REPORT.md checklist to checked.
26. Run final pytest -q.
27. Run git diff --check and git diff --cached --check.
28. Commit Step 14 artifacts.
29. Push to GitHub.
30. Verify local HEAD equals origin/main.
```

Do not report a short probe as Step 14 acceptance. Step 14 acceptance requires all five Step 14 baselines, pytest, completed report, and GitHub push.

## 19. Verification Commands

Primary:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Baseline commands:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_scale_box_48.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_scale_squid_proxy_48.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_feasibility_64.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_scaling_summary.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_artifact_manifest.py
```

Log-saving form:

```powershell
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_scale_box_48.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step14_scale_box_48.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_scale_squid_proxy_48.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step14_scale_squid_proxy_48.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_feasibility_64.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step14_feasibility_64.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_scaling_summary.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step14_scaling_summary.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_artifact_manifest.py 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step14_artifact_manifest.log; $out; if ($code -ne 0) { exit $code }
$out = & 'D:\working\taichi\env\python.exe' -m pytest -q 2>&1; $code = $LASTEXITCODE; $out | Out-File -Encoding utf8 logs\step14_pytest.log; $out; if ($code -ne 0) { exit $code }
```

Git hygiene:

```powershell
git status --short --branch
git status --short external
git diff --check
git diff --cached --check
```

## 20. Hard Acceptance Checklist

All must be true before Step 14 is complete:

```text
[ ] main is on the Step 14 final commit
[ ] configs/step14_scale_48_none.json exists
[ ] configs/step14_scale_48_penalty.json exists
[ ] configs/step14_scale_48_moving_boundary.json exists
[ ] configs/step14_scale_48_squid_proxy_none.json exists
[ ] configs/step14_scale_48_squid_proxy_penalty.json exists
[ ] configs/step14_scale_48_squid_proxy_moving_boundary.json exists
[ ] configs/step14_feasibility_64_none.json exists
[ ] configs/step14_feasibility_64_penalty.json exists
[ ] 48^3 box none baseline passes
[ ] 48^3 box penalty baseline passes
[ ] 48^3 box moving_boundary baseline passes
[ ] 48^3 squid_proxy none baseline passes
[ ] 48^3 squid_proxy penalty baseline passes
[ ] 48^3 squid_proxy moving_boundary baseline passes
[ ] 64^3 none feasibility baseline passes
[ ] 64^3 penalty feasibility baseline passes
[ ] rho_min > 0.95 for all stable rows
[ ] rho_max < 1.05 for all stable rows
[ ] lbm_max_v < 0.1 for all stable rows
[ ] mpm_min_J > 0 for all stable rows
[ ] mpm_max_speed < 10 for all stable rows
[ ] active_cell_count > 0 where projection is active
[ ] projected_mass > 0 where projection is active
[ ] no NaN
[ ] no Inf
[ ] scaling_summary.csv exists
[ ] scaling_summary.json exists
[ ] scaling summary references 32^3, 48^3, and 64^3
[ ] artifact manifest exists
[ ] artifact manifest reports total size and large_file_count
[ ] write_vtk is false in required scale configs
[ ] write_particles is false in required scale configs
[ ] no new FSI physics
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no real squid validation claims
[ ] no sparse storage implementation
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] docs/13_larger_grid_validation.md exists
[ ] README.md documents larger-grid validation conservatively
[ ] docs/08_roadmap.md updated
[ ] docs/10_performance_memory.md updated
[ ] docs/12_geometry_ingestion.md updated
[ ] STEP14_LARGER_GRID_VALIDATION_REPORT.md complete
[ ] tests/test_step14_larger_grid_contract.py exists
[ ] pytest -q passes
[ ] logs/step14_pytest.log exists
[ ] git diff --check passes
[ ] Step 14 artifacts are committed
[ ] Step 14 artifacts are pushed to GitHub
```

## 21. Failure Handling

If a 48^3 box mode is unstable:

```text
Inspect diagnostics first.
Reduce only Step 14 config aggressiveness if needed.
Do not change penalty or moving_boundary formulas.
Do not report a shorter probe as full acceptance.
```

If 48^3 squid_proxy moving_boundary is unstable:

```text
First reduce target_u_lbm and/or mb_force_cap_norm in the Step 14 squid_proxy moving_boundary config.
Keep n_lbm_steps at 10 unless the user explicitly revises the goal.
Record the original failure and final accepted parameters in the report.
Do not alter moving bounce-back or reaction-transfer formulas.
```

If 64^3 feasibility fails due to memory or runtime:

```text
Record the exact failure and environment.
Do not claim 64^3 feasibility passed.
Do not silently shrink to 48^3 or 32^3.
Ask for a revised feasibility contract if the hardware cannot run the required case.
```

If artifact manifest finds large files:

```text
Identify whether they are required baseline artifacts.
Move optional scratch outputs out of the committed artifact path if they were created by the current task.
Record large_file_count and total_size_mb in the report.
Do not delete user-created files without explicit approval.
```

If Step 10, Step 12, or Step 13 regression tests fail:

```text
Stop and inspect whether Step 14 changed existing behavior.
Fix orchestration/config compatibility only.
Do not weaken existing tests unless the failure is a demonstrably stale documentation-only assertion and the report explains why.
```

If pytest fails:

```text
Record the exact failing tests and error text.
Fix only issues caused by Step 14 unless the user explicitly broadens scope.
```

If GitHub push fails:

```text
Keep the local commit.
Record the exact push error.
Do not force-push unless explicitly requested.
```

## 22. Completion Definition

Step 14 is complete only when:

```text
1. all required Step 14 files exist
2. 48^3 box none/penalty/moving_boundary baselines pass
3. 48^3 squid_proxy none/penalty/moving_boundary baselines pass
4. 64^3 none/penalty feasibility baselines pass
5. scaling summary is generated
6. artifact manifest is generated and reported
7. scale configs keep heavy outputs disabled by default
8. docs and README updates are complete
9. Step 14 report has a completed checklist
10. pytest -q passes
11. logs/step14_pytest.log is saved
12. external/taichi_LBM3D remains unchanged
13. no FSI physics was changed
14. no real squid validation is claimed
15. final Step 14 commit is pushed to GitHub
16. local HEAD matches origin/main
```

Only after those conditions are satisfied may the report mark:

```text
Can proceed to Step 15?

- [x] Yes
- [ ] No
```

Suggested Step 15 title:

```text
Step 15: Moving-boundary reaction calibration and sharper momentum accounting
```
