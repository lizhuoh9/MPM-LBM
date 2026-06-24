# Step106 Outlet Boundary Flow Propagation Repair

Step106 repairs the x-right pressure outlet behavior for the committed Fluent-inspired duct-flap proxy. Step105 showed that the 50-step transient smoke developed positive inlet and mid-duct velocity, but the outlet plane remained exactly zero. The repaired x-right pressure outlet now uses the interior neighbor velocity for fluid-neighbor pressure outlet reconstruction.

This document is a proxy diagnostic record. It is not a Fluent validation record and does not permit direct quantitative equivalence claims.

## Repair Boundary

Changed:

- `src/mpm_lbm/sim/lbm/fluid.py`
- `bc_x_right == 1`
- fluid interior neighbor branch
- pressure outlet equilibrium source changed from outlet boundary self velocity to `self.v[self.nx-2,j,k]`

Unchanged:

- collision
- tau convention
- streaming sequence
- moving bounce-back
- moving-boundary coupling
- reaction transfer
- MPM stress and integration
- Step36 wall velocity behavior
- flap-tip monitor definition
- dimensional mapping

## Evidence Pattern

Step106 separates two questions:

- duct-only LBM propagation: hard gate for nonzero outlet flow
- 20-step FSI regression smoke: regression guard for canonical driver behavior

The duct-only runner is the authoritative outlet repair evidence because it removes MPM/FSI coupling from the boundary-condition diagnosis.

## Duct-Only Outcome

The final duct-only report passed with:

- inlet mean ux: `0.02000000700354576`
- mid-duct mean ux: `0.013426314108073711`
- outlet mean ux: `0.014053558930754662`
- outlet max ux: `0.019373983144760132`
- `rho_min = 0.9999998211860657`
- `rho_max = 1.029547929763794`
- no NaN
- no Inf

The outlet plane is no longer zero-locked.

## FSI Regression Outcome

The 20-step FSI regression smoke passed with:

- completed LBM steps: `20`
- diagnostics rows: `21`
- flap-tip rows: `21`
- fixed-base max displacement norm: `0.0`
- fixed-base max velocity norm: `0.0`
- target inlet applied: `true`
- target solid initial velocity applied: `false`
- Step36 wall velocity used: `false`
- outlet plane flow present: `true`
- no NaN
- no Inf

This smoke remains short and gap-only. It does not prove a developed transient, a Fluent monitor match, or a physical displacement match.

## Files

- `configs/step106_outlet_boundary_flow_policy.json`
- `configs/step106_duct_only_lbm_outlet_boundary_flow_48.json`
- `configs/step106_fluent_duct_flap_proxy_48_20step_outlet_repair_regression_smoke.json`
- `src/mpm_lbm/evidence/step106_outlet_boundary_flow_propagation_runner.py`
- `src/mpm_lbm/evidence/step106_output_guard.py`
- `baseline_tests/run_step106_outlet_boundary_flow_propagation.py`
- `baseline_tests/run_step106_fsi_outlet_repair_regression_smoke.py`
- `tests/test_step106_outlet_boundary_flow_propagation_contract.py`
- `tests/test_step106_output_guard_contract.py`
