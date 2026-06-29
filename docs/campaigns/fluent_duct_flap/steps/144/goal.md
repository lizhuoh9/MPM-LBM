# Step144 Mass-Neutral Plane-Flux Final48 Probe Goal

## Source State

This goal starts from `origin/main = 618cf188827e0b9538e5279e8ab042fabd92a0b2`.
Step143 produced a bounded four-row `48^3 / 250` LBM-only mass-neutral diagnostic
phase and the audit decision:

```text
decision_case = mass_neutral_design_supports_step144_single_500step_probe
step144_single_500step_probe_proposal_allowed = true
step144_selected96_execution_allowed = false
selected96_execution_allowed = false
validation_claim_allowed = false
```

Step144 is allowed to run exactly one `48^3 / 500-step` final-evidence probe
using the exact Step143 best enabled row setting. Step144 is not allowed to run
selected96, selected-static, `96^3`, Fluent, FSI, quasi-2D validation, Figure
29.3 parity, or production-readiness validation.

## Goal Statement

Implement Step144 as a single real LBM-only long-window evidence probe:

```text
Step144 Mass-Neutral Plane-Flux Final48 Probe
phase = planeflux_mass_neutral_final48
row_role = mass_neutral_final_evidence_candidate_48
grid = 48^3
n_steps = 500
output_interval = 10
semantics = regularized_plane_flux_controlled_pressure_outlet
row_count = exactly 1
```

The scientific question is narrow:

```text
Can the Step143 high mass-neutral setting, which improved 250-step mass and flow
diagnostics, survive a single 500-step long-window final-evidence probe?
```

Even a passing Step144 result only supports a later Step145 proposal for selected
candidate-surface review. Step144 must not directly select a boundary, run
selected96, or make a validation claim.

## Hard Boundaries

Step144 must preserve all of these boundaries:

- exactly one real row
- `48^3` only
- `500` steps only
- `output_interval = 10`
- LBM-only
- duct-only geometry
- no selected96
- no selected-static
- no `96^3`
- no Fluent
- no FSI
- no validation claim
- no gate relaxation
- no second row
- no tuning during Step144
- no selected-candidate semantics activation
- no production-readiness claim

The exact required documentation strings must appear in the Step144 goal,
Step144 report, and current gate/status docs:

```text
Step144 did not run selected96
Step144 did not run selected-static
Step144 did not run 96^3
Step144 ran exactly one 48^3 / 500-step LBM-only row
Step144 did not run Fluent
Step144 did not run FSI
Step144 does not make a validation claim
Step144 keeps selected96 blocked
```

## Exact Row Parameters

The single Step144 row must use the Step143 best enabled high setting exactly:

```text
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

open_boundary_mass_neutral_flux_control_enabled = true
open_boundary_mass_neutral_flux_control_mode = global_mass_error_density_offset
open_boundary_mass_neutral_mass_error_gain = 0.50
open_boundary_mass_neutral_mass_error_cap = 0.00100
open_boundary_mass_neutral_correction_blend = 1.0
open_boundary_mass_neutral_reference_mass_mode = initial
```

The required row name is:

```text
duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010_mnhigh_mgain0p50_mcap0p001_blend1p00_out10_500step_mass_neutral_final
```

## Provenance Requirements

Step144 must derive from committed Step143 artifacts, not from a new ad hoc
search for the best row. The implementation must read or directly reference:

```text
outputs/step143_mass_neutral_design_diagnostic/step143_decision_summary.json
outputs/step143_mass_neutral_design_diagnostic/step143_mass_neutral_comparison.json
```

The Step144 row, run summary, metadata, manifest expected row, and audit outputs
must preserve these provenance fields:

```text
source_step = 143
source_step143_decision_hash
source_step143_comparison_hash
source_step143_best_row_name
source_step143_best_row_solver_state_hash
source_step143_best_row_run_manifest_hash
source_step143_best_row_mass_neutral_activation_hash
source_step143_decision_case = mass_neutral_design_supports_step144_single_500step_probe
```

The campaign manifest must reject stale row artifacts when any of the Step143
decision/comparison provenance hashes or the mass-neutral activation hash do not
match the current Step144 spec.

## Code Changes

Add:

```text
tests/test_step144_mass_neutral_final48_contract.py
experiments/steps/step144_mass_neutral_final48_audit.py
docs/campaigns/fluent_duct_flap/steps/144/report.md
outputs/step144_mass_neutral_final48/mass_neutral_final48/...
outputs/step144_mass_neutral_final48/step144_long_window_comparison.json
outputs/step144_mass_neutral_final48/step144_long_window_comparison.csv
outputs/step144_mass_neutral_final48/step144_decision_summary.json
```

Modify:

```text
experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py
experiments/steps/step120_lbm_boundary_repair_large_real_execution.py
docs/current/ACTIVE_CAMPAIGN.json
docs/current/STATUS.md
docs/current/VALIDATION_GATES.md
docs/current/READING_ORDER.md
README.md
```

Do not edit `src/mpm_lbm/sim/lbm/fluid.py` unless a reporting field gap is found
that cannot be solved in Step120/Step121/audit surfaces. Step144 should use the
Step143 runtime formula unchanged.

## Step121 Phase Contract

Add constants:

```text
STEP144_MASS_NEUTRAL_FINAL_PHASE = "planeflux_mass_neutral_final48"
STEP144_MASS_NEUTRAL_FINAL_ROLE = "mass_neutral_final_evidence_candidate_48"
```

Add:

```python
step121_mass_neutral_final_48_specs(output_interval: int = 10) -> List[Step120RunSpec]
```

The function must return exactly one `Step120RunSpec` and must:

- use the exact Step143 best high setting
- set `n_steps = requested_n_steps = 500`
- set `output_interval = 10`
- set `row_role = mass_neutral_final_evidence_candidate_48`
- set `source_step = 143`
- set `allow_large_real_run_without_flag = True`
- set `not_used_for_validation = True`
- keep the role out of `SELECTED_CHAIN_ROLES`
- keep the regularized plane-flux semantics out of selected candidate sets
- preserve `selected96_claim_allowed = false` and `validation_claim_allowed = false`

`resolve_step121_phase_specs("planeflux_mass_neutral_final48", output_interval=10)`
must return this exact one-row spec.

## Step144 Success Gate

The Step144 audit may return `mass_neutral_final48_probe_passed` only when all
of the following are true:

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

The audit must report, but not hard-gate on, these Step144 monitoring fields:

```text
mass_neutral_feedback_saturation_fraction_tail
mass_neutral_rho_feedback_tail_mean
mass_neutral_mass_error_tail_mean
mass_neutral_mass_error_final
controller_authority_ratio_tail_mean
controller_saturation_fraction_tail
drop_guard_activation_fraction_tail
```

Because Step143's best row had high mass-neutral feedback saturation in the tail,
the Step144 report must explicitly discuss whether the 500-step tail still
spends substantial time at the mass-neutral cap.

## Step144 Audit Contract

Add:

```text
experiments/steps/step144_mass_neutral_final48_audit.py
```

Inputs:

```text
outputs/step143_mass_neutral_design_diagnostic/step143_decision_summary.json
outputs/step143_mass_neutral_design_diagnostic/step143_mass_neutral_comparison.json
outputs/step144_mass_neutral_final48/mass_neutral_final48/.../finite_stability_report.json
outputs/step144_mass_neutral_final48/mass_neutral_final48/.../flow_development_diagnostics_summary.json
```

Outputs:

```text
outputs/step144_mass_neutral_final48/step144_long_window_comparison.json
outputs/step144_mass_neutral_final48/step144_long_window_comparison.csv
outputs/step144_mass_neutral_final48/step144_decision_summary.json
```

Decision cases:

```text
mass_neutral_final48_probe_passed
mass_neutral_mass_long_window_failure
mass_neutral_flow_stationarity_long_window_failure
mass_neutral_design_unstable_long_window
missing_input
```

If the probe passes all hard gates, the only allowed next-step recommendation is
for Step145 selected-candidate-surface review proposal. `selected96` remains
blocked in every Step144 decision case.

## Contract Tests

Add `tests/test_step144_mass_neutral_final48_contract.py` covering at least:

1. phase resolves exactly one row
2. row is `48^3 / 500-step / output_interval 10`
3. row uses exact Step143 best setting: gain `0.50`, cap `0.00100`, blend `1.0`, mode `global_mass_error_density_offset`
4. row role is `mass_neutral_final_evidence_candidate_48`
5. role is not in `SELECTED_CHAIN_ROLES`
6. semantics are not in `CANDIDATE_SEMANTICS` or `REPAIRED_CANDIDATE_SEMANTICS`
7. `source_step = 143` and Step143 decision/comparison hashes are recorded
8. `source_step143_best_row_name` matches Step143 decision summary
9. `source_step143_best_row_mass_neutral_activation_hash` matches the Step143 comparison best row
10. manifest rejects stale rows with wrong Step143 decision hash
11. manifest rejects stale rows with wrong mass-neutral activation hash
12. Step144 rows cannot enable selected96 even if mocked final gates pass
13. audit only allows Step145 proposal if full 500-step hard gates pass
14. audit missing inputs produce `missing_input`, not a synthesized decision
15. docs/report/current gates contain the required no-selected96/no-validation statements

## Required Commands

RED contract:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step144-red `
  tests\test_step144_mass_neutral_final48_contract.py
```

Pre-run focused verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\lbm\fluid.py `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py `
  experiments\steps\step144_mass_neutral_final48_audit.py `
  tests\test_step144_mass_neutral_final48_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step144-focused-pre `
  tests\test_step144_mass_neutral_final48_contract.py `
  tests\test_step143_mass_neutral_design_contract.py `
  tests\test_step142_mass_neutral_plane_flux_design_contract.py
```

Real Step144 phase:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_mass_neutral_final48 `
  --output-dir outputs\step144_mass_neutral_final48\mass_neutral_final48 `
  --allow-large-real-rows `
  --output-interval 10 `
  --force `
  --no-resume
```

Audit:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step144_mass_neutral_final48_audit `
  --phase-root outputs\step144_mass_neutral_final48\mass_neutral_final48 `
  --step143-decision outputs\step143_mass_neutral_design_diagnostic\step143_decision_summary.json `
  --step143-comparison outputs\step143_mass_neutral_design_diagnostic\step143_mass_neutral_comparison.json `
  --output-dir outputs\step144_mass_neutral_final48 `
  --force
```

Final focused verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step144-focused-final `
  tests\test_step144_mass_neutral_final48_contract.py `
  tests\test_step143_mass_neutral_design_contract.py `
  tests\test_step142_mass_neutral_plane_flux_design_contract.py `
  tests\test_step141_density_feedback_isolation_contract.py `
  tests\test_step140_long_window_drift_forensics_contract.py

& 'D:\working\taichi\env\python.exe' -c "<json load check for Step144 artifacts and current docs>"

git diff --check
```

## Completion Criteria

Step144 is complete only when:

- the detailed goal file exists and the active goal references it
- the RED Step144 contract test failed before implementation
- Step144 code, audit, docs, current campaign docs, and real artifacts are implemented
- the single real `48^3 / 500-step` row has run
- Step144 audit outputs exist and are JSON/CSV loadable
- focused Step140-Step144 regression passes
- `git diff --check` passes
- changes are committed and pushed to `origin/main`
- the final remote ref is verified against local `HEAD`

