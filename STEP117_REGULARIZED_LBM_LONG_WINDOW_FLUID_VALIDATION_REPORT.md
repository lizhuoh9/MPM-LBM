# Step117 Regularized LBM Long-Window Fluid Validation Report

Step117 upgrades the Step116 bounded LBM-only probes into real long-window
fluid-only validation artifacts. It does not run full FSI and does not claim
Fluent validation, Figure 29.3 parity, official mesh/case reproduction, or
production readiness.

## Implemented

- Added `summarize_timeseries_trends(records, tail_fraction=0.2)` to
  `src/mpm_lbm/sim/diagnostics/lbm_boundary_diagnostics.py`.
- Added `experiments/steps/step117_regularized_lbm_long_window_fluid_validation.py`,
  a dedicated Step117 runner with `--row`, `--max-rows`, `--resume`,
  `--force`, `--output-interval`, `--profile-only`, and `--no-large-arrays`.
- Added Step117 long-window gates for density range, mass drift, flux
  development, flux imbalance trend reporting, outlet reflection proxy, and
  regularized-vs-legacy comparison.
- Added strict physical-nu tau policy artifacts and a surrogate Reynolds
  feasibility report.
- Added focused Step117 tests for trend summaries, runner contracts, row-level
  resume, strict tau skip, profile-only output, and committed artifact schema.

## Committed Artifacts

Artifacts live under:

`outputs/step117_regularized_lbm_long_window_fluid_validation/`

Committed required rows:

- `duct_only_48_legacy_boundary_500step_full`
- `duct_only_48_regularized_boundary_500step_full`
- `duct_only_96_regularized_boundary_1000step_full`
- `static_two_flap_96_regularized_1000step_full`
- `duct_only_96_regularized_boundary_physical_nu_report_only_100step_guarded`

The first four rows were executed as real long-window LBM-only rows. The
physical-nu row was strict tau-gated and skipped before stepping, as intended.

## Long-Window Results

| Row | Window Complete | Density Gate | Mass Gate | Final Mass Drift | Final Flux Imbalance | Tail Outlet Flux | Runtime |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| `duct_only_48_legacy_boundary_500step_full` | true | true | true | `7.730374927e-4` | `2.374315448e-2` | `40.3914` | `112.434 s` |
| `duct_only_48_regularized_boundary_500step_full` | true | true | true | `2.957161604e-3` | `4.502873392e-1` | `52.1999` | `39.773 s` |
| `duct_only_96_regularized_boundary_1000step_full` | true | false | false | `1.211313979e8` | `~1.0` | `220.2711` | `279.218 s` |
| `static_two_flap_96_regularized_1000step_full` | true | false | false | `7.938583357e8` | `~1.0` | `91.8085` | `204.204 s` |
| `duct_only_96_regularized_boundary_physical_nu_report_only_100step_guarded` | false | false | false | n/a | n/a | n/a | `0.0 s` |

## Answers To The Step117 Questions

1. Did the 48^3 legacy row complete 500 steps?
   Yes. It completed the requested window, stayed finite, passed the density
   and mass gates, and developed nonzero outlet flux.
2. Did the 48^3 regularized row complete 500 steps?
   Yes. It completed the requested window and passed the density and mass
   gates, but its final mass drift and flux imbalance were worse than the
   48^3 legacy row.
3. Did the 96^3 regularized duct-only row complete 1000 steps?
   It completed the requested step count, but failed the long-window validation
   gates. The final density range was approximately
   `[-9.826e12, 6.274e12]`, and final mass drift was about `1.211e8`.
4. Did the static two-flap 96^3 regularized row complete 1000 steps?
   It completed the requested step count, but failed the long-window validation
   gates. The final density range was approximately
   `[-2.022e13, 2.404e13]`, and final mass drift was about `7.939e8`.
5. Is regularized better than legacy?
   No. The committed comparison result is
   `regularized_not_acceptable_for_long_window`.
6. Is the physical-nu official-like path still blocked by tau margin?
   Yes. The strict physical-nu row skipped before stepping and is marked
   `not_used_for_validation=true`.
7. Can Step118 proceed to quasi-2D?
   No. Step118 must continue LBM boundary/stability work rather than quasi-2D
   or FSI.

## Technical Findings

- Step117 proves that the runner can execute real 48^3/500 and 96^3/1000
  LBM-only windows and persist compact CSV/JSON artifacts.
- The 48^3 regularized row is not a clear improvement over the legacy boundary:
  final mass drift is higher and final/tail flux imbalance is much worse.
- The 96^3 regularized duct-only row numerically destabilizes near the end of
  the 1000-step window.
- The 96^3 static two-flap row also destabilizes near the end of the 1000-step
  window.
- The official-like physical viscosity mapping remains blocked by the tau
  margin policy and cannot be used as validation.

## Step118 Gate

Step118 quasi-2D is not allowed from this evidence. The required 96^3
regularized rows completed the requested step counts but failed density and
mass-drift gates, and the regularized 48^3 row was worse than legacy by the
comparison rule.

The next step should repair or replace the LBM open-boundary behavior and
rerun the long-window fluid gate before adding quasi-2D, conservative
interface traction, small-strain solid behavior, or full FSI.

## Verification

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py `
  experiments\steps\step116_regularized_lbm_duct_flow_baseline.py `
  experiments\steps\step117_regularized_lbm_long_window_fluid_validation.py `
  src\mpm_lbm\sim\lbm\fluid.py `
  src\mpm_lbm\sim\drivers\fsi_config.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step116_lbm_boundary_diagnostics_contract.py `
  tests\test_step116_regularized_boundary_runner_contract.py `
  tests\test_step116_duct_flow_baseline_artifacts_contract.py `
  tests\test_step117_long_window_runner_contract.py `
  tests\test_step117_timeseries_trend_summary_contract.py `
  tests\test_step117_long_window_artifacts_contract.py `
  tests\test_step115_lbm_open_boundary_and_force_accumulation_contract.py `
  tests\test_step114_fluent_solver_physics_repair_contract.py `
  tests\test_step104_fluent_duct_flap_setup_repair_contract.py `
  tests\test_step106_outlet_boundary_flow_propagation_contract.py `
  tests\test_step112_planar_constraint_contract.py `
  tests\test_step113_mirrored_duct_flap_geometry_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q
git diff --check
```
