# Step 47 Controlled Runtime Geometry Wall Velocity Short-Step Coupling Envelope Report

## 1. Goal

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

The implementation follows `STEP47_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_SHORT_STEP_COUPLING_ENVELOPE_GOAL.md`.

## 2. Files Created And Updated

Created Step 47 configs, source modules, runners, contract test, docs, report, logs, and compact artifacts:

- `configs/step47_runtime_geometry_wall_velocity_short_step_envelope.json`
- `configs/step47_original_static_32_5step.json`
- `configs/step47_runtime_geometry_only_32_5step.json`
- `configs/step47_wall_velocity_only_32_5step.json`
- `configs/step47_runtime_geometry_plus_wall_velocity_32_5step.json`
- `src/runtime_geometry_wall_velocity_envelope_config.py`
- `src/runtime_geometry_wall_velocity_envelope.py`
- `src/runtime_geometry_wall_velocity_envelope_diagnostics.py`
- `src/runtime_geometry_wall_velocity_envelope_state_guard.py`
- `baseline_tests/step47_common.py`
- `baseline_tests/run_step47_*.py`
- `tests/test_step47_runtime_geometry_wall_velocity_short_step_envelope_contract.py`
- `docs/47_controlled_runtime_geometry_wall_velocity_short_step_coupling_envelope.md`
- `outputs/step47_*`
- `logs/step47_*`

Updated `README.md` to document the Step 47 boundary.

## 3. Explicit Non-Goals

Step 47 does not enable persistent projected state, persistent displaced geometry, persistent LBM `solid_vel`, particle-array writes, dense-field writes, VTR writes, default driver geometry updates, default LBM/MPM/projection state updates, dynamic solid state updates, broad boundary-link rebuilds, or formula edits.

Step 47 does not add free-body dynamics, squid-swimming behavior, animal-model validation, propulsion validation, jet-validation claims, or final solver-readiness claims.

## 4. Short-Step Config Validation

`run_step47_short_step_config_validation.py` validates `configs/step47_runtime_geometry_wall_velocity_short_step_envelope.json`.

Result:

- row count: `35`
- pass count: `35`
- envelope id: `step47_runtime_geometry_wall_velocity_short_step_envelope`
- grid size: `32`
- LBM steps: `5`
- MPM substeps per LBM step: `5`
- phase sequence: `[0.0, 0.05, 0.1, 0.2, 0.35]`
- coupling mode: `moving_boundary`
- reaction transfer mode: `engineering`
- runtime geometry projection enabled in the umbrella diagnostic: `true`
- wall velocity application enabled in the umbrella diagnostic: `true`
- diagnostic-only: `true`
- all mutation flags false: `true`

## 5. Short-Step Envelope Matrix

`run_step47_short_step_envelope_matrix.py` generates four rows:

- `original_static_32_5step`
- `runtime_geometry_only_32_5step`
- `wall_velocity_only_32_5step`
- `runtime_geometry_plus_wall_velocity_32_5step`

Result:

- row count: `4`
- stable count: `4`
- step count per row: `5`
- original static row count: `1`
- geometry-only row count: `1`
- wall-velocity-only row count: `1`
- combined row count: `1`
- completed LBM steps minimum: `5`
- total MPM substeps minimum: `25`
- projected mass minimum: `1.0`
- active-cell count minimum: `443`
- global rho min: `0.9982921917004111`
- global rho max: `1.001707808299589`
- global LBM max velocity: `0.007042082995889119`
- minimum bounce-back link count: `2658`
- NaN count: `0`
- Inf count: `0`
- matrix pass: `true`

## 6. Short-Step Envelope Quality

`run_step47_short_step_envelope_quality.py` checks the four matrix rows.

Result:

- quality pass: `true`
- row count pass: `true`
- step count pass: `true`
- stability pass: `true`
- projection pass: `true`
- wall velocity pass: `true`
- combined row pass: `true`
- diagnostic-only pass: `true`
- no persistent state pass: `true`

## 7. Component Effect Envelope

`run_step47_component_effect_envelope.py` compares five component deltas over the five-step window.

Result:

- comparison count: `5`
- comparison pass count: `5`
- comparison pass: `true`
- geometry-effect active-cell delta nonzero: `true`
- wall-velocity-effect applied velocity nonzero: `true`
- combined row has runtime geometry and wall velocity: `true`
- max active-cell delta: `205`
- max applied-velocity delta: `0.007042082995889119`

## 8. Phase Progression Diagnostics

`run_step47_phase_progression_diagnostics.py` checks the five-step phase sequence.

Result:

- phase count: `5`
- phase sequence: `[0.0, 0.05, 0.1, 0.2, 0.35]`
- phase sequence pass: `true`
- runtime geometry phase response pass: `true`
- wall velocity phase response pass: `true`
- combined phase response pass: `true`
- phase `0.0` to phase `0.35` projection delta nonzero: `true`
- phase `0.0` to phase `0.35` wall-velocity delta finite: `true`

## 9. Mass Force Bounce-Back Envelope

`run_step47_mass_force_bounceback_envelope.py` checks density, max velocity, bounce-back link count, max correction, and proxy hydrodynamic force diagnostics.

Result:

- row count: `4`
- envelope pass count: `4`
- envelope pass: `true`
- global rho min: `0.9982921917004111`
- global rho max: `1.001707808299589`
- minimum bounce-back link count: `2658`
- global max bounce-back correction: `0.007042082995889119`
- global max hydrodynamic force norm: `0.002050114988871742`
- NaN count: `0`
- Inf count: `0`

## 10. State Mutation Guard

`run_step47_state_mutation_guard.py` checks hash stability and forbidden Step 47 outputs.

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
- displaced particle output count: `0`
- dense displacement output count: `0`
- VTR output count: `0`
- Step 47 `geo_all_fluid_*.dat` output count: `0`

## 11. Step 46 Regression Guard

`run_step47_step46_regression_guard.py` verifies the accepted Step 46 evidence remains available and green.

Result:

- row count: `9`
- pass count: `9`
- regression pass: `true`

## 12. Artifact Manifest Summary

`run_step47_artifact_manifest.py` verifies the Step 47 artifact budget after the Step 47 artifacts are generated.

Result:

- artifact budget pass: `true`
- repository file count: `3484`
- Step 47 related file count: `51`
- repository total size MB: about `211.23`
- Step 47 total size MB: under `0.50`
- large Step 47 file count: `0`
- Step 47 VTR count: `0`
- Step 47 particle NPY count: `0`
- Step 47 displaced particle output count: `0`
- Step 47 dense displacement output count: `0`
- raw candidate large-file count: `0`
- scan-data count: `0`
- private absolute path count: `0`
- Step 47 `geo_all_fluid_*.dat` output count: `0`

## 13. Verification Commands

Verification uses `D:\working\taichi\env\python.exe`.

Commands:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\runtime_geometry_wall_velocity_envelope_config.py src\runtime_geometry_wall_velocity_envelope.py src\runtime_geometry_wall_velocity_envelope_diagnostics.py src\runtime_geometry_wall_velocity_envelope_state_guard.py baseline_tests\step47_common.py baseline_tests\run_step47_short_step_config_validation.py baseline_tests\run_step47_short_step_envelope_matrix.py baseline_tests\run_step47_short_step_envelope_quality.py baseline_tests\run_step47_component_effect_envelope.py baseline_tests\run_step47_phase_progression_diagnostics.py baseline_tests\run_step47_mass_force_bounceback_envelope.py baseline_tests\run_step47_state_mutation_guard.py baseline_tests\run_step47_step46_regression_guard.py baseline_tests\run_step47_artifact_manifest.py tests\test_step47_runtime_geometry_wall_velocity_short_step_envelope_contract.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step47_short_step_config_validation.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step47_short_step_envelope_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step47_short_step_envelope_quality.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step47_component_effect_envelope.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step47_phase_progression_diagnostics.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step47_mass_force_bounceback_envelope.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step47_state_mutation_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step47_step46_regression_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step47_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step47_runtime_geometry_wall_velocity_short_step_envelope_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
```

## 14. GitHub Sync Information

This section is finalized by the commit and push proof. The expected target is `origin/main`.

## 15. Acceptance Checklist

- [x] Step 47 detailed goal file exists.
- [x] Short-step config validation passes.
- [x] Grid size is `32`.
- [x] LBM step count is `5`.
- [x] MPM substeps per LBM step is `5`.
- [x] Phase sequence is `0.0`, `0.05`, `0.1`, `0.2`, `0.35`.
- [x] Coupling mode is `moving_boundary`.
- [x] Reaction transfer mode is `engineering`.
- [x] No link-area transfer row is included.
- [x] No `48^3` row is included.
- [x] Persistent displaced geometry is disabled.
- [x] Persistent projected state is disabled.
- [x] Persistent LBM `solid_vel` is disabled.
- [x] Displaced particle writes are disabled.
- [x] Dense displacement field writes are disabled.
- [x] VTK writes are disabled.
- [x] Particle writes are disabled.
- [x] Default driver state update is disabled.
- [x] Default LBM state update is disabled.
- [x] Default MPM state update is disabled.
- [x] Default projection state update is disabled.
- [x] Persistent dynamic solid update is disabled.
- [x] Broad boundary-link recomputation is disabled.
- [x] Moving bounce-back formula modification is disabled.
- [x] Short-step envelope matrix has four rows.
- [x] Each row has five step records.
- [x] Original static row passes.
- [x] Runtime geometry-only row passes.
- [x] Wall-velocity-only row passes.
- [x] Runtime geometry plus wall-velocity row passes.
- [x] All rows complete at least five LBM steps.
- [x] All rows complete at least twenty-five MPM substeps.
- [x] Density lower bound remains above `0.95`.
- [x] Density upper bound remains below `1.05`.
- [x] LBM max velocity remains below `0.1`.
- [x] Projected mass is positive.
- [x] Active-cell count is positive.
- [x] Bounce-back link count is positive.
- [x] No NaN is detected.
- [x] No Inf is detected.
- [x] Runtime geometry-only row shows nonzero projection envelope effect.
- [x] Wall-velocity-only row shows positive applied velocity.
- [x] Combined row has runtime geometry projection and wall velocity.
- [x] Short-step envelope quality passes.
- [x] Component-effect envelope passes.
- [x] Phase-progression diagnostics pass.
- [x] Mass/force/bounce-back envelope passes.
- [x] State mutation guard passes.
- [x] Original geometry hash remains stable.
- [x] Region mask hash remains stable.
- [x] Default driver state mutation count is `0`.
- [x] Default LBM state mutation count is `0`.
- [x] Default MPM state mutation count is `0`.
- [x] Default projection state mutation count is `0`.
- [x] Persistent projected state count is `0`.
- [x] Persistent displaced geometry count is `0`.
- [x] Displaced particle output count is `0`.
- [x] Dense displacement output count is `0`.
- [x] VTR output count is `0`.
- [x] Step 47 `geo_all_fluid_*.dat` count is `0`.
- [x] Step 46 regression guard passes.
- [x] Default geometry motion mode remains static.
- [x] Default geometry motion application mode remains disabled.
- [x] Default boundary motion mode remains static.
- [x] Default wall velocity application mode remains disabled.
- [x] No default behavior change is introduced.
- [x] No moving bounce-back formula changes are introduced.
- [x] No LBM collision formula changes are introduced.
- [x] No MPM constitutive formula changes are introduced.
- [x] No projection formula changes are introduced.
- [x] `external/taichi_LBM3D` remains untouched.
- [x] No jet-validation claim is made.
- [x] No squid-swimming claim is made.
- [x] No real-squid validation claim is made.
- [x] No Step 47 VTR outputs exist.
- [x] No Step 47 particle NPY outputs exist.
- [x] Artifact large-file count is `0`.
- [x] Step 47 output total-size budget passes.
- [x] Repository artifact summary total size remains under `360` MB.
- [x] Step 47 focused contract test passes.
- [x] Full pytest passes.
- [x] Artifact manifest is refreshed after final pytest logs.

## 16. Decision For Step 48

Step 47 is acceptable as a controlled five-step engineering-only envelope. Step 48 should remain explicitly bounded if it extends the diagnostic window, and it should continue to avoid implicit default solver-state activation.
