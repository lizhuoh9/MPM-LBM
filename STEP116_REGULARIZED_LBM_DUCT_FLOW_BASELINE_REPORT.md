# Step116 Regularized LBM Duct Flow Baseline Report

Step116 turns the Step115 open-boundary repair into simulation-backed
fluid-only evidence. It does not claim Fluent validation, Figure 29.3 parity,
official mesh/case reproduction, full FSI readiness, or production solver
readiness.

## Implemented

- Added `src/mpm_lbm/sim/diagnostics/lbm_boundary_diagnostics.py` with NumPy
  post-processing diagnostics for fluid masks, x-plane flux, x-plane mean
  velocity, density stats, total mass, centerline profiles, outlet reflection
  proxies, and compact per-step summaries.
- Added `experiments/steps/step116_regularized_lbm_duct_flow_baseline.py`, a
  bounded LBM-only runner for duct-only and static two-flap fluid baselines.
- The runner supports legacy `equilibrium_all_population_reset` and opt-in
  `regularized_velocity_pressure` boundary semantics.
- The runner writes per-row metadata, boundary reports, diagnostics CSVs,
  density drift CSVs, flux CSVs, velocity summaries, and finite stability
  reports.
- The runner treats strict tau failures as pre-step skips and records
  report-only tau risk in completed rows.
- Added focused Step116 contract tests for diagnostics, runner output, tau
  gating, and committed artifact schemas.

## Committed Artifacts

Artifacts live under:

`outputs/step116_regularized_lbm_duct_flow_baseline/`

Committed rows:

- `duct_only_48_legacy_boundary_500step`
- `duct_only_48_regularized_boundary_500step`
- `duct_only_96_regularized_boundary_1000step`
- `duct_only_96_regularized_boundary_physical_nu_report_only_100step`
- `static_two_flap_96_regularized_1000step`

The row names preserve the requested Step116 matrix. The committed executions
are bounded LBM-only rows with `executed_nx=8`, `steps_completed=5`, and
`requested_window_completed=false`. This is intentional and recorded in every
row metadata file. The full requested 48^3/96^3 long windows remain open for a
later explicit long-run pass.

## Answers To The Step116 Questions

1. Is regularized boundary more stable than legacy all-population reset?
   Not proven. Both committed 48-named bounded rows are finite, but the
   regularized row is not better by final mass drift in the committed data.
2. Do 48^3 and 96^3 duct-only rows run a long finite window?
   Not yet. The committed rows are simulation-backed bounded probes, not full
   requested 500/1000-step 48^3/96^3 windows.
3. Does static two-flap flow develop finite bounded downstream flow?
   The committed static two-flap fluid-only row stays finite for the bounded
   probe and writes throat/recirculation proxies. It is not FSI.
4. Is official-like physical-Re direct simulation still blocked by tau margin?
   Yes. The report-only physical-nu row records `tau_margin_pass=false`.
5. Can the project proceed to Fluent-equivalent FSI?
   No. Remaining blockers include long-window fluid validation, quasi-2D or
   periodic-z flow semantics, conservative traction transfer, and a
   Fluent-like small-strain solid path.

## Key Findings

- The Step115 regularized boundary can run in a real LBM-only row and emit
  mass/flux/density diagnostics.
- The committed bounded rows are too short and too small to validate outlet
  reflection, long-window mass conservation, or 96^3 stability.
- The physical-nu report-only row correctly keeps the near-half-tau risk
  visible instead of converting it into a validation claim.
- The static-flap row provides fluid-only flow diagnostics around fixed
  obstacles, but it does not include MPM, deformation, or two-way FSI.

## Verification

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py `
  experiments\steps\step116_regularized_lbm_duct_flow_baseline.py `
  src\mpm_lbm\sim\lbm\fluid.py `
  src\mpm_lbm\sim\drivers\fsi_config.py `
  src\mpm_lbm\sim\drivers\fsi_driver.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step115_lbm_open_boundary_and_force_accumulation_contract.py `
  tests\test_step116_lbm_boundary_diagnostics_contract.py `
  tests\test_step116_regularized_boundary_runner_contract.py `
  tests\test_step116_duct_flow_baseline_artifacts_contract.py `
  tests\test_step104_fluent_duct_flap_setup_repair_contract.py `
  tests\test_step106_outlet_boundary_flow_propagation_contract.py `
  tests\test_step112_planar_constraint_contract.py `
  tests\test_step113_mirrored_duct_flap_geometry_contract.py `
  tests\test_step114_fluent_solver_physics_repair_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q
git diff --check
```
