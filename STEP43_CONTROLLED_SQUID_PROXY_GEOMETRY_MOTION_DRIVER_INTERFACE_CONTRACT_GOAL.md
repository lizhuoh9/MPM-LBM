# Step 43 Controlled Squid Proxy Geometry Motion Driver Interface Contract Goal

## 1. Objective

Implement Step 43: Controlled Squid Proxy Geometry Motion Driver Interface Contract.

Step 43 adds a guarded driver-side geometry-motion interface for `static` and `prescribed_kinematic` modes. It remains no-op/report-only and does not mutate particles, LBM fields, projection state, `dynamic_solid`, boundary links, solver formulas, or coupled geometry.

The Step 43 implementation must bridge the accepted Step 42 prescribed geometry displacement diagnostics into a driver-facing interface contract without activating geometry mutation. It must prove the interface can be configured, validated, reported, and run through short smoke driver rows while leaving static physics diagnostics equivalent to diagnostic-only geometry-motion rows.

## 2. Source Of Truth

This file is the source-of-truth contract for Step 43. The inline `/goal` should reference this file by absolute path rather than attempting to carry the whole implementation contract.

## 3. Prior Accepted Boundary

Step 42 is accepted and remains the upstream dependency:

- Step 42 derives prescribed geometry displacement diagnostics only.
- Step 42 does not update driver geometry.
- Step 42 does not displace MPM particles in `FSIDriver3D`.
- Step 42 does not update LBM `solid_phi`.
- Step 42 does not update `dynamic_solid`.
- Step 42 does not change moving bounce-back formulas.
- Step 42 produces 243 displacement rows: 81 phases times three tracked regions.
- Step 42 configs keep `apply_to_driver`, `apply_to_lbm`, `apply_to_mpm`, `apply_to_projection`, `update_dynamic_solid`, and `driver_integration_enabled` false.

Step 43 may read Step 42 configs and committed Step 42 artifacts, but it must not reinterpret Step 42 diagnostics as coupled geometry mutation or solver validation.

## 4. Hard Non-Goals

Step 43 must not implement:

- driver-coupled geometry update
- MPM particle displacement
- solid particle position mutation
- LBM `solid_phi` update
- LBM `solid_vel` update from geometry displacement
- `dynamic_solid` update
- projection from displaced geometry
- boundary-link recomputation from displaced geometry
- moving bounce-back formula changes
- LBM collision or streaming formula changes
- MPM constitutive formula changes
- coupler formula changes
- wall-velocity formula changes
- free-body motion
- body trajectory
- squid swimming
- jet propulsion validation
- real jet validation
- real squid validation
- production sharp-interface FSI readiness
- edits under `external/taichi_LBM3D`
- raw real-geometry or scan-data intake

## 5. Allowed Work

Step 43 may add:

- `geometry_motion_mode` config schema
- `geometry_motion_application_mode` config schema
- driver-facing geometry-motion interface config
- diagnostic-only geometry-motion interface report
- `FSIDriver3D` no-op/report-only hook
- static 48^3 regression rows
- prescribed diagnostic-only 48^3 no-op rows
- static-vs-diagnostic no-op comparison artifacts
- no geometry-state mutation guard
- Step 42 regression guard
- strict quality-report aggregation for Step 43 driver rows
- small CSV/JSON/NPZ/log artifacts
- docs, report, README updates, and contract tests

## 6. Required Source Changes

### `src/fsi_config.py`

Add safe geometry-motion defaults:

```python
VALID_GEOMETRY_MOTION_MODES = ("static", "prescribed_kinematic")
VALID_GEOMETRY_MOTION_APPLICATION_MODES = ("disabled", "diagnostic_only")

geometry_motion_mode: str = "static"
geometry_motion_config_path: Optional[str] = None
geometry_motion_report_enabled: bool = False

geometry_motion_application_mode: str = "disabled"
geometry_motion_application_config_path: Optional[str] = None
geometry_motion_application_report_enabled: bool = False
```

Validation rules:

- `geometry_motion_mode` is `static` or `prescribed_kinematic`.
- `geometry_motion_application_mode` is `disabled` or `diagnostic_only`.
- Static mode requires `geometry_motion_config_path is None`.
- Static mode requires `geometry_motion_application_mode == "disabled"`.
- Disabled application mode requires `geometry_motion_application_config_path is None`.
- Prescribed diagnostic-only mode requires a geometry-motion config path.
- No Step 43 config path may enable mutation flags.

### `src/geometry_motion_config.py`

Add `GeometryMotionInterfaceConfig` as a frozen dataclass. It must load and validate:

- `geometry_motion_id`
- `geometry_motion_mode`
- `displacement_config_path`
- `displacement_artifact_path`
- `schedule_config_path`
- `motion_mapping_config_path`
- `region_config_path`
- `geometry_config_path`
- `application_mode = "diagnostic_only"`
- `apply_to_driver = False`
- `apply_to_mpm_particles = False`
- `apply_to_lbm_solid_phi = False`
- `apply_to_lbm_solid_vel = False`
- `apply_to_projection = False`
- `update_dynamic_solid = False`
- `recompute_boundary_links = False`
- `mutate_geometry_state = False`
- `diagnostic_only = True`

Validation must confirm:

- `application_mode == "diagnostic_only"`
- `diagnostic_only is True`
- all mutation flags are false
- all referenced config/artifact paths exist
- Step 42 displacement artifact has `row_count == 243`
- Step 42 displacement artifact has `phase_sample_count == 81`
- tracked regions are exactly `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy`
- Step 42 displacement quality and cycle closure remain passing when used by the interface report

### `src/geometry_motion_interface.py`

Add no-op/report-only helpers:

- `load_geometry_motion_interface_config(path)`
- `validate_geometry_motion_interface_config(config, root=None)`
- `summarize_geometry_motion_interface(config, root=None)`
- `write_geometry_motion_interface_report(config, out_dir)`
- `assert_geometry_motion_noop_flags(config)`

The report summary must include:

- `geometry_motion_mode`
- `application_mode`
- `diagnostic_only`
- `displacement_row_count`
- `phase_sample_count`
- `tracked_region_count`
- `tracked_regions`
- `max_displacement_norm`
- `cycle_closure_pass`
- `repeatability_pass`
- `apply_to_driver`
- `apply_to_mpm_particles`
- `apply_to_lbm_solid_phi`
- `apply_to_lbm_solid_vel`
- `apply_to_projection`
- `update_dynamic_solid`
- `recompute_boundary_links`
- `mutate_geometry_state`
- `no_op_pass`

### `src/fsi_driver.py`

Add a report-only geometry-motion hook near initialization/report hooks:

- If `geometry_motion_application_mode == "disabled"`, do nothing and write nothing.
- If `geometry_motion_application_mode == "diagnostic_only"`, load and validate the configured interface, optionally write `geometry_motion_interface_report.json`, and return/store report metadata for runner summary.

The hook must not:

- mutate `self.solid.x`
- mutate `self.solid.v`
- mutate LBM `solid_phi`
- mutate LBM `solid_vel`
- mutate LBM `dynamic_solid`
- call projection from geometry-motion path
- recompute boundary links from displaced geometry
- mutate coupler state
- change step order or solver formulas

## 7. Required Configs

Add:

- `configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json`
- `configs/step43_static_48_moving_boundary.json`
- `configs/step43_diagnostic_geometry_motion_48_moving_boundary.json`
- `configs/step43_static_48_link_area.json`
- `configs/step43_diagnostic_geometry_motion_48_link_area.json`

Driver rows must use:

- `geometry_type = "squid_proxy"`
- `geometry_config_path = "configs/step30_squid_proxy_geometry.json"`
- `n_grid = 48`
- `n_particles = 4096`
- `n_lbm_steps = 5`
- `mpm_substeps_per_lbm_step = 5`
- `target_u_lbm = [0.0, 0.0, 0.0]`
- `quality_check_enabled = true`
- `quality_check_strict = true`
- `write_vtk = false`
- `write_particles = false`
- `wall_velocity_application_mode = "disabled"`

Static rows must keep:

- `geometry_motion_mode = "static"`
- `geometry_motion_application_mode = "disabled"`

Diagnostic rows must set:

- `geometry_motion_mode = "prescribed_kinematic"`
- `geometry_motion_config_path = "configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json"`
- `geometry_motion_report_enabled = true`
- `geometry_motion_application_mode = "diagnostic_only"`
- `geometry_motion_application_config_path = "configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json"`
- `geometry_motion_application_report_enabled = true`

## 8. Required Baseline Runners

Add:

- `baseline_tests/step43_common.py`
- `baseline_tests/run_step43_geometry_motion_config_validation.py`
- `baseline_tests/run_step43_geometry_motion_interface_report.py`
- `baseline_tests/run_step43_static_driver_regression.py`
- `baseline_tests/run_step43_diagnostic_geometry_motion_noop_smoke.py`
- `baseline_tests/run_step43_static_vs_diagnostic_noop_comparison.py`
- `baseline_tests/run_step43_no_geometry_state_mutation_guard.py`
- `baseline_tests/run_step43_quality_report_aggregation.py`
- `baseline_tests/run_step43_step42_regression_guard.py`
- `baseline_tests/run_step43_artifact_manifest.py`

## 9. Required Outputs

Step 43 must commit these small artifacts:

- `outputs/step43_geometry_motion_config_validation/geometry_motion_config_validation.csv`
- `outputs/step43_geometry_motion_config_validation/geometry_motion_config_validation.json`
- `outputs/step43_geometry_motion_interface_report/geometry_motion_interface_report.json`
- `outputs/step43_geometry_motion_interface_report/geometry_motion_interface_summary.csv`
- `outputs/step43_static_driver_regression/static_driver_results.csv`
- `outputs/step43_static_driver_regression/static_driver_results.json`
- `outputs/step43_static_driver_regression/static_driver_results.npz`
- `outputs/step43_diagnostic_geometry_motion_noop_smoke/diagnostic_noop_results.csv`
- `outputs/step43_diagnostic_geometry_motion_noop_smoke/diagnostic_noop_results.json`
- `outputs/step43_diagnostic_geometry_motion_noop_smoke/diagnostic_noop_results.npz`
- `outputs/step43_static_vs_diagnostic_noop_comparison/static_vs_diagnostic_noop.csv`
- `outputs/step43_static_vs_diagnostic_noop_comparison/static_vs_diagnostic_noop.json`
- `outputs/step43_no_geometry_state_mutation_guard/no_geometry_state_mutation_guard.csv`
- `outputs/step43_no_geometry_state_mutation_guard/no_geometry_state_mutation_guard.json`
- `outputs/step43_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step43_quality_report_aggregation/quality_report_summary.json`
- `outputs/step43_step42_regression_guard/step42_regression_guard.csv`
- `outputs/step43_step42_regression_guard/step42_regression_guard.json`
- `outputs/step43_artifact_manifest/artifact_manifest.csv`
- `outputs/step43_artifact_manifest/artifact_summary.csv`
- `outputs/step43_artifact_manifest/artifact_summary.json`

Each runner must write a corresponding `logs/step43_*.log` marker.

## 10. Required Contract Test

Add:

- `tests/test_step43_geometry_motion_driver_interface_contract.py`

The contract test must cover:

1. required files and logs exist
2. `FSIDriverConfig` geometry-motion defaults are safe
3. geometry-motion config validation passes
4. geometry-motion interface report passes
5. static driver regression passes
6. diagnostic geometry-motion no-op smoke passes
7. static-vs-diagnostic no-op comparison passes
8. no geometry-state mutation guard passes
9. quality report aggregation passes
10. Step 42 regression guard passes
11. default modes remain unchanged
12. docs/report scope phrases exist
13. forbidden claims are absent
14. artifact budget passes
15. report acceptance checklist is complete
16. configs and reports contain disabled mutation flags

Required scope phrases:

- `Step 43 is controlled squid proxy geometry motion driver interface.`
- `Step 43 defines a guarded driver interface only.`
- `Step 43 keeps geometry motion diagnostic-only.`
- `Step 43 does not update driver geometry.`
- `Step 43 does not displace MPM particles.`
- `Step 43 does not update LBM solid_phi.`
- `Step 43 does not update dynamic_solid.`
- `Step 43 does not recompute boundary links from displaced geometry.`
- `Step 43 does not change moving bounce-back formulas.`
- `The default geometry_motion_mode remains static.`
- `The default geometry_motion_application_mode remains disabled.`
- `The default boundary_motion_mode remains static.`
- `The default wall_velocity_application_mode remains disabled.`

Forbidden claims:

- `driver geometry is updated`
- `geometry displacement is integrated into FSIDriver3D`
- `MPM particles are displaced by Step 43`
- `LBM solid_phi is updated by geometry motion`
- `LBM solid_vel is updated by geometry motion`
- `dynamic_solid is updated by geometry motion`
- `projection is updated from displaced geometry`
- `boundary links are recomputed from displaced geometry`
- `moving bounce-back formula is changed`
- `squid swimming is implemented`
- `free-body motion is implemented`
- `real jet validation`
- `real squid simulation is validated`
- `production-ready sharp-interface FSI`

## 11. Required Docs And Report

Add:

- `docs/43_controlled_squid_proxy_geometry_motion_driver_interface.md`
- `STEP43_CONTROLLED_SQUID_PROXY_GEOMETRY_MOTION_DRIVER_INTERFACE_CONTRACT_REPORT.md`

Update:

- `README.md`

The report must include:

- `## 1. Goal`
- `## 2. Files Created And Updated`
- `## 3. Explicit Non-Goals`
- `## 4. Geometry Motion Config Validation`
- `## 5. Geometry Motion Interface Report`
- `## 6. Static Driver Regression`
- `## 7. Diagnostic Geometry Motion No-Op Smoke`
- `## 8. Static Vs Diagnostic No-Op Comparison`
- `## 9. No Geometry State Mutation Guard`
- `## 10. Quality Report Aggregation`
- `## 11. Step 42 Regression Guard`
- `## 12. Artifact Manifest Summary`
- `## 13. Verification Commands`
- `## 14. GitHub Sync Information`
- `## 15. Acceptance Checklist`
- `## 16. Decision For Step 44`

All checklist entries must be checked before the final commit.

## 12. Driver Acceptance Criteria

Static driver regression:

- `row_count == 2`
- `stable_count == 2`
- `geometry_motion_mode == "static"`
- `geometry_motion_application_mode == "disabled"`
- `completed_lbm_steps >= 5`
- `total_mpm_substeps >= 25`
- `rho_min_global > 0.95`
- `rho_max_global < 1.05`
- `lbm_max_v_global < 0.1`
- `mpm_min_J_global > 0`
- `projected_mass_min > 0`
- `active_cell_count > 0`
- `quality_pass == true`
- no NaN
- no Inf

Diagnostic geometry-motion smoke:

- `row_count == 2`
- `stable_count == 2`
- `geometry_motion_mode == "prescribed_kinematic"`
- `geometry_motion_application_mode == "diagnostic_only"`
- `geometry_motion_report_count == 2`
- `no_op_pass == true` for every report
- all mutation flags false
- same stability thresholds as static driver

Static-vs-diagnostic comparison:

- `row_count == 2`
- `comparison_pass_count == 2`
- physics diagnostic deltas are effectively zero for no-op fields
- timing fields may be ignored

## 13. Mutation Guard Acceptance Criteria

The no geometry-state mutation guard must report:

- `guard_pass == true`
- `mpm_particle_mutation_count == 0`
- `lbm_solid_phi_mutation_count == 0`
- `lbm_solid_vel_mutation_count == 0`
- `dynamic_solid_mutation_count == 0`
- `projection_call_from_geometry_motion_count == 0`
- `boundary_link_recompute_count == 0`
- `geometry_state_mutation_count == 0`
- `displaced_particle_output_count == 0`
- `dense_displacement_field_output_count == 0`

## 14. Artifact Budget

The Step 43 artifact manifest must pass:

- `large_file_count == 0`
- `step43_total_size_mb < 10`
- `total_size_mb < 320`
- `step43_vtr_count == 0`
- `step43_particle_npy_count == 0`
- `raw_candidate_large_file_count == 0`
- `scan_data_file_count == 0`
- `private_absolute_path_count == 0`

## 15. Verification Commands

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\geometry_motion_config.py src\geometry_motion_interface.py src\fsi_config.py src\fsi_driver.py baseline_tests\step43_common.py baseline_tests\run_step43_geometry_motion_config_validation.py baseline_tests\run_step43_geometry_motion_interface_report.py baseline_tests\run_step43_static_driver_regression.py baseline_tests\run_step43_diagnostic_geometry_motion_noop_smoke.py baseline_tests\run_step43_static_vs_diagnostic_noop_comparison.py baseline_tests\run_step43_no_geometry_state_mutation_guard.py baseline_tests\run_step43_quality_report_aggregation.py baseline_tests\run_step43_step42_regression_guard.py baseline_tests\run_step43_artifact_manifest.py tests\test_step43_geometry_motion_driver_interface_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step43_geometry_motion_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step43_geometry_motion_interface_report.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step43_static_driver_regression.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step43_diagnostic_geometry_motion_noop_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step43_static_vs_diagnostic_noop_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step43_no_geometry_state_mutation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step43_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step43_step42_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step43_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step43_geometry_motion_driver_interface_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Regenerate the artifact manifest after final verification logs exist.

## 16. GitHub Delivery

After implementation and verification:

1. Verify branch and remote.
2. Stage only Step 43 relevant code, configs, docs, tests, logs, and small artifacts.
3. Commit with a conventional message, preferably `feat: add step 43 geometry motion driver interface`.
4. Push to the configured GitHub remote branch.
5. Report final commit hash, branch, remote, test pass counts, artifact summary, and any verification caveats.

## 17. Final Acceptance Checklist

- [ ] Step 43 detailed goal file exists.
- [ ] `geometry_motion_mode` default is `static`.
- [ ] `geometry_motion_application_mode` default is `disabled`.
- [ ] Geometry-motion config validation passes.
- [ ] Prescribed geometry-motion config is `diagnostic_only`.
- [ ] Step 42 displacement artifact path exists.
- [ ] Step 42 displacement row count is 243.
- [ ] Tracked regions include `mantle_outer`.
- [ ] Tracked regions include `mantle_cavity_proxy`.
- [ ] Tracked regions include `funnel_outlet_proxy`.
- [ ] `apply_to_driver` is false.
- [ ] `apply_to_mpm_particles` is false.
- [ ] `apply_to_lbm_solid_phi` is false.
- [ ] `apply_to_lbm_solid_vel` is false.
- [ ] `apply_to_projection` is false.
- [ ] `update_dynamic_solid` is false.
- [ ] `recompute_boundary_links` is false.
- [ ] `mutate_geometry_state` is false.
- [ ] Geometry-motion interface report exists.
- [ ] Geometry-motion interface `no_op_pass` is true.
- [ ] Static driver regression runs two rows.
- [ ] Diagnostic geometry-motion no-op smoke runs two rows.
- [ ] All four driver rows are stable.
- [ ] All rows complete at least five LBM steps.
- [ ] All rows complete at least 25 MPM substeps.
- [ ] Every driver row writes `geometry_quality_report.json`.
- [ ] Every quality report passes.
- [ ] Static-vs-diagnostic no-op comparison passes.
- [ ] No geometry-state mutation guard passes.
- [ ] MPM particle mutation count is 0.
- [ ] LBM `solid_phi` mutation count is 0.
- [ ] LBM `solid_vel` mutation count is 0.
- [ ] `dynamic_solid` mutation count is 0.
- [ ] Projection call from geometry-motion count is 0.
- [ ] Boundary-link recompute count is 0.
- [ ] Step 42 regression guard passes.
- [ ] Default `boundary_motion_mode` remains `static`.
- [ ] Default `wall_velocity_application_mode` remains `disabled`.
- [ ] No default behavior changes.
- [ ] No moving bounce-back formula changes.
- [ ] No LBM collision formula changes.
- [ ] No MPM constitutive formula changes.
- [ ] No projection formula changes.
- [ ] No `external/taichi_LBM3D` edits.
- [ ] No real jet validation claim.
- [ ] No jet propulsion validation claim.
- [ ] No squid swimming claim.
- [ ] No real squid validation claim.
- [ ] No Step 43 `.vtr` outputs.
- [ ] No Step 43 particle `.npy` outputs.
- [ ] Artifact `large_file_count == 0`.
- [ ] Step 43 output total-size budget passes.
- [ ] Repo artifact summary `total_size_mb < 320`.
- [ ] Step 43 contract test passes.
- [ ] Full `pytest -q` passes.
- [ ] `git diff --check` passes.
- [ ] Staged whitespace check passes.
- [ ] Pre-push hook passes.
- [ ] Step 43 artifacts are pushed to `origin/main`.

## 18. Decision For Step 44

If Step 43 is accepted, Step 44 may consider a controlled diagnostic geometry-update smoke. Step 44 must still be opt-in and conservative. It should start with a diagnostic runtime copy or projection-only smoke rather than directly coupling displaced geometry, wall velocity, projection, and moving bounce-back into full production-style motion.
