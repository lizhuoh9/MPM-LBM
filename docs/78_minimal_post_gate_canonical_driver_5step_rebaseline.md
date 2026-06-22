# Step78 Minimal Post-Gate Canonical Driver 5-Step Rebaseline

Step78 extends the Step77 post-gate canonical driver rebaseline from three LBM
steps to five LBM steps. It deliberately changes duration only.

## Scope

Step78 may:

- call canonical `FSIDriver3D.run()` for the required 32^3/five-step row
- write the four normal lightweight driver outputs
- write JSON, CSV, log, report, and manifest evidence
- confirm Step77 committed evidence remains green

Step78 may not:

- activate runtime geometry
- activate wall velocity
- activate real geometry
- activate squid proxy behavior
- use link-area transfer
- add 48^3 or 64^3 rows
- add a 10-step baseline
- run optional rows
- write VTR or particle NPY outputs
- change solver formulas or tau semantics
- claim physical validation, grid convergence, real squid validation, or production readiness

## Required Row

```text
row_name = canonical_driver_moving_boundary_engineering_32_5step_rebaseline
n_grid = 32
n_particles = 1024
n_lbm_steps = 5
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
```

Expected driver-run files:

```text
outputs/step78_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_rebaseline/driver_config.json
outputs/step78_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_rebaseline/geo_all_fluid_32.dat
outputs/step78_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_rebaseline/diagnostics_timeseries.csv
outputs/step78_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_rebaseline/diagnostics_timeseries.npz
```

## Interpretation

Passing Step78 means the canonical driver can complete the same post-gate
moving-boundary engineering baseline for five LBM steps while all advanced
activation features and heavy outputs remain closed. It does not authorize
runtime geometry, wall velocity, real geometry, squid proxy behavior, or
physical production claims.

After Step78, the next work should not be a 10-step box baseline. The next
phase should start single-feature activation planning with runtime geometry
diagnostic-only plan and guard work.
