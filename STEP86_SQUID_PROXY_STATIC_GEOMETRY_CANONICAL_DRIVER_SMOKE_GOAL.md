# Step86 Squid Proxy Static Geometry Canonical Driver Smoke Goal

## Source State

- Repository: `lizhuoh9/MPM-LBM`
- Branch: `main`
- Required starting commit: `f74e44a540f00dd59d2f1b231c942a334bd0891b`
- Accepted predecessor: Step85 squid proxy static geometry activation plan and guard.
- Step86 status before this work: not started.

## Step86 Objective

Run the first post-gate canonical-driver smoke row that enables only procedural static `squid_proxy` geometry. Step86 must execute
exactly one required `FSIDriver3D.run()` row and prove that the row is stable, writes a geometry quality report, preserves the
Step85/Step84/Step31 boundaries, and does not open runtime geometry, wall velocity, real geometry, link-area transfer, larger grids,
VTR output, particle NPY output, solver formula changes, tau migration, or production-readiness claims.

## Correct Claim

Step86 may claim only:

`squid_proxy static geometry canonical driver 3-step smoke passed`.

Step86 must not claim:

- real squid geometry validation;
- squid swimming;
- squid actuation;
- physical validation;
- grid convergence;
- production readiness.

## Required Driver Row

Run exactly one required row:

- row name: `canonical_driver_squid_proxy_static_geometry_32_3step_smoke`
- campaign id: `step86_squid_proxy_static_geometry_canonical_driver_smoke`
- `n_grid`: `32`
- `n_particles`: `1024`
- `n_lbm_steps`: `3`
- `mpm_substeps_per_lbm_step`: `1`
- `coupling_mode`: `moving_boundary`
- `reaction_transfer_mode`: `engineering`
- `geometry_type`: `squid_proxy`
- `geometry_config_path`: `configs/step85_squid_proxy_geometry_1024.json`
- `boundary_motion_mode`: `static`
- `geometry_motion_mode`: `static`
- `geometry_motion_application_mode`: `disabled`
- `wall_velocity_application_mode`: `disabled`
- `quality_check_enabled`: `true`
- `quality_check_strict`: `false`
- `write_vtk`: `false`
- `write_particles`: `false`
- `output_interval`: `1`

Do not add an optional row.

## Required Driver Config

Add `configs/step86_canonical_driver_squid_proxy_static_geometry_32_3step_smoke.json` with the row values above.

The config should not set `target_u_lbm` unless an actual runtime failure forces a narrow row-local correction. The default driver
target flow is acceptable because Step86 is a geometry activation smoke, not a wall-velocity cap isolation step. If a row-local
target-flow change becomes necessary, it must be documented explicitly in the report and evidence; do not hide it in runtime code.

## Hard Boundaries

Step86 may run the canonical driver only through the explicit Step86 runner. It must not edit solver/runtime code.

Forbidden edits:

- `src/mpm_lbm/sim/**`
- `src/mpm_lbm/diagnostics/**`
- `src/mpm_lbm/sim/drivers/**`
- `src/mpm_lbm/sim/coupling/**`
- `src/mpm_lbm/sim/lbm/**`
- `src/mpm_lbm/sim/mpm/**`
- `src/mpm_lbm/sim/geometry/**`
- `src/mpm_lbm/sim/motion/**`
- `src/mpm_lbm/sim/wall_velocity/**`
- `external/taichi_LBM3D/**`
- `data/real_geometry_candidates/**`

If Step86 fails, debug only Step86 config, evidence parsing, acceptance bounds, output guard assumptions, or the already-planned
geometry config. Do not repair the failure by changing solver formulas or runtime behavior.

## Required Files

Top-level:

- `STEP86_SQUID_PROXY_STATIC_GEOMETRY_CANONICAL_DRIVER_SMOKE_GOAL.md`
- `STEP86_SQUID_PROXY_STATIC_GEOMETRY_CANONICAL_DRIVER_SMOKE_REPORT.md`

Configs:

- `configs/step86_squid_proxy_static_geometry_smoke_matrix.json`
- `configs/step86_canonical_driver_squid_proxy_static_geometry_32_3step_smoke.json`
- `configs/step86_squid_proxy_static_geometry_acceptance_policy.json`
- `configs/step86_activation_guard_policy.json`
- `configs/step86_output_guard_policy.json`
- `configs/step86_step85_regression_policy.json`
- `configs/step86_step84_regression_policy.json`
- `configs/step86_step31_reference_policy.json`
- `configs/step86_artifact_manifest_policy.json`

Evidence modules:

- `src/mpm_lbm/evidence/step86_squid_proxy_static_geometry_smoke_runner.py`
- `src/mpm_lbm/evidence/step86_squid_proxy_static_geometry_smoke_audit.py`
- `src/mpm_lbm/evidence/step86_squid_proxy_static_geometry_quality_audit.py`
- `src/mpm_lbm/evidence/step86_squid_proxy_static_geometry_activation_guard.py`
- `src/mpm_lbm/evidence/step86_output_guard.py`
- `src/mpm_lbm/evidence/step86_step85_regression_guard.py`
- `src/mpm_lbm/evidence/step86_step84_regression_guard.py`
- `src/mpm_lbm/evidence/step86_step31_reference_guard.py`

Baseline runners:

- `baseline_tests/step86_common.py`
- `baseline_tests/run_step86_squid_proxy_static_geometry_smoke_matrix.py`
- `baseline_tests/run_step86_squid_proxy_static_geometry_quality.py`
- `baseline_tests/run_step86_activation_guard.py`
- `baseline_tests/run_step86_output_guard.py`
- `baseline_tests/run_step86_step85_regression_guard.py`
- `baseline_tests/run_step86_step84_regression_guard.py`
- `baseline_tests/run_step86_step31_reference_guard.py`
- `baseline_tests/run_step86_artifact_manifest.py`

Tests:

- `tests/test_step86_squid_proxy_static_geometry_smoke_matrix_contract.py`
- `tests/test_step86_squid_proxy_static_geometry_quality_contract.py`
- `tests/test_step86_activation_guard_contract.py`
- `tests/test_step86_output_guard_contract.py`
- `tests/test_step86_step85_regression_contract.py`
- `tests/test_step86_step84_regression_contract.py`
- `tests/test_step86_step31_reference_contract.py`

Docs:

- `docs/86_squid_proxy_static_geometry_canonical_driver_smoke.md`

Allowed status docs to update:

- `README.md`
- `docs/00_project_status.md`
- `docs/ACTIVATION_PRECONDITIONS.md`
- `docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md`
- `docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md`

## Required Outputs

Driver run directory:

- `outputs/step86_driver_runs/canonical_driver_squid_proxy_static_geometry_32_3step_smoke/`

Expected driver files:

- `driver_config.json`
- `driver_timing.json`
- `geo_all_fluid_32.dat`
- `diagnostics_timeseries.csv`
- `diagnostics_timeseries.npz`
- `geometry_quality_report.json`

Forbidden driver files:

- `*.vtr`
- `particle*.npy`
- `geometry_motion_interface_report.json`
- `boundary_motion_interface_report.json`
- `wall_velocity_application_report.json`
- `dense_wall_velocity*.npy`
- `sparse_wall_velocity*.npy`
- `dense_displacement*.npy`
- `displaced_particles*.npy`
- raw real geometry output
- optional driver run dirs

Evidence output directories:

- `outputs/step86_squid_proxy_static_geometry_smoke_matrix/`
- `outputs/step86_squid_proxy_static_geometry_quality/`
- `outputs/step86_activation_guard/`
- `outputs/step86_output_guard/`
- `outputs/step86_step85_regression_guard/`
- `outputs/step86_step84_regression_guard/`
- `outputs/step86_step31_reference_guard/`
- `outputs/step86_artifact_manifest/`

Logs:

- `logs/step86_*.log`

## Smoke Matrix Acceptance

The smoke matrix row must record and pass:

- `driver_run_called = true`
- `canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver`
- `legacy_driver_module_used_as_implementation = false`
- `row_name = canonical_driver_squid_proxy_static_geometry_32_3step_smoke`
- `n_grid = 32`
- `n_particles = 1024`
- `n_lbm_steps = 3`
- `mpm_substeps_per_lbm_step = 1`
- `coupling_mode = moving_boundary`
- `reaction_transfer_mode = engineering`
- `geometry_type = squid_proxy`
- `geometry_config_path = configs/step85_squid_proxy_geometry_1024.json`
- `geometry_config_path_exists = true`
- `completed_lbm_steps = 3`
- `total_mpm_substeps >= 3`
- `diagnostics_row_count >= 4`
- `has_nan = false`
- `has_inf = false`
- `stable = true`
- `runtime_hard_fail = false`

The matrix summary must record and pass:

- `step86_squid_proxy_static_geometry_smoke_matrix_pass = true`
- `required_row_count = 1`
- `optional_row_count = 0`
- `required_stable_count = 1`
- `activation_feature_count = 1`
- `procedural_geometry_enabled_count = 1`
- `squid_proxy_enabled_count = 1`
- `real_geometry_candidate_enabled_count = 0`
- `real_geometry_enabled_count = 0`
- `runtime_geometry_enabled_count = 0`
- `wall_velocity_enabled_count = 0`
- `combined_runtime_geometry_wall_velocity_enabled_count = 0`
- `link_area_enabled_count = 0`
- `grid_48_enabled_count = 0`
- `grid_64_enabled_count = 0`
- `write_vtk_count = 0`
- `write_particles_count = 0`
- `runtime_code_changed = false`
- `solver_behavior_changed = false`
- `physics_feature_expansion = squid_proxy_static_geometry_only`

Important definition:

`squid_proxy` is a procedural proxy geometry, not real geometry candidate data. Step86 evidence must explicitly distinguish:

- `procedural_geometry_enabled = true`
- `squid_proxy_enabled = true`
- `real_geometry_candidate_enabled = false`
- `real_geometry_enabled = false`

Do not reuse older logic that treats any non-box geometry as real geometry.

## Geometry Quality Acceptance

The driver must write `geometry_quality_report.json`. The quality audit must record and pass:

- `step86_squid_proxy_static_geometry_quality_pass = true`
- `geometry_quality_report_exists = true`
- `geometry_quality_report_pass = true`
- `geometry_quality_report_pass_count = 1`
- `geometry_quality_strict = false`
- `quality_report_geometry_type = squid_proxy`
- `quality_report_empty = false`
- `quality_report_occupied_count > 0`
- `quality_report_surface_voxel_count > 0`
- `quality_report_touches_domain_boundary = false`
- `finite_max_grid_reaction_norm_count = 1`
- `squid_proxy_enabled_count = 1`

If particle-component counts are not available from existing runtime reports, do not change runtime just to synthesize them. The Step86 report should state that Step86 uses committed geometry quality report fields rather than adding new sampler stats.

## Numeric Smoke Bounds

Use broad smoke bounds:

- `rho_min_min > 0.90`
- `rho_max_max < 1.10`
- `lbm_max_v_max < 0.5`
- `mpm_min_J_min > 0.0`
- `mpm_max_speed_max < 10.0`
- `projected_mass_final > 0.0`
- `active_cell_count_final > 0`
- `bb_link_count_max > 0`
- `max_grid_reaction_norm_max` finite

## Activation Guard Acceptance

The activation guard artifact must prove:

- `step86_activation_guard_pass = true`
- `activation_feature_count = 1`
- `squid_proxy_enabled_count = 1`
- `procedural_geometry_enabled_count = 1`
- `real_geometry_enabled_count = 0`
- `real_geometry_candidate_enabled_count = 0`
- `runtime_geometry_enabled_count = 0`
- `wall_velocity_enabled_count = 0`
- `combined_runtime_geometry_wall_velocity_enabled_count = 0`
- `link_area_enabled_count = 0`
- `grid_48_enabled_count = 0`
- `grid_64_enabled_count = 0`
- `write_vtk_count = 0`
- `write_particles_count = 0`

## Output Guard Acceptance

The output guard artifact must prove:

- `output_guard_pass = true`
- `step86_required_driver_run_dir_count = 1`
- `step86_optional_driver_run_dir_count = 0`
- `step86_vtr_count = 0`
- `step86_particle_npy_count = 0`
- `step86_dense_wall_velocity_output_count = 0`
- `step86_sparse_wall_velocity_output_count = 0`
- `step86_dense_displacement_output_count = 0`
- `step86_displaced_particle_output_count = 0`
- `step86_raw_geometry_output_count = 0`
- `step86_real_geometry_candidate_output_count = 0`
- `private_absolute_path_count = 0`
- `protected_external_edit_count = 0`
- `protected_real_geometry_candidate_edit_count = 0`
- `protected_sim_edit_count = 0`
- `protected_diagnostics_edit_count = 0`
- `artifact_budget_pass = true`

## Regression Guards

Step85 regression guard must prove:

- `step85_squid_proxy_static_geometry_activation_plan_pass = true`
- `step85_squid_proxy_static_geometry_activation_guard_pass = true`
- `step85_step84_regression_guard_pass = true`
- `step85_step31_reference_guard_pass = true`
- `step85_output_guard_pass = true`
- `step85_artifact_budget_pass = true`
- `step85_activation_feature_count = 0`
- `planned_step86_activation_feature_count = 1`
- `step85_driver_run_dir_count = 0`
- `step85_vtr_count = 0`
- `step85_particle_npy_count = 0`

Step84 regression guard must prove:

- `step84_runtime_geometry_wall_velocity_combined_smoke_matrix_pass = true`
- `step84_runtime_geometry_wall_velocity_combined_quality_pass = true`
- `step84_activation_guard_pass = true`
- `step84_output_guard_pass = true`
- `step84_artifact_budget_pass = true`
- `step84_activation_feature_count = 2`
- `step84_runtime_geometry_enabled_count = 1`
- `step84_wall_velocity_enabled_count = 1`
- `step84_combined_runtime_geometry_wall_velocity_enabled_count = 1`
- `step84_squid_proxy_enabled_count = 0`
- `step84_vtr_count = 0`
- `step84_particle_npy_count = 0`

Step31 reference guard must prove:

- `step85_step31_reference_guard_pass = true`
- `step30_squid_proxy_geometry_config_exists = true`
- `step30_geometry_type = squid_proxy`
- `step31_static_driver_reference_exists = true`
- `step31_not_real_squid_validation_claim = true`
- `step31_no_squid_swimming_claim = true`

## Verification Commands

Run baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step86_squid_proxy_static_geometry_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step86_squid_proxy_static_geometry_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step86_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step86_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step86_step85_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step86_step84_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step86_step31_reference_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step86_artifact_manifest.py
```

Run focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q tests\test_step86_squid_proxy_static_geometry_smoke_matrix_contract.py tests\test_step86_squid_proxy_static_geometry_quality_contract.py tests\test_step86_activation_guard_contract.py tests\test_step86_output_guard_contract.py tests\test_step86_step85_regression_contract.py tests\test_step86_step84_regression_contract.py tests\test_step86_step31_reference_contract.py
```

Run full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Refresh output guard and artifact manifest after final pytest logs are written.

Run git checks:

```powershell
git diff --check
git diff --cached --check
git status --short src/mpm_lbm/sim src/mpm_lbm/diagnostics external/taichi_LBM3D data/real_geometry_candidates
```

## Commit And Push

After verification:

- confirm `origin/main` still points at `f74e44a540f00dd59d2f1b231c942a334bd0891b` before committing;
- commit with `test: add step86 squid proxy static geometry canonical driver smoke`;
- push to `origin main`;
- report final commit hash and branch.

## Step87 Direction

If Step86 is green, the next step should not jump directly to user simulation. The safer next step is a plan-and-guard phase for combining:

- squid proxy static geometry;
- runtime geometry diagnostic-only;
- wall velocity `solid_vel`.

That combined path should also be planned and guarded before a smoke run.
