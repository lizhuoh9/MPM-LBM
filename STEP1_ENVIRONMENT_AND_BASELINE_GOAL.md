# Step 1 Environment And Code Baseline Goal

This document is the detailed execution contract for Step 1 of the MPM-LBM-FSI project.
The short `/goal` should reference this file instead of repeating all details.

## Objective

Create a clean baseline project that proves the environment and the two uncoupled numerical baselines work before any MPM-LBM coupling is attempted.

Step 1 must prove:

1. Taichi imports and runs on this machine.
2. Taichi CPU backend runs a small deterministic kernel.
3. Taichi GPU backend runs a small deterministic kernel.
4. `taichi_LBM3D` Single_phase D3Q19 MRT LBM can run independently and write VTK output.
5. A simple 3D Taichi MPM smoke demo can run independently without NaN, Inf, or non-positive volume measure.

GPU success is mandatory for this user's target. CPU success alone is useful diagnostic evidence but is not enough to mark Step 1 complete.

## Non-Goals

Do not implement MPM-LBM coupling in Step 1.

Do not implement immersed boundary, penalty force, moving bounce-back, momentum exchange, or reaction-force transfer in Step 1.

Do not port the squid model in Step 1.

Do not use `ReducedSquidFSI`.

Do not modify the core `taichi_LBM3D` solver algorithms in Step 1. If a smoke run needs shorter iteration counts, create local wrapper scripts under `baseline_tests/` rather than editing third-party solver files.

Do not use the two-phase, phase-change, or grey-scale solvers in Step 1. Only use `Single_phase`.

Do not treat Taichi demo `mpm3d.py` as the final solid solver. In Step 1 it is only a reference for a standalone smoke test.

## Required Project Layout

Create the following structure under the repository root:

```text
MPM-LBM/
  external/
    taichi_LBM3D/
  baseline_tests/
    check_taichi_backend.py
    run_lbm_smoke_baseline.py
    run_lbm_poiseuille_baseline.py
    run_mpm3d_baseline.py
  outputs/
    lbm_smoke/
    lbm_poiseuille/
    mpm3d/
  scripts/
  logs/
  environment.yml
  requirements.txt
  STEP1_BASELINE_REPORT.md
```

`external/taichi_LBM3D/` should be a clone of:

```text
https://github.com/yjhp1016/taichi_LBM3D
```

If the workspace already has a sibling clone at `D:\working\squid robot\LBM\taichi_LBM3D`, it may be used only as a source/reference for cloning or copying into `external/`. The Step 1 report must record the commit hash actually used by `external/taichi_LBM3D`.

## Environment

Use Python 3.10.

Recommended dependency set:

```text
taichi==1.7.4
numpy
pyevtk
sympy
pytest
```

Create both:

```text
requirements.txt
environment.yml
```

`environment.yml` should define a conda environment named `mpm-lbm` with Python 3.10 and the same pip dependencies.

The report must record:

```text
OS
Python version
Taichi version
NumPy version
pyevtk import status/version if available
sympy version
GPU backend status
CUDA/device information if Taichi exposes it in logs
taichi_LBM3D commit hash
```

## Backend Test Script

Create:

```text
baseline_tests/check_taichi_backend.py
```

The script must:

1. Print Python version.
2. Print Taichi version.
3. Test `ti.cpu`.
4. Test `ti.gpu`.
5. For each backend, run a small Taichi kernel over `n = 1024`.
6. Fill `x[i] = i * 0.5`.
7. Fill `y[i] = x[i] * 2.0 + 1.0`.
8. Copy only the small `y` field to NumPy for verification.
9. Assert `max(abs(y - (arange(n) + 1))) < 1e-5`.
10. Print a clear summary.

Expected log path:

```text
logs/check_taichi_backend.log
```

Acceptance:

```text
CPU: OK
GPU: OK
```

For this project, GPU failure is a blocking issue. Do not mark Step 1 complete if `ti.gpu` fails.

## LBM All-Fluid Smoke Baseline

Create:

```text
baseline_tests/run_lbm_smoke_baseline.py
```

This script must use `external/taichi_LBM3D/Single_phase/LBM_3D_SinglePhase_Solver.py` as the LBM source.

Use the single-phase D3Q19 MRT solver class:

```text
LB3D_Solver_Single_Phase
```

Do not use:

```text
2phase
Grey_Scale
Phase_change
```

The script must:

1. Initialize Taichi with GPU first.
2. Use a small dense grid, initially `32 x 32 x 32`.
3. Generate a simple all-fluid smoke geometry file locally under `outputs/lbm_smoke/`.
4. Use `0 = fluid`, `1 = solid`.
5. Save geometry using Fortran order because the original solver reshapes with `order='F'`.
6. Instantiate `LB3D_Solver_Single_Phase(nx, ny, nz, sparse_storage=False)`.
7. Set `niu = 0.1`.
8. Apply a small velocity boundary no larger than `0.03` in lattice units.
9. Call `init_geo()`.
10. Call `init_simulation()`.
11. Run at least 500 steps.
12. Print progress every 100 steps with finite `max_v`.
13. Export VTK at least once into `outputs/lbm_smoke/`.
14. Fail immediately on NaN or Inf.

Expected log path:

```text
logs/lbm_smoke_baseline.log
```

Acceptance:

```text
LBM run reaches at least 500 steps.
max_v remains finite.
VTK output exists under outputs/lbm_smoke/.
No NaN or Inf is reported.
Density/velocity fields can be inspected in ParaView.
```

Step 1 does not require physical convergence of the all-fluid smoke flow. It only requires a finite, non-exploding baseline with output.

## LBM Pressure-Driven Poiseuille Baseline

Create:

```text
baseline_tests/run_lbm_poiseuille_baseline.py
```

This script must use the same upstream Single_phase solver and provide a physical channel-flow baseline for later Step 2 comparison.

The script must:

1. Initialize Taichi with GPU first.
2. Use a small dense grid, initially `32 x 32 x 32`.
3. Generate a channel geometry file locally under `outputs/lbm_poiseuille/`.
4. Use `0 = fluid`, `1 = solid`.
5. Keep x direction open/pressure-driven.
6. Make y/z boundary planes solid walls.
7. Apply a small pressure/density difference in x, for example `rho_in=1.0001`, `rho_out=1.0`.
8. Call `init_geo()`.
9. Call `init_simulation()`.
10. Run at least 1000 steps.
11. Print finite `max_v`, `rho_min`, `rho_max`, mean x velocity, centerline x velocity, and near-wall x velocity.
12. Export VTK at least once into `outputs/lbm_poiseuille/`.
13. Fail immediately on NaN or Inf.

Expected log path:

```text
logs/lbm_poiseuille_baseline.log
```

Acceptance:

```text
Poiseuille run reaches at least 1000 steps.
rho remains finite and bounded.
max_v < 0.05.
x velocity forms a channel-like profile: centerline ux > near-wall ux.
VTK output exists under outputs/lbm_poiseuille/.
No NaN or Inf is reported.
```

## MPM 3D Baseline

Create:

```text
baseline_tests/run_mpm3d_baseline.py
```

This script must be a standalone Taichi 3D MPM smoke test. It must not depend on the LBM solver.

It may use a simplified demonstrator model for Step 1 only:

```text
dim = 3
n_grid = 32
steps = 50
dt = 4e-4 or smaller if needed
E = 400.0 or smaller if needed
```

The script must:

1. Initialize Taichi with GPU first.
2. Create a small particle cloud inside the unit cube.
3. Use 3D particle fields for position, velocity, affine matrix, and scalar volume measure `J`.
4. Use 3D grid fields for velocity and mass.
5. Run P2G, grid update, boundary condition, G2P, position update, and `J` update.
6. Print stats every 10 steps:
   - `min_y`
   - `max_y`
   - `max_speed`
   - `min_J`
7. Fail immediately on NaN or Inf.
8. Fail immediately if `min_J <= 0`.
9. Save particle positions to:

```text
outputs/mpm3d/mpm3d_positions.npy
```

Expected log path:

```text
logs/mpm3d_baseline.log
```

Acceptance:

```text
MPM run reaches at least 50 steps.
min_y, max_y, max_speed, min_J are finite.
min_J remains positive.
outputs/mpm3d/mpm3d_positions.npy exists.
```

If the MPM smoke test becomes unstable, first reduce `dt`, then reduce `E`, then disable gravity for diagnosis. Do not hide instability by ignoring invalid diagnostics.

## Output Check

After baseline scripts run, verify output inventory:

```text
outputs/lbm_smoke/
outputs/lbm_poiseuille/
outputs/mpm3d/mpm3d_positions.npy
```

The project should contain logs for every run:

```text
logs/check_taichi_backend.log
logs/lbm_smoke_baseline.log
logs/lbm_poiseuille_baseline.log
logs/mpm3d_baseline.log
```

## Step 1 Report

Create:

```text
STEP1_BASELINE_REPORT.md
```

The report must include:

```text
1. Environment
2. Repository commit hashes
3. Backend test command and result
4. LBM baseline command and result
5. MPM baseline command and result
6. Output file inventory
7. Blocking issues
8. Decision: can proceed to Step 2?
```

The report must explicitly state:

```text
Taichi GPU backend: OK / FAILED
```

If GPU is failed, the decision must be:

```text
Can proceed to Step 2? No
```

## Required Commands To Run

Use PowerShell-compatible commands on this machine.

At minimum, run:

```powershell
python baseline_tests/check_taichi_backend.py
python baseline_tests/run_lbm_smoke_baseline.py
python baseline_tests/run_lbm_poiseuille_baseline.py
python baseline_tests/run_mpm3d_baseline.py
git -C external/taichi_LBM3D rev-parse HEAD
python -m pip freeze
```

If `python` is not the intended environment interpreter, use the resolved environment interpreter consistently and record it in `STEP1_BASELINE_REPORT.md`.

## Hard Acceptance Checklist

Step 1 is complete only when all required items are true:

```text
[ ] Python 3.10 environment is documented and reproducible.
[ ] requirements.txt exists.
[ ] environment.yml exists.
[ ] taichi import succeeds.
[ ] numpy import succeeds.
[ ] pyevtk import succeeds.
[ ] sympy import succeeds.
[ ] Taichi CPU backend succeeds.
[ ] Taichi GPU backend succeeds.
[ ] external/taichi_LBM3D exists.
[ ] taichi_LBM3D commit hash is recorded.
[ ] LBM all-fluid smoke baseline runs at least 500 steps.
[ ] LBM smoke max_v remains finite.
[ ] LBM smoke VTK output exists.
[ ] LBM Poiseuille baseline runs at least 1000 steps.
[ ] LBM Poiseuille rho remains bounded.
[ ] LBM Poiseuille max_v < 0.05.
[ ] LBM Poiseuille VTK output exists.
[ ] MPM 3D baseline runs at least 50 steps.
[ ] MPM diagnostics remain finite.
[ ] MPM min_J remains positive.
[ ] MPM particle npy output exists.
[ ] All logs are saved under logs/.
[ ] STEP1_BASELINE_REPORT.md is complete.
```

## Failure Policy

Do not continue to Step 2 if:

```text
Taichi GPU backend fails.
LBM baseline produces NaN or Inf.
LBM baseline cannot write VTK.
MPM baseline produces NaN or Inf.
MPM min_J becomes non-positive.
```

If failure occurs, stop and report:

```text
exact command
log path
first failing error
whether it is environment, dependency, GPU, LBM, or MPM related
next proposed fix
```

## Relationship To Later FSI Work

This Step 1 baseline intentionally prepares for, but does not implement, the later real FSI route:

```text
Taichi = unified runtime
taichi_LBM3D Single_phase = LBM fluid baseline
custom MPMSolid3D = solid baseline in later steps
coupling.py = later dynamic interface and momentum exchange
```

Later steps should preserve the recorded rule that the first coupling MVP is:

```text
MPM solid + single-phase LBM + penalty/immersed-boundary force
```

Only after that MVP is stable should the route upgrade to:

```text
MPM solid + single-phase LBM + moving bounce-back + momentum exchange
```
