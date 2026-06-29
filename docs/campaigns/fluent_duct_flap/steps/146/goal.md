# Step146 Goal: Coupled Saturation-Stationarity Design Proposal

## Purpose

Step146 must turn the Step145 artifact-only forensics result into a bounded
design proposal for the next diagnostic surface. Step145 classified the Step144
long-window failure as `mixed_saturation_stationarity_failure`: the
mass-neutral density feedback saturated through the Step144 hard-gate tail, but
candidate mass acceptance, mean flux imbalance, and outlet stationarity all
remained outside gate.

Step146 must not run a new solver row. The goal is to produce an artifact-only
readiness report and design note that answer one question:

```text
Given Step144 mass-neutral feedback saturation plus recurring outlet
stationarity failure, what bounded Step147 diagnostic should be proposed
without relaxing any selected96, selected-candidate, 500-step, Fluent, FSI, or
validation gate?
```

## Hard Scope Boundaries

Step146 is design-only and artifact-only. It must preserve every boundary below:

- Do not add a Step121 real phase.
- Do not run LBM.
- Do not run a 48^3 row.
- Do not run a 500-step row.
- Do not run selected96.
- Do not run selected-static.
- Do not run 96^3.
- Do not run Fluent.
- Do not run FSI.
- Do not claim validation.
- Do not relax any gate.
- Do not start selected-candidate-surface review.
- Do not modify solver formulas, population reconstruction, or runtime stepping.
- Do not tune a parameter sweep in Step146.
- Do not synthesize readiness when source artifacts are missing or contradict
  the Step145 decision.

Step146 may only propose, not execute, a later Step147 bounded 48^3 / 250-step
diagnostic. Step146 must keep the later 500-step probe blocked.

## Required Source Inputs

The Step146 report generator may read only these committed artifacts:

- `outputs/step145_mass_neutral_long_window_forensics/step145_failure_mechanism_summary.json`
- `outputs/step145_mass_neutral_long_window_forensics/saturation_segment_report.json`
- `outputs/step145_mass_neutral_long_window_forensics/stationarity_segment_report.json`
- `outputs/step145_mass_neutral_long_window_forensics/controller_lag_segment_report.json`
- `outputs/step144_mass_neutral_final48/step144_decision_summary.json`
- `outputs/step144_mass_neutral_final48/step144_long_window_comparison.json`

If any required input is missing, the generator must emit:

```text
status = missing_input
missing_input = true
design_readiness_present = false
recommended_design = null
step147_250step_diagnostic_proposal_allowed = false
```

The missing-input path must not fabricate a design readiness conclusion.

## Required Source Decision Gates

Step146 readiness is valid only when the source artifacts prove all of the
following:

```text
source_step145_decision_case = mixed_saturation_stationarity_failure
source_step145_dominant_failure_mechanism = mixed_saturation_stationarity_failure
source_step146_500step_probe_allowed = false
source_selected_candidate_surface_review_allowed = false
source_selected96_execution_allowed = false
source_validation_claim_allowed = false
source_step144_decision_case = mass_neutral_flow_stationarity_long_window_failure
```

If the source decision does not satisfy those gates, the generator must emit:

```text
status = blocked_by_source_decision
missing_input = false
design_readiness_present = false
recommended_design = null
step147_250step_diagnostic_proposal_allowed = false
step146_500step_probe_allowed = false
```

## Files To Add

- `docs/campaigns/fluent_duct_flap/steps/146/goal.md`
- `docs/campaigns/fluent_duct_flap/steps/146/report.md`
- `docs/campaigns/fluent_duct_flap/steps/146/coupled_saturation_stationarity_design.md`
- `experiments/steps/step146_coupled_saturation_stationarity_design_report.py`
- `tests/test_step146_coupled_saturation_stationarity_design_contract.py`
- `outputs/step146_coupled_saturation_stationarity_design/step146_design_readiness_report.json`
- `outputs/step146_coupled_saturation_stationarity_design/step146_design_readiness_report.md`

## Files To Update

- `docs/current/ACTIVE_CAMPAIGN.json`
- `docs/current/STATUS.md`
- `docs/current/VALIDATION_GATES.md`
- `docs/current/READING_ORDER.md`
- `README.md`

`ACTIVE_CAMPAIGN.json` must also record the Step145 final push identity:

```json
{
  "final_repository_head_after_step145_push": "8f4199f1d454f929dc1ebcdd29ee297b0ffa5ab8",
  "step145_artifact_generation_base_commit": "6fdf9bddea667bdbf36ab0f8e802c12db2a0def5"
}
```

The wording must keep these identities distinct: Step145 artifacts were derived
from the Step144/Step145 artifact state, while the final Step145 remote commit
records the reviewed docs/tests/artifacts push.

## Design Content

Step146 must evaluate two design options and recommend only one for Step147.

### Design A: Saturation-Aware Mass-Neutral Relief With Stationarity Damping

Design A is the recommended Step147 diagnostic direction.

Core idea:

```text
When mass-neutral density feedback is saturated for a long tail window, do not
blindly raise the cap. Reduce how aggressively mass correction couples into the
outlet while adding stationarity damping, so the diagnostic can separate mass
relief from outlet oscillation amplification.
```

The proposed Step147 row surface is bounded to at most four 48^3 / 250-step
rows:

```text
mass_neutral_high_baseline:
  gain_mass = 0.50
  cap_mass = 0.00100
  blend = 1.0
  role = repeat current Step144/Step143 high setting baseline

relief_low:
  gain_mass = 0.35
  cap_mass = 0.00100
  blend = 0.50
  stationarity damping stronger:
    slew_alpha = 0.25 or delta_cap_u = 0.00025

relief_mid:
  gain_mass = 0.50
  cap_mass = 0.00100
  blend = 0.50
  stationarity damping stronger

relief_cap_test:
  gain_mass = 0.50
  cap_mass = 0.00150
  blend = 0.50
  role = diagnostic cap test only, not promotion
```

The key design rule is: do not recommend a cap increase alone. A cap test may
only appear as a diagnostic row paired with lower blend and stationarity
damping.

### Design B: Outlet Population Projection Feasibility, Report-Only

Design B is the fallback telemetry design. It must stay report-only in Step146.

Core idea:

```text
Do not change runtime population reconstruction in Step146. Instead, define a
future report-only feasibility calculation for a zeroth-moment neutral
projection: estimate the population correction needed and the possible
x-momentum cost before any runtime activation is considered.
```

Design B is not recommended for direct Step147 execution unless Design A later
fails or proves uninformative. Step146 must not implement population projection.

## Required Readiness Artifact

`step146_design_readiness_report.json` must include at least:

```json
{
  "step": 146,
  "artifact": "step146_coupled_saturation_stationarity_design_readiness",
  "source_step": 145,
  "source_step145_decision_case": "mixed_saturation_stationarity_failure",
  "source_step145_summary_hash": "...",
  "design_only": true,
  "artifact_only": true,
  "new_lbm_run_executed": false,
  "new_parameter_tuning_executed": false,
  "step121_phase_added": false,
  "selected96_execution_allowed": false,
  "selected_static_execution_allowed": false,
  "selected_candidate_surface_review_allowed": false,
  "validation_claim_allowed": false,
  "fluent_validation_claim_allowed": false,
  "fsi_validation_claim_allowed": false,
  "step146_500step_probe_allowed": false,
  "step147_250step_diagnostic_proposal_allowed": true,
  "recommended_design": "saturation_aware_mass_neutral_relief_with_stationarity_damping",
  "fallback_design": "outlet_population_projection_report_only",
  "recommended_step147_phase": "planeflux_saturation_stationarity48",
  "recommended_step147_row_role": "saturation_stationarity_diagnostic_48",
  "max_step147_rows": 4,
  "max_step147_steps": 250
}
```

It must also preserve artifact-backed Step144/Step145 facts:

- `step144_final_mass_abs = 0.007345390662776274`
- `step144_flux_imbalance_rel_tail_mean = 0.1023209978570283`
- `step144_outlet_flux_tail_cv = 0.11500661338208944`
- `step144_mass_neutral_feedback_saturation_fraction_tail = 0.9374677783363148`
- `tail_controller_authority_ratio_slope = -0.0017484489151022653`

These values may be read from the existing artifacts rather than hardcoded in
tests, but the committed report must surface them.

## Contract Tests

Add `tests/test_step146_coupled_saturation_stationarity_design_contract.py` and
cover at least:

1. The report generator exposes only the six Step145/Step144 source input paths.
2. The report generator does not import the Step121 real campaign runner and
   does not import solver runtime modules.
3. Missing source input returns `missing_input`, writes JSON/Markdown summary,
   and does not synthesize readiness.
4. A wrong Step145 decision returns `blocked_by_source_decision`.
5. Valid readiness requires `source_step145_decision_case =
   mixed_saturation_stationarity_failure`.
6. Valid readiness sets `design_only = true` and `artifact_only = true`.
7. Valid readiness sets `new_lbm_run_executed = false`.
8. Valid readiness sets `new_parameter_tuning_executed = false`.
9. Valid readiness sets `step121_phase_added = false`.
10. Valid readiness sets `selected96_execution_allowed = false`.
11. Valid readiness sets `selected_candidate_surface_review_allowed = false`.
12. Valid readiness sets `validation_claim_allowed = false`.
13. Valid readiness sets `step146_500step_probe_allowed = false`.
14. Valid readiness sets `step147_250step_diagnostic_proposal_allowed = true`.
15. The recommended Step147 phase is proposal-only in Step146 and is not added
    to Step121.
16. Step121 source has no `STEP146`, no `planeflux_saturation_stationarity48`,
    and no Step146 runner reference.
17. Source text contains no selected96, selected-static, 96^3, Fluent, FSI, or
    500-step execution command except as forbidden/boundary text.
18. Current docs preserve Step144 failure and Step145
    `mixed_saturation_stationarity_failure`.
19. Current docs say selected96, selected-candidate-surface review, 500-step
    probe, and validation remain blocked.
20. README points readers to the Step146 status without claiming validation.

## Verification Commands

Use the trusted local interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step146-red `
  tests\test_step146_coupled_saturation_stationarity_design_contract.py

& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step146_coupled_saturation_stationarity_design_report.py `
  tests\test_step146_coupled_saturation_stationarity_design_contract.py

& 'D:\working\taichi\env\python.exe' -m experiments.steps.step146_coupled_saturation_stationarity_design_report `
  --step145-summary outputs\step145_mass_neutral_long_window_forensics\step145_failure_mechanism_summary.json `
  --step145-saturation outputs\step145_mass_neutral_long_window_forensics\saturation_segment_report.json `
  --step145-stationarity outputs\step145_mass_neutral_long_window_forensics\stationarity_segment_report.json `
  --step145-controller outputs\step145_mass_neutral_long_window_forensics\controller_lag_segment_report.json `
  --step144-decision outputs\step144_mass_neutral_final48\step144_decision_summary.json `
  --step144-comparison outputs\step144_mass_neutral_final48\step144_long_window_comparison.json `
  --output-dir outputs\step146_coupled_saturation_stationarity_design `
  --force

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step146-focused `
  tests\test_step146_coupled_saturation_stationarity_design_contract.py `
  tests\test_step145_mass_neutral_long_window_forensics_contract.py `
  tests\test_step144_mass_neutral_final48_contract.py `
  tests\test_step143_mass_neutral_design_contract.py `
  tests\test_step142_mass_neutral_plane_flux_design_contract.py `
  tests\test_step141_density_feedback_isolation_contract.py `
  tests\test_step140_long_window_drift_forensics_contract.py

& 'D:\working\taichi\env\python.exe' -c "<json load check for Step146 artifacts and current docs>"

git diff --check
```

## Completion Criteria

Step146 is complete only when:

- The detailed goal is committed under
  `docs/campaigns/fluent_duct_flap/steps/146/goal.md`.
- The short working goal references that file directly.
- A focused RED test fails before implementation for the missing Step146
  surface.
- The Step146 generator emits the required JSON and Markdown reports from
  existing Step145/Step144 artifacts only.
- The generated report recommends Design A and keeps Design B as fallback
  telemetry.
- The generated report blocks selected96, selected-static, selected-candidate
  review, validation, Fluent, FSI, and a Step146 500-step probe.
- Current docs and README point to Step146 without changing the campaign claim
  boundaries.
- Focused Step140-Step146 regression passes.
- JSON artifacts load successfully.
- `git diff --check` passes.
- The final commit is pushed to `origin/main`, with remote ref proof.

If the normal pre-push hook times out after focused verification has passed,
the final report must state that the focused verification passed, the pre-push
hook timed out, the push used `--no-verify`, and `origin/main` was verified by
remote ref.
