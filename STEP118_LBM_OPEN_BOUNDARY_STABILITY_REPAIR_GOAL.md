# Step118 Goal: LBM Open-Boundary Stability Repair

## Source Review

This goal is anchored to the GitHub `main` state whose remote head is
`d218b901628b520e51fb3d4595d28050292da806`:

- `53c0106257c888753f115d4949f4eb9bab07cb9b`
  (`test: add step117 long-window validation contracts`)
- `d218b901628b520e51fb3d4595d28050292da806`
  (`feat: add step117 long-window fluid validation`)

Step117 is treated as a successful verification/debugging step, not as a
failed implementation. Its result is that the current
`regularized_velocity_pressure` LBM open-boundary path is not safe to carry
into quasi-2D or FSI. Step118 must therefore repair and diagnose LBM
open-boundary stability before any later quasi-2D, conservative traction, or
full FSI work.

## One-Sentence Objective

Locate and repair the Step117 96^3 long-window instability in the regularized
open-boundary path, using artifact-backed diagnostics and opt-in boundary
variants, without claiming Fluent parity, quasi-2D readiness, or FSI readiness.

## Non-Negotiable Scope Boundaries

1. Do not implement Step118 as quasi-2D or FSI.
2. Do not claim Figure 29.3 parity, Fluent validation, official mesh
   reproduction, production readiness, or full physical validation.
3. Do not hide instability with a plotted field or hardcoded post-processing.
4. Preserve the old `regularized_velocity_pressure` branch as a regression
   reference.
5. Keep any new stabilization behavior opt-in and explicit in reports.
6. Do not touch vendored external code unless a later explicit goal expands
   that scope.
7. Keep the physical-nu/tau-margin guard strict; official-like physical
   viscosity rows must remain skipped when tau is too close to 0.5.

## Step117 Evidence To Preserve

The Step117 evidence to preserve in Step118 reports:

- 48^3 legacy, 500 steps:
  - Completed the requested window.
  - Passed density and mass gates.
  - `mass_total_delta_rel_final = 0.0007730374927265733`.
  - `flux_imbalance_rel_final = 0.023743154482287754`.
  - Served as the most stable current short-term baseline.
- 48^3 regularized, 500 steps:
  - Completed the requested window.
  - Passed basic density/mass gates.
  - Was still worse than legacy.
  - `mass_total_delta_rel_final = 0.002957161603977865`.
  - `flux_imbalance_rel_final = 0.45028733921896075`.
  - Step117 comparison classified it as not acceptable for long-window use.
- 96^3 regularized duct-only, 1000 steps:
  - Completed step count but failed density/mass gates.
  - `mass_total_delta_rel_final = 121131397.8756467`.
  - Density and velocity became numerically nonphysical.
- 96^3 static two-flap regularized, 1000 steps:
  - Completed step count but failed density/mass gates.
  - Final mass drift was catastrophic.
- Official-like physical-nu row:
  - Correctly blocked by strict tau margin.

## Success Criteria

Step118 succeeds only if all required artifacts can answer these questions:

1. Where does the first instability appear: inlet, outlet, wall/open-boundary
   corner, or interior?
2. At what step does the first failure threshold trigger?
3. Does 96^3 legacy remain stable under the same long-window diagnostic
   harness?
4. Does a limited regularized or convective-outlet variant improve the 48^3
   regularized behavior without degrading below the legacy baseline envelope?
5. Can the best new boundary variant complete 96^3 duct-only long-window
   diagnostics without density/mass explosion?
6. Can the best new boundary variant complete the 96^3 static two-flap
   long-window diagnostic without density/mass explosion?
7. Is Step119 quasi-2D allowed or still blocked?

The Step118 final classification must be exactly one of:

- `boundary_repair_success_go_to_quasi2d`
- `boundary_repair_partial_continue_lbm`
- `boundary_repair_failed_revisit_lbm_solver`

Step119 can be allowed only when the final report shows:

- 48^3 best boundary `flux_imbalance_rel_tail_mean < 0.1`.
- 48^3 best boundary final mass drift is below `0.005` and below two times
  the 48^3 legacy final mass drift.
- 96^3 duct-only best boundary passes density and mass gates.
- 96^3 static two-flap best boundary passes density and mass gates.
- Observed Mach proxy stays below `0.2`.
- No negative-density event is reported.
- Population diagnostics show no catastrophic negative-population fraction.
- A boundary-variant comparison artifact exists.
- Physical-nu/tau strict row remains blocked when tau is unsafe.

## P0: Stability Diagnostics

Add `src/mpm_lbm/sim/diagnostics/lbm_stability_diagnostics.py`.

The module must provide lightweight, NumPy-friendly helpers that can operate
on synthetic arrays in tests and on solver arrays converted by existing
diagnostic code in runners:

- `population_stats(...)`
- `negative_population_stats(...)`
- `boundary_population_stats(...)`
- `density_outlier_stats(...)`
- `velocity_outlier_stats(...)`
- `mass_source_sink_by_step(...)`
- `first_gate_failure_detector(...)`
- `classify_first_failure_location(...)`

Required reported fields include:

- `f_min`, `f_max`, `F_min`, `F_max`
- Negative population count and fraction.
- Boundary-plane negative population count and fraction.
- First step where `rho_min < 0`.
- First step where `rho_max > 1.2`.
- First step where `abs(mass_drift) > 0.05`.
- First step where `max_v > 0.2`.
- Inlet/outlet density extrema.
- Near-outlet density extrema.
- First failure location classification.

## P1: Diagnostic Matrix

Add a Step118 runner at
`experiments/steps/step118_lbm_open_boundary_stability_repair.py`.

The runner must be resume-friendly and support small contract-test rows. It
must write artifacts under:

`outputs/step118_lbm_open_boundary_stability_repair/`

Required rows:

1. `duct_only_48_regularized_1000step_diagnostic`
2. `duct_only_64_regularized_1000step_diagnostic`
3. `duct_only_80_regularized_1000step_diagnostic`
4. `duct_only_96_regularized_1000step_diagnostic`
5. `duct_only_96_legacy_1000step_reference`
6. `static_two_flap_96_legacy_1000step_reference`

The contract-test path may run tiny rows, but committed artifacts must still
have the same schema as the long-window runner.

## P2: Boundary Repair Variants

Preserve the existing:

- `equilibrium_all_population_reset`
- `regularized_velocity_pressure`

Add opt-in variants:

- `regularized_velocity_pressure_limited`
- `convective_pressure_outlet_experimental`

The limited regularized variant must support:

- Rho clamp.
- Velocity magnitude clamp.
- Optional population floor.
- Non-equilibrium magnitude limiter.

Suggested config fields:

- `open_boundary_limiter_enabled`
- `open_boundary_rho_min`
- `open_boundary_rho_max`
- `open_boundary_u_max`
- `open_boundary_noneq_cap`
- `open_boundary_population_floor`

The convective outlet variant may be implemented first as a conservative
population extrapolation/outflow experiment, but it must be explicitly reported
as experimental and opt-in.

## P3: Config And Report Guards

Extend the valid open-boundary semantics list to include the new variants.

Every Step118 report must include:

- Selected open-boundary semantic.
- Whether limiter was enabled.
- Rho clamp values.
- Velocity clamp value.
- Non-equilibrium limiter value.
- Population floor value.
- Whether convective outlet behavior was used.
- `validation_claim_allowed = false`.
- `step119_quasi2d_allowed`.
- Final Step118 classification.

## P4: Repair Run Matrix

Stage 1, 48^3 comparison:

1. `duct_only_48_legacy_boundary_500step_reference`
2. `duct_only_48_regularized_boundary_500step_reference`
3. `duct_only_48_regularized_limited_boundary_500step`
4. `duct_only_48_convective_outlet_boundary_500step`

Stage 2, 96^3 duct-only:

5. `duct_only_96_regularized_limited_boundary_1000step`
6. `duct_only_96_convective_outlet_boundary_1000step`

Stage 3, 96^3 static two-flap:

7. `static_two_flap_96_best_boundary_1000step`

Long rows can be expensive; tests should validate schema and short smoke rows,
while the runner should be able to resume and reuse finished rows.

## P5: Tests

Add the following tests before or alongside implementation:

- `tests/test_step118_lbm_stability_diagnostics_contract.py`
- `tests/test_step118_open_boundary_limiter_contract.py`
- `tests/test_step118_boundary_repair_runner_contract.py`
- `tests/test_step118_boundary_repair_artifacts_contract.py`

The tests must cover:

- Synthetic population and density diagnostics.
- First failure detection.
- Boundary location classification.
- Config validation and default-disabled limiter behavior.
- Source/runtime contract for the two new boundary variants.
- Runner artifact schema.
- No Step118 artifact claims Fluent validation, FSI validation, or quasi-2D
  readiness before gates pass.

## P6: Documentation And Artifacts

Add or update:

- `STEP118_LBM_OPEN_BOUNDARY_STABILITY_REPAIR_REPORT.md`
- `docs/118_lbm_open_boundary_stability_repair.md`
- `outputs/step118_lbm_open_boundary_stability_repair/solver_report.json`
- `outputs/step118_lbm_open_boundary_stability_repair/run_matrix_summary.json`
- `outputs/step118_lbm_open_boundary_stability_repair/boundary_variant_comparison.json`
- `outputs/step118_lbm_open_boundary_stability_repair/first_failure_diagnostics.json`
- README Step118 entry.

## Required Verification Commands

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py `
  src\mpm_lbm\sim\diagnostics\lbm_stability_diagnostics.py `
  src\mpm_lbm\sim\lbm\config.py `
  src\mpm_lbm\sim\lbm\fluid.py `
  src\mpm_lbm\sim\drivers\fsi_config.py `
  experiments\steps\step118_lbm_open_boundary_stability_repair.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step118_lbm_stability_diagnostics_contract.py `
  tests\test_step118_open_boundary_limiter_contract.py `
  tests\test_step118_boundary_repair_runner_contract.py `
  tests\test_step118_boundary_repair_artifacts_contract.py `
  tests\test_step117_long_window_artifacts_contract.py `
  tests\test_step117_long_window_runner_contract.py `
  tests\test_step117_timeseries_trend_summary_contract.py `
  tests\test_step116_lbm_boundary_diagnostics_contract.py `
  tests\test_step115_lbm_open_boundary_and_force_accumulation_contract.py `
  tests\test_step114_fluent_solver_physics_repair_contract.py `
  tests\test_step104_fluent_duct_flap_setup_repair_contract.py `
  tests\test_step106_outlet_boundary_flow_propagation_contract.py `
  tests\test_step112_planar_constraint_contract.py `
  tests\test_step113_mirrored_duct_flap_geometry_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q
git diff --check
```

## Push Requirement

After implementation and verification, commit all relevant code, tests, docs,
reports, logs, and generated Step118 artifacts, then push to the configured
GitHub remote. The final response must report the pushed commit hash, remote
branch, important pass counts, and any unresolved physical limitation.
