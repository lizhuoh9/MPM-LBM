# Step142 Mass-Neutral Plane-Flux Controller Design Goal

## Objective

Implement Step142 as a design/contract step for a future mass-neutral
plane-flux outlet controller. Step142 must use the Step141 result as its source
evidence and must not run a real LBM campaign row.

The core question is:

```text
Since Step141 showed that lowering or disabling gain_rho does not explain or
repair the Step139/Step140 post-250 tail failure, what contract and disabled
runtime surface should exist for a future mass-neutral plane-flux outlet
controller?
```

Step142 should add a report-visible, disabled-by-default config surface and
design readiness artifacts. It must not activate new solver behavior by
default, must not alter current hard gates, and must not promote any row to
selected96 or 500-step final evidence.

## Source Evidence

Step142 starts from remote/head:

```text
24f5bef3d10e6102fbc2a1cd28c383df81ad7bf3
```

The accepted Step141 result is:

```text
decision_case = density_feedback_isolation_insufficient
best_gain_rho = 0.001
row_count = 4
step142_single_500step_final_evidence_proposal_allowed = false
selected96_execution_allowed = false
validation_claim_allowed = false
```

Step141 comparison showed:

```text
gain_rho = 0.001
candidate_mass_acceptance_observed_abs = 0.003974863988826804
flux_imbalance_rel_tail_mean = 0.08826485542410979
outlet_flux_tail_cv = 0.09651149130583905

gain_rho = 0.0005
candidate_mass_acceptance_observed_abs = 0.003977426612971523
flux_imbalance_rel_tail_mean = 0.08823144079765681
outlet_flux_tail_cv = 0.09651284032492045

gain_rho = 0.00025
candidate_mass_acceptance_observed_abs = 0.003978707752511535
flux_imbalance_rel_tail_mean = 0.08821456045076578
outlet_flux_tail_cv = 0.09651300200390653

gain_rho = 0.0
candidate_mass_acceptance_observed_abs = 0.003979989185473907
flux_imbalance_rel_tail_mean = 0.0881982312839506
outlet_flux_tail_cv = 0.09651379624841921
```

Interpretation:

```text
The 250-step window is nearly invariant to gain_rho. Removing density feedback
slightly reduces mean flux imbalance but slightly worsens mass acceptance and
outlet stationarity. Step141 therefore does not support density feedback as the
dominant cause of Step140's post-250 long-window failure.
```

Step142 must preserve the Step140/Step141 interpretation:

```text
post_250_mass_excursion_with_tail_acceptance_failure
```

This is not a claim of strictly monotonic mass accumulation. It means the mass
rose quickly after step 250, later partly relaxed, and still failed the
hard-tail candidate mass-acceptance gate in the 500-step Step139 window.

## Scope Boundary

Step142 is a design/contract step only.

Forbidden:

```text
no selected96
no selected-static
no 96^3
no Fluent
no FSI
no 500-step run
no real 48^3 campaign rows
no validation claim
no quasi-2D validation claim
no Fluent/Figure 29.3 parity claim
no production-readiness claim
no Step121/Step124 hard-gate relaxation
no adding plane-flux semantics to CANDIDATE_SEMANTICS
no adding Step142 row role to SELECTED_CHAIN_ROLES
no Step142 direct approval of any 500-step final evidence
```

Allowed:

```text
add disabled-by-default config fields
record those fields in driver/config/report surfaces
add report-only design docs and artifacts
add static/contract tests
add an optional report generator that only reads Step141 outputs
fix the stale ACTIVE_CAMPAIGN commit note from Step141
```

## Required Config Surface

Add disabled-by-default fields to `LBMConfig`:

```python
open_boundary_mass_neutral_flux_control_enabled: bool = False
open_boundary_mass_neutral_flux_control_mode: str = "disabled"
open_boundary_mass_neutral_mass_error_gain: float = 0.0
open_boundary_mass_neutral_mass_error_cap: float = 0.0
open_boundary_mass_neutral_correction_blend: float = 0.0
open_boundary_mass_neutral_reference_mass_mode: str = "initial"
```

Allowed modes:

```text
disabled
global_mass_error_density_offset
outlet_population_projection_report_only
```

Allowed reference mass modes:

```text
initial
runtime_initial
```

Validation rules:

```text
enabled must be bool-like
mode must be one of the allowed modes
gain must be non-negative
cap must be non-negative
blend must be in [0, 1]
reference_mass_mode must be one of the allowed modes
if mode == disabled then enabled must be false
if enabled == true in Step142, tests should reject activating it through Step120/Step121 specs
```

Step142 must keep default behavior identical:

```text
open_boundary_mass_neutral_flux_control_enabled = false
open_boundary_mass_neutral_flux_control_mode = disabled
all gains/caps/blend = 0
```

## Required Fluid Surface

`LBMFluid3D` must store the new config fields and report them through existing
open-boundary stats. In Step142, this is only a report-visible surface.

Required reported fields:

```text
mass_neutral_flux_control_enabled
mass_neutral_flux_control_mode
mass_neutral_mass_error_gain
mass_neutral_mass_error_cap
mass_neutral_correction_blend
mass_neutral_reference_mass_mode
mass_neutral_projection_enabled
mass_neutral_runtime_behavior_active
```

In Step142:

```text
mass_neutral_projection_enabled = false
mass_neutral_runtime_behavior_active = false
```

No Step142 code may write altered `f` or `F` populations from these fields.
Report-only mode may expose planned telemetry names, but it must not execute a
projection or change solver state.

## Step120 Reporting Requirements

Step120 specs, driver config, metadata, boundary reports, finite summaries, and
run manifest rows must expose the new mass-neutral fields so future Step143 rows
can be audited without reading code.

Required spec fields:

```text
open_boundary_mass_neutral_flux_control_enabled
open_boundary_mass_neutral_flux_control_mode
open_boundary_mass_neutral_mass_error_gain
open_boundary_mass_neutral_mass_error_cap
open_boundary_mass_neutral_correction_blend
open_boundary_mass_neutral_reference_mass_mode
```

Required report fields:

```text
mass_neutral_flux_control_enabled
mass_neutral_flux_control_mode
mass_neutral_mass_error_gain
mass_neutral_mass_error_cap
mass_neutral_correction_blend
mass_neutral_reference_mass_mode
mass_neutral_projection_enabled
mass_neutral_runtime_behavior_active
selected96_claim_allowed = false
validation_claim_allowed = false
```

Hash policy:

```text
The new fields may be included in new future run-manifest/config surfaces.
Existing committed Step141 artifacts are not recomputed retroactively.
The default disabled fields must not activate solver behavior.
```

## Step121 Requirements

Step142 must not add a Step121 real-run phase.

Explicitly forbidden phase names in Step142:

```text
planeflux_mass_neutral_design48
step142_mass_neutral48
mass_neutral_design48
```

Those names are reserved for a possible later Step143 48^3 / 250-step
diagnostic, not for Step142.

Step121 selected96 and selected-static branches must remain unchanged.
Step142 row roles must not be added to `SELECTED_CHAIN_ROLES`.

## Design Proposal

Step142 should document two designs and recommend only one for a possible
Step143 diagnostic.

### Design A: global_mass_error_density_offset

Core idea:

```text
Separate flux-error control from global-mass-error control.
Use flux error only for u_feedback.
Use global mass error only for a tiny outlet density/pressure offset that
opposes accumulated domain mass drift.
```

Pseudo formula:

```text
mass_error = (mass_total - mass_initial) / mass_initial
rho_mass_feedback = clamp(-gain_mass * mass_error, -cap_mass, cap_mass)
target_rho = outlet_rho + rho_mass_feedback + existing_rho_feedback
```

Benefits:

```text
report-visible
physically interpretable as outlet pressure/density micro-adjustment
does not directly rewrite unknown-population projection
can be tested later with tiny gain/cap in a bounded 250-step diagnostic
```

Risks:

```text
may perturb outlet ratio or mean flux imbalance
must be capped tightly
must not be advanced to 500-step until a later 250-step diagnostic improves
mass, flux mean, outlet CV, and collapse state together
```

### Design B: outlet_population_projection_report_only

Core idea:

```text
Quantify how large a projection would be needed to make outlet correction
zeroth moment neutral, but do not apply it in Step142.
```

Planned telemetry names:

```text
mass_neutral_projection_delta_sum_step
mass_neutral_projection_delta_abs_sum_step
mass_neutral_projection_velocity_moment_cost_step
mass_neutral_projection_enabled = false
```

Benefits:

```text
does not change solver behavior
can quantify whether a future projection would strongly damage momentum
keeps D3Q19 unknown-population coupling risk visible
```

Risks:

```text
D3Q19 outlet unknown populations couple zeroth moment and x-momentum
actual projection must be designed later with stronger tests
Step142 must not silently implement it
```

Recommended design for Step143:

```text
global_mass_error_density_offset
```

Fallback design:

```text
outlet_population_projection_report_only
```

## Required Design Readiness Artifacts

Add:

```text
experiments/steps/step142_mass_neutral_plane_flux_design_report.py
outputs/step142_mass_neutral_plane_flux_design/design_readiness_report.json
outputs/step142_mass_neutral_plane_flux_design/design_readiness_report.md
docs/campaigns/fluent_duct_flap/steps/142/report.md
docs/campaigns/fluent_duct_flap/steps/142/mass_neutral_plane_flux_design.md
```

The report generator must only read Step141 decision artifacts and write
Step142 design artifacts. It must not import or run `run_step120_matrix`,
`LBMFluid3D`, `create_step120_lbm`, or any selected96 runner.

Required `design_readiness_report.json` fields:

```json
{
  "step": 142,
  "artifact": "step142_mass_neutral_plane_flux_design_readiness",
  "source_step": 141,
  "source_decision_case": "density_feedback_isolation_insufficient",
  "source_step141_decision_hash": "...",
  "design_only": true,
  "new_lbm_run_executed": false,
  "new_parameter_tuning_executed": false,
  "solver_runtime_behavior_changed_by_default": false,
  "selected96_execution_allowed": false,
  "selected_static_execution_allowed": false,
  "validation_claim_allowed": false,
  "step142_500step_final_evidence_allowed": false,
  "step143_250step_diagnostic_proposal_allowed": true,
  "recommended_design": "global_mass_error_density_offset",
  "fallback_design": "outlet_population_projection_report_only",
  "recommended_step143_phase": "planeflux_mass_neutral_design48"
}
```

If the source Step141 decision file is missing or does not have
`density_feedback_isolation_insufficient`, the report generator must produce a
blocked/missing-input artifact and must not allow Step143.

## Required Docs

Add:

```text
docs/campaigns/fluent_duct_flap/steps/142/goal.md
docs/campaigns/fluent_duct_flap/steps/142/report.md
docs/campaigns/fluent_duct_flap/steps/142/mass_neutral_plane_flux_design.md
```

Update:

```text
docs/current/ACTIVE_CAMPAIGN.json
docs/current/STATUS.md
docs/current/VALIDATION_GATES.md
docs/current/READING_ORDER.md
```

Required current-doc facts:

```text
Step142 is design-only.
Step142 did not run LBM.
Step142 did not run 48^3 real rows.
Step142 did not run 500-step.
Step142 did not run selected96/selected-static/96^3.
Step142 did not claim validation.
Step143 may only propose bounded 48^3 / 250-step diagnostics.
Step143 may not run selected96 or 500-step.
Step144 is the earliest possible place for a single 500-step final-evidence
proposal, and only if Step143 improves mass, flux_mean, outlet_CV, and collapse
state together.
```

Also fix the Step141 `ACTIVE_CAMPAIGN.json` note drift:

```text
repository_head_at_report identifies the Step141 runtime/report head used
before the final pushed Step141 commit.
final_repository_head_after_push = 24f5bef3d10e6102fbc2a1cd28c383df81ad7bf3
```

## Required Tests

Add:

```text
tests/test_step142_mass_neutral_plane_flux_design_contract.py
```

Tests must cover:

1. Default `LBMConfig` keeps mass-neutral control disabled and validates the
   allowed modes.
2. `LBMFluid3D` source stores the disabled-by-default mass-neutral fields and
   exposes report-only stats fields without a population-writing implementation.
3. Step120 default specs expose mass-neutral fields as disabled in driver config,
   metadata, boundary report, and summary/report rows.
4. Step142 does not add a Step121 phase and does not add selected96,
   selected-static, 96^3, Fluent, FSI, or 500-step commands.
5. Step142 row roles are not added to `SELECTED_CHAIN_ROLES`.
6. Step141/earlier selected-candidate semantics remain unchanged.
7. The design report generator reads Step141 decision summary, checks its hash,
   requires `density_feedback_isolation_insufficient`, and writes JSON/MD
   artifacts with all claim flags false.
8. Missing or wrong Step141 decision input produces blocked/missing-input
   artifacts and does not allow Step143.
9. Step142 docs explicitly forbid 500-step, selected96, Fluent, FSI, and
   validation.
10. Committed Step142 outputs exist and match the design-only contract.

Use red-to-green where practical: first run the new contract tests before the
implementation so the failure records missing fields/report/artifacts, then
implement the smallest report-only surface that satisfies the contract.

## Verification

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\lbm\config.py `
  src\mpm_lbm\sim\lbm\fluid.py `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py `
  experiments\steps\step142_mass_neutral_plane_flux_design_report.py `
  tests\test_step142_mass_neutral_plane_flux_design_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step142 `
  tests\test_step142_mass_neutral_plane_flux_design_contract.py `
  tests\test_step141_density_feedback_isolation_contract.py `
  tests\test_step140_long_window_drift_forensics_contract.py

& 'D:\working\taichi\env\python.exe' -m experiments.steps.step142_mass_neutral_plane_flux_design_report `
  --step141-decision outputs\step141_density_feedback_isolation\step141_decision_summary.json `
  --output-dir outputs\step142_mass_neutral_plane_flux_design `
  --force

& 'D:\working\taichi\env\python.exe' -c "<json load check for Step142/current docs artifacts>"

git diff --check
```

If the global ECC pre-push hook times out, the final report must say:

```text
focused verification passed
full pre-push hook timed out
push used --no-verify
origin/main verified by git ls-remote
GitHub Actions not run / no workflow status if unavailable
```

## Done Criteria

Step142 is done only when:

- this goal file exists and the active goal references it;
- the source Step141 decision is read and hashed;
- config/report-only mass-neutral fields exist and are default-disabled;
- default runtime behavior is unchanged;
- no Step142 real-run phase exists;
- no real 48^3, 500-step, selected96, Fluent, or FSI work was run;
- Step142 design readiness JSON/MD artifacts exist;
- Step142 docs and current docs reflect the design-only blocked state;
- focused verification passes;
- changes are committed and pushed to `origin/main`;
- remote `origin/main` is verified at the final commit hash.
