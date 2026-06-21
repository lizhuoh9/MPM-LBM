# Step 46 Controlled Runtime Geometry + Wall Velocity One-Step Coupling Smoke Goal

## 1. Objective

Implement Step 46: Controlled Runtime Geometry + Wall Velocity One-Step Coupling Smoke.

Step 46 must combine the accepted Step 45 transient runtime-geometry projection path with the accepted opt-in `solid_vel` wall-velocity application path in a single ultra-short one-step diagnostic smoke. It is the first controlled smoke where runtime displaced geometry projection and wall velocity application appear in the same matrix, but it must remain opt-in, local/transient, one-step, and non-production.

Step 46 must not run full-cycle moving geometry, must not persist displaced geometry or projected state, must not alter formulas, and must not claim real jet validation, real squid validation, squid swimming, or production sharp-interface FSI readiness.

## 2. Accepted Inputs

Use the current repository state on `origin/main` after accepted Step 45:

- Step 45 goal: `STEP45_CONTROLLED_RUNTIME_GEOMETRY_PROJECTION_INTEGRATION_SMOKE_GOAL.md`
- Step 45 report: `STEP45_CONTROLLED_RUNTIME_GEOMETRY_PROJECTION_INTEGRATION_SMOKE_REPORT.md`
- Step 45 runtime projection config: `configs/step45_runtime_geometry_projection_integration.json`
- Step 45 runtime projection artifact: `outputs/step45_runtime_projection_integration/runtime_projection_integration.json`
- Step 45 runtime projection state guard: `outputs/step45_runtime_projection_state_guard/runtime_projection_state_guard.json`
- Step 45 artifact manifest: `outputs/step45_artifact_manifest/artifact_summary.json`
- Step 44 diagnostic geometry update config: `configs/step44_diagnostic_geometry_update.json`
- Step 41 selected wall velocity application config: `configs/step41_wall_velocity_application_scale_0050_64.json`
- Step 34 boundary-motion interface config: `configs/step34_boundary_motion_interface_prescribed_kinematic.json`
- Step 30 squid proxy geometry config: `configs/step30_squid_proxy_geometry.json`
- Step 30 squid proxy region config: `configs/step30_squid_proxy_region_config.json`

Step 46 must preserve the accepted Step 45 result:

- Step 45 uses transient projection state only.
- Step 45 does not persist projected state.
- Step 45 does not persist displaced geometry.
- Step 45 does not update default driver geometry.
- Step 45 does not update default LBM/MPM/projection state.
- Step 45 does not change moving bounce-back formulas.

Step 46 must also preserve the accepted Step 36/41 wall-velocity result:

- Wall velocity is applied only through opt-in `solid_vel` diagnostics.
- LBM populations are not directly modified.
- MPM state is not directly modified.
- Projection formulas are not modified.
- Moving bounce-back formulas are not modified.
- Default `wall_velocity_application_mode` remains disabled.

## 3. Required Scope

Step 46 is controlled runtime geometry plus wall velocity one-step coupling smoke.

Step 46 is opt-in and ultra-short.

Step 46 combines transient runtime geometry projection with `solid_vel` wall velocity application.

Step 46 may:

- Load Step 45 runtime projection rows for `phase = 0.35` and `n_grid = 32`.
- Load Step 41 wall velocity application config with `wall_velocity_scale = 0.05` and `wall_velocity_cap_lbm = 0.01`.
- Build an isolated one-step diagnostic matrix with four rows:
  - `original_static_32_1step`
  - `runtime_geometry_only_32_phase035_1step`
  - `wall_velocity_only_32_phase035_1step`
  - `runtime_geometry_plus_wall_velocity_32_phase035_1step`
- Use runtime geometry projection flags as a transient/local diagnostic input.
- Use wall-velocity application flags as a transient/local diagnostic input.
- Keep coupling mode as `moving_boundary`.
- Keep reaction transfer mode as `engineering`.
- Compute compact mass, projection, wall-velocity, bounce-back, force, and stability summary fields.
- Compare geometry-only, wall-velocity-only, and combined effects against original static.
- Prove all rows are finite, bounded, and stable at one step.
- Prove no default or persistent state mutation.
- Write compact CSV/JSON/NPZ/log artifacts.
- Add artifact-backed contract tests.

Step 46 must not:

- Run a full-cycle moving-geometry simulation.
- Run multi-step dynamic geometry update.
- Promote runtime geometry into a production driver path.
- Persist displaced geometry.
- Persist projected state.
- Persist LBM `solid_phi` updates.
- Persist LBM `solid_vel` updates.
- Persist MPM state updates.
- Persist projection state updates.
- Persist `dynamic_solid` updates.
- Recompute production boundary links from displaced geometry.
- Write displaced particles.
- Write dense displacement fields.
- Write VTR outputs.
- Write Step 46 particle `.npy` outputs.
- Add Step 46 `geo_all_fluid_*.dat` artifacts.
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

## 4. Required Validation Matrix

Step 46 must run exactly four 32^3 one-step diagnostic rows at `phase = 0.35`:

| row name | runtime geometry projection | wall velocity application | purpose |
| --- | ---: | ---: | --- |
| `original_static_32_1step` | no | no | baseline |
| `runtime_geometry_only_32_phase035_1step` | yes | no | geometry projection effect |
| `wall_velocity_only_32_phase035_1step` | no | yes | wall-velocity effect |
| `runtime_geometry_plus_wall_velocity_32_phase035_1step` | yes | yes | first combined smoke |

Required common parameters:

- `phase = 0.35`
- `n_grid = 32`
- `n_particles = 4096`
- `n_lbm_steps = 1`
- `mpm_substeps_per_lbm_step = 1`
- `output_interval = 1`
- `coupling_mode = "moving_boundary"`
- `reaction_transfer_mode = "engineering"`
- `quality_check_enabled = true`
- `quality_check_strict = true`
- `write_vtk = false`
- `write_particles = false`
- `target_u_lbm = [0.0, 0.0, 0.0]`

Do not add a Step 46 `link_area` row to the primary matrix.

## 5. Required Configuration Files

Add `configs/step46_runtime_geometry_wall_velocity_coupling_smoke.json`.

Required semantics:

- `coupling_smoke_id = "step46_runtime_geometry_wall_velocity_one_step"`
- `runtime_projection_config_path = "configs/step45_runtime_geometry_projection_integration.json"`
- `diagnostic_geometry_update_config_path = "configs/step44_diagnostic_geometry_update.json"`
- `wall_velocity_application_config_path = "configs/step41_wall_velocity_application_scale_0050_64.json"`
- `boundary_motion_config_path = "configs/step34_boundary_motion_interface_prescribed_kinematic.json"`
- `geometry_config_path = "configs/step30_squid_proxy_geometry.json"`
- `region_config_path = "configs/step30_squid_proxy_region_config.json"`
- `phase = 0.35`
- `n_grid = 32`
- `n_lbm_steps = 1`
- `mpm_substeps_per_lbm_step = 1`
- `coupling_mode = "moving_boundary"`
- `reaction_transfer_mode = "engineering"`
- `enable_runtime_geometry_projection = true`
- `enable_wall_velocity_application = true`
- `persist_displaced_geometry = false`
- `persist_projected_state = false`
- `persist_lbm_solid_vel = false`
- `write_displaced_particles = false`
- `write_dense_displacement_field = false`
- `write_vtk = false`
- `write_particles = false`
- `update_default_driver_geometry = false`
- `update_default_lbm_state = false`
- `update_default_mpm_state = false`
- `update_default_projection_state = false`
- `update_dynamic_solid_persistently = false`
- `recompute_production_boundary_links = false`
- `modify_moving_bounceback_formula = false`
- `diagnostic_only = true`
- `scope_note = "one-step opt-in runtime geometry plus wall velocity coupling smoke only"`

Add four row descriptors:

- `configs/step46_original_static_32_1step.json`
- `configs/step46_runtime_geometry_only_32_phase035_1step.json`
- `configs/step46_wall_velocity_only_32_phase035_1step.json`
- `configs/step46_runtime_geometry_plus_wall_velocity_32_phase035_1step.json`

These descriptors may be consumed by Step 46 runners rather than by production `FSIDriver3D`. They must disable VTK and particle output and must not enable persistent state mutation.

## 6. Required Source Modules

Add `src/runtime_geometry_wall_velocity_coupling_config.py`.

This module must define an immutable Step 46 config and validation helpers. Validation must require:

- phase equals `0.35`,
- `n_grid == 32`,
- `n_lbm_steps == 1`,
- `mpm_substeps_per_lbm_step == 1`,
- `coupling_mode == "moving_boundary"`,
- `reaction_transfer_mode == "engineering"`,
- runtime geometry projection and wall velocity application are enabled in the umbrella config,
- all persistence/write/update/formula flags remain false,
- `diagnostic_only == true`,
- all referenced Step 45, Step 44, Step 41, Step 34, and Step 30 config/artifact paths exist.

Add `src/runtime_geometry_wall_velocity_coupling.py`.

This module must orchestrate the four-row smoke matrix. It may read Step 45 projection rows and Step 41 wall-velocity summaries, but it must keep all state local/transient. It must write one row per matrix entry with at least:

- row name,
- phase,
- grid size,
- runtime geometry projection enabled,
- wall velocity application enabled,
- projected mass,
- active cell count,
- solid-phi min/max,
- applied cell count,
- max applied velocity norm,
- wall velocity cap,
- rho min/max,
- LBM max velocity,
- bounce-back link count,
- bounce-back max correction,
- hydro force max norm,
- completed LBM steps,
- total MPM substeps,
- NaN/Inf flags,
- diagnostic-only flag,
- persistent state flags,
- stable flag.

Add `src/runtime_geometry_wall_velocity_diagnostics.py`.

This module must summarize coupling-smoke quality, component-effect comparison, and mass/force/bounce-back diagnostics.

Add `src/runtime_geometry_wall_velocity_state_guard.py`.

This module must prove original geometry hashes remain stable, mutation counters remain zero, and forbidden Step 46 outputs are absent.

## 7. Required Baseline Runners

Add:

- `baseline_tests/step46_common.py`
- `baseline_tests/run_step46_coupling_smoke_config_validation.py`
- `baseline_tests/run_step46_one_step_coupling_smoke_matrix.py`
- `baseline_tests/run_step46_coupling_smoke_quality.py`
- `baseline_tests/run_step46_component_effect_comparison.py`
- `baseline_tests/run_step46_mass_force_bounceback_diagnostics.py`
- `baseline_tests/run_step46_state_mutation_guard.py`
- `baseline_tests/run_step46_step45_regression_guard.py`
- `baseline_tests/run_step46_artifact_manifest.py`

Each runner must write a log marker under `logs/step46_*.log` and compact CSV/JSON artifacts under `outputs/step46_*`.

## 8. Runner Acceptance Criteria

`run_step46_coupling_smoke_config_validation.py` must prove:

- validation passes,
- phase is `0.35`,
- `n_grid == 32`,
- `n_lbm_steps == 1`,
- `mpm_substeps_per_lbm_step == 1`,
- all persistence/write/update/formula flags are false,
- diagnostic-only is true.

`run_step46_one_step_coupling_smoke_matrix.py` must generate:

- `row_count == 4`,
- `stable_count == 4`,
- original static row count is `1`,
- geometry-only row count is `1`,
- wall-velocity-only row count is `1`,
- combined row count is `1`,
- every row completes at least one LBM step,
- every row completes at least one MPM substep,
- global `rho_min > 0.95`,
- global `rho_max < 1.05`,
- `lbm_max_v < 0.1`,
- `projected_mass > 0`,
- `active_cell_count > 0`,
- `bb_link_count > 0`,
- no NaN,
- no Inf.

Row-specific requirements:

- original static: no runtime geometry projection and no wall velocity application,
- geometry-only: runtime geometry projection enabled, wall velocity application disabled, projection differs from original static,
- wall-velocity-only: runtime geometry projection disabled, wall velocity application enabled, applied cell count > 0,
- combined: runtime geometry projection enabled, wall velocity application enabled, applied cell count > 0.

`run_step46_coupling_smoke_quality.py` must prove:

- `quality_pass == true`,
- `row_count_pass == true`,
- `stability_pass == true`,
- `projection_pass == true`,
- `wall_velocity_pass == true`,
- `combined_row_pass == true`,
- `diagnostic_only_pass == true`,
- `no_persistent_state_pass == true`.

`run_step46_component_effect_comparison.py` must compare:

- geometry-only minus original static,
- wall-velocity-only minus original static,
- combined minus original static,
- combined minus geometry-only,
- combined minus wall-velocity-only.

Acceptance:

- comparison count is at least `5`,
- comparison pass is true,
- geometry-only projection delta is nonzero,
- wall-velocity-only applied velocity is nonzero,
- combined has both runtime geometry and wall velocity,
- all mass, velocity, force, and bounce-back metrics are finite,
- projected-mass delta and active-cell delta are bounded.

`run_step46_mass_force_bounceback_diagnostics.py` must prove:

- `row_count == 4`,
- diagnostics pass is true,
- global `rho_min > 0.95`,
- global `rho_max < 1.05`,
- `bb_max_correction` is finite,
- `bb_link_count > 0`,
- `hydro_force_max_norm` is finite,
- `max_applied_velocity_norm <= wall_velocity_cap_lbm` for rows with wall velocity,
- no NaN,
- no Inf.

`run_step46_state_mutation_guard.py` must prove:

- guard pass is true,
- original geometry hash before equals after,
- default driver state mutation count is `0`,
- default LBM state mutation count is `0`,
- default MPM state mutation count is `0`,
- default projection state mutation count is `0`,
- persistent projected state count is `0`,
- persistent displaced geometry count is `0`,
- displaced particle output count is `0`,
- dense displacement output count is `0`,
- VTR output count is `0`,
- Step 46 `geo_all_fluid_*.dat` count is `0`.

`run_step46_step45_regression_guard.py` must prove:

- Step 45 report exists,
- Step 45 runtime projection row count is `10`,
- Step 45 projection pass count is `10`,
- Step 45 state guard passes,
- Step 45 artifact large-file count is `0`,
- Step 45 VTR count is `0`,
- Step 45 particle NPY count is `0`,
- Step 45 `geo_all_fluid_*.dat` count is `0`.

`run_step46_artifact_manifest.py` must prove:

- `large_file_count == 0`,
- `step46_total_size_mb < 10`,
- repo `total_size_mb < 350`,
- `step46_vtr_count == 0`,
- `step46_particle_npy_count == 0`,
- raw candidate large-file count is `0`,
- scan-data count is `0`,
- private absolute path count is `0`,
- Step 46 `geo_all_fluid_*.dat` count is `0`.

## 9. Contract Test

Add `tests/test_step46_runtime_geometry_wall_velocity_coupling_smoke_contract.py` with tests for:

- required artifacts,
- coupling-smoke config validity,
- one-step coupling smoke matrix validity,
- coupling-smoke quality,
- component-effect comparison,
- mass/force/bounce-back diagnostics,
- state mutation guard,
- Step 45 regression guard,
- default modes unchanged,
- docs scope and forbidden claims,
- artifact budget,
- report acceptance complete,
- no persistent geometry outputs,
- no full-cycle claims,
- no formula changes.

The contract test must avoid importing heavy package initializers if that risks pre-push hook instability. Prefer source-text and artifact-backed assertions where possible.

## 10. Documentation And Report

Add:

- `docs/46_controlled_runtime_geometry_wall_velocity_one_step_coupling_smoke.md`
- `STEP46_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_STEP_COUPLING_SMOKE_REPORT.md`

Required scope phrases:

- `Step 46 is controlled runtime geometry plus wall velocity one-step coupling smoke.`
- `Step 46 is opt-in and ultra-short.`
- `Step 46 combines transient runtime geometry projection with solid_vel wall velocity application.`
- `Step 46 does not persist displaced geometry.`
- `Step 46 does not persist projected state.`
- `Step 46 does not run a full-cycle moving-geometry simulation.`
- `Step 46 does not change moving bounce-back formulas.`
- `The default geometry_motion_mode remains static.`
- `The default geometry_motion_application_mode remains disabled.`
- `The default boundary_motion_mode remains static.`
- `The default wall_velocity_application_mode remains disabled.`

Forbidden claims:

- `full-cycle moving geometry is implemented`
- `production moving geometry is implemented`
- `driver geometry is persistently updated`
- `LBM solid_phi is persistently updated`
- `dynamic_solid is persistently updated`
- `production boundary links are recomputed`
- `moving bounce-back formula is changed`
- `squid swimming is implemented`
- `free-body motion is implemented`
- `real jet validation`
- `real squid simulation is validated`
- `production-ready sharp-interface FSI`

Update `README.md` with a Step 46 implemented bullet and Step 46 boundary section.

The report must include:

- goal,
- files created and updated,
- explicit non-goals,
- coupling smoke config validation,
- one-step coupling smoke matrix,
- coupling smoke quality,
- component effect comparison,
- mass force bounce-back diagnostics,
- state mutation guard,
- Step 45 regression guard,
- artifact manifest summary,
- verification commands,
- GitHub sync information,
- acceptance checklist,
- decision for Step 47.

## 11. Verification Commands

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\runtime_geometry_wall_velocity_coupling_config.py src\runtime_geometry_wall_velocity_coupling.py src\runtime_geometry_wall_velocity_diagnostics.py src\runtime_geometry_wall_velocity_state_guard.py baseline_tests\step46_common.py baseline_tests\run_step46_coupling_smoke_config_validation.py baseline_tests\run_step46_one_step_coupling_smoke_matrix.py baseline_tests\run_step46_coupling_smoke_quality.py baseline_tests\run_step46_component_effect_comparison.py baseline_tests\run_step46_mass_force_bounceback_diagnostics.py baseline_tests\run_step46_state_mutation_guard.py baseline_tests\run_step46_step45_regression_guard.py baseline_tests\run_step46_artifact_manifest.py tests\test_step46_runtime_geometry_wall_velocity_coupling_smoke_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step46_coupling_smoke_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step46_one_step_coupling_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step46_coupling_smoke_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step46_component_effect_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step46_mass_force_bounceback_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step46_state_mutation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step46_step45_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step46_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step46_runtime_geometry_wall_velocity_coupling_smoke_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
git diff --check
git diff --cached --check
```

The final `git push origin main` must let the ECC pre-push hook run and pass.

## 12. Acceptance Checklist

- [ ] Step 46 detailed goal file exists.
- [ ] Coupling smoke config validation passes.
- [ ] Phase is `0.35`.
- [ ] `n_grid` is `32`.
- [ ] `n_lbm_steps` is `1`.
- [ ] `mpm_substeps_per_lbm_step` is `1`.
- [ ] Persistent displaced geometry is disabled.
- [ ] Persistent projected state is disabled.
- [ ] Persistent LBM `solid_vel` is disabled.
- [ ] Displaced particle writes are disabled.
- [ ] Dense displacement field writes are disabled.
- [ ] VTK writes are disabled.
- [ ] Particle writes are disabled.
- [ ] Default driver geometry update is disabled.
- [ ] Default LBM state update is disabled.
- [ ] Default MPM state update is disabled.
- [ ] Default projection state update is disabled.
- [ ] Persistent dynamic-sold update is disabled.
- [ ] Production boundary-link recomputation is disabled.
- [ ] Moving bounce-back formula modification is disabled.
- [ ] One-step coupling smoke matrix runs 4 rows.
- [ ] Original static row passes.
- [ ] Runtime geometry-only row passes.
- [ ] Wall-velocity-only row passes.
- [ ] Runtime geometry plus wall-velocity row passes.
- [ ] All rows complete at least 1 LBM step.
- [ ] All rows complete at least 1 MPM substep.
- [ ] `rho_min > 0.95`.
- [ ] `rho_max < 1.05`.
- [ ] `lbm_max_v < 0.1`.
- [ ] `projected_mass > 0`.
- [ ] `active_cell_count > 0`.
- [ ] `bb_link_count > 0`.
- [ ] No NaN is detected.
- [ ] No Inf is detected.
- [ ] Geometry-only row shows nonzero projection delta.
- [ ] Wall-velocity-only row shows positive applied velocity.
- [ ] Combined row has runtime geometry projection and positive wall velocity.
- [ ] Coupling smoke quality passes.
- [ ] Component effect comparison passes.
- [ ] Mass/force/bounce-back diagnostics pass.
- [ ] State mutation guard passes.
- [ ] Original geometry hash remains stable.
- [ ] Default driver state mutation count is `0`.
- [ ] Default LBM state mutation count is `0`.
- [ ] Default MPM state mutation count is `0`.
- [ ] Default projection state mutation count is `0`.
- [ ] Persistent projected state count is `0`.
- [ ] Persistent displaced geometry count is `0`.
- [ ] Displaced particle output count is `0`.
- [ ] Dense displacement output count is `0`.
- [ ] VTR output count is `0`.
- [ ] Step 46 `geo_all_fluid_*.dat` count is `0`.
- [ ] Step 45 regression guard passes.
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
- [ ] No Step 46 VTR outputs.
- [ ] No Step 46 particle `.npy` outputs.
- [ ] Artifact large-file count is `0`.
- [ ] Step 46 output total-size budget passes.
- [ ] Repo artifact total-size budget passes.
- [ ] `logs/step46_pytest.log` exists.
- [ ] Step 46 contract test passes.
- [ ] Full pytest passes.
- [ ] `git diff --check` passes.
- [ ] Staged whitespace check passes.
- [ ] ECC pre-push hook passes.
- [ ] Step 46 artifacts are pushed to `origin/main`.

## 13. Decision For Step 47

If Step 46 passes, Step 47 may consider `Controlled Runtime Geometry + Wall Velocity Short-Step Coupling Envelope`. Step 47 should start with `32^3`, a very short step window, engineering moving-boundary only, and selected phase samples from the accepted schedule. Full-cycle moving geometry must remain a later step.
