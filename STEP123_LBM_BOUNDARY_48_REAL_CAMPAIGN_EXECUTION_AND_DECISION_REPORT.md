# Step123 LBM Boundary 48 Real Campaign Execution And Decision Report

## Status

Step123 is a campaign-decision hardening step. It does not claim that the real
48^3 references, 48^3 candidates, selected 96^3 duct row, selected 96^3 static
row, quasi-2D, two-way FSI, Fluent validation, or Figure 29.3 parity are now
complete.

The current refreshed artifact remains the Step121 tiny real-run smoke:

- output directory:
  `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/`
- row: `tiny_step121_real_runner_smoke`
- executed window: 3/3 steps on a 5-cell tiny smoke grid
- campaign state: `awaiting_48_references`
- final classification: `boundary_repair_partial_continue_lbm`
- quasi-2D allowed: `false`
- FSI claim allowed: `false`
- Fluent/Figure 29.3 claim allowed: `false`

## What Changed

Step120 and Step121 now distinguish campaign terminal evidence from validation
success. A row can be terminal because it finished the requested window or
because it stopped on a simulation-backed physical failure. Wall-time expiry,
manual interruption, placeholders, and non-simulation rows are not counted as
terminal physical evidence.

Step120 now exposes separate identities for solver state and run manifest:

- `solver_state_hash` covers numerical state such as grid, viscosity/tau,
  inlet/outlet, geometry, limiter settings, force settings, and physical mapping
  fields that affect evolution.
- `run_manifest_hash` covers run-control/audit settings such as output cadence,
  checkpoint cadence, and snapshot behavior.
- checkpoint restore validates solver-state identity, while run-manifest
  identity is recorded for audit.
- `config_hash` is preserved as the solver-state hash for backward-compatible
  artifact readers.

Step120 also adds a spec-aware reusable-row predicate,
`step120_row_reusable_for_spec(row_dir, spec)`, and uses it before reusing a
completed/resumable row. Selected rows must match selected-source provenance
instead of being accepted by same-name output directories.

Step121 selected 96^3 gates now require flow-development evidence. A selected
96^3 duct pass requires reported flux balance, non-zero outlet tail flux,
acceptable tail flux imbalance, no first-failure marker, and the regular window
and validation checks. Missing flow-development fields fail the formal selected
gate instead of silently passing.

Formal selected 96^3 spec creation now fails fast when selected-boundary
provenance is missing. Legacy default provenance is still available only behind
an explicit legacy/migration flag.

The LBM diagnostics now summarize tail means for inlet/outlet flux, inlet and
midplane velocity, and outlet/midplane ratios. These fields are written into row
reports, summaries, and selected-gate reports.

## Errors Found While Running

The refreshed tiny smoke stayed numerically finite, but it is not a developed
duct-flow validation artifact:

- `flow_development_gate_pass`: `false`
- `flux_imbalance_rel_tail_mean`: `1.000001473653276`
- `outlet_flux_tail_mean`: `-8.940696893944235e-08`
- `outlet_to_inlet_flux_ratio_tail_mean`: `-1.4736532761617296e-06`
- `midplane_to_inlet_flux_ratio_tail_mean`: `0.04419642087891448`
- `mass_total_delta_rel_final`: `0.00960255265235901`

This is expected for the 5-cell, 3-step smoke and is now explicitly blocked
from being interpreted as selected 96^3 physical readiness.

The Step122 assumption corrected by this step is that completion/stability
fields alone were enough for selected campaign decisions. Step123 requires
terminal-evidence semantics, selected-source provenance, solver-state identity,
and flow-development evidence before a selected row can be accepted.

## Refreshed Artifacts

- `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/solver_report.json`
- `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/step121_gate_report.json`
- `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/tiny_step121_real_runner_smoke/finite_stability_report.json`
- `outputs/step121_lbm_boundary_real_campaign_and_gate_correction/tiny_step121_real_runner_smoke/run_metadata.json`

The refreshed gate report includes `selected_96_flow_development_gate`, currently
with `duct_pass=false` and `static_pass=false` because no selected boundary row
has been produced.

## Verification

Focused validation passed:

```powershell
D:\working\taichi\env\python.exe -m pytest -q tests\test_step123_boundary_campaign_execution_decision_contract.py -k "not real_taichi and not real_lbm"
# 10 passed, 2 deselected

D:\working\taichi\env\python.exe -m pytest -q tests\test_step123_boundary_campaign_execution_decision_contract.py -k "real_taichi or real_lbm"
# 2 passed, 10 deselected

D:\working\taichi\env\python.exe -m pytest -q tests\test_step123_boundary_campaign_execution_decision_contract.py
# 12 passed

D:\working\taichi\env\python.exe -m pytest -q tests\test_step121_campaign_gate_contract.py tests\test_step122_boundary_campaign_hardening_contract.py
# 12 passed

D:\working\taichi\env\python.exe -m pytest -q tests\test_step120_row_status_resume_contract.py
# 3 passed

D:\working\taichi\env\python.exe -m pytest -q tests\test_step120_checkpoint_restart_contract.py
# 1 passed

D:\working\taichi\env\python.exe -m pytest -q tests\test_step120_lightweight_reduction_contract.py
# 1 passed

D:\working\taichi\env\python.exe -m pytest -q tests\test_step120_actual_limiter_counter_contract.py tests\test_step120_best_boundary_selection_contract.py tests\test_step120_quasi2d_gate_contract.py tests\test_step120_skipped_artifact_semantics_contract.py
# 8 passed

D:\working\taichi\env\python.exe -m py_compile experiments\steps\step120_lbm_boundary_repair_large_real_execution.py experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py src\mpm_lbm\sim\lbm\fluid.py src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py
# passed

D:\working\taichi\env\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase smoke --force
# completed 3/3 tiny smoke steps

git diff --check
# passed, with Git line-ending normalization warnings only
```

Full-suite validation was attempted:

```powershell
D:\working\taichi\env\python.exe -m pytest -q
```

That run was stopped by the 20-minute command timeout after progressing past
71% with no failure output. Therefore this report does not claim a full-suite
green result for Step123.

## Remaining Blockers

The next real campaign step still has to execute and archive:

1. 48^3 reference rows.
2. 48^3 candidate rows.
3. selected 96^3 duct row, using the selected 48^3 provenance.
4. selected 96^3 static row, only after the selected 96^3 duct row passes.

Only after those artifacts pass the Step121/Step123 gates can the project reopen
quasi-2D, FSI, Fluent validation, or Figure 29.3 parity claims.
