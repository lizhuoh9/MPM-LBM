# Step143 Mass-Neutral Design 48^3 / 250-Step Diagnostic Goal

## Objective

Implement Step143 as the first bounded activation of the Step142
mass-neutral plane-flux controller design. Step143 must first harden the
activated mass-neutral parameter identity surface, then run at most four real
48^3 / 250-step LBM-only diagnostic rows for `global_mass_error_density_offset`.

The core question is:

```text
Can global_mass_error_density_offset reduce mass-bias risk in the 48^3 /
250-step diagnostic window without damaging flow-development gates, outlet CV,
compact-collapse state, or numerical stability?
```

Step143 is not selected-candidate evidence, not 500-step final evidence, not
selected96, not selected-static, not 96^3, not Fluent, not FSI, and not a
validation step. Step143 may only decide whether Step144 is allowed to propose
one 48^3 / 500-step final-evidence row for the exact best Step143 setting.

## Source Evidence

Step143 starts from:

```text
origin/main = e792735d5572bb11716aca4a8249eccba3bb36d7
source Step142 artifact = outputs/step142_mass_neutral_plane_flux_design/step142_design_readiness_report.json
source Step142 status = design_ready
source Step142 recommended next phase = planeflux_mass_neutral_design48
source Step142 recommended design = global_mass_error_density_offset
source Step142 selected96_execution_allowed = false
source Step142 validation_claim_allowed = false
```

Step141 remains the runtime evidence source behind Step142:

```text
decision_case = density_feedback_isolation_insufficient
best_gain_rho = 0.001
row_count = 4
step142_single_500step_final_evidence_proposal_allowed = false
selected96_execution_allowed = false
validation_claim_allowed = false
```

Step142 correctly introduced default-disabled mass-neutral config/report fields
and no runtime activation. Step143 is allowed to activate Design A only inside
the bounded real diagnostic envelope specified here.

## Step142 Reconciliation Required First

Before adding Step143 runtime phase support, fix the two Step142 goal/document
drifts found during review:

1. `docs/campaigns/fluent_duct_flap/steps/142/goal.md` must list only
   `initial` as the allowed `open_boundary_mass_neutral_reference_mass_mode`,
   matching the actual `LBMConfig` implementation and tests.
2. `docs/campaigns/fluent_duct_flap/steps/142/goal.md` must use the committed
   artifact filenames:

```text
outputs/step142_mass_neutral_plane_flux_design/step142_design_readiness_report.json
outputs/step142_mass_neutral_plane_flux_design/step142_design_readiness_report.md
```

Do not extend runtime behavior just to satisfy the stale `runtime_initial`
wording. Keep the implementation on `initial` only unless a later step
explicitly expands it.

## Hard Scope Boundary

Allowed:

```text
add Step143 goal/report/docs
add activated mass-neutral identity hashing and manifest rejection checks
add Step121 phase planeflux_mass_neutral_design48
add at most four 48^3 / 250-step LBM-only diagnostic rows
activate only global_mass_error_density_offset for Step143 rows
add mass-neutral telemetry to finite summary and flow diagnostics
add a Step143 audit over completed Step143 rows
update current docs and README
commit generated Step143 JSON/CSV/MD artifacts
```

Forbidden:

```text
no selected96
no selected-static
no 96^3
no 500-step run
no Fluent run
no FSI run
no quasi-2D validation
no Fluent validation
no Figure 29.3 parity claim
no production-readiness claim
no selected-boundary claim
no adding plane-flux semantics to CANDIDATE_SEMANTICS
no adding mass_neutral_design_diagnostic_48 to SELECTED_CHAIN_ROLES
no relaxing Step121/Step124 hard gates
no Step143 direct approval of selected96
no Step143 direct approval of validation
```

## Activated Identity Requirement

Step142 intentionally kept the new mass-neutral fields out of
`SOLVER_STATE_HASH_FIELDS` to avoid retroactively changing old Step139-Step142
hashes. Step143 must preserve that historical compatibility and add a separate
activated identity surface:

```text
mass_neutral_activation_hash
```

The hash payload must include:

```text
open_boundary_mass_neutral_flux_control_enabled
open_boundary_mass_neutral_flux_control_mode
open_boundary_mass_neutral_mass_error_gain
open_boundary_mass_neutral_mass_error_cap
open_boundary_mass_neutral_correction_blend
open_boundary_mass_neutral_reference_mass_mode
```

Required behavior:

```text
mass_neutral_activation_hash differs across the four Step143 specs
summary_row includes mass_neutral_activation_hash
metadata includes mass_neutral_activation_hash
boundary_report includes mass_neutral_activation_hash
flow diagnostics include mass_neutral_activation_hash
Step121 campaign manifest expected_rows include mass-neutral fields and hash
Step121 manifest stale-artifact rejection checks mass-neutral fields and hash
old solver_state_hash behavior remains stable for earlier committed rows
```

Do not add these fields directly into `SOLVER_STATE_HASH_FIELDS` in Step143.

## Runtime Implementation Requirement

Implement opt-in mass-neutral density feedback inside `LBMFluid3D` for:

```text
open_boundary_mass_neutral_flux_control_enabled = true
open_boundary_mass_neutral_flux_control_mode = global_mass_error_density_offset
```

Disabled behavior must stay equivalent to Step142/current behavior:

```text
enabled = false
mode = disabled
gain = 0
cap = 0
blend = 0
rho_mass_feedback = 0
mass_neutral_runtime_behavior_active = false
```

Activated formula:

```text
mass_error = (mass_total_current - mass_initial_reference) / mass_initial_reference
rho_mass_feedback_raw = -gain_mass * mass_error
rho_mass_feedback_bounded = clamp(rho_mass_feedback_raw, -cap_mass, cap_mass)
rho_mass_feedback = correction_blend * rho_mass_feedback_bounded
repaired_rho = target_rho + existing_density_feedback + rho_mass_feedback
```

Use `initial` reference mode only:

```text
first mass-neutral update records mass_initial_reference
later updates reuse that reference
```

Implementation guidance:

```text
add Taichi scalar fields for mass-neutral mass/current/error/feedback counters
reset step counters in the existing open-boundary per-step counter reset path
initialize run fields in the existing run-counter reset path
compute mass-neutral feedback in update_open_boundary_plane_flux_controller()
apply feedback only in _regularized_plane_flux_controlled_population()
keep convective and non-plane-flux semantics unchanged
```

Required telemetry:

```text
mass_neutral_runtime_behavior_active
mass_neutral_mass_current
mass_neutral_mass_initial_reference
mass_neutral_mass_error
mass_neutral_rho_feedback
mass_neutral_rho_feedback_abs
mass_neutral_feedback_saturation_count_step
mass_neutral_feedback_saturation_count_run
mass_neutral_feedback_update_count_step
mass_neutral_feedback_update_count_run
mass_neutral_feedback_saturation_fraction_run
mass_neutral_activation_hash
```

Flow-development diagnostics and summary artifacts must expose tail metrics:

```text
mass_neutral_rho_feedback_tail_mean
mass_neutral_rho_feedback_abs_tail_mean
mass_neutral_mass_error_tail_mean
mass_neutral_feedback_saturation_fraction_tail
```

## Step143 Phase And Rows

Add the Step121 phase:

```text
phase = planeflux_mass_neutral_design48
row_role = mass_neutral_design_diagnostic_48
```

The phase resolves exactly four specs:

```text
grid = 48^3
n_steps = 250
output_interval = 5
semantics = regularized_plane_flux_controlled_pressure_outlet
geometry_mode = duct_only
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
source_step = 142
source_step142_readiness_hash = sha256(outputs/step142_mass_neutral_plane_flux_design/step142_design_readiness_report.json)
```

Rows:

```text
baseline_disabled:
  enabled = false
  mode = disabled
  gain_mass = 0.0
  cap_mass = 0.0
  blend = 0.0

mass_neutral_low:
  enabled = true
  mode = global_mass_error_density_offset
  gain_mass = 0.10
  cap_mass = 0.00025
  blend = 1.0

mass_neutral_mid:
  enabled = true
  mode = global_mass_error_density_offset
  gain_mass = 0.25
  cap_mass = 0.00050
  blend = 1.0

mass_neutral_high:
  enabled = true
  mode = global_mass_error_density_offset
  gain_mass = 0.50
  cap_mass = 0.00100
  blend = 1.0
```

Suggested row names:

```text
duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010_mn_disabled_ramp85_target0p80_out5_250step_mass_neutral_design
duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010_mn_gain0p10_mcap0p00025_blend1p00_ramp85_target0p80_out5_250step_mass_neutral_design
duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010_mn_gain0p25_mcap0p00050_blend1p00_ramp85_target0p80_out5_250step_mass_neutral_design
duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010_mn_gain0p50_mcap0p00100_blend1p00_ramp85_target0p80_out5_250step_mass_neutral_design
```

Every row must keep:

```text
selected96_claim_allowed = false
validation_claim_allowed = false
fluent_validation_claim_allowed = false
fsi_validation_claim_allowed = false
quasi2d_validation_claim_allowed = false
production_readiness_claim_allowed = false
```

## Step143 Audit

Add:

```text
experiments/steps/step143_mass_neutral_design_audit.py
```

Input:

```text
phase_root = outputs/step143_mass_neutral_design_diagnostic/mass_neutral_design48
step142_readiness = outputs/step142_mass_neutral_plane_flux_design/step142_design_readiness_report.json
```

Outputs:

```text
outputs/step143_mass_neutral_design_diagnostic/step143_mass_neutral_comparison.json
outputs/step143_mass_neutral_design_diagnostic/step143_mass_neutral_comparison.csv
outputs/step143_mass_neutral_design_diagnostic/step143_decision_summary.json
```

Comparison sort order:

```text
candidate_mass_acceptance_observed_abs
outlet_flux_tail_cv
flux_imbalance_rel_tail_mean
abs(outlet_to_inlet_flux_ratio_tail_mean - 1.0)
abs(mass_neutral_rho_feedback_tail_mean)
controller_saturation_fraction_tail
```

Decision cases:

```text
mass_neutral_design_supports_step144_single_500step_probe:
  best enabled row improves mass_abs over disabled baseline
  and best enabled row passes flow_development_gate
  and best enabled row improves outlet_flux_tail_cv over disabled baseline
  and no first_failure/collapse
  => Step144 may propose one exact-setting 48^3 / 500-step final-evidence row.

mass_neutral_reduces_mass_but_damages_flow:
  enabled rows improve mass but fail flow/CV/collapse checks
  => Step144 must be formulation diagnosis, no 500-step.

mass_neutral_design_insufficient:
  enabled rows do not improve disabled baseline
  => return to projection/formulation design, no 500-step.

mass_neutral_design_unstable:
  any enabled row introduces first failure or compact collapse
  => stop parameter progression and revisit boundary stability.
```

Audit always keeps:

```text
selected96_execution_allowed = false
selected_static_execution_allowed = false
validation_claim_allowed = false
fluent_validation_claim_allowed = false
fsi_validation_claim_allowed = false
quasi2d_validation_claim_allowed = false
production_readiness_claim_allowed = false
```

## Required Tests

Add:

```text
tests/test_step143_mass_neutral_design_contract.py
```

Tests must cover:

1. Step142 goal reconciliation: only `initial` reference mode and correct
   `step142_design_readiness_report.*` filenames.
2. Step143 phase resolves exactly four specs.
3. All specs are 48^3 / 250-step / output_interval 5.
4. All specs use `row_role = mass_neutral_design_diagnostic_48`.
5. The role is not in `SELECTED_CHAIN_ROLES`.
6. The plane-flux semantics remain outside `CANDIDATE_SEMANTICS` and
   `REPAIRED_CANDIDATE_SEMANTICS`.
7. The disabled row has enabled false and mode disabled.
8. Enabled rows have mode `global_mass_error_density_offset`.
9. Only mass-neutral fields vary across the activated sweep rows.
10. `mass_neutral_activation_hash` differs across the four specs.
11. The manifest expected row records mass-neutral fields and hash.
12. Manifest collection rejects stale rows with a wrong
    `mass_neutral_activation_hash`.
13. Disabled row behavior remains equivalent to the Step141 baseline at
    default report/identity level except for Step143 provenance/name/role.
14. Flow diagnostics include mass-neutral telemetry and claim flags false.
15. A mocked Step143 row that passes all gates still cannot select a boundary.
16. Step143 audit blocks Step144 if enabled rows do not improve mass, flow, and
    outlet CV together.
17. Step143 goal/report/current docs forbid selected96, selected-static, 96^3,
    Fluent, FSI, validation, and Step143 500-step execution.

Run the new test file before production code changes and require a valid RED
state caused by missing Step143 support.

## Required Real Diagnostic Run

After GREEN code/tests are in place, run exactly this bounded phase:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_mass_neutral_design48 `
  --output-dir outputs\step143_mass_neutral_design_diagnostic\mass_neutral_design48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume
```

Then run the audit:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step143_mass_neutral_design_audit `
  --phase-root outputs\step143_mass_neutral_design_diagnostic\mass_neutral_design48 `
  --step142-readiness outputs\step142_mass_neutral_plane_flux_design\step142_design_readiness_report.json `
  --output-dir outputs\step143_mass_neutral_design_diagnostic `
  --force
```

Do not run:

```text
selected96
selected-static
96^3
500-step
Fluent
FSI
```

## Required Docs

Add:

```text
docs/campaigns/fluent_duct_flap/steps/143/report.md
```

Update:

```text
README.md
docs/current/ACTIVE_CAMPAIGN.json
docs/current/STATUS.md
docs/current/VALIDATION_GATES.md
docs/current/READING_ORDER.md
```

Docs must state:

```text
Step143 ran only bounded 48^3 / 250-step LBM-only diagnostic rows.
Step143 did not run 500-step.
Step143 did not run selected96, selected-static, or 96^3.
Step143 did not run Fluent or FSI.
Step143 did not claim validation.
Step143 can only propose Step144 48^3 / 500-step final evidence if the audit
decision supports it.
selected96 remains blocked.
```

If the audit decision does not support Step144, docs must say no 500-step
promotion is justified.

## Verification

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step143-red `
  tests\test_step143_mass_neutral_design_contract.py

& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\lbm\config.py `
  src\mpm_lbm\sim\lbm\fluid.py `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py `
  experiments\steps\step143_mass_neutral_design_audit.py `
  tests\test_step143_mass_neutral_design_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step143-focused `
  tests\test_step143_mass_neutral_design_contract.py `
  tests\test_step142_mass_neutral_plane_flux_design_contract.py `
  tests\test_step141_density_feedback_isolation_contract.py `
  tests\test_step140_long_window_drift_forensics_contract.py `
  tests\test_step139_planeflux_final48_contract.py

& 'D:\working\taichi\env\python.exe' -c "<json load check for Step143 artifacts and current docs>"

git diff --check
```

If the global ECC pre-push hook times out, report:

```text
focused verification passed
full pre-push hook timed out
push used --no-verify
origin/main verified by git ls-remote
GitHub Actions unavailable or no workflow runs if true
```

## Done Criteria

Step143 is done only when:

- this goal file exists and the active goal references it;
- Step142 goal drift is fixed;
- Step143 mass-neutral activation hash exists and gates stale artifacts;
- Step143 phase resolves exactly four 48^3 / 250-step rows;
- runtime activation is opt-in and only for `global_mass_error_density_offset`;
- disabled behavior remains equivalent to Step142/current behavior;
- real Step143 bounded diagnostic rows are executed or explicitly reused only
  if exact matching artifacts already exist and pass manifest identity checks;
- Step143 audit artifacts exist;
- docs/current and README reflect the exact Step143 state;
- selected96/selected-static/96^3/500-step/Fluent/FSI/validation claims remain
  blocked unless a later step explicitly earns them;
- focused verification passes;
- changes are committed and pushed to `origin/main`;
- remote `origin/main` is verified at the final commit hash.
