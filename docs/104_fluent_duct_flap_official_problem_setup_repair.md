# Step104 Fluent Duct-Flap Official Problem Setup Repair

Step104 repairs the problem setup gap found after Step103. Step103 produced a
Fluent-inspired proxy smoke, but the driver was still solving the wrong setup:
`target_u_lbm` was used as solid initial velocity, the LBM geometry was an
all-fluid cube, the duct inlet/outlet were not explicit, the flap base was only
metadata, the silicone material reference was not mapped into MPM, Step36 squid
wall velocity was still connected, and no flap-tip displacement time series was
available.

Step104 changes only setup wiring and evidence. It does not change LBM
collision, tau convention, MPM update formulas, moving-boundary formulas, or
reaction-transfer formulas.

## Repaired Setup

- Driver row: `fluent_duct_flap_setup_repair_48_5step_smoke`
- Driver module: `src.mpm_lbm.sim.drivers.fsi_driver`
- Grid/particles/steps: `48^3`, `1024`, `5`
- Coupling: `moving_boundary`, engineering reaction transfer
- Geometry type: `duct_flap_proxy`
- LBM geometry file: `geo_duct_flap_proxy_48.dat`, not an all-fluid cube
- LBM boundary mode: `duct_velocity_inlet_pressure_outlet`
- Velocity inlet: x-min, `target_u_lbm = [0.02, 0.0, 0.0]`
- Pressure outlet: x-max, `rho = 1.0`
- Solid initial velocity: `initial_solid_velocity_norm = [0.0, 0.0, 0.0]`
- Step36 squid wall velocity: disabled
- MPM material mapping: `p_rho = 1600.0`, `young_modulus = 1000000.0`,
  `poisson_ratio = 0.47`
- Fixed-base MPM mask: applied to `319` particles
- Proxy flap-tip monitor: committed as
  `outputs/step104_fluent_duct_flap_setup_repair/flap_tip_displacement_timeseries.csv`

## Evidence

Primary artifacts:

- `outputs/step104_fluent_duct_flap_setup_repair/setup_repair_report.json`
- `outputs/step104_fluent_duct_flap_setup_repair/duct_boundary_condition_report.json`
- `outputs/step104_fluent_duct_flap_setup_repair/duct_static_geometry_report.json`
- `outputs/step104_fluent_duct_flap_setup_repair/flap_tip_displacement_timeseries.csv`
- `outputs/step104_output_guard/output_guard_report.json`
- `outputs/step104_artifact_manifest/artifact_manifest.json`

Important evidence values:

- completed LBM steps: `5`
- diagnostics rows: `6`
- `has_nan = false`
- `has_inf = false`
- inlet fluid cells: `80`
- pressure outlet fluid cells: `80`
- duct wall cells: `106752`
- fluid cells: `3840`
- all-fluid geometry used: `false`
- fixed-base max displacement: `0.0`
- fixed-base max velocity: `0.0`
- direct quantitative Fluent equivalence allowed: `false`
- validation claim allowed: `false`

## Remaining Gaps

Step104 still reports capability gaps:

- The public Fluent tutorial is a 2D case; this solver remains 3D.
- The public Fluent tutorial uses Fluent intrinsic FSI and dynamic mesh; this
  code does not reproduce that exact formulation.
- The flap-tip time series is a proxy monitor, not a proven direct equivalent
  to the official Fluent structural-point monitor.
- The Step104 smoke is five steps, not the full `50 x 0.0005 s` public tutorial
  transient.

The allowed Step104 claim is only that the duct-flap problem setup repair is
wired for a short proxy smoke and the remaining equivalence gaps are reported.
