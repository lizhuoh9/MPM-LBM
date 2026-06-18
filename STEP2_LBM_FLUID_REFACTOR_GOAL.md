# Step 2 Goal: LBM Fluid Module Refactor

## Paste-Ready `/goal`

```text
/goal
在 D:\working\squid robot\LBM\MPM-LBM 中执行 Step 2: LBM Fluid Module Refactor。详细执行合同以 D:\working\squid robot\LBM\MPM-LBM\STEP2_LBM_FLUID_REFACTOR_GOAL.md 为唯一权威说明。

目标：把 external/taichi_LBM3D/Single_phase/LBM_3D_SinglePhase_Solver.py 复制并重构为 src/lbm_fluid.py 中的 LBMFluid3D；新增 src/lbm_config.py；保留原始 D3Q19 MRT 单相 LBM 物理和 step 顺序；增加 cell_force、hydro_force、solid_phi、solid_vel、static_solid、old_solid、reinit_flag、stats、扩展 VTK 和三类 Step 2 baseline。

硬边界：不要实现 MPM；不要做真实 FSI；不要写粒子到网格投影；不要写 penalty coupling、immersed boundary、moving bounce-back 或 momentum exchange；不要使用 ReducedSquidFSI；不要改 external/taichi_LBM3D 核心文件；不要改 MRT 矩阵、D3Q19 速度集合或原始 streaming/bounce-back 物理；不要启用 sparse storage、two-phase、grey-scale 或 phase-change solver。

必须产物：src/lbm_config.py、src/lbm_fluid.py、baseline_tests/run_lbm_refactored_smoke.py、baseline_tests/run_lbm_refactored_poiseuille.py、baseline_tests/run_lbm_refactored_body_force.py、baseline_tests/run_lbm_refactored_dynamic_solid_dummy.py、logs/step2_lbm_refactor_smoke.log、logs/step2_lbm_refactor_poiseuille.log、logs/step2_lbm_refactor_force.log、logs/step2_lbm_refactor_dynamic_solid.log、outputs/lbm_refactored_smoke/、outputs/lbm_refactored_poiseuille/、outputs/lbm_refactored_force/、outputs/lbm_refactored_dynamic_solid/、STEP2_LBM_REFACTOR_REPORT.md。

验收：完整执行 STEP2_LBM_FLUID_REFACTOR_GOAL.md 的 Hard Acceptance Checklist。失败时停止并报告 exact command、log path、first failing error、失败类别、失败的验收项和下一步最小修复建议。不要把短探针冒充完整 Step 2 验收。
```

## 1. Objective

Refactor the vendored `taichi_LBM3D` single-phase D3Q19 MRT solver into a coupling-ready LBM fluid module.

The original solver is an independent example-style solver:

```text
static geometry + single-phase LBM solver
```

Step 2 must turn it into:

```text
LBMFluid3D fluid backend
+ external solid projection fields
+ grid-local coupling force input
+ placeholder hydrodynamic reaction force output
```

This step must not change the LBM physical model. It must preserve the original D3Q19 MRT collision/streaming behavior while adding interfaces required by later MPM-LBM coupling.

## 2. Workspace And Source

Work in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Original upstream solver:

```text
external/taichi_LBM3D/Single_phase/LBM_3D_SinglePhase_Solver.py
```

Refactored local module:

```text
src/lbm_fluid.py
```

Do not edit the original upstream file under `external/taichi_LBM3D/Single_phase/`.

Step 1 baseline evidence already exists and should remain valid:

```text
STEP1_BASELINE_REPORT.md
logs/check_taichi_backend.log
logs/lbm_smoke_baseline.log
logs/lbm_poiseuille_baseline.log
logs/mpm3d_baseline.log
outputs/lbm_smoke/LB_SingelPhase_500.vtr
outputs/lbm_poiseuille/LB_SingelPhase_1000.vtr
outputs/mpm3d/mpm3d_positions.npy
```

Use the known working Python environment:

```powershell
& 'D:\working\taichi\env\python.exe' ...
```

GPU support is expected. Step 2 validation should run with Taichi CUDA unless a script explicitly performs a CPU-only static check.

## 3. Strict Non-Goals

Do not implement these in Step 2:

```text
1. No MPM solid module.
2. No particle-to-grid projection.
3. No real penalty coupling.
4. No immersed-boundary coupling.
5. No moving bounce-back.
6. No momentum-exchange force model.
7. No squid case or real squid geometry.
8. No ReducedSquidFSI.
9. No two-phase, grey-scale, or phase-change solver.
10. No sparse storage.
11. No D3Q19 velocity-set changes.
12. No MRT matrix changes.
13. No changes to external/taichi_LBM3D core solver files.
```

The only allowed physics-facing change is adding a grid-local force path that is zero by default and therefore should not change zero-force baseline behavior.

## 4. Required Final Structure

Create or update:

```text
src/
  __init__.py
  lbm_config.py
  lbm_fluid.py

baseline_tests/
  run_lbm_refactored_smoke.py
  run_lbm_refactored_poiseuille.py
  run_lbm_refactored_body_force.py
  run_lbm_refactored_dynamic_solid_dummy.py

outputs/
  lbm_refactored_smoke/
  lbm_refactored_poiseuille/
  lbm_refactored_force/
  lbm_refactored_dynamic_solid/

logs/
  step2_lbm_refactor_smoke.log
  step2_lbm_refactor_poiseuille.log
  step2_lbm_refactor_force.log
  step2_lbm_refactor_dynamic_solid.log

STEP2_LBM_REFACTOR_REPORT.md
```

Existing Step 1 files must remain intact.

## 5. `LBMConfig`

Create:

```text
src/lbm_config.py
```

Implement:

```python
from dataclasses import dataclass
from typing import Tuple


@dataclass
class LBMConfig:
    nx: int
    ny: int
    nz: int

    niu: float = 0.1
    rho0: float = 1.0
    sparse_storage: bool = False

    force: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    bc_x_left: int = 0
    bc_x_right: int = 0
    bc_y_left: int = 0
    bc_y_right: int = 0
    bc_z_left: int = 0
    bc_z_right: int = 0

    rho_bc_x_left: float = 1.0
    rho_bc_x_right: float = 1.0
    rho_bc_y_left: float = 1.0
    rho_bc_y_right: float = 1.0
    rho_bc_z_left: float = 1.0
    rho_bc_z_right: float = 1.0

    vel_bc_x_left: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    vel_bc_x_right: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    vel_bc_y_left: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    vel_bc_y_right: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    vel_bc_z_left: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    vel_bc_z_right: Tuple[float, float, float] = (0.0, 0.0, 0.0)
```

First version may support only:

```python
fluid = LBMFluid3D(config)
```

Direct `LBMFluid3D(nx=..., ny=..., nz=...)` compatibility is optional.

## 6. `LBMFluid3D` Base Requirements

Create `src/lbm_fluid.py` by copying the original upstream solver once, then refactor the local copy.

Rename:

```python
@ti.data_oriented
class LB3D_Solver_Single_Phase:
```

to:

```python
@ti.data_oriented
class LBMFluid3D:
```

Do not subclass the upstream solver. Taichi data-oriented classes, fields, and kernels are easier to validate when copied and refactored directly.

`LBMFluid3D.__init__()` must accept an `LBMConfig`.

Dense storage only:

```python
if config.sparse_storage:
    raise NotImplementedError(
        "Step 2 only supports dense storage. Enable sparse storage after FSI coupling is validated."
    )
```

Keep original core fields:

```text
f, F, rho, v, solid
e, e_f, w
M, inv_M, S_dig, LR
max_v
```

Keep original step order:

```python
def step(self):
    self.colission()
    self.streaming1()
    self.Boundary_condition()
    self.streaming3()
```

Do not change static bounce-back or boundary physics in Step 2.

## 7. New Coupling-Ready Fields

Add dense fields:

```python
self.static_solid = ti.field(ti.i8, shape=(nx, ny, nz))
self.old_solid = ti.field(ti.i8, shape=(nx, ny, nz))

self.solid_phi = ti.field(ti.f32, shape=(nx, ny, nz))
self.solid_mass = ti.field(ti.f32, shape=(nx, ny, nz))
self.solid_vel = ti.Vector.field(3, ti.f32, shape=(nx, ny, nz))

self.cell_force = ti.Vector.field(3, ti.f32, shape=(nx, ny, nz))
self.hydro_force = ti.Vector.field(3, ti.f32, shape=(nx, ny, nz))

self.reinit_flag = ti.field(ti.i8, shape=(nx, ny, nz))
```

Also add stats fields:

```python
self.rho_min = ti.field(ti.f32, shape=())
self.rho_max = ti.field(ti.f32, shape=())
self.mass_total = ti.field(ti.f32, shape=())
self.force_norm_max = ti.field(ti.f32, shape=())
```

Field meanings:

```text
static_solid  = fixed geometry from initial solid mask
old_solid     = previous-step solid mask
solid_phi     = later MPM solid volume fraction, dummy-filled in Step 2
solid_mass    = later MPM projected mass, dummy-filled in Step 2
solid_vel     = later MPM projected solid velocity, dummy-filled in Step 2
cell_force    = grid-local force applied to LBM
hydro_force   = placeholder reaction force exported for later solid side
reinit_flag   = solid-to-fluid reinitialization marker
```

## 8. Force Path Requirements

Refactor:

```python
@ti.func
def cal_local_force(self, i, j, k):
    return ti.Vector([self.fx, self.fy, self.fz]) + self.cell_force[i, j, k]
```

The force path must work when global `force=(0,0,0)` but `cell_force[i,j,k]` is nonzero.

The original solver uses `force_flag` and `ti.static(self.force_flag == 1)`. That static branch must not disable local force coupling.

Required behavior:

```text
1. Guo force logic is compiled regardless of initial global force.
2. If global force and cell_force are zero, force contribution is zero.
3. If cell_force is nonzero after initialization, it affects collision and velocity correction.
```

Do not keep a static compile-time branch that can remove local force logic.

## 9. Required New Kernels And Methods

Implement these interfaces:

```python
def init_geo(self, filename: str):
    ...

def init_simulation(self):
    ...

def step(self):
    ...

def export_VTK(self, n: int, out_prefix: str = "./LBMFluid"):
    ...

def get_stats(self) -> dict:
    ...

@ti.kernel
def clear_coupling_fields(self):
    ...

@ti.kernel
def copy_solid_to_static(self):
    ...

@ti.kernel
def update_dynamic_solid(self, threshold: ti.f32):
    ...

@ti.kernel
def reinitialize_new_fluid_cells(self):
    ...

@ti.kernel
def set_uniform_cell_force(self, fx: ti.f32, fy: ti.f32, fz: ti.f32):
    ...

@ti.kernel
def set_spherical_cell_force(
    self,
    cx: ti.f32,
    cy: ti.f32,
    cz: ti.f32,
    radius: ti.f32,
    fx: ti.f32,
    fy: ti.f32,
    fz: ti.f32,
):
    ...

@ti.kernel
def set_dummy_solid_phi_block(
    self,
    x0: ti.i32,
    x1: ti.i32,
    y0: ti.i32,
    y1: ti.i32,
    z0: ti.i32,
    z1: ti.i32,
):
    ...

@ti.kernel
def build_dummy_hydro_force(self):
    ...
```

### 9.1 `clear_coupling_fields`

Must clear:

```text
solid_phi
solid_mass
solid_vel
cell_force
hydro_force
reinit_flag
```

Do not clear `static_solid`.

### 9.2 `copy_solid_to_static`

After `init_geo()`, copy initial `solid` into both:

```text
static_solid
old_solid
```

### 9.3 `update_dynamic_solid`

Required semantics:

```text
old_solid = previous solid
dynamic solid = solid_phi >= threshold
solid = static_solid OR dynamic solid
reinit_flag = 1 only for solid -> fluid cells
```

### 9.4 `reinitialize_new_fluid_cells`

For cells with `reinit_flag == 1`:

```text
rho = rho0
v = solid_vel if nonzero, otherwise zero
f and F reset to feq(rho0, v)
reinit_flag reset to 0
```

Must not produce NaN or Inf.

### 9.5 `set_uniform_cell_force`

Set `cell_force=(fx,fy,fz)` only where `solid == 0`; set zero force inside solid cells.

### 9.6 `set_spherical_cell_force`

Set force inside a spherical region and only on fluid cells.

### 9.7 `set_dummy_solid_phi_block`

For testing only. It should fill a rectangular block:

```text
solid_phi = 1.0
solid_vel = (0.01, 0.0, 0.0)
```

### 9.8 `build_dummy_hydro_force`

Step 2 placeholder only:

```python
self.hydro_force[I] = -self.cell_force[I]
```

Make clear in comments/report that real hydrodynamic reaction force is deferred.

## 10. VTK Output Requirements

`export_VTK(n, out_prefix)` must output at least:

```text
Solid
StaticSolid
rho
velocity
solid_phi
solid_mass
solid_vel
cell_force
hydro_force
```

Use output prefix names like:

```text
outputs/lbm_refactored_smoke/LBMFluid
outputs/lbm_refactored_poiseuille/LBMFluid
outputs/lbm_refactored_force/LBMFluid
outputs/lbm_refactored_dynamic_solid/LBMFluid
```

The old misspelled name `LB_SingelPhase` does not need to be used for new outputs.

## 11. Statistics Requirements

Implement:

```python
def get_stats(self) -> dict:
    return {
        "max_v": ...,
        "rho_min": ...,
        "rho_max": ...,
        "mass_total": ...,
        "force_norm_max": ...,
    }
```

Stats should only include fluid cells where appropriate.

Must be used by Step 2 baseline scripts and recorded in logs.

## 12. Required Baseline Scripts

### 12.1 Refactored All-Fluid Smoke

Create:

```text
baseline_tests/run_lbm_refactored_smoke.py
```

Purpose:

```text
Verify that zero cell_force keeps the refactored solver close to the Step 1 all-fluid smoke behavior.
```

Settings:

```text
nx = ny = nz = 32
steps = 500
cell_force = 0
small velocity boundary comparable to Step 1
GPU backend
```

Must write:

```text
logs/step2_lbm_refactor_smoke.log
outputs/lbm_refactored_smoke/*.vtr
```

Acceptance:

```text
completed 500 steps
max_v finite
rho_min finite
rho_max finite
VTK exists
max_v order comparable to Step 1 LBM baseline
rho_min > 0.95
rho_max < 1.05
max_v < 0.05 preferred, max_v < 0.1 hard limit
no NaN/Inf
```

### 12.2 Refactored Poiseuille

Create:

```text
baseline_tests/run_lbm_refactored_poiseuille.py
```

Purpose:

```text
Verify that the refactored solver preserves the Step 1 pressure-driven channel-flow baseline.
```

Settings:

```text
pressure-driven x-channel
y/z solid walls
rho_in=1.0001, rho_out=1.0 or equivalent small pressure difference
steps = 1000
GPU backend
```

Must write:

```text
logs/step2_lbm_refactor_poiseuille.log
outputs/lbm_refactored_poiseuille/*.vtr
```

Acceptance:

```text
completed 1000 steps
rho_min > 0.95
rho_max < 1.05
max_v < 0.05 preferred, max_v < 0.1 hard limit
centerline ux > near-wall ux
VTK exists
no NaN/Inf
```

### 12.3 Uniform Body Force

Create:

```text
baseline_tests/run_lbm_refactored_body_force.py
```

Purpose:

```text
Verify that cell_force -> cal_local_force -> Guo forcing -> velocity field is active.
```

Settings:

```text
periodic or simple channel domain
force = (1e-6, 0, 0)
steps = 1000
GPU backend
```

Must write:

```text
logs/step2_lbm_refactor_force.log
outputs/lbm_refactored_force/*.vtr
```

Acceptance:

```text
completed 1000 steps
max_v increases from near zero
force_norm_max approximately 1e-6
velocity direction mainly x
rho_min > 0.95
rho_max < 1.05
max_v < 0.05 preferred, max_v < 0.1 hard limit
no NaN/Inf
```

### 12.4 Dynamic Solid Dummy

Create:

```text
baseline_tests/run_lbm_refactored_dynamic_solid_dummy.py
```

Purpose:

```text
Verify solid_phi can update solid mask and trigger solid-to-fluid reinitialization.
```

Flow:

```text
1. initialize all-fluid or simple geometry
2. copy_solid_to_static()
3. clear_coupling_fields()
4. set_dummy_solid_phi_block(12,20,12,20,12,20)
5. update_dynamic_solid(threshold=0.5)
6. export VTK with dynamic solid block
7. clear_coupling_fields()
8. update_dynamic_solid(threshold=0.5)
9. reinitialize_new_fluid_cells()
10. export VTK after clearing dynamic solid
```

Must write:

```text
logs/step2_lbm_refactor_dynamic_solid.log
outputs/lbm_refactored_dynamic_solid/*.vtr
```

Acceptance:

```text
solid_phi block appears in VTK
Solid field becomes 1 in block
clear_coupling_fields clears solid_phi
dynamic block returns to fluid after update_dynamic_solid
solid -> fluid cells are reinitialized without NaN/Inf
```

## 13. Recommended Execution Order

Follow this order unless a blocking compile/runtime issue requires a narrower probe:

```text
1. Create src/__init__.py.
2. Create src/lbm_config.py.
3. Copy upstream solver to src/lbm_fluid.py.
4. Rename class to LBMFluid3D.
5. Convert constructor to LBMConfig.
6. Disable sparse_storage.
7. Keep original step order and run a small import/initialization check.
8. Add coupling fields.
9. Add stats fields.
10. Modify cal_local_force().
11. Remove force_flag static shielding from force branch.
12. Add clear_coupling_fields().
13. Add copy_solid_to_static().
14. Add update_dynamic_solid().
15. Add reinitialize_new_fluid_cells().
16. Add set_uniform_cell_force().
17. Add set_spherical_cell_force().
18. Add set_dummy_solid_phi_block().
19. Add build_dummy_hydro_force().
20. Extend export_VTK().
21. Add get_stats().
22. Add refactored smoke script and run it.
23. Add refactored Poiseuille script and run it.
24. Add uniform body-force script and run it.
25. Add dynamic-solid dummy script and run it.
26. Update pytest artifact checks if useful.
27. Write STEP2_LBM_REFACTOR_REPORT.md.
28. Run final pytest.
29. Inspect git status and summarize changed files.
```

## 14. Required Report

Create:

```text
STEP2_LBM_REFACTOR_REPORT.md
```

The report must include:

```text
1. Goal
2. Original source file
3. Refactored source file
4. Main changes checklist
5. Smoke command/result/stats/output path
6. Poiseuille command/result/stats/output path
7. Body-force command/result/stats/output path
8. Dynamic-solid dummy command/result/output path
8. Known issues
9. Decision: can proceed to Step 3 or not
```

The decision may be "No" if any hard acceptance item fails. Do not mark Step 2 complete on partial evidence.

## 15. Hard Acceptance Checklist

All must pass:

```text
[ ] src/lbm_fluid.py exists
[ ] src/lbm_config.py exists
[ ] LBMFluid3D can initialize from LBMConfig
[ ] init_geo() can read original geometry format
[ ] copy_solid_to_static() runs
[ ] init_simulation() runs
[ ] original step sequence remains intact
[ ] zero cell_force smoke baseline completes
[ ] refactored Poiseuille baseline completes
[ ] set_uniform_cell_force() produces a reasonable velocity response
[ ] clear_coupling_fields() clears solid_phi, solid_mass, solid_vel, cell_force, hydro_force
[ ] update_dynamic_solid() changes solid based on solid_phi
[ ] reinitialize_new_fluid_cells() runs without NaN/Inf
[ ] export_VTK() writes rho, velocity, solid_phi, cell_force, hydro_force
[ ] get_stats() returns max_v, rho_min, rho_max, mass_total, force_norm_max
[ ] logs are saved under logs/
[ ] outputs are saved under outputs/
[ ] STEP2_LBM_REFACTOR_REPORT.md is complete
[ ] pytest passes
```

Numerical hard limits:

```text
[ ] rho_min > 0.95
[ ] rho_max < 1.05
[ ] max_v < 0.1
[ ] no NaN
[ ] no Inf
[ ] no memory/runtime crash
```

Preferred stricter target:

```text
max_v < 0.05
```

## 16. Failure Handling

If a script fails, stop and record:

```text
exact command
log path
first failing error
which acceptance item failed
whether failure is compile/import/runtime/numerical/output
next minimal fix
```

Do not hide a failure by reducing validation below the stated step count unless explicitly labeling it as a diagnostic probe and then returning to the required run.

## 17. Completion Definition

Step 2 is complete only when:

```text
1. The refactored LBMFluid3D module exists.
2. Zero-force behavior is validated against Step 1 scale.
3. Local cell_force is proven active.
4. Dynamic solid mask/reinitialization interfaces compile and pass dummy validation.
5. VTK output includes the new coupling fields.
6. STEP2_LBM_REFACTOR_REPORT.md records evidence and decision.
7. pytest passes.
```

This completion does not mean real FSI exists. It only means the LBM fluid backend is ready for Step 3 and later coupling work.
