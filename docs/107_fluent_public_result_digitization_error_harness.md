# Step107 Public Fluent Result Digitization Error Harness

Step107 turns the public Ansys Fluent Figure 29.4 displacement plot into a derived approximate reference curve and compares the current solver displacement output against it.

The committed reference is not an official Fluent data export. It is a small numeric approximation from the public plot, with explicit uncertainty and source metadata.

## What Was Added

- public reference metadata config
- derived Figure 29.4 digitized CSV
- pure-Python reference and solver curve loaders
- pure-Python displacement error metrics
- Step107 evidence runners
- output guard and artifact manifest
- focused contract tests

## Reference Data

The reference CSV has 51 rows on the official transient grid:

- start: `0.0 s`
- end: `0.025 s`
- spacing: `0.0005 s`
- max digitized displacement: `0.000395 m`
- uncertainty: `2.5e-5 m`

The reference lives at:

- `benchmarks/public/fluent_fsi_2way_digitized/figure_29_4_structural_point_flap_digitized.csv`

## First Comparison

The first error report compares against:

- `outputs/step106_fsi_outlet_repair_regression/flap_tip_displacement_timeseries.csv`

This uses `free_tip_proxy_mean`, not the exact Fluent structural point. The report therefore records:

- `monitor_equivalence = false`
- `validation_claim_allowed = false`
- `direct_quantitative_equivalence_allowed = false`

Step107 measures the current mismatch; it does not tune the solver.

## Guard Boundary

The Step107 guard allows only derived public-plot numeric data and comparison artifacts. It blocks official case, mesh, journal, case/data, image, and private Fluent CSV payloads from this step.
