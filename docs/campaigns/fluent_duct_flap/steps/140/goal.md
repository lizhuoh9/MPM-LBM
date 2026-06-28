# Step140 Long-Window Drift Forensics Goal

## Objective

Implement Step140 as a forensics-only, artifact-backed diagnosis of the
Step139 long-window failure mechanism. Step140 must explain why the Step138
short-window passing row failed Step139 48^3 / 500-step final evidence with
small but gate-breaking mass accumulation, mean flux imbalance drift, and
outlet stationarity drift.

Step140 is not a promotion step. It must not run selected96, selected-static,
96^3, Fluent, FSI, or any new LBM simulation row. It must not add tuning rows,
change gates, change solver formulas, or add selected-candidate semantics.

## Source Finding To Preserve

The remote commit checked by the reviewer was:

```text
b83c1514e325c3bb5f29d73f8adeab13f6ac623d
```

The accepted Step139 facts are:

- `planeflux_final48` is wired into Step121 and resolves to exactly one
  48^3 / 500-step row.
- The row inherits the Step138 passing parameters:
  `ramp_steps = 85`, `target_scale = 0.80`, `gain_u = 0.75`,
  `cap_u = 0.0075`, `gain_rho = 0.001`, `filter_alpha = 0.02`,
  `delta_cap_u = 0.0005`, `slew_alpha = 0.50`, `measure_offset = 2`,
  and outlet drop guard min ratio `0.70`.
- The row has `row_role = final_evidence_candidate_48`, records Step138 source
  provenance, and is not selected-candidate evidence.
- Step139 completed 500/500, stayed finite, had no first failure, and passed
  density, population, Mach, mass-drift hard-stop, ratio, max-imbalance,
  collapse, and limiter checks.
- Step139 failed the final hard gate on:
  `candidate_mass_acceptance_observed_abs = 0.008321150189010917`,
  `flux_imbalance_rel_tail_mean = 0.10270018561574665`, and
  `outlet_flux_tail_cv = 0.11556697847525366`.
- `ACTIVE_CAMPAIGN.json`, `STATUS.md`, and `VALIDATION_GATES.md` keep the
  selected96/96^3/Fluent/FSI/Figure 29.3/production claims blocked.

## Step140 Questions

Step140 must answer these questions from existing Step139 artifacts:

1. Is mass drift after step 250 monotonic accumulation, oscillation, or only a
   final-tail artifact?
2. Is outlet CV drift a true outlet-plane stationarity problem or a
   near-outlet / measurement-plane mismatch?
3. Does the controller enter a slow bias after step 250 through filtered error,
   target-scale behavior, density feedback, or feedback damping?
4. Is the long-window failure dominated by mass drift, outlet stationarity,
   flux imbalance, controller lag, profile / near-outlet mismatch, or an
   unresolved mixed mechanism?

## Required Preliminary Reconciliation

Before adding Step140 reports, reconcile two Step139 documentation surfaces:

1. Clarify commit identity:
   - Preserve `4e43162a641085e56a4ba72c8bc013e58cb08cc3` as the Step139
     `code_commit_at_run`.
   - Record `b83c1514e325c3bb5f29d73f8adeab13f6ac623d` as the final
     Step139 report/docs repository commit.
   - Avoid letting `current_code_commit` be misread as the final repository
     HEAD if it intentionally points to the run-time code commit.
2. Reconcile Step139 goal Task5/Task6 filenames with implemented artifacts:
   - Actual generic solver contract:
     `docs/GENERIC_SOLVER_ARCHITECTURE_CONTRACT.md`.
   - Actual Fluent official local-execution guard:
     `docs/campaigns/fluent_duct_flap/fluent_official_local_execution_guard.md`.
   - Actual guard schemas:
     `configs/fluent_official_2way_fsi_local_execution_schema.json` and
     `configs/fluent_official_monitor_export_schema.json`.
   - Actual guard report:
     `outputs/fluent_official_local_execution_prep/guard_report.json`.

These reconciliation edits must not change Step139 data, Step139 metrics,
gates, selected-candidate logic, or Step121 phase behavior.

## Allowed Inputs

Step140 may read only the committed Step139 artifacts and current docs needed
for claim-boundary reporting:

```text
outputs/step139_planeflux_final48/planeflux_final48/campaign_manifest.json
outputs/step139_planeflux_final48/planeflux_final48/step121_summary.json
outputs/step139_planeflux_final48/planeflux_final48/step121_gate_report.json
outputs/step139_planeflux_final48/planeflux_final48/step121_best_boundary_selection.json
outputs/step139_planeflux_final48/planeflux_final48/*/finite_stability_report.json
outputs/step139_planeflux_final48/planeflux_final48/*/flow_development_diagnostics.csv
outputs/step139_planeflux_final48/planeflux_final48/*/flow_development_diagnostics_summary.json
outputs/step139_planeflux_final48/planeflux_final48/*/boundary_flux_timeseries.csv
outputs/step139_planeflux_final48/planeflux_final48/*/density_drift_timeseries.csv
outputs/step139_planeflux_final48/step139_long_window_comparison.json
outputs/step139_planeflux_final48/step139_failure_forensics.json
docs/current/STATUS.md
docs/current/ACTIVE_CAMPAIGN.json
docs/current/VALIDATION_GATES.md
```

If a required Step139 artifact is missing, Step140 must fail with a
`missing_input` report and must not synthesize a mechanism conclusion.

## Forbidden Work

Step140 must not:

- add a Step121 phase;
- add any `selected96`, `selected-static`, or 96^3 command;
- run a new LBM simulation;
- run Fluent or read private Fluent files;
- add new tuning rows;
- alter Step121/Step124 gate formulas;
- alter Step120/Step121 solver behavior;
- add candidate semantics for Step139 or Step140;
- claim repaired 48^3 success, selected 96^3 success, quasi-2D validation,
  FSI validation, Fluent validation, Figure 29.3 parity, or production
  readiness.

## Required Files

Add or update:

```text
docs/campaigns/fluent_duct_flap/steps/140/goal.md
docs/campaigns/fluent_duct_flap/steps/140/report.md
experiments/steps/step140_long_window_drift_forensics.py
tests/test_step140_long_window_drift_forensics_contract.py
outputs/step140_long_window_drift_forensics/mass_drift_segment_report.json
outputs/step140_long_window_drift_forensics/flux_stationarity_segment_report.json
outputs/step140_long_window_drift_forensics/controller_response_segment_report.json
outputs/step140_long_window_drift_forensics/x_profile_evolution_report.json
outputs/step140_long_window_drift_forensics/step140_failure_mechanism_summary.json
outputs/step140_long_window_drift_forensics/step140_failure_mechanism_summary.md
```

Update current docs as needed:

```text
docs/current/STATUS.md
docs/current/ACTIVE_CAMPAIGN.json
docs/current/VALIDATION_GATES.md
docs/current/READING_ORDER.md
```

README must be checked. Update it only if the public contract or entrypoint
changes.

## Segment Windows

Analyze Step139 records over these fixed windows:

```text
0-100
100-200
200-250
250-300
300-400
400-500
tail_80pct_diagnostic
tail_20pct_hard_gate
```

The diagnostic tail windows must not change hard-gate definitions. They are
trend aids only.

## Segment Metrics

For each available window, compute these metrics when the source fields exist:

```text
mass_total_delta_rel mean / final / slope / max_abs
inlet_flux mean / cv / slope
outlet_flux mean / cv / slope
midplane_flux mean / cv / slope
outlet_to_inlet_flux_ratio mean / slope
midplane_to_inlet_flux_ratio mean / slope
flux_imbalance_rel mean / max / slope
outlet_flux_tail_cv equivalent
controller_target_outlet_flux mean / slope
controller_measured_outlet_flux mean / slope
controller_filtered_flux_error mean / slope
controller_u_feedback mean / abs_mean / slope
controller_authority_ratio mean / slope
controller_saturation_fraction
drop_guard_activation_fraction
near_outlet_to_outlet_flux_ratio mean / slope
x_profile_flux_samples by x
```

If a source field does not exist in the Step139 artifacts, record it under
`unavailable_fields` rather than fabricating a value.

## Required Output Semantics

The final summary JSON must include:

```text
selected96_execution_allowed = false
validation_claim_allowed = false
new_lbm_run_executed = false
new_parameter_tuning_executed = false
input_step = 139
input_row_completed_500 = true
input_final_hard_gate_pass = false
segment_count >= 6
mass_drift_failure_classified = true
outlet_cv_failure_classified = true
flux_mean_failure_classified = true
mechanism_summary_present = true
next_experiment_recommendation_count <= 1
```

The mechanism summary must classify:

- `mass_drift_mechanism`;
- `outlet_cv_mechanism`;
- `flux_mean_mechanism`;
- `controller_response_mechanism`;
- `dominant_failure_mechanism`;
- `recommended_next_step`.

The recommended next step must be at most one bounded Step141 direction. It
may recommend no new parameter run if the mechanism remains unresolved.

## Step141 Branch Policy To Encode

Encode the Step141 branch policy in the Step140 summary:

```text
If mass drift dominates:
    Step141 may propose a mass-neutral plane-flux controller or outlet density
    feedback correction design proposal only.
If outlet CV dominates:
    Step141 may propose a stationarity-focused 48^3 / 250-step diagnostic sweep.
If controller lag dominates:
    Step141 may propose a filter_alpha / slew / delta_cap bounded diagnostic
    with no more than 6 rows.
If profile or near-outlet mismatch dominates:
    Step141 may propose measurement-plane / x-profile forensics with no more
    than 250 steps.
If the mechanism remains unclear:
    Step141 must add diagnostics before tuning.
```

Do not create Step141 runtime rows in Step140.

## Tests

Add contract tests that prove:

1. Step140 does not add a Step121 phase.
2. Step140 does not add selected96, selected-static, or 96^3 commands.
3. Step140 reads Step139 artifacts only.
4. Missing Step139 inputs produce a `missing_input` result and no mechanism
   conclusion.
5. All claim flags in Step140 outputs are false.
6. Segment JSON fields are complete for all windows.
7. The mechanism summary is present and contains at most one next-experiment
   recommendation.
8. Step139 goal reconciliation names the actual Task5/Task6 paths.
9. Commit identity is explicit enough to distinguish run-time commit from
   final repository report/docs commit.

Use a red-to-green workflow where practical: run the Step140 contract test
before the parser/report is complete and keep the failing output in the final
report.

## Verification

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile experiments\steps\step140_long_window_drift_forensics.py tests\test_step140_long_window_drift_forensics_contract.py
& 'D:\working\taichi\env\python.exe' -m pytest -q --basetemp outputs\tmp\pytest-step140 tests\test_step140_long_window_drift_forensics_contract.py
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step140_long_window_drift_forensics --step139-root outputs\step139_planeflux_final48 --output-dir outputs\step140_long_window_drift_forensics --force
& 'D:\working\taichi\env\python.exe' -m pytest -q --basetemp outputs\tmp\pytest-step140-final tests\test_step140_long_window_drift_forensics_contract.py tests\test_step139_planeflux_final48_contract.py tests\test_step138_high_authority_outlet_contract.py
git diff --check
```

Run additional focused Step124/current-doc tests if current campaign documents
are touched.

## Done Criteria

Step140 is done only when:

- the detailed goal file exists and the active goal references it;
- Step139 reconciliation edits are made without altering Step139 evidence;
- Step140 parser exists and is covered by tests;
- Step140 outputs exist and are generated from Step139 artifacts;
- report and current docs describe the mechanism result and keep claims blocked;
- selected96/96^3/Fluent/FSI claims remain forbidden;
- focused verification passes;
- README has been checked and updated if necessary;
- changes are committed and pushed to `origin/main`;
- the final response reports the remote branch, final commit hash, test counts,
  and key Step140 conclusion.
