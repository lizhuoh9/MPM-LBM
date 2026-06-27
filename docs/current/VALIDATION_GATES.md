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

Current Step128/Step129 repair surface and evidence:

- New repaired 48^3 semantics exist for bounded open-boundary repair:
  `regularized_mass_balanced_pressure_outlet` and
  `convective_mass_balanced_pressure_outlet`.
- Step121 has a separate `repair48` phase for repaired candidates.
- Step120 now reports hard-stop mass-drift fields separately from candidate
  mass-acceptance fields.
- Step129 persisted repaired boundary counters across checkpoints so
  `mass_balance_correction_count`, `mass_balance_correction_abs_sum`, and
  `unknown_population_delta_abs_sum` survive resume.
- Step129 ran both repaired 48^3 / 500-step candidates as real LBM-only rows.
- Both repaired candidates completed 500/500 steps and passed finite, density,
  mass, population, mach, first-failure, and candidate-mass-acceptance checks.
- Both repaired candidates failed flow-development hard gates:
  `regularized_mass_balanced_pressure_outlet` had
  `flux_imbalance_rel_tail_mean = 0.3722224827902342` and
  `outlet_to_inlet_flux_ratio_tail_mean = 1.264735695477319`;
  `convective_mass_balanced_pressure_outlet` had
  `flux_imbalance_rel_tail_mean = 0.40325868347534677` and
  `outlet_to_inlet_flux_ratio_tail_mean = 1.2722701740330669`.
- No repaired 48^3 / 500-step acceptance artifact has passed the hard gates.
- Selected 96^3 execution remains blocked.

Current Step130 flow-repair triage surface and evidence:

- New flow-repair 48^3 triage semantics exist for bounded LBM-only outlet
  repair: `regularized_flux_matched_pressure_outlet` and
  `convective_flux_matched_damped_outlet`.
- Step121 has a separate `flowrepair48` phase for these triage rows.
- Step130 semantics are not in the selected-candidate semantics set and cannot
  enable selected 96^3.
- Both Step130 rows completed 250/250 as real simulation-backed LBM-only triage
  artifacts, but both failed hard flow-development gates and failed candidate
  mass-acceptance.
- `regularized_flux_matched_pressure_outlet` ended with
  `flux_imbalance_rel_tail_mean = 0.391091092110087`,
  `outlet_to_inlet_flux_ratio_tail_mean = 1.582099528142026`, and
  `candidate_mass_acceptance_observed_abs = 0.027093607822589214`.
- `convective_flux_matched_damped_outlet` ended with
  `flux_imbalance_rel_tail_mean = 0.5063421113905975`,
  `outlet_to_inlet_flux_ratio_tail_mean = 2.0460586163795886`, and
  `candidate_mass_acceptance_observed_abs = 0.030650375098126185`.
- No 500-step promotion was run from Step130 triage.
- Selected 96^3 execution remains blocked.

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
