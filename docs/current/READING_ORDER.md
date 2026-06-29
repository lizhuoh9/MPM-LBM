# Reading Order

Read these files first for the current boundary-repair campaign state:

1. `docs/current/STATUS.md`
2. `docs/current/ACTIVE_CAMPAIGN.json`
3. `docs/current/VALIDATION_GATES.md`
4. `docs/current/READING_ORDER.md`
5. `docs/campaigns/fluent_duct_flap/steps/142/goal.md`
6. `docs/campaigns/fluent_duct_flap/steps/142/report.md`
7. `docs/campaigns/fluent_duct_flap/steps/142/mass_neutral_plane_flux_design.md`
8. `outputs/step142_mass_neutral_plane_flux_design/step142_design_readiness_report.json`
9. `docs/campaigns/fluent_duct_flap/steps/141/goal.md`
10. `docs/campaigns/fluent_duct_flap/steps/141/report.md`
11. `outputs/step141_density_feedback_isolation/step141_decision_summary.json`
12. `outputs/step141_density_feedback_isolation/step141_density_feedback_comparison.json`
13. `docs/campaigns/fluent_duct_flap/steps/140/goal.md`
14. `docs/campaigns/fluent_duct_flap/steps/140/report.md`
15. `outputs/step140_long_window_drift_forensics/step140_failure_mechanism_summary.json`
16. `docs/campaigns/fluent_duct_flap/steps/139/report.md`
17. `outputs/step139_planeflux_final48/step139_long_window_comparison.json`
18. `outputs/step139_planeflux_final48/step139_failure_forensics.json`
19. `docs/GENERIC_SOLVER_ARCHITECTURE_CONTRACT.md`
20. `docs/campaigns/fluent_duct_flap/fluent_official_local_execution_guard.md`
21. `outputs/fluent_official_local_execution_prep/guard_report.json`
22. `docs/campaigns/fluent_duct_flap/steps/138/report.md`
23. `experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py`

Older Step102-Step126 documents remain useful history, but they are not the
current entry point for deciding whether the campaign may advance to selected
96^3. Step127 found that both old real 48^3 candidate boundaries failed hard
gates. Step128 added a repaired-boundary code surface and `repair48` phase.
Step129 ran both repaired 48^3 / 500-step candidates; both completed but failed
flow-development hard gates. Step130 added `flowrepair48` 250-step triage; both
flow-repair rows completed but failed promotion gates, so selected 96^3 remains
blocked. Step131 added `planeflux48` 250-step triage with a true
plane-integrated flux-error controller; both rows completed but failed promotion
gates. Step132 added `planeflux_sweep48` controller-authority triage; all six
real 48^3 / 250-step rows completed, stayed finite, and had no first-failure
event, but accepted row count remained zero. Step133 added
`planeflux_mass_damped48` slow density feedback and feedback-damping triage; all
six real 48^3 / 250-step rows completed, stayed finite, and had no
first-failure event, but accepted row count remained zero. Step134 added
`planeflux_stationarity48` outlet tail-collapse diagnosis and near-outlet
control-plane offsets; all six real 48^3 / 250-step rows completed, stayed
finite, and had no first-failure event, but accepted row count remained zero.
No Step134 500-step promotion or selected 96^3 run is justified, so selected
96^3 remains blocked. Step135 added `planeflux_interior_diag48` interior
reflection / bulk-dynamics diagnostics; all six real 48^3 / 250-step diagnostic
rows completed, stayed finite, and had no first-failure event, but no row passed
the relaxed reporting gates. Step135 points to bulk/startup transient behavior,
not an outlet-local readout artifact. No Step135 500-step promotion or selected
96^3 run is justified. Step136 added `planeflux_ramp_tuned48` ramped-inlet
throughput calibration and `open_boundary_flux_control_target_scale`; all six
real 48^3 / 250-step calibration rows completed, stayed finite, and had no
first-failure event. Target0.90 and target0.95 passed candidate mass
acceptance, but all six rows still failed flow-development gates. No Step136
500-step promotion or selected 96^3 run is justified. Step137 added
`planeflux_ramp_refined48` refined ramp-target diagnostics; all six real 48^3 /
250-step rows completed, stayed finite, passed candidate mass acceptance, and
avoided compact x-profile collapse, but all six still failed final hard
flow-development gates. No Step137 500-step promotion or selected 96^3 run is
justified. Step138 added `planeflux_high_authority48` high-authority outlet
diagnostics; all six real 48^3 / 250-step rows completed and stayed finite.
One row, ramp85 / target0.80 / gain0.75 / cap0.0075, passed the full final hard
gate including mass acceptance and no compact-collapse label. This justifies a
later Step139 single 48^3 / 500-step final-evidence proposal only. Step138 did
not run 500 steps, did not add selected-candidate semantics, and selected 96^3
remains blocked. Step139 ran that single Step138 source row for 500 steps as
`planeflux_final48`; it completed 500/500, stayed finite, had no first-failure
event, and had no compact-collapse label, but failed the final hard gate on
candidate mass acceptance, mean flux imbalance, and outlet stationarity.
Step139 therefore falsifies the Step138 short-window promotion candidate. No
selected boundary, Step140 promotion, selected 96^3, quasi-2D validation, FSI
validation, Fluent validation, Figure 29.3 parity, or production-readiness
claim is justified. Step140 is a forensics-only read of the existing Step139
artifacts. It classifies the long-window failure as
`mass_accumulation_with_outlet_stationarity_drift`: mass acceptance failed after
the 250-step window, outlet stationarity and mean flux imbalance failed in the
400-500 hard-gate tail, and controller authority decayed without saturation.
Step140 did not add a Step121 phase, did not run LBM, did not tune parameters,
and did not enable selected96. Step141 then ran exactly four bounded 48^3 /
250-step density-feedback isolation rows. All four completed and passed the
bounded 250-step checks, but reducing or removing `gain_rho` did not improve
mass acceptance versus the `gain_rho = 0.001` baseline repeat. Step141 reports
`density_feedback_isolation_insufficient`, does not allow a Step142 500-step
final-evidence proposal, and selected 96^3 remains blocked. Step142 is the
design-only mass-neutral plane-flux controller contract for a later bounded
diagnostic. It adds default-disabled config/report surfaces and readiness
artifacts only; it does not add a Step121 phase, run real 48^3/500-step rows,
or enable selected96.
