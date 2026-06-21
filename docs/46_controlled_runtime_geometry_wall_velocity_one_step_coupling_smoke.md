# Step 46 Controlled Runtime Geometry Wall Velocity One-Step Coupling Smoke

Step 46 is controlled runtime geometry plus wall velocity one-step coupling smoke.
Step 46 is opt-in and ultra-short.
Step 46 combines transient runtime geometry projection with solid_vel wall velocity application.
Step 46 does not persist displaced geometry.
Step 46 does not persist projected state.
Step 46 does not run a full-cycle moving-geometry simulation.
Step 46 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

Step 46 is a four-row `32^3`, phase-`0.35`, one-step diagnostic matrix. It combines the accepted Step 45 transient runtime projection path with the accepted opt-in wall-velocity application path, while keeping all persistent geometry, solver-state, dense-field, particle, and VTR writes disabled.

## Validation Surface

- `configs/step46_runtime_geometry_wall_velocity_coupling_smoke.json` defines the umbrella coupling-smoke contract.
- `configs/step46_original_static_32_1step.json` records the static one-step baseline row.
- `configs/step46_runtime_geometry_only_32_phase035_1step.json` records the runtime-geometry-only row.
- `configs/step46_wall_velocity_only_32_phase035_1step.json` records the wall-velocity-only row.
- `configs/step46_runtime_geometry_plus_wall_velocity_32_phase035_1step.json` records the combined row.
- `src/runtime_geometry_wall_velocity_coupling_config.py` validates explicit mode, grid, phase, step count, and disabled mutation flags.
- `src/runtime_geometry_wall_velocity_coupling.py` builds the compact four-row diagnostic matrix.
- `src/runtime_geometry_wall_velocity_diagnostics.py` checks quality, component deltas, density, force, and bounce-back proxy diagnostics.
- `src/runtime_geometry_wall_velocity_state_guard.py` checks original geometry and region-mask hash stability plus forbidden-output counters.
- `baseline_tests/run_step46_*.py` generates committed Step 46 evidence artifacts and OK logs.
- `tests/test_step46_runtime_geometry_wall_velocity_coupling_smoke_contract.py` verifies the artifact-backed contract.

## Four-Row Matrix

The matrix rows are:

- `original_static_32_1step`: runtime projection off, wall velocity off.
- `runtime_geometry_only_32_phase035_1step`: runtime projection on, wall velocity off.
- `wall_velocity_only_32_phase035_1step`: runtime projection off, wall velocity on.
- `runtime_geometry_plus_wall_velocity_32_phase035_1step`: runtime projection on, wall velocity on.

The generated matrix passes with `4` stable rows. The phase is `0.35`, the grid is `32^3`, completed LBM steps are `1`, and total MPM substeps are `1` per row. The runtime-geometry rows show an active-cell delta of `205` relative to the static baseline. The wall-velocity rows apply velocity to `648` cells with max applied velocity norm `0.0001774519625640706`, below the `0.01` cap.

## Evidence Summary

The matrix summary reports:

- row count: `4`
- stable count: `4`
- global rho min: `0.9989617548037436`
- global rho max: `1.0010382451962565`
- global LBM max velocity: `0.0001774519625640706`
- minimum bounce-back link count: `2658`
- NaN count: `0`
- Inf count: `0`
- matrix pass: `true`

The component-effect comparison reports `5` passing comparisons. The quality runner reports `quality_pass=true`, including row-count, stability, projection, wall-velocity, combined-row, diagnostic-only, and no-persistent-state checks. The mass/force/bounce-back diagnostic reports `4` passing rows with finite force and correction values.

## Explicit Boundary

Step 46 keeps projected geometry and wall velocity application transient inside the diagnostic matrix. It does not write displaced particles, dense displacement fields, VTR files, or `geo_all_fluid_*.dat` artifacts. It does not update default driver, LBM, MPM, projection, or dynamic solid state. It does not alter solver, projection, coupling, wall-velocity, or moving-boundary equations.

The state guard records stable original-geometry and region-mask hashes. The artifact manifest records Step 46 total size under `0.39` MB, no large Step 46 files, no Step 46 VTR files, no particle NPY files, no raw candidate large files, no scan-data files, and no private absolute paths.

Step 47 can build on this by adding another explicitly bounded diagnostic. Step 46 itself remains a one-step coupling smoke only.
