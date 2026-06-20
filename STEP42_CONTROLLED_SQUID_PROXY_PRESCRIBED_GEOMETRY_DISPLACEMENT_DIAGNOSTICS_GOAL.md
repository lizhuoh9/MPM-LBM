# Step 42 Controlled Squid Proxy Prescribed Geometry Displacement Diagnostics Goal

## Objective

Implement Step 42 as controlled squid proxy prescribed geometry displacement diagnostics. Step 42 derives diagnostic-only displacement evidence for `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy` from the accepted Step 32 kinematics schedule and Step 33 motion mapping. It must not update driver geometry, MPM particles, LBM solid fields, dynamic solid state, projection state, coupling state, or moving bounce-back formulas.

The deliverable must include explicit configs, source modules, baseline runners, committed output artifacts, contract tests, documentation, a final report, verification logs, a clean artifact manifest, and a pushed GitHub commit on `origin/main`.

## Scope Statement

Step 42 is controlled squid proxy prescribed geometry displacement diagnostics.

Step 42 derives displacement diagnostics only.

Step 42 does not update driver geometry.

Step 42 does not displace MPM particles in FSIDriver3D.

Step 42 does not update LBM solid_phi.

Step 42 does not update dynamic_solid.

Step 42 does not change moving bounce-back formulas.

Step 42 remains diagnostic-only.

The default `boundary_motion_mode` remains `static`.

The default `wall_velocity_application_mode` remains `disabled`.

## Why Step 42 Exists

Steps 32 through 41 have established:

- prescribed schedule artifacts
- motion mapping artifacts
- wall velocity field diagnostics
- opt-in `solid_vel` wall-velocity application
- tethered one-cycle and multi-cycle jet-cycle proxy diagnostics
- Step 40 parameter sensitivity
- Step 41 selected-parameter `64^3` feasibility

The missing bridge is diagnostic evidence for how the squid proxy geometry itself would move under the accepted kinematics. Step 42 adds that evidence without connecting it to `FSIDriver3D`.

## Non-Goals And Hard Boundaries

Do not implement, enable, or claim any of the following:

- driver geometry update
- MPM particle position update
- solid particle displacement in `FSIDriver3D`
- projection update from displaced geometry
- LBM `solid_phi` update from displaced geometry
- dynamic solid update from displaced geometry
- moving bounce-back formula change
- LBM collision formula change
- LBM streaming formula change
- MPM constitutive formula change
- projection formula change
- coupler formula change
- free-body motion
- body trajectory
- squid swimming
- real jet validation
- real squid validation
- production sharp-interface FSI
- `external/taichi_LBM3D` edits
- raw real geometry or scan data
- dense displacement field output
- displaced particle output

Allowed work is limited to:

- explicit Step 42 geometry-displacement configs
- CPU/NumPy diagnostic displacement calculations
- region-wise displacement summaries
- bounding-box, volume proxy, aperture proxy, and overlap-style diagnostics
- grid coverage diagnostics at `32^3`, `48^3`, and `64^3`
- cycle closure diagnostics
- schedule-displacement consistency checks
- motion-displacement consistency checks
- repeatability hashes
- Step 41 regression guard
- small CSV/JSON/NPZ/log artifacts

## Tracked Regions

Primary tracked regions:

- `mantle_outer`
- `mantle_cavity_proxy`
- `funnel_outlet_proxy`

Context regions:

- `head_proxy`
- `arms_proxy`
- `left_fin_proxy`
- `right_fin_proxy`

Context regions must remain diagnostic-only and are not required acceptance subjects.

## Sampling

Use the accepted Step 32 phase sampling:

- `sample_count = 32768`
- `phase_sample_count = 81`
- phases from `0.0` to `1.0`
- `cycle_period_steps = 40`

Grid diagnostics:

- `32^3`
- `48^3`
- `64^3`

## Required Configs

Add:

- `configs/step42_squid_proxy_geometry_displacement.json`
- `configs/step42_squid_proxy_displacement_sampling.json`

`configs/step42_squid_proxy_geometry_displacement.json` must include:

- `displacement_id = step42_squid_proxy_geometry_displacement_diagnostics`
- `schedule_config_path = configs/step32_squid_proxy_kinematics_schedule.json`
- `motion_mapping_config_path = configs/step33_squid_proxy_motion_mapping.json`
- `region_config_path = configs/step30_squid_proxy_region_config.json`
- `geometry_config_path = configs/step30_squid_proxy_geometry.json`
- tracked regions `mantle_outer`, `mantle_cavity_proxy`, `funnel_outlet_proxy`
- context regions `head_proxy`, `arms_proxy`, `left_fin_proxy`, `right_fin_proxy`
- `sample_count = 32768`
- `phase_sample_count = 81`
- `grid_sizes = [32, 48, 64]`
- `mantle_displacement_model = radial_scale_proxy`
- `cavity_displacement_model = volume_scale_proxy`
- `funnel_displacement_model = aperture_scale_proxy`
- `max_displacement_norm_allowed = 0.25`
- `write_dense_displacement_field = false`
- `write_displaced_particles = false`
- `apply_to_driver = false`
- `apply_to_lbm = false`
- `apply_to_mpm = false`
- `apply_to_projection = false`
- `update_dynamic_solid = false`
- `driver_integration_enabled = false`
- `deterministic = true`
- `scope_note = geometry displacement diagnostics only; no driver-coupled geometry update`

## Required Source Modules

Add:

- `src/geometry_displacement_config.py`
- `src/geometry_displacement_field.py`
- `src/geometry_displacement_quality.py`
- `src/geometry_displacement_consistency.py`
- `src/geometry_displacement_grid_diagnostics.py`

### `src/geometry_displacement_config.py`

Define a frozen dataclass for the Step 42 displacement config and validation helpers.

Validation must check:

- all referenced configs exist
- tracked regions include `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy`
- `sample_count > 0`
- `phase_sample_count >= 41`
- grid sizes are positive
- `max_displacement_norm_allowed > 0`
- `write_dense_displacement_field == false`
- `write_displaced_particles == false`
- `apply_to_driver == false`
- `apply_to_lbm == false`
- `apply_to_mpm == false`
- `apply_to_projection == false`
- `update_dynamic_solid == false`
- `driver_integration_enabled == false`

### `src/geometry_displacement_field.py`

Generate diagnostic displacement rows only.

Required responsibilities:

- load geometry displacement inputs
- sample deterministic squid proxy points
- compute region masks from Step 30 region semantics
- compute mantle radial displacement proxy
- compute cavity volume-scale displacement proxy
- compute funnel aperture displacement proxy
- generate `81 * 3 = 243` rows
- summarize displacement rows
- write CSV/JSON outputs
- write optional compact NPZ summary arrays, not dense fields

Required row fields include:

- `sample_index`
- `phase`
- `region_id`
- `displacement_model`
- `point_count`
- `displacement_norm_min`
- `displacement_norm_max`
- `displacement_norm_mean`
- `velocity_norm_proxy_max`
- bounding box min/max fields
- `volume_scale`
- `aperture_scale`
- `finite_pass`
- `bounds_pass`
- `diagnostic_only`
- `apply_to_driver`
- `apply_to_lbm`
- `apply_to_mpm`
- `apply_to_projection`

### `src/geometry_displacement_quality.py`

Analyze generated displacement rows.

Required summary keys:

- `quality_pass`
- `finite_pass`
- `bounds_pass`
- `coverage_pass`
- `cycle_closure_pass`
- `endpoint_repeatability_pass`
- `diagnostic_only_pass`
- `no_driver_update_pass`
- `no_lbm_update_pass`
- `no_mpm_update_pass`
- `no_projection_update_pass`
- `no_dense_field_pass`
- `no_displaced_particles_pass`

### `src/geometry_displacement_consistency.py`

Compare displacement rows to Step 32 schedule and Step 33 motion mapping.

Required checks:

- phase samples match
- mantle radius scale matches mantle displacement envelope
- cavity volume scale matches cavity displacement proxy
- funnel aperture scale matches funnel displacement proxy
- velocity and displacement signs are consistent
- phase `0` and phase `1` displacement envelopes match

### `src/geometry_displacement_grid_diagnostics.py`

Summarize diagnostic grid coverage for displaced proxy rows at `32^3`, `48^3`, and `64^3`.

Required row fields:

- `grid_size`
- `region_id`
- `phase_count`
- `active_cell_count_min`
- `active_cell_count_max`
- bounding box cell fields
- `max_displacement_norm`
- `coverage_pass`

## Required Baseline Runners

Add:

- `baseline_tests/step42_common.py`
- `baseline_tests/run_step42_displacement_config_validation.py`
- `baseline_tests/run_step42_generate_geometry_displacement.py`
- `baseline_tests/run_step42_displacement_quality.py`
- `baseline_tests/run_step42_displacement_repeatability.py`
- `baseline_tests/run_step42_schedule_displacement_consistency.py`
- `baseline_tests/run_step42_motion_displacement_consistency.py`
- `baseline_tests/run_step42_grid_displacement_diagnostics.py`
- `baseline_tests/run_step42_cycle_closure_diagnostics.py`
- `baseline_tests/run_step42_no_driver_update_guard.py`
- `baseline_tests/run_step42_step41_regression_guard.py`
- `baseline_tests/run_step42_artifact_manifest.py`

## Runner Outputs And Acceptance

### Displacement Config Validation

Outputs:

- `outputs/step42_displacement_config_validation/displacement_config_validation.csv`
- `outputs/step42_displacement_config_validation/displacement_config_validation.json`
- `logs/step42_displacement_config_validation.log`

Acceptance:

- `validation_pass == true`
- `tracked_region_count == 3`
- tracked regions include all three primary regions
- `grid_sizes == [32, 48, 64]`
- `phase_sample_count == 81`
- dense field and displaced particle writes are disabled
- all driver/LBM/MPM/projection/dynamic-solid integration flags are disabled

### Generate Geometry Displacement

Outputs:

- `outputs/step42_geometry_displacement/geometry_displacement.csv`
- `outputs/step42_geometry_displacement/geometry_displacement.json`
- `outputs/step42_geometry_displacement/geometry_displacement_summary.npz`
- `logs/step42_generate_geometry_displacement.log`

Acceptance:

- `row_count == 243`
- `phase_sample_count == 81`
- `tracked_region_count == 3`
- `finite_pass == true`
- `bounds_pass == true`
- `max_displacement_norm <= max_displacement_norm_allowed`
- every row is diagnostic-only
- every apply-to-driver/LBM/MPM/projection flag is false

### Displacement Quality

Outputs:

- `outputs/step42_displacement_quality/displacement_quality.csv`
- `outputs/step42_displacement_quality/displacement_quality.json`
- `logs/step42_displacement_quality.log`

Acceptance:

- `quality_pass == true`
- `finite_pass == true`
- `bounds_pass == true`
- `coverage_pass == true`
- `cycle_closure_pass == true`
- `endpoint_repeatability_pass == true`
- `diagnostic_only_pass == true`
- all no-update and no-heavy-output checks pass

### Displacement Repeatability

Outputs:

- `outputs/step42_displacement_repeatability/displacement_repeatability.csv`
- `outputs/step42_displacement_repeatability/displacement_repeatability.json`
- `logs/step42_displacement_repeatability.log`

Acceptance:

- `row_count_first == 243`
- `row_count_second == 243`
- full displacement hash repeats
- mantle displacement hash repeats
- cavity displacement hash repeats
- funnel displacement hash repeats
- `repeatability_pass == true`

### Schedule-Displacement Consistency

Outputs:

- `outputs/step42_schedule_displacement_consistency/schedule_displacement_consistency.csv`
- `outputs/step42_schedule_displacement_consistency/schedule_displacement_consistency.json`
- `logs/step42_schedule_displacement_consistency.log`

Acceptance:

- `schedule_row_count == 81`
- `displacement_sample_count == 81`
- `phase_samples_match == true`
- `mantle_scale_consistency_pass == true`
- `cavity_volume_scale_consistency_pass == true`
- `funnel_aperture_scale_consistency_pass == true`
- `consistency_pass == true`

### Motion-Displacement Consistency

Outputs:

- `outputs/step42_motion_displacement_consistency/motion_displacement_consistency.csv`
- `outputs/step42_motion_displacement_consistency/motion_displacement_consistency.json`
- `logs/step42_motion_displacement_consistency.log`

Acceptance:

- `motion_mapping_row_count == 243`
- `displacement_row_count == 243`
- `phase_match_pass == true`
- `region_match_pass == true`
- `velocity_displacement_sign_pass == true`
- `mantle_motion_displacement_pass == true`
- `cavity_motion_displacement_pass == true`
- `funnel_motion_displacement_pass == true`
- `consistency_pass == true`

### Grid Displacement Diagnostics

Outputs:

- `outputs/step42_grid_displacement_diagnostics/grid_displacement_diagnostics.csv`
- `outputs/step42_grid_displacement_diagnostics/grid_displacement_diagnostics.json`
- `logs/step42_grid_displacement_diagnostics.log`

Acceptance:

- `row_count == 9`
- `grid_size_count == 3`
- `tracked_region_count == 3`
- `active_cell_count_min > 0`
- `active_cell_count_max >= active_cell_count_min`
- max displacement norm is finite
- `coverage_pass == true` for all rows

### Cycle Closure Diagnostics

Outputs:

- `outputs/step42_cycle_closure_diagnostics/cycle_closure_diagnostics.csv`
- `outputs/step42_cycle_closure_diagnostics/cycle_closure_diagnostics.json`
- `logs/step42_cycle_closure_diagnostics.log`

Acceptance:

- `row_count == 3`
- all three tracked regions close
- `phase0_phase1_displacement_delta <= 1e-8` or an explicitly conservative tolerance
- `cycle_closure_pass == true`

### No Driver Update Guard

Outputs:

- `outputs/step42_no_driver_update_guard/no_driver_update_guard.csv`
- `outputs/step42_no_driver_update_guard/no_driver_update_guard.json`
- `logs/step42_no_driver_update_guard.log`

Acceptance:

- `guard_pass == true`
- `driver_update_count == 0`
- `lbm_update_count == 0`
- `mpm_update_count == 0`
- `projection_update_count == 0`
- `dynamic_solid_update_count == 0`
- `displaced_particle_output_count == 0`
- `dense_displacement_field_output_count == 0`
- `fsidriver_integration_count == 0`

### Step 41 Regression Guard

Inputs:

- `STEP41_CONTROLLED_JET_CYCLE_PROXY_SELECTED_PARAMETER_64_FEASIBILITY_REPORT.md`
- `outputs/step41_64_selected_parameter_driver/selected_parameter_64_results.json`
- `outputs/step41_64_feasibility_summary/feasibility_summary.json`
- `outputs/step41_wall_velocity_64_quality/wall_velocity_64_quality.json`
- `outputs/step41_tethered_no_free_body_guard/tethered_no_free_body_guard.json`
- `outputs/step41_artifact_manifest/artifact_summary.json`

Acceptance:

- Step 41 report exists
- Step 41 driver `row_count == 4`
- Step 41 driver `stable_count == 4`
- Step 41 selected scale is `0.05`
- Step 41 `n_grid == 64`
- Step 41 wall-velocity quality passes
- Step 41 tethered guard passes
- Step 41 large-file count is 0
- Step 41 VTR count is 0
- Step 41 particle NPY count is 0

### Artifact Manifest

Outputs:

- `outputs/step42_artifact_manifest/artifact_manifest.csv`
- `outputs/step42_artifact_manifest/artifact_summary.csv`
- `outputs/step42_artifact_manifest/artifact_summary.json`
- `logs/step42_artifact_manifest.log`

Acceptance:

- `large_file_count == 0`
- `step42_total_size_mb < 5`
- `total_size_mb < 310`
- `step42_vtr_count == 0`
- `step42_particle_npy_count == 0`
- `raw_candidate_large_file_count == 0`
- `scan_data_file_count == 0`
- `private_absolute_path_count == 0`

## Contract Test

Add:

- `tests/test_step42_geometry_displacement_diagnostics_contract.py`

Required tests:

- required artifacts exist
- displacement config is valid
- geometry displacement output is valid
- displacement quality is valid
- displacement repeatability is valid
- schedule-displacement consistency is valid
- motion-displacement consistency is valid
- grid displacement diagnostics are valid
- cycle closure diagnostics are valid
- no driver update guard is valid
- Step 41 regression guard is valid
- default modes remain unchanged
- docs scope and forbidden claims are valid
- artifact budget is valid
- report acceptance is complete
- no driver-coupling claims exist

Forbidden exact claims in docs/report:

- `geometry displacement is integrated into FSIDriver3D`
- `driver geometry is updated`
- `MPM particles are displaced by Step 42`
- `LBM solid_phi is updated by displaced geometry`
- `dynamic_solid is updated by displaced geometry`
- `moving bounce-back formula is changed`
- `real jet validation`
- `jet propulsion is validated`
- `squid swimming is implemented`
- `free-body motion is implemented`
- `real squid simulation is validated`
- `production-ready sharp-interface FSI`
- `default wall velocity application is enabled`

Required scope phrases in docs/report:

- `Step 42 is controlled squid proxy prescribed geometry displacement diagnostics.`
- `Step 42 derives displacement diagnostics only.`
- `Step 42 does not update driver geometry.`
- `Step 42 does not displace MPM particles in FSIDriver3D.`
- `Step 42 does not update LBM solid_phi.`
- `Step 42 does not update dynamic_solid.`
- `Step 42 does not change moving bounce-back formulas.`
- `Step 42 remains diagnostic-only.`
- `The default boundary_motion_mode remains static.`
- `The default wall_velocity_application_mode remains disabled.`

## Documentation And Report

Add:

- `docs/42_controlled_squid_proxy_prescribed_geometry_displacement_diagnostics.md`
- `STEP42_CONTROLLED_SQUID_PROXY_PRESCRIBED_GEOMETRY_DISPLACEMENT_DIAGNOSTICS_REPORT.md`

The report must include:

1. Goal
2. Files Created And Updated
3. Explicit Non-Goals
4. Displacement Config Validation
5. Generated Geometry Displacement
6. Displacement Quality
7. Displacement Repeatability
8. Schedule-Displacement Consistency
9. Motion-Displacement Consistency
10. Grid Displacement Diagnostics
11. Cycle Closure Diagnostics
12. No Driver Update Guard
13. Step 41 Regression Guard
14. Artifact Manifest Summary
15. Verification Commands
16. GitHub Sync Information
17. Acceptance Checklist
18. Decision For Step 43

If Step 42 passes, recommend Step 43 as `Controlled Squid Proxy Geometry Motion Driver Interface Contract`, still no-op/report-only and not geometry-state coupled.

## Verification Commands

Use:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\geometry_displacement_config.py src\geometry_displacement_field.py src\geometry_displacement_quality.py src\geometry_displacement_consistency.py src\geometry_displacement_grid_diagnostics.py baseline_tests\step42_common.py baseline_tests\run_step42_displacement_config_validation.py baseline_tests\run_step42_generate_geometry_displacement.py baseline_tests\run_step42_displacement_quality.py baseline_tests\run_step42_displacement_repeatability.py baseline_tests\run_step42_schedule_displacement_consistency.py baseline_tests\run_step42_motion_displacement_consistency.py baseline_tests\run_step42_grid_displacement_diagnostics.py baseline_tests\run_step42_cycle_closure_diagnostics.py baseline_tests\run_step42_no_driver_update_guard.py baseline_tests\run_step42_step41_regression_guard.py baseline_tests\run_step42_artifact_manifest.py tests\test_step42_geometry_displacement_diagnostics_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step42_displacement_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step42_generate_geometry_displacement.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step42_displacement_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step42_displacement_repeatability.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step42_schedule_displacement_consistency.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step42_motion_displacement_consistency.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step42_grid_displacement_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step42_cycle_closure_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step42_no_driver_update_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step42_step41_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step42_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step42_geometry_displacement_diagnostics_contract.py -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Write final pytest logs to:

- `logs/step42_pytest.log`
- `logs/step42_contract_pytest.log`

Regenerate the Step 42 artifact manifest after final pytest logs exist.

## GitHub Delivery

After implementation and verification:

- stage only Step 42-relevant files plus required README/doc/report updates
- verify `external/taichi_LBM3D` is unchanged
- verify `data/real_geometry_candidates` is unchanged
- commit with `test: add step42 geometry displacement diagnostics`
- push to `origin/main`
- report final commit hash, remote branch, and verification results

## Acceptance Checklist

- [ ] Step 42 detailed goal file exists
- [ ] displacement config validation passes
- [ ] tracked regions include mantle_outer
- [ ] tracked regions include mantle_cavity_proxy
- [ ] tracked regions include funnel_outlet_proxy
- [ ] phase_sample_count is 81
- [ ] grid sizes are 32, 48, 64
- [ ] write_dense_displacement_field is false
- [ ] write_displaced_particles is false
- [ ] apply_to_driver is false
- [ ] apply_to_lbm is false
- [ ] apply_to_mpm is false
- [ ] apply_to_projection is false
- [ ] update_dynamic_solid is false
- [ ] generated displacement row_count is 243
- [ ] displacement fields are finite
- [ ] displacement fields are bounded
- [ ] max displacement norm is within configured limit
- [ ] displacement repeatability passes
- [ ] mantle displacement hash repeats
- [ ] cavity displacement hash repeats
- [ ] funnel displacement hash repeats
- [ ] schedule-displacement consistency passes
- [ ] motion-displacement consistency passes
- [ ] grid displacement diagnostics pass at 32^3
- [ ] grid displacement diagnostics pass at 48^3
- [ ] grid displacement diagnostics pass at 64^3
- [ ] cycle closure diagnostics pass
- [ ] phase 0 and phase 1 displacement envelopes match
- [ ] no driver update guard passes
- [ ] driver_update_count is 0
- [ ] lbm_update_count is 0
- [ ] mpm_update_count is 0
- [ ] projection_update_count is 0
- [ ] dynamic_solid_update_count is 0
- [ ] displaced_particle_output_count is 0
- [ ] dense_displacement_field_output_count is 0
- [ ] Step 41 regression guard passes
- [ ] default boundary_motion_mode remains static
- [ ] default wall_velocity_application_mode remains disabled
- [ ] no default behavior change
- [ ] no moving bounce-back formula changes
- [ ] no LBM collision formula changes
- [ ] no MPM constitutive formula changes
- [ ] no projection formula changes
- [ ] no external/taichi_LBM3D edits
- [ ] no real jet validation claim
- [ ] no jet propulsion validation claim
- [ ] no squid swimming claim
- [ ] no real squid validation claim
- [ ] no Step 42 .vtr outputs
- [ ] no Step 42 particle .npy outputs
- [ ] artifact large_file_count is 0
- [ ] Step 42 output total-size budget passes
- [ ] repo artifact summary total_size_mb is below 310
- [ ] logs/step42_pytest.log exists
- [ ] full pytest passes
- [ ] Step 42 contract test passes
- [ ] git diff --check passes
- [ ] staged whitespace check passes
- [ ] pre-push hook passes
- [ ] Step 42 artifacts are pushed to origin/main
