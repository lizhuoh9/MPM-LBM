# Step128 LBM Open-Boundary Formulation Repair Goal

## Source Review

This goal follows Step127 and the external review conclusion that Step127 is
acceptable as real 48^3 candidate terminal evidence.

Current accepted Step127 commit:

```text
227fc7a8fafb151f1fa660819b44c578b937d74c
test: run Step127 48 candidate campaign
```

The active campaign state after Step127 is:

```text
state = 48_candidates_failed
final_classification = boundary_repair_failed_revisit_lbm_solver
best_boundary_selected = false
selected96_allowed = false
validation_claim_allowed = false
```

Step127 did not expose a campaign automation, checkpoint, provenance, stale-row,
or runner crash defect. It exposed a boundary-formulation failure: neither
available 48^3 candidate satisfies the Step124/Step121 hard gates.

Therefore Step128 must be LBM open-boundary formulation repair. Step128 must not
be selected 96^3 execution.

## Step127 Evidence Baseline

### Passing Legacy Reference

`duct_only_48_legacy_boundary_500step_reference_real` remains the usable 48^3
duct-only reference:

```text
requested_window_completed = true
step120_validation_claimed = true
flow_development_gate_pass = true
mass_total_delta_rel_final = 0.0007730374927265733
flux_imbalance_rel_tail_mean = 0.04043317017445867
flux_imbalance_rel_tail_max = 0.08607841290325333
outlet_to_inlet_flux_ratio_tail_mean = 0.9595668298255413
midplane_to_inlet_flux_ratio_tail_mean = 0.9556179894908249
outlet_flux_tail_cv = 0.02463282965556423
```

### Failed Old-Regularized Reference

`duct_only_48_regularized_boundary_500step_reference_real` is a valid failed
comparison baseline:

```text
requested_window_completed = true
step120_validation_claimed = true
flow_development_gate_pass = false
mass_total_delta_rel_final = 0.002957161603977865
flux_imbalance_rel_tail_mean = 0.5116500495884674
flux_imbalance_rel_tail_max = 0.8660866973898724
outlet_to_inlet_flux_ratio_tail_mean = 1.4127437709040476
midplane_to_inlet_flux_ratio_tail_mean = 1.3061915562381126
outlet_flux_tail_cv = 0.4528776651615377
```

### Failed Limited-Regularized Candidate

`duct_only_48_regularized_limited_boundary_500step_real` completed the requested
real window but failed flow development:

```text
semantics = regularized_velocity_pressure_limited
requested_window_completed = true
steps_completed = 500
step120_validation_claimed = true
flow_development_gate_pass = false
mass_total_delta_rel_final = 0.002957166349791136
flux_imbalance_rel_tail_mean = 0.5116500063984565
flux_imbalance_rel_tail_max = 0.8660864636023118
outlet_to_inlet_flux_ratio_tail_mean = 1.4127439008448124
midplane_to_inlet_flux_ratio_tail_mean = 1.3061913967849994
outlet_flux_tail_cv = 0.452877609631164
limiter_activation_fraction = 0.0
first_failure_step = null
first_failure_reason = null
candidate_pass = false
```

Interpretation: this is stable real evidence, but it reproduces the old
regularized failed-baseline behavior. Since limiter activation was zero, the
failure is not explained by limiter clipping. Step128 should not tune limiter
parameters as the primary repair.

### Failed Convective Candidate

`duct_only_48_convective_outlet_boundary_500step_real` produced terminal real
failure evidence before the requested window:

```text
semantics = convective_pressure_outlet_experimental
requested_window_completed = false
steps_completed = 200
step120_validation_claimed = false
flow_development_gate_pass = false
mass_total_delta_rel_final = 0.04684463072340483
flux_imbalance_rel_tail_mean = 0.2616703854049617
flux_imbalance_rel_tail_max = 0.2690680105951848
outlet_to_inlet_flux_ratio_tail_mean = 0.7382269660347947
midplane_to_inlet_flux_ratio_tail_mean = 0.7541387863811425
outlet_flux_tail_cv = 0.0038570089621531574
limiter_activation_fraction = 0.0
first_failure_step = 200
first_failure_reason = mass_drift
stop_reason = lightweight_failure:mass_drift
candidate_pass = false
```

Interpretation: the convective outlet improves tail stationarity, but it loses
mass closure and under-delivers outlet throughput. It is not a valid selected
96^3 source.

## Step128 Objective

Repair the LBM x-axis open-boundary formulation so at least one new 48^3
duct-only candidate can run real simulation evidence and satisfy the existing
Step124/Step121 hard gates.

Step128 must add new repair semantics instead of overwriting the old semantics.
The old behaviors must remain reproducible:

```text
equilibrium_all_population_reset
regularized_velocity_pressure
regularized_velocity_pressure_limited
convective_pressure_outlet_experimental
```

The initial Step128 repair candidates should be:

```text
regularized_mass_balanced_pressure_outlet
convective_mass_balanced_pressure_outlet
```

Optional fallback if bounded smoke evidence justifies it:

```text
hybrid_ramped_mass_balanced_outlet
```

## Non-Negotiable Scope Boundary

Step128 may:

- Add Step128 goal, report, tests, and current-campaign documentation.
- Add telemetry/report fields that clarify hard-stop mass drift versus candidate
  mass acceptance.
- Add new `LBMConfig.open_boundary_semantics` values for repaired open
  boundaries.
- Add new Step120/Step121 candidate rows for Step128 repaired 48^3 semantics.
- Change `src/mpm_lbm/sim/lbm/fluid.py` boundary formulas only for the new
  Step128 semantics.
- Add bounded tiny smoke tests and focused contract tests.
- Run short bounded Step128 smoke/triage rows.
- Run real 48^3 repaired candidate rows only after the bounded tests pass.
- Commit and push the verified result to `origin/main`.

Step128 must not:

- Run selected 96^3 duct or selected 96^3 static rows from the current Step127
  state.
- Run quasi-2D.
- Run FSI.
- Claim Fluent validation.
- Claim Figure 29.3 parity.
- Relax Step124/Step121 hard gates to make a candidate pass.
- Rewrite Step127 artifacts to manufacture a selected boundary.
- Replace legacy, regularized, limited, or convective semantics in-place.
- Use limiter clipping as the primary stability mechanism.
- Touch vendored `external/taichi_LBM3D`.
- Hide solver physics in case-specific code.

## Phase 0: Baseline Freeze

Before implementation, confirm:

```powershell
git status --short
git rev-parse HEAD
git branch --show-current
```

Expected local baseline at Step128 start:

```text
HEAD = 227fc7a8fafb151f1fa660819b44c578b937d74c
branch = main
worktree clean
```

Read-first files:

```text
docs/current/STATUS.md
docs/current/ACTIVE_CAMPAIGN.json
docs/current/VALIDATION_GATES.md
docs/campaigns/fluent_duct_flap/steps/127/goal.md
docs/campaigns/fluent_duct_flap/steps/127/report.md
experiments/steps/step120_lbm_boundary_repair_large_real_execution.py
experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py
src/mpm_lbm/sim/lbm/config.py
src/mpm_lbm/sim/lbm/fluid.py
```

## Phase 1: Telemetry / Contract Clarity

Step127 convective artifacts can show both:

```text
first_failure_reason = mass_drift
stop_reason = lightweight_failure:mass_drift
mass_drift_gate_pass = true
```

This is not a Step127 selection bug, because Step121 still rejects the row
through first-failure, incomplete-window, validation, mass, and flow gates.
However, the naming is easy to misread during audit.

Step128 must clarify this by adding explicit hard-stop fields to Step120 report
rows and artifacts:

```text
hard_stop_failure_reason
hard_stop_failure_step
hard_stop_mass_drift_abs_max
hard_stop_mass_drift_gate_pass
candidate_mass_acceptance_abs_max
candidate_mass_acceptance_gate_pass
```

Rules:

- `hard_stop_mass_drift_gate_pass` reflects the lightweight failure detector
  threshold used at failure-check intervals.
- `candidate_mass_acceptance_gate_pass` reflects the stricter candidate
  acceptance threshold used by Step121.
- These fields must not change existing Step127 decisions.
- A row with `first_failure_reason = mass_drift` cannot be selected even if an
  older `mass_drift_gate_pass` field is true.

## Phase 2: New Boundary Semantics

Add new valid semantics in `src/mpm_lbm/sim/lbm/config.py` and dispatch them in
`src/mpm_lbm/sim/lbm/fluid.py`.

### Candidate A: Regularized Mass-Balanced Pressure Outlet

Semantics:

```text
regularized_mass_balanced_pressure_outlet
```

Intent:

- Preserve regularized pressure-outlet structure.
- Apply a bounded mass/flux correction only to unknown x-max populations.
- Avoid all-population resets.
- Avoid limiter-dependent success.

Implementation direction:

```text
target_rho_outlet = rho_bcxr + bounded_density_feedback
target_u_outlet_x = interior_u_x + bounded_normal_velocity_feedback
unknown populations = feq(target_rho_outlet, target_u_outlet) + interior noneq
```

The correction must be bounded and observable through counters.

### Candidate B: Convective Mass-Balanced Pressure Outlet

Semantics:

```text
convective_mass_balanced_pressure_outlet
```

Intent:

- Preserve the useful stationarity of convective extrapolation.
- Add bounded mass/throughput feedback to unknown x-max populations.
- Avoid disturbing tangential velocity more than necessary.

Implementation direction:

```text
unknown populations = convective extrapolation
unknown populations receive bounded normal-population correction
target = reduce outlet/inlet ratio error and mass drift
```

The correction must be bounded and observable through counters.

## Phase 3: Step120/Step121 Campaign Surface

Add Step128 candidate rows in Step120 while preserving prior Step127 rows:

```text
duct_only_48_regularized_mass_balanced_pressure_outlet_500step_real
duct_only_48_convective_mass_balanced_pressure_outlet_500step_real
```

Use `row_role = candidate_48` for Step128 repaired candidates. Do not make old
limited/convective rows disappear from reports or artifact history.

Update candidate semantics sets so Step121 can evaluate the new semantics. The
Step121 decision rule must still require terminal real evidence for required
Step127 candidate semantics before declaring Step127 complete, but Step128
repair evaluation must not be blocked by the old failed candidate set once the
new repair phase is explicitly selected.

Acceptable implementation strategies:

- Add a distinct Step128 repair phase, such as `repair48`, with Step128
  required candidate semantics; or
- Add Step128-specific helper functions/tests that evaluate repaired candidates
  without changing the Step127 `candidates48` contract.

Do not use a hidden broad `all48` rerun to mix old failed rows and new repaired
rows without clear phase labeling.

## Phase 4: TDD Contract Tests

Add:

```text
tests/test_step128_boundary_formulation_repair_contract.py
```

The tests must cover at least:

1. `LBMConfig` accepts the new Step128 semantics.
2. `LBMFluid3D.Boundary_condition` dispatches the new semantics to distinct
   Step128 kernels.
3. Step120 solver-state hash includes the new semantics and differs from old
   limited/convective hashes.
4. Step120 candidate semantics include the repaired candidates without removing
   old semantics.
5. Step120 report rows expose hard-stop mass-drift clarity fields.
6. A hard-stop mass-drift row reports
   `hard_stop_mass_drift_gate_pass = false`.
7. A row with `first_failure_reason = mass_drift` cannot pass selection.
8. A candidate with `mass_total_delta_rel_final >= 0.005` cannot pass selection.
9. A candidate with flow ratio outside `[0.80, 1.20]` cannot pass selection.
10. A stale Step127 artifact cannot be reused as a Step128 repaired row because
    solver-state hash / semantics mismatch blocks reuse.

If a tiny Taichi smoke is affordable, add a bounded 4x3x3 or 8x6x6 real row
that verifies the new semantics are finite for a short run and that correction
counters are non-negative.

## Phase 5: Bounded Verification Before Real 48^3

Run compile checks:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\lbm\fluid.py `
  src\mpm_lbm\sim\lbm\config.py `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py
```

Run focused contract tests:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step128-preflight `
  tests\test_step128_boundary_formulation_repair_contract.py `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

If the solver formulas in `fluid.py` change, Step128 verification must include
the Step128 contract tests plus the existing Step123-Step125 campaign tests.

## Phase 6: 48^3 Triage

Only after tests pass, run short triage rows for repaired semantics. Suggested
rows:

```text
regularized_mass_balanced_pressure_outlet_48_250step_triage
convective_mass_balanced_pressure_outlet_48_250step_triage
```

Triage is screening only. It must not be reported as final validation.

Reject a triage candidate if it shows:

```text
nonfinite
rho outside [0.85, 1.15]
mass_total_delta_rel > 0.02 before 250
negative_population_fraction > 1e-3
outlet_to_inlet_flux_ratio_tail_mean outside [0.70, 1.30]
flux_imbalance_rel_tail_mean > 0.25
outlet_flux_tail_cv > 0.25
```

Triage passing can be looser than final gates, but it must be visibly better
than Step127 failed candidates.

## Phase 7: Real 48^3 / 500-Step Acceptance

Promote only the best repaired triage candidate(s) to 500-step real rows.

Final acceptance is unchanged:

```text
requested_window_completed = true
simulation_backed_artifact = true
step120_validation_claimed = true
finite_pass = true
density_gate_pass = true
mass_drift_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
first_failure_step = null
first_failure_reason = null

0.80 <= abs(outlet_to_inlet_flux_ratio_tail_mean) <= 1.20
0.80 <= abs(midplane_to_inlet_flux_ratio_tail_mean) <= 1.20
flux_imbalance_rel_tail_mean < 0.10
flux_imbalance_rel_tail_max < 0.20
outlet_flux_tail_cv < 0.10
limiter_activation_fraction <= 0.05
mass_total_delta_rel_final < 0.005
```

## Phase 8: Decision Outcomes

Step128 report must choose exactly one outcome:

### Outcome A: No Repaired Candidate Passes 48^3

```text
campaign_state = 48_candidates_failed
final_classification = boundary_repair_failed_revisit_lbm_solver
best_boundary_selected = false
selected96_allowed = false
```

Do not run selected 96^3.

### Outcome B: One Repaired Candidate Passes 48^3

```text
campaign_state = repaired_48_candidate_selected
final_classification = boundary_repair_partial_continue_lbm
best_boundary_selected = true
selected96_allowed_for_next_step = true
```

The next step may create a selected 96^3 duct-only goal, but Step128 itself
still must not claim selected 96^3, quasi-2D, FSI, Fluent validation, or
Figure 29.3 parity.

### Outcome C: Multiple Repaired Candidates Pass 48^3

Select by:

1. Flow-development pass margin.
2. `flux_imbalance_rel_tail_mean`.
3. `mass_total_delta_rel_final`.
4. `outlet_flux_tail_cv`.
5. Correction/limiter activation.
6. Runtime.

## Required Documentation Updates

Create or update:

```text
docs/campaigns/fluent_duct_flap/steps/128/goal.md
docs/campaigns/fluent_duct_flap/steps/128/report.md
docs/current/ACTIVE_CAMPAIGN.json
docs/current/STATUS.md
docs/current/VALIDATION_GATES.md
docs/current/READING_ORDER.md
```

If real Step128 outputs are generated, place them under a Step128-specific
artifact root, for example:

```text
outputs/step128_lbm_boundary_formulation_repair/
```

Do not overwrite Step127 artifacts.

## Final Verification Before Push

Minimum final verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\lbm\fluid.py `
  src\mpm_lbm\sim\lbm\config.py `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step128-final-focused `
  tests\test_step128_boundary_formulation_repair_contract.py `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py

git diff --check
```

If any real Step128 triage or acceptance runs are performed, the final report
must list:

```text
command
runtime commit
row names
steps completed
whether checkpoints were restored
hard-stop fields
mass/flux/ratio/tail-CV fields
candidate decision
claim boundary
```

## Push Condition

The user has approved push after the Step128 modifications are implemented and
verified. Push only after:

- The detailed Step128 goal is committed or included in the final commit.
- Code changes are covered by Step128 contract tests.
- Focused verification passes.
- Current docs describe Step128 honestly.
- `git status --short` contains only intended changes.
- The commit message follows the repo convention.
- The pushed `origin/main` hash is verified.

