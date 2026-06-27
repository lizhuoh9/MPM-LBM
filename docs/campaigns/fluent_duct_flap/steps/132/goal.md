# Step132 Plane-Flux Controller Authority Calibration Goal

## Source Review

Step132 follows the post-Step131 review conclusion:

```text
origin/main contains final commit:
1c7de683aaffcf8cb4688505a6ec22bc49e02bfe
test: record Step131 plane flux triage

Step131 is accepted as a valid code-surface step and as real 48^3 / 250-step
planeflux triage evidence.

Both Step131 rows completed 250/250, stayed finite, and had no first-failure
event.

Both Step131 rows failed candidate mass acceptance and flow-development hard
gates.

No 500-step promotion was justified, and selected 96^3 remains blocked.
```

GitHub commit search and repository metadata matched the Step131 final commit,
but GitHub combined status and workflow runs were empty. Therefore the
Step131 `1347 passed, 76 warnings` result is local full-suite / pre-push
evidence, not GitHub Actions evidence. Step132 reports must keep that
distinction explicit.

## Step131 Evidence Baseline

Step131 regularized plane-flux-controlled triage row:

```text
row = duct_only_48_regularized_plane_flux_controlled_pressure_outlet_250step_triage
semantics = regularized_plane_flux_controlled_pressure_outlet
requested_window_completed = true
steps_completed = 250
finite_pass = true
density_gate_pass = true
hard_stop_mass_drift_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
first_failure_step = null
mass_total_delta_rel_final = -0.0283421114698597
candidate_mass_acceptance_observed_abs = 0.0283421114698597
candidate_mass_acceptance_gate_pass = false
flow_development_gate_pass = false
flux_imbalance_rel_tail_mean = 0.39787865621449087
flux_imbalance_rel_tail_max = 0.5034860408405382
outlet_to_inlet_flux_ratio_tail_mean = 1.6088762675407298
midplane_to_inlet_flux_ratio_tail_mean = 1.3339702270861844
outlet_flux_tail_cv = 0.3523076810492384
controller_filtered_flux_error_final = -33.369258880615234
controller_u_feedback_final = -3.9424925489583984e-05
controller_u_feedback_tail_mean = -4.043218238318028e-05
controller_saturation_fraction_run = 0.0
```

Step131 convective plane-flux-controlled triage row:

```text
row = duct_only_48_convective_plane_flux_controlled_damped_outlet_250step_triage
semantics = convective_plane_flux_controlled_damped_outlet
requested_window_completed = true
steps_completed = 250
finite_pass = true
density_gate_pass = true
hard_stop_mass_drift_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
first_failure_step = null
mass_total_delta_rel_final = -0.02858492044911549
candidate_mass_acceptance_observed_abs = 0.02858492044911549
candidate_mass_acceptance_gate_pass = false
flow_development_gate_pass = false
flux_imbalance_rel_tail_mean = 0.4090919843128926
flux_imbalance_rel_tail_max = 0.5348760352869728
outlet_to_inlet_flux_ratio_tail_mean = 1.7338794180572676
midplane_to_inlet_flux_ratio_tail_mean = 1.60001489270226
outlet_flux_tail_cv = 0.15801241453426013
controller_filtered_flux_error_final = -31.221101760864258
controller_u_feedback_final = -3.6886933230562136e-05
controller_u_feedback_tail_mean = -4.035353291934977e-05
controller_saturation_fraction_run = 0.0
```

## Technical Diagnosis

Step131 successfully changed the controller input from Step130's local velocity
proxy to a true plane-integrated flux-error controller:

```text
target_outlet_flux = inlet_flux_plane
measured_outlet_flux = outlet_flux_plane
raw_error = target_outlet_flux - measured_outlet_flux
filtered_error = low_pass(raw_error)
u_feedback = clamp(gain_u * filtered_error / outlet_fluid_area, -cap, cap)
target_u_x = interior_u_x + u_feedback
```

The Step131 failure mode is not a sign error and not a disconnected controller.
The failure mode is insufficient control authority:

```text
gain_u = 0.0025
cap_u = 0.002
filter_alpha = 0.02
outlet_fluid_area ~= 2116 on the 48^3 duct outlet plane
filtered_error ~= -33
u_feedback ~= -33 / 2116 * 0.0025 ~= -3.9e-05
```

The observed `controller_u_feedback` values match that scale. They are roughly
two orders of magnitude below the configured cap, and
`controller_saturation_fraction_run = 0.0`. The controller architecture is now
correct, but the initial gain/area-normalization/cap authority is too weak to
meaningfully reduce outlet over-throughput.

## Step132 Objective

Calibrate the Step131 plane-flux closed-loop controller authority on bounded
48^3 LBM-only triage rows.

The technical goal is:

```text
Increase effective controller authority enough to change outlet/midplane
throughput while preserving finite/density/population/Mach stability and
improving candidate mass acceptance.
```

Step132 must not introduce a fourth boundary concept by default. It should reuse
the Step131 semantics:

```text
regularized_plane_flux_controlled_pressure_outlet
convective_plane_flux_controlled_damped_outlet
```

and vary controller parameters through distinct Step132 row specs and manifest
metadata.

## Non-Negotiable Scope Boundary

Step132 may:

- Add this checked-in goal file and a Step132 report.
- Patch `docs/current/VALIDATION_GATES.md` so the read-first current docs
  include Step131 planeflux evidence.
- Add controller authority diagnostics to the existing bounded flow-development
  CSV/JSON surface.
- Add a distinct Step121 phase:

```text
planeflux_sweep48
```

- Add Step132 48^3 / 250-step sweep specs that reuse the Step131 semantics with
  higher `open_boundary_flux_feedback_gain_u`, existing `cap_u`, and existing
  filter/blend controls.
- Add focused Step132 contract tests.
- Run a tiny real controller-authority smoke before the 48^3 sweep if tests
  pass.
- Run bounded 48^3 / 250-step `planeflux_sweep48` rows after the smoke passes.
- Update current docs and campaign artifacts with the exact Step132 outcome.
- Commit and push verified code, tests, docs, and generated artifacts to
  `origin/main`.

Step132 must not:

- Mutate Step130 or Step131 semantics or artifacts.
- Reclassify Step131 triage rows as repaired 48^3 acceptance evidence.
- Add another boundary-condition semantics concept unless the sweep proves the
  existing concept cannot express the required control authority.
- Run 500-step final rows unless a Step132 250-step sweep row first clears the
  explicit relaxed triage gates.
- Run selected 96^3 duct rows.
- Run selected 96^3 static rows.
- Run quasi-2D rows.
- Run FSI rows.
- Claim Fluent validation.
- Claim Figure 29.3 parity.
- Relax Step121/Step124 hard gates.
- Delete, rewrite, or mask Step127, Step128, Step129, Step130, or Step131
  artifacts.
- Touch vendored `external/taichi_LBM3D`.
- Use `--force` by default for new Step132 rows; if a fresh rerun requires
  `--force`, the report must explain why.

## Phase 0: Current Docs Consistency Patch

Patch `docs/current/VALIDATION_GATES.md` before implementation work proceeds
past the Step132 goal:

```text
- New Step131 plane-flux-control semantics exist:
  regularized_plane_flux_controlled_pressure_outlet
  convective_plane_flux_controlled_damped_outlet
- Step121 has a separate planeflux48 phase.
- Both Step131 48^3 / 250-step rows completed but failed candidate mass
  acceptance and flow-development gates.
- Controller feedback was finite but too small relative to cap; no saturation
  occurred.
- No 500-step promotion was run from Step131 triage.
- Selected 96^3 remains blocked.
```

This docs patch does not change gate semantics. It only makes the read-first
current document set internally consistent.

## Phase 1: Step132 Goal Anchor and Active Goal

Create this checked-in goal file first, then create the active short goal as a
path reference to this file.

The active short goal must identify this file as the source of truth and must
state that completion includes implementation, tests, bounded 48^3 sweep
artifacts when tests/smoke pass, report/current-doc updates, verified commit,
and push to `origin/main`.

## Phase 2: Reuse Existing Semantics

Do not add new `LBMConfig` semantics initially.

The Step132 sweep specs should reuse:

```text
regularized_plane_flux_controlled_pressure_outlet
convective_plane_flux_controlled_damped_outlet
```

The row names and parameter metadata must distinguish Step132 from Step131.
Example row names:

```text
duct_only_48_regularized_plane_flux_controlled_pressure_outlet_gain005_cap002_250step_triage
duct_only_48_regularized_plane_flux_controlled_pressure_outlet_gain010_cap002_250step_triage
duct_only_48_regularized_plane_flux_controlled_pressure_outlet_gain025_cap002_250step_triage
duct_only_48_regularized_plane_flux_controlled_pressure_outlet_gain025_cap005_250step_triage
duct_only_48_convective_plane_flux_controlled_damped_outlet_gain005_cap002_250step_triage
duct_only_48_convective_plane_flux_controlled_damped_outlet_gain010_cap002_250step_triage
```

The row role remains:

```text
plane_flux_control_candidate_48
```

The phase must be distinct:

```text
planeflux_sweep48
```

The solver-state hash already includes gain/filter/cap parameters. Step132
tests must prove parameter changes create distinct row identity or manifest
identity so stale Step131 rows cannot be reused as Step132 sweep evidence.

## Phase 3: Bounded Parameter Sweep Design

The compact initial sweep should test whether authority, not a new formulation,
is the blocking factor.

Expected initial parameter set:

```text
regularized:
  gain_u = 0.05, cap_u = 0.002, alpha = 0.02, gain_rho = 0.0, blend = 0.02
  gain_u = 0.10, cap_u = 0.002, alpha = 0.02, gain_rho = 0.0, blend = 0.02
  gain_u = 0.25, cap_u = 0.002, alpha = 0.02, gain_rho = 0.0, blend = 0.02
  gain_u = 0.25, cap_u = 0.005, alpha = 0.02, gain_rho = 0.0, blend = 0.02

convective:
  gain_u = 0.05, cap_u = 0.002, alpha = 0.02, gain_rho = 0.0, blend = 0.02
  gain_u = 0.10, cap_u = 0.002, alpha = 0.02, gain_rho = 0.0, blend = 0.02
```

Rationale:

```text
Step131 gain = 0.0025 produced |u_feedback| ~= 4e-05.
gain = 0.10 should produce |u_feedback| ~= 0.0016 for filtered_error ~= -33.
gain = 0.25 should often reach cap = 0.002 if the same flux imbalance persists.
```

Do not run an exhaustive 24-combination grid in this step. Step132 is a bounded
authority calibration sweep, not an open-ended optimizer.

## Phase 4: Controller Authority Diagnostics

Add or ensure bounded diagnostics expose these summary fields:

```text
controller_u_feedback_tail_mean
controller_u_feedback_tail_abs_max
controller_u_feedback_tail_std
controller_saturation_fraction_tail
controller_saturation_fraction_run
controller_raw_flux_error_tail_mean
controller_filtered_flux_error_tail_mean
controller_target_outlet_flux_tail_mean
controller_measured_outlet_flux_tail_mean
controller_authority_ratio_tail_mean
controller_authority_ratio_tail_max
```

Define:

```text
controller_authority_ratio = abs(controller_u_feedback) / correction_cap_u
```

Clamp/guard the denominator if `correction_cap_u <= 0` so diagnostics remain
finite and explicit.

The diagnostics should make these failure modes distinguishable:

```text
authority too weak
authority saturating
wrong sign
oscillation / high feedback variance
mass coupling remains poor despite stronger velocity feedback
```

## Phase 5: Step132 Tests

Add:

```text
tests/test_step132_plane_flux_authority_sweep_contract.py
```

Required coverage:

1. `planeflux_sweep48` exists and is separate from `planeflux48`.
2. All Step132 sweep specs use `requested_n_steps = 250`.
3. Sweep row names encode gain/cap or manifest metadata records parameters
   clearly enough to audit row identity.
4. Solver-state/config hash differs across gain/cap/filter settings.
5. Sweep rows cannot enable selected 96^3.
6. Flow-development diagnostics include `controller_authority_ratio`.
7. Diagnostic summaries include tail controller authority fields.
8. Stale Step131 rows cannot be reused as Step132 sweep rows if params or phase
   differ.
9. Sweep artifacts stay bounded-size and report-only until a row actually
   passes triage gates.

Keep existing Step131 tests in focused regression.

## Phase 6: Tiny Controller-Authority Smoke

Before the 48^3 sweep, run a tiny real smoke:

```text
nx = 8
ny = 6
nz = 6
n_steps = 20
semantics = regularized_plane_flux_controlled_pressure_outlet
gain_u = 0.25
cap_u = 0.002
alpha = 0.02
gain_rho = 0.0
```

Expected checks:

```text
finite_pass = true
requested_window_completed = true
abs(controller_u_feedback) <= cap_u
controller_authority_ratio_abs_max <= 1.0 + tolerance
authority ratio is materially larger than the Step131 baseline
validation_claim_allowed = false
selected96_claim_allowed = false
```

If the tiny smoke is unstable, reduce `cap_u` before 48^3. Do not hide the
failure by changing hard gates.

## Phase 7: Bounded 48^3 / 250-Step Sweep

Run the sweep only after tests and tiny smoke pass:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_sweep48 `
  --allow-large-real-rows `
  --output-interval 25
```

Do not use `--force` for new rows unless stale artifacts require a fresh rerun.
If `--force` is used, Step132 report must explain the reason.

## Phase 8: Step132 Relaxed Triage Promotion Criteria

A Step132 sweep row may be considered for a later 500-step 48^3 final row only
if it clears all of these relaxed triage conditions:

```text
requested_window_completed = true
finite_pass = true
density_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
first_failure_step = null
hard_stop_mass_drift_gate_pass = true
candidate_mass_acceptance_observed_abs < 0.01
0.85 <= abs(outlet_to_inlet_flux_ratio_tail_mean) <= 1.15
0.85 <= abs(midplane_to_inlet_flux_ratio_tail_mean) <= 1.15
flux_imbalance_rel_tail_mean < 0.20
flux_imbalance_rel_tail_max < 0.35
outlet_flux_tail_cv < 0.20
0.10 <= controller_authority_ratio_tail_mean <= 0.95
```

If no candidate passes, stop at triage and keep selected 96^3 blocked.

If one or two rows pass, do not jump to selected 96^3. The next step should be
a 500-step 48^3 final evidence row.

## Phase 9: Outcome Interpretation

Interpret Step132 results as follows:

```text
Case A: higher gain improves ratios but mass acceptance still fails
  -> next step may add slow density feedback gain_rho sweep.

Case B: higher gain saturates but ratios remain high
  -> inspect whether measured flux should use x = nx - 2 near-outlet plane
     rather than x = nx - 1 outlet plane.

Case C: ratios improve but outlet CV explodes
  -> reduce filter_alpha and cap_u; keep gain moderate.

Case D: convective remains worse but regularized improves
  -> keep regularized as the primary 500-step candidate surface.

Case E: one triage row clears relaxed gates
  -> next step is a 500-step 48^3 final row, not selected 96^3.
```

## Phase 10: Required Step132 Report Contents

Create:

```text
docs/campaigns/fluent_duct_flap/steps/132/report.md
```

Required report contents:

```text
- Step131 baseline metrics.
- Validation-gates docs consistency patch summary.
- Exact sweep specs and parameters.
- Command used, including explicit no-force or force explanation.
- Tiny smoke result.
- Each 48^3 sweep row:
  gain_u, cap_u, filter_alpha, blend, gain_rho
  completed steps
  candidate_mass_acceptance_observed_abs
  outlet_to_inlet_flux_ratio_tail_mean
  midplane_to_inlet_flux_ratio_tail_mean
  flux_imbalance_rel_tail_mean
  flux_imbalance_rel_tail_max
  outlet_flux_tail_cv
  controller_u_feedback_tail_mean
  controller_u_feedback_tail_abs_max
  controller_u_feedback_tail_std
  controller_authority_ratio_tail_mean
  controller_authority_ratio_tail_max
  controller_saturation_fraction_tail
  controller_saturation_fraction_run
- selected 96^3 blocked/allowed decision.
- 500-step 48^3 promotion blocked/allowed decision.
```

Expected final state unless a row passes relaxed triage gates:

```text
state = 48_candidates_failed
best_boundary_selected = false
selected96_allowed = false
```

## Phase 11: Verification

Minimum compile check:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\lbm\fluid.py `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py `
  tests\test_step132_plane_flux_authority_sweep_contract.py
```

Focused regression:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step132-final-focused `
  tests\test_step132_plane_flux_authority_sweep_contract.py `
  tests\test_step131_plane_flux_controller_contract.py `
  tests\test_step130_flow_development_repair_contract.py `
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
  --basetemp outputs\tmp\pytest-step132-final-policy `
  tests\test_step56_behavior_preservation_contract.py `
  tests\test_step57_step56_regression_contract.py `
  tests\test_step58_step57_regression_contract.py
```

Run the full suite before push:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step132-final-all
```

Also run:

```powershell
git diff --check
```

## Recommended Commit Structure

Prefer:

```text
docs: add Step132 plane flux authority goal
docs: update validation gates for Step131 evidence
feat/test: add Step132 plane flux authority sweep
test: run Step132 plane flux authority 48 triage sweep
```

It is acceptable to combine the validation-gates docs patch with the Step132
goal commit if the final history remains clear.

## Completion Definition

Step132 is complete only when:

```text
- The detailed goal file is checked in and the active goal references it.
- VALIDATION_GATES.md includes Step131 planeflux evidence.
- Step132 contract tests are added and pass.
- The controller authority diagnostics are present in bounded CSV/JSON output.
- Tiny controller-authority smoke is run and recorded.
- planeflux_sweep48 48^3 / 250-step rows are run only after tests/smoke pass.
- Step132 report records exact outcomes and claim boundaries.
- Current docs are updated with the outcome.
- Full verification passes or any failure is explicitly reported.
- The final verified code/docs/artifacts are committed and pushed to
  origin/main.
- Final response reports final commit hash, branch/remote proof, pass counts,
  and whether selected 96^3 remains blocked.
```
