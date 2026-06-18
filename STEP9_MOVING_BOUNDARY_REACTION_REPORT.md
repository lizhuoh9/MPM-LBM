# Step 9 Moving-Boundary Reaction Report

## 1. Goal

Transfer Step 8 link-wise moving-boundary `hydro_force` back to `MPMSolid3D.grid_f_ext` through a dedicated `MovingBoundaryFSICoupler3D`, then validate a reproducible moving-boundary two-way MPM-LBM MVP.

Step 9 adds a dedicated moving-boundary reaction coupler.
Step 9 does not replace the Step 6/7 penalty coupler.
Step 9 does not change the Step 8 moving bounce-back formula.
Step 9 moving-boundary reaction uses an engineering coupling scale, not a final strict momentum-conserving sharp-interface integration.
Step 9 moving-boundary mode keeps `lbm.cell_force` at zero.

## 2. Files

Created / updated:

- `src/moving_boundary_coupling.py`
- `src/__init__.py`
- `baseline_tests/run_step9_moving_boundary_reaction_field.py`
- `baseline_tests/run_step9_moving_boundary_two_way_mpm_reaction.py`
- `baseline_tests/run_step9_moving_boundary_coupled_smoke.py`
- `baseline_tests/run_step9_compare_penalty_vs_moving_boundary.py`
- `tests/test_step9_moving_boundary_reaction_contract.py`
- `STEP9_MOVING_BOUNDARY_REACTION_REPORT.md`

Generated:

- `logs/step9_mb_reaction_field.log`
- `logs/step9_mb_two_way_reaction.log`
- `logs/step9_mb_coupled_smoke.log`
- `logs/step9_compare_modes.log`
- `outputs/step9_mb_reaction_field/`
- `outputs/step9_mb_two_way_reaction/`
- `outputs/step9_mb_coupled_smoke/`
- `outputs/step9_compare_modes/`

## 3. Reaction model

```text
sampled_hydro_lbm = sum(weight * lbm.hydro_force[I])
force_density_scale_lbm_to_norm = dx_norm / lbm_dt_phys^2
particle_force_norm = sampled_hydro_lbm * force_density_scale_lbm_to_norm * particle_volume * reaction_scale
solid.grid_f_ext += weight * particle_force_norm
```

The Step 9 transfer samples Step 8 moving-boundary `hydro_force` and projected `solid_phi` with the same 3x3x3 quadratic stencil used by MPM. Particles with sampled `solid_phi <= phi_min` are ignored. The particle force is clamped by `force_cap_norm` before it is scattered to `solid.grid_f_ext`.

The scale `dx_norm / lbm_dt_phys^2` is an engineering coupling scale for this MVP. It is not the final strict momentum-conserving area/link integration model.

Stable window observed:

- Reaction field sanity: `reaction_scale=1.0`, `force_cap_norm=1.0e-2`
- Isolated two-way MPM reaction: `reaction_scale=1.0`, `force_cap_norm=1.0e-2`
- 20-step coupled smoke and comparison moving-boundary mode: `reaction_scale=1.0`, `force_cap_norm=1.0e-4`

The stronger `1.0e-2` cap produced excessive coupled response in the 20-step moving-boundary loop, so the full coupled baselines use the documented stable cap `1.0e-4`.

## 4. Explicit non-goals

Step 9 does not implement a new bounce-back formula, two-phase flow, contact angle physics, squid geometry, sparse storage, ReducedSquidFSI, or edits to `external/taichi_LBM3D`.

Step 9 does not make `lbm.step_moving_bounceback()` the default `lbm.step()`.

Step 9 does not route moving-boundary reaction through `lbm.cell_force`.

Step 9 does not claim strict final momentum-conserving sharp-interface FSI or real squid validation.

## 5. Reaction field sanity

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step9_moving_boundary_reaction_field.py
```

Result:

- bb_link_count: 2602
- hydro_force_max_norm: 4.174053967e-01
- active_reaction_particle_count: 3448
- max_particle_reaction_norm: 3.710629884e-03
- max_grid_reaction_norm: 1.329938998e-03
- net_particle_reaction_force_x: -4.243572354e-01
- net_grid_reaction_force_x: -4.243514538e-01
- cell_force_max_norm: 0.000000000e+00
- rho_min: 9.800003767e-01
- rho_max: 1.020000339e+00
- lbm_max_v: 2.380830236e-02
- Log marker: `[OK] Step 9 moving-boundary reaction field finished`

## 6. Two-way MPM reaction

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step9_moving_boundary_two_way_mpm_reaction.py
```

Result:

- initial_solid_mean_vx_norm: 1.562547684e-01
- final_solid_mean_vx_norm: -2.054505348e-01
- active_reaction_particle_count: 3448
- net_grid_reaction_force_x: -2.325235903e-01
- mpm_min_J: 8.278859258e-01
- mpm_max_speed: 2.726269007e+00
- Log marker: `[OK] Step 9 moving-boundary MPM reaction finished`

## 7. Moving-boundary coupled smoke

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step9_moving_boundary_coupled_smoke.py
```

Result:

- completed_lbm_steps: 20
- total_mpm_substeps: 200
- projection_zone_fluid_mean_ux_initial: 0.000000000e+00
- projection_zone_fluid_mean_ux_final: 1.293939771e-03
- initial_solid_mean_vx_norm: 1.562547684e-01
- final_solid_mean_vx_norm: 1.509043723e-01
- bb_link_count: 2322
- hydro_force_max_norm: 4.021632075e-01
- active_reaction_particle_count: 3520
- net_grid_reaction_force_x: -1.804006286e-02
- cell_force_max_norm: 0.000000000e+00
- rho_min: 9.851435423e-01
- rho_max: 1.014919639e+00
- lbm_max_v: 2.135871910e-02
- mpm_min_J: 9.723306298e-01
- mpm_max_speed: 2.192057818e-01
- Log marker: `[OK] Step 9 moving-boundary coupled smoke finished`

## 8. Penalty vs moving-boundary comparison

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step9_compare_penalty_vs_moving_boundary.py
```

Result:

| mode | stable | fluid_mean_ux_final | projection_zone_ux_final | solid_mean_vx_final | rho_min | rho_max | lbm_max_v | mpm_min_J | cell_force_max_norm | hydro_force_max_norm |
| ---- | ------ | ------------------: | -----------------------: | ------------------: | ------: | ------: | --------: | --------: | ------------------: | -------------------: |
| penalty | True | 1.451979301e-06 | 3.118352106e-05 | 1.536530405e-01 | 9.999890924e-01 | 1.000013471e+00 | 4.151002940e-05 | 9.999932647e-01 | 1.963135401e-05 | 1.963135401e-05 |
| moving_boundary | True | 5.752437282e-04 | 1.293938607e-03 | 1.509043574e-01 | 9.851434231e-01 | 1.014919639e+00 | 2.135867253e-02 | 9.723307490e-01 | 0.000000000e+00 | 4.021632373e-01 |

Log marker: `[OK] Step 9 penalty vs moving-boundary comparison finished`

## 9. Acceptance checklist

- [x] main is on the Step 9 final commit
- [x] src/moving_boundary_coupling.py exists
- [x] src/__init__.py exports MovingBoundaryFSICoupler3D
- [x] MovingBoundaryFSICoupler3D exists
- [x] clear_reaction_diagnostics() exists
- [x] add_moving_boundary_reaction_to_mpm_grid() exists
- [x] force_density_scale_lbm_to_norm is documented and used
- [x] moving-boundary hydro_force can write to MPMSolid3D.grid_f_ext
- [x] reaction field baseline completes
- [x] reaction field baseline has active_reaction_particle_count > 0
- [x] reaction field baseline has net_grid_reaction_force_x < 0 for +x moving solid
- [x] two-way MPM reaction baseline completes
- [x] two-way MPM reaction baseline shows final_solid_mean_vx_norm < initial_solid_mean_vx_norm
- [x] moving-boundary coupled smoke completes 20 LBM steps
- [x] moving-boundary coupled smoke completes 200 MPM substeps
- [x] comparison baseline completes
- [x] comparison baseline shows penalty mode stable
- [x] comparison baseline shows moving-boundary mode stable
- [x] moving-boundary mode keeps cell_force_max_norm == 0
- [x] moving-boundary mode has bb_link_count > 0
- [x] penalty mode has cell_force_max_norm > 0
- [x] rho_min > 0.95
- [x] rho_max < 1.05
- [x] lbm_max_v < 0.1
- [x] mpm_min_J > 0
- [x] mpm_max_speed < 10
- [x] no NaN
- [x] no Inf
- [x] no two-phase flow
- [x] no contact angle physics
- [x] no ReducedSquidFSI
- [x] no external/taichi_LBM3D edits
- [x] logs are saved under logs/
- [x] outputs are saved under outputs/
- [x] STEP9_MOVING_BOUNDARY_REACTION_REPORT.md is complete
- [x] pytest -q passes

## 10. Decision

Can proceed to Step 10?

- [x] Yes
- [ ] No
