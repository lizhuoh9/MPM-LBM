# Step 51 Controlled One-Cycle Runtime Geometry + Wall Velocity Transfer Comparison Goal

## Short Goal Reference

Implement Step 51 exactly as this file specifies. Step 51 compares `engineering`
and `link_area_experimental` transfer behavior for the accepted Step 50
one-cycle runtime-geometry plus wall-velocity diagnostic envelope. It remains
32^3, one-cycle, opt-in, non-persistent, diagnostic-only, and not a real jet,
free-body, production moving-geometry, or squid-swimming validation.

## Background

Step 50 accepted the 32^3, 40-step, engineering-only, runtime geometry plus wall
velocity diagnostic envelope. That step kept all default geometry and wall
velocity modes static or disabled, kept all displaced geometry and projected
state non-persistent, and did not change any moving bounce-back, LBM, MPM,
projection, coupler, or wall-velocity formulas.

Step 51 must keep the Step 50 envelope as the baseline and add one bounded
comparison dimension:

```text
engineering vs link_area_experimental
```

The goal is a controlled transfer-mode comparison, not a larger or more
physical simulation claim.

## Required Scope

Step 51 must prove, through checked-in configs, runners, outputs, logs, tests,
docs, and a report:

1. The 32^3 one-cycle runtime geometry plus wall velocity envelope remains
   stable under `engineering`.
2. The same 32^3 one-cycle envelope is finite and bounded under
   `link_area_experimental`.
3. `link_area_experimental` reports finite `area_scale` values within
   `[0.25, 2.0]`.
4. Runtime geometry effect, wall velocity effect, and combined effect remain
   distinguishable for both transfer modes.
5. Engineering-vs-link-area deltas for rho, LBM velocity, projected mass, active
   cells, hydro force, bounce-back, and impulse proxy diagnostics are finite and
   bounded.
6. The Step 50 engineering rows remain comparable to Step 51 engineering rows.
7. Default `geometry_motion_mode`, `geometry_motion_application_mode`,
   `boundary_motion_mode`, and `wall_velocity_application_mode` remain static or
   disabled.
8. No Step 51 code changes the protected solver formulas.
9. No Step 51 artifact persists displaced geometry, projected state, LBM
   `solid_vel`, VTR, particle NPY, dense displacement, scan data, or raw real
   geometry outputs.
10. Documentation does not claim real jet propulsion validation, squid
    swimming, production moving-geometry support, or physical superiority of
    `link_area_experimental`.

## Explicit Non-Goals

Step 51 must not implement or claim:

```text
48^3 or 64^3 run
multi-cycle run
free-body motion
body trajectory
squid swimming
real jet validation
jet propulsion validation
real squid validation
production moving geometry solver
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
link_area physical validation
link_area superiority
```

## Validation Matrix

Step 51 must run an 8-row, 40-step matrix.

Engineering baseline rows:

```text
engineering_original_static_32_40step
engineering_runtime_geometry_only_32_40step
engineering_wall_velocity_only_32_40step
engineering_runtime_geometry_plus_wall_velocity_32_40step
```

Link-area comparison rows:

```text
link_area_original_static_32_40step
link_area_runtime_geometry_only_32_40step
link_area_wall_velocity_only_32_40step
link_area_runtime_geometry_plus_wall_velocity_32_40step
```

All rows must use:

```text
n_grid = 32
n_lbm_steps = 40
mpm_substeps_per_lbm_step = 5
cycle_period_steps = 40
coupling_mode = moving_boundary
target_u_lbm = [0, 0, 0]
quality_check_enabled = true
quality_check_strict = true
write_vtk = false
write_particles = false
diagnostic_only = true
```

Transfer modes:

```text
engineering rows: reaction_transfer_mode = engineering
link-area rows: reaction_transfer_mode = link_area_experimental
```

Link-area bounds:

```text
link_area_policy = inverse_length
link_area_scale_min = 0.25
link_area_scale_max = 2.0
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

Closure diagnostic:

```text
closure_phase = 1.0
```

## Files To Add

Configs:

```text
configs/step51_transfer_comparison_one_cycle_envelope.json
configs/step51_engineering_original_static_32_40step.json
configs/step51_engineering_runtime_geometry_only_32_40step.json
configs/step51_engineering_wall_velocity_only_32_40step.json
configs/step51_engineering_runtime_geometry_plus_wall_velocity_32_40step.json
configs/step51_link_area_original_static_32_40step.json
configs/step51_link_area_runtime_geometry_only_32_40step.json
configs/step51_link_area_wall_velocity_only_32_40step.json
configs/step51_link_area_runtime_geometry_plus_wall_velocity_32_40step.json
```

Source:

```text
src/runtime_geometry_wall_velocity_transfer_config.py
src/runtime_geometry_wall_velocity_transfer_envelope.py
src/runtime_geometry_wall_velocity_transfer_diagnostics.py
src/runtime_geometry_wall_velocity_transfer_state_guard.py
```

Baseline runners:

```text
baseline_tests/step51_common.py
baseline_tests/run_step51_transfer_config_validation.py
baseline_tests/run_step51_transfer_comparison_matrix.py
baseline_tests/run_step51_transfer_envelope_quality.py
baseline_tests/run_step51_engineering_vs_link_area_comparison.py
baseline_tests/run_step51_link_area_envelope.py
baseline_tests/run_step51_component_effect_by_transfer.py
baseline_tests/run_step51_cycle_closure_by_transfer.py
baseline_tests/run_step51_step50_engineering_prefix_comparison.py
baseline_tests/run_step51_mass_force_bounceback_transfer_envelope.py
baseline_tests/run_step51_state_mutation_guard.py
baseline_tests/run_step51_step50_regression_guard.py
baseline_tests/run_step51_artifact_manifest.py
```

Tests and docs:

```text
tests/test_step51_one_cycle_transfer_comparison_contract.py
docs/51_controlled_runtime_geometry_wall_velocity_transfer_comparison.md
STEP51_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_TRANSFER_COMPARISON_REPORT.md
```

## Required Outputs

Each runner must write small CSV/JSON/NPZ/log artifacts under Step 51 specific
directories:

```text
outputs/step51_transfer_config_validation/
outputs/step51_transfer_comparison_matrix/
outputs/step51_transfer_envelope_quality/
outputs/step51_engineering_vs_link_area_comparison/
outputs/step51_link_area_envelope/
outputs/step51_component_effect_by_transfer/
outputs/step51_cycle_closure_by_transfer/
outputs/step51_step50_engineering_prefix_comparison/
outputs/step51_mass_force_bounceback_transfer_envelope/
outputs/step51_state_mutation_guard/
outputs/step51_step50_regression_guard/
outputs/step51_artifact_manifest/
logs/step51_*.log
```

## Acceptance Criteria

All of the following must be true:

```text
Step 51 detailed goal file exists
transfer config validation passes
n_grid is 32
n_lbm_steps is 40
mpm_substeps_per_lbm_step is 5
cycle_period_steps is 40
engineering transfer mode exists
link_area_experimental transfer mode exists
no 48^3 row is included
no 64^3 row is included
no multi-cycle row is included
link_area_scale_min is 0.25
link_area_scale_max is 2.0
all persistence flags are false
all default state update flags are false
modify_moving_bounceback_formula is false
transfer comparison matrix runs 8 rows
engineering row count is 4
link_area row count is 4
each row has 40 step records
all rows complete at least 40 LBM steps
all rows complete at least 200 MPM substeps
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
projected_mass > 0
active_cell_count > 0
bb_link_count > 0
no NaN
no Inf
transfer envelope quality passes
engineering vs link_area comparison passes
link_area envelope passes
area_scale is finite
0.25 <= area_scale <= 2.0
component effect by transfer passes
cycle closure by transfer passes
Step 50 engineering prefix comparison passes
mass/force/bounce-back transfer envelope passes
state mutation guard passes
original geometry hash remains stable
region mask hash remains stable
default driver state mutation count is 0
default LBM state mutation count is 0
default MPM state mutation count is 0
persistent projected state count is 0
persistent displaced geometry count is 0
persistent LBM solid_vel count is 0
displaced particle output count is 0
dense displacement output count is 0
VTR output count is 0
geo_all_fluid_dat_count_added is 0
Step 50 regression guard passes
default geometry_motion_mode remains static
default geometry_motion_application_mode remains disabled
default boundary_motion_mode remains static
default wall_velocity_application_mode remains disabled
no default behavior change
no moving bounce-back formula changes
no LBM collision formula changes
no MPM constitutive formula changes
no projection formula changes
no external/taichi_LBM3D edits
no real jet validation claim
no jet propulsion validation claim
no squid swimming claim
no real squid validation claim
no link_area physical superiority claim
no Step 51 .vtr outputs
no Step 51 particle .npy outputs
artifact large_file_count == 0
Step 51 output total-size budget passes
repo artifact summary total_size_mb < 400
logs/step51_pytest.log exists
pytest -q passes
Step 51 contract test passes
git diff --check passes
staged whitespace check passes
Step 51 artifacts are pushed to origin/main
```

## Verification Commands

Run the Step 51 specific runners first, then full pytest:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\runtime_geometry_wall_velocity_transfer_config.py src\runtime_geometry_wall_velocity_transfer_envelope.py src\runtime_geometry_wall_velocity_transfer_diagnostics.py src\runtime_geometry_wall_velocity_transfer_state_guard.py baseline_tests\step51_common.py baseline_tests\run_step51_transfer_config_validation.py baseline_tests\run_step51_transfer_comparison_matrix.py baseline_tests\run_step51_transfer_envelope_quality.py baseline_tests\run_step51_engineering_vs_link_area_comparison.py baseline_tests\run_step51_link_area_envelope.py baseline_tests\run_step51_component_effect_by_transfer.py baseline_tests\run_step51_cycle_closure_by_transfer.py baseline_tests\run_step51_step50_engineering_prefix_comparison.py baseline_tests\run_step51_mass_force_bounceback_transfer_envelope.py baseline_tests\run_step51_state_mutation_guard.py baseline_tests\run_step51_step50_regression_guard.py baseline_tests\run_step51_artifact_manifest.py tests\test_step51_one_cycle_transfer_comparison_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step51_transfer_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step51_transfer_comparison_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step51_transfer_envelope_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step51_engineering_vs_link_area_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step51_link_area_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step51_component_effect_by_transfer.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step51_cycle_closure_by_transfer.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step51_step50_engineering_prefix_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step51_mass_force_bounceback_transfer_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step51_state_mutation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step51_step50_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step51_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step51_one_cycle_transfer_comparison_contract.py -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## Report Requirements

The Step 51 report must include:

```text
Goal
Files Created And Updated
Explicit Non-Goals
Transfer Config Validation
Transfer Comparison Matrix
Transfer Envelope Quality
Engineering Vs Link-Area Comparison
Link-Area Envelope
Component Effect By Transfer
Cycle Closure By Transfer
Step 50 Engineering Prefix Comparison
Mass Force Bounce-Back Transfer Envelope
State Mutation Guard
Step 50 Regression Guard
Artifact Manifest Summary
Verification Commands
GitHub Sync Information
Acceptance Checklist
Decision For Step 52
```

## Step 52 Reserved Direction

If Step 51 passes, Step 52 may consider one selected 48^3 feasibility row plus
a static baseline, using the more stable or conservative Step 51 transfer mode.
Step 52 should not simultaneously expand grid size, transfer matrix size, and
cycle count.
