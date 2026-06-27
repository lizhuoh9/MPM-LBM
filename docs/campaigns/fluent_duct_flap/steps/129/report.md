# Step129 Repair48 Real 48^3 Candidate Campaign Report

## Summary

Step129 ran the real Step121 `repair48` campaign for both Step128 repaired
48^3 / 500-step LBM-only candidates.

Both repaired candidates produced simulation-backed terminal 500-step evidence,
but neither passed the existing Step124/Step121 flow-development hard gates.
No boundary is selected, and selected 96^3 remains blocked.

Current campaign state:

```text
state = 48_candidates_failed
final_classification = boundary_repair_failed_revisit_lbm_solver
best_boundary_selected = false
selected96_allowed = false
validation_claim_allowed = false
```

Step129 did not run selected 96^3, quasi-2D, FSI, Fluent validation, or Figure
29.3 parity.

## Baseline

Step129 started from the accepted Step128 surface:

```text
51ce57b3bf6ab02985556ea6a800e5581eb6a7c1
fix/test: add Step128 boundary formulation repair surface
```

Step129 then added the detailed goal and repair-counter checkpoint persistence
patch before the real `repair48` run:

```text
95f0985 docs: add Step129 repair48 real-run goal
25b03a2 fix/test: persist Step129 repair counters across checkpoints
```

The real repaired rows were executed from runtime commit:

```text
25b03a22d1b1345b01888fe6a54102c4dd54a3be
```

At the preflight check before the real run, local `main` was clean at
`25b03a22d1b1345b01888fe6a54102c4dd54a3be`. `origin/main` still pointed to
Step128 `51ce57b3bf6ab02985556ea6a800e5581eb6a7c1` because Step129 commits were
kept local until final verification and push.

## Checkpoint Counter Patch

Step129 patched repaired-boundary counter persistence before running the real
campaign.

Checkpoint metadata now stores:

```text
mass_balance_correction_count
mass_balance_correction_abs_sum
unknown_population_delta_abs_sum
```

Checkpoint restore now restores those repaired counters through a dedicated
`LBMFluid3D.set_open_boundary_repair_run_counters(...)` API after restoring the
legacy limiter counters. This keeps existing checkpoint behavior compatible
while preventing Step128/Step129 repaired counter telemetry from restarting at
zero after resume.

Added test:

```text
tests/test_step129_repair_checkpoint_counter_contract.py
```

## Preflight Verification

Compile:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\lbm\config.py `
  src\mpm_lbm\sim\lbm\fluid.py `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py
```

Result:

```text
pass
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step129-preflight `
  tests\test_step129_repair_checkpoint_counter_contract.py `
  tests\test_step128_boundary_formulation_repair_contract.py `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

Result:

```text
36 passed, 16 warnings in 211.48s
```

Warnings were the existing Taichi 19x19 matrix-size warnings during tiny real
LBM initialization.

Final post-run focused regression after refreshing current campaign docs:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step129-final-focused `
  tests\test_step129_repair_checkpoint_counter_contract.py `
  tests\test_step128_boundary_formulation_repair_contract.py `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

Result:

```text
36 passed, 16 warnings in 183.27s
```

## Commands Run

Real `repair48` run:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase repair48 `
  --allow-large-real-rows `
  --output-interval 25
```

Summary refresh:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase summary
```

The run did not use `--force`. Existing Step127 artifacts were preserved.

## Manifest Evidence

Artifact root:

```text
outputs/step121_lbm_boundary_real_campaign_and_gate_correction
```

Manifest phase history:

```text
smoke
references48
candidates48
repair48
```

Manifest phase commit history:

```text
smoke        -> 516b1aaa4c71d5468ce5ea444a21ffa07741c8bc
references48 -> 6ad3108994c55d1863fc2c2d4a830a26799fc9f4
candidates48 -> e2be90f89f4b31d9bd8f63d405017fc701c15cc8
repair48     -> 25b03a22d1b1345b01888fe6a54102c4dd54a3be
```

`step121_summary.json` was refreshed with:

```text
phase = summary
row_count = 7
campaign_state = 48_candidates_failed
final_classification = boundary_repair_failed_revisit_lbm_solver
quasi2d_allowed = false
validation_claim_allowed = false
```

## Repaired Candidate Results

### Regularized Mass-Balanced Pressure Outlet

Row:

```text
duct_only_48_regularized_mass_balanced_pressure_outlet_500step_real
```

Identity:

```text
row_role = repair_candidate_48
semantics = regularized_mass_balanced_pressure_outlet
code_commit_at_run = 25b03a22d1b1345b01888fe6a54102c4dd54a3be
solver_state_hash = d8c34da71896a454208d6d4beab27a6adc93901049e7933de26af642eec5792d
run_manifest_hash = 11691fb4abef3e4e39ebabe20f6d0bf962522189d7bcb80fbe66e6b7a0074b53
restored_checkpoint = null
runtime_s = 127.82917480001925
```

Stability and acceptance fields:

```text
requested_window_completed = true
steps_completed = 500
simulation_backed_artifact = true
step120_validation_claimed = true
finite_pass = true
density_gate_pass = true
mass_drift_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
first_failure_step = null
first_failure_reason = null
hard_stop_failure_reason = null
hard_stop_failure_step = null
hard_stop_mass_drift_gate_pass = true
candidate_mass_acceptance_gate_pass = true
mass_total_delta_rel_final = 0.0019035086161313225
```

Flow-development fields:

```text
flow_development_gate_pass = false
flux_imbalance_rel_tail_mean = 0.3722224827902342
flux_imbalance_rel_tail_max = 0.5721747900550053
outlet_to_inlet_flux_ratio_tail_mean = 1.264735695477319
midplane_to_inlet_flux_ratio_tail_mean = 1.2098449625412
outlet_flux_tail_cv = 0.33003290861468526
```

Rejection reasons:

```text
flux_imbalance_gate
flux_imbalance_rel_tail_max
flux_imbalance_rel_tail_mean
flux_worse_than_legacy
midplane_to_inlet_flux_ratio_tail_mean
outlet_flux_tail_cv
outlet_to_inlet_flux_ratio_tail_mean
```

Repair/limiter counters:

```text
mass_balance_correction_count = 5290000
mass_balance_correction_abs_sum = 4014.11865234375
unknown_population_delta_abs_sum = 356.963623046875
limiter_activation_fraction = 0.0
```

Decision: failed hard gates. It is terminal real evidence, but not selectable.

### Convective Mass-Balanced Pressure Outlet

Row:

```text
duct_only_48_convective_mass_balanced_pressure_outlet_500step_real
```

Identity:

```text
row_role = repair_candidate_48
semantics = convective_mass_balanced_pressure_outlet
code_commit_at_run = 25b03a22d1b1345b01888fe6a54102c4dd54a3be
solver_state_hash = a4f3f1e947ece670e78cff0dfb5df74aae0f54089adcdd7b8c31092066f45ada
run_manifest_hash = 7f54f028cf709f740c1c99a7c7fcebdae7be451278223e5dfa6a0a2dfe9a2d43
restored_checkpoint = null
runtime_s = 52.37323039997136
```

Stability and acceptance fields:

```text
requested_window_completed = true
steps_completed = 500
simulation_backed_artifact = true
step120_validation_claimed = true
finite_pass = true
density_gate_pass = true
mass_drift_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
first_failure_step = null
first_failure_reason = null
hard_stop_failure_reason = null
hard_stop_failure_step = null
hard_stop_mass_drift_gate_pass = true
candidate_mass_acceptance_gate_pass = true
mass_total_delta_rel_final = -0.0011874128939383197
```

Flow-development fields:

```text
flow_development_gate_pass = false
flux_imbalance_rel_tail_mean = 0.40325868347534677
flux_imbalance_rel_tail_max = 0.5735062556642948
outlet_to_inlet_flux_ratio_tail_mean = 1.2722701740330669
midplane_to_inlet_flux_ratio_tail_mean = 1.2671693838169262
outlet_flux_tail_cv = 0.5513854681310228
```

Rejection reasons:

```text
flux_imbalance_gate
flux_imbalance_rel_tail_max
flux_imbalance_rel_tail_mean
flux_worse_than_legacy
midplane_to_inlet_flux_ratio_tail_mean
outlet_flux_tail_cv
outlet_to_inlet_flux_ratio_tail_mean
```

Repair/limiter counters:

```text
mass_balance_correction_count = 10580000
mass_balance_correction_abs_sum = 5227.38232421875
unknown_population_delta_abs_sum = 630.7147827148438
limiter_activation_fraction = 0.0
```

Decision: failed hard gates. It is terminal real evidence, but not selectable.

## Selection Decision

Step121 selection output:

```text
best_boundary_selected = false
campaign_should_stop_at_48 = true
campaign_state = 48_candidates_failed
final_classification = boundary_repair_failed_revisit_lbm_solver
reference_comparison_ready = true
selection_reason = both_real_48_candidates_failed_hard_gates
validation_claim_allowed = false
```

Both repaired candidates completed 500 steps and passed finite, density, mass,
population, mach, first-failure, and candidate-mass-acceptance checks. They
failed the shared flow-development hard gates by over-delivering outlet and
midplane flux and by producing high tail imbalance/stationarity error.

Therefore Step129 outcome is Outcome A from the goal:

```text
campaign_state = 48_candidates_failed
final_classification = boundary_repair_failed_revisit_lbm_solver
best_boundary_selected = false
selected96_allowed = false
```

## Claims Not Made

Step129 does not claim:

- selected 96^3 duct success.
- selected 96^3 static success.
- quasi-2D validation.
- FSI validation.
- Fluent validation.
- Figure 29.3 parity.
- repaired 48^3 candidate acceptance.

## Next Technical Direction

The Step128 mass-balanced repair surface improved stability enough for the old
convective-like repaired candidate to complete 500/500 steps, but both repaired
rows still fail flow-development gates. The next step should be another
boundary-formulation repair iteration focused on outlet/midplane flux balance
and tail stationarity, not selected 96^3.
