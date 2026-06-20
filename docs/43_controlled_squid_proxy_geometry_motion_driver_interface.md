# Step 43 Controlled Squid Proxy Geometry Motion Driver Interface

Step 43 is controlled squid proxy geometry motion driver interface.
Step 43 defines a guarded driver interface only.
Step 43 keeps geometry motion diagnostic-only.
Step 43 does not update driver geometry.
Step 43 does not displace MPM particles.
Step 43 does not update LBM solid_phi.
Step 43 does not update dynamic_solid.
Step 43 does not recompute boundary links from displaced geometry.
Step 43 does not change moving bounce-back formulas.
The default geometry_motion_mode remains static.
The default geometry_motion_application_mode remains disabled.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.

## Purpose

Step 43 adds a driver-facing geometry-motion contract that can load the accepted Step 42 displacement artifact and write a no-op interface report. It establishes safe config fields and a report-only `FSIDriver3D` hook without entering geometry mutation, projection mutation, or solver-formula paths.

## Inputs

- `configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json`
- `outputs/step42_geometry_displacement/geometry_displacement.json`
- `outputs/step42_displacement_quality/displacement_quality.json`
- `outputs/step42_displacement_repeatability/displacement_repeatability.json`
- `outputs/step42_cycle_closure_diagnostics/cycle_closure_diagnostics.json`

## Driver Rows

Step 43 uses four short 48^3 rows:

- static engineering moving-boundary row
- diagnostic-only engineering moving-boundary row
- static link-area moving-boundary row
- diagnostic-only link-area moving-boundary row

All rows keep wall-velocity application disabled, VTK disabled, particle output disabled, and strict geometry quality checks enabled.

## Reports

Diagnostic-only rows write `geometry_motion_interface_report.json` in their case directories. Static rows write no geometry-motion report. The report confirms that the Step 42 displacement artifact is readable and finite, then records that every geometry mutation flag is disabled.

## Validation

The Step 43 validation surface includes config validation, interface report generation, static short-driver regression, diagnostic no-op smoke rows, static-vs-diagnostic no-op comparison, mutation guard, quality aggregation, Step 42 regression, artifact manifest, and contract tests.

The diagnostic-only path is accepted only when it remains observational and the driver diagnostics match the static rows within the Step 43 no-op tolerance.
