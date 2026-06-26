# Current Status

The active campaign is the Fluent duct/flap LBM open-boundary repair campaign.
The current artifact state is `awaiting_48_references` with final
classification `boundary_repair_partial_continue_lbm`.

The committed smoke artifact is runner plumbing evidence only. It is not a
48^3 reference campaign, not a 96^3 selected-row campaign, not quasi-2D
validation, not FSI validation, not Fluent validation, and not Figure 29.3
parity evidence.

Step124 tightens the campaign decision contract before any larger real run:
terminal legacy reference failure now stops the 48 campaign, candidate and
selected-row acceptance require dimensionless flow-development gates, and the
summary phase must ignore stale rows that do not match the campaign manifest.
