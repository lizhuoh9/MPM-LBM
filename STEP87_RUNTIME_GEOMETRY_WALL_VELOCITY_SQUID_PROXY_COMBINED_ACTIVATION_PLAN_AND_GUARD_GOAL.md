# Step87 Runtime Geometry Wall Velocity Squid Proxy Combined Activation Plan And Guard Goal

## Source State

- Repository: `lizhuoh9/MPM-LBM`
- Branch: `main`
- Required starting commit: `e69e11971728a370465e54f753988d2b9ab228b5`
- Accepted predecessor: Step86 squid proxy static geometry canonical driver smoke.
- Step87 status before this work: not started.

## Step87 Objective

Step87 is a plan-and-guard-only step. It must not run `FSIDriver3D`,
must not call `driver.run()`, and must not execute a simulation.

Step87 must plan and guard exactly one future Step88 canonical driver smoke row
that combines three previously validated feature branches in one row:

- `squid_proxy_static_geometry` from Step86;
- `runtime_geometry_diagnostic_only` from Step80 and Step84;
- `wall_velocity_solid_vel` from Step82 and Step84.

The Step87 deliverable is explicit JSON configuration, evidence modules, runner
scripts, contract tests, docs, reports, logs, output guard evidence, artifact
manifest evidence, and regression guards proving that Step88 is allowed only
inside the stated bounded envelope.

## Correct Step87 Claim

Step87 may claim only:

```text
runtime geometry diagnostic-only + wall velocity solid_vel + squid_proxy combined smoke is planned and guarded for Step88.
```

Step87 must not claim:

- three-feature combined smoke passed;
- squid swimming works;
- squid actuation works;
- real squid validation;
- moving geometry physical validation;
- moving-wall physics validation;
- physical validation;
- grid convergence;
- production readiness.

## Hard Runtime Boundary

Step87 must not run:

- `FSIDriver3D`;
- `driver.run()`;
- any simulation;
- any projection smoke;
- any canonical driver row.

Step87 must not create any `outputs/step87_driver_runs/` directory.

## Protected Paths

Step87 must not edit:

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

The implementation should live only in Step87 configs, evidence modules,
baseline runners, tests, docs, reports, logs, and output artifacts.

## Forbidden Activations

Step87 must keep these closed:

- real geometry candidate data;
- real geometry runtime activation;
- link-area transfer;
- 48^3 rows;
- 64^3 rows;
- VTR output;
- particle NPY output;
- dense wall velocity output;
- sparse wall velocity output;
- dense displacement output;
- displaced particle output;
- raw real-geometry output;
- solver formula changes;
- tau migration;
- bounce-back formula changes;
- direct LBM population writes through wall velocity;
- MPM state writes through wall velocity;
- projector state writes through wall velocity;
- squid swimming claims;
- squid actuation claims;
- real squid validation claims;
- physical validation claims;
- production readiness claims.

## Planned Step88 Row

Step87 may plan exactly one required future Step88 row:

```text
canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

The planned Step88 row parameters must be:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = squid_proxy
geometry_config_path = configs/step85_squid_proxy_geometry_1024.json
quality_check_enabled = true
quality_check_strict = false
```

Runtime geometry plan:

```text
geometry_motion_mode = prescribed_kinematic
geometry_motion_application_mode = diagnostic_only
geometry_motion_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_application_config_path = configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json
geometry_motion_report_enabled = true
geometry_motion_application_report_enabled = true
geometry_mutation_allowed = false
```

Wall velocity plan:

```text
boundary_motion_mode = prescribed_kinematic
boundary_motion_config_path = configs/step34_boundary_motion_interface_prescribed_kinematic.json
boundary_motion_report_enabled = true
wall_velocity_application_mode = solid_vel_experimental
wall_velocity_application_config_path = configs/step36_wall_velocity_application_solid_vel_experimental.json
wall_velocity_application_report_enabled = true
target_lbm_field = solid_vel
apply_to_lbm_solid_vel_allowed = true
apply_to_lbm_populations_allowed = false
apply_to_mpm_allowed = false
apply_to_projector_allowed = false
modify_bounceback_formula_allowed = false
```

Output plan:

```text
write_vtk = false
write_particles = false
```

Step88 may combine `geometry_type = squid_proxy` with runtime geometry
diagnostic-only reporting and `solid_vel_experimental` wall-velocity reporting.
The planned runtime geometry remains diagnostic-only/no-op. The Step88 plan is
not real geometry mutation and not squid actuation.

## Required New Files

Root artifacts:

- `STEP87_RUNTIME_GEOMETRY_WALL_VELOCITY_SQUID_PROXY_COMBINED_ACTIVATION_PLAN_AND_GUARD_GOAL.md`
- `STEP87_RUNTIME_GEOMETRY_WALL_VELOCITY_SQUID_PROXY_COMBINED_ACTIVATION_PLAN_AND_GUARD_REPORT.md`

Configs:

- `configs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan.json`
- `configs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_guard_policy.json`
- `configs/step87_step86_regression_policy.json`
- `configs/step87_step84_regression_policy.json`
- `configs/step87_step82_regression_policy.json`
- `configs/step87_step80_regression_policy.json`
- `configs/step87_output_guard_policy.json`
- `configs/step87_artifact_manifest_policy.json`

Evidence modules:

- `src/mpm_lbm/evidence/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan.py`
- `src/mpm_lbm/evidence/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard.py`
- `src/mpm_lbm/evidence/step87_step86_regression_guard.py`
- `src/mpm_lbm/evidence/step87_step84_regression_guard.py`
- `src/mpm_lbm/evidence/step87_step82_regression_guard.py`
- `src/mpm_lbm/evidence/step87_step80_regression_guard.py`
- `src/mpm_lbm/evidence/step87_output_guard.py`

Baseline runners:

- `baseline_tests/step87_common.py`
- `baseline_tests/run_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan.py`
- `baseline_tests/run_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard.py`
- `baseline_tests/run_step87_step86_regression_guard.py`
- `baseline_tests/run_step87_step84_regression_guard.py`
- `baseline_tests/run_step87_step82_regression_guard.py`
- `baseline_tests/run_step87_step80_regression_guard.py`
- `baseline_tests/run_step87_output_guard.py`
- `baseline_tests/run_step87_artifact_manifest.py`

Tests:

- `tests/test_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_contract.py`
- `tests/test_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard_contract.py`
- `tests/test_step87_step86_regression_contract.py`
- `tests/test_step87_step84_regression_contract.py`
- `tests/test_step87_step82_regression_contract.py`
- `tests/test_step87_step80_regression_contract.py`
- `tests/test_step87_output_guard_contract.py`

Docs:

- `docs/87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_and_guard.md`

Outputs:

- `outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan/`
- `outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard/`
- `outputs/step87_step86_regression_guard/`
- `outputs/step87_step84_regression_guard/`
- `outputs/step87_step82_regression_guard/`
- `outputs/step87_step80_regression_guard/`
- `outputs/step87_output_guard/`
- `outputs/step87_artifact_manifest/`

Logs:

- `logs/step87_*.log`

## Allowed Existing File Updates

Step87 may update only these existing docs/status surfaces:

- `README.md`
- `docs/00_project_status.md`
- `docs/ACTIVATION_PRECONDITIONS.md`
- `docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md`
- `docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md`

Do not update runtime docs in a way that overstates Step87 as a simulation.

## Required Activation Plan Config

Add `configs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan.json`
with fields matching this contract. It must include at least:

```json
{
  "step": "Step87",
  "campaign_id": "step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_and_guard",
  "previous_step": "Step86",
  "previous_required_commit": "e69e11971728a370465e54f753988d2b9ab228b5",
  "activation_kind": "combined_feature_plan_only",
  "features_under_plan": [
    "squid_proxy_static_geometry",
    "runtime_geometry_diagnostic_only",
    "wall_velocity_solid_vel"
  ],
  "driver_run_required": false,
  "fsidriver_run_allowed": false,
  "simulation_run_allowed": false,
  "step88_allowed": true,
  "step88_allowed_row_name": "canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke",
  "step88_allowed_n_grid": 32,
  "step88_allowed_n_particles": 1024,
  "step88_allowed_n_lbm_steps": 3,
  "step88_allowed_mpm_substeps_per_lbm_step": 1,
  "step88_allowed_coupling_mode": "moving_boundary",
  "step88_allowed_reaction_transfer_mode": "engineering",
  "squid_proxy_planned_for_step88": true,
  "geometry_type_allowed_for_step88": "squid_proxy",
  "geometry_config_path_allowed_for_step88": "configs/step85_squid_proxy_geometry_1024.json",
  "quality_check_enabled_allowed_for_step88": true,
  "quality_check_strict_allowed_for_step88": false,
  "geometry_quality_report_required_for_step88": true,
  "runtime_geometry_planned_for_step88": true,
  "geometry_motion_mode_allowed_for_step88": "prescribed_kinematic",
  "geometry_motion_application_mode_allowed_for_step88": "diagnostic_only",
  "geometry_motion_config_path_allowed_for_step88": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
  "geometry_motion_application_config_path_allowed_for_step88": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
  "geometry_motion_interface_report_required_for_step88": true,
  "geometry_mutation_allowed": false,
  "wall_velocity_planned_for_step88": true,
  "boundary_motion_mode_allowed_for_step88": "prescribed_kinematic",
  "boundary_motion_config_path_allowed_for_step88": "configs/step34_boundary_motion_interface_prescribed_kinematic.json",
  "wall_velocity_application_mode_allowed_for_step88": "solid_vel_experimental",
  "wall_velocity_application_config_path_allowed_for_step88": "configs/step36_wall_velocity_application_solid_vel_experimental.json",
  "wall_velocity_application_report_required_for_step88": true,
  "target_lbm_field_planned_for_step88": "solid_vel",
  "combined_runtime_geometry_wall_velocity_planned_for_step88": true,
  "planned_step88_activation_feature_count": 3,
  "step87_activation_feature_count": 0,
  "apply_to_lbm_solid_vel_allowed": true,
  "apply_to_lbm_populations_allowed": false,
  "apply_to_mpm_allowed": false,
  "apply_to_projector_allowed": false,
  "modify_bounceback_formula_allowed": false,
  "jet_model_allowed": false,
  "actuation_claim_allowed": false,
  "real_geometry_allowed": false,
  "real_geometry_candidate_data_allowed": false,
  "link_area_allowed": false,
  "grid_48_allowed": false,
  "grid_64_allowed": false,
  "vtr_output_allowed": false,
  "particle_npy_output_allowed": false,
  "runtime_code_changed": false,
  "solver_behavior_changed": false,
  "solver_formula_change_allowed": false,
  "tau_migration_allowed": false,
  "physical_validation_claim_allowed": false,
  "production_readiness_claim_allowed": false,
  "real_squid_validation_claim_allowed": false,
  "squid_swimming_claim_allowed": false,
  "squid_actuation_claim_allowed": false
}
```

## Required Activation Guard Policy

Add `configs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_guard_policy.json`.
It must check:

- `driver_run_required = false`
- `fsidriver_run_allowed = false`
- `simulation_run_allowed = false`
- `step87_activation_feature_count = 0`
- `planned_step88_activation_feature_count = 3`
- `squid_proxy_planned_for_step88 = true`
- `geometry_type_allowed_for_step88 = squid_proxy`
- `geometry_config_path_allowed_for_step88 = configs/step85_squid_proxy_geometry_1024.json`
- `geometry_quality_report_required_for_step88 = true`
- `runtime_geometry_planned_for_step88 = true`
- `geometry_motion_application_mode_allowed_for_step88 = diagnostic_only`
- `geometry_mutation_allowed = false`
- `wall_velocity_planned_for_step88 = true`
- `wall_velocity_application_mode_allowed_for_step88 = solid_vel_experimental`
- `target_lbm_field_planned_for_step88 = solid_vel`
- `apply_to_lbm_solid_vel_allowed = true`
- `apply_to_lbm_populations_allowed = false`
- `apply_to_mpm_allowed = false`
- `apply_to_projector_allowed = false`
- `modify_bounceback_formula_allowed = false`
- `combined_runtime_geometry_wall_velocity_planned_for_step88 = true`
- `real_geometry_allowed = false`
- `real_geometry_candidate_data_allowed = false`
- `link_area_allowed = false`
- `grid_48_allowed = false`
- `grid_64_allowed = false`
- `vtr_output_allowed = false`
- `particle_npy_output_allowed = false`
- `physical_validation_claim_allowed = false`
- `production_readiness_claim_allowed = false`
- `real_squid_validation_claim_allowed = false`
- `squid_swimming_claim_allowed = false`

## Required Plan Evidence Output

The activation plan runner must write:

- `outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan/runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan.json`
- `outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan/runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan.csv`
- `outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan/runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_summary.csv`

The plan summary must include:

```text
step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_pass = true
previous_step = Step86
previous_commit = e69e11971728a370465e54f753988d2b9ab228b5
driver_run_required = false
fsidriver_run_allowed = false
simulation_run_allowed = false
squid_proxy_planned_for_step88 = true
geometry_type_allowed_for_step88 = squid_proxy
geometry_config_path_allowed_for_step88 = configs/step85_squid_proxy_geometry_1024.json
runtime_geometry_planned_for_step88 = true
geometry_motion_application_mode_allowed_for_step88 = diagnostic_only
geometry_mutation_allowed = false
wall_velocity_planned_for_step88 = true
wall_velocity_application_mode_allowed_for_step88 = solid_vel_experimental
target_lbm_field_planned_for_step88 = solid_vel
combined_runtime_geometry_wall_velocity_planned_for_step88 = true
step87_activation_feature_count = 0
planned_step88_activation_feature_count = 3
real_geometry_allowed = false
real_geometry_candidate_data_allowed = false
link_area_allowed = false
grid_48_allowed = false
grid_64_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
step88_allowed = true
step88_allowed_row_name = canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

## Required Activation Guard Evidence Output

The activation guard runner must write:

- `outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard/runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard.json`
- `outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard/runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard.csv`
- `outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard/runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard_summary.csv`

The guard summary must include:

```text
step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard_pass = true
guard_row_count > 0
guard_pass_count = guard_row_count
step87_activation_feature_count = 0
planned_step88_activation_feature_count = 3
squid_proxy_planned_for_step88 = true
geometry_type_planned_for_step88 = squid_proxy
geometry_quality_report_required_for_step88 = true
runtime_geometry_planned_for_step88 = true
runtime_geometry_application_mode_planned_for_step88 = diagnostic_only
geometry_mutation_allowed = false
wall_velocity_planned_for_step88 = true
wall_velocity_application_mode_planned_for_step88 = solid_vel_experimental
apply_to_lbm_solid_vel_planned_for_step88 = true
apply_to_lbm_populations_planned_for_step88 = false
modify_bounceback_formula_planned_for_step88 = false
combined_runtime_geometry_wall_velocity_planned_for_step88 = true
real_geometry_planned_for_step88 = false
real_geometry_candidate_data_planned_for_step88 = false
link_area_planned_for_step88 = false
write_vtk_planned_for_step88 = false
write_particles_planned_for_step88 = false
```

## Required Regression Guards

Step87 must add regression guards for Step86, Step84, Step82, and Step80.

### Step86 Regression Guard

Outputs:

- `outputs/step87_step86_regression_guard/step86_regression_guard.json`
- `outputs/step87_step86_regression_guard/step86_regression_guard.csv`
- `outputs/step87_step86_regression_guard/step86_regression_guard_summary.csv`

Required checks:

```text
step86_squid_proxy_static_geometry_smoke_matrix_pass = true
step86_squid_proxy_static_geometry_quality_pass = true
step86_activation_guard_pass = true
step86_output_guard_pass = true
step86_step85_regression_guard_pass = true
step86_step84_regression_guard_pass = true
step86_step31_reference_guard_pass = true
step86_artifact_budget_pass = true
step86_activation_feature_count = 1
step86_squid_proxy_enabled_count = 1
step86_procedural_geometry_enabled_count = 1
step86_real_geometry_candidate_enabled_count = 0
step86_runtime_geometry_enabled_count = 0
step86_wall_velocity_enabled_count = 0
step86_combined_runtime_geometry_wall_velocity_enabled_count = 0
step86_vtr_count = 0
step86_particle_npy_count = 0
```

### Step84 Regression Guard

Outputs:

- `outputs/step87_step84_regression_guard/step84_regression_guard.json`
- `outputs/step87_step84_regression_guard/step84_regression_guard.csv`
- `outputs/step87_step84_regression_guard/step84_regression_guard_summary.csv`

Required checks:

```text
step84_runtime_geometry_wall_velocity_combined_smoke_matrix_pass = true
step84_runtime_geometry_wall_velocity_combined_quality_pass = true
step84_activation_guard_pass = true
step84_output_guard_pass = true
step84_artifact_budget_pass = true
step84_activation_feature_count = 2
step84_runtime_geometry_enabled_count = 1
step84_wall_velocity_enabled_count = 1
step84_combined_runtime_geometry_wall_velocity_enabled_count = 1
step84_squid_proxy_enabled_count = 0
step84_vtr_count = 0
step84_particle_npy_count = 0
```

### Step82 Regression Guard

Outputs:

- `outputs/step87_step82_regression_guard/step82_regression_guard.json`
- `outputs/step87_step82_regression_guard/step82_regression_guard.csv`
- `outputs/step87_step82_regression_guard/step82_regression_guard_summary.csv`

Required checks:

```text
step82_wall_velocity_solid_vel_smoke_matrix_pass = true
step82_wall_velocity_solid_vel_quality_pass = true
step82_activation_guard_pass = true
step82_output_guard_pass = true
step82_artifact_budget_pass = true
step82_activation_feature_count = 1
step82_wall_velocity_enabled_count = 1
step82_runtime_geometry_enabled_count = 0
step82_squid_proxy_enabled_count = 0
step82_vtr_count = 0
step82_particle_npy_count = 0
```

### Step80 Regression Guard

Outputs:

- `outputs/step87_step80_regression_guard/step80_regression_guard.json`
- `outputs/step87_step80_regression_guard/step80_regression_guard.csv`
- `outputs/step87_step80_regression_guard/step80_regression_guard_summary.csv`

Required checks:

```text
step80_runtime_geometry_diagnostic_only_smoke_matrix_pass = true
step80_runtime_geometry_diagnostic_only_quality_pass = true
step80_activation_guard_pass = true
step80_output_guard_pass = true
step80_artifact_budget_pass = true
step80_activation_feature_count = 1
step80_runtime_geometry_enabled_count = 1
step80_wall_velocity_enabled_count = 0
step80_squid_proxy_enabled_count = 0
step80_vtr_count = 0
step80_particle_npy_count = 0
```

## Required Output Guard

The Step87 output guard must write:

- `outputs/step87_output_guard/output_guard.json`
- `outputs/step87_output_guard/output_guard.csv`
- `outputs/step87_output_guard/output_guard_summary.csv`

It must prove:

```text
output_guard_pass = true
step87_driver_run_dir_count = 0
step87_vtr_count = 0
step87_particle_npy_count = 0
step87_raw_geometry_output_count = 0
step87_real_geometry_candidate_output_count = 0
step87_dense_wall_velocity_output_count = 0
step87_sparse_wall_velocity_output_count = 0
step87_dense_displacement_output_count = 0
step87_displaced_particle_output_count = 0
private_absolute_path_count = 0
protected_sim_edit_count = 0
protected_diagnostics_edit_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step87_large_file_count = 0
```

## Required Artifact Manifest

The artifact manifest must write:

- `outputs/step87_artifact_manifest/artifact_manifest.csv`
- `outputs/step87_artifact_manifest/artifact_summary.csv`
- `outputs/step87_artifact_manifest/artifact_summary.json`

The summary must prove:

```text
artifact_budget_pass = true
step87_file_count <= 70
step87_total_size_mb < 5
step87_driver_run_dir_count = 0
step87_vtr_count = 0
step87_particle_npy_count = 0
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step87_file_count = 0
protected_real_geometry_candidates_step87_file_count = 0
raw_geometry_file_count = 0
```

The manifest must be refreshed after final pytest logs are produced.

## Required Tests

Add contract tests for:

- combined activation plan;
- combined activation guard;
- Step86 regression guard;
- Step84 regression guard;
- Step82 regression guard;
- Step80 regression guard;
- output guard.

The tests should read committed Step87 output artifacts and assert the summary
fields listed in this goal. Keep tests lightweight and avoid importing heavy
runtime packages when artifact checks are sufficient.

## Required Verification Commands

Run these baseline runners with the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step87_step86_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step87_step84_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step87_step82_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step87_step80_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step87_output_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step87_artifact_manifest.py
```

Run focused Step87 tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q tests\test_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_contract.py tests\test_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard_contract.py tests\test_step87_step86_regression_contract.py tests\test_step87_step84_regression_contract.py tests\test_step87_step82_regression_contract.py tests\test_step87_step80_regression_contract.py tests\test_step87_output_guard_contract.py
```

Run full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Run git checks:

```powershell
git diff --check
git diff --cached --check
git status --short -- src\mpm_lbm\sim src\mpm_lbm\diagnostics external\taichi_LBM3D data\real_geometry_candidates
```

## Required Report Conclusion

The Step87 report must conclude:

```text
Step87 accepted.

Step87 is a plan-and-guard step only.
Step87 does not run FSIDriver3D.
Step87 does not call driver.run().
Step87 does not execute simulation.
Step87 does not activate the three-feature combined row.

Step87 only plans and guards Step88:
canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke

Step88 may run exactly one 32^3 / 1024-particle / 3-step /
moving_boundary / engineering row with:
geometry_type = squid_proxy
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental

Step88 must not enable real geometry candidate data.
Step88 must not enable link-area transfer.
Step88 must not enable 48^3 or 64^3.
Step88 must not write VTR or particle NPY.
Step88 must not change solver formulas.
Step88 must not claim physical validation, squid swimming, real squid validation, or production readiness.
```

## Commit And Push

After implementation and verification, commit with exactly:

```text
test: add step87 runtime geometry wall velocity squid proxy combined activation plan and guard
```

Then push to `origin/main` and report the final commit hash and remote branch.
