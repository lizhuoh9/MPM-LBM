# Step73 Wall Velocity Activation Readiness Audit Goal

## Repository Baseline

- Repository: `lizhuoh9/MPM-LBM`
- Local workspace: `D:\working\squid robot\LBM\MPM-LBM`
- Branch: `main`
- Required upstream baseline: Step72 commit `2efdd5f423556b7ce5573e1652793e85b391f397`
- Step72 accepted scope:
  - Runtime geometry readiness audit passed.
  - Runtime geometry activation remains closed.
  - Wall velocity activation remains closed.
  - Combined runtime geometry plus wall velocity activation remains closed.
  - No `FSIDriver3D` run, initialize, or step was performed by Step72.
  - No VTR, particle NPY, dense displacement, protected external edit, or real-geometry candidate edit was introduced.

## Step Name

`Step73 Wall Velocity Activation Readiness Audit`

## Objective

Add a bounded, evidence-backed wall velocity activation readiness audit. Step73
must prove that the canonical wall velocity modules are importable, the wall
velocity config schemas remain stable against the Step70 schema freeze, driver
wall-velocity gates remain closed by default, opt-in application safety remains
restricted to `lbm.solid_vel`, output policy remains clean, all Step70 activation
gates remain closed, Step72 evidence remains green, and no simulation is run.

Step73 is an audit and documentation step only. It must not activate wall
velocity, runtime geometry, combined runtime geometry plus wall velocity, real
geometry, squid simulation, larger-grid simulation, or production coupling.

## Required Deliverables

### Top-level goal and report

- `STEP73_WALL_VELOCITY_ACTIVATION_READINESS_AUDIT_GOAL.md`
- `STEP73_WALL_VELOCITY_ACTIVATION_READINESS_AUDIT_REPORT.md`

### Documentation

- `docs/73_wall_velocity_activation_readiness_audit.md`
- `docs/WALL_VELOCITY_ACTIVATION_READINESS.md`
- Update `docs/ACTIVATION_PRECONDITIONS.md` with Step73 readiness status while keeping all activation gates closed.
- Update `docs/00_project_status.md` and `README.md` with a concise Step73 status note.

### Policies

Add Step73 JSON policy files under `configs/`:

- `configs/step73_wall_velocity_readiness_policy.json`
- `configs/step73_wall_velocity_api_policy.json`
- `configs/step73_wall_velocity_config_schema_policy.json`
- `configs/step73_wall_velocity_driver_gate_policy.json`
- `configs/step73_wall_velocity_application_safety_policy.json`
- `configs/step73_wall_velocity_output_policy.json`
- `configs/step73_full_activation_gate_coverage_policy.json`
- `configs/step73_no_simulation_policy.json`
- `configs/step73_step72_regression_policy.json`

### Evidence builders

Add Step73 evidence modules under `src/mpm_lbm/evidence/`:

- `wall_velocity_readiness_audit.py`
- `wall_velocity_api_audit.py`
- `wall_velocity_config_schema_audit.py`
- `wall_velocity_driver_gate_audit.py`
- `wall_velocity_application_safety_audit.py`
- `wall_velocity_output_policy_audit.py`
- `full_activation_gate_coverage_audit.py`
- `step73_no_simulation_audit.py`
- `step73_regression_guard.py`

### Runners and artifacts

Add baseline runners under `baseline_tests/`:

- `baseline_tests/step73_common.py`
- `baseline_tests/run_step73_wall_velocity_readiness_audit.py`
- `baseline_tests/run_step73_wall_velocity_api_audit.py`
- `baseline_tests/run_step73_wall_velocity_config_schema_audit.py`
- `baseline_tests/run_step73_wall_velocity_driver_gate_audit.py`
- `baseline_tests/run_step73_wall_velocity_application_safety_audit.py`
- `baseline_tests/run_step73_wall_velocity_output_policy_audit.py`
- `baseline_tests/run_step73_full_activation_gate_coverage_audit.py`
- `baseline_tests/run_step73_no_simulation_audit.py`
- `baseline_tests/run_step73_step72_regression_guard.py`
- `baseline_tests/run_step73_artifact_manifest.py`

Generate committed artifacts and logs under:

- `outputs/step73_wall_velocity_readiness_audit/`
- `outputs/step73_wall_velocity_api_audit/`
- `outputs/step73_wall_velocity_config_schema_audit/`
- `outputs/step73_wall_velocity_driver_gate_audit/`
- `outputs/step73_wall_velocity_application_safety_audit/`
- `outputs/step73_wall_velocity_output_policy_audit/`
- `outputs/step73_full_activation_gate_coverage_audit/`
- `outputs/step73_no_simulation_audit/`
- `outputs/step73_step72_regression_guard/`
- `outputs/step73_artifact_manifest/`
- `logs/step73_*.log`

Every audit runner should emit CSV, JSON, summary CSV, and a log marker. The
artifact manifest must exclude its own output directory so reruns do not
oscillate on manifest content.

### Tests

Add focused contract tests:

- `tests/test_step73_wall_velocity_readiness_contract.py`
- `tests/test_step73_wall_velocity_api_contract.py`
- `tests/test_step73_wall_velocity_config_schema_contract.py`
- `tests/test_step73_wall_velocity_driver_gate_contract.py`
- `tests/test_step73_wall_velocity_application_safety_contract.py`
- `tests/test_step73_wall_velocity_output_policy_contract.py`
- `tests/test_step73_full_activation_gate_coverage_contract.py`
- `tests/test_step73_no_simulation_contract.py`
- `tests/test_step73_step72_regression_contract.py`

## Canonical Wall Velocity Surfaces To Check

The API audit must check canonical modules and required public symbols:

- `src.mpm_lbm.sim.wall_velocity.config`
  - `WallVelocityFieldConfig`
  - `validate_wall_velocity_config`
  - `assert_valid_wall_velocity_config`
  - `STEP35_EXECUTION_FLAG_FIELDS`
- `src.mpm_lbm.sim.wall_velocity.application_config`
  - `WallVelocityApplicationConfig`
  - `validate_wall_velocity_application_config`
  - `assert_valid_wall_velocity_application_config`
  - `APPLICATION_FLAG_FIELDS`
- `src.mpm_lbm.sim.wall_velocity.field`
  - `load_wall_velocity_inputs`
  - `interpolate_motion_rows_to_phase`
  - `compute_wall_velocity_summary`
  - `generate_wall_velocity_field_rows`
  - `summarize_wall_velocity_rows`
- `src.mpm_lbm.sim.wall_velocity.application`
  - `load_wall_velocity_application_config`
  - `build_wall_velocity_grid`
  - `summarize_wall_velocity_application`
  - `build_wall_velocity_application_report`
  - `apply_wall_velocity_application_to_lbm`
- `src.mpm_lbm.sim.wall_velocity.application_envelope`
  - `collect_wall_velocity_application_reports`
  - `summarize_application_envelope`
- `src.mpm_lbm.sim.wall_velocity.consistency`
  - `compare_wall_velocity_to_motion_mapping`
- `src.mpm_lbm.sim.wall_velocity.quality`
  - `analyze_wall_velocity_quality`

Imports must not construct `FSIDriver3D`, run the solver, or write outputs.

## Positive Acceptance Criteria

Step73 is complete only if all criteria are true:

1. Goal, report, docs, policies, evidence builders, runners, tests, logs, and artifacts exist.
2. Wall velocity API audit passes:
   - canonical imports pass;
   - all required symbols are present;
   - `solver_run = false`;
   - `output_snapshot_unchanged = true`.
3. Wall velocity config schema audit passes:
   - `WallVelocityFieldConfig` schema hash matches Step70 freeze;
   - `WallVelocityApplicationConfig` schema hash matches Step70 freeze;
   - `from_json` availability remains true for both;
   - `to_dict` availability remains true for both;
   - `missing_required_field_count = 0`.
4. `WallVelocityFieldConfig` unsafe execution defaults remain false:
   - `write_dense_field`;
   - `write_sparse_samples`;
   - `apply_to_lbm`;
   - `lbm_population_update_enabled`;
   - `moving_bounceback_update_enabled`;
   - `driver_integration_enabled`;
   - `jet_model_enabled`;
   - `actuation_enabled`.
5. `WallVelocityApplicationConfig` application safety defaults remain:
   - `apply_to_lbm_solid_vel = true`;
   - `apply_to_lbm_populations = false`;
   - `apply_to_mpm = false`;
   - `apply_to_projector = false`;
   - `modify_bounceback_formula = false`;
   - `jet_model_enabled = false`;
   - `actuation_claim_enabled = false`;
   - `diagnostic_report_enabled = true`.
6. Driver gate audit passes:
   - default `FSIDriverConfig.wall_velocity_application_mode == "disabled"`;
   - default `wall_velocity_application_config_path is None`;
   - default `wall_velocity_application_report_enabled is False`;
   - default `boundary_motion_mode == "static"`;
   - default `boundary_motion_config_path is None`;
   - default `write_vtk is False`;
   - default `write_particles is False`;
   - invalid wall velocity activation combinations are rejected;
   - no driver is constructed, initialized, stepped, or run.
7. Application safety audit passes:
   - LBM population update is forbidden;
   - MPM update is forbidden;
   - projector update is forbidden;
   - bounce-back formula modification is forbidden;
   - jet model claims are forbidden;
   - actuation claims are forbidden;
   - the committed opt-in application config remains limited to `solid_vel`.
8. Output policy audit passes:
   - no `outputs/step73_driver_runs`;
   - no `.vtr` files;
   - no particle `.npy` files;
   - no dense wall velocity field output;
   - no sparse wall velocity sample output;
   - no private absolute paths;
   - no protected `external/taichi_LBM3D/` edits;
   - no protected `data/real_geometry_candidates/` edits.
9. Full activation gate coverage audit passes:
   - all 10 Step70 activation gates are checked;
   - `required_gate_count = 10`;
   - `closed_gate_count = 10`;
   - `activation_allowed_count = 0`.
10. No-simulation audit passes:
    - no `driver.run`;
    - no `FSIDriver3D(...).run`;
    - no `driver.initialize`;
    - no `driver.step_once`;
    - no forbidden Step73 output directory.
11. Step72 regression guard passes:
    - Step72 runtime geometry readiness remains green;
    - Step72 API/config schema/driver gate/state guard/output policy/no-simulation/regression artifacts remain green;
    - Step72 artifact manifest remains green;
    - runtime geometry, wall velocity, and combined activation gates remain false.
12. Validation passes with the trusted interpreter:
    - Step73 Python files compile;
    - focused Step73 pytest passes;
    - full pytest passes under `D:\working\taichi\env\python.exe`;
    - full pytest is attempted under `D:\TOOL\Anaconda\python.exe` when available;
    - pre-push hook passes.
13. Git checks pass:
    - `git diff --check`;
    - `git diff --cached --check`;
    - protected directories remain clean.

## Negative Constraints

Step73 must not:

- Run `driver.run()`.
- Run `FSIDriver3D(...).run()`.
- Run `driver.initialize()`.
- Run `driver.step_once()`.
- Create `outputs/step73_driver_runs`.
- Activate wall velocity.
- Activate runtime geometry.
- Activate combined runtime geometry plus wall velocity.
- Run real geometry.
- Run squid simulation.
- Run 48^3 or 64^3 simulations.
- Write VTR output.
- Write particle NPY output.
- Write dense wall velocity field output.
- Write sparse wall velocity samples.
- Update LBM populations.
- Modify moving bounce-back formulas.
- Mutate MPM state.
- Mutate projector state.
- Migrate tau convention.
- Change solver formulas.
- Claim physics validation, jet propulsion validation, grid convergence, solver completion, or production readiness.
- Edit `external/taichi_LBM3D/`.
- Edit `data/real_geometry_candidates/`.

Allowed activities:

- canonical import checks;
- config schema checks;
- constructor-only invalid-combination checks;
- source-level guard checks;
- committed config validation;
- existing artifact regression checks;
- activation-policy checks;
- no-output and no-simulation checks.

## Verification Commands

Use the trusted Taichi Python interpreter for authoritative validation:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile <new Step73 Python files>
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest <focused Step73 tests> -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
```

Also attempt the Anaconda full suite if available:

```powershell
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Commit and push only after verification:

```powershell
git diff --check
git diff --cached --check
git commit -m "test: add step73 wall velocity activation readiness audit"
git push origin main
```

## Commit and Push

- Commit message: `test: add step73 wall velocity activation readiness audit`
- Push target: `origin main`
- Final report must include final commit hash, remote branch, validation results, and artifact manifest summary.
