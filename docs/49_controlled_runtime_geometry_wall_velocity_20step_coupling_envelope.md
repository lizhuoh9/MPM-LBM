# Step 49 Controlled Runtime Geometry Wall Velocity 20-Step Coupling Envelope

Step 49 is controlled runtime geometry plus wall velocity 20-step coupling envelope.
Step 49 is opt-in and engineering-only.
Step 49 runs a 32^3 twenty-step envelope.
Step 49 does not run a full-cycle moving-geometry simulation.
Step 49 does not persist displaced geometry.
Step 49 does not persist projected state.
Step 49 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

Step 49 extends the accepted Step 48 ten-step envelope to a twenty-step diagnostic window. The phase sequence is `[0.0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.5]`. The grid remains `32^3`, the coupling mode remains `moving_boundary`, and the reaction transfer mode remains `engineering`.

## Validation Surface

- `configs/step49_runtime_geometry_wall_velocity_20step_envelope.json` defines the umbrella envelope contract.
- `configs/step49_original_static_32_20step.json` records the static twenty-step baseline row.
- `configs/step49_runtime_geometry_only_32_20step.json` records the runtime-geometry-only row.
- `configs/step49_wall_velocity_only_32_20step.json` records the wall-velocity-only row.
- `configs/step49_runtime_geometry_plus_wall_velocity_32_20step.json` records the combined row.
- `src/runtime_geometry_wall_velocity_20step_config.py` validates phase sequence, grid, step count, transfer mode, and disabled mutation flags.
- `src/runtime_geometry_wall_velocity_20step_envelope.py` builds the four-row by twenty-step diagnostic matrix.
- `src/runtime_geometry_wall_velocity_20step_diagnostics.py` checks quality, component effects, phase progression, early-refill transition behavior, density, force, bounce-back proxy diagnostics, and Step 48 prefix equality for shared phases.
- `src/runtime_geometry_wall_velocity_20step_state_guard.py` checks original geometry and region-mask hash stability plus forbidden-output counters.
- `baseline_tests/run_step49_*.py` generates the committed Step 49 evidence artifacts.
- `tests/test_step49_runtime_geometry_wall_velocity_20step_envelope_contract.py` verifies the artifact-backed contract.

## Four-Row Envelope

The matrix rows are:

- `original_static_32_20step`: runtime projection off, wall velocity off.
- `runtime_geometry_only_32_20step`: runtime projection on, wall velocity off.
- `wall_velocity_only_32_20step`: runtime projection off, wall velocity on.
- `runtime_geometry_plus_wall_velocity_32_20step`: runtime projection on, wall velocity on.

The generated envelope passes with `4` stable rows, `20` step records per row, minimum completed LBM steps `20`, and minimum total MPM substeps `100`. The runtime-geometry rows show a max active-cell delta of `205` relative to the static baseline. The wall-velocity rows apply velocity to `648` cells, with max applied velocity norm `0.007042082995889119`, below the `0.01` cap.

## Evidence Summary

The matrix summary reports:

- row count: `4`
- stable count: `4`
- step count per row: `20`
- global rho min: `0.9982680917004111`
- global rho max: `1.0017319082995888`
- global LBM max velocity: `0.007042082995889119`
- minimum active-cell count: `443`
- minimum bounce-back link count: `2658`
- NaN count: `0`
- Inf count: `0`
- matrix pass: `true`

The component-effect envelope reports `5` passing comparisons. The phase-progression diagnostic confirms the expected twenty-step phase sequence, nonzero projection response from phase `0.0` to phase `0.35`, finite wall-velocity response from phase `0.0` to phase `0.5`, and a combined row with both effects.

The early-refill transition diagnostic checks phases `[0.35, 0.375, 0.4, 0.425, 0.45, 0.5]`. It reports `4` passing transition rows, bounded runtime-geometry active-cell counts, positive wall-velocity application counts, velocity-cap compliance, NaN count `0`, and Inf count `0`.

The mass/force/bounce-back envelope reports `4` passing rows with finite correction and force proxy values. The global max bounce-back correction is `0.007042082995889119`, and the global max hydrodynamic-force proxy norm is `0.002050114988871742`.

Step 48 prefix comparison checks the shared phases `[0.0, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35]` against the accepted ten-step matrix. All four row pairs pass with zero projected-mass, active-cell, and applied-velocity deltas for those shared phases.

## Explicit Boundary

Step 49 keeps projected geometry and wall velocity application transient inside the diagnostic envelope. It does not write displaced particles, dense displacement fields, VTR files, or `geo_all_fluid_*.dat` artifacts. It does not update default driver, LBM, MPM, projection, or dynamic solid state. It does not alter solver, projection, coupling, wall-velocity, or moving-boundary equations.

The state guard records stable original-geometry and region-mask hashes. The artifact manifest records no large Step 49 files, no Step 49 VTR files, no particle NPY files, no raw candidate large files, no scan-data files, and no private absolute paths.

Step 50 can build on this only by adding another explicitly bounded diagnostic window or a separately reviewed contract. Step 49 itself remains a twenty-step engineering-only envelope.
