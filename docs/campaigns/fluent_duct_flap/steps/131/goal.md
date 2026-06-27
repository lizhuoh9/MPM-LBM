# Step131 Plane-Flux Closed-Loop Outlet Repair Goal

## Source Review

Step131 follows the post-Step130 review conclusion:

```text
Step130 is accepted as real 48^3 / 250-step flow-development triage evidence.

Both Step130 triage rows completed 250/250 with finite/density/mass/population
/ Mach stability and no first-failure event.

Both Step130 triage rows failed candidate mass acceptance and failed
flow-development hard gates. No 500-step promotion was justified.

selected 96^3 remains blocked. The next step must remain 48^3 LBM-only
boundary formulation/debugging.
```

Verified Step130 final commit:

```text
e4a942c3f2769ae32c5bbcf321df5967dd99cde7
test: update Step56 LBM defaults policy
```

The previous `1340 passed, 69 warnings` result is local pre-push evidence, not
GitHub Actions evidence. Step131 reports must keep that distinction explicit.

## Step130 Evidence Baseline

Step130 regularized flow-repair triage row:

```text
row = duct_only_48_regularized_flux_matched_pressure_outlet_250step_triage
semantics = regularized_flux_matched_pressure_outlet
requested_window_completed = true
steps_completed = 250
finite_pass = true
density_gate_pass = true
mass_drift_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
first_failure_step = null
mass_total_delta_rel_final = -0.027093607822589214
candidate_mass_acceptance_observed_abs = 0.027093607822589214
candidate_mass_acceptance_gate_pass = false
flux_imbalance_rel_tail_mean = 0.391091092110087
flux_imbalance_rel_tail_max = 0.49363649493296946
outlet_to_inlet_flux_ratio_tail_mean = 1.582099528142026
midplane_to_inlet_flux_ratio_tail_mean = 1.319799119019448
outlet_flux_tail_cv = 0.3462613196020457
flow_development_gate_pass = false
```

Step130 convective flow-repair triage row:

```text
row = duct_only_48_convective_flux_matched_damped_outlet_250step_triage
semantics = convective_flux_matched_damped_outlet
requested_window_completed = true
steps_completed = 250
finite_pass = true
density_gate_pass = true
mass_drift_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
first_failure_step = null
mass_total_delta_rel_final = -0.030650375098126185
candidate_mass_acceptance_observed_abs = 0.030650375098126185
candidate_mass_acceptance_gate_pass = false
flux_imbalance_rel_tail_mean = 0.5063421113905975
flux_imbalance_rel_tail_max = 0.5638390864941747
outlet_to_inlet_flux_ratio_tail_mean = 2.0460586163795886
midplane_to_inlet_flux_ratio_tail_mean = 1.097643901750551
outlet_flux_tail_cv = 0.08348317549327117
flow_development_gate_pass = false
```

Technical diagnosis:

```text
Step130 diagnostics show large target/outlet plane-flux mismatch.

The Step130 kernel records filtered outlet/flow error, but the active outlet
population reconstruction still uses local velocity proxy feedback:

velocity_error = vx_bcxl - target_u[0]
velocity_feedback = gain_u * velocity_error

Therefore Step130 is diagnostic flux matching, not a true plane-integrated
flux-error controller.
```

## Step131 Objective

Implement a true plane-flux closed-loop outlet controller for bounded 48^3
LBM-only duct triage.

The core Step131 behavior must be:

```text
target_outlet_flux = inlet_flux_plane
measured_outlet_flux = outlet_flux_plane
raw_error = target_outlet_flux - measured_outlet_flux
filtered_error = (1 - alpha) * previous_filtered_error + alpha * raw_error
u_feedback = clamp(gain_u * filtered_error / outlet_fluid_area, -cap, cap)
target_u_x = interior_u_x + u_feedback
```

This is the required difference from Step130. Step131 must use the
plane-integrated flux error as the control input, not `vx_bcxl - target_u[0]`.

## Non-Negotiable Scope Boundary

Step131 may:

- Add this checked-in goal file and a Step131 report.
- Add scalar Taichi controller state for plane-flux control.
- Add new semantics:

```text
regularized_plane_flux_controlled_pressure_outlet
convective_plane_flux_controlled_damped_outlet
```

- Add a distinct row role:

```text
plane_flux_control_candidate_48
```

- Add a distinct Step121 phase:

```text
planeflux48
```

- Add controller diagnostics to the existing bounded flow-development CSV/JSON
  surface.
- Add focused Step131 contract tests.
- Run a tiny real controller smoke before 48^3 triage if implementation and
  tests pass.
- Run bounded 48^3 / 250-step `planeflux48` triage rows after the smoke passes.
- Update current docs and campaign artifacts with the exact Step131 outcome.
- Commit and push verified code, tests, docs, and generated artifacts to
  `origin/main`.

Step131 must not:

- Mutate Step130 semantics or Step130 artifacts.
- Reclassify Step130 triage rows as repaired 48^3 acceptance evidence.
- Run 500-step final rows unless a Step131 triage row first clears the relaxed
  triage gates.
- Run selected 96^3 duct rows.
- Run selected 96^3 static rows.
- Run quasi-2D rows.
- Run FSI rows.
- Claim Fluent validation.
- Claim Figure 29.3 parity.
- Relax Step121/Step124 hard gates.
- Delete, rewrite, or mask Step127, Step128, Step129, or Step130 artifacts.
- Touch vendored `external/taichi_LBM3D`.

## Phase 0: Goal Anchor and Commit Policy

Create this checked-in goal file first, then create the active short goal as a
path reference to this file.

Recommended commit structure:

```text
docs: add Step131 plane-flux controller goal
feat/test: add Step131 plane-flux closed-loop outlet controller
test: run Step131 plane-flux 48 triage campaign
```

If no triage candidate passes relaxed gates, stop at triage and keep selected
96^3 blocked. If a triage candidate passes, use a separate later commit or
future step for 500-step 48^3 final evidence.

## Phase 1: Controller State

Add scalar Taichi fields to `LBMFluid3D`:

```text
ob_target_outlet_flux
ob_measured_outlet_flux
ob_flux_error_filtered
ob_outlet_fluid_area
ob_flux_control_u_feedback
```

Additional scalar diagnostics may be added if useful:

```text
ob_flux_control_saturation_count_step
ob_flux_control_saturation_count_run
```

The controller must use scalar reductions/state only. Do not compute dense
Python diagnostics every step for controller operation. Existing full
diagnostics may remain output-interval only.

## Phase 2: Controller Update Sequence

Before applying the new Step131 outlet boundary reconstruction each step:

1. Clear only per-step counters.
2. Reduce inlet-plane flux, outlet-plane flux, and outlet fluid area on the
   Taichi side.
3. Update filtered plane-flux error.
4. Compute bounded normal-velocity feedback.
5. Apply the selected Step131 boundary kernel using that scalar feedback.

Expected control sign:

```text
target_outlet_flux > measured_outlet_flux -> u_feedback > 0
target_outlet_flux < measured_outlet_flux -> u_feedback < 0
abs(u_feedback) <= open_boundary_flux_correction_cap_u
```

## Phase 3: New Semantics, No Step130 Mutation

Keep Step130 semantics intact:

```text
regularized_flux_matched_pressure_outlet
convective_flux_matched_damped_outlet
```

Add new Step131 semantics:

```text
regularized_plane_flux_controlled_pressure_outlet
convective_plane_flux_controlled_damped_outlet
```

Use distinct kernels or dispatch functions so tests can prove Step131 is not
silently reusing Step130 local-velocity feedback.

## Phase 4: Step120/Step121 Campaign Surface

Add Step131 specs separated from Step130:

```text
row_role = plane_flux_control_candidate_48
phase = planeflux48
```

Expected 250-step triage rows:

```text
duct_only_48_regularized_plane_flux_controlled_pressure_outlet_250step_triage
duct_only_48_convective_plane_flux_controlled_damped_outlet_250step_triage
```

Conservative initial parameters:

```text
open_boundary_flux_feedback_gain_u = 0.0025
open_boundary_flux_feedback_gain_rho = 0.0 or 0.001
open_boundary_flux_filter_alpha = 0.02
open_boundary_flux_correction_cap_u = 0.002
open_boundary_convective_blend_weight = 0.02
```

These rows must be visibly non-final:

```text
requested_n_steps = 250
row_role = plane_flux_control_candidate_48
not selected96 enabling evidence
validation_claim_allowed = false
```

## Phase 5: Controller Contract Tests

Add:

```text
tests/test_step131_plane_flux_controller_contract.py
```

Minimum coverage:

```text
1. New semantics are accepted by LBMConfig.
2. New semantics dispatch to distinct Step131 kernels.
3. Controller scalar fields exist and reset correctly.
4. Positive target-minus-outlet error increases outlet normal velocity only
   within cap.
5. Negative target-minus-outlet error decreases outlet normal velocity only
   within cap.
6. filter_alpha changes controller response and enters solver_state_hash.
7. correction_cap_u enters solver_state_hash.
8. planeflux48 phase is separate from flowrepair48, repair48, and candidates48.
9. Step131 triage rows cannot enable selected96.
10. Stale Step130 rows cannot be reused as Step131 rows.
```

## Phase 6: Tiny Controller Smoke

Before 48^3 triage, run a tiny real smoke:

```text
nx = 8
ny = 6
nz = 6
n_steps = 20
```

The smoke must check/report:

```text
finite_pass = true
controller fields finite
u_feedback not always zero
abs(u_feedback) <= cap
filtered_error sign is consistent with outlet over/under-flow
no selected96 claim
```

This smoke is not validation evidence. It is only a sign/cap sanity guard before
spending time on 48^3 triage.

## Phase 7: 48^3 / 250-Step Planeflux Triage

Command structure:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux48 `
  --allow-large-real-rows `
  --output-interval 25
```

Do not run 500-step final rows in this Step131 commit unless at least one
triage row passes the relaxed Step131 triage gates.

## Phase 8: Relaxed Step131 Triage Gates

Use Step130 triage gates plus controller-specific gates:

```text
requested_window_completed = true for 250 steps
finite_pass = true
density_gate_pass = true
mass_drift_abs_max < 0.04
candidate_mass_acceptance_observed_abs < 0.01 by 250
negative_population_fraction = 0
0.85 <= abs(outlet_to_inlet_flux_ratio_tail_mean) <= 1.15
0.85 <= abs(midplane_to_inlet_flux_ratio_tail_mean) <= 1.15
flux_imbalance_rel_tail_mean < 0.20
flux_imbalance_rel_tail_max < 0.35
outlet_flux_tail_cv < 0.20
abs(controller_u_feedback_tail_mean) < correction_cap_u
controller_saturation_fraction_tail < 0.50
```

If no row passes, stop at triage and keep selected96 blocked.

## Phase 9: Diagnostics Report Requirements

For each Step131 row, report:

```text
target_outlet_flux_tail_mean
measured_outlet_flux_tail_mean
raw_flux_error_tail_mean
filtered_flux_error_tail_mean
controller_u_feedback_tail_mean
controller_u_feedback_tail_max_abs
controller_saturation_fraction_tail
outlet_to_inlet_flux_ratio_tail_mean
midplane_to_inlet_flux_ratio_tail_mean
flux_imbalance_rel_tail_mean
flux_imbalance_rel_tail_max
outlet_flux_tail_cv
candidate_mass_acceptance_observed_abs
```

Decision interpretation:

```text
If controller saturates and still overflows:
  cap/gain insufficient or target coupling wrong.

If controller oscillates sign frequently:
  filter_alpha too high or feedback phase wrong.

If outlet ratio improves but mass acceptance fails:
  add slower density feedback or global mass correction in a future step.

If mass improves but ratio remains bad:
  controller is not using the correct plane flux or the wrong outlet plane.
```

## Phase 10: Current Documentation Updates

Update:

```text
docs/current/ACTIVE_CAMPAIGN.json
docs/current/STATUS.md
docs/current/VALIDATION_GATES.md
docs/current/READING_ORDER.md
```

Rules:

```text
If Step131 stops at triage, state that selected96 remains blocked.
If no final 500-step row passes, state that selected96 remains blocked.
Keep local pre-push hook evidence distinct from GitHub Actions evidence.
Do not claim quasi-2D, FSI, Fluent validation, or Figure 29.3 parity.
```

## Final Verification Before Push

Minimum compile:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\lbm\config.py `
  src\mpm_lbm\sim\lbm\fluid.py `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py
```

Minimum focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step131-final-focused `
  tests\test_step131_plane_flux_controller_contract.py `
  tests\test_step130_flow_development_repair_contract.py `
  tests\test_step130_flow_development_diagnostics_contract.py `
  tests\test_step129_repair_checkpoint_counter_contract.py `
  tests\test_step128_boundary_formulation_repair_contract.py `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

If LBMConfig defaults change, keep Step56/57/58 policy guards in the focused
verification set.

Before push:

```powershell
git diff --check
pytest -q
git push origin main
git ls-remote origin refs/heads/main
```

Done criteria:

```text
goal/report/code/tests/artifacts/docs are consistent
Step131 artifacts identify Step131 row role and semantics
Step131 controller diagnostics show plane-flux error, filtered error, feedback,
and saturation state
triage rows are not treated as selected 96^3 enablers
selected96/quasi2D/FSI/Fluent/Figure29.3 remain blocked unless a future final
48^3 hard-gate pass explicitly justifies future allowance
final commit is pushed to origin/main
remote main hash is reported
```
