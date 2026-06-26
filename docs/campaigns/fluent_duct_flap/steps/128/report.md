# Step128 LBM Open-Boundary Formulation Repair Report

## Summary

Step128 implemented the first boundary-formulation repair surface after the
Step127 48^3 candidate failure.

This step did not run selected 96^3, quasi-2D, FSI, Fluent validation, or
Figure 29.3 parity. It also did not claim that a repaired 48^3 candidate has
passed the hard gates. The campaign remains blocked at the Step127 state until
a repaired 48^3 candidate produces real 500-step passing evidence.

Current campaign state remains:

```text
state = 48_candidates_failed
final_classification = boundary_repair_failed_revisit_lbm_solver
best_boundary_selected = false
selected96_allowed = false
```

## Code Changes

### New Open-Boundary Semantics

Added two new LBM open-boundary semantics:

```text
regularized_mass_balanced_pressure_outlet
convective_mass_balanced_pressure_outlet
```

They are registered in `LBMConfig` and dispatched by `LBMFluid3D` without
changing the existing Step127 semantics:

```text
equilibrium_all_population_reset
regularized_velocity_pressure
regularized_velocity_pressure_limited
convective_pressure_outlet_experimental
```

The new kernels apply bounded local mass/throughput feedback only to x-max
unknown populations. They preserve the old kernels so Step127 artifacts remain
reproducible.

### Repair Counters

Added repair counters to the open-boundary diagnostics:

```text
mass_balance_correction_count
mass_balance_correction_abs_sum
unknown_population_delta_abs_sum
```

These are surfaced through Step120 row summaries so later Step128 runs can
audit whether a candidate is passing through a real bounded correction or
through unrelated limiter clipping.

### Hard-Stop Mass Drift Telemetry

Added explicit hard-stop fields to Step120 reports:

```text
hard_stop_failure_reason
hard_stop_failure_step
hard_stop_mass_drift_abs_max
hard_stop_mass_drift_observed_abs
hard_stop_mass_drift_gate_pass
candidate_mass_acceptance_abs_max
candidate_mass_acceptance_observed_abs
candidate_mass_acceptance_gate_pass
```

This keeps the Step120 lightweight hard-stop threshold separate from the
Step121 candidate mass acceptance threshold. A row can no longer look
ambiguous when it stops on `lightweight_failure:mass_drift` while an older
summary-level `mass_drift_gate_pass` remains true.

### Step121 Repair Phase

Added a distinct Step121 phase:

```text
repair48
```

`repair48` resolves only the new `repair_candidate_48` specs:

```text
duct_only_48_regularized_mass_balanced_pressure_outlet_500step_real
duct_only_48_convective_mass_balanced_pressure_outlet_500step_real
```

The old `candidates48` phase still resolves only the Step127 candidates:

```text
duct_only_48_regularized_limited_boundary_500step_real
duct_only_48_convective_outlet_boundary_500step_real
```

This prevents Step128 from silently redefining Step127.

## Test Coverage

Added:

```text
tests/test_step128_boundary_formulation_repair_contract.py
```

Coverage includes:

- New semantics are valid `LBMConfig` values.
- New semantics dispatch to distinct Step128 kernels.
- `repair48` is separate from Step127 `candidates48`.
- Solver-state hashes separate repaired semantics from old semantics.
- Two 4x3x3 / 1-step real Taichi smoke rows run through the new kernels.
- Step120 hard-stop mass-drift telemetry is explicit.
- Step120 summary rows expose hard-stop and candidate mass-acceptance fields.
- Repaired candidates can be selected only when old Step127 terminal evidence
  exists and the repaired row passes hard gates.
- Repaired candidates still fail on first-failure, mass, and flow-ratio gates.
- Stale Step127 artifacts cannot be reused as Step128 repaired rows.

## Verification

Compile check:

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

Step128 focused contract:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step128-green-2 `
  tests\test_step128_boundary_formulation_repair_contract.py
```

Result:

```text
12 passed, 8 warnings in 147.30s
```

Warnings are the existing Taichi 19x19 matrix-size warnings emitted during LBM
initialization. They are not Step128 failures.

Final focused campaign verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step128-final-focused `
  tests\test_step128_boundary_formulation_repair_contract.py `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

Result:

```text
34 passed, 16 warnings in 135.84s
```

The same Taichi 19x19 matrix-size warning appears in the tiny real LBM smoke
tests and the existing Step123 real runner test.

## Real 48^3 Status

No Step128 repaired 48^3 / 500-step acceptance run was executed in this code
patch.

The new `repair48` phase is now available for a later real run:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase repair48 `
  --allow-large-real-rows `
  --output-interval 25
```

After that real run, summary must still enforce the Step124/Step121 gates. A
future selected 96^3 goal is allowed only if a repaired 48^3 candidate passes
those gates.

## Claims Not Made

Step128 does not claim:

- selected 96^3 duct success.
- selected 96^3 static success.
- quasi-2D validation.
- FSI validation.
- Fluent validation.
- Figure 29.3 parity.
- repaired 48^3 candidate acceptance.
