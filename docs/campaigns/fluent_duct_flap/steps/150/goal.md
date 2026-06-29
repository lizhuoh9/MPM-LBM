# Step150 Goal: Fluent Official Monitor Intake and Real Error Localization

## Source Contract

Step150 follows `origin/main = a0385a395376ab96b9b67dcceec4cf66d376b162`.
Step148 correctly changed direction by running this repository's `FSIDriver3D`
MPM-LBM/FSI solver and writing comparison-ready solver monitors. Step149
correctly added an official-vs-solver error-localization pipeline, but the
current artifact state is blocked because the private official monitor is not
present in this checkout.

The current state to preserve:

- Step148 ran our solver, not Fluent.
- Step148 wrote `outputs/step148_our_solver_fluent_official_case/solver_monitor.csv`
  with 26 rows from step 0 to step 250.
- Step148 force monitor values are report-only solver force proxies, not direct
  Fluent wall-integral equivalence.
- Step148 geometry is still `proxy_geometry_mapped`; it does not import the
  official mesh.
- Step149 loaded the Step148 solver monitor.
- Step149 reported `missing_official_monitor` /
  `official_reference_missing`.
- Step149 did not fabricate metrics, bug hypotheses, or a Step150 solver-fix
  target.
- selected96, Fluent validation, Figure parity, production readiness, and
  Step151 solver changes remain blocked.

Step150 is the official monitor intake wrapper and real error-localization
step. It must not fix the solver. It must validate the local official monitor,
record private-file metadata without committing private data, then run the
existing Step149 comparison logic when the official monitor is usable.

## Objective

Connect the local official monitor at:

```text
benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv
```

to the Step149 comparison pipeline and emit either:

- a real official-vs-solver error-localization result with metrics, ranked bug
  hypotheses, and a Step151 target; or
- a precise blocked state (`missing_official_monitor`, `schema_invalid`,
  `missing_solver_monitor`, or `no_time_overlap`) with no fabricated metrics or
  hypotheses.

## Scope Boundaries

Step150 must:

- Validate official monitor existence, schema, row count, hash, monotonic time,
  and time overlap with the Step148 solver monitor.
- Reuse Step149 comparison behavior for real metric and hypothesis generation.
- Write official monitor metadata and hash, but never copy or commit the
  private official CSV.
- Preserve validation and selected96 blocked flags.
- Identify Step151 only when real hypotheses are present.

Step150 must not:

- Run Fluent.
- Modify solver formulas, `FSIDriver3D`, LBM, MPM, coupling, geometry, or
  monitor extraction logic.
- Re-run Step148 unless a later contract explicitly asks for it.
- Touch Step121, selected96, selected-static, or Step147 outlet-controller
  repair code.
- Commit `benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv` or
  any private Fluent payload.
- Fabricate official reference rows, error metrics, force metrics, phase-lag
  metrics, bug hypotheses, or Step151 targets.

## Inputs

Official reference:

```text
benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv
```

Required minimum official monitor columns:

```text
time_s
flap_tip_total_displacement_m
```

Recommended official monitor columns:

```text
flap_tip_x_displacement_m
flap_tip_y_displacement_m
fluid_force_magnitude_n
fluid_force_x_n
fluid_force_y_n
```

Step148 solver inputs:

```text
outputs/step148_our_solver_fluent_official_case/solver_monitor.csv
outputs/step148_our_solver_fluent_official_case/solver_force_monitor.csv
outputs/step148_our_solver_fluent_official_case/solver_reproduction_summary.json
outputs/step148_our_solver_fluent_official_case/geometry_mapping_report.json
outputs/step148_our_solver_fluent_official_case/unit_mapping_report.json
outputs/step148_our_solver_fluent_official_case/coupling_diagnostics_summary.json
```

## Required Files

Add:

```text
docs/campaigns/fluent_duct_flap/steps/150/goal.md
docs/campaigns/fluent_duct_flap/steps/150/report.md
experiments/steps/step150_official_monitor_intake_and_error_localization.py
tests/test_step150_official_monitor_intake_and_error_localization_contract.py
```

Generate:

```text
outputs/step150_official_monitor_error_localization/official_monitor_intake_summary.json
outputs/step150_official_monitor_error_localization/official_monitor_schema_report.json
outputs/step150_official_monitor_error_localization/official_monitor_private_hash_report.json
outputs/step150_official_monitor_error_localization/aligned_monitor_comparison.csv
outputs/step150_official_monitor_error_localization/displacement_error_metrics.json
outputs/step150_official_monitor_error_localization/force_error_metrics.json
outputs/step150_official_monitor_error_localization/phase_lag_metrics.json
outputs/step150_official_monitor_error_localization/solver_bug_hypotheses.json
outputs/step150_official_monitor_error_localization/error_localization_summary.json
outputs/step150_official_monitor_error_localization/step150_decision_summary.json
outputs/step150_official_monitor_error_localization/report.md
```

Update:

```text
docs/current/STATUS.md
docs/current/ACTIVE_CAMPAIGN.json
docs/current/READING_ORDER.md
docs/current/VALIDATION_GATES.md
```

## Runner Command

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step150_official_monitor_intake_and_error_localization `
  --official-monitor benchmarks\private\fluent_fsi_2way\outputs\official_monitor.csv `
  --solver-monitor outputs\step148_our_solver_fluent_official_case\solver_monitor.csv `
  --solver-force-monitor outputs\step148_our_solver_fluent_official_case\solver_force_monitor.csv `
  --solver-summary outputs\step148_our_solver_fluent_official_case\solver_reproduction_summary.json `
  --output-dir outputs\step150_official_monitor_error_localization `
  --force
```

## Required Intake Behavior

Step150 must:

1. Check whether the official monitor path exists.
2. Check whether the Step148 solver monitor exists.
3. Read official monitor header and row count when present.
4. Require a `time_s` column.
5. Require a displacement column compatible with Step149 aliases, preferably
   `flap_tip_total_displacement_m`.
6. Detect optional force columns compatible with Step149 aliases.
7. Validate that `time_s` values are finite and strictly monotonic
   non-decreasing.
8. Validate that official and solver time ranges overlap before invoking
   Step149 comparison.
9. Write SHA-256 hash and size for the official monitor when present.
10. Report `official_monitor_committed = false`.
11. Record official monitor columns, row count, time range, displacement column,
    optional force column, and validation status.

## Required Statuses

Missing official monitor:

```json
{
  "status": "missing_official_monitor",
  "error_metrics_present": false,
  "solver_bug_hypotheses_present": false,
  "next_code_fix_step_identified": false,
  "validation_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

Missing solver monitor:

```json
{
  "status": "missing_solver_monitor",
  "error_metrics_present": false,
  "solver_bug_hypotheses_present": false,
  "next_code_fix_step_identified": false
}
```

Invalid schema:

```json
{
  "status": "schema_invalid",
  "schema_valid": false,
  "schema_errors": ["..."],
  "error_metrics_present": false,
  "solver_bug_hypotheses_present": false,
  "next_code_fix_step_identified": false
}
```

No time overlap:

```json
{
  "status": "no_time_overlap",
  "error_metrics_present": false,
  "solver_bug_hypotheses_present": false,
  "next_code_fix_step_identified": false
}
```

Success:

```json
{
  "status": "error_localization_complete",
  "official_reference_loaded": true,
  "solver_monitor_loaded": true,
  "official_monitor_hash": "...",
  "official_monitor_rows": "> 0",
  "solver_monitor_rows": 26,
  "aligned_sample_count": "> 1",
  "error_metrics_present": true,
  "solver_bug_hypotheses_present": true,
  "top_bug_category": "...",
  "next_code_fix_step_identified": true,
  "recommended_next_step": 151,
  "validation_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

## Contract Tests

Add `tests/test_step150_official_monitor_intake_and_error_localization_contract.py`
covering:

1. Missing official monitor -> `missing_official_monitor`.
2. Missing solver monitor -> `missing_solver_monitor`.
3. Official monitor missing `time_s` -> `schema_invalid`.
4. Official monitor missing displacement -> `schema_invalid`.
5. Official monitor non-monotonic `time_s` -> `schema_invalid`.
6. Official / solver monitor no overlap -> `no_time_overlap`.
7. Synthetic official + solver monitor -> real metrics and hypotheses.
8. `official_monitor_committed = false`.
9. `official_monitor_hash` present when official monitor exists.
10. `top_bug_category` present when metrics are present.
11. `next_code_fix_step_identified = true` when hypotheses are present.
12. `validation_claim_allowed = false`.
13. `selected96_execution_allowed = false`.

Tests must be lightweight and must not require a private official monitor in
the repository.

## Report Requirements

`docs/campaigns/fluent_duct_flap/steps/150/report.md` and
`outputs/step150_official_monitor_error_localization/report.md` must state:

- whether the official monitor was found;
- row count and time range when available;
- schema status and schema errors;
- whether Step149 comparison ran;
- whether real metrics and hypotheses were emitted;
- top bug category and recommended next step when present;
- that validation and selected96 remain blocked;
- that private official CSV data was not committed.

## Done Criteria

Step150 is complete when:

- The detailed goal file exists and the active goal references it.
- Step150 runner and contract tests are implemented.
- Current docs point to Step150 as the active intake/error-localization gate.
- Step150 output artifacts exist for the current local state.
- If the official monitor is missing, artifacts honestly report
  `missing_official_monitor`.
- If a synthetic official monitor is used in tests, metrics and hypotheses are
  generated and Step151 is identified only there.
- Focused verification passes with the trusted interpreter.
- `git diff --check` passes.
- Changes are committed and pushed to `origin/main`.
- codebase-memory MCP is refreshed after push.
