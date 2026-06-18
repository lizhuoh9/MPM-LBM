# Step 3 Goal: Independent 3D MPM Solid Module

## Paste-Ready `/goal`

```text
/goal
在 D:\working\squid robot\LBM\MPM-LBM 中执行 Step 3: Independent 3D MPM Solid Module。详细执行合同以 D:\working\squid robot\LBM\MPM-LBM\STEP3_MPM_SOLID_GOAL.md 为唯一权威说明。

目标：在不接 LBM、不做真实 FSI 的前提下，把 Step 1 的 3D MPM smoke demo 工程化为 src/mpm_config.py 和 src/mpm_solid.py 中的 MPMConfig、MPMSolid3D。MPMSolid3D 必须能独立创建 3D MPM 粒子块、执行 P2G、grid update、边界处理、G2P、deformation gradient F 更新、fixed-corotated elastic material、gravity/external grid force placeholder、stats 和粒子输出。

前置小修正：先修 Step 2 的两个非 blocker 问题：1) 对 ti.i8 field 赋值显式 ti.cast，消除 i8 <- i32 warning；2) 给 LBMFluid3D.get_stats() 加 diagnostic-only 注释，说明它会执行 GPU->CPU NumPy 拷贝，不能在正式大算例每步调用。

硬边界：不要连接 LBMFluid3D；不要做 solid_phi 投影；不要写 penalty force；不要使用 hydro_force；不要写 fluid-solid momentum exchange；不要写 moving bounce-back；不要做 immersed boundary；不要做两相流；不要使用 ReducedSquidFSI；不要改 external/taichi_LBM3D；不要把短探针冒充完整验收。

必须产物：src/mpm_config.py、src/mpm_solid.py、更新 src/__init__.py、baseline_tests/run_mpm_rest_block.py、baseline_tests/run_mpm_falling_block.py、baseline_tests/run_mpm_elastic_block.py、logs/step3_mpm_rest_block.log、logs/step3_mpm_falling_block.log、logs/step3_mpm_elastic_block.log、outputs/mpm_rest_block/、outputs/mpm_falling_block/、outputs/mpm_elastic_block/、STEP3_MPM_SOLID_REPORT.md，并更新 pytest artifact/contract 检查。

验收：完整执行 STEP3_MPM_SOLID_GOAL.md 的 Hard Acceptance Checklist。失败时停止并报告 exact command、log path、first failing error、失败类别、失败的验收项和下一步最小修复建议。完成后必须 pytest 通过，并把代码、日志、输出和报告推送到 GitHub。
```

## 1. Current Baseline

Step 2 is accepted and can be used as the starting point. Existing completed modules:

```text
src/lbm_config.py
src/lbm_fluid.py
baseline_tests/run_lbm_refactored_smoke.py
baseline_tests/run_lbm_refactored_poiseuille.py
baseline_tests/run_lbm_refactored_body_force.py
baseline_tests/run_lbm_refactored_dynamic_solid_dummy.py
STEP2_LBM_REFACTOR_REPORT.md
```

Step 2 validated:

```text
LBMConfig exists and is exported.
LBMFluid3D exists and is exported.
Dense D3Q19 MRT fields are retained.
Coupling-ready fields exist: cell_force, solid_phi, solid_vel, hydro_force, reinit_flag.
cell_force -> cal_local_force -> Guo forcing -> velocity correction is active.
smoke / Poiseuille / body-force / dynamic-solid dummy baselines passed.
```

Known Step 2 cleanup before Step 3 implementation:

```text
1. Remove Taichi i8 <- i32 warnings by explicit casts in LBMFluid3D dynamic-solid kernels.
2. Document get_stats() as diagnostic-only because it copies Taichi fields to NumPy.
```

These cleanup items are required in this Step 3 goal because they reduce diagnostic noise before adding the MPM module.

## 2. Objective

Implement an independent 3D MPM solid module:

```text
MPMConfig
MPMSolid3D
standalone rest/falling/elastic block baselines
diagnostic stats and particle outputs
```

The Step 3 result must prove that the solid solver alone is stable, reusable, and diagnosable.

Step 3 must not implement FSI. It only prepares the solid side for later coupling.

## 3. Workspace

Work in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Known Python environment:

```powershell
& 'D:\working\taichi\env\python.exe' ...
```

Validation should use Taichi CUDA unless a specific check is static or CPU-only.

## 4. Strict Non-Goals

Do not implement these in Step 3:

```text
1. No coupling to LBMFluid3D.
2. No solid_phi projection.
3. No penalty force.
4. No hydro_force use.
5. No fluid-solid momentum exchange.
6. No moving bounce-back.
7. No immersed boundary.
8. No two-phase flow.
9. No ReducedSquidFSI.
10. No squid geometry or real squid case.
11. No edits to external/taichi_LBM3D core files.
```

If any implementation needs data from LBM or writes into LBM fields, it is out of scope for Step 3.

## 5. Required Final Structure

Create or update:

```text
src/
  __init__.py
  mpm_config.py
  mpm_solid.py

baseline_tests/
  run_mpm_rest_block.py
  run_mpm_falling_block.py
  run_mpm_elastic_block.py

outputs/
  mpm_rest_block/
  mpm_falling_block/
  mpm_elastic_block/

logs/
  step3_mpm_rest_block.log
  step3_mpm_falling_block.log
  step3_mpm_elastic_block.log

STEP3_MPM_SOLID_REPORT.md
```

Update:

```python
from .lbm_config import LBMConfig
from .lbm_fluid import LBMFluid3D
from .mpm_config import MPMConfig
from .mpm_solid import MPMSolid3D

__all__ = [
    "LBMConfig",
    "LBMFluid3D",
    "MPMConfig",
    "MPMSolid3D",
]
```

## 6. Step 2 Preflight Cleanup Requirements

### 6.1 Remove `i8 <- i32` Warnings

In `src/lbm_fluid.py`, update dynamic-solid assignments to use explicit casts:

```python
self.solid[I] = ti.cast(new_solid, ti.i8)
self.reinit_flag[I] = ti.cast(0, ti.i8)
self.reinit_flag[I] = ti.cast(1, ti.i8)
```

Acceptance:

```text
Dynamic-solid baseline log no longer contains "Assign may lose precision: i8 <- i32" from these fields.
```

### 6.2 Document `get_stats()`

Add a docstring or clear comment to `LBMFluid3D.get_stats()`:

```python
def get_stats(self):
    """
    Diagnostic-only. Do not call every production step because it copies fields to NumPy.
    """
```

Acceptance:

```text
The diagnostic-only warning is visible in src/lbm_fluid.py.
```

## 7. `MPMConfig`

Create:

```text
src/mpm_config.py
```

Suggested first version:

```python
from dataclasses import dataclass
from typing import Tuple


@dataclass
class MPMConfig:
    n_grid: int = 32
    dx: float = 1.0 / 32.0
    dt: float = 4.0e-4

    gravity: Tuple[float, float, float] = (0.0, -9.8, 0.0)

    p_rho: float = 1.0
    particles_per_cell: int = 2

    young_modulus: float = 400.0
    poisson_ratio: float = 0.2

    bound: int = 3
    use_apic: bool = True

    box_min: Tuple[float, float, float] = (0.25, 0.35, 0.25)
    box_max: Tuple[float, float, float] = (0.55, 0.65, 0.55)

    output_interval: int = 10
```

The values may be extended if needed, but keep the first implementation small and aligned with the Step 1 MPM smoke test.

## 8. `MPMSolid3D` Base Requirements

Create:

```text
src/mpm_solid.py
```

Implement:

```python
@ti.data_oriented
class MPMSolid3D:
    def __init__(self, config: MPMConfig, n_particles: int):
        ...
```

Required fields:

```text
config
dim = 3
n_grid
dx
inv_dx
dt
n_particles

particle fields:
  x: ti.Vector.field(3, ti.f32)
  v: ti.Vector.field(3, ti.f32)
  C: ti.Matrix.field(3, 3, ti.f32)
  F: ti.Matrix.field(3, 3, ti.f32)
  Jp: ti.field(ti.f32)
  mass: ti.field(ti.f32)
  vol0: ti.field(ti.f32)

grid fields:
  grid_v: ti.Vector.field(3, ti.f32)
  grid_m: ti.field(ti.f32)
  grid_f_ext: ti.Vector.field(3, ti.f32)

diagnostics:
  min_x: ti.Vector.field(3, ti.f32, shape=())
  max_x: ti.Vector.field(3, ti.f32, shape=())
  max_speed: ti.field(ti.f32, shape=())
  min_J: ti.field(ti.f32, shape=())
  max_J: ti.field(ti.f32, shape=())
  total_mass: ti.field(ti.f32, shape=())
```

The Step 1 smoke MPM used a scalar `J`; Step 3 should upgrade to full deformation gradient `F` while retaining `J = det(F)` diagnostics.

## 9. Required Kernels And Methods

Implement these interfaces:

```python
@ti.kernel
def init_box(self):
    ...

@ti.kernel
def clear_grid(self):
    ...

@ti.kernel
def p2g(self):
    ...

@ti.kernel
def grid_update(self):
    ...

@ti.kernel
def g2p(self):
    ...

def substep(self):
    self.clear_grid()
    self.p2g()
    self.grid_update()
    self.g2p()

def get_stats(self) -> dict:
    ...

def export_particles(self, out_dir: str, prefix: str):
    ...
```

Optional but useful:

```python
def export_particles_ply(self, frame: int, path: str):
    ...
```

### 9.1 `init_box()`

Initialize particles inside `config.box_min` to `config.box_max`.

First version may use random sampling. A later version can switch to regular sampling if needed.

Required initialization:

```text
x[p] in box
v[p] = 0
C[p] = zero matrix
F[p] = identity
Jp[p] = 1
mass[p] > 0
vol0[p] > 0
```

### 9.2 `clear_grid()`

Clear:

```text
grid_v
grid_m
grid_f_ext
```

### 9.3 `p2g()`

Implement APIC-style P2G using the same 3x3x3 quadratic B-spline stencil structure as the Step 1 MPM smoke test:

```text
Xp = x[p] * inv_dx
base = cast(Xp - 0.5, i32)
fx = Xp - base
weights = quadratic B-spline weights
loop over 27 neighboring grid nodes
```

P2G must transfer:

```text
particle mass
particle momentum
elastic stress
APIC affine C
```

### 9.4 Fixed-Corotated Elasticity

Use fixed-corotated hyperelastic material if stable:

```text
F = U Sigma V^T
R = U V^T
J = det(F)

mu = E / (2(1 + nu))
lambda = E * nu / ((1 + nu) * (1 - 2 * nu))

P = 2 * mu * (F - R) + lambda * (J - 1) * J * F^{-T}
stress = -dt * vol0[p] * P @ F[p].transpose() * inv_dx * inv_dx
affine = stress + mass[p] * C[p]
```

Taichi pattern:

```python
U, sig, V = ti.svd(self.F[p])
R = U @ V.transpose()
J = self.F[p].determinant()
```

If 3D `ti.svd()` or `F.inverse()` causes a compile/runtime blocker, use a clearly labeled fallback:

```text
Step 3A: scalar-J smoke-compatible model
Step 3B: upgrade to full F + fixed-corotated
```

Do not silently downgrade the final result. If the fallback is used, record it in `STEP3_MPM_SOLID_REPORT.md` and do not mark fixed-corotated acceptance as complete.

### 9.5 `grid_update()`

Required behavior:

```text
if grid_m[I] > 0:
    grid_v[I] /= grid_m[I]
    grid_v[I] += dt * gravity
    grid_v[I] += dt * grid_f_ext[I] / grid_m[I]
    apply domain boundary
```

`grid_f_ext` is only a placeholder in Step 3. It must remain zero in baseline scripts unless explicitly used by a standalone MPM diagnostic. It must not come from LBM.

### 9.6 Boundary Handling

Grid boundary must prevent particles from leaving the normalized `[0, 1]^3` domain.

At minimum:

```text
if I.x < bound and grid_v[I].x < 0: grid_v[I].x = 0
if I.x > n_grid - bound and grid_v[I].x > 0: grid_v[I].x = 0
same for y and z
```

Particle positions should remain finite and inside the domain, or be clamped consistently after G2P.

### 9.7 `g2p()`

Required behavior:

```text
new_v = sum(weight * grid_v)
new_C = 4 * inv_dx * inv_dx * sum(weight * grid_v outer dpos)
F[p] = (I + dt * new_C) @ F[p]
x[p] += dt * new_v
v[p] = new_v
C[p] = new_C
Jp[p] = det(F[p])
```

Must not produce NaN/Inf.

### 9.8 `get_stats()`

Return at least:

```python
{
    "min_x": ...,
    "max_x": ...,
    "max_speed": ...,
    "min_J": ...,
    "max_J": ...,
    "total_mass": ...,
}
```

Stats may use `.to_numpy()` in Step 3 baseline scripts. Add a comment/docstring that this is diagnostic-only and not for every production step in large GPU runs.

### 9.9 Particle Output

Each case must write final `.npy` diagnostics:

```text
particles_x.npy
particles_v.npy
particles_F.npy
particles_J.npy
```

Optional `.ply` point cloud output may be added for visualization, but `.npy` is sufficient for Step 3 acceptance.

## 10. Required Baselines

### 10.1 Rest Block

Create:

```text
baseline_tests/run_mpm_rest_block.py
```

Settings:

```text
gravity = (0, 0, 0)
initial velocity = 0
young_modulus = 400
poisson_ratio = 0.2
steps = 100
GPU backend
```

Acceptance:

```text
completed 100 steps
max_speed < 1e-5 preferred, small nonzero numerical noise acceptable if explained
min_J > 0
0.95 < min_J <= max_J < 1.05
particle positions finite
no NaN/Inf
outputs/mpm_rest_block/particles_x.npy exists
outputs/mpm_rest_block/particles_v.npy exists
outputs/mpm_rest_block/particles_F.npy exists
outputs/mpm_rest_block/particles_J.npy exists
```

### 10.2 Falling Block

Create:

```text
baseline_tests/run_mpm_falling_block.py
```

Settings:

```text
gravity = (0, -9.8, 0)
steps = 100
GPU backend
```

Acceptance:

```text
completed 100 steps
min_y decreases over time
max_speed increases from near zero
min_J > 0
particle positions finite
no NaN/Inf
outputs/mpm_falling_block/particles_x.npy exists
outputs/mpm_falling_block/particles_v.npy exists
outputs/mpm_falling_block/particles_F.npy exists
outputs/mpm_falling_block/particles_J.npy exists
```

### 10.3 Elastic Block

Create:

```text
baseline_tests/run_mpm_elastic_block.py
```

Settings:

```text
gravity = (0, -9.8, 0)
initial block high enough to fall/compress against bottom boundary
steps = 300 to 500
GPU backend
```

Acceptance:

```text
completed requested steps
particles remain finite
particles remain in domain or are boundary-limited
min_J > 0
max_speed < 10 hard limit
landing/compression is visible in stats, for example min_y reaches boundary zone and J changes from 1
no NaN/Inf
outputs/mpm_elastic_block/particles_x.npy exists
outputs/mpm_elastic_block/particles_v.npy exists
outputs/mpm_elastic_block/particles_F.npy exists
outputs/mpm_elastic_block/particles_J.npy exists
```

Step 3 does not require exact physical calibration. It requires a standalone stable solid module.

## 11. Required Report

Create:

```text
STEP3_MPM_SOLID_REPORT.md
```

Report must include:

```text
1. Goal
2. Step 2 preflight cleanup results
3. MPMConfig summary
4. MPMSolid3D field/kernel summary
5. Material model used: fixed-corotated or explicitly labeled fallback
6. Rest block command/result/stats/output path
7. Falling block command/result/stats/output path
8. Elastic block command/result/stats/output path
9. Known issues
10. Hard Acceptance Checklist
11. Decision: can proceed to Step 4 or not
```

Do not mark Step 3 complete on partial evidence.

## 12. Hard Acceptance Checklist

All must pass:

```text
[ ] Step 2 i8 warning cleanup implemented
[ ] LBMFluid3D.get_stats() diagnostic-only comment/docstring added
[ ] src/mpm_config.py exists
[ ] src/mpm_solid.py exists
[ ] src/__init__.py exports MPMConfig and MPMSolid3D
[ ] MPMSolid3D can initialize
[ ] init_box() generates a 3D solid block
[ ] clear_grid() runs
[ ] p2g() runs
[ ] grid_update() runs
[ ] g2p() runs
[ ] substep() runs
[ ] F[p] initializes to identity
[ ] J = det(F) is computed and exported/statistically reported
[ ] gravity can be disabled for rest block
[ ] gravity can be enabled for falling/elastic blocks
[ ] grid boundary prevents unbounded domain escape
[ ] run_mpm_rest_block.py completes
[ ] run_mpm_falling_block.py completes
[ ] run_mpm_elastic_block.py completes
[ ] logs are saved under logs/
[ ] outputs are saved under outputs/
[ ] particle_x/v/F/J .npy outputs exist for each baseline
[ ] STEP3_MPM_SOLID_REPORT.md is complete
[ ] pytest passes
```

Numerical hard limits:

```text
[ ] no NaN
[ ] no Inf
[ ] min_J > 0
[ ] max_speed < 10
[ ] particle positions remain finite
[ ] particles remain inside [0, 1]^3 or are boundary-limited with documented clamping
```

## 13. Recommended Execution Order

Follow this order unless a compile/runtime blocker requires a narrower diagnostic probe:

```text
1. Add Step 3 pytest contract/artifact checks.
2. Run pytest and confirm RED for missing Step 3 artifacts.
3. Fix Step 2 i8 casts.
4. Add diagnostic-only comment to LBMFluid3D.get_stats().
5. Create src/mpm_config.py.
6. Create src/mpm_solid.py with fields and empty method skeletons.
7. Implement init_box().
8. Implement clear_grid().
9. Port Step 1 MPM quadratic B-spline P2G/G2P structure.
10. Implement deformation gradient F update.
11. Implement fixed-corotated elasticity.
12. Implement grid_update() and boundary handling.
13. Implement get_stats().
14. Implement export_particles().
15. Add run_mpm_rest_block.py and run it.
16. Add run_mpm_falling_block.py and run it.
17. Add run_mpm_elastic_block.py and run it.
18. Write STEP3_MPM_SOLID_REPORT.md.
19. Run final pytest.
20. Inspect git status and external/ tree.
21. Commit and push to GitHub.
```

Suggested commit split:

```text
commit A: test: add step 3 mpm solid contract
commit B: feat: add standalone mpm solid module
```

If fixed-corotated implementation is risky:

```text
commit B1: add scalar-J smoke-compatible MPMSolid3D
commit B2: upgrade MPMSolid3D to full F fixed-corotated elasticity
```

## 14. Failure Handling

If any required baseline fails, stop and record:

```text
exact command
log path
first failing error
which acceptance item failed
whether failure is compile/import/runtime/numerical/output
next minimal fix
```

Do not reduce the required steps and call it complete. A shorter run may be used only as a clearly labeled diagnostic probe, followed by the full required run.

## 15. Completion Definition

Step 3 is complete only when:

```text
1. Step 2 preflight cleanup is done.
2. MPMConfig and MPMSolid3D exist and are exported.
3. The MPM solid can initialize a 3D block.
4. P2G, grid update, boundary handling, G2P, F update, and J diagnostics run.
5. Rest, falling, and elastic block baselines complete on GPU.
6. Outputs include particle x, v, F, and J arrays.
7. STEP3_MPM_SOLID_REPORT.md records evidence and decision.
8. pytest passes.
9. The completed code, report, logs, and outputs are pushed to GitHub.
```

Completion does not mean real FSI exists. It only means the standalone MPM solid backend is ready for later projection/coupling steps.
