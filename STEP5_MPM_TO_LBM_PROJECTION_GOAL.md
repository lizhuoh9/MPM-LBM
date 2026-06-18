# Step 5 Goal: MPM-to-LBM Projection

## Paste-Ready `/goal`

```text
/goal
In D:\working\squid robot\LBM\MPM-LBM, execute Step 5: MPM-to-LBM Projection. The only authoritative execution contract is D:\working\squid robot\LBM\MPM-LBM\STEP5_MPM_TO_LBM_PROJECTION_GOAL.md.

Goal: project MPM solid particle fields into LBM grid diagnostic/coupling-preparation fields only: solid_phi, solid_mass, and solid_vel. Use the Step 4 UnifiedSimConfig and GridUnitMapper conventions. solid_vel must be converted from normalized MPM velocity to LBM lattice velocity. Do not implement force coupling.

Hard boundaries: no cell_force computation, no hydro_force computation or use, no penalty force, no moving bounce-back, no momentum exchange, no immersed boundary, no two-phase flow, no ReducedSquidFSI, no real squid geometry, no edits to external/taichi_LBM3D, and no short probe reported as complete acceptance.

Required artifacts, execution order, baseline settings, Hard Acceptance Checklist, failure handling, and completion definition are all defined in STEP5_MPM_TO_LBM_PROJECTION_GOAL.md. Finish only after pytest passes and code, logs, outputs, and report are pushed to GitHub.
```

## 1. Current Baseline

Step 4 is accepted and is the starting point.

Existing Step 4 modules:

```text
src/lbm_config.py
src/lbm_fluid.py
src/mpm_config.py
src/mpm_solid.py
src/sim_config.py
src/units.py
```

Step 4 validated:

```text
UnifiedSimConfig creates shared cubic LBM/MPM configs.
GridUnitMapper converts positions, velocities, accelerations, and viscosity.
MPMSolid3D has set_uniform_velocity().
LBMFluid3D and MPMSolid3D can coexist in one dummy synchronized loop.
20 LBM steps and 200 MPM substeps run without data exchange.
No MPM -> LBM projection or force coupling exists yet.
```

Step 4 evidence:

```text
STEP4_UNITS_GRID_TIMESTEP_REPORT.md
logs/step4_units_consistency.log
logs/step4_shared_domain.log
logs/step4_time_sync_dummy.log
outputs/step4_shared_domain/particle_lbm_indices.npy
outputs/step4_shared_domain/particles_x.npy
outputs/step4_time_sync_dummy/LBMFluid_20.vtr
```

Carry-forward issue that Step 5 must solve:

```text
LBM currently cannot see where the MPM solid is.
LBM solid_phi, solid_mass, and solid_vel exist, but Step 4 intentionally did not populate them from MPM.
```

## 2. Objective

Implement:

```text
MPMToLBMProjector3D
MPM particle -> LBM solid_phi projection
MPM particle -> LBM solid_mass projection
MPM particle velocity -> LBM solid_vel projection with correct velocity units
projection diagnostics and conservation checks
static block projection baseline
moving block velocity projection baseline
projection after MPM motion baseline
dynamic solid mask dry-run baseline
```

The result must prove that LBM can see an MPM solid as grid fields:

```text
solid_phi  = solid volume fraction in each LBM cell, clamped to [0, 1]
solid_mass = projected MPM mass in each LBM cell
solid_vel  = projected MPM velocity in LBM lattice velocity units
```

Step 5 does not implement FSI. It only populates LBM solid diagnostic/coupling-preparation fields.

## 3. Workspace

Work in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Known Python environment:

```powershell
& 'D:\working\taichi\env\python.exe' ...
```

Runtime baselines should use Taichi CUDA:

```python
ti.init(arch=ti.gpu, default_fp=ti.f32)
```

## 4. Strict Non-Goals

Do not implement these in Step 5:

```text
1. No LBM cell_force computation from MPM.
2. No hydro_force computation or use.
3. No penalty force.
4. No moving bounce-back.
5. No momentum exchange.
6. No immersed boundary.
7. No two-phase flow.
8. No ReducedSquidFSI.
9. No real squid geometry or real squid case.
10. No edits to external/taichi_LBM3D core files.
11. No LBM step that claims a physical FSI response.
```

Allowed in Step 5:

```text
write lbm.solid_phi
write lbm.solid_mass
write lbm.solid_vel
read lbm.cell_force and lbm.hydro_force only to verify they remain zero
optionally call update_dynamic_solid() and reinitialize_new_fluid_cells() in a clearly labeled dry run
```

The dynamic solid mask dry run is not FSI and must not be presented as FSI.

## 5. Required Final Structure

Create or update:

```text
src/
  __init__.py
  lbm_fluid.py
  projection.py

baseline_tests/
  run_step5_projection_static_block.py
  run_step5_projection_moving_block.py
  run_step5_projection_after_mpm_motion.py
  run_step5_dynamic_solid_mask_dryrun.py

outputs/
  step5_projection_static/
  step5_projection_moving/
  step5_projection_motion/
  step5_dynamic_solid_mask/

logs/
  step5_projection_static.log
  step5_projection_moving.log
  step5_projection_motion.log
  step5_dynamic_solid_mask.log

tests/
  test_step5_projection_contract.py

STEP5_MPM_TO_LBM_PROJECTION_REPORT.md
```

Update `src/__init__.py` to export:

```python
from .projection import MPMToLBMProjector3D
```

and include `"MPMToLBMProjector3D"` in `__all__`.

## 6. Projection Field Definitions

LBM fields already available:

```text
lbm.solid_phi   # solid volume fraction, clamped to [0, 1]
lbm.solid_mass  # projected MPM mass in each LBM cell
lbm.solid_vel   # mass-weighted projected solid velocity in LBM lattice velocity units
```

MPM source fields:

```text
solid.x[p]      # normalized particle position in [0, 1]^3
solid.v[p]      # normalized velocity
solid.mass[p]   # particle mass
solid.vol0[p]   # reference particle volume
solid.Jp[p]     # current volume ratio
```

Current particle volume:

```text
current_volume[p] = solid.vol0[p] * max(solid.Jp[p], 0)
```

LBM cell normalized volume:

```text
cell_volume_norm = dx_norm^3
```

## 7. Spatial Projection Convention

Use the same quadratic 3x3x3 stencil convention as MPM P2G:

```text
Xp = solid.x[p] / dx_norm
base = int(Xp - 0.5)
fx = Xp - base

w0 = 0.5 * (1.5 - fx)^2
w1 = 0.75 - (fx - 1.0)^2
w2 = 0.5 * (fx - 0.5)^2
```

For every offset in `3 x 3 x 3`:

```text
I = base + offset
weight = wx * wy * wz
```

Only write if `I` is inside the LBM grid:

```text
0 <= I.x < lbm.nx
0 <= I.y < lbm.ny
0 <= I.z < lbm.nz
```

Step 5 still uses only the cubic normalized domain:

```text
n_grid = nx = ny = nz = 32 by default
domain_length = 1.0
dx_norm = 1 / n_grid
```

Do not add rectangular domain support in Step 5.

## 8. Velocity Unit Conversion

MPM velocity is normalized velocity:

```text
v_norm = normalized length / physical time
```

LBM solid velocity must be LBM lattice velocity:

```text
v_lbm = lattice cell / LBM step
```

Use the Step 4 formula:

```text
v_lbm = v_norm * lbm_dt_phys / dx_norm
v_norm = v_lbm * dx_norm / lbm_dt_phys
```

Projector scale:

```text
vel_scale_norm_to_lbm = lbm_dt_phys / dx_norm
```

With Step 4 defaults:

```text
n_grid = 32
dx_norm = 0.03125
lbm_dt_phys = 0.004
target_u_lbm = 0.03
target_u_norm = 0.234375
```

Do not write `solid.v[p]` directly into `lbm.solid_vel[I]`.

## 9. Volume, Mass, And Velocity Projection

Volume fraction contribution:

```text
lbm.solid_phi[I] += weight * current_volume[p] / cell_volume_norm
```

Mass contribution:

```text
lbm.solid_mass[I] += weight * solid.mass[p]
```

Momentum-like velocity numerator:

```text
lbm.solid_vel[I] += weight * solid.mass[p] * v_lbm[p]
```

Normalize after all particle projection:

```text
if lbm.solid_mass[I] > eps_mass:
    lbm.solid_vel[I] /= lbm.solid_mass[I]
else:
    lbm.solid_vel[I] = 0
```

Clamp final volume fraction:

```text
solid_phi_raw = lbm.solid_phi[I]
lbm.solid_phi[I] = clamp(solid_phi_raw, 0, 1)
```

Track both raw and clamped volume:

```text
projected_volume_raw += solid_phi_raw * cell_volume_norm
projected_volume_clamped += lbm.solid_phi[I] * cell_volume_norm
max_phi_raw = max(max_phi_raw, solid_phi_raw)
active_cell_count = count(lbm.solid_phi[I] > 1e-8)
```

This makes oversaturation visible in the report instead of hiding it.

## 10. `src/projection.py` Required Interface

Create:

```text
src/projection.py
```

Implement:

```python
@ti.data_oriented
class MPMToLBMProjector3D:
    def __init__(self, sim_config):
        ...

    @ti.kernel
    def clear_projection(self, lbm: ti.template()):
        ...

    @ti.func
    def inside_lbm(self, I, lbm: ti.template()):
        ...

    @ti.kernel
    def project_particles(self, solid: ti.template(), lbm: ti.template()):
        ...

    @ti.kernel
    def normalize_projection(self, lbm: ti.template()):
        ...

    def project(self, solid, lbm, clear=True):
        ...

    def get_stats(self):
        ...
```

Required diagnostic fields:

```text
projected_mass
projected_volume_raw
projected_volume_clamped
max_phi_raw
active_cell_count
vel_scale_norm_to_lbm
```

`clear_projection()` may clear only:

```text
lbm.solid_phi
lbm.solid_mass
lbm.solid_vel
```

It must not clear or write:

```text
lbm.cell_force
lbm.hydro_force
```

## 11. Optional Warning Cleanup

Step 4 shared-domain log showed:

```text
Assign may lose precision: i8 <- f64
```

Apply a non-physical dtype cleanup in `LBMFluid3D.init_geo()`:

```python
in_dat = np.loadtxt(filename)
in_dat[in_dat > 0] = 1
in_dat = np.reshape(in_dat, (self.nx, self.ny, self.nz), order="F")
in_dat = in_dat.astype(np.int8)
self.solid.from_numpy(in_dat)
```

This is allowed because it only removes geometry dtype noise and does not change physics.

Acceptance target:

```text
Step 5 logs should not contain "Assign may lose precision: i8 <- f64".
```

## 12. Required Baselines

### 12.1 Static Block Projection

Create:

```text
baseline_tests/run_step5_projection_static_block.py
```

Purpose:

```text
Verify a resting MPM block projects into LBM solid_phi, solid_mass, and solid_vel.
```

Required flow:

```text
1. ti.init(arch=ti.gpu, default_fp=ti.f32)
2. Create UnifiedSimConfig(n_grid=32).
3. Create GridUnitMapper from sim.
4. Initialize all-fluid LBM geometry.
5. Create LBMFluid3D from sim.make_lbm_config().
6. Create MPMSolid3D from sim.make_mpm_config(gravity=(0,0,0)).
7. solid.init_box().
8. projector = MPMToLBMProjector3D(sim).
9. projector.project(solid, lbm).
10. Save projection arrays and VTK.
```

Acceptance:

```text
projected_mass approximately equals sum(solid.mass)
relative_mass_error < 1e-5
active_cell_count > 0
solid_phi finite
solid_mass finite
solid_vel finite
0 <= solid_phi <= 1
max |solid_vel| < 1e-8
cell_force remains zero
hydro_force remains zero
```

Required outputs:

```text
outputs/step5_projection_static/LBMProjection_0.vtr
outputs/step5_projection_static/solid_phi.npy
outputs/step5_projection_static/solid_mass.npy
outputs/step5_projection_static/solid_vel.npy
outputs/step5_projection_static/particles_x.npy
```

### 12.2 Moving Block Velocity Projection

Create:

```text
baseline_tests/run_step5_projection_moving_block.py
```

Purpose:

```text
Verify normalized MPM velocity is converted to LBM lattice velocity before projection.
```

Settings:

```text
target_u_lbm = (0.03, 0.0, 0.0)
target_u_norm = mapper.velocity_lbm_to_norm(target_u_lbm)
solid.set_uniform_velocity(*target_u_norm)
```

After projection, compute:

```python
solid_mass_np = lbm.solid_mass.to_numpy()
solid_vel_np = lbm.solid_vel.to_numpy()
active = solid_mass_np > 1e-12
mean_vel = np.average(solid_vel_np[active], axis=0, weights=solid_mass_np[active])
```

Acceptance:

```text
active_cell_count > 0
projected_mass relative error < 1e-5
abs(mean_vel[0] - 0.03) < 1e-6
abs(mean_vel[1]) < 1e-8
abs(mean_vel[2]) < 1e-8
solid_phi finite
0 <= solid_phi <= 1
cell_force remains zero
hydro_force remains zero
```

Required outputs:

```text
outputs/step5_projection_moving/LBMProjection_0.vtr
outputs/step5_projection_moving/solid_phi.npy
outputs/step5_projection_moving/solid_mass.npy
outputs/step5_projection_moving/solid_vel.npy
outputs/step5_projection_moving/particles_x.npy
```

### 12.3 Projection After MPM Motion

Create:

```text
baseline_tests/run_step5_projection_after_mpm_motion.py
```

Purpose:

```text
Verify projection follows MPM particle motion and updates projected spatial range.
```

Recommended settings:

```text
gravity = (0.0, 0.0, 0.0)
target_u_lbm = (0.02, 0.0, 0.0)
target_u_norm = mapper.velocity_lbm_to_norm(target_u_lbm)
mpm_substeps = 50
```

Required flow:

```text
1. Initialize MPM block.
2. Set uniform velocity from target_u_norm.
3. Project frame 0 and record particle center_x_0, active_cell_count_0, index range.
4. Run 50 MPM substeps.
5. Project frame 1 and record particle center_x_1, active_cell_count_1, index range.
6. Save both frames.
```

Acceptance:

```text
center_x_final > center_x_initial
projected mass relative error < 1e-5 for both frames
active_cell_count > 0 for both frames
solid_phi finite for both frames
solid_vel finite for both frames
no NaN
no Inf
cell_force remains zero
hydro_force remains zero
```

Required outputs:

```text
outputs/step5_projection_motion/LBMProjection_0.vtr
outputs/step5_projection_motion/LBMProjection_1.vtr
outputs/step5_projection_motion/solid_phi_0.npy
outputs/step5_projection_motion/solid_phi_1.npy
outputs/step5_projection_motion/solid_mass_0.npy
outputs/step5_projection_motion/solid_mass_1.npy
outputs/step5_projection_motion/solid_vel_0.npy
outputs/step5_projection_motion/solid_vel_1.npy
```

### 12.4 Dynamic Solid Mask Dry Run

Create:

```text
baseline_tests/run_step5_dynamic_solid_mask_dryrun.py
```

Purpose:

```text
Verify projected solid_phi can drive LBM dynamic solid mask logic without force coupling.
```

Required flow:

```text
1. Initialize LBM all-fluid static geometry.
2. Initialize MPM block.
3. Project MPM -> LBM solid_phi.
4. Call lbm.update_dynamic_solid(threshold=0.5).
5. Count dynamic solid cells.
6. Clear projection.
7. Call lbm.update_dynamic_solid(threshold=0.5).
8. Call lbm.reinitialize_new_fluid_cells().
9. Count released/reinitialized cells and check rho/v finite.
```

Allowed calls in this baseline:

```text
lbm.update_dynamic_solid()
lbm.reinitialize_new_fluid_cells()
```

Forbidden calls in this baseline:

```text
lbm.step()
lbm.set_uniform_cell_force()
lbm.set_spherical_cell_force()
lbm.build_dummy_hydro_force()
```

Acceptance:

```text
solid_on_count > 0
solid_off_count == 0 after clearing if static_solid is zero
reinit_count > 0
rho finite
velocity finite
cell_force remains zero
hydro_force remains zero
```

Required outputs:

```text
outputs/step5_dynamic_solid_mask/LBMProjection_mask_on.vtr
outputs/step5_dynamic_solid_mask/LBMProjection_mask_off.vtr
outputs/step5_dynamic_solid_mask/solid_on.npy
outputs/step5_dynamic_solid_mask/solid_off.npy
```

## 13. Required Report

Create:

```text
STEP5_MPM_TO_LBM_PROJECTION_REPORT.md
```

Report must include:

```text
1. Goal
2. Files created/updated
3. Projection convention
4. Velocity unit conversion
5. Static block projection command/result
6. Moving block velocity projection command/result
7. Projection after MPM motion command/result
8. Dynamic solid mask dry-run command/result
9. Explicit non-goal confirmation
10. Hard Acceptance Checklist
11. Decision: can proceed to Step 6 or not
```

Report default values:

```text
n_grid
dx_norm
mpm_dt
mpm_substeps_per_lbm_step
lbm_dt_phys
vel_scale_norm_to_lbm
target_u_lbm
target_u_norm
```

## 14. Pytest Contract

Create:

```text
tests/test_step5_projection_contract.py
```

Recommended tests:

```python
def test_step5_required_artifacts_exist():
    ...

def test_step5_projection_source_contains_required_interfaces():
    ...

def test_step5_scripts_do_not_implement_force_coupling():
    ...

def test_step5_logs_record_successful_baselines():
    ...

def test_step5_report_acceptance_complete():
    ...
```

Required source keywords:

```text
class MPMToLBMProjector3D
clear_projection
inside_lbm
project_particles
normalize_projection
projected_mass
projected_volume_raw
projected_volume_clamped
max_phi_raw
active_cell_count
vel_scale_norm_to_lbm
solid_phi
solid_mass
solid_vel
```

Forbidden behavior checks:

```text
Do not call set_uniform_cell_force().
Do not call set_spherical_cell_force().
Do not call build_dummy_hydro_force().
Do not assign nonzero values into lbm.cell_force.
Do not assign nonzero values into lbm.hydro_force.
Do not use penalty force.
Do not use momentum exchange.
Do not use moving bounce-back.
Do not use ReducedSquidFSI.
```

Important nuance:

```text
The words cell_force and hydro_force may appear in tests and baselines only when verifying they remain zero.
Do not globally ban those strings.
Ban force-producing calls and nonzero assignments instead.
```

Log checks should verify:

```text
[OK] Step 5 static block projection baseline finished
[OK] Step 5 moving block velocity projection baseline finished
[OK] Step 5 projection after MPM motion baseline finished
[OK] Step 5 dynamic solid mask dry run finished
relative_mass_error
projected_mean_solid_vel
center_x_initial
center_x_final
solid_on_count
reinit_count
```

## 15. Hard Acceptance Checklist

All must pass:

```text
[ ] main is on the Step 5 final commit
[ ] src/projection.py exists
[ ] src/__init__.py exports MPMToLBMProjector3D
[ ] optional LBMFluid3D.init_geo dtype cleanup is applied if warning persists
[ ] MPMToLBMProjector3D.clear_projection() clears solid_phi, solid_mass, solid_vel
[ ] MPMToLBMProjector3D.project_particles() writes solid_phi
[ ] MPMToLBMProjector3D.project_particles() writes solid_mass
[ ] MPMToLBMProjector3D.project_particles() writes solid_vel
[ ] solid velocity uses normalized-to-LBM lattice velocity scaling
[ ] volume fraction uses current_volume = vol0 * Jp
[ ] solid_phi is clamped to [0, 1]
[ ] projected raw/clamped volume diagnostics are recorded
[ ] static block projection baseline passes
[ ] moving block velocity projection baseline passes
[ ] projection after MPM motion baseline passes
[ ] dynamic solid mask dry-run baseline passes
[ ] projected_mass relative error < 1e-5 in required baselines
[ ] static block projected solid_vel is approximately zero
[ ] moving block projected solid_vel matches target_u_lbm
[ ] particle center_x increases after motion baseline
[ ] active_cell_count > 0
[ ] solid_phi finite
[ ] solid_mass finite
[ ] solid_vel finite
[ ] no NaN
[ ] no Inf
[ ] cell_force remains zero
[ ] hydro_force remains zero
[ ] no penalty force is implemented
[ ] no momentum exchange is implemented
[ ] no moving bounce-back is implemented
[ ] no FSI force coupling is implemented
[ ] logs are saved under logs/
[ ] outputs are saved under outputs/
[ ] STEP5_MPM_TO_LBM_PROJECTION_REPORT.md is complete
[ ] pytest -q passes
```

Numerical thresholds:

```text
Mass projection:
  relative_mass_error < 1e-5

Velocity projection:
  abs(projected_mean_vel_x - target_u_lbm_x) < 1e-6
  abs(projected_mean_vel_y) < 1e-8
  abs(projected_mean_vel_z) < 1e-8

solid_phi:
  min_phi >= 0
  max_phi <= 1
  active_cell_count > 0

fields:
  no NaN
  no Inf

force fields:
  max_norm(cell_force) == 0
  max_norm(hydro_force) == 0
```

## 16. Recommended Execution Order

Follow this order:

```text
1. Add Step 5 pytest contract/artifact checks.
2. Run pytest and confirm RED for missing Step 5 artifacts.
3. Create src/projection.py.
4. Export MPMToLBMProjector3D from src/__init__.py.
5. Apply LBMFluid3D.init_geo dtype cleanup if warning persists.
6. Implement clear_projection().
7. Implement project_particles().
8. Implement normalize_projection().
9. Implement get_stats().
10. Add and run static block projection baseline.
11. Add and run moving block velocity projection baseline.
12. Add and run projection after MPM motion baseline.
13. Add and run dynamic solid mask dry-run baseline.
14. Write STEP5_MPM_TO_LBM_PROJECTION_REPORT.md.
15. Run final pytest.
16. Inspect git status and confirm external/ is unchanged.
17. Commit and push to GitHub.
```

Suggested commits:

```text
test: add step 5 projection contract
feat: add mpm to lbm projection scaffold
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

Do not weaken the required baselines and call Step 5 complete.

Shorter runs may be used only as clearly labeled diagnostic probes, followed by the full required baselines.

## 18. Completion Definition

Step 5 is complete only when:

```text
1. MPMToLBMProjector3D exists.
2. MPM particle mass, volume, and velocity are projected to LBM solid fields.
3. solid_vel is in LBM lattice velocity units.
4. static projection passes conservation and field checks.
5. moving projection proves velocity conversion.
6. after-motion projection proves projected location follows MPM motion.
7. dynamic solid mask dry run proves projected solid_phi can drive mask logic.
8. No force coupling is implemented.
9. cell_force and hydro_force remain zero in Step 5 baselines.
10. Logs, outputs, and STEP5_MPM_TO_LBM_PROJECTION_REPORT.md record evidence.
11. pytest passes.
12. The completed code, report, logs, and outputs are pushed to GitHub.
```

Completion does not mean FSI exists. It means LBM can see MPM solid geometry, mass, and velocity fields correctly, so Step 6 can implement force coupling on top of validated projection fields.
