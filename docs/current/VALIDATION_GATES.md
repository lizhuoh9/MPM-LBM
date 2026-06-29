# Validation Gates

The campaign cannot claim selected 96^3, quasi-2D, FSI, Fluent validation, or
Figure 29.3 parity from the current 48^3 LBM-only candidate artifacts.

Current Step146 coupled design evidence:

- Step146 is design-only and artifact-only.
- Step146 reads the Step145 and Step144 artifacts only.
- Step146 did not run a new LBM row.
- Step146 did not add a Step121 phase.
- Step146 did not run selected96.
- Step146 did not run selected-static.
- Step146 did not run 96^3.
- Step146 did not run Fluent.
- Step146 did not run FSI.
- Step146 did not run a 500-step probe.
- Step146 does not make a validation claim.
- Step146 preserves the Step145 mechanism:
  `mixed_saturation_stationarity_failure`.
- selected96 remains blocked.
- selected-candidate-surface review remains blocked.
- validation claim remains blocked.
- 500-step probe remains blocked.
- Step146 recommends only a later bounded Step147 `48^3 / 250-step`
  diagnostic proposal under `planeflux_saturation_stationarity48`.
- Step146 does not add that Step147 phase to Step121.

Current Step145 failure-forensics evidence:

- Step145 is artifact-only over Step144, Step143, and Step140 outputs.
- Step144 failed the final hard gate: the single Step144 row completed 500/500
  and stayed finite, but failed mass acceptance, mean flux imbalance, and
  outlet stationarity.
- Step145 did not run a new LBM row.
- Step145 did not add a Step121 phase.
- Step145 did not run selected96.
- Step145 did not run selected-static.
- Step145 did not run 96^3.
- Step145 did not run Fluent.
- Step145 did not run FSI.
- Step145 does not make a validation claim.
- Step145 classifies the dominant mechanism as
  `mixed_saturation_stationarity_failure`.
- selected96 remains blocked.
- selected-candidate-surface review remains blocked.
- validation claim remains blocked.
- Step145 keeps `selected96_execution_allowed = false`,
  `selected_candidate_surface_review_allowed = false`, and
  `validation_claim_allowed = false`.
- Step145 allows at most a Step146 bounded 250-step diagnostic/design proposal;
  it does not allow a 500-step probe or selected96 execution.

Current Step144 mass-neutral final48 probe evidence:

- Step144 adds the distinct `planeflux_mass_neutral_final48` phase with exactly
  one real `48^3 / 500-step` LBM-only row.
- Step144 row role is `mass_neutral_final_evidence_candidate_48`; this role is
  not in the selected chain and `regularized_plane_flux_controlled_pressure_outlet`
  remains outside selected-candidate semantics.
- Step144 did not run selected96.
- Step144 did not run selected-static.
- Step144 did not run 96^3.
- Step144 ran exactly one 48^3 / 500-step LBM-only row.
- Step144 did not run Fluent.
- Step144 did not run FSI.
- Step144 does not make a validation claim.
- Step144 keeps selected96 blocked.
- The row completed 500/500, stayed finite, had no first-failure event, and had
  no compact-collapse label.
- The row failed final hard gates with
  `candidate_mass_acceptance_observed_abs = 0.007345390662776274`,
  `flux_imbalance_rel_tail_mean = 0.1023209978570283`, and
  `outlet_flux_tail_cv = 0.11500661338208944`.
- The ratio and max-imbalance fields stayed inside bounds:
  `outlet_to_inlet_flux_ratio_tail_mean = 1.0364764885085453`,
  `midplane_to_inlet_flux_ratio_tail_mean = 0.9977253037978716`, and
  `flux_imbalance_rel_tail_max = 0.16828271633544037`.
- Mass-neutral tail saturation remained high:
  `mass_neutral_feedback_saturation_fraction_tail = 0.9374677783363148`.
- Step144 audit decision:
  `mass_neutral_flow_stationarity_long_window_failure`.
- Step144 does not allow Step145 selected-candidate-surface review and does not
  allow selected 96^3 execution.

Current Step143 mass-neutral design diagnostic surface and evidence:

- Step143 adds the distinct `planeflux_mass_neutral_design48` phase with four
  real `48^3 / 250-step` LBM-only diagnostic rows.
- Step143 row role is `mass_neutral_design_diagnostic_48`; this role is not in
  the selected chain and `regularized_plane_flux_controlled_pressure_outlet`
  remains outside selected-candidate semantics.
- Step143 did not run selected96.
- Step143 did not run selected-static.
- Step143 did not run 96^3.
- Step143 did not run a 500-step row.
- Step143 did not run Fluent.
- Step143 did not run FSI.
- Step143 does not make a validation claim.
- All four rows completed 250/250, stayed finite, had no first-failure event,
  and retained `selected96_claim_allowed = false` and
  `validation_claim_allowed = false`.
- The disabled baseline ended with
  `candidate_mass_acceptance_observed_abs = 0.003974863988826804`,
  `outlet_flux_tail_cv = 0.09651149130583905`, and
  `flux_imbalance_rel_tail_mean = 0.08826485542410979`.
- The best enabled row used mass-neutral `gain = 0.50`, `cap = 0.00100`, and
  `blend = 1.0`; it ended with
  `candidate_mass_acceptance_observed_abs = 0.0031636249081530357`,
  `outlet_flux_tail_cv = 0.09161249772040454`, and
  `flux_imbalance_rel_tail_mean = 0.08579940196467845`.
- Step143 audit decision:
  `mass_neutral_design_supports_step144_single_500step_probe`.
- Step143 permits only a later Step144 proposal for one `48^3 / 500-step`
  final-evidence probe at the exact best Step143 setting. Selected 96^3
  execution remains blocked.

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

Current Step137 refined ramp-target throughput-window evidence:

- Step137 adds a distinct `planeflux_ramp_refined48` phase for bounded
  intermediate-ramp and lower-target-scale diagnostics.
- The Step137 phase ran six real 48^3 / 250-step LBM-only diagnostic rows
  across `ramp_steps = 85, 90, 100` and `target_scale = 0.80, 0.85, 0.90`.
  Every row completed 250/250, stayed finite, and had no first-failure
  evidence.
- Step137 rows use `row_role = interior_reflection_diagnostic_48`; they are
  not in the selected-candidate semantics set and cannot enable selected 96^3.
- All six rows passed candidate mass acceptance and avoided the compact
  x-profile collapse label.
- All six rows failed final hard flow-development gates. The best outlet-ratio
  row was ramp85 / target0.85 with
  `outlet_to_inlet_flux_ratio_tail_mean = 1.246561166160358`,
  `midplane_to_inlet_flux_ratio_tail_mean = 1.1418110718950278`,
  `flux_imbalance_rel_tail_mean = 0.19102045308771165`, and
  `flux_imbalance_rel_tail_max = 0.29227885610916315`.
- `target_scale = 0.80` did not fix outlet overdrive: ramp90 / target0.80 had
  `outlet_to_inlet_flux_ratio_tail_mean = 1.2636158741752672` and
  `flux_imbalance_rel_tail_mean = 0.20201121638125025`.
- No 500-step promotion is justified from Step137 diagnostics.
- Selected 96^3 execution remains blocked.

Current Step138 high-authority outlet diagnostic evidence:

- Step138 adds a distinct `planeflux_high_authority48` phase for bounded
  high-authority outlet diagnostics.
- The Step138 phase ran six real 48^3 / 250-step LBM-only diagnostic rows
  across `ramp_steps = 85, 90`, `target_scale = 0.80, 0.85`,
  `gain_u = 0.75, 1.00`, and `cap_u = 0.0050, 0.0075, 0.0100`.
  Every row completed 250/250, stayed finite, and had no first-failure
  evidence.
- Step138 rows use `row_role = interior_reflection_diagnostic_48`; they are
  not in the selected-candidate semantics set and cannot enable selected 96^3.
- Four rows passed candidate mass acceptance, three rows avoided compact
  x-profile collapse labels, and two rows passed the raw ratio/imbalance/outlet
  stationarity flow-development gate.
- One row passed the full final hard gate including mass acceptance and no
  compact-collapse label: ramp85 / target0.80 / gain0.75 / cap0.0075 with
  `candidate_mass_acceptance_observed_abs = 0.003974863988826804`,
  `outlet_to_inlet_flux_ratio_tail_mean = 1.0589469344632336`,
  `midplane_to_inlet_flux_ratio_tail_mean = 0.9372161279428126`,
  `flux_imbalance_rel_tail_mean = 0.08826485542410979`,
  `flux_imbalance_rel_tail_max = 0.18087974336724078`, and
  `outlet_flux_tail_cv = 0.09651149130583905`, with
  `collapse_first_x = null` and `collapse_first_step = null`.
- This justifies a later Step139 single 48^3 / 500-step final-evidence proposal
  for that row.
- No 500-step promotion was run from Step138 diagnostics.
- Selected 96^3 execution remains blocked.

Current Step139 plane-flux final48 evidence:

- Step139 adds a distinct `planeflux_final48` phase containing exactly one
  real 48^3 / 500-step LBM-only final-evidence row copied from the Step138
  passing source row.
- The Step139 row uses
  `row_role = final_evidence_candidate_48`; it is not in the
  selected-candidate semantics set and cannot enable selected 96^3.
- The row preserves Step138 provenance:
  `source_step = 138`,
  `source_solver_state_hash =
  34437ee966ac063d03d80bd4a9c9dea30961897cbb87d41cc5c7de1571ef3ed8`,
  `source_run_manifest_hash =
  e689ad17b0de0f478d57ef9d419e2ed10579692cfb94866dbc1095b5c7239969`, and
  `source_code_commit = f0284d3f6207eb1c9341dfc9906293b651c6b0f7`.
- The Step139 row completed 500/500 steps, stayed finite, had no
  first-failure evidence, had no limiter activation, and did not produce a
  compact x-profile collapse label.
- Step139 failed the final hard gate. It failed candidate mass acceptance with
  `candidate_mass_acceptance_observed_abs = 0.008321150189010917`, failed
  flow development with `flow_development_gate_pass = false`, failed mean flux
  imbalance with `flux_imbalance_rel_tail_mean = 0.10270018561574665`, and
  failed outlet stationarity with `outlet_flux_tail_cv =
  0.11556697847525366`.
- Step139 retained ratio and max-imbalance checks inside their hard ranges:
  `outlet_to_inlet_flux_ratio_tail_mean = 1.0372606489398013`,
  `midplane_to_inlet_flux_ratio_tail_mean = 0.9995829419859176`, and
  `flux_imbalance_rel_tail_max = 0.16810119026843742`.
- Step139 falsifies the Step138 short-window promotion candidate. It does not
  select a boundary and does not justify Step140 selected96 promotion.
- Selected 96^3 execution remains blocked.

Current Step140 long-window drift forensics evidence:

- Step140 is report-only forensics over the existing Step139 artifacts in
  `outputs/step139_planeflux_final48`.
- Step140 did not add a Step121 phase, did not run LBM, did not tune
  parameters, did not add selected-candidate semantics, and did not enable
  selected96 execution.
- Step140 generated segment reports under
  `outputs/step140_long_window_drift_forensics` for mass drift, flux
  stationarity, controller response, x-profile evolution, and failure-mechanism
  summary.
- Step140 classifies the dominant failure mechanism as
  `mass_accumulation_with_outlet_stationarity_drift`.
- The `200_250` segment retained the short-window mass pass with
  `mass_total_delta_rel = 0.003974863988826804`, but `250_300` rose to
  `mass_total_delta_rel = 0.010577758938477861`, and the `400_500` hard-gate
  tail ended at `mass_total_delta_rel = 0.008321150189010917`.
- In the `400_500` hard-gate tail, `flux_imbalance_rel` mean was
  `0.10270018561574665`, outlet flux CV was `0.11556697847525366`, and
  near-outlet to true-outlet ratio mean was `0.9978928625164406`.
- Controller saturation stayed at `0.0`, while `controller_authority_ratio`
  declined to final `0.38176060964663827` with
  `slope_per_step = -0.0017400182162721955`.
- Step140 does not justify selected boundary, selected96, 96^3, quasi-2D, FSI,
  Fluent, Figure 29.3, or production-readiness claims.

Current Step141 density-feedback isolation evidence:

- Step141 adds a distinct `planeflux_density_feedback_isolation48` phase for
  bounded density-feedback isolation only.
- The phase ran exactly four real 48^3 / 250-step LBM-only rows with
  `output_interval = 5`; no selected96, selected-static, 96^3, Fluent, FSI, or
  500-step row was run.
- Step141 rows use `row_role = density_feedback_isolation_diagnostic_48`; the
  role is not in `SELECTED_CHAIN_ROLES`, and
  `regularized_plane_flux_controlled_pressure_outlet` remains outside
  `CANDIDATE_SEMANTICS` and `REPAIRED_CANDIDATE_SEMANTICS`.
- Each row preserves Step139/Step140 provenance including
  `source_step = 140`, the Step139 source row hashes, and
  `source_step140_summary_hash =
  a2cabe6f927750f161e892b8b625087193f2a43218ebe4c68a2e970d3817f7d8`.
- All four rows completed 250/250, stayed finite, passed density/population/Mach
  and the bounded 250-step flow-development gate, and had no first-failure or
  compact-collapse label.
- The audit decision is `density_feedback_isolation_insufficient`. The best
  250-step mass result remained the baseline repeat with `gain_rho = 0.001`:
  `candidate_mass_acceptance_observed_abs = 0.003974863988826804`. Removing
  density feedback had `candidate_mass_acceptance_observed_abs =
  0.003979989185473907`, so Step141 does not support density feedback as the
  dominant cause of the Step140 post-250 tail failure.
- `step142_single_500step_final_evidence_proposal_allowed = false`.
- Selected 96^3 execution remains blocked.

Current Step142 mass-neutral plane-flux design contract:

- Step142 is design-only. It did not run a real 48^3 row, did not run a
  500-step row, did not add a Step121 phase, and did not enable selected96.
- Step142 adds default-disabled report-visible config fields for a future
  mass-neutral plane-flux controller:
  `open_boundary_mass_neutral_flux_control_enabled`,
  `open_boundary_mass_neutral_flux_control_mode`,
  `open_boundary_mass_neutral_mass_error_gain`,
  `open_boundary_mass_neutral_mass_error_cap`,
  `open_boundary_mass_neutral_correction_blend`, and
  `open_boundary_mass_neutral_reference_mass_mode`.
- The Step142 design-readiness artifact is
  `outputs/step142_mass_neutral_plane_flux_design/step142_design_readiness_report.json`.
- The readiness report records `status = design_ready`,
  `step142_real_48_run_executed = false`,
  `step142_single_500step_final_evidence_proposal_allowed = false`,
  `selected96_execution_allowed = false`, and
  `validation_claim_allowed = false`.
- A future Step143 bounded 48^3 / 250-step diagnostic may be proposed as
  `planeflux_mass_neutral_design48`; that phase is not present in Step121
  during Step142.
- selected 96^3 execution remains blocked.

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
