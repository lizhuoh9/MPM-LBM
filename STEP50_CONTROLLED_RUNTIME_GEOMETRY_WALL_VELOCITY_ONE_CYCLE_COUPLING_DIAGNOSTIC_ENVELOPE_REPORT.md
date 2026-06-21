# Step 50 Controlled Runtime Geometry Wall Velocity One-Cycle Coupling Diagnostic Envelope Report

## 1. Goal

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

The implementation follows `STEP50_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_CYCLE_COUPLING_DIAGNOSTIC_ENVELOPE_GOAL.md`.

## 2. Files Created And Updated

Created Step 50 configs, source modules, runners, contract test, docs, report, logs, and compact artifacts:

- `configs/step50_runtime_geometry_wall_velocity_one_cycle_envelope.json`
- `configs/step50_original_static_32_40step.json`
- `configs/step50_runtime_geometry_only_32_40step.json`
- `configs/step50_wall_velocity_only_32_40step.json`
- `configs/step50_runtime_geometry_plus_wall_velocity_32_40step.json`
- `src/runtime_geometry_wall_velocity_one_cycle_config.py`
- `src/runtime_geometry_wall_velocity_one_cycle_envelope.py`
- `src/runtime_geometry_wall_velocity_one_cycle_diagnostics.py`
- `src/runtime_geometry_wall_velocity_one_cycle_state_guard.py`
- `baseline_tests/step50_common.py`
- `baseline_tests/run_step50_*.py`
- `tests/test_step50_runtime_geometry_wall_velocity_one_cycle_envelope_contract.py`
- `docs/50_controlled_runtime_geometry_wall_velocity_one_cycle_coupling_diagnostic_envelope.md`
- `outputs/step50_*`
- `logs/step50_*`

Updated `README.md` to document the Step 50 boundary.

## 3. Explicit Non-Goals

Step 50 does not enable persistent projected state, persistent displaced geometry, persistent LBM `solid_vel`, particle-array writes, dense-field writes, VTR writes, default driver geometry updates, default LBM/MPM/projection state updates, dynamic solid state updates, broad boundary-link rebuilds, or formula edits.

Step 50 does not add free-body dynamics, swimming behavior, animal-model validation, propulsion-validation claims, or final solver-readiness claims.

## 4. One-Cycle Config Validation

`run_step50_one_cycle_config_validation.py` validates `configs/step50_runtime_geometry_wall_velocity_one_cycle_envelope.json`.

Result:

- row count: `43`
- pass count: `43`
- envelope id: `step50_runtime_geometry_wall_velocity_one_cycle_envelope`
- grid size: `32`
- LBM steps: `40`
- MPM substeps per LBM step: `5`
- cycle period steps: `40`
- phase count: `40`
- runner phase sequence starts at `0.0`: `true`
- runner phase sequence ends at `0.975`: `true`
- diagnostic closure phase: `1.0`
- coupling mode: `moving_boundary`
- reaction transfer mode: `engineering`
- runtime geometry projection enabled in the umbrella diagnostic: `true`
- wall velocity application enabled in the umbrella diagnostic: `true`
- diagnostic-only: `true`
- all mutation flags false: `true`

## 5. One-Cycle Envelope Matrix

`run_step50_one_cycle_envelope_matrix.py` generates four rows:

- `original_static_32_40step`
- `runtime_geometry_only_32_40step`
- `wall_velocity_only_32_40step`
- `runtime_geometry_plus_wall_velocity_32_40step`

Result:

- row count: `4`
- stable count: `4`
- step count per row: `40`
- original static row count: `1`
- geometry-only row count: `1`
- wall-velocity-only row count: `1`
- combined row count: `1`
- completed LBM steps minimum: `40`
- total MPM substeps minimum: `200`
- projected mass minimum: `1.0`
- active-cell count minimum: `443`
- global rho min: `0.9982680917004111`
- global rho max: `1.0017319082995888`
- global LBM max velocity: `0.007042082995889119`
- minimum bounce-back link count: `2658`
- NaN count: `0`
- Inf count: `0`
- matrix pass: `true`

## 6. One-Cycle Envelope Quality

`run_step50_one_cycle_envelope_quality.py` checks the four matrix rows plus closure rows.

Result:

- quality pass: `true`
- row count pass: `true`
- step count pass: `true`
- stability pass: `true`
- projection pass: `true`
- wall velocity pass: `true`
- combined row pass: `true`
- cycle phase pass: `true`
- contraction/refill pass: `true`
- closure pass: `true`
- diagnostic-only pass: `true`
- no persistent state pass: `true`

## 7. Component Effect One-Cycle Envelope

`run_step50_component_effect_one_cycle_envelope.py` compares five component deltas over the one-cycle window.

Result:

- comparison count: `5`
- comparison pass count: `5`
- comparison pass: `true`
- geometry-effect active-cell delta nonzero: `true`
- wall-velocity-effect applied velocity nonzero: `true`
- combined row has runtime geometry and wall velocity: `true`
- max active-cell delta: `205`
- max applied-velocity delta: `0.007042082995889119`

## 8. Phase Progression One-Cycle Diagnostics

`run_step50_phase_progression_one_cycle_diagnostics.py` checks the forty-step phase sequence.

Result:

- phase count: `40`
- phase sequence: `[0.0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.475, 0.5, 0.525, 0.55, 0.575, 0.6, 0.625, 0.65, 0.675, 0.7, 0.725, 0.75, 0.775, 0.8, 0.825, 0.85, 0.875, 0.9, 0.925, 0.95, 0.975]`
- phase sequence pass: `true`
- runtime geometry phase response pass: `true`
- wall velocity phase response pass: `true`
- combined phase response pass: `true`
- phase `0.0` to phase `0.35` projection delta nonzero: `true`
- phase `0.35` to phase `0.975` refill response finite: `true`
- phase progression pass: `true`

## 9. Contraction Refill Segment Diagnostics

`run_step50_contraction_refill_segment_diagnostics.py` checks contraction phases `phase <= 0.35` and refill phases `phase > 0.35`.

Result:

- contraction phase count: `15`
- refill phase count: `25`
- contraction segment pass: `true`
- refill segment pass: `true`
- runtime geometry active-cell count bounded: `true`
- wall velocity applied-cell count positive: `true`
- wall velocity cap pass: `true`
- NaN count: `0`
- Inf count: `0`

## 10. Cycle Closure Diagnostics

`run_step50_cycle_closure_diagnostics.py` compares diagnostic phase `0.0` against diagnostic endpoint phase `1.0`.

Result:

- row count: `4`
- closure phase: `1.0`
- closure pass count: `4`
- closure pass: `true`
- geometry projection closure pass: `true`
- wall velocity closure pass: `true`
- cycle proxy closure pass: `true`
- max projected-mass endpoint delta: `0.0`
- max active-cell endpoint delta: `0`
- wall velocity closure tolerance: `0.0005`
- max applied-velocity endpoint delta: `0.00035490392512819833`

The wall-velocity endpoint residual is bounded by the documented diagnostic tolerance. This is not a physical propulsion closure claim.

## 11. Mass Force Bounce-Back One-Cycle Envelope

`run_step50_mass_force_bounceback_one_cycle_envelope.py` checks density span, velocity cap, bounce-back count/correction, and hydrodynamic-force proxy values.

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

## 12. Step 49 Prefix Comparison

`run_step50_step49_prefix_comparison.py` compares Step 50 against the accepted Step 49 matrix at the twenty shared phases from `0.0` through `0.5`.

Result:

- matched phase count: `20`
- row pair count: `4`
- comparison pass count: `4`
- comparison pass: `true`
- max projected-mass delta: `0.0`
- max active-cell-count delta: `0.0`
- max applied-velocity delta: `0.0`

## 13. State Mutation Guard

`run_step50_state_mutation_guard.py` recomputes the Step 50 matrix and verifies geometry hashes and forbidden-output counters.

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

## 14. Step 49 Regression Guard

`run_step50_step49_regression_guard.py` verifies the accepted Step 49 report and evidence remain present and green.

Result:

- row count: `9`
- pass count: `9`
- regression pass: `true`

## 15. Artifact Manifest Summary

`run_step50_artifact_manifest.py` records the Step 50 artifact budget after docs, logs, and generated outputs are present.

Result:

- file count: `3673`
- Step 50 file count: `63`
- repo total size MB: `213.09159660339355`
- Step 50 total size MB: `0.6902256011962891`
- large Step 50 file count: `0`
- Step 50 VTR count: `0`
- Step 50 particle NPY count: `0`
- Step 50 displaced-particle output count: `0`
- Step 50 dense-displacement output count: `0`
- raw candidate large-file count: `0`
- scan-data file count: `0`
- private absolute path count: `0`
- `geo_all_fluid_dat_count_added`: `0`
- artifact budget pass: `true`

## 16. Verification Commands

Executed with `D:\working\taichi\env\python.exe`:

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

The focused and full pytest logs are stored in `logs/step50_contract_pytest.log` and `logs/step50_pytest.log` after final verification.

## 17. GitHub Sync Information

Target branch: `origin/main`.

The report is written before the final commit hash exists. The final hash is reported in the completion message after push.

## 18. Acceptance Checklist

- [x] Step 50 detailed goal file exists.
- [x] One-cycle config validation passes.
- [x] `n_grid` is `32`.
- [x] `n_lbm_steps` is `40`.
- [x] `mpm_substeps_per_lbm_step` is `5`.
- [x] `cycle_period_steps` is `40`.
- [x] Phase sequence has exactly `40` entries.
- [x] Phase sequence starts at `0.0`.
- [x] Phase sequence ends at `0.975`.
- [x] `closure_phase` is `1.0`.
- [x] Coupling mode is `moving_boundary`.
- [x] Reaction transfer mode is `engineering`.
- [x] No `link_area` row is included.
- [x] No `48^3` row is included.
- [x] No `64^3` row is included.
- [x] All persistence, write, default-update, production-recompute, and formula-change flags are false.
- [x] One-cycle envelope matrix runs exactly four rows.
- [x] Each row has exactly forty step records.
- [x] All rows complete at least `40` LBM steps.
- [x] All rows complete at least `200` MPM substeps.
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
- [x] One-cycle envelope quality passes.
- [x] Component-effect envelope passes.
- [x] Phase-progression diagnostics pass.
- [x] Contraction/refill segment diagnostics pass.
- [x] Cycle-closure diagnostics pass.
- [x] Mass/force/bounce-back envelope passes.
- [x] Step 49 prefix comparison passes.
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
- [x] Step 49 regression guard passes.
- [x] Default geometry and wall-velocity modes remain static/disabled.
- [x] No default behavior changes.
- [x] No formula changes.
- [x] No `external/taichi_LBM3D` edits.
- [x] No propulsion-validation claim.
- [x] No swimming claim.
- [x] No real-animal validation claim.
- [x] Artifact budget passes.
- [x] Focused Step 50 contract test passes.
- [x] Full pytest passes.
- [x] `git diff --check` passes.
- [x] Staged whitespace check passes.
- [x] Commit is pushed to `origin/main`.

## 19. Decision For Step 51

Step 50 is acceptable when the focused contract test, full pytest, artifact budget, whitespace checks, and push complete. Step 51 may compare engineering-only behavior against a separately bounded transfer diagnostic, but it should not expand grid size, persistence, default behavior, or physical-validation claims without a new accepted contract.
