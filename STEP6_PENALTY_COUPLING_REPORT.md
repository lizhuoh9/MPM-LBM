# Step 6 Penalty Coupling Report

## 1. Goal

Step 6 implements the first penalty-force MPM-LBM two-way coupling MVP on top of the Step 5 projection fields.

The implemented coupling uses:

```text
cell_force = beta_lbm * solid_phi * rho_f * (solid_vel - fluid_vel)
hydro_force = -cell_force
```

`cell_force` drives the LBM fluid toward the projected MPM solid velocity. `hydro_force` is the equal-and-opposite reaction sampled back to MPM particles and deposited on `MPMSolid3D.grid_f_ext`.

## 2. Files Created Or Updated

```text
src/coupling.py
src/__init__.py
baseline_tests/run_step6_penalty_force_field.py
baseline_tests/run_step6_lbm_response_to_moving_solid.py
baseline_tests/run_step6_two_way_mpm_reaction.py
baseline_tests/run_step6_coupled_smoke.py
tests/test_step6_penalty_coupling_contract.py
logs/step6_penalty_force_field.log
logs/step6_lbm_response.log
logs/step6_two_way_reaction.log
logs/step6_coupled_smoke.log
outputs/step6_penalty_force_field/
outputs/step6_lbm_response/
outputs/step6_two_way_reaction/
outputs/step6_coupled_smoke/
STEP6_PENALTY_COUPLING_REPORT.md
```

## 3. Coupling Model

`PenaltyFSICoupler3D` provides:

```text
clear_force_fields(lbm)
inside_lbm(I, lbm)
build_penalty_force(lbm)
add_lbm_reaction_to_mpm_grid(solid, lbm)
get_stats()
```

The sign convention is:

```text
moving solid +x, still fluid:
  cell_force_x > 0
  hydro_force_x < 0
```

The force norm is capped by `force_cap_lbm` for stability.

## 4. Unit Conversion For Reaction Force

The MPM grid force is in normalized-domain units. The conversion used by `PenaltyFSICoupler3D` is:

```text
force_density_scale_lbm_to_norm = dx_norm / lbm_dt_phys^2
```

With the Step 6 default grid:

```text
n_grid = 32
dx_norm = 0.03125
mpm_dt = 0.0004
mpm_substeps_per_lbm_step = 10
lbm_dt_phys = 0.004
force_density_scale_lbm_to_norm = 1953.125
```

Reaction transfer:

```text
hydro_density_lbm_at_particle = sum(weight * lbm.hydro_force[I])
hydro_density_norm = hydro_density_lbm_at_particle * force_density_scale_lbm_to_norm
particle_force_norm = hydro_density_norm * current_particle_volume * reaction_scale
solid.grid_f_ext += weight * particle_force_norm
```

Baseline values:

```text
beta_lbm = 1.0e-3 for penalty force, MPM reaction, and coupled smoke
beta_lbm = 3.0e-3 for LBM response
phi_min = 1.0e-6
force_cap_lbm = 1.0e-4
reaction_scale = 1.0
```

## 5. Explicit Non-Goals

Step 6 does not implement:

```text
moving bounce-back
momentum exchange
sharp-interface FSI
two-phase flow
contact angle physics
squid geometry
sparse storage
ReducedSquidFSI
edits to external/taichi_LBM3D
```

The Step 6 penalty baselines keep projected cells fluid-active and do not use the Step 5 dynamic-mask dry run as FSI evidence.

## 6. Penalty Force Field

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step6_penalty_force_field.py
```

Log:

```text
logs/step6_penalty_force_field.log
```

Result:

```text
[Taichi] Starting on arch=cuda
target_u_lbm=(0.03, 0.0, 0.0)
target_u_norm=(0.234375, 0.0, 0.0)
active_force_cell_count=1584
cell_force_max_norm=3.000001925e-05
hydro_force_max_norm=3.000001925e-05
net_cell_force=[0.026506015475760147, 0.0, 0.0]
net_hydro_force=[-0.026506015475760147, 0.0, 0.0]
balance_error=0.000000000e+00
rho_delta=0.000000000e+00
J_delta=0.000000000e+00
[OK] Step 6 penalty force field baseline finished
```

Outputs:

```text
outputs/step6_penalty_force_field/LBMForce_0.vtr
outputs/step6_penalty_force_field/cell_force.npy
outputs/step6_penalty_force_field/hydro_force.npy
```

## 7. LBM Response

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step6_lbm_response_to_moving_solid.py
```

Log:

```text
logs/step6_lbm_response.log
```

Result:

```text
[Taichi] Starting on arch=cuda
target_u_lbm=(0.03, 0.0, 0.0)
target_u_norm=(0.234375, 0.0, 0.0)
n_lbm_steps=100
initial_fluid_mean_ux=0.000000000e+00
final_fluid_mean_ux=5.122571019e-04
active_force_cell_count=1584
cell_force_max_norm=8.836216875e-05
hydro_force_max_norm=8.836216875e-05
rho_min=9.999490976e-01
rho_max=1.000054359e+00
lbm_max_v=7.148829754e-04
[OK] Step 6 LBM response baseline finished
```

Outputs:

```text
outputs/step6_lbm_response/LBMFluid_100.vtr
outputs/step6_lbm_response/cell_force.npy
outputs/step6_lbm_response/hydro_force.npy
```

## 8. MPM Reaction

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step6_two_way_mpm_reaction.py
```

Log:

```text
logs/step6_two_way_reaction.log
```

Result:

```text
[Taichi] Starting on arch=cuda
target_u_lbm=(0.03, 0.0, 0.0)
target_u_norm=(0.234375, 0.0, 0.0)
reaction_substeps=50
initial_solid_mean_vx_norm=2.343750000e-01
final_solid_mean_vx_norm=2.333916724e-01
max_reaction_grid_force_norm=1.570245161e-07
net_reaction_grid_force=(-0.0013262658612802625, 0.0, 0.0)
mpm_min_J=9.999901652e-01
mpm_max_speed=2.334775776e-01
[OK] Step 6 MPM reaction baseline finished
```

Outputs:

```text
outputs/step6_two_way_reaction/particles_x.npy
outputs/step6_two_way_reaction/particles_v.npy
outputs/step6_two_way_reaction/particles_F.npy
outputs/step6_two_way_reaction/particles_J.npy
```

## 9. Coupled Smoke

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step6_coupled_smoke.py
```

Log:

```text
logs/step6_coupled_smoke.log
```

Result:

```text
[Taichi] Starting on arch=cuda
n_grid=32
n_lbm_steps=20
mpm_substeps_per_lbm_step=10
target_u_lbm=(0.02, 0.0, 0.0)
target_u_norm=(0.15625, 0.0, 0.0)
initial_fluid_mean_ux=0.000000000e+00
final_fluid_mean_ux=3.118429595e-05
initial_solid_mean_vx_norm=1.562500000e-01
final_solid_mean_vx_norm=1.536528170e-01
active_force_cell_count=1584
cell_force_max_norm=1.963135037e-05
hydro_force_max_norm=1.963135037e-05
net_cell_force=(0.01734890230000019, -4.51098669529415e-09, 1.6600392171994827e-08)
net_hydro_force=(-0.01734890230000019, 4.511206963542236e-09, -1.6600392171994827e-08)
max_reaction_grid_force_norm=1.017982498e-07
net_reaction_grid_force=(-0.0008700874168425798, 2.1612188427777568e-10, -4.4330308868190116e-10)
completed_lbm_steps=20
total_mpm_substeps=200
rho_min=9.999890327e-01
rho_max=1.000013232e+00
lbm_max_v=4.153085320e-05
mpm_min_J=9.999936819e-01
mpm_max_speed=1.536898315e-01
[OK] Step 6 coupled smoke baseline finished
```

Outputs:

```text
outputs/step6_coupled_smoke/LBMFluid_20.vtr
outputs/step6_coupled_smoke/particles_x.npy
outputs/step6_coupled_smoke/particles_v.npy
outputs/step6_coupled_smoke/particles_F.npy
outputs/step6_coupled_smoke/particles_J.npy
outputs/step6_coupled_smoke/cell_force.npy
outputs/step6_coupled_smoke/hydro_force.npy
```

## 10. Hard Acceptance Checklist

- [x] main is on the Step 6 final commit
- [x] `src/coupling.py` exists
- [x] `src/__init__.py` exports `PenaltyFSICoupler3D`
- [x] `PenaltyFSICoupler3D.clear_force_fields()` exists
- [x] `PenaltyFSICoupler3D.build_penalty_force()` exists
- [x] `PenaltyFSICoupler3D.add_lbm_reaction_to_mpm_grid()` exists
- [x] `build_penalty_force()` writes nonzero `lbm.cell_force` when projected solid moves
- [x] `build_penalty_force()` writes `lbm.hydro_force`
- [x] `hydro_force = -cell_force`
- [x] moving solid +x gives `net_cell_force_x > 0`
- [x] moving solid +x gives `net_hydro_force_x < 0`
- [x] `net_cell_force + net_hydro_force` approximately zero
- [x] LBM response baseline shows fluid mean ux increases
- [x] MPM reaction baseline shows solid mean vx decreases
- [x] coupled smoke baseline completes 20 LBM steps
- [x] coupled smoke baseline completes 200 MPM substeps
- [x] `rho_min > 0.95`
- [x] `rho_max < 1.05`
- [x] `lbm_max_v < 0.1`
- [x] `mpm_min_J > 0`
- [x] `mpm_max_speed < 10`
- [x] no NaN
- [x] no Inf
- [x] no moving bounce-back
- [x] no momentum exchange
- [x] no two-phase flow
- [x] no contact angle physics
- [x] no ReducedSquidFSI
- [x] no `update_dynamic_solid()` in Step 6 baselines
- [x] no `reinitialize_new_fluid_cells()` in Step 6 baselines
- [x] no `external/taichi_LBM3D` edits
- [x] logs are saved under `logs/`
- [x] outputs are saved under `outputs/`
- [x] `STEP6_PENALTY_COUPLING_REPORT.md` is complete
- [x] `pytest -q` passes

## 11. Decision

Can proceed to Step 7?

- [x] Yes

Step 6 establishes a minimal stable penalty-force MPM-LBM prototype. It is sufficient evidence to proceed to Step 7 planning for stronger interface treatment or higher-fidelity FSI validation, but it is not sharp-interface no-slip FSI and not a real squid validation.
