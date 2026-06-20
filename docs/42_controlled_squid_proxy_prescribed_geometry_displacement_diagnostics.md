# Step 42 Controlled Squid Proxy Prescribed Geometry Displacement Diagnostics

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

## Purpose

Step 42 converts the accepted Step 32 cycle schedule and Step 33 tracked proxy regions into prescribed geometry displacement diagnostics for:

- `mantle_outer`
- `mantle_cavity_proxy`
- `funnel_outlet_proxy`

The result is an artifact-only displacement envelope: per-phase displacement norms, displaced proxy bounding boxes, grid coverage summaries, repeatability hashes, and consistency checks against the schedule and motion mapping. The implementation intentionally stops before any coupled-state write.

## Inputs

- `configs/step42_squid_proxy_geometry_displacement.json`
- `configs/step42_squid_proxy_displacement_sampling.json`
- `configs/step32_squid_proxy_kinematics_schedule.json`
- `configs/step33_squid_proxy_motion_mapping.json`
- `configs/step30_squid_proxy_geometry.json`
- `configs/step30_squid_proxy_region_config.json`

## Outputs

Step 42 writes compact CSV/JSON diagnostics and one compressed NPZ summary:

- `outputs/step42_displacement_config_validation/`
- `outputs/step42_geometry_displacement/`
- `outputs/step42_displacement_quality/`
- `outputs/step42_displacement_repeatability/`
- `outputs/step42_schedule_displacement_consistency/`
- `outputs/step42_motion_displacement_consistency/`
- `outputs/step42_grid_displacement_diagnostics/`
- `outputs/step42_cycle_closure_diagnostics/`
- `outputs/step42_no_driver_update_guard/`
- `outputs/step42_step41_regression_guard/`
- `outputs/step42_artifact_manifest/`

No dense displacement field, displaced particle set, VTR file, or particle NPY file is produced by Step 42.

## Model Boundary

The mantle displacement proxy uses the Step 32 mantle radius scale as a radial contraction/return diagnostic. The cavity displacement proxy uses the cubic root of the prescribed cavity volume scale as a uniform local proxy. The funnel displacement proxy uses the normalized Step 32 aperture scale as a transverse outlet-opening diagnostic.

These are controlled proxy diagnostics. They are not written into the coupled solver state, not used to modify `FSIDriver3D`, and not interpreted as free-body motion or production solver readiness.

## Validation

The Step 42 validation surface is:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step42_displacement_config_validation.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step42_generate_geometry_displacement.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step42_displacement_quality.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step42_displacement_repeatability.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step42_schedule_displacement_consistency.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step42_motion_displacement_consistency.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step42_grid_displacement_diagnostics.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step42_cycle_closure_diagnostics.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step42_no_driver_update_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step42_step41_regression_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step42_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step42_geometry_displacement_diagnostics_contract.py -q
```

The artifact manifest is intentionally rerun after logs and pytest logs are present so the final budget reflects the committed artifact set.
