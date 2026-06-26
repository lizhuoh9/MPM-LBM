# Step123 LBM Boundary 48 Real Campaign Execution And Decision

Step123 hardens the Step120/Step121 boundary-campaign decision path before the
real 48^3/96^3 campaign is allowed to become a physical readiness claim.

It remains LBM-only. It does not open quasi-2D, FSI, Fluent validation, or
Figure 29.3 parity claims.

## Decision Semantics

Step123 separates two concepts that were too tightly coupled before:

- terminal evidence: a row either completed the requested window or stopped on a
  simulation-backed physical failure;
- validation pass: a row satisfied the actual campaign gate.

This lets the campaign fail decisively when real candidate rows both terminate
with physical failures, while still keeping wall-time expiry, manual
interruption, placeholders, and non-simulation rows in an awaiting state.

## Provenance And Reuse

Step120 now records and uses two identities:

- `solver_state_hash` for numerical state;
- `run_manifest_hash` for run-control and audit settings.

Checkpoint restore validates `solver_state_hash`, not output/checkpoint cadence.
Same-name row reuse now goes through `step120_row_reusable_for_spec(row_dir,
spec)`, which rejects stale config/provenance and selected-source mismatches.

## Selected 96 Gate

Selected 96^3 duct acceptance now requires flow-development evidence in addition
to stability/window checks:

- flux balance is reported;
- tail outlet flux is non-zero;
- tail flux imbalance is below the selected threshold;
- no first-failure marker is present;
- the regular Step121 row-validation path passes.

The selected gate report exposes:

- `outlet_flux_tail_mean`;
- `outlet_to_inlet_flux_ratio_tail_mean`;
- `midplane_to_inlet_flux_ratio_tail_mean`;
- `flow_development_gate_pass`.

Missing flow-development fields fail the formal selected gate.

## Current Artifact Status

The refreshed artifact is still the tiny Step121 smoke row:

- `tiny_step121_real_runner_smoke`
- 5-cell tiny smoke grid
- 3/3 requested steps completed
- `campaign_state=awaiting_48_references`
- `final_classification=boundary_repair_partial_continue_lbm`
- `flow_development_gate_pass=false`

The smoke row is useful for runner plumbing, but it is not a real 48^3/96^3
campaign result.

## Verification Summary

Step123 focused contracts passed:

- Step123 contract tests: `12 passed`
- Step121/Step122 campaign gate regressions: `12 passed`
- Step120 row status regression: `3 passed`
- Step120 checkpoint restart regression: `1 passed`
- Step120 lightweight reduction regression: `1 passed`
- remaining Step120 focused regressions: `8 passed`
- changed Python compile check: passed
- Step121 tiny real smoke rerun: completed 3/3 steps

Full `pytest -q` was attempted but hit the 20-minute command timeout after
progressing past 71% with no failure output. Step123 therefore does not claim a
full-suite green run.

## Next Step

The next campaign step should run the real sequence in order:

1. 48^3 references.
2. 48^3 candidates.
3. selected 96^3 duct.
4. selected 96^3 static.

Selected 96^3 static remains blocked until the selected 96^3 duct artifact is
present, provenance-matched, and flow-developed.
