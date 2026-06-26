# Step120 Report: LBM Boundary Repair Large Real Execution

## Result

Step120 repairs the Step119 real-run workflow so large LBM boundary rows are
recoverable, low-overhead, and correctly gated before any quasi-2D or FSI work
is allowed.

Final classification from the committed default artifact:

`boundary_repair_failed_revisit_lbm_solver`

Step120 quasi-2D remains blocked. No Fluent validation is claimed. No Figure
29.3 parity is claimed. No full FSI validation is claimed.

## What Changed

Code changes:

- Added `experiments/steps/step120_lbm_boundary_repair_large_real_execution.py`.
- Added strict row status classification so incomplete large-row placeholders
  are not treated as resume-complete rows.
- Added real checkpoint write/restore for LBM fields under
  `outputs/tmp/step120_checkpoints`, with committed artifacts containing only
  metadata and gate summaries.
- Added checkpoint persistence for actual open-boundary limiter counters, so
  resumed rows keep cumulative limiter counts.
- Added lightweight Taichi-side stability reductions for density, velocity,
  population min/max, and negative-population counts.
- Added direct Taichi open-boundary limiter counters for rho, velocity, noneq,
  population floor, and reconstructed boundary population denominator.
- Added best-boundary selection logic that ranks only completed 48^3
  candidates and then requires only the selected 96^3 duct/static rows.
- Added Step120 gate artifacts that keep quasi-2D, Fluent, Figure 29.3, and
  full-FSI claims closed unless the required real rows pass.

Tests added:

- `tests/test_step120_row_status_resume_contract.py`
- `tests/test_step120_checkpoint_restart_contract.py`
- `tests/test_step120_lightweight_reduction_contract.py`
- `tests/test_step120_actual_limiter_counter_contract.py`
- `tests/test_step120_best_boundary_selection_contract.py`
- `tests/test_step120_quasi2d_gate_contract.py`
- `tests/test_step120_skipped_artifact_semantics_contract.py`

Artifacts added under:

`outputs/step120_lbm_boundary_repair_large_real_execution/`

## Important Artifact Boundary

The committed output includes one real tiny LBM row:

`tiny_step120_real_runner_smoke`

That row completed 3 real LBM steps on a 5x4x4 duct-only grid. It proves the
Step120 runner can instantiate `LBMFluid3D`, step the limited regularized open
boundary, write checkpoints, emit lightweight stability diagnostics, and report
actual limiter counters. It is explicitly `not_used_for_validation=true`.

The 48^3 rows remain incomplete real-run targets unless the operator passes
`--allow-large-real-rows`. They are recorded as
`large_real_row_requires_explicit_allowance`, with
`flux_balance_reported=false`, so they cannot be mistaken for completed
validation.

The physical-nu 96^3 strict guard row is recorded as an expected tau-margin
policy skip. It is not a failed simulation and not a validation pass.

## Current Gate State

From `outputs/step120_lbm_boundary_repair_large_real_execution/step120_gate_report.json`:

- `quasi2d_allowed = false`
- `step121_quasi2d_allowed = false`
- `best_boundary_selected = false`
- `validation_claim_allowed = false`
- `final_classification = boundary_repair_failed_revisit_lbm_solver`

Row status summary:

- `completed = 1`
- `incomplete_placeholder = 4`
- `expected_policy_skip = 1`

Tiny smoke final metrics:

- `steps_completed = 3`
- `limiter_activation_count = 0`
- `limiter_activation_denominator = 120`
- `negative_population_count = 0`
- `mass_total_delta_rel_final = 0.00960255265235901`
- `flux_imbalance_rel_final = 1.000001473653276`

The tiny flux imbalance is not a validation failure because the row is a tiny
runner smoke and is excluded from physical validation.

## Findings

1. Step119's placeholder resume hazard is fixed: rows skipped because large
   real execution was not authorized classify as `incomplete_placeholder` and
   are not resume-complete.
2. The previous `checkpoint_every` contract is now backed by real `.npz`
   checkpoints in ignored runtime storage.
3. Resume now restores cumulative limiter counters from checkpoint metadata;
   the checkpoint test checks resumed and uninterrupted limiter counts match.
4. Step120 no longer needs full `f/F/rho/v/solid` NumPy snapshots for routine
   stability checks. The default failure checks use Taichi scalar reductions.
5. Limiter activation is now measured by direct kernel counters instead of a
   post-processed estimate.
6. Best-boundary selection no longer requires both limited and convective 96^3
   rows. It first selects a passing 48^3 candidate and then requires only the
   selected duct-only 96^3 and selected static two-flap 96^3 rows.
7. Large-row skipped artifacts correctly report `flux_balance_reported=false`.
8. The actual large 48^3/96^3 campaign has not been run in this commit, so no
   boundary repair success or Fluent/Figure 29.3 parity claim is justified.

## Remaining Work

Run the real rows in controlled order:

1. `duct_only_48_legacy_boundary_500step_reference_real`
2. `duct_only_48_regularized_boundary_500step_reference_real`
3. `duct_only_48_regularized_limited_boundary_500step_real`
4. `duct_only_48_convective_outlet_boundary_500step_real`
5. Select the best passing 48^3 candidate, if one exists.
6. Run only the selected 96^3 duct-only row.
7. If that passes, run only the selected 96^3 static two-flap row.
8. Open Step121 quasi-2D only if Step120 ends as
   `boundary_repair_success_go_to_quasi2d`.

Example explicit row command:

```powershell
& 'D:\working\taichi\env\python.exe' `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  --row duct_only_48_regularized_limited_boundary_500step_real `
  --allow-large-real-rows `
  --force
```

Runtime checkpoints stay under `outputs/tmp/step120_checkpoints` and are not
committed.

## Verification

Step120 focused contract tests:

`13 passed, 28 warnings in 232.58s`

Step119 plus Step120 regression slice:

`23 passed, 32 warnings in 345.43s`

Checkpoint/resume contract after counter persistence fix:

`1 passed, 12 warnings in 125.62s`

Post-final lightweight/resume focused subset:

`5 passed, 24 warnings in 240.70s`

Default Step120 artifact refresh:

`& 'D:\working\taichi\env\python.exe' experiments\steps\step120_lbm_boundary_repair_large_real_execution.py --force`

The artifact refresh completed and produced the committed
`outputs/step120_lbm_boundary_repair_large_real_execution/` tree.

Full repository pytest:

`1280 passed, 48 warnings in 1051.49s`

The warnings are the existing Taichi 19x19 matrix/vector initialization
warnings exercised by the LBM runtime smoke paths.
