# Step141 Density-Feedback Isolation Diagnostic Goal

## Objective

Implement Step141 as a bounded 48^3 / 250-step LBM-only density-feedback
isolation diagnostic for the Step139/Step140 long-window failure. Step141 must
answer whether `gain_rho = 0.001` in the Step138/Step139 source row is a major
contributor to the post-250 mass excursion, outlet stationarity drift, and mean
flux-imbalance tail drift classified by Step140.

Step141 is not a fix, not a promotion, and not validation. It must not run or
enable selected96, selected-static, 96^3, Fluent, FSI, or any 500-step row. It
must not change selected-candidate semantics, hard gates, Step124 gate policy,
or solver formulas. It must keep all broad validation and production-readiness
claims blocked.

## Source Finding To Preserve

The reviewed remote Step140 commit is:

```text
90fa5798754942cd8f7de2a1c24a483804667478
```

The accepted Step140 facts are:

- Step140 is an artifact-only parser over existing Step139 artifacts.
- Step140 did not add a Step121 phase, did not run LBM, and did not tune
  parameters.
- Step140 produced reports under
  `outputs/step140_long_window_drift_forensics`.
- Step140 kept these flags false:
  `new_lbm_run_executed`, `new_parameter_tuning_executed`,
  `selected96_execution_allowed`, `validation_claim_allowed`,
  quasi-2D, FSI, Fluent, Figure 29.3, and production-readiness claim flags.
- Step140 classified the dominant mechanism as
  `mass_accumulation_with_outlet_stationarity_drift`.
- Step140 also recorded the more precise components:
  `mass_drift_mechanism = tail_mass_acceptance_failure`,
  `flux_mean_mechanism = mean_flux_imbalance_tail_drift`,
  `outlet_cv_mechanism = true_outlet_stationarity_oscillation`,
  `controller_response_mechanism = unsaturated_controller_authority_decay`,
  `near_outlet_to_outlet_tail_mean = 0.9978928625164406`, and
  `controller_authority_ratio_tail_slope = -0.0017400182162721955`.

Step141 must preserve the reviewer nuance that Step140's "accumulation" label
must not be overread as strictly monotonic mass growth from step 250 to 500.
The precise mechanism wording for Step141 should be:

```text
post_250_mass_excursion_with_tail_acceptance_failure
```

or an equivalent statement that the mass rises quickly after step 250, later
partly relaxes, but remains above the `< 0.005` hard-tail candidate
mass-acceptance gate.

## Scope Boundary

Step141 must stay inside this envelope:

```text
48^3 only
250 steps only
LBM-only
at most 4 real rows
no selected96
no selected-static
no 96^3
no Fluent or FSI
no 500-step run
no selected-candidate semantics
no gate relaxation
no solver-formula drift
```

Step141 may add one Step121 phase that runs the four 48^3 / 250-step rows
listed below. It may add report-visible provenance/claim fields to Step120
outputs if needed, but it must not change the open-boundary equations or the
physics update path.

## Required Phase

Add the Step121 phase:

```text
planeflux_density_feedback_isolation48
```

The phase must resolve to exactly four rows and no more.

Use row role:

```text
density_feedback_isolation_diagnostic_48
```

This role must not be added to:

```text
CANDIDATE_SEMANTICS
REPAIRED_CANDIDATE_SEMANTICS
SELECTED_CHAIN_ROLES
```

The phase must remain outside selected-boundary selection. Even if a mocked or
real row passes all local metrics, it must not select a boundary and must not
enable selected96.

## Required Row Matrix

All four rows inherit the Step139/Step140 locked baseline except for
`open_boundary_flux_feedback_gain_rho`.

Common parameters:

```text
grid = 48^3
n_steps = 250
output_interval = 5
semantics = regularized_plane_flux_controlled_pressure_outlet
geometry_mode = duct_only
ramp_steps = 85
target_scale = 0.80
gain_u = 0.75
cap_u = 0.0075
alpha = 0.02
delta_cap_u = 0.0005
slew_alpha = 0.50
measure_offset = 2
guard_enabled = true
guard_min_ratio = 0.70
lbm_niu = 0.10
selected96_claim_allowed = false
validation_claim_allowed = false
```

Rows:

```text
1. baseline_repeat_rho0p001
   gain_rho = 0.001

2. rho_off
   gain_rho = 0.0

3. rho_quarter
   gain_rho = 0.00025

4. rho_half
   gain_rho = 0.0005
```

Preferred row names:

```text
duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_out5_250step_density_iso
duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0000_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_out5_250step_density_iso
duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p00025_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_out5_250step_density_iso
duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0005_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_out5_250step_density_iso
```

## Provenance Requirements

Each Step141 row must record provenance to Step140 and the Step139 source row:

```text
source_step = 140
source_step139_row_name
source_step139_solver_state_hash
source_step139_run_manifest_hash
source_step139_code_commit
source_step140_summary_hash
source_step140_summary_path
source_step140_dominant_failure_mechanism
source_step140_mass_drift_mechanism
```

The campaign manifest must include the same provenance fields in
`expected_rows`. Collection must reject stale rows whose solver-state hash,
run-manifest hash, or source Step140 summary hash does not match the manifest.

## Required Step120 Reporting Surface

Step120 row metadata, boundary reports, finite summaries, and flow diagnostics
must include enough report-visible information to audit Step141 without
reading code:

```text
step141_density_feedback_isolation_candidate
source_step
source_step139_row_name
source_step139_solver_state_hash
source_step139_run_manifest_hash
source_step139_code_commit
source_step140_summary_hash
source_step140_summary_path
source_step140_dominant_failure_mechanism
source_step140_mass_drift_mechanism
selected96_claim_allowed = false
validation_claim_allowed = false
```

Step120 may add these report fields only. Do not alter the solver stepping
semantics, the boundary-control formula, or gate thresholds.

## Required Per-Row Report Fields

Each row and the Step141 audit artifacts must report:

```text
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
controller_authority_ratio_tail_mean
controller_saturation_fraction_tail
controller_density_feedback_tail_mean
outlet_flux_drop_guard_activation_fraction_tail
selected96_claim_allowed
validation_claim_allowed
```

## Audit Script

Add:

```text
experiments/steps/step141_density_feedback_isolation_audit.py
```

The audit reads the Step141 phase root and Step140 summary, then writes:

```text
outputs/step141_density_feedback_isolation/step141_density_feedback_comparison.json
outputs/step141_density_feedback_isolation/step141_density_feedback_comparison.csv
outputs/step141_density_feedback_isolation/step141_decision_summary.json
```

The comparison sort order is:

1. `candidate_mass_acceptance_observed_abs` ascending.
2. `outlet_flux_tail_cv` ascending.
3. `flux_imbalance_rel_tail_mean` ascending.
4. absolute deviation of `outlet_to_inlet_flux_ratio_tail_mean` from `1.0`
   ascending.
5. `controller_saturation_fraction_tail` ascending.

The audit may allow at most:

```text
step142_single_500step_final_evidence_proposal_allowed = true/false
selected96_execution_allowed = false
validation_claim_allowed = false
```

It must never allow selected96 or validation.

If the phase-root inputs are missing, the audit must emit a `missing_input`
decision summary and must not synthesize a winning row.

## Decision Policy

Encode these decision cases in the Step141 report and audit summary:

```text
Case A: rho_off or rho_reduced clearly lowers mass_abs and does not break flow gates
    conclusion = density_feedback_contributes_to_mass_stationarity_drift
    next = Step142 may propose one 48^3 / 500-step final-evidence row for the best rho setting.
    selected96 remains blocked.

Case B: all rho variants reproduce mass/stationarity failure
    conclusion = density_feedback_isolation_insufficient
    next = Step142 should be a mass-neutral plane-flux controller design proposal, not 500-step.

Case C: rho_off improves mass but damages ratio or flux
    conclusion = density_feedback_trades_mass_against_throughput
    next = Step142 should be controller formulation diagnosis only, not selected96.

Case D: any row shows compact collapse or first failure
    conclusion = long_window_drift_workaround_unstable
    next = stop parameter progression and return to solver/boundary formulation diagnosis.
```

## Required Files

Add:

```text
docs/campaigns/fluent_duct_flap/steps/141/goal.md
docs/campaigns/fluent_duct_flap/steps/141/report.md
tests/test_step141_density_feedback_isolation_contract.py
experiments/steps/step141_density_feedback_isolation_audit.py
outputs/step141_density_feedback_isolation/density_feedback_isolation48/...
outputs/step141_density_feedback_isolation/step141_density_feedback_comparison.json
outputs/step141_density_feedback_isolation/step141_density_feedback_comparison.csv
outputs/step141_density_feedback_isolation/step141_decision_summary.json
```

Modify:

```text
experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py
experiments/steps/step120_lbm_boundary_repair_large_real_execution.py
docs/current/ACTIVE_CAMPAIGN.json
docs/current/STATUS.md
docs/current/VALIDATION_GATES.md
docs/current/READING_ORDER.md
README.md only if the public repository contract changes
```

## Required Tests

Add `tests/test_step141_density_feedback_isolation_contract.py` covering at
least:

1. `planeflux_density_feedback_isolation48` resolves exactly four rows.
2. All rows are 48^3 / 250-step / `output_interval = 5`.
3. Only `open_boundary_flux_feedback_gain_rho` differs across rows.
4. Every row uses `row_role = density_feedback_isolation_diagnostic_48`.
5. `regularized_plane_flux_controlled_pressure_outlet` is not in
   `CANDIDATE_SEMANTICS` or `REPAIRED_CANDIDATE_SEMANTICS`.
6. Step141 rows cannot enable selected96 even if mocked metrics pass.
7. Step141 provenance records `source_step = 140`,
   `source_step139_row_name`, and `source_step140_summary_hash`.
8. Manifest collection rejects stale rows with wrong solver-state hash,
   run-manifest hash, or source Step140 summary hash.
9. Flow diagnostics include the Step141 flag, source provenance, and
   `selected96_claim_allowed = false`.
10. Report/artifact scans forbid selected96, selected-static, 96^3, Fluent, and
    FSI commands or claims.
11. The audit script emits comparison and decision artifacts with all claim
    flags false.
12. Missing audit inputs produce `missing_input`, not a fake decision.

Use red-to-green where practical: run the Step141 contract before implementing
the phase/audit and keep the failure as local evidence.

## Run Commands

Real Step141 phase:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_density_feedback_isolation48 `
  --output-dir outputs\step141_density_feedback_isolation\density_feedback_isolation48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume
```

Audit:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step141_density_feedback_isolation_audit `
  --phase-root outputs\step141_density_feedback_isolation\density_feedback_isolation48 `
  --step140-summary outputs\step140_long_window_drift_forensics\step140_failure_mechanism_summary.json `
  --output-dir outputs\step141_density_feedback_isolation `
  --force
```

## Verification

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py `
  experiments\steps\step141_density_feedback_isolation_audit.py `
  tests\test_step141_density_feedback_isolation_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step141-red `
  tests\test_step141_density_feedback_isolation_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step141-focused `
  tests\test_step141_density_feedback_isolation_contract.py `
  tests\test_step140_long_window_drift_forensics_contract.py `
  tests\test_step139_planeflux_final48_contract.py `
  tests\test_step138_high_authority_outlet_contract.py

& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_density_feedback_isolation48 `
  --output-dir outputs\step141_density_feedback_isolation\density_feedback_isolation48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume

& 'D:\working\taichi\env\python.exe' -m experiments.steps.step141_density_feedback_isolation_audit `
  --phase-root outputs\step141_density_feedback_isolation\density_feedback_isolation48 `
  --step140-summary outputs\step140_long_window_drift_forensics\step140_failure_mechanism_summary.json `
  --output-dir outputs\step141_density_feedback_isolation `
  --force

& 'D:\working\taichi\env\python.exe' -c "<json load check for Step141 artifacts and current docs>"

git diff --check
```

If the global pre-push hook again times out or fails from full-suite execution,
the final report must explicitly say focused verification passed, the hook
failed with the exact error, push used `--no-verify`, remote main was verified
with `git ls-remote`, and GitHub Actions did not run if no workflow status is
available.

## Done Criteria

Step141 is done only when:

- this detailed goal file exists and the active goal references it;
- the Step121 phase resolves exactly the four intended rows;
- Step120 reporting surfaces include Step141 provenance and claim flags without
  solver-formula drift;
- Step141 real 48^3 / 250-step rows have been executed or an explicit
  artifact-backed blocker has been recorded;
- audit JSON/CSV artifacts exist and are generated from Step141 rows plus the
  Step140 summary;
- `docs/campaigns/fluent_duct_flap/steps/141/report.md` records the bounded
  result and keeps selected96/validation blocked;
- current docs point to Step141 as the current entry point while preserving
  Step139/Step140 evidence boundaries;
- README has been checked and updated only if the user-facing contract changed;
- focused verification passes;
- changes are committed and pushed to `origin/main`;
- remote `origin/main` is verified at the final commit hash.
