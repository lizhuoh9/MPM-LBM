# Step117 Regularized LBM Long-Window Fluid Validation Goal

## Source And Baseline

This goal is based on the review of GitHub commit `304c8080fed280829c2e4af6d60351daadd59f81`
(`test: add step116 lbm fluid baseline artifacts`) in `lizhuoh9/MPM-LBM`.

Step116 is accepted as a correct diagnostic and artifact-path step: it added
the Step116 LBM-only runner, NumPy diagnostics, tau feasibility reporting, and
bounded duct/static-flap artifacts. Step116 did not complete the requested
48^3 or 96^3 long-window rows; all committed Step116 rows intentionally used
`executed_nx=8`, `steps_completed=5`, and `requested_window_completed=false`.

Step117 must convert that bounded probe surface into a real long-window
fluid-only validation gate. It must not proceed to quasi-2D, conservative
traction transfer, small-strain solid repair, or full FSI.

## One-Sentence Objective

Use the Step116 runner and diagnostics foundation to execute and report real
48^3/96^3 LBM-only long-window duct/static-flap validation, then decide whether
`regularized_velocity_pressure` is acceptable as the fluid baseline for later
quasi-2D and FSI steps.

## Hard Scope Boundaries

- Do not run full FSI.
- Do not tune flap deformation or solid response.
- Do not claim Fluent validation, Figure 29.3 parity, official mesh/case
  reproduction, official transient equivalence, or production readiness.
- Do not overwrite Step116 artifacts.
- Do not commit dense full 96^3 velocity fields unless they are compressed or
  sampled small enough to keep the artifact payload reasonable.
- Keep `external/taichi_LBM3D` unmodified.
- Preserve Step115/Step116 boundary and tau semantics unless a Step117
  contract test proves that a narrow report/runner repair is required.

## Required Runtime Matrix

Write Step117 artifacts under:

`outputs/step117_regularized_lbm_long_window_fluid_validation/`

The required first-pass matrix is:

1. `duct_only_48_legacy_boundary_500step_full`
   - geometry: `duct_only`
   - grid: 48^3
   - steps: 500
   - boundary: `equilibrium_all_population_reset`
   - role: legacy long-window reference

2. `duct_only_48_regularized_boundary_500step_full`
   - geometry: `duct_only`
   - grid: 48^3
   - steps: 500
   - boundary: `regularized_velocity_pressure`
   - role: direct comparison against the legacy 48^3 row

3. `duct_only_96_regularized_boundary_1000step_full`
   - geometry: `duct_only`
   - grid: 96^3
   - steps: 1000
   - boundary: `regularized_velocity_pressure`
   - role: requested high-grid regularized long-window row

4. `static_two_flap_96_regularized_1000step_full`
   - geometry: `static_two_flap`
   - grid: 96^3
   - steps: 1000
   - boundary: `regularized_velocity_pressure`
   - role: static two-flap fluid-only flow-development gate

5. `duct_only_96_regularized_boundary_physical_nu_report_only_100step_guarded`
   - geometry: `duct_only`
   - grid: 96^3 requested context
   - steps: 100 requested context
   - boundary: `regularized_velocity_pressure`
   - viscosity semantics: `physical_nu_mapping`
   - strict row must skip when tau margin fails
   - report-only row may run only if clearly marked not used for validation

Optional rows may be added only after the required rows are handled:

- `static_two_flap_48_legacy_boundary_500step_full`
- `static_two_flap_48_regularized_boundary_500step_full`
- `duct_only_96_legacy_boundary_500step_reference`

## Required Runner

Add a dedicated Step117 runner:

`experiments/steps/step117_regularized_lbm_long_window_fluid_validation.py`

The runner may reuse Step116 dataclasses and helper functions, but it must keep
Step117 output, report names, and summaries independent from Step116.

The runner must support:

- `--row <row-name>` to run one named row
- `--max-rows <n>` to limit a batch run
- `--resume` and default resume behavior to avoid rerunning completed rows
- `--force` to rebuild selected rows
- `--output-interval <n>` to control diagnostic cadence
- `--profile-only` to write planned row/profile metadata without stepping
- `--no-large-arrays` to keep committed artifacts CSV/JSON-first

The runner must be row-level resume friendly. A failed 96^3 row must not force
the completed 48^3 rows to rerun. Diagnostics should be written frequently
enough that partial progress can be inspected.

## Required Per-Row Artifacts

Each row directory must contain:

- `run_metadata.json`
- `driver_config.json`
- `duct_boundary_condition_report.json`
- `finite_stability_report.json`
- `fluid_diagnostics_timeseries.csv`
- `boundary_flux_timeseries.csv`
- `density_drift_timeseries.csv`
- `velocity_profile_summary.json`

Static two-flap rows must additionally contain:

- `flap_region_flow_summary.json`
- `throat_speed_summary.json`
- `recirculation_proxy_summary.json`

Step117 top-level output must contain:

- `run_matrix_summary.json`
- `run_matrix_summary.csv`
- `solver_report.json`
- `regularized_vs_legacy_comparison.json`
- `reynolds_relaxed_surrogate_report.json`
- `README.md`

## Required Long-Window Gates

Keep the Step116 base gates:

- `finite_pass`
- `density_gate_pass`
- `mass_drift_gate_pass`
- `flux_balance_reported`
- `requested_window_completed`

Add Step117 long-window gates:

- `density_range_gate_pass`
  - initial threshold: `0.85 < rho_min <= rho_max < 1.15`
- `mass_drift_gate_pass`
  - initial threshold: `abs(mass_total_delta_rel_final) < 0.05`
- `flux_development_gate_pass`
  - outlet flux must develop away from zero, and midplane/outlet motion must
    be quantified; this gate may fail honestly.
- `flux_imbalance_trend_reported`
  - report final, min, max, and tail-window mean.
- `outlet_reflection_proxy_gate_pass`
  - negative ux fraction, rho std, and ux std must not explode.
- `regularized_vs_legacy_comparison_reported`
  - compare the two 48^3 duct rows.

If a row does not complete its requested window, `requested_window_completed`
must remain false and the report must list it as incomplete. It must not be
presented as full validation.

## Required Trend Diagnostics

Add a reusable trend summary function:

`summarize_timeseries_trends(records, tail_fraction=0.2)`

It must produce at least:

- `rho_min_global`
- `rho_max_global`
- `mass_drift_final`
- `mass_drift_abs_max`
- `flux_imbalance_rel_final`
- `flux_imbalance_rel_tail_mean`
- `outlet_flux_final`
- `outlet_flux_tail_mean`
- `midplane_mean_ux_tail_mean`
- `max_v_global`
- `mach_proxy_observed_max`
- `negative_ux_fraction_tail_mean`
- `rho_std_outlet_tail_mean`

It must fail fast on empty records.

## Regularized-Versus-Legacy Decision

Compare:

- `duct_only_48_legacy_boundary_500step_full`
- `duct_only_48_regularized_boundary_500step_full`

Use:

- final mass drift
- tail mean mass drift
- final/tail flux imbalance
- density min/max/std
- outlet reflection proxy
- profile smoothness
- runtime

The final comparison result must be one of:

- `regularized_better_than_legacy_for_long_window`
- `regularized_comparable_but_not_better`
- `regularized_not_acceptable_for_long_window`
- `insufficient_completed_rows`

If the result is not the first value, Step118 must not proceed to quasi-2D/FSI.

## Physical-Nu / Tau Policy

The official-like physical-nu path must be hardened into policy:

- strict physical-nu rows with failed tau margin must skip before stepping and
  report `steps_completed=0`.
- report-only physical-nu rows must mark:
  - `tau_margin_pass=false`
  - `physical_reynolds_direct_simulation_feasible_with_current_lbm=false`
  - `not_used_for_validation=true`

Add:

`reynolds_relaxed_surrogate_report.json`

It must report:

- target Reynolds number: `26666.67`
- minimum safe `nu_lbm` under the current tau margin
- corresponding physical viscosity or Reynolds implications
- whether matching official-like Re directly is feasible under current LBM
  stability constraints
- options: increase grid, change dt, introduce a turbulence/modeling strategy,
  or explicitly accept a surrogate Reynolds comparison

## Required Tests

Add:

- `tests/test_step117_long_window_runner_contract.py`
- `tests/test_step117_long_window_artifacts_contract.py`
- `tests/test_step117_timeseries_trend_summary_contract.py`

The runner contract tests must:

- use repo-local ignored temp output, not system temp
- run a tiny 10-step spec to check long-window schema
- prove row-level resume does not rerun completed rows
- prove strict tau rows skip before stepping
- prove `--profile-only` writes planning metadata without claiming validation

The trend summary tests must:

- use synthetic records
- verify tail means, global min/max, final values, and finite handling
- verify empty records fail fast

The artifact tests must:

- verify the committed Step117 output directory has the expected top-level
  reports and required row directories or honest incomplete status.
- verify non-skipped rows that claim full validation have
  `requested_window_completed=true`.
- verify `fluent_validation_claim_allowed=false`.
- verify `full_fsi_rerun_done=false`.
- verify incomplete rows are listed as incomplete and not used to advance
  Step118.

## Required Documentation

Add:

- `STEP117_REGULARIZED_LBM_LONG_WINDOW_FLUID_VALIDATION_REPORT.md`
- `docs/117_regularized_lbm_long_window_fluid_validation.md`
- README Step117 entry

The report must answer:

1. Did the 48^3 legacy row complete 500 steps?
2. Did the 48^3 regularized row complete 500 steps?
3. Did the 96^3 regularized row complete 1000 steps?
4. Did the static two-flap 96^3 regularized row complete 1000 steps?
5. Is regularized better than legacy?
6. Is official-like physical-nu still blocked by tau margin?
7. Is Step118 quasi-2D allowed?

Step118 is allowed only if:

- the 48^3 regularized 500-step row completed,
- the 96^3 regularized 1000-step row completed,
- the static two-flap 96^3 regularized 1000-step row completed,
- those rows are finite,
- density gates pass,
- mass drift does not keep diverging,
- outlet flux develops away from zero,
- regularized is not worse than legacy,
- official-like physical-nu risk is reported and not used as validation.

Otherwise Step118 must continue LBM boundary work rather than quasi-2D/FSI.

## Verification Commands

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py `
  experiments\steps\step116_regularized_lbm_duct_flow_baseline.py `
  experiments\steps\step117_regularized_lbm_long_window_fluid_validation.py `
  src\mpm_lbm\sim\lbm\fluid.py `
  src\mpm_lbm\sim\drivers\fsi_config.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step116_lbm_boundary_diagnostics_contract.py `
  tests\test_step116_regularized_boundary_runner_contract.py `
  tests\test_step116_duct_flow_baseline_artifacts_contract.py `
  tests\test_step117_long_window_runner_contract.py `
  tests\test_step117_timeseries_trend_summary_contract.py `
  tests\test_step117_long_window_artifacts_contract.py `
  tests\test_step115_lbm_open_boundary_and_force_accumulation_contract.py `
  tests\test_step114_fluent_solver_physics_repair_contract.py `
  tests\test_step104_fluent_duct_flap_setup_repair_contract.py `
  tests\test_step106_outlet_boundary_flow_propagation_contract.py `
  tests\test_step112_planar_constraint_contract.py `
  tests\test_step113_mirrored_duct_flap_geometry_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q
git diff --check
```

Do not put the expensive long-window runtime into pytest. Pytest should verify
contracts and committed artifact schema. The Step117 runner should generate
the runtime artifacts before commit.

## Done Criteria

Step117 is done only when:

- the detailed goal file exists and is referenced by the active goal,
- the Step117 runner exists and supports the required CLI,
- Step117 trend diagnostics are covered by tests,
- Step117 artifact schema is covered by tests,
- Step117 report and docs are committed,
- runtime artifacts are generated or incomplete rows are honestly recorded,
- Step118 readiness is explicitly answered,
- focused and full verification commands pass,
- `git diff --check` passes,
- the finished code, docs, tests, and artifacts are committed,
- the commit is pushed to `origin/main`.
