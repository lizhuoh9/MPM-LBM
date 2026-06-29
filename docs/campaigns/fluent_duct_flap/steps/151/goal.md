# Step151 Goal: Targeted Solver Fix From Official Error Localization

## Source Contract

Step151 follows `origin/main = c599657a434d8550b69423ac5288aedca8c75459`.
Step150 is correctly implemented and honest: when the private official monitor
is absent, it reports `missing_official_monitor`, does not fabricate
displacement metrics, force metrics, phase-lag metrics, solver bug hypotheses,
or a Step151 target, and leaves validation and selected96 claims blocked.

The current hard blocker is still the missing private official monitor:

```text
benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv
```

Without that file, Step151 must not modify solver code. The only legal Step151
state in the current checkout is a checked-in blocked result that proves the
gate exists and refuses to proceed without real Step150 official-vs-solver
error localization.

## Objective

Add the Step151 targeted-fix entrypoint and contracts. Step151 must read the
real Step150 outputs and either:

- stop as `blocked_by_missing_error_localization` with `solver_code_modified =
  false` when Step150 did not complete real official error localization; or
- when Step150 has real metrics and a ranked top bug category, produce a
  category-specific targeted fix plan and require a later verified solver fix
  plus post-fix Step148/Step150 reruns before any improvement claim.

This step must not guess the solver bug category. It must use Step150 output as
the source of truth.

## Current Local Expected State

Because the private official monitor is not present in this checkout, running
Step151 against the current Step150 artifacts must produce:

```json
{
  "status": "blocked_by_missing_error_localization",
  "solver_code_modified": false,
  "reason": "Step150 has no real official comparison",
  "source_step150_status": "missing_official_monitor",
  "validation_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

It must not touch MPM, LBM, FSI coupling, geometry, monitor extraction, or
runtime solver formulas in this blocked state.

## Required Inputs

Step151 runner inputs:

```text
outputs/step150_official_monitor_error_localization/error_localization_summary.json
outputs/step150_official_monitor_error_localization/solver_bug_hypotheses.json
outputs/step150_official_monitor_error_localization/displacement_error_metrics.json
outputs/step150_official_monitor_error_localization/force_error_metrics.json
outputs/step150_official_monitor_error_localization/phase_lag_metrics.json
outputs/step148_our_solver_fluent_official_case/solver_reproduction_summary.json
outputs/step148_our_solver_fluent_official_case/geometry_mapping_report.json
outputs/step148_our_solver_fluent_official_case/unit_mapping_report.json
outputs/step148_our_solver_fluent_official_case/coupling_diagnostics_summary.json
```

Hard preconditions for a real targeted fix:

```text
Step150 status must be error_localization_complete
next_code_fix_step_identified must be true
solver_bug_hypotheses_present must be true
top_bug_category must be non-null
```

If any precondition is false or missing, Step151 must write the blocked result
and must not modify solver code.

## Step151 Taxonomy

Step151 must accept the Step149/150 bug taxonomy:

```text
geometry_mapping_error
unit_mapping_error
fluid_boundary_error
structural_model_error
coupling_force_transfer_error
solid_to_fluid_motion_error
time_integration_or_subcycling_error
monitor_extraction_error
numerical_stability_error
```

Unknown top categories must not trigger solver edits. They must produce a
blocked or review-required result that preserves validation and selected96
blocked flags.

## Category-Specific Planning Requirements

When Step150 is complete, Step151 must generate a targeted plan for exactly the
highest-confidence top bug category.

### geometry_mapping_error

Prioritize:

```text
official mesh/proxy geometry mapping
flap dimensions
flap base/fixed constraint
monitor point location
duct height/length/thickness
coordinate frame
```

The plan/report must include:

```text
official_mesh_metadata_mapped
proxy_geometry_gap_reported
monitor_point_mapping_error_reduced
```

Step151 does not have to import a full `.msh` mesh immediately, but it must at
least identify the official mesh metadata / flap anchor / monitor point / duct
dimension gap that a real fix would address.

### structural_model_error

Prioritize:

```text
MPM Young's modulus
solid density
damping
flap thickness / mass / volume
fixed-base mask
material unit scaling
```

The plan/report must reserve:

```text
outputs/step151_targeted_solver_fix/structural_mapping_fix_report.json
```

### coupling_force_transfer_error

Prioritize:

```text
fluid force sign convention
force area weighting
reaction force accumulation
force-to-particle distribution
force units
force monitor extraction
```

If force error is high, Step151 must first distinguish monitor/force extraction
from actual physics changes because Step148 force fields are report-only solver
force proxies, not direct Fluent wall-integral equivalence.

### time_integration_or_subcycling_error

Prioritize:

```text
FSI coupling interval
LBM steps per official FSI time
MPM dt
substep force accumulation
monitor sampling time
```

Step148 currently has 26 solver monitor rows over `0.0` to `0.125` seconds.
Official monitor time spacing and peak timing must be compared before changing
time integration parameters.

### monitor_extraction_error

Prioritize:

```text
flap-tip monitor point selection
component direction
total displacement definition
force component/magnitude definition
CSV extraction alignment
```

This category is a safer first fix than changing solver physics, but it still
requires Step150 real official metrics before activation.

## Required Files

Add:

```text
docs/campaigns/fluent_duct_flap/steps/151/goal.md
docs/campaigns/fluent_duct_flap/steps/151/report.md
experiments/steps/step151_targeted_solver_fix_from_official_error.py
tests/test_step151_targeted_solver_fix_from_official_error_contract.py
```

Generate:

```text
outputs/step151_targeted_solver_fix/step151_fix_plan.json
outputs/step151_targeted_solver_fix/step151_fix_report.json
outputs/step151_targeted_solver_fix/post_fix_step148_summary.json
outputs/step151_targeted_solver_fix/post_fix_step150_summary.json
outputs/step151_targeted_solver_fix/error_delta_report.json
outputs/step151_targeted_solver_fix/report.md
```

Update:

```text
docs/current/STATUS.md
docs/current/ACTIVE_CAMPAIGN.json
docs/current/READING_ORDER.md
docs/current/VALIDATION_GATES.md
```

## Runner Commands

First confirm Step150:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step150_official_monitor_intake_and_error_localization `
  --official-monitor benchmarks\private\fluent_fsi_2way\outputs\official_monitor.csv `
  --solver-monitor outputs\step148_our_solver_fluent_official_case\solver_monitor.csv `
  --solver-force-monitor outputs\step148_our_solver_fluent_official_case\solver_force_monitor.csv `
  --solver-summary outputs\step148_our_solver_fluent_official_case\solver_reproduction_summary.json `
  --output-dir outputs\step150_official_monitor_error_localization `
  --force
```

Then run Step151:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step151_targeted_solver_fix_from_official_error `
  --step150-summary outputs\step150_official_monitor_error_localization\error_localization_summary.json `
  --hypotheses outputs\step150_official_monitor_error_localization\solver_bug_hypotheses.json `
  --displacement-metrics outputs\step150_official_monitor_error_localization\displacement_error_metrics.json `
  --force-metrics outputs\step150_official_monitor_error_localization\force_error_metrics.json `
  --phase-lag-metrics outputs\step150_official_monitor_error_localization\phase_lag_metrics.json `
  --step148-summary outputs\step148_our_solver_fluent_official_case\solver_reproduction_summary.json `
  --geometry-report outputs\step148_our_solver_fluent_official_case\geometry_mapping_report.json `
  --unit-report outputs\step148_our_solver_fluent_official_case\unit_mapping_report.json `
  --coupling-report outputs\step148_our_solver_fluent_official_case\coupling_diagnostics_summary.json `
  --output-dir outputs\step151_targeted_solver_fix `
  --force
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step151-focused `
  tests\test_step148_our_solver_fluent_official_case_reproduction_contract.py `
  tests\test_step149_fluent_official_vs_our_solver_error_localization_contract.py `
  tests\test_step150_official_monitor_intake_and_error_localization_contract.py `
  tests\test_step151_targeted_solver_fix_from_official_error_contract.py
```

## Contract Tests

Add `tests/test_step151_targeted_solver_fix_from_official_error_contract.py`
covering:

1. Current Step150 `missing_official_monitor` summary produces
   `blocked_by_missing_error_localization`.
2. Missing Step150 summary produces `blocked_by_missing_error_localization`.
3. Step150 complete without `solver_bug_hypotheses_present` blocks.
4. Step150 complete without `top_bug_category` blocks.
5. Unknown top bug category produces review-required/blocked output and does
   not modify solver code.
6. Synthetic complete `geometry_mapping_error` produces a category-specific
   fix plan without claiming a solver change.
7. Synthetic complete `monitor_extraction_error` produces a monitor extraction
   plan without claiming validation.
8. All outputs preserve `validation_claim_allowed = false`.
9. All outputs preserve `selected96_execution_allowed = false`.
10. Blocked outputs write placeholder post-fix summaries and error delta report
    with no improvement claim.

Tests must be lightweight, must not require private official monitor data, and
must not run Fluent, selected96, or long solver jobs.

## Output Semantics

Blocked result:

```json
{
  "status": "blocked_by_missing_error_localization",
  "solver_code_modified": false,
  "reason": "Step150 has no real official comparison",
  "validation_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

Ready plan result for synthetic/real complete Step150:

```json
{
  "status": "targeted_fix_plan_ready",
  "source_step150_status": "error_localization_complete",
  "source_top_bug_category": "...",
  "solver_code_modified": false,
  "targeted_fix_applied": false,
  "requires_solver_patch": true,
  "post_fix_step148_run_executed": false,
  "post_fix_step150_comparison_executed": false,
  "error_delta_report_present": true,
  "primary_metric_improved": false,
  "validation_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

Actual `targeted_fix_applied` is not allowed in the current checkout because
Step150 has not completed real official comparison.

## Prohibited Actions

Do not:

```text
return to Step147 outlet repair
run selected96
claim validation, Fluent parity, Figure 29.3 parity, or production readiness
change MPM/LBM/FSI parameters based on guesses
commit official_monitor.csv
copy official Fluent payload into outputs or the repository
change solver runtime while Step150 is not error_localization_complete
write a design-only Step151 with no executable gate or tests
```

## Done Criteria

Step151 is complete when:

- The detailed goal file exists and the active goal references it.
- The Step151 runner and contract tests exist.
- The runner blocks cleanly on current Step150 `missing_official_monitor`
  artifacts and writes all required Step151 outputs.
- Synthetic complete Step150 fixtures produce category-specific targeted plans
  without solver edits or validation claims.
- No solver runtime files are modified in the current missing-official state.
- Current docs point to Step151 as the active gate after Step150.
- Focused Step148/149/150/151 tests pass with
  `D:\working\taichi\env\python.exe`.
- JSON and `git diff --check` verification pass.
- Private official monitor data is not staged or committed.
- Changes are committed, pushed to `origin/main`, and codebase-memory is
  refreshed.
