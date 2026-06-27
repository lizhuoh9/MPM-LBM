# Step131 Plane-Flux Closed-Loop Outlet Repair Report

## Result

Step131 added a true plane-integrated flux-error controller for the LBM-only
open-boundary repair surface and ran the requested bounded 48^3 / 250-step
`planeflux48` triage rows.

Both Step131 rows completed 250/250 with finite density/population/mach
behavior and no first-failure event. Both rows still failed candidate mass
acceptance and the flow-development hard gates. No 500-step promotion was
justified, and selected 96^3 remains blocked.

This step does not claim repaired 48^3 acceptance, selected 96^3 success,
quasi-2D validation, FSI validation, Fluent validation, or Figure 29.3 parity.

## Code Surface

Implemented and tested:

- New semantics:
  `regularized_plane_flux_controlled_pressure_outlet` and
  `convective_plane_flux_controlled_damped_outlet`.
- A Taichi-side scalar plane-flux controller:
  `target_outlet_flux = inlet_flux_plane`,
  `measured_outlet_flux = outlet_flux_plane`,
  `raw_error = target_outlet_flux - measured_outlet_flux`,
  low-pass filtered error, and bounded
  `u_feedback = gain_u * filtered_error / outlet_fluid_area`.
- New controller diagnostics in the bounded flow-development CSV/JSON surface:
  target/measured outlet flux, raw/filtered controller error, bounded
  controller velocity feedback, and saturation counters.
- New Step121 phase:
  `planeflux48`, with `row_role = plane_flux_control_candidate_48`.
- Step131 semantics are intentionally separate from Step130 semantics and are
  not included in the selected-candidate surface. They do not enable selected
  96^3.

## Tiny Smoke Evidence

Artifact root:
`outputs/step131_plane_flux_controller_smoke/tiny_step131_regularized_plane_flux_controller_20step_smoke`

Runtime code commit:
`8b5e5ff5767073ad15d46f779c6c1f18348f4b5d`

The 8x6x6 / 20-step smoke completed 20/20 with `finite_pass = true`,
`requested_window_completed = true`, `first_failure_reason = null`, and
`validation_claim_allowed = false`. This smoke is only a controller sign/cap and
diagnostics check; it is not validation evidence.

## Real Triage Evidence

Artifact root:
`outputs/step121_lbm_boundary_real_campaign_and_gate_correction`

Runtime code commit used by the triage rows:
`8b5e5ff5767073ad15d46f779c6c1f18348f4b5d`

Rows:

- `duct_only_48_regularized_plane_flux_controlled_pressure_outlet_250step_triage`
  - Completed 250/250.
  - `finite_pass = true`, `density_gate_pass = true`,
    `hard_stop_mass_drift_gate_pass = true`, `population_gate_pass = true`,
    `mach_gate_pass = true`, `first_failure_step = null`.
  - `mass_total_delta_rel_final = -0.0283421114698597`.
  - `candidate_mass_acceptance_observed_abs = 0.0283421114698597`,
    above the 0.005 candidate threshold.
  - `flow_development_gate_pass = false`.
  - `flux_imbalance_rel_tail_mean = 0.39787865621449087`.
  - `flux_imbalance_rel_tail_max = 0.5034860408405382`.
  - `outlet_to_inlet_flux_ratio_tail_mean = 1.6088762675407298`.
  - `midplane_to_inlet_flux_ratio_tail_mean = 1.3339702270861844`.
  - `outlet_flux_tail_cv = 0.3523076810492384`.
  - Controller tail mean:
    `target = 41.07821528116862`,
    `measured = 67.7467753092448`,
    `raw_error = -26.668560028076172`,
    `filtered_error = -34.22179921468099`,
    `u_feedback = -4.043218238318028e-05`.
  - `controller_saturation_fraction_run = 0.0`.
- `duct_only_48_convective_plane_flux_controlled_damped_outlet_250step_triage`
  - Completed 250/250.
  - `finite_pass = true`, `density_gate_pass = true`,
    `hard_stop_mass_drift_gate_pass = true`, `population_gate_pass = true`,
    `mach_gate_pass = true`, `first_failure_step = null`.
  - `mass_total_delta_rel_final = -0.02858492044911549`.
  - `candidate_mass_acceptance_observed_abs = 0.02858492044911549`,
    above the 0.005 candidate threshold.
  - `flow_development_gate_pass = false`.
  - `flux_imbalance_rel_tail_mean = 0.4090919843128926`.
  - `flux_imbalance_rel_tail_max = 0.5348760352869728`.
  - `outlet_to_inlet_flux_ratio_tail_mean = 1.7338794180572676`.
  - `midplane_to_inlet_flux_ratio_tail_mean = 1.60001489270226`.
  - `outlet_flux_tail_cv = 0.15801241453426013`.
  - Controller tail mean:
    `target = 39.63297780354818`,
    `measured = 68.60497792561848`,
    `raw_error = -28.972000122070312`,
    `filtered_error = -34.1552308400472`,
    `u_feedback = -4.035353291934977e-05`.
  - `controller_saturation_fraction_run = 0.0`.

Step121 summary after Step131:

- `campaign_state = 48_candidates_failed`
- `final_classification = boundary_repair_failed_revisit_lbm_solver`
- `best_boundary_selected = false`
- `quasi2d_allowed = false`
- `validation_claim_allowed = false`

## Decision

Step131 is a valid code-surface and bounded diagnostic step. The real 48^3
triage artifacts prove the controller can run through the requested 250-step
window and record controller diagnostics, but the two new rows still do not meet
promotion criteria.

The next step should remain 48^3 LBM-only boundary formulation/debugging. It
should not start selected 96^3, quasi-2D, FSI, Fluent parity, or Figure 29.3
work until a future 48^3 candidate passes the hard gates.

## Verification

Commands run with `D:\working\taichi\env\python.exe`:

```text
python -m py_compile src\mpm_lbm\sim\lbm\config.py src\mpm_lbm\sim\lbm\fluid.py experiments\steps\step120_lbm_boundary_repair_large_real_execution.py experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py tests\test_step131_plane_flux_controller_contract.py
python -m pytest -q --basetemp outputs\tmp\pytest-step131-full tests\test_step131_plane_flux_controller_contract.py
python -m pytest -q --basetemp outputs\tmp\pytest-step131-adjacent-old tests\test_step130_flow_development_repair_contract.py tests\test_step130_flow_development_diagnostics_contract.py tests\test_step129_repair_checkpoint_counter_contract.py tests\test_step128_boundary_formulation_repair_contract.py tests\test_step125_campaign_provenance_identity_contract.py tests\test_step124_boundary_campaign_execution_contract.py tests\test_step123_boundary_campaign_execution_decision_contract.py
python -m pytest -q --basetemp outputs\tmp\pytest-step131-policy-solo tests\test_step56_behavior_preservation_contract.py tests\test_step57_step56_regression_contract.py tests\test_step58_step57_regression_contract.py
python -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase planeflux48 --allow-large-real-rows --output-interval 25 --force
python -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase summary
python -m pytest -q --basetemp outputs\tmp\pytest-step131-final-all
git diff --check
```

Verification results:

- Step131 contract tests: 7 passed.
- Adjacent Step123-Step130 focused regression: 44 passed.
- Step56/57/58 behavior-preservation guards: 10 passed.
- `py_compile`: passed.
- Tiny controller smoke: completed 20/20, finite.
- Step131 `planeflux48`: both 48^3 rows completed 250/250, finite, no
  first-failure event, but both failed promotion gates.
- Full suite: 1347 passed, 76 warnings.
- `git diff --check`: passed with only Windows line-ending warnings.
