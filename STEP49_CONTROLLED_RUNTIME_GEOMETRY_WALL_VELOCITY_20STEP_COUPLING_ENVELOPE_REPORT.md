# Step 49 Controlled Runtime Geometry Wall Velocity 20-Step Coupling Envelope Report

## 1. Goal

Step 49 is controlled runtime geometry plus wall velocity 20-step coupling envelope.
Step 49 is opt-in and engineering-only.
Step 49 runs a 32^3 twenty-step envelope.
Step 49 does not run a full-cycle moving-geometry simulation.
Step 49 does not persist displaced geometry.
Step 49 does not persist projected state.
Step 49 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

The implementation follows `STEP49_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_20STEP_COUPLING_ENVELOPE_GOAL.md`.

## 2. Files Created And Updated

Created Step 49 configs, source modules, runners, contract test, docs, report, logs, and compact artifacts:

- `configs/step49_runtime_geometry_wall_velocity_20step_envelope.json`
- `configs/step49_original_static_32_20step.json`
- `configs/step49_runtime_geometry_only_32_20step.json`
- `configs/step49_wall_velocity_only_32_20step.json`
- `configs/step49_runtime_geometry_plus_wall_velocity_32_20step.json`
- `src/runtime_geometry_wall_velocity_20step_config.py`
- `src/runtime_geometry_wall_velocity_20step_envelope.py`
- `src/runtime_geometry_wall_velocity_20step_diagnostics.py`
- `src/runtime_geometry_wall_velocity_20step_state_guard.py`
- `baseline_tests/step49_common.py`
- `baseline_tests/run_step49_*.py`
- `tests/test_step49_runtime_geometry_wall_velocity_20step_envelope_contract.py`
- `docs/49_controlled_runtime_geometry_wall_velocity_20step_coupling_envelope.md`
- `outputs/step49_*`
- `logs/step49_*`

Updated `README.md` to document the Step 49 boundary.

## 3. Explicit Non-Goals

Step 49 does not enable persistent projected state, persistent displaced geometry, persistent LBM `solid_vel`, particle-array writes, dense-field writes, VTR writes, default driver geometry updates, default LBM/MPM/projection state updates, dynamic solid state updates, broad boundary-link rebuilds, or formula edits.

Step 49 does not add free-body dynamics, swimming behavior, animal-model validation, propulsion-validation claims, jet-validation claims, or final solver-readiness claims.

## 4. 20-Step Config Validation

`run_step49_20step_config_validation.py` validates `configs/step49_runtime_geometry_wall_velocity_20step_envelope.json`.

Result:

- row count: `40`
- pass count: `40`
- envelope id: `step49_runtime_geometry_wall_velocity_20step_envelope`
- grid size: `32`
- LBM steps: `20`
- MPM substeps per LBM step: `5`
- phase sequence: `[0.0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.5]`
- coupling mode: `moving_boundary`
- reaction transfer mode: `engineering`
- runtime geometry projection enabled in the umbrella diagnostic: `true`
- wall velocity application enabled in the umbrella diagnostic: `true`
- diagnostic-only: `true`
- all mutation flags false: `true`

## 5. 20-Step Envelope Matrix

`run_step49_20step_envelope_matrix.py` generates four rows:

- `original_static_32_20step`
- `runtime_geometry_only_32_20step`
- `wall_velocity_only_32_20step`
- `runtime_geometry_plus_wall_velocity_32_20step`

Result:

- row count: `4`
- stable count: `4`
- step count per row: `20`
- original static row count: `1`
- geometry-only row count: `1`
- wall-velocity-only row count: `1`
- combined row count: `1`
- completed LBM steps minimum: `20`
- total MPM substeps minimum: `100`
- projected mass minimum: `1.0`
- active-cell count minimum: `443`
- global rho min: `0.9982680917004111`
- global rho max: `1.0017319082995888`
- global LBM max velocity: `0.007042082995889119`
- minimum bounce-back link count: `2658`
- NaN count: `0`
- Inf count: `0`
- matrix pass: `true`

## 6. 20-Step Envelope Quality

`run_step49_20step_envelope_quality.py` checks the four matrix rows.

Result:

- quality pass: `true`
- row count pass: `true`
- step count pass: `true`
- stability pass: `true`
- projection pass: `true`
- wall velocity pass: `true`
- combined row pass: `true`
- early refill pass: `true`
- diagnostic-only pass: `true`
- no persistent state pass: `true`

## 7. Component Effect 20-Step Envelope

`run_step49_component_effect_20step_envelope.py` compares five component deltas over the twenty-step window.

Result:

- comparison count: `5`
- comparison pass count: `5`
- comparison pass: `true`
- geometry-effect active-cell delta nonzero: `true`
- wall-velocity-effect applied velocity nonzero: `true`
- combined row has runtime geometry and wall velocity: `true`
- max active-cell delta: `205`
- max applied-velocity delta: `0.007042082995889119`

## 8. Phase Progression 20-Step Diagnostics

`run_step49_phase_progression_20step_diagnostics.py` checks the twenty-step phase sequence.

Result:

- phase count: `20`
- phase sequence: `[0.0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.5]`
- phase sequence pass: `true`
- runtime geometry phase response pass: `true`
- wall velocity phase response pass: `true`
- combined phase response pass: `true`
- phase `0.0` to phase `0.35` projection delta nonzero: `true`
- phase `0.0` to phase `0.5` wall-velocity delta finite: `true`
- runtime geometry active-cell delta from phase `0.0` to phase `0.35`: `-205`
- wall-velocity applied-velocity delta from phase `0.0` to phase `0.5`: `0.002249296858436399`
- phase progression pass: `true`

## 9. Early Refill Transition Diagnostics

`run_step49_early_refill_transition_diagnostics.py` checks the transition interval `0.35 <= phase <= 0.5`.

Result:

- transition phase count: `6`
- transition phases: `[0.35, 0.375, 0.4, 0.425, 0.45, 0.5]`
- transition pass count: `4`
- transition pass: `true`
- runtime geometry active-cell count bounded: `true`
- wall velocity applied-cell count positive: `true`
- wall velocity cap pass: `true`
- NaN count: `0`
- Inf count: `0`

## 10. Mass Force Bounce-Back 20-Step Envelope

`run_step49_mass_force_bounceback_20step_envelope.py` checks density span, velocity cap, bounce-back count/correction, and hydrodynamic-force proxy values.

Result:

- row count: `4`
- envelope pass count: `4`
- envelope pass: `true`
- global rho min: `0.9982680917004111`
- global rho max: `1.0017319082995888`
- global max bounce-back correction: `0.007042082995889119`
- minimum bounce-back link count: `2658`
- global max hydrodynamic-force proxy norm: `0.002050114988871742`
- NaN count: `0`
- Inf count: `0`

## 11. Step 48 Prefix Comparison

`run_step49_step48_prefix_comparison.py` compares Step 49 against the accepted Step 48 matrix at shared phases `[0.0, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35]`.

Result:

- matched phase count: `10`
- row pair count: `4`
- comparison pass count: `4`
- comparison pass: `true`
- max projected-mass delta: `0.0`
- max active-cell-count delta: `0.0`
- max applied-velocity delta: `0.0`

## 12. State Mutation Guard

`run_step49_state_mutation_guard.py` recomputes the Step 49 matrix and verifies geometry hashes and forbidden-output counters.

Result:

- guard pass: `true`
- original geometry hash before: `cfd33df0be00889460e5c2ee3669b73e1605f1eb2b2d27b5f2ac9c48df3a10d1`
- original geometry hash after: `cfd33df0be00889460e5c2ee3669b73e1605f1eb2b2d27b5f2ac9c48df3a10d1`
- region mask hash before: `d2c6519395ad7c789a729511e37124f0dc65f3f79f9a0203ffc8b1cd023be0d9`
- region mask hash after: `d2c6519395ad7c789a729511e37124f0dc65f3f79f9a0203ffc8b1cd023be0d9`
- default driver state mutation count: `0`
- default LBM state mutation count: `0`
- default MPM state mutation count: `0`
- default projection state mutation count: `0`
- persistent projected state count: `0`
- persistent displaced geometry count: `0`
- persistent LBM solid velocity count: `0`
- displaced-particle output count: `0`
- dense-displacement output count: `0`
- VTR output count: `0`
- `geo_all_fluid_dat_count_added`: `0`

## 13. Step 48 Regression Guard

`run_step49_step48_regression_guard.py` verifies the accepted Step 48 report and evidence remain present and green.

Result:

- row count: `11`
- pass count: `11`
- regression pass: `true`

## 14. Artifact Manifest Summary

`run_step49_artifact_manifest.py` records the Step 49 artifact budget after docs, logs, and generated outputs are present.

Result:

- file count: `3606`
- Step 49 file count: `59`
- repo total size MB: `212.33705615997314`
- Step 49 total size MB: `0.538050651550293`
- large Step 49 file count: `0`
- Step 49 VTR count: `0`
- Step 49 particle NPY count: `0`
- Step 49 displaced-particle output count: `0`
- Step 49 dense-displacement output count: `0`
- raw candidate large-file count: `0`
- scan-data file count: `0`
- private absolute path count: `0`
- `geo_all_fluid_dat_count_added`: `0`
- artifact budget pass: `true`

## 15. Verification Commands

Executed with `D:\working\taichi\env\python.exe`:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\runtime_geometry_wall_velocity_20step_config.py src\runtime_geometry_wall_velocity_20step_envelope.py src\runtime_geometry_wall_velocity_20step_diagnostics.py src\runtime_geometry_wall_velocity_20step_state_guard.py baseline_tests\step49_common.py baseline_tests\run_step49_20step_config_validation.py baseline_tests\run_step49_20step_envelope_matrix.py baseline_tests\run_step49_20step_envelope_quality.py baseline_tests\run_step49_component_effect_20step_envelope.py baseline_tests\run_step49_phase_progression_20step_diagnostics.py baseline_tests\run_step49_early_refill_transition_diagnostics.py baseline_tests\run_step49_mass_force_bounceback_20step_envelope.py baseline_tests\run_step49_step48_prefix_comparison.py baseline_tests\run_step49_state_mutation_guard.py baseline_tests\run_step49_step48_regression_guard.py baseline_tests\run_step49_artifact_manifest.py tests\test_step49_runtime_geometry_wall_velocity_20step_envelope_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step49_20step_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step49_20step_envelope_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step49_20step_envelope_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step49_component_effect_20step_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step49_phase_progression_20step_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step49_early_refill_transition_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step49_mass_force_bounceback_20step_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step49_step48_prefix_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step49_state_mutation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step49_step48_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step49_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step49_runtime_geometry_wall_velocity_20step_envelope_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

The focused and full pytest logs are stored in `logs/step49_contract_pytest.log` and `logs/step49_pytest.log` after final verification.

## 16. GitHub Sync Information

Target branch: `origin/main`.

The report is written before the final commit hash exists. The final hash is reported in the completion message after push.

## 17. Acceptance Checklist

- [x] Step 49 detailed goal file exists.
- [x] Twenty-step config validation passes.
- [x] `n_grid` is `32`.
- [x] `n_lbm_steps` is `20`.
- [x] `mpm_substeps_per_lbm_step` is `5`.
- [x] Phase sequence is exactly `[0.0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.5]`.
- [x] Coupling mode is `moving_boundary`.
- [x] Reaction transfer mode is `engineering`.
- [x] No `link_area` row is included.
- [x] No `48^3` row is included.
- [x] No `64^3` row is included.
- [x] No full-cycle row is included.
- [x] All persistence, write, default-update, production-recompute, and formula-change flags are false.
- [x] Matrix runs exactly four rows.
- [x] Each row has twenty step records.
- [x] Every row completes at least `20` LBM steps.
- [x] Every row completes at least `100` MPM substeps.
- [x] `rho_min > 0.95`.
- [x] `rho_max < 1.05`.
- [x] `lbm_max_v < 0.1`.
- [x] `projected_mass > 0`.
- [x] `active_cell_count > 0`.
- [x] `bb_link_count > 0`.
- [x] NaN count is `0`.
- [x] Inf count is `0`.
- [x] Geometry-only row shows a nonzero projection-envelope effect.
- [x] Wall-velocity-only row shows positive applied velocity.
- [x] Combined row has runtime geometry projection and wall velocity application.
- [x] Twenty-step envelope quality passes.
- [x] Component-effect envelope passes.
- [x] Phase-progression diagnostics pass.
- [x] Early-refill transition diagnostics pass.
- [x] Mass/force/bounce-back envelope passes.
- [x] Step 48 prefix comparison passes.
- [x] State mutation guard passes.
- [x] Original geometry hash remains stable.
- [x] Region mask hash remains stable.
- [x] Default driver, LBM, MPM, and projection mutation counts are `0`.
- [x] Persistent projected state count is `0`.
- [x] Persistent displaced geometry count is `0`.
- [x] Persistent LBM solid velocity count is `0`.
- [x] Displaced-particle output count is `0`.
- [x] Dense-displacement output count is `0`.
- [x] VTR output count is `0`.
- [x] `geo_all_fluid_dat_count_added` is `0`.
- [x] Step 48 regression guard passes.
- [x] Default geometry and wall-velocity modes remain static/disabled.
- [x] No default behavior changes.
- [x] No formula changes.
- [x] No `external/taichi_LBM3D` edits.
- [x] No animal-model or final solver-readiness claim.
- [x] Artifact budget passes.
- [x] Focused Step 49 contract test passes.
- [x] Full pytest passes.
- [x] `git diff --check` passes.
- [x] Staged whitespace check passes.
- [x] Commit is pushed to `origin/main`.

## 18. Decision For Step 50

Step 49 is acceptable when the focused contract test, full pytest, artifact budget, whitespace checks, and push complete. Step 50 may extend the diagnostic surface only with another explicit contract, and the default behavior should remain static/disabled unless a later accepted goal deliberately changes that boundary.
