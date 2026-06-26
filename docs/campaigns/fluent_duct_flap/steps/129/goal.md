# Step129 Repair48 Real 48^3 Candidate Campaign Goal

## Source Review

Step129 follows the Step128 review conclusion:

```text
Step128 is accepted as a code and contract surface.
Step128 did not run selected 96^3.
Step128 did not claim repaired 48^3 acceptance.
The next step is to run the two real repair48 48^3 repaired candidates and
refresh Step121 summary/selection.
```

Baseline commit at Step129 planning time:

```text
51ce57b3bf6ab02985556ea6a800e5581eb6a7c1
fix/test: add Step128 boundary formulation repair surface
```

Step128 added:

```text
regularized_mass_balanced_pressure_outlet
convective_mass_balanced_pressure_outlet
```

Step128 also added the distinct Step121 phase:

```text
repair48
```

Step128 did not produce repaired 48^3 / 500-step acceptance evidence. The active
campaign must therefore still be treated as:

```text
state = 48_candidates_failed
final_classification = boundary_repair_failed_revisit_lbm_solver
best_boundary_selected = false
selected96_allowed = false
validation_claim_allowed = false
```

## Step129 Objective

Run real 48^3 / 500-step repaired candidates through the Step121 `repair48`
phase, refresh the Step121 summary/selection artifacts, and decide whether a
repaired 48^3 boundary candidate is selectable.

Step129 is an evidence-producing LBM-only campaign step. It must not change the
meaning of selected 96^3, quasi-2D, FSI, Fluent validation, or Figure 29.3
parity.

## Non-Negotiable Scope Boundary

Step129 may:

- Add this Step129 goal file and a Step129 report.
- Add a small repair-counter checkpoint persistence patch so repaired counter
  telemetry survives checkpoint resume.
- Add focused contract tests for repaired counter checkpoint persistence.
- Run only the Step121 `repair48` phase for the two repaired 48^3 candidates.
- Run Step121 `summary` after `repair48`.
- Update current campaign docs to reflect the actual Step129 artifact-backed
  decision.
- Commit and push the verified goal, code, tests, docs, and generated artifacts
  to `origin/main`.

Step129 must not:

- Run selected 96^3 duct rows.
- Run selected 96^3 static rows.
- Run quasi-2D rows.
- Run FSI rows.
- Claim Fluent validation.
- Claim Figure 29.3 parity.
- Relax Step124/Step121 hard gates.
- Delete, rewrite, or mask Step127 artifacts.
- Reclassify Step128 as repaired 48^3 acceptance evidence.
- Use a fresh empty artifact root that loses Step127 terminal evidence unless
  the report explicitly justifies why selection cannot be evaluated.
- Touch vendored `external/taichi_LBM3D`.

## Artifact Root Policy

Use the existing Step121 campaign artifact root:

```text
outputs/step121_lbm_boundary_real_campaign_and_gate_correction
```

Reason:

- Step121 selection still needs old Step127 terminal evidence and reference
  rows to be visible during collection.
- The new repaired rows should be added to the same campaign manifest/history
  rather than evaluated in an empty artifact root.
- Existing Step127 rows must remain intact and collectable.

Do not delete existing Step121/Step127 row directories.

## Phase 0: Goal Anchor and Runtime Commit Policy

Create this checked-in goal file first. Then create the active short goal as a
path reference to this file.

If Step129 adds the repair-counter checkpoint persistence patch, the real
`repair48` rows should be run from the commit that includes:

```text
docs/campaigns/fluent_duct_flap/steps/129/goal.md
repair-counter checkpoint persistence code
repair-counter checkpoint persistence tests
```

This ensures `code_commit_at_run` and phase commit history point to the actual
Step129 runtime surface, not the bare Step128 implementation commit.

## Phase 1: Repair-Counter Checkpoint Persistence

Step128 exposed repaired boundary counters:

```text
mass_balance_correction_count
mass_balance_correction_abs_sum
unknown_population_delta_abs_sum
```

Step129 must make these run-level counters checkpoint-persistent before the
real 500-step campaign.

Required behavior:

- Step120 checkpoint metadata includes the three repaired counter values.
- Step120 checkpoint restore restores those values into
  `get_open_boundary_limiter_stats()`.
- Existing limiter counters continue to restore unchanged.
- If a checkpoint is restored during a repaired 48^3 run, the final run-level
  repair counters must not restart from zero after restore.

Preferred implementation:

- Extend `_checkpoint_limiter_counters(lbm)` with repaired counter fields.
- Extend the LBM restore API or add a focused repair-counter restore API.
- Restore repaired counters in the same checkpoint restore path that restores
  old limiter counters.

Required test:

```text
tests/test_step129_repair_checkpoint_counter_contract.py
```

Minimum contract:

```text
test_step129_checkpoint_metadata_includes_repair_counters
test_step129_checkpoint_restore_preserves_repair_run_counters
```

The test may use a tiny real LBM row or direct counter APIs, but it must prove
the checkpoint metadata and restored `get_open_boundary_limiter_stats()` values
are nonzero/stable for repaired counters.

## Phase 2: Preflight

Before running real repaired rows, confirm:

```powershell
git status --short
git rev-parse HEAD
git branch --show-current
git ls-remote origin refs/heads/main
```

Expected:

```text
branch = main
worktree clean
origin/main = local HEAD
```

Compile:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\lbm\config.py `
  src\mpm_lbm\sim\lbm\fluid.py `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step129-preflight `
  tests\test_step129_repair_checkpoint_counter_contract.py `
  tests\test_step128_boundary_formulation_repair_contract.py `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

## Phase 3: Real Repair48 Run

Run only:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase repair48 `
  --allow-large-real-rows `
  --output-interval 25
```

Do not add `--force` unless the report documents that the existing repaired
rows were stale, incomplete, or produced by the wrong runtime commit.

Expected repaired rows:

```text
duct_only_48_regularized_mass_balanced_pressure_outlet_500step_real
duct_only_48_convective_mass_balanced_pressure_outlet_500step_real
```

Expected repaired row role:

```text
row_role = repair_candidate_48
```

Expected semantics:

```text
regularized_mass_balanced_pressure_outlet
convective_mass_balanced_pressure_outlet
```

## Phase 4: Summary Refresh

After `repair48`, run:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase summary
```

Inspect:

```text
outputs/step121_lbm_boundary_real_campaign_and_gate_correction/campaign_manifest.json
outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_best_boundary_selection.json
outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_gate_report.json
outputs/step121_lbm_boundary_real_campaign_and_gate_correction/solver_report.json
```

Required manifest evidence:

```text
phase_history includes repair48
phase_history includes summary after repair48
phase_commit_history includes repair48 -> <Step129 runtime commit>
expected_rows includes both repair_candidate_48 rows
old Step127 reference and candidate rows remain collectable
```

## Phase 5: Repaired Row Audit Fields

For each repaired row, audit at least:

```text
run_metadata.json
finite_stability_report.json
duct_boundary_condition_report.json
limiter_activation_summary.json
velocity_profile_summary.json
boundary_flux_timeseries.csv
density_drift_timeseries.csv
stability_diagnostics_timeseries.csv
```

Required row-level fields:

```text
code_commit_at_run
solver_state_hash
run_manifest_hash
row_role
lbm_open_boundary_semantics
requested_window_completed
steps_completed
step120_validation_claimed
finite_pass
density_gate_pass
mass_drift_gate_pass
population_gate_pass
mach_gate_pass
first_failure_step
first_failure_reason
hard_stop_failure_reason
hard_stop_failure_step
hard_stop_mass_drift_gate_pass
candidate_mass_acceptance_gate_pass
mass_balance_correction_count
mass_balance_correction_abs_sum
unknown_population_delta_abs_sum
flow_development_gate_pass
flow_development_rejection_reasons
mass_total_delta_rel_final
flux_imbalance_rel_tail_mean
flux_imbalance_rel_tail_max
outlet_to_inlet_flux_ratio_tail_mean
midplane_to_inlet_flux_ratio_tail_mean
outlet_flux_tail_cv
limiter_activation_fraction
runtime_s
restored_checkpoint
```

## Phase 6: Acceptance Gates

A repaired candidate is selectable only if all of these are true:

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
candidate_mass_acceptance_gate_pass = true
```

Flow-development hard gates remain:

```text
abs(inlet_flux_tail_mean) > 1e-6
inlet/outlet sign consistent
0.80 <= abs(outlet_to_inlet_flux_ratio_tail_mean) <= 1.20
0.80 <= abs(midplane_to_inlet_flux_ratio_tail_mean) <= 1.20
flux_imbalance_rel_tail_mean < 0.10
flux_imbalance_rel_tail_max < 0.20
outlet_flux_tail_cv < 0.10
```

Additional Step129 audit rules:

```text
mass_balance_correction_count > 0 is acceptable.
correction magnitude must be bounded and reported.
limiter_activation_fraction must not make a failed physical row look passing.
```

## Phase 7: Decision Outcomes

### Outcome A: Both Repaired Candidates Fail

Report:

```text
campaign_state = 48_candidates_failed
final_classification = boundary_repair_failed_revisit_lbm_solver
best_boundary_selected = false
selected96_allowed = false
```

Next step must be another boundary-formulation repair iteration, not selected
96^3.

### Outcome B: Exactly One Repaired Candidate Passes

Report:

```text
best_boundary_selected = true
selected_boundary_semantics = <repair semantics>
selected_boundary_slug = regularized_mass_balanced or convective_mass_balanced
selected96_allowed_for_next_step = true
```

The next step may create a selected 96^3 duct-only goal. Step129 itself still
must not run selected 96^3.

### Outcome C: Both Repaired Candidates Pass

Select by:

```text
1. flow-development pass margin
2. flux_imbalance_rel_tail_mean
3. mass_total_delta_rel_final
4. outlet_flux_tail_cv
5. repair correction activation magnitude
6. limiter activation
7. runtime
```

## Phase 8: Step129 Report

Create:

```text
docs/campaigns/fluent_duct_flap/steps/129/report.md
```

The report must include:

```text
baseline commit and remote ref
Step129 runtime commit used by repair48
whether checkpoint repair-counter persistence was patched
preflight compile/test results
repair48 command
summary command
manifest phase_history
manifest phase_commit_history
metrics for both repaired candidates
old Step127 baseline/candidate comparison summary
selected boundary or failure classification
explicit selected 96^3 allowed/blocked decision
claims not made
```

## Phase 9: Current Documentation Updates

Update:

```text
docs/current/ACTIVE_CAMPAIGN.json
docs/current/STATUS.md
docs/current/VALIDATION_GATES.md
docs/current/READING_ORDER.md
```

Rules:

- If no repaired candidate passes, keep selected 96^3 blocked.
- If a repaired candidate passes, mark selected 96^3 as allowed only for a
  future step; do not imply Step129 ran selected 96^3.
- Keep GitHub Actions/CI language honest. Local pre-push `pytest -q` evidence
  is local hook evidence, not GitHub Actions evidence.

## Final Verification Before Push

Minimum:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\lbm\config.py `
  src\mpm_lbm\sim\lbm\fluid.py `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step129-final-focused `
  tests\test_step129_repair_checkpoint_counter_contract.py `
  tests\test_step128_boundary_formulation_repair_contract.py `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py

git diff --check
git status --short
```

Push only after:

- Goal/report/code/tests/artifacts/docs are consistent.
- The repaired rows were produced from the intended Step129 runtime commit.
- The report states exactly what was and was not run.
- `git status --short` contains only intended changes before commit.
- The final commit is pushed to `origin/main`.
- `git ls-remote origin refs/heads/main` verifies the pushed hash.
