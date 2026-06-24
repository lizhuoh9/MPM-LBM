# Step103 Goal: Fluent-Inspired Duct-Flap Proxy Solver Comparison Smoke

## Source Of Truth

This document is the detailed implementation contract for Step103. The active Codex goal should reference this file instead of inlining the full text, because the goal text length is limited.

User-provided GitHub baseline:

- `origin/main = 13ce2bf6ce2198e7dce5aa0b217b2dd715acde3d`
- Step102 is accepted.
- The next step is Step103, not the original Step101 48^3 / 10-step GGUI route.

Expected final commit message:

```text
test: add step103 fluent-inspired duct-flap proxy solver comparison smoke
```

## One-Sentence Objective

Implement and run `Step103 Fluent-Inspired Duct-Flap Proxy Solver Comparison Smoke`: a real 48-grid, 1024-particle, 5-step MPM-LBM solver smoke run that uses a procedural duct-flap proxy inspired by the public Fluent 2-way FSI tutorial, emits solver-gap comparison artifacts, and explicitly refuses validation/equivalence claims.

## Allowed Claim

The only accepted result claim is:

```text
Fluent-inspired duct-flap proxy comparison smoke ran and produced a solver gap report.
```

## Forbidden Claims

Do not claim any of the following:

- The current solver matches Fluent.
- The current solver is validated against Fluent.
- Physical validation is complete.
- Real FSI validation is complete.
- The workflow is production ready.

## Step Identity

Required canonical row name:

```text
fluent_inspired_duct_flap_proxy_48_5step_ggui_comparison_smoke
```

Required driver module:

```text
src.mpm_lbm.sim.drivers.fsi_driver
```

Required geometry type:

```text
duct_flap_proxy
```

## Required Solver Run Configuration

The run must be a real solver run, not plan-only:

- `n_grid = 48`
- `n_particles = 1024`
- `n_lbm_steps = 5`
- `mpm_substeps_per_lbm_step = 1`
- `coupling_mode = moving_boundary`
- `reaction_transfer_mode = engineering`
- `geometry_type = duct_flap_proxy`
- `geometry_config_path = configs/step103_fluent_inspired_duct_flap_proxy_geometry_1024.json`
- `target_u_lbm = [0.02, 0.0, 0.0]`
- `geometry_motion_mode = prescribed_kinematic`
- `geometry_motion_application_mode = diagnostic_only`
- `wall_velocity_application_mode = solid_vel_experimental`
- `target_lbm_field = solid_vel`
- `ggui_visualization_enabled = true`
- `ggui_screenshot_enabled = true`
- `ggui_video_enabled = false`
- `write_vtk = false`
- `write_particles = false`
- `output_interval = 1`

## Fluent Reference Boundary

The public Fluent 2-way FSI tutorial can be cited as inspiration, but no official Fluent files may be imported, copied, committed, or used as runtime input.

Forbidden official/proprietary runtime inputs include, but are not limited to:

- `fsi_2way.zip`
- `flap.msh`
- `steady_fluid_flow.jou`
- `flap_fsi_2way.cas.h5`
- `flap_fsi_2way.dat.h5`

The optional local reference CSV path is:

```text
benchmarks/private/fluent_fsi_2way/reference/fluent_structural_point_flap_displacement.csv
```

This path must remain private and ignored by Git. The harness must support both modes:

- CSV exists locally: load it, validate schema, and emit local comparison metadata.
- CSV is missing: emit committed reports with `fluent_reference_available = false` and capability-gap fields.

## Required Solver-Limitation Disclosures

All comparison reports must make these limitations explicit:

- Official Fluent case dimensionality is 2D; current solver dimensionality is 3D.
- Official Fluent uses conformal fluid-solid mesh; current solver uses procedural voxel/particle proxy geometry.
- Official Fluent uses intrinsic FSI with linear elasticity; current solver does not reproduce the exact structural model.
- Official Fluent has dynamic mesh deformation; current runtime geometry mutation path remains diagnostic-only/no-op.
- Official monitor quantity is flap displacement; current solver may not expose a physically equivalent flap-tip displacement.
- Official inlet velocity is dimensional `10 m/s`; current LBM target velocity is nondimensional/mapped.
- Exact quantitative equivalence is not allowed.

## Narrow Runtime Change Envelope

Allowed source changes are limited to:

- Procedural `duct_flap_proxy` geometry generation.
- Geometry registry/config parser support for `geometry_type = duct_flap_proxy`.
- Geometry quality report support.
- Proxy sampling/proxy point generation.
- Step103 evidence runners, guards, comparison/report generation, tests, configs, docs, and artifacts.

Strictly forbidden source changes:

- LBM collision formula changes.
- LBM tau convention changes.
- MPM update formula changes.
- Coupling formula changes.
- Moving-boundary formula changes.
- Wall-velocity formula changes.
- Reaction-transfer formula changes.
- Solver stability hacks.
- Changes under `external/taichi_LBM3D/**`.
- Changes under `data/real_geometry_candidates/**`.

## Required Geometry Config

Create:

```text
configs/step103_fluent_inspired_duct_flap_proxy_geometry_1024.json
```

Required contents include normalized duct/flap geometry:

- duct:
  - `x = [0.0, 1.0]`
  - `y = [0.3, 0.7]`
  - `z = [0.45, 0.55]`
- flap:
  - `anchor_x = 0.505`
  - `anchor_y = 0.3`
  - `height_over_duct_height = 0.25`
  - `thickness_over_duct_height = 0.075`
  - `normalized_height = 0.10`
  - `normalized_thickness = 0.03`
  - `z = [0.45, 0.55]`
  - `fixed_base = true`
- material reference:
  - `density = 1600`
  - `youngs_modulus = 1e6`
  - `poisson_ratio = 0.47`
  - `used_for_exact_structural_model = false`
- quality:
  - `quality_check_enabled = true`
  - `strict = false`
  - `deterministic = true`

## Required Driver Config

Create:

```text
configs/step103_fluent_inspired_duct_flap_proxy_48_5step_ggui_comparison_smoke.json
```

The config must include boundary motion, moving-boundary coupling, diagnostic-only geometry motion, `solid_vel_experimental` wall velocity application, `solid_vel` target field, `target_u_lbm = [0.02, 0.0, 0.0]`, `48 / 1024 / 5`, output interval `1`, and disabled VTK/particle/video outputs.

## Required Policy Config Files

Create and use these policy/config files:

- `configs/step103_fluent_reference_csv_schema.json`
- `configs/step103_fluent_solver_comparison_policy.json`
- `configs/step103_acceptance_policy.json`
- `configs/step103_activation_guard_policy.json`
- `configs/step103_output_guard_policy.json`
- `configs/step103_step102_regression_policy.json`
- `configs/step103_step100_regression_policy.json`
- `configs/step103_artifact_manifest_policy.json`

## Required Source Files

Create:

- `src/mpm_lbm/sim/geometry/duct_flap_proxy.py`
- `src/mpm_lbm/evidence/step103_fluent_inspired_duct_flap_proxy_runner.py`
- `src/mpm_lbm/evidence/step103_fluent_reference_loader.py`
- `src/mpm_lbm/evidence/step103_fluent_solver_gap_comparison.py`
- `src/mpm_lbm/evidence/step103_activation_guard.py`
- `src/mpm_lbm/evidence/step103_output_guard.py`
- `src/mpm_lbm/evidence/step103_step102_regression_guard.py`
- `src/mpm_lbm/evidence/step103_step100_regression_guard.py`

## Required Baseline Runners

Create:

- `baseline_tests/step103_common.py`
- `baseline_tests/run_step103_fluent_inspired_duct_flap_proxy_smoke_matrix.py`
- `baseline_tests/run_step103_fluent_solver_gap_comparison.py`
- `baseline_tests/run_step103_activation_guard.py`
- `baseline_tests/run_step103_output_guard.py`
- `baseline_tests/run_step103_step102_regression_guard.py`
- `baseline_tests/run_step103_step100_regression_guard.py`
- `baseline_tests/run_step103_artifact_manifest.py`

## Required Tests

Create focused contract tests:

- `tests/test_step103_fluent_inspired_duct_flap_proxy_smoke_matrix_contract.py`
- `tests/test_step103_fluent_solver_gap_comparison_contract.py`
- `tests/test_step103_activation_guard_contract.py`
- `tests/test_step103_output_guard_contract.py`
- `tests/test_step103_step102_regression_contract.py`
- `tests/test_step103_step100_regression_contract.py`

## Required Docs And Reports

Create:

- `docs/103_fluent_inspired_duct_flap_proxy_solver_comparison_smoke.md`
- `STEP103_FLUENT_INSPIRED_DUCT_FLAP_PROXY_SOLVER_COMPARISON_SMOKE_REPORT.md`

The final report must include the allowed claim, the forbidden claim guard, solver run metadata, output manifest, guard results, and exact verification commands/results.

## Required Outputs And Logs

Produce and commit Step103 artifacts under:

- `outputs/step103_driver_runs/fluent_inspired_duct_flap_proxy_48_5step_ggui_comparison_smoke/`
- `outputs/step103_ggui_visualization/`
- `outputs/step103_fluent_comparison/`
- `outputs/step103_smoke_matrix/`
- `outputs/step103_activation_guard/`
- `outputs/step103_output_guard/`
- `outputs/step103_step102_regression_guard/`
- `outputs/step103_step100_regression_guard/`
- `outputs/step103_artifact_manifest/`
- `logs/step103_*.log`

Required comparison artifacts:

- `outputs/step103_fluent_comparison/fluent_solver_gap_report.json`
- `outputs/step103_fluent_comparison/fluent_solver_gap_report.csv`
- `outputs/step103_fluent_comparison/fluent_solver_gap_report.md`

## Required Comparison Report Fields

The JSON/CSV/MD gap report must include:

- `fluent_reference_available`
- `fluent_reference_row_count`
- `our_solver_run_stable`
- `our_solver_has_nan`
- `our_solver_has_inf`
- `official_case_dimensionality = 2D`
- `our_solver_dimensionality = 3D`
- `direct_quantitative_equivalence_allowed = false`
- `official_structural_model = linear_elasticity_intrinsic_fsi`
- `our_structural_model_equivalent = false`
- `official_dynamic_mesh = true`
- `our_geometry_mutation_enabled = false`
- `official_monitor_quantity = total_displacement`
- `our_equivalent_flap_tip_displacement_available = false` unless a genuinely equivalent monitor is implemented and documented
- `capability_gap_count > 0`
- `comparison_status = capability_gap_detected` when no real equivalent flap-tip displacement is available

## Acceptance Criteria

### Solver Run

- `driver_run_called = true`
- canonical driver module is `src.mpm_lbm.sim.drivers.fsi_driver`
- row name equals `fluent_inspired_duct_flap_proxy_48_5step_ggui_comparison_smoke`
- `geometry_type = duct_flap_proxy`
- `n_grid = 48`
- `n_particles = 1024`
- `n_lbm_steps = 5`
- completed steps equals `5`
- diagnostics row count is at least `6`
- `has_nan = false`
- `has_inf = false`
- stable is `true`

### Geometry

- `duct_flap_proxy_enabled = true`
- geometry quality report exists
- geometry quality report passes
- Fluent-inspired geometry ratios are recorded
- `official_mesh_imported = false`
- `official_fluent_files_used_as_runtime_input = false`

### Comparison And Gap Report

- Fluent source/inspiration is recorded
- Fluent CSV schema check is represented
- official case is recorded as `2D`
- current solver is recorded as `3D`
- direct quantitative equivalence is recorded as `false`
- validation is recorded as `false`
- `capability_gap_count >= 1`
- dynamic mesh equivalence gap is recorded
- linear elasticity equivalence gap is recorded
- flap-tip displacement equivalence gap is recorded as true unless a genuine equivalent monitor exists

### Output Guard

- official/proprietary file count is `0`
- `.vtr` count is `0`
- particle `.npy` count is `0`
- video count is `0`
- GGUI screenshot count is `1`
- protected external edits count is `0`
- protected real-geometry edits count is `0`

## Required Verification Commands

Run the Step103 baseline runners:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_fluent_inspired_duct_flap_proxy_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_fluent_solver_gap_comparison.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_activation_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_step102_regression_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_step100_regression_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests/run_step103_artifact_manifest.py
```

Run focused Step103 tests:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests/test_step103_fluent_inspired_duct_flap_proxy_smoke_matrix_contract.py `
  tests/test_step103_fluent_solver_gap_comparison_contract.py `
  tests/test_step103_activation_guard_contract.py `
  tests/test_step103_output_guard_contract.py `
  tests/test_step103_step102_regression_contract.py `
  tests/test_step103_step100_regression_contract.py
```

Run full tests with both local interpreters:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -m pytest -q
```

Run Git/pre-push checks:

```powershell
git diff --check
git diff --cached --check
git status --short benchmarks/private
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
git grep -n "fsi_2way.zip\|flap.msh\|steady_fluid_flow.jou\|flap_fsi_2way.cas.h5\|flap_fsi_2way.dat.h5"
```

The final `git grep` may only find policy/docs/tests that forbid or describe private inputs; it must not indicate that official Fluent file contents are committed or used as runtime inputs.

## Push Rule

After all implementation, artifacts, docs, tests, and guards pass, commit and push to `origin main`. Report the final commit hash and pushed branch. Mark the active goal complete only after the push succeeds.
