# Step76 Minimal Post-Gate Canonical Driver Rebaseline

Step76 runs the first and smallest post-gate canonical driver rebaseline allowed
by Step75. The run is intentionally narrow: one moving-boundary engineering row
at 32^3 for one LBM step.

## Scope

Step76 may:

- call canonical `FSIDriver3D.run()` for the required 32^3/one-step row
- write the four normal lightweight driver outputs
- write JSON, CSV, log, report, and manifest evidence
- confirm Step75 remains green

Step76 may not:

- activate runtime geometry
- activate wall velocity
- activate real geometry
- activate squid proxy behavior
- use link-area transfer
- add 48^3 or 64^3 rows
- run the optional 32^3/three-step row
- write VTR or particle NPY outputs
- change solver formulas or tau semantics
- claim physical validation, grid convergence, real squid validation, or production readiness

## Required Row

```text
row_name = canonical_driver_moving_boundary_engineering_32_1step_rebaseline
n_grid = 32
n_particles = 1024
n_lbm_steps = 1
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
```

## Interpretation

Passing Step76 means the canonical driver still completes the minimal
post-gate rebaseline row after the Step63-Step75 structural and evidence work.
It does not authorize advanced activation. The next possible extension is a
separate Step77 decision for the disabled 32^3/three-step rebaseline row.
