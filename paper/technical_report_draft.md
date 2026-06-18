# A Taichi-based Prototype for 3D MPM-LBM Fluid-Solid Coupling

## Abstract

This project implements a Taichi-based prototype framework for three-dimensional fluid-solid coupling between a 3D MPM solid solver and a single-phase D3Q19 MRT LBM fluid solver. The codebase provides two coupled MVP paths: a diffuse penalty-force mode and an opt-in moving-boundary bounce-back mode with reaction transfer to the MPM grid. A unified driver, configuration object, and diagnostics scaffold standardize grid resolution, timestep synchronization, MPM-to-LBM projection, coupled stepping, CSV/NPZ output, and lightweight timing. Current validation is limited to small-scale 32^3 / 4096-particle validation baselines and short stability windows. The implementation is not final strict momentum-conserving sharp-interface FSI and has no two-phase flow, contact-angle physics, or real squid geometry. Instead, the repository establishes a reproducible engineering scaffold for comparing coupling modes, tracking stability regressions, and preparing future higher-fidelity work. The present documentation package summarizes the architecture, numerical methods, mode matrix, committed Step 10 results, limitations, and reproducibility commands.

## 1. Introduction

MPM-LBM coupling is attractive for deformable solid and fluid interaction prototypes because MPM handles large solid deformation while LBM provides a structured-grid fluid update. This repository explores that combination in a controlled Taichi implementation.

The goal is not to claim final solver fidelity. The goal is to keep a reproducible prototype where coupling paths can be compared under the same grid, timestep, diagnostics, and output layout.

## 2. System Architecture

The architecture has these main components:

- `LBMFluid3D`: dense single-phase LBM fluid wrapper
- `MPMSolid3D`: 3D MPM solid solver
- `UnifiedSimConfig`: shared grid and timestep configuration
- `GridUnitMapper`: normalized/LBM unit conversion
- `MPMToLBMProjector3D`: particle-to-grid solid projection
- `PenaltyFSICoupler3D`: penalty-force coupling path
- `MovingBoundaryFSICoupler3D`: moving-boundary reaction transfer path
- `FSIDriver3D`: unified driver and diagnostics scaffold

Data flow:

```text
MPM particles
  -> projection
  -> LBM solid_phi / solid_mass / solid_vel
  -> coupling mode
  -> LBM step
  -> hydro reaction
  -> MPM grid_f_ext
```

## 3. Numerical Methods

The fluid side uses a dense single-phase D3Q19 MRT LBM wrapper derived from the vendored taichi_LBM3D solver. It supports static bounce-back, a force path for `cell_force`, and an opt-in moving bounce-back path.

The solid side uses 3D MPM with quadratic B-spline transfer, APIC affine velocity, deformation gradient tracking, and fixed-corotated elasticity.

Projection transfers MPM volume, mass, and velocity to LBM fields. The projected fields are `solid_phi`, `solid_mass`, and `solid_vel`.

## 4. Coupling Modes

The unified driver supports:

- `none`: coexistence baseline with no reaction
- `penalty`: diffuse-interface MVP using `PenaltyFSICoupler3D`
- `moving_boundary`: moving bounce-back MVP using `MovingBoundaryFSICoupler3D`

Penalty mode uses:

```text
cell_force = beta_lbm * solid_phi * rho * (solid_vel - fluid_vel)
```

Moving-boundary mode uses dynamic solid masks and link-wise `hydro_force` diagnostics. The reaction transfer currently uses engineering scaling, not final strict link-area momentum integration.

## 5. Validation Baselines

Steps 1-10 establish:

1. Taichi and backend smoke tests
2. standalone LBM baseline
3. standalone MPM baseline
4. unified units, grid, and timestep
5. MPM-to-LBM projection
6. penalty coupling MVP
7. penalty validation and stability sweep
8. moving bounce-back scaffold
9. moving-boundary reaction coupling
10. unified driver, mode matrix, and performance profile

## 6. Results

Step 10 mode matrix:

| mode | projection_zone_ux_final | solid_vx_final | rho_min | rho_max |
| ---- | -----------------------: | -------------: | ------: | ------: |
| none | 0.000000000e+00 | 1.562558860e-01 | 1.000000358e+00 | 1.000000358e+00 |
| penalty | 3.118396126e-05 | 1.536530405e-01 | 9.999890327e-01 | 1.000013232e+00 |
| moving_boundary | 1.293938956e-03 | 1.509043574e-01 | 9.851434231e-01 | 1.014919758e+00 |

The committed mode matrix shows:

```text
projection_zone_ux_final(moving_boundary) > projection_zone_ux_final(penalty) > projection_zone_ux_final(none)
```

These are small-scale engineering baselines, not final accuracy validation.

## 7. Limitations

- Single-phase fluid only
- No two-phase surface tension or contact angle physics
- No real squid geometry
- Dense grid only
- Moving-boundary reaction uses engineering scale
- Not strict final momentum-conserving sharp-interface FSI
- Small-scale validation only

## 8. Future Work

Future work should preserve the current baselines while adding one risk at a time:

- performance and memory cleanup
- geometry ingestion or squid proxy geometry
- larger-grid validation
- sharper moving-boundary reaction calibration
- optional two-phase LBM exploration

## Appendix A: Reproducibility Commands

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_penalty_mode.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_moving_boundary_mode.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_driver_mode_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step10_performance_profile.py
```

## Appendix B: Configuration Examples

See:

```text
configs/step10_penalty_default.json
configs/step10_moving_boundary_default.json
configs/step10_mode_matrix.json
```

These JSON files are loaded through `FSIDriverConfig.from_json(path)`.
