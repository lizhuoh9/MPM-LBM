# Current Status

The active campaign is the Fluent duct/flap LBM open-boundary repair campaign.
The current artifact state is `48_candidates_failed` with final classification
`boundary_repair_failed_revisit_lbm_solver`.

Step128 has added the code and contract surface for LBM open-boundary
formulation repair. It introduces two new repaired 48^3 candidate semantics,
`regularized_mass_balanced_pressure_outlet` and
`convective_mass_balanced_pressure_outlet`, plus a distinct Step121 `repair48`
phase. The old Step127 `candidates48` phase is unchanged.

Step128 has not yet produced real 48^3 / 500-step repaired-candidate acceptance
evidence. Selected 96^3 duct-only work remains blocked until a repaired 48^3
candidate passes the existing hard gates.

Step127 ran real 48^3 LBM-only candidates. The limited regularized candidate
completed 500/500 steps but failed the flow-development gates, essentially
reproducing the old regularized failed-baseline flux behavior. The convective
outlet candidate produced terminal real evidence at step 200 with
`first_failure_reason = mass_drift`, did not complete the requested window, and
also failed flow-development ratio/imbalance gates.

Step127 selected no best 48^3 boundary. Selected 96^3 duct-only work is not
allowed from the current artifacts. The next step should be boundary formulation
repair grounded in the Step127 failures.

Step126 ran real 48^3 LBM-only references. The legacy reference completed
500/500 steps and passed the flow-development gate. The old regularized
reference completed 500/500 steps as simulation-backed comparison evidence but
failed the flow-development gate.

Step124 tightened the campaign decision contract before any larger real run:
terminal legacy reference failure now stops the 48 campaign, candidate and
selected-row acceptance require dimensionless flow-development gates, and the
summary phase must ignore stale rows that do not match the campaign manifest.

Step125 was the provenance-only patch. It separates the campaign base
commit from the current code commit in `ACTIVE_CAMPAIGN.json` and Step121
campaign manifests, and it records `code_commit_at_run` for Step120 row
artifacts.

Step128 does not claim 48^3 repaired-candidate success, selected 96^3 success,
quasi-2D validation, FSI validation, Fluent validation, or Figure 29.3 parity.
