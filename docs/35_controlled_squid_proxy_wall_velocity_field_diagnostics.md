# Step 35 Controlled Squid Proxy Wall Velocity Field Diagnostics

Step 35 is controlled squid proxy moving-wall velocity field diagnostics.
Step 35 generates diagnostic wall velocity fields only.
Step 35 does not apply moving wall velocity to LBM.
Step 35 does not update LBM populations.
Step 35 does not change moving bounce-back formulas.
Step 35 does not implement a jet model.
Step 35 does not implement squid swimming.
Step 35 does not implement new FSI physics.
The default boundary_motion_mode remains static.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.

## Purpose

Step 34 accepted a guarded boundary-motion driver interface that remains report-only. Step 35 takes the next narrow step: it converts the accepted Step 34 interface, Step 32 schedule, Step 33 motion mapping, and Step 30 squid proxy regions into sparse wall velocity diagnostic summaries.

The generated rows are designed for inspection and contract testing. They are not consumed by `FSIDriver3D`, `LBMFluid3D`, moving bounce-back, MPM, projection, or any FSI coupler.

## Inputs

- `configs/step35_squid_proxy_wall_velocity_field.json`
- `configs/step34_boundary_motion_interface_prescribed_kinematic.json`
- `configs/step33_squid_proxy_motion_mapping.json`
- `configs/step32_squid_proxy_kinematics_schedule.json`
- `configs/step30_squid_proxy_region_config.json`
- `configs/step30_squid_proxy_geometry.json`

## Diagnostic Rows

The diagnostic generator writes 63 rows:

- 3 grid sizes: `32`, `48`, `64`
- 7 phases: `0.0`, `0.1`, `0.2`, `0.35`, `0.5`, `0.75`, `1.0`
- 3 tracked regions: `mantle_outer`, `mantle_cavity_proxy`, `funnel_outlet_proxy`

Each row records active cell coverage, velocity norm statistics, mean vector components, source motion rates, and diagnostic-only safety flags.

## Region Proxies

- `mantle_outer` uses the Step 33 radial-scale proxy as a signed radial diagnostic velocity.
- `mantle_cavity_proxy` uses the Step 33 cavity volume-rate proxy as a small signed axis diagnostic velocity.
- `funnel_outlet_proxy` uses the Step 33 aperture-rate proxy as a small signed `+y` axis diagnostic velocity.

These proxies are intentionally diagnostic summaries. They are not driver actuation, and they are not a fluid forcing model.

## Outputs

- `outputs/step35_wall_velocity_config_validation/wall_velocity_config_validation.json`
- `outputs/step35_wall_velocity_field/wall_velocity_field.json`
- `outputs/step35_wall_velocity_quality/wall_velocity_quality.json`
- `outputs/step35_wall_velocity_repeatability/wall_velocity_repeatability.json`
- `outputs/step35_motion_velocity_consistency/motion_velocity_consistency.json`
- `outputs/step35_grid_coverage_diagnostics/grid_coverage_diagnostics.json`
- `outputs/step35_no_lbm_update_guard/no_lbm_update_guard.json`
- `outputs/step35_step34_regression_guard/step34_regression_guard.json`
- `outputs/step35_artifact_manifest/artifact_summary.json`

## Safety Boundaries

Step 35 keeps all LBM and FSI execution paths unchanged. The no-update guard checks Step 35 source and artifacts for population writes, moving bounce-back calls, driver integration flags, dynamic-solid mutation, and projector mutation.

Future Step 36 work may use these diagnostics as an input reference for a guarded opt-in smoke. That is a separate contract.
