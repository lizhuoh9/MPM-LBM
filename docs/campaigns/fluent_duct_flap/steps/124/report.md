# Step124 LBM Boundary Campaign-Readiness Report

## Scope

Step124 implements the campaign-readiness fixes requested after commit
`516b1aaa4c71d5468ce5ea444a21ffa07741c8bc`.

The result remains bounded to LBM campaign gating. It does not claim quasi-2D,
FSI, Fluent validation, or Figure 29.3 parity.

## Code Changes

- Added terminal reference handling for legacy 48^3 reference physical failure:
  the campaign now reports `48_legacy_reference_failed` and stops at 48 instead
  of staying in `awaiting_48_references`.
- Kept old regularized 48^3 reference physical failure available as explicit
  failed-baseline comparison evidence.
- Added shared dimensionless flow-development gates for 48^3 candidates and
  selected 96^3 rows:
  inlet flux minimum, inlet/outlet sign consistency, outlet-to-inlet ratio,
  midplane-to-inlet ratio, tail mean imbalance, tail max imbalance, and outlet
  tail CV.
- Added `flux_imbalance_rel_tail_max` and `outlet_flux_tail_cv` to LBM boundary
  trend summaries and Step120 summary rows.
- Made 48^3 candidate selection reject zero-throughput and oscillating-tail
  candidates before they can be selected as best boundary rows.
- Added campaign manifest writing/reading for Step121 collection. Summary now
  ignores rows with mismatched solver-state hashes or selected-source
  provenance when a manifest is present, and reports ignored rows explicitly.
- Added current campaign docs under `docs/current/` and moved Step124 goal/report
  into `docs/campaigns/fluent_duct_flap/steps/124/`.
- Added a small Step116 runner isolation fix: Step116 now resets/reinitializes
  Taichi between rows in its historical two-row matrix runner. This fixed a
  silent process exit found while running the full regression suite; it does not
  change solver formulas.

## Refreshed Artifacts

The Step121 smoke artifact was rerun with:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase smoke --force
```

The refreshed artifact is still only tiny smoke runner evidence:

- row: `tiny_step121_real_runner_smoke`
- completed steps: 3/3
- `campaign_state=awaiting_48_references`
- `final_classification=boundary_repair_partial_continue_lbm`
- `quasi2d_allowed=false`
- `full_fsi_validation_claim_allowed=false`
- `fluent_validation_claim_allowed=false`
- `figure_29_3_parity_claim_allowed=false`

The new manifest is:

- `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/campaign_manifest.json`

## Validation

Commands and outcomes:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step124_boundary_campaign_execution_contract.py
```

Result: `7 passed`.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step121_campaign_gate_contract.py tests\test_step122_boundary_campaign_hardening_contract.py tests\test_step123_boundary_campaign_execution_decision_contract.py
```

Result: `24 passed`.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests\test_step120_actual_limiter_counter_contract.py tests\test_step120_best_boundary_selection_contract.py tests\test_step120_checkpoint_restart_contract.py tests\test_step120_lightweight_reduction_contract.py tests\test_step120_quasi2d_gate_contract.py tests\test_step120_row_status_resume_contract.py tests\test_step120_skipped_artifact_semantics_contract.py
```

Result: split Step120 runs passed: `4 passed`, `6 passed`, `1 passed`,
`1 passed`, and `1 passed` across the focused groups.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q --cache-clear --tb=short tests\test_step116_lbm_boundary_diagnostics_contract.py tests\test_step116_regularized_boundary_runner_contract.py
```

Result after the Step116 row-isolation fix: `4 passed`.

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile experiments\steps\step116_regularized_lbm_duct_flow_baseline.py experiments\steps\step120_lbm_boundary_repair_large_real_execution.py experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py tests\test_step124_boundary_campaign_execution_contract.py
```

Result: passed.

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q --cache-clear --durations=50 --disable-warnings
```

Result: `1315 passed, 56 warnings in 1220.69s (0:20:20)`.

## Errors Found While Running

- The first full pytest attempt exited with code 1 around the Step116 runner
  region and no assertion traceback.
- Isolating the ordered collection showed the exit occurred at
  `test_step116_tiny_legacy_and_regularized_runner_emit_diagnostics`.
- Single Step116 legacy and regularized rows passed independently, but the
  two-row Step116 matrix exited when both ran in one Taichi runtime.
- Manual row-by-row probing showed that `ti.reset()` plus reinitialization
  between Step116 rows prevented the exit. The Step116 runner now applies that
  isolation between rows.

## Remaining Boundary

Step124 is a gate/readiness step. The real campaign still must run, in order:

1. 48^3 references.
2. 48^3 candidates.
3. Selected 96^3 duct.
4. Selected 96^3 static.

Only artifacts from those real phases can change the current blocked status for
quasi-2D, FSI, Fluent validation, or Figure 29.3 parity.
