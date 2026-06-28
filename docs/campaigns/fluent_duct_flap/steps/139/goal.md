# Step139 Overnight Queue Goal

## Objective

Implement the overnight Step139 queue from the user-provided contract.

The primary work is a single real 48^3 / 500-step final-evidence run for the
exact Step138 passing row:

```text
ramp85 / target0.80 / gain0.75 / cap0.0075
```

This is not selected 96^3 work, not selected-static work, not a Fluent run, and
not a Fluent/FSI/production validation claim.

## Global Constraints

- Do not run selected96.
- Do not run selected-static.
- Do not run 96^3.
- Do not claim quasi-2D validation.
- Do not claim FSI validation.
- Do not claim Fluent validation.
- Do not claim Figure 29.3 parity.
- Do not claim production readiness.
- Do not commit Ansys or Fluent official proprietary files.
- Do not relax Step121 or Step124 hard gates.
- Preserve Step138 artifacts as immutable source evidence.
- If the Step139 long run fails, record the failure and stop parameter work.
- Do not auto-tune parameters.
- Do not run a second Step139 row.
- Keep solver formula changes out of this step unless a test reveals a wiring
  bug that prevents the requested already-existing boundary behavior from
  running.

## Source Of Truth

Read these before implementation:

1. `docs/current/STATUS.md`
2. `docs/current/ACTIVE_CAMPAIGN.json`
3. `docs/current/VALIDATION_GATES.md`
4. `docs/current/READING_ORDER.md`
5. `docs/campaigns/fluent_duct_flap/steps/138/report.md`
6. `experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py`
7. `tests/test_step138_high_authority_outlet_contract.py`

Step138 source row:

```text
duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_out5_250step_high_authority
```

Step138 source provenance that must be carried into Step139 artifacts or
reports where relevant:

```text
source_step = 138
source_row_name = duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_out5_250step_high_authority
source_solver_state_hash = 34437ee966ac063d03d80bd4a9c9dea30961897cbb87d41cc5c7de1571ef3ed8
source_run_manifest_hash = e689ad17b0de0f478d57ef9d419e2ed10579692cfb94866dbc1095b5c7239969
source_code_commit = f0284d3f6207eb1c9341dfc9906293b651c6b0f7
```

## Task 1: Step139 Single 48^3 / 500-Step Final Evidence

Add a bounded Step121 phase:

```text
phase = planeflux_final48
```

The phase must contain exactly one real row:

```text
duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_500step_final
```

Required row parameters:

```text
semantics = regularized_plane_flux_controlled_pressure_outlet
geometry_mode = duct_only
grid = 48^3
n_steps = 500
ramp_steps = 85
target_scale = 0.80
gain_u = 0.75
cap_u = 0.0075
gain_rho = 0.001
alpha = 0.02
delta_cap_u = 0.0005
slew_alpha = 0.50
measure_offset = 2
guard_enabled = true
guard_min_ratio = 0.70
lbm_niu = 0.10
output_interval = 10
row_role = final_evidence_candidate_48
selected96_claim_allowed = false
validation_claim_allowed = false
```

Create or update:

- `tests/test_step139_planeflux_final48_contract.py`
- `experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py`
- Any Step120 reporting surface needed to make Step139 rows visible as Step139
  final evidence, without changing hard gates.
- `docs/campaigns/fluent_duct_flap/steps/139/report.md`
- `outputs/step139_planeflux_final48/planeflux_final48/...`
- `docs/current/ACTIVE_CAMPAIGN.json`
- `docs/current/STATUS.md`
- `docs/current/VALIDATION_GATES.md`
- `docs/current/READING_ORDER.md`

Run command:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_final48 `
  --output-dir outputs\step139_planeflux_final48\planeflux_final48 `
  --allow-large-real-rows `
  --output-interval 10 `
  --force `
  --no-resume
```

Step139 succeeds only if all of the following are true:

```text
steps_completed = 500
requested_window_completed = true
simulation_backed_artifact = true
finite_pass = true
density_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
mass_drift_gate_pass = true
first_failure_step = null
first_failure_reason = null
candidate_mass_acceptance_gate_pass = true
candidate_mass_acceptance_observed_abs < 0.005
flow_development_gate_pass = true
0.80 <= outlet_to_inlet_flux_ratio_tail_mean <= 1.20
0.80 <= midplane_to_inlet_flux_ratio_tail_mean <= 1.20
flux_imbalance_rel_tail_mean < 0.10
flux_imbalance_rel_tail_max < 0.20
outlet_flux_tail_cv < 0.10
collapse_first_x = null
collapse_first_step = null
limiter_activation_fraction <= 0.05
selected96_claim_allowed = false
validation_claim_allowed = false
```

If the row fails any required gate, record that failure honestly. Do not tune
parameters and do not run another row.

## Task 2: Step139 Long-Window Comparison Audit

After the Step139 run completes or fails, create:

- `outputs/step139_planeflux_final48/step139_long_window_comparison.json`
- `outputs/step139_planeflux_final48/step139_long_window_comparison.csv`

The audit must compare the Step138 250-step passing row against the Step139
500-step final row for:

- `mass_abs`
- `outlet_to_inlet_flux_ratio_tail_mean`
- `midplane_to_inlet_flux_ratio_tail_mean`
- `flux_imbalance_rel_tail_mean`
- `flux_imbalance_rel_tail_max`
- `outlet_flux_tail_cv`
- `collapse_first_x`
- `collapse_first_step`
- `controller_authority_ratio_tail_mean`
- `controller_saturation_fraction_tail`
- `limiter_activation_fraction`
- `first_failure_step`
- `runtime_s`

If Step139 passes, report:

```text
Step139 confirms the Step138 250-step passing row survives the 500-step 48^3 final-evidence window.
This supports a later Step140 candidate-surface promotion proposal.
Selected96 remains blocked until a separate explicit step.
```

If Step139 fails, report:

```text
Step139 falsifies the Step138 short-window promotion candidate.
No selected boundary.
No selected96.
Next step should analyze first failure or long-window flow-development drift.
```

## Task 3: Conditional Step140 Promotion Proposal

Run this task only if Step139 completes 500/500 and passes all final hard
gates.

If Step139 fails, skip this task.

If Step139 passes, create a proposal only:

- `docs/campaigns/fluent_duct_flap/steps/140/goal.md`
- `tests/test_step140_planeflux_promotion_contract.py`
- `outputs/step140_planeflux_promotion_readiness/promotion_readiness_report.json`
- `docs/campaigns/fluent_duct_flap/steps/140/report.md`

Required Step140 checks:

```text
source_step = 139
source_row_completed_500 = true
source_flow_development_gate_pass = true
source_candidate_mass_acceptance_gate_pass = true
source_first_failure_step = null
source_collapse_first_x = null
source_selected96_claim_allowed = false
promotion_readiness = true
selected96_execution_allowed = false
next_step_may_update_selection_surface = true
```

Step140 must not:

- Create selected96 specs.
- Call `--phase selected96`.
- Run selected-static.
- Run 96^3.
- Update current state to `selected96_allowed`.
- Claim `best_boundary_selected` unless a later explicit step changes the
  selection surface with dedicated tests.

## Task 4: Conditional Step139 Failure Forensics

Run this task only if Step139 fails any final hard gate or does not complete
500/500.

If Step139 passes, skip this task.

If Step139 fails, create:

- `outputs/step139_planeflux_final48/step139_failure_forensics.json`
- `outputs/step139_planeflux_final48/step139_failure_forensics.md`
- A failure-forensics section in
  `docs/campaigns/fluent_duct_flap/steps/139/report.md`

Classify the first failure into one or more of:

- `first_failure_nonfinite_density_population_mach`
- `mass_acceptance_failed_after_250`
- `flow_ratio_drift`
- `flux_mean_or_max_drift`
- `outlet_cv_drift`
- `compact_collapse_appeared`
- `limiter_correction_or_saturation_artifact`

Forensics must include:

- `first_failed_gate`
- `first_failed_step_if_available`
- `last_good_step_window`
- `tail_metrics_at_250_equivalent_point`
- `tail_metrics_at_500_final`
- `trend_slope`
- `suggested_next_diagnostic`

The suggestion must be report-only. Do not implement a new diagnostic in this
step.

## Task 5: Generic Solver Architecture Contract

Create a lightweight architecture contract that separates solver core,
benchmark adapters, and comparison layers without changing solver physics or
running simulations.

Create:

- `docs/architecture/GENERIC_FSI_SOLVER_CONTRACT.md`
- `docs/architecture/BENCHMARK_ADAPTER_CONTRACT.md`
- `docs/architecture/VALIDATION_CLAIM_BOUNDARY.md`
- `tests/test_step139_generic_solver_architecture_contract.py`

The contract must enforce:

1. `src/mpm_lbm/sim/lbm`, `src/mpm_lbm/sim/mpm`,
   `src/mpm_lbm/sim/coupling`, and `src/mpm_lbm/sim/drivers` are generic.
2. Fluent-specific metadata belongs only in benchmark adapter, config, or
   comparison layers.
3. Solver core must not import Fluent official config, Ansys-specific files, or
   benchmark-specific modules.
4. Benchmark adapters may generate generic `SolverConfig`, `GeometryConfig`,
   `MaterialConfig`, and `MonitorConfig` surfaces.
5. The comparison layer reads outputs only and cannot affect solver runtime.
6. Validation claims remain false unless explicit artifact-backed gates pass.

Recommended directory contract:

```text
src/mpm_lbm/sim/lbm/
src/mpm_lbm/sim/mpm/
src/mpm_lbm/sim/coupling/
src/mpm_lbm/sim/geometry/
src/mpm_lbm/sim/monitors/
src/mpm_lbm/benchmarks/
src/mpm_lbm/comparison/
```

Tests must check:

- Solver core files do not import benchmark or Fluent modules.
- Benchmark adapter files may import solver config schemas.
- Comparison files may read outputs but not solver runtime internals.
- No official Fluent files are committed.
- The architecture docs do not enable selected96, Fluent validation, FSI
  validation, or production-readiness claims.

## Task 6: Fluent Official Local Execution Prep Guard

Create a local-execution preparation contract for official Fluent assets. Do
not run Fluent and do not commit official assets.

Create:

- `docs/campaigns/fluent_duct_flap/fluent_official_local_execution_plan.md`
- `configs/fluent_official_2way_fsi_local_execution_schema.json`
- `configs/fluent_official_monitor_export_schema.json`
- `tests/test_fluent_official_local_execution_guard.py`
- `outputs/fluent_official_local_execution_prep/guard_report.json`

The contract must keep official files local-only under:

```text
benchmarks/private/fluent_fsi_2way/
```

Allowed local-only files:

```text
fsi_2way.zip
flap.msh
steady_fluid_flow.jou
*.cas.h5
*.dat.h5
exported monitor CSV
```

Committed artifacts may include only:

- Local execution manifest without proprietary payload.
- Exported monitor summary if user-generated and policy-safe.
- Schema check report.
- Gap-only comparison readiness report.

Step102 already established that official Fluent files remain private, Step102
did not run Fluent, and Step102 did not commit official files. Preserve that
boundary.

## Task 7: Verification

Use the trusted interpreter:

```text
D:\working\taichi\env\python.exe
```

Compile:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py `
  src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py `
  src\mpm_lbm\sim\lbm\config.py `
  src\mpm_lbm\sim\lbm\fluid.py
```

Step139 / recent focused:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-overnight-step139-focused `
  tests\test_step139_planeflux_final48_contract.py `
  tests\test_step138_high_authority_outlet_contract.py `
  tests\test_step137_ramp_target_refinement_contract.py `
  tests\test_step136_ramped_throughput_calibration_contract.py `
  tests\test_step135_interior_reflection_diagnostics_contract.py `
  tests\test_step134_outlet_stationarity_contract.py `
  tests\test_step133_mass_damped_plane_flux_contract.py `
  tests\test_step132_plane_flux_authority_sweep_contract.py `
  tests\test_step131_plane_flux_controller_contract.py
```

Campaign/provenance:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-overnight-campaign-provenance `
  tests\test_step130_flow_development_diagnostics_contract.py `
  tests\test_step129_repair_checkpoint_counter_contract.py `
  tests\test_step128_boundary_formulation_repair_contract.py `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

Policy guards:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-overnight-policy `
  tests\test_step56_behavior_preservation_contract.py `
  tests\test_step57_step56_regression_contract.py `
  tests\test_step58_step57_regression_contract.py
```

Hygiene:

```powershell
git diff --check
git diff --cached --check
git status --short
```

## Commit And Push Plan

Use targeted commits in this order:

```text
1. docs: add Step139 48 final-evidence goal
2. feat/test: add Step139 planeflux final48 phase
3. test: record Step139 single 48 final-evidence run
4. docs/test: add generic solver architecture contract
5. docs/test: add Fluent official local execution guard
```

If Step139 fails, use this subject for the third commit:

```text
test: record Step139 failed 48 final-evidence run
```

After verification, push to `origin/main` and verify the remote ref.

## Morning Read Order

The first files to inspect after completion are:

1. `docs/campaigns/fluent_duct_flap/steps/139/report.md`
2. `outputs/step139_planeflux_final48/planeflux_final48/*/finite_stability_report.json`
3. `outputs/step139_planeflux_final48/step139_long_window_comparison.json`
4. `docs/current/STATUS.md`
5. `docs/current/VALIDATION_GATES.md`

The key answer is:

```text
Step139 final hard gate pass = true/false
```

If true, a later step may consider promotion-surface work. If false, continue
with failure forensics and do not run selected96.
