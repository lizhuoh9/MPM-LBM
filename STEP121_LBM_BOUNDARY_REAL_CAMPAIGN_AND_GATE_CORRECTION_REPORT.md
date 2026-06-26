# Step121 LBM Boundary Real Campaign And Gate Correction Report

## Status

Step121 implemented the campaign/gate corrections requested after the review of
remote `main` commit `ef4a19c254383cf92397bd0353f29c6dab668287`.

Current committed Step121 artifact state:

- Output directory:
  `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/`
- Phase executed in this commit: `smoke`
- Campaign state: `awaiting_48_references`
- Final classification: `boundary_repair_partial_continue_lbm`
- Quasi-2D allowed: `false`
- Fluent/Figure 29.3/FSI claim allowed: `false`

This is intentionally not a physical success claim. The real 48^3 and selected
96^3 rows are now expressible through the Step121 phase CLI, but they were not
marked complete by the smoke artifact.

## Code Changes

Step121 added a new campaign controller:

- `experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py`

The controller provides:

- pending-versus-failed campaign states,
- reference readiness checks before best-boundary selection,
- candidate summaries that keep failed and rejected candidates visible,
- dynamic selected 96^3 duct/static spec generation,
- selected 96^3 phase guards requiring a best-selection artifact,
- selected-chain-only limiter gates,
- JSON/CSV Step121 summary and solver-report artifacts,
- lightweight failure detector helper,
- checkpoint payload helper with atomic write and fallback loading,
- localized failure snapshot helper that keeps raw arrays in ignored runtime
  storage.

The Step120 runner was repaired because Step121 real phases call it for actual
LBM execution:

- `failure_check_interval` now performs an immediate lightweight stop instead
  of waiting for a full output sample.
- A lightweight stop writes a checkpoint and a failure snapshot.
- Checkpoint writes are tmp-write, reopen-validate, and atomic replace.
- Checkpoint restore falls back to the newest valid previous checkpoint when a
  later checkpoint is corrupted.
- Restarted rows load and de-duplicate existing CSV history so trend checks
  include pre-checkpoint diagnostics.
- Failure snapshots write committed stats/locator JSON and ignored raw `rho`,
  `v`, `f`, and `F` arrays under `outputs/tmp/step120_failure_snapshots`.

## Step121 CLI

Supported phases:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase smoke --force
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase references48 --allow-large-real-rows
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase candidates48 --allow-large-real-rows
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase selected96 --best-selection-path outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_best_boundary_selection.json --allow-large-real-rows
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase selected-static --best-selection-path outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_best_boundary_selection.json --allow-large-real-rows
```

The selected 96^3 phases intentionally reject missing best-selection artifacts.

## Tests Added

- `tests/test_step121_campaign_gate_contract.py`
- `tests/test_step121_checkpoint_failure_contract.py`

The new tests cover:

- pending candidates are partial, not failed,
- failure classification requires both real 48^3 candidates to have run and fail,
- selection requires simulation-backed 48^3 references,
- failed candidates remain visible even when rejected from validation,
- selected-only limiter gate ignores unrelated rows,
- selected 96^3 phase guard requires best selection,
- lightweight failure detector reasons,
- history de-duplication by step,
- atomic checkpoint fallback,
- localized failure snapshot stats plus ignored raw field dump.

## Verification

Commands run:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest tests\test_step121_campaign_gate_contract.py tests\test_step121_checkpoint_failure_contract.py -q
```

Result: `10 passed`.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest tests\test_step120_checkpoint_restart_contract.py::test_step120_tiny_checkpoint_resume_matches_uninterrupted_result -q
```

Result: `1 passed`.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest <all test_step120*.py and test_step121*.py files> -q
```

Result: `23 passed`.

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase smoke --force
```

Result: completed `tiny_step121_real_runner_smoke` and wrote Step121 artifacts.

## What Was Not Claimed

Step121 does not claim:

- 48^3 boundary repair success,
- selected 96^3 duct-only success,
- selected 96^3 static two-flap success,
- quasi-2D readiness,
- two-way FSI readiness,
- Fluent parity,
- Figure 29.3 parity.

The current committed state is a corrected execution controller and a small
smoke artifact. The real campaign remains pending until the 48^3 and selected
96^3 phases are run.

## Next Execution Order

1. Run `references48` with `--allow-large-real-rows`.
2. Run `candidates48` with `--allow-large-real-rows`.
3. Inspect `step121_best_boundary_selection.json`.
4. If a best 48^3 candidate is selected, run `selected96` with that selection
   artifact.
5. If selected 96^3 duct passes, run `selected-static`.
6. Re-run `--phase summary` to refresh Step121 campaign state.
