# Step145 Goal: Mass-Neutral Long-Window Failure Forensics

## Scope

Step145 is an artifact-only forensic step after Step144.  It must explain why
the Step143 high mass-neutral setting improved the 250-step diagnostic window
but failed the Step144 48^3 / 500-step final hard gate.

Step145 must not promote anything into selected candidate review.  Step144
finished the single 48^3 / 500-step row and stayed finite, but failed final
hard gates through mass acceptance, mean flux imbalance, and outlet
stationarity.  Therefore the correct Step145 surface is failure-mechanism
classification, not promotion.

## Hard Boundaries

Step145 must preserve every boundary below:

- No new LBM run.
- No new Step121 phase.
- No new 48^3 real row.
- No new 500-step row.
- No selected96 execution.
- No selected-static execution.
- No 96^3 execution.
- No Fluent execution.
- No FSI execution.
- No validation claim.
- No gate relaxation.
- No selected-candidate-surface review.
- No synthetic mechanism conclusion when required inputs are missing.

## Required Inputs

Step145 may read only the Step144 artifacts plus declared Step143 and Step140
context artifacts:

- `outputs/step144_mass_neutral_final48/step144_decision_summary.json`
- `outputs/step144_mass_neutral_final48/step144_long_window_comparison.json`
- `outputs/step144_mass_neutral_final48/mass_neutral_final48/*/finite_stability_report.json`
- `outputs/step144_mass_neutral_final48/mass_neutral_final48/*/flow_development_diagnostics.csv`
- `outputs/step144_mass_neutral_final48/mass_neutral_final48/*/flow_development_diagnostics_summary.json`
- `outputs/step144_mass_neutral_final48/mass_neutral_final48/*/boundary_flux_timeseries.csv`
- `outputs/step144_mass_neutral_final48/mass_neutral_final48/*/density_drift_timeseries.csv`
- `outputs/step143_mass_neutral_design_diagnostic/step143_decision_summary.json`
- `outputs/step143_mass_neutral_design_diagnostic/step143_mass_neutral_comparison.json`
- `outputs/step140_long_window_drift_forensics/step140_failure_mechanism_summary.json`

If any required Step144 critical input is missing, Step145 must emit a
`missing_input` status and must not emit a classified dominant mechanism.

## Files To Add

- `docs/campaigns/fluent_duct_flap/steps/145/goal.md`
- `docs/campaigns/fluent_duct_flap/steps/145/report.md`
- `experiments/steps/step145_mass_neutral_long_window_forensics.py`
- `tests/test_step145_mass_neutral_long_window_forensics_contract.py`
- `outputs/step145_mass_neutral_long_window_forensics/saturation_segment_report.json`
- `outputs/step145_mass_neutral_long_window_forensics/stationarity_segment_report.json`
- `outputs/step145_mass_neutral_long_window_forensics/mass_neutral_error_segment_report.json`
- `outputs/step145_mass_neutral_long_window_forensics/controller_lag_segment_report.json`
- `outputs/step145_mass_neutral_long_window_forensics/step145_failure_mechanism_summary.json`
- `outputs/step145_mass_neutral_long_window_forensics/step145_failure_mechanism_summary.md`

## Files To Update

- `docs/current/ACTIVE_CAMPAIGN.json`
- `docs/current/STATUS.md`
- `docs/current/VALIDATION_GATES.md`
- `docs/current/READING_ORDER.md`
- `README.md` only if the current reading path needs a Step145 pointer.

`ACTIVE_CAMPAIGN.json` must also record:

- `final_repository_head_after_step144_push = 6fdf9bddea667bdbf36ab0f8e802c12db2a0def5`
- A commit identity note that distinguishes the Step144 runtime commit from the
  final Step144 docs/tests/artifacts push.

## Segment Windows

The Step145 segment reports must include exactly these analysis windows:

- `0_100`
- `100_200`
- `200_250`
- `250_300`
- `300_400`
- `400_500`
- `tail_80pct_diagnostic`
- `tail_20pct_hard_gate`

The 250-300 segment is important because earlier long-window diagnostics
showed post-250 excursion behavior.  The 400-500 segment is the Step144 final
hard-gate tail.

## Required Metrics

For each available window, compute and record:

- `mass_total_delta_rel`: mean, final, slope, max_abs.
- `flux_imbalance_rel`: mean, max, slope.
- `outlet_flux`: mean, coefficient of variation, slope.
- `outlet_to_inlet_flux_ratio`: mean, slope.
- `midplane_to_inlet_flux_ratio`: mean, slope.
- Controller target outlet flux: mean, coefficient of variation, slope.
- Controller measured outlet flux: mean, coefficient of variation, slope.
- Controller filtered flux error: mean, slope.
- Controller velocity feedback: mean, abs_mean, slope.
- Controller authority ratio: mean, slope.
- Controller saturation fraction or saturation proxy when telemetry exists.
- Drop-guard activation fraction or proxy when telemetry exists.
- `mass_neutral_mass_error`: mean, final, slope, max_abs.
- `mass_neutral_rho_feedback`: mean, abs_mean, slope.
- `mass_neutral_feedback_saturation_fraction`.
- `mass_neutral_feedback_update_count`.
- `near_outlet_to_outlet_flux_ratio`: mean, slope when telemetry exists.
- X-profile flux samples when telemetry exists.
- Collapse markers from the Step144 diagnostics summary.

## Mechanism Questions

Step145 must answer these questions without running a new solver row:

1. Is the mass-neutral cap too low, or is the feedback direction/location
   insufficient?
   - A1: cap too low.
   - A2: gain/cap arrives too late because of lag.
   - A3: outlet density offset is the wrong or insufficient actuator.
   - A4: mass error is coupled to outlet stationarity, not only a mass offset.
2. Is outlet CV caused by the mass-neutral feedback, or is the original
   plane-flux stationarity failure recurring?
   - Compare Step144 outlet CV and flux imbalance against Step140/Step139
     long-window forensics where available.
3. Why does the Step143 250-step improvement not extrapolate to Step144 500?
   - Generate a 250-equivalent versus 500-final comparison.
   - Do not interpret a 250-step pass as long-window readiness.

## Decision Cases

The final Step145 summary must choose one of:

- `mass_neutral_cap_saturation_dominant`
- `stationarity_drift_dominant`
- `controller_lag_or_slew_dominant`
- `mass_neutral_actuator_insufficient`
- `mixed_saturation_stationarity_failure`
- `mechanism_unresolved`

The expected likely outcomes from current Step144 telemetry are
`mixed_saturation_stationarity_failure` or
`mass_neutral_actuator_insufficient`.  The implementation must let the artifacts
decide.

## Required Summary Fields

`step145_failure_mechanism_summary.json` must include:

```json
{
  "step": 145,
  "status": "mechanism_classified",
  "source_step": 144,
  "source_step144_decision_case": "mass_neutral_flow_stationarity_long_window_failure",
  "new_lbm_run_executed": false,
  "new_parameter_tuning_executed": false,
  "selected96_execution_allowed": false,
  "validation_claim_allowed": false,
  "selected_candidate_surface_review_allowed": false,
  "step146_250step_diagnostic_proposal_allowed": true,
  "step146_500step_probe_allowed": false,
  "dominant_failure_mechanism": "...",
  "recommended_next_step": "..."
}
```

It must also keep the next recommendation list to at most one item.

## Contract Tests

`tests/test_step145_mass_neutral_long_window_forensics_contract.py` must cover:

1. Step145 reads Step144 artifacts plus declared Step143/Step140 context only.
2. Missing Step144 input produces `missing_input` and no synthetic mechanism.
3. No Step121 phase is added.
4. No selected96, selected-static, 96^3, Fluent, FSI, or 500-step command exists.
5. Segment windows contain the required eight windows.
6. The saturation report includes `mass_neutral_feedback_saturation_fraction`.
7. The stationarity report includes outlet flux CV and flux imbalance mean.
8. The controller lag report includes authority ratio and filtered error.
9. The failure summary blocks selected96 and validation claims.
10. The failure summary blocks selected-candidate-surface review.
11. The recommended next-step list has length no greater than one.
12. Current docs preserve Step144 failure and the blocked selected96 state.

## Verification Commands

Use the trusted local interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step145-red `
  tests\test_step145_mass_neutral_long_window_forensics_contract.py

& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step145_mass_neutral_long_window_forensics.py `
  tests\test_step145_mass_neutral_long_window_forensics_contract.py

& 'D:\working\taichi\env\python.exe' -m experiments.steps.step145_mass_neutral_long_window_forensics `
  --step144-root outputs\step144_mass_neutral_final48 `
  --step143-root outputs\step143_mass_neutral_design_diagnostic `
  --step140-root outputs\step140_long_window_drift_forensics `
  --output-dir outputs\step145_mass_neutral_long_window_forensics `
  --force

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step145-focused `
  tests\test_step145_mass_neutral_long_window_forensics_contract.py `
  tests\test_step144_mass_neutral_final48_contract.py `
  tests\test_step143_mass_neutral_design_contract.py `
  tests\test_step142_mass_neutral_plane_flux_design_contract.py `
  tests\test_step141_density_feedback_isolation_contract.py `
  tests\test_step140_long_window_drift_forensics_contract.py

& 'D:\working\taichi\env\python.exe' -c "<json load check for Step145 artifacts and current docs>"

git diff --check
```

## Completion Criteria

Step145 is complete only when:

- The RED test fails before implementation for the missing Step145 surface.
- The Step145 forensics script emits all required reports from existing
  artifacts only.
- Focused Step140-Step145 regression passes.
- Generated JSON artifacts load successfully.
- Current docs preserve Step144 failure and blocked selected96/validation
  status.
- `git diff --check` passes.
- The final commit is pushed to `origin/main`.

