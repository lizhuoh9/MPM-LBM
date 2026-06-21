# Step 52 Controlled 48 Engineering One-Cycle Feasibility Goal

## Short Goal Reference

Implement Step 52 exactly as this file specifies. Step 52 is a controlled
48^3 engineering one-cycle feasibility probe built on the accepted Step 50 and
Step 51 diagnostic envelope. It runs only two 48^3 engineering rows, remains
diagnostic-only and non-persistent, does not use `link_area_experimental`, does
not change solver formulas or defaults, and does not make real jet, squid
swimming, grid-convergence, production-readiness, or physical-validation claims.

## Background

Step 51 accepted the 32^3 engineering vs link_area_experimental one-cycle
transfer comparison. Step 51 remained stable, bounded, diagnostic-only, and
non-persistent. It also reserved Step 52 for a selected transfer-mode 48^3
feasibility probe without expanding transfer matrix size and cycle count at the
same time.

Step 52 must therefore expand exactly one dimension:

```text
grid size: 32^3 -> 48^3
```

Step 52 must not expand these dimensions:

```text
transfer modes: engineering only
row matrix: static + combined only
cycle count: one cycle only
physical claims: none
solver behavior: no formula or default changes
```

## Required Scope

Step 52 must prove, through checked-in configs, source wrappers, baseline
runners, outputs, logs, tests, docs, and a report:

1. A 48^3 static engineering one-cycle diagnostic row is finite and bounded.
2. A 48^3 runtime geometry plus wall velocity engineering one-cycle diagnostic
   row is finite and bounded.
3. Both rows run 40 diagnostic step records with 5 MPM substeps per LBM step.
4. Both rows complete at least 40 LBM steps and 200 MPM substeps.
5. The combined 48^3 row is distinguishable from the 48^3 static row by
   diagnostic runtime-geometry and wall-velocity effects.
6. The 48^3 combined row is compared to the Step 51 32^3 engineering combined
   row using finite diagnostic scaling ratios. The comparison must report
   whether projected active-cell growth is observed; if the 48^3 diagnostic
   projection does not increase that summary count, the result must remain
   honest and rely only on non-decreasing active cells, increased applied
   wall-cell support, bounded fields, and explicit no-claim metadata.
7. Cycle closure remains a diagnostic endpoint check only.
8. State mutation guard remains green: no persistent projected state, displaced
   geometry, LBM `solid_vel`, default state mutation, VTR, particle NPY, dense
   displacement, scan data, or `geo_all_fluid_*.dat` outputs.
9. Step 51 evidence remains present and green.
10. Artifact budget remains small and repository total size remains below
    400 MB.

## Explicit Non-Goals

Step 52 must not implement or claim:

```text
64^3 run
multi-cycle run
link_area_experimental 48^3 row
full transfer-mode matrix
runtime-geometry-only 48^3 row
wall-velocity-only 48^3 row
free-body motion
body trajectory
squid swimming
real jet validation
jet propulsion validation
real squid validation
production moving-geometry solver
persistent displaced geometry
persistent projected state
persistent LBM solid_phi update
persistent LBM solid_vel update
persistent dynamic_solid update
production boundary-link recomputation
moving bounce-back formula change
LBM collision or streaming formula change
MPM constitutive formula change
projection formula change
coupler formula change
wall velocity formula change
default behavior change
external/taichi_LBM3D edits
raw real geometry or scan data
grid convergence validation
48^3 physical validation
production solver readiness
```

## Validation Matrix

Step 52 must run exactly two rows:

```text
engineering_static_48_40step
engineering_runtime_geometry_plus_wall_velocity_48_40step
```

Both rows must use:

```text
n_grid = 48
n_lbm_steps = 40
mpm_substeps_per_lbm_step = 5
cycle_period_steps = 40
closure_phase = 1.0
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0, 0, 0]
quality_check_enabled = true
quality_check_strict = true
write_vtk = false
write_particles = false
diagnostic_only = true
```

Phase sequence:

```text
0.0, 0.025, 0.05, 0.075, 0.1,
0.125, 0.15, 0.175, 0.2, 0.225,
0.25, 0.275, 0.3, 0.325, 0.35,
0.375, 0.4, 0.425, 0.45, 0.475,
0.5, 0.525, 0.55, 0.575, 0.6,
0.625, 0.65, 0.675, 0.7, 0.725,
0.75, 0.775, 0.8, 0.825, 0.85,
0.875, 0.9, 0.925, 0.95, 0.975
```

## Files To Add

Configs:

```text
configs/step52_48_engineering_one_cycle_feasibility.json
configs/step52_engineering_static_48_40step.json
configs/step52_engineering_runtime_geometry_plus_wall_velocity_48_40step.json
configs/step52_step51_reference_summary.json
```

Source:

```text
src/runtime_geometry_wall_velocity_48_feasibility_config.py
src/runtime_geometry_wall_velocity_48_feasibility_envelope.py
src/runtime_geometry_wall_velocity_48_feasibility_diagnostics.py
src/runtime_geometry_wall_velocity_48_feasibility_state_guard.py
```

Baseline runners:

```text
baseline_tests/step52_common.py
baseline_tests/run_step52_48_config_validation.py
baseline_tests/run_step52_48_feasibility_matrix.py
baseline_tests/run_step52_48_feasibility_quality.py
baseline_tests/run_step52_48_vs_step51_engineering_scaling_comparison.py
baseline_tests/run_step52_cycle_closure.py
baseline_tests/run_step52_mass_force_bounceback_envelope.py
baseline_tests/run_step52_state_mutation_guard.py
baseline_tests/run_step52_step51_regression_guard.py
baseline_tests/run_step52_artifact_manifest.py
```

Tests and docs:

```text
tests/test_step52_48_engineering_one_cycle_feasibility_contract.py
docs/52_controlled_48_engineering_one_cycle_feasibility.md
STEP52_CONTROLLED_48_ENGINEERING_ONE_CYCLE_FEASIBILITY_REPORT.md
```

## Required Outputs

Each runner must write small CSV/JSON/NPZ/log artifacts under Step 52 specific
directories:

```text
outputs/step52_48_config_validation/
outputs/step52_48_feasibility_matrix/
outputs/step52_48_feasibility_quality/
outputs/step52_48_vs_step51_engineering_scaling_comparison/
outputs/step52_cycle_closure/
outputs/step52_mass_force_bounceback_envelope/
outputs/step52_state_mutation_guard/
outputs/step52_step51_regression_guard/
outputs/step52_artifact_manifest/
logs/step52_*.log
```

The NPZ file may contain only compact summary arrays. It must not contain dense
field dumps, particle arrays, VTR data, raw geometry, or scan data.

## Acceptance Criteria

All of the following must be true:

```text
Step 52 detailed goal file exists
umbrella config exists
2 row configs exist
n_grid is 48
n_lbm_steps is 40
mpm_substeps_per_lbm_step is 5
cycle_period_steps is 40
closure_phase is 1.0
phase_count is 40
phase sequence starts at 0.0
phase sequence ends at 0.975
coupling_mode is moving_boundary
reaction_transfer_mode is engineering
diagnostic_only is true
write_vtk is false
write_particles is false
all persistence flags are false
all default state update flags are false
modify_moving_bounceback_formula is false
no link_area_experimental row is included
no 64^3 row is included
no multi-cycle row is included
48 feasibility matrix row_count is 2
static row count is 1
combined row count is 1
each row has 40 step records
all rows complete at least 40 LBM steps
all rows complete at least 200 MPM substeps
all rows are stable
no NaN
no Inf
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
projected_mass > 0
active_cell_count > 0
bb_link_count > 0
runtime geometry effect active_cell_delta_max_abs > 0
wall velocity effect applied_velocity_delta_max_abs > 0
hydro_force_max_norm is finite
impulse_proxy_max_norm is finite
bb_link_count_delta is finite
rho delta is finite
lbm velocity delta is finite
48 vs Step 51 engineering scaling comparison passes
all scaling ratios are finite
active_cell_count_48 >= active_cell_count_32
active_cell_count_growth_observed is reported
applied_cell_count_48 > applied_cell_count_32
cycle closure passes
state mutation guard passes
Step 51 regression guard passes
artifact budget passes
step52_total_size_mb < 10
repo total_size_mb < 400
large_file_count == 0
step52_vtr_count == 0
step52_particle_npy_count == 0
step52_dense_displacement_output_count == 0
step52_displaced_particle_output_count == 0
scan_data_file_count == 0
raw_candidate_large_file_count == 0
private_absolute_path_count == 0
default geometry_motion_mode remains static
default geometry_motion_application_mode remains disabled
default boundary_motion_mode remains static
default wall_velocity_application_mode remains disabled
no protected solver formula changes
no external/taichi_LBM3D edits
no real jet validation claim
no jet propulsion validation claim
no squid swimming claim
no real squid validation claim
no grid convergence claim
no production readiness claim
logs/step52_pytest.log exists
pytest -q passes
Step 52 contract test passes
git diff --check passes
staged whitespace check passes
Step 52 artifacts are pushed to origin/main
```

## Verification Commands

Use the trusted interpreter path:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\runtime_geometry_wall_velocity_48_feasibility_config.py src\runtime_geometry_wall_velocity_48_feasibility_envelope.py src\runtime_geometry_wall_velocity_48_feasibility_diagnostics.py src\runtime_geometry_wall_velocity_48_feasibility_state_guard.py baseline_tests\step52_common.py baseline_tests\run_step52_48_config_validation.py baseline_tests\run_step52_48_feasibility_matrix.py baseline_tests\run_step52_48_feasibility_quality.py baseline_tests\run_step52_48_vs_step51_engineering_scaling_comparison.py baseline_tests\run_step52_cycle_closure.py baseline_tests\run_step52_mass_force_bounceback_envelope.py baseline_tests\run_step52_state_mutation_guard.py baseline_tests\run_step52_step51_regression_guard.py baseline_tests\run_step52_artifact_manifest.py tests\test_step52_48_engineering_one_cycle_feasibility_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step52_48_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step52_48_feasibility_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step52_48_feasibility_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step52_48_vs_step51_engineering_scaling_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step52_cycle_closure.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step52_mass_force_bounceback_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step52_state_mutation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step52_step51_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step52_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step52_48_engineering_one_cycle_feasibility_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## Report Requirements

The Step 52 report must include:

```text
Goal
Files Created And Updated
Explicit Non-Goals
48 Config Validation
48 Feasibility Matrix
48 Feasibility Quality
48 Vs Step 51 Engineering Scaling Comparison
Cycle Closure
Mass Force Bounce-Back Envelope
State Mutation Guard
Step 51 Regression Guard
Artifact Manifest Summary
Verification Commands
GitHub Sync Information
Acceptance Checklist
Decision For Step 53
```

## Step 53 Reserved Direction

If Step 52 passes, Step 53 may choose exactly one of these directions:

```text
48^3 link_area_experimental comparison, still one-cycle, still 2 rows max
or
32^3 or 48^3 longer diagnostic duration without expanding transfer matrix size
```

Step 53 should not combine 64^3, link_area, and multi-cycle expansion in the
same step.
