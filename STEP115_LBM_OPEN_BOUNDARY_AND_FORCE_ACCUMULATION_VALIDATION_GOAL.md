# Step115 LBM Open Boundary And Force Accumulation Validation Goal

## User Request

Use the post-Step114 GitHub review of commit
`4e313119e2f431aedb3e787542529f26048ab737` as the implementation
contract. The review accepts Step114 as a correct first repair layer, but says
the solver is still not Fluent-equivalent. Step115 must not tune a picture or
start a full 96^3 FSI comparison. It must first make the fluid boundary and
Step114 force exchange behavior testable at runtime.

## Step115 Objective

Implement a bounded Step115 repair layer that turns the Step114 solver surfaces
into executable, auditable behavior:

1. Add a runtime/kernel-level numerical test proving the moving-boundary
   force accumulator really averages all substep force samples.
2. Implement an opt-in D3Q19 x-inlet/x-outlet open-boundary mode named
   `regularized_velocity_pressure` that reconstructs only unknown incoming
   populations and preserves known streamed non-equilibrium content.
3. Keep the legacy `equilibrium_all_population_reset` mode unchanged and
   explicitly report which boundary implementation is active.
4. Add physical viscosity/tau feasibility diagnostics so dangerous
   near-0.5 tau mappings are visible and can be made strict for
   Fluent-like configs.
5. Add small duct-only/static-flow evidence and artifact-backed tests for the
   new boundary and tau reports.
6. Update docs, reports, README, and config-policy guards without claiming
   Fluent validation, Figure 29.3 parity, official mesh/case reproduction, or
   production readiness.

## Non-Goals And Guardrails

- Do not run Fluent.
- Do not import, commit, or copy private Ansys case/data/mesh files.
- Do not claim exact Fluent equivalence, exact Figure 29.3 jet parity, exact
  structural monitor equivalence, official dynamic mesh reproduction, or
  production-ready FSI.
- Do not touch `external/taichi_LBM3D`.
- Do not replace the solid model with small-strain linear elasticity in
  Step115.
- Do not implement conservative interface traction transfer in Step115.
- Do not implement D2Q9 planar flow or a quasi-2D periodic-z solver in
  Step115.
- Do not make `regularized_velocity_pressure` the default. The legacy default
  must remain stable for prior Step tests.

## Required P0 Work

### P0.1 Runtime Moving-Boundary Force Accumulator Test

Problem: Step114 proved source wiring, but it did not run a numeric Taichi test
showing that two or more different `hydro_force` samples are averaged by
`finalize_moving_boundary_force_accumulator()`.

Required implementation:

- Add a small test helper path that can write deterministic values into
  `LBMFluid3D.hydro_force`.
- Run the real Taichi accumulator kernels:
  `clear_moving_boundary_force_accumulator()`,
  `accumulate_moving_boundary_force_sample()`, and
  `finalize_moving_boundary_force_accumulator()`.
- Verify that samples `[1, 0, 0]` and `[3, 0, 0]` produce final
  `hydro_force = [2, 0, 0]` at the selected cell.
- Verify `mb_subcycle_force_sample_count == 2`.
- Verify `mb_subcycle_force_accum_norm_max` and
  `mb_subcycle_force_mean_norm_max` are finite and match the expected
  accumulator behavior.
- Add a regression check that the non-subcycled moving-boundary path does not
  call the accumulator.

Acceptance:

- The new test must fail against Step114 if the accumulator kernels are absent
  or if finalize writes the last sample instead of the mean.
- Step114 tests must still pass.

### P0.2 Regularized X Open-Boundary Mode

Problem: the current duct inlet/outlet mode resets all D3Q19 populations to
equilibrium at open boundaries. That erases non-equilibrium stress and is not
acceptable as the next fluid baseline for Fluent-inspired comparisons.

Required implementation:

- Make `lbm_open_boundary_semantics = "regularized_velocity_pressure"` an
  accepted, implemented opt-in mode.
- Keep `lbm_open_boundary_semantics = "equilibrium_all_population_reset"` as
  the default legacy mode.
- Pass the selected open-boundary semantics from `FSIDriverConfig` through
  `UnifiedSimConfig` into `LBMConfig` and `LBMFluid3D`.
- In `LBMFluid3D.Boundary_condition()`, branch on the open-boundary semantics:
  - legacy mode: preserve the current all-population equilibrium overwrite;
  - regularized mode: for x-min velocity inlet and x-max pressure outlet,
    reconstruct only the unknown incoming populations while preserving known
    streamed populations.
- Scope the new implementation to the x-axis duct case only. Other axes may
  remain legacy or fail by config guard.
- For velocity inlet, use the configured inlet velocity and a density derived
  from the streamed known populations when possible, with finite fallback to
  `rho0`.
- For pressure outlet, use configured outlet density and extrapolate velocity
  from the adjacent interior cell.
- Do not silently call the legacy all-population loop inside the regularized
  x-boundary branch.

Required reporting:

- `duct_boundary_condition_report.json` must include:
  - `lbm_open_boundary_semantics`
  - `unknown_population_reconstruction_used`
  - `all_population_equilibrium_reset_used`
  - `implemented_axis`
  - `pressure_outlet_density`
  - `velocity_inlet_target`
  - `boundary_condition_equivalence_claim_allowed = false`

Acceptance:

- Config construction accepts `regularized_velocity_pressure`.
- Config construction still rejects `zou_he_reconstruct_unknowns`.
- Legacy behavior remains the default.
- Source/contract tests prove the regularized branch reconstructs unknown x
  populations instead of overwriting all 19 populations.
- A small runtime duct-only smoke can run finite with the new mode.

### P0.3 Tau/Re Feasibility Guard

Problem: Step114 can compute physical viscosity mapping, but a public
official-speed air mapping at 96^3 can push `tau` extremely close to `0.5`.
The code currently only rejects `tau <= 0.5`, which hides a meaningful
numerical risk.

Required implementation:

- Add config fields:
  - `lbm_min_tau_margin`
  - `lbm_tau_stability_policy`
- Valid tau stability policies:
  - `report_only`
  - `strict`
- Preserve `report_only` as the default to avoid breaking legacy configs.
- In the viscosity mapping report, include:
  - `tau_minus_half`
  - `lbm_min_tau_margin`
  - `lbm_tau_stability_policy`
  - `tau_margin_pass`
  - `mach_proxy`
  - `reynolds_from_config`
  - `target_reynolds_number`
  - `target_reynolds_match`
  - `physical_reynolds_direct_simulation_feasible_with_current_lbm`
- If policy is `strict`, reject mappings where `tau_minus_half` is smaller
  than `lbm_min_tau_margin`.
- If `target_reynolds_number` is provided, compute
  `Re = U * H / nu` from the available dimensional fields and report whether
  it matches.

Acceptance:

- A test proves official-like physical mapping produces a near-half tau report
  and marks feasibility as false or unknown.
- A strict-policy test rejects the same risky mapping.
- A report-only test accepts the same mapping but exposes the risk in the
  mapping report.

### P0.4 Step115 Evidence Artifacts

Create a lightweight committed output directory:

`outputs/step115_lbm_open_boundary_repair/`

Required artifacts:

- `solver_report.json`: summary of Step115 code paths, tests, and remaining
  gaps.
- `boundary_condition_semantics_report.json`: static report describing legacy
  vs regularized semantics and the active x-axis reconstruction scope.
- `tau_feasibility_report.json`: official-like physical mapping report showing
  tau margin and feasibility fields.

Optional if runtime cost is small enough:

- a small duct-only smoke report from the new regularized mode with finite
  density/velocity checks.

Acceptance:

- Artifacts are deterministic, small, and committed.
- Artifacts do not include private official Ansys files or large simulation
  arrays.
- Tests validate artifact schema and key fields.

## Required P1 Work

### P1.1 Documentation

Update:

- `STEP115_LBM_OPEN_BOUNDARY_AND_FORCE_ACCUMULATION_VALIDATION_REPORT.md`
- `docs/115_lbm_open_boundary_repair.md`
- `README.md`

The docs must state:

- Step115 is not Fluent validation.
- `regularized_velocity_pressure` is an opt-in x-boundary repair, not Fluent's
  pressure-based solver.
- The default legacy boundary is preserved.
- Physical-Re direct matching remains risky when tau is too close to `0.5`.
- Full FSI parity remains blocked by solid model, conservative traction, and
  planar/symmetry gaps.

### P1.2 Policy/Regression Updates

Update existing config/schema/preservation policy files only as needed to make
intentional Step115 fields explicit. Do not weaken guards unrelated to Step115.

Expected intentional schema/config additions may include:

- `lbm_open_boundary_semantics` on `LBMConfig` and `UnifiedSimConfig`
- `lbm_min_tau_margin` on `FSIDriverConfig`
- `lbm_tau_stability_policy` on `FSIDriverConfig`

## Verification Plan

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\drivers\fsi_config.py `
  src\mpm_lbm\sim\drivers\fsi_driver.py `
  src\mpm_lbm\sim\drivers\sim_config.py `
  src\mpm_lbm\sim\lbm\config.py `
  src\mpm_lbm\sim\lbm\fluid.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step114_fluent_solver_physics_repair_contract.py `
  tests\test_step115_lbm_open_boundary_and_force_accumulation_contract.py `
  tests\test_step104_fluent_duct_flap_setup_repair_contract.py `
  tests\test_step106_outlet_boundary_flow_propagation_contract.py `
  tests\test_step112_planar_constraint_contract.py `
  tests\test_step113_mirrored_duct_flap_geometry_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q
git diff --check
```

Expected result:

- Step115 tests fail before implementation and pass after implementation.
- Existing Step104/Step106/Step112/Step113/Step114 contracts still pass.
- Full test suite passes.
- README/docs/report describe the new boundary and tau behavior accurately.
- The final pushed commit includes code, tests, goal, report, docs, and small
  deterministic Step115 artifacts.

## Push Requirement

After implementation and verification, commit and push to the configured GitHub
remote `origin/main`. Report:

- final commit hash
- branch and remote
- focused and full test results
- whether push succeeded
- known remaining solver gaps
