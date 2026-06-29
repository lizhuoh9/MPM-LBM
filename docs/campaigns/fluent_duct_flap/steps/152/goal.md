# Step152 Goal: Apply First Targeted Solver Fix From Official Error Localization

## Source Contract

Step152 follows `origin/main = 3a69bf030f85d12067d382de1500208519318a78`.
Step151 is a correct targeted-fix gate: it reads Step150 official
error-localization outputs and blocks solver patches when Step150 has no real
official comparison. It does not pretend to modify the solver while the private
official reference is absent.

The current hard blocker remains:

```text
benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv
```

That file is not present in this checkout. Therefore current Step150 status is
`missing_official_monitor`, current Step151 status is
`blocked_by_missing_error_localization`, and Step152 must not modify solver
runtime code in the current state.

## Objective

Add Step152 as the executable "apply targeted solver fix" step. It must read
the Step151 targeted fix plan and either:

- block honestly when Step151 is not `targeted_fix_plan_ready`; or
- when Step151 is ready from real Step150 official error localization, apply
  exactly one targeted solver patch for the single highest-priority
  `source_top_bug_category`, then require post-fix Step148/Step150 reruns and an
  error-delta report before any improvement claim.

Because the current checkout still lacks the private official monitor, the
current legal output is the blocked path. This is not a validation claim and
not a solver patch.

## Current Local Expected State

Running Step152 against the current checked-in Step151 artifacts must produce:

```json
{
  "status": "blocked_by_missing_targeted_fix_plan",
  "source_step151_status": "blocked_by_missing_error_localization",
  "source_step150_status": "missing_official_monitor",
  "solver_code_modified": false,
  "targeted_fix_applied": false,
  "post_fix_step148_run_executed": false,
  "post_fix_step150_comparison_executed": false,
  "primary_metric_improved": false,
  "validation_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

Step152 must not touch MPM, LBM, FSI coupling, geometry, monitor extraction, or
runtime solver formulas in this blocked state.

## Required Inputs

Step152 runner inputs:

```text
outputs/step151_targeted_solver_fix/step151_fix_report.json
outputs/step151_targeted_solver_fix/step151_fix_plan.json
outputs/step151_targeted_solver_fix/error_delta_report.json
outputs/step150_official_monitor_error_localization/error_localization_summary.json
outputs/step150_official_monitor_error_localization/solver_bug_hypotheses.json
outputs/step150_official_monitor_error_localization/displacement_error_metrics.json
outputs/step150_official_monitor_error_localization/force_error_metrics.json
outputs/step150_official_monitor_error_localization/phase_lag_metrics.json
outputs/step148_our_solver_fluent_official_case/solver_reproduction_summary.json
```

Hard preconditions for a real solver patch:

```text
Step151 status must be targeted_fix_plan_ready
Step151 source_step150_status must be error_localization_complete
Step151 source_top_bug_category must be non-null and registered
Step151 requires_solver_patch must be true
Step151 solver_code_modified must be false before Step152
Step151 targeted_fix_applied must be false before Step152
Step150 error_metrics_present must be true
Step150 solver_bug_hypotheses_present must be true
```

If any precondition is false or missing, Step152 must write the blocked result
and must not modify solver code.

## Targeted Patch Scope

When the hard preconditions pass, Step152 may apply exactly one patch for the
single Step151 `source_top_bug_category`. It must not fix multiple categories
in one run.

### geometry_mapping_error

Allowed focus:

```text
official mesh/proxy geometry mapping
flap dimensions
flap base/fixed constraint
monitor point location
duct height/length/thickness
coordinate frame
```

Required Step152 outputs after a real patch:

```text
official_mesh_metadata_mapped = true
proxy_geometry_gap_reported = true
monitor_point_mapping_error_reduced = true
```

This may add official geometry metadata intake from a private manifest or mesh
metadata. It must not commit private Fluent payloads.

### monitor_extraction_error

Allowed focus:

```text
flap-tip monitor point selection
component direction
total displacement definition
force component/magnitude definition
CSV extraction alignment
```

Required tests after a real patch include:

```text
tests/test_fsi_monitor_extraction_contract.py
```

### coupling_force_transfer_error

Allowed focus:

```text
fluid-to-solid force sign convention
reaction force accumulation
force area weighting
force unit mapping
force monitor extraction
```

Required tests after a real patch include:

```text
tests/test_fsi_force_transfer_units.py
```

Step148 current force outputs are solver diagnostic force proxies, not direct
Fluent wall-integral equivalence. Step152 must distinguish monitor/extraction
repairs from physics changes before modifying force-transfer formulas.

### structural_model_error

Allowed focus:

```text
MPM Young's modulus
solid density
damping
flap thickness / mass / volume
fixed-base mask
material unit scaling
```

### time_integration_or_subcycling_error

Allowed focus:

```text
official FSI dt mapping
LBM/MPM substep ratio
monitor sampling time
force averaging window
```

Required tests after a real patch include:

```text
tests/test_fsi_time_mapping_contract.py
```

## Required Files

Add:

```text
docs/campaigns/fluent_duct_flap/steps/152/goal.md
docs/campaigns/fluent_duct_flap/steps/152/report.md
experiments/steps/step152_apply_targeted_solver_fix.py
tests/test_step152_apply_targeted_solver_fix_contract.py
```

Generate:

```text
outputs/step152_apply_targeted_solver_fix/step152_apply_summary.json
outputs/step152_apply_targeted_solver_fix/step152_patch_plan.json
outputs/step152_apply_targeted_solver_fix/modified_modules_report.json
outputs/step152_apply_targeted_solver_fix/post_fix_step148_summary.json
outputs/step152_apply_targeted_solver_fix/post_fix_step150_summary.json
outputs/step152_apply_targeted_solver_fix/error_delta_report.json
outputs/step152_apply_targeted_solver_fix/report.md
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
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step152_apply_targeted_solver_fix `
  --step151-report outputs\step151_targeted_solver_fix\step151_fix_report.json `
  --step151-plan outputs\step151_targeted_solver_fix\step151_fix_plan.json `
  --step151-error-delta outputs\step151_targeted_solver_fix\error_delta_report.json `
  --step150-summary outputs\step150_official_monitor_error_localization\error_localization_summary.json `
  --hypotheses outputs\step150_official_monitor_error_localization\solver_bug_hypotheses.json `
  --displacement-metrics outputs\step150_official_monitor_error_localization\displacement_error_metrics.json `
  --force-metrics outputs\step150_official_monitor_error_localization\force_error_metrics.json `
  --phase-lag-metrics outputs\step150_official_monitor_error_localization\phase_lag_metrics.json `
  --step148-summary outputs\step148_our_solver_fluent_official_case\solver_reproduction_summary.json `
  --output-dir outputs\step152_apply_targeted_solver_fix `
  --force
```

## Contract Tests

Add `tests/test_step152_apply_targeted_solver_fix_contract.py` covering:

1. Current Step151 `blocked_by_missing_error_localization` produces
   `blocked_by_missing_targeted_fix_plan`.
2. Missing Step151 report produces `blocked_by_missing_targeted_fix_plan`.
3. Step151 report missing `source_top_bug_category` blocks.
4. Step151 report with unknown category blocks and requires human review.
5. Synthetic `targeted_fix_plan_ready` for `geometry_mapping_error` produces a
   category-specific apply plan but does not claim a solver patch unless an
   explicit patch implementation is present.
6. Synthetic `targeted_fix_plan_ready` for `monitor_extraction_error` produces
   a category-specific apply plan with expected tests.
7. Current blocked output writes placeholder post-fix Step148/Step150 summaries
   and error-delta report with `primary_metric_improved = false`.
8. All paths preserve `validation_claim_allowed = false`.
9. All paths preserve `selected96_execution_allowed = false`.
10. Current missing-official state modifies no solver runtime files.

Tests must be lightweight. They must not require private official monitor data,
must not run Fluent, must not run selected96, and must not perform long solver
jobs.

## Output Semantics

Blocked result:

```json
{
  "status": "blocked_by_missing_targeted_fix_plan",
  "source_step151_status": "blocked_by_missing_error_localization",
  "source_step150_status": "missing_official_monitor",
  "solver_code_modified": false,
  "targeted_fix_applied": false,
  "validation_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

Ready but not implemented result for a synthetic ready plan:

```json
{
  "status": "targeted_fix_patch_required",
  "source_step151_status": "targeted_fix_plan_ready",
  "source_top_bug_category": "...",
  "solver_code_modified": false,
  "targeted_fix_applied": false,
  "patch_implementation_present": false,
  "validation_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

Actual applied result, allowed only after a real Step151 ready plan and a real
category-specific patch:

```json
{
  "status": "targeted_fix_applied",
  "source_step151_status": "targeted_fix_plan_ready",
  "source_top_bug_category": "...",
  "solver_code_modified": true,
  "modified_modules": ["..."],
  "new_tests_added": true,
  "post_fix_step148_run_executed": true,
  "post_fix_step150_comparison_executed": true,
  "error_delta_report_present": true,
  "primary_metric_improved": true,
  "validation_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

If a real patch runs but the metric does not improve, Step152 must report:

```json
{
  "status": "targeted_fix_applied_no_metric_improvement",
  "primary_metric_improved": false,
  "next_action": "revert_or_reclassify",
  "validation_claim_allowed": false
}
```

## Prohibited Actions

Do not:

```text
continue to Step153/154 gate-only work
return to LBM outlet-controller repair
run selected96
claim validation, Fluent parity, Figure 29.3 parity, or production readiness
change MPM/LBM/FSI parameters while Step151 is blocked
commit official_monitor.csv
commit private Fluent payload
modify multiple bug categories in one Step152 run
fake post-fix Step148/Step150 reruns
fake primary metric improvement
```

## Done Criteria

Step152 is complete for the current checkout when:

- The detailed goal file exists and the active goal references it.
- The Step152 runner and contract tests exist.
- The current missing-official state produces
  `blocked_by_missing_targeted_fix_plan`.
- Current Step152 artifacts exist and state that no solver runtime code was
  modified.
- Synthetic ready-plan fixtures produce category-specific patch-required plans
  without validation claims or fake solver modifications.
- No private official monitor data is staged or committed.
- No solver runtime files are modified while Step151 is blocked.
- Current docs point to Step152 as the active gate after Step151.
- Focused Step148/149/150/151/152 tests pass with
  `D:\working\taichi\env\python.exe`.
- JSON and `git diff --check` verification pass.
- Changes are committed, pushed to `origin/main`, and codebase-memory is
  refreshed.
