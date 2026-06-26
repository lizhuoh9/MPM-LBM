# Step122 LBM Boundary Real Campaign Execution And Selection

Step122 hardens the Step120/Step121 real LBM boundary campaign path before any
larger selected-grid claim is allowed.

It remains LBM-only. It does not open quasi-2D, FSI, Fluent parity, or Figure
29.3 parity claims.

## Hard Gates

The selected-static phase now requires a completed selected `96^3` duct row in
the same output directory. The row must report:

- `requested_window_completed: true`
- `step120_validation_claimed: true`
- no first failure
- Step121 row-validation pass

If those conditions are missing, selected-static raises an error instead of
creating a static spec.

## Provenance

Step121 selection now stores selected-boundary provenance from the chosen 48^3
candidate:

- limiter enabled flag,
- density clamps,
- velocity cap,
- non-equilibrium cap,
- population floor,
- inlet velocity,
- outlet density,
- LBM viscosity value,
- viscosity and relaxation semantics,
- tau,
- source config hash.

Selected 96^3 duct/static specs inherit those values.

## Checkpoint And Failure Handling

Step120 checkpoints already wrote `.npz` `history_json`; Step122 adds restore
support for that history and merges it with row CSV history on resume.

The lightweight Taichi reduction now includes `mass_total`, allowing immediate
mass-drift failure checks before the next full NumPy diagnostic sample.

## Current Evidence

The committed artifact refresh is still a smoke row:

- output directory:
  `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/`
- phase: `smoke`
- row: `tiny_step121_real_runner_smoke`
- campaign state: `awaiting_48_references`
- final classification: `boundary_repair_partial_continue_lbm`
- quasi-2D allowed: `false`

No 48^3 or 96^3 physical success is claimed by the smoke artifact.

## Verification

The Step122 commit was checked with:

- Step122 hardening contracts: `6 passed`
- Step120/Step121/Step122 focused regression: `18 passed`
- syntax compilation for changed Python files: passed
- full pytest suite: `1296 passed, 48 warnings`
- Step121 smoke rerun: completed 3/3 steps
