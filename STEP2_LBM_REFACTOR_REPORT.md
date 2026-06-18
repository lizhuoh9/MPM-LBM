# Step 2 LBM Refactor Report

## 1. Goal

Refactor the vendored `taichi_LBM3D` single-phase D3Q19 MRT solver into a local coupling-ready fluid backend without implementing MPM or real FSI.

Step 2 result:

```text
src/lbm_config.py
src/lbm_fluid.py
baseline_tests/run_lbm_refactored_smoke.py
baseline_tests/run_lbm_refactored_poiseuille.py
baseline_tests/run_lbm_refactored_body_force.py
baseline_tests/run_lbm_refactored_dynamic_solid_dummy.py
```

The refactored solver keeps the original D3Q19 velocity set, MRT matrices, collision-streaming-boundary-update step order, and static bounce-back behavior. The new fields are only coupling-ready interfaces for later steps.

## 2. Source Files

- Original source file: `external/taichi_LBM3D/Single_phase/LBM_3D_SinglePhase_Solver.py`
- Refactored source file: `src/lbm_fluid.py`
- Config source file: `src/lbm_config.py`

The original file under `external/taichi_LBM3D` was not modified.

## 3. Main Changes Checklist

- [x] Added `LBMConfig`.
- [x] Added `LBMFluid3D`.
- [x] Disabled sparse storage for Step 2 with `NotImplementedError`.
- [x] Preserved original `step()` sequence: `colission()`, `streaming1()`, `Boundary_condition()`, `streaming3()`.
- [x] Added `static_solid`, `old_solid`, `solid_phi`, `solid_mass`, `solid_vel`, `cell_force`, `hydro_force`, and `reinit_flag`.
- [x] Added stats fields: `rho_min`, `rho_max`, `mass_total`, and `force_norm_max`.
- [x] Changed `cal_local_force()` to return global force plus grid-local `cell_force`.
- [x] Removed the compile-time `ti.static(self.force_flag == 1)` shielding from the force path.
- [x] Added dummy hydrodynamic reaction export: `hydro_force = -cell_force`.
- [x] Extended VTK output with `Solid`, `StaticSolid`, `rho`, `velocity`, `solid_phi`, `solid_mass`, `solid_vel`, `cell_force`, and `hydro_force`.

## 4. Smoke Baseline

Command:

```powershell
cmd /c ""D:\working\taichi\env\python.exe" baseline_tests\run_lbm_refactored_smoke.py > logs\step2_lbm_refactor_smoke.log 2>&1"
```

Result:

```text
[OK] Step 2 refactored smoke baseline finished.
steps: 500
max_v_min: 3.000000e-02
max_v_max: 3.000000e-02
rho_min: 1.000000e+00
rho_max: 1.000001e+00
mass_total: 3.276802e+04
force_norm_max: 0.000000e+00
```

Output:

```text
outputs/lbm_refactored_smoke/LBMFluid_500.vtr
```

## 5. Poiseuille Baseline

Command:

```powershell
cmd /c ""D:\working\taichi\env\python.exe" baseline_tests\run_lbm_refactored_poiseuille.py > logs\step2_lbm_refactor_poiseuille.log 2>&1"
```

Result:

```text
[OK] Step 2 refactored Poiseuille baseline finished.
steps: 1000
final_max_v: 2.576960e-05
rho_min: 1.000000e+00
rho_max: 1.000100e+00
mean_ux: 1.500001e-05
center_ux: 2.041414e-05
near_wall_ux: 3.752902e-06
force_norm_max: 0.000000e+00
```

Output:

```text
outputs/lbm_refactored_poiseuille/LBMFluid_1000.vtr
```

## 6. Body-Force Baseline

Command:

```powershell
cmd /c ""D:\working\taichi\env\python.exe" baseline_tests\run_lbm_refactored_body_force.py > logs\step2_lbm_refactor_force.log 2>&1"
```

Result:

```text
[OK] Step 2 refactored body-force baseline finished.
steps: 1000
initial_max_v: 0.000000e+00
final_max_v: 1.123704e-04
rho_min: 1.000000e+00
rho_max: 1.000000e+00
mean_ux: 1.123704e-04
force_norm_max: 1.000000e-06
```

This test uses `set_uniform_cell_force(1e-6, 0, 0)` with zero global force, proving that the grid-local `cell_force` path reaches Guo forcing and updates the velocity field.

Output:

```text
outputs/lbm_refactored_force/LBMFluid_1000.vtr
```

## 7. Dynamic-Solid Dummy Baseline

Command:

```powershell
cmd /c ""D:\working\taichi\env\python.exe" baseline_tests\run_lbm_refactored_dynamic_solid_dummy.py > logs\step2_lbm_refactor_dynamic_solid.log 2>&1"
```

Result:

```text
[OK] Step 2 dynamic-solid dummy baseline finished.
solid_on_count: 512
phi_on_count: 512
reinit_count: 512
solid_off_count: 0
phi_off_count: 0
rho_min: 1.000000e+00
rho_max: 1.000000e+00
```

Outputs:

```text
outputs/lbm_refactored_dynamic_solid/LBMFluid_dynamic_on_0.vtr
outputs/lbm_refactored_dynamic_solid/LBMFluid_dynamic_off_1.vtr
```

## 8. VTK Field Check

Checked `outputs/lbm_refactored_smoke/LBMFluid_500.vtr`. Present fields:

```text
Solid
StaticSolid
rho
solid_phi
solid_mass
velocity
solid_vel
cell_force
hydro_force
```

## 9. Hard Acceptance Checklist

- [x] `src/lbm_fluid.py` exists
- [x] `src/lbm_config.py` exists
- [x] `LBMFluid3D` can initialize from `LBMConfig`
- [x] `init_geo()` can read original geometry format
- [x] `copy_solid_to_static()` runs
- [x] `init_simulation()` runs
- [x] Original step sequence remains intact
- [x] Zero `cell_force` smoke baseline completes
- [x] Refactored Poiseuille baseline completes
- [x] `set_uniform_cell_force()` produces a velocity response
- [x] Dynamic solid dummy baseline completes
- [x] `clear_coupling_fields()` clears `solid_phi`, `solid_mass`, `solid_vel`, `cell_force`, and `hydro_force`
- [x] `update_dynamic_solid()` changes `solid` based on `solid_phi`
- [x] `reinitialize_new_fluid_cells()` runs without NaN/Inf
- [x] `export_VTK()` writes `rho`, `velocity`, `solid_phi`, `cell_force`, and `hydro_force`
- [x] `get_stats()` returns `max_v`, `rho_min`, `rho_max`, `mass_total`, and `force_norm_max`
- [x] Logs are saved under `logs/`
- [x] Outputs are saved under `outputs/`
- [x] `STEP2_LBM_REFACTOR_REPORT.md` is complete
- [x] `pytest` passes

Numerical limits:

- [x] `rho_min > 0.95`
- [x] `rho_max < 1.05`
- [x] `max_v < 0.1`
- [x] no NaN
- [x] no Inf
- [x] no memory/runtime crash

## 10. Known Issues

- Taichi emits warnings about 19x19 matrix/vector compile-time unrolling. This matches the upstream MRT representation and is not changed in Step 2 because the contract forbids MRT matrix changes.
- `hydro_force` is only the Step 2 placeholder `-cell_force`; real hydrodynamic force, momentum exchange, moving bounce-back, immersed boundary, and MPM coupling are deferred.
- `set_spherical_cell_force()` is implemented for later diagnostics but is not part of the four required Step 2 baselines.

## 11. Decision

Can proceed to Step 3?

- [x] Yes
- [ ] No

Step 2 is complete as an LBM fluid backend refactor only. It does not claim real FSI.
