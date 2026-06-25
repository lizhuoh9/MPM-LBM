# Step118 Report: LBM Open-Boundary Stability Repair

## Result

Step118 adds the LBM open-boundary stability repair surface requested after
Step117. The implementation adds diagnostics, opt-in boundary variants,
contract tests, a Step118 runner, and committed schema artifacts.

Final classification:

`boundary_repair_partial_continue_lbm`

Step119 quasi-2D remains blocked. No Fluent validation is claimed. No full FSI validation is claimed.

## What Changed

Code changes:

- Added `src/mpm_lbm/sim/diagnostics/lbm_stability_diagnostics.py`.
- Extended `src/mpm_lbm/sim/lbm/config.py` with:
  - `regularized_velocity_pressure_limited`
  - `convective_pressure_outlet_experimental`
  - limiter fields for rho, velocity, non-equilibrium, and population floor.
- Extended `src/mpm_lbm/sim/drivers/sim_config.py` and
  `src/mpm_lbm/sim/drivers/fsi_config.py` so the new fields can reach
  `LBMConfig`.
- Extended `src/mpm_lbm/sim/lbm/fluid.py` with opt-in x-boundary branches:
  - `apply_regularized_limited_x_open_boundaries`
  - `apply_convective_pressure_outlet_x_open_boundaries`
- Added `experiments/steps/step118_lbm_open_boundary_stability_repair.py`.

Tests added:

- `tests/test_step118_lbm_stability_diagnostics_contract.py`
- `tests/test_step118_open_boundary_limiter_contract.py`
- `tests/test_step118_boundary_repair_runner_contract.py`
- `tests/test_step118_boundary_repair_artifacts_contract.py`

Artifacts added under:

`outputs/step118_lbm_open_boundary_stability_repair/`

## Important Artifact Boundary

The committed Step118 rows are explicitly marked as `synthetic_diagnostic_mode`.
They verify schema, stability-diagnostic plumbing, boundary-variant reporting,
strict tau skip behavior, and artifact gates. They are not real 48^3/96^3
long-window simulations.

The runner still supports real rows through the same `Step118RunSpec`; those
rows must be run separately for physical stability claims.

This boundary exists because an added runtime smoke that instantiated
`LBMFluid3D` directly exposed the existing Taichi initialization cost around
the 19x19 MRT matrix host initialization. That issue is not a new Step118
physics failure, but it makes extra Taichi runtime rows unsuitable for
pre-push contract tests. The Step118 pytest surface therefore keeps long rows
out of pytest and tests schema/contract behavior with synthetic diagnostic
rows.

## Findings

1. Step117 remains the authoritative real-run evidence:
   - 48^3 legacy is the current stable reference.
   - 48^3 regularized completed but was worse than legacy.
   - 96^3 regularized duct-only and static two-flap rows numerically
     destabilized.
   - Physical-nu official-like rows remain blocked by tau margin.
2. Step118 implements the repair surface but does not prove repair success yet.
3. The new limited regularized and convective outlet modes are opt-in.
4. The legacy and old regularized branches remain available as regression
   references.
5. The committed Step118 matrix does not allow Step119.

## Current Solver Gate State

From `outputs/step118_lbm_open_boundary_stability_repair/solver_report.json`:

- `simulation_backed_artifacts = false`
- `validation_claim_allowed = false`
- `fluent_validation_claim_allowed = false`
- `figure_29_3_parity_claim_allowed = false`
- `full_fsi_rerun_done = false`
- `step119_quasi2d_allowed = false`
- `final_classification = boundary_repair_partial_continue_lbm`

## Remaining Work

The next real evidence step is to run Step118 non-synthetic rows in controlled
order:

1. 48^3 legacy 500-step reference.
2. 48^3 old regularized 500-step reference.
3. 48^3 limited regularized 500-step repair row.
4. 48^3 convective outlet 500-step repair row.
5. 96^3 limited regularized 1000-step duct-only row.
6. 96^3 convective outlet 1000-step duct-only row.
7. 96^3 static two-flap best-boundary 1000-step row.

Only if those rows pass density, mass, population, Mach, and first-failure gates
should Step119 quasi-2D be reopened.

## Verification

Focused Step118 implementation tests:

`13 passed`

Focused Step118 plus Step117/116/115/114/113/112/106/104 regression slice:

`55 passed`

Full repository verification:

`1257 passed, 16 warnings`
