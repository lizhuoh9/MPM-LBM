# Step126 LBM Boundary 48^3 Reference Campaign Execution Report

## Summary

Step126 executed the real 48^3 reference phase for the Fluent duct/flap LBM
open-boundary repair campaign.

Rows run:

- `duct_only_48_legacy_boundary_500step_reference_real`
- `duct_only_48_regularized_boundary_500step_reference_real`

Both rows reached `500/500` steps with simulation-backed artifacts and no first
failure. The legacy reference passed the flow-development gate. The old
regularized reference completed the stability window but failed the
flow-development gate, which is useful comparison evidence for the next
candidate phase.

The refreshed Step121 summary state is:

```text
campaign_state = awaiting_48_candidates
final_classification = boundary_repair_partial_continue_lbm
```

Step127 `candidates48` is allowed. Step126 did not run candidates, selected
96^3 duct, selected 96^3 static, quasi-2D, FSI, Fluent validation, or Figure
29.3 parity validation.

## Preflight

Local and live remote refs before the real run:

```text
HEAD = 6ad3108994c55d1863fc2c2d4a830a26799fc9f4
origin/main = 6ad3108994c55d1863fc2c2d4a830a26799fc9f4
```

Preflight focused campaign contracts:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step126-preflight `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

Result:

```text
22 passed, 8 warnings in 192.79s
```

## Runtime Commands

References:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase references48 `
  --allow-large-real-rows `
  --output-interval 25
```

Summary refresh:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase summary
```

No `--force` was used. No checkpoint restore was used by either reference row.

## Manifest Provenance

Campaign manifest:

```text
campaign_base_commit = 516b1aaa4c71d5468ce5ea444a21ffa07741c8bc
current_code_commit = 6ad3108994c55d1863fc2c2d4a830a26799fc9f4
git_commit = 6ad3108994c55d1863fc2c2d4a830a26799fc9f4
phase_history = smoke, references48
```

Phase commit history:

```text
smoke -> 516b1aaa4c71d5468ce5ea444a21ffa07741c8bc
references48 -> 6ad3108994c55d1863fc2c2d4a830a26799fc9f4
```

## Reference Rows

### Legacy Reference

```text
name = duct_only_48_legacy_boundary_500step_reference_real
semantics = equilibrium_all_population_reset
code_commit_at_run = 6ad3108994c55d1863fc2c2d4a830a26799fc9f4
solver_state_hash = aa4d0a0d2bd146209d3c915b06f0d0390c1ccbfa68f4ebb7a0a1f511ffdab461
run_manifest_hash = 25ed0f637e30110ee52fbe7a46e8f9e9069a7cd7ec9876839ad07566f4e47d50
requested_window_completed = true
steps_completed = 500
simulation_backed_artifact = true
step120_validation_claimed = true
finite_pass = true
density_gate_pass = true
mass_drift_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
flow_development_gate_pass = true
mass_total_delta_rel_final = 0.0007730374927265733
flux_imbalance_rel_tail_mean = 0.04043317017445867
flux_imbalance_rel_tail_max = 0.08607841290325333
outlet_to_inlet_flux_ratio_tail_mean = 0.9595668298255413
midplane_to_inlet_flux_ratio_tail_mean = 0.9556179894908249
outlet_flux_tail_cv = 0.02463282965556423
first_failure_step = null
first_failure_reason = null
runtime_s = 186.73114650000934
checkpoint_available = true
restored_checkpoint = null
```

### Old Regularized Reference

```text
name = duct_only_48_regularized_boundary_500step_reference_real
semantics = regularized_velocity_pressure
code_commit_at_run = 6ad3108994c55d1863fc2c2d4a830a26799fc9f4
solver_state_hash = 2eb3ff1c97e321a47262dd91b483c7cf26630cdeae7b85026ceed67e7d9af4d3
run_manifest_hash = 6423a781435a5bbf4bfa868659bc4f81a40feaa967c2d7e8913b4d584620c29c
requested_window_completed = true
steps_completed = 500
simulation_backed_artifact = true
step120_validation_claimed = true
finite_pass = true
density_gate_pass = true
mass_drift_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
flow_development_gate_pass = false
mass_total_delta_rel_final = 0.002957161603977865
flux_imbalance_rel_tail_mean = 0.5116500495884674
flux_imbalance_rel_tail_max = 0.8660866973898724
outlet_to_inlet_flux_ratio_tail_mean = 1.4127437709040476
midplane_to_inlet_flux_ratio_tail_mean = 1.3061915562381126
outlet_flux_tail_cv = 0.4528776651615377
first_failure_step = null
first_failure_reason = null
runtime_s = 65.5859053999884
checkpoint_available = true
restored_checkpoint = null
```

## Decision

`step121_best_boundary_selection.json` reports:

```text
reference_comparison_ready = true
legacy_reference_failed = false
failed_reference_semantics = []
incomplete_reference_semantics = []
missing_reference_semantics = []
selection_reason = 48_candidate_rows_not_complete
campaign_should_stop_at_48 = false
```

Therefore Step126 permits Step127 to run `candidates48`.

## Verification

Changed entry-point Python files compiled:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py
```

Result: pass.

The first post-run focused test pass exposed a stale Step124 documentation
assertion that hardcoded `awaiting_48_references` in `STATUS.md`. That was no
longer valid after Step126 advanced the real campaign to
`awaiting_48_candidates`. The assertion was narrowed to require the active
campaign state from `ACTIVE_CAMPAIGN.json` to appear in `STATUS.md`.

Final focused campaign contracts:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step126-focused `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

Result:

```text
22 passed, 8 warnings in 88.70s
```

## Claims Not Made

Step126 remains LBM-only reference execution. It does not claim:

- 48^3 candidate success.
- selected 96^3 duct success.
- selected 96^3 static success.
- quasi-2D validation.
- FSI validation.
- Fluent validation.
- Figure 29.3 parity.

## Next Step

Create Step127 for `candidates48` only if the user approves the next execution
step. The expected command is:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase candidates48 `
  --allow-large-real-rows `
  --output-interval 25
```
