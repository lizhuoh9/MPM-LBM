# Step140 Long-Window Drift Forensics Report

Step140 is a forensics-only diagnosis of the existing Step139 48^3 /
500-step artifacts. It did not add a Step121 phase, did not run a new LBM
simulation, did not tune parameters, and did not enable selected96 execution.

## Inputs

- Source artifacts: `outputs/step139_planeflux_final48`
- Source row: the single Step139 `planeflux_final48` row copied from the
  Step138 passing short-window parameters.
- Source outcome: Step139 completed 500/500 and stayed finite, but failed the
  final hard gate on candidate mass acceptance, mean flux imbalance, and outlet
  stationarity.
- Step140 artifacts: `outputs/step140_long_window_drift_forensics`

## Generated Artifacts

Step140 generated these report-only artifacts from the Step139 CSV/JSON output:

- `outputs/step140_long_window_drift_forensics/mass_drift_segment_report.json`
- `outputs/step140_long_window_drift_forensics/flux_stationarity_segment_report.json`
- `outputs/step140_long_window_drift_forensics/controller_response_segment_report.json`
- `outputs/step140_long_window_drift_forensics/x_profile_evolution_report.json`
- `outputs/step140_long_window_drift_forensics/step140_failure_mechanism_summary.json`
- `outputs/step140_long_window_drift_forensics/step140_failure_mechanism_summary.md`

The parser used fixed windows: `0_100`, `100_200`, `200_250`, `250_300`,
`300_400`, `400_500`, `tail_80pct_diagnostic`, and
`tail_20pct_hard_gate`.

## Diagnosis

The dominant failure mechanism is
`mass_accumulation_with_outlet_stationarity_drift`.

Step139 looked promotable at the Step138 250-step window, but the long window
shows renewed mass accumulation immediately after that point. The
`200_250` segment ended with `mass_total_delta_rel = 0.003974863988826804`,
inside the candidate mass-acceptance limit. The `250_300` segment then rose to
`mass_total_delta_rel = 0.010577758938477861` with
`slope_per_step = 0.00013628106427297047`. The final hard-gate tail
(`400_500`) ended at `mass_total_delta_rel = 0.008321150189010917`, so the row
failed candidate mass acceptance.

The outlet failure is a true tail stationarity issue, not only a near-outlet
measurement-plane mismatch. In the hard-gate tail, the outlet flux CV was
`0.11556697847525366`, the mean flux imbalance was
`0.10270018561574665`, and the near-outlet to true-outlet ratio stayed close
to one with mean `0.9978928625164406`.

The controller telemetry does not show a saturation-only explanation. In the
hard-gate tail, `controller_saturation_fraction_run` stayed at `0.0`, while
`controller_authority_ratio` declined from a tail maximum of
`0.6605062012871107` to final `0.38176060964663827` with
`slope_per_step = -0.0017400182162721955`. The measured outlet flux remained
more variable than the target: `controller_measured_outlet_flux` CV was
`0.12288506684678856`, while `controller_target_outlet_flux` CV was
`0.0037379431910501324`.

## Gate State

Step140 does not change the campaign gate state:

- `selected96_execution_allowed = false`
- `validation_claim_allowed = false`
- `quasi2d_validation_claim_allowed = false`
- `fsi_validation_claim_allowed = false`
- `fluent_validation_claim_allowed = false`
- `figure29_3_parity_claim_allowed = false`
- `production_readiness_claim_allowed = false`

Step139 remains a falsified long-window candidate. No selected boundary,
selected96, 96^3, quasi-2D, FSI, Fluent, Figure 29.3, or production-readiness
claim is justified.

## Next-Step Policy

Step141 may propose one bounded 48^3 / 250-step diagnostic design focused on
mass-neutral plane-flux or density-feedback isolation. Step141 must not run
selected96, must not run 500 steps, and must not claim validation.
