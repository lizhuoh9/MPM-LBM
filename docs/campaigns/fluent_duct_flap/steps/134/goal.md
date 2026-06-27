# Step134 Outlet Tail-Collapse Diagnosis and Near-Outlet Control-Plane Repair Goal

## Source Review

Step134 starts from the post-Step133 review conclusion:

```text
origin/main contains final commit:
17bbf59c2466e00df3e35df6d6e5ac82e04f63b9
test: record Step133 mass damped plane flux triage
```

The Step133 evidence is accepted only as bounded real 48^3 / 250-step
mass-damped plane-flux triage evidence:

```text
6 / 6 planeflux_mass_damped48 rows completed 250 / 250.
All rows stayed finite.
All rows had first_failure_step = null and first_failure_reason = null.
accepted_row_count = 0.
No 500-step promotion was justified.
selected 96^3 remains blocked.
```

GitHub combined status and workflow runs were empty during the review, so
Step134 must continue treating Step133 verification as local decomposed-suite
evidence plus an honestly reported full-suite timeout, not as GitHub Actions
evidence.

## Step133 Technical Finding

Step133 verified that slow density feedback and simple feedback slew/delta
damping did not solve the remaining failure.

The best Step133 mass row was:

```text
duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_rho0p0005_alpha0p02_du0p0005_slew0p50_250step_triage
semantics = regularized_plane_flux_controlled_pressure_outlet
gain_u = 0.25
cap_u = 0.005
gain_rho = 0.0005
filter_alpha = 0.02
delta_cap_u = 0.0005
slew_alpha = 0.50
```

Observed result:

```text
requested_window_completed = true
steps_completed = 250
finite_pass = true
first_failure_step = null
candidate_mass_acceptance_observed_abs = 0.014184975814691638
flux_imbalance_rel_tail_mean = 0.3987696128026395
flux_imbalance_rel_tail_max = 0.6558913031436817
outlet_to_inlet_flux_ratio_tail_mean = 1.0280528796842723
midplane_to_inlet_flux_ratio_tail_mean = 0.9111280219154153
outlet_flux_tail_cv = 0.47087164136218246
```

Interpretation:

```text
Mean outlet/inlet and midplane/inlet ratios are already near the desired range.
Mass acceptance is still above the relaxed < 0.01 threshold.
The decisive blockers are outlet_flux_tail_cv, flux_imbalance_tail_max,
flux_imbalance_tail_mean, and late-tail outlet collapse.
```

The best regularized branch has the following late-tail outlet behavior:

```text
step 200 outlet flux ~= 58.49
step 225 outlet flux ~= 55.08
step 250 outlet flux ~= 14.31
```

This indicates a late-window outlet stationarity failure, not a basic finite
stability failure and not a controller sign-disconnection failure.

The best Step133 flux-imbalance row was the convective diagnostic comparator:

```text
duct_only_48_convective_plane_flux_controlled_damped_gain0p10_cap0p002_rho0p001_alpha0p02_du0p0005_slew0p50_250step_triage
candidate_mass_acceptance_observed_abs = 0.022125313054974453
flux_imbalance_rel_tail_mean = 0.2630888340905568
outlet_to_inlet_flux_ratio_tail_mean = 1.408879778823433
midplane_to_inlet_flux_ratio_tail_mean = 1.2372221853054948
outlet_flux_tail_cv = 0.20262416501645636
```

It is not a selected boundary. It remains diagnostic only.

## Step134 Objective

Implement and test a bounded 48^3 LBM-only Step134 phase named:

```text
planeflux_stationarity48
```

The technical objective is:

```text
Diagnose and repair late-tail outlet flux collapse / outlet stationarity
failure in 48^3 LBM-only triage by adding compact near-outlet flux diagnostics,
a configurable controller measurement-plane offset, and an optional outlet
flux drop guard.
```

Step134 is a triage and diagnostic-repair step. It does not authorize selected
96^3. It does not authorize 500-step evidence unless a 250-step Step134 row
first passes the explicit relaxed promotion gates in this file.

## Non-Negotiable Scope Boundary

Step134 may:

- Add this checked-in goal file and an active goal that references it.
- Add compact stationarity/root-cause diagnostics to bounded CSV/JSON
  artifacts.
- Add a config field for controller measurement plane:

```text
open_boundary_flux_control_measure_plane_offset
```

- Add optional outlet flux anti-collapse guard fields:

```text
open_boundary_outlet_flux_drop_guard_enabled
open_boundary_outlet_flux_drop_guard_min_ratio
```

- Add these fields to solver-state identity and Step row metadata.
- Keep default behavior identical to Step131-Step133 when fields are unset.
- Add a distinct Step121 phase named `planeflux_stationarity48`.
- Add at most six bounded 48^3 / 250-step Step134 triage specs.
- Add focused Step134 contract tests.
- Run a tiny real smoke before any 48^3 Step134 run.
- Run bounded 48^3 / 250-step Step134 triage only after tests and tiny smoke
  pass.
- Write a Step134 report and update current docs after artifacts are produced.
- Commit and push verified code, tests, docs, and generated artifacts to
  `origin/main`.

Step134 must not:

- Run selected 96^3 duct rows.
- Run selected 96^3 static rows.
- Run quasi-2D rows.
- Run FSI rows.
- Claim Fluent validation.
- Claim Figure 29.3 parity.
- Relax Step121/Step124 hard gates.
- Reclassify Step127 through Step133 artifacts.
- Delete or rewrite earlier Step artifacts.
- Touch vendored `external/taichi_LBM3D`.
- Add a new selected-candidate semantics surface.
- Run 500-step promotion unless a Step134 250-step row clears the explicit
  relaxed promotion gates below.

## Phase 1: Stationarity Root-Cause Diagnostics

Add compact diagnostics, not dense arrays:

```text
tail_outlet_flux_values
tail_inlet_flux_values
tail_midplane_flux_values
outlet_flux_tail_slope
outlet_flux_tail_drop_ratio
outlet_flux_tail_last_to_mean_ratio
near_outlet_flux_xminus1
near_outlet_flux_xminus2
near_outlet_flux_xminus3
near_outlet_to_outlet_flux_ratio
controller_feedback_last_to_tail_mean
density_feedback_last_to_tail_mean
outlet_rho_last
outlet_rho_tail_mean
outlet_ux_min_last
outlet_ux_negative_fraction_last
```

The key new diagnostic is:

```text
near_outlet_flux_xminus2
```

Reason:

```text
Step131-Step133 measured outlet control at x = nx - 1. The failure pattern may
come from controlling the actual outlet plane after boundary reconstruction
while the near-outlet interior x = nx - 2 carries a different flux state.
If x = nx - 2 remains healthy while x = nx - 1 collapses, the issue is outlet
reconstruction. If both collapse, inspect interior wave/reflection behavior.
```

The diagnostic surface must stay bounded-size. Store tail values as a short
fixed-length list derived from the existing sampled diagnostics, not as dense
grid arrays.

## Phase 2: Measurement-Plane Offset

Reuse Step131-Step133 plane-flux semantics. Do not add a new selected-candidate
semantics concept.

Add:

```text
open_boundary_flux_control_measure_plane_offset
```

Allowed values:

```text
0 -> measure x = nx - 1 outlet plane
1 -> measure x = nx - 2 near-outlet plane
2 -> measure x = nx - 3 near-outlet plane
```

Default:

```text
open_boundary_flux_control_measure_plane_offset = 0
```

The default must preserve Step131-Step133 behavior.

Include this field in:

```text
LBMConfig
validation
solver_state_hash
driver_config
run_metadata
finite_stability_report
boundary reports where relevant
flow-development diagnostics
summary rows
Step134 contract tests
```

Step134 rows should test offset `1` first, because the main hypothesis is that
the actual outlet plane and the near-outlet interior plane diverge late.

## Phase 3: Outlet Flux Drop Guard

For the best regularized branch, the controller may over-correct until the
outlet flux collapses late. Add an optional stationarity guard:

```text
open_boundary_outlet_flux_drop_guard_enabled
open_boundary_outlet_flux_drop_guard_min_ratio
```

Conservative defaults:

```text
open_boundary_outlet_flux_drop_guard_enabled = false
open_boundary_outlet_flux_drop_guard_min_ratio = 0.60
```

The default must preserve Step131-Step133 behavior.

When enabled, the guard should prevent further negative feedback escalation
when the measured outlet flux has already collapsed:

```text
if measured_outlet_flux_current < min_ratio * reference_or_filtered_target_flux:
    do not further decrease u_feedback
    optionally relax negative feedback toward zero
```

The guard must be bounded and reportable:

```text
drop_guard_active
drop_guard_activation_count
drop_guard_min_ratio
drop_guard_reference_flux
drop_guard_measured_flux
drop_guard_feedback_before
drop_guard_feedback_after
```

It must not be a hidden pressure/velocity shortcut. It is an outlet stationarity
protection probe inside the already bounded plane-flux controller surface.

## Phase 4: Candidate Rows

Use row role:

```text
plane_flux_control_candidate_48
```

Use phase:

```text
planeflux_stationarity48
```

Use row names or manifest metadata that encode:

```text
offset
guard_on/off
guard_min_ratio
gain_u
cap_u
gain_rho
alpha
delta_cap_u
slew_alpha
```

Primary baseline is the best Step133 regularized row:

```text
semantics = regularized_plane_flux_controlled_pressure_outlet
gain_u = 0.25
cap_u = 0.005
gain_rho = 0.0005
filter_alpha = 0.02
delta_cap_u = 0.0005
slew_alpha = 0.50
```

Initial max-six-row plan:

```text
1. regularized offset1 guard_off min0p60 alpha0p02
2. regularized offset1 guard_on  min0p50 alpha0p02
3. regularized offset1 guard_on  min0p70 alpha0p02
4. regularized offset1 guard_on  min0p70 alpha0p01
5. regularized offset2 guard_on  min0p70 alpha0p02
6. convective diagnostic offset1 guard_on min0p70 gain0p10 cap0p002
```

The convective row is diagnostic-only. The regularized surface remains the
primary Step134 repair candidate unless evidence says otherwise.

## Phase 5: Step134 Tests

Create:

```text
tests/test_step134_outlet_stationarity_contract.py
```

Required coverage:

1. `planeflux_stationarity48` exists and is separate from
   `planeflux_mass_damped48`, `planeflux_sweep48`, and `planeflux48`.
2. The six Step134 specs are 48^3 / 250-step triage rows with
   `row_role = plane_flux_control_candidate_48`.
3. Row names or manifest metadata encode offset and guard params.
4. `open_boundary_flux_control_measure_plane_offset`,
   `open_boundary_outlet_flux_drop_guard_enabled`, and
   `open_boundary_outlet_flux_drop_guard_min_ratio` enter
   `solver_state_hash`.
5. Stale Step133 rows cannot be reused as Step134 rows.
6. Diagnostics contain near-outlet flux and outlet-tail collapse fields.
7. Rows cannot enable selected96, even with good mocked metrics.
8. Defaults preserve Step133 behavior when offset is 0 and guard is disabled.
9. Bounded CSV/JSON diagnostics remain controlled-size and do not contain dense
   per-cell arrays.

If config defaults change, include Step56/57/58 policy guards in focused
verification.

## Phase 6: Tiny Smoke

Before 48^3, run a tiny real smoke:

```text
nx = 8
ny = 6
nz = 6
n_steps = 20
semantics = regularized_plane_flux_controlled_pressure_outlet
gain_u = 0.25
cap_u = 0.005
gain_rho = 0.0005
filter_alpha = 0.02
delta_cap_u = 0.0005
slew_alpha = 0.50
open_boundary_flux_control_measure_plane_offset = 1
open_boundary_outlet_flux_drop_guard_enabled = true
open_boundary_outlet_flux_drop_guard_min_ratio = 0.70
```

Expected smoke checks:

```text
requested_window_completed = true
finite_pass = true
first_failure_step = null
controller fields finite
near-outlet diagnostics present
drop-guard diagnostics present
validation_claim_allowed = false
selected96_claim_allowed = false
```

If the tiny smoke fails, stop and report honestly. Do not hide failure by
relaxing gates.

## Phase 7: Bounded 48^3 Triage Run

Run only after tests and tiny smoke pass:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_stationarity48 `
  --output-dir outputs\step134_outlet_stationarity_repair\planeflux_stationarity48 `
  --allow-large-real-rows `
  --output-interval 25
```

Avoid `--force` by default because these should be new row names. If stale
artifacts require `--force`, explain why in the report.

## Phase 8: Relaxed Triage Gate for Possible Later 500-Step Promotion

A Step134 row may be considered for a later 500-step 48^3 final row only if it
passes all of:

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
outlet_flux_tail_last_to_mean_ratio >= 0.70
abs(outlet_flux_tail_slope) below a documented threshold
0.10 <= controller_authority_ratio_tail_mean <= 0.95
controller_saturation_fraction_tail < 0.80
```

If no row passes, stop triage. Do not run 500-step final evidence. Do not run
selected 96^3.

## Phase 9: Outcome Interpretation

Interpret Step134 outcomes as follows:

```text
Case A: offset1 fixes outlet CV / flux max but mass remains > 0.01
=> Next step may combine offset1 with stronger mass coupling or near-outlet
   density feedback, but selected96 remains blocked.

Case B: guard fixes collapse but outlet ratio drifts high
=> Guard is too aggressive; lower min_ratio or reduce feedback cap.

Case C: offset1 and guard do not change tail collapse
=> Failure is not mainly measurement-plane mismatch; inspect interior
   reflection / bulk relaxation.

Case D: regularized row passes relaxed gates
=> Next step is 500-step 48^3 final evidence, not selected96.

Case E: convective diagnostic wins only on CV but ratio/mass fail
=> Keep it diagnostic; do not select it.
```

## Required Step134 Report

Create:

```text
docs/campaigns/fluent_duct_flap/steps/134/report.md
```

The report must include:

```text
- Step133 baseline and tail-collapse time series.
- Exact Step134 code/config/test surface.
- Tiny smoke command and result.
- 48^3 triage command and force/no-force status.
- Per-row parameter table:
  semantics, offset, guard, min_ratio, gain_u, cap_u, gain_rho, alpha,
  delta_cap_u, slew_alpha.
- Per-row outcome table:
  completed steps, first failure, mass acceptance, outlet/inlet ratio,
  mid/inlet ratio, flux mean/max, outlet CV,
  outlet_flux_tail_last_to_mean_ratio, outlet_flux_tail_slope,
  near_outlet_to_outlet_flux_ratio, controller authority/saturation,
  density feedback, guard activation count.
- accepted_row_count.
- promotion_to_500step_allowed decision.
- selected96_claim_allowed decision.
- Verification commands and pass counts.
- Explicit statement that no Fluent/Figure29.3/quasi2D/FSI claim is made.
```

## Verification

Use the trusted interpreter:

```text
D:\working\taichi\env\python.exe
```

Minimum focused verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\lbm\config.py `
  src\mpm_lbm\sim\lbm\fluid.py `
  src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py `
  experiments\steps\step118_lbm_open_boundary_stability_repair.py `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py `
  tests\test_step134_outlet_stationarity_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step134-focused `
  tests\test_step134_outlet_stationarity_contract.py `
  tests\test_step133_mass_damped_plane_flux_contract.py `
  tests\test_step132_plane_flux_authority_sweep_contract.py `
  tests\test_step131_plane_flux_controller_contract.py `
  tests\test_step130_flow_development_diagnostics_contract.py `
  tests\test_step129_repair_checkpoint_counter_contract.py `
  tests\test_step128_boundary_formulation_repair_contract.py `
  tests\test_step125_campaign_provenance_identity_contract.py `
  tests\test_step124_boundary_campaign_execution_contract.py `
  tests\test_step123_boundary_campaign_execution_decision_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step56_behavior_preservation_contract.py `
  tests\test_step57_step56_regression_contract.py `
  tests\test_step58_step57_regression_contract.py
```

Given Step133's full-suite timeout, either run the full suite with a larger
timeout or explicitly use the same decomposed verification strategy and report
it honestly.

Run before push:

```powershell
git diff --check
```

## Recommended Commit Structure

Prefer:

```text
docs: add Step134 outlet stationarity goal
feat/test: add Step134 near-outlet stationarity diagnostics and control-plane options
test: run Step134 outlet stationarity 48 triage
```

Combining adjacent commits is acceptable if the final history remains clear
and the report is exact.

## Completion Definition

Step134 is complete only when:

```text
- This detailed goal file is checked in and the active goal references it.
- Step134 contract tests are added and pass.
- Near-outlet flux diagnostics are implemented through bounded CSV/JSON
  artifact surfaces.
- Measurement-plane offset is implemented with default offset 0 preserving
  Step133 behavior.
- Outlet flux drop guard is implemented as opt-in, bounded, and reportable.
- Tiny smoke is run and recorded.
- Step134 48^3 / 250-step triage is run only after tests/smoke pass.
- Step134 report records exact outcomes and claim boundaries.
- Current docs are updated with the Step134 outcome.
- Full verification or decomposed verification is reported honestly.
- Final code/docs/artifacts are committed and pushed to origin/main.
- Final response reports final commit hash, branch/remote proof, pass counts,
  and whether selected 96^3 remains blocked.
```
