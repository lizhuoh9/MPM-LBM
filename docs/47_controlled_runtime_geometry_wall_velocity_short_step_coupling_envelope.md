# Step 47 Controlled Runtime Geometry Wall Velocity Short-Step Coupling Envelope

Step 47 is controlled runtime geometry plus wall velocity short-step coupling envelope.
Step 47 is opt-in and engineering-only.
Step 47 runs a 32^3 five-step envelope.
Step 47 does not run a full-cycle moving-geometry simulation.
Step 47 does not persist displaced geometry.
Step 47 does not persist projected state.
Step 47 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

Step 47 extends the accepted Step 46 one-step coupling smoke to a compact five-step diagnostic window. The phase sequence is `[0.0, 0.05, 0.1, 0.2, 0.35]`. The grid remains `32^3`, the coupling mode remains `moving_boundary`, and the reaction transfer mode remains `engineering`.

## Validation Surface

- `configs/step47_runtime_geometry_wall_velocity_short_step_envelope.json` defines the umbrella envelope contract.
- `configs/step47_original_static_32_5step.json` records the static five-step baseline row.
- `configs/step47_runtime_geometry_only_32_5step.json` records the runtime-geometry-only row.
- `configs/step47_wall_velocity_only_32_5step.json` records the wall-velocity-only row.
- `configs/step47_runtime_geometry_plus_wall_velocity_32_5step.json` records the combined row.
- `src/runtime_geometry_wall_velocity_envelope_config.py` validates phase sequence, grid, step count, transfer mode, and disabled mutation flags.
- `src/runtime_geometry_wall_velocity_envelope.py` builds the four-row by five-step diagnostic matrix.
- `src/runtime_geometry_wall_velocity_envelope_diagnostics.py` checks quality, component effects, phase progression, density, force, and bounce-back proxy diagnostics.
- `src/runtime_geometry_wall_velocity_envelope_state_guard.py` checks original geometry and region-mask hash stability plus forbidden-output counters.
- `baseline_tests/run_step47_*.py` generates the committed Step 47 evidence artifacts.
- `tests/test_step47_runtime_geometry_wall_velocity_short_step_envelope_contract.py` verifies the artifact-backed contract.

## Four-Row Envelope

The matrix rows are:

- `original_static_32_5step`: runtime projection off, wall velocity off.
- `runtime_geometry_only_32_5step`: runtime projection on, wall velocity off.
- `wall_velocity_only_32_5step`: runtime projection off, wall velocity on.
- `runtime_geometry_plus_wall_velocity_32_5step`: runtime projection on, wall velocity on.

The generated envelope passes with `4` stable rows, `5` step records per row, minimum completed LBM steps `5`, and minimum total MPM substeps `25`. The runtime-geometry rows show a max active-cell delta of `205` relative to the static baseline. The wall-velocity rows apply velocity to `648` cells, with max applied velocity norm `0.007042082995889119`, below the `0.01` cap.

## Evidence Summary

The matrix summary reports:

- row count: `4`
- stable count: `4`
- step count per row: `5`
- global rho min: `0.9982921917004111`
- global rho max: `1.001707808299589`
- global LBM max velocity: `0.007042082995889119`
- minimum active-cell count: `443`
- minimum bounce-back link count: `2658`
- NaN count: `0`
- Inf count: `0`
- matrix pass: `true`

The component-effect envelope reports `5` passing comparisons. The phase-progression diagnostic confirms the expected phase sequence, nonzero projection response from phase `0.0` to phase `0.35`, finite wall-velocity response, and a combined row with both effects. The mass/force/bounce-back envelope reports `4` passing rows with finite correction and force proxy values.

## Explicit Boundary

Step 47 keeps projected geometry and wall velocity application transient inside the diagnostic envelope. It does not write displaced particles, dense displacement fields, VTR files, or `geo_all_fluid_*.dat` artifacts. It does not update default driver, LBM, MPM, projection, or dynamic solid state. It does not alter solver, projection, coupling, wall-velocity, or moving-boundary equations.

The state guard records stable original-geometry and region-mask hashes. The artifact manifest records Step 47 total size under `0.50` MB after final verification logs, no large Step 47 files, no Step 47 VTR files, no particle NPY files, no raw candidate large files, no scan-data files, and no private absolute paths.

Step 48 can build on this by adding another explicitly bounded diagnostic window. Step 47 itself remains a five-step engineering-only envelope.
