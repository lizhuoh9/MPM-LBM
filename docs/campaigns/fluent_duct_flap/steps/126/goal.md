# Step126 LBM Boundary 48^3 Reference Campaign Execution Goal

## Source Review

This goal follows the review confirming remote `main` at commit
`6ad3108994c55d1863fc2c2d4a830a26799fc9f4`, commit message
`fix: record Step125 campaign provenance identity`.

Step125 is accepted as a provenance-only patch. It separated the campaign base
commit from current code identity, upgraded Step121 campaign manifests to schema
version 2, and added `code_commit_at_run` to future Step120 row artifacts. It
did not run real 48^3/96^3 rows, did not change solver physics, did not change
LBM boundary formulas, and did not make quasi-2D, FSI, Fluent validation, or
Figure 29.3 parity claims.

## Step126 Objective

Execute the real 48^3 reference phase under the existing Step121/Step124/Step125
campaign controller and gate system.

Step126 must produce real artifacts for:

- `duct_only_48_legacy_boundary_500step_reference_real`
- `duct_only_48_regularized_boundary_500step_reference_real`

Then Step126 must refresh the campaign summary and decide, from the real
reference artifacts only, whether the campaign may advance to the 48^3 candidate
phase.

## Scope Boundary

Step126 is a real 48^3 references execution step.

It may:

- Run `--phase references48`.
- Resume from existing checkpoints if interrupted.
- Run `--phase summary` after references complete or fail terminally.
- Commit generated reference-phase artifacts needed for audit.
- Update current docs and Step126 report.
- Add a focused regression test only if the real run exposes a runner,
  manifest, provenance, checkpoint, or gate bug.
- Make the minimum code fix required by such a bug.

It must not:

- Run `candidates48`.
- Run selected 96^3 duct.
- Run selected 96^3 static two-flap.
- Run quasi-2D.
- Run FSI.
- Claim Fluent validation or Figure 29.3 parity.
- Use `--force`.
- Reset, delete, or manually rewrite checkpoint state to manufacture success.
- Change LBM solver physics, boundary formulas, or gate thresholds unless a
  real runtime bug is first captured by a regression test and the fix is
  strictly required to complete the Step126 objective.

## Phase 0: Preflight

Confirm the local and remote refs:

```powershell
git status --short
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Run focused preflight tests using the trusted interpreter and a repo-local
pytest temp directory:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step126-preflight `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

This verifies the campaign controller, provenance identity, manifest filtering,
and gate contracts before expensive real rows run.

## Phase 1: Run Real 48^3 References

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase references48 `
  --allow-large-real-rows `
  --output-interval 25
```

Rules:

- Do not add `--force`.
- If interrupted, repeat the exact same command to resume.
- Preserve runtime provenance in `campaign_manifest.json`.
- Each row artifact must include `code_commit_at_run`.
- Runtime checkpoints stay under `outputs/tmp` and are not committed unless
  already part of an intentional tracked artifact.

## Phase 2: Refresh Summary

After the reference phase finishes or reaches a terminal real failure, run:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase summary
```

Inspect:

- `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_gate_report.json`
- `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_best_boundary_selection.json`
- `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/solver_report.json`
- each reference row `finite_stability_report.json`
- each reference row `run_metadata.json`

## Phase 3: Decision Rules

### Legacy Reference Passes

The legacy reference passes only if the row is real simulation-backed evidence
and satisfies at least:

- `requested_window_completed = true`
- `simulation_backed_artifact = true`
- `finite_pass = true`
- `density_gate_pass = true`
- `mass_drift_gate_pass = true`
- `population_gate_pass = true`
- `mach_gate_pass = true`
- `first_failure_reason = null`
- `first_failure_step = null`

If both the legacy reference and the old-regularized reference complete or the
old-regularized row provides accepted terminal comparison evidence, summary may
advance to:

```text
campaign_state = awaiting_48_candidates
final_classification = boundary_repair_partial_continue_lbm
```

Only this state permits a future Step127 `candidates48` goal.

### Legacy Reference Fails

If the legacy reference has simulation-backed terminal physical failure such as
`rho_range`, `mass_drift`, `negative_population_fraction`, `max_v`, or
`nonfinite_field`, the campaign must stop:

```text
campaign_state = 48_legacy_reference_failed
final_classification = boundary_repair_failed_revisit_lbm_solver
```

In that case, do not run candidates. The next work becomes legacy baseline
instability diagnosis focused on MRT relaxation, legacy all-pop boundary,
streaming/boundary order, mass drift first-failure location, wall/open-boundary
corners, and density blow-up location.

### Old-Regularized Reference Fails But Legacy Passes

If the old-regularized reference fails with simulation-backed terminal evidence
while legacy passes, this is valid failed-baseline comparison evidence. The
campaign may still advance to `awaiting_48_candidates` if the Step121 summary
contract accepts it.

## Report Requirements

Create:

```text
docs/campaigns/fluent_duct_flap/steps/126/report.md
```

The report must include:

- `HEAD` used before references.
- live remote `main` before references.
- `campaign_base_commit`.
- `current_code_commit` after manifest refresh.
- `phase_commit_history`.
- row names.
- row runtimes.
- checkpoint usage.
- row `code_commit_at_run`.
- row `solver_state_hash`.
- row `run_manifest_hash`.
- `requested_window_completed`.
- `steps_completed`.
- `mass_total_delta_rel_final`.
- `flux_imbalance_rel_tail_mean`.
- `flow_development_gate_pass`.
- `first_failure_step`.
- `first_failure_reason`.
- final `campaign_state`.
- final `final_classification`.
- explicit decision on whether Step127 candidates are allowed.
- explicit no-claim statement for quasi-2D, FSI, Fluent validation, and Figure
  29.3 parity.

## Verification

Run compile checks:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py
```

Run focused campaign tests:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step126-focused `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

If a code fix is made, add the smallest regression test that fails before the
fix and passes afterward.

## Push Condition

Push to `origin/main` only after:

- Preflight passes.
- The reference phase and summary phase complete or produce a terminal
  Step121-recognized state.
- Step126 report is written.
- Focused verification and compile checks pass.
- `git status --short` contains only intended tracked/untracked changes before
  commit.
- The final pushed remote `main` hash is verified with a live remote query.
