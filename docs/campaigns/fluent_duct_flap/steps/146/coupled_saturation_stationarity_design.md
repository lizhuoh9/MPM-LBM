# Step146 Coupled Saturation-Stationarity Design

Step146 evaluates the Step145 conclusion that Step144 failed through coupled
mass-neutral saturation and outlet stationarity. The design stays artifact-only
and does not change solver runtime behavior.

## Source Facts

- Step145 decision: `mixed_saturation_stationarity_failure`
- Step144 decision: `mass_neutral_flow_stationarity_long_window_failure`
- Step144 final mass abs: `0.007345390662776274`
- Step144 mean flux imbalance tail: `0.1023209978570283`
- Step144 outlet flux tail CV: `0.11500661338208944`
- Step144 mass-neutral saturation tail: `0.9374677783363148`
- Tail controller authority ratio slope: `-0.0017484489151022653`

These facts mean the current evidence does not support a selected boundary,
selected96 execution, selected-candidate-surface review, a Step146 500-step
probe, or any validation claim.

## Design A: Saturation-Aware Mass-Neutral Relief With Stationarity Damping

Design A is the recommended later Step147 diagnostic.

The key rule is not to raise the mass-neutral cap alone. Step144 already shows
that the mass-neutral feedback can stay saturated while mass acceptance and
outlet stationarity still fail. A bounded next diagnostic should reduce the
direct mass actuator aggressiveness and add stationarity damping so the two
failure channels can be separated.

Proposed later Step147 rows:

```text
mass_neutral_high_baseline:
  gain_mass = 0.50
  cap_mass = 0.00100
  blend = 1.0
  role = repeat current Step144/Step143 high setting baseline

relief_low:
  gain_mass = 0.35
  cap_mass = 0.00100
  blend = 0.50
  stationarity damping stronger: slew_alpha = 0.25 or delta_cap_u = 0.00025

relief_mid:
  gain_mass = 0.50
  cap_mass = 0.00100
  blend = 0.50
  stationarity damping stronger

relief_cap_test:
  gain_mass = 0.50
  cap_mass = 0.00150
  blend = 0.50
  role = diagnostic cap test only, not promotion
```

Step147, if approved later, should be limited to:

```text
phase = planeflux_saturation_stationarity48
row_role = saturation_stationarity_diagnostic_48
max rows = 4
max steps = 250
output_interval = 5
```

## Design B: Outlet Population Projection Feasibility, Report-Only

Design B is fallback telemetry. It should not be activated in Step146.

The idea is to define a future report-only feasibility calculation for a
zeroth-moment neutral projection: estimate the population correction needed and
the possible x-momentum cost before any runtime population reconstruction
change is considered.

Design B is intentionally not the Step147 recommendation because Step144 did
not show numerical instability; it showed coupled mass-neutral saturation and
outlet stationarity failure. A stationarity-aware bounded diagnostic is the
more controlled next move.

## Final Step146 Decision

Recommend Design A for a later bounded Step147 diagnostic.
Keep Design B as fallback telemetry only.

Step146 itself remains design-only and artifact-only. It does not run LBM, does
not add a Step121 phase, does not run selected96, does not run selected-static,
does not run 96^3, does not run Fluent, does not run FSI, does not run a
500-step probe, and does not make a validation claim.
