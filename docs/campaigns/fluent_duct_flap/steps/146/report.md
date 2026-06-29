# Step146 Report: Coupled Saturation-Stationarity Design Proposal

Step146 is design-only and artifact-only. It reads the committed Step145 and
Step144 artifacts, produces a design readiness artifact, and does not run a new
solver row.

Step144 failed the final hard gate. The single Step144 `48^3 / 500-step`
LBM-only row completed 500/500 and stayed finite, but failed candidate mass
acceptance, mean flux imbalance, and outlet stationarity:

- `candidate_mass_acceptance_observed_abs = 0.007345390662776274`
- `flux_imbalance_rel_tail_mean = 0.1023209978570283`
- `outlet_flux_tail_cv = 0.11500661338208944`
- `mass_neutral_feedback_saturation_fraction_tail = 0.9374677783363148`
- `tail_controller_authority_ratio_slope = -0.0017484489151022653`

Step145 classified this as `mixed_saturation_stationarity_failure`: the
mass-neutral density feedback saturated through the hard-gate tail, but mass
acceptance and outlet stationarity still failed. Step146 therefore does not
recommend raising the mass cap alone.

## Boundary Statements

Step146 did not run a new LBM row.
Step146 did not add a Step121 phase.
Step146 did not run selected96.
Step146 did not run selected-static.
Step146 did not run 96^3.
Step146 did not run a 500-step row.
Step146 did not run Fluent.
Step146 did not run FSI.
Step146 does not make a validation claim.
Step146 keeps selected-candidate-surface review blocked.
Step146 keeps selected96 blocked.
Step146 keeps validation claim blocked.
Step146 keeps the 500-step probe blocked.

selected-candidate-surface review remains blocked.
selected96 remains blocked.
500-step probe remains blocked.

## Outputs

Step146 generated:

- `outputs/step146_coupled_saturation_stationarity_design/step146_design_readiness_report.json`
- `outputs/step146_coupled_saturation_stationarity_design/step146_design_readiness_report.md`
- `docs/campaigns/fluent_duct_flap/steps/146/coupled_saturation_stationarity_design.md`

The readiness artifact records:

- `design_only = true`
- `artifact_only = true`
- `new_lbm_run_executed = false`
- `new_parameter_tuning_executed = false`
- `step121_phase_added = false`
- `selected96_execution_allowed = false`
- `selected_candidate_surface_review_allowed = false`
- `validation_claim_allowed = false`
- `step146_500step_probe_allowed = false`
- `step147_250step_diagnostic_proposal_allowed = true`

## Recommendation

Step146 recommends Design A,
`saturation_aware_mass_neutral_relief_with_stationarity_damping`, for a later
bounded Step147 diagnostic. Design B,
`outlet_population_projection_report_only`, remains fallback telemetry only.

The proposed later Step147 surface is at most four `48^3 / 250-step` rows under
`planeflux_saturation_stationarity48` with
`row_role = saturation_stationarity_diagnostic_48`. Step146 does not implement
that phase and does not execute those rows.
