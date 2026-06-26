# Validation Gates

The campaign cannot claim selected 96^3, quasi-2D, FSI, Fluent validation, or
Figure 29.3 parity from the current 48^3 LBM-only candidate artifacts.

Current Step127 outcome:

- Legacy 48^3 reference passed the flow-development gate.
- Old regularized 48^3 reference completed but failed flow development.
- Limited regularized 48^3 candidate completed but failed flow development.
- Convective outlet 48^3 candidate stopped on terminal mass-drift evidence and
  failed flow development.
- No best 48^3 boundary is selected.
- Selected 96^3 execution is blocked.

Current Step124 gate requirements:

- 48^3 legacy reference rows must either complete the requested real window or
  stop the campaign as `48_legacy_reference_failed` on simulation-backed
  physical terminal failure.
- Old regularized reference rows may provide failed-baseline comparison
  evidence, but they do not make the legacy reference valid.
- Candidate 48^3 rows must pass the shared flow-development gate before they
  can be selected.
- Selected 96^3 duct and static rows must pass the same dimensionless
  development checks, including inlet/outlet sign, outlet-to-inlet ratio,
  midplane-to-inlet ratio, tail imbalance max, and outlet-tail stationarity.
- Summary collection is campaign-manifest driven when a manifest is present;
  stale solver-state rows and wrong selected-source rows must be ignored.
