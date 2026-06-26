# Step123 LBM Boundary 48 Real Campaign Execution And Decision Goal

## Source Review

This goal implements the review attached for remote `main` commit
`c403622498dd8d10424160b7a1cfc61507da961d`, which accepted Step122's
boundary-campaign hardening but identified correctness gaps that must be fixed
before treating the 48^3/96^3 boundary campaign as a real decision artifact.

Step122's committed evidence remains bounded:

- `campaign_state=awaiting_48_references`
- `final_classification=boundary_repair_partial_continue_lbm`
- quasi-2D, Fluent/Figure 29.3 parity, and FSI claims are still false
- local tests passed in Step122, but GitHub Actions did not provide independent
  evidence
- current smoke evidence is not a replacement for a completed real 48^3/96^3
  campaign

## Non-Negotiable Scope

Step123 must repair campaign decision logic and add tests before any real
campaign result can be trusted. It must not fake a Fluent-like jet, must not
turn smoke artifacts into campaign evidence, and must not claim quasi-2D,
two-way FSI, Fluent parity, or Figure 29.3 equivalence unless a later artifact
actually supports those claims.

Solver behavior and campaign gates must stay in the Step120/Step121 campaign
logic and LBM core contracts. Case/report code may summarize evidence, but it
must not hide solver or decision fixes.

## P0.1 Early-Stop Candidate Decision Semantics

Problem: Step122 can leave a real campaign permanently in
`awaiting_48_candidates` when both candidate rows stopped early on simulation-
backed physical failure, because completion is currently tied too tightly to
`requested_window_completed=true`.

Required behavior:

- Introduce a clear distinction between:
  - real terminal evidence: a row has either completed the requested window or
    has a simulation-backed physical stop-on-failure artifact
  - real validation pass: a row completed or stopped only in a way that satisfies
    the validation gate
- Treat simulation-backed physical stop-on-failure rows as terminal evidence.
- Exclude wall-time expiry, manual interruption, placeholders, and non-simulation
  rows from terminal evidence.
- If both 48^3 candidate rows are terminal evidence and neither validates, the
  campaign must become:
  - `campaign_state=48_candidates_failed`
  - `final_classification=boundary_repair_failed_revisit_lbm_solver`
- If a row stopped because of wall-time or interruption, the campaign must remain
  awaiting runnable evidence instead of being marked failed.

Tests:

- Add a red contract test where two simulation-backed candidate rows stop early
  for physical failure and the campaign becomes failed.
- Add a negative test where a wall-time/interrupted row remains non-terminal.

## P0.2 Selected 96 Flow-Development Gate

Problem: The selected 96^3 gate can pass based on stability/window checks while
the duct flow is still physically undeveloped or flux-inconsistent.

Required behavior:

- The selected 96^3 duct pass must require:
  - `flux_balance_reported=true`
  - `abs(outlet_flux_tail_mean) > outlet_flux_min`
  - `flux_imbalance_rel_tail_mean < 0.1`
  - no first-failure marker
  - regular window and validation requirements already enforced by Step121
- The selected gate/report must expose:
  - `outlet_to_inlet_flux_ratio_tail_mean`
  - `midplane_to_inlet_flux_ratio_tail_mean`
  - `flow_development_gate_pass`
- Missing flow-development fields on selected 96^3 rows should fail the formal
  selected gate rather than silently passing.

Tests:

- Add a selected 96^3 gate test where stability fields pass but zero/invalid
  outlet flux blocks the selected gate.
- Add a passing selected gate fixture with explicit flux-development fields so
  the expected formal path remains covered.

## P0.3 Spec-Aware Artifact Reuse And Provenance Guard

Problem: Resume and selected-static paths can reuse an old same-name artifact
even when the artifact was produced under a different config hash or provenance.

Required behavior:

- Add a reusable-row predicate such as `step120_row_reusable_for_spec(row_dir,
  spec)` that validates artifact provenance against the current spec.
- The reusable predicate must compare the row's current solver/config identity
  with the requested spec.
- For selected rows, the predicate must also validate selected-source
  provenance fields and boundary semantics, including tau/relaxation-related
  semantics where represented in the artifact.
- Step120 resume must not reuse a terminal/completed row if the provenance does
  not match the current spec.
- Step121 selected-static guard and final selected-chain gate must use the same
  provenance validation instead of trusting same-name output directories.

Tests:

- Add a test proving a same-name row with mismatched config/provenance is not
  reusable.
- Add a matching-provenance positive test.
- Cover selected-source mismatch rejection.

## P0.4 Split Solver-State Hash From Run-Manifest Hash

Problem: The existing `_config_hash()` includes run-control fields such as
`output_interval`, `failure_check_interval`, checkpoint cadence, and snapshot
settings. Those fields change the manifest, not the numerical solver state, and
should not block checkpoint restore.

Required behavior:

- Add a solver-state hash containing only fields that affect numerical state:
  - grid and dimensions
  - viscosity/relaxation/tau
  - inlet/outlet settings
  - geometry and boundary semantics
  - limiter numeric parameters
  - force settings
  - timestep/physical mapping fields that alter numerical evolution
- Add a separate run-manifest hash containing audit/run-control fields.
- Checkpoint metadata must validate solver-state hash for restore.
- Run-manifest hash must be recorded for audit but not used to block restore.
- Preserve backward-compatible artifact fields where practical, but document
  their current meaning in report text.

Tests:

- Add a test showing specs that differ only by output/checkpoint cadence have the
  same solver-state hash but a different run-manifest hash.
- Add a checkpoint restore test proving changed output/checkpoint cadence does
  not reject a solver-compatible checkpoint.

## P0.5 Formal Selected-96 Provenance Must Fail Fast

Problem: `make_selected_96_specs()` still defaults missing provenance, which is
acceptable only for explicit legacy migration, not for a formal campaign.

Required behavior:

- Formal selected-96 spec creation must require complete selection provenance.
- Missing provenance should raise a clear error.
- Legacy/default provenance behavior may remain only behind an explicit
  migration/legacy flag and must not be the default campaign path.

Tests:

- Add a test that missing selected provenance raises by default.
- Add a test for the explicit legacy mode if retained.

## P0.6 Real Taichi Lightweight Mass Reduction Assertion

Problem: The lightweight mass-reduction path is relied on for early physical
failure detection, but Step122 did not directly assert that the real Taichi
implementation reports mass from the actual fluid density field.

Required behavior:

- Add a small real-Taichi test proving
  `get_lightweight_stability_stats()["mass_total"]` matches the sum of `rho` over
  fluid cells.
- Preferably add a runner-level test where a real tiny LBM row stops at a
  non-full-sample step due to mass drift. Any perturbation helper must still use
  the real Taichi LBM fields/reduction path, not a fake LBM object.

Tests:

- Direct real-Taichi mass reduction equality test.
- Runner-level early-stop test if feasible without excessive runtime.

## Implementation Plan

1. Add Step123 red tests covering P0.1 through P0.6.
2. Repair Step120 hash/checkpoint/resume/provenance logic.
3. Repair Step121 terminal-evidence, selected-96 gate, and selected-provenance
   logic.
4. Add required flow-development fields to row summaries and gate reports.
5. Run focused validation, then full repo validation if runtime permits.
6. Update Step123 report/docs with exact commands, pass/fail counts, artifacts,
   and remaining blocked claims.
7. Commit and push to GitHub only after the code and tests are green.

## Required Validation

Use the trusted local Taichi Python interpreter when available:

```powershell
D:\working\taichi\env\python.exe -m py_compile experiments\steps\step120_lbm_boundary_repair_large_real_execution.py experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py src\mpm_lbm\sim\lbm\fluid.py
D:\working\taichi\env\python.exe -m pytest -q tests\test_step120*.py tests\test_step121*.py tests\test_step122*.py tests\test_step123*.py
D:\working\taichi\env\python.exe -m pytest -q
git diff --check
```

If full validation cannot be run within the available machine budget, the final
report must state that explicitly and must not imply full campaign readiness.

## Deliverables

- Step123 contract tests.
- Step120/Step121 implementation changes.
- Step123 report documenting:
  - what changed
  - exact tests run and their results
  - whether any real campaign run was executed
  - what remains blocked
  - which previous Step122 assumptions were corrected
- Any generated smoke artifacts needed by the report, if rerun.
- Git commit and push to remote `main` after verification.

## Success Criteria

The Step123 work is complete only when:

- all P0 tests pass
- existing Step120/Step121/Step122 tests remain green
- checkpoint restore uses solver-state identity instead of run-control identity
- selected 96^3 gate cannot pass without flux-development evidence
- formal selected provenance fails fast when missing
- same-name stale artifacts cannot be silently reused
- reports clearly state that real 48^3/96^3 campaign execution remains separate
  unless it was actually completed in this step
- changes are committed and pushed to GitHub `main`
