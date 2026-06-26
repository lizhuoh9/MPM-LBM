# Step127 LBM Boundary 48^3 Candidate Campaign Execution Goal

## Source Review

This goal follows the review confirming GitHub remote `main` at commit
`1441c5e1a01e7640de350187f96193dc5040656b`, commit message
`test: run Step126 48 reference campaign`.

Step126 is accepted as a real 48^3 reference execution step. It ran only
`references48`, generated simulation-backed artifacts for the legacy and old
regularized reference rows, refreshed the Step121 summary, and advanced the
campaign state to:

```text
campaign_state = awaiting_48_candidates
final_classification = boundary_repair_partial_continue_lbm
best_boundary_selected = false
quasi2d_allowed = false
```

Step126 did not run candidates, selected 96^3, quasi-2D, FSI, Fluent validation,
or Figure 29.3 parity.

## Step126 Evidence Baseline

### Passing Legacy Reference

`duct_only_48_legacy_boundary_500step_reference_real` completed 500/500 steps,
passed the basic stability gates, passed the Step124 flow-development gate, and
had no first failure.

Important metrics:

```text
mass_total_delta_rel_final = 0.0007730374927265733
flux_imbalance_rel_tail_mean = 0.04043317017445867
flux_imbalance_rel_tail_max = 0.08607841290325333
outlet_to_inlet_flux_ratio_tail_mean = 0.9595668298255413
midplane_to_inlet_flux_ratio_tail_mean = 0.9556179894908249
outlet_flux_tail_cv = 0.02463282965556423
```

This means the 48^3 duct-only legacy baseline is usable. The current campaign
question is therefore not whether 48^3 duct-only can run, but which
open-boundary formulation should be selected for the next larger validation
step.

### Failed Old-Regularized Comparison Reference

`duct_only_48_regularized_boundary_500step_reference_real` also completed
500/500 steps and passed the basic finite/density/mass/population/Mach gates
without a first failure, but it failed the Step124 flow-development gate.

Important metrics:

```text
mass_total_delta_rel_final = 0.002957161603977865
flux_imbalance_rel_tail_mean = 0.5116500495884674
flux_imbalance_rel_tail_max = 0.8660866973898724
outlet_to_inlet_flux_ratio_tail_mean = 1.4127437709040476
midplane_to_inlet_flux_ratio_tail_mean = 1.3061915562381126
outlet_flux_tail_cv = 0.4528776651615377
```

This is valid failed-baseline comparison evidence for Step127. A candidate that
does not materially improve over this row should not be promoted.

## Step127 Objective

Execute the real `candidates48` phase under the existing Step121/Step124/Step125
campaign controller and gate system.

Step127 must produce or refresh real simulation-backed artifacts for exactly
these 48^3 candidate rows:

```text
duct_only_48_regularized_limited_boundary_500step_real
duct_only_48_convective_outlet_boundary_500step_real
```

After the rows complete or reach Step121-recognized terminal evidence, Step127
must refresh the campaign summary and decide whether the campaign has selected a
best 48^3 boundary formulation that may advance to selected 96^3 duct-only work
in a later step.

## Scope Boundary

Step127 is a real 48^3 candidate execution and comparison step.

It may:

- Run `--phase candidates48`.
- Resume from existing checkpoints if interrupted.
- Run `--phase summary` after candidates complete or fail terminally.
- Commit generated candidate-phase artifacts needed for audit.
- Update current campaign docs and Step127 report.
- Add a focused regression test only if the real run exposes a runner,
  manifest, provenance, checkpoint, or gate bug.
- Make the minimum code fix required by such a captured bug.

It must not:

- Run selected 96^3 duct.
- Run selected 96^3 static two-flap.
- Run quasi-2D.
- Run FSI.
- Claim Fluent validation.
- Claim Figure 29.3 parity.
- Use `--force`.
- Delete or manually rewrite checkpoints to manufacture success.
- Change LBM solver physics, boundary formulas, or gate thresholds unless real
  runtime evidence first exposes a code defect and a failing regression captures
  the defect.

## Phase 0: Preflight

Confirm the local worktree and live remote baseline:

```powershell
git status --short
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Expected source baseline before the Step127 goal file is created:

```text
HEAD = 1441c5e1a01e7640de350187f96193dc5040656b
origin/main = 1441c5e1a01e7640de350187f96193dc5040656b
```

For cleaner provenance, commit this Step127 goal locally before running
`candidates48`. In that case, candidate artifacts should record the local
Step127 goal commit in `code_commit_at_run`, while the live remote `origin/main`
may still point to `1441c5e1a01e7640de350187f96193dc5040656b` until the final
verified push.

Run focused campaign contracts using the trusted interpreter and a repo-local
pytest temp directory:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step127-preflight `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

Compile the real campaign entry points:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py
```

Do not proceed to `candidates48` if the preflight contracts or compile checks
fail.

## Phase 1: Run Real 48^3 Candidates

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase candidates48 `
  --allow-large-real-rows `
  --output-interval 25
```

Rules:

- Do not add `--force`.
- If the process is interrupted, repeat the exact same command so the
  checkpoint/resume path can continue the same real rows.
- Preserve `campaign_manifest.json`.
- `phase_history` should include `smoke`, `references48`, and `candidates48`.
- `phase_commit_history` must include `candidates48 -> <Step127 runtime commit>`.
- Each row artifact must include `code_commit_at_run`, `solver_state_hash`, and
  `run_manifest_hash`.

If a runtime bug appears, stop broad execution, capture the failure in the
Step127 report, add the narrowest regression that reproduces the defect, fix the
defect in the smallest relevant code path, then rerun the affected focused
checks and the campaign command as needed.

## Phase 2: Refresh Summary

After candidate execution completes or reaches terminal Step121 evidence, run:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase summary
```

Inspect:

```text
outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_best_boundary_selection.json
outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_gate_report.json
outputs/step121_lbm_boundary_real_campaign_and_gate_correction/solver_report.json
outputs/step121_lbm_boundary_real_campaign_and_gate_correction/campaign_manifest.json
```

Also inspect each candidate row's:

```text
run_metadata.json
finite_stability_report.json
duct_boundary_condition_report.json
velocity_profile_summary.json
limiter_activation_summary.json
```

## Phase 3: Candidate Acceptance Rules

Each candidate must satisfy all basic real-row conditions:

```text
requested_window_completed = true
simulation_backed_artifact = true
step120_validation_claimed = true
finite_pass = true
density_gate_pass = true
mass_drift_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
first_failure_step = null
first_failure_reason = null
```

Each candidate must also satisfy the Step124 flow-development gate:

```text
abs(inlet_flux_tail_mean) > 1e-6
inlet/outlet sign consistent
0.80 <= abs(outlet_to_inlet_flux_ratio_tail_mean) <= 1.20
0.80 <= abs(midplane_to_inlet_flux_ratio_tail_mean) <= 1.20
flux_imbalance_rel_tail_mean < 0.10
flux_imbalance_rel_tail_max < 0.20
outlet_flux_tail_cv < 0.10
```

The limited regularized candidate must also satisfy:

```text
limiter_activation_fraction <= 0.05
```

Each candidate must materially improve over the failed old-regularized
reference and must not be materially worse than the passing legacy reference in
flow-development behavior. The Step127 report must compare candidates against
both reference baselines.

## Phase 4: Decision Outcomes

### Outcome A: Both Candidates Fail

If both candidates reach terminal real evidence and neither passes the hard
acceptance gates, the campaign must not advance to 96^3.

Expected final classification:

```text
campaign_state = 48_candidates_failed
final_classification = boundary_repair_failed_revisit_lbm_solver
selected96_allowed = false
```

The report must identify the failure category:

- `rho_range` or `mass_drift`: investigate inlet density closure and outlet mass
  balance.
- `flux_imbalance_gate` or ratio gate: investigate open-boundary formulation.
- `outlet_flux_tail_cv`: investigate outlet reflection and tail oscillation.
- high limiter activation: reject limited boundary as numerical clipping rather
  than a physically usable candidate.

### Outcome B: Exactly One Candidate Passes

If exactly one candidate passes:

```text
best_boundary_selected = true
campaign_state = best_48_selected
selected96_allowed = true
```

The passing candidate becomes the only valid input for a later Step128 selected
96^3 duct-only goal.

### Outcome C: Both Candidates Pass

If both candidates pass, select the best boundary by this priority:

1. Flow-development pass margin and throughput penalty.
2. `flux_imbalance_rel_tail_mean`.
3. `mass_total_delta_rel_final`.
4. Limiter activation.
5. Mach margin.
6. Runtime.

The report must list:

```text
selected_boundary_semantics
selected_boundary_slug
selected_boundary_provenance
selected_48_metrics
rejected_candidate_reasons
```

## Report Requirements

Create:

```text
docs/campaigns/fluent_duct_flap/steps/127/report.md
```

The report must include:

- Runtime commit and live remote baseline.
- Manifest `campaign_base_commit`, `current_code_commit`, `phase_history`, and
  `phase_commit_history`.
- Candidate rows run.
- Limited regularized candidate metrics.
- Convective outlet candidate metrics.
- Legacy reference metrics.
- Old regularized reference metrics.
- Candidate summaries and rejection reasons.
- Selected boundary or failure classification.
- Whether selected 96^3 duct-only is allowed.
- Explicit no-claim statement for quasi-2D, FSI, Fluent validation, and Figure
  29.3 parity.

For each candidate, list:

```text
code_commit_at_run
solver_state_hash
run_manifest_hash
requested_window_completed
steps_completed
step120_validation_claimed
flow_development_gate_pass
flow_development_rejection_reasons
mass_total_delta_rel_final
flux_imbalance_rel_tail_mean
flux_imbalance_rel_tail_max
outlet_to_inlet_flux_ratio_tail_mean
midplane_to_inlet_flux_ratio_tail_mean
outlet_flux_tail_cv
limiter_activation_fraction
first_failure_step
first_failure_reason
runtime_s
restored_checkpoint
```

## Final Verification

Run compile checks:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py
```

Run focused campaign contracts:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step127-focused `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

Full-repo pytest is not a required Step127 gate unless code changes broaden the
blast radius. If code changes are made, the final report must explain why the
focused tests cover the changed contract.

## Push Condition

Push to `origin/main` only after:

- Step127 goal and report are written.
- Preflight tests and compile checks pass.
- `candidates48` completes or reaches terminal Step121-recognized evidence.
- Summary refresh completes.
- Candidate decision is documented from artifacts.
- Final focused verification passes.
- `git status --short` contains only intended changes before commit.
- The final pushed remote `main` hash is verified with a live remote query.

## Step128 Gate

Step128 may only be created later if Step127 produces:

```text
best_boundary_selected = true
campaign_state = best_48_selected
```

If Step127 does not select a best 48^3 boundary, do not run selected 96^3. The
next step must instead become a boundary formulation repair step grounded in the
Step127 failure evidence.
