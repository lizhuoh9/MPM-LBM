# Step118 LBM Open-Boundary Stability Repair

Step118 responds to Step117's real long-window result: the existing
`regularized_velocity_pressure` boundary cannot be used as the basis for
quasi-2D or FSI yet.

Step119 quasi-2D remains blocked. No Fluent validation is claimed. No full FSI validation is claimed.

## Implemented Surface

- Stability diagnostics for population extrema, negative populations, density
  outliers, velocity outliers, first gate failure, and boundary-local
  population state.
- New opt-in LBM open-boundary semantics:
  - `regularized_velocity_pressure_limited`
  - `convective_pressure_outlet_experimental`
- Limiter configuration fields passed from `FSIDriverConfig` through
  `UnifiedSimConfig` to `LBMConfig`.
- Step118 runner with row-level resume, strict tau skip, boundary comparison,
  first-failure artifacts, and committed report schema.

## Committed Artifact Scope

The checked-in Step118 rows are synthetic diagnostic rows. They are intentionally
not simulation-backed physical validation. Their role is to keep the artifact
schema, diagnostics, reporting, and gates under regression coverage without
putting expensive 48^3/96^3 long-window rows into pytest.

Real evidence must be produced by running non-synthetic Step118 rows and
reviewing:

- `solver_report.json`
- `run_matrix_summary.json`
- `boundary_variant_comparison.json`
- `first_failure_diagnostics.json`
- each row's `stability_diagnostics_timeseries.csv`

## Gate For Reopening Step119

Step119 remains blocked until real Step118 rows show:

- 48^3 best boundary flux imbalance tail mean below `0.1`.
- 48^3 best boundary final mass drift below `0.005` and below two times the
  48^3 legacy drift.
- 96^3 duct-only best boundary passes density and mass gates.
- 96^3 static two-flap best boundary passes density and mass gates.
- Max Mach proxy remains below `0.2`.
- No negative-density event.
- No catastrophic negative-population fraction.
- Physical-nu/tau strict row remains skipped when tau is unsafe.

Until those gates pass, Step118 is a boundary-stability repair layer, not a
quasi-2D or FSI readiness claim.
