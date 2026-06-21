# Step 45 Controlled Runtime Geometry Projection Integration Smoke Goal

## 1. Objective

Implement Step 45: Controlled Runtime Geometry Projection Integration Smoke.

Step 45 must integrate the accepted Step 44 runtime displaced geometry copy into an isolated transient projection path, verify projected solid-field and boundary-coverage diagnostics for selected phases, and run ultra-short opt-in smoke descriptors without persistent geometry mutation or full-cycle moving-geometry coupling.

Step 45 is a controlled integration smoke. It may feed a phase-selected runtime displaced copy into a transient projection target and summarize projected occupancy/solid-field diagnostics. It must not promote displaced geometry into production driver state, persistent LBM state, persistent MPM state, dynamic-sold state, production boundary-link recomputation, or full prescribed moving-geometry simulation.

## 2. Accepted Inputs

Use the current repository state on `origin/main` after accepted Step 44:

- Step 44 goal: `STEP44_CONTROLLED_SQUID_PROXY_DIAGNOSTIC_GEOMETRY_UPDATE_SMOKE_GOAL.md`
- Step 44 report: `STEP44_CONTROLLED_SQUID_PROXY_DIAGNOSTIC_GEOMETRY_UPDATE_SMOKE_REPORT.md`
- Step 44 diagnostic geometry update config: `configs/step44_diagnostic_geometry_update.json`
- Step 44 runtime displaced-copy artifact: `outputs/step44_runtime_displaced_copy/runtime_displaced_copy.json`
- Step 44 projection-only smoke artifact: `outputs/step44_projection_only_smoke/projection_only_smoke.json`
- Step 44 state mutation guard: `outputs/step44_state_mutation_guard/state_mutation_guard.json`
- Step 44 artifact manifest: `outputs/step44_artifact_manifest/artifact_summary.json`
- Step 43 geometry-motion interface config: `configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json`
- Step 42 displacement artifact: `outputs/step42_geometry_displacement/geometry_displacement.json`
- Step 30 squid proxy geometry config: `configs/step30_squid_proxy_geometry.json`
- Step 30 squid proxy region config: `configs/step30_squid_proxy_region_config.json`

Step 45 must preserve the accepted Step 44 boundary:

- Step 44 uses runtime diagnostic geometry copies only.
- Step 44 does not persist displaced geometry.
- Step 44 does not update driver geometry state.
- Step 44 does not update LBM `solid_phi`.
- Step 44 does not update `dynamic_solid`.
- Step 44 does not change moving bounce-back formulas.

## 3. Required Scope

Step 45 is controlled runtime geometry projection integration smoke.

Step 45 may:

- Load Step 44 diagnostic geometry update config.
- Load Step 44 runtime displaced-copy and projection-only artifacts as regression references.
- Reuse the accepted Step 44 runtime displaced-copy construction path.
- Select phases `0.0`, `0.2`, `0.35`, `0.5`, and `1.0`.
- Use grid sizes `32` and `48`.
- Track `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy`.
- Project the runtime displaced-copy union into an isolated transient projection target.
- Write compact projected diagnostics for `solid_phi` bounds, occupancy, projected mass, active cells, boundary cells, bbox cells, and transient-only flags.
- Compare original static projection baselines against runtime displaced-copy projection rows.
- Check phase `0.0` and phase `1.0` projection closure.
- Align Step 45 transient projection rows with accepted Step 44 detached projection-only smoke rows.
- Record an ultra-short opt-in projection driver smoke descriptor for original static and phase `0.35` runtime-copy paths.
- Prove state mutation guards and artifact budgets.
- Write small CSV/JSON/log artifacts and contract tests.

Step 45 must not:

- Persist projected state.
- Persist displaced geometry.
- Write displaced particles.
- Write dense displacement fields.
- Write VTR outputs.
- Write Step 45 particle `.npy` outputs.
- Update default driver geometry state.
- Update default LBM `solid_phi` or `solid_vel`.
- Update default MPM state.
- Update default projection state.
- Update `dynamic_solid`.
- Recompute production boundary links from displaced geometry.
- Change moving bounce-back formulas.
- Change LBM collision or streaming formulas.
- Change MPM constitutive formulas.
- Change projection formulas.
- Change coupler formulas.
- Change wall-velocity formulas.
- Implement free-body motion.
- Implement body trajectory.
- Implement squid swimming.
- Claim real jet validation.
- Claim real squid validation.
- Claim production-ready sharp-interface FSI.
- Edit `external/taichi_LBM3D`.
- Add raw real geometry or scan data.
- Add Step 45 `geo_all_fluid_*.dat` artifacts.

## 4. Required Configuration Files

Add `configs/step45_runtime_geometry_projection_integration.json`.

Required semantics:

- `projection_integration_id = "step45_runtime_geometry_projection_integration_smoke"`
- `diagnostic_geometry_update_config_path = "configs/step44_diagnostic_geometry_update.json"`
- `geometry_motion_interface_config_path = "configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json"`
- `displacement_artifact_path = "outputs/step42_geometry_displacement/geometry_displacement.json"`
- `geometry_config_path = "configs/step30_squid_proxy_geometry.json"`
- `region_config_path = "configs/step30_squid_proxy_region_config.json"`
- `step44_projection_artifact_path = "outputs/step44_projection_only_smoke/projection_only_smoke.json"`
- `selected_phases = [0.0, 0.2, 0.35, 0.5, 1.0]`
- `grid_sizes = [32, 48]`
- `tracked_regions = ["mantle_outer", "mantle_cavity_proxy", "funnel_outlet_proxy"]`
- `integration_mode = "transient_projection_only"`
- `persist_projected_state = false`
- `persist_displaced_geometry = false`
- `write_displaced_particles = false`
- `write_dense_displacement_field = false`
- `write_vtk = false`
- `apply_to_driver_state = false`
- `apply_to_default_lbm_state = false`
- `apply_to_default_mpm_state = false`
- `apply_to_default_projection_state = false`
- `update_dynamic_solid = false`
- `recompute_production_boundary_links = false`
- `mutate_original_geometry = false`
- `diagnostic_only = true`
- `deterministic = true`

Add ultra-short smoke descriptors:

- `configs/step45_original_32_static_1step.json`
- `configs/step45_displaced_phase035_32_moving_boundary_1step.json`
- `configs/step45_displaced_phase035_32_link_area_1step.json`

These descriptors are Step 45 validation descriptors only. They must disable VTK and particle output and must not activate persistent runtime geometry updates.

## 5. Required Source Modules

Add `src/runtime_geometry_projection_config.py`.

This module must define an immutable `RuntimeGeometryProjectionIntegrationConfig` and validation helpers. Validation must reject any config that enables persistent projected state, persistent displaced geometry, particle writes, dense displacement writes, VTK writes, driver-state application, default LBM state application, default MPM state application, default projection-state application, dynamic-sold update, production boundary-link recomputation, or original-geometry mutation.

Add `src/runtime_geometry_projection.py`.

This module must load accepted Step 44 inputs, build transient runtime displaced-copy projection rows, compute projected mass, active cell count, solid-phi bounds, boundary-cell count, bbox-cell bounds, region coverage, and transient-only flags, then write compact CSV/JSON rows. It must not modify `src/projection.py`, production driver state, or any persistent geometry artifact.

Add `src/runtime_geometry_projection_quality.py`.

This module must analyze Step 45 projection rows for row count, finite values, valid bounds, active cells, projected mass, solid-phi bounds, phase coverage, grid coverage, transient-only status, and no persistent state.

Add `src/runtime_geometry_projection_consistency.py`.

This module must compare original static projection rows against runtime displaced-copy projection rows, summarize phase closure between phases `0.0` and `1.0`, and compare Step 44 projection-only smoke rows against Step 45 transient projection integration rows.

Add `src/runtime_geometry_projection_state_guard.py`.

This module must prove original geometry hashes and region-mask hashes remain stable, mutation counters remain zero, and no forbidden Step 45 outputs are written.

## 6. Required Baseline Runners

Add:

- `baseline_tests/step45_common.py`
- `baseline_tests/run_step45_projection_integration_config_validation.py`
- `baseline_tests/run_step45_runtime_projection_integration.py`
- `baseline_tests/run_step45_runtime_projection_quality.py`
- `baseline_tests/run_step45_original_vs_runtime_projection_comparison.py`
- `baseline_tests/run_step45_projection_phase_closure.py`
- `baseline_tests/run_step45_step44_projection_alignment.py`
- `baseline_tests/run_step45_runtime_projection_state_guard.py`
- `baseline_tests/run_step45_ultrashort_projection_driver_smoke.py`
- `baseline_tests/run_step45_step44_regression_guard.py`
- `baseline_tests/run_step45_artifact_manifest.py`

Each runner must write a log marker under `logs/step45_*.log` and compact CSV/JSON artifacts under `outputs/step45_*`.

## 7. Runner Acceptance Criteria

`run_step45_projection_integration_config_validation.py` must prove:

- validation passes,
- `integration_mode == "transient_projection_only"`,
- selected phase count is `5`,
- grid sizes are `[32, 48]`,
- tracked region count is `3`,
- all mutation/write/persistence flags are disabled.

`run_step45_runtime_projection_integration.py` must generate:

- `row_count == 10`,
- `grid_size_count == 2`,
- `phase_count == 5`,
- `projection_pass_count == 10`,
- `projected_mass > 0` for every row,
- `active_cell_count > 0` for every row,
- `solid_phi_min >= 0`,
- `solid_phi_max <= 1`,
- no NaN,
- no Inf,
- `transient_only == true`,
- `persist_projected_state == false`.

`run_step45_runtime_projection_quality.py` must prove:

- `quality_pass == true`,
- `row_count_pass == true`,
- `finite_pass == true`,
- `bounds_pass == true`,
- `active_cell_pass == true`,
- `projected_mass_pass == true`,
- `solid_phi_bounds_pass == true`,
- `phase_coverage_pass == true`,
- `grid_coverage_pass == true`,
- `transient_only_pass == true`,
- `no_persistent_state_pass == true`.

`run_step45_original_vs_runtime_projection_comparison.py` must prove:

- `row_count == 10`,
- comparison pass is true,
- phase `0.0` is close to original,
- phase `1.0` is close to original,
- mid-cycle projection delta is nonzero,
- projected mass deltas are finite,
- active-cell deltas are finite,
- bbox deltas are finite.

`run_step45_projection_phase_closure.py` must prove:

- `row_count == 2`,
- closure pass is true at `32^3` and `48^3`,
- phase `0.0` and phase `1.0` projected mass delta is within tolerance,
- active-cell delta is bounded,
- bbox delta is bounded.

`run_step45_step44_projection_alignment.py` must prove:

- `row_count == 10`,
- alignment pass count is `10`,
- projected mass deltas are finite and bounded,
- active-cell count deltas are bounded,
- solid-phi min/max deltas are zero or conservatively bounded.

`run_step45_runtime_projection_state_guard.py` must prove:

- guard pass is true,
- original geometry hash before equals after,
- region-mask hash before equals after,
- driver state mutation count is `0`,
- default LBM state mutation count is `0`,
- default MPM state mutation count is `0`,
- default projection state mutation count is `0`,
- dynamic-sold mutation count is `0`,
- persistent projected state count is `0`,
- displaced particle output count is `0`,
- dense displacement output count is `0`,
- VTR output count is `0`,
- Step 45 `geo_all_fluid_*.dat` count is `0`.

`run_step45_ultrashort_projection_driver_smoke.py` must record three conservative smoke rows:

- original `32^3` static one-step moving-boundary engineering descriptor,
- phase `0.35` runtime-copy `32^3` one-step moving-boundary engineering descriptor,
- phase `0.35` runtime-copy `32^3` one-step moving-boundary link-area descriptor.

Acceptance:

- `row_count == 3`,
- `stable_count == 3`,
- diagnostic copy row count is `2`,
- completed LBM steps are at least `1`,
- total MPM substeps are at least `1`,
- `rho_min > 0.95`,
- `rho_max < 1.05`,
- `lbm_max_v < 0.1`,
- `projected_mass > 0`,
- `active_cell_count > 0`,
- quality pass is true,
- diagnostic-copy-only is true for displaced-copy rows,
- no persistent geometry mutation,
- no full coupled-motion claim.

`run_step45_step44_regression_guard.py` must prove:

- Step 44 report exists,
- Step 44 runtime displaced-copy row count is `15`,
- Step 44 projection-only row count is `10`,
- Step 44 state mutation guard passes,
- Step 44 artifact large-file count is `0`,
- Step 44 VTR count is `0`,
- Step 44 particle NPY count is `0`,
- Step 44 `geo_all_fluid_*.dat` count is `0`.

`run_step45_artifact_manifest.py` must prove:

- `large_file_count == 0`,
- `step45_total_size_mb < 15`,
- repo `total_size_mb < 340`,
- `step45_vtr_count == 0`,
- `step45_particle_npy_count == 0`,
- raw candidate large-file count is `0`,
- scan-data count is `0`,
- private absolute path count is `0`,
- Step 45 `geo_all_fluid_*.dat` count is `0`.

## 8. Contract Test

Add `tests/test_step45_runtime_geometry_projection_integration_contract.py` with tests for:

- required artifacts,
- projection integration config validity,
- runtime projection integration validity,
- runtime projection quality,
- original-vs-runtime projection comparison,
- projection phase closure,
- Step 44 projection alignment,
- runtime projection state guard,
- ultra-short projection driver smoke,
- Step 44 regression guard,
- default modes unchanged,
- docs scope and forbidden claims,
- artifact budget,
- report acceptance complete,
- no persistent geometry outputs,
- no full coupled geometry claims.

The contract test must avoid importing heavy package initializers if that risks pre-push hook instability. Prefer source-text and artifact-backed assertions where possible.

## 9. Documentation And Report

Add:

- `docs/45_controlled_runtime_geometry_projection_integration_smoke.md`
- `STEP45_CONTROLLED_RUNTIME_GEOMETRY_PROJECTION_INTEGRATION_SMOKE_REPORT.md`

Required scope phrases:

- `Step 45 is controlled runtime geometry projection integration smoke.`
- `Step 45 uses transient projection state only.`
- `Step 45 does not persist projected state.`
- `Step 45 does not persist displaced geometry.`
- `Step 45 does not write displaced particles.`
- `Step 45 does not update default driver geometry.`
- `Step 45 does not persist LBM solid_phi updates.`
- `Step 45 does not update dynamic_solid.`
- `Step 45 does not change moving bounce-back formulas.`
- `The default geometry_motion_mode remains static.`
- `The default geometry_motion_application_mode remains disabled.`

Forbidden claims:

- `full coupled geometry motion is implemented`
- `production moving geometry is implemented`
- `driver geometry is persistently updated`
- `MPM particles are persistently displaced`
- `LBM solid_phi is persistently updated`
- `dynamic_solid is persistently updated`
- `production boundary links are recomputed`
- `moving bounce-back formula is changed`
- `squid swimming is implemented`
- `free-body motion is implemented`
- `real jet validation`
- `real squid simulation is validated`
- `production-ready sharp-interface FSI`

Update `README.md` with a Step 45 implemented bullet and Step 45 boundary section.

The report must include:

- goal,
- files created and updated,
- explicit non-goals,
- config validation,
- runtime projection integration,
- runtime projection quality,
- original-vs-runtime projection comparison,
- projection phase closure,
- Step 44 projection alignment,
- runtime projection state guard,
- ultra-short projection driver smoke,
- Step 44 regression guard,
- artifact manifest summary,
- verification commands,
- GitHub sync information,
- acceptance checklist,
- decision for Step 46.

## 10. Verification Commands

Use the trusted interpreter:

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
git diff --check
git diff --cached --check
```

The final `git push origin main` must let the ECC pre-push hook run and pass.

## 11. Acceptance Checklist

- [ ] Step 45 detailed goal file exists.
- [ ] Projection integration config validation passes.
- [ ] Integration mode is `transient_projection_only`.
- [ ] Selected phases are `0.0`, `0.2`, `0.35`, `0.5`, and `1.0`.
- [ ] Grid sizes are `32` and `48`.
- [ ] Tracked regions include `mantle_outer`.
- [ ] Tracked regions include `mantle_cavity_proxy`.
- [ ] Tracked regions include `funnel_outlet_proxy`.
- [ ] Persistent projected state is disabled.
- [ ] Persistent displaced geometry is disabled.
- [ ] Displaced particle writes are disabled.
- [ ] Dense displacement field writes are disabled.
- [ ] VTK writes are disabled.
- [ ] Driver state application is disabled.
- [ ] Default LBM state application is disabled.
- [ ] Default MPM state application is disabled.
- [ ] Default projection state application is disabled.
- [ ] Dynamic solid update is disabled.
- [ ] Production boundary-link recomputation is disabled.
- [ ] Original geometry mutation is disabled.
- [ ] Runtime projection integration runs 10 rows.
- [ ] Projection passes at `32^3`.
- [ ] Projection passes at `48^3`.
- [ ] Projected mass is positive.
- [ ] Active cell count is positive.
- [ ] Solid-phi bounds are valid.
- [ ] No NaN is detected.
- [ ] No Inf is detected.
- [ ] Runtime projection quality passes.
- [ ] Original-vs-runtime projection comparison passes.
- [ ] Mid-cycle projection delta is nonzero.
- [ ] Phase `0.0` / phase `1.0` projection closure passes.
- [ ] Step 44 projection alignment passes.
- [ ] Runtime projection state guard passes.
- [ ] Original geometry hash remains stable.
- [ ] Default LBM state mutation count is `0`.
- [ ] Default MPM state mutation count is `0`.
- [ ] Default projection state mutation count is `0`.
- [ ] Persistent projected state count is `0`.
- [ ] Displaced particle output count is `0`.
- [ ] Dense displacement output count is `0`.
- [ ] VTR output count is `0`.
- [ ] Step 45 `geo_all_fluid_*.dat` count is `0`.
- [ ] Ultra-short projection driver smoke passes.
- [ ] No full coupled-motion claim is made.
- [ ] Step 44 regression guard passes.
- [ ] Default `geometry_motion_mode` remains `static`.
- [ ] Default `geometry_motion_application_mode` remains `disabled`.
- [ ] Default `boundary_motion_mode` remains `static`.
- [ ] Default `wall_velocity_application_mode` remains `disabled`.
- [ ] No default behavior changes.
- [ ] No moving bounce-back formula changes.
- [ ] No LBM collision formula changes.
- [ ] No MPM constitutive formula changes.
- [ ] No projection formula changes.
- [ ] No `external/taichi_LBM3D` edits.
- [ ] No real jet validation claim.
- [ ] No swimming claim.
- [ ] No real squid validation claim.
- [ ] No Step 45 VTR outputs.
- [ ] No Step 45 particle `.npy` outputs.
- [ ] Artifact large-file count is `0`.
- [ ] Step 45 output total-size budget passes.
- [ ] Repo artifact total-size budget passes.
- [ ] `logs/step45_pytest.log` exists.
- [ ] Step 45 contract test passes.
- [ ] Full pytest passes.
- [ ] `git diff --check` passes.
- [ ] Staged whitespace check passes.
- [ ] ECC pre-push hook passes.
- [ ] Step 45 artifacts are pushed to `origin/main`.

## 12. Decision For Step 46

If Step 45 passes, Step 46 may consider a controlled runtime geometry plus wall-velocity one-step coupling smoke. Step 46 can combine transient runtime geometry projection, opt-in solid-velocity application, and moving-boundary bounce-back in a one-step or ultra-short experimental smoke. Step 46 must still not claim full-cycle moving geometry, free-body motion, squid swimming, real jet validation, or production sharp-interface FSI.
