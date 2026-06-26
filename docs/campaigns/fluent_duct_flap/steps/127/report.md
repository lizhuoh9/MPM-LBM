# Step127 LBM Boundary 48^3 Candidate Campaign Execution Report

## Summary

Step127 executed the real 48^3 `candidates48` phase for the Fluent duct/flap
LBM open-boundary repair campaign.

Rows run:

- `duct_only_48_regularized_limited_boundary_500step_real`
- `duct_only_48_convective_outlet_boundary_500step_real`

Both rows produced simulation-backed artifacts. Neither candidate passed the
hard Step124 candidate gates. The refreshed Step121 summary state is:

```text
campaign_state = 48_candidates_failed
final_classification = boundary_repair_failed_revisit_lbm_solver
best_boundary_selected = false
quasi2d_allowed = false
```

Step127 therefore does not allow selected 96^3 duct execution. The next work
should be boundary-formulation repair grounded in these candidate failures, not
96^3, quasi-2D, FSI, Fluent validation, or Figure 29.3 parity.

## Preflight

Local and live remote refs before the real candidate run:

```text
HEAD = e2be90f89f4b31d9bd8f63d405017fc701c15cc8
origin/main = 1441c5e1a01e7640de350187f96193dc5040656b
```

`HEAD` is the local Step127 goal commit. It was intentionally committed before
the candidate run so each candidate artifact could record a clean
`code_commit_at_run`.

Focused campaign contracts:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step127-preflight `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

Result:

```text
22 passed, 8 warnings in 133.44s
```

Entry-point compile check:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py
```

Result: pass.

## Runtime Commands

Candidates:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase candidates48 `
  --allow-large-real-rows `
  --output-interval 25
```

Summary refresh:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase summary
```

No `--force` was used. No checkpoint restore was used by either candidate row.

## Manifest Provenance

Campaign manifest:

```text
campaign_base_commit = 516b1aaa4c71d5468ce5ea444a21ffa07741c8bc
current_code_commit = e2be90f89f4b31d9bd8f63d405017fc701c15cc8
git_commit = e2be90f89f4b31d9bd8f63d405017fc701c15cc8
phase_history = smoke, references48, candidates48
```

Phase commit history:

```text
smoke -> 516b1aaa4c71d5468ce5ea444a21ffa07741c8bc
references48 -> 6ad3108994c55d1863fc2c2d4a830a26799fc9f4
candidates48 -> e2be90f89f4b31d9bd8f63d405017fc701c15cc8
```

## Candidate Rows

### Limited Regularized Candidate

```text
name = duct_only_48_regularized_limited_boundary_500step_real
semantics = regularized_velocity_pressure_limited
code_commit_at_run = e2be90f89f4b31d9bd8f63d405017fc701c15cc8
solver_state_hash = 5e100a3e77c58a39f17b8eb37a8823f50c8afe0ee482c7752f4c6d3fabaf05bf
run_manifest_hash = 59a937533edb9bdabf87700205b9b7d3072a3844d1010718d9b19510793171e0
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
flow_development_rejection_reasons = flux_imbalance_rel_tail_max, flux_imbalance_rel_tail_mean, midplane_to_inlet_flux_ratio_tail_mean, outlet_flux_tail_cv, outlet_to_inlet_flux_ratio_tail_mean
mass_total_delta_rel_final = 0.002957166349791136
flux_imbalance_rel_tail_mean = 0.5116500063984565
flux_imbalance_rel_tail_max = 0.8660864636023118
outlet_to_inlet_flux_ratio_tail_mean = 1.4127439008448124
midplane_to_inlet_flux_ratio_tail_mean = 1.3061913967849994
outlet_flux_tail_cv = 0.452877609631164
limiter_activation_fraction = 0.0
first_failure_step = null
first_failure_reason = null
runtime_s = 119.18069949999335
restored_checkpoint = null
candidate_pass = false
```

This row did not fail numerically, but it did not improve the open-boundary
flow-development behavior. It closely matches the old regularized reference's
bad outlet/inlet ratio and flux imbalance. The limiter did not activate, so the
failure is not caused by limiter clipping.

### Convective Outlet Candidate

```text
name = duct_only_48_convective_outlet_boundary_500step_real
semantics = convective_pressure_outlet_experimental
code_commit_at_run = e2be90f89f4b31d9bd8f63d405017fc701c15cc8
solver_state_hash = 5d56100e46467c9bfee29a9f3411ebc33436b6b663b664e7eb21ac79714ab075
run_manifest_hash = 243a8a501e8ae4096acca196566eaa4e5bb142c5db60adef7966f84e0478af4d
requested_window_completed = false
steps_completed = 200
simulation_backed_artifact = true
step120_validation_claimed = false
finite_pass = true
density_gate_pass = true
mass_drift_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
flow_development_gate_pass = false
flow_development_rejection_reasons = flux_imbalance_rel_tail_max, flux_imbalance_rel_tail_mean, midplane_to_inlet_flux_ratio_tail_mean, outlet_to_inlet_flux_ratio_tail_mean
mass_total_delta_rel_final = 0.04684463072340483
flux_imbalance_rel_tail_mean = 0.2616703854049617
flux_imbalance_rel_tail_max = 0.2690680105951848
outlet_to_inlet_flux_ratio_tail_mean = 0.7382269660347947
midplane_to_inlet_flux_ratio_tail_mean = 0.7541387863811425
outlet_flux_tail_cv = 0.0038570089621531574
limiter_activation_fraction = 0.0
first_failure_step = 200
first_failure_reason = mass_drift
runtime_s = 37.23936519998824
restored_checkpoint = null
candidate_pass = false
```

This row produced terminal real evidence before the requested 500-step window.
It stopped on `lightweight_failure:mass_drift`, with `first_failure_step = 200`.
It also failed the flow-development ratio and flux-imbalance gates. It is not a
candidate for selected 96^3.

## Reference Baselines

### Legacy Reference

```text
name = duct_only_48_legacy_boundary_500step_reference_real
semantics = equilibrium_all_population_reset
requested_window_completed = true
simulation_backed_artifact = true
flow_development_gate_pass = true
mass_total_delta_rel_final = 0.0007730374927265733
flux_imbalance_rel_tail_mean = 0.04043317017445867
flux_imbalance_rel_tail_max = 0.08607841290325333
outlet_to_inlet_flux_ratio_tail_mean = 0.9595668298255413
midplane_to_inlet_flux_ratio_tail_mean = 0.9556179894908249
outlet_flux_tail_cv = 0.02463282965556423
```

### Old Regularized Reference

```text
name = duct_only_48_regularized_boundary_500step_reference_real
semantics = regularized_velocity_pressure
requested_window_completed = true
simulation_backed_artifact = true
flow_development_gate_pass = false
mass_total_delta_rel_final = 0.002957161603977865
flux_imbalance_rel_tail_mean = 0.5116500495884674
flux_imbalance_rel_tail_max = 0.8660866973898724
outlet_to_inlet_flux_ratio_tail_mean = 1.4127437709040476
midplane_to_inlet_flux_ratio_tail_mean = 1.3061915562381126
outlet_flux_tail_cv = 0.4528776651615377
```

The limited candidate does not materially improve over the failed old
regularized reference. The convective candidate improves the outlet-tail
stationarity and some flux imbalance values, but it fails mass drift, does not
complete the requested window, and remains worse than the passing legacy
reference in key flow-development gates.

## Decision

`step121_best_boundary_selection.json` reports:

```text
reference_comparison_ready = true
campaign_state = 48_candidates_failed
selection_reason = both_real_48_candidates_failed_hard_gates
campaign_should_stop_at_48 = true
best_boundary_selected = false
final_classification = boundary_repair_failed_revisit_lbm_solver
validation_claim_allowed = false
```

Therefore Step127 stops the current 48^3 candidate chain. Step128 selected 96^3
is not allowed.

## Runtime Issues Found

No runner crash, checkpoint corruption, provenance bug, or stale-row selection
bug was found during Step127.

The physical/numerical finding is that the two available candidate formulations
do not satisfy the Step124 hard gates:

- limited regularized: stable but still has severe outlet/inlet flux mismatch
  and tail instability.
- convective outlet: reaches terminal mass-drift evidence before 500 steps.

This points to a boundary formulation repair step rather than more campaign
automation or larger-grid execution.

## Verification

Final entry-point compile check:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py
```

Result: pass.

Final focused campaign contracts:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step127-focused `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

Result:

```text
22 passed, 8 warnings in 118.67s
```

## Claims Not Made

Step127 remains LBM-only candidate execution. It does not claim:

- selected 96^3 duct success.
- selected 96^3 static success.
- quasi-2D validation.
- FSI validation.
- Fluent validation.
- Figure 29.3 parity.

## Next Step

Do not create Step128 selected 96^3 from this state. The next step should be a
boundary-formulation repair goal using the Step127 failure evidence, with
priority on:

- convective outlet mass drift and mass balance closure.
- open-boundary flux ratio and flux imbalance.
- why limited regularized reproduces the old regularized failed-baseline
  behavior despite zero limiter activation.
