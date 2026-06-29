# Step147 Saturation-Stationarity Diagnostic Report

Status: `decision_ready`.

Step147 ran exactly four 48^3 / 250-step LBM-only rows.
Step147 did not run selected96.
Step147 did not run selected-static.
Step147 did not run 96^3.
Step147 did not run a 500-step row.
Step147 did not run Fluent.
Step147 did not run FSI.
Step147 does not make a validation claim.
Step147 keeps selected96 blocked.

Source contract:

- `origin/main = 54afab0c6b4bdae05fa08f50f274e8d2f557e1d9`
- Source readiness: `outputs/step146_coupled_saturation_stationarity_design/step146_design_readiness_report.json`
- Source readiness hash: `9970b5e0bcd7eeb05c456a34280025f890ea15b994782d72196755c485cec999`
- Source Step146 status: `design_ready`
- Source Step145 decision: `mixed_saturation_stationarity_failure`
- Source Step144 decision: `mass_neutral_flow_stationarity_long_window_failure`

Artifacts:

- Phase root: `outputs/step147_saturation_stationarity_diagnostic/saturation_stationarity48`
- Decision summary: `outputs/step147_saturation_stationarity_diagnostic/step147_decision_summary.json`
- Comparison JSON: `outputs/step147_saturation_stationarity_diagnostic/step147_saturation_stationarity_comparison.json`
- Comparison CSV: `outputs/step147_saturation_stationarity_diagnostic/step147_saturation_stationarity_comparison.csv`

Rows:

| label | steps | mass abs | outlet CV | mean imbalance | saturation tail | flow gate | collapse |
|---|---:|---:|---:|---:|---:|---|---|
| `baseline_high_repeat` | 250/250 | 0.0031636249081530357 | 0.09161249772040454 | 0.08579940196467845 | 0.8749355566726297 | pass | none |
| `relief_low_slew025` | 250/250 | 0.0022374840016654626 | 0.08431679599209875 | 0.06942484368219749 | 0.7575016526694245 | pass | x=24 at step 240 |
| `relief_mid_slew025` | 250/250 | 0.0021991438855004522 | 0.08380908570402525 | 0.07019307308346165 | 0.844115851855766 | pass | x=24 at step 240 |
| `relief_cap_test_slew025` | 250/250 | 0.002093421390940915 | 0.08294339447357761 | 0.06738282016989694 | 0.7280537236557635 | pass | x=24 at step 240 |

Decision:

- `decision_case = relief_design_unstable`
- `step148_500step_probe_proposal_allowed = false`
- `selected96_execution_allowed = false`
- `selected_static_execution_allowed = false`
- `selected_candidate_surface_review_allowed = false`
- `validation_claim_allowed = false`
- `fluent_validation_claim_allowed = false`
- `fsi_validation_claim_allowed = false`
- `production_readiness_claim_allowed = false`

Interpretation:

All four rows completed the requested bounded window and the relief rows reduced
mass error, outlet CV, and mean imbalance versus the baseline repeat. That is
not sufficient for promotion because all three relief rows reported compact
x-profile collapse at x=24, step 240. The only row without the collapse marker
was the baseline repeat, and its saturation tail remained high at
0.8749355566726297. The Step147 evidence therefore blocks Step148 and requires
a formulation-level diagnosis before any longer-window or selected-boundary
execution.
