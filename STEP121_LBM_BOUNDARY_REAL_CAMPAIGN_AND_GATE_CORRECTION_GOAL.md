# Step121 LBM Boundary Real Campaign And Gate Correction Goal

## Source Review

This Step121 goal is derived from the remote-main review of commit
`ef4a19c254383cf92397bd0353f29c6dab668287`.

Step120 is accepted as an infrastructure repair step:

- Placeholder resume rows are no longer treated as complete large real rows.
- Restart state now restores real LBM fields and checkpoint metadata.
- 96^3 diagnostics use cheaper Taichi-side reductions.
- Limiter counters come from real kernel counters.
- Skipped artifact semantics are explicit.

Step120 is not accepted as physical proof that the boundary-condition repair has
succeeded. Step121 must repair the remaining campaign, gate, checkpoint, and
artifact semantics before any quasi-2D, FSI, Fluent, or Figure 29.3-style claim.

## Primary Objective

Implement Step121 as a solver/campaign-control correction for the Step120 LBM
boundary repair workflow.

Step121 must make pending campaign rows distinguishable from failed campaign
rows, support selected 96^3 gate execution after a real 48^3 selection, stop
large rows promptly on lightweight physical failure signals, preserve checkpoint
diagnostic history across restarts, write actionable failure snapshots, and gate
the final status only on the selected evidence chain.

After implementation, Step121 must provide tests, run artifacts, and a report
that state exactly what was executed and what remains blocked.

## Non-Negotiable Scope Rules

- Do not claim quasi-2D readiness unless Step121 success gates are satisfied.
- Do not claim FSI readiness. Static two-flap rows are LBM-only geometry gates.
- Do not claim Fluent parity or Figure 29.3 parity from Step121.
- Do not treat skipped, placeholder, interrupted, or not-yet-run rows as failed
  physical evidence.
- Do not hide failed candidates by filtering them out of summaries.
- Do not aggregate limiter gates across unrelated tiny, reference, rejected, or
  diagnostic rows when deciding final Step121 success.
- Keep the large-real campaign opt-in and explicit. Tests must remain small and
  fast unless the user intentionally starts a large-real phase.

## Required Campaign States

Step121 must expose campaign state separately from final classification:

- `awaiting_48_references`: legacy and regularized 48^3 references are not both
  completed with simulation-backed evidence.
- `awaiting_48_candidates`: references are ready, but the limited and convective
  48^3 candidates are not both completed with simulation-backed evidence.
- `48_candidates_failed`: both real 48^3 candidates ran and both failed the hard
  candidate gates.
- `best_48_selected`: at least one real 48^3 candidate passed, and a best
  boundary has been selected.
- `awaiting_selected_96_duct`: a best 48^3 boundary has been selected, but its
  selected 96^3 duct-only gate has not completed.
- `awaiting_selected_96_static`: the selected 96^3 duct-only gate completed, but
  the selected 96^3 static two-flap gate has not completed.
- `complete`: selected 48^3, selected 96^3 duct-only, and selected 96^3 static
  two-flap evidence are complete and pass all Step121 gates.

## Required Final Classifications

- `boundary_repair_partial_continue_lbm`:
  - any required campaign row is not yet run,
  - a row is interrupted or wall-time limited,
  - references are incomplete,
  - a best 48^3 candidate is selected but selected 96^3 gates are incomplete,
  - selected 96^3 duct or static geometry fails after selection.
- `boundary_repair_failed_revisit_lbm_solver`:
  - only when both limited and convective 48^3 candidates were actually executed
    as real simulation-backed rows, and both failed hard candidate gates.
- `boundary_repair_success_go_to_quasi2d`:
  - only when references are complete,
  - one best 48^3 candidate improves or stabilizes the boundary evidence,
  - selected 96^3 duct-only passes,
  - selected 96^3 static two-flap passes,
  - selected-chain limiter counters are acceptable,
  - no selected-chain physical failure snapshot was produced,
  - physical-nu strict rows remain explicitly policy-skipped if applicable.

## P0 Implementation Repairs

### P0.1 Pending-Versus-Failed Campaign Semantics

The Step121 summary logic must treat unrun candidate rows as pending. If 48^3
limited and convective candidates are absent, skipped, placeholders, or
interrupted, the campaign state is pending and the final classification is
`boundary_repair_partial_continue_lbm`.

The final failure classification is allowed only when both real 48^3 candidates
have completed and both fail their hard gates.

### P0.2 Dynamic Selected 96^3 Specs

Step121 must be able to construct selected 96^3 execution specs from the selected
48^3 boundary semantics:

- `duct_only_96_limited_1000step_real`
- `duct_only_96_convective_1000step_real`
- `static_two_flap_96_limited_1000step_real`
- `static_two_flap_96_convective_1000step_real`

The CLI must expose phase-oriented execution:

- `--phase references48`
- `--phase candidates48`
- `--phase selected96`
- `--phase selected-static`
- `--best-selection-path <path>`

The selected 96^3 phases must refuse to run without an explicit best-selection
artifact.

### P0.3 Immediate Lightweight Failure Stop

`failure_check_interval` must not wait for full sampled outputs. A lightweight
failure detector must run at the configured interval and stop the row promptly
when physical or numerical failure is detected.

The lightweight detector must inspect at least:

- density minimum and maximum,
- maximum velocity,
- finite status for `f`, `F`, `rho`, and `v`,
- negative population fraction,
- mass total if available.

When a lightweight failure is detected, the runner must write a checkpoint,
write a failure snapshot, mark the row as failed/interrupted according to the
actual stop reason, and not continue to the next full sample interval.

### P0.4 Checkpoint History Continuity

Restarting from a checkpoint must preserve pre-checkpoint diagnostic history.
`records`, `stability_records`, and `combined_records` must be restored from a
checkpoint payload or loaded from existing CSV artifacts, de-duplicated by step,
and merged with newly produced records.

Trend checks after resume must use the full merged series, not only the records
generated after restart.

### P0.5 Atomic Checkpoint Write And Fallback

Checkpoint writes must be atomic:

- write to a temporary file,
- reopen and validate the temporary checkpoint,
- atomically replace the current checkpoint,
- keep the last two or three valid checkpoints,
- fall back to the newest valid previous checkpoint if the latest checkpoint is
  corrupted or incomplete.

### P0.6 Selection, Visibility, And Limiter Scope

Best-boundary selection must require completed reference evidence:

- legacy 48^3 reference complete and simulation-backed,
- regularized 48^3 reference complete and simulation-backed.

If references are not ready, report `campaign_state = awaiting_48_references`
and do not select a best candidate.

Candidate summaries must include all rows with `row_role == "candidate_48"`,
including rows rejected from validation. Failed candidates must remain visible
with rejection reasons.

Limiter gates for final Step121 success must evaluate only the selected evidence
chain:

- selected 48^3 candidate,
- selected 96^3 duct-only gate,
- selected 96^3 static two-flap gate.

## P1 Required 48^3 Reference Rows

Step121 must support real execution of:

- `duct_only_48_legacy_boundary_500step_reference_real`
- `duct_only_48_regularized_boundary_500step_reference_real`

These rows are reference evidence only. They are not candidate boundary repairs.

## P2 Required 48^3 Candidate Rows

Step121 must support real execution of:

- `duct_only_48_regularized_limited_boundary_500step_real`
- `duct_only_48_convective_outlet_boundary_500step_real`

Candidate hard gates must include physical/numerical stability, density bounds,
finite populations, mass drift, and limiter activity. The limited candidate must
report limiter activation and should not pass if limiter activation exceeds
`0.05`.

## P3 Best Boundary Selection Artifact

Step121 must write a best-selection artifact that includes:

- reference readiness status,
- every candidate row,
- each candidate's completion state,
- each candidate's pass/fail state,
- rejection reasons for failed or excluded candidates,
- selected boundary semantics,
- selected boundary parameters,
- selected metrics,
- selection reason,
- campaign state after selection.

## P4 Selected 96^3 Duct-Only Gate

Only after a best 48^3 candidate is selected, Step121 must run the matching
selected 96^3 duct-only row:

- `duct_only_96_<selected_slug>_1000step_real`

The selected row must use:

- `failure_check_interval = 5`,
- output interval `100`,
- checkpoint interval `100`.

If the selected 96^3 duct-only row fails, Step121 may run the legacy 96^3
duct-only reference for diagnosis, but that diagnostic row must not become the
selected-chain proof.

## P5 Selected 96^3 Static Two-Flap Gate

Only after the selected 96^3 duct-only row passes, Step121 must run the matching
selected static two-flap row:

- `static_two_flap_96_<selected_slug>_1000step_real`

This is still a static geometry LBM-only gate. It must not be described as
two-way FSI.

## P6 Required Tests

Add Step121 tests for:

1. Pending rows are classified as partial/pending, not failed.
2. Failure classification is emitted only when both real 48^3 candidates ran and
   both failed.
3. Best-boundary selection refuses to proceed until both references are complete
   and simulation-backed.
4. Failed or rejected candidate rows remain visible in the candidate summary.
5. Dynamic selected 96^3 specs are generated for both limited and convective
   selected boundaries.
6. Selected 96^3 phases reject missing best-selection artifacts.
7. Lightweight failure detection stops before the next full sample interval.
8. Checkpoint history survives restart and is de-duplicated by step.
9. Atomic checkpoint fallback loads the newest valid previous checkpoint when
   the latest checkpoint is corrupted.
10. Final limiter gates evaluate only the selected evidence chain.
11. Failure snapshots include field statistics and localized anomaly windows,
    while large raw arrays remain in ignored runtime storage.

## P7 Required Artifacts

Step121 must produce:

- `STEP121_LBM_BOUNDARY_REAL_CAMPAIGN_AND_GATE_CORRECTION_REPORT.md`
- `docs/121_lbm_boundary_real_campaign_and_gate_correction.md`
- an output directory under
  `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/`
- JSON/CSV artifacts for the executed Step121 phases,
- a best-selection JSON artifact when selection is possible,
- local failure-snapshot stats JSON when a row fails early,
- ignored runtime snapshot files for bulky raw field data.

## Verification Contract

Use the repository's trusted Taichi Python interpreter:

`D:\working\taichi\env\python.exe`

Required verification:

- run focused Step121 tests,
- run Step120 compatibility tests touched by the Step121 interfaces,
- run syntax/import checks for the Step121 runner,
- run any small default Step121 artifact generation that does not falsely claim
  large-real completion,
- execute explicit large-real phases only through the Step121 phase CLI and
  record whether each phase completed, failed, was interrupted, or remained
  pending.

## Push Approval Condition

After Step121 implementation and verification:

- commit code, tests, docs, and small committed artifacts,
- do not commit bulky ignored runtime snapshots,
- push `main` to GitHub,
- report the final commit hash, remote branch, verification commands, campaign
  state, and any remaining physics or execution blockers.
