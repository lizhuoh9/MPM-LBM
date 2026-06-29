# Step143 Mass-Neutral Design Diagnostic Report

Status: `decision_ready`.

Step143 activated the Step142 `global_mass_error_density_offset` design only
inside the bounded `planeflux_mass_neutral_design48` phase. The phase ran four
real LBM-only rows at `48^3 / 250` steps with `output_interval = 5`.

Step143 did not run selected96.
Step143 did not run selected-static.
Step143 did not run 96^3.
Step143 did not run a 500-step row.
Step143 did not run Fluent.
Step143 did not run FSI.
Step143 does not make a validation claim.

## Evidence

Artifacts:

```text
outputs/step143_mass_neutral_design_diagnostic/mass_neutral_design48
outputs/step143_mass_neutral_design_diagnostic/step143_mass_neutral_comparison.json
outputs/step143_mass_neutral_design_diagnostic/step143_mass_neutral_comparison.csv
outputs/step143_mass_neutral_design_diagnostic/step143_decision_summary.json
```

The disabled baseline completed 250/250 with:

```text
candidate_mass_acceptance_observed_abs = 0.003974863988826804
outlet_flux_tail_cv = 0.09651149130583905
flux_imbalance_rel_tail_mean = 0.08826485542410979
```

The best enabled row was `gain = 0.50`, `cap = 0.00100`,
`blend = 1.0`. It completed 250/250 with:

```text
candidate_mass_acceptance_observed_abs = 0.0031636249081530357
outlet_flux_tail_cv = 0.09161249772040454
flux_imbalance_rel_tail_mean = 0.08579940196467845
mass_neutral_rho_feedback_tail_mean = -0.0010000000474974513
mass_neutral_feedback_saturation_fraction_tail = 0.8749355566726297
```

All four rows stayed finite, had no first-failure event, had no compact-collapse
label, completed the requested 250-step window, and kept
`selected96_claim_allowed = false` and `validation_claim_allowed = false`.

## Decision

The audit decision is:

```text
mass_neutral_design_supports_step144_single_500step_probe
```

This means Step144 may propose one 48^3 / 500-step final-evidence probe for the
exact best Step143 setting only. It does not approve selected96,
selected-static, 96^3 execution, Fluent validation, FSI validation,
quasi-2D validation, Figure 29.3 parity, or production-readiness.
