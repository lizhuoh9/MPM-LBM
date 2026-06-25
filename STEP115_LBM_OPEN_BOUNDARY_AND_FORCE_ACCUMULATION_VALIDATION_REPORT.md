# Step115 LBM Open Boundary And Force Accumulation Validation Report

Step115 upgrades the Step114 repair from source-level guards to runtime and
configuration-level evidence. It does not claim Fluent validation, exact Figure
29.3 parity, official mesh/case reproduction, or full FSI readiness.

## Implemented

- Added a Taichi runtime test for the moving-boundary force accumulator. The
  test writes two different `hydro_force` samples, accumulates them through the
  real kernels, and verifies that `finalize_moving_boundary_force_accumulator()`
  writes the mean force field.
- Fixed the Step114 accumulator finalize kernel so Taichi no longer nests a
  `struct_for` under a runtime `if`.
- Added `open_boundary_semantics` to `LBMConfig` and
  `lbm_open_boundary_semantics` to `UnifiedSimConfig`.
- Made `lbm_open_boundary_semantics = "regularized_velocity_pressure"` an
  implemented opt-in mode while preserving
  `equilibrium_all_population_reset` as the default legacy mode.
- Added a D3Q19 x-axis open-boundary path that reconstructs only unknown
  incoming populations at x-min/x-max boundaries and leaves known streamed
  populations intact.
- Added a small 6 x 4 x 4 regularized-boundary runtime smoke that runs three
  LBM steps and checks finite density/velocity behavior.
- Kept `zou_he_reconstruct_unknowns` fail-fast because it is still not
  implemented.
- Added tau feasibility reporting fields:
  `tau_minus_half`, `lbm_min_tau_margin`, `lbm_tau_stability_policy`,
  `tau_margin_pass`, `mach_proxy`, `reynolds_from_config`,
  `target_reynolds_match`, and
  `physical_reynolds_direct_simulation_feasible_with_current_lbm`.
- Added strict/report-only tau stability policy. The default is report-only;
  strict mode rejects mappings whose tau margin is too close to 0.5.
- Updated duct boundary reports so they record whether unknown-population
  reconstruction or all-population equilibrium reset was used.

## Evidence Artifacts

- `outputs/step115_lbm_open_boundary_repair/solver_report.json`
- `outputs/step115_lbm_open_boundary_repair/boundary_condition_semantics_report.json`
- `outputs/step115_lbm_open_boundary_repair/tau_feasibility_report.json`

The artifacts are deterministic summaries, not full simulation payloads. They
do not include private Ansys files or large arrays.

## Key Findings

- The Step115 runtime test found that the Step114 accumulator finalize kernel
  was not actually Taichi-compilable because the field loop was nested under a
  runtime `if`. Moving the loop outside the conditional fixed this without
  changing the intended mean-force semantics.
- For the official-like air mapping with `n_grid=96`, `u_lbm=0.02`,
  `dt_lbm=2.0833333333333334e-6 s`, `duct_length=0.1 m`, and
  `nu_air=1.5e-5 m^2/s`, the computed `nu_lbm` is `2.88e-5` and
  `tau=0.5000864`. With the Step115 default minimum tau margin of `1.0e-4`,
  this fails the tau-margin gate. Report-only mode allows construction but
  marks direct Reynolds-number simulation feasibility as false.

## Remaining Gaps

- `regularized_velocity_pressure` is a bounded D3Q19 x-boundary repair, not a
  Fluent pressure-based solver.
- The solid model remains finite-deformation MPM, not Fluent small-strain
  linear elasticity.
- Moving-boundary reaction transfer remains the existing engineering or
  experimental area-scaled path, not conservative wall traction transfer.
- The solver remains 3D D3Q19. Step115 does not implement D2Q9 planar flow or
  quasi-2D periodic/symmetry-z behavior.
- Step115 does not rerun full FSI; it prepares a safer fluid baseline for later
  steps.

## Verification

Step115 uses the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step115_lbm_open_boundary_and_force_accumulation_contract.py
```

Final verification also requires the adjacent Step104/Step106/Step112/Step113/
Step114 contracts, full `pytest -q`, and `git diff --check`.
