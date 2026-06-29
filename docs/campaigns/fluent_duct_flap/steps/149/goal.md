# Step149 Goal: Fluent Official vs Our-Solver Error Localization

## Source Contract

Step149 consumes official local monitor data and Step148 our-solver monitor
data. Its job is not to claim validation. Its job is to quantify the mismatch,
map the error features to likely solver bug classes, and identify the highest
confidence target for Step150.

Step149 must not run Fluent and must not modify solver code. Solver fixes belong
to Step150 after Step149 ranks the top bug hypothesis.

## Inputs

Official reference:

```text
benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv
```

Our solver artifacts from Step148:

```text
outputs/step148_our_solver_fluent_official_case/solver_monitor.csv
outputs/step148_our_solver_fluent_official_case/solver_force_monitor.csv
outputs/step148_our_solver_fluent_official_case/solver_reproduction_summary.json
outputs/step148_our_solver_fluent_official_case/geometry_mapping_report.json
outputs/step148_our_solver_fluent_official_case/unit_mapping_report.json
outputs/step148_our_solver_fluent_official_case/coupling_diagnostics_summary.json
```

If the official monitor is missing, Step149 must output
`missing_official_monitor` and must not fabricate error metrics. If the solver
monitor is missing, Step149 must output `missing_solver_monitor`.

## Required Files

Add:

```text
docs/campaigns/fluent_duct_flap/steps/149/goal.md
docs/campaigns/fluent_duct_flap/steps/149/report.md
experiments/steps/step149_fluent_official_vs_our_solver_error_localization.py
tests/test_step149_fluent_official_vs_our_solver_error_localization_contract.py
```

Generate:

```text
outputs/step149_fluent_official_vs_our_solver_error_localization/aligned_monitor_comparison.csv
outputs/step149_fluent_official_vs_our_solver_error_localization/displacement_error_metrics.json
outputs/step149_fluent_official_vs_our_solver_error_localization/force_error_metrics.json
outputs/step149_fluent_official_vs_our_solver_error_localization/phase_lag_metrics.json
outputs/step149_fluent_official_vs_our_solver_error_localization/solver_bug_hypotheses.json
outputs/step149_fluent_official_vs_our_solver_error_localization/error_localization_summary.json
outputs/step149_fluent_official_vs_our_solver_error_localization/report.md
```

Update current docs with Step149 status once artifacts exist.

## Runner Command

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step149_fluent_official_vs_our_solver_error_localization `
  --official-monitor benchmarks\private\fluent_fsi_2way\outputs\official_monitor.csv `
  --solver-monitor outputs\step148_our_solver_fluent_official_case\solver_monitor.csv `
  --solver-force-monitor outputs\step148_our_solver_fluent_official_case\solver_force_monitor.csv `
  --solver-summary outputs\step148_our_solver_fluent_official_case\solver_reproduction_summary.json `
  --output-dir outputs\step149_fluent_official_vs_our_solver_error_localization `
  --force
```

## Required Metrics

Displacement:

- RMS error.
- Normalized RMS error.
- Peak amplitude error.
- Peak time error.
- Final displacement error.
- Correlation.
- Sign agreement.

Force:

- RMS force error.
- Normalized RMS force error.
- Peak force error.
- Impulse mismatch.
- Force/displacement phase lag.

Time:

- Official time range.
- Solver time range.
- Overlap time range.
- Interpolation method.

## Error Classification

Step149 must emit ranked hypotheses with category, confidence, evidence, and
suspect modules. Allowed categories:

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

Example payload shape:

```json
{
  "ranked_solver_bug_hypotheses": [
    {
      "category": "coupling_force_transfer_error",
      "confidence": 0.82,
      "evidence": [
        "force sign mismatch",
        "force peak timing inconsistent with displacement"
      ],
      "suspect_modules": [
        "fluid-to-solid force accumulation",
        "boundary reaction transfer",
        "MPM force application"
      ]
    }
  ]
}
```

## Required Summary Fields

`error_localization_summary.json` must include:

```json
{
  "step": 149,
  "official_reference_loaded": true,
  "solver_monitor_loaded": true,
  "error_metrics_present": true,
  "solver_bug_hypotheses_present": true,
  "top_bug_hypothesis": "...",
  "next_code_fix_step_identified": true,
  "validation_claim_allowed": false,
  "selected96_execution_allowed": false
}
```

When official reference is missing:

```json
{
  "status": "missing_official_monitor",
  "official_reference_loaded": false,
  "error_metrics_present": false,
  "solver_bug_hypotheses_present": false,
  "validation_claim_allowed": false
}
```

## Step149 Contract Tests

Add tests that prove:

1. Missing official monitor produces `missing_official_monitor`.
2. Missing solver monitor produces `missing_solver_monitor`.
3. Synthetic aligned official/solver monitors produce displacement, force, and
   phase metrics.
4. Known force sign/timing synthetic errors rank
   `coupling_force_transfer_error`.
5. Known amplitude/frequency synthetic errors rank `structural_model_error` or
   `time_integration_or_subcycling_error` as appropriate.
6. Each top hypothesis includes non-empty `suspect_modules`.
7. Validation, selected96, Fluent parity, FSI validation, and production
   readiness remain blocked.

## Verification Commands

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step149-red `
  tests\test_step149_fluent_official_vs_our_solver_error_localization_contract.py

& 'D:\working\taichi\env\python.exe' -m experiments.steps.step149_fluent_official_vs_our_solver_error_localization `
  --official-monitor benchmarks\private\fluent_fsi_2way\outputs\official_monitor.csv `
  --solver-monitor outputs\step148_our_solver_fluent_official_case\solver_monitor.csv `
  --solver-force-monitor outputs\step148_our_solver_fluent_official_case\solver_force_monitor.csv `
  --solver-summary outputs\step148_our_solver_fluent_official_case\solver_reproduction_summary.json `
  --output-dir outputs\step149_fluent_official_vs_our_solver_error_localization `
  --force

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step149-focused `
  tests\test_step149_fluent_official_vs_our_solver_error_localization_contract.py
```

## Completion Criteria

Step149 is complete only when:

- The goal is committed under this path.
- A RED contract test fails before implementation.
- Step149 comparison runner exists.
- Missing-input paths produce explicit summaries.
- When both monitors are available, metrics and ranked bug hypotheses are
  generated.
- Committed Step149 artifacts include the required JSON/CSV/report outputs.
- Current docs point to Step149 as the error-localization track.
- No validation or selected-boundary claim is made.
- Focused tests pass.
- JSON artifacts load successfully.
- `git diff --check` passes.
- The final commit is pushed to `origin/main`, with remote ref proof.
