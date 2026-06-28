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

Current Step131 plane-flux-control triage surface and evidence:

- New plane-flux-control 48^3 triage semantics exist for bounded LBM-only
  outlet controller evidence: `regularized_plane_flux_controlled_pressure_outlet`
  and `convective_plane_flux_controlled_damped_outlet`.
- Step121 has a separate `planeflux48` phase for these triage rows.
- Step131 semantics are not in the selected-candidate semantics set and cannot
  enable selected 96^3.
- Both Step131 rows completed 250/250 as real simulation-backed LBM-only triage
  artifacts with finite state and no first-failure evidence, but both failed
  candidate mass acceptance and hard flow-development gates.
- `regularized_plane_flux_controlled_pressure_outlet` ended with
  `candidate_mass_acceptance_observed_abs = 0.0283421114698597`,
  `flux_imbalance_rel_tail_mean = 0.39787865621449087`,
  `flux_imbalance_rel_tail_max = 0.5034860408405382`,
  `outlet_to_inlet_flux_ratio_tail_mean = 1.6088762675407298`,
  `midplane_to_inlet_flux_ratio_tail_mean = 1.3339702270861844`, and
  `outlet_flux_tail_cv = 0.3523076810492384`.
- `convective_plane_flux_controlled_damped_outlet` ended with
  `candidate_mass_acceptance_observed_abs = 0.02858492044911549`,
  `flux_imbalance_rel_tail_mean = 0.4090919843128926`,
  `flux_imbalance_rel_tail_max = 0.5348760352869728`,
  `outlet_to_inlet_flux_ratio_tail_mean = 1.7338794180572676`,
  `midplane_to_inlet_flux_ratio_tail_mean = 1.60001489270226`, and
  `outlet_flux_tail_cv = 0.15801241453426013`.
- Controller telemetry was connected and sign-correct, but Step131 authority was
  too weak for the observed errors: the regularized row ended with
  `controller_filtered_flux_error = -33.369258880615234`,
  `controller_u_feedback = -3.9424925489583984e-05`,
  `controller_u_feedback_tail_mean = -4.043218238318028e-05`, and
  `controller_saturation_fraction_tail = 0.0`; the convective row ended with
  `controller_filtered_flux_error = -31.221101760864258`,
  `controller_u_feedback = -3.6886933230562136e-05`,
  `controller_u_feedback_tail_mean = -4.035353291934977e-05`, and
  `controller_saturation_fraction_tail = 0.0`.
- No 500-step promotion was run from Step131 triage.
- Selected 96^3 execution remains blocked.

Current Step132 plane-flux-controller authority sweep evidence:

- Step132 reuses the Step131 plane-flux-control semantics and adds a distinct
  `planeflux_sweep48` phase for controller-authority calibration.
- The Step132 sweep ran six real 48^3 / 250-step LBM-only rows across bounded
  gain/cap combinations. Every row completed 250/250, stayed finite, and had no
  first-failure evidence.
- Step132 sweep rows remain triage rows with
  `row_role = plane_flux_control_candidate_48`; they are not in the
  selected-candidate semantics set and cannot enable selected 96^3.
- All six rows failed candidate mass acceptance and flow-development hard
  gates. `accepted_row_count = 0`.
- The best mass row was
  `duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_250step_triage`
  with `candidate_mass_acceptance_observed_abs = 0.014016928659457415`,
  `flux_imbalance_rel_tail_mean = 0.39506523169401825`,
  `outlet_to_inlet_flux_ratio_tail_mean = 1.0307369515412572`,
  `midplane_to_inlet_flux_ratio_tail_mean = 0.9160340533832297`, and
  `outlet_flux_tail_cv = 0.46453328972807856`.
- The best flux-imbalance row was
  `duct_only_48_convective_plane_flux_controlled_damped_gain0p10_cap0p002_250step_triage`
  with `flux_imbalance_rel_tail_mean = 0.26260675631911695`,
  `candidate_mass_acceptance_observed_abs = 0.02197742027071526`,
  `outlet_to_inlet_flux_ratio_tail_mean = 1.4076835420515006`,
  `midplane_to_inlet_flux_ratio_tail_mean = 1.2354670381858301`, and
  `outlet_flux_tail_cv = 0.20215625232941636`.
- No 500-step promotion was run from Step132 triage.
- Selected 96^3 execution remains blocked.

Current Step133 mass-damped plane-flux triage evidence:

- Step133 reuses the Step131/Step132 plane-flux-control semantics and adds a
  distinct `planeflux_mass_damped48` phase for slow density feedback and
  feedback-stationarity damping.
- The Step133 triage ran six real 48^3 / 250-step LBM-only rows across bounded
  `gain_rho`, `filter_alpha`, `delta_cap_u`, and `slew_alpha` combinations.
  Every row completed 250/250, stayed finite, and had no first-failure
  evidence.
- Step133 rows remain triage rows with
  `row_role = plane_flux_control_candidate_48`; they are not in the
  selected-candidate semantics set and cannot enable selected 96^3.
- All six rows failed the relaxed promotion gate. `accepted_row_count = 0`.
- The best mass row was
  `duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_rho0p0005_alpha0p02_du0p0005_slew0p50_250step_triage`
  with `candidate_mass_acceptance_observed_abs = 0.014184975814691638`,
  `flux_imbalance_rel_tail_mean = 0.3987696128026395`,
  `outlet_to_inlet_flux_ratio_tail_mean = 1.0280528796842723`,
  `midplane_to_inlet_flux_ratio_tail_mean = 0.9111280219154153`, and
  `outlet_flux_tail_cv = 0.47087164136218246`.
- The best flux-imbalance row was
  `duct_only_48_convective_plane_flux_controlled_damped_gain0p10_cap0p002_rho0p001_alpha0p02_du0p0005_slew0p50_250step_triage`
  with `flux_imbalance_rel_tail_mean = 0.2630888340905568`,
  `candidate_mass_acceptance_observed_abs = 0.022125313054974453`,
  `outlet_to_inlet_flux_ratio_tail_mean = 1.408879778823433`,
  `midplane_to_inlet_flux_ratio_tail_mean = 1.2372221853054948`, and
  `outlet_flux_tail_cv = 0.20262416501645636`.
- No 500-step promotion was run from Step133 triage.
- Selected 96^3 execution remains blocked.

Current Step134 outlet-stationarity triage evidence:

- Step134 reuses the Step131-Step133 plane-flux-control semantics and adds a
  distinct `planeflux_stationarity48` phase for outlet tail-collapse diagnosis,
  near-outlet control-plane offsets, and an optional outlet flux drop guard.
- The Step134 triage ran six real 48^3 / 250-step LBM-only rows across bounded
  offset, guard, `min_ratio`, `filter_alpha`, and convective comparator
  settings. Every row completed 250/250, stayed finite, and had no
  first-failure evidence.
- Step134 rows remain triage rows with
  `row_role = plane_flux_control_candidate_48`; they are not in the
  selected-candidate semantics set and cannot enable selected 96^3.
- All six rows failed the promotion gates. `accepted_row_count = 0`.
- The best mass row was
  `duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_250step_triage`
  with `candidate_mass_acceptance_observed_abs = 0.014007222184954796`,
  `flux_imbalance_rel_tail_mean = 0.39347561119048463`,
  `outlet_to_inlet_flux_ratio_tail_mean = 1.0272119275600675`,
  `midplane_to_inlet_flux_ratio_tail_mean = 0.9077078805411898`, and
  `outlet_flux_tail_cv = 0.46403458232245004`.
- The best flux-imbalance row was
  `duct_only_48_convective_plane_flux_controlled_damped_gain0p10_cap0p002_rho0p001_alpha0p02_du0p0005_slew0p50_offset1_guard_on_min0p70_250step_triage`
  with `flux_imbalance_rel_tail_mean = 0.2598977291666475`,
  `candidate_mass_acceptance_observed_abs = 0.022051240592753655`,
  `outlet_to_inlet_flux_ratio_tail_mean = 1.4026043007528752`,
  `midplane_to_inlet_flux_ratio_tail_mean = 1.240713111991833`, and
  `outlet_flux_tail_cv = 0.20179832248145668`.
- Regularized Step134 rows retained near-outlet to true-outlet tail ratios from
  `0.9913981762897958` to `0.9990451987612539`, while still collapsing to final
  tail outlet flux around `14.4` to `16.0`; this indicates the near-outlet
  control planes and the true outlet plane collapse together.
- No 500-step promotion was run from Step134 triage.
- Selected 96^3 execution remains blocked.

Current Step135 interior-reflection diagnostic evidence:

- Step135 adds a distinct `planeflux_interior_diag48` phase for compact
  x-profile, inlet-ramp, and niu-sensitivity diagnostics.
- The Step135 phase ran six real 48^3 / 250-step LBM-only diagnostic rows:
  baseline high-frequency regularized, ramp50, ramp100, `lbm_niu = 0.08`,
  `lbm_niu = 0.12`, and a convective comparator.
- Every row completed 250/250, stayed finite, and had no first-failure
  evidence.
- Step135 rows use `row_role = interior_reflection_diagnostic_48`; they are not
  in the selected-candidate semantics set and cannot enable selected 96^3.
- No Step135 row passed the relaxed reporting gate set. The ramp100 row
  improved mass and outlet stationarity but failed ratio and flux gates:
  `outlet_to_inlet_flux_ratio_tail_mean = 1.5815747922655192`,
  `midplane_to_inlet_flux_ratio_tail_mean = 1.4639728217023902`,
  `flux_imbalance_rel_tail_mean = 0.36544508198725295`, and
  `flux_imbalance_rel_tail_max = 0.4148086159154826`.
- The baseline compact x-profile collapse label appeared at interior `x = 24`,
  step 220, not as a one-cell true-outlet artifact.
- No 500-step promotion was run from Step135 diagnostics.
- Selected 96^3 execution remains blocked.

Current Step136 ramped-inlet throughput calibration evidence:

- Step136 adds a distinct `planeflux_ramp_tuned48` phase for bounded
  ramped-inlet throughput calibration.
- Step136 also adds report-visible
  `open_boundary_flux_control_target_scale`, with default `1.0`, to scale the
  plane-flux controller target without changing existing default behavior.
- The Step136 phase ran six real 48^3 / 250-step LBM-only calibration rows
  across bounded ramp, feedback gain, correction cap, and target-scale values.
  Every row completed 250/250, stayed finite, and had no first-failure
  evidence.
- Step136 rows use `row_role = interior_reflection_diagnostic_48`; they are not
  in the selected-candidate semantics set and cannot enable selected 96^3.
- Two rows passed candidate mass acceptance: ramp100 / gain0.50 / cap0.005 /
  target0.90 with `candidate_mass_acceptance_observed_abs =
  0.0027411073257309804`, and ramp100 / gain0.50 / cap0.005 / target0.95 with
  `candidate_mass_acceptance_observed_abs = 0.004158116831305122`.
- All six rows failed flow-development gates. The target0.90 row still had
  `flux_imbalance_rel_tail_mean = 0.22888777098124222`,
  `outlet_to_inlet_flux_ratio_tail_mean = 1.3064291443826772`, and
  `midplane_to_inlet_flux_ratio_tail_mean = 1.228018341923524`.
- The best flux-imbalance row was ramp75 / gain0.50 / cap0.005 / target1.00
  with `flux_imbalance_rel_tail_mean = 0.17995040672859994`, but it
  reintroduced a compact-collapse label at interior `x = 24`, step 250.
- No 500-step promotion was run from Step136 calibration.
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
