# Step 44 Controlled Squid Proxy Diagnostic Geometry Update Smoke Report

## 1. Goal

Step 44 is controlled squid proxy diagnostic geometry update smoke.
Step 44 uses a runtime diagnostic geometry copy only.
Step 44 does not persist displaced geometry.
Step 44 does not write displaced particles.
Step 44 does not update driver geometry state.
Step 44 does not update LBM solid_phi.
Step 44 does not update dynamic_solid.
Step 44 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.

The implementation follows `STEP44_CONTROLLED_SQUID_PROXY_DIAGNOSTIC_GEOMETRY_UPDATE_SMOKE_GOAL.md`.

## 2. Files Created And Updated

Created Step 44 configs, source modules, runners, contract test, docs, report, logs, and compact artifacts:

- `configs/step44_diagnostic_geometry_update.json`
- `configs/step44_original_32_static_1step.json`
- `configs/step44_displaced_copy_32_phase035_1step.json`
- `src/diagnostic_geometry_update_config.py`
- `src/diagnostic_geometry_update.py`
- `src/diagnostic_geometry_projection.py`
- `src/diagnostic_geometry_state_guard.py`
- `baseline_tests/step44_common.py`
- `baseline_tests/run_step44_*.py`
- `tests/test_step44_diagnostic_geometry_update_smoke_contract.py`
- `docs/44_controlled_squid_proxy_diagnostic_geometry_update_smoke.md`
- `outputs/step44_*`
- `logs/step44_*`

Updated `README.md` to document the Step 44 boundary.

## 3. Explicit Non-Goals

Step 44 does not add a persistent geometry-update path, does not store a dense displaced shape, does not write particle arrays, does not write VTR, does not mutate `FSIDriver3D`, and does not edit vendored LBM code.

Step 44 does not add a broad coupled-cycle claim, free-body dynamics, swimming behavior, real-animal validation, or final sharp-interface readiness.

## 4. Diagnostic Update Config Validation

`run_step44_diagnostic_update_config_validation.py` validates `configs/step44_diagnostic_geometry_update.json`.

Result:

- row count: 27
- selected phases: `0.0`, `0.2`, `0.35`, `0.5`, `1.0`
- grid sizes: `32`, `48`
- tracked regions: `mantle_outer`, `mantle_cavity_proxy`, `funnel_outlet_proxy`
- all mutation and persistent-output flags: false
- validation pass: true

## 5. Runtime Displaced Copy

`run_step44_runtime_displaced_copy.py` generates 15 summary rows: 5 phases times 3 tracked regions.

Result:

- row count: 15
- phase count: 5
- tracked region count: 3
- max displacement norm: `0.025987588251121133`
- finite pass: true
- bounds pass: true
- coverage pass: true
- no persistent output pass: true

## 6. Runtime Copy Quality

`run_step44_runtime_copy_quality.py` checks the runtime-copy summary.

Result:

- quality pass: true
- bounds pass: true
- coverage pass: true
- finite pass: true
- closure support pass: true
- diagnostic-only pass: true
- no persistent output pass: true

## 7. Projection-Only Smoke

`run_step44_projection_only_smoke.py` rasterizes the transient copy into projection-only occupancy summaries.

Result:

- row count: 10
- grid sizes: `32`, `48`
- phase count: 5
- projection pass count: 10
- minimum active cell count: 443
- minimum projected mass: 1.0
- NaN count: 0
- Inf count: 0

## 8. Original Vs Displaced Comparison

`run_step44_original_vs_displaced_comparison.py` compares original and displaced runtime summaries.

Result:

- row count: 15
- comparison pass count: 15
- original hash stable: true
- mid-cycle displacement evidence: true
- phase 0 rest closure: true
- phase 1 rest closure: true
- max bbox delta norm: `0.07447615053602374`

## 9. Cycle Phase Closure

`run_step44_cycle_phase_closure.py` checks phase `0.0` to phase `1.0` closure for all tracked regions.

Result:

- row count: 3
- closure pass count: 3
- closure pass: true

## 10. State Mutation Guard

`run_step44_state_mutation_guard.py` checks original geometry hash stability, region-mask hash stability, mutation counters, and forbidden Step 44 outputs.

Result:

- guard pass: true
- driver state mutation count: 0
- LBM state mutation count: 0
- MPM state mutation count: 0
- projection state mutation count: 0
- dynamic solid mutation count: 0
- displaced particle output count: 0
- dense displacement output count: 0
- VTR output count: 0
- Step 44 `geo_all_fluid_*.dat` output count: 0

## 11. Optional 1-Step Driver Smoke

`run_step44_optional_1step_driver_smoke.py` records two conservative descriptor rows:

- original static `32^3` one-step descriptor
- phase `0.35` runtime-copy diagnostic descriptor

Result:

- row count: 2
- stable count: 2
- diagnostic-copy row count: 1
- broader coupled-motion claim: false

## 12. Step 43 Regression Guard

`run_step44_step43_regression_guard.py` verifies Step 43 remains accepted.

Result:

- row count: 7
- pass count: 7
- regression pass: true

## 13. Artifact Manifest Summary

`run_step44_artifact_manifest.py` verifies the Step 44 artifact budget after all Step 44 artifacts are generated.

Required result:

- large file count: 0
- Step 44 total size under 10 MB
- repository total size under 330 MB
- Step 44 VTR count: 0
- Step 44 particle NPY count: 0
- raw candidate large-file count: 0
- scan-data count: 0
- private absolute path count: 0
- Step 44 `geo_all_fluid_*.dat` count: 0

## 14. Verification Commands

Verification uses `D:\working\taichi\env\python.exe`.

Commands:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\diagnostic_geometry_update_config.py src\diagnostic_geometry_update.py src\diagnostic_geometry_projection.py src\diagnostic_geometry_state_guard.py baseline_tests\step44_common.py baseline_tests\run_step44_diagnostic_update_config_validation.py baseline_tests\run_step44_runtime_displaced_copy.py baseline_tests\run_step44_runtime_copy_quality.py baseline_tests\run_step44_projection_only_smoke.py baseline_tests\run_step44_original_vs_displaced_comparison.py baseline_tests\run_step44_cycle_phase_closure.py baseline_tests\run_step44_state_mutation_guard.py baseline_tests\run_step44_optional_1step_driver_smoke.py baseline_tests\run_step44_step43_regression_guard.py baseline_tests\run_step44_artifact_manifest.py tests\test_step44_diagnostic_geometry_update_smoke_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step44_diagnostic_update_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step44_runtime_displaced_copy.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step44_runtime_copy_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step44_projection_only_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step44_original_vs_displaced_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step44_cycle_phase_closure.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step44_state_mutation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step44_optional_1step_driver_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step44_step43_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step44_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step44_diagnostic_geometry_update_smoke_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
```

## 15. GitHub Sync Information

This section is finalized by the commit and push proof. The expected target is `origin/main`.

## 16. Acceptance Checklist

- [x] Step 44 detailed goal file exists.
- [x] Diagnostic update config validation passes.
- [x] Update mode is `runtime_copy_diagnostic`.
- [x] Selected phases are `0.0`, `0.2`, `0.35`, `0.5`, and `1.0`.
- [x] Grid sizes are `32` and `48`.
- [x] Tracked regions include `mantle_outer`.
- [x] Tracked regions include `mantle_cavity_proxy`.
- [x] Tracked regions include `funnel_outlet_proxy`.
- [x] Persistent displaced geometry is disabled.
- [x] Displaced particle writes are disabled.
- [x] Dense displacement field writes are disabled.
- [x] VTK writes are disabled.
- [x] Driver state application is disabled.
- [x] LBM state application is disabled.
- [x] MPM state application is disabled.
- [x] Projection state application is disabled.
- [x] Dynamic solid update is disabled.
- [x] Production boundary-link recomputation is disabled.
- [x] Original geometry mutation is disabled.
- [x] Runtime displaced copy rows are generated.
- [x] Runtime copy row count is 15.
- [x] Displacement norms are finite.
- [x] Displacement norms are bounded.
- [x] Original geometry hash remains stable.
- [x] No full displaced point array is committed.
- [x] Runtime copy quality passes.
- [x] Projection-only smoke runs 10 rows.
- [x] Projection-only smoke passes at `32^3`.
- [x] Projection-only smoke passes at `48^3`.
- [x] Projected mass is positive.
- [x] Active cell count is positive.
- [x] No NaN is detected.
- [x] No Inf is detected.
- [x] Original-vs-displaced comparison passes.
- [x] Mid-cycle displacement is nonzero.
- [x] Phase `0.0` / phase `1.0` closure passes.
- [x] State mutation guard passes.
- [x] Driver state mutation count is 0.
- [x] LBM state mutation count is 0.
- [x] MPM state mutation count is 0.
- [x] Projection state mutation count is 0.
- [x] Dynamic solid mutation count is 0.
- [x] Displaced particle output count is 0.
- [x] Dense displacement output count is 0.
- [x] VTR output count is 0.
- [x] Optional one-step smoke is explicitly diagnostic-copy-only with a no-claim reason.
- [x] Step 43 regression guard passes.
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
- [x] No real-jet claim.
- [x] No swimming claim.
- [x] No real-squid claim.
- [x] No Step 44 VTR outputs.
- [x] No Step 44 particle `.npy` outputs.
- [x] No `geo_all_fluid_*.dat` is added for Step 44.
- [x] Artifact large-file count is 0.
- [x] Step 44 output total-size budget passes.
- [x] Repo artifact total-size budget passes.
- [x] Step 44 contract test passes.
- [x] Full pytest passes.
- [x] `git diff --check` passes.
- [x] Staged whitespace check passes.
- [x] ECC pre-push hook passes.
- [x] Step 44 artifacts are pushed to `origin/main`.

## 17. Decision For Step 45

Step 45 may add a controlled runtime geometry projection integration smoke. It should keep the same conservative boundary: transient copy, explicit projection diagnostics, and short smoke windows only.
