# Step116 Regularized LBM Duct Flow Baseline

Step116 adds simulation-backed LBM-only baseline diagnostics for the Step115
`regularized_velocity_pressure` open-boundary path.

## What It Does

- Converts LBM fields to NumPy snapshots for post-processing diagnostics.
- Reports fluid-only mass, density, x-plane flux, mean velocity, centerline
  velocity, observed Mach proxy, and outlet reflection proxies.
- Runs bounded duct-only and static two-flap fluid rows through the LBM solver.
- Writes small CSV/JSON artifacts under
  `outputs/step116_regularized_lbm_duct_flow_baseline/`.
- Keeps legacy `equilibrium_all_population_reset` as the default boundary.
- Keeps `regularized_velocity_pressure` opt-in.

## Scope Boundary

The committed artifacts are bounded probes: `executed_nx=8`,
`steps_completed=5`, and `requested_window_completed=false` for the preserved
48/96-named rows. They are useful as a runner/diagnostics baseline, but they
are not the long-window 48^3/96^3 validation requested by the review.

Step116 is not Fluent validation. It does not implement Fluent's pressure
solver, official dynamic mesh, small-strain solid, conservative traction
transfer, quasi-2D flow, D2Q9 flow, or full FSI.

## Reading The Artifacts

- `run_matrix_summary.json` tells which rows ran, which requested window they
  correspond to, and whether the requested long window was actually completed.
- `finite_stability_report.json` records finite, density, mass-drift, flux, and
  tau gates for each row.
- `fluid_diagnostics_timeseries.csv` records the per-step diagnostics.
- Static two-flap rows also write throat speed and recirculation proxy reports.

Do not use these bounded rows as Figure 29.3 evidence. The next credible step
is an explicit long-window pass using the same runner or a more optimized LBM
diagnostic path.
