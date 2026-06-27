# Reading Order

Read these files first for the current boundary-repair campaign state:

1. `docs/current/STATUS.md`
2. `docs/current/ACTIVE_CAMPAIGN.json`
3. `docs/current/VALIDATION_GATES.md`
4. `docs/campaigns/fluent_duct_flap/steps/133/goal.md`
5. `docs/campaigns/fluent_duct_flap/steps/133/report.md`
6. `docs/campaigns/fluent_duct_flap/steps/132/goal.md`
7. `docs/campaigns/fluent_duct_flap/steps/132/report.md`
8. `experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py`

Older Step102-Step126 documents remain useful history, but they are not the
current entry point for deciding whether the campaign may advance to selected
96^3. Step127 found that both old real 48^3 candidate boundaries failed hard
gates. Step128 added a repaired-boundary code surface and `repair48` phase.
Step129 ran both repaired 48^3 / 500-step candidates; both completed but failed
flow-development hard gates. Step130 added `flowrepair48` 250-step triage; both
flow-repair rows completed but failed promotion gates, so selected 96^3 remains
blocked. Step131 added `planeflux48` 250-step triage with a true
plane-integrated flux-error controller; both rows completed but failed promotion
gates. Step132 added `planeflux_sweep48` controller-authority triage; all six
real 48^3 / 250-step rows completed, stayed finite, and had no first-failure
event, but accepted row count remained zero. Step133 added
`planeflux_mass_damped48` slow density feedback and feedback-damping triage; all
six real 48^3 / 250-step rows completed, stayed finite, and had no
first-failure event, but accepted row count remained zero. No Step133 500-step
promotion or selected 96^3 run is justified, so selected 96^3 remains blocked.
