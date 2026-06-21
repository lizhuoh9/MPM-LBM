# Step 45 Controlled Runtime Geometry Projection Integration Smoke

Step 45 is controlled runtime geometry projection integration smoke.
Step 45 uses transient projection state only.
Step 45 does not persist projected state.
Step 45 does not persist displaced geometry.
Step 45 does not write displaced particles.
Step 45 does not update default driver geometry.
Step 45 does not persist LBM solid_phi updates.
Step 45 does not update dynamic_solid.
Step 45 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.

Step 45 moves one step beyond the Step 44 detached projection smoke by routing the accepted runtime displaced geometry copy into an isolated transient projection target. The result is a compact projection-integration diagnostic for selected phases and grid sizes, not a production geometry-update path.

The selected phases are `0.0`, `0.2`, `0.35`, `0.5`, and `1.0`. The projection grids are `32^3` and `48^3`. The tracked regions remain `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy`.

## Validation Surface

- `configs/step45_runtime_geometry_projection_integration.json` defines the transient projection-only integration contract.
- `src/runtime_geometry_projection_config.py` validates disabled mutation and persistence flags.
- `src/runtime_geometry_projection.py` builds runtime displaced-copy projection rows without writing dense geometry or touching persistent driver state.
- `src/runtime_geometry_projection_quality.py` checks row count, finite values, bounds, phase coverage, grid coverage, transient-only status, and no persistent state.
- `src/runtime_geometry_projection_consistency.py` compares original static projection rows, Step 45 runtime projection rows, phase closure, and accepted Step 44 projection-only rows.
- `src/runtime_geometry_projection_state_guard.py` checks hash stability and forbidden-output counters.
- `baseline_tests/run_step45_*.py` produces the committed Step 45 evidence artifacts.
- `tests/test_step45_runtime_geometry_projection_integration_contract.py` verifies the artifact contract.

## Evidence Summary

The runtime projection integration writes 10 rows: 2 grid sizes times 5 phases. Every row is finite, transient-only, and projection-passing. The minimum active-cell count is 443 and the minimum projected mass is 1.0.

The original-vs-runtime comparison confirms phase `0.0` and phase `1.0` return to the original projection while mid-cycle phases change occupancy or projected bbox diagnostics. The Step 44 projection alignment check confirms the Step 45 transient projection rows preserve the accepted Step 44 detached projection-only mass and solid-field summary.

The ultra-short smoke descriptor records one original static row and two phase-`0.35` runtime-copy rows. These rows are diagnostic descriptors only and keep persistent geometry mutation disabled.

## Explicit Boundary

Step 45 does not add default driver integration for moving geometry. It does not write a displaced geometry file, a particle-array artifact, a dense displacement field, or a VTR output. It does not alter LBM, MPM, projection, coupling, wall-velocity, or moving-boundary formulas.

Step 46 may combine transient projection with opt-in wall-velocity application in an ultra-short smoke, but the default Step 45 path remains static and disabled.
