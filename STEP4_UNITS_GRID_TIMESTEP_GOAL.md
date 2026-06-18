# Step 4 Goal: Units, Grid, and Timestep Synchronization

## Paste-Ready `/goal`

```text
/goal
在 D:\working\squid robot\LBM\MPM-LBM 中执行 Step 4: Units, Grid, and Timestep Synchronization。详细执行合同以 D:\working\squid robot\LBM\MPM-LBM\STEP4_UNITS_GRID_TIMESTEP_GOAL.md 为唯一权威说明。

目标：在不做 MPM→LBM 投影、不做真实 FSI 的前提下，让 LBMFluid3D 和 MPMSolid3D 可以在同一个 simulation scaffold 中同时存在，使用同一个 cubic normalized domain、明确的 LBM/MPM 单位转换、确定的 MPM substep 与 LBM step 同步关系，并能在 dummy 主循环里独立稳定推进。

硬边界：不要把 MPM solid_phi 写进 LBM；不要计算 cell_force；不要计算或使用 hydro_force；不要写 penalty force；不要写 moving bounce-back；不要写 momentum exchange；不要做 immersed boundary；不要做两相流；不要使用 ReducedSquidFSI；不要改 external/taichi_LBM3D；不要把短探针冒充完整验收。

必须产物：src/sim_config.py、src/units.py、更新 src/__init__.py、baseline_tests/run_step4_units_consistency.py、baseline_tests/run_step4_shared_domain.py、baseline_tests/run_step4_time_sync_dummy.py、logs/step4_units_consistency.log、logs/step4_shared_domain.log、logs/step4_time_sync_dummy.log、outputs/step4_shared_domain/、outputs/step4_time_sync_dummy/、STEP4_UNITS_GRID_TIMESTEP_REPORT.md、tests/test_step4_units_grid_timestep_contract.py。

验收：完整执行 STEP4_UNITS_GRID_TIMESTEP_GOAL.md 的 Hard Acceptance Checklist。失败时停止并报告 exact command、log path、first failing error、失败类别、失败的验收项和下一步最小修复建议。完成后必须 pytest 通过，并把代码、日志、输出和报告推送到 GitHub。
```

## 1. Current Baseline

Step 3 is accepted and can be used as the starting point.

Existing completed modules:

```text
src/lbm_config.py
src/lbm_fluid.py
src/mpm_config.py
src/mpm_solid.py
```

Existing Step 3 evidence:

```text
STEP3_MPM_SOLID_REPORT.md
logs/step3_mpm_rest_block.log
logs/step3_mpm_falling_block.log
logs/step3_mpm_elastic_block.log
outputs/mpm_rest_block/particles_x.npy
outputs/mpm_falling_block/particles_x.npy
outputs/mpm_elastic_block/particles_x.npy
```

Step 3 validated:

```text
MPMSolid3D initializes a 3D block.
P2G, grid_update, G2P, F update, and J diagnostics run.
fixed-corotated elasticity is implemented.
rest/falling/elastic block baselines pass.
```

Carry-forward issue that Step 4 must solve:

```text
MPMSolid3D uses normalized [0, 1]^3 coordinates.
LBMFluid3D uses lattice-index grid coordinates.
```

Step 4 must make that relationship explicit before any projection or force coupling is attempted.

## 2. Objective

Implement:

```text
UnifiedSimConfig
GridUnitMapper
unit conversion baselines
shared-domain baseline
time-synchronized dummy co-simulation loop
```

The result must prove that LBM and MPM can be instantiated together with a shared grid size, shared normalized spatial convention, explicit unit conversions, and deterministic time synchronization.

Step 4 does not implement FSI. It only prepares a clean scaffold for later projection and coupling.

## 3. Workspace

Work in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Known Python environment:

```powershell
& 'D:\working\taichi\env\python.exe' ...
```

Validation should use Taichi CUDA for runtime baselines unless a check is static or NumPy-only.

## 4. Strict Non-Goals

Do not implement these in Step 4:

```text
1. No MPM -> LBM solid_phi projection.
2. No solid_vel projection.
3. No LBM cell_force computation.
4. No hydro_force computation or use.
5. No penalty force.
6. No moving bounce-back.
7. No momentum exchange.
8. No immersed boundary.
9. No two-phase flow.
10. No ReducedSquidFSI.
11. No squid geometry or real squid case.
12. No edits to external/taichi_LBM3D core files.
```

Any code that writes MPM data into LBM fields is out of scope for Step 4.

## 5. Required Final Structure

Create or update:

```text
src/
  __init__.py
  sim_config.py
  units.py

baseline_tests/
  run_step4_units_consistency.py
  run_step4_shared_domain.py
  run_step4_time_sync_dummy.py

outputs/
  step4_shared_domain/
  step4_time_sync_dummy/

logs/
  step4_units_consistency.log
  step4_shared_domain.log
  step4_time_sync_dummy.log

tests/
  test_step4_units_grid_timestep_contract.py

STEP4_UNITS_GRID_TIMESTEP_REPORT.md
```

Update `src/__init__.py` to export:

```python
from .sim_config import UnifiedSimConfig
from .units import GridUnitMapper

__all__ = [
    "LBMConfig",
    "LBMFluid3D",
    "MPMConfig",
    "MPMSolid3D",
    "UnifiedSimConfig",
    "GridUnitMapper",
]
```

## 6. Spatial Convention

Step 4 uses a cubic normalized domain only:

```text
normalized domain: [0, 1]^3
n_grid = nx = ny = nz
dx_norm = domain_length / n_grid
domain_length = 1.0 by default
```

MPM already uses:

```text
x_mpm in [0, 1]^3
dx_mpm = 1 / n_grid
```

LBM uses lattice indexing:

```text
i, j, k = 0, 1, ..., n_grid - 1
```

Mapping convention:

```text
x_lbm_coord = x_norm / dx_norm
i = floor(x_lbm_coord)
x_center_norm = (i + 0.5) * dx_norm
```

Do not support rectangular domains in Step 4:

```text
No nx != ny != nz.
No domain_x != domain_y != domain_z.
```

These can be added after projection and coupling are validated.

## 7. Time Convention

LBM lattice time step:

```text
dt_lbm_lattice = 1
```

MPM physical/normalized time step:

```text
mpm_dt = 4.0e-4
```

Step 4 defines:

```text
mpm_substeps_per_lbm_step = 10
lbm_dt_phys = mpm_substeps_per_lbm_step * mpm_dt
```

Default:

```text
n_grid = 32
mpm_dt = 4.0e-4
mpm_substeps_per_lbm_step = 10
lbm_dt_phys = 4.0e-3
```

Dummy synchronized loop:

```python
for lbm_step in range(n_lbm_steps):
    lbm.step()

    for _ in range(sim.mpm_substeps_per_lbm_step):
        solid.substep()
```

Step 4 does not exchange data between the solvers.

## 8. Unit Conversion Formulas

### 8.1 Position

```text
x_lbm = x_norm / dx_norm
x_norm = x_lbm * dx_norm
i = floor(x_norm / dx_norm)
x_center_norm = (i + 0.5) * dx_norm
```

### 8.2 Velocity

Normalized velocity:

```text
u_norm = normalized length / physical time
```

LBM lattice velocity:

```text
u_lbm = lattice cell / LBM step
```

Conversion:

```text
u_lbm = u_norm * lbm_dt_phys / dx_norm
u_norm = u_lbm * dx_norm / lbm_dt_phys
```

Example with defaults:

```text
n_grid = 32
dx_norm = 0.03125
lbm_dt_phys = 0.004
u_lbm = 0.03
u_norm = 0.03 * 0.03125 / 0.004 = 0.234375
```

### 8.3 Acceleration

Normalized acceleration:

```text
a_norm = normalized length / physical time^2
```

LBM lattice acceleration:

```text
a_lbm = lattice cell / LBM step^2
```

Conversion:

```text
a_lbm = a_norm * lbm_dt_phys^2 / dx_norm
a_norm = a_lbm * dx_norm / lbm_dt_phys^2
```

Example with defaults:

```text
a_norm = 9.8
a_lbm = 9.8 * 0.004^2 / 0.03125 = 0.0050176
```

### 8.4 Viscosity

```text
nu_lbm = nu_norm * lbm_dt_phys / dx_norm^2
nu_norm = nu_lbm * dx_norm^2 / lbm_dt_phys
```

Step 4 does not calibrate a physical fluid. It records the current LBM value:

```text
niu_lbm = 0.1
nu_norm = 0.1 * dx_norm^2 / lbm_dt_phys
```

## 9. `UnifiedSimConfig`

Create:

```text
src/sim_config.py
```

Implement:

```python
from dataclasses import dataclass


@dataclass
class UnifiedSimConfig:
    n_grid: int = 32

    domain_length: float = 1.0
    mpm_dt: float = 4.0e-4
    mpm_substeps_per_lbm_step: int = 10

    lbm_niu: float = 0.1
    lbm_rho0: float = 1.0

    @property
    def nx(self) -> int:
        return self.n_grid

    @property
    def ny(self) -> int:
        return self.n_grid

    @property
    def nz(self) -> int:
        return self.n_grid

    @property
    def dx_norm(self) -> float:
        return self.domain_length / self.n_grid

    @property
    def lbm_dt_phys(self) -> float:
        return self.mpm_substeps_per_lbm_step * self.mpm_dt
```

Optional helper methods are allowed:

```python
def make_lbm_config(self) -> LBMConfig:
    ...

def make_mpm_config(self, **overrides) -> MPMConfig:
    ...
```

If helper methods are added, they must preserve the Step 4 non-goals: no projection, no coupling.

## 10. `GridUnitMapper`

Create:

```text
src/units.py
```

Implement:

```python
from dataclasses import dataclass
import numpy as np


@dataclass
class GridUnitMapper:
    n_grid: int
    dx_norm: float
    lbm_dt_phys: float

    def norm_to_lbm_coord(self, x_norm):
        return np.asarray(x_norm) / self.dx_norm

    def lbm_coord_to_norm(self, x_lbm):
        return np.asarray(x_lbm) * self.dx_norm

    def norm_to_lbm_index(self, x_norm):
        idx = np.floor(self.norm_to_lbm_coord(x_norm)).astype(np.int32)
        return np.clip(idx, 0, self.n_grid - 1)

    def lbm_index_to_norm_center(self, idx):
        return (np.asarray(idx, dtype=np.float32) + 0.5) * self.dx_norm

    def velocity_norm_to_lbm(self, v_norm):
        return np.asarray(v_norm) * self.lbm_dt_phys / self.dx_norm

    def velocity_lbm_to_norm(self, v_lbm):
        return np.asarray(v_lbm) * self.dx_norm / self.lbm_dt_phys

    def acceleration_norm_to_lbm(self, a_norm):
        return np.asarray(a_norm) * self.lbm_dt_phys**2 / self.dx_norm

    def acceleration_lbm_to_norm(self, a_lbm):
        return np.asarray(a_lbm) * self.dx_norm / self.lbm_dt_phys**2

    def viscosity_norm_to_lbm(self, nu_norm):
        return float(nu_norm) * self.lbm_dt_phys / (self.dx_norm**2)

    def viscosity_lbm_to_norm(self, nu_lbm):
        return float(nu_lbm) * (self.dx_norm**2) / self.lbm_dt_phys
```

This file is the core Step 4 artifact.

## 11. Minimal Existing-Class Change

Add to `MPMSolid3D`:

```python
@ti.kernel
def set_uniform_velocity(self, vx: ti.f32, vy: ti.f32, vz: ti.f32):
    for p in range(self.n_particles):
        self.v[p] = ti.Vector([vx, vy, vz])
```

Purpose:

```text
1. Step 4 can validate velocity conversion.
2. Later moving-block tests can initialize known MPM velocities.
```

Optional:

```python
def set_gravity(self, gravity):
    self.gravity_x, self.gravity_y, self.gravity_z = gravity
```

Do not modify LBM collision, streaming, boundary, or force logic in Step 4.

## 12. Required Baselines

### 12.1 Unit Consistency

Create:

```text
baseline_tests/run_step4_units_consistency.py
```

Purpose:

```text
Verify all NumPy unit conversion formulas and round trips.
```

Settings:

```text
n_grid = 32
dx_norm = 1 / 32
mpm_dt = 4e-4
mpm_substeps_per_lbm_step = 10
lbm_dt_phys = 0.004
```

Required checks:

```text
position coordinate mapping
index clipping
cell center mapping
velocity round trip
acceleration round trip
viscosity round trip
example u_lbm=0.03 -> u_norm=0.234375
example a_norm=9.8 -> a_lbm=0.0050176
```

Acceptance:

```text
round-trip error < 1e-12 for velocity, acceleration, and viscosity
all formula examples logged
logs/step4_units_consistency.log exists
```

### 12.2 Shared Domain

Create:

```text
baseline_tests/run_step4_shared_domain.py
```

Purpose:

```text
Verify LBMConfig and MPMConfig can be generated from one UnifiedSimConfig and MPM particles map to valid LBM indices.
```

Required flow:

```text
1. Create UnifiedSimConfig(n_grid=32).
2. Create GridUnitMapper from sim.
3. Create LBMConfig from sim.
4. Create MPMConfig from sim.
5. Initialize LBMFluid3D and MPMSolid3D.
6. Initialize all-fluid LBM geometry.
7. Initialize MPM box.
8. Map every MPM particle position to an LBM index.
9. Save particle_lbm_indices.npy and particles_x.npy.
```

Hard boundary:

```text
Do not write indices into LBM solid_phi.
Do not write MPM velocity into LBM solid_vel.
```

Acceptance:

```text
LBM grid shape == MPM grid shape == 32^3
particle positions finite
all mapped indices are in [0, n_grid - 1]
index min/max are logged
outputs/step4_shared_domain/particle_lbm_indices.npy exists
outputs/step4_shared_domain/particles_x.npy exists
```

### 12.3 Time Sync Dummy

Create:

```text
baseline_tests/run_step4_time_sync_dummy.py
```

Purpose:

```text
Verify LBMFluid3D and MPMSolid3D can run in one synchronized main loop without exchanging data.
```

Settings:

```text
n_grid = 32
n_lbm_steps = 20
mpm_substeps_per_lbm_step = 10
mpm_dt = 4e-4
lbm_dt_phys = 0.004
MPM gravity = (0, 0, 0) recommended for rest-sync stability
LBM zero force or stable smoke settings
```

Required loop:

```python
total_mpm_substeps = 0
for lbm_step in range(n_lbm_steps + 1):
    if lbm_step > 0:
        lbm.step()

        for _ in range(sim.mpm_substeps_per_lbm_step):
            solid.substep()
            total_mpm_substeps += 1

    if lbm_step % output_interval == 0:
        lbm_stats = lbm.get_stats()
        mpm_stats = solid.get_stats()
        print(lbm_step, total_mpm_substeps, lbm_stats, mpm_stats)
```

Acceptance:

```text
completed 20 LBM steps
total_mpm_substeps = n_lbm_steps * mpm_substeps_per_lbm_step = 200
LBM rho_min > 0.95
LBM rho_max < 1.05
LBM max_v < 0.1
MPM min_J > 0
MPM max_speed < 10
no NaN/Inf
outputs/step4_time_sync_dummy/LBMFluid_20.vtr exists
outputs/step4_time_sync_dummy/particles_x.npy exists
outputs/step4_time_sync_dummy/particles_v.npy exists
outputs/step4_time_sync_dummy/particles_F.npy exists
outputs/step4_time_sync_dummy/particles_J.npy exists
```

## 13. Required Report

Create:

```text
STEP4_UNITS_GRID_TIMESTEP_REPORT.md
```

Report must include:

```text
1. Goal
2. Files created/updated
3. Chosen convention
4. Conversion formulas
5. Unit consistency command/result
6. Shared domain command/result
7. Time sync dummy command/result
8. Explicit non-goal confirmation: no projection, no FSI force
9. Hard Acceptance Checklist
10. Decision: can proceed to Step 5 or not
```

Report the chosen default values:

```text
n_grid
dx_norm
mpm_dt
mpm_substeps_per_lbm_step
lbm_dt_phys
lbm_niu
lbm_rho0
```

## 14. Pytest Contract

Create:

```text
tests/test_step4_units_grid_timestep_contract.py
```

Recommended tests:

```python
def test_step4_required_files_exist():
    ...

def test_units_round_trip_formulas_exist():
    ...

def test_step4_logs_record_success():
    ...

def test_step4_report_acceptance_complete():
    ...
```

At minimum, test for these source keywords:

```text
class UnifiedSimConfig
class GridUnitMapper
norm_to_lbm_coord
lbm_coord_to_norm
norm_to_lbm_index
lbm_index_to_norm_center
velocity_lbm_to_norm
velocity_norm_to_lbm
acceleration_lbm_to_norm
acceleration_norm_to_lbm
viscosity_lbm_to_norm
viscosity_norm_to_lbm
mpm_substeps_per_lbm_step
lbm_dt_phys
set_uniform_velocity
```

Log checks should verify:

```text
[OK] Step 4 units consistency baseline finished
[OK] Step 4 shared domain baseline finished
[OK] Step 4 time sync dummy baseline finished
total_mpm_substeps=200
```

## 15. Hard Acceptance Checklist

All must pass:

```text
[ ] main is on the Step 4 final commit
[ ] src/sim_config.py exists
[ ] src/units.py exists
[ ] src/__init__.py exports UnifiedSimConfig and GridUnitMapper
[ ] MPMSolid3D has set_uniform_velocity()
[ ] LBM and MPM use the same n_grid
[ ] nx = ny = nz = n_grid
[ ] dx_norm = 1 / n_grid
[ ] lbm_dt_phys = mpm_substeps_per_lbm_step * mpm_dt
[ ] position mapping works
[ ] velocity round trip works
[ ] acceleration round trip works
[ ] viscosity round trip works
[ ] LBMFluid3D and MPMSolid3D can initialize in one script
[ ] shared-domain particle indices are valid
[ ] synchronized dummy loop runs
[ ] total_mpm_substeps = n_lbm_steps * mpm_substeps_per_lbm_step
[ ] LBM rho remains stable
[ ] MPM min_J > 0
[ ] no NaN
[ ] no Inf
[ ] no MPM -> LBM projection is implemented
[ ] no FSI force coupling is implemented
[ ] logs are saved under logs/
[ ] outputs are saved under outputs/
[ ] STEP4_UNITS_GRID_TIMESTEP_REPORT.md is complete
[ ] pytest -q passes
```

Numerical thresholds:

```text
LBM:
  rho_min > 0.95
  rho_max < 1.05
  max_v < 0.1

MPM:
  min_J > 0
  max_speed < 10
  particle data finite

Mapping:
  round-trip error < 1e-12 for NumPy formulas
```

## 16. Recommended Execution Order

Follow this order:

```text
1. Add Step 4 pytest contract/artifact checks.
2. Run pytest and confirm RED for missing Step 4 artifacts.
3. Create src/sim_config.py.
4. Create src/units.py.
5. Export UnifiedSimConfig and GridUnitMapper from src/__init__.py.
6. Add MPMSolid3D.set_uniform_velocity().
7. Add run_step4_units_consistency.py and run it.
8. Add run_step4_shared_domain.py and run it.
9. Add run_step4_time_sync_dummy.py and run it.
10. Write STEP4_UNITS_GRID_TIMESTEP_REPORT.md.
11. Run final pytest.
12. Inspect git status and confirm external/ is unchanged.
13. Commit and push to GitHub.
```

Suggested commits:

```text
test: add step 4 units grid timestep contract
feat: add units grid timestep scaffold
```

## 17. Failure Handling

If any required baseline fails, stop and record:

```text
exact command
log path
first failing error
which acceptance item failed
whether failure is compile/import/runtime/numerical/output
next minimal fix
```

Do not reduce the required synchronized loop and call it complete. A shorter run may be used only as a clearly labeled diagnostic probe, followed by the full required run.

## 18. Completion Definition

Step 4 is complete only when:

```text
1. UnifiedSimConfig exists and defines cubic shared-domain defaults.
2. GridUnitMapper exists and passes position/velocity/acceleration/viscosity round-trip checks.
3. LBMFluid3D and MPMSolid3D can be created from one UnifiedSimConfig.
4. MPM particle positions map to valid LBM indices.
5. A synchronized dummy loop runs 20 LBM steps and 200 MPM substeps.
6. No projection or FSI force coupling is implemented.
7. Logs, outputs, and STEP4_UNITS_GRID_TIMESTEP_REPORT.md record evidence.
8. pytest passes.
9. The completed code, report, logs, and outputs are pushed to GitHub.
```

Completion does not mean MPM-LBM coupling exists. It only means the coordinate, unit, and timestep scaffold is ready for Step 5 projection work.
