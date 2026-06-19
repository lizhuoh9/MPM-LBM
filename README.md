# MPM-LBM FSI Prototype

A Taichi-based prototype framework for 3D MPM solid and LBM fluid coupling.

Current status: engineering prototype.

This repository is a small-scale engineering prototype for comparing MPM-LBM coupling paths. It is not production ready and should not be described as a completed sharp-interface FSI solver or a real squid simulation.

## Implemented

- 3D single-phase LBM backend based on taichi_LBM3D
- 3D MPM solid backend
- unified grid/unit/timestep scaffold
- MPM-to-LBM projection
- penalty-force two-way coupling
- moving-boundary bounce-back path
- moving-boundary reaction transfer to MPM
- unified FSIDriver3D with modes: none, penalty, moving_boundary
- shared diagnostics, CSV/NPZ outputs, logs, and small validation baselines
- larger-grid engineering baselines through 48^3 and 64^3 feasibility checks
- moving-boundary reaction calibration diagnostics and recommended moving_boundary configs
- Step 16 long-run validation for calibrated 48^3 moving_boundary cases and a conservative 64^3 moving_boundary feasibility row

## Not Implemented

- two-phase flow
- contact angle physics
- sparse storage
- real squid geometry
- final strict momentum-conserving sharp-interface FSI
- production-grade solver readiness

## Quick Start

Use the known Windows Python environment for this workspace:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Run the main Step 10 driver baselines:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_penalty_mode.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_moving_boundary_mode.py
```

The committed Step 10 artifacts are the current reproducibility baseline. Step 11 adds documentation and does not require rerunning heavy simulations when those artifacts are present and tests pass.

## Core Modes

| mode | LBM path | MPM reaction | cell_force | dynamic solid |
| ---- | -------- | ------------ | ---------- | ------------- |
| none | `lbm.step()` | none | zero | no |
| penalty | `lbm.step()` | `PenaltyFSICoupler3D` | nonzero | no |
| moving_boundary | `lbm.step_moving_bounceback()` | `MovingBoundaryFSICoupler3D` | zero | yes |

## Repository Layout

```text
src/
  lbm_fluid.py
  mpm_solid.py
  projection.py
  coupling.py
  moving_boundary_coupling.py
  fsi_config.py
  fsi_driver.py
  diagnostics.py

baseline_tests/
configs/
docs/
logs/
outputs/
paper/
tests/
```

## Reproducibility

All step reports and baseline logs are committed for reproducibility. The main validated driver entry points are the Step 10 baselines and the `FSIDriver3D` mode matrix.

Current validation includes small 32^3 regression cases, 48^3 engineering scale baseline cases, and 64^3 short feasibility checks. These runs are useful regression and comparison baselines, not final accuracy validation and not production benchmark data.

## Performance and Artifact Policy

See:

- docs/10_performance_memory.md
- docs/11_artifact_policy.md

## Geometry Support

Step 13 adds procedural geometry initialization:

- box
- ellipsoid
- squid_proxy

The squid_proxy is procedural and is not real squid validation.

## Larger-Grid Validation

Step 14 adds 48^3 scale validation and 64^3 feasibility checks. These are engineering scale baselines, not production benchmark data or real squid validation. Step 14 does not add new FSI physics.

## Moving-Boundary Calibration

Step 15 adds `MomentumAccounting3D`, calibration helpers, reaction_scale and force_cap_norm sweeps, and recommended moving_boundary configs for 48^3 box and 48^3 procedural squid_proxy cases. Step 15 does not change the moving bounce-back formula and does not claim strict final momentum conservation.

## Long-Run Validation

Step 16 does not add new FSI physics. It uses the Step 15 calibrated moving_boundary settings for longer 48^3 box and procedural squid_proxy runs, then adds a conservative 64^3 moving_boundary feasibility row and a 64^3 none/penalty/moving_boundary mode comparison.

The 64^3 moving_boundary row is a feasibility baseline. squid_proxy is procedural and not real squid validation. Strict link-area momentum-conserving coupling remains future work.

## Upstream LBM Note

The LBM backend is derived from the vendored taichi_LBM3D single-phase solver under external/taichi_LBM3D. The external source is kept unmodified in this project workflow. For license details, see the upstream repository and vendored license files if present.
