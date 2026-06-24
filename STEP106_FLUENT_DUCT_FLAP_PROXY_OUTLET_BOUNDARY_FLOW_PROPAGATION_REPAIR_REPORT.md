# Step106 Fluent Duct-Flap Proxy Outlet Boundary Flow Propagation Repair Report

## Result

Step106 passed as a bounded outlet-boundary flow propagation repair. The only solver behavior change was the x-right pressure outlet branch in `src/mpm_lbm/sim/lbm/fluid.py`: for fluid interior neighbors, the pressure outlet now reconstructs equilibrium from `self.v[self.nx-2,j,k]` instead of the outlet boundary cell's old self velocity.

This is not Fluent validation, not Fluent equivalence, and not a displacement-curve match. It repairs a proxy LBM boundary propagation blocker exposed by Step105.

## Duct-Only Boundary Evidence

The isolated duct-only LBM runner used:

- row: `duct_only_lbm_outlet_boundary_flow_48`
- grid: `48^3`
- x-min velocity inlet: `target_u_lbm = [0.02, 0.0, 0.0]`
- x-max pressure outlet: `rho_bc_x_right = 1.0`
- static geometry: Step104 duct walls only, flap excluded from the LBM static geometry
- steps: `160`

Final duct-only metrics:

- `duct_only_outlet_boundary_flow_pass = true`
- inlet plane mean ux: `0.02000000700354576`
- mid-duct plane mean ux: `0.013426314108073711`
- outlet plane mean ux: `0.014053558930754662`
- outlet plane max ux: `0.019373983144760132`
- outlet-to-inlet mean ux ratio: `0.7026777004759616`
- outlet-to-mid mean ux ratio: `1.0467175739843422`
- `rho_min = 0.9999998211860657`
- `rho_max = 1.029547929763794`
- `has_nan = false`
- `has_inf = false`

These values clear the Step106 hard gates:

- outlet mean ux greater than `1e-5`
- outlet max ux greater than `1e-5`
- mid-duct mean ux greater than `1e-4`
- inlet mean ux inside `[0.015, 0.025]`
- density bounded inside `(0.95, 1.10)`

## Boundary Semantics

The committed semantics report records:

- `velocity_inlet_policy = fixed_equilibrium_velocity`
- `pressure_outlet_policy = interior_neighbor_velocity_extrapolation`
- `pressure_outlet_uses_boundary_self_velocity = false`
- `pressure_outlet_uses_interior_neighbor_velocity = true`
- `direct_quantitative_equivalence_allowed = false`
- `validation_claim_allowed = false`

## FSI Regression Smoke

The 20-step canonical driver smoke used the repaired Step104/Step105 duct-flap proxy setup:

- row: `fluent_duct_flap_proxy_48_20step_outlet_repair_regression_smoke`
- `n_grid = 48`
- `n_particles = 1024`
- `n_lbm_steps = 20`
- `mpm_dt = 0.0005`
- `target_u_lbm = [0.02, 0.0, 0.0]`
- `lbm_boundary_condition_mode = duct_velocity_inlet_pressure_outlet`
- `wall_velocity_application_mode = disabled`

Regression metrics:

- `step106_fsi_outlet_repair_regression_pass = true`
- completed LBM steps: `20`
- diagnostics rows: `21`
- flap-tip rows: `21`
- fixed-base particle count: `319`
- fixed-base max displacement norm: `0.0`
- fixed-base max velocity norm: `0.0`
- `target_u_lbm_applied_to_inlet = true`
- `target_u_lbm_applied_to_solid_initial_velocity = false`
- `step36_squid_wall_velocity_config_used = false`
- outlet plane mean ux: `1.1406370958866319e-07`
- outlet plane max ux: `1.844018271413006e-07`
- `outlet_plane_flow_present = true`
- `has_nan = false`
- `has_inf = false`
- gap count: `8`

The FSI regression remains a short smoke. It does not prove a physically developed outlet profile or close the Step105 gaps.

## Artifacts

Key artifacts:

- `outputs/step106_outlet_boundary_flow_propagation/flow_plane_report.json`
- `outputs/step106_outlet_boundary_flow_propagation/flow_plane_timeseries.csv`
- `outputs/step106_outlet_boundary_flow_propagation/boundary_condition_semantics_report.json`
- `outputs/step106_fsi_outlet_repair_regression/fsi_outlet_repair_regression_report.json`
- `outputs/step106_output_guard/output_guard_report.json`
- `outputs/step106_artifact_manifest/artifact_manifest.json`

## Verification

Verification run for Step106:

- `D:\working\taichi\env\python.exe -m py_compile ...` passed
- `D:\working\taichi\env\python.exe baseline_tests\run_step106_outlet_boundary_flow_propagation.py` passed
- `D:\working\taichi\env\python.exe baseline_tests\run_step106_fsi_outlet_repair_regression_smoke.py` passed
- output guard, artifact manifest, focused pytest, full pytest, and git checks are recorded in the final commit evidence/logs

## Remaining Gaps

Step106 intentionally leaves the Step105 Fluent-equivalence gaps open:

- 2D official case versus 3D proxy
- official mesh/conformal setup not imported
- official linear-elastic structural model not reproduced
- Fluent dynamic mesh not reproduced
- exact monitor definition not reproduced
- proxy inlet speed not dimensionally equal to the public tutorial inlet speed
- current LBM fluid model not a Fluent model reproduction
- official steady preflow initial condition not reproduced

Next work should start with steady preflow proxy initialization only after this repaired outlet boundary path remains stable.
