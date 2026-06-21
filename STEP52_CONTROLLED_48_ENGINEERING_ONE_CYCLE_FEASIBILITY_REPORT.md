# Step 52 Controlled 48 Engineering One-Cycle Feasibility Report

## 1. Goal

Step 52 is a controlled 48^3 engineering one-cycle diagnostic feasibility probe.
Step 52 runs exactly two engineering rows: static and runtime geometry plus wall velocity.
Step 52 remains diagnostic-only and non-persistent.
Step 52 does not validate real jet propulsion.
Step 52 does not implement squid swimming.
Step 52 does not change moving bounce-back formulas.
Step 52 is not grid convergence validation.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

The detailed goal is in `STEP52_CONTROLLED_48_ENGINEERING_ONE_CYCLE_FEASIBILITY_GOAL.md`.

## 2. Files Created And Updated

Step 52 adds a detailed goal, a 48^3 engineering umbrella config, two row
configs, diagnostic wrapper source, baseline runners, contract tests, docs,
report text, and small generated artifacts under `outputs/step52_*` and
`logs/step52_*`.

## 3. Explicit Non-Goals

Step 52 does not add a 64^3 run, multiple cycles, link_area_experimental 48^3
rows, runtime-only or wall-only rows, free-body motion, body trajectory, squid
swimming, persistent displaced geometry, persistent projected state, persistent
LBM solid velocity, default state mutation, external solver edits, formula
changes, or heavy visualization outputs.

## 4. 48 Config Validation

The config validation passes `45/45` checks. The accepted umbrella config uses
`n_grid = 48`, `n_lbm_steps = 40`, `mpm_substeps_per_lbm_step = 5`,
`cycle_period_steps = 40`, `closure_phase = 1.0`, one `engineering` transfer
mode, and forty phases from `0.0` to `0.975`.

## 5. 48 Feasibility Matrix

The matrix contains exactly two rows: one static row and one runtime geometry
plus wall velocity row. Each row records 40 diagnostic step records and
completes 40 LBM steps with 200 MPM substeps. The matrix summary is
`row_count = 2`, `stable_count = 2`, `step_count_per_row = 40`,
`rho_min_global = 0.9982878216689931`, `rho_max_global =
1.0017121783310068`, `lbm_max_v_global = 0.007021783310068709`,
`active_cell_count_min = 644`, and `bb_link_count_min = 3864`.

## 6. 48 Feasibility Quality

The quality summary passes row count, static row, combined row, step count,
stability, projection, transfer mode, component effect, diagnostic-only, and
non-persistent checks. The combined row is distinguishable from the static row
through runtime-geometry active-cell deltas and wall-velocity application.

## 7. 48 Vs Step 51 Engineering Scaling Comparison

The Step 52 combined row is compared only against the accepted Step 51
engineering combined row. The scaling comparison passes as diagnostic-only:
all ratios are finite, `active_cell_count_48 = 648`,
`active_cell_count_32 = 648`, `active_cell_count_growth_observed = false`,
`active_cell_count_non_decreasing = true`, `applied_cell_count_48 = 2136`,
`applied_cell_count_32 = 648`, and `applied_cell_count_ratio_48_vs_32 =
3.2962962962962963`.

This is not a grid-convergence result. The projected active-cell summary did
not grow at 48^3, and the report keeps that observation explicit.

## 8. Cycle Closure

Cycle closure passes for both rows at `closure_phase = 1.0`. The diagnostic
closure summary reports `row_count = 2`, `closure_pass_count = 2`,
`phase0_phase1_projected_mass_delta_max = 0.0`,
`phase0_phase1_active_cell_delta_max = 0`, and
`phase0_phase1_applied_velocity_delta_max = 0.00035388087013428016` within the
configured wall-velocity closure tolerance `0.0005`.

## 9. Mass Force Bounce-Back Envelope

The mass, force, bounce-back, and impulse-proxy envelope passes for both rows.
The envelope summary reports `rho_min_global = 0.9982878216689931`,
`rho_max_global = 1.0017121783310068`, `bb_link_count_min = 3864`,
`bb_link_count_max = 3888`, `bb_max_correction_global =
0.007021783310068709`, `hydro_force_max_norm_global =
4.58601088618242e-05`, and `impulse_proxy_max_norm_global =
0.001834404354472968`.

## 10. State Mutation Guard

The state mutation guard passes. It reports stable original-geometry and
region-mask hashes, zero default driver/LBM/MPM/projection state mutations,
zero persistent projected state, zero persistent displaced geometry, zero
persistent LBM solid velocity, and zero forbidden heavy output counts.

## 11. Step 51 Regression Guard

The Step 51 regression guard passes `10/10` checks. The accepted Step 51 report,
eight-row matrix, link-area envelope, state guard, and artifact budget remain
present and green.

## 12. Artifact Manifest Summary

The Step 52 artifact manifest passes. It reports `file_count = 3798`,
`step52_file_count = 50`, `step52_total_size_mb < 0.552`,
`total_size_mb < 214.911`, `large_file_count = 0`,
`step52_vtr_count = 0`, `step52_particle_npy_count = 0`,
`step52_displaced_particle_output_count = 0`,
`step52_dense_displacement_output_count = 0`, `scan_data_file_count = 0`,
`raw_candidate_large_file_count = 0`, `private_absolute_path_count = 0`, and
`geo_all_fluid_dat_count_added = 0`.

## 13. Verification Commands

Verification uses `D:\working\taichi\env\python.exe` for py_compile, every
Step 52 runner, the Step 52 contract test, full pytest, and git whitespace
checks. The Step 52 contract test passed 12 tests, and the full suite passed
604 tests. The pytest output is recorded in `logs/step52_contract_pytest.log`
and `logs/step52_pytest.log`.

## 14. GitHub Sync Information

Target remote branch is `origin/main`. The final commit hash is reported in the
final response after push, because embedding the hash into the same commit would
change the hash.

## 15. Acceptance Checklist

- [x] Step 52 detailed goal file exists
- [x] config validation passes
- [x] n_grid is 48
- [x] n_lbm_steps is 40
- [x] mpm_substeps_per_lbm_step is 5
- [x] cycle_period_steps is 40
- [x] closure_phase is 1.0
- [x] phase count is 40
- [x] only engineering transfer mode is used
- [x] no link_area_experimental row is included
- [x] no 64^3 row is included
- [x] no multi-cycle row is included
- [x] all persistence flags are false
- [x] all default state update flags are false
- [x] modify_moving_bounceback_formula is false
- [x] feasibility matrix has exactly two rows
- [x] static row count is one
- [x] combined row count is one
- [x] each row has 40 step records
- [x] all rows complete at least 40 LBM steps
- [x] all rows complete at least 200 MPM substeps
- [x] no NaN
- [x] no Inf
- [x] rho and velocity diagnostics are bounded
- [x] projected mass, active cell count, and bounce-back link count are positive
- [x] combined row differs from static row diagnostically
- [x] 48 vs Step 51 scaling comparison passes as diagnostic-only
- [x] active-cell non-decrease is reported
- [x] applied wall-cell support growth is reported
- [x] cycle closure passes
- [x] mass/force/bounce-back envelope passes
- [x] state mutation guard passes
- [x] Step 51 regression guard passes
- [x] artifact budget passes
- [x] no physical propulsion, swimming, grid-convergence, or production-readiness claim

## 16. Decision For Step 53

Step 53 should not treat Step 52 as physical validation. A later step may choose
between more refined 48^3 diagnostics and longer-cycle preparation, but it
should not simultaneously expand grid size, cycle count, transfer-mode matrix,
and solver behavior.
