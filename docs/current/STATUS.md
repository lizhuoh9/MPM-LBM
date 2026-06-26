# Current Status

The active campaign is the Fluent duct/flap LBM open-boundary repair campaign.
The current artifact state is `awaiting_48_candidates` with final
classification `boundary_repair_partial_continue_lbm`.

Step126 ran real 48^3 LBM-only references. The legacy reference completed
500/500 steps and passed the flow-development gate. The old regularized
reference completed 500/500 steps as simulation-backed comparison evidence but
failed the flow-development gate. The campaign may now proceed to 48^3
candidates in a later step.

Step124 tightened the campaign decision contract before any larger real run:
terminal legacy reference failure now stops the 48 campaign, candidate and
selected-row acceptance require dimensionless flow-development gates, and the
summary phase must ignore stale rows that do not match the campaign manifest.

Step125 was the provenance-only patch. It separates the campaign base
commit from the current code commit in `ACTIVE_CAMPAIGN.json` and Step121
campaign manifests, and it records `code_commit_at_run` for Step120 row
artifacts.

Step126 does not claim 48^3 candidate success, selected 96^3 success, quasi-2D
validation, FSI validation, Fluent validation, or Figure 29.3 parity.
