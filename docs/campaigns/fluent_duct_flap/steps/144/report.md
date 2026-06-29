# Step144 Mass-Neutral Plane-Flux Final48 Probe Report

Status: `decision_ready`.

Step144 ran exactly one real LBM-only row in the
`planeflux_mass_neutral_final48` phase. The row used the exact Step143 best
mass-neutral high setting at `48^3 / 500` steps with `output_interval = 10`.

Step144 did not run selected96.
Step144 did not run selected-static.
Step144 did not run 96^3.
Step144 ran exactly one 48^3 / 500-step LBM-only row.
Step144 did not run Fluent.
Step144 did not run FSI.
Step144 does not make a validation claim.
Step144 keeps selected96 blocked.

## Evidence

Artifacts:

```text
outputs/step144_mass_neutral_final48/mass_neutral_final48
outputs/step144_mass_neutral_final48/step144_long_window_comparison.json
outputs/step144_mass_neutral_final48/step144_long_window_comparison.csv
outputs/step144_mass_neutral_final48/step144_decision_summary.json
```

The single row was:

```text
duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010_mnhigh_mgain0p50_mcap0p001_blend1p00_out10_500step_mass_neutral_final
```

It completed 500/500 and stayed finite with no first-failure event and no
compact-collapse label, but it failed the Step144 final hard gate:

```text
candidate_mass_acceptance_observed_abs = 0.007345390662776274
candidate_mass_acceptance_gate_pass = false
flux_imbalance_rel_tail_mean = 0.1023209978570283
outlet_flux_tail_cv = 0.11500661338208944
flow_development_gate_pass = false
```

The ratio and max-imbalance fields remained within their hard bounds:

```text
outlet_to_inlet_flux_ratio_tail_mean = 1.0364764885085453
midplane_to_inlet_flux_ratio_tail_mean = 0.9977253037978716
flux_imbalance_rel_tail_max = 0.16828271633544037
```

The mass-neutral feedback stayed highly saturated in the 500-step tail:

```text
mass_neutral_feedback_saturation_fraction_tail = 0.9374677783363148
mass_neutral_mass_error_tail_mean = 0.0070619042962789536
mass_neutral_mass_error_final = 0.0077638872899115086
mass_neutral_rho_feedback_tail_mean = -0.0010000000474974513
```

This confirms the Step143 risk signal: the high setting still spends most of
the long-window tail at the mass-neutral cap and does not keep the final mass
or outlet-stationarity gates inside bounds.

## Decision

The Step144 audit decision is:

```text
mass_neutral_flow_stationarity_long_window_failure
```

Step144 therefore does not allow Step145 selected-candidate-surface review,
does not allow selected96, does not allow selected-static, does not allow 96^3,
does not allow Fluent or FSI validation, and does not make a validation claim.
The next step should diagnose long-window stationarity/controller lag and
mass-neutral saturation rather than run selected96.

