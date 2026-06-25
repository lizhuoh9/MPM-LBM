# Step114 Fluent Solver Physics Repair

Step114 is the first bounded solver-physics repair after the Step113 mirrored
duct-flap runs exposed under-deformation and unstable full-FSI behavior.

The implementation addresses the highest-risk code issue directly:
subcycled moving-boundary FSI no longer advances MPM from only the final LBM
substep's `hydro_force`. The LBM solver now accumulates moving-boundary force
samples over the official FSI exchange window and finalizes the mean force
before MPM reaction transfer.

Step114 also adds explicit configuration/reporting for physical viscosity
mapping, LBM open-boundary semantics, solid-model identity, reaction-transfer
identity, flow-dimensionality identity, and Fluent-like monitor separation.

## New Solver Surfaces

- `lbm_viscosity_semantics = "legacy_external"` preserves the old default.
- `lbm_viscosity_semantics = "physical_nu_mapping"` computes `nu_lbm` from
  physical viscosity, physical `dx`, and physical LBM `dt`, then uses the
  standard `tau = 3 * nu_lbm + 0.5` formula.
- `lbm_open_boundary_semantics = "equilibrium_all_population_reset"` records
  the current duct inlet/outlet implementation honestly.
- Unimplemented Fluent-like options fail fast rather than silently using the
  old solver.
- `fluent_like_monitor_enabled = true` writes a separate
  `fluent_like_monitor_timeseries.csv`.

## Non-Claims

Step114 does not claim Fluent validation, official mesh/case reproduction,
exact Figure 29.3/29.5 contour parity, exact Fluent monitor equivalence,
linear-elastic structural equivalence, or production readiness.

## Tests

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step114_fluent_solver_physics_repair_contract.py
```

The Step114 contract covers physical viscosity mapping, legacy mapping
preservation, invalid mapping rejection, source-level subcycle accumulation
wiring, Fluent-like nearest-particle monitor behavior, and fail-fast guards for
unimplemented Fluent-parity modes.
