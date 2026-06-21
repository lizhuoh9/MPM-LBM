# Step 46 Controlled Runtime Geometry Wall Velocity One-Step Coupling Smoke Report

## 1. Goal

Step 46 is controlled runtime geometry plus wall velocity one-step coupling smoke.
Step 46 is opt-in and ultra-short.
Step 46 combines transient runtime geometry projection with solid_vel wall velocity application.
Step 46 does not persist displaced geometry.
Step 46 does not persist projected state.
Step 46 does not run a full-cycle moving-geometry simulation.
Step 46 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

The implementation follows `STEP46_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_STEP_COUPLING_SMOKE_GOAL.md`.

## 2. Files Created And Updated

Created Step 46 configs, source modules, runners, contract test, docs, report, logs, and compact artifacts:

- `configs/step46_runtime_geometry_wall_velocity_coupling_smoke.json`
- `configs/step46_original_static_32_1step.json`
- `configs/step46_runtime_geometry_only_32_phase035_1step.json`
- `configs/step46_wall_velocity_only_32_phase035_1step.json`
- `configs/step46_runtime_geometry_plus_wall_velocity_32_phase035_1step.json`
- `src/runtime_geometry_wall_velocity_coupling_config.py`
- `src/runtime_geometry_wall_velocity_coupling.py`
- `src/runtime_geometry_wall_velocity_diagnostics.py`
- `src/runtime_geometry_wall_velocity_state_guard.py`
- `baseline_tests/step46_common.py`
- `baseline_tests/run_step46_*.py`
- `tests/test_step46_runtime_geometry_wall_velocity_coupling_smoke_contract.py`
- `docs/46_controlled_runtime_geometry_wall_velocity_one_step_coupling_smoke.md`
- `outputs/step46_*`
- `logs/step46_*`

Updated `README.md` to document the Step 46 boundary.

## 3. Explicit Non-Goals

Step 46 does not enable persistent projected state, persistent displaced geometry, particle-array writes, dense-field writes, VTR writes, default driver geometry updates, default LBM/MPM/projection state updates, dynamic solid state updates, boundary-link rebuilds for a broader run, or formula edits.

Step 46 does not add free-body dynamics, swimming behavior, animal-model validation, propulsion validation, or final solver readiness claims.

## 4. Coupling Smoke Config Validation

`run_step46_coupling_smoke_config_validation.py` validates `configs/step46_runtime_geometry_wall_velocity_coupling_smoke.json`.

Result:

- row count: `32`
- pass count: `32`
- coupling smoke id: `step46_runtime_geometry_wall_velocity_one_step`
- phase: `0.35`
- grid size: `32`
- LBM steps: `1`
- MPM substeps per LBM step: `1`
- coupling mode: `moving_boundary`
- reaction transfer mode: `engineering`
- runtime geometry projection enabled in the umbrella diagnostic: `true`
- wall velocity application enabled in the umbrella diagnostic: `true`
- diagnostic-only: `true`
- all mutation flags false: `true`

## 5. One-Step Coupling Smoke Matrix

`run_step46_one_step_coupling_smoke_matrix.py` generates four rows:

- `original_static_32_1step`
- `runtime_geometry_only_32_phase035_1step`
- `wall_velocity_only_32_phase035_1step`
- `runtime_geometry_plus_wall_velocity_32_phase035_1step`

Result:

- row count: `4`
- stable count: `4`
- original static row count: `1`
- geometry-only row count: `1`
- wall-velocity-only row count: `1`
- combined row count: `1`
- matrix pass: `true`
- global rho min: `0.9989617548037436`
- global rho max: `1.0010382451962565`
- global LBM max velocity: `0.0001774519625640706`
- minimum bounce-back link count: `2658`
- NaN count: `0`
- Inf count: `0`

## 6. Runtime Geometry Effect

The runtime-geometry-only row changes active-cell count from `648` to `443` at phase `0.35`, producing an active-cell delta of `205`. Projected mass remains `1.0`, solid-phi bounds remain `[0.0, 1.0]`, and the row is stable.

The combined row carries the same runtime projection effect while also applying wall velocity. It remains diagnostic-only and leaves persistent projection and displaced-geometry fields disabled.

## 7. Wall Velocity Effect

The wall-velocity-only and combined rows each apply wall velocity to `648` cells. The max applied velocity norm is `0.0001774519625640706`, and the configured cap is `0.01`.

No row persists `solid_vel` into the default LBM state. The Step 46 wall velocity application is only part of the generated one-step diagnostic rows.

## 8. Component Effect Comparison

`run_step46_component_effect_comparison.py` compares five component deltas.

Result:

- comparison count: `5`
- comparison pass count: `5`
- comparison pass: `true`
- geometry-only projection delta nonzero: `true`
- wall-velocity-only applied velocity nonzero: `true`
- combined row has runtime geometry and wall velocity: `true`

## 9. Coupling Smoke Quality

`run_step46_coupling_smoke_quality.py` checks the four matrix rows.

Result:

- quality pass: `true`
- row count pass: `true`
- stability pass: `true`
- projection pass: `true`
- wall velocity pass: `true`
- combined row pass: `true`
- diagnostic-only pass: `true`
- no persistent state pass: `true`

## 10. Mass, Force, And Bounce-Back Diagnostics

`run_step46_mass_force_bounceback_diagnostics.py` checks density, max velocity, bounce-back link count, max correction, and proxy hydrodynamic force diagnostics.

Result:

- row count: `4`
- diagnostics pass count: `4`
- diagnostics pass: `true`
- global rho min: `0.9989617548037436`
- global rho max: `1.0010382451962565`
- minimum bounce-back link count: `2658`
- global max bounce-back correction: `0.0001774519625640706`
- global max hydrodynamic force norm: `0.002050114988871742`
- NaN count: `0`
- Inf count: `0`

## 11. State Mutation Guard

`run_step46_state_mutation_guard.py` checks hash stability and forbidden Step 46 outputs.

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
- Step 46 `geo_all_fluid_*.dat` output count: `0`

## 12. Step 45 Regression Guard

`run_step46_step45_regression_guard.py` verifies the accepted Step 45 evidence remains available and green.

Result:

- row count: `8`
- pass count: `8`
- regression pass: `true`

## 13. Artifact Manifest Summary

`run_step46_artifact_manifest.py` verifies the Step 46 artifact budget after all Step 46 artifacts are generated.

Result:

- artifact budget pass: `true`
- repository file count: `3429`
- Step 46 related file count: `47`
- repository total size MB: about `210.75`
- Step 46 total size MB: under `0.39`
- large Step 46 file count: `0`
- Step 46 VTR count: `0`
- Step 46 particle NPY count: `0`
- Step 46 displaced particle output count: `0`
- Step 46 dense displacement output count: `0`
- raw candidate large-file count: `0`
- scan-data count: `0`
- private absolute path count: `0`
- Step 46 `geo_all_fluid_*.dat` output count: `0`

## 14. Acceptance Checklist

- [x] Step 46 detailed goal file exists.
- [x] Coupling smoke config validation passes.
- [x] Phase is `0.35`.
- [x] Grid size is `32`.
- [x] LBM step count is `1`.
- [x] MPM substeps per LBM step is `1`.
- [x] Coupling mode is `moving_boundary`.
- [x] Reaction transfer mode is `engineering`.
- [x] Four-row one-step matrix exists.
- [x] Original static baseline row exists.
- [x] Runtime-geometry-only row exists.
- [x] Wall-velocity-only row exists.
- [x] Combined runtime-geometry plus wall-velocity row exists.
- [x] All matrix rows are stable.
- [x] Runtime geometry row has nonzero active-cell delta.
- [x] Wall velocity row has nonzero applied velocity.
- [x] Combined row has runtime geometry and wall velocity enabled.
- [x] Density bounds remain close to `1.0`.
- [x] LBM max velocity remains below `0.1`.
- [x] Bounce-back link counts are positive.
- [x] Hydrodynamic force proxy values are finite.
- [x] NaN count is `0`.
- [x] Inf count is `0`.
- [x] Diagnostic-only pass is true.
- [x] Persistent projected state is disabled.
- [x] Persistent displaced geometry is disabled.
- [x] LBM solid velocity persistence is disabled.
- [x] Displaced particle writes are disabled.
- [x] Dense displacement field writes are disabled.
- [x] VTR writes are disabled.
- [x] Default driver state mutation count is `0`.
- [x] Default LBM state mutation count is `0`.
- [x] Default MPM state mutation count is `0`.
- [x] Default projection state mutation count is `0`.
- [x] Original geometry hash remains stable.
- [x] Region mask hash remains stable.
- [x] Step 45 regression guard passes.
- [x] Artifact manifest passes.
- [x] README documents the Step 46 boundary.
- [x] Step 46 does not alter protected solver formula files.

## 15. Decision For Step 47

Step 46 is acceptable as a controlled one-step coupling smoke. Step 47 should only extend the chain through another explicit diagnostic contract with opt-in configuration, artifact-backed tests, and no implicit default solver-state activation.

## 16. Verification Commands

Verification uses `D:\working\taichi\env\python.exe`.

Commands:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\runtime_geometry_wall_velocity_coupling_config.py src\runtime_geometry_wall_velocity_coupling.py src\runtime_geometry_wall_velocity_diagnostics.py src\runtime_geometry_wall_velocity_state_guard.py baseline_tests\step46_common.py baseline_tests\run_step46_coupling_smoke_config_validation.py baseline_tests\run_step46_one_step_coupling_smoke_matrix.py baseline_tests\run_step46_coupling_smoke_quality.py baseline_tests\run_step46_component_effect_comparison.py baseline_tests\run_step46_mass_force_bounceback_diagnostics.py baseline_tests\run_step46_state_mutation_guard.py baseline_tests\run_step46_step45_regression_guard.py baseline_tests\run_step46_artifact_manifest.py tests\test_step46_runtime_geometry_wall_velocity_coupling_smoke_contract.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step46_coupling_smoke_config_validation.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step46_one_step_coupling_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step46_coupling_smoke_quality.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step46_component_effect_comparison.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step46_mass_force_bounceback_diagnostics.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step46_state_mutation_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step46_step45_regression_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step46_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step46_runtime_geometry_wall_velocity_coupling_smoke_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
```

## 17. GitHub Sync Information

This section is finalized by the commit and push proof. The expected target is `origin/main`.
