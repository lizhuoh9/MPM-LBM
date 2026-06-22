# Step72 Runtime Geometry Activation Readiness Audit Goal

## Repository Baseline

- Repository: `lizhuoh9/MPM-LBM`
- Local workspace: `D:\working\squid robot\LBM\MPM-LBM`
- Branch: `main`
- Required upstream baseline: Step71 commit `0825da645bb020ebfabca231b75dc5c6cfa39ced`
- Step71 accepted scope:
  - `FSIDriverConfig.write_vtk` defaults to `False`.
  - `FSIDriverConfig.write_particles` defaults to `False`.
  - LBM tau convention remains legacy helper semantics, with the Step71 decision documented.
  - Step71 did not run or activate solver physics, wall velocity, runtime geometry, VTR, particle dumps, or real geometry.

## Step Name

`Step72 Runtime Geometry Activation Readiness Audit`

## Objective

Add a bounded, evidence-backed readiness audit for the runtime geometry activation surface. Step72 must prove that the existing runtime geometry projection/config/guard surfaces are importable, schema-stable, closed by default, protected by driver gates, protected by state guards, compatible with the Step70 activation freeze, compatible with Step71 output defaults, and still non-simulating.

This step is an audit and documentation step only. It must not enable or partially enable runtime moving-geometry coupling.

## Required Deliverables

### Top-level goal and report

- `STEP72_RUNTIME_GEOMETRY_ACTIVATION_READINESS_AUDIT_GOAL.md`
- `STEP72_RUNTIME_GEOMETRY_ACTIVATION_READINESS_AUDIT_REPORT.md`

### Documentation

- `docs/72_runtime_geometry_activation_readiness_audit.md`
- `docs/RUNTIME_GEOMETRY_ACTIVATION_READINESS.md`
- Update `docs/ACTIVATION_PRECONDITIONS.md` with Step72 readiness status while keeping activation gates closed.
- Update `docs/00_project_status.md` and `README.md` with a concise Step72 status note.

### Policies

Add Step72 JSON policy files under `configs/` for:

- Runtime geometry readiness aggregation.
- Canonical runtime geometry API surface.
- Runtime geometry config schema and safe defaults.
- FSI driver runtime geometry gate behavior.
- Runtime geometry state guard behavior.
- Runtime geometry output artifact safety.
- Step72 no-simulation enforcement.
- Step71 regression guard.

### Evidence builders

Add Step72 evidence modules under `src/mpm_lbm/evidence/` for:

- Canonical import/API readiness.
- Config schema stability and safe mutation/persistence defaults.
- Driver gate default-closed and invalid-combination rejection behavior.
- State guard readiness for transient runtime projection.
- Output artifact policy readiness.
- Aggregated runtime geometry activation readiness.
- No-simulation enforcement.
- Step71 regression guard.

### Runners and artifacts

Add baseline runners under `baseline_tests/` and generate committed artifacts under `outputs/` and `logs/` for every Step72 audit. Required output directories:

- `outputs/step72_runtime_geometry_api_audit/`
- `outputs/step72_runtime_geometry_config_schema_audit/`
- `outputs/step72_runtime_geometry_driver_gate_audit/`
- `outputs/step72_runtime_geometry_state_guard_audit/`
- `outputs/step72_runtime_geometry_output_policy_audit/`
- `outputs/step72_runtime_geometry_readiness_audit/`
- `outputs/step72_no_simulation_audit/`
- `outputs/step72_step71_regression_guard/`
- `outputs/step72_artifact_manifest/`

Each audit should write CSV, JSON, summary CSV, and a log marker. The artifact manifest must be self-excluding so rerunning it does not oscillate on its own output directory.

### Tests

Add focused contract tests under `tests/` for:

- Runtime geometry API audit.
- Runtime geometry config schema audit.
- Runtime geometry driver gate audit.
- Runtime geometry state guard audit.
- Runtime geometry output policy audit.
- Aggregated readiness audit.
- Step72 no-simulation audit.
- Step72 Step71 regression guard and artifact manifest.

## Positive Acceptance Criteria

Step72 is complete only if all of the following are true:

1. Canonical runtime geometry modules import without constructing `FSIDriver3D`.
2. Required runtime geometry symbols remain present:
   - `RuntimeGeometryProjectionIntegrationConfig`
   - `validate_runtime_geometry_projection_config`
   - `summarize_runtime_geometry_projection_config_validation`
   - `mutation_flags`
   - `mutation_flag_enabled_count`
   - `compute_runtime_projection_rows`
   - `compute_original_projection_rows`
   - `project_transient_geometry_copy`
   - `summarize_runtime_projection_rows`
   - `analyze_runtime_projection_quality`
   - `compare_original_vs_runtime_projection`
   - `summarize_original_vs_runtime_projection`
   - `compute_runtime_projection_state_guard`
   - `write_runtime_projection_state_guard`
3. `RuntimeGeometryProjectionIntegrationConfig` schema still matches the Step70 frozen schema row.
4. Every mutation, persistence, production link, VTR, dense displacement, and displaced particle flag in the runtime geometry projection config defaults to `False`.
5. `diagnostic_only` defaults to `True` and `deterministic` defaults to `True`.
6. `configs/step45_runtime_geometry_projection_integration.json` remains diagnostic-only and no-mutation.
7. `FSIDriverConfig` runtime geometry gates are closed by default:
   - `geometry_motion_mode == "static"`
   - `geometry_motion_config_path is None`
   - `geometry_motion_report_enabled is False`
   - `geometry_motion_application_mode == "disabled"`
   - `geometry_motion_application_config_path is None`
   - `geometry_motion_application_report_enabled is False`
8. Invalid runtime geometry driver combinations are rejected by config validation.
9. Step70 activation preconditions remain closed, including runtime geometry activation.
10. Step71 output default safety remains green:
    - default `write_vtk` is `False`
    - default `write_particles` is `False`
    - explicit opt-in remains allowed
11. Step72 does not add VTR output, particle NPY output, dense displacement fields, driver-run output directories, protected external edits, or real-geometry candidate edits.
12. Step72 artifacts remain small enough for commit and are covered by an artifact manifest.
13. Focused Step72 tests pass.
14. Full test suite passes, or any failure is clearly unrelated and documented with exact command output.

## Negative Constraints

Step72 must not:

- Run `FSIDriver3D.initialize()`, `FSIDriver3D.step_once()`, `FSIDriver3D.run()`, or an equivalent driver loop.
- Activate runtime geometry in the solver.
- Activate wall velocity or combine wall velocity with runtime geometry.
- Activate real geometry, squid simulation, or production moving-boundary coupling.
- Generate or commit `.vtr` files.
- Generate or commit particle `.npy` files.
- Generate or commit dense displacement fields.
- Edit `external/taichi_LBM3D/`.
- Edit `data/real_geometry_candidates/`.
- Change LBM formulas, tau formulas, bounceback formulas, force transfer formulas, MPM formulas, pressure handling, or numerical update order.
- Replace Step71 tau convention behavior.
- Claim physical validation, solver completion, production readiness, squid swimming, jet correctness, or real-geometry validation.

## Verification Commands

Use the trusted Taichi Python interpreter for meaningful validation:

```powershell
D:\working\taichi\env\python.exe -m py_compile <new Step72 Python files>
D:\working\taichi\env\python.exe -m pytest <focused Step72 tests> -q
D:\working\taichi\env\python.exe -m pytest -q
```

If the full suite is run with another interpreter for comparison, record the exact interpreter and result separately. The final acceptance should prefer `D:\working\taichi\env\python.exe`.

## Commit and Push

After implementation, evidence generation, and verification are complete:

- Commit message: `test: add step72 runtime geometry activation readiness audit`
- Push target: `origin main`
- Final report must include the final commit hash and pushed branch.
