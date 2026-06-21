# Step 44 Controlled Squid Proxy Diagnostic Geometry Update Smoke Goal

## 1. Objective

Implement Step 44: Controlled Squid Proxy Diagnostic Geometry Update Smoke.

Step 44 must create a transient runtime diagnostic geometry-update copy from the accepted Step 42 prescribed geometry displacement diagnostics, run projection-only smoke checks on that copy at 32^3 and 48^3, run a tightly scoped optional 32^3 one-step driver smoke descriptor, and prove that original driver state, default modes, solver formulas, and persistent geometry artifacts remain unchanged.

The Step 44 implementation must stay diagnostic and contract-first. It may summarize a displaced runtime copy and use that copy in isolated projection-only diagnostics, but it must not promote geometry motion into a full coupled moving-geometry simulation.

## 2. Accepted Inputs

Use the current repository state on `origin/main` after Step 43:

- Step 42 displacement config: `configs/step42_squid_proxy_geometry_displacement.json`
- Step 42 displacement artifact: `outputs/step42_geometry_displacement/geometry_displacement.json`
- Step 43 geometry-motion interface config: `configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json`
- Step 30 squid proxy geometry config: `configs/step30_squid_proxy_geometry.json`
- Step 30 squid proxy region config: `configs/step30_squid_proxy_region_config.json`
- Step 43 report and guards as regression evidence

Step 44 must preserve the Step 43 result: `geometry_motion_mode` defaults to `static`, `geometry_motion_application_mode` defaults to `disabled`, and Step 43 remains diagnostic/report-only.

## 3. Required Scope

Step 44 is controlled squid proxy diagnostic geometry update smoke.

Step 44 uses a runtime diagnostic geometry copy only.

Step 44 may:

- Load Step 42 displacement diagnostics.
- Select five representative phases: `0.0`, `0.2`, `0.35`, `0.5`, and `1.0`.
- Use the three tracked regions `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy`.
- Build transient displaced point summaries inside runner/source code.
- Write compact CSV/JSON/NPZ/log artifacts.
- Run projection-only smoke rows for 5 phases times 2 grid sizes.
- Run an optional 32^3 one-step smoke descriptor that distinguishes original geometry from diagnostic copy scope without claiming full coupled moving geometry validation.
- Compare original vs displaced summaries.
- Check cycle closure between phase `0.0` and phase `1.0`.
- Prove state mutation guards and artifact budgets.

Step 44 must not:

- Persist displaced geometry.
- Commit full displaced point arrays.
- Write displaced particle files.
- Write dense displacement field outputs.
- Write VTR files.
- Add Step 44 particle `.npy` outputs.
- Update original `GeometryConfig`.
- Mutate `FSIDriver3D` persistent geometry state.
- Update MPM particles in `FSIDriver3D`.
- Update LBM `solid_phi` or `solid_vel` in persistent driver state.
- Update `dynamic_solid` as a long-term coupled path.
- Recompute production boundary links from displaced geometry.
- Change moving bounce-back formulas.
- Change LBM collision or streaming formulas.
- Change MPM constitutive formulas.
- Change projection formulas.
- Change coupler formulas.
- Change wall-velocity formulas.
- Implement free-body motion.
- Implement squid swimming.
- Claim real jet validation.
- Claim real squid validation.
- Claim production-ready sharp-interface FSI.
- Edit `external/taichi_LBM3D`.
- Add raw real geometry or scan data.
- Add `geo_all_fluid_*.dat` Step 44 artifacts.

## 4. New Configuration Files

Add `configs/step44_diagnostic_geometry_update.json` with these semantics:

- `geometry_update_id = "step44_diagnostic_geometry_update_smoke"`
- `geometry_motion_interface_config_path = "configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json"`
- `displacement_config_path = "configs/step42_squid_proxy_geometry_displacement.json"`
- `displacement_artifact_path = "outputs/step42_geometry_displacement/geometry_displacement.json"`
- `geometry_config_path = "configs/step30_squid_proxy_geometry.json"`
- `region_config_path = "configs/step30_squid_proxy_region_config.json"`
- `selected_phases = [0.0, 0.2, 0.35, 0.5, 1.0]`
- `grid_sizes = [32, 48]`
- `tracked_regions = ["mantle_outer", "mantle_cavity_proxy", "funnel_outlet_proxy"]`
- `update_mode = "runtime_copy_diagnostic"`
- `persist_displaced_geometry = false`
- `write_displaced_particles = false`
- `write_dense_displacement_field = false`
- `write_vtk = false`
- `apply_to_driver_state = false`
- `apply_to_lbm_state = false`
- `apply_to_mpm_state = false`
- `apply_to_projection_state = false`
- `update_dynamic_solid = false`
- `recompute_production_boundary_links = false`
- `mutate_original_geometry = false`
- `diagnostic_only = true`
- `deterministic = true`

Add optional smoke descriptors:

- `configs/step44_original_32_static_1step.json`
- `configs/step44_displaced_copy_32_phase035_1step.json`

These descriptors are Step 44 validation descriptors, not production driver activation configs. They must keep VTK and particle output disabled and must not require new persistent driver state.

## 5. New Source Modules

Add `src/diagnostic_geometry_update_config.py`.

This module must define an immutable configuration object and validation helpers for the Step 44 diagnostic update config. Validation must reject any config that enables persistent geometry mutation, displaced particle writes, dense displacement writes, VTR writes, driver/LBM/MPM/projection state application, dynamic solid update, or production boundary-link recomputation.

Add `src/diagnostic_geometry_update.py`.

This module must load the accepted Step 42/43 inputs, sample deterministic squid proxy region points, build phase-selected runtime displaced copy summaries, compare original/displaced summaries, compute stable hashes, and write compact rows. It must not write full displaced arrays.

Add `src/diagnostic_geometry_projection.py`.

This module must run projection-only diagnostics on transient displaced-copy points for `32^3` and `48^3` without modifying persistent driver state. It may rasterize sampled runtime copy points into compact occupancy/projection summaries. It must not change `src/projection.py` formulas.

Add `src/diagnostic_geometry_state_guard.py`.

This module must check original geometry hash stability, region-mask hash stability, absence of forbidden Step 44 artifacts, and zero mutation counters for driver/LBM/MPM/projection/dynamic-sold state.

## 6. New Baseline Runners

Add:

- `baseline_tests/step44_common.py`
- `baseline_tests/run_step44_diagnostic_update_config_validation.py`
- `baseline_tests/run_step44_runtime_displaced_copy.py`
- `baseline_tests/run_step44_runtime_copy_quality.py`
- `baseline_tests/run_step44_projection_only_smoke.py`
- `baseline_tests/run_step44_original_vs_displaced_comparison.py`
- `baseline_tests/run_step44_cycle_phase_closure.py`
- `baseline_tests/run_step44_state_mutation_guard.py`
- `baseline_tests/run_step44_optional_1step_driver_smoke.py`
- `baseline_tests/run_step44_step43_regression_guard.py`
- `baseline_tests/run_step44_artifact_manifest.py`

Each runner must write a log marker under `logs/step44_*.log` and compact CSV/JSON artifacts under `outputs/step44_*`.

## 7. Runner Acceptance Criteria

`run_step44_diagnostic_update_config_validation.py` must prove:

- validation passes,
- update mode is `runtime_copy_diagnostic`,
- selected phase count is 5,
- grid sizes are `[32, 48]`,
- tracked region count is 3,
- all mutation/write flags are disabled.

`run_step44_runtime_displaced_copy.py` must generate:

- `row_count == 15`,
- `phase_count == 5`,
- `tracked_region_count == 3`,
- `point_count > 0` for every row,
- finite displacement norms,
- bounded displacement norms,
- original hash present,
- displaced summary hash present,
- persistent geometry and particle output flags false.

`run_step44_runtime_copy_quality.py` must prove:

- `quality_pass == true`,
- `bounds_pass == true`,
- `coverage_pass == true`,
- `finite_pass == true`,
- `closure_support_pass == true`,
- `diagnostic_only_pass == true`,
- `no_persistent_output_pass == true`.

`run_step44_projection_only_smoke.py` must generate:

- `row_count == 10`,
- `grid_size_count == 2`,
- `phase_count == 5`,
- `projection_pass_count == 10`,
- positive projected mass,
- positive active cell count,
- `solid_phi_min >= 0`,
- `solid_phi_max <= 1`,
- no NaN or Inf.

`run_step44_original_vs_displaced_comparison.py` must prove:

- `row_count == 15`,
- comparison pass is true,
- original hash remains stable,
- mid-cycle displacement is nonzero,
- phase `0.0` and phase `1.0` are close to rest,
- bbox deltas are finite and bounded.

`run_step44_cycle_phase_closure.py` must prove closure for:

- `mantle_outer`,
- `mantle_cavity_proxy`,
- `funnel_outlet_proxy`.

`run_step44_state_mutation_guard.py` must prove:

- guard pass is true,
- original geometry hash before equals after,
- region mask hash before equals after,
- driver state mutation count is 0,
- LBM state mutation count is 0,
- MPM state mutation count is 0,
- projection state mutation count is 0,
- dynamic solid mutation count is 0,
- displaced particle output count is 0,
- dense displacement output count is 0,
- VTR output count is 0,
- Step 44 `geo_all_fluid_*.dat` count is 0.

`run_step44_optional_1step_driver_smoke.py` must be conservative:

- It may run a true one-step original 32^3 driver row if affordable.
- It may represent diagnostic displaced copy as a one-step diagnostic-copy smoke descriptor if the production driver cannot safely accept runtime copy points yet.
- It must not claim full coupled moving geometry validation.
- It must record `diagnostic_copy_only == true` for displaced-copy scope.
- It must record no persistent geometry mutation.

`run_step44_step43_regression_guard.py` must prove:

- Step 43 report exists,
- Step 43 diagnostic-only config validation passed,
- Step 43 no geometry mutation guard passed,
- Step 43 artifact manifest large-file count is 0,
- Step 43 did not produce Step 43 VTR or particle `.npy` artifacts.

`run_step44_artifact_manifest.py` must prove:

- `large_file_count == 0`,
- `step44_total_size_mb < 10`,
- repo `total_size_mb < 330`,
- `step44_vtr_count == 0`,
- `step44_particle_npy_count == 0`,
- `raw_candidate_large_file_count == 0`,
- `scan_data_file_count == 0`,
- `private_absolute_path_count == 0`,
- `geo_all_fluid_dat_count_added == 0`.

## 8. Contract Test

Add `tests/test_step44_diagnostic_geometry_update_smoke_contract.py` with tests for:

- required artifacts,
- config validation,
- runtime displaced-copy validity,
- runtime copy quality,
- projection-only smoke,
- original-vs-displaced comparison,
- cycle phase closure,
- state mutation guard,
- optional one-step smoke,
- Step 43 regression guard,
- defaults unchanged,
- docs scope and forbidden claims,
- artifact budget,
- report acceptance complete,
- no persistent geometry outputs,
- no coupled geometry claims.

The contract test must avoid importing heavy package initializers if that would risk pre-push hook instability. Prefer source-text and artifact-backed assertions when possible.

## 9. Documentation And Report

Add:

- `docs/44_controlled_squid_proxy_diagnostic_geometry_update_smoke.md`
- `STEP44_CONTROLLED_SQUID_PROXY_DIAGNOSTIC_GEOMETRY_UPDATE_SMOKE_REPORT.md`

Required scope phrases:

- `Step 44 is controlled squid proxy diagnostic geometry update smoke.`
- `Step 44 uses a runtime diagnostic geometry copy only.`
- `Step 44 does not persist displaced geometry.`
- `Step 44 does not write displaced particles.`
- `Step 44 does not update driver geometry state.`
- `Step 44 does not update LBM solid_phi.`
- `Step 44 does not update dynamic_solid.`
- `Step 44 does not change moving bounce-back formulas.`
- `The default geometry_motion_mode remains static.`
- `The default geometry_motion_application_mode remains disabled.`

Forbidden claims:

- `full coupled geometry motion is implemented`
- `driver geometry is persistently updated`
- `MPM particles are persistently displaced`
- `LBM solid_phi is updated by runtime geometry`
- `dynamic_solid is updated by runtime geometry`
- `production boundary links are recomputed`
- `moving bounce-back formula is changed`
- `squid swimming is implemented`
- `free-body motion is implemented`
- `real jet validation`
- `real squid simulation is validated`
- `production-ready sharp-interface FSI`

Update `README.md` with a Step 44 implemented bullet and a Step 44 boundary section matching the documentation.

The report must include:

- goal,
- files created and updated,
- explicit non-goals,
- config validation,
- runtime displaced copy,
- runtime copy quality,
- projection-only smoke,
- original-vs-displaced comparison,
- cycle phase closure,
- state mutation guard,
- optional one-step driver smoke,
- Step 43 regression guard,
- artifact manifest summary,
- verification commands,
- GitHub sync information,
- acceptance checklist,
- decision for Step 45.

## 10. Verification Commands

Use the trusted interpreter:

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
git diff --check
git diff --cached --check
```

The final `git push origin main` must let the ECC pre-push hook run and pass.

## 11. Acceptance Checklist

- [ ] Step 44 detailed goal file exists.
- [ ] Diagnostic update config validation passes.
- [ ] Update mode is `runtime_copy_diagnostic`.
- [ ] Selected phases are `0.0`, `0.2`, `0.35`, `0.5`, and `1.0`.
- [ ] Grid sizes are `32` and `48`.
- [ ] Tracked regions include `mantle_outer`.
- [ ] Tracked regions include `mantle_cavity_proxy`.
- [ ] Tracked regions include `funnel_outlet_proxy`.
- [ ] Persistent displaced geometry is disabled.
- [ ] Displaced particle writes are disabled.
- [ ] Dense displacement field writes are disabled.
- [ ] VTK writes are disabled.
- [ ] Driver state application is disabled.
- [ ] LBM state application is disabled.
- [ ] MPM state application is disabled.
- [ ] Projection state application is disabled.
- [ ] Dynamic solid update is disabled.
- [ ] Production boundary-link recomputation is disabled.
- [ ] Original geometry mutation is disabled.
- [ ] Runtime displaced copy rows are generated.
- [ ] Runtime copy row count is 15.
- [ ] Displacement norms are finite.
- [ ] Displacement norms are bounded.
- [ ] Original geometry hash remains stable.
- [ ] No full displaced point array is committed.
- [ ] Runtime copy quality passes.
- [ ] Projection-only smoke runs 10 rows.
- [ ] Projection-only smoke passes at `32^3`.
- [ ] Projection-only smoke passes at `48^3`.
- [ ] Projected mass is positive.
- [ ] Active cell count is positive.
- [ ] No NaN is detected.
- [ ] No Inf is detected.
- [ ] Original-vs-displaced comparison passes.
- [ ] Mid-cycle displacement is nonzero.
- [ ] Phase `0.0` / phase `1.0` closure passes.
- [ ] State mutation guard passes.
- [ ] Driver state mutation count is 0.
- [ ] LBM state mutation count is 0.
- [ ] MPM state mutation count is 0.
- [ ] Projection state mutation count is 0.
- [ ] Dynamic solid mutation count is 0.
- [ ] Displaced particle output count is 0.
- [ ] Dense displacement output count is 0.
- [ ] VTR output count is 0.
- [ ] Optional one-step smoke passes or is explicitly marked diagnostic-copy-only with a no-claim reason.
- [ ] Step 43 regression guard passes.
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
- [ ] No squid swimming claim.
- [ ] No real squid validation claim.
- [ ] No Step 44 VTR outputs.
- [ ] No Step 44 particle `.npy` outputs.
- [ ] No `geo_all_fluid_*.dat` is added for Step 44.
- [ ] Artifact large-file count is 0.
- [ ] Step 44 output total-size budget passes.
- [ ] Repo artifact total-size budget passes.
- [ ] Step 44 contract test passes.
- [ ] Full pytest passes.
- [ ] `git diff --check` passes.
- [ ] Staged whitespace check passes.
- [ ] ECC pre-push hook passes.
- [ ] Step 44 artifacts are pushed to `origin/main`.

## 12. Decision For Step 45

If Step 44 passes, Step 45 may consider a controlled runtime geometry projection integration smoke. Step 45 should still remain conservative: phase-selected runtime displaced geometry, projection refresh on transient copy, boundary coverage diagnostics, and 1-step or 5-step 32^3 smoke only. A full prescribed-geometry update plus wall velocity plus moving bounce-back one-cycle run must remain a later step.
