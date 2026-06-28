# Current Status

The active campaign is the Fluent duct/flap LBM open-boundary repair campaign.
The current artifact state remains selected-boundary blocked. Step139 is a
single 48^3 / 500-step final-evidence test of the one Step138 passing
short-window row. It is not selected-candidate evidence and it does not enable
selected 96^3.
Current campaign state: `48_candidates_failed`.

Step139 added a bounded `planeflux_final48` phase with exactly one real
48^3 / 500-step LBM-only row copied from the Step138 passing parameters:
ramp85 / target0.80 / gain0.75 / cap0.0075. The row completed 500/500, stayed
finite, passed density, population, Mach, mass-drift, first-failure, ratio,
max-imbalance, collapse, and limiter checks, but it failed the full final hard
gate. The 500-step tail had `candidate_mass_acceptance_observed_abs =
0.008321150189010917`, which failed the `< 0.005` candidate mass-acceptance
gate; `flux_imbalance_rel_tail_mean = 0.10270018561574665`, which failed the
`< 0.10` mean-imbalance gate; and `outlet_flux_tail_cv =
0.11556697847525366`, which failed the `< 0.10` outlet-stationarity gate. The
ratio checks stayed inside bounds with `outlet_to_inlet_flux_ratio_tail_mean =
1.0372606489398013` and `midplane_to_inlet_flux_ratio_tail_mean =
0.9995829419859176`; `flux_imbalance_rel_tail_max =
0.16810119026843742`; `collapse_first_x = null`; and `collapse_first_step =
null`. Step139 therefore falsifies the Step138 short-window promotion
candidate. No selected boundary, selected96, selected-static, 96^3, quasi-2D,
FSI, Fluent, Figure 29.3, or production-readiness claim is allowed.

Step139 also records two bounded guard surfaces without changing solver
equations or running external tools. `docs/GENERIC_SOLVER_ARCHITECTURE_CONTRACT.md`
keeps solver-core packages benchmark-agnostic and keeps benchmark adapters out
of solver formulas. `docs/campaigns/fluent_duct_flap/fluent_official_local_execution_guard.md`
prepares a future manual local Fluent official execution manifest and monitor
export schema, but its guard report records `fluent_run_executed = false`,
`external_action_taken = false`, `official_payload_committed = false`, and
`validation_claim_allowed = false`.

Step138 added a bounded `planeflux_high_authority48` phase. Six real 48^3 /
250-step LBM-only diagnostic rows completed 250/250 with finite state and no
first-failure event. All six rows passed density, population, and Mach gates;
four passed candidate mass acceptance; three avoided the compact x-profile
collapse label; two passed the raw flow-development gate; and one row passed
the full final hard gate including mass acceptance and no compact-collapse
label. The passing row was ramp85 / target0.80 / gain0.75 / cap0.0075 with
`candidate_mass_acceptance_observed_abs = 0.003974863988826804`,
`outlet_to_inlet_flux_ratio_tail_mean = 1.0589469344632336`,
`midplane_to_inlet_flux_ratio_tail_mean = 0.9372161279428126`,
`flux_imbalance_rel_tail_mean = 0.08826485542410979`,
`flux_imbalance_rel_tail_max = 0.18087974336724078`, and
`outlet_flux_tail_cv = 0.09651149130583905`, with no compact-collapse label.
Step138 therefore justifies a later Step139 single 48^3 / 500-step
final-evidence proposal for that row. Step138 itself did not run 500 steps, did
not add selected-candidate semantics, and selected 96^3 remains blocked.

Step137 added a bounded `planeflux_ramp_refined48` phase. Six real 48^3 /
250-step LBM-only diagnostic rows completed 250/250 with finite state and no
first-failure event. All six rows passed candidate mass acceptance and avoided
the compact x-profile collapse label, but no row passed the final hard
flow-development gate. The best outlet-ratio row was ramp85 / target0.85 with
`outlet_to_inlet_flux_ratio_tail_mean = 1.246561166160358`,
`midplane_to_inlet_flux_ratio_tail_mean = 1.1418110718950278`,
`flux_imbalance_rel_tail_mean = 0.19102045308771165`, and
`flux_imbalance_rel_tail_max = 0.29227885610916315`. The best mass row was
ramp90 / target0.80 with `candidate_mass_acceptance_observed_abs =
0.0006162400457775661`, but it still failed flow development with
`outlet_to_inlet_flux_ratio_tail_mean = 1.2636158741752672` and
`flux_imbalance_rel_tail_mean = 0.20201121638125025`. Step137 therefore does
not justify Step138 48^3 / 500-step final evidence, and selected 96^3 remains
blocked.

Step136 added a bounded `planeflux_ramp_tuned48` phase and a report-visible
`open_boundary_flux_control_target_scale` parameter. Six real 48^3 / 250-step
LBM-only calibration rows completed 250/250 with finite state and no
first-failure event. Two rows passed candidate mass acceptance: target0.90
(`candidate_mass_acceptance_observed_abs = 0.0027411073257309804`) and
target0.95 (`candidate_mass_acceptance_observed_abs =
0.004158116831305122`). No row passed the flow-development gate. The best
flux-imbalance row was ramp75 / target1.00 with
`flux_imbalance_rel_tail_mean = 0.17995040672859994`, but it reintroduced a
compact-collapse label at interior `x = 24`, step 250. The best mass row,
ramp100 / target0.90, still had
`outlet_to_inlet_flux_ratio_tail_mean = 1.3064291443826772` and
`midplane_to_inlet_flux_ratio_tail_mean = 1.228018341923524`. Step136 therefore
supports continued bounded 48^3 calibration only; it does not justify a
500-step promotion or selected 96^3.

Step135 added a bounded `planeflux_interior_diag48` interior reflection and
bulk-dynamics diagnostic phase. Six real 48^3 / 250-step LBM-only diagnostic
rows completed 250/250 with finite state and no first-failure event, but no row
passed the relaxed reporting gate set. The baseline high-frequency regularized
row first labeled compact profile collapse at interior `x = 24`, step 220, not
at the true outlet; `lbm_niu = 0.08` and `lbm_niu = 0.12` retained the same
interior-collapse pattern. Inlet ramping changed the failure mode: ramp50
delayed collapse to step 245 and ramp100 removed the compact collapse label,
but ramp100 failed ratio and flux gates with
`outlet_to_inlet_flux_ratio_tail_mean = 1.5815747922655192`,
`midplane_to_inlet_flux_ratio_tail_mean = 1.4639728217023902`, and
`flux_imbalance_rel_tail_mean = 0.36544508198725295`. Step135 therefore
supports a bulk/startup-transient diagnosis, not outlet-local measurement
repair, and it does not justify a 500-step promotion or selected 96^3.

Step134 added a bounded `planeflux_stationarity48` outlet tail-collapse
diagnostic and near-outlet control-plane repair phase. Six real 48^3 / 250-step
LBM-only rows completed 250/250 with finite state and no first-failure event,
but all six failed promotion gates. The best mass row was
`duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_250step_triage`
with `candidate_mass_acceptance_observed_abs = 0.014007222184954796`; the best
flux-imbalance row was
`duct_only_48_convective_plane_flux_controlled_damped_gain0p10_cap0p002_rho0p001_alpha0p02_du0p0005_slew0p50_offset1_guard_on_min0p70_250step_triage`
with `flux_imbalance_rel_tail_mean = 0.2598977291666475`. Near-outlet ratios in
the regularized rows stayed near the true outlet ratio (`0.9913981762897958` to
`0.9990451987612539`), so Step134 did not support the hypothesis that the
tail collapse was only an `nx - 1` measurement-plane artifact. No 500-step
promotion was justified, and selected 96^3 remains blocked.

Step133 added a bounded `planeflux_mass_damped48` slow-density-feedback and
feedback-stationarity-damping phase. Six real 48^3 / 250-step LBM-only rows
completed 250/250 with finite state and no first-failure event, but all six
still failed the relaxed triage promotion gate. The best mass row was
`duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_rho0p0005_alpha0p02_du0p0005_slew0p50_250step_triage`
with `candidate_mass_acceptance_observed_abs = 0.014184975814691638`; the best
flux-imbalance row was
`duct_only_48_convective_plane_flux_controlled_damped_gain0p10_cap0p002_rho0p001_alpha0p02_du0p0005_slew0p50_250step_triage`
with `flux_imbalance_rel_tail_mean = 0.2630888340905568`. No 500-step
promotion was justified, and selected 96^3 remains blocked.

Step132 added a bounded `planeflux_sweep48` controller-authority calibration
phase that reuses the Step131 plane-flux semantics. Six real 48^3 / 250-step
LBM-only sweep rows completed 250/250 with finite state and no first-failure
event, but all six still failed candidate mass acceptance and flow-development
hard gates. The best mass row was
`duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_250step_triage`
with `candidate_mass_acceptance_observed_abs = 0.014016928659457415`; the best
flux-imbalance row was
`duct_only_48_convective_plane_flux_controlled_damped_gain0p10_cap0p002_250step_triage`
with `flux_imbalance_rel_tail_mean = 0.26260675631911695`. No 500-step
promotion was justified, and selected 96^3 remains blocked.

Step131 added a true plane-integrated flux-error controller with
`regularized_plane_flux_controlled_pressure_outlet` and
`convective_plane_flux_controlled_damped_outlet`, plus a distinct Step121
`planeflux48` phase. Both new 48^3 / 250-step LBM-only triage rows completed
250/250 with finite/density/mass/population/mach stability and no first-failure
event, but both failed candidate mass acceptance and flow-development hard
gates. No 500-step promotion was justified, and selected 96^3 remains blocked.

Step129 ran the Step121 `repair48` phase for both Step128 repaired 48^3 /
500-step LBM-only candidates. Both repaired rows completed 500/500 steps and
produced simulation-backed terminal real evidence, but both failed the
flow-development hard gates. Selected 96^3 duct-only work remains blocked.

Step130 added a distinct bounded `flowrepair48` triage surface with
`regularized_flux_matched_pressure_outlet` and
`convective_flux_matched_damped_outlet`. Both new 48^3 / 250-step LBM-only
triage rows completed 250/250 with finite/density/mass/population/mach stability
gates passing and no first-failure event, but both failed flow-development hard
gates and candidate mass-acceptance. No 500-step promotion was justified, and
selected 96^3 remains blocked.

Step128 remains the code and contract surface for LBM open-boundary formulation
repair. It introduced two new repaired 48^3 candidate semantics,
`regularized_mass_balanced_pressure_outlet` and
`convective_mass_balanced_pressure_outlet`, plus a distinct Step121 `repair48`
phase. The old Step127 `candidates48` phase is unchanged.

Step129 also added checkpoint persistence for the repaired boundary counters:
`mass_balance_correction_count`, `mass_balance_correction_abs_sum`, and
`unknown_population_delta_abs_sum`.

Step129 repaired-candidate outcome:

- `duct_only_48_regularized_mass_balanced_pressure_outlet_500step_real`
  completed 500/500 steps with `mass_total_delta_rel_final =
  0.0019035086161313225`, but failed flow development:
  `flux_imbalance_rel_tail_mean = 0.3722224827902342`,
  `outlet_to_inlet_flux_ratio_tail_mean = 1.264735695477319`,
  `midplane_to_inlet_flux_ratio_tail_mean = 1.2098449625412`, and
  `outlet_flux_tail_cv = 0.33003290861468526`.
- `duct_only_48_convective_mass_balanced_pressure_outlet_500step_real`
  completed 500/500 steps with `mass_total_delta_rel_final =
  -0.0011874128939383197`, but failed flow development:
  `flux_imbalance_rel_tail_mean = 0.40325868347534677`,
  `outlet_to_inlet_flux_ratio_tail_mean = 1.2722701740330669`,
  `midplane_to_inlet_flux_ratio_tail_mean = 1.2671693838169262`, and
  `outlet_flux_tail_cv = 0.5513854681310228`.

Step127 ran real 48^3 LBM-only candidates. The limited regularized candidate
completed 500/500 steps but failed the flow-development gates, essentially
reproducing the old regularized failed-baseline flux behavior. The convective
outlet candidate produced terminal real evidence at step 200 with
`first_failure_reason = mass_drift`, did not complete the requested window, and
also failed flow-development ratio/imbalance gates.

Step127 selected no best 48^3 boundary. Selected 96^3 duct-only work is not
allowed from the current artifacts. Step128, Step129, Step130, Step131,
Step132, Step133, Step134, Step135, Step136, Step137, Step138, and Step139
continue that blocked 48^3 boundary-repair sequence without selecting a
boundary.

Step126 ran real 48^3 LBM-only references. The legacy reference completed
500/500 steps and passed the flow-development gate. The old regularized
reference completed 500/500 steps as simulation-backed comparison evidence but
failed the flow-development gate.

Step124 tightened the campaign decision contract before any larger real run:
terminal legacy reference failure now stops the 48 campaign, candidate and
selected-row acceptance require dimensionless flow-development gates, and the
summary phase must ignore stale rows that do not match the campaign manifest.

Step125 was the provenance-only patch. It separates the campaign base
commit from the current code commit in `ACTIVE_CAMPAIGN.json` and Step121
campaign manifests, and it records `code_commit_at_run` for Step120 row
artifacts.

Step139 does not claim 48^3 repaired-candidate success, selected 96^3 success,
quasi-2D validation, FSI validation, Fluent validation, or Figure 29.3 parity.
