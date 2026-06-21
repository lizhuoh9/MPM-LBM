# Project Status

Current status: engineering prototype.

Step 11 is documentation and reproducibility work. It converts the Step 1-10 prototype into a readable package without adding solver code or new FSI physics.

## Completed Milestones

- Step 1: environment and baselines
- Step 2: refactored LBMFluid3D
- Step 3: MPMSolid3D
- Step 4: unified units, grid, timestep
- Step 5: MPM-to-LBM projection
- Step 6: penalty coupling MVP
- Step 7: penalty validation and stability window
- Step 8: moving bounce-back scaffold
- Step 9: moving-boundary reaction coupling
- Step 10: unified FSI driver
- Step 54: repository evidence integrity repair
- Step 55: repository code layout separation and import-boundary contract
- Step 56: canonical runtime implementation migration wave 1
- Step 57: canonical driver support migration wave 2

## Current Validated Modes

- none
- penalty
- moving_boundary

The current mode matrix is validated through committed Step 10 logs and outputs. The validation scale is small-scale 32^3 / 4096-particle engineering baselines.

## What Exists

- Single-phase D3Q19 MRT LBM fluid wrapper
- 3D MPM solid solver
- Shared normalized cubic domain
- MPM-to-LBM projection of `solid_phi`, `solid_mass`, and `solid_vel`
- Penalty-force coupling MVP
- Moving-boundary bounce-back MVP with reaction transfer
- Unified `FSIDriver3D`
- Shared diagnostics and output files

## Current Limitations

- Single-phase fluid only
- Dense grid only
- No real squid geometry
- No two-phase flow or contact angle physics
- Moving-boundary reaction uses engineering scale
- Not strict final momentum-conserving sharp-interface FSI
- Small validation windows, not large production runs

## Status Summary

The repository is ready for documentation review, reproducibility review, and conservative next-step planning. It is not production ready and does not yet validate a real squid case.

The latest repository-structure work has moved the first runtime implementation wave and the driver-support implementation wave into canonical `src/mpm_lbm/...` modules while preserving legacy root imports as compatibility shims. This is code ownership migration, not new physics validation.
