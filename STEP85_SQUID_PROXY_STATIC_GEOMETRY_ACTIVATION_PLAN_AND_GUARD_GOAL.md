# Step85 Squid Proxy Static Geometry Activation Plan And Guard Goal

## Source State

- Repository: `lizhuoh9/MPM-LBM`
- Branch: `main`
- Required starting commit: `29a130ccef93f095deeaa941b44003720f2291c5`
- Accepted predecessor: Step84 runtime-geometry plus wall-velocity combined canonical-driver smoke.
- Step85 status before this work: not started.

## Step85 Objective

Add a diagnostic-only planning and guard layer for the next safe single-feature activation:
`squid_proxy` static geometry in a 32^3, 1024-particle, 3-step canonical-driver smoke planned for Step86.

Step85 must not run the canonical driver and must not change solver/runtime behavior. It only records the Step86 allowed row,
adds planned-only geometry/config policies, validates the Step84 acceptance artifacts, validates the historical Step31 squid-proxy
static reference, and guards Step85 artifacts against accidental driver outputs or forbidden feature expansion.

## Hard Boundary

Step85 is plan-and-guard only.

- Do not instantiate `FSIDriver3D`.
- Do not call `driver.run()`.
- Do not execute a simulation.
- Do not edit runtime solver code.
- Do not change coupling, collision, bounce-back, tau, population update, geometry motion, wall velocity, diagnostics, or driver behavior.
- Do not introduce physical-validation, production-readiness, swimming, actuation, real-squid, or real-geometry claims.

## Protected Paths

No Step85 edit may touch these paths:

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

## Forbidden Feature Openings

Step85 must keep all of these closed:

- runtime geometry
- wall velocity
- combined runtime geometry plus wall velocity
- real geometry data candidates
- `link_area`
- 48^3 and 64^3 grids
- VTR output
- particle NPY output
- raw geometry output
- solver formula changes
- tau migration
- physical validation claims
- production readiness claims
- swimming or actuation claims

## Allowed Claim

The only positive claim Step85 may make is:

`squid_proxy static geometry single-feature smoke is planned and guarded for Step86`.

Step85 must not claim that the planned Step86 simulation has passed, that real squid geometry is validated, that swimming works,
or that the solver is production ready.

## Planned Step86 Row

Step85 must define exactly one planned Step86 row:

- row name: `canonical_driver_squid_proxy_static_geometry_32_3step_smoke`
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
- `write_vtk`: `false`
- `write_particles`: `false`
- `quality_check_enabled`: `true`
- `quality_check_strict`: `false`

The planned Step86 row is a contract only. Step85 must not run it.

## Planned Geometry Config

Add `configs/step85_squid_proxy_geometry_1024.json` as a planned-only geometry config. It must preserve the Step30 procedural
`squid_proxy` shape semantics while lowering particle count to 1024 and disabling strict quality checks for the planned smoke.

Required fields:

- `geometry_type`: `squid_proxy`
- `n_particles`: `1024`
- `mantle_center`: `[0.50, 0.58, 0.50]`
- `mantle_radii`: `[0.16, 0.24, 0.12]`
- `head_center`: `[0.50, 0.36, 0.50]`
- `head_radii`: `[0.11, 0.10, 0.09]`
- `arm_length`: `0.22`
- `arm_radius`: `0.018`
- `fin_radius`: `0.07`
- `quality_check_enabled`: `true`
- `quality_check_strict`: `false`
- `deterministic`: `true`

## Required New Config Files

- `configs/step85_squid_proxy_static_geometry_activation_plan.json`
- `configs/step85_squid_proxy_static_geometry_guard_policy.json`
- `configs/step85_step84_regression_policy.json`
- `configs/step85_step31_reference_policy.json`
- `configs/step85_output_guard_policy.json`
- `configs/step85_artifact_manifest_policy.json`
- `configs/step85_squid_proxy_geometry_1024.json`

## Required Evidence Modules

- `src/mpm_lbm/evidence/step85_squid_proxy_static_geometry_activation_plan.py`
- `src/mpm_lbm/evidence/step85_squid_proxy_static_geometry_activation_guard.py`
- `src/mpm_lbm/evidence/step85_step84_regression_guard.py`
- `src/mpm_lbm/evidence/step85_step31_reference_guard.py`
- `src/mpm_lbm/evidence/step85_output_guard.py`

## Required Baseline Runners

- `baseline_tests/step85_common.py`
- `baseline_tests/run_step85_squid_proxy_static_geometry_activation_plan.py`
- `baseline_tests/run_step85_squid_proxy_static_geometry_activation_guard.py`
- `baseline_tests/run_step85_step84_regression_guard.py`
- `baseline_tests/run_step85_step31_reference_guard.py`
- `baseline_tests/run_step85_output_guard.py`
- `baseline_tests/run_step85_artifact_manifest.py`

## Required Tests

- `tests/test_step85_squid_proxy_static_geometry_activation_plan_contract.py`
- `tests/test_step85_squid_proxy_static_geometry_activation_guard_contract.py`
- `tests/test_step85_step84_regression_contract.py`
- `tests/test_step85_step31_reference_contract.py`
- `tests/test_step85_output_guard_contract.py`

## Required Documentation And Report

- `docs/85_squid_proxy_static_geometry_activation_plan_and_guard.md`
- `STEP85_SQUID_PROXY_STATIC_GEOMETRY_ACTIVATION_PLAN_AND_GUARD_REPORT.md`
- Update the existing status/roadmap surfaces only if the edits remain within Step85's plan-and-guard scope:
  - `README.md`
  - `docs/00_project_status.md`
  - `docs/ACTIVATION_PRECONDITIONS.md`
  - `docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md`
  - `docs/POST_GATE_SIMULATION_CAMPAIGN_STATUS.md`

## Required Evidence Outputs

Generate these output directories with JSON, CSV, and summary CSV artifacts:

- `outputs/step85_squid_proxy_static_geometry_activation_plan/`
- `outputs/step85_squid_proxy_static_geometry_activation_guard/`
- `outputs/step85_step84_regression_guard/`
- `outputs/step85_step31_reference_guard/`
- `outputs/step85_output_guard/`
- `outputs/step85_artifact_manifest/`

Generate matching logs under `logs/step85_*.log`.

## Activation Plan Acceptance

The activation plan artifact must prove:

- previous commit is `29a130ccef93f095deeaa941b44003720f2291c5`
- Step85 activation feature count is `0`
- planned Step86 activation feature count is `1`
- driver run, `FSIDriver3D`, and simulation run are not allowed in Step85
- planned Step86 row is exactly the single `squid_proxy` static-geometry row above
- quality check is enabled but not strict for Step86
- runtime geometry, geometry mutation, wall velocity, combined runtime geometry/wall velocity, real geometry, real geometry candidates,
  `link_area`, 48^3, 64^3, VTR, particle NPY, solver formula changes, and tau migration are all closed
- physical validation, production readiness, real squid validation, swimming, and actuation claims are all closed

## Activation Guard Acceptance

The activation guard artifact must prove:

- every guard row passes
- Step85 activation feature count remains `0`
- planned Step86 activation feature count is exactly `1`
- planned Step86 feature is `squid_proxy_static_geometry`
- planned Step86 geometry config path is `configs/step85_squid_proxy_geometry_1024.json`
- the planned geometry config exists and is procedural `squid_proxy`
- Step86 quality report is required
- no other feature is planned or enabled

## Step84 Regression Acceptance

The Step84 regression artifact must prove the accepted Step84 evidence still says:

- Step84 smoke matrix passed
- Step84 quality audit passed
- Step84 activation guard passed
- Step84 output guard passed
- Step84 artifact manifest passed
- Step84 Step80/82/83 regression guards passed
- activation feature count is `2`
- runtime geometry enabled count is `1`
- wall velocity enabled count is `1`
- combined runtime geometry plus wall velocity enabled count is `1`
- real geometry, squid proxy, link area, 48^3, 64^3, VTR, and particle NPY counts remain `0`

## Step31 Reference Acceptance

The Step31 reference artifact must not rerun Step31. It must only validate that historical Step31/Step30 reference surfaces still exist
and make the correct claim boundary:

- `configs/step30_squid_proxy_geometry.json` exists
- Step30 geometry type is `squid_proxy`
- Step30 procedural geometry is deterministic
- Step31 static driver reference report exists
- Step31 is a controlled squid-proxy static-region reference, not real squid validation
- Step31 makes no squid swimming claim

## Output Guard Acceptance

The Step85 output guard must prove:

- no Step85 driver-run directory exists
- no VTR output exists
- no particle NPY output exists
- no raw geometry output exists
- no real geometry candidate output exists
- no dense or sparse wall-velocity output exists
- no dense displacement or displaced-particle output exists
- no private absolute paths are written into Step85 output/log artifacts
- no protected external, real-geometry, diagnostics, or runtime solver paths are changed
- no large Step85 artifact is produced

## Artifact Manifest Acceptance

The artifact manifest must prove:

- Step85 file count stays within policy budget
- Step85 total size stays under policy budget
- no Step85 driver-run directory exists
- no Step85 VTR or particle NPY outputs exist
- no Step85 raw geometry files exist
- no protected external or real-geometry path is touched
- no private absolute paths appear in Step85 outputs/logs

## Verification Commands

Run these with the trusted Taichi environment:

```powershell
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step85_squid_proxy_static_geometry_activation_plan.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step85_squid_proxy_static_geometry_activation_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step85_step84_regression_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step85_step31_reference_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step85_output_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step85_artifact_manifest.py
D:\working\taichi\env\python.exe -W ignore -m pytest -q tests\test_step85_squid_proxy_static_geometry_activation_plan_contract.py tests\test_step85_squid_proxy_static_geometry_activation_guard_contract.py tests\test_step85_step84_regression_contract.py tests\test_step85_step31_reference_contract.py tests\test_step85_output_guard_contract.py
D:\working\taichi\env\python.exe -W ignore -m pytest -q
D:\TOOL\Anaconda\python.exe -W ignore -m pytest -q
```

Capture focused/full pytest outputs in `logs/step85_*.log`.

## Git And Push Requirement

After implementation and verification:

- confirm no forbidden protected path is changed
- confirm `origin/main` has not moved unexpectedly
- commit with:
  `test: add step85 squid proxy static geometry activation plan and guard`
- push to `origin main`
- report final commit hash and pushed branch
