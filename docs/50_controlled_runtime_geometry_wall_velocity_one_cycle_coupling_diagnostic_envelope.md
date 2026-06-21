# Step 50 Controlled Runtime Geometry Wall Velocity One-Cycle Coupling Diagnostic Envelope

Step 50 is controlled runtime geometry plus wall velocity one-cycle coupling diagnostic envelope.
Step 50 is opt-in and engineering-only.
Step 50 runs a 32^3 one-cycle diagnostic envelope.
Step 50 remains non-persistent.
Step 50 does not implement a production moving-geometry solver.
Step 50 does not validate real jet propulsion.
Step 50 does not implement squid swimming.
Step 50 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

Step 50 extends the accepted Step 49 twenty-step envelope to a complete prescribed-cycle diagnostic window at `32^3`. The runner phase sequence has forty entries from `0.0` through `0.975`; phase `1.0` is used only as a diagnostic closure endpoint. The coupling mode remains `moving_boundary`, and the reaction transfer mode remains `engineering`.

## Validation Surface

- `configs/step50_runtime_geometry_wall_velocity_one_cycle_envelope.json` defines the umbrella one-cycle diagnostic contract.
- `configs/step50_original_static_32_40step.json` records the static forty-step baseline row.
- `configs/step50_runtime_geometry_only_32_40step.json` records the runtime-geometry-only row.
- `configs/step50_wall_velocity_only_32_40step.json` records the wall-velocity-only row.
- `configs/step50_runtime_geometry_plus_wall_velocity_32_40step.json` records the combined row.
- `src/runtime_geometry_wall_velocity_one_cycle_config.py` validates phase sequence, closure phase, grid, step count, transfer mode, and disabled mutation flags.
- `src/runtime_geometry_wall_velocity_one_cycle_envelope.py` builds the four-row by forty-step diagnostic matrix and the phase-`1.0` closure rows.
- `src/runtime_geometry_wall_velocity_one_cycle_diagnostics.py` checks quality, component effects, phase progression, contraction/refill segments, closure, mass/force/bounce-back proxies, and Step 49 prefix equality.
- `src/runtime_geometry_wall_velocity_one_cycle_state_guard.py` checks original geometry and region-mask hash stability plus forbidden-output counters.
- `baseline_tests/run_step50_*.py` generates the committed Step 50 evidence artifacts.
- `tests/test_step50_runtime_geometry_wall_velocity_one_cycle_envelope_contract.py` verifies the artifact-backed contract.

## Four-Row Envelope

The matrix rows are:

- `original_static_32_40step`: runtime projection off, wall velocity off.
- `runtime_geometry_only_32_40step`: runtime projection on, wall velocity off.
- `wall_velocity_only_32_40step`: runtime projection off, wall velocity on.
- `runtime_geometry_plus_wall_velocity_32_40step`: runtime projection on, wall velocity on.

The generated envelope passes with `4` stable rows, `40` step records per row, minimum completed LBM steps `40`, and minimum total MPM substeps `200`. The runtime-geometry rows show a max active-cell delta of `205` relative to the static baseline. The wall-velocity rows apply velocity to `648` cells, with max applied velocity norm `0.007042082995889119`, below the `0.01` cap.

## Evidence Summary

The matrix summary reports:

- row count: `4`
- stable count: `4`
- step count per row: `40`
- global rho min: `0.9982680917004111`
- global rho max: `1.0017319082995888`
- global LBM max velocity: `0.007042082995889119`
- minimum active-cell count: `443`
- minimum bounce-back link count: `2658`
- NaN count: `0`
- Inf count: `0`
- matrix pass: `true`

The component-effect envelope reports `5` passing comparisons. The phase-progression diagnostic confirms the forty-step phase sequence, nonzero projection response from phase `0.0` to phase `0.35`, and finite refill response through phase `0.975`.

The contraction/refill segment diagnostic reports `15` contraction phases and `25` refill phases. Both segments pass with bounded runtime-geometry active-cell counts, positive wall-velocity application counts for wall-velocity rows, velocity-cap compliance, NaN count `0`, and Inf count `0`.

The cycle-closure diagnostic compares phase `0.0` against diagnostic endpoint phase `1.0`. Projection mass and active-cell counts close exactly in the committed diagnostic rows. The wall-velocity endpoint residual is bounded by the documented tolerance `0.0005`; the observed max endpoint delta is `0.00035490392512819833`. This closure check is a diagnostic endpoint check, not physical propulsion validation.

Step 49 prefix comparison checks the shared phases `[0.0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.5]` against the accepted Step 49 matrix. All four row pairs pass with zero projected-mass, active-cell, and applied-velocity deltas for those shared phases.

## Explicit Boundary

Step 50 keeps projected geometry and wall velocity application transient inside the diagnostic envelope. It does not write displaced particles, dense displacement fields, VTR files, or `geo_all_fluid_*.dat` artifacts. It does not update default driver, LBM, MPM, projection, or dynamic solid state. It does not alter solver, projection, coupling, wall-velocity, or moving-boundary equations.

The state guard records stable original-geometry and region-mask hashes. The artifact manifest records no large Step 50 files, no Step 50 VTR files, no particle NPY files, no raw candidate large files, no scan-data files, and no private absolute paths.

Step 51 can build on this only by adding another explicitly bounded comparison surface. Step 50 itself remains a one-cycle engineering-only diagnostic envelope.
