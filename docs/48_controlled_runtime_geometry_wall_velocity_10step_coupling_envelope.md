# Step 48 Controlled Runtime Geometry Wall Velocity 10-Step Coupling Envelope

Step 48 is controlled runtime geometry plus wall velocity 10-step coupling envelope.
Step 48 is opt-in and engineering-only.
Step 48 runs a 32^3 ten-step envelope.
Step 48 does not run a full-cycle moving-geometry simulation.
Step 48 does not persist displaced geometry.
Step 48 does not persist projected state.
Step 48 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

Step 48 extends the accepted Step 47 five-step envelope to a ten-step diagnostic window. The phase sequence is `[0.0, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35]`. The grid remains `32^3`, the coupling mode remains `moving_boundary`, and the reaction transfer mode remains `engineering`.

## Validation Surface

- `configs/step48_runtime_geometry_wall_velocity_10step_envelope.json` defines the umbrella envelope contract.
- `configs/step48_original_static_32_10step.json` records the static ten-step baseline row.
- `configs/step48_runtime_geometry_only_32_10step.json` records the runtime-geometry-only row.
- `configs/step48_wall_velocity_only_32_10step.json` records the wall-velocity-only row.
- `configs/step48_runtime_geometry_plus_wall_velocity_32_10step.json` records the combined row.
- `src/runtime_geometry_wall_velocity_10step_config.py` validates phase sequence, grid, step count, transfer mode, and disabled mutation flags.
- `src/runtime_geometry_wall_velocity_10step_envelope.py` builds the four-row by ten-step diagnostic matrix.
- `src/runtime_geometry_wall_velocity_10step_diagnostics.py` checks quality, component effects, phase progression, density, force, bounce-back proxy diagnostics, and Step 47 prefix equality for shared phases.
- `src/runtime_geometry_wall_velocity_10step_state_guard.py` checks original geometry and region-mask hash stability plus forbidden-output counters.
- `baseline_tests/run_step48_*.py` generates the committed Step 48 evidence artifacts.
- `tests/test_step48_runtime_geometry_wall_velocity_10step_envelope_contract.py` verifies the artifact-backed contract.

## Four-Row Envelope

The matrix rows are:

- `original_static_32_10step`: runtime projection off, wall velocity off.
- `runtime_geometry_only_32_10step`: runtime projection on, wall velocity off.
- `wall_velocity_only_32_10step`: runtime projection off, wall velocity on.
- `runtime_geometry_plus_wall_velocity_32_10step`: runtime projection on, wall velocity on.

The generated envelope passes with `4` stable rows, `10` step records per row, minimum completed LBM steps `10`, and minimum total MPM substeps `50`. The runtime-geometry rows show a max active-cell delta of `205` relative to the static baseline. The wall-velocity rows apply velocity to `648` cells, with max applied velocity norm `0.007042082995889119`, below the `0.01` cap.

## Evidence Summary

The matrix summary reports:

- row count: `4`
- stable count: `4`
- step count per row: `10`
- global rho min: `0.9982710917004111`
- global rho max: `1.0017289082995888`
- global LBM max velocity: `0.007042082995889119`
- minimum active-cell count: `443`
- minimum bounce-back link count: `2658`
- NaN count: `0`
- Inf count: `0`
- matrix pass: `true`

The component-effect envelope reports `5` passing comparisons. The phase-progression diagnostic confirms the expected ten-step phase sequence, nonzero projection response from phase `0.0` to phase `0.35`, finite wall-velocity response, and a combined row with both effects. The mass/force/bounce-back envelope reports `4` passing rows with finite correction and force proxy values.

Step 47 prefix comparison checks the shared phases `[0.0, 0.05, 0.1, 0.2, 0.35]` against the accepted five-step matrix. All four row pairs pass with zero projected-mass, active-cell, and applied-velocity deltas for those shared phases.

## Explicit Boundary

Step 48 keeps projected geometry and wall velocity application transient inside the diagnostic envelope. It does not write displaced particles, dense displacement fields, VTR files, or `geo_all_fluid_*.dat` artifacts. It does not update default driver, LBM, MPM, projection, or dynamic solid state. It does not alter solver, projection, coupling, wall-velocity, or moving-boundary equations.

The state guard records stable original-geometry and region-mask hashes. The artifact manifest records no large Step 48 files, no Step 48 VTR files, no particle NPY files, no raw candidate large files, no scan-data files, and no private absolute paths.

Step 49 can build on this only by adding another explicitly bounded diagnostic window. Step 48 itself remains a ten-step engineering-only envelope.
