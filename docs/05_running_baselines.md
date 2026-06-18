# Running Baselines

Use the known Python interpreter in this workspace:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

## Step 10 Driver Baselines

The main validated driver entry points are:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_penalty_mode.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_moving_boundary_mode.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_mode_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_performance_profile.py
```

## Earlier-Step Baseline Inventory

Earlier validation scripts include:

```text
baseline_tests/check_taichi_backend.py
baseline_tests/run_lbm_smoke_baseline.py
baseline_tests/run_lbm_poiseuille_baseline.py
baseline_tests/run_mpm3d_baseline.py
baseline_tests/run_step4_unified_scaffold.py
baseline_tests/run_step5_projection_baseline.py
baseline_tests/run_step6_penalty_couette_baseline.py
baseline_tests/run_step7_couette_validation.py
baseline_tests/run_step8_moving_wall_bounceback.py
baseline_tests/run_step9_moving_boundary_reaction.py
```

Some exact filenames may reflect earlier step naming, but the committed step reports identify the accepted artifacts.

## Logs and Outputs

Logs are saved under:

```text
logs/
```

Simulation outputs are saved under:

```text
outputs/
```

Step 10 driver outputs include VTK, particle arrays, diagnostics CSV, diagnostics NPZ, mode matrix CSV/NPZ, and performance CSV/NPZ.

## Probes Versus Acceptance

A short diagnostic probe is useful for debugging. It is not a full acceptance baseline. A Step acceptance claim should cite the required baseline command, logs, outputs, and report checklist.

Step 11 itself does not require rerunning heavy simulations if existing Step 10 artifacts are present and tests pass. Step 11 acceptance is based on documentation artifacts, documentation contract tests, full pytest, and GitHub sync.
