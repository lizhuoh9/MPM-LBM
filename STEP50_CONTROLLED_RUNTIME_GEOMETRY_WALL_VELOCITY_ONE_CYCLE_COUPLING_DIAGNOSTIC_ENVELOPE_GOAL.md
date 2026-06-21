# Step 50 Controlled Runtime Geometry Wall Velocity One-Cycle Coupling Diagnostic Envelope Goal

## 1. Objective

Implement Step 50: Controlled Runtime Geometry + Wall Velocity One-Cycle Coupling Diagnostic Envelope.

Step 50 extends the accepted Step 49 `32^3` twenty-step engineering-only diagnostic envelope to one full prescribed cycle at `32^3`. It remains opt-in, engineering-only, diagnostic-only, transient, non-persistent, and not a production moving-geometry solver or swimming simulation.

The Step 50 envelope must prove, with committed configs, source modules, baseline runners, tests, docs, reports, logs, and compact artifacts, that the existing transient runtime-geometry projection and wall-velocity application diagnostics can cover a complete prescribed cycle without changing default solver behavior or protected formulas.

## 2. Required Scope

Step 50 must implement an artifact-backed diagnostic surface with:

- `n_grid = 32`
- `n_lbm_steps = 40`
- `mpm_substeps_per_lbm_step = 5`
- `cycle_period_steps = 40`
- `closure_phase = 1.0`
- `coupling_mode = moving_boundary`
- `reaction_transfer_mode = engineering`
- `target_u_lbm = [0, 0, 0]` when represented in row descriptors
- `quality_check_enabled = true` when represented in row descriptors
- `quality_check_strict = true` when represented in row descriptors
- `write_vtk = false`
- `write_particles = false`
- no `link_area` row
- no `48^3` row
- no `64^3` row
- no persistent projected state
- no persistent displaced geometry
- no persistent LBM `solid_vel`
- no default driver/LBM/MPM/projection mutation
- no production boundary-link recomputation
- no moving bounce-back formula change

## 3. One-Cycle Phase Contract

The Step 50 runner matrix must use exactly this 40-entry phase sequence:

```text
[0.0, 0.025, 0.05, 0.075, 0.1,
 0.125, 0.15, 0.175, 0.2, 0.225,
 0.25, 0.275, 0.3, 0.325, 0.35,
 0.375, 0.4, 0.425, 0.45, 0.475,
 0.5, 0.525, 0.55, 0.575, 0.6,
 0.625, 0.65, 0.675, 0.7, 0.725,
 0.75, 0.775, 0.8, 0.825, 0.85,
 0.875, 0.9, 0.925, 0.95, 0.975]
```

The closure phase is not a 41st driver step. It must be a diagnostic endpoint:

```text
closure_phase = 1.0
```

The one-cycle contract is therefore:

- the 40 runner steps cover phases `0.0` through `0.975`
- cycle closure is checked by comparing diagnostic phase `0.0` against diagnostic phase `1.0`
- closure diagnostics do not claim physical cycle validation
- closure diagnostics do not persist state

## 4. Main Four-Row Matrix

The Step 50 matrix must contain exactly these rows:

```text
original_static_32_40step
runtime_geometry_only_32_40step
wall_velocity_only_32_40step
runtime_geometry_plus_wall_velocity_32_40step
```

Each row must complete:

- at least `40` LBM steps
- at least `200` MPM substeps
- exactly `40` step records
- no NaN
- no Inf
- finite density, velocity, projection, bounce-back, and force proxy diagnostics

Expected row semantics:

- `original_static_32_40step`: runtime projection off, wall velocity off, applied cell count remains `0`
- `runtime_geometry_only_32_40step`: runtime projection on, wall velocity off, active-cell count differs from the static baseline somewhere in the cycle
- `wall_velocity_only_32_40step`: runtime projection off, wall velocity on, applied cell count is positive and applied velocity is capped
- `runtime_geometry_plus_wall_velocity_32_40step`: runtime projection on, wall velocity on, both effects are present

## 5. Config Files

Create the umbrella config:

```text
configs/step50_runtime_geometry_wall_velocity_one_cycle_envelope.json
```

It must include:

- `one_cycle_envelope_id = step50_runtime_geometry_wall_velocity_one_cycle_envelope`
- `base_step49_config_path = configs/step49_runtime_geometry_wall_velocity_20step_envelope.json`
- `runtime_projection_config_path = configs/step45_runtime_geometry_projection_integration.json`
- `diagnostic_geometry_update_config_path = configs/step44_diagnostic_geometry_update.json`
- `wall_velocity_application_config_path = configs/step41_wall_velocity_application_scale_0050_64.json`
- `boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json`
- `geometry_config_path = configs/step30_squid_proxy_geometry.json`
- `region_config_path = configs/step30_squid_proxy_region_config.json`
- the exact Step 50 phase sequence
- `closure_phase = 1.0`
- all persistence, write, default-update, production-recompute, and formula-change flags set to `false`
- `diagnostic_only = true`

Create the row descriptor configs:

```text
configs/step50_original_static_32_40step.json
configs/step50_runtime_geometry_only_32_40step.json
configs/step50_wall_velocity_only_32_40step.json
configs/step50_runtime_geometry_plus_wall_velocity_32_40step.json
```

The row descriptors must not contain `link_area`, `48^3`, `64^3`, or any enabled persistence/output/default-update/formula-change flag.

## 6. Source Modules

Create:

```text
src/runtime_geometry_wall_velocity_one_cycle_config.py
src/runtime_geometry_wall_velocity_one_cycle_envelope.py
src/runtime_geometry_wall_velocity_one_cycle_diagnostics.py
src/runtime_geometry_wall_velocity_one_cycle_state_guard.py
```

### Config Module Requirements

The config module must:

- load and validate the umbrella JSON config
- verify `n_grid == 32`
- verify `n_lbm_steps == 40`
- verify `mpm_substeps_per_lbm_step == 5`
- verify `cycle_period_steps == 40`
- verify the phase sequence has exactly 40 entries
- verify the first phase is `0.0`
- verify the last runner phase is `0.975`
- verify `closure_phase == 1.0`
- verify phases are finite, bounded in `[0, 1]`, and nondecreasing
- verify `coupling_mode == moving_boundary`
- verify `reaction_transfer_mode == engineering`
- verify runtime geometry projection is enabled in the umbrella diagnostic
- verify wall velocity application is enabled in the umbrella diagnostic
- verify `diagnostic_only == true`
- verify every mutation/write/formula flag is false

### Envelope Module Requirements

The envelope module must:

- load Step 44 geometry-displacement inputs
- load Step 45 runtime projection config
- load Step 41 wall velocity application config
- project original and transient runtime geometry per phase
- build wall-velocity summaries per phase
- compute the four-row by forty-step diagnostic matrix
- include one diagnostic closure payload comparing phase `0.0` to `1.0`
- write CSV, JSON, and NPZ matrix outputs

Each step record must include:

- `row_name`
- `step_index`
- `phase`
- `cycle_index`
- `runtime_geometry_projection_enabled`
- `wall_velocity_application_enabled`
- `projected_mass`
- `active_cell_count`
- `active_cell_count_delta_from_original`
- `applied_cell_count`
- `max_applied_velocity_norm`
- `wall_velocity_cap_lbm`
- `rho_min`
- `rho_max`
- `lbm_max_v`
- `bb_link_count`
- `bb_max_correction`
- `hydro_force_max_norm`
- `has_nan`
- `has_inf`

### Diagnostics Module Requirements

The diagnostics module must provide:

- one-cycle envelope quality summary
- component-effect comparison
- phase-progression diagnostics
- contraction/refill segment diagnostics
- cycle-closure diagnostics
- mass/force/bounce-back envelope diagnostics
- Step 49 prefix comparison

The contraction segment is:

```text
phase <= 0.35
```

The refill segment is:

```text
phase > 0.35
```

The Step 49 prefix comparison must compare shared phases `0.0` through `0.5` against:

```text
outputs/step49_20step_envelope_matrix/twenty_step_envelope_matrix.json
```

If accumulated flow state would differ in a future real solver, this Step 50 comparison must remain limited to projection and wall-velocity diagnostic fields for matched phases.

### State Guard Requirements

The state guard must prove:

- original geometry hash remains stable
- region mask hash remains stable
- default driver state mutation count is `0`
- default LBM state mutation count is `0`
- default MPM state mutation count is `0`
- default projection state mutation count is `0`
- persistent projected state count is `0`
- persistent displaced geometry count is `0`
- persistent LBM `solid_vel` count is `0`
- displaced-particle output count is `0`
- dense-displacement output count is `0`
- VTR output count is `0`
- `geo_all_fluid_dat_count_added` is `0`

## 7. Baseline Runners

Create:

```text
baseline_tests/step50_common.py
baseline_tests/run_step50_one_cycle_config_validation.py
baseline_tests/run_step50_one_cycle_envelope_matrix.py
baseline_tests/run_step50_one_cycle_envelope_quality.py
baseline_tests/run_step50_component_effect_one_cycle_envelope.py
baseline_tests/run_step50_phase_progression_one_cycle_diagnostics.py
baseline_tests/run_step50_contraction_refill_segment_diagnostics.py
baseline_tests/run_step50_cycle_closure_diagnostics.py
baseline_tests/run_step50_mass_force_bounceback_one_cycle_envelope.py
baseline_tests/run_step50_step49_prefix_comparison.py
baseline_tests/run_step50_state_mutation_guard.py
baseline_tests/run_step50_step49_regression_guard.py
baseline_tests/run_step50_artifact_manifest.py
```

Every runner must write a small log marker under `logs/step50_*`.

## 8. Required Outputs

The config validation runner must produce:

```text
outputs/step50_one_cycle_config_validation/one_cycle_config_validation.csv
outputs/step50_one_cycle_config_validation/one_cycle_config_validation.json
```

The matrix runner must produce:

```text
outputs/step50_one_cycle_envelope_matrix/one_cycle_envelope_matrix.csv
outputs/step50_one_cycle_envelope_matrix/one_cycle_envelope_matrix.json
outputs/step50_one_cycle_envelope_matrix/one_cycle_envelope_matrix.npz
```

The quality runner must produce:

```text
outputs/step50_one_cycle_envelope_quality/one_cycle_envelope_quality.csv
outputs/step50_one_cycle_envelope_quality/one_cycle_envelope_quality.json
```

The component-effect runner must produce:

```text
outputs/step50_component_effect_one_cycle_envelope/component_effect_one_cycle_envelope.csv
outputs/step50_component_effect_one_cycle_envelope/component_effect_one_cycle_envelope.json
```

The phase-progression runner must produce:

```text
outputs/step50_phase_progression_one_cycle_diagnostics/phase_progression_one_cycle_diagnostics.csv
outputs/step50_phase_progression_one_cycle_diagnostics/phase_progression_one_cycle_diagnostics.json
```

The contraction/refill runner must produce:

```text
outputs/step50_contraction_refill_segment_diagnostics/contraction_refill_segment_diagnostics.csv
outputs/step50_contraction_refill_segment_diagnostics/contraction_refill_segment_diagnostics.json
```

The cycle-closure runner must produce:

```text
outputs/step50_cycle_closure_diagnostics/cycle_closure_diagnostics.csv
outputs/step50_cycle_closure_diagnostics/cycle_closure_diagnostics.json
```

The mass/force/bounce-back runner must produce:

```text
outputs/step50_mass_force_bounceback_one_cycle_envelope/mass_force_bounceback_one_cycle_envelope.csv
outputs/step50_mass_force_bounceback_one_cycle_envelope/mass_force_bounceback_one_cycle_envelope.json
```

The Step 49 prefix comparison runner must produce:

```text
outputs/step50_step49_prefix_comparison/step49_prefix_comparison.csv
outputs/step50_step49_prefix_comparison/step49_prefix_comparison.json
```

The state guard runner must produce:

```text
outputs/step50_state_mutation_guard/state_mutation_guard.csv
outputs/step50_state_mutation_guard/state_mutation_guard.json
```

The Step 49 regression guard must produce:

```text
outputs/step50_step49_regression_guard/step49_regression_guard.csv
outputs/step50_step49_regression_guard/step49_regression_guard.json
```

The artifact manifest runner must produce:

```text
outputs/step50_artifact_manifest/artifact_manifest.csv
outputs/step50_artifact_manifest/artifact_summary.csv
outputs/step50_artifact_manifest/artifact_summary.json
```

Final verification logs must include:

```text
logs/step50_contract_pytest.log
logs/step50_pytest.log
```

## 9. Contract Test

Create:

```text
tests/test_step50_runtime_geometry_wall_velocity_one_cycle_envelope_contract.py
```

The test must verify:

- required files exist
- required output artifacts exist
- required log markers exist
- the one-cycle config is valid
- the matrix has exactly four rows
- every row has exactly forty step records
- every row completes at least forty LBM steps and two hundred MPM substeps
- density and velocity bounds remain finite and conservative
- no NaN/Inf is present
- component effects are present and bounded
- phase progression passes
- contraction/refill segment diagnostics pass
- closure diagnostics pass
- mass/force/bounce-back diagnostics pass
- Step 49 prefix comparison passes with twenty matched phases
- Step 50 state mutation guard passes
- Step 49 regression guard passes
- default modes remain unchanged in `src/fsi_config.py`
- docs and report contain required scope phrases
- docs and report do not contain forbidden claims
- artifact budget passes
- report headings and acceptance checklist are complete
- no persistent geometry outputs are present
- no physical-validation claim is made
- protected formula files are not modified for Step 50

Protected formula files:

```text
src/lbm_fluid.py
src/projection.py
src/coupling.py
src/moving_boundary_coupling.py
src/wall_velocity_application.py
```

## 10. Required Documentation

Create:

```text
docs/50_controlled_runtime_geometry_wall_velocity_one_cycle_coupling_diagnostic_envelope.md
STEP50_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_CYCLE_COUPLING_DIAGNOSTIC_ENVELOPE_REPORT.md
```

Update:

```text
README.md
```

Required scope phrases for docs and report:

```text
Step 50 is controlled runtime geometry plus wall velocity one-cycle coupling diagnostic envelope.
Step 50 is opt-in and engineering-only.
Step 50 runs a 32^3 one-cycle diagnostic envelope.
Step 50 remains non-persistent.
Step 50 does not implement a production moving-geometry solver.
Step 50 does not validate real jet propulsion.
Step 50 does not implement squid swimming.
Step 50 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.
```

Forbidden claims for docs and report:

```text
production moving geometry is implemented
driver geometry is persistently updated
LBM solid_phi is persistently updated
LBM solid_vel is persistently updated
dynamic_solid is persistently updated
production boundary links are recomputed
moving bounce-back formula is changed
squid swimming is implemented
free-body motion is implemented
real jet validation
jet propulsion is validated
real squid simulation is validated
production-ready sharp-interface FSI
```

## 11. Step 50 Report Headings

The Step 50 report must contain:

```text
## 1. Goal
## 2. Files Created And Updated
## 3. Explicit Non-Goals
## 4. One-Cycle Config Validation
## 5. One-Cycle Envelope Matrix
## 6. One-Cycle Envelope Quality
## 7. Component Effect One-Cycle Envelope
## 8. Phase Progression One-Cycle Diagnostics
## 9. Contraction Refill Segment Diagnostics
## 10. Cycle Closure Diagnostics
## 11. Mass Force Bounce-Back One-Cycle Envelope
## 12. Step 49 Prefix Comparison
## 13. State Mutation Guard
## 14. Step 49 Regression Guard
## 15. Artifact Manifest Summary
## 16. Verification Commands
## 17. GitHub Sync Information
## 18. Acceptance Checklist
## 19. Decision For Step 51
```

The final report must not contain unchecked acceptance items.

## 12. Artifact Budget

The Step 50 artifact manifest must pass:

- `large_file_count == 0`
- `step50_total_size_mb < 30`
- `total_size_mb < 390`
- `step50_vtr_count == 0`
- `step50_particle_npy_count == 0`
- `step50_displaced_particle_output_count == 0`
- `step50_dense_displacement_output_count == 0`
- `raw_candidate_large_file_count == 0`
- `scan_data_file_count == 0`
- `private_absolute_path_count == 0`
- `geo_all_fluid_dat_count_added == 0`

## 13. Verification Commands

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\runtime_geometry_wall_velocity_one_cycle_config.py src\runtime_geometry_wall_velocity_one_cycle_envelope.py src\runtime_geometry_wall_velocity_one_cycle_diagnostics.py src\runtime_geometry_wall_velocity_one_cycle_state_guard.py baseline_tests\step50_common.py baseline_tests\run_step50_one_cycle_config_validation.py baseline_tests\run_step50_one_cycle_envelope_matrix.py baseline_tests\run_step50_one_cycle_envelope_quality.py baseline_tests\run_step50_component_effect_one_cycle_envelope.py baseline_tests\run_step50_phase_progression_one_cycle_diagnostics.py baseline_tests\run_step50_contraction_refill_segment_diagnostics.py baseline_tests\run_step50_cycle_closure_diagnostics.py baseline_tests\run_step50_mass_force_bounceback_one_cycle_envelope.py baseline_tests\run_step50_step49_prefix_comparison.py baseline_tests\run_step50_state_mutation_guard.py baseline_tests\run_step50_step49_regression_guard.py baseline_tests\run_step50_artifact_manifest.py tests\test_step50_runtime_geometry_wall_velocity_one_cycle_envelope_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step50_one_cycle_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step50_one_cycle_envelope_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step50_one_cycle_envelope_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step50_component_effect_one_cycle_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step50_phase_progression_one_cycle_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step50_contraction_refill_segment_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step50_cycle_closure_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step50_mass_force_bounceback_one_cycle_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step50_step49_prefix_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step50_state_mutation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step50_step49_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step50_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step50_runtime_geometry_wall_velocity_one_cycle_envelope_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q

git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

The final artifact manifest must be regenerated after `logs/step50_contract_pytest.log` and `logs/step50_pytest.log` exist.

## 14. Acceptance Checklist

- [ ] Step 50 detailed goal file exists.
- [ ] One-cycle config validation passes.
- [ ] `n_grid` is `32`.
- [ ] `n_lbm_steps` is `40`.
- [ ] `mpm_substeps_per_lbm_step` is `5`.
- [ ] `cycle_period_steps` is `40`.
- [ ] Phase sequence has exactly `40` entries.
- [ ] Phase sequence starts at `0.0`.
- [ ] Phase sequence ends at `0.975`.
- [ ] `closure_phase` is `1.0`.
- [ ] Coupling mode is `moving_boundary`.
- [ ] Reaction transfer mode is `engineering`.
- [ ] No `link_area` row is included.
- [ ] No `48^3` row is included.
- [ ] No `64^3` row is included.
- [ ] `persist_displaced_geometry` is false.
- [ ] `persist_projected_state` is false.
- [ ] `persist_lbm_solid_vel` is false.
- [ ] `write_displaced_particles` is false.
- [ ] `write_dense_displacement_field` is false.
- [ ] `write_vtk` is false.
- [ ] `write_particles` is false.
- [ ] `update_default_driver_geometry` is false.
- [ ] `update_default_lbm_state` is false.
- [ ] `update_default_mpm_state` is false.
- [ ] `update_default_projection_state` is false.
- [ ] `update_dynamic_solid_persistently` is false.
- [ ] `recompute_production_boundary_links` is false.
- [ ] `modify_moving_bounceback_formula` is false.
- [ ] One-cycle envelope matrix runs exactly four rows.
- [ ] Each row has exactly forty step records.
- [ ] Original static row passes.
- [ ] Runtime geometry only row passes.
- [ ] Wall velocity only row passes.
- [ ] Runtime geometry plus wall velocity row passes.
- [ ] All rows complete at least `40` LBM steps.
- [ ] All rows complete at least `200` MPM substeps.
- [ ] `rho_min > 0.95`.
- [ ] `rho_max < 1.05`.
- [ ] `lbm_max_v < 0.1`.
- [ ] `projected_mass > 0`.
- [ ] `active_cell_count > 0`.
- [ ] `bb_link_count > 0`.
- [ ] No NaN.
- [ ] No Inf.
- [ ] Geometry-only row shows nonzero projection-envelope effect.
- [ ] Wall-velocity-only row shows positive applied velocity.
- [ ] Combined row has runtime geometry projection and wall velocity application.
- [ ] One-cycle envelope quality passes.
- [ ] Component-effect envelope passes.
- [ ] Phase-progression diagnostics pass.
- [ ] Contraction/refill segment diagnostics pass.
- [ ] Cycle closure diagnostics pass.
- [ ] Mass/force/bounce-back envelope passes.
- [ ] Step 49 prefix comparison passes.
- [ ] State mutation guard passes.
- [ ] Original geometry hash remains stable.
- [ ] Region mask hash remains stable.
- [ ] Default driver state mutation count is `0`.
- [ ] Default LBM state mutation count is `0`.
- [ ] Default MPM state mutation count is `0`.
- [ ] Persistent projected state count is `0`.
- [ ] Persistent displaced geometry count is `0`.
- [ ] Persistent LBM solid velocity count is `0`.
- [ ] Displaced-particle output count is `0`.
- [ ] Dense-displacement output count is `0`.
- [ ] VTR output count is `0`.
- [ ] `geo_all_fluid_dat_count_added` is `0`.
- [ ] Step 49 regression guard passes.
- [ ] Default geometry modes remain static/disabled.
- [ ] Default wall-velocity modes remain static/disabled.
- [ ] No default behavior changes.
- [ ] No moving bounce-back formula changes.
- [ ] No LBM collision formula changes.
- [ ] No MPM constitutive formula changes.
- [ ] No projection formula changes.
- [ ] No `external/taichi_LBM3D` edits.
- [ ] No propulsion-validation claim.
- [ ] No swimming claim.
- [ ] No real-squid validation claim.
- [ ] No Step 50 `.vtr` outputs.
- [ ] No Step 50 particle `.npy` outputs.
- [ ] Artifact large-file count is `0`.
- [ ] Step 50 output total-size budget passes.
- [ ] Repo artifact summary total size stays below `390 MB`.
- [ ] `logs/step50_pytest.log` exists.
- [ ] Focused Step 50 contract test passes.
- [ ] Full pytest passes.
- [ ] `git diff --check` passes.
- [ ] Staged whitespace check passes.
- [ ] Pre-push hook passes.
- [ ] Step 50 artifacts are pushed to `origin/main`.

## 15. Commit And Push

Commit message:

```text
test: add step50 runtime geometry wall velocity one cycle envelope
```

Push target:

```text
origin/main
```

Report the final commit hash, pushed branch, focused test count, full pytest count, pre-push result, and final artifact manifest summary.
