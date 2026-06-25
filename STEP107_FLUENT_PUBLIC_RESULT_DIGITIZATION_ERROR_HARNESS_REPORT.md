# Step107 Fluent Public Result Digitization Error Harness Report

## Result

Step107 passed as a comparison-infrastructure step. It adds a derived approximate public-plot reference curve from Ansys Fluent tutorial Figure 29.4 and a pure-Python displacement error harness that compares our committed solver time series against that public reference.

This step does not modify solver behavior. It does not use official Fluent case files, mesh files, journals, case/data files, image payloads, or private Fluent CSV exports.

## Public Reference Metadata

The reference metadata records:

- source: Ansys Fluent Tutorial Chapter 29, Modeling Two-Way Fluid-Structure Interaction Within Fluent
- URL: `https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_tg/flu_tg_fsi_2way.html`
- public result figure: Figure 29.4
- monitor: `structural-point-flap`
- quantity: total displacement
- operation: vertex average
- monitor point: `x = 0.0505 m`, `y = 0.0095 m`
- transient setup: 50 steps, `0.0005 s`, final time `0.025 s`
- inlet velocity: `10.0 m/s`
- material: density `1600 kg/m^3`, Young's modulus `1.0e6 Pa`, Poisson ratio `0.47`

The committed metadata keeps:

- `official_case_files_used = false`
- `official_png_committed = false`
- `digitized_from_public_plot = true`
- `validation_claim_allowed = false`
- `direct_quantitative_equivalence_allowed = false`

## Digitized Reference

The committed reference is:

- `benchmarks/public/fluent_fsi_2way_digitized/figure_29_4_structural_point_flap_digitized.csv`

The generated copy is:

- `outputs/step107_public_reference_digitization/figure_29_4_digitized_reference.csv`

Digitization summary:

- sample count: `51`
- time range: `0.0 s` to `0.025 s`
- time spacing: `0.0005 s`
- method: `manual_visual_anchor_linear_interpolation`
- uncertainty per row: `2.5e-5 m`
- max digitized displacement: `0.000395 m`
- min digitized displacement: `0.0 m`
- official image committed: `false`

This is an approximate public-plot reference, not raw Fluent output.

## Error Harness

The first comparison uses the current committed Step106 proxy solver output:

- solver curve: `outputs/step106_fsi_outlet_repair_regression/flap_tip_displacement_timeseries.csv`
- monitor used: `free_tip_proxy_mean`
- monitor equivalence: `false`

The error report is:

- `outputs/step107_error_comparison/error_report.json`
- `outputs/step107_error_comparison/error_report.csv`
- `outputs/step107_error_comparison/error_report.md`

Metrics:

- sample count: `51`
- peak reference: `0.000395 m`
- peak solver: `3.766233760416071e-07 m`
- peak absolute error: `0.0003946233766239584 m`
- peak relative error: `0.9990465230986288`
- RMS absolute error: `0.00024358400587801233 m`
- normalized RMS error: `0.6166683693114237`
- final reference: `6e-05 m`
- final solver: `3.766233760416071e-07 m`
- final absolute error: `5.9623376623958394e-05 m`
- final relative error: `0.9937229437326399`
- reference peak time: `0.004 s`
- solver peak time: `0.01 s`
- peak time error: `0.006 s`
- shape correlation: `0.07747139097796335`
- all metrics finite: `true`

Step107 does not require these errors to be small. It only requires the comparison to be computed, finite, and honestly labeled.

## Guard Results

Step107 output guard passed:

- official case file count: `0`
- official mesh file count: `0`
- official journal file count: `0`
- official case/data H5 count: `0`
- official image count: `0`
- private Fluent CSV count: `0`
- validation-claim count: `0`
- direct-equivalence positive-claim count: `0`
- protected external edit count: `0`
- protected real geometry candidate edit count: `0`
- artifact budget pass: `true`

Artifact manifest passed:

- Step107 file count: `34`
- Step107 total size: `0.07219505310058594 MB`
- large file count: `0`
- official image count: `0`
- proprietary official file count: `0`

## Remaining Boundaries

This step uses the public Fluent tutorial result plot, not official case files. No official Fluent mesh, journal, case, data, or image file is committed. The digitized curve is an approximate public-plot reference with recorded uncertainty. The comparison is against the public plot, not against proprietary Fluent result files.

The current comparison uses the Step106 free-tip proxy mean, not the exact Fluent structural-point monitor, so `monitor_equivalence = false`.

Next work should use this harness while addressing low-Mach dimensional scaling, steady preflow, and monitor-definition gaps in later steps.
