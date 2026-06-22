# Step77 Minimal Post-Gate Canonical Driver 3-Step Rebaseline

Step77 extends the Step76 post-gate canonical driver rebaseline from one LBM
step to three LBM steps. It deliberately changes duration only.

## Scope

Step77 may:

- call canonical `FSIDriver3D.run()` for the required 32^3/three-step row
- write the four normal lightweight driver outputs
- write JSON, CSV, log, report, and manifest evidence
- confirm Step76 committed evidence remains green

Step77 may not:

- activate runtime geometry
- activate wall velocity
- activate real geometry
- activate squid proxy behavior
- use link-area transfer
- add 48^3 or 64^3 rows
- run optional rows
- write VTR or particle NPY outputs
- change solver formulas or tau semantics
- claim physical validation, grid convergence, real squid validation, or production readiness

## Required Row

```text
row_name = canonical_driver_moving_boundary_engineering_32_3step_rebaseline
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
```

Expected driver-run files:

```text
outputs/step77_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_rebaseline/driver_config.json
outputs/step77_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_rebaseline/geo_all_fluid_32.dat
outputs/step77_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_rebaseline/diagnostics_timeseries.csv
outputs/step77_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_rebaseline/diagnostics_timeseries.npz
```

## Interpretation

Passing Step77 means the canonical driver can complete the same post-gate
moving-boundary engineering baseline for three LBM steps while all advanced
activation features and heavy outputs remain closed. It does not authorize
runtime geometry, wall velocity, real geometry, squid proxy behavior, or
physical production claims.
