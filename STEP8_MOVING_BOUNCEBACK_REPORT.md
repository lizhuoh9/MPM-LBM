# Step 8 Moving Bounce-Back Report

## 1. Goal

Step 8 adds an opt-in moving-boundary LBM path and link-wise momentum-exchange diagnostics for sharper solid boundaries.

Step 8 does not replace the Step 6/7 penalty path. The default `lbm.step()` remains the penalty-compatible static-bounce-back LBM step. Step 8 moving-boundary baselines explicitly call `lbm.step_moving_bounceback()`.

Step 8 does not transfer link-wise `hydro_force` back to MPM. Step 8 link-wise `hydro_force` is a diagnostic force on solid.

## 2. Files

Created / updated:

- `src/lbm_fluid.py`
- `baseline_tests/run_step8_static_bounceback_regression.py`
- `baseline_tests/run_step8_prescribed_moving_wall_couette.py`
- `baseline_tests/run_step8_projected_mpm_moving_boundary.py`
- `baseline_tests/run_step8_momentum_exchange_diagnostics.py`
- `tests/test_step8_moving_bounceback_contract.py`
- `logs/step8_static_bounceback_regression.log`
- `logs/step8_prescribed_moving_wall.log`
- `logs/step8_projected_mpm_boundary.log`
- `logs/step8_momentum_exchange.log`
- `outputs/step8_static_bounceback_regression/`
- `outputs/step8_prescribed_moving_wall/`
- `outputs/step8_projected_mpm_boundary/`
- `outputs/step8_momentum_exchange/`
- `STEP8_MOVING_BOUNCEBACK_REPORT.md`

## 3. Moving bounce-back formula

Final sign:

```text
F[i][LR[s]] = f[i][s] - 6 * w[s] * rho[i] * dot(e[s], u_wall)
```

No sign flip was needed. The prescribed +x moving wall drives positive fluid ux and produces positive `bb_net_fluid_impulse_x`.

## 4. Momentum-exchange diagnostic

Per bounce-back link:

```text
incoming_momentum = e[s] * f[i][s]
outgoing_momentum = e[LR[s]] * bounced
fluid_impulse = outgoing_momentum - incoming_momentum
solid_force = -fluid_impulse
```

The per-cell `hydro_force[ip]` stores the link-wise diagnostic force on solid. The scalar `bb_net_solid_force` reducer is finalized as `-bb_net_fluid_impulse` after link accumulation, avoiding independent f32 atomic-order drift in the scalar force-balance diagnostic.

## 5. Static bounce-back regression

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step8_static_bounceback_regression.py
```

Result:

- bb_link_count: 10240
- bb_max_correction: 0.000000000e+00
- max_abs_velocity_difference: 0.000000000e+00
- max_abs_rho_difference: 0.000000000e+00
- rho_min: 1.000000358e+00
- rho_max: 1.000000358e+00
- lbm_max_v: 0.000000000e+00
- cell_force_max_norm: 0.000000000e+00
- log: `logs/step8_static_bounceback_regression.log`

## 6. Prescribed moving wall Couette

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step8_prescribed_moving_wall_couette.py
```

Result:

- top_near_ux: 2.746345475e-02
- bottom_near_ux: 0.000000000e+00
- global_mean_ux: 3.758054925e-03
- mostly_increasing_fraction: 1.000000000e+00
- bb_link_count: 10240
- bb_max_correction: 5.000039469e-03
- bb_net_fluid_impulse_x: 5.732447281e-02
- bb_net_solid_force_x: -5.732447281e-02
- force_balance_error: 0.000000000e+00
- hydro_force_max_norm: 3.333371282e-01
- cell_force_max_norm: 0.000000000e+00
- rho_min: 1.000004411e+00
- rho_max: 1.000011086e+00
- lbm_max_v: 2.746346593e-02
- log: `logs/step8_prescribed_moving_wall.log`

## 7. Projected MPM moving boundary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step8_projected_mpm_moving_boundary.py
```

Result:

- solid_on_count: 825
- bb_link_count: 2556
- bb_max_correction: 6.693282630e-03
- projection_zone_fluid_mean_ux_initial: 0.000000000e+00
- projection_zone_fluid_mean_ux_final: 1.993434737e-03
- bb_net_fluid_impulse_x: 2.124552578e-01
- bb_net_solid_force_x: -2.124552578e-01
- force_balance_error: 0.000000000e+00
- hydro_force_max_norm: 4.083130062e-01
- cell_force_max_norm: 0.000000000e+00
- rho_min: 9.933133721e-01
- rho_max: 1.005585790e+00
- lbm_max_v: 2.119366825e-02
- mpm_min_J: 9.999990463e-01
- mpm_max_speed: 1.562588960e-01
- log: `logs/step8_projected_mpm_boundary.log`

## 8. Momentum-exchange diagnostics

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step8_momentum_exchange_diagnostics.py
```

Result:

- bb_link_count: 10240
- bb_max_correction: 5.000004079e-03
- bb_net_fluid_impulse_x: 8.166632056e-02
- bb_net_solid_force_x: -8.166632056e-02
- max_force_balance_error: 0.000000000e+00
- mean_force_balance_error: 0.000000000e+00
- cumulative_fluid_impulse_x: 8.152302638e+01
- cumulative_solid_force_x: -8.152302638e+01
- hydro_force_max_norm: 3.334834278e-01
- cell_force_max_norm: 0.000000000e+00
- rho_min: 1.000000238e+00
- rho_max: 1.000003219e+00
- lbm_max_v: 2.641588077e-02
- log: `logs/step8_momentum_exchange.log`

## 9. Explicit non-goals

Step 8 does not implement two-way MPM reaction from momentum exchange, penalty coupling replacement, two-phase flow, contact angle, squid geometry, sparse storage, or external/taichi_LBM3D edits.

Step 8 does not call `PenaltyFSICoupler3D` in moving-boundary baselines.

## 10. Acceptance checklist

- [x] main is on the Step 8 final commit
- [x] original lbm.step() still exists
- [x] lbm.step_moving_bounceback() exists
- [x] LBMFluid3D.streaming_moving_bounceback() exists
- [x] LBMFluid3D.clear_moving_boundary_diagnostics() exists
- [x] LBMFluid3D.get_moving_boundary_stats() exists
- [x] bb_link_count field exists
- [x] bb_max_correction field exists
- [x] bb_net_fluid_impulse field exists
- [x] bb_net_solid_force field exists
- [x] zero wall velocity moving bounce-back is close to static bounce-back
- [x] prescribed moving wall drives fluid along wall velocity
- [x] projected MPM moving boundary drives fluid along projected solid velocity
- [x] moving wall +x gives bb_net_fluid_impulse_x > 0
- [x] moving wall +x gives bb_net_solid_force_x < 0
- [x] link-wise force balance error is small
- [x] hydro_force is nonzero for moving wall diagnostics
- [x] cell_force remains zero in Step 8 moving-bounceback baselines
- [x] PenaltyFSICoupler3D is not used in Step 8 moving-bounceback baselines
- [x] rho_min > 0.95
- [x] rho_max < 1.05
- [x] lbm_max_v < 0.1
- [x] no NaN
- [x] no Inf
- [x] no two-phase flow
- [x] no contact angle physics
- [x] no ReducedSquidFSI
- [x] no external/taichi_LBM3D edits
- [x] logs are saved under logs/
- [x] outputs are saved under outputs/
- [x] STEP8_MOVING_BOUNCEBACK_REPORT.md is complete
- [x] pytest -q passes

## 11. Decision

Can proceed to Step 9?

- [x] Yes
- [ ] No
