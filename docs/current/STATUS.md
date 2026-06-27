# Current Status

The active campaign is the Fluent duct/flap LBM open-boundary repair campaign.
The current artifact state remains selected-boundary blocked. Step135 is a
diagnostic continuation of the 48^3 boundary-repair loop, not selected-candidate
evidence.

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
Step132, Step133, Step134, and Step135 continue that blocked 48^3
boundary-repair sequence without selecting a boundary.

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

Step135 does not claim 48^3 repaired-candidate success, selected 96^3 success,
quasi-2D validation, FSI validation, Fluent validation, or Figure 29.3 parity.
