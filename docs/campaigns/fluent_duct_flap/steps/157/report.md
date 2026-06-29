# Step157 Official Subcycled Flow Development Repair

Step157 diagnosed the Step155/Step156 flow-development failure as a
time-scale/subcycling mismatch candidate. Step155 used one LBM step per
official FSI step, while the Step154/Step155 dimensional velocity mapping
requires 120 LBM substeps per 0.0005 s official FSI step on the 48^3 grid.

Step157 ran the official tutorial proxy case with
fsi_exchange_mode = lbm_subcycled_per_fsi_step,
lbm_substeps_per_fsi_step = 120,
lbm_dt_phys_override_s = 4.166666666666667e-6 s,
for 50 official steps and 6000 total LBM substeps.

Step157 did not run Fluent, did not load or fabricate official monitor data,
did not run Step150, did not run selected96, and does not make a validation
claim.

Subcycling reached a density instability before the flow-development tail window, so the raw tail flux ratios are not valid improvement evidence. The next step must diagnose open-boundary behavior, outlet propagation, or geometry/mask mismatch before re-evaluating flow development.

The flow-development comparison against Step156 is recorded in:
`outputs/step157_official_subcycled_flow_development_repair/flow_development_comparison_report.json`.

## Current Comparison

- Step157 flow gate pass: `False`
- Outlet ratio improved: `False`
- Flux imbalance improved: `False`
- Flow metrics valid for gate: `False`
- Flow metrics invalid reason: `density_gate_failed_before_tail_window`
- First density gate failure step: `9`
- Validation claim allowed: `False`
