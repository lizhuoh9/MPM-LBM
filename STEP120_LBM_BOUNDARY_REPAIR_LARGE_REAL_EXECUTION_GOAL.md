# Step120 LBM Boundary Repair Large Real Execution Goal

## Source Review

This goal is derived from the user-provided review of GitHub `origin/main`
commit `1e8a33a7803a713c716b546ae93c581198cdfb9b`
(`feat: add step119 real boundary validation runner`).

The review accepts Step119 as a truthful runner framework:

- Step119 added a real, non-synthetic LBM runner.
- Step119 committed one real tiny smoke row.
- Step119 required explicit `--allow-large-real-rows` for 48^3/96^3 target
  rows.
- Step119 recorded unexecuted target rows as incomplete rather than forged
  successes.
- Step119 kept quasi-2D, FSI, and Fluent parity gates closed.

The review also states that Step119 only proves the tiny runner can initialize
`LBMFluid3D`, run the limited regularized boundary path, read stability
diagnostics, and emit the artifact schema. It does not prove long-window
boundary repair success. Step120 must repair the runner, diagnostics, resume,
checkpoint, limiter accounting, and gate semantics before any later quasi-2D
or FSI work is allowed.

## Objective

Repair Step119 into a recoverable, low-overhead, comparison-gated large-real
execution system. Step120 must:

1. Fix row status and resume so incomplete placeholder artifacts are never
   mistaken for completed runs.
2. Implement or explicitly report real checkpoint behavior for resumable LBM
   state, with checkpoint files kept out of Git.
3. Replace long-window full-array diagnostic polling with a lightweight
   reduction path suitable for 96^3 runs.
4. Add actual open-boundary limiter counters at the boundary application
   surface rather than relying only on post-processed outlier estimates.
5. Rewrite best-boundary selection and quasi-2D gating so only the selected
   candidate must pass 96^3 and static two-flap validation.
6. Fix skipped-row artifact semantics, including `flux_balance_reported=false`
   when no fluid records exist.
7. Generate truthful Step120 reports/artifacts that distinguish completed,
   skipped, failed, wall-time-stopped, checkpoint-available, and incomplete
   rows.
8. Keep Fluent parity, FSI, and dynamic/quasi-2D claims closed unless the
   explicit Step120 success classification is achieved.

This step is not a quasi-2D step. It is the last LBM-only large-real execution
gate before a possible later
`STEP121_D3Q19_QUASI_2D_PERIODIC_Z_FLOW_BASELINE_GOAL.md`.

## Non-Negotiable Constraints

- Preserve upstream Step numbering and naming.
- Do not claim Fluent parity, FSI validity, dynamic flap behavior, or quasi-2D
  readiness from tiny smoke rows.
- Do not mark a skipped or placeholder large row as a validation pass.
- Do not require both limited and convective candidates to pass if only one is
  selected by the 48^3 comparison gate.
- Do not hard-code the static two-flap row to limited boundary semantics. It
  must follow the selected best boundary.
- Do not commit runtime checkpoints. They must live in an ignored local path.
- Do not hide expensive long-window work behind synthetic artifacts.
- If large rows cannot be run within the local wall-clock budget, record that
  as `boundary_repair_partial_continue_lbm`, not as success.

## Phase P0: Runner Correctness

### P0.1 Row Status and Resume

Add explicit row statuses:

- `completed`
- `expected_policy_skip`
- `incomplete_placeholder`
- `stopped_on_failure`
- `stopped_on_walltime`
- `checkpoint_available`
- `interrupted`

Rules:

- `requested_window_completed=true` means `completed`.
- `skipped_reason=tau_margin` means `expected_policy_skip`.
- `skipped_reason=large_real_row_requires_explicit_allowance` means
  `incomplete_placeholder`.
- A row with a checkpoint but without a completed requested window is
  resumable, not complete.
- A row stopped by first failure is completed failure evidence, but not a
  validation pass.
- A row stopped by max wall time is not a validation pass and should expose
  checkpoint availability if present.

Required regression:

- Given a placeholder row artifact and a subsequent run with
  `--allow-large-real-rows` without `--force`, the runner must not resume the
  placeholder as complete. It must begin real execution or restore a real
  checkpoint.

### P0.2 Checkpoint Semantics

Implement runtime checkpoints for real rows or explicitly emit
`checkpoint_every_not_implemented=true`. The preferred implementation is real
checkpointing.

Checkpoint files must be written under an ignored path such as:

```text
outputs/tmp/step120_checkpoints/<row>/
```

Checkpoint payload must include at least:

- `f`
- `F`
- `rho`
- `v`
- `solid` or `static_solid`
- current step
- config hash
- schema version

Restore must validate:

- field shapes
- boundary semantics
- relaxation semantics
- config hash
- schema version

Required regression:

- Run a tiny real row to step 4 and write a checkpoint.
- Resume to step 10.
- Compare against an uninterrupted 10-step run within tolerance.

### P0.3 Artifact Semantics

Fix summary semantics:

- If a row has no records, `flux_balance_reported=false`.
- A tau-margin policy skip is not an incomplete validation row.
- Required validation rows, policy guard rows, optional comparison rows, and
  tiny smoke rows must be reported separately.

## Phase P1: Low-Overhead Diagnostics for 96^3

### P1.1 Lightweight Reduction Fields

Add a lightweight diagnostic path that can return scalar reductions without
copying full 96^3 `f` and `F` arrays every few steps.

Required fields:

- `rho_min_reduced`
- `rho_max_reduced`
- `max_v_reduced`
- `f_min_reduced`
- `f_max_reduced`
- `F_min_reduced`
- `F_max_reduced`
- `negative_population_count_reduced`
- `boundary_x_min_negative_count`
- `boundary_x_max_negative_count`

Required regression:

- On a small grid, lightweight reductions must agree with the existing full
  NumPy diagnostics within tolerance.

### P1.2 Actual Limiter Counters

Add direct open-boundary limiter counters:

- `rho_clip_count_step`
- `rho_clip_count_run`
- `velocity_clip_count_step`
- `velocity_clip_count_run`
- `noneq_clip_count_step`
- `noneq_clip_count_run`
- `population_floor_count_step`
- `population_floor_count_run`
- `reconstructed_population_count_step`
- `reconstructed_population_count_run`

Step counters must be cleared before each boundary application. Run counters
must accumulate. The activation fraction must be:

```text
actual limiter activations / actual reconstructed boundary-population operations
```

Required regression:

- Construct a boundary state that triggers rho, velocity, nonequilibrium, and
  population-floor limiting. Verify counters increment directly and the
  denominator is reconstructed boundary-population operations, not full-domain
  populations.

### P1.3 Two-Level Sampling

Support separate controls:

- `failure_check_interval`
- `summary_output_interval`
- `full_population_snapshot_interval`
- `snapshot_on_failure`
- `snapshot_on_final`

Recommended defaults:

- 48^3 summary interval: 25 or 50.
- 96^3 summary interval: 100.
- Lightweight failure checks every 5 steps or less.
- Full population snapshots off by default, except failure and final snapshots.

## Phase P2: Best-Boundary Selection and Final Gate

### Row Roles

Reference rows:

- `duct_only_48_legacy_boundary_500step_reference_real`
- `duct_only_48_regularized_boundary_500step_reference_real`
- optional 96^3 legacy reference

Candidate rows:

- `duct_only_48_regularized_limited_boundary_500step_real`
- `duct_only_48_convective_outlet_boundary_500step_real`
- selected 96^3 best candidate

Policy guard:

- physical-nu strict tau row

Final geometry row:

- 96^3 static two-flap selected best candidate

### 48^3 Comparison Gate

A new boundary candidate must:

- complete 500 steps;
- pass density, mass, population, Mach, and first-failure gates;
- satisfy `flux_imbalance_rel_tail_mean < 0.1`;
- satisfy `abs(mass_drift_final) < 0.005`;
- improve over old regularized boundary;
- not be materially worse than legacy:
  - mass drift no more than 2x legacy and still under absolute 0.005;
  - flux tail imbalance within a documented tolerance;
- keep direct limiter activation under threshold.

### Best Boundary Selection

Rank only 48^3 candidates. Exclude:

- tiny smoke rows;
- references;
- skipped rows;
- `not_used_for_validation=true` rows.

Ranking keys:

1. hard gates pass;
2. lower `flux_imbalance_rel_tail_mean`;
3. lower `abs(mass_drift_final)`;
4. lower limiter activation fraction;
5. lower max Mach;
6. lower runtime.

Write:

```text
best_boundary_selection.json
```

It must record:

- selected boundary semantics;
- selected limiter parameters;
- 48^3 comparison metrics;
- selection reason;
- candidate rejection reasons.

### 96^3 and Static Flap Gate

Do not require both limited and convective 96^3 rows to pass. The correct logic
is:

```text
48^3 best selected
AND 96^3 same best boundary passes
AND 96^3 static two-flap same boundary passes
AND actual limiter activation acceptable
AND physical-nu strict guard remains skipped
=> quasi2d_allowed
```

## Phase P3: Real 48^3 Campaign

Execute rows in stages rather than all at once:

1. Legacy reference.
2. Old regularized reference.
3. Limited candidate with actual limiter counters.
4. Convective candidate.

Recommended command shape:

```powershell
python experiments/steps/step120_lbm_boundary_repair_large_real_execution.py `
  --row duct_only_48_legacy_boundary_500step_reference_real `
  --allow-large-real-rows `
  --force `
  --output-interval 25 `
  --checkpoint-every 100
```

If both limited and convective fail the 48^3 comparison gate, stop and classify:

```text
boundary_repair_failed_revisit_lbm_solver
```

If at least one candidate passes, select the best boundary and continue.

## Phase P4: Real 96^3 Duct-Only Campaign

Run only the selected best candidate first:

```text
duct_only_96_<best_boundary>_1000step_real
```

Recommended policy:

- summary interval 100;
- lightweight failure checks every 5 steps;
- checkpoint every 100 steps;
- stop on first failure;
- full NumPy snapshots only on first failure and final.

If the selected candidate fails:

1. Run optional 96^3 legacy reference.
2. Optionally run the second candidate.
3. Emit scale diagnosis:
   - legacy stable plus candidates fail => open-boundary repair failed;
   - legacy also fails => broader 96^3 solver/MRT/wall-corner stability issue.

## Phase P5: Static Two-Flap Validation

Only after a 96^3 duct-only selected boundary passes, generate:

```text
static_two_flap_96_<selected_boundary>_1000step_real
```

The static two-flap row must use exactly the same:

- boundary semantics;
- limiter parameters;
- viscosity semantics;
- output/failure policy.

Success requires:

- requested window complete;
- density, mass, population, Mach gates pass;
- no first failure;
- actual limiter activation acceptable;
- finite throat, recirculation, and flap-region diagnostics;
- explicit static LBM-only labeling, with no FSI claim.

## Phase P6: Required Artifacts

Top-level artifacts:

```text
outputs/step120_lbm_boundary_repair_large_real_execution/
  solver_report.json
  run_matrix_summary.json
  row_status_summary.json
  boundary_variant_48_comparison.json
  best_boundary_selection.json
  boundary_variant_96_validation.json
  first_failure_global_summary.json
  limiter_actual_activation_summary.json
  step120_gate_report.json
  README.md
```

Per-row artifacts:

```text
run_metadata.json
driver_config.json
duct_boundary_condition_report.json
finite_stability_report.json
first_failure_diagnostics.json
limiter_activation_summary.json
fluid_diagnostics_timeseries.csv
density_drift_timeseries.csv
boundary_flux_timeseries.csv
stability_diagnostics_timeseries.csv
```

Runtime checkpoint artifacts must not be committed.

## Phase P7: Required Tests

Add focused tests:

1. `test_step120_row_status_resume_contract.py`
   - placeholder does not count complete;
   - tau skip is expected policy completion;
   - real completed row resumes normally.
2. `test_step120_checkpoint_restart_contract.py`
   - tiny segmented restart and uninterrupted result agree within tolerance.
3. `test_step120_lightweight_reduction_contract.py`
   - reduction agrees with small-grid full NumPy diagnostics.
4. `test_step120_actual_limiter_counter_contract.py`
   - triggered rho, velocity, nonequilibrium, and floor limiting increments
     direct counters.
5. `test_step120_best_boundary_selection_contract.py`
   - limited-only pass can select limited;
   - convective-only pass can select convective;
   - both-fail stops at 48^3.
6. `test_step120_quasi2d_gate_contract.py`
   - comparison not improved keeps gate closed;
   - selected 96^3 failure keeps gate closed;
   - static row failure keeps gate closed;
   - failed non-selected candidate is not required to pass.
7. `test_step120_skipped_artifact_semantics_contract.py`
   - skipped row has `flux_balance_reported=false`;
   - no-record row cannot pass density, mass, or population validation.

## Final Classification

Only these classifications are allowed.

### `boundary_repair_success_go_to_quasi2d`

Requires:

- 48^3 best candidate improvement established;
- 96^3 best candidate 1000-step row passes;
- 96^3 static two-flap 1000-step row passes;
- direct limiter counters do not show excessive limiter dependence;
- no first failure;
- physical-nu strict row remains policy skip;
- no Fluent or FSI claim.

### `boundary_repair_partial_continue_lbm`

Use when:

- 48^3 improves but 96^3 or static flap still fails;
- or large rows are incomplete due resource or wall-clock limits.

### `boundary_repair_failed_revisit_lbm_solver`

Use when:

- limited and convective both fail to improve at 48^3;
- or stability relies on excessive limiter activation;
- or 96^3 legacy also reveals broader solver instability.

## Verification Requirements

Before committing and pushing:

- Run a red-to-green focused Step120 test slice.
- Run `py_compile` on touched runner and diagnostics files.
- Run focused Step119/Step120 regression tests.
- Run the full repository `pytest -q` with the trusted Taichi interpreter if
  feasible in the current turn.
- If full pytest is not feasible, report the exact reason and the strongest
  completed focused verification.
- Commit all relevant code, tests, reports, docs, and generated Step120
  artifacts.
- Push to `origin/main` and report the final commit hash and branch.
