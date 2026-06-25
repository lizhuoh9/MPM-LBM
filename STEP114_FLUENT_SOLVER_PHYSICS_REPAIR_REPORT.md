# Step114 Fluent Solver Physics Repair Report

Step114 implements the first bounded solver-physics repair layer from the
post-Step113 review. It does not claim Fluent validation or exact Figure 29.3
parity. It fixes the most direct code issue and adds explicit solver surfaces
so future Fluent-like runs cannot silently use the wrong assumptions.

## Implemented

- Subcycled moving-boundary FSI now accumulates `hydro_force` across the whole
  official FSI exchange window and passes the mean substep force to MPM.
- LBM relaxation can now be driven by explicit physical viscosity mapping:
  `nu_lbm = nu_phys * dt_phys / dx_phys**2`, with
  `tau = 3 * nu_lbm + 0.5`.
- Legacy `niu=0.1` behavior remains the default unless
  `lbm_viscosity_semantics = "physical_nu_mapping"` is selected.
- Step114 adds a Fluent-like monitor helper and driver output path that reports
  official-point-like nearest-particle displacement separately from the old
  free-tip mean monitor.
- Boundary-condition semantics are now explicit. The current duct inlet/outlet
  path is reported as `equilibrium_all_population_reset`, not Fluent-like
  Zou-He/regularized open boundary.
- Unimplemented Fluent-parity modes now fail fast:
  `small_strain_linear_elastic`, `plane_strain_2d`, `d2q9_planar`,
  `zou_he_reconstruct_unknowns`, and
  `interface_traction_conservative`.
- Moving-boundary reaction reports now state that `engineering` is a
  volume-sampled bridge, not conservative wall traction.

## Key Code Paths

- `src/mpm_lbm/sim/lbm/fluid.py`
  - Adds `hydro_force_accum`.
  - Adds `clear_moving_boundary_force_accumulator()`.
  - Adds `accumulate_moving_boundary_force_sample()`.
  - Adds `finalize_moving_boundary_force_accumulator()`.
  - Adds accumulation diagnostics.
- `src/mpm_lbm/sim/drivers/fsi_driver.py`
  - Calls the accumulator around the subcycled LBM loop.
  - Records accumulation diagnostics in driver time series.
  - Writes `fluent_like_monitor_timeseries.csv` when enabled.
- `src/mpm_lbm/sim/drivers/fsi_config.py`
  - Adds physical viscosity/Re mapping fields.
  - Adds boundary, solid, reaction-transfer, and flow-dimensionality guard
    fields.
- `src/mpm_lbm/sim/lbm/config.py`
  - Adds relaxation semantics.
- `src/mpm_lbm/sim/monitoring/fluent_like.py`
  - Adds deterministic nearest-particle official-point-like monitor logic.

## Remaining Gaps

- The current LBM open boundary is still the old all-population equilibrium
  reset. Step114 labels it honestly but does not implement a full D3Q19
  Zou-He/regularized open boundary.
- The current solid model is still explicit finite-deformation MPM. Step114
  adds fail-fast guards for Fluent-like small-strain linear elasticity but does
  not implement the small-strain solver.
- The current moving-boundary reaction transfer is still engineering or
  link-area experimental. Step114 does not implement conservative interface
  traction transfer.
- The current solver is still 3D D3Q19. Step114 does not implement D2Q9 planar
  or quasi-2D periodic/symmetry-z flow.

## Verification

Initial red test:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step114_fluent_solver_physics_repair_contract.py
```

Result before implementation: `6 failed`.

Green Step114 test:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step114_fluent_solver_physics_repair_contract.py
```

Result after implementation: `6 passed`.

Full verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
git diff --check
```

Result: `1221 passed in 180.50s`. `git diff --check` reported only LF/CRLF
conversion warnings and no whitespace errors.
