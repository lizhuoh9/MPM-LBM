# Step122 LBM Boundary Real Campaign Execution And Selection Goal

## Source Review

This Step122 goal is derived from the review of GitHub remote `main` commit
`82ded671a598940e120f3c9dcc63983a44b9c21a`, commit message
`fix: add step121 boundary campaign gates`.

The review accepted the Step121 campaign controller direction:

- pending and failed campaign states are separated,
- reference readiness is required before selection,
- failed candidates stay visible,
- selected 96^3 specs are generated dynamically,
- final limiter gates are selected-chain only,
- Step120 actual row execution gained lightweight failure stops,
- checkpoint writes are atomic and fallback-capable,
- failure snapshots now include real field data,
- the committed Step121 smoke artifact is real LBM but explicitly not
  validation evidence.

The review also found remaining execution-consistency issues that must be fixed
before large-grid execution is trusted.

## Primary Objective

Implement Step122 as the last hardening layer before and during the real LBM
boundary campaign:

1. fix the remaining Step121/Step120 execution-consistency issues,
2. add regression and actual-run integration tests for those issues,
3. run a full repository pytest pass after the hardening,
4. execute the real 48^3 reference and candidate phases when the hardened code is
   ready,
5. select the best 48^3 boundary from actual data,
6. only then allow selected 96^3 duct and selected static two-flap phases.

Step122 must keep quasi-2D, FSI, Fluent, and Figure 29.3 parity claims closed
unless the selected evidence chain actually satisfies the declared gates.

## Non-Negotiable Scope Rules

- Do not run `selected-static` before the selected 96^3 duct row exists and
  passes.
- Do not let selected 96^3 rows silently use different boundary parameters from
  the selected 48^3 candidate.
- Do not rely only on row CSV files for restart history if checkpoint
  `history_json` contains newer records.
- Do not delay mass-drift failure detection until the next full output sample if
  mass can be reduced cheaply at `failure_check_interval`.
- Do not claim large-grid success from helper tests or smoke rows.
- Do not treat interrupted, wall-time-limited, placeholder, or unrun rows as
  physical failures.
- Keep Step122 static two-flap rows LBM-only; do not describe them as two-way
  FSI.
- Keep raw checkpoint and raw field snapshot payloads under ignored
  `outputs/tmp`.

## P0 Required Hardening Before Large Runs

### P0.1 Selected-Static Requires Selected 96^3 Duct Pass

`resolve_step121_phase_specs("selected-static", ...)` must inspect the output
directory and require the selected duct row:

- exists,
- has `requested_window_completed = true`,
- has `step120_validation_claimed = true`,
- has `first_failure_step = null`,
- has `first_failure_reason = null`.

If this gate is not satisfied, selected-static must fail fast before constructing
or running the static row.

### P0.2 Full Boundary/Config Provenance In Best Selection

The best-selection artifact must store enough provenance to reconstruct the
selected boundary and detect drift:

- `open_boundary_rho_min`,
- `open_boundary_rho_max`,
- `open_boundary_u_max`,
- `open_boundary_noneq_cap`,
- `open_boundary_population_floor`,
- `inlet_u_lbm`,
- `outlet_rho`,
- `lbm_niu`,
- `lbm_viscosity_semantics`,
- `lbm_relaxation_semantics`,
- `tau` or equivalent tau report field if available,
- source spec/config hash,
- selected row name and selected semantics.

Selected 96^3 duct and selected static rows must inherit this provenance instead
of relying on defaults.

### P0.3 Selected 96^3 Provenance Validation

Before selected 96^3 duct/static specs run, Step121/Step122 must validate that
the selected spec provenance matches the best-selection artifact. A mismatch
must fail fast with a clear error.

### P0.4 Actual `.npz` Checkpoint History Restore

Step120 actual checkpoint restore must read `history_json` from `.npz`
checkpoints when present and return/merge it with existing row CSV history.

Required merged history order:

1. checkpoint `history_json`,
2. existing row CSV history,
3. newly produced runtime records.

The merged records must be de-duplicated by `step`, with newer records replacing
older records at the same step.

### P0.5 Mass Drift In Actual Lightweight Stop

The actual `failure_check_interval` path must detect mass drift before the next
full sample. Add Taichi-side or otherwise bounded lightweight mass reduction so
the runner can compute mass drift at failure-check cadence.

The detector must include:

- `mass_total`,
- `mass_initial`,
- `mass_total_delta_rel`,
- `mass_drift` reason if `abs(delta_rel) > 0.05`.

### P0.6 Actual Tiny Immediate-Failure/Restart Integration Test

Add a real tiny integration test that exercises the actual LBM row runner path,
not only helper functions:

- configure `failure_check_interval < output_interval`,
- force a controlled failure before the next full output sample,
- verify the row stops immediately,
- verify a real `.npz` checkpoint exists,
- verify raw failure snapshot payload is in ignored runtime storage,
- verify committed snapshot JSON contains anomaly statistics,
- corrupt the newest checkpoint and verify restore falls back to the previous
  valid checkpoint,
- verify merged history remains continuous after restart.

The test must stay tiny and bounded.

### P0.7 Full Repository Regression

After P0 code changes, run:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

If the full suite is too slow or blocked, record the exact blocker in the report
and run the broadest feasible Step120/Step121/Step122 regression slice.

## P1 Real 48^3 References

After P0 passes, run:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase references48 --allow-large-real-rows --output-interval 50
```

Do not use `--force` on resumable large rows unless intentionally discarding
prior evidence.

Expected post-refresh state:

- `campaign_state = awaiting_48_candidates`,
- `reference_comparison_ready = true`.

Reference rows:

- `duct_only_48_legacy_boundary_500step_reference_real`,
- `duct_only_48_regularized_boundary_500step_reference_real`.

## P2 Real 48^3 Candidates

Run:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase candidates48 --allow-large-real-rows --output-interval 50
```

Candidate rows:

- `duct_only_48_regularized_limited_boundary_500step_real`,
- `duct_only_48_convective_outlet_boundary_500step_real`.

Candidate hard gates:

- `requested_window_completed = true`,
- `simulation_backed_artifact = true`,
- `finite_pass = true`,
- `density_gate_pass = true`,
- `mass_drift_gate_pass = true`,
- `population_gate_pass = true`,
- `mach_gate_pass = true`,
- `first_failure_reason = null`,
- `flux_imbalance_rel_tail_mean < 0.1`,
- `abs(mass_total_delta_rel_final) < 0.005`.

Limited candidate additionally requires:

- actual limiter activation fraction `<= 0.05`.

## P3 48^3 Decision

Refresh summary and inspect:

`outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_best_boundary_selection.json`

Allowed outcomes:

- both candidates failed actual 48^3 gates:
  `campaign_state = 48_candidates_failed`,
  `final_classification = boundary_repair_failed_revisit_lbm_solver`,
  stop and do not run 96^3.
- one candidate passed:
  `best_boundary_selected = true`,
  `campaign_state = best_48_selected`,
  proceed to selected 96^3 duct.
- both candidates passed:
  rank by flux imbalance tail mean, mass drift, limiter activation, Mach, then
  runtime.

## P4 Selected 96^3 Duct

Only after a valid best-selection artifact:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase selected96 --best-selection-path outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_best_boundary_selection.json --allow-large-real-rows --output-interval 100
```

Required settings:

- `failure_check_interval = 5`,
- `checkpoint_every = 100`,
- `snapshot_on_failure = true`,
- exact selected 48^3 boundary/config provenance.

If it fails, keep:

- `campaign_state = awaiting_selected_96_duct`,
- `final_classification = boundary_repair_partial_continue_lbm`.

Do not run selected static after a selected duct failure.

## P5 Selected Static Two-Flap

Only after selected 96^3 duct passes:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase selected-static --best-selection-path outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_best_boundary_selection.json --allow-large-real-rows --output-interval 100
```

This row must be described only as a static two-flap LBM-only geometry gate, not
FSI.

## P6 Final Summary And Classification

Refresh:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase summary
```

Final classification rules:

- `boundary_repair_failed_revisit_lbm_solver`: only when both real 48^3
  candidates executed and failed.
- `boundary_repair_partial_continue_lbm`: any incomplete, interrupted, failed
  selected 96/static, wall-time-limited, or checkpoint-pending chain.
- `boundary_repair_success_go_to_quasi2d`: only when references complete, best
  48^3 passes, selected 96^3 duct passes, selected static two-flap passes,
  selected-chain limiter is acceptable, selected-chain first failure is absent,
  physical-nu remains policy guarded, and no Fluent/FSI/Figure 29.3 claim is
  made.

## Required Step122 Artifacts

- `STEP122_LBM_BOUNDARY_REAL_CAMPAIGN_EXECUTION_AND_SELECTION_REPORT.md`
- `docs/122_lbm_boundary_real_campaign_execution_and_selection.md`
- Step122 tests under `tests/test_step122_*.py`
- refreshed Step121/Step122 output artifacts under
  `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/`
- committed proof of current campaign state and executed rows
- no committed bulky raw arrays from `outputs/tmp`

## Verification And Push Conditions

Before pushing:

- run `git diff --check`,
- run focused Step122 tests,
- run Step120/Step121 compatibility tests touched by the changes,
- run full repository pytest if feasible,
- run any completed Step122 phase artifact refresh,
- inspect `git status --short`,
- commit all relevant code, tests, docs, and small artifacts,
- push `main` to GitHub,
- verify `origin/main` equals local `HEAD`.

Report the final commit hash, remote branch, exact tests, exact campaign state,
and any remaining execution blockers.
