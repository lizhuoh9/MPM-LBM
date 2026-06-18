# Step 8 Goal: Moving Bounce-Back Sharp-Interface Scaffold

## Paste-Ready `/goal`

```text
/goal
In D:\working\squid robot\LBM\MPM-LBM, execute Step 8: Moving bounce-back sharp-interface scaffold. The only authoritative execution contract is D:\working\squid robot\LBM\MPM-LBM\STEP8_MOVING_BOUNCEBACK_GOAL.md.

Goal: add an independent LBM moving-wall bounce-back path and link-wise momentum-exchange diagnostics without breaking the existing Step 6/7 penalty coupling path. Keep lbm.step() as the default penalty-compatible LBM step. Add lbm.step_moving_bounceback() for Step 8 moving-boundary baselines, driven by prescribed wall velocities and projected MPM solid_vel.

Hard boundaries: do not implement two-way MPM reaction from momentum exchange, do not replace PenaltyFSICoupler3D, do not make moving bounce-back the default step(), do not implement two-phase flow, contact angle physics, squid geometry, sparse storage, ReducedSquidFSI, or edits to external/taichi_LBM3D. Step 8 may use update_dynamic_solid() and reinitialize_new_fluid_cells() because moving solid masks are now in scope. Step 8 may use momentum_exchange wording for diagnostics only.

Required artifacts, execution order, baseline settings, pytest contract, Hard Acceptance Checklist, failure handling, and completion definition are all defined in STEP8_MOVING_BOUNCEBACK_GOAL.md. Finish only after all Step 8 baselines pass, pytest passes, and code/logs/outputs/report are pushed to GitHub.
```

## 1. Current Baseline

Step 7 is accepted and is the starting point.

Current Step 7 final commit:

```text
507a50981610450db0b81ade5c27a64016cf24f8
```

Step 7 validated:

```text
FSIDiagnostics3D exists and is exported.
Couette-like qualitative penalty-coupled validation passes.
Momentum / impulse diagnostics pass for the Step 6 penalty force pair.
Beta sweep is stable for 3.0e-4, 1.0e-3, and 3.0e-3.
Long coupled stability completes 100 LBM steps / 1000 MPM substeps.
No external/taichi_LBM3D edits.
No new FSI physics was added in Step 7.
```

Step 7 evidence:

```text
src/diagnostics.py
STEP7_FSI_VALIDATION_REPORT.md
logs/step7_couette_like.log
logs/step7_momentum_impulse.log
logs/step7_beta_sweep.log
logs/step7_long_stability.log
outputs/step7_couette_like/
outputs/step7_momentum_impulse/
outputs/step7_beta_sweep/
outputs/step7_long_stability/
tests/test_step7_validation_contract.py
```

Step 7 means:

```text
The current penalty-force MPM-LBM prototype has reproducible qualitative FSI response and a documented small-scale stability window.
```

Step 7 still does not mean:

```text
sharp-interface no-slip FSI exists
moving bounce-back exists
momentum-exchange FSI exists
real squid validation is complete
```

## 2. Step 8 Objective

Step 8 starts a new interface-physics stage. Its purpose is to add a sharper LBM moving-boundary path while preserving the Step 6/7 penalty path.

Implement this progression:

```text
static bounce-back
    -> moving-wall bounce-back
    -> link-wise momentum-exchange diagnostics
```

Current `LBMFluid3D.streaming1()` handles a solid neighbor with static bounce-back:

```python
if self.solid[ip] == 0:
    self.F[ip][s] = self.f[i][s]
else:
    self.F[i][self.LR[s]] = self.f[i][s]
```

Step 8 must add a separate moving-boundary streaming path:

```text
when neighbor ip is solid and has solid_vel[ip],
reflect f[i][s] back to F[i][LR[s]] with moving-wall correction.
```

Step 8 must prove:

```text
1. zero wall velocity regresses to static bounce-back;
2. prescribed moving wall drives fluid in the wall direction;
3. projected MPM solid_vel can drive moving-boundary bounce-back;
4. link-wise fluid impulse and solid reaction diagnostics have correct signs;
5. Step 6/7 penalty path remains intact.
```

## 3. Workspace And Environment

Work in:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Known Python environment:

```powershell
& 'D:\working\taichi\env\python.exe' ...
```

Runtime baselines should use:

```python
ti.init(arch=ti.gpu, default_fp=ti.f32)
```

## 4. Strict Non-Goals

Do not implement these in Step 8:

```text
1. No two-way MPM reaction from moving-boundary momentum diagnostics.
2. No replacement or deletion of PenaltyFSICoupler3D.
3. No replacement of existing lbm.step() behavior.
4. No two-phase LBM.
5. No contact angle physics.
6. No squid geometry or real squid case.
7. No sparse storage.
8. No ReducedSquidFSI.
9. No edits to external/taichi_LBM3D.
10. No claim that real squid FSI is validated.
```

Allowed in Step 8:

```text
moving-wall bounce-back
moving-boundary diagnostics
link-wise momentum-exchange diagnostics
hydro_force as moving-boundary diagnostic force on solid
update_dynamic_solid() in Step 8 projected-MPM boundary baselines
reinitialize_new_fluid_cells() in Step 8 projected-MPM boundary baselines
```

Important distinction:

```text
Step 8's hydro_force is link-wise moving-boundary diagnostic force on solid.
Step 6's hydro_force is penalty-force reaction.
These modes must not be mixed in the same baseline.
```

## 5. Required Final Structure

Update:

```text
src/lbm_fluid.py
```

Optional new module only if it keeps code clearer:

```text
src/momentum_exchange.py
```

Create:

```text
baseline_tests/
  run_step8_static_bounceback_regression.py
  run_step8_prescribed_moving_wall_couette.py
  run_step8_projected_mpm_moving_boundary.py
  run_step8_momentum_exchange_diagnostics.py

outputs/
  step8_static_bounceback_regression/
  step8_prescribed_moving_wall/
  step8_projected_mpm_boundary/
  step8_momentum_exchange/

logs/
  step8_static_bounceback_regression.log
  step8_prescribed_moving_wall.log
  step8_projected_mpm_boundary.log
  step8_momentum_exchange.log

tests/
  test_step8_moving_bounceback_contract.py

STEP8_MOVING_BOUNCEBACK_REPORT.md
```

## 6. LBM Moving-Boundary Fields

Add to `LBMFluid3D.__init__()`:

```python
self.bb_link_count = ti.field(ti.i32, shape=())
self.bb_max_correction = ti.field(ti.f32, shape=())
self.bb_net_fluid_impulse = ti.Vector.field(3, ti.f32, shape=())
self.bb_net_solid_force = ti.Vector.field(3, ti.f32, shape=())
```

Meanings:

```text
bb_link_count         number of bounce-back links encountered in moving-boundary streaming
bb_max_correction     maximum absolute moving-wall distribution correction
bb_net_fluid_impulse  net impulse applied to fluid by link reflection
bb_net_solid_force    equal-and-opposite diagnostic reaction on solid
```

Reuse existing:

```text
lbm.hydro_force
```

as a diagnostic field containing link-wise force on solid in moving-boundary baselines.

Do not use:

```text
lbm.cell_force
```

in Step 8 moving-boundary baselines. It must remain zero.

## 7. Clear Moving-Boundary Diagnostics

Add:

```python
@ti.kernel
def clear_moving_boundary_diagnostics(self):
    self.bb_link_count[None] = 0
    self.bb_max_correction[None] = 0.0
    self.bb_net_fluid_impulse[None] = ti.Vector([0.0, 0.0, 0.0])
    self.bb_net_solid_force[None] = ti.Vector([0.0, 0.0, 0.0])

    for I in ti.grouped(self.rho):
        self.hydro_force[I] = ti.Vector([0.0, 0.0, 0.0])
```

Recommended:

```text
Do not clear cell_force here.
Instead, baseline checks must verify cell_force is already zero when using moving-boundary mode.
```

This keeps Step 8 mode separate from penalty forcing.

## 8. Moving Bounce-Back Streaming

Add:

```python
@ti.kernel
def streaming_moving_bounceback(self):
    ...
```

Core logic:

```python
for i in ti.grouped(self.rho):
    if self.solid[i] == 0:
        for s in ti.static(range(19)):
            ip = self.periodic_index(i + self.e[s])

            if self.solid[ip] == 0:
                self.F[ip][s] = self.f[i][s]
            else:
                rho_local = self.rho[i]
                u_wall = self.solid_vel[ip]

                correction = -6.0 * self.w[s] * rho_local * self.e_f[s].dot(u_wall)
                bounced = self.f[i][s] + correction
                self.F[i][self.LR[s]] = bounced
```

Required formula to start with:

```text
F[i][LR[s]] = f[i][s] - 6 * w[s] * rho[i] * dot(e[s], u_wall)
```

Sign convention:

```text
For a +x moving wall, prescribed moving wall baseline must show:
  top_near_ux > bottom_near_ux
  global_mean_ux > 0
  bb_net_fluid_impulse_x > 0
  bb_net_solid_force_x < 0
```

If the prescribed moving-wall baseline shows fluid moves in the wrong direction, only flip the correction sign and record the final sign in the report.

## 9. Link-Wise Momentum-Exchange Diagnostics

For each bounce-back link, compute:

```python
incoming_momentum = self.e_f[s] * self.f[i][s]
outgoing_momentum = self.e_f[self.LR[s]] * bounced
fluid_impulse = outgoing_momentum - incoming_momentum
solid_force = -fluid_impulse
```

Then update diagnostics:

```python
ti.atomic_add(self.bb_link_count[None], 1)
ti.atomic_max(self.bb_max_correction[None], abs(correction))

for d in ti.static(range(3)):
    ti.atomic_add(self.bb_net_fluid_impulse[None][d], fluid_impulse[d])
    ti.atomic_add(self.bb_net_solid_force[None][d], solid_force[d])
    ti.atomic_add(self.hydro_force[ip][d], solid_force[d])
```

This is diagnostic-only in Step 8.

Do not transfer this `hydro_force` to MPM grid in Step 8. That belongs to Step 9.

## 10. Moving-Boundary Step

Keep existing default:

```python
def step(self):
    self.colission()
    self.streaming1()
    self.Boundary_condition()
    self.streaming3()
```

Add:

```python
def step_moving_bounceback(self):
    self.clear_moving_boundary_diagnostics()
    self.colission()
    self.streaming_moving_bounceback()
    self.Boundary_condition()
    self.streaming3()
```

This ensures:

```text
Step 6/7 penalty baselines keep using lbm.step().
Step 8 moving-boundary baselines explicitly opt in to lbm.step_moving_bounceback().
```

## 11. Moving-Boundary Stats

Add:

```python
def get_moving_boundary_stats(self):
    return {
        "bb_link_count": int(self.bb_link_count[None]),
        "bb_max_correction": float(self.bb_max_correction[None]),
        "bb_net_fluid_impulse": tuple(...),
        "bb_net_solid_force": tuple(...),
    }
```

This method is diagnostic-only.

## 12. Relationship To MPM Projector

Step 8 may reuse Step 5 projection:

```python
projector.project(solid, lbm)
lbm.update_dynamic_solid(threshold=0.5)
lbm.reinitialize_new_fluid_cells()
lbm.step_moving_bounceback()
```

Step 8 must not use penalty coupling in moving-boundary baselines:

```text
Do not call PenaltyFSICoupler3D.build_penalty_force().
Do not call PenaltyFSICoupler3D.add_lbm_reaction_to_mpm_grid().
```

Kinematic MPM motion is allowed in the projected-MPM moving-boundary baseline:

```text
solid.substep() may be used with gravity = 0 and prescribed initial velocity.
No moving-boundary hydro_force is transferred back to MPM in Step 8.
```

## 13. Baseline 1: Static Bounce-Back Regression

Create:

```text
baseline_tests/run_step8_static_bounceback_regression.py
```

Purpose:

```text
Verify step_moving_bounceback() with zero solid_vel regresses to original static bounce-back behavior.
```

Recommended geometry:

```text
n_grid = 32
solid block or y-wall geometry
solid_vel = 0 everywhere
LBM initial fluid state
n_steps = 100
```

Run two solvers:

```text
A: lbm.step()
B: lbm.step_moving_bounceback()
```

Compare:

```text
rho_min/rho_max
max_v
max_abs_velocity_difference
max_abs_rho_difference
```

Acceptance:

```text
bb_link_count > 0
bb_max_correction == 0
max_abs_velocity_difference < 1.0e-6, or documented tighter/looser value if floating point requires it
max_abs_rho_difference < 1.0e-6, or documented tighter/looser value if floating point requires it
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
no NaN
no Inf
```

Required outputs:

```text
outputs/step8_static_bounceback_regression/LBMStatic_100.vtr
outputs/step8_static_bounceback_regression/LBMMovingZero_100.vtr
outputs/step8_static_bounceback_regression/velocity_difference.npy
outputs/step8_static_bounceback_regression/rho_difference.npy
```

Required log marker:

```text
[OK] Step 8 static bounce-back regression finished
```

## 14. Baseline 2: Prescribed Moving Wall Couette

Create:

```text
baseline_tests/run_step8_prescribed_moving_wall_couette.py
```

Purpose:

```text
Verify moving bounce-back produces fluid motion in the prescribed wall direction.
```

Geometry:

```text
n_grid = 32
bottom wall: y = 0, solid_vel = (0, 0, 0)
top wall: y = ny - 1, solid_vel = (0.03, 0, 0)
middle cells are fluid
```

Geometry mask:

```python
solid[:, 0, :] = 1
solid[:, ny - 1, :] = 1
```

Recommended settings:

```text
steps = 1000, or 2000 if runtime is acceptable
niu = 0.1
target_u_lbm = (0.03, 0, 0)
```

Acceptance:

```text
top_near_ux > bottom_near_ux
global_mean_ux > 0
ux_profile_y is mostly increasing
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
bb_link_count > 0
bb_max_correction > 0
bb_net_fluid_impulse_x > 0
bb_net_solid_force_x < 0
cell_force remains zero
no NaN
no Inf
```

Required outputs:

```text
outputs/step8_prescribed_moving_wall/LBMFluid_1000.vtr
outputs/step8_prescribed_moving_wall/ux_profile_y.npy
outputs/step8_prescribed_moving_wall/diagnostics.npz
```

Required log marker:

```text
[OK] Step 8 prescribed moving wall Couette finished
```

## 15. Baseline 3: Projected MPM Moving Boundary

Create:

```text
baseline_tests/run_step8_projected_mpm_moving_boundary.py
```

Purpose:

```text
Verify projected MPM solid_phi / solid_vel can drive moving bounce-back through a dynamic solid mask.
```

Recommended settings:

```text
n_grid = 32
n_particles = 4096
gravity = (0, 0, 0)
target_u_lbm = (0.02, 0, 0)
threshold = 0.5
n_steps = 100
mpm_substeps_per_lbm_step = 10
```

Required flow:

```python
solid.init_box()
solid.set_uniform_velocity(*target_u_norm)

for step in range(n_steps):
    projector.project(solid, lbm)
    lbm.update_dynamic_solid(threshold=0.5)
    lbm.reinitialize_new_fluid_cells()
    lbm.step_moving_bounceback()

    for _ in range(sim.mpm_substeps_per_lbm_step):
        solid.substep()
```

Important:

```text
This baseline uses kinematic MPM motion only.
Do not send moving-boundary hydro_force back to MPM.
Do not use PenaltyFSICoupler3D.
```

Acceptance:

```text
solid_on_count > 0
bb_link_count > 0
projection_zone_fluid_mean_ux_final > projection_zone_fluid_mean_ux_initial
bb_net_fluid_impulse_x > 0
bb_net_solid_force_x < 0
cell_force remains zero
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
no NaN
no Inf
```

Required outputs:

```text
outputs/step8_projected_mpm_boundary/LBMFluid_100.vtr
outputs/step8_projected_mpm_boundary/particles_x.npy
outputs/step8_projected_mpm_boundary/particles_v.npy
outputs/step8_projected_mpm_boundary/solid.npy
outputs/step8_projected_mpm_boundary/solid_phi.npy
outputs/step8_projected_mpm_boundary/diagnostics.npz
```

Required log marker:

```text
[OK] Step 8 projected MPM moving boundary finished
```

## 16. Baseline 4: Momentum-Exchange Diagnostics

Create:

```text
baseline_tests/run_step8_momentum_exchange_diagnostics.py
```

Purpose:

```text
Verify link-wise moving-boundary impulse and solid-force diagnostics have consistent direction and balance.
```

Recommended settings:

```text
prescribed moving top wall
n_grid = 32
steps = 500
target_u_lbm = (0.03, 0, 0)
```

Record every sample:

```text
step
bb_link_count
bb_max_correction
bb_net_fluid_impulse_x
bb_net_solid_force_x
force_balance_error = norm(bb_net_fluid_impulse + bb_net_solid_force)
hydro_force_max_norm
cell_force_max_norm
rho_min
rho_max
lbm_max_v
```

Acceptance:

```text
bb_link_count > 0
bb_max_correction > 0
bb_net_fluid_impulse_x > 0
bb_net_solid_force_x < 0
max_force_balance_error < 1.0e-6, or documented small tolerance if f32 reductions require it
hydro_force_max_norm > 0
cell_force_max_norm == 0
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
no NaN
no Inf
```

Required outputs:

```text
outputs/step8_momentum_exchange/momentum_exchange_timeseries.npz
outputs/step8_momentum_exchange/LBMFluid_500.vtr
```

Required log marker:

```text
[OK] Step 8 momentum-exchange diagnostics finished
```

## 17. Required Report

Create:

```text
STEP8_MOVING_BOUNCEBACK_REPORT.md
```

Report must include:

```text
1. Goal
2. Files created/updated
3. Moving bounce-back formula
4. Momentum-exchange diagnostic definition
5. Static bounce-back regression command/result
6. Prescribed moving wall Couette command/result
7. Projected MPM moving boundary command/result
8. Momentum-exchange diagnostics command/result
9. Explicit non-goals
10. Hard Acceptance Checklist
11. Decision: can proceed to Step 9 or not
```

Report must explicitly state:

```text
Step 8 adds an opt-in moving-boundary LBM path.
Step 8 does not replace the Step 6/7 penalty path.
Step 8 does not transfer link-wise hydro_force back to MPM.
Step 8 link-wise hydro_force is a diagnostic force on solid.
```

Recommended report template:

````markdown
# Step 8 Moving Bounce-Back Report

## 1. Goal

Implement an opt-in moving-wall bounce-back path and link-wise momentum-exchange diagnostics for sharper LBM solid boundaries.

## 2. Files

Created / updated:

- src/lbm_fluid.py
- baseline_tests/run_step8_static_bounceback_regression.py
- baseline_tests/run_step8_prescribed_moving_wall_couette.py
- baseline_tests/run_step8_projected_mpm_moving_boundary.py
- baseline_tests/run_step8_momentum_exchange_diagnostics.py
- tests/test_step8_moving_bounceback_contract.py

## 3. Moving bounce-back formula

```text
F[i][LR[s]] = f[i][s] - 6 * w[s] * rho[i] * dot(e[s], u_wall)
```

If sign was adjusted during testing, document final sign here.

## 4. Momentum-exchange diagnostic

```text
incoming_momentum = e[s] * f[i][s]
outgoing_momentum = e[LR[s]] * bounced
fluid_impulse = outgoing_momentum - incoming_momentum
solid_force = -fluid_impulse
```

## 5. Static bounce-back regression

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step8_static_bounceback_regression.py
```

Result:

- bb_link_count:
- bb_max_correction:
- max_abs_velocity_difference:
- max_abs_rho_difference:

## 6. Prescribed moving wall Couette

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step8_prescribed_moving_wall_couette.py
```

Result:

- top_near_ux:
- bottom_near_ux:
- global_mean_ux:
- bb_net_fluid_impulse_x:
- bb_net_solid_force_x:
- rho_min:
- rho_max:

## 7. Projected MPM moving boundary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step8_projected_mpm_moving_boundary.py
```

Result:

- solid_on_count:
- bb_link_count:
- projection_zone_fluid_mean_ux_initial:
- projection_zone_fluid_mean_ux_final:
- cell_force_max_norm:

## 8. Momentum-exchange diagnostics

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step8_momentum_exchange_diagnostics.py
```

Result:

- max_force_balance_error:
- cumulative_fluid_impulse_x:
- cumulative_solid_force_x:
- hydro_force_max_norm:

## 9. Explicit non-goals

Step 8 does not implement two-way MPM reaction from momentum exchange, penalty coupling replacement, two-phase flow, contact angle, squid geometry, sparse storage, or external/taichi_LBM3D edits.

## 10. Acceptance checklist

- [ ] `streaming_moving_bounceback()` exists
- [ ] `step_moving_bounceback()` exists
- [ ] zero wall velocity regresses to static bounce-back
- [ ] prescribed moving wall drives fluid in correct direction
- [ ] projected MPM moving boundary drives fluid in correct direction
- [ ] link-wise momentum diagnostics exist
- [ ] `bb_net_fluid_impulse_x > 0` for +x moving wall
- [ ] `bb_net_solid_force_x < 0` for +x moving wall
- [ ] `cell_force` remains zero in moving-bounceback baselines
- [ ] no penalty force is used in Step 8 moving-bounceback baselines
- [ ] no external/taichi_LBM3D edits
- [ ] logs saved
- [ ] outputs saved
- [ ] pytest passes

## 11. Decision

Can proceed to Step 9?

- [ ] Yes
- [ ] No
````

## 18. Pytest Contract

Create:

```text
tests/test_step8_moving_bounceback_contract.py
```

Recommended tests:

```python
def test_step8_required_artifacts_exist():
    ...

def test_step8_lbm_source_contains_required_interfaces():
    ...

def test_step8_scripts_do_not_use_forbidden_methods():
    ...

def test_step8_logs_record_successful_baselines():
    ...

def test_step8_report_acceptance_complete():
    ...
```

Required artifact paths:

```text
baseline_tests/run_step8_static_bounceback_regression.py
baseline_tests/run_step8_prescribed_moving_wall_couette.py
baseline_tests/run_step8_projected_mpm_moving_boundary.py
baseline_tests/run_step8_momentum_exchange_diagnostics.py
logs/step8_static_bounceback_regression.log
logs/step8_prescribed_moving_wall.log
logs/step8_projected_mpm_boundary.log
logs/step8_momentum_exchange.log
outputs/step8_static_bounceback_regression/LBMStatic_100.vtr
outputs/step8_static_bounceback_regression/LBMMovingZero_100.vtr
outputs/step8_static_bounceback_regression/velocity_difference.npy
outputs/step8_static_bounceback_regression/rho_difference.npy
outputs/step8_prescribed_moving_wall/LBMFluid_1000.vtr
outputs/step8_prescribed_moving_wall/ux_profile_y.npy
outputs/step8_prescribed_moving_wall/diagnostics.npz
outputs/step8_projected_mpm_boundary/LBMFluid_100.vtr
outputs/step8_projected_mpm_boundary/particles_x.npy
outputs/step8_projected_mpm_boundary/particles_v.npy
outputs/step8_projected_mpm_boundary/solid.npy
outputs/step8_projected_mpm_boundary/solid_phi.npy
outputs/step8_projected_mpm_boundary/diagnostics.npz
outputs/step8_momentum_exchange/momentum_exchange_timeseries.npz
outputs/step8_momentum_exchange/LBMFluid_500.vtr
STEP8_MOVING_BOUNCEBACK_REPORT.md
```

Required source keywords:

```text
streaming_moving_bounceback
step_moving_bounceback
clear_moving_boundary_diagnostics
get_moving_boundary_stats
bb_link_count
bb_max_correction
bb_net_fluid_impulse
bb_net_solid_force
solid_vel
hydro_force
```

Required log markers:

```text
[OK] Step 8 static bounce-back regression finished
[OK] Step 8 prescribed moving wall Couette finished
[OK] Step 8 projected MPM moving boundary finished
[OK] Step 8 momentum-exchange diagnostics finished
bb_link_count
bb_max_correction
bb_net_fluid_impulse_x
bb_net_solid_force_x
cell_force_max_norm=0.000000000e+00
```

Forbidden tokens in Step 8 source and baselines:

```text
two_phase
contact_angle
ReducedSquidFSI
```

Do not forbid:

```text
momentum_exchange
moving_bounceback
update_dynamic_solid
reinitialize_new_fluid_cells
```

These are in scope for Step 8.

## 19. Hard Acceptance Checklist

All must pass:

```text
[ ] main is on the Step 8 final commit
[ ] original lbm.step() still exists
[ ] lbm.step_moving_bounceback() exists
[ ] LBMFluid3D.streaming_moving_bounceback() exists
[ ] LBMFluid3D.clear_moving_boundary_diagnostics() exists
[ ] LBMFluid3D.get_moving_boundary_stats() exists
[ ] bb_link_count field exists
[ ] bb_max_correction field exists
[ ] bb_net_fluid_impulse field exists
[ ] bb_net_solid_force field exists
[ ] zero wall velocity moving bounce-back is close to static bounce-back
[ ] prescribed moving wall drives fluid along wall velocity
[ ] projected MPM moving boundary drives fluid along projected solid velocity
[ ] moving wall +x gives bb_net_fluid_impulse_x > 0
[ ] moving wall +x gives bb_net_solid_force_x < 0
[ ] link-wise force balance error is small
[ ] hydro_force is nonzero for moving wall diagnostics
[ ] cell_force remains zero in Step 8 moving-bounceback baselines
[ ] PenaltyFSICoupler3D is not used in Step 8 moving-bounceback baselines
[ ] rho_min > 0.95
[ ] rho_max < 1.05
[ ] lbm_max_v < 0.1
[ ] no NaN
[ ] no Inf
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] logs are saved under logs/
[ ] outputs are saved under outputs/
[ ] STEP8_MOVING_BOUNCEBACK_REPORT.md is complete
[ ] pytest -q passes
```

## 20. Recommended Execution Order

Follow this order:

```text
1. Add Step 8 pytest contract/artifact checks.
2. Run pytest and confirm RED for missing Step 8 artifacts.
3. Add moving-boundary diagnostics fields to LBMFluid3D.
4. Add clear_moving_boundary_diagnostics().
5. Add streaming_moving_bounceback().
6. Add step_moving_bounceback().
7. Add get_moving_boundary_stats().
8. Add and run static bounce-back regression.
9. Add and run prescribed moving wall Couette.
10. Add and run projected MPM moving boundary baseline.
11. Add and run momentum-exchange diagnostics baseline.
12. Write STEP8_MOVING_BOUNCEBACK_REPORT.md.
13. Run final pytest.
14. Inspect git status and confirm external/ is unchanged.
15. Commit and push to GitHub.
```

Suggested commits:

```text
test: add step 8 moving bounce-back contract
feat: add moving bounce-back lbm path
feat: add step 8 moving-boundary baselines
```

## 21. Failure Handling

If any required baseline fails, stop and record:

```text
exact command
log path
first failing error
which acceptance item failed
whether failure is compile/import/runtime/numerical/output
next minimal fix
```

Do not weaken the required baselines and call Step 8 complete.

Shorter runs may be used only as clearly labeled diagnostic probes, followed by the full required baseline.

If the prescribed moving wall drives fluid in the wrong direction:

```text
1. do not change unrelated code;
2. flip only the moving-wall correction sign;
3. rerun static regression and prescribed moving wall;
4. document the final sign in STEP8_MOVING_BOUNCEBACK_REPORT.md.
```

## 22. Completion Definition

Step 8 is complete only when:

```text
1. Existing lbm.step() remains available and unchanged for penalty baselines.
2. New lbm.step_moving_bounceback() exists and is opt-in.
3. Moving bounce-back with zero wall velocity regresses to static bounce-back.
4. Prescribed moving wall drives fluid in correct direction.
5. Projected MPM moving boundary drives fluid in correct direction.
6. Link-wise momentum-exchange diagnostics show correct signs and small balance error.
7. cell_force remains zero in Step 8 moving-boundary baselines.
8. PenaltyFSICoupler3D is not used in Step 8 moving-boundary baselines.
9. All stability thresholds pass.
10. No forbidden physics or external edits are introduced.
11. Logs, outputs, and STEP8_MOVING_BOUNCEBACK_REPORT.md record evidence.
12. pytest passes.
13. The completed code, report, logs, and outputs are pushed to GitHub.
```

Completion means:

```text
The project has an opt-in LBM moving bounce-back sharp-interface scaffold with link-wise diagnostics.
```

Completion does not mean:

```text
full MPM reaction from moving-boundary momentum exchange is complete
real squid validation is complete
two-phase FSI exists
```

Those belong to Step 9 or later.
