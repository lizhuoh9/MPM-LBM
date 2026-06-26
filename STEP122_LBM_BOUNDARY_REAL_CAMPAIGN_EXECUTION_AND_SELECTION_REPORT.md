# Step122 LBM Boundary Real Campaign Execution And Selection Report

## Status

Step122 implements the hardening requested after review of remote `main` commit
`82ded671a598940e120f3c9dcc63983a44b9c21a`.

Current committed artifact state:

- Goal file:
  `STEP122_LBM_BOUNDARY_REAL_CAMPAIGN_EXECUTION_AND_SELECTION_GOAL.md`
- Output directory refreshed:
  `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/`
- Phase executed in this commit: `smoke`
- Campaign state: `awaiting_48_references`
- Final classification: `boundary_repair_partial_continue_lbm`
- Quasi-2D allowed: `false`
- Fluent/Figure 29.3/FSI claim allowed: `false`

This is not a real 48^3/96^3 success claim. The full campaign still requires
the explicit `references48`, `candidates48`, selected `96^3` duct, and selected
`96^3` static phases to run and pass.

## What Was Fixed

Step122 closes five solver-runner and campaign-control gaps:

1. `selected-static` now fails fast unless the selected `96^3` duct row exists
   in the selected output directory and has actually passed its Step120 row
   gate.
2. Step121 best-boundary selection now records selected 48^3 boundary
   provenance, including limiter settings, open-boundary clamps, inlet/outlet
   values, viscosity/relaxation semantics, tau, and config hash.
3. Selected `96^3` duct/static specs now inherit the selected 48^3 boundary
   parameters instead of silently falling back to defaults.
4. Step120 `.npz` checkpoint restore now has a history-preserving API and the
   runner merges checkpoint history with CSV history on resume.
5. Step120 lightweight stability reduction now carries `mass_total`, so the
   immediate failure detector can stop on mass drift before the next full
   NumPy diagnostic sample.

## Code Changes

Changed files:

- `experiments/steps/step120_lbm_boundary_repair_large_real_execution.py`
- `experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py`
- `src/mpm_lbm/sim/lbm/fluid.py`
- `tests/test_step122_boundary_campaign_hardening_contract.py`

Step120 changes:

- Added selected-source provenance fields to `Step120RunSpec`.
- Added `restore_latest_step120_checkpoint_with_history(...)` while preserving
  the previous three-field `restore_latest_step120_checkpoint(...)` API.
- Merged restored `.npz` history with row CSV history before continuing a row.
- Added lightweight `mass_total` and `mass_total_delta_rel` to the stability
  timeseries.
- Added immediate mass-drift detection to `_step120_lightweight_failure_detector`.

Step121 changes:

- Added `selected_boundary_provenance` to the best-boundary selection payload.
- Added provenance inheritance in `make_selected_96_specs(...)`.
- Added an `output_dir`-aware `selected-static` guard so static execution cannot
  start before the selected duct row has completed and passed.

LBM core change:

- `LBMFluid3D.reduce_lbm_stability_diagnostics()` now accumulates fluid-cell
  mass and fluid-cell count on the Taichi side.

## Errors Found During Implementation

- The previous selected-static phase could be generated from only the selection
  JSON and did not inspect the selected 96^3 duct result directory first.
- The selected 96^3 specs only inherited the selected boundary semantics and
  limiter enabled flag; the actual selected 48^3 physical/numerical boundary
  parameters were lost.
- Checkpoints already wrote `history_json`, but restore ignored that payload.
- Lightweight stopping checked density, speed, finite fields, and negative
  population fraction, but not mass drift.
- Tests covered helper contracts, but not the runner path where immediate
  lightweight failure writes a checkpoint and failure snapshot.

## Verification

Commands run:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest tests\test_step122_boundary_campaign_hardening_contract.py -q
```

Result: `6 passed`.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest tests\test_step120_lightweight_reduction_contract.py tests\test_step120_checkpoint_restart_contract.py tests\test_step121_campaign_gate_contract.py tests\test_step121_checkpoint_failure_contract.py tests\test_step122_boundary_campaign_hardening_contract.py -q
```

Result: `18 passed`.

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile experiments\steps\step120_lbm_boundary_repair_large_real_execution.py experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py src\mpm_lbm\sim\lbm\fluid.py tests\test_step122_boundary_campaign_hardening_contract.py
```

Result: passed.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
```

Result: `1296 passed, 48 warnings in 1247.35s`.

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase smoke --force
```

Result: completed `tiny_step121_real_runner_smoke` through 3/3 steps and
refreshed Step121 smoke artifacts. The final smoke mass drift was about
`0.00960255`.

The warnings are the existing Taichi warning about 19x19 matrix/vector fields
being compile-time unrolled.

## What Was Not Claimed

Step122 does not claim:

- real 48^3 references completed,
- real 48^3 candidate selection completed,
- selected 96^3 duct-only success,
- selected 96^3 static two-flap success,
- quasi-2D readiness,
- two-way FSI readiness,
- Fluent parity,
- Figure 29.3 parity.

## Next Execution Order

1. Run `references48` with `--allow-large-real-rows`.
2. Run `candidates48` with `--allow-large-real-rows`.
3. Inspect `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_best_boundary_selection.json`.
4. If a best 48^3 candidate is selected, run `selected96`.
5. Only after the selected 96^3 duct row passes, run `selected-static`.
6. Refresh `--phase summary` and inspect `step121_gate_report.json`.
