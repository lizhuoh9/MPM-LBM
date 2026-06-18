# Step 9 Goal: Moving-Boundary Two-Way Reaction Coupling

## Paste-Ready `/goal`

```text
/goal
In D:\working\squid robot\LBM\MPM-LBM, execute Step 9: Moving-boundary two-way reaction coupling. The only authoritative execution contract is D:\working\squid robot\LBM\MPM-LBM\STEP9_MOVING_BOUNDARY_REACTION_GOAL.md.

Goal: transfer the Step 8 link-wise moving-boundary hydro_force diagnostic back to MPMSolid3D.grid_f_ext through a dedicated MovingBoundaryFSICoupler3D, so the moving-boundary path becomes a reproducible two-way FSI MVP. Preserve the Step 6/7 penalty two-way path and the Step 8 opt-in moving bounce-back path.

Hard boundaries: do not change the Step 8 moving bounce-back formula, do not make lbm.step_moving_bounceback() the default lbm.step(), do not replace or delete PenaltyFSICoupler3D, do not route moving-boundary reaction through lbm.cell_force, do not implement two-phase flow, contact angle physics, squid geometry, sparse storage, ReducedSquidFSI, strict final momentum-conserving sharp-interface FSI, or edits to external/taichi_LBM3D. PenaltyFSICoupler3D may appear only in the required comparison baseline.

Required artifacts, execution order, baseline settings, pytest contract, Hard Acceptance Checklist, failure handling, and completion definition are all defined in STEP9_MOVING_BOUNDARY_REACTION_GOAL.md. Finish only after all Step 9 baselines pass, pytest passes, and code/logs/outputs/report are pushed to GitHub.
```

## 1. Current Baseline

Step 8 is accepted and is the starting point.

Current Step 8 final commit:

```text
1192369824229d7febdab5bfd812a5ea14aa4d28
```

Step 8 validated:

```text
LBMFluid3D.step() remains the default penalty-compatible static-bounce-back path.
LBMFluid3D.step_moving_bounceback() is opt-in.
Moving-wall bounce-back with zero wall velocity regresses to static bounce-back.
Prescribed +x moving wall drives positive fluid ux.
Projected MPM solid_phi / solid_vel can drive moving-boundary bounce-back.
Link-wise diagnostics provide bb_link_count, bb_max_correction, bb_net_fluid_impulse, bb_net_solid_force, and hydro_force.
Step 8 moving-boundary baselines keep lbm.cell_force at zero.
Step 8 does not transfer moving-boundary hydro_force back to MPM.
```

Step 8 evidence:

```text
src/lbm_fluid.py
STEP8_MOVING_BOUNCEBACK_REPORT.md
baseline_tests/run_step8_static_bounceback_regression.py
baseline_tests/run_step8_prescribed_moving_wall_couette.py
baseline_tests/run_step8_projected_mpm_moving_boundary.py
baseline_tests/run_step8_momentum_exchange_diagnostics.py
logs/step8_static_bounceback_regression.log
logs/step8_prescribed_moving_wall.log
logs/step8_projected_mpm_boundary.log
logs/step8_momentum_exchange.log
outputs/step8_static_bounceback_regression/
outputs/step8_prescribed_moving_wall/
outputs/step8_projected_mpm_boundary/
outputs/step8_momentum_exchange/
tests/test_step8_moving_bounceback_contract.py
```

Step 8 means:

```text
The project has an opt-in LBM moving bounce-back sharp-interface scaffold with link-wise diagnostics.
```

Step 8 still does not mean:

```text
moving-boundary hydro_force is returned to MPM
moving-boundary two-way coupling is complete
strict momentum-conserving sharp-interface FSI is complete
real squid validation is complete
```

## 2. Step 9 Objective

Step 9 turns the Step 8 moving-boundary diagnostic force into a controlled two-way reaction MVP.

Implement this progression:

```text
MPM projection
  -> LBM dynamic solid mask + moving bounce-back
  -> link-wise hydro_force diagnostic on solid
  -> dedicated moving-boundary reaction transfer to MPMSolid3D.grid_f_ext
  -> MPM solid velocity / deformation responds
```

Step 9 must prove:

```text
1. Step 8 moving-boundary hydro_force can be sampled near MPM particles.
2. The sampled reaction can be written into MPMSolid3D.grid_f_ext.
3. A +x moving solid receives a net -x reaction in moving-boundary mode.
4. MPM solid mean vx decreases under this reaction.
5. A short moving-boundary two-way coupled smoke run is stable.
6. Penalty two-way mode and moving-boundary two-way mode both remain available and stable in a qualitative comparison.
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

If a short diagnostic probe is needed, label it as a probe and then rerun the full required baseline. Do not report short probes as full acceptance.

## 4. Strict Non-Goals

Do not implement these in Step 9:

```text
1. No new moving bounce-back formula.
2. No replacement or deletion of PenaltyFSICoupler3D.
3. No replacement of existing lbm.step() behavior.
4. No default switch from lbm.step() to lbm.step_moving_bounceback().
5. No moving-boundary reaction through lbm.cell_force.
6. No two-phase LBM.
7. No contact angle physics.
8. No squid geometry or real squid case.
9. No sparse storage.
10. No ReducedSquidFSI.
11. No edits to external/taichi_LBM3D.
12. No claim that strict momentum-conserving sharp-interface FSI is complete.
13. No claim that real squid FSI is validated.
```

Allowed in Step 9:

```text
dedicated moving-boundary reaction coupler
sampling Step 8 lbm.hydro_force near MPM particles
writing reaction force to MPMSolid3D.grid_f_ext
using lbm.update_dynamic_solid()
using lbm.reinitialize_new_fluid_cells()
using lbm.step_moving_bounceback()
using PenaltyFSICoupler3D only in the comparison baseline
```

Important distinction:

```text
Step 6/7 hydro_force is penalty-force reaction.
Step 8/9 hydro_force is link-wise moving-boundary diagnostic force on solid.
The two meanings must not be mixed in the same baseline.
```

## 5. Required Final Structure

Create:

```text
src/
  moving_boundary_coupling.py

baseline_tests/
  run_step9_moving_boundary_reaction_field.py
  run_step9_moving_boundary_two_way_mpm_reaction.py
  run_step9_moving_boundary_coupled_smoke.py
  run_step9_compare_penalty_vs_moving_boundary.py

outputs/
  step9_mb_reaction_field/
  step9_mb_two_way_reaction/
  step9_mb_coupled_smoke/
  step9_compare_modes/

logs/
  step9_mb_reaction_field.log
  step9_mb_two_way_reaction.log
  step9_mb_coupled_smoke.log
  step9_compare_modes.log

tests/
  test_step9_moving_boundary_reaction_contract.py

STEP9_MOVING_BOUNDARY_REACTION_REPORT.md
```

Update:

```text
src/__init__.py
```

Export:

```python
MovingBoundaryFSICoupler3D
```

## 6. Why Not Reuse PenaltyFSICoupler3D

Do not directly reuse `PenaltyFSICoupler3D.add_lbm_reaction_to_mpm_grid()` for Step 9 moving-boundary reaction.

Reason:

```text
PenaltyFSICoupler3D assumes lbm.hydro_force is the equal-and-opposite reaction to a penalty body-force density field.
Step 8 moving-boundary hydro_force is a link-wise diagnostic force on solid produced by bounce-back momentum exchange.
```

Therefore Step 9 must add a dedicated `MovingBoundaryFSICoupler3D` to avoid semantic mixing between penalty and moving-boundary modes.

## 7. MovingBoundaryFSICoupler3D Contract

Create:

```text
src/moving_boundary_coupling.py
```

Class:

```python
@ti.data_oriented
class MovingBoundaryFSICoupler3D:
    ...
```

Constructor:

```python
def __init__(
    self,
    sim_config,
    reaction_scale: float = 1.0,
    force_cap_norm: float = 1.0e-2,
    phi_min: float = 1.0e-6,
):
    ...
```

Required scalar parameters:

```text
self.n_grid
self.dx_norm
self.inv_dx_norm
self.lbm_dt_phys
self.reaction_scale
self.force_cap_norm
self.phi_min
self.force_density_scale_lbm_to_norm
```

Required diagnostic fields:

```text
self.active_reaction_particle_count = ti.field(ti.i32, shape=())
self.max_particle_reaction_norm = ti.field(ti.f32, shape=())
self.max_grid_reaction_norm = ti.field(ti.f32, shape=())
self.net_particle_reaction_force = ti.Vector.field(3, ti.f32, shape=())
self.net_grid_reaction_force = ti.Vector.field(3, ti.f32, shape=())
```

Required methods:

```text
inside_lbm(I, lbm)
clear_reaction_diagnostics()
add_moving_boundary_reaction_to_mpm_grid(solid, lbm)
get_stats()
```

## 8. Reaction Transfer Model

Step 9 reaction transfer should use particle sampling of LBM moving-boundary `hydro_force`, then write the resulting reaction into MPM grid force.

Core logic:

```text
for each MPM particle p:
    sample lbm.hydro_force at x[p] using the same 3x3x3 quadratic stencil as MPM
    sample lbm.solid_phi at x[p] using the same stencil
    if sampled_phi > phi_min:
        particle_volume = solid.vol0[p] * max(solid.Jp[p], 0)
        particle_force_norm = sampled_hydro_lbm * force_density_scale_lbm_to_norm * particle_volume * reaction_scale
        clamp particle_force_norm to force_cap_norm
        scatter particle_force_norm to solid.grid_f_ext with the MPM stencil
```

Use this initial engineering scale:

```text
force_density_scale_lbm_to_norm = dx_norm / lbm_dt_phys^2
particle_force_norm = sampled_hydro_lbm * force_density_scale_lbm_to_norm * particle_volume * reaction_scale
```

Report this explicitly as an engineering coupling scale for the Step 9 MVP. Do not claim it is the final strict momentum-conserving area/link integration model.

For a +x moving solid, the moving-boundary diagnostic solid force from Step 8 should produce a negative x reaction on the solid:

```text
net_particle_reaction_force_x < 0
net_grid_reaction_force_x < 0
```

## 9. Required Kernels

### 9.1 Clear reaction diagnostics

Add:

```python
@ti.kernel
def clear_reaction_diagnostics(self):
    self.active_reaction_particle_count[None] = 0
    self.max_particle_reaction_norm[None] = 0.0
    self.max_grid_reaction_norm[None] = 0.0
    self.net_particle_reaction_force[None] = ti.Vector([0.0, 0.0, 0.0])
    self.net_grid_reaction_force[None] = ti.Vector([0.0, 0.0, 0.0])
```

Do not clear `solid.grid_f_ext` in this method. `MPMSolid3D.clear_grid()` owns that reset.

### 9.2 Add moving-boundary reaction to MPM grid

Add:

```python
@ti.kernel
def add_moving_boundary_reaction_to_mpm_grid(
    self,
    solid: ti.template(),
    lbm: ti.template(),
):
    ...
```

Implementation requirements:

```text
1. Loop over solid.n_particles.
2. Use normalized coordinates and sim_config.dx_norm to locate the particle in LBM grid space.
3. Sample lbm.hydro_force and lbm.solid_phi using a 3x3x3 quadratic stencil.
4. Ignore particles with sampled_phi <= phi_min.
5. Convert sampled_hydro_lbm to normalized particle force using the Step 9 scale.
6. Clamp by force_cap_norm.
7. Add particle force to net_particle_reaction_force.
8. Scatter particle force to solid.grid_f_ext using the same 3x3x3 stencil.
9. Add grid contributions to net_grid_reaction_force.
10. Record active_reaction_particle_count, max_particle_reaction_norm, and max_grid_reaction_norm.
```

Do not call a Python method from inside a Taichi kernel. Baselines should call:

```python
solid.clear_grid()
solid.p2g()
mb_coupler.clear_reaction_diagnostics()
mb_coupler.add_moving_boundary_reaction_to_mpm_grid(solid, lbm)
solid.grid_update()
solid.g2p()
```

## 10. Moving-Boundary Two-Way Loop

Step 9 moving-boundary two-way mode must use this structure:

```python
for lbm_step in range(n_lbm_steps):
    projector.project(solid, lbm)
    lbm.update_dynamic_solid(threshold=0.5)
    lbm.reinitialize_new_fluid_cells()
    lbm.step_moving_bounceback()

    for _ in range(sim.mpm_substeps_per_lbm_step):
        solid.clear_grid()
        solid.p2g()
        mb_coupler.clear_reaction_diagnostics()
        mb_coupler.add_moving_boundary_reaction_to_mpm_grid(solid, lbm)
        solid.grid_update()
        solid.g2p()
```

This moving-boundary mode must not call:

```text
PenaltyFSICoupler3D.build_penalty_force()
PenaltyFSICoupler3D.add_lbm_reaction_to_mpm_grid()
lbm.set_uniform_cell_force()
lbm.set_spherical_cell_force()
```

The comparison baseline is the only Step 9 baseline allowed to import and use `PenaltyFSICoupler3D`.

## 11. Baseline 1: Reaction Field Sanity

Create:

```text
baseline_tests/run_step9_moving_boundary_reaction_field.py
```

Purpose:

```text
Verify Step 8 moving-boundary hydro_force can be sampled and written into MPMSolid3D.grid_f_ext.
```

Recommended settings:

```text
n_grid = 32
n_particles = 4096
gravity = (0, 0, 0)
target_u_lbm = (0.02, 0, 0)
threshold = 0.5
reaction_scale = 1.0
force_cap_norm = 1.0e-2
```

Required flow:

```text
1. Initialize all-fluid LBM geometry.
2. Initialize MPM block with +x velocity.
3. projector.project(solid, lbm)
4. lbm.update_dynamic_solid(threshold=0.5)
5. lbm.reinitialize_new_fluid_cells()
6. lbm.step_moving_bounceback()
7. solid.clear_grid()
8. solid.p2g()
9. mb_coupler.clear_reaction_diagnostics()
10. mb_coupler.add_moving_boundary_reaction_to_mpm_grid(solid, lbm)
11. Do not run grid_update() or g2p(); inspect grid_f_ext and diagnostics only.
```

Acceptance:

```text
bb_link_count > 0
hydro_force_max_norm > 0
active_reaction_particle_count > 0
max_particle_reaction_norm > 0
max_grid_reaction_norm > 0
net_particle_reaction_force_x < 0
net_grid_reaction_force_x < 0
cell_force_max_norm == 0
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
no NaN
no Inf
```

Required outputs:

```text
outputs/step9_mb_reaction_field/LBMFluid_0.vtr
outputs/step9_mb_reaction_field/grid_f_ext.npy
outputs/step9_mb_reaction_field/hydro_force.npy
outputs/step9_mb_reaction_field/diagnostics.npz
```

Required log:

```text
logs/step9_mb_reaction_field.log
```

Required log marker:

```text
[OK] Step 9 moving-boundary reaction field finished
```

## 12. Baseline 2: Two-Way MPM Reaction

Create:

```text
baseline_tests/run_step9_moving_boundary_two_way_mpm_reaction.py
```

Purpose:

```text
Verify moving-boundary link reaction can slow down a moving MPM solid without advancing multiple LBM steps.
```

Recommended settings:

```text
n_grid = 32
n_particles = 4096
gravity = (0, 0, 0)
target_u_lbm = (0.02, 0, 0)
threshold = 0.5
reaction_scale = 1.0
force_cap_norm = 1.0e-2
mpm_reaction_substeps = 100
```

Required flow:

```text
1. Initialize MPM block with +x velocity.
2. projector.project(solid, lbm)
3. lbm.update_dynamic_solid(threshold=0.5)
4. lbm.reinitialize_new_fluid_cells()
5. lbm.step_moving_bounceback()
6. Run multiple MPM substeps with mb_coupler.add_moving_boundary_reaction_to_mpm_grid().
7. Do not advance LBM multiple steps; isolate the reaction effect.
```

Acceptance:

```text
initial_solid_mean_vx_norm > 0
final_solid_mean_vx_norm < initial_solid_mean_vx_norm
net_grid_reaction_force_x < 0
active_reaction_particle_count > 0
mpm_min_J > 0
mpm_max_speed < 10
no NaN
no Inf
```

Required outputs:

```text
outputs/step9_mb_two_way_reaction/particles_x.npy
outputs/step9_mb_two_way_reaction/particles_v.npy
outputs/step9_mb_two_way_reaction/particles_F.npy
outputs/step9_mb_two_way_reaction/particles_J.npy
outputs/step9_mb_two_way_reaction/diagnostics.npz
```

Required log:

```text
logs/step9_mb_two_way_reaction.log
```

Required log marker:

```text
[OK] Step 9 moving-boundary MPM reaction finished
```

## 13. Baseline 3: Moving-Boundary Coupled Smoke

Create:

```text
baseline_tests/run_step9_moving_boundary_coupled_smoke.py
```

Purpose:

```text
Run a short full moving-boundary two-way coupled loop.
```

Recommended settings:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 20
mpm_substeps_per_lbm_step = 10
gravity = (0, 0, 0)
target_u_lbm = (0.02, 0, 0)
threshold = 0.5
reaction_scale = 1.0
force_cap_norm = 1.0e-2
```

Acceptance:

```text
completed_lbm_steps = 20
total_mpm_substeps = 200
bb_link_count > 0
hydro_force_max_norm > 0
active_reaction_particle_count > 0
projection_zone_fluid_mean_ux_final > projection_zone_fluid_mean_ux_initial
solid_mean_vx_final < solid_mean_vx_initial
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
cell_force_max_norm == 0
no NaN
no Inf
```

Required outputs:

```text
outputs/step9_mb_coupled_smoke/LBMFluid_20.vtr
outputs/step9_mb_coupled_smoke/particles_x.npy
outputs/step9_mb_coupled_smoke/particles_v.npy
outputs/step9_mb_coupled_smoke/particles_F.npy
outputs/step9_mb_coupled_smoke/particles_J.npy
outputs/step9_mb_coupled_smoke/diagnostics_timeseries.npz
```

Required log:

```text
logs/step9_mb_coupled_smoke.log
```

Required log marker:

```text
[OK] Step 9 moving-boundary coupled smoke finished
```

## 14. Baseline 4: Penalty vs Moving-Boundary Comparison

Create:

```text
baseline_tests/run_step9_compare_penalty_vs_moving_boundary.py
```

Purpose:

```text
Compare Step 7 penalty mode and Step 9 moving-boundary mode under similar initial conditions.
```

Penalty mode flow:

```python
projector.project(solid, lbm)
penalty_coupler.build_penalty_force(lbm)
lbm.step()
for _ in range(sim.mpm_substeps_per_lbm_step):
    solid.clear_grid()
    solid.p2g()
    penalty_coupler.add_lbm_reaction_to_mpm_grid(solid, lbm)
    solid.grid_update()
    solid.g2p()
```

Moving-boundary mode flow:

```python
projector.project(solid, lbm)
lbm.update_dynamic_solid(threshold=0.5)
lbm.reinitialize_new_fluid_cells()
lbm.step_moving_bounceback()
for _ in range(sim.mpm_substeps_per_lbm_step):
    solid.clear_grid()
    solid.p2g()
    mb_coupler.clear_reaction_diagnostics()
    mb_coupler.add_moving_boundary_reaction_to_mpm_grid(solid, lbm)
    solid.grid_update()
    solid.g2p()
```

Recommended settings:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 20
mpm_substeps_per_lbm_step = 10
target_u_lbm = (0.02, 0, 0)
```

Record:

```text
mode
stable
fluid_mean_ux_final
projection_zone_ux_final
solid_mean_vx_initial
solid_mean_vx_final
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
active_force_or_bb_link_count
cell_force_max_norm
hydro_force_max_norm
```

Acceptance:

```text
both modes stable
both modes fluid ux increases
both modes solid vx decreases
moving-boundary mode has cell_force_max_norm == 0
penalty mode has cell_force_max_norm > 0
moving-boundary mode has bb_link_count > 0
rho_min > 0.95 for both modes
rho_max < 1.05 for both modes
lbm_max_v < 0.1 for both modes
mpm_min_J > 0 for both modes
mpm_max_speed < 10 for both modes
no NaN
no Inf
```

Required outputs:

```text
outputs/step9_compare_modes/comparison_results.csv
outputs/step9_compare_modes/comparison_results.npz
```

Required log:

```text
logs/step9_compare_modes.log
```

Required log marker:

```text
[OK] Step 9 penalty vs moving-boundary comparison finished
```

## 15. Required Report

Create:

```text
STEP9_MOVING_BOUNDARY_REACTION_REPORT.md
```

Report must include:

```text
1. Goal
2. Files created/updated
3. Reaction transfer model and unit scale
4. Explicit non-goals
5. Reaction field sanity command/result
6. Two-way MPM reaction command/result
7. Moving-boundary coupled smoke command/result
8. Penalty vs moving-boundary comparison command/result
9. Hard Acceptance Checklist
10. Decision: can proceed to Step 10 or not
```

Report must explicitly state:

```text
Step 9 adds a dedicated moving-boundary reaction coupler.
Step 9 does not replace the Step 6/7 penalty coupler.
Step 9 does not change the Step 8 moving bounce-back formula.
Step 9 moving-boundary reaction uses an engineering coupling scale, not a final strict momentum-conserving sharp-interface integration.
Step 9 moving-boundary mode keeps lbm.cell_force at zero.
```

Recommended report template:

````markdown
# Step 9 Moving-Boundary Reaction Report

## 1. Goal

Transfer Step 8 link-wise moving-boundary hydro_force back to MPMSolid3D.grid_f_ext and validate moving-boundary two-way coupling.

## 2. Files

Created / updated:

- src/moving_boundary_coupling.py
- src/__init__.py
- baseline_tests/run_step9_moving_boundary_reaction_field.py
- baseline_tests/run_step9_moving_boundary_two_way_mpm_reaction.py
- baseline_tests/run_step9_moving_boundary_coupled_smoke.py
- baseline_tests/run_step9_compare_penalty_vs_moving_boundary.py
- tests/test_step9_moving_boundary_reaction_contract.py

## 3. Reaction model

```text
sampled_hydro_lbm = sum(weight * lbm.hydro_force[I])
force_density_scale_lbm_to_norm = dx_norm / lbm_dt_phys^2
particle_force_norm = sampled_hydro_lbm * force_density_scale_lbm_to_norm * particle_volume * reaction_scale
solid.grid_f_ext += weight * particle_force_norm
```

## 4. Explicit non-goals

Step 9 does not implement a new bounce-back formula, two-phase flow, contact angle physics, squid geometry, sparse storage, ReducedSquidFSI, or external/taichi_LBM3D edits.

## 5. Reaction field sanity

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step9_moving_boundary_reaction_field.py
```

Result:

- bb_link_count:
- hydro_force_max_norm:
- active_reaction_particle_count:
- max_grid_reaction_norm:
- net_grid_reaction_force_x:

## 6. Two-way MPM reaction

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step9_moving_boundary_two_way_mpm_reaction.py
```

Result:

- initial_solid_mean_vx_norm:
- final_solid_mean_vx_norm:
- net_grid_reaction_force_x:
- mpm_min_J:
- mpm_max_speed:

## 7. Moving-boundary coupled smoke

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step9_moving_boundary_coupled_smoke.py
```

Result:

- completed_lbm_steps:
- total_mpm_substeps:
- projection_zone_fluid_mean_ux_initial:
- projection_zone_fluid_mean_ux_final:
- initial_solid_mean_vx_norm:
- final_solid_mean_vx_norm:
- rho_min:
- rho_max:
- mpm_min_J:

## 8. Penalty vs moving-boundary comparison

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step9_compare_penalty_vs_moving_boundary.py
```

Result:

| mode | stable | fluid_mean_ux_final | solid_mean_vx_final | rho_min | rho_max | mpm_min_J |
| ---- | ------ | ------------------: | ------------------: | ------: | ------: | --------: |

## 9. Acceptance checklist

- [ ] main is on the Step 9 final commit
- [ ] src/moving_boundary_coupling.py exists
- [ ] src/__init__.py exports MovingBoundaryFSICoupler3D
- [ ] MovingBoundaryFSICoupler3D exists
- [ ] add_moving_boundary_reaction_to_mpm_grid() exists
- [ ] moving-boundary hydro_force can write to MPMSolid3D.grid_f_ext
- [ ] reaction field baseline passes
- [ ] two-way MPM reaction baseline passes
- [ ] moving-boundary coupled smoke passes
- [ ] penalty vs moving-boundary comparison passes
- [ ] net_grid_reaction_force_x < 0 for +x moving solid
- [ ] moving-boundary reaction gives solid slowdown
- [ ] moving-boundary mode keeps cell_force_max_norm == 0
- [ ] moving-boundary mode has bb_link_count > 0
- [ ] penalty mode remains available and stable
- [ ] rho_min > 0.95
- [ ] rho_max < 1.05
- [ ] lbm_max_v < 0.1
- [ ] mpm_min_J > 0
- [ ] mpm_max_speed < 10
- [ ] no NaN
- [ ] no Inf
- [ ] no two-phase flow
- [ ] no contact angle physics
- [ ] no ReducedSquidFSI
- [ ] no external/taichi_LBM3D edits
- [ ] logs are saved under logs/
- [ ] outputs are saved under outputs/
- [ ] STEP9_MOVING_BOUNDARY_REACTION_REPORT.md is complete
- [ ] pytest -q passes

## 10. Decision

Can proceed to Step 10?

- [ ] Yes
- [ ] No
````

## 16. Pytest Contract

Create:

```text
tests/test_step9_moving_boundary_reaction_contract.py
```

Recommended tests:

```python
def test_step9_required_artifacts_exist():
    ...

def test_step9_source_contains_required_interfaces():
    ...

def test_step9_scripts_respect_mode_boundaries():
    ...

def test_step9_logs_record_successful_baselines:
    ...

def test_step9_report_acceptance_complete():
    ...
```

Required artifact paths:

```text
src/moving_boundary_coupling.py
baseline_tests/run_step9_moving_boundary_reaction_field.py
baseline_tests/run_step9_moving_boundary_two_way_mpm_reaction.py
baseline_tests/run_step9_moving_boundary_coupled_smoke.py
baseline_tests/run_step9_compare_penalty_vs_moving_boundary.py
logs/step9_mb_reaction_field.log
logs/step9_mb_two_way_reaction.log
logs/step9_mb_coupled_smoke.log
logs/step9_compare_modes.log
outputs/step9_mb_reaction_field/LBMFluid_0.vtr
outputs/step9_mb_reaction_field/grid_f_ext.npy
outputs/step9_mb_reaction_field/hydro_force.npy
outputs/step9_mb_reaction_field/diagnostics.npz
outputs/step9_mb_two_way_reaction/particles_x.npy
outputs/step9_mb_two_way_reaction/particles_v.npy
outputs/step9_mb_two_way_reaction/particles_F.npy
outputs/step9_mb_two_way_reaction/particles_J.npy
outputs/step9_mb_two_way_reaction/diagnostics.npz
outputs/step9_mb_coupled_smoke/LBMFluid_20.vtr
outputs/step9_mb_coupled_smoke/particles_x.npy
outputs/step9_mb_coupled_smoke/particles_v.npy
outputs/step9_mb_coupled_smoke/particles_F.npy
outputs/step9_mb_coupled_smoke/particles_J.npy
outputs/step9_mb_coupled_smoke/diagnostics_timeseries.npz
outputs/step9_compare_modes/comparison_results.csv
outputs/step9_compare_modes/comparison_results.npz
STEP9_MOVING_BOUNDARY_REACTION_REPORT.md
```

Required source keywords:

```text
class MovingBoundaryFSICoupler3D
add_moving_boundary_reaction_to_mpm_grid
clear_reaction_diagnostics
force_density_scale_lbm_to_norm
reaction_scale
force_cap_norm
phi_min
grid_f_ext
hydro_force
bb_link_count
active_reaction_particle_count
net_particle_reaction_force
net_grid_reaction_force
```

Required log markers:

```text
[OK] Step 9 moving-boundary reaction field finished
[OK] Step 9 moving-boundary MPM reaction finished
[OK] Step 9 moving-boundary coupled smoke finished
[OK] Step 9 penalty vs moving-boundary comparison finished
active_reaction_particle_count
net_grid_reaction_force_x
cell_force_max_norm=0.000000000e+00
bb_link_count
```

Forbidden tokens in Step 9 source and baselines:

```text
two_phase
contact_angle
ReducedSquidFSI
```

Do not forbid:

```text
PenaltyFSICoupler3D
```

Reason: `PenaltyFSICoupler3D` is required in the Step 9 comparison baseline.

Mode-boundary test requirement:

```text
The three moving-boundary baselines must not call PenaltyFSICoupler3D.
Only baseline_tests/run_step9_compare_penalty_vs_moving_boundary.py may call PenaltyFSICoupler3D.
```

## 17. Hard Acceptance Checklist

All must pass:

```text
[ ] main is on the Step 9 final commit
[ ] src/moving_boundary_coupling.py exists
[ ] src/__init__.py exports MovingBoundaryFSICoupler3D
[ ] MovingBoundaryFSICoupler3D exists
[ ] clear_reaction_diagnostics() exists
[ ] add_moving_boundary_reaction_to_mpm_grid() exists
[ ] force_density_scale_lbm_to_norm is documented and used
[ ] moving-boundary hydro_force can write to MPMSolid3D.grid_f_ext
[ ] reaction field baseline completes
[ ] reaction field baseline has active_reaction_particle_count > 0
[ ] reaction field baseline has net_grid_reaction_force_x < 0 for +x moving solid
[ ] two-way MPM reaction baseline completes
[ ] two-way MPM reaction baseline shows final_solid_mean_vx_norm < initial_solid_mean_vx_norm
[ ] moving-boundary coupled smoke completes 20 LBM steps
[ ] moving-boundary coupled smoke completes 200 MPM substeps
[ ] comparison baseline completes
[ ] comparison baseline shows penalty mode stable
[ ] comparison baseline shows moving-boundary mode stable
[ ] moving-boundary mode keeps cell_force_max_norm == 0
[ ] moving-boundary mode has bb_link_count > 0
[ ] penalty mode has cell_force_max_norm > 0
[ ] rho_min > 0.95
[ ] rho_max < 1.05
[ ] lbm_max_v < 0.1
[ ] mpm_min_J > 0
[ ] mpm_max_speed < 10
[ ] no NaN
[ ] no Inf
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] logs are saved under logs/
[ ] outputs are saved under outputs/
[ ] STEP9_MOVING_BOUNDARY_REACTION_REPORT.md is complete
[ ] pytest -q passes
```

## 18. Recommended Execution Order

Follow this order:

```text
1. Add Step 9 pytest contract/artifact checks.
2. Run pytest and confirm RED for missing Step 9 artifacts.
3. Create src/moving_boundary_coupling.py.
4. Implement MovingBoundaryFSICoupler3D fields and constructor.
5. Implement inside_lbm().
6. Implement clear_reaction_diagnostics().
7. Implement add_moving_boundary_reaction_to_mpm_grid().
8. Export MovingBoundaryFSICoupler3D from src/__init__.py.
9. Add and run reaction field sanity baseline.
10. Add and run two-way MPM reaction baseline.
11. Add and run moving-boundary coupled smoke baseline.
12. Add and run penalty vs moving-boundary comparison baseline.
13. Write STEP9_MOVING_BOUNDARY_REACTION_REPORT.md.
14. Run final pytest -q.
15. Inspect git diff and git status.
16. Confirm external/taichi_LBM3D is unchanged.
17. Commit and push code, logs, outputs, tests, and report to GitHub.
```

Suggested commits:

```text
test: add step 9 moving-boundary reaction contract
feat: add moving-boundary reaction coupler
feat: add step 9 two-way reaction baselines
docs: add step 9 moving-boundary reaction report
```

It is acceptable to squash into one final commit if the user asks for a single deliverable commit.

## 19. Failure Handling

If any required baseline fails, stop and record:

```text
exact command
log path
first failing error
which acceptance item failed
whether failure is compile/import/runtime/numerical/output
next minimal fix
```

Do not weaken the required baselines and call Step 9 complete.

If reaction force has the wrong sign:

```text
1. Do not change Step 8 moving bounce-back formula.
2. Inspect whether sampled lbm.hydro_force is solid force or fluid impulse.
3. Fix only the Step 9 transfer sign if needed.
4. Rerun reaction field, two-way MPM reaction, and coupled smoke baselines.
5. Document final sign convention in STEP9_MOVING_BOUNDARY_REACTION_REPORT.md.
```

If MPM becomes unstable:

```text
1. Reduce reaction_scale.
2. Reduce force_cap_norm.
3. Keep required full baselines after tuning.
4. Document the final stable reaction window.
```

Do not hide instability by reducing the required acceptance run length.

## 20. Completion Definition

Step 9 is complete only when:

```text
1. MovingBoundaryFSICoupler3D exists and is exported.
2. Step 8 moving-boundary hydro_force is transferred to MPMSolid3D.grid_f_ext.
3. Reaction field sanity baseline passes.
4. Two-way MPM reaction baseline passes and shows solid slowdown.
5. Moving-boundary coupled smoke passes.
6. Penalty vs moving-boundary comparison passes.
7. Moving-boundary mode keeps lbm.cell_force at zero.
8. Penalty path remains available and unchanged.
9. No forbidden physics or external edits are introduced.
10. Logs, outputs, and STEP9_MOVING_BOUNDARY_REACTION_REPORT.md record evidence.
11. pytest -q passes.
12. The completed code, report, logs, and outputs are pushed to GitHub.
```

Completion means:

```text
The project has a moving-boundary two-way MPM-LBM coupling MVP in addition to the existing penalty two-way MVP.
```

Completion does not mean:

```text
strict final momentum-conserving sharp-interface FSI is complete
real squid validation is complete
two-phase FSI exists
```

Those belong to later steps.
