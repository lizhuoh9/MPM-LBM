# Step130 Flow-Development Boundary Repair Goal

## Source Review

Step130 follows the post-Step129 review conclusion:

```text
Step129 is accepted as real repair48 48^3 / 500-step repaired-candidate
evidence.

Both repaired candidates completed 500/500 and passed basic stability, mass,
finite, population, Mach, first-failure, and candidate-mass-acceptance checks.

Both repaired candidates failed the flow-development hard gates. No repaired
48^3 boundary is selected. selected 96^3 remains blocked.
```

Verified Step129 final commit:

```text
5b034fb8466ab59bbe566dd59012de0192af227f
test: run Step129 repaired 48 candidate campaign
```

The previous local pre-push result:

```text
1332 passed, 65 warnings
```

is local pre-push hook evidence, not GitHub Actions evidence. Step130 reports
must keep that distinction explicit.

## Step129 Evidence Baseline

Step129 regularized repaired row:

```text
row = duct_only_48_regularized_mass_balanced_pressure_outlet_500step_real
semantics = regularized_mass_balanced_pressure_outlet
requested_window_completed = true
steps_completed = 500
mass_total_delta_rel_final = 0.0019035086161313225
flux_imbalance_rel_tail_mean = 0.3722224827902342
flux_imbalance_rel_tail_max = 0.5721747900550053
outlet_to_inlet_flux_ratio_tail_mean = 1.264735695477319
midplane_to_inlet_flux_ratio_tail_mean = 1.2098449625412
outlet_flux_tail_cv = 0.33003290861468526
flow_development_gate_pass = false
```

Step129 convective repaired row:

```text
row = duct_only_48_convective_mass_balanced_pressure_outlet_500step_real
semantics = convective_mass_balanced_pressure_outlet
requested_window_completed = true
steps_completed = 500
mass_total_delta_rel_final = -0.0011874128939383197
flux_imbalance_rel_tail_mean = 0.40325868347534677
flux_imbalance_rel_tail_max = 0.5735062556642948
outlet_to_inlet_flux_ratio_tail_mean = 1.2722701740330669
midplane_to_inlet_flux_ratio_tail_mean = 1.2671693838169262
outlet_flux_tail_cv = 0.5513854681310228
flow_development_gate_pass = false
```

Technical diagnosis:

```text
Step127 convective failed mass stability and stopped at 200 steps, but its
outlet tail CV was low.

Step129 mass-balanced repairs fixed the 500-step stability/mass problem, but
over-delivered outlet and midplane flux and introduced high tail imbalance and
tail stationarity error.
```

Therefore Step130 must move from mass-only feedback toward throughput-matched
and damping/low-pass outlet repair.

## Step130 Objective

Add a bounded third-generation 48^3 LBM-only flow-development repair surface
that:

- preserves Step128/Step129 semantics and artifacts unchanged.
- adds compact diagnostics for outlet throughput and tail stationarity.
- adds new Step130 candidate semantics distinct from Step128/Step129.
- adds a Step130 `flowrepair48` campaign phase or a clearly separated Step130
  runner surface.
- runs bounded 48^3 triage rows first, not selected 96^3.
- promotes only the best 1-2 triage candidates to a final 500-step 48^3 row if
  and only if triage passes the explicit relaxed triage gates.
- keeps selected 96^3, quasi-2D, FSI, Fluent validation, and Figure 29.3 parity
  blocked unless a future step is explicitly allowed.

## Non-Negotiable Scope Boundary

Step130 may:

- Add this Step130 goal file and a Step130 report.
- Add compact open-boundary flow-development diagnostics.
- Add new LBM config fields for Step130 feedback gains, damping, filter alpha,
  and velocity correction caps if they are included in solver-state hashes.
- Add new candidate semantics:

```text
regularized_flux_matched_pressure_outlet
convective_flux_matched_damped_outlet
```

- Optionally add one diagnostic control-baseline semantics:

```text
legacy_unknown_population_targeted_reset
```

- Add a distinct row role:

```text
flow_repair_candidate_48
```

- Add a distinct phase:

```text
flowrepair48
```

- Add focused Step130 tests.
- Run bounded 250-step 48^3 triage rows if the implementation and tests pass.
- Run final 500-step 48^3 rows only when triage evidence clears the relaxed
  triage gates in this goal.
- Update current docs and campaign artifacts with the exact Step130 outcome.
- Commit and push verified code, tests, docs, and generated artifacts to
  `origin/main`.

Step130 must not:

- Run selected 96^3 duct rows.
- Run selected 96^3 static rows.
- Run quasi-2D rows.
- Run FSI rows.
- Claim Fluent validation.
- Claim Figure 29.3 parity.
- Relax Step121/Step124 hard gates.
- Delete, rewrite, or mask Step127, Step128, or Step129 artifacts.
- Mutate Step128/Step129 semantics in place.
- Reclassify Step129 repaired 48^3 evidence as accepted.
- Treat triage rows as final 500-step acceptance evidence.
- Touch vendored `external/taichi_LBM3D`.

## Phase 0: Goal Anchor and Commit Policy

Create this checked-in goal file first, then create the active short goal as a
path reference to this file.

Recommended commit structure:

```text
docs: add Step130 flow-development repair goal
fix/test: add Step130 flow-matched outlet diagnostics and semantics
test: run Step130 flow-repair 48 triage campaign
```

If no triage candidate passes the relaxed triage gates, do not run final
500-step rows. In that case the final evidence commit should remain a triage
campaign commit.

If 1-2 triage candidates pass, a later commit may run only those candidates as
500-step 48^3 rows:

```text
test: run Step130 flow-repair 48 candidate campaign
```

## Phase 1: Diagnostics Before Formula Claims

Step130 must add compact diagnostics that help distinguish:

```text
A. outlet unknown-population correction is too strong.
B. outlet pressure/velocity target feedback sign or scale is wrong.
C. outlet-plane local jetting/backflow drives plane-integrated oscillation.
D. interior midplane has already been polluted by outlet reflection.
E. fixed inlet velocity and outlet pressure/correction coupling are mismatched.
```

Add per-output-interval diagnostic fields where practical:

```text
outlet_flux_raw_before_correction
outlet_flux_after_correction
target_outlet_flux
outlet_flux_error
outlet_flux_error_filtered
correction_gain_effective
correction_delta_abs_sum
outlet_plane_ux_min
outlet_plane_ux_max
outlet_plane_ux_mean
outlet_plane_negative_ux_fraction
midplane_flux
sampled_x_profile_flux
```

Diagnostics must be bounded-size. Do not commit large dense arrays. Compact CSV
and JSON summary artifacts are acceptable.

Required minimum test:

```text
tests/test_step130_flow_development_diagnostics_contract.py
```

Minimum contract:

```text
diagnostic fields exist for Step130 repaired semantics
diagnostic CSV remains bounded-size
no selected96 claim appears
stale Step129 artifacts are not mistaken for Step130 rows
```

## Phase 2: New Semantics, No Step129 Mutation

Keep Step128/Step129 semantics intact:

```text
regularized_mass_balanced_pressure_outlet
convective_mass_balanced_pressure_outlet
```

Add new Step130 semantics:

```text
regularized_flux_matched_pressure_outlet
convective_flux_matched_damped_outlet
```

Do not overwrite existing Step128/Step129 kernels or row definitions. Step129
must remain reproducible from its artifacts and solver-state hashes.

### Candidate A: regularized_flux_matched_pressure_outlet

Goal:

```text
Reduce outlet/inlet over-throughput while preserving Step129 mass stability.
```

Design direction:

```text
target_outlet_flux = filtered_inlet_flux
flux_error = target_outlet_flux - measured_outlet_flux_previous_window
u_feedback = gain_u * flux_error / outlet_area
rho_feedback = gain_rho * mass_error
```

Requirements:

```text
Use previous-window or running estimates, not same-step hard coupling.
Low-pass the feedback to avoid step 250-500 oscillation.
Use a smaller normal-velocity correction cap than Step128.
Target tail mean ratio [0.8, 1.2] and outlet tail CV < 0.10, not exact
per-step flux equality.
```

### Candidate B: convective_flux_matched_damped_outlet

Goal:

```text
Keep convective smoothing while damping the Step129 over-correction and tail
oscillation.
```

Design direction:

```text
convective_raw = old convective extrapolation
regularized_target = regularized_flux_matched target
blend_weight = bounded small adaptive value
repaired = convective_raw + blend_weight * (regularized_target - convective_raw)
```

Requirements:

```text
Initial blend_weight <= 0.05.
If outlet tail CV rises, reduce effective blend.
If mass drift rises while tail is stable, allow slight blend increase.
Do not use the Step129 fixed 0.15 blend for Step130 final behavior.
```

### Optional Candidate C: legacy_unknown_population_targeted_reset

This is diagnostic control only, not the preferred physical candidate.

Requirements:

```text
Reset only unknown x-max populations.
Do not reset all populations.
Do not use it as a physical validation claim unless a future goal explicitly
allows that.
Use it to determine whether the legacy pass is primarily a damping effect.
```

## Phase 3: Step120/Step121 Campaign Surface

Add Step130 specs separated from Step129:

```text
row_role = flow_repair_candidate_48
phase = flowrepair48
```

Expected 250-step triage rows:

```text
duct_only_48_regularized_flux_matched_pressure_outlet_250step_triage
duct_only_48_convective_flux_matched_damped_outlet_250step_triage
optional: duct_only_48_legacy_unknown_population_targeted_reset_250step_triage
```

Expected final 500-step rows only if triage passes:

```text
duct_only_48_regularized_flux_matched_pressure_outlet_500step_real
duct_only_48_convective_flux_matched_damped_outlet_500step_real
optional: duct_only_48_legacy_unknown_population_targeted_reset_500step_real
```

Triage rows must be visibly non-final:

```text
requested_n_steps = 250
row_role = flow_repair_candidate_48
triage = true, or equivalent artifact/report marker
not selected96 enabling evidence
```

## Phase 4: Bounded Parameter Sweep

If Step130 adds a sweep, keep it bounded and artifact-small.

Suggested parameter ranges:

```text
gain_u in {0.005, 0.01, 0.02}
gain_rho in {0.005, 0.01}
blend_weight in {0.02, 0.05, 0.08}
filter_alpha in {0.02, 0.05, 0.10}
correction_cap_u in {0.002, 0.005, 0.01}
```

The implementation may start with one conservative fixed setting per candidate
if a full sweep would overrun the step. If doing that, the report must state
that Step130 ran bounded triage, not an exhaustive sweep.

Relaxed triage gates:

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
```

If no triage candidate passes these relaxed gates, stop at triage and keep
selected96 blocked.

## Phase 5: Final 500-Step Promotion Gate

Promote only the best 1-2 triage candidates to 500-step 48^3 rows, and only
when triage clears the relaxed gates.

Final 500-step acceptance does not relax Step121 hard gates:

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
candidate_mass_acceptance_gate_pass = true
0.80 <= abs(outlet_to_inlet_flux_ratio_tail_mean) <= 1.20
0.80 <= abs(midplane_to_inlet_flux_ratio_tail_mean) <= 1.20
flux_imbalance_rel_tail_mean < 0.10
flux_imbalance_rel_tail_max < 0.20
outlet_flux_tail_cv < 0.10
```

If final 500-step pass occurs, Step130 may report that a future selected 96^3
duct-only goal is allowed. Step130 itself still must not run selected 96^3.

## Phase 6: Required Tests

Add:

```text
tests/test_step130_flow_development_repair_contract.py
```

Minimum coverage:

```text
1. new semantics are accepted by LBMConfig.
2. new semantics dispatch to distinct Step130 kernels or functions.
3. new semantics solver_state_hash differs from Step128/Step129 semantics.
4. flowrepair48 phase is separated from repair48 and candidates48.
5. Step130 diagnostic fields exist.
6. Step130 gain/cap parameters enter solver_state_hash.
7. stale Step129 repaired rows cannot be reused as Step130 rows.
8. Step130 candidates cannot enable selected96 unless final hard gates pass.
```

If a parameter sweep runner is added, also add:

```text
tests/test_step130_parameter_sweep_artifact_contract.py
```

Minimum coverage:

```text
sweep artifacts are bounded-size
triage rows cannot be mistaken as final 500-step acceptance
triage pass does not allow selected96
```

## Phase 7: Step130 Report

Create:

```text
docs/campaigns/fluent_duct_flap/steps/130/report.md
```

The report must compare:

```text
1. Legacy reference passing target behavior.
2. Step127 limited/convective failures.
3. Step129 mass-balanced failures.
4. Step130 flow-repair triage or final candidates.
```

Core comparison fields:

```text
row
semantics
completed
mass_total_delta_rel_final
outlet_to_inlet_flux_ratio_tail_mean
midplane_to_inlet_flux_ratio_tail_mean
flux_imbalance_rel_tail_mean
flux_imbalance_rel_tail_max
outlet_flux_tail_cv
limiter_activation_fraction
repair_correction_abs_sum
selected
```

Decision rules:

```text
If mass improves but flow still fails, do not select.
If ratio passes but outlet CV fails, continue damping/oscillation repair.
If CV passes but ratio fails, continue throughput matching.
Only full hard-gate pass can allow future selected96.
```

## Phase 8: Current Documentation Updates

Update:

```text
docs/current/ACTIVE_CAMPAIGN.json
docs/current/STATUS.md
docs/current/VALIDATION_GATES.md
docs/current/READING_ORDER.md
```

Rules:

```text
If Step130 stops at triage, state that selected96 remains blocked.
If no final 500-step row passes, state that selected96 remains blocked.
If one final 500-step row passes, mark selected96 as allowed only for a future
goal, not as already run.
Keep local pre-push hook evidence distinct from GitHub Actions evidence.
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
  --basetemp outputs\tmp\pytest-step130-final-focused `
  tests\test_step130_flow_development_repair_contract.py `
  tests\test_step130_flow_development_diagnostics_contract.py `
  tests\test_step129_repair_checkpoint_counter_contract.py `
  tests\test_step128_boundary_formulation_repair_contract.py `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py
```

If a sweep runner is added:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step130-sweep `
  tests\test_step130_parameter_sweep_artifact_contract.py
```

Before push:

```powershell
git diff --check
git status --short
git push origin main
git ls-remote origin refs/heads/main
```

Done criteria:

```text
goal/report/code/tests/artifacts/docs are consistent
Step130 artifacts identify Step130 row roles and semantics
triage rows are not treated as selected 96^3 enablers
selected96/quasi2D/FSI/Fluent/Figure29.3 remain blocked unless final hard gates
justify future allowance
final commit is pushed to origin/main
remote main hash is reported
```
