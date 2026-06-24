# Step103 Fluent-Inspired Duct-Flap Proxy Solver Comparison Smoke Report

Allowed claim:

```text
Fluent-inspired duct-flap proxy comparison smoke ran and produced a solver gap report.
```

This report does not claim Fluent equivalence, Fluent validation, physical validation, real FSI validation, or production readiness.

## Source Boundary

- Public inspiration/source metadata: Ansys Fluent Tutorial Chapter 29, "Modeling Two-Way Fluid-Structure Interaction (FSI) Within Fluent", 2024 R2.
- Source URL recorded from Step102: `https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_tg/flu_tg_fsi_2way.html`
- Official Fluent files were not imported, committed, or used as runtime input.
- Optional local CSV path remains private: `benchmarks/private/fluent_fsi_2way/reference/fluent_structural_point_flap_displacement.csv`

## Implementation Summary

- Added procedural `duct_flap_proxy` geometry support under `src/mpm_lbm/sim/geometry/`.
- Added Step103 driver, Fluent reference loader, solver-gap comparison, activation guard, output guard, Step100/Step102 regression guards, and artifact manifest runner.
- Added Step103 configs, contract tests, documentation, outputs, logs, and this report.
- Updated existing schema/behavior audits to record the controlled `GeometryConfig` extension and new `duct_flap_proxy` geometry type.
- Did not modify LBM collision, LBM tau, MPM update, coupling, moving-boundary, wall-velocity, or reaction-transfer formulas.
- Did not edit `external/taichi_LBM3D/**` or `data/real_geometry_candidates/**`.

## Solver Smoke Result

Artifact: `outputs/step103_smoke_matrix/fluent_inspired_duct_flap_proxy_smoke_matrix.json`

- row: `fluent_inspired_duct_flap_proxy_48_5step_ggui_comparison_smoke`
- canonical driver: `src.mpm_lbm.sim.drivers.fsi_driver`
- geometry type: `duct_flap_proxy`
- `n_grid = 48`
- `n_particles = 1024`
- `n_lbm_steps = 5`
- completed LBM steps: `5`
- diagnostics rows: `6`
- `has_nan = false`
- `has_inf = false`
- stable: `true`
- GGUI screenshot count: `1`
- VTR outputs: `0`
- particle NPY outputs: `0`
- video outputs: `0`

## Gap Report Result

Artifact: `outputs/step103_fluent_comparison/fluent_solver_gap_report.json`

- `comparison_status = capability_gap_detected`
- `fluent_reference_available = false`
- `fluent_reference_row_count = 0`
- `official_case_dimensionality = 2D`
- `our_solver_dimensionality = 3D`
- `direct_quantitative_equivalence_allowed = false`
- `validation_claim_allowed = false`
- `official_structural_model = linear_elasticity_intrinsic_fsi`
- `our_structural_model_equivalent = false`
- `official_dynamic_mesh = true`
- `our_geometry_mutation_enabled = false`
- `official_monitor_quantity = total_displacement`
- `our_equivalent_flap_tip_displacement_available = false`
- `capability_gap_count = 6`

Recorded capability gaps:

- dimensionality equivalence
- conformal mesh equivalence
- linear elasticity equivalence
- dynamic mesh equivalence
- exact flap-tip displacement
- dimensional velocity mapping

## Guard Results

- Step103 activation guard: passed
- Step103 output guard: passed
- Step103 Step102 regression guard: passed
- Step103 Step100 regression guard: passed
- Step103 artifact manifest: passed
- Step57 behavior preservation audit after controlled geometry-type update: passed
- Step71 config schema delta audit after controlled `GeometryConfig` delta: passed

## Verification Commands

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step103_fluent_inspired_duct_flap_proxy_smoke_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step103_fluent_solver_gap_comparison.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step103_activation_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step103_step102_regression_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step103_step100_regression_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step103_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step103_artifact_manifest.py
```

Result: all passed.

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step57_behavior_preservation_audit.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step71_config_schema_delta_audit.py
```

Result: both passed.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step103_fluent_inspired_duct_flap_proxy_smoke_matrix_contract.py tests\test_step103_fluent_solver_gap_comparison_contract.py tests\test_step103_activation_guard_contract.py tests\test_step103_output_guard_contract.py tests\test_step103_step102_regression_contract.py tests\test_step103_step100_regression_contract.py
```

Result: `6 passed in 1.40s`.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Result: `1146 passed in 152.38s`.

```powershell
& 'D:\TOOL\Anaconda\python.exe' -m pytest -q
```

Result: `1146 passed, 1 warning in 77.64s`. The warning is a third-party Taichi deprecation warning from Anaconda Python.

## Notes

- A first full pytest run exposed expected audit drift from adding `duct_flap_proxy` to `GeometryConfig`; the Step57 and Step71 audit policies and artifacts were updated to record this controlled Step103 schema/geometry-type extension.
- The Step103 wall-velocity acceptance uses Step103 invariants: `solid_vel` target, finite/capped report semantics, no LBM population update, no MPM/projector application, and no formula modification. It does not reuse the old Step36 aggregate `report_pass` as a hard Step103 gate.
