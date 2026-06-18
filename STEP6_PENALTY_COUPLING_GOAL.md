# Step 6 Goal: Penalty-Force Two-Way Coupling MVP

## Paste-Ready `/goal`

```text
/goal
In D:\working\squid robot\LBM\MPM-LBM, execute Step 6: Penalty-force two-way coupling MVP. The only authoritative execution contract is D:\working\squid robot\LBM\MPM-LBM\STEP6_PENALTY_COUPLING_GOAL.md.

Goal: using the Step 5 projection fields solid_phi, solid_mass, and solid_vel, build the first penalty-force MPM-LBM two-way coupling MVP. Construct LBM cell_force = beta_lbm * solid_phi * rho * (solid_vel - fluid_vel), set hydro_force = -cell_force, and transfer hydro_force back to MPMSolid3D.grid_f_ext with explicit unit conversion. Demonstrate that moving MPM solids drag LBM fluid, and LBM reaction slows MPM solids, under small stable parameters.

Hard boundaries: do not implement moving bounce-back, momentum exchange, sharp-interface FSI, two-phase flow, contact angle physics, squid geometry, sparse storage, ReducedSquidFSI, or edits to external/taichi_LBM3D. In Step 6 penalty coupling baselines, do not call update_dynamic_solid() to mark projected MPM cells as LBM solids; Step 6 must isolate penalty forcing from dynamic-mask/bounce-back behavior. Do not report a short diagnostic probe as full acceptance.

Required artifacts, execution order, baseline settings, Hard Acceptance Checklist, failure handling, and completion definition are all defined in STEP6_PENALTY_COUPLING_GOAL.md. Finish only after all Step 6 baselines pass, pytest passes, and code/logs/outputs/report are pushed to GitHub.
```

## 1. Current Baseline

Step 5 is accepted and is the starting point.

Existing Step 5 modules:

```text
src/lbm_config.py
src/lbm_fluid.py
src/mpm_config.py
src/mpm_solid.py
src/sim_config.py
src/units.py
src/projection.py
```

Step 5 validated:

```text
MPMToLBMProjector3D projects MPM particles to LBM solid_phi, solid_mass, solid_vel.
solid_vel is converted from normalized MPM velocity to LBM lattice velocity.
solid_phi is clamped to [0, 1].
projected mass is conserved within required tolerance.
cell_force and hydro_force remain zero in Step 5.
dynamic solid mask dry-run works but is not used as FSI evidence.
```

Step 5 evidence:

```text
STEP5_MPM_TO_LBM_PROJECTION_REPORT.md
logs/step5_projection_static.log
logs/step5_projection_moving.log
logs/step5_projection_motion.log
logs/step5_dynamic_solid_mask.log
outputs/step5_projection_static/LBMProjection_0.vtr
outputs/step5_projection_moving/LBMProjection_0.vtr
outputs/step5_projection_motion/LBMProjection_0.vtr
outputs/step5_projection_motion/LBMProjection_1.vtr
outputs/step5_dynamic_solid_mask/LBMProjection_mask_on.vtr
outputs/step5_dynamic_solid_mask/LBMProjection_mask_off.vtr
```

Carry-forward issue that Step 6 must solve:

```text
LBM can see MPM solids as projected fields, but no force coupling exists.
cell_force and hydro_force are still diagnostic placeholders.
MPM grid_f_ext exists but is not yet fed by LBM reaction.
```

## 2. Objective

Implement:

```text
PenaltyFSICoupler3D
LBM penalty force field construction
hydro_force = -cell_force reaction field
LBM hydro_force -> MPM grid_f_ext transfer
one-way LBM response baseline
one-way MPM reaction baseline
full small coupled smoke baseline
```

Step 6 must prove four things:

```text
1. Moving projected MPM solid creates nonzero LBM cell_force in the correct direction.
2. hydro_force is equal and opposite to cell_force.
3. LBM fluid velocity responds to moving projected solid.
4. MPM solid velocity responds to LBM reaction force.
```

Step 6 creates a minimum penalty-force two-way coupling prototype. It is not sharp-interface FSI and does not implement no-slip by moving bounce-back or momentum exchange.

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

Do not implement these in Step 6:

```text
1. No moving bounce-back.
2. No momentum exchange method.
3. No sharp-interface FSI.
4. No two-phase flow.
5. No contact angle physics.
6. No squid geometry or real squid case.
7. No sparse storage.
8. No ReducedSquidFSI.
9. No edits to external/taichi_LBM3D core files.
10. No update_dynamic_solid() in Step 6 penalty coupling baselines.
11. No reinitialize_new_fluid_cells() in Step 6 penalty coupling baselines.
```

Important boundary:

```text
Step 6 penalty coupling must not turn projected MPM cells into LBM solid cells.
The LBM fluid field must remain active in the projected region so the penalty body force can drag fluid velocity.
Dynamic solid mask was validated in Step 5 as a dry run only. It must not be mixed into Step 6 coupling evidence.
```

Allowed in Step 6:

```text
write lbm.cell_force
write lbm.hydro_force
read lbm.solid_phi
read lbm.solid_vel
read lbm.rho
read lbm.v
write solid.grid_f_ext during explicit coupled MPM substeps
call lbm.step()
call solid.clear_grid(), solid.p2g(), solid.grid_update(), solid.g2p()
```

## 5. Required Final Structure

Create or update:

```text
src/
  __init__.py
  coupling.py

baseline_tests/
  run_step6_penalty_force_field.py
  run_step6_lbm_response_to_moving_solid.py
  run_step6_two_way_mpm_reaction.py
  run_step6_coupled_smoke.py

outputs/
  step6_penalty_force_field/
  step6_lbm_response/
  step6_two_way_reaction/
  step6_coupled_smoke/

logs/
  step6_penalty_force_field.log
  step6_lbm_response.log
  step6_two_way_reaction.log
  step6_coupled_smoke.log

tests/
  test_step6_penalty_coupling_contract.py

STEP6_PENALTY_COUPLING_REPORT.md
```

Update `src/__init__.py` to export:

```python
from .coupling import PenaltyFSICoupler3D
```

and include `"PenaltyFSICoupler3D"` in `__all__`.

## 6. Coupling Model

Use Step 5 projection fields:

```text
lbm.solid_phi
lbm.solid_mass
lbm.solid_vel
```

Build LBM penalty force:

```text
cell_force = beta_lbm * solid_phi * rho_f * (u_solid - u_fluid)
```

Set reaction field:

```text
hydro_force = -cell_force
```

Direction convention:

```text
If projected MPM solid velocity is +x and fluid velocity is zero:
  solid_vel - fluid_vel > 0
  cell_force_x > 0
  hydro_force_x < 0
```

Interpretation:

```text
cell_force drags LBM fluid toward the moving solid.
hydro_force is the equal-and-opposite reaction applied back to MPM.
```

## 7. `PenaltyFSICoupler3D` Required Interface

Create:

```text
src/coupling.py
```

Implement:

```python
@ti.data_oriented
class PenaltyFSICoupler3D:
    def __init__(
        self,
        sim_config,
        beta_lbm: float = 1.0e-3,
        phi_min: float = 1.0e-6,
        force_cap_lbm: float = 1.0e-4,
        reaction_scale: float = 1.0,
    ):
        ...

    @ti.kernel
    def clear_force_fields(self, lbm: ti.template()):
        ...

    @ti.func
    def inside_lbm(self, I, lbm: ti.template()):
        ...

    @ti.kernel
    def build_penalty_force(self, lbm: ti.template()):
        ...

    @ti.kernel
    def add_lbm_reaction_to_mpm_grid(self, solid: ti.template(), lbm: ti.template()):
        ...

    def get_stats(self):
        ...
```

Required configuration fields:

```text
n_grid
dx_norm
inv_dx_norm
lbm_dt_phys
beta_lbm
phi_min
force_cap_lbm
reaction_scale
force_density_scale_lbm_to_norm
```

Required diagnostic fields:

```text
active_force_cell_count
max_cell_force_norm
max_hydro_force_norm
net_cell_force
net_hydro_force
max_reaction_grid_force_norm
net_reaction_grid_force
```

Recommended defaults:

```text
beta_lbm = 1.0e-3
phi_min = 1.0e-6
force_cap_lbm = 1.0e-4
reaction_scale = 1.0
```

## 8. Force Field Construction

`clear_force_fields()`:

```python
@ti.kernel
def clear_force_fields(self, lbm: ti.template()):
    for I in ti.grouped(lbm.rho):
        lbm.cell_force[I] = ti.Vector([0.0, 0.0, 0.0])
        lbm.hydro_force[I] = ti.Vector([0.0, 0.0, 0.0])
```

`build_penalty_force()`:

```python
@ti.kernel
def build_penalty_force(self, lbm: ti.template()):
    self.active_force_cell_count[None] = 0
    self.max_cell_force_norm[None] = 0.0
    self.max_hydro_force_norm[None] = 0.0
    self.net_cell_force[None] = ti.Vector([0.0, 0.0, 0.0])
    self.net_hydro_force[None] = ti.Vector([0.0, 0.0, 0.0])

    for I in ti.grouped(lbm.rho):
        force = ti.Vector([0.0, 0.0, 0.0])

        if lbm.solid[I] == 0:
            phi = lbm.solid_phi[I]
            if phi > self.phi_min:
                delta_u = lbm.solid_vel[I] - lbm.v[I]
                force = self.beta_lbm * phi * lbm.rho[I] * delta_u

                norm = force.norm()
                if norm > self.force_cap_lbm:
                    force = force * (self.force_cap_lbm / norm)

                ti.atomic_add(self.active_force_cell_count[None], 1)

        lbm.cell_force[I] = force
        lbm.hydro_force[I] = -force

        ti.atomic_max(self.max_cell_force_norm[None], force.norm())
        ti.atomic_max(self.max_hydro_force_norm[None], force.norm())
        ti.atomic_add(self.net_cell_force[None], force)
        ti.atomic_add(self.net_hydro_force[None], -force)
```

Required invariants:

```text
cell_force is zero outside active projected cells.
hydro_force = -cell_force.
force norm is capped by force_cap_lbm.
active_force_cell_count counts cells with phi > phi_min.
```

## 9. Reaction Transfer To MPM

MPM `grid_f_ext` expects normalized force on MPM grid nodes.

Unit conversion:

```text
a_norm = a_lbm * dx_norm / lbm_dt_phys^2
force_density_norm = force_density_lbm * dx_norm / lbm_dt_phys^2
force_density_scale_lbm_to_norm = dx_norm / lbm_dt_phys^2
```

Recommended transfer:

```text
hydro_density_lbm_at_particle = sum(weight * lbm.hydro_force[I])
hydro_density_norm = hydro_density_lbm_at_particle * force_density_scale_lbm_to_norm
particle_force_norm = hydro_density_norm * current_particle_volume * reaction_scale
grid_f_ext += weight * particle_force_norm
```

Implement:

```python
@ti.kernel
def add_lbm_reaction_to_mpm_grid(self, solid: ti.template(), lbm: ti.template()):
    self.max_reaction_grid_force_norm[None] = 0.0
    self.net_reaction_grid_force[None] = ti.Vector([0.0, 0.0, 0.0])

    for p in range(solid.n_particles):
        Xp = solid.x[p] * self.inv_dx_norm
        base = ti.cast(Xp - 0.5, ti.i32)
        fx = Xp - ti.cast(base, ti.f32)

        w = [...]
        hydro_density_lbm = ti.Vector([0.0, 0.0, 0.0])

        for offset in ti.static(ti.grouped(ti.ndrange(3, 3, 3))):
            I = base + offset
            if self.inside_lbm(I, lbm):
                weight = ...
                hydro_density_lbm += weight * lbm.hydro_force[I]

        J = ti.max(solid.Jp[p], 0.0)
        particle_volume = solid.vol0[p] * J
        particle_force_norm = (
            hydro_density_lbm
            * self.force_density_scale_lbm_to_norm
            * particle_volume
            * self.reaction_scale
        )

        for offset in ti.static(ti.grouped(ti.ndrange(3, 3, 3))):
            I = base + offset
            if solid.inside_grid(I):
                weight = ...
                contribution = weight * particle_force_norm
                ti.atomic_add(solid.grid_f_ext[I], contribution)
                ti.atomic_max(self.max_reaction_grid_force_norm[None], contribution.norm())
                ti.atomic_add(self.net_reaction_grid_force[None], contribution)
```

Important:

```text
Do not call solid.substep() when applying reaction force, because solid.substep() calls clear_grid() internally.
Use explicit MPM substep order:
  solid.clear_grid()
  solid.p2g()
  coupler.add_lbm_reaction_to_mpm_grid(solid, lbm)
  solid.grid_update()
  solid.g2p()
```

## 10. Coupled Step Order

Use this weakly coupled order:

```python
for lbm_step in range(n_lbm_steps):
    projector.project(solid, lbm)
    coupler.build_penalty_force(lbm)
    lbm.step()

    for _ in range(sim.mpm_substeps_per_lbm_step):
        solid.clear_grid()
        solid.p2g()
        coupler.add_lbm_reaction_to_mpm_grid(solid, lbm)
        solid.grid_update()
        solid.g2p()
```

Do not insert:

```text
lbm.update_dynamic_solid()
lbm.reinitialize_new_fluid_cells()
```

into Step 6 penalty coupling loops.

## 11. Required Baselines

### 11.1 Penalty Force Field

Create:

```text
baseline_tests/run_step6_penalty_force_field.py
```

Purpose:

```text
Verify projected solid_phi/solid_vel produce nonzero cell_force and equal-opposite hydro_force.
Do not advance LBM.
Do not advance MPM.
```

Required flow:

```text
1. Initialize all-fluid LBM.
2. Initialize MPM block with gravity=(0,0,0).
3. Set target_u_lbm=(0.03,0,0).
4. Convert target_u_norm with GridUnitMapper.
5. solid.set_uniform_velocity(*target_u_norm).
6. projector.project(solid, lbm).
7. coupler.clear_force_fields(lbm).
8. coupler.build_penalty_force(lbm).
9. Check direction, balance, and unchanged state.
```

Acceptance:

```text
active_force_cell_count > 0
cell_force_max_norm > 0
hydro_force_max_norm > 0
net_cell_force_x > 0
net_hydro_force_x < 0
norm(net_cell_force + net_hydro_force) < 1e-10
abs(net_cell_force_y) < 1e-10
abs(net_cell_force_z) < 1e-10
rho unchanged
MPM J unchanged
no NaN
no Inf
```

Required outputs:

```text
outputs/step6_penalty_force_field/LBMForce_0.vtr
outputs/step6_penalty_force_field/cell_force.npy
outputs/step6_penalty_force_field/hydro_force.npy
```

### 11.2 LBM Response To Moving Solid

Create:

```text
baseline_tests/run_step6_lbm_response_to_moving_solid.py
```

Purpose:

```text
Verify moving projected solid drags LBM fluid in the projected active zone.
This baseline may keep MPM prescribed and does not need MPM reaction.
```

Recommended settings:

```text
target_u_lbm = (0.03, 0.0, 0.0)
beta_lbm = 1.0e-3 or 3.0e-3
force_cap_lbm = 1.0e-4
n_lbm_steps = 100
gravity = (0.0, 0.0, 0.0)
```

Required loop:

```python
for step in range(n_lbm_steps):
    projector.project(solid, lbm)
    coupler.build_penalty_force(lbm)
    lbm.step()
```

Acceptance:

```text
initial_fluid_mean_ux recorded in active projected zone
final_fluid_mean_ux > initial_fluid_mean_ux
final_fluid_mean_ux > 0
active_force_cell_count > 0
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
no NaN
no Inf
```

Required outputs:

```text
outputs/step6_lbm_response/LBMFluid_100.vtr
outputs/step6_lbm_response/cell_force.npy
outputs/step6_lbm_response/hydro_force.npy
```

### 11.3 Two-Way MPM Reaction

Create:

```text
baseline_tests/run_step6_two_way_mpm_reaction.py
```

Purpose:

```text
Verify hydro_force reaction path decreases MPM solid velocity.
This baseline may avoid advancing LBM and isolate MPM reaction transfer.
```

Recommended settings:

```text
target_u_lbm = (0.03, 0.0, 0.0)
target_u_norm = GridUnitMapper.velocity_lbm_to_norm(target_u_lbm)
gravity = (0.0, 0.0, 0.0)
reaction_substeps = 50
beta_lbm = 1.0e-3
force_cap_lbm = 1.0e-4
```

Required flow:

```text
1. Initialize moving MPM block.
2. Record initial_solid_mean_vx_norm.
3. Project and build penalty force.
4. For reaction_substeps, use explicit MPM sequence:
   solid.clear_grid()
   solid.p2g()
   coupler.add_lbm_reaction_to_mpm_grid(solid, lbm)
   solid.grid_update()
   solid.g2p()
5. Record final_solid_mean_vx_norm.
```

Acceptance:

```text
initial_solid_mean_vx_norm > 0
final_solid_mean_vx_norm < initial_solid_mean_vx_norm
max_reaction_grid_force_norm > 0
net_reaction_grid_force_x < 0
min_J > 0
max_speed < 10
no NaN
no Inf
```

Required outputs:

```text
outputs/step6_two_way_reaction/particles_x.npy
outputs/step6_two_way_reaction/particles_v.npy
outputs/step6_two_way_reaction/particles_F.npy
outputs/step6_two_way_reaction/particles_J.npy
```

### 11.4 Coupled Smoke

Create:

```text
baseline_tests/run_step6_coupled_smoke.py
```

Purpose:

```text
Run a small full penalty-coupled MPM-LBM loop and verify stability plus bidirectional response.
```

Recommended settings:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 20
mpm_substeps_per_lbm_step = 10
gravity = (0.0, 0.0, 0.0)
initial target_u_lbm = (0.02, 0.0, 0.0)
beta_lbm = 1.0e-3
force_cap_lbm = 1.0e-4
```

Required loop:

```python
for lbm_step in range(n_lbm_steps + 1):
    if lbm_step > 0:
        projector.project(solid, lbm)
        coupler.build_penalty_force(lbm)
        lbm.step()

        for _ in range(sim.mpm_substeps_per_lbm_step):
            solid.clear_grid()
            solid.p2g()
            coupler.add_lbm_reaction_to_mpm_grid(solid, lbm)
            solid.grid_update()
            solid.g2p()
```

Acceptance:

```text
completed_lbm_steps = 20
total_mpm_substeps = 200
cell_force_max_norm > 0
hydro_force_max_norm > 0
final_fluid_mean_ux > initial_fluid_mean_ux
final_solid_mean_vx_norm < initial_solid_mean_vx_norm
rho_min > 0.95
rho_max < 1.05
lbm_max_v < 0.1
mpm_min_J > 0
mpm_max_speed < 10
particle positions finite
no NaN
no Inf
```

Required outputs:

```text
outputs/step6_coupled_smoke/LBMFluid_20.vtr
outputs/step6_coupled_smoke/particles_x.npy
outputs/step6_coupled_smoke/particles_v.npy
outputs/step6_coupled_smoke/particles_F.npy
outputs/step6_coupled_smoke/particles_J.npy
outputs/step6_coupled_smoke/cell_force.npy
outputs/step6_coupled_smoke/hydro_force.npy
```

## 12. Required Report

Create:

```text
STEP6_PENALTY_COUPLING_REPORT.md
```

Report must include:

```text
1. Goal
2. Files created/updated
3. Coupling model
4. Unit conversion for reaction force
5. Explicit non-goals
6. Penalty force field command/result
7. LBM response command/result
8. MPM reaction command/result
9. Coupled smoke command/result
10. Hard Acceptance Checklist
11. Decision: can proceed to Step 7 or not
```

Report default values:

```text
n_grid
dx_norm
mpm_dt
mpm_substeps_per_lbm_step
lbm_dt_phys
beta_lbm
phi_min
force_cap_lbm
reaction_scale
force_density_scale_lbm_to_norm
```

## 13. Pytest Contract

Create:

```text
tests/test_step6_penalty_coupling_contract.py
```

Recommended tests:

```python
def test_step6_required_artifacts_exist():
    ...

def test_step6_coupling_source_contains_required_interfaces():
    ...

def test_step6_scripts_do_not_use_forbidden_methods():
    ...

def test_step6_logs_record_successful_baselines():
    ...

def test_step6_report_acceptance_complete():
    ...
```

Required source keywords:

```text
class PenaltyFSICoupler3D
clear_force_fields
inside_lbm
build_penalty_force
add_lbm_reaction_to_mpm_grid
cell_force
hydro_force
solid_phi
solid_vel
beta_lbm
force_cap_lbm
force_density_scale_lbm_to_norm
grid_f_ext
net_cell_force
net_hydro_force
net_reaction_grid_force
```

Forbidden keywords or calls in Step 6 source/baselines:

```text
moving_bounce_back
momentum_exchange
two_phase
contact_angle
ReducedSquidFSI
update_dynamic_solid(
reinitialize_new_fluid_cells(
```

Important:

```text
Step 6 is allowed to use cell_force, hydro_force, and penalty force.
Do not ban these words in the Step 6 contract.
```

Required log markers:

```text
[OK] Step 6 penalty force field baseline finished
[OK] Step 6 LBM response baseline finished
[OK] Step 6 MPM reaction baseline finished
[OK] Step 6 coupled smoke baseline finished
active_force_cell_count
cell_force_max_norm
hydro_force_max_norm
net_cell_force
net_hydro_force
initial_fluid_mean_ux
final_fluid_mean_ux
initial_solid_mean_vx_norm
final_solid_mean_vx_norm
completed_lbm_steps=20
total_mpm_substeps=200
```

## 14. Hard Acceptance Checklist

All must pass:

```text
[ ] main is on the Step 6 final commit
[ ] src/coupling.py exists
[ ] src/__init__.py exports PenaltyFSICoupler3D
[ ] PenaltyFSICoupler3D.clear_force_fields() exists
[ ] PenaltyFSICoupler3D.build_penalty_force() exists
[ ] PenaltyFSICoupler3D.add_lbm_reaction_to_mpm_grid() exists
[ ] build_penalty_force() writes nonzero lbm.cell_force when projected solid moves
[ ] build_penalty_force() writes lbm.hydro_force
[ ] hydro_force = -cell_force
[ ] moving solid +x gives net_cell_force_x > 0
[ ] moving solid +x gives net_hydro_force_x < 0
[ ] net_cell_force + net_hydro_force approximately zero
[ ] LBM response baseline shows fluid mean ux increases
[ ] MPM reaction baseline shows solid mean vx decreases
[ ] coupled smoke baseline completes 20 LBM steps
[ ] coupled smoke baseline completes 200 MPM substeps
[ ] rho_min > 0.95
[ ] rho_max < 1.05
[ ] lbm_max_v < 0.1
[ ] mpm_min_J > 0
[ ] mpm_max_speed < 10
[ ] no NaN
[ ] no Inf
[ ] no moving bounce-back
[ ] no momentum exchange
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no ReducedSquidFSI
[ ] no update_dynamic_solid() in Step 6 baselines
[ ] no reinitialize_new_fluid_cells() in Step 6 baselines
[ ] no external/taichi_LBM3D edits
[ ] logs are saved under logs/
[ ] outputs are saved under outputs/
[ ] STEP6_PENALTY_COUPLING_REPORT.md is complete
[ ] pytest -q passes
```

Numerical thresholds:

```text
Force direction:
  active_force_cell_count > 0
  cell_force_max_norm > 0
  hydro_force_max_norm > 0
  net_cell_force_x > 0
  net_hydro_force_x < 0
  norm(net_cell_force + net_hydro_force) < 1e-10

LBM:
  rho_min > 0.95
  rho_max < 1.05
  lbm_max_v < 0.1
  final_fluid_mean_ux > initial_fluid_mean_ux
  final_fluid_mean_ux > 0

MPM:
  mpm_min_J > 0
  mpm_max_speed < 10
  final_solid_mean_vx_norm < initial_solid_mean_vx_norm

Coupled smoke:
  completed_lbm_steps = 20
  total_mpm_substeps = 200
```

## 15. Recommended Execution Order

Follow this order:

```text
1. Add Step 6 pytest contract/artifact checks.
2. Run pytest and confirm RED for missing Step 6 artifacts.
3. Create src/coupling.py.
4. Export PenaltyFSICoupler3D from src/__init__.py.
5. Implement clear_force_fields().
6. Implement build_penalty_force().
7. Add and run penalty force field baseline.
8. Add and run LBM response baseline.
9. Implement add_lbm_reaction_to_mpm_grid().
10. Add and run MPM reaction baseline.
11. Add and run coupled smoke baseline.
12. Write STEP6_PENALTY_COUPLING_REPORT.md.
13. Run final pytest.
14. Inspect git status and confirm external/ is unchanged.
15. Commit and push to GitHub.
```

Suggested commits:

```text
test: add step 6 penalty coupling contract
feat: add penalty coupling force field
feat: add penalty coupling mpm reaction
```

If keeping the change smaller, two GREEN commits are recommended:

```text
commit A:
  LBM-side penalty force only
  penalty force field + LBM response baselines pass

commit B:
  MPM reaction transfer
  MPM reaction + coupled smoke baselines pass
```

## 16. Failure Handling

If any required baseline fails, stop and record:

```text
exact command
log path
first failing error
which acceptance item failed
whether failure is compile/import/runtime/numerical/output
next minimal fix
```

Do not weaken the required baselines and call Step 6 complete.

Shorter runs may be used only as clearly labeled diagnostic probes, followed by the full required baselines.

## 17. Completion Definition

Step 6 is complete only when:

```text
1. PenaltyFSICoupler3D exists.
2. LBM-side penalty force construction works and has correct direction.
3. hydro_force is equal and opposite to cell_force.
4. LBM response baseline proves fluid is dragged by moving projected solid.
5. MPM reaction baseline proves solid is slowed by LBM reaction.
6. Coupled smoke baseline runs 20 LBM steps and 200 MPM substeps.
7. All stability thresholds pass.
8. No forbidden coupling methods are implemented.
9. Step 6 does not use dynamic solid mask as penalty coupling evidence.
10. Logs, outputs, and STEP6_PENALTY_COUPLING_REPORT.md record evidence.
11. pytest passes.
12. The completed code, report, logs, and outputs are pushed to GitHub.
```

Completion means a minimal penalty-force MPM-LBM FSI prototype exists.

Completion does not mean:

```text
sharp-interface FSI exists
moving bounce-back exists
momentum exchange exists
high-accuracy no-slip exists
real squid simulation is validated
```

Those belong to later steps after the penalty-force MVP is stable.
