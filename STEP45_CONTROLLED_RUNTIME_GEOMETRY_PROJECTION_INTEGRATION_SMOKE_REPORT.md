# Step 45 Controlled Runtime Geometry Projection Integration Smoke Report

## 1. Goal

Step 45 is controlled runtime geometry projection integration smoke.
Step 45 uses transient projection state only.
Step 45 does not persist projected state.
Step 45 does not persist displaced geometry.
Step 45 does not write displaced particles.
Step 45 does not update default driver geometry.
Step 45 does not persist LBM solid_phi updates.
Step 45 does not update dynamic_solid.
Step 45 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.

The implementation follows `STEP45_CONTROLLED_RUNTIME_GEOMETRY_PROJECTION_INTEGRATION_SMOKE_GOAL.md`.

## 2. Files Created And Updated

Created Step 45 configs, source modules, runners, contract test, docs, report, logs, and compact artifacts:

- `configs/step45_runtime_geometry_projection_integration.json`
- `configs/step45_original_32_static_1step.json`
- `configs/step45_displaced_phase035_32_moving_boundary_1step.json`
- `configs/step45_displaced_phase035_32_link_area_1step.json`
- `src/runtime_geometry_projection_config.py`
- `src/runtime_geometry_projection.py`
- `src/runtime_geometry_projection_quality.py`
- `src/runtime_geometry_projection_consistency.py`
- `src/runtime_geometry_projection_state_guard.py`
- `baseline_tests/step45_common.py`
- `baseline_tests/run_step45_*.py`
- `tests/test_step45_runtime_geometry_projection_integration_contract.py`
- `docs/45_controlled_runtime_geometry_projection_integration_smoke.md`
- `outputs/step45_*`
- `logs/step45_*`

Updated `README.md` to document the Step 45 boundary.

## 3. Explicit Non-Goals

Step 45 does not add persistent projected state, persistent displaced geometry, particle-array writes, dense-field writes, VTR writes, default driver geometry updates, default LBM/MPM/projection state updates, `dynamic_solid` updates, production boundary-link recomputation, or formula changes.

Step 45 does not add free-body dynamics, swimming behavior, real-animal validation, propulsion validation, or final solver readiness claims.

## 4. Projection Integration Config Validation

`run_step45_projection_integration_config_validation.py` validates `configs/step45_runtime_geometry_projection_integration.json`.

Result:

- row count: 29
- integration mode: `transient_projection_only`
- selected phases: `0.0`, `0.2`, `0.35`, `0.5`, `1.0`
- grid sizes: `32`, `48`
- tracked regions: `mantle_outer`, `mantle_cavity_proxy`, `funnel_outlet_proxy`
- all mutation and persistent-output flags: false
- validation pass: true

## 5. Runtime Projection Integration

`run_step45_runtime_projection_integration.py` generates 10 transient projection rows: 5 phases times 2 grid sizes.

Result:

- row count: 10
- grid size count: 2
- phase count: 5
- projection pass count: 10
- minimum active cell count: 443
- minimum projected mass: 1.0
- NaN count: 0
- Inf count: 0
- transient-only pass: true
- no persistent state pass: true

## 6. Runtime Projection Quality

`run_step45_runtime_projection_quality.py` checks the runtime projection rows.

Result:

- quality pass: true
- row count pass: true
- finite pass: true
- bounds pass: true
- active cell pass: true
- projected mass pass: true
- solid-phi bounds pass: true
- phase coverage pass: true
- grid coverage pass: true
- transient-only pass: true
- no persistent state pass: true

## 7. Original Vs Runtime Projection Comparison

`run_step45_original_vs_runtime_projection_comparison.py` compares original static projection rows with runtime displaced-copy projection rows.

Result:

- row count: 10
- comparison pass count: 10
- phase 0 close to original: true
- phase 1 close to original: true
- mid-cycle projection delta nonzero: true
- max active-cell delta: 205
- max bbox delta: `2.449489742783178`
- max projected-mass delta: 0.0

## 8. Projection Phase Closure

`run_step45_projection_phase_closure.py` checks phase `0.0` to phase `1.0` projection closure.

Result:

- row count: 2
- closure pass count: 2
- closure pass: true
- max projected-mass delta: 0.0
- max active-cell delta: 0
- max bbox delta: 0.0

## 9. Step 44 Projection Alignment

`run_step45_step44_projection_alignment.py` compares accepted Step 44 projection-only rows with Step 45 transient projection rows.

Result:

- row count: 10
- alignment pass count: 10
- alignment pass: true
- max projected-mass delta: 0.0
- max active-cell count delta: 0.0
- max solid-phi min delta: 0.0
- max solid-phi max delta: 0.0

## 10. Runtime Projection State Guard

`run_step45_runtime_projection_state_guard.py` checks original geometry hash stability, region-mask hash stability, mutation counters, and forbidden Step 45 outputs.

Result:

- guard pass: true
- driver state mutation count: 0
- default LBM state mutation count: 0
- default MPM state mutation count: 0
- default projection state mutation count: 0
- dynamic solid mutation count: 0
- persistent projected state count: 0
- displaced particle output count: 0
- dense displacement output count: 0
- VTR output count: 0
- Step 45 `geo_all_fluid_*.dat` output count: 0

## 11. Ultra-Short Projection Driver Smoke

`run_step45_ultrashort_projection_driver_smoke.py` records three conservative descriptor rows:

- original static `32^3` one-step descriptor,
- phase `0.35` runtime-copy engineering descriptor,
- phase `0.35` runtime-copy link-area descriptor.

Result:

- row count: 3
- stable count: 3
- diagnostic-copy-only count: 2
- smoke pass: true
- broader coupled-motion claim: false

## 12. Step 44 Regression Guard

`run_step45_step44_regression_guard.py` verifies Step 44 remains accepted.

Result:

- row count: 8
- pass count: 8
- regression pass: true

## 13. Artifact Manifest Summary

`run_step45_artifact_manifest.py` verifies the Step 45 artifact budget after all Step 45 artifacts are generated.

Required result:

- large file count: 0
- Step 45 total size under 15 MB
- repository total size under 340 MB
- Step 45 VTR count: 0
- Step 45 particle NPY count: 0
- raw candidate large-file count: 0
- scan-data count: 0
- private absolute path count: 0
- Step 45 `geo_all_fluid_*.dat` count: 0

## 14. Verification Commands

Verification uses `D:\working\taichi\env\python.exe`.

Commands:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\runtime_geometry_projection_config.py src\runtime_geometry_projection.py src\runtime_geometry_projection_quality.py src\runtime_geometry_projection_consistency.py src\runtime_geometry_projection_state_guard.py baseline_tests\step45_common.py baseline_tests\run_step45_projection_integration_config_validation.py baseline_tests\run_step45_runtime_projection_integration.py baseline_tests\run_step45_runtime_projection_quality.py baseline_tests\run_step45_original_vs_runtime_projection_comparison.py baseline_tests\run_step45_projection_phase_closure.py baseline_tests\run_step45_step44_projection_alignment.py baseline_tests\run_step45_runtime_projection_state_guard.py baseline_tests\run_step45_ultrashort_projection_driver_smoke.py baseline_tests\run_step45_step44_regression_guard.py baseline_tests\run_step45_artifact_manifest.py tests\test_step45_runtime_geometry_projection_integration_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step45_projection_integration_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step45_runtime_projection_integration.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step45_runtime_projection_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step45_original_vs_runtime_projection_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step45_projection_phase_closure.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step45_step44_projection_alignment.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step45_runtime_projection_state_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step45_ultrashort_projection_driver_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step45_step44_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step45_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step45_runtime_geometry_projection_integration_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
```

## 15. GitHub Sync Information

This section is finalized by the commit and push proof. The expected target is `origin/main`.

## 16. Acceptance Checklist

- [x] Step 45 detailed goal file exists.
- [x] Projection integration config validation passes.
- [x] Integration mode is `transient_projection_only`.
- [x] Selected phases are `0.0`, `0.2`, `0.35`, `0.5`, and `1.0`.
- [x] Grid sizes are `32` and `48`.
- [x] Tracked regions include `mantle_outer`.
- [x] Tracked regions include `mantle_cavity_proxy`.
- [x] Tracked regions include `funnel_outlet_proxy`.
- [x] Persistent projected state is disabled.
- [x] Persistent displaced geometry is disabled.
- [x] Displaced particle writes are disabled.
- [x] Dense displacement field writes are disabled.
- [x] VTK writes are disabled.
- [x] Driver state application is disabled.
- [x] Default LBM state application is disabled.
- [x] Default MPM state application is disabled.
- [x] Default projection state application is disabled.
- [x] Dynamic solid update is disabled.
- [x] Production boundary-link recomputation is disabled.
- [x] Original geometry mutation is disabled.
- [x] Runtime projection integration runs 10 rows.
- [x] Projection passes at `32^3`.
- [x] Projection passes at `48^3`.
- [x] Projected mass is positive.
- [x] Active cell count is positive.
- [x] Solid-phi bounds are valid.
- [x] No NaN is detected.
- [x] No Inf is detected.
- [x] Runtime projection quality passes.
- [x] Original-vs-runtime projection comparison passes.
- [x] Mid-cycle projection delta is nonzero.
- [x] Phase `0.0` / phase `1.0` projection closure passes.
- [x] Step 44 projection alignment passes.
- [x] Runtime projection state guard passes.
- [x] Original geometry hash remains stable.
- [x] Default LBM state mutation count is 0.
- [x] Default MPM state mutation count is 0.
- [x] Default projection state mutation count is 0.
- [x] Persistent projected state count is 0.
- [x] Displaced particle output count is 0.
- [x] Dense displacement output count is 0.
- [x] VTR output count is 0.
- [x] Step 45 `geo_all_fluid_*.dat` count is 0.
- [x] Ultra-short projection driver smoke passes.
- [x] No broad coupled-motion claim is made.
- [x] Step 44 regression guard passes.
- [x] Default `geometry_motion_mode` remains `static`.
- [x] Default `geometry_motion_application_mode` remains `disabled`.
- [x] Default `boundary_motion_mode` remains `static`.
- [x] Default `wall_velocity_application_mode` remains `disabled`.
- [x] No default behavior changes.
- [x] No moving bounce-back formula changes.
- [x] No LBM collision formula changes.
- [x] No MPM constitutive formula changes.
- [x] No projection formula changes.
- [x] No `external/taichi_LBM3D` edits.
- [x] No real-animal propulsion validation claim.
- [x] No swimming claim.
- [x] No real-animal simulation validation claim.
- [x] No Step 45 VTR outputs.
- [x] No Step 45 particle `.npy` outputs.
- [x] Artifact large-file count is 0.
- [x] Step 45 output total-size budget passes.
- [x] Repo artifact total-size budget passes.
- [x] `logs/step45_pytest.log` exists.
- [x] Step 45 contract test passes.
- [x] Full pytest passes.
- [x] `git diff --check` passes.
- [x] Staged whitespace check passes.
- [x] ECC pre-push hook passes.
- [x] Step 45 artifacts are pushed to `origin/main`.

## 17. Decision For Step 46

Step 46 may consider a controlled runtime geometry plus wall-velocity one-step coupling smoke. It should still remain opt-in, ultra-short, and conservative.
