# Step 47 Controlled Runtime Geometry Wall Velocity Short-Step Coupling Envelope Goal

## 1. Objective

Implement Step 47 as a controlled runtime geometry plus wall velocity short-step coupling envelope.

Step 47 must extend the accepted Step 46 one-step combined smoke into a guarded `32^3`, five-step, engineering-only envelope. It must combine transient runtime geometry projection with opt-in `solid_vel` wall-velocity application across a short phase sequence while keeping default solver behavior static and disabled.

Step 47 is diagnostic only. It must not activate a broad moving-geometry run, a production geometry-update path, free-body motion, squid swimming, propulsion validation, jet-validation claims, real-squid claims, or final solver-readiness claims.

The implementation must be artifact-backed, contract-first, small, and pushed to `origin/main` when complete.

## 2. Required Step Name

Use this exact Step naming in files, docs, report, logs, and tests:

```text
Step 47 Controlled Runtime Geometry + Wall Velocity Short-Step Coupling Envelope
```

Use these filename stems:

```text
STEP47_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_SHORT_STEP_COUPLING_ENVELOPE_GOAL.md
STEP47_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_SHORT_STEP_COUPLING_ENVELOPE_REPORT.md
docs/47_controlled_runtime_geometry_wall_velocity_short_step_coupling_envelope.md
```

## 3. Relationship To Accepted Prior Steps

Step 47 must treat Step 46 as accepted and must preserve its boundaries:

- Step 46 already proved a four-row `32^3`, phase-`0.35`, one-step combined smoke.
- Step 46 left `geometry_motion_mode`, `geometry_motion_application_mode`, `boundary_motion_mode`, and `wall_velocity_application_mode` defaulting to static or disabled.
- Step 46 used transient runtime projection and opt-in wall velocity only.
- Step 46 did not persist projected geometry, displaced geometry, or LBM `solid_vel`.
- Step 46 did not change solver, projection, coupling, wall-velocity, or moving-boundary formulas.

Step 47 must add a Step 46 regression guard that reads accepted Step 46 artifacts and proves they still pass after the new work.

## 4. Strict Scope

Allowed scope:

- `32^3` only.
- `5` LBM steps only.
- `5` MPM substeps per LBM step.
- `25` total MPM substeps per row.
- `moving_boundary` coupling mode only.
- `engineering` reaction transfer mode only.
- Four component rows:
  - `original_static_32_5step`
  - `runtime_geometry_only_32_5step`
  - `wall_velocity_only_32_5step`
  - `runtime_geometry_plus_wall_velocity_32_5step`
- A short phase sequence derived from the accepted Step 32 early-contraction schedule:
  - step `0`: phase `0.0`
  - step `1`: phase `0.05`
  - step `2`: phase `0.1`
  - step `3`: phase `0.2`
  - step `4`: phase `0.35`
- Transient runtime displaced-copy projection per step.
- Opt-in `solid_vel` wall-velocity application per step.
- Small CSV, JSON, NPZ, and log artifacts.
- Docs, report, and artifact-backed contract tests.

Forbidden scope:

- No `48^3` or `64^3` coupled moving-geometry rows.
- No `link_area` or `link_area_experimental` rows.
- No 40-step cycle.
- No complete moving-geometry cycle.
- No persistent displaced geometry.
- No persistent projected state.
- No persistent LBM `solid_phi` update.
- No persistent LBM `solid_vel` update.
- No persistent `dynamic_solid` update.
- No default driver state mutation.
- No default LBM state mutation.
- No default MPM state mutation.
- No default projection state mutation.
- No broad boundary-link recomputation path.
- No moving bounce-back formula change.
- No LBM collision or streaming formula change.
- No MPM constitutive formula change.
- No projection formula change.
- No coupler formula change.
- No wall-velocity formula change.
- No body trajectory model.
- No free-body dynamics.
- No animal-model validation claim.
- No propulsion-validation claim.
- No final solver-readiness claim.
- No `external/taichi_LBM3D` edits.
- No raw real-geometry or scan-data files.
- No displaced particle output files.
- No dense displacement-field output files.
- No VTR output files.
- No Step 47 `geo_all_fluid_*.dat` artifacts.

## 5. Required Config Files

Create the umbrella config:

```text
configs/step47_runtime_geometry_wall_velocity_short_step_envelope.json
```

It must include:

```json
{
  "short_step_envelope_id": "step47_runtime_geometry_wall_velocity_short_step_envelope",
  "base_coupling_smoke_config_path": "configs/step46_runtime_geometry_wall_velocity_coupling_smoke.json",
  "runtime_projection_config_path": "configs/step45_runtime_geometry_projection_integration.json",
  "diagnostic_geometry_update_config_path": "configs/step44_diagnostic_geometry_update.json",
  "wall_velocity_application_config_path": "configs/step41_wall_velocity_application_scale_0050_64.json",
  "boundary_motion_config_path": "configs/step34_boundary_motion_interface_prescribed_kinematic.json",
  "geometry_config_path": "configs/step30_squid_proxy_geometry.json",
  "region_config_path": "configs/step30_squid_proxy_region_config.json",
  "n_grid": 32,
  "n_lbm_steps": 5,
  "mpm_substeps_per_lbm_step": 5,
  "phase_sequence": [0.0, 0.05, 0.1, 0.2, 0.35],
  "coupling_mode": "moving_boundary",
  "reaction_transfer_mode": "engineering",
  "enable_runtime_geometry_projection": true,
  "enable_wall_velocity_application": true,
  "persist_displaced_geometry": false,
  "persist_projected_state": false,
  "persist_lbm_solid_vel": false,
  "write_displaced_particles": false,
  "write_dense_displacement_field": false,
  "write_vtk": false,
  "write_particles": false,
  "update_default_driver_geometry": false,
  "update_default_lbm_state": false,
  "update_default_mpm_state": false,
  "update_default_projection_state": false,
  "update_dynamic_solid_persistently": false,
  "recompute_production_boundary_links": false,
  "modify_moving_bounceback_formula": false,
  "diagnostic_only": true,
  "scope_note": "32^3 five-step engineering-only runtime geometry plus wall velocity envelope"
}
```

Create four row descriptor configs:

```text
configs/step47_original_static_32_5step.json
configs/step47_runtime_geometry_only_32_5step.json
configs/step47_wall_velocity_only_32_5step.json
configs/step47_runtime_geometry_plus_wall_velocity_32_5step.json
```

Each row descriptor must explicitly record:

- `row_name`
- `n_grid = 32`
- `n_lbm_steps = 5`
- `mpm_substeps_per_lbm_step = 5`
- `phase_sequence = [0.0, 0.05, 0.1, 0.2, 0.35]`
- `coupling_mode = "moving_boundary"`
- `reaction_transfer_mode = "engineering"`
- booleans for runtime geometry and wall velocity
- `quality_check_enabled = true`
- `quality_check_strict = true`
- `write_vtk = false`
- `write_particles = false`
- `target_u_lbm = [0.0, 0.0, 0.0]`
- `diagnostic_only = true`
- all persistence and broad-activation flags false

## 6. Required Source Files

Create:

```text
src/runtime_geometry_wall_velocity_envelope_config.py
src/runtime_geometry_wall_velocity_envelope.py
src/runtime_geometry_wall_velocity_envelope_diagnostics.py
src/runtime_geometry_wall_velocity_envelope_state_guard.py
```

### 6.1 Config Module

`runtime_geometry_wall_velocity_envelope_config.py` must define an immutable dataclass for the Step 47 config and validation helpers.

Validation must prove:

- `short_step_envelope_id` equals `step47_runtime_geometry_wall_velocity_short_step_envelope`.
- All referenced prior-step config files exist.
- `n_grid == 32`.
- `n_lbm_steps == 5`.
- `mpm_substeps_per_lbm_step == 5`.
- `phase_sequence == [0.0, 0.05, 0.1, 0.2, 0.35]`.
- Every phase is finite and within `[0.0, 1.0]`.
- `coupling_mode == "moving_boundary"`.
- `reaction_transfer_mode == "engineering"`.
- Runtime projection and wall velocity are enabled in the umbrella diagnostic.
- `diagnostic_only == true`.
- Every persistence, output, state-update, broad recomputation, and formula-modification flag is false.

### 6.2 Envelope Module

`runtime_geometry_wall_velocity_envelope.py` must build a four-row by five-step matrix without importing the full driver stack.

Required public functions:

```python
load_short_step_envelope_inputs(config_path)
build_step_phase_sequence(config)
run_short_step_row(config, descriptor, projection_rows, original_projection_rows, wall_summary_by_phase)
run_short_step_envelope_matrix(config_path)
summarize_short_step_envelope_matrix(rows)
write_short_step_envelope_rows(rows, csv_path, json_path, npz_path, summary=None)
```

Each output row must summarize the row-level envelope and include:

- `row_name`
- `n_grid`
- `n_lbm_steps`
- `mpm_substeps_per_lbm_step`
- `phase_sequence`
- `runtime_geometry_projection_enabled`
- `wall_velocity_application_enabled`
- `completed_lbm_steps`
- `total_mpm_substeps`
- `projected_mass_min`
- `projected_mass_max`
- `active_cell_count_min`
- `active_cell_count_max`
- `active_cell_count_delta_from_original_max`
- `applied_cell_count_min`
- `applied_cell_count_max`
- `max_applied_velocity_norm`
- `wall_velocity_cap_lbm`
- `rho_min_global`
- `rho_max_global`
- `lbm_max_v_global`
- `bb_link_count_min`
- `bb_max_correction_global`
- `hydro_force_max_norm_global`
- `has_nan`
- `has_inf`
- `diagnostic_only`
- `persist_projected_state`
- `persist_displaced_geometry`
- `persist_lbm_solid_vel`
- `complete_cycle_claim`
- `production_geometry_claim`
- `stable`
- `step_records`
- `notes`

Each `step_records` item must include:

- `step_index`
- `phase`
- `runtime_geometry_projection_enabled`
- `wall_velocity_application_enabled`
- `projected_mass`
- `active_cell_count`
- `active_cell_count_delta_from_original`
- `applied_cell_count`
- `max_applied_velocity_norm`
- `rho_min`
- `rho_max`
- `lbm_max_v`
- `bb_link_count`
- `bb_max_correction`
- `hydro_force_max_norm`
- `has_nan`
- `has_inf`

### 6.3 Diagnostics Module

`runtime_geometry_wall_velocity_envelope_diagnostics.py` must define:

```python
summarize_short_step_envelope_quality(rows)
compare_short_step_components(rows)
summarize_phase_progression(rows)
mass_force_bounceback_envelope(rows)
summary_rows(summary)
```

Diagnostics must prove:

- Four rows exist.
- Each row has five steps.
- All rows are stable.
- Projection values are finite and positive.
- Wall-velocity rows have positive applied cells and positive applied velocity.
- The combined row has both runtime geometry and wall velocity enabled.
- Runtime geometry has a nonzero active-cell envelope effect.
- Wall velocity has a nonzero velocity effect.
- Phase progression has the expected sequence and nonzero phase response from `0.0` to `0.35`.
- Density, velocity, bounce-back, and hydro-force proxy metrics remain bounded and finite.
- Diagnostic-only and no-persistent-state flags are true.

### 6.4 State Guard Module

`runtime_geometry_wall_velocity_envelope_state_guard.py` must prove:

- Original geometry hash is stable.
- Region mask hash is stable.
- Default driver state mutation count is `0`.
- Default LBM state mutation count is `0`.
- Default MPM state mutation count is `0`.
- Default projection state mutation count is `0`.
- Persistent projected state count is `0`.
- Persistent displaced geometry count is `0`.
- Displaced particle output count is `0`.
- Dense displacement output count is `0`.
- VTR output count is `0`.
- Step 47 `geo_all_fluid_*.dat` count is `0`.

## 7. Required Runner Files

Create:

```text
baseline_tests/step47_common.py
baseline_tests/run_step47_short_step_config_validation.py
baseline_tests/run_step47_short_step_envelope_matrix.py
baseline_tests/run_step47_short_step_envelope_quality.py
baseline_tests/run_step47_component_effect_envelope.py
baseline_tests/run_step47_phase_progression_diagnostics.py
baseline_tests/run_step47_mass_force_bounceback_envelope.py
baseline_tests/run_step47_state_mutation_guard.py
baseline_tests/run_step47_step46_regression_guard.py
baseline_tests/run_step47_artifact_manifest.py
```

Every runner must write an OK marker to `logs/step47_*.log`.

Required OK markers:

```text
[OK] Step 47 short-step config validation finished
[OK] Step 47 short-step envelope matrix finished
[OK] Step 47 short-step envelope quality finished
[OK] Step 47 component effect envelope finished
[OK] Step 47 phase progression diagnostics finished
[OK] Step 47 mass force bounce-back envelope finished
[OK] Step 47 state mutation guard finished
[OK] Step 47 Step 46 regression guard finished
[OK] Step 47 artifact manifest finished
```

## 8. Required Output Artifacts

Create these outputs:

```text
outputs/step47_short_step_config_validation/short_step_config_validation.csv
outputs/step47_short_step_config_validation/short_step_config_validation.json
outputs/step47_short_step_envelope_matrix/short_step_envelope_matrix.csv
outputs/step47_short_step_envelope_matrix/short_step_envelope_matrix.json
outputs/step47_short_step_envelope_matrix/short_step_envelope_matrix.npz
outputs/step47_short_step_envelope_quality/short_step_envelope_quality.csv
outputs/step47_short_step_envelope_quality/short_step_envelope_quality.json
outputs/step47_component_effect_envelope/component_effect_envelope.csv
outputs/step47_component_effect_envelope/component_effect_envelope.json
outputs/step47_phase_progression_diagnostics/phase_progression_diagnostics.csv
outputs/step47_phase_progression_diagnostics/phase_progression_diagnostics.json
outputs/step47_mass_force_bounceback_envelope/mass_force_bounceback_envelope.csv
outputs/step47_mass_force_bounceback_envelope/mass_force_bounceback_envelope.json
outputs/step47_state_mutation_guard/state_mutation_guard.csv
outputs/step47_state_mutation_guard/state_mutation_guard.json
outputs/step47_step46_regression_guard/step46_regression_guard.csv
outputs/step47_step46_regression_guard/step46_regression_guard.json
outputs/step47_artifact_manifest/artifact_manifest.csv
outputs/step47_artifact_manifest/artifact_summary.csv
outputs/step47_artifact_manifest/artifact_summary.json
```

Also create final verification logs:

```text
logs/step47_contract_pytest.log
logs/step47_pytest.log
```

## 9. Required Contract Test

Create:

```text
tests/test_step47_runtime_geometry_wall_velocity_short_step_envelope_contract.py
```

The contract test must include at least these checks:

- required files and outputs exist
- Step 47 config is valid
- short-step envelope matrix is valid
- short-step envelope quality is valid
- component-effect envelope is valid
- phase-progression diagnostics are valid
- mass/force/bounce-back envelope is valid
- state mutation guard is valid
- Step 46 regression guard is valid
- default modes remain unchanged
- docs contain required scope phrases
- docs and report do not contain forbidden overclaims
- artifact budget is valid
- report acceptance checklist is complete
- no persistent geometry outputs exist
- no complete-cycle or production-geometry claims are made
- protected formula files do not reference Step 47 implementation strings

Required scope phrases:

```text
Step 47 is controlled runtime geometry plus wall velocity short-step coupling envelope.
Step 47 is opt-in and engineering-only.
Step 47 runs a 32^3 five-step envelope.
Step 47 does not run a full-cycle moving-geometry simulation.
Step 47 does not persist displaced geometry.
Step 47 does not persist projected state.
Step 47 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.
```

Forbidden wording in user-facing docs/report:

- Do not say that complete-cycle moving geometry is implemented.
- Do not say that production moving geometry is implemented.
- Do not say that driver geometry is persistently updated.
- Do not say that LBM `solid_phi` is persistently updated.
- Do not say that `dynamic_solid` is persistently updated.
- Do not say that broad boundary links are recomputed.
- Do not say that the moving bounce-back formula is changed.
- Do not say that squid swimming is implemented.
- Do not say that free-body motion is implemented.
- Do not claim jet validation.
- Do not claim real-squid validation.
- Do not claim production sharp-interface FSI readiness.

## 10. README And Report Requirements

Update `README.md`:

- Add Step 47 to the implemented list.
- Add a Step 47 boundary section after Step 46.
- State that Step 47 is opt-in, engineering-only, `32^3`, five-step, diagnostic, and non-persistent.
- State that default modes remain static or disabled.
- State that no solver formula changes are introduced.

Create `docs/47_controlled_runtime_geometry_wall_velocity_short_step_coupling_envelope.md`.

Create `STEP47_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_SHORT_STEP_COUPLING_ENVELOPE_REPORT.md` with sections:

```text
## 1. Goal
## 2. Files Created And Updated
## 3. Explicit Non-Goals
## 4. Short-Step Config Validation
## 5. Short-Step Envelope Matrix
## 6. Short-Step Envelope Quality
## 7. Component Effect Envelope
## 8. Phase Progression Diagnostics
## 9. Mass Force Bounce-Back Envelope
## 10. State Mutation Guard
## 11. Step 46 Regression Guard
## 12. Artifact Manifest Summary
## 13. Verification Commands
## 14. GitHub Sync Information
## 15. Acceptance Checklist
## 16. Decision For Step 48
```

The report must have no unchecked `- [ ]` items after completion.

## 11. Artifact Manifest Budget

`run_step47_artifact_manifest.py` must enforce:

- `large_file_count == 0`
- `step47_total_size_mb < 15`
- repository `total_size_mb < 360`
- `step47_vtr_count == 0`
- `step47_particle_npy_count == 0`
- `step47_displaced_particle_output_count == 0`
- `step47_dense_displacement_output_count == 0`
- `raw_candidate_large_file_count == 0`
- `scan_data_file_count == 0`
- `private_absolute_path_count == 0`
- `geo_all_fluid_dat_count_added == 0`

The manifest must be refreshed after final pytest logs are written.

## 12. Verification Commands

Run these before commit:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\runtime_geometry_wall_velocity_envelope_config.py src\runtime_geometry_wall_velocity_envelope.py src\runtime_geometry_wall_velocity_envelope_diagnostics.py src\runtime_geometry_wall_velocity_envelope_state_guard.py baseline_tests\step47_common.py baseline_tests\run_step47_short_step_config_validation.py baseline_tests\run_step47_short_step_envelope_matrix.py baseline_tests\run_step47_short_step_envelope_quality.py baseline_tests\run_step47_component_effect_envelope.py baseline_tests\run_step47_phase_progression_diagnostics.py baseline_tests\run_step47_mass_force_bounceback_envelope.py baseline_tests\run_step47_state_mutation_guard.py baseline_tests\run_step47_step46_regression_guard.py baseline_tests\run_step47_artifact_manifest.py tests\test_step47_runtime_geometry_wall_velocity_short_step_envelope_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step47_short_step_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step47_short_step_envelope_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step47_short_step_envelope_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step47_component_effect_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step47_phase_progression_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step47_mass_force_bounceback_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step47_state_mutation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step47_step46_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step47_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step47_runtime_geometry_wall_velocity_short_step_envelope_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

The ECC pre-push hook must also pass.

## 13. Acceptance Checklist

- [ ] Step 47 detailed goal file exists.
- [ ] Short-step config validation passes.
- [ ] `n_grid` is `32`.
- [ ] `n_lbm_steps` is `5`.
- [ ] `mpm_substeps_per_lbm_step` is `5`.
- [ ] Phase sequence is `0.0`, `0.05`, `0.1`, `0.2`, `0.35`.
- [ ] Coupling mode is `moving_boundary`.
- [ ] Reaction transfer mode is `engineering`.
- [ ] No `link_area` row is included.
- [ ] No `48^3` row is included.
- [ ] Persistent displaced geometry is false.
- [ ] Persistent projected state is false.
- [ ] Persistent LBM `solid_vel` is false.
- [ ] Displaced-particle writes are false.
- [ ] Dense displacement-field writes are false.
- [ ] VTK writes are false.
- [ ] Particle writes are false.
- [ ] Default driver state update is false.
- [ ] Default LBM state update is false.
- [ ] Default MPM state update is false.
- [ ] Default projection state update is false.
- [ ] Persistent dynamic solid update is false.
- [ ] Broad boundary-link recomputation is false.
- [ ] Moving bounce-back formula modification is false.
- [ ] Short-step envelope matrix has four rows.
- [ ] Each row has five step records.
- [ ] Original static row passes.
- [ ] Runtime geometry-only row passes.
- [ ] Wall-velocity-only row passes.
- [ ] Runtime geometry plus wall-velocity row passes.
- [ ] All rows complete at least five LBM steps.
- [ ] All rows complete at least twenty-five MPM substeps.
- [ ] `rho_min_global > 0.95`.
- [ ] `rho_max_global < 1.05`.
- [ ] `lbm_max_v_global < 0.1`.
- [ ] Projected mass is positive.
- [ ] Active-cell count is positive.
- [ ] Bounce-back link count is positive.
- [ ] No NaN is detected.
- [ ] No Inf is detected.
- [ ] Runtime geometry-only row shows nonzero projection envelope effect.
- [ ] Wall-velocity-only row shows positive applied velocity.
- [ ] Combined row has runtime geometry projection and wall velocity.
- [ ] Short-step envelope quality passes.
- [ ] Component-effect envelope passes.
- [ ] Phase-progression diagnostics pass.
- [ ] Mass/force/bounce-back envelope passes.
- [ ] State mutation guard passes.
- [ ] Original geometry hash remains stable.
- [ ] Region mask hash remains stable.
- [ ] Default driver state mutation count is `0`.
- [ ] Default LBM state mutation count is `0`.
- [ ] Default MPM state mutation count is `0`.
- [ ] Default projection state mutation count is `0`.
- [ ] Persistent projected state count is `0`.
- [ ] Persistent displaced geometry count is `0`.
- [ ] Displaced particle output count is `0`.
- [ ] Dense displacement output count is `0`.
- [ ] VTR output count is `0`.
- [ ] Step 47 `geo_all_fluid_*.dat` count is `0`.
- [ ] Step 46 regression guard passes.
- [ ] Default geometry motion mode remains static.
- [ ] Default geometry motion application mode remains disabled.
- [ ] Default boundary motion mode remains static.
- [ ] Default wall velocity application mode remains disabled.
- [ ] No default behavior change is introduced.
- [ ] No moving bounce-back formula changes are introduced.
- [ ] No LBM collision formula changes are introduced.
- [ ] No MPM constitutive formula changes are introduced.
- [ ] No projection formula changes are introduced.
- [ ] `external/taichi_LBM3D` remains untouched.
- [ ] No jet-validation claim is made.
- [ ] No squid-swimming claim is made.
- [ ] No real-squid validation claim is made.
- [ ] No Step 47 VTR outputs exist.
- [ ] No Step 47 particle NPY outputs exist.
- [ ] Artifact large-file count is `0`.
- [ ] Step 47 output total-size budget passes.
- [ ] Repository artifact summary total size remains under `360` MB.
- [ ] `logs/step47_pytest.log` exists.
- [ ] Full pytest passes.
- [ ] Step 47 contract test passes.
- [ ] `git diff --check` passes.
- [ ] Staged whitespace check passes.
- [ ] ECC pre-push hook passes.
- [ ] Step 47 artifacts are pushed to `origin/main`.

## 14. Expected Commit

Use a concise conventional commit message:

```text
test: add step47 runtime geometry wall velocity envelope
```

## 15. Completion Criteria

The task is complete only after:

- All Step 47 configs, source, runners, tests, docs, reports, logs, and outputs are present.
- The Step 47 contract test passes.
- Full pytest passes.
- Artifact manifest is refreshed after final pytest logs.
- `git diff --check` and `git diff --cached --check` pass.
- Work is committed.
- ECC pre-push hook passes.
- Commit is pushed to `origin/main`.
- The final response reports commit hash, remote branch, pass counts, and any residual risk.
