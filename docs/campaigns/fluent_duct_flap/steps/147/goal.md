# Step147 Goal: Saturation-Stationarity 48^3 / 250-Step Diagnostic

## Purpose

Step147 is the first bounded real diagnostic allowed by Step146. Step146 was
design-only and artifact-only; it recommended a later small diagnostic surface
for coupled mass-neutral saturation and outlet stationarity failure. Step147
may execute that diagnostic surface, but it must remain a bounded diagnostic
only.

Core question:

```text
If mass-neutral actuator aggressiveness is reduced and stationarity damping is
introduced, can a 48^3 / 250-step LBM-only diagnostic reduce mass drift, outlet
CV, mean flux imbalance, and mass-neutral saturation together, without
selected96, selected-candidate review, 500-step evidence, Fluent, FSI, or
validation claims?
```

Step147 is not promotion evidence. Step144 already proved that a 250-step
improvement is not enough to claim 500-step readiness. Step147 can only decide
whether a later Step148 single 48^3 / 500-step probe may be proposed for the
exact best Step147 relief row, and only if the coupled 250-step criteria pass.

## Hard Scope Boundaries

Step147 must preserve every boundary below:

- At most four real rows.
- 48^3 only.
- 250 steps only.
- `output_interval = 5`.
- LBM-only diagnostic rows only.
- No 500-step row.
- No selected96 execution.
- No selected-static execution.
- No 96^3 execution.
- No Fluent execution.
- No FSI execution.
- No validation claim.
- No selected-candidate-surface review.
- No gate relaxation.
- No solver-formula changes.
- Do not add `regularized_plane_flux_controlled_pressure_outlet` to
  `CANDIDATE_SEMANTICS` or `REPAIRED_CANDIDATE_SEMANTICS`.
- Do not add `saturation_stationarity_diagnostic_48` to
  `SELECTED_CHAIN_ROLES`.
- Do not mark any Step147 row as selected-candidate semantics.
- Do not allow selected96 even if all mocked Step147 metrics pass.

## Required Source Gate

Step147 must read and lock:

```text
outputs/step146_coupled_saturation_stationarity_design/step146_design_readiness_report.json
```

The Step147 phase resolver must fail fast if the Step146 readiness artifact is
missing or does not satisfy:

```text
status = design_ready
source_step145_decision_case = mixed_saturation_stationarity_failure
source_step144_decision_case = mass_neutral_flow_stationarity_long_window_failure
recommended_design = saturation_aware_mass_neutral_relief_with_stationarity_damping
recommended_step147_phase = planeflux_saturation_stationarity48
recommended_step147_row_role = saturation_stationarity_diagnostic_48
step147_250step_diagnostic_proposal_allowed = true
step146_500step_probe_allowed = false
selected96_execution_allowed = false
selected_candidate_surface_review_allowed = false
validation_claim_allowed = false
max_step147_rows <= 4
max_step147_steps = 250
```

Every Step147 manifest and audit row must record:

```text
source_step = 146
source_step146_readiness_path
source_step146_readiness_hash
source_step146_status = design_ready
source_step146_recommended_design = saturation_aware_mass_neutral_relief_with_stationarity_damping
source_step146_recommended_phase = planeflux_saturation_stationarity48
source_step146_recommended_row_role = saturation_stationarity_diagnostic_48
source_step145_decision_case = mixed_saturation_stationarity_failure
source_step144_decision_case = mass_neutral_flow_stationarity_long_window_failure
selected96_claim_allowed = false
validation_claim_allowed = false
```

Completed row reuse must reject stale row directories if the recorded
`source_step146_readiness_hash` or `mass_neutral_activation_hash` differs from
the expected row spec.

## Files To Add

- `docs/campaigns/fluent_duct_flap/steps/147/goal.md`
- `docs/campaigns/fluent_duct_flap/steps/147/report.md`
- `experiments/steps/step147_saturation_stationarity_audit.py`
- `tests/test_step147_saturation_stationarity_contract.py`
- `outputs/step147_saturation_stationarity_diagnostic/saturation_stationarity48/...`
- `outputs/step147_saturation_stationarity_diagnostic/step147_saturation_stationarity_comparison.json`
- `outputs/step147_saturation_stationarity_diagnostic/step147_saturation_stationarity_comparison.csv`
- `outputs/step147_saturation_stationarity_diagnostic/step147_decision_summary.json`

## Files To Update

- `experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py`
- `experiments/steps/step120_lbm_boundary_repair_large_real_execution.py` if
  needed for provenance/manifest enforcement.
- `docs/current/ACTIVE_CAMPAIGN.json`
- `docs/current/STATUS.md`
- `docs/current/VALIDATION_GATES.md`
- `docs/current/READING_ORDER.md`
- `README.md`

Prefer not to edit solver-core files. Step147 should use existing mass-neutral
config fields and existing plane-flux controller damping surfaces.

## Exact Phase

Step147 must add exactly one diagnostic phase:

```text
phase = planeflux_saturation_stationarity48
row_role = saturation_stationarity_diagnostic_48
semantics = regularized_plane_flux_controlled_pressure_outlet
row_count = 4
```

The phase must not be selected-candidate semantics and must not be in the
selected chain.

## Shared Row Parameters

All four rows must use:

```text
requested_nx = 48
requested_n_steps = 250
output_interval = 5
open_boundary_semantics = regularized_plane_flux_controlled_pressure_outlet
row_role = saturation_stationarity_diagnostic_48
open_boundary_flux_control_target_scale = 0.80
open_boundary_flux_feedback_gain_u = 0.75
open_boundary_flux_feedback_cap_u = 0.0075
open_boundary_flux_feedback_gain_rho = 0.001
open_boundary_flux_feedback_alpha = 0.02
open_boundary_flux_feedback_delta_cap_u = 0.0005
open_boundary_flux_feedback_measure_offset = 2
open_boundary_flux_feedback_guard_enabled = true
open_boundary_flux_feedback_guard_min_ratio = 0.70
lbm_niu = 0.10
source_step = 146
selected96_claim_allowed = false
validation_claim_allowed = false
```

Step147 uses one stationarity damping knob first:

```text
baseline row: open_boundary_flux_feedback_slew_alpha = 0.50
relief rows: open_boundary_flux_feedback_slew_alpha = 0.25
```

Do not change `open_boundary_flux_feedback_delta_cap_u` in the relief rows.
Step146 offered slew or delta-cap damping; changing both at once would make the
audit ambiguous.

## Exact Rows

### Row 1: baseline_high_repeat

```text
name = duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010_mnhigh_mgain0p50_mcap0p001_blend1p00_slew0p50_out5_250step_satstat
mass_neutral_label = mass_neutral_high_baseline
open_boundary_mass_neutral_mass_error_gain = 0.50
open_boundary_mass_neutral_mass_error_cap = 0.00100
open_boundary_mass_neutral_correction_blend = 1.0
open_boundary_flux_feedback_slew_alpha = 0.50
diagnostic_purpose = repeat Step143/Step144 high setting at 250 steps
diagnostic_cap_test_only = false
```

### Row 2: relief_low_slew025

```text
name = duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010_mnrelieflow_mgain0p35_mcap0p001_blend0p50_slew0p25_out5_250step_satstat
mass_neutral_label = relief_low
open_boundary_mass_neutral_mass_error_gain = 0.35
open_boundary_mass_neutral_mass_error_cap = 0.00100
open_boundary_mass_neutral_correction_blend = 0.50
open_boundary_flux_feedback_slew_alpha = 0.25
diagnostic_purpose = lower mass actuator aggressiveness plus stationarity damping
diagnostic_cap_test_only = false
```

### Row 3: relief_mid_slew025

```text
name = duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010_mnreliefmid_mgain0p50_mcap0p001_blend0p50_slew0p25_out5_250step_satstat
mass_neutral_label = relief_mid
open_boundary_mass_neutral_mass_error_gain = 0.50
open_boundary_mass_neutral_mass_error_cap = 0.00100
open_boundary_mass_neutral_correction_blend = 0.50
open_boundary_flux_feedback_slew_alpha = 0.25
diagnostic_purpose = same mass gain/cap as high with lower effective blend and damping
diagnostic_cap_test_only = false
```

### Row 4: relief_cap_test_slew025

```text
name = duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010_mncaptest_mgain0p50_mcap0p0015_blend0p50_slew0p25_out5_250step_satstat
mass_neutral_label = relief_cap_test
open_boundary_mass_neutral_mass_error_gain = 0.50
open_boundary_mass_neutral_mass_error_cap = 0.00150
open_boundary_mass_neutral_correction_blend = 0.50
open_boundary_flux_feedback_slew_alpha = 0.25
diagnostic_purpose = diagnostic cap test only; effective max feedback is 0.00075 because blend is 0.50
diagnostic_cap_test_only = true
```

## Required Audit

Add `experiments/steps/step147_saturation_stationarity_audit.py`.

Inputs:

```text
outputs/step147_saturation_stationarity_diagnostic/saturation_stationarity48
outputs/step146_coupled_saturation_stationarity_design/step146_design_readiness_report.json
outputs/step145_mass_neutral_long_window_forensics/step145_failure_mechanism_summary.json
```

Outputs:

```text
outputs/step147_saturation_stationarity_diagnostic/step147_saturation_stationarity_comparison.json
outputs/step147_saturation_stationarity_diagnostic/step147_saturation_stationarity_comparison.csv
outputs/step147_saturation_stationarity_diagnostic/step147_decision_summary.json
```

The audit must support missing-input mode:

```text
status = missing_input
missing_input = true
step148_500step_probe_proposal_allowed = false
selected96_execution_allowed = false
validation_claim_allowed = false
```

## Required Comparison Fields

Each comparison row must include at least:

```text
name
row_role
requested_nx
requested_n_steps
steps_completed
requested_window_completed
finite_pass
density_gate_pass
population_gate_pass
mach_gate_pass
mass_drift_gate_pass
first_failure_step
first_failure_reason
candidate_mass_acceptance_observed_abs
candidate_mass_acceptance_gate_pass
flow_development_gate_pass
outlet_to_inlet_flux_ratio_tail_mean
midplane_to_inlet_flux_ratio_tail_mean
flux_imbalance_rel_tail_mean
flux_imbalance_rel_tail_max
outlet_flux_tail_cv
collapse_first_x
collapse_first_step
mass_neutral_feedback_saturation_fraction_tail
mass_neutral_rho_feedback_tail_mean
mass_neutral_mass_error_tail_mean
controller_authority_ratio_tail_mean
controller_saturation_fraction_tail
controller_drop_guard_activation_fraction_tail
open_boundary_mass_neutral_mass_error_gain
open_boundary_mass_neutral_mass_error_cap
open_boundary_mass_neutral_correction_blend
open_boundary_flux_feedback_slew_alpha
open_boundary_flux_feedback_delta_cap_u
selected96_claim_allowed
validation_claim_allowed
source_step146_readiness_hash
mass_neutral_activation_hash
solver_state_hash
run_manifest_hash
```

## Decision Cases

`step147_decision_summary.json` must use exactly one of:

- `saturation_stationarity_relief_supported`
- `mass_relief_without_stationarity`
- `stationarity_relief_without_mass`
- `relief_design_insufficient`
- `relief_design_unstable`
- `missing_input`
- `blocked_by_source_decision`

### Case A: saturation_stationarity_relief_supported

Required conditions:

- A relief row beats `baseline_high_repeat` on
  `mass_neutral_feedback_saturation_fraction_tail`.
- The same relief row beats baseline on `outlet_flux_tail_cv`.
- The same relief row beats baseline on `flux_imbalance_rel_tail_mean`.
- The same relief row beats baseline on
  `candidate_mass_acceptance_observed_abs`.
- `flow_development_gate_pass = true`.
- No first failure.
- No compact collapse.
- `mass_neutral_feedback_saturation_fraction_tail < 0.75`.
- `selected96_claim_allowed = false`.
- `validation_claim_allowed = false`.

Allowed result:

```text
step148_500step_probe_proposal_allowed = true
selected96_execution_allowed = false
```

Even in this case, Step147 may only propose one later 48^3 / 500-step Step148
probe for the exact best Step147 relief setting. It must not run it.

### Case B: mass_relief_without_stationarity

Mass or saturation improves, but outlet CV or mean flux imbalance fails or
worsens. No Step148 500-step proposal.

### Case C: stationarity_relief_without_mass

Outlet stationarity improves, but mass acceptance or mass-neutral error fails
or worsens. No Step148 500-step proposal.

### Case D: relief_design_insufficient

No relief row improves the baseline in a coupled way. No Step148 500-step
proposal. Return to report-only projection feasibility or formulation design.

### Case E: relief_design_unstable

Any relevant row has nonfinite state, first failure, compact collapse, or
terminal hard stop. Stop parameter progression.

## Contract Tests

Add `tests/test_step147_saturation_stationarity_contract.py` and cover:

1. Phase resolver produces exactly four rows.
2. All rows are 48^3 / 250-step / `output_interval = 5`.
3. All rows use `row_role = saturation_stationarity_diagnostic_48`.
4. That role is not in `SELECTED_CHAIN_ROLES`.
5. `regularized_plane_flux_controlled_pressure_outlet` is not in
   `CANDIDATE_SEMANTICS` or `REPAIRED_CANDIDATE_SEMANTICS`.
6. Every spec records `source_step = 146` and
   `source_step146_readiness_hash`.
7. Phase resolver fails if Step146 readiness is missing or not `design_ready`.
8. Exactly one baseline row uses the Step143/Step144 high mass-neutral setting.
9. Three relief rows use `blend = 0.50` and `slew_alpha = 0.25`.
10. `relief_cap_test` uses `cap_mass = 0.00150`, `blend = 0.50`, and is marked
    diagnostic-only.
11. `mass_neutral_activation_hash` differs across the four rows.
12. Completed-row reuse rejects stale rows with wrong Step146 readiness hash.
13. Completed-row reuse rejects stale rows with wrong mass-neutral activation
    hash.
14. Flow diagnostics and run manifests include Step147 and source Step146
    fields.
15. Step147 rows cannot enable selected96 even if mocked metrics pass.
16. Audit missing input outputs `missing_input`.
17. Audit permits Step148 only when coupled relief improves saturation, mass,
    outlet CV, and mean imbalance.
18. Current docs preserve selected96, validation, selected-candidate review,
    and Step147 500-step execution blocked.

## Verification Commands

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step147-red `
  tests\test_step147_saturation_stationarity_contract.py

& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py `
  experiments\steps\step147_saturation_stationarity_audit.py `
  tests\test_step147_saturation_stationarity_contract.py

& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_saturation_stationarity48 `
  --output-dir outputs\step147_saturation_stationarity_diagnostic\saturation_stationarity48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume

& 'D:\working\taichi\env\python.exe' -m experiments.steps.step147_saturation_stationarity_audit `
  --phase-root outputs\step147_saturation_stationarity_diagnostic\saturation_stationarity48 `
  --step146-readiness outputs\step146_coupled_saturation_stationarity_design\step146_design_readiness_report.json `
  --output-dir outputs\step147_saturation_stationarity_diagnostic `
  --force

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step147-focused `
  tests\test_step147_saturation_stationarity_contract.py `
  tests\test_step146_coupled_saturation_stationarity_design_contract.py `
  tests\test_step145_mass_neutral_long_window_forensics_contract.py `
  tests\test_step144_mass_neutral_final48_contract.py `
  tests\test_step143_mass_neutral_design_contract.py `
  tests\test_step142_mass_neutral_plane_flux_design_contract.py `
  tests\test_step141_density_feedback_isolation_contract.py `
  tests\test_step140_long_window_drift_forensics_contract.py

& 'D:\working\taichi\env\python.exe' -c "<json load check for Step147 artifacts and current docs>"

git diff --check
```

## Completion Criteria

Step147 is complete only when:

- The detailed goal is committed under
  `docs/campaigns/fluent_duct_flap/steps/147/goal.md`.
- The short working goal references that file directly.
- A RED test fails before implementation for the missing Step147 surface.
- Step147 phase resolver creates exactly four bounded diagnostic rows.
- Real Step147 row artifacts exist under
  `outputs/step147_saturation_stationarity_diagnostic/saturation_stationarity48`.
- The Step147 audit emits JSON and CSV comparison plus a decision summary.
- The audit decision honestly reports whether Step148 is allowed; selected96
  remains blocked in all cases.
- Current docs preserve selected96, selected-candidate review, validation,
  Fluent, FSI, and direct Step147 500-step execution blocks.
- Focused Step140-Step147 regression passes.
- JSON artifacts load successfully.
- `git diff --check` passes.
- The final commit is pushed to `origin/main`, with remote ref proof.

If the normal pre-push hook times out after focused verification has passed,
the final report must say so and must include explicit remote-ref confirmation.

## Required Bounded-State Phrases

These exact phrases must remain in Step147 docs/current artifacts:

- Step147 ran exactly four 48^3 / 250-step LBM-only rows
- Step147 did not run selected96
- Step147 did not run selected-static
- Step147 did not run 96^3
- Step147 did not run a 500-step row
- Step147 did not run Fluent
- Step147 did not run FSI
- Step147 does not make a validation claim
- origin/main = 54afab0c6b4bdae05fa08f50f274e8d2f557e1d9
