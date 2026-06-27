# Step130 Flow-Development Repair Triage Report

## Result

Step130 added a bounded third-generation LBM-only outlet repair surface and ran
the two requested 48^3 / 250-step triage rows. Both rows completed the requested
250/250 window with finite density/population/mach behavior and no first-failure
event, but both failed the Step121 flow-development hard gate and failed the
candidate mass-acceptance threshold. No 500-step promotion was justified, and
selected 96^3 remains blocked.

This step does not claim repaired 48^3 acceptance, selected 96^3 success,
quasi-2D validation, FSI validation, Fluent validation, or Figure 29.3 parity.

## Code Surface

Implemented and tested:

- New semantics:
  `regularized_flux_matched_pressure_outlet` and
  `convective_flux_matched_damped_outlet`.
- New bounded open-boundary controls:
  `open_boundary_flux_feedback_gain_u`,
  `open_boundary_flux_feedback_gain_rho`,
  `open_boundary_flux_filter_alpha`,
  `open_boundary_flux_correction_cap_u`, and
  `open_boundary_convective_blend_weight`.
- New flow-development diagnostics:
  `flow_development_diagnostics.csv`,
  `flow_development_diagnostics_summary.json`, outlet-plane ux stats,
  midplane flux, sampled x-profile flux, and correction counters.
- New Step121 phase:
  `flowrepair48`, with `row_role = flow_repair_candidate_48`.
- Step130 semantics are intentionally not included in the selected-candidate
  surface. They do not enable selected 96^3.

## Real Triage Evidence

Artifact root:
`outputs/step121_lbm_boundary_real_campaign_and_gate_correction`

Runtime code commit used by the triage rows:
`cf6576dfa8fa25477510a40a7711ca4667625ea1`

Rows:

- `duct_only_48_regularized_flux_matched_pressure_outlet_250step_triage`
  - Completed 250/250.
  - `finite_pass = true`, `density_gate_pass = true`,
    `mass_drift_gate_pass = true`, `population_gate_pass = true`,
    `mach_gate_pass = true`, `first_failure_step = null`.
  - `mass_total_delta_rel_final = -0.027093607822589214`.
  - `candidate_mass_acceptance_observed_abs = 0.027093607822589214`,
    above the 0.005 candidate threshold.
  - `flow_development_gate_pass = false`.
  - `flux_imbalance_rel_tail_mean = 0.391091092110087`.
  - `flux_imbalance_rel_tail_max = 0.49363649493296946`.
  - `outlet_to_inlet_flux_ratio_tail_mean = 1.582099528142026`.
  - `midplane_to_inlet_flux_ratio_tail_mean = 1.319799119019448`.
  - `outlet_flux_tail_cv = 0.3462613196020457`.
- `duct_only_48_convective_flux_matched_damped_outlet_250step_triage`
  - Completed 250/250.
  - `finite_pass = true`, `density_gate_pass = true`,
    `mass_drift_gate_pass = true`, `population_gate_pass = true`,
    `mach_gate_pass = true`, `first_failure_step = null`.
  - `mass_total_delta_rel_final = -0.030650375098126185`.
  - `candidate_mass_acceptance_observed_abs = 0.030650375098126185`,
    above the 0.005 candidate threshold.
  - `flow_development_gate_pass = false`.
  - `flux_imbalance_rel_tail_mean = 0.5063421113905975`.
  - `flux_imbalance_rel_tail_max = 0.5638390864941747`.
  - `outlet_to_inlet_flux_ratio_tail_mean = 2.0460586163795886`.
  - `midplane_to_inlet_flux_ratio_tail_mean = 1.097643901750551`.
  - `outlet_flux_tail_cv = 0.08348317549327117`.

Step121 summary after Step130:

- `campaign_state = 48_candidates_failed`
- `final_classification = boundary_repair_failed_revisit_lbm_solver`
- `best_boundary_selected = false`
- `quasi2d_allowed = false`
- `validation_claim_allowed = false`

## Decision

Step130 is a valid bounded diagnostic and repair-surface step. Its 250-step
triage rows are real simulation-backed artifacts, but they are not sufficient to
advance. Because both flowrepair rows failed hard flow-development gates and
candidate mass acceptance, no 500-step follow-up was run in this step.

The next step should stay in 48^3 LBM-only boundary formulation/debugging. It
should not start selected 96^3, quasi-2D, FSI, Fluent parity, or Figure 29.3
work until a future 48^3 candidate passes the hard gates.

## Verification

Commands run with `D:\working\taichi\env\python.exe`:

```text
python -m py_compile src\mpm_lbm\sim\lbm\config.py src\mpm_lbm\sim\lbm\fluid.py src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py experiments\steps\step118_lbm_open_boundary_stability_repair.py experiments\steps\step120_lbm_boundary_repair_large_real_execution.py experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py
python -m pytest -q --basetemp outputs\tmp\pytest-step130-green tests\test_step130_flow_development_repair_contract.py tests\test_step130_flow_development_diagnostics_contract.py
python -m pytest -q --basetemp outputs\tmp\pytest-step130-adjacent tests\test_step130_flow_development_repair_contract.py tests\test_step130_flow_development_diagnostics_contract.py tests\test_step129_repair_checkpoint_counter_contract.py tests\test_step128_boundary_formulation_repair_contract.py tests\test_step125_campaign_provenance_identity_contract.py tests\test_step124_boundary_campaign_execution_contract.py tests\test_step123_boundary_campaign_execution_decision_contract.py
python -m pytest -q tests\test_step56_behavior_preservation_contract.py tests\test_step57_step56_regression_contract.py tests\test_step58_step57_regression_contract.py
python -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase flowrepair48 --allow-large-real-rows --output-interval 25
python -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase summary
git diff --check
```

Verification results:

- Step130 contract tests: 8 passed.
- Adjacent Step123-Step130 focused regression: 44 passed.
- Step56/57/58 behavior-preservation guards after Step130 config defaults:
  10 passed.
- `py_compile`: passed.
- `git diff --check`: passed with only Windows line-ending warnings.
