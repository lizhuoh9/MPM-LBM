# Step116 Regularized LBM Duct Flow Baseline Goal

## User Request

Use the post-Step115 GitHub review of commit
`c45340f3c933be51a14f8cf72eb52dacba2aa1b0` as the implementation
contract. Step115 successfully fixed the Step114 runtime accumulator issue and
landed an opt-in D3Q19 x-axis `regularized_velocity_pressure` open-boundary
path, but it only proved a small runtime smoke and deterministic summary
artifacts. Step116 must convert that boundary repair into simulation-backed
duct-only and static-flap fluid evidence before any later full FSI work.

## Step116 Objective

Build a bounded, auditable fluid-baseline step for the Step115 regularized
open-boundary implementation:

1. Add reusable LBM boundary/mass/flux diagnostics that operate on Taichi field
   snapshots converted to NumPy arrays.
2. Add a resumable Step116 runner that can run duct-only and static-flap
   fluid-only baselines with legacy and regularized open-boundary semantics.
3. Produce committed, small, simulation-backed artifacts under
   `outputs/step116_regularized_lbm_duct_flow_baseline/`.
4. Quantify mass drift, density range, inlet/outlet flux balance, velocity
   development, observed Mach proxy, outlet reflection proxy, and tau
   feasibility.
5. Add artifact-backed tests that prove the diagnostics, runner, committed
   reports, and scope boundaries are present and finite.
6. Update docs, README, and Step116 report without claiming Fluent validation,
   Figure 29.3 parity, official mesh/case reproduction, full FSI readiness, or
   production solver readiness.

## Non-Goals And Guardrails

- Do not run Fluent.
- Do not import, copy, or commit private Ansys/Fluent case, data, or mesh files.
- Do not run full FSI in Step116.
- Do not tune flap deformation or change MPM solid response in Step116.
- Do not claim exact Fluent equivalence, exact Figure 29.3 jet parity, exact
  official monitor equivalence, official dynamic-mesh reproduction, or
  production-ready FSI.
- Do not touch `external/taichi_LBM3D`.
- Do not implement quasi-2D / periodic-z in Step116.
- Do not implement conservative interface traction transfer in Step116.
- Do not implement small-strain linear elasticity in Step116.
- Do not make `regularized_velocity_pressure` the default; legacy
  `equilibrium_all_population_reset` must remain the default behavior.
- Keep generated artifacts small enough to commit; do not commit full 96^3
  velocity fields or large binary dumps.

## Required P0 Work: Boundary/Mass/Flux Diagnostics

Add:

`src/mpm_lbm/sim/diagnostics/lbm_boundary_diagnostics.py`

Required diagnostic functions:

- `fluid_mask(lbm_or_snapshot)`
- `plane_flux_x(lbm_or_snapshot, x_index)`
- `plane_mean_velocity_x(lbm_or_snapshot, x_index)`
- `density_stats(lbm_or_snapshot)`
- `mass_total(lbm_or_snapshot)`
- `centerline_profile_x(lbm_or_snapshot, y_index=None, z_index=None)`
- `outlet_reflection_proxy(lbm_or_snapshot)`
- a compact one-call summary function suitable for runner output

Implementation requirements:

- Work on Taichi `LBMFluid3D` objects by converting `rho`, `v`, and `solid`
  fields to NumPy.
- Also accept lightweight dict/snapshot inputs so tests can use synthetic
  arrays without compiling Taichi.
- Count only `solid == 0` fluid cells for flux, mean velocity, mass, density,
  centerline, and outlet diagnostics.
- Use finite-safe calculations; if a plane has no fluid cells, report zero
  counts and `None` or finite zero fields explicitly rather than throwing an
  uncontrolled exception.
- `outlet_reflection_proxy` should be honest proxy diagnostics, such as
  outlet-near-plane `ux` standard deviation, negative-ux fraction, and density
  variation. It must not claim a physical reflection coefficient.

Acceptance:

- Synthetic tests prove flux excludes solid cells.
- Synthetic tests prove density/mass/centerline/outlet proxy schemas are
  finite and stable.
- The module has no dependency on private data or full driver initialization.

## Required P1 Work: Step116 Fluid Baseline Runner

Add a bounded, resumable runner under:

`experiments/steps/step116_regularized_lbm_duct_flow_baseline.py`

Required capabilities:

- Run small deterministic LBM-only duct rows using `LBMFluid3D` directly.
- Support `lbm_open_boundary_semantics` values:
  - `equilibrium_all_population_reset`
  - `regularized_velocity_pressure`
- Support a static two-flap fluid-only obstacle mask for a bounded baseline.
- Record diagnostics at a fixed interval and final step.
- Write metadata, boundary report, timeseries CSVs, summary JSON, and finite
  stability report for each row.
- Treat tau feasibility as a run gate:
  - `strict` plus failed tau margin should skip the row before LBM stepping and
    write `skipped_due_to_tau_margin=true`.
  - `report_only` plus failed tau margin may run, but must mark direct
    physical-Re feasibility false in the report.
- Reuse completed row outputs when `--resume` is enabled unless `--force` is
  provided.

Initial committed run matrix:

1. `duct_only_48_legacy_boundary_500step`
2. `duct_only_48_regularized_boundary_500step`
3. `duct_only_96_regularized_boundary_1000step`
4. `duct_only_96_regularized_boundary_physical_nu_report_only_100step`
5. `static_two_flap_96_regularized_1000step`
6. Optional if runtime remains reasonable:
   `static_two_flap_96_legacy_1000step`

If the full suggested matrix is too slow for the current turn, the runner must
still support the names and schema, and committed artifacts must honestly state
which rows ran, which were skipped, and why. Do not fake completed long runs.

## Required P2 Work: Simulation-Backed Artifacts

Create committed output directory:

`outputs/step116_regularized_lbm_duct_flow_baseline/`

Required top-level files:

- `solver_report.json`
- `run_matrix_summary.csv`
- `run_matrix_summary.json`
- `README.md` or equivalent artifact index if useful

Each completed row directory must include:

- `run_metadata.json`
- `driver_config.json` or lightweight LBM config report
- `duct_boundary_condition_report.json`
- `fluid_diagnostics_timeseries.csv`
- `boundary_flux_timeseries.csv`
- `density_drift_timeseries.csv`
- `velocity_profile_summary.json`
- `finite_stability_report.json`

Static two-flap rows should additionally include:

- `flap_region_flow_summary.json`
- `throat_speed_summary.json`
- `recirculation_proxy_summary.json`

Required recorded metrics:

- `step`
- `rho_min`
- `rho_max`
- `rho_mean`
- `mass_total`
- `mass_total_delta_from_initial`
- `mass_total_delta_rel`
- `inlet_mean_ux`
- `outlet_mean_ux`
- `midplane_mean_ux`
- `inlet_flux`
- `outlet_flux`
- `flux_imbalance_abs`
- `flux_imbalance_rel`
- `max_v`
- `mach_proxy_observed`
- `centerline_ux_profile`
- `outlet_reflection_proxy`

Initial engineering gates:

- All committed records must be finite unless a row is explicitly skipped.
- Completed rows must report whether `rho_min > 0.8` and `rho_max < 1.2`.
- Completed rows must report whether
  `abs(mass_total_delta_from_initial) / mass_initial < 5%`.
- Regularized 48^3 must not be reported as better than legacy unless the
  artifact data supports it.
- 96^3 regularized must report whether it completed the requested window and
  whether it stayed finite.

## Required P3 Work: Tests

Add focused tests:

1. `tests/test_step116_lbm_boundary_diagnostics_contract.py`
2. `tests/test_step116_regularized_boundary_runner_contract.py`
3. `tests/test_step116_duct_flow_baseline_artifacts_contract.py`

Test requirements:

- Diagnostics tests use synthetic arrays to prove fluid masks, flux, mass,
  density stats, centerline schema, and outlet reflection proxy behavior.
- Runner tests execute tiny legacy and regularized LBM-only rows, such as
  `8 x 6 x 6` for `5-10` steps, and verify CSV/JSON output fields.
- Runner tests verify `lbm_open_boundary_semantics` is written into metadata.
- Runner tests verify tau strict risky configs are skipped before stepping.
- Artifact tests verify committed Step116 outputs exist and include
  `finite_pass`, `density_gate_pass`, `flux_balance_reported`,
  `fluent_validation_claim_allowed=false`, and `full_fsi_rerun_done=false`.
- Step115 tests and adjacent Fluent-step contract tests must remain green.

## Required P4 Work: Docs And Reports

Add:

- `STEP116_REGULARIZED_LBM_DUCT_FLOW_BASELINE_REPORT.md`
- `docs/116_regularized_lbm_duct_flow_baseline.md`
- README Step116 implemented entry and a scoped Step116 section

The Step116 report must answer:

1. Is regularized boundary more stable than legacy all-population reset?
2. Do 48^3 and 96^3 duct-only rows run a long finite window?
3. Does static two-flap flow develop finite bounded downstream flow?
4. Is official-like physical-Re direct simulation still blocked by tau margin?
5. Can the project proceed to FSI now? If not, what remains blocked?

The expected answer is conservative: Step116 may establish a more useful
fluid-only baseline, but it still must not claim Fluent-equivalent FSI.

## Verification Plan

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

If the 48^3/96^3 baseline rows are too expensive for pytest, keep them in the
Step116 runner and make pytest validate committed artifact schemas. Tiny rows
only may run inside pytest.

## Push Requirement

After implementation and verification, commit and push to the configured
GitHub remote `origin/main`. Report:

- final commit hash
- branch and remote
- focused and full test results
- committed artifact summary
- whether push succeeded
- known remaining solver gaps
