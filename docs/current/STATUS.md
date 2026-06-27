# Current Status

The active campaign is the Fluent duct/flap LBM open-boundary repair campaign.
The current artifact state is `48_candidates_failed` with final classification
`boundary_repair_failed_revisit_lbm_solver`.

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
allowed from the current artifacts. Step128, Step129, and Step130 continue that
blocked 48^3 boundary-repair sequence without selecting a boundary. Step131
continues the same blocked 48^3 boundary-repair sequence without selecting a
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

Step131 does not claim 48^3 repaired-candidate success, selected 96^3 success,
quasi-2D validation, FSI validation, Fluent validation, or Figure 29.3 parity.
