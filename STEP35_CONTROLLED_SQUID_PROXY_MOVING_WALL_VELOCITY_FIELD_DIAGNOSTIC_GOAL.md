# Step 35 Goal: Controlled Squid Proxy Moving-Wall Velocity Field Diagnostic Contract

## Objective

Implement Step 35 as a controlled squid proxy moving-wall velocity field diagnostic contract. Step 35 converts the accepted Step 34 diagnostic-only boundary-motion interface into grid-level and region-level wall velocity diagnostics that can be inspected and quality-gated before any future LBM application work.

Step 35 must remain diagnostic-only. It must generate, validate, aggregate, and report moving-wall velocity field diagnostics derived from the Step 32 kinematics schedule, Step 33 motion mapping, Step 30 squid proxy regions, and Step 34 boundary-motion interface. It must not apply wall velocity to LBM populations, must not change moving bounce-back formulas, must not mutate driver integration paths, and must not introduce new FSI physics.

Step 35 is the acceptance gate for a future Step 36 experimental moving-wall LBM application smoke. Step 35 itself is not Step 36.

## Required Scope Statements

- Step 35 is controlled squid proxy moving-wall velocity field diagnostics.
- Step 35 generates diagnostic wall velocity fields only.
- Step 35 derives diagnostics from the accepted Step 34 boundary-motion interface.
- Step 35 samples the Step 32 kinematics schedule and Step 33 motion mapping.
- Step 35 distinguishes mantle outer wall, mantle cavity proxy, and funnel outlet proxy contributions.
- Step 35 validates finite, bounded, deterministic wall velocity summaries.
- Step 35 writes small CSV and JSON artifacts only.
- Step 35 does not apply moving wall velocity to LBM.
- Step 35 does not update LBM populations.
- Step 35 does not change moving bounce-back formulas.
- Step 35 does not modify LBM, MPM, projection, coupler, or driver execution formulas.
- Step 35 does not implement a jet model.
- Step 35 does not implement mantle actuation, funnel actuation, or squid swimming.
- Step 35 does not implement new FSI physics.
- The default boundary_motion_mode remains static.
- The default quality_check_enabled remains false.
- The default quality_check_strict remains false.
- The default reaction_transfer_mode remains engineering.

## Explicit Non-Goals

Do not implement or claim any of the following:

- LBM population update.
- Moving bounce-back formula change.
- `step_moving_bounceback` modification.
- Wall velocity applied to fluid.
- Jet model.
- Fluid forcing from mantle or funnel motion.
- Mantle contraction driver behavior.
- Funnel actuation driver behavior.
- Free-body motion.
- Squid swimming.
- Real squid validation.
- New FSI physics.
- New coupling formula.
- Changes to `PenaltyFSICoupler3D`.
- Changes to `MovingBoundaryFSICoupler3D`.
- Changes to `LinkAreaMovingBoundaryCoupler3D`.
- Changes to LBM formulas.
- Changes to MPM constitutive formulas.
- Changes to projection formulas.
- Production sharp-interface FSI.
- Production mesh repair.
- Automatic remeshing.
- Two-phase flow.
- Contact-angle physics.
- Sparse storage.
- Edits under `external/taichi_LBM3D`.

Allowed Step 35 work:

- Wall velocity diagnostic config schema.
- CPU/NumPy wall velocity diagnostic generation.
- Grid-cell and region-tagged wall velocity summaries.
- Coverage diagnostics.
- Schedule and motion-mapping consistency checks.
- Repeatability hashes.
- No-LBM-update guard.
- Step 34 regression guard.
- Documentation, report, tests, logs, and small committed artifacts.

## Inputs

Step 35 must reuse these accepted inputs:

- `configs/step34_boundary_motion_interface_prescribed_kinematic.json`
- `configs/step33_squid_proxy_motion_mapping.json`
- `configs/step33_squid_proxy_motion_sampling.json`
- `configs/step32_squid_proxy_kinematics_schedule.json`
- `configs/step32_squid_proxy_kinematics_sampling.json`
- `configs/step30_squid_proxy_region_config.json`
- `configs/step30_squid_proxy_geometry.json`
- `outputs/step33_motion_mapping/motion_mapping.csv`
- `outputs/step33_motion_mapping/motion_mapping.json`
- `outputs/step34_boundary_motion_interface_report/boundary_motion_interface_report.json`

The implementation may regenerate Step 35 artifacts from source configs and accepted Step 32/33 APIs, but it must not require rerunning fluid/solid driver cases.

## Config Contract

Add:

- `configs/step35_squid_proxy_wall_velocity_field.json`
- `configs/step35_squid_proxy_wall_velocity_sampling.json`

The field config must include:

```json
{
  "velocity_field_id": "step35_squid_proxy_wall_velocity_diagnostic",
  "boundary_motion_config_path": "configs/step34_boundary_motion_interface_prescribed_kinematic.json",
  "motion_mapping_config_path": "configs/step33_squid_proxy_motion_mapping.json",
  "schedule_config_path": "configs/step32_squid_proxy_kinematics_schedule.json",
  "region_config_path": "configs/step30_squid_proxy_region_config.json",
  "geometry_config_path": "configs/step30_squid_proxy_geometry.json",
  "grid_sizes": [32, 48, 64],
  "phase_samples": [0.0, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0],
  "tracked_regions": ["mantle_outer", "mantle_cavity_proxy", "funnel_outlet_proxy"],
  "wall_velocity_model": "diagnostic_proxy",
  "funnel_axis": "+y",
  "max_velocity_norm_allowed": 1.0,
  "write_dense_field": false,
  "write_sparse_samples": false,
  "apply_to_lbm": false,
  "lbm_population_update_enabled": false,
  "moving_bounceback_update_enabled": false,
  "driver_integration_enabled": false,
  "jet_model_enabled": false,
  "actuation_enabled": false,
  "deterministic": true,
  "scope_note": "velocity field diagnostics only; no LBM population update"
}
```

Validation requirements:

- All referenced source paths exist.
- `grid_sizes` are positive integers and exactly `[32, 48, 64]`.
- `phase_samples` are finite values in `[0, 1]` and exactly `[0.0, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0]`.
- `tracked_regions` include exactly `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy`.
- `wall_velocity_model` is `diagnostic_proxy`.
- `funnel_axis` is `+y`.
- `max_velocity_norm_allowed` is finite and positive.
- `write_dense_field` is false.
- `write_sparse_samples` is false.
- `apply_to_lbm` is false.
- `lbm_population_update_enabled` is false.
- `moving_bounceback_update_enabled` is false.
- `driver_integration_enabled` is false.
- `jet_model_enabled` is false.
- `actuation_enabled` is false.
- `deterministic` is true.

## Source Module Contract

Add `src/wall_velocity_config.py`.

Required behavior:

- Define an immutable Step 35 wall velocity config object.
- Load JSON config files.
- Resolve paths relative to the repository root.
- Emit a serializable dictionary.
- Validate all source paths, sample sets, region sets, and diagnostic-only flags.
- Return row-level validation records for artifact generation.
- Raise clear `ValueError` or `FileNotFoundError` on invalid configs.

Add `src/wall_velocity_field.py`.

Required behavior:

- Load Step 35 config and accepted Step 32/33 inputs.
- Generate sparse diagnostic summary rows, not dense vector fields.
- Generate rows for `3 grid sizes * 7 phases * 3 regions = 63` rows.
- Use deterministic CPU/NumPy calculations only.
- Assign region-specific velocity directions and magnitudes from Step 33 motion mapping rows:
  - `mantle_outer` uses the mantle radial velocity proxy.
  - `mantle_cavity_proxy` uses the cavity volume-rate proxy as a diagnostic radial or axial proxy.
  - `funnel_outlet_proxy` uses the funnel aperture/outlet-axis proxy.
- Compute active wall-cell coverage from Step 30 region definitions and the requested grid size.
- Compute finite and bounded velocity statistics.
- Preserve `diagnostic_only=true` and all LBM/driver execution flags as false in every row.
- Provide deterministic hash helpers for repeatability checks.

Suggested public functions:

- `load_wall_velocity_inputs(config_path)`
- `interpolate_motion_rows_to_phase(motion_rows, phase)`
- `compute_wall_velocity_summary(config, phase, grid_size, region_id, motion_rows, region_points)`
- `generate_wall_velocity_field_rows(config)`
- `summarize_wall_velocity_rows(rows)`
- `write_wall_velocity_rows(rows, csv_path, json_path)`

Required output row fields:

- `grid_size`
- `phase`
- `region_id`
- `active_cell_count`
- `sample_point_count`
- `velocity_norm_min`
- `velocity_norm_max`
- `velocity_norm_mean`
- `velocity_x_mean`
- `velocity_y_mean`
- `velocity_z_mean`
- `displacement_norm_max`
- `source_motion_model`
- `finite_pass`
- `bounds_pass`
- `diagnostic_only`
- `apply_to_lbm`
- `lbm_population_update_enabled`
- `moving_bounceback_update_enabled`

Add `src/wall_velocity_quality.py`.

Required behavior:

- Analyze generated wall velocity rows against the Step 35 config.
- Verify expected row count.
- Verify finite values.
- Verify max velocity norm is bounded by config.
- Verify positive active-cell coverage.
- Verify diagnostic-only flags.
- Verify no LBM update, no moving bounce-back update, and no driver integration.

Suggested public function:

- `analyze_wall_velocity_quality(rows, config)`

Add `src/wall_velocity_consistency.py`.

Required behavior:

- Compare Step 35 wall velocity rows to Step 33 motion mapping rows.
- Check phase coverage.
- Check region coverage.
- Check mantle velocity finite and nonzero on moving phases.
- Check cavity rate sign consistency.
- Check funnel rate sign consistency.
- Return row-level consistency records and a summary.

Suggested public function:

- `compare_wall_velocity_to_motion_mapping(wall_velocity_rows, motion_mapping_rows)`

## Baseline Runner Contract

Add:

- `baseline_tests/step35_common.py`
- `baseline_tests/run_step35_wall_velocity_config_validation.py`
- `baseline_tests/run_step35_generate_wall_velocity_field.py`
- `baseline_tests/run_step35_wall_velocity_quality.py`
- `baseline_tests/run_step35_wall_velocity_repeatability.py`
- `baseline_tests/run_step35_motion_velocity_consistency.py`
- `baseline_tests/run_step35_grid_coverage_diagnostics.py`
- `baseline_tests/run_step35_no_lbm_update_guard.py`
- `baseline_tests/run_step35_step34_regression_guard.py`
- `baseline_tests/run_step35_artifact_manifest.py`

The runners must write logs with stable success markers under `logs/step35_*.log`.

### Config Validation Runner

Output:

- `outputs/step35_wall_velocity_config_validation/wall_velocity_config_validation.csv`
- `outputs/step35_wall_velocity_config_validation/wall_velocity_config_validation.json`
- `logs/step35_wall_velocity_config_validation.log`

Acceptance:

- `validation_pass == true`
- `grid_size_count == 3`
- `phase_sample_count == 7`
- `tracked_region_count == 3`
- `write_dense_field == false`
- `write_sparse_samples == false`
- `apply_to_lbm == false`
- `lbm_population_update_enabled == false`
- `moving_bounceback_update_enabled == false`
- `driver_integration_enabled == false`
- `jet_model_enabled == false`
- `actuation_enabled == false`

### Wall Velocity Field Generation Runner

Output:

- `outputs/step35_wall_velocity_field/wall_velocity_field.csv`
- `outputs/step35_wall_velocity_field/wall_velocity_field.json`
- `logs/step35_generate_wall_velocity_field.log`

Acceptance:

- `row_count == 63`
- `finite_pass == true`
- `bounds_pass == true`
- `active_cell_count > 0` for every row
- `velocity_norm_max` is finite for every row
- `velocity_norm_mean` is finite for every row
- `diagnostic_only == true` for every row
- `apply_to_lbm == false` for every row
- `lbm_population_update_enabled == false` for every row

### Wall Velocity Quality Runner

Output:

- `outputs/step35_wall_velocity_quality/wall_velocity_quality.csv`
- `outputs/step35_wall_velocity_quality/wall_velocity_quality.json`
- `logs/step35_wall_velocity_quality.log`

Acceptance:

- `quality_pass == true`
- `row_count_pass == true`
- `finite_pass == true`
- `bounds_pass == true`
- `coverage_pass == true`
- `max_velocity_norm_pass == true`
- `diagnostic_only_pass == true`
- `no_lbm_update_pass == true`
- `no_bounceback_update_pass == true`
- `no_driver_integration_pass == true`

### Repeatability Runner

Generate the wall velocity field twice and compare stable hashes.

Output:

- `outputs/step35_wall_velocity_repeatability/wall_velocity_repeatability.csv`
- `outputs/step35_wall_velocity_repeatability/wall_velocity_repeatability.json`
- `logs/step35_wall_velocity_repeatability.log`

Acceptance:

- `row_count_first == 63`
- `row_count_second == 63`
- `velocity_field_hash_first == velocity_field_hash_second`
- `mantle_velocity_hash_first == mantle_velocity_hash_second`
- `cavity_velocity_hash_first == cavity_velocity_hash_second`
- `funnel_velocity_hash_first == funnel_velocity_hash_second`
- `repeatability_pass == true`

### Motion-Velocity Consistency Runner

Output:

- `outputs/step35_motion_velocity_consistency/motion_velocity_consistency.csv`
- `outputs/step35_motion_velocity_consistency/motion_velocity_consistency.json`
- `logs/step35_motion_velocity_consistency.log`

Acceptance:

- `row_count >= 21`
- `phase_match_pass == true`
- `region_match_pass == true`
- `mantle_velocity_consistency_pass == true`
- `cavity_rate_sign_consistency_pass == true`
- `funnel_rate_sign_consistency_pass == true`
- `consistency_pass == true`

### Grid Coverage Diagnostics Runner

Output:

- `outputs/step35_grid_coverage_diagnostics/grid_coverage_diagnostics.csv`
- `outputs/step35_grid_coverage_diagnostics/grid_coverage_diagnostics.json`
- `logs/step35_grid_coverage_diagnostics.log`

Acceptance:

- `row_count == 9`
- `coverage_pass == true` for every row
- `active_cell_count_min > 0`
- `velocity_nonzero_phase_count > 0` for each region

### No LBM Update Guard Runner

This is the core Step 35 safety guard.

Output:

- `outputs/step35_no_lbm_update_guard/no_lbm_update_guard.csv`
- `outputs/step35_no_lbm_update_guard/no_lbm_update_guard.json`
- `logs/step35_no_lbm_update_guard.log`

Required checks:

- No Step 35 source writes to `lbm.f`, `lbm.f_next`, or population aliases.
- No Step 35 source calls or modifies moving bounce-back update routines.
- No Step 35 source mutates dynamic solid state.
- No Step 35 source mutates projector state.
- No Step 35 config enables driver integration.
- No Step 35 output claims wall velocity was written to LBM state.

Acceptance:

- `guard_pass == true`
- `lbm_population_update_count == 0`
- `moving_bounceback_update_count == 0`
- `driver_integration_enabled_count == 0`
- `apply_to_lbm_count == 0`

### Step 34 Regression Guard Runner

Inputs:

- `STEP34_CONTROLLED_SQUID_PROXY_BOUNDARY_MOTION_DRIVER_INTERFACE_REPORT.md`
- `outputs/step34_boundary_motion_interface_report/boundary_motion_interface_report.json`
- `outputs/step34_noop_state_guard/noop_state_guard.json`
- `outputs/step34_artifact_manifest/artifact_summary.json`

Acceptance:

- Step 34 report exists.
- Step 34 `no_op_pass == true`.
- Step 34 no-op state guard `pass_count == 2`.
- Step 34 quality report count remains `6`.
- Step 34 `large_file_count == 0`.
- Step 34 `.vtr` count remains `0`.
- Step 34 particle `.npy` count remains `0`.

### Artifact Manifest Runner

Acceptance:

- `large_file_count == 0`
- `step35_total_size_mb < 5`
- `total_size_mb < 210`
- `step35_vtr_count == 0`
- `step35_particle_npy_count == 0`
- `raw_candidate_large_file_count == 0`
- `scan_data_file_count == 0`
- `private_absolute_path_count == 0`

## Test Contract

Add `tests/test_step35_wall_velocity_field_diagnostics_contract.py` with these contract checks:

- `test_step35_required_artifacts_exist`
- `test_step35_wall_velocity_config_is_valid`
- `test_step35_wall_velocity_field_is_valid`
- `test_step35_wall_velocity_quality_is_valid`
- `test_step35_wall_velocity_repeatability_is_valid`
- `test_step35_motion_velocity_consistency_is_valid`
- `test_step35_grid_coverage_diagnostics_is_valid`
- `test_step35_no_lbm_update_guard_is_valid`
- `test_step35_step34_regression_guard_is_valid`
- `test_step35_default_modes_remain_unchanged`
- `test_step35_docs_scope_and_forbidden_claims_are_valid`
- `test_step35_artifact_budget_is_valid`
- `test_step35_report_acceptance_complete`

Forbidden claims in docs and reports:

- `moving wall velocity is applied to LBM`
- `LBM populations are updated by wall velocity`
- `moving bounce-back formula is changed`
- `jet model is implemented`
- `squid actuation is implemented`
- `squid swimming is implemented`
- `mantle contraction is integrated into the driver`
- `funnel actuation is integrated into the driver`
- `real squid simulation is validated`
- `production-ready sharp-interface FSI`
- `final solver readiness`
- `implements two_phase`
- `implements contact_angle`

Required scope phrases in docs and reports:

- `Step 35 is controlled squid proxy moving-wall velocity field diagnostics.`
- `Step 35 generates diagnostic wall velocity fields only.`
- `Step 35 does not apply moving wall velocity to LBM.`
- `Step 35 does not update LBM populations.`
- `Step 35 does not change moving bounce-back formulas.`
- `Step 35 does not implement a jet model.`
- `Step 35 does not implement squid swimming.`
- `Step 35 does not implement new FSI physics.`
- `The default boundary_motion_mode remains static.`
- `The default quality_check_enabled remains false.`
- `The default quality_check_strict remains false.`
- `The default reaction_transfer_mode remains engineering.`

## Documentation And Report Contract

Add:

- `docs/35_controlled_squid_proxy_wall_velocity_field_diagnostics.md`
- `STEP35_CONTROLLED_SQUID_PROXY_MOVING_WALL_VELOCITY_FIELD_DIAGNOSTIC_REPORT.md`

The report must contain:

1. Goal
2. Files Created And Updated
3. Explicit Non-Goals
4. Wall Velocity Config Validation
5. Generated Wall Velocity Field
6. Wall Velocity Quality
7. Wall Velocity Repeatability
8. Motion-Velocity Consistency
9. Grid Coverage Diagnostics
10. No LBM Update Guard
11. Step 34 Regression Guard
12. Artifact Manifest Summary
13. Verification Commands
14. GitHub Sync Information
15. Acceptance Checklist
16. Decision For Step 36

The Step 36 decision must state that a future LBM boundary-motion application smoke may only be guarded, opt-in, short-step, and experimental.

## Verification Contract

Run and capture logs for:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\wall_velocity_config.py src\wall_velocity_field.py src\wall_velocity_quality.py src\wall_velocity_consistency.py baseline_tests\step35_common.py baseline_tests\run_step35_wall_velocity_config_validation.py baseline_tests\run_step35_generate_wall_velocity_field.py baseline_tests\run_step35_wall_velocity_quality.py baseline_tests\run_step35_wall_velocity_repeatability.py baseline_tests\run_step35_motion_velocity_consistency.py baseline_tests\run_step35_grid_coverage_diagnostics.py baseline_tests\run_step35_no_lbm_update_guard.py baseline_tests\run_step35_step34_regression_guard.py baseline_tests\run_step35_artifact_manifest.py tests\test_step35_wall_velocity_field_diagnostics_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_wall_velocity_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_generate_wall_velocity_field.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_wall_velocity_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_wall_velocity_repeatability.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_motion_velocity_consistency.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_grid_coverage_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_no_lbm_update_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_step34_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step35_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q *> logs\step35_pytest.log
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step35_wall_velocity_field_diagnostics_contract.py -q

git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

The trusted full pytest result must be recorded in `logs/step35_pytest.log`.

## Acceptance Checklist

- [ ] Wall velocity config validation passes.
- [ ] Grid sizes are exactly `32`, `48`, and `64`.
- [ ] Phase samples are valid and exactly `0.0`, `0.1`, `0.2`, `0.35`, `0.5`, `0.75`, and `1.0`.
- [ ] Tracked regions include `mantle_outer`.
- [ ] Tracked regions include `mantle_cavity_proxy`.
- [ ] Tracked regions include `funnel_outlet_proxy`.
- [ ] `write_dense_field` is false.
- [ ] `write_sparse_samples` is false.
- [ ] `apply_to_lbm` is false.
- [ ] `lbm_population_update_enabled` is false.
- [ ] `moving_bounceback_update_enabled` is false.
- [ ] `driver_integration_enabled` is false.
- [ ] `jet_model_enabled` is false.
- [ ] `actuation_enabled` is false.
- [ ] Generated wall velocity field has 63 rows.
- [ ] Velocity fields are finite.
- [ ] Velocity fields are bounded.
- [ ] Active cell coverage is positive.
- [ ] `diagnostic_only` is true for all rows.
- [ ] Wall velocity quality passes.
- [ ] Wall velocity repeatability hash passes.
- [ ] Mantle velocity hash repeats.
- [ ] Cavity velocity hash repeats.
- [ ] Funnel velocity hash repeats.
- [ ] Motion-velocity consistency passes.
- [ ] Grid coverage diagnostics pass.
- [ ] No-LBM-update guard passes.
- [ ] LBM population update count is 0.
- [ ] Moving bounce-back update count is 0.
- [ ] Step 34 regression guard passes.
- [ ] Default `boundary_motion_mode` remains static.
- [ ] Default `quality_check_enabled` remains false.
- [ ] Default `quality_check_strict` remains false.
- [ ] Default `reaction_transfer_mode` remains engineering.
- [ ] No moving wall velocity application.
- [ ] No LBM population update.
- [ ] No moving bounce-back formula changes.
- [ ] No jet model.
- [ ] No mantle contraction driver behavior.
- [ ] No funnel actuation driver behavior.
- [ ] No squid swimming claim.
- [ ] No real squid validation claim.
- [ ] No new FSI physics.
- [ ] No LBM formula changes.
- [ ] No MPM constitutive formula changes.
- [ ] No projection formula changes.
- [ ] No `external/taichi_LBM3D` edits.
- [ ] No Step 35 `.vtr` outputs.
- [ ] No Step 35 particle `.npy` outputs.
- [ ] Artifact `large_file_count == 0`.
- [ ] Step 35 output total-size budget passes.
- [ ] Repo artifact summary `total_size_mb < 210`.
- [ ] `logs/step35_pytest.log` exists.
- [ ] Full pytest passes.
- [ ] Step 35 contract test passes.
- [ ] `git diff --check` passes.
- [ ] Staged whitespace check passes.
- [ ] Pre-push hook passes.
- [ ] Step 35 artifacts are pushed to `origin/main`.

## Commit Contract

Use this commit message:

```text
test: add step35 wall velocity field diagnostics
```

Push target:

```text
origin/main
```
