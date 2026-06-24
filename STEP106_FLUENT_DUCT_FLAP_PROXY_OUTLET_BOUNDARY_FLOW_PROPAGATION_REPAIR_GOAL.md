# Step106 Fluent Duct-Flap Proxy Outlet Boundary Flow Propagation Repair Goal

## Source Commit And Scope

This goal starts from `origin/main` commit `4e62e197e426de436b64179bab5cd807a68cf9de`, where Step105 was accepted only as a 50-step transient smoke and dimensional gap audit. Step105 proved that the repaired Step104 duct-flap proxy can run, but it also exposed a boundary-condition blocker: the inlet and mid-duct planes have positive x-velocity while the x-max outlet plane remains exactly zero.

Step106 is a red-to-green repair of that specific outlet-boundary propagation defect. The work is intentionally narrow. It must not become a Fluent validation step, a force tuning step, a displacement-curve fitting step, or a broad solver refactor.

## One-Sentence Goal

Repair and prove the duct velocity-inlet / pressure-outlet LBM boundary propagation so the repaired 48^3 duct proxy no longer leaves the x-max outlet plane zero-velocity, while preserving all Fluent-equivalence and physical-validation claim guards.

## Current Evidence From Step105

Step105 evidence established:

- `target_u_lbm = [0.02, 0.0, 0.0]` is applied to the x-min velocity inlet.
- The 48^3 / 1024-particle / 50-step duct-flap proxy smoke completed with no NaN or Inf diagnostics.
- The fixed flap base remained constrained.
- The solid initial velocity was not initialized from `target_u_lbm`.
- Step36 squid wall-velocity config stayed disconnected.
- The dimensional mapping report showed the current proxy inlet maps to about `0.08333333333333333 m/s`, not the public tutorial inlet velocity of `10 m/s`.
- The gap taxonomy still blocks Fluent validation and direct quantitative equivalence.

Step105 also exposed the next blocker:

- inlet plane mean ux: about `0.02000000700354576`
- mid-duct plane mean ux: about `0.010271445848047733`
- outlet plane mean ux: `0.0`
- outlet plane max ux: `0.0`
- `outlet_plane_flow_present = false`

The suspected implementation defect is the x-right pressure outlet branch in `src/mpm_lbm/sim/lbm/fluid.py`: when the interior neighbor is fluid, the boundary distribution is rebuilt from the outlet boundary cell's own old velocity instead of the interior neighbor velocity. From a zero initial state, this can self-lock the pressure outlet velocity at zero.

## Allowed Claims

The final Step106 report may claim only:

- The duct proxy x-right pressure outlet boundary propagation was repaired for the committed 48^3 proxy setup.
- A duct-only LBM runner demonstrates nonzero flow reaches the outlet plane under the repaired x-min velocity inlet / x-max pressure outlet configuration.
- A small FSI regression smoke confirms the repaired boundary path does not break the Step104/Step105 fixed-base, no-NaN, no-Inf, and gap-only evidence boundaries.
- The repair remains a proxy diagnostic and does not close the existing Fluent-equivalence gaps.

## Forbidden Claims

The final Step106 report, docs, tests, logs, and artifact text must not claim:

- Fluent validation
- Fluent equivalence
- physical validation
- real FSI validation
- official steady-preflow reproduction
- official displacement-curve match
- production readiness
- official mesh or proprietary Fluent file usage
- exact monitor equivalence

## Required Implementation Boundary

The only solver behavior change allowed in Step106 is the x-right pressure outlet velocity source in `src/mpm_lbm/sim/lbm/fluid.py`.

Allowed implementation change:

- For `bc_x_right == 1` and a fluid interior neighbor at `nx-2`, reconstruct the x-right pressure outlet equilibrium with `rho_bcxr` and `self.v[self.nx-2, j, k]` instead of `self.v[self.nx-1, j, k]`.

Do not modify:

- LBM collision formula
- LBM tau / viscosity convention
- streaming kernels except where required by the existing boundary call
- x-left, y, or z pressure boundaries unless a failing Step106 test proves they are in scope
- moving bounce-back formula
- moving-boundary coupling
- reaction transfer
- MPM stress update
- MPM integration
- material model
- force scaling
- flap-tip monitor definition
- dimensional mapping
- Step36 wall-velocity behavior
- vendored external code

## Required TDD Sequence

Step106 must be implemented red-to-green:

1. Add Step106 contract tests before changing `fluid.py`.
2. Run the focused Step106 tests and confirm they fail because Step106 configs/artifacts/semantics are missing or because the current output does not satisfy the outlet-flow contract.
3. Implement the minimal runner, evidence, guard, and x-right outlet repair.
4. Run the Step106 evidence generators.
5. Re-run the Step106 tests until they pass.
6. Run the full existing test suite before commit and push.

The tests should remain hook-friendly. They should primarily validate committed configs, reports, and source semantics rather than running heavy Taichi simulations inside pytest.

## Required New Files

Goal, report, and documentation:

- `STEP106_FLUENT_DUCT_FLAP_PROXY_OUTLET_BOUNDARY_FLOW_PROPAGATION_REPAIR_GOAL.md`
- `STEP106_FLUENT_DUCT_FLAP_PROXY_OUTLET_BOUNDARY_FLOW_PROPAGATION_REPAIR_REPORT.md`
- `docs/106_fluent_duct_flap_proxy_outlet_boundary_flow_propagation_repair.md`

Configs:

- `configs/step106_outlet_boundary_flow_policy.json`
- `configs/step106_duct_only_lbm_outlet_boundary_flow_48.json`
- `configs/step106_fluent_duct_flap_proxy_48_20step_outlet_repair_regression_smoke.json`
- `configs/step106_output_guard_policy.json`
- `configs/step106_artifact_manifest_policy.json`

Evidence modules:

- `src/mpm_lbm/evidence/step106_common.py`
- `src/mpm_lbm/evidence/step106_outlet_boundary_flow_propagation_runner.py`
- `src/mpm_lbm/evidence/step106_output_guard.py`

Baseline runners:

- `baseline_tests/step106_common.py`
- `baseline_tests/run_step106_outlet_boundary_flow_propagation.py`
- `baseline_tests/run_step106_fsi_outlet_repair_regression_smoke.py`
- `baseline_tests/run_step106_output_guard.py`
- `baseline_tests/run_step106_artifact_manifest.py`

Tests:

- `tests/test_step106_outlet_boundary_flow_propagation_contract.py`
- `tests/test_step106_output_guard_contract.py`

Modified source:

- `src/mpm_lbm/sim/lbm/fluid.py`

README should also receive one concise Step106 bullet in the implemented-step list.

## Required Duct-Only Runner

Create a duct-only LBM boundary propagation runner that excludes MPM/FSI particles. This runner isolates the x-min velocity inlet / x-max pressure outlet behavior.

Runner requirements:

- Use `LBMFluid3D`.
- Use `LBMConfig` with `nx = ny = nz = 48`.
- Use `bc_x_left = 2`.
- Use `bc_x_right = 1`.
- Use `vel_bc_x_left = [0.02, 0.0, 0.0]`.
- Use `rho_bc_x_right = 1.0`.
- Use the Step104 repaired duct-flap geometry config.
- Build static duct geometry with `include_flap = false`, matching Step104/Step105 LBM static duct-wall semantics.
- Write outputs under `outputs/step106_outlet_boundary_flow_propagation/`.
- Write `geo_duct_flap_proxy_48.dat` only inside the Step106 output directory.
- Run long enough for the outlet boundary repair to be observable in duct-only diagnostics while remaining a short diagnostic run.

Required duct-only outputs:

- `outputs/step106_outlet_boundary_flow_propagation/flow_plane_timeseries.csv`
- `outputs/step106_outlet_boundary_flow_propagation/flow_plane_report.json`
- `outputs/step106_outlet_boundary_flow_propagation/flow_plane_report.csv`
- `outputs/step106_outlet_boundary_flow_propagation/flow_plane_report.md`
- `outputs/step106_outlet_boundary_flow_propagation/boundary_condition_semantics_report.json`
- `outputs/step106_outlet_boundary_flow_propagation/duct_static_geometry_report.json`

Required `flow_plane_timeseries.csv` fields:

- `step`
- `inlet_mean_ux`
- `inlet_max_ux`
- `mid_mean_ux`
- `mid_max_ux`
- `outlet_mean_ux`
- `outlet_max_ux`
- `outlet_to_mid_mean_ux_ratio`
- `outlet_to_inlet_mean_ux_ratio`
- `rho_min`
- `rho_max`
- `mass_total`
- `has_nan`
- `has_inf`

The ratio fields are diagnostics only. Do not make fully-developed-flow ratios hard gates in Step106.

## Required Boundary Semantics Report

`boundary_condition_semantics_report.json` must include:

- `bc_x_left = 2`
- `bc_x_right = 1`
- `velocity_inlet_policy = "fixed_equilibrium_velocity"`
- `pressure_outlet_policy = "interior_neighbor_velocity_extrapolation"`
- `pressure_outlet_velocity_source = "self.v[self.nx-2,j,k] when the x-right interior neighbor is fluid"`
- `pressure_outlet_uses_boundary_self_velocity = false`
- `pressure_outlet_uses_interior_neighbor_velocity = true`
- `target_u_lbm = [0.02, 0.0, 0.0]`
- `rho_bc_x_right = 1.0`
- `direct_quantitative_equivalence_allowed = false`
- `validation_claim_allowed = false`

The tests must hard-assert the two pressure-outlet velocity-source booleans.

## Required FSI Regression Smoke

After the duct-only boundary runner passes, run a small FSI regression smoke using the repaired Step104/Step105 setup:

- row name: `fluent_duct_flap_proxy_48_20step_outlet_repair_regression_smoke`
- `n_grid = 48`
- `n_particles = 1024`
- `n_lbm_steps = 20`
- `mpm_dt = 0.0005`
- `mpm_substeps_per_lbm_step = 1`
- `target_u_lbm = [0.02, 0.0, 0.0]`
- `initial_solid_velocity_norm = [0.0, 0.0, 0.0]`
- `geometry_type = "duct_flap_proxy"`
- `geometry_config_path = "configs/step104_fluent_duct_flap_geometry_1024.json"`
- `lbm_boundary_condition_mode = "duct_velocity_inlet_pressure_outlet"`
- `coupling_mode = "moving_boundary"`
- `reaction_transfer_mode = "engineering"`
- `wall_velocity_application_mode = "disabled"`
- `write_vtk = false`
- `write_particles = false`

Required FSI regression outputs:

- `outputs/step106_fsi_outlet_repair_regression/fsi_outlet_repair_regression_report.json`
- `outputs/step106_fsi_outlet_repair_regression/fsi_outlet_repair_regression_report.csv`
- `outputs/step106_fsi_outlet_repair_regression/fsi_outlet_repair_regression_report.md`
- `outputs/step106_fsi_outlet_repair_regression/duct_boundary_condition_report.json`
- `outputs/step106_fsi_outlet_repair_regression/duct_static_geometry_report.json`
- `outputs/step106_fsi_outlet_repair_regression/flap_tip_displacement_timeseries.csv`

The FSI regression smoke must verify:

- `FSIDriver3D.run()` is called.
- The completed LBM step count is exactly 20.
- Diagnostics are present.
- The flap-tip time series is emitted.
- The fixed-base constraint remains applied.
- The fixed-base maximum displacement and velocity remain near zero.
- `target_u_lbm` is applied to the inlet.
- `target_u_lbm` is not applied to solid initial velocity.
- Step36 wall velocity remains disabled.
- The run has no NaN or Inf diagnostics.
- Direct quantitative equivalence and validation claims remain false.

## Hard Acceptance Criteria

The Step106 duct-only outlet boundary runner passes only when:

- `duct_only_outlet_boundary_flow_pass = true`
- final outlet plane mean ux is greater than `1.0e-5`
- final outlet plane max ux is greater than `1.0e-5`
- final mid-duct plane mean ux is greater than `1.0e-4`
- final inlet plane mean ux is within `[0.015, 0.025]`
- final `rho_min > 0.95`
- final `rho_max < 1.10`
- no NaN values are detected
- no Inf values are detected
- `pressure_outlet_uses_boundary_self_velocity = false`
- `pressure_outlet_uses_interior_neighbor_velocity = true`
- `direct_quantitative_equivalence_allowed = false`
- `validation_claim_allowed = false`

The Step106 output guard passes only when:

- official/proprietary Fluent file count is zero
- private Fluent CSV count is zero
- Fluent case/data output count is zero
- particle NPY count is zero
- VTR count is zero
- video count is zero
- protected external edit count is zero
- protected real geometry candidate edit count is zero
- forbidden validation claim count is zero
- Step36 wall-velocity reference count is zero
- Step106 artifacts remain within the configured size budget

## Required Verification Commands

Use the trusted Taichi environment first:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\mpm_lbm\sim\lbm\fluid.py src\mpm_lbm\evidence\step106_common.py src\mpm_lbm\evidence\step106_outlet_boundary_flow_propagation_runner.py src\mpm_lbm\evidence\step106_output_guard.py baseline_tests\step106_common.py baseline_tests\run_step106_outlet_boundary_flow_propagation.py baseline_tests\run_step106_fsi_outlet_repair_regression_smoke.py baseline_tests\run_step106_output_guard.py baseline_tests\run_step106_artifact_manifest.py tests\test_step106_outlet_boundary_flow_propagation_contract.py tests\test_step106_output_guard_contract.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step106_outlet_boundary_flow_propagation.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step106_fsi_outlet_repair_regression_smoke.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step106_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step106_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step106_outlet_boundary_flow_propagation_contract.py tests\test_step106_output_guard_contract.py
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Then verify the general local test entrypoints used by the repo and hooks:

```powershell
& 'D:\TOOL\Anaconda\python.exe' -m pytest -q
pytest -q
git diff --check
git status --short --branch
```

If any environment cannot import Taichi, report that explicitly and do not turn it into a false pass.

## Commit And Push Requirement

When Step106 implementation and verification are complete, commit all relevant code, configs, docs, reports, logs, and generated artifacts, then push `main` to the configured GitHub remote. The final response must report:

- branch
- commit hash
- pushed remote branch
- key verification commands and pass/fail result
- the exact remaining scope limit: Step106 repairs outlet boundary propagation only and is not Fluent validation
