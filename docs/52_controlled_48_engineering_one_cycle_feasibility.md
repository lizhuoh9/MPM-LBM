# Step 52 Controlled 48 Engineering One-Cycle Feasibility

Step 52 is a controlled 48^3 engineering one-cycle diagnostic feasibility probe.
Step 52 runs exactly two engineering rows: static and runtime geometry plus wall velocity.
Step 52 remains diagnostic-only and non-persistent.
Step 52 does not validate real jet propulsion.
Step 52 does not implement squid swimming.
Step 52 does not change moving bounce-back formulas.
Step 52 is not grid convergence validation.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

## Scope

This step extends the accepted Step 51 engineering combined row from 32^3 to
48^3 while holding the transfer mode, cycle count, and row matrix fixed. It
uses only `engineering` transfer, only one prescribed forty-step diagnostic
cycle, and only two rows:

```text
engineering_static_48_40step
engineering_runtime_geometry_plus_wall_velocity_48_40step
```

Both rows use `n_lbm_steps = 40`, `mpm_substeps_per_lbm_step = 5`,
`cycle_period_steps = 40`, `closure_phase = 1.0`, `coupling_mode =
moving_boundary`, and zero target velocity. The runner records compact
diagnostic summaries only.

## 48 Vs Step 51 Boundary

The 48^3 comparison is diagnostic scaling only. The checked artifact records
that projected active-cell count did not grow relative to the Step 51 32^3
engineering combined row, while applied wall-cell support did grow. That result
is reported directly and is not converted into a grid-convergence or physical
claim.

## Artifacts

Step 52 writes small CSV, JSON, NPZ, and log artifacts under `outputs/step52_*`
and `logs/step52_*`. It does not write VTR, particle NPY, displaced-particle,
dense-displacement, scan-data, raw geometry, or `geo_all_fluid_*.dat` outputs.

## Decision Boundary

Passing Step 52 means the 48^3 engineering-only one-cycle diagnostic envelope
is finite, bounded, non-persistent, and small enough to keep in the repository.
It does not activate a production moving-geometry solver, free-body motion,
trajectory integration, real squid swimming, or real jet analysis.
