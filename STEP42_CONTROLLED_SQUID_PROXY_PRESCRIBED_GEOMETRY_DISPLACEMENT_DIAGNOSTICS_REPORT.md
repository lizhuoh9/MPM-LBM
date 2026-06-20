# Step 42 Controlled Squid Proxy Prescribed Geometry Displacement Diagnostics Report

## 1. Scope

Step 42 is controlled squid proxy prescribed geometry displacement diagnostics.
Step 42 derives displacement diagnostics only.
Step 42 does not update driver geometry.
Step 42 does not displace MPM particles in FSIDriver3D.
Step 42 does not update LBM solid_phi.
Step 42 does not update dynamic_solid.
Step 42 does not change moving bounce-back formulas.
Step 42 remains diagnostic-only.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

## 2. Goal File

The detailed implementation goal is recorded in `STEP42_CONTROLLED_SQUID_PROXY_PRESCRIBED_GEOMETRY_DISPLACEMENT_DIAGNOSTICS_GOAL.md`.

## 3. Inputs

Step 42 uses the Step 30 squid proxy geometry and region masks, the Step 32 prescribed cycle schedule, and the Step 33 tracked-region motion mapping config.

## 4. Configs

- `configs/step42_squid_proxy_geometry_displacement.json`
- `configs/step42_squid_proxy_displacement_sampling.json`

Both configs keep `apply_to_driver`, `apply_to_lbm`, `apply_to_mpm`, `apply_to_projection`, `update_dynamic_solid`, and `driver_integration_enabled` set to `false`.

## 5. Source Modules

- `src/geometry_displacement_config.py`
- `src/geometry_displacement_field.py`
- `src/geometry_displacement_quality.py`
- `src/geometry_displacement_consistency.py`
- `src/geometry_displacement_grid_diagnostics.py`

## 6. Baseline Runners

- `baseline_tests/run_step42_displacement_config_validation.py`
- `baseline_tests/run_step42_generate_geometry_displacement.py`
- `baseline_tests/run_step42_displacement_quality.py`
- `baseline_tests/run_step42_displacement_repeatability.py`
- `baseline_tests/run_step42_schedule_displacement_consistency.py`
- `baseline_tests/run_step42_motion_displacement_consistency.py`
- `baseline_tests/run_step42_grid_displacement_diagnostics.py`
- `baseline_tests/run_step42_cycle_closure_diagnostics.py`
- `baseline_tests/run_step42_no_driver_update_guard.py`
- `baseline_tests/run_step42_step41_regression_guard.py`
- `baseline_tests/run_step42_artifact_manifest.py`

## 7. Displacement Construction

The mantle proxy uses radial displacement from the mantle center under the Step 32 mantle radius scale. The cavity proxy uses a local uniform displacement derived from the cubic root of the cavity volume scale. The funnel proxy uses a transverse outlet displacement derived from the normalized aperture scale.

## 8. Displacement Output

`outputs/step42_geometry_displacement/geometry_displacement.json` contains 243 rows: 81 phase samples times three tracked regions.

## 9. Quality Output

`outputs/step42_displacement_quality/displacement_quality.json` records finite, bounded, coverage, closure, repeatability, and diagnostic-only checks.

## 10. Repeatability Output

`outputs/step42_displacement_repeatability/displacement_repeatability.json` records stable hashes for the full displacement table and each tracked region.

## 11. Schedule Consistency

`outputs/step42_schedule_displacement_consistency/schedule_displacement_consistency.json` verifies that phases and prescribed Step 32 scale fields match the generated displacement diagnostics.

## 12. Motion Consistency

`outputs/step42_motion_displacement_consistency/motion_displacement_consistency.json` verifies that Step 42 rows align with Step 33 motion mapping rows by phase, region, and proxy scale.

## 13. Grid Diagnostics

`outputs/step42_grid_displacement_diagnostics/grid_displacement_diagnostics.json` summarizes active grid-cell coverage over 32, 48, and 64 grids for the tracked regions.

## 14. Cycle Closure

`outputs/step42_cycle_closure_diagnostics/cycle_closure_diagnostics.json` verifies that phase 0 and phase 1 displacement diagnostics close within tolerance for all tracked regions.

## 15. Guards

`outputs/step42_no_driver_update_guard/no_driver_update_guard.json` verifies that no driver, LBM, MPM, projection, or dynamic-solid update path is enabled. `outputs/step42_step41_regression_guard/step41_regression_guard.json` verifies that the accepted Step 41 evidence surface remains present and passing.

## 16. Artifact Budget

`outputs/step42_artifact_manifest/artifact_summary.json` enforces the Step 42 small-artifact budget and confirms that Step 42 produced no VTR files and no particle NPY files.

## 17. Acceptance Checklist

- [x] Step 42 goal file exists and defines a diagnostic-only implementation boundary.
- [x] Step 42 configs exist and keep all solver integration flags disabled.
- [x] Step 42 source modules generate finite, bounded displacement diagnostics for mantle, cavity, and funnel proxy regions.
- [x] Step 42 runner outputs are CSV/JSON/NPZ only and remain small.
- [x] Step 42 repeatability hashes are deterministic.
- [x] Step 42 schedule and motion consistency diagnostics pass.
- [x] Step 42 grid diagnostics pass for 32, 48, and 64 grids.
- [x] Step 42 cycle closure diagnostics pass.
- [x] Step 42 no-driver-update guard passes.
- [x] Step 42 Step 41 regression guard passes.
- [x] Step 42 artifact manifest passes.
- [x] Step 42 contract test passes.

## 18. Decision For Step 43

Step 42 can be accepted when the generated artifacts and contract test are green. Step 43 should only proceed by adding another explicitly controlled, opt-in boundary; it should not reinterpret Step 42 diagnostics as coupled geometry mutation or solver validation.
