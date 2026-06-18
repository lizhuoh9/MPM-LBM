# Step 7 Goal: Penalty-Coupled FSI Validation Cases And Stability Window

## Paste-Ready `/goal`

```text
/goal
In D:\working\squid robot\LBM\MPM-LBM, execute Step 7: Penalty-coupled FSI validation cases and stability window. The only authoritative execution contract is D:\working\squid robot\LBM\MPM-LBM\STEP7_FSI_VALIDATION_GOAL.md.

Goal: do not add new FSI physics. Validate the Step 6 penalty-force MPM-LBM coupling by adding diagnostic utilities, Couette-like qualitative validation, force/impulse trend diagnostics, beta_lbm stability sweep, and a longer coupled stability run. Establish a reproducible validation baseline before any later moving bounce-back or sharper interface work.

Hard boundaries: do not implement moving bounce-back, momentum exchange, sharp-interface FSI, a new immersed-boundary model, two-phase flow, contact angle physics, squid geometry, sparse storage, ReducedSquidFSI, or edits to external/taichi_LBM3D. Step 7 may use momentum and impulse diagnostics, but must not implement a momentum-exchange coupling method. Do not report short probes as full acceptance.

Required artifacts, execution order, baseline settings, pytest contract, Hard Acceptance Checklist, failure handling, and completion definition are all defined in STEP7_FSI_VALIDATION_GOAL.md. Finish only after all Step 7 baselines pass, pytest passes, and code/logs/outputs/report are pushed to GitHub.
```

## 1. Current Baseline

Step 6 is accepted and is the starting point.

Current Step 6 final commit:

```text
4f9ee368d7c2f6ea681c907c25618789200b249c
```

Step 6 validated:

```text
PenaltyFSICoupler3D exists.
LBM cell_force is computed from projected MPM solid_phi and solid_vel.
hydro_force = -cell_force.
LBM response baseline shows fluid ux increases.
MPM reaction baseline shows solid vx decreases.
Coupled smoke baseline completes 20 LBM steps / 200 MPM substeps.
No external/taichi_LBM3D edits.
No moving bounce-back.
No momentum exchange.
```

Step 6 evidence:

```text
src/coupling.py
STEP6_PENALTY_COUPLING_REPORT.md
logs/step6_penalty_force_field.log
logs/step6_lbm_response.log
logs/step6_two_way_reaction.log
logs/step6_coupled_smoke.log
outputs/step6_penalty_force_field/
outputs/step6_lbm_response/
outputs/step6_two_way_reaction/
outputs/step6_coupled_smoke/
tests/test_step6_penalty_coupling_contract.py
```

Step 6 means the project has a minimal working penalty-force two-way prototype. It does not mean:

```text
sharp-interface no-slip FSI exists
moving bounce-back FSI exists
momentum-exchange FSI exists
real squid simulation is validated
high-accuracy FSI is proven
```

## 2. Step 7 Objective

Step 7 is a validation and diagnostics stage. It must not introduce new coupling physics.

The objective is to answer:

```text
1. Does the Step 6 penalty coupling produce a reasonable Couette-like qualitative flow response?
2. Are force, reaction, impulse, and velocity trends directionally consistent over time?
3. What small baseline stability window exists for beta_lbm and force_cap_lbm?
4. Can the coupled run remain stable longer than the Step 6 smoke case?
5. What evidence should be used as the baseline before Step 8 moving bounce-back or sharper interface work?
```

Step 7 must produce reproducible diagnostic evidence, not a new FSI method.

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

Do not implement these in Step 7:

```text
1. No moving bounce-back.
2. No momentum exchange method.
3. No sharp-interface FSI.
4. No new immersed-boundary method.
5. No two-phase LBM.
6. No contact angle physics.
7. No squid geometry or real squid case.
8. No sparse storage.
9. No ReducedSquidFSI.
10. No edits to external/taichi_LBM3D.
11. No use of dynamic solid mask as FSI proof.
```

Allowed in Step 7:

```text
diagnostic-only NumPy analysis
longer penalty-coupled runs
parameter sweep
Couette-like qualitative validation
momentum and impulse diagnostics
drag/reaction direction validation
stability report
```

Important distinction:

```text
The word "momentum" is allowed in diagnostics.
The method "momentum_exchange" is forbidden.
```

## 5. Required Final Structure

Create or update:

```text
src/
  __init__.py
  diagnostics.py

baseline_tests/
  run_step7_couette_like_validation.py
  run_step7_momentum_impulse_diagnostics.py
  run_step7_beta_sweep.py
  run_step7_long_coupled_stability.py

outputs/
  step7_couette_like/
  step7_momentum_impulse/
  step7_beta_sweep/
  step7_long_stability/

logs/
  step7_couette_like.log
  step7_momentum_impulse.log
  step7_beta_sweep.log
  step7_long_stability.log

tests/
  test_step7_validation_contract.py

STEP7_FSI_VALIDATION_REPORT.md
```

Update `src/__init__.py` to export:

```python
from .diagnostics import FSIDiagnostics3D
```

and include `"FSIDiagnostics3D"` in `__all__`.

## 6. Diagnostic Module

Create:

```text
src/diagnostics.py
```

Implement:

```python
class FSIDiagnostics3D:
    @staticmethod
    def lbm_fluid_stats(lbm):
        ...

    @staticmethod
    def mpm_particle_stats(solid):
        ...

    @staticmethod
    def projection_zone_fluid_mean_velocity(lbm, phi_threshold=1.0e-6):
        ...

    @staticmethod
    def far_field_fluid_mean_velocity(lbm, phi_threshold=1.0e-6):
        ...

    @staticmethod
    def projected_solid_mean_velocity(lbm, eps_mass=1.0e-12):
        ...

    @staticmethod
    def force_stats(lbm):
        ...

    @staticmethod
    def solid_mean_velocity_norm(solid):
        ...

    @staticmethod
    def solid_momentum_norm(solid):
        ...

    @staticmethod
    def lbm_velocity_profile_x_over_y(lbm, z_slice=None):
        ...
```

These diagnostics may use NumPy and host reads. Mark this as diagnostic-only in the module docstring. Do not move coupling logic into diagnostics.

Recommended diagnostic definitions:

### LBM all-fluid mean velocity

```python
fluid = lbm.solid.to_numpy() == 0
mean_u = np.mean(lbm.v.to_numpy()[fluid], axis=0)
```

### Projection-zone fluid mean velocity

```python
active = lbm.solid_phi.to_numpy() > phi_threshold
mean_u_active = np.average(lbm.v.to_numpy()[active], axis=0, weights=lbm.solid_phi.to_numpy()[active])
```

### Far-field fluid mean velocity

```python
far = (lbm.solid.to_numpy() == 0) & (lbm.solid_phi.to_numpy() <= phi_threshold)
mean_u_far = np.mean(lbm.v.to_numpy()[far], axis=0)
```

### Projected solid mean velocity

```python
mass = lbm.solid_mass.to_numpy()
vel = lbm.solid_vel.to_numpy()
active = mass > eps_mass
mean_solid_vel = np.average(vel[active], axis=0, weights=mass[active])
```

### Force balance

```python
cell_force = lbm.cell_force.to_numpy()
hydro_force = lbm.hydro_force.to_numpy()
net_cell_force = np.sum(cell_force.reshape(-1, 3), axis=0)
net_hydro_force = np.sum(hydro_force.reshape(-1, 3), axis=0)
force_balance_error = np.linalg.norm(net_cell_force + net_hydro_force)
```

### MPM solid mean velocity

```python
mass = solid.mass.to_numpy()
vel = solid.v.to_numpy()
mean_v = np.average(vel, axis=0, weights=mass)
```

### LBM ux profile over y

For a qualitative Couette-like check, average `lbm.v[..., 0]` over `x` and `z` for each y index. This is a qualitative profile, not a strict analytical Couette error metric.

## 7. Baseline 1: Couette-Like Validation

Create:

```text
baseline_tests/run_step7_couette_like_validation.py
```

Purpose:

```text
Validate that the Step 6 penalty coupling creates a reasonable Couette-like qualitative response:
projection-zone fluid ux increases;
projection-zone fluid ux is larger than far-field ux;
global fluid ux becomes positive;
solid vx decreases due to reaction;
rho and MPM state remain stable.
```

This is not strict analytical Couette validation. The current model uses diffuse projected penalty forcing, not a sharp moving wall, so the acceptance criteria must be trend-based.

Recommended settings:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 100
mpm_substeps_per_lbm_step = 10
gravity = (0.0, 0.0, 0.0)

solid block:
  box_min = (0.25, 0.55, 0.25)
  box_max = (0.55, 0.75, 0.55)

initial solid velocity:
  target_u_lbm = (0.03, 0.0, 0.0)
  target_u_norm = GridUnitMapper.velocity_lbm_to_norm(target_u_lbm)

coupling:
  beta_lbm = 1.0e-3
  force_cap_lbm = 1.0e-4
```

Required coupled loop:

```python
for step in range(n_lbm_steps):
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
initial_projection_zone_fluid_mean_ux recorded
final_projection_zone_fluid_mean_ux > initial_projection_zone_fluid_mean_ux
final_projection_zone_fluid_mean_ux > far_field_fluid_mean_ux
final_global_fluid_mean_ux > 0
final_solid_mean_vx_norm < initial_solid_mean_vx_norm
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
outputs/step7_couette_like/LBMFluid_100.vtr
outputs/step7_couette_like/particles_x.npy
outputs/step7_couette_like/particles_v.npy
outputs/step7_couette_like/ux_profile_y.npy
outputs/step7_couette_like/diagnostics.npz
```

Required log marker:

```text
[OK] Step 7 Couette-like validation finished
```

## 8. Baseline 2: Momentum / Impulse Diagnostics

Create:

```text
baseline_tests/run_step7_momentum_impulse_diagnostics.py
```

Purpose:

```text
Validate long-enough diagnostic consistency of force direction, impulse trend, fluid response, and solid slowdown.
```

Important:

```text
LBM and MPM are still represented on different discrete measures.
Do not claim strict total momentum conservation.
Step 7 validates diagnostic consistency, not a conservation theorem.
```

Recommended settings:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 100
mpm_substeps_per_lbm_step = 10
gravity = (0.0, 0.0, 0.0)
target_u_lbm = (0.03, 0.0, 0.0)
beta_lbm = 1.0e-3
force_cap_lbm = 1.0e-4
```

Record every LBM step:

```text
step
net_cell_force_x
net_hydro_force_x
force_balance_error
fluid_mean_ux
projection_zone_fluid_mean_ux
solid_mean_vx_norm
cumulative_cell_impulse_x
cumulative_hydro_impulse_x
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
```

Diagnostic impulse accumulation:

```text
cumulative_cell_impulse_x += net_cell_force_x
cumulative_hydro_impulse_x += net_hydro_force_x
```

Acceptance:

```text
max_force_balance_error < 1.0e-5
mean_force_balance_error < 1.0e-6
cumulative_cell_impulse_x > 0
cumulative_hydro_impulse_x < 0
fluid_mean_ux_final > fluid_mean_ux_initial
solid_mean_vx_final < solid_mean_vx_initial
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
outputs/step7_momentum_impulse/diagnostics_timeseries.npz
outputs/step7_momentum_impulse/LBMFluid_100.vtr
```

Required log marker:

```text
[OK] Step 7 momentum impulse diagnostics finished
```

## 9. Baseline 3: Beta Sweep

Create:

```text
baseline_tests/run_step7_beta_sweep.py
```

Purpose:

```text
Find the small baseline stability window for Step 6 penalty coupling.
Validate that stronger beta produces non-weaker fluid response and non-weaker solid slowdown within small numerical tolerance.
```

Recommended sweep:

```text
beta_lbm values:
  3.0e-4
  1.0e-3
  3.0e-3

force_cap_lbm = 1.0e-4
n_lbm_steps = 50
n_grid = 32
n_particles = 4096
mpm_substeps_per_lbm_step = 10
target_u_lbm = (0.02, 0.0, 0.0)
gravity = (0.0, 0.0, 0.0)
```

For each beta record:

```text
beta_lbm
stable
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
initial_fluid_mean_ux
final_fluid_mean_ux
initial_solid_mean_vx_norm
final_solid_mean_vx_norm
solid_slowdown_norm
max_cell_force_norm
max_hydro_force_norm
active_force_cell_count
failure_reason
```

Acceptance:

```text
3.0e-4 stable
1.0e-3 stable
3.0e-3 stable unless clearly recorded as stable-window boundary
at least 3.0e-4 and 1.0e-3 stable
for stable rows, rho_min > 0.95
for stable rows, rho_max < 1.05
for stable rows, lbm_max_v < 0.1
for stable rows, mpm_min_J > 0
for stable rows, mpm_max_speed < 10
for stable rows, final_fluid_mean_ux > initial_fluid_mean_ux
for stable rows, final_solid_mean_vx_norm < initial_solid_mean_vx_norm
fluid response is non-decreasing with beta within tolerance 1.0e-7
solid slowdown is non-decreasing with beta within tolerance 1.0e-7
no NaN
no Inf
```

Required outputs:

```text
outputs/step7_beta_sweep/beta_sweep_results.csv
outputs/step7_beta_sweep/beta_sweep_results.npz
```

CSV header:

```csv
beta_lbm,stable,rho_min,rho_max,lbm_max_v,mpm_min_J,mpm_max_speed,initial_fluid_mean_ux,final_fluid_mean_ux,initial_solid_mean_vx_norm,final_solid_mean_vx_norm,solid_slowdown_norm,max_cell_force_norm,max_hydro_force_norm,active_force_cell_count,failure_reason
```

Required log marker:

```text
[OK] Step 7 beta sweep finished
```

## 10. Baseline 4: Long Coupled Stability

Create:

```text
baseline_tests/run_step7_long_coupled_stability.py
```

Purpose:

```text
Extend the Step 6 coupled smoke from 20 LBM steps / 200 MPM substeps to 100 LBM steps / 1000 MPM substeps.
Validate that the penalty-coupled run remains stable for a longer baseline interval.
```

Recommended settings:

```text
n_grid = 32
n_particles = 4096
n_lbm_steps = 100
mpm_substeps_per_lbm_step = 10
gravity = (0.0, 0.0, 0.0)
target_u_lbm = (0.02, 0.0, 0.0)
beta_lbm = 1.0e-3
force_cap_lbm = 1.0e-4
```

Acceptance:

```text
completed_lbm_steps = 100
total_mpm_substeps = 1000
active_force_cell_count > 0
final_fluid_mean_ux > 0
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
outputs/step7_long_stability/LBMFluid_100.vtr
outputs/step7_long_stability/particles_x.npy
outputs/step7_long_stability/particles_v.npy
outputs/step7_long_stability/particles_F.npy
outputs/step7_long_stability/particles_J.npy
outputs/step7_long_stability/diagnostics_timeseries.npz
```

Required log marker:

```text
[OK] Step 7 long coupled stability finished
```

## 11. Required Report

Create:

```text
STEP7_FSI_VALIDATION_REPORT.md
```

Report must include:

```text
1. Goal
2. Files created/updated
3. Explicit non-goals
4. Diagnostics definitions
5. Couette-like validation command/result
6. Momentum / impulse diagnostics command/result
7. Beta sweep command/result
8. Long coupled stability command/result
9. Stability window summary
10. Hard Acceptance Checklist
11. Decision: can proceed to Step 8 or not
```

Report must explicitly state:

```text
Step 7 validates Step 6 penalty coupling.
Step 7 does not implement a new coupling method.
Step 7 evidence is qualitative/trend/stability evidence, not sharp-interface validation.
```

Recommended report template:

````markdown
# Step 7 FSI Validation Report

## 1. Goal

Validate the Step 6 penalty-force MPM-LBM coupling using trend, stability, and diagnostic baselines. No new FSI model is implemented.

## 2. Files

Created:

- src/diagnostics.py
- baseline_tests/run_step7_couette_like_validation.py
- baseline_tests/run_step7_momentum_impulse_diagnostics.py
- baseline_tests/run_step7_beta_sweep.py
- baseline_tests/run_step7_long_coupled_stability.py
- tests/test_step7_validation_contract.py

## 3. Explicit non-goals

Step 7 does not implement moving bounce-back, momentum exchange, sharp-interface FSI, two-phase flow, squid geometry, or external/taichi_LBM3D edits.

## 4. Couette-like validation

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step7_couette_like_validation.py
```

Result:

- initial_projection_zone_fluid_mean_ux:
- final_projection_zone_fluid_mean_ux:
- far_field_fluid_mean_ux:
- initial_solid_mean_vx_norm:
- final_solid_mean_vx_norm:
- rho_min:
- rho_max:
- mpm_min_J:

## 5. Momentum / impulse diagnostics

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step7_momentum_impulse_diagnostics.py
```

Result:

- max_force_balance_error:
- mean_force_balance_error:
- cumulative_cell_impulse_x:
- cumulative_hydro_impulse_x:
- final_fluid_mean_ux:
- final_solid_mean_vx_norm:

## 6. Beta sweep

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step7_beta_sweep.py
```

Result:

| beta_lbm | stable | rho_min | rho_max | final_fluid_mean_ux | final_solid_mean_vx_norm |
| ---: | :--- | ---: | ---: | ---: | ---: |

## 7. Long coupled stability

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step7_long_coupled_stability.py
```

Result:

- completed_lbm_steps:
- total_mpm_substeps:
- final_fluid_mean_ux:
- final_solid_mean_vx_norm:
- rho_min:
- rho_max:
- mpm_min_J:
- mpm_max_speed:

## 8. Hard Acceptance Checklist

- [ ] main is on the Step 7 final commit
- [ ] src/diagnostics.py exists
- [ ] src/__init__.py exports FSIDiagnostics3D
- [ ] Couette-like validation passes
- [ ] momentum / impulse diagnostics pass
- [ ] beta sweep passes
- [ ] long coupled stability passes
- [ ] no moving bounce-back
- [ ] no momentum exchange
- [ ] no sharp-interface FSI
- [ ] no two-phase flow
- [ ] no external/taichi_LBM3D edits
- [ ] logs saved
- [ ] outputs saved
- [ ] pytest -q passes

## 9. Decision

Can proceed to Step 8?

- [ ] Yes
- [ ] No
````

## 12. Pytest Contract

Create:

```text
tests/test_step7_validation_contract.py
```

Recommended tests:

```python
def test_step7_required_artifacts_exist():
    ...

def test_step7_diagnostics_source_contains_required_interfaces():
    ...

def test_step7_scripts_do_not_use_forbidden_methods():
    ...

def test_step7_logs_record_successful_baselines():
    ...

def test_step7_report_acceptance_complete():
    ...
```

Required artifact paths:

```text
src/diagnostics.py
baseline_tests/run_step7_couette_like_validation.py
baseline_tests/run_step7_momentum_impulse_diagnostics.py
baseline_tests/run_step7_beta_sweep.py
baseline_tests/run_step7_long_coupled_stability.py
logs/step7_couette_like.log
logs/step7_momentum_impulse.log
logs/step7_beta_sweep.log
logs/step7_long_stability.log
outputs/step7_couette_like/LBMFluid_100.vtr
outputs/step7_couette_like/particles_x.npy
outputs/step7_couette_like/particles_v.npy
outputs/step7_couette_like/ux_profile_y.npy
outputs/step7_couette_like/diagnostics.npz
outputs/step7_momentum_impulse/diagnostics_timeseries.npz
outputs/step7_momentum_impulse/LBMFluid_100.vtr
outputs/step7_beta_sweep/beta_sweep_results.csv
outputs/step7_beta_sweep/beta_sweep_results.npz
outputs/step7_long_stability/LBMFluid_100.vtr
outputs/step7_long_stability/particles_x.npy
outputs/step7_long_stability/particles_v.npy
outputs/step7_long_stability/particles_F.npy
outputs/step7_long_stability/particles_J.npy
outputs/step7_long_stability/diagnostics_timeseries.npz
STEP7_FSI_VALIDATION_REPORT.md
```

Required source keywords:

```text
class FSIDiagnostics3D
lbm_fluid_stats
mpm_particle_stats
projection_zone_fluid_mean_velocity
far_field_fluid_mean_velocity
projected_solid_mean_velocity
force_stats
solid_mean_velocity_norm
solid_momentum_norm
lbm_velocity_profile_x_over_y
diagnostic-only
```

Required log markers:

```text
[OK] Step 7 Couette-like validation finished
[OK] Step 7 momentum impulse diagnostics finished
[OK] Step 7 beta sweep finished
[OK] Step 7 long coupled stability finished
initial_projection_zone_fluid_mean_ux
final_projection_zone_fluid_mean_ux
far_field_fluid_mean_ux
max_force_balance_error
mean_force_balance_error
cumulative_cell_impulse_x
cumulative_hydro_impulse_x
beta_lbm=3.000000000e-04
beta_lbm=1.000000000e-03
completed_lbm_steps=100
total_mpm_substeps=1000
```

Forbidden tokens in Step 7 source and baselines:

```text
moving_bounce_back
momentum_exchange
sharp_interface
two_phase
contact_angle
ReducedSquidFSI
```

Do not ban:

```text
momentum
impulse
cell_force
hydro_force
penalty
```

These are required diagnostics or existing Step 6 coupling fields.

## 13. Hard Acceptance Checklist

All must pass:

```text
[ ] main is on the Step 7 final commit
[ ] src/diagnostics.py exists
[ ] src/__init__.py exports FSIDiagnostics3D
[ ] FSIDiagnostics3D.lbm_fluid_stats() exists
[ ] FSIDiagnostics3D.mpm_particle_stats() exists
[ ] FSIDiagnostics3D.projection_zone_fluid_mean_velocity() exists
[ ] FSIDiagnostics3D.far_field_fluid_mean_velocity() exists
[ ] FSIDiagnostics3D.projected_solid_mean_velocity() exists
[ ] FSIDiagnostics3D.force_stats() exists
[ ] FSIDiagnostics3D.solid_mean_velocity_norm() exists
[ ] FSIDiagnostics3D.lbm_velocity_profile_x_over_y() exists
[ ] Couette-like validation passes
[ ] projection zone fluid ux increases
[ ] projection zone fluid ux > far-field ux
[ ] global fluid ux > 0
[ ] solid mean vx decreases
[ ] momentum / impulse diagnostics pass
[ ] force balance error is small
[ ] cumulative cell impulse x > 0
[ ] cumulative hydro impulse x < 0
[ ] beta sweep passes
[ ] beta sweep has stable 3.0e-4 row
[ ] beta sweep has stable 1.0e-3 row
[ ] fluid response is non-decreasing with beta within tolerance
[ ] solid slowdown is non-decreasing with beta within tolerance
[ ] long coupled stability completes 100 LBM steps
[ ] long coupled stability completes 1000 MPM substeps
[ ] active_force_cell_count > 0
[ ] rho_min > 0.95
[ ] rho_max < 1.05
[ ] lbm_max_v < 0.1
[ ] mpm_min_J > 0
[ ] mpm_max_speed < 10
[ ] no NaN
[ ] no Inf
[ ] no moving bounce-back
[ ] no momentum exchange
[ ] no sharp-interface FSI
[ ] no two-phase flow
[ ] no contact angle physics
[ ] no ReducedSquidFSI
[ ] no external/taichi_LBM3D edits
[ ] logs are saved under logs/
[ ] outputs are saved under outputs/
[ ] STEP7_FSI_VALIDATION_REPORT.md is complete
[ ] pytest -q passes
```

## 14. Recommended Execution Order

Follow this order:

```text
1. Add Step 7 pytest contract/artifact checks.
2. Run pytest and confirm RED for missing Step 7 artifacts.
3. Create src/diagnostics.py.
4. Export FSIDiagnostics3D from src/__init__.py.
5. Implement NumPy diagnostic-only functions.
6. Add and run Couette-like validation.
7. Add and run momentum / impulse diagnostics.
8. Add and run beta sweep.
9. Add and run long coupled stability.
10. Write STEP7_FSI_VALIDATION_REPORT.md.
11. Run final pytest.
12. Inspect git status and confirm external/ is unchanged.
13. Commit and push to GitHub.
```

Suggested commits:

```text
test: add step 7 validation contract
feat: add fsi diagnostics and qualitative validation
feat: add step 7 stability sweep and long run
```

## 15. Failure Handling

If any required baseline fails, stop and record:

```text
exact command
log path
first failing error
which acceptance item failed
whether failure is compile/import/runtime/numerical/output
next minimal fix
```

Do not weaken the required baselines and call Step 7 complete.

Shorter runs may be used only as clearly labeled diagnostic probes, followed by the full required baseline.

If `beta_lbm = 3.0e-3` is unstable, record it as the upper boundary candidate in the beta sweep, but at least `3.0e-4` and `1.0e-3` must be stable for Step 7 completion.

## 16. Completion Definition

Step 7 is complete only when:

```text
1. FSIDiagnostics3D exists and is exported.
2. Couette-like validation passes.
3. Projection-zone fluid velocity increases and is larger than far-field velocity.
4. MPM solid velocity decreases under reaction.
5. Momentum / impulse diagnostics show consistent signs.
6. Force balance error remains small.
7. Beta sweep identifies a stable small-parameter window.
8. Long coupled stability completes 100 LBM steps / 1000 MPM substeps.
9. All stability thresholds pass.
10. No forbidden coupling methods are implemented.
11. Logs, outputs, and STEP7_FSI_VALIDATION_REPORT.md record evidence.
12. pytest passes.
13. The completed code, report, logs, and outputs are pushed to GitHub.
```

Completion means:

```text
The current penalty-force MPM-LBM prototype has reproducible qualitative FSI response and a documented small-scale stability window.
```

Completion does not mean:

```text
no-slip accuracy is proven
sharp-interface FSI exists
momentum-exchange FSI exists
real squid validation is complete
```

Those belong to Step 8 or later.
