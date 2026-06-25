# Step115 LBM Open Boundary Repair

Step115 adds the first opt-in LBM open-boundary repair after Step114. The goal
is to stop using a full-population equilibrium overwrite as the only duct
inlet/outlet path when preparing Fluent-inspired fluid baselines.

## What Changed

- Legacy mode remains `equilibrium_all_population_reset`.
- New opt-in mode is `regularized_velocity_pressure`.
- The new mode is scoped to D3Q19 x-min velocity inlet and x-max pressure
  outlet style duct cases.
- Unknown incoming populations are reconstructed from equilibrium plus
  adjacent-cell non-equilibrium content.
- Known streamed populations are not overwritten.
- Driver reports now state whether unknown-population reconstruction or
  all-population reset was used.

## Tau Feasibility

Physical viscosity mapping now reports tau margin and Reynolds-number
diagnostics. Report-only mode records the risk without rejecting construction.
Strict mode rejects physical mappings whose `tau - 0.5` is below
`lbm_min_tau_margin`.

The official-like air mapping at 96^3 produces `tau=0.5000864`, so Step115
marks direct physical-Re simulation feasibility as false under the current
margin. This is a numerical-stability guard, not a Fluent validation result.

## Scope Boundary

Step115 is not Fluent validation. It does not implement Fluent's pressure-based
solver, small-strain linear elasticity, conservative wall traction transfer,
D2Q9 planar flow, official mesh import, official dynamic mesh, or Figure 29.3
parity. It only makes the current MPM-LBM prototype more explicit and more
testable before later FSI work.
