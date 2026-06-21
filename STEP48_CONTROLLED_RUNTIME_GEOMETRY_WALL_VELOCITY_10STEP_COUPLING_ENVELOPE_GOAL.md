# Step 48 Controlled Runtime Geometry + Wall Velocity 10-Step Coupling Envelope Goal

## 1. Source And Intent

Step 47 is accepted. Step 48 must extend the accepted Step 47 `32^3` five-step engineering-only envelope to a `32^3` ten-step engineering-only diagnostic envelope. Step 48 stays opt-in, transient, non-persistent, and diagnostic-only.

Step 48 must not turn this into a production moving-geometry solver path. It must not enable full-cycle motion, persistent geometry updates, persistent projected state, production boundary-link recomputation, `link_area`, real animal-model validation, swimming, or external solver edits.

The work must be artifact-backed. Claims in the report must be supported by small JSON/CSV/NPZ/log artifacts and by pytest contract coverage.

## 2. Required Scope

Step 48 must prove all of the following:

- A `32^3` ten-step runtime geometry plus wall velocity envelope can be evaluated in a bounded engineering-only diagnostic window.
- Each row completes at least `10` LBM steps and `50` MPM substeps.
- The phase sequence covers early-to-contraction-end motion without running a full prescribed cycle.
- Runtime geometry projection diagnostics remain finite and bounded across the phase sequence.
- Wall velocity application diagnostics remain finite and capped across the phase sequence.
- The combined row keeps both runtime geometry projection and wall velocity application active.
- Mass, density span, LBM max velocity, bounce-back count/correction, and hydrodynamic-force proxy diagnostics remain stable.
- The state guard proves original geometry, region masks, default driver/LBM/MPM/projection state, projected state, displaced geometry, LBM solid velocity, VTR/particle/dense-displacement outputs, and `geo_all_fluid_*.dat` artifacts are not persistently mutated or produced.
- Step 47 artifacts still pass the regression guard after Step 48 is added.

## 3. Explicit Non-Goals

Step 48 must not add or claim:

- full prescribed-cycle motion;
- 40-step moving-geometry run;
- `48^3` or `64^3` coupled moving-geometry run;
- `link_area` transfer;
- production moving-geometry integration;
- persistent displaced geometry;
- persistent projected state;
- persistent LBM `solid_phi` update;
- persistent LBM `solid_vel` update;
- persistent `dynamic_solid` update;
- production boundary-link recomputation;
- moving bounce-back formula changes;
- LBM collision or streaming formula changes;
- MPM constitutive formula changes;
- projection formula changes;
- coupler formula changes;
- wall velocity formula changes;
- free-body motion;
- body trajectory integration;
- swimming;
- real-jet or real animal-model validation;
- production sharp-interface FSI readiness;
- edits under `external/taichi_LBM3D`;
- raw real geometry or scan data;
- particle, dense-field, VTR, or `geo_all_fluid_*.dat` outputs for Step 48.

## 4. Matrix Contract

Step 48 must add and evaluate exactly these four rows:

```text
original_static_32_10step
runtime_geometry_only_32_10step
wall_velocity_only_32_10step
runtime_geometry_plus_wall_velocity_32_10step
```

All rows must use:

```text
n_grid = 32
n_lbm_steps = 10
mpm_substeps_per_lbm_step = 5
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
target_u_lbm = [0, 0, 0]
write_vtk = false
write_particles = false
diagnostic_only = true
```

The required phase sequence is:

```text
[0.0, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35]
```

This sequence intentionally stops at contraction-end. It is a ten-sample envelope, not a full-cycle run.

## 5. Required Configs

Create:

```text
configs/step48_runtime_geometry_wall_velocity_10step_envelope.json
configs/step48_original_static_32_10step.json
configs/step48_runtime_geometry_only_32_10step.json
configs/step48_wall_velocity_only_32_10step.json
configs/step48_runtime_geometry_plus_wall_velocity_32_10step.json
```

The umbrella config must contain:

```json
{
  "ten_step_envelope_id": "step48_runtime_geometry_wall_velocity_10step_envelope",
  "base_step47_config_path": "configs/step47_runtime_geometry_wall_velocity_short_step_envelope.json",
  "runtime_projection_config_path": "configs/step45_runtime_geometry_projection_integration.json",
  "diagnostic_geometry_update_config_path": "configs/step44_diagnostic_geometry_update.json",
  "wall_velocity_application_config_path": "configs/step41_wall_velocity_application_scale_0050_64.json",
  "boundary_motion_config_path": "configs/step34_boundary_motion_interface_prescribed_kinematic.json",
  "geometry_config_path": "configs/step30_squid_proxy_geometry.json",
  "region_config_path": "configs/step30_squid_proxy_region_config.json",
  "n_grid": 32,
  "n_lbm_steps": 10,
  "mpm_substeps_per_lbm_step": 5,
  "phase_sequence": [0.0, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35],
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
  "scope_note": "32^3 ten-step engineering-only runtime geometry plus wall velocity envelope"
}
```

The exact config may include additional diagnostic metadata, but it must preserve the fields and values above.

## 6. Required Source Modules

Create:

```text
src/runtime_geometry_wall_velocity_10step_config.py
src/runtime_geometry_wall_velocity_10step_envelope.py
src/runtime_geometry_wall_velocity_10step_diagnostics.py
src/runtime_geometry_wall_velocity_10step_state_guard.py
```

The config module must validate:

- `ten_step_envelope_id == "step48_runtime_geometry_wall_velocity_10step_envelope"`;
- `n_grid == 32`;
- `n_lbm_steps == 10`;
- `mpm_substeps_per_lbm_step == 5`;
- phase sequence equals the required ten values;
- phase sequence values are finite and in `[0, 1]`;
- `coupling_mode == "moving_boundary"`;
- `reaction_transfer_mode == "engineering"`;
- runtime geometry projection and wall velocity application are enabled in the umbrella config;
- every persistence, write, default-update, production-recompute, and formula-change flag is false;
- `diagnostic_only is true`;
- referenced Step 47, Step 45, Step 44, Step 41, Step 34, and Step 30 configs exist.

The envelope module must run the four-row matrix and write row summaries without mutating default solver state. Per-step records must include:

```text
row_name
step_index
phase
runtime_geometry_projection_enabled
wall_velocity_application_enabled
projected_mass
active_cell_count
active_cell_count_delta_from_original
applied_cell_count
max_applied_velocity_norm
wall_velocity_cap_lbm
rho_min
rho_max
lbm_max_v
bb_link_count
bb_max_correction
hydro_force_max_norm
has_nan
has_inf
```

The diagnostics module must provide:

- ten-step envelope quality summary;
- component-effect comparisons;
- phase-progression diagnostics;
- mass/force/bounce-back diagnostics;
- Step 47 prefix comparison for phases `0.0`, `0.05`, `0.1`, `0.2`, and `0.35`.

The state guard must prove Step 48 does not persist geometry, projected state, default state, or large geometry artifacts.

## 7. Required Baseline Runners

Create:

```text
baseline_tests/step48_common.py
baseline_tests/run_step48_10step_config_validation.py
baseline_tests/run_step48_10step_envelope_matrix.py
baseline_tests/run_step48_10step_envelope_quality.py
baseline_tests/run_step48_component_effect_10step_envelope.py
baseline_tests/run_step48_phase_progression_10step_diagnostics.py
baseline_tests/run_step48_mass_force_bounceback_10step_envelope.py
baseline_tests/run_step48_step47_prefix_comparison.py
baseline_tests/run_step48_state_mutation_guard.py
baseline_tests/run_step48_step47_regression_guard.py
baseline_tests/run_step48_artifact_manifest.py
```

Each runner must write a small log marker on success.

## 8. Required Outputs

Create these output artifacts:

```text
outputs/step48_10step_config_validation/ten_step_config_validation.csv
outputs/step48_10step_config_validation/ten_step_config_validation.json
outputs/step48_10step_envelope_matrix/ten_step_envelope_matrix.csv
outputs/step48_10step_envelope_matrix/ten_step_envelope_matrix.json
outputs/step48_10step_envelope_matrix/ten_step_envelope_matrix.npz
outputs/step48_10step_envelope_quality/ten_step_envelope_quality.csv
outputs/step48_10step_envelope_quality/ten_step_envelope_quality.json
outputs/step48_component_effect_10step_envelope/component_effect_10step_envelope.csv
outputs/step48_component_effect_10step_envelope/component_effect_10step_envelope.json
outputs/step48_phase_progression_10step_diagnostics/phase_progression_10step_diagnostics.csv
outputs/step48_phase_progression_10step_diagnostics/phase_progression_10step_diagnostics.json
outputs/step48_mass_force_bounceback_10step_envelope/mass_force_bounceback_10step_envelope.csv
outputs/step48_mass_force_bounceback_10step_envelope/mass_force_bounceback_10step_envelope.json
outputs/step48_step47_prefix_comparison/step47_prefix_comparison.csv
outputs/step48_step47_prefix_comparison/step47_prefix_comparison.json
outputs/step48_state_mutation_guard/state_mutation_guard.csv
outputs/step48_state_mutation_guard/state_mutation_guard.json
outputs/step48_step47_regression_guard/step47_regression_guard.csv
outputs/step48_step47_regression_guard/step47_regression_guard.json
outputs/step48_artifact_manifest/artifact_manifest.csv
outputs/step48_artifact_manifest/artifact_summary.csv
outputs/step48_artifact_manifest/artifact_summary.json
```

Create these logs:

```text
logs/step48_10step_config_validation.log
logs/step48_10step_envelope_matrix.log
logs/step48_10step_envelope_quality.log
logs/step48_component_effect_10step_envelope.log
logs/step48_phase_progression_10step_diagnostics.log
logs/step48_mass_force_bounceback_10step_envelope.log
logs/step48_step47_prefix_comparison.log
logs/step48_state_mutation_guard.log
logs/step48_step47_regression_guard.log
logs/step48_artifact_manifest.log
logs/step48_contract_pytest.log
logs/step48_pytest.log
```

## 9. Required Contract Test

Create:

```text
tests/test_step48_runtime_geometry_wall_velocity_10step_envelope_contract.py
```

The test must cover required files, config validity, matrix validity, quality summary, component-effect summary, phase-progression summary, mass/force/bounce-back summary, Step 47 prefix comparison, state mutation guard, Step 47 regression guard, unchanged default modes, docs scope and forbidden claims, artifact budget, report checklist completion, absence of persistent geometry outputs, and absence of full-cycle/production-ready claims.

The contract must intentionally fail before implementation and pass after all Step 48 artifacts are generated.

## 10. Required Documentation

Create:

```text
docs/48_controlled_runtime_geometry_wall_velocity_10step_coupling_envelope.md
STEP48_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_10STEP_COUPLING_ENVELOPE_REPORT.md
```

Update:

```text
README.md
```

The report must contain:

```text
## 1. Goal
## 2. Files Created And Updated
## 3. Explicit Non-Goals
## 4. 10-Step Config Validation
## 5. 10-Step Envelope Matrix
## 6. 10-Step Envelope Quality
## 7. Component Effect 10-Step Envelope
## 8. Phase Progression 10-Step Diagnostics
## 9. Mass Force Bounce-Back 10-Step Envelope
## 10. Step 47 Prefix Comparison
## 11. State Mutation Guard
## 12. Step 47 Regression Guard
## 13. Artifact Manifest Summary
## 14. Verification Commands
## 15. GitHub Sync Information
## 16. Acceptance Checklist
## 17. Decision For Step 49
```

Docs and report must include these scope phrases:

```text
Step 48 is controlled runtime geometry plus wall velocity 10-step coupling envelope.
Step 48 is opt-in and engineering-only.
Step 48 runs a 32^3 ten-step envelope.
Step 48 does not run a full-cycle moving-geometry simulation.
Step 48 does not persist displaced geometry.
Step 48 does not persist projected state.
Step 48 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.
```

Docs and report must not claim production readiness, swimming, persistent geometry, formula changes, or real validation.

## 11. Artifact Budget

Step 48 artifacts must remain small:

- `large_file_count == 0`;
- `step48_total_size_mb < 20`;
- `total_size_mb < 370`;
- `step48_vtr_count == 0`;
- `step48_particle_npy_count == 0`;
- `step48_displaced_particle_output_count == 0`;
- `step48_dense_displacement_output_count == 0`;
- `raw_candidate_large_file_count == 0`;
- `scan_data_file_count == 0`;
- `private_absolute_path_count == 0`;
- `geo_all_fluid_dat_count_added == 0`.

## 12. Verification Commands

Use the trusted Taichi environment:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\runtime_geometry_wall_velocity_10step_config.py src\runtime_geometry_wall_velocity_10step_envelope.py src\runtime_geometry_wall_velocity_10step_diagnostics.py src\runtime_geometry_wall_velocity_10step_state_guard.py baseline_tests\step48_common.py baseline_tests\run_step48_10step_config_validation.py baseline_tests\run_step48_10step_envelope_matrix.py baseline_tests\run_step48_10step_envelope_quality.py baseline_tests\run_step48_component_effect_10step_envelope.py baseline_tests\run_step48_phase_progression_10step_diagnostics.py baseline_tests\run_step48_mass_force_bounceback_10step_envelope.py baseline_tests\run_step48_step47_prefix_comparison.py baseline_tests\run_step48_state_mutation_guard.py baseline_tests\run_step48_step47_regression_guard.py baseline_tests\run_step48_artifact_manifest.py tests\test_step48_runtime_geometry_wall_velocity_10step_envelope_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step48_10step_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step48_10step_envelope_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step48_10step_envelope_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step48_component_effect_10step_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step48_phase_progression_10step_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step48_mass_force_bounceback_10step_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step48_step47_prefix_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step48_state_mutation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step48_step47_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step48_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step48_runtime_geometry_wall_velocity_10step_envelope_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q

git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## 13. Acceptance Checklist

- [ ] Step 48 detailed goal file exists.
- [ ] Ten-step config validation passes.
- [ ] `n_grid` is `32`.
- [ ] `n_lbm_steps` is `10`.
- [ ] `mpm_substeps_per_lbm_step` is `5`.
- [ ] Phase sequence is exactly `[0.0, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35]`.
- [ ] Coupling mode is `moving_boundary`.
- [ ] Reaction transfer mode is `engineering`.
- [ ] No `link_area` row is included.
- [ ] No `48^3` row is included.
- [ ] No full-cycle row is included.
- [ ] All persistence, write, default-update, production-recompute, and formula-change flags are false.
- [ ] Matrix runs exactly four rows.
- [ ] Each row has ten step records.
- [ ] Every row completes at least `10` LBM steps.
- [ ] Every row completes at least `50` MPM substeps.
- [ ] `rho_min > 0.95`.
- [ ] `rho_max < 1.05`.
- [ ] `lbm_max_v < 0.1`.
- [ ] `projected_mass > 0`.
- [ ] `active_cell_count > 0`.
- [ ] `bb_link_count > 0`.
- [ ] NaN count is `0`.
- [ ] Inf count is `0`.
- [ ] Geometry-only row shows a nonzero projection-envelope effect.
- [ ] Wall-velocity-only row shows positive applied velocity.
- [ ] Combined row has runtime geometry projection and wall velocity application.
- [ ] Ten-step envelope quality passes.
- [ ] Component-effect envelope passes.
- [ ] Phase-progression diagnostics pass.
- [ ] Mass/force/bounce-back envelope passes.
- [ ] Step 47 prefix comparison passes.
- [ ] State mutation guard passes.
- [ ] Original geometry hash remains stable.
- [ ] Region mask hash remains stable.
- [ ] Default driver, LBM, MPM, and projection mutation counts are `0`.
- [ ] Persistent projected state count is `0`.
- [ ] Persistent displaced geometry count is `0`.
- [ ] Persistent LBM solid velocity count is `0`.
- [ ] Displaced-particle output count is `0`.
- [ ] Dense-displacement output count is `0`.
- [ ] VTR output count is `0`.
- [ ] `geo_all_fluid_dat_count_added` is `0`.
- [ ] Step 47 regression guard passes.
- [ ] Default geometry and wall-velocity modes remain static/disabled.
- [ ] No default behavior changes.
- [ ] No formula changes.
- [ ] No `external/taichi_LBM3D` edits.
- [ ] No real-validation or swimming claim.
- [ ] Artifact budget passes.
- [ ] Focused Step 48 contract test passes.
- [ ] Full pytest passes.
- [ ] `git diff --check` passes.
- [ ] Staged whitespace check passes.
- [ ] Commit is pushed to `origin/main`.

## 14. Commit And Push

After implementation and verification, commit with:

```text
test: add step48 runtime geometry wall velocity 10step envelope
```

Push to:

```text
origin main
```

Report the final commit hash, remote branch, verification summary, and goal completion status.
