# Step 51 Controlled One-Cycle Runtime Geometry + Wall Velocity Transfer Comparison Report

## 1. Goal

Step 51 is controlled one-cycle runtime geometry plus wall velocity transfer comparison.
Step 51 compares engineering and link_area_experimental diagnostically.
Step 51 remains 32^3 and one-cycle.
Step 51 remains non-persistent.
Step 51 does not validate real jet propulsion.
Step 51 does not implement squid swimming.
Step 51 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

The detailed goal is in `STEP51_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_TRANSFER_COMPARISON_GOAL.md`.

## 2. Files Created And Updated

Step 51 adds transfer comparison configs, source modules, baseline runners,
contract tests, docs, report text, and small generated artifacts under
`outputs/step51_*` and `logs/step51_*`.

## 3. Explicit Non-Goals

Step 51 does not expand to 48^3 or 64^3, does not run multiple cycles, does not
activate free-body motion, does not persist displaced geometry or projected
state, does not update default solver state, and does not edit
`external/taichi_LBM3D`.

## 4. Transfer Config Validation

The transfer config validates `n_grid = 32`, `n_lbm_steps = 40`,
`mpm_substeps_per_lbm_step = 5`, `cycle_period_steps = 40`, transfer modes
`engineering` and `link_area_experimental`, and link-area scale bounds
`[0.25, 2.0]`. The generated validation result is `49/49` checks passed.

## 5. Transfer Comparison Matrix

The matrix contains 8 rows: 4 engineering rows and 4 link_area_experimental
rows. Each row records 40 diagnostic step records and keeps all values finite
and bounded. The matrix result is `row_count = 8`, `stable_count = 8`,
`step_count_per_row = 40`, `rho_min_global = 0.9982680917004111`,
`rho_max_global = 1.0017319082995888`, `lbm_max_v_global =
0.007042082995889119`, and `bb_link_count_min = 2658`.

## 6. Transfer Envelope Quality

Transfer envelope quality requires row count, step count, stability, projection,
wall velocity, transfer mode, link-area, diagnostic-only, and non-persistent
checks to pass.

## 7. Engineering Vs Link-Area Comparison

Each component row is compared across transfer modes. The acceptance condition
is finite, bounded, and comparable behavior; Step 51 does not claim that either
transfer mode is physically better. All 4 engineering-vs-link-area component
comparisons passed. The maximum hydro-force diagnostic delta is
`0.00042938357281110907`, and the maximum impulse-proxy diagnostic delta is
`0.017175342912444366`.

## 8. Link-Area Envelope

The link-area envelope checks that every link_area_experimental row is stable
and reports finite `area_scale` values within `[0.25, 2.0]`. The observed
link-area envelope is `area_scale_min_observed = 1.0` and
`area_scale_max_observed = 1.2094436532301125`.

## 9. Component Effect By Transfer

For each transfer mode, Step 51 checks geometry-only, wall-velocity-only, and
combined effects against the static baseline and against each other.

## 10. Cycle Closure By Transfer

Cycle closure compares phase `0.0` and closure phase `1.0` diagnostically for
both transfer modes. The closure is a diagnostic endpoint check only.

## 11. Step 50 Engineering Prefix Comparison

Step 51 engineering rows are compared against the accepted Step 50 engineering
rows over all 40 phases.

## 12. Mass Force Bounce-Back Transfer Envelope

The mass, force, bounce-back, and impulse-proxy envelope requires finite rho,
velocity, bounce-back link count, hydro force, impulse proxy, and area-scale
diagnostics across all 8 rows.

## 13. State Mutation Guard

The state guard checks stable original geometry and region-mask hashes, zero
default state mutation counts, zero persistent projected or displaced state,
zero persistent LBM solid velocity, and zero forbidden heavy outputs.

## 14. Step 50 Regression Guard

The Step 50 regression guard keeps the accepted Step 50 report, matrix, cycle
closure, state guard, and artifact-budget checks green.

## 15. Artifact Manifest Summary

The artifact manifest enforces zero large Step 51 files, no VTR output, no
particle NPY output, no displaced-particle output, no dense-displacement output,
no raw scan data, no private absolute user paths, and total repository artifact
size below the Step 51 budget. The manifest reports `file_count = 3744`,
`step51_file_count = 67`, `step51_total_size_mb = 1.1351757049560547`,
`total_size_mb = 214.30058479309082`, `large_file_count = 0`,
`step51_vtr_count = 0`, `step51_particle_npy_count = 0`, and
`geo_all_fluid_dat_count_added = 0`.

## 16. Verification Commands

Verification uses `D:\working\taichi\env\python.exe` for py_compile, every
Step 51 runner, full pytest, the Step 51 contract test, and git whitespace
checks. The Step 51 contract test passed `19 passed in 0.14s`, and the full
suite passed `592 passed in 5.94s`. `git diff --check` passed, and
`external/taichi_LBM3D` plus `data/real_geometry_candidates` remained
unchanged.

## 17. GitHub Sync Information

Target remote branch is `origin/main`. The final commit hash is reported in the
final response after push, because the hash cannot be embedded into the same
commit without changing it.

## 18. Acceptance Checklist

- [x] Step 51 detailed goal file exists
- [x] transfer config validation passes
- [x] n_grid is 32
- [x] n_lbm_steps is 40
- [x] mpm_substeps_per_lbm_step is 5
- [x] cycle_period_steps is 40
- [x] engineering transfer mode exists
- [x] link_area_experimental transfer mode exists
- [x] no 48^3 row is included
- [x] no 64^3 row is included
- [x] no multi-cycle row is included
- [x] link_area_scale_min is 0.25
- [x] link_area_scale_max is 2.0
- [x] all persistence flags are false
- [x] all default state update flags are false
- [x] modify_moving_bounceback_formula is false
- [x] transfer comparison matrix runs 8 rows
- [x] engineering row count is 4
- [x] link_area row count is 4
- [x] each row has 40 step records
- [x] all rows complete at least 40 LBM steps
- [x] all rows complete at least 200 MPM substeps
- [x] no NaN
- [x] no Inf
- [x] transfer envelope quality passes
- [x] engineering vs link_area comparison passes
- [x] link_area envelope passes
- [x] area_scale is finite
- [x] component effect by transfer passes
- [x] cycle closure by transfer passes
- [x] Step 50 engineering prefix comparison passes
- [x] mass/force/bounce-back transfer envelope passes
- [x] state mutation guard passes
- [x] Step 50 regression guard passes
- [x] default modes remain static or disabled
- [x] no default behavior change
- [x] no protected solver formula changes
- [x] no external/taichi_LBM3D edits
- [x] no physical propulsion or swimming claim
- [x] no Step 51 VTR or particle NPY outputs
- [x] Step 51 artifact budget passes
- [x] Step 51 contract test passes

## 19. Decision For Step 52

If Step 51 remains green after push, Step 52 may select one conservative
transfer mode for a 48^3 one-cycle feasibility probe with a static baseline and
combined row only. It should not expand grid size, transfer matrix size, and
cycle count at the same time.
