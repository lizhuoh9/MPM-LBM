# Step145 Report: Mass-Neutral Long-Window Failure Forensics

Step145 is an artifact-only forensic read of Step144, Step143, and Step140
outputs. It did not run a new solver row and did not change promotion gates.

Step144 failed the final hard gate. The single Step144 row completed 500/500
and stayed finite, but failed mass acceptance, mean flux imbalance, and outlet
stationarity:

- `candidate_mass_acceptance_observed_abs = 0.007345390662776274`
- `flux_imbalance_rel_tail_mean = 0.1023209978570283`
- `outlet_flux_tail_cv = 0.11500661338208944`
- `mass_neutral_feedback_saturation_fraction_tail = 0.9374677783363148`
- `mass_neutral_mass_error_final = 0.0077638872899115086`
- `mass_neutral_rho_feedback_tail_mean = -0.0010000000474974513`

Step145 classifies the dominant mechanism as
`mixed_saturation_stationarity_failure`. The mass-neutral density offset was
near cap through most of the hard-gate tail while both mass acceptance and
outlet stationarity remained outside gate. Step140 already classified the
original long-window failure as `mass_accumulation_with_outlet_stationarity_drift`,
and Step145 sees the same stationarity signal recurring after the Step143
mass-neutral design.

The 250-step Step143 best row does not extrapolate to 500-step readiness:

- Step143 best 250-step mass abs: `0.0031636249081530357`
- Step143 best 250-step outlet CV: `0.09161249772040454`
- Step143 best 250-step mean flux imbalance: `0.08579940196467845`
- Step144 500-step mass abs: `0.007345390662776274`
- Step144 500-step outlet CV: `0.11500661338208944`
- Step144 500-step mean flux imbalance: `0.1023209978570283`

## Boundary Statements

Step145 did not run a new LBM row.
Step145 did not add a Step121 phase.
Step145 did not run selected96.
Step145 did not run selected-static.
Step145 did not run 96^3.
Step145 did not run a 500-step row.
Step145 did not run Fluent.
Step145 did not run FSI.
Step145 does not make a validation claim.
Step145 keeps selected-candidate-surface review blocked.
Step145 keeps selected96 blocked.

## Outputs

Step145 generated:

- `outputs/step145_mass_neutral_long_window_forensics/saturation_segment_report.json`
- `outputs/step145_mass_neutral_long_window_forensics/stationarity_segment_report.json`
- `outputs/step145_mass_neutral_long_window_forensics/mass_neutral_error_segment_report.json`
- `outputs/step145_mass_neutral_long_window_forensics/controller_lag_segment_report.json`
- `outputs/step145_mass_neutral_long_window_forensics/step145_failure_mechanism_summary.json`
- `outputs/step145_mass_neutral_long_window_forensics/step145_failure_mechanism_summary.md`

The summary keeps `selected96_execution_allowed = false`,
`validation_claim_allowed = false`, and
`selected_candidate_surface_review_allowed = false`.

## Recommendation

The single recommendation is: Step146 should be a design proposal for coupled
mass-neutral saturation and stationarity failure. It should not run selected96,
selected-static, 96^3, or a 500-step probe from the current evidence.

