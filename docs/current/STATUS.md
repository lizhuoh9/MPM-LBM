# Current Status

The active campaign has moved from outlet-controller repair to Fluent official
case reproduction with the repository MPM-LBM/FSI solver. Step148 ran the
repository `FSIDriver3D` at 48 grid / 250 FSI steps using the duct/flap proxy
geometry and wrote comparison-ready solver monitors under
`outputs/step148_our_solver_fluent_official_case`. Step148 did not run Fluent,
did not commit private official payloads, did not use the private official
monitor as runtime input, did not run selected96, and does not make a validation
claim. The Step148 run base was
`67e05ebbce10e92f5331dde20b424e7b5c081b7b`.

Step150 is now the current official-monitor intake wrapper for the
official-vs-solver error-localization track. It checks
`benchmarks/private/fluent_fsi_2way/outputs/official_monitor.csv`, verifies the
private official monitor schema before calling the Step149 comparison logic,
records only private-file metadata/hash, and refuses to fabricate metrics when
the official reference is absent. In this checkout the private official monitor
is not present, so Step150 reports `missing_official_monitor` /
`official_reference_missing`. It confirms the Step148 solver monitor is present,
but it does not generate displacement metrics, force metrics, phase-lag metrics,
or solver bug hypotheses. No Step151 code-fix target is identified until the
official monitor is available or a user-provided reference monitor is supplied.

Step151 is now the current targeted-fix gate after Step150. It reads the
Step150 error-localization summary and solver bug hypotheses before allowing
any solver patch. In the current checkout Step150 is still
`missing_official_monitor`, so Step151 correctly reports
`blocked_by_missing_error_localization`: `solver_code_modified = false`,
`targeted_fix_applied = false`, `post_fix_step148_run_executed = false`,
`post_fix_step150_comparison_executed = false`, and
`primary_metric_improved = false`. Step151 does not change MPM, LBM, FSI
coupling, geometry, monitor extraction, or runtime solver formulas in this
state.

The previous LBM outlet-controller repair line remains selected-boundary
blocked. Step147 ran exactly four 48^3 / 250-step LBM-only rows under
`planeflux_saturation_stationarity48` from the Step146 readiness artifact.
Step147 did not run selected96. Step147 did not run selected-static. Step147
did not run 96^3. Step147 did not run a 500-step row. Step147 did not run
Fluent. Step147 did not run FSI. Step147 does not make a validation claim.
`origin/main = 54afab0c6b4bdae05fa08f50f274e8d2f557e1d9` is the checked
Step146 source ref for this Step147 implementation.

Step147 artifacts are under
`outputs/step147_saturation_stationarity_diagnostic`. The audit decision is
`relief_design_unstable`: all four rows completed 250/250 and flow gates passed,
but all three relief rows reported compact x-profile collapse at x=24, step
240. The best-looking relief cap-test row ended with
`candidate_mass_acceptance_observed_abs = 0.002093421390940915`,
`flux_imbalance_rel_tail_mean = 0.06738282016989694`,
`outlet_flux_tail_cv = 0.08294339447357761`, and
`mass_neutral_feedback_saturation_fraction_tail = 0.7280537236557635`, but the
collapse marker blocks promotion. Step148 500-step probe remains blocked,
selected96 remains blocked, selected-candidate-surface review remains blocked,
and validation claim remains blocked.

Step147 bounded-state phrases:

- Step147 ran exactly four 48^3 / 250-step LBM-only rows
- Step147 did not run selected96
- Step147 did not run selected-static
- Step147 did not run 96^3
- Step147 did not run a 500-step row
- Step147 did not run Fluent
- Step147 did not run FSI
- Step147 does not make a validation claim
- origin/main = 54afab0c6b4bdae05fa08f50f274e8d2f557e1d9

Step146 is design-only and artifact-only. It reads the existing Step145 and
Step144 artifacts, records a coupled saturation-stationarity design readiness
report, and allowed only the now-completed bounded Step147 `48^3 / 250-step`
diagnostic proposal. Step146 did not run a new LBM row, did not run selected96,
selected-static, 96^3, Fluent, or FSI, did not run a 500-step probe, and does
not make a validation claim.
Current campaign state:
`targeted_solver_fix_blocked_missing_error_localization`.

Step146 artifacts are under
`outputs/step146_coupled_saturation_stationarity_design`. The design readiness
report is
`outputs/step146_coupled_saturation_stationarity_design/step146_design_readiness_report.json`.
It records `status = design_ready`, `source_step145_decision_case =
mixed_saturation_stationarity_failure`, `design_only = true`, `artifact_only =
true`, `new_lbm_run_executed = false`, `step121_phase_added = false`,
`selected96_execution_allowed = false`,
`selected_candidate_surface_review_allowed = false`, and
`validation_claim_allowed = false`. It recommends Design A,
`saturation_aware_mass_neutral_relief_with_stationarity_damping`, for a later
Step147 proposal and keeps Design B,
`outlet_population_projection_report_only`, as fallback telemetry only.

Step145 is an artifact-only failure-forensics step over the existing Step144,
Step143, and Step140 outputs. It classifies the Step144 long-window failure as
`mixed_saturation_stationarity_failure`: mass-neutral feedback saturated through
the hard-gate tail while mass acceptance and outlet stationarity both remained
outside gate.

Step144 failed the final hard gate after running the single `48^3 / 500-step`
LBM-only mass-neutral final-evidence probe that Step143 allowed. The row
completed 500/500 and stayed finite, but failed mass acceptance, mean flux
imbalance, and outlet stationarity. Step145 did not run a new LBM row, did not
add a Step121 phase, did not run selected96, did not run selected-static, did
not run 96^3, did not run Fluent, did not run FSI, and does not make a
validation claim. selected96 remains blocked, selected-candidate-surface review remains blocked,
and validation claim remains blocked.

Step145 artifacts are under
`outputs/step145_mass_neutral_long_window_forensics`. The failure mechanism
summary is
`outputs/step145_mass_neutral_long_window_forensics/step145_failure_mechanism_summary.json`.
It records `dominant_failure_mechanism =
mixed_saturation_stationarity_failure`,
`selected96_execution_allowed = false`,
`selected_candidate_surface_review_allowed = false`, and
`validation_claim_allowed = false`. The only Step146 allowance was a bounded
250-step diagnostic/design proposal; Step146 now converts that allowance into a
design-only readiness artifact. A 500-step probe and selected96 remain blocked.

Step144 did not run selected96.
Step144 did not run selected-static.
Step144 did not run 96^3.
Step144 ran exactly one 48^3 / 500-step LBM-only row.
Step144 did not run Fluent.
Step144 did not run FSI.
Step144 does not make a validation claim.
Step144 keeps selected96 blocked.

Step144 generated artifacts under `outputs/step144_mass_neutral_final48`. The
real phase root is `outputs/step144_mass_neutral_final48/mass_neutral_final48`,
and the audit decision is
`mass_neutral_flow_stationarity_long_window_failure`. The single row completed
500/500 with `candidate_mass_acceptance_observed_abs =
0.007345390662776274`, `flux_imbalance_rel_tail_mean =
0.1023209978570283`, and `outlet_flux_tail_cv =
0.11500661338208944`, so it failed the `< 0.005` mass gate, `< 0.10` mean
imbalance gate, and `< 0.10` outlet-CV gate. It kept
`selected96_claim_allowed = false` and `validation_claim_allowed = false`.
Mass-neutral feedback stayed saturated through most of the tail with
`mass_neutral_feedback_saturation_fraction_tail = 0.9374677783363148`.
Step145 selected-candidate-surface review is not allowed from this evidence.

Step143 did not run selected96.
Step143 did not run selected-static.
Step143 did not run 96^3.
Step143 did not run a 500-step row.
Step143 did not run Fluent.
Step143 did not run FSI.
Step143 does not make a validation claim.

Step143 generated artifacts under
`outputs/step143_mass_neutral_design_diagnostic`. The real phase root is
`outputs/step143_mass_neutral_design_diagnostic/mass_neutral_design48`, and the
audit decision is
`mass_neutral_design_supports_step144_single_500step_probe`.
The best enabled row used `open_boundary_mass_neutral_mass_error_gain = 0.50`,
`open_boundary_mass_neutral_mass_error_cap = 0.00100`, and
`open_boundary_mass_neutral_correction_blend = 1.0`. It completed 250/250 with
`candidate_mass_acceptance_observed_abs = 0.0031636249081530357`,
`outlet_flux_tail_cv = 0.09161249772040454`, and
`flux_imbalance_rel_tail_mean = 0.08579940196467845`, improving over the
disabled baseline values `0.003974863988826804`, `0.09651149130583905`, and
`0.08826485542410979`. All Step143 rows stayed finite, had no first-failure
event, and kept `selected96_claim_allowed = false` and
`validation_claim_allowed = false`.

Step142 is a design-only mass-neutral plane-flux controller contract over the
Step141 decision. It did not add a Step121 phase, did not run a real 48^3 row,
did not run 500 steps, and did not enable selected96.

Commit identity note: Step141 was executed with `code_commit_at_run =
90fa5798754942cd8f7de2a1c24a483804667478`. The Step139 source row still
records `step139_code_commit_at_run =
4e43162a641085e56a4ba72c8bc013e58cb08cc3`. These fields are intentionally
separate from the final Step141 report/push commit
`24f5bef3d10e6102fbc2a1cd28c383df81ad7bf3`.

Step142 adds default-disabled report-visible config fields for a future
mass-neutral plane-flux controller:

```text
open_boundary_mass_neutral_flux_control_enabled
open_boundary_mass_neutral_flux_control_mode
open_boundary_mass_neutral_mass_error_gain
open_boundary_mass_neutral_mass_error_cap
open_boundary_mass_neutral_correction_blend
open_boundary_mass_neutral_reference_mass_mode
```

The Step142 readiness artifact is
`outputs/step142_mass_neutral_plane_flux_design/step142_design_readiness_report.json`.
It records `status = design_ready`, `step142_real_48_run_executed = false`,
`step142_single_500step_final_evidence_proposal_allowed = false`,
`selected96_execution_allowed = false`, and
`step143_250step_diagnostic_proposal_allowed = true`. The proposed later phase
name is `planeflux_mass_neutral_design48`, but that phase is not added to
Step121 in Step142.

Step141 adds the distinct `planeflux_density_feedback_isolation48` phase with
exactly four real 48^3 / 250-step rows. All rows use
`row_role = density_feedback_isolation_diagnostic_48` and
`regularized_plane_flux_controlled_pressure_outlet`; only
`open_boundary_flux_feedback_gain_rho` varies across `0.001`, `0.0`,
`0.00025`, and `0.0005`. The role and semantics are not selected-candidate
semantics and cannot enable selected 96^3.

Step141 generated artifacts under
`outputs/step141_density_feedback_isolation`. The audit decision is
`density_feedback_isolation_insufficient`: the baseline repeat with
`gain_rho = 0.001` had the lowest 250-step
`candidate_mass_acceptance_observed_abs = 0.003974863988826804`, while
`gain_rho = 0.0` had `candidate_mass_acceptance_observed_abs =
0.003979989185473907`. All four rows completed 250/250, stayed finite, passed
the bounded 250-step flow-development gate, and kept
`selected96_claim_allowed = false` and `validation_claim_allowed = false`.
Lowering density feedback therefore did not explain or repair Step140's
post-250 tail failure, and Step142 must not proceed to a 500-step final-evidence
run from this diagnostic.

Step140 is a forensics-only long-window drift diagnosis from existing Step139
artifacts. It does not add a Step121 phase, run a new LBM simulation, tune new
parameters, or enable selected96. Its artifact root is
`outputs/step140_long_window_drift_forensics`.

Step140 classifies the Step139 long-window failure mechanism as
`mass_accumulation_with_outlet_stationarity_drift`. The `200_250` segment still
looked like the Step138 short-window pass with `mass_total_delta_rel =
0.003974863988826804`, but `250_300` rose to
`mass_total_delta_rel = 0.010577758938477861` with
`slope_per_step = 0.00013628106427297047`, and the hard-gate `400_500` tail
ended at `mass_total_delta_rel = 0.008321150189010917`. The hard-gate tail also
had `flux_imbalance_rel` mean `0.10270018561574665` and outlet flux CV
`0.11556697847525366`; `near_outlet_to_outlet_flux_ratio` mean stayed close to
one at `0.9978928625164406`, so Step140 does not support a measurement-plane
mismatch-only explanation. The precise Step141 interpretation is
`post_250_mass_excursion_with_tail_acceptance_failure`, not a claim of strictly
monotonic accumulation. Controller saturation stayed at `0.0`, while
`controller_authority_ratio` declined to final `0.38176060964663827` with
`slope_per_step = -0.0017400182162721955`.

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
