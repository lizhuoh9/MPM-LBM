# Step119 Report: LBM Boundary Repair Real-Run Validation

## Result

Step119 adds the real non-synthetic validation runner and artifact gates for
the Step118 boundary repair variants.

Final classification:

`boundary_repair_partial_continue_lbm`

Step119 quasi-2D remains blocked. No Fluent validation is claimed. No full FSI validation is claimed.

## What Changed

Code changes:

- Added `experiments/steps/step119_lbm_boundary_repair_real_run_validation.py`.
- Added real-row `Step119RunSpec` defaults with `synthetic_diagnostic_mode=false`.
- Added a one-row runner flow for real LBM-only rows.
- Added explicit large-row gating through `--allow-large-real-rows`.
- Added Step119 gate report generation.
- Added Step119 limiter activation summaries.
- Added first-failure localization fields for Step119 artifacts.

Tests added:

- `tests/test_step119_real_run_runner_contract.py`
- `tests/test_step119_boundary_repair_real_artifacts_contract.py`
- `tests/test_step119_limiter_activation_summary_contract.py`
- `tests/test_step119_gate_report_contract.py`

Artifacts added under:

`outputs/step119_lbm_boundary_repair_real_run_validation/`

## Important Artifact Boundary

All Step119 committed rows are marked `synthetic_diagnostic_mode=false`.

The committed output includes one real tiny LBM row:

`tiny_step119_real_runner_smoke`

That row proves the Step119 runner can instantiate `LBMFluid3D`, step the
limited regularized boundary path, and write real diagnostics. It is explicitly
`not_used_for_validation=true`.

The required 48^3 and 96^3 long-window rows are not executed in the committed
artifact set. They are written as incomplete real-run targets with
`large_real_row_requires_explicit_allowance`, so they cannot be mistaken for
synthetic success or physical validation.

## Current Gate State

From `outputs/step119_lbm_boundary_repair_real_run_validation/step119_gate_report.json`:

- `quasi2d_allowed = false`
- `step120_quasi2d_allowed = false`
- `validation_claim_allowed = false`
- `final_classification = boundary_repair_partial_continue_lbm`

Incomplete required rows:

- `duct_only_48_legacy_boundary_500step_reference_real`
- `duct_only_48_regularized_boundary_500step_reference_real`
- `duct_only_48_regularized_limited_boundary_500step_real`
- `duct_only_48_convective_outlet_boundary_500step_real`
- `duct_only_96_regularized_limited_boundary_1000step_real`
- `duct_only_96_convective_outlet_boundary_1000step_real`
- `static_two_flap_96_best_boundary_1000step_real`

## Findings

1. The real tiny row completed, so Step119 no longer relies only on synthetic
   schema rows.
2. `LBMFluid3D` still emits the existing Taichi 19x19 MRT matrix warning during
   initialization; this remains the main runtime-cost issue for repeated real
   rows.
3. The required long-window rows are intentionally not run by default. Running
   them now requires `--allow-large-real-rows` plus explicit row selection.
4. No Step119 artifact proves that limited or convective boundaries improve
   over Step117 regularized behavior yet.
5. No real 96^3 first-failure location has been identified yet.

## Remaining Work

The next evidence step is to run the real rows in controlled order:

1. `duct_only_48_legacy_boundary_500step_reference_real`
2. `duct_only_48_regularized_boundary_500step_reference_real`
3. `duct_only_48_regularized_limited_boundary_500step_real`
4. `duct_only_48_convective_outlet_boundary_500step_real`
5. Only if 48^3 improves: run the 96^3 duct-only rows.
6. Only if a 96^3 duct-only row passes: run
   `static_two_flap_96_best_boundary_1000step_real`.

Example explicit row command:

```powershell
& 'D:\working\taichi\env\python.exe' `
  experiments\steps\step119_lbm_boundary_repair_real_run_validation.py `
  --row duct_only_48_regularized_limited_boundary_500step_real `
  --allow-large-real-rows `
  --force
```

Only after the real 48^3, 96^3 duct-only, and 96^3 static two-flap gates pass
should quasi-2D be reconsidered.

## Verification

Step119 focused contract tests:

`10 passed, 4 warnings in 33.21s`

Step119 plus Step118/117/116/115/114/113/112/106/104 regression slice:

`63 passed, 16 warnings in 217.31s`

Full repository pytest:

`1267 passed, 20 warnings in 513.47s`

The warnings are the existing Taichi 19x19 matrix/vector initialization
warnings exercised by the LBM runtime smoke paths.
