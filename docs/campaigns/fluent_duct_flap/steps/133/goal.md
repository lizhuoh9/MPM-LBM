# Step133 Slow Density Feedback and Outlet Stationarity Repair Goal

## Source Review

Step133 starts from the post-Step132 review conclusion:

```text
origin/main contains final commit:
73e6fe111cb02ba94345a2b4e00a9250fe926ddf
test: record Step132 plane flux authority sweep

Step132 is accepted as real 48^3 / 250-step controller-authority sweep
evidence.
```

The accepted Step132 evidence is bounded:

```text
6 / 6 planeflux_sweep48 rows completed 250 / 250.
All rows stayed finite.
All rows had first_failure_step = null and first_failure_reason = null.
accepted_row_count = 0.
No 500-step promotion was justified.
selected 96^3 remains blocked.
```

Step132 local verification and pre-push evidence are local machine evidence, not
GitHub Actions evidence. GitHub status and workflow runs were empty during the
review. Step133 reports must keep that distinction explicit.

## Mandatory Phase 0 Docs Fix

Before Step133 implementation claims are made, fix the current read-first docs
that still point to Step131:

```text
docs/current/ACTIVE_CAMPAIGN.json
docs/current/READING_ORDER.md
```

Required `ACTIVE_CAMPAIGN.json` update:

```text
current_code_commit = 4e358d43ac86a5e520b82838f4f2e1a218ca3ef9
read_first includes docs/campaigns/fluent_duct_flap/steps/132/goal.md
read_first includes docs/campaigns/fluent_duct_flap/steps/132/report.md
```

Required `READING_ORDER.md` update:

```text
Include Step132 goal/report in the current read-first order.
State that Step132 completed six real 48^3 / 250-step authority-sweep rows.
State that no Step132 row was accepted.
State that no 500-step promotion or selected 96^3 run is justified.
```

This is a docs-only consistency patch. It must not change validation gates or
reinterpret Step132 as repaired 48^3 acceptance evidence.

## Step132 Baseline for Step133

The best Step132 starting surface is:

```text
semantics = regularized_plane_flux_controlled_pressure_outlet
gain_u = 0.25
cap_u = 0.005
filter_alpha = 0.02
convective_blend_weight = 0.02
gain_rho = 0.0
row = duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_250step_triage
```

Observed Step132 result for that row:

```text
requested_window_completed = true
steps_completed = 250
finite_pass = true
first_failure_step = null
candidate_mass_acceptance_observed_abs = 0.014016928659457415
flow_development_gate_pass = false
flux_imbalance_rel_tail_mean = 0.39506523169401825
flux_imbalance_rel_tail_max = 0.6458331484894854
outlet_to_inlet_flux_ratio_tail_mean = 1.0307369515412572
midplane_to_inlet_flux_ratio_tail_mean = 0.9160340533832297
outlet_flux_tail_cv = 0.46453328972807856
controller_authority_ratio_tail_mean = 0.43761600585033494
controller_saturation_fraction_tail = 0.0
```

Interpretation:

```text
Velocity feedback authority was no longer disconnected.
Mass acceptance still failed.
Outlet stationarity was poor, especially outlet_flux_tail_cv.
The next bounded repair should add slow density/mass coupling and damp
controller step-to-step stationarity.
```

## Step133 Objective

Implement and test a bounded 48^3 LBM-only Step133 phase named:

```text
planeflux_mass_damped48
```

The technical objective is:

```text
Starting from the best Step132 regularized plane-flux controller surface, add a
slow density feedback channel and an outlet velocity-feedback slew/delta cap so
mass drift and outlet stationarity can be diagnosed without widening the
validation claim surface.
```

Step133 is a triage and diagnostic step. It does not authorize selected 96^3.

## Non-Negotiable Scope Boundary

Step133 may:

- Add this checked-in goal file and an active goal that references it.
- Patch the Step132 current-doc read-first drift.
- Add Step133 config fields for controller stationarity damping:

```text
open_boundary_flux_feedback_delta_cap_u
open_boundary_flux_feedback_slew_alpha
```

- Use the existing `open_boundary_flux_feedback_gain_rho` surface as slow
  density feedback.
- Add Step133 diagnostics to bounded flow-development CSV/JSON artifacts.
- Add a distinct Step121 phase named `planeflux_mass_damped48`.
- Add at most six bounded 48^3 / 250-step triage specs.
- Add focused Step133 contract tests.
- Run a tiny real smoke before 48^3.
- Run bounded 48^3 / 250-step Step133 triage only after tests/smoke pass.
- Write a Step133 report and current-doc update.
- Commit and push verified code, tests, docs, and generated artifacts to
  `origin/main`.

Step133 must not:

- Run selected 96^3 duct rows.
- Run selected 96^3 static rows.
- Run quasi-2D rows.
- Run FSI rows.
- Claim Fluent validation.
- Claim Figure 29.3 parity.
- Relax Step121/Step124 hard gates.
- Reclassify Step127 through Step132 artifacts.
- Delete or rewrite earlier Step artifacts.
- Touch vendored `external/taichi_LBM3D`.
- Add a new boundary-condition semantics concept by default.
- Run a 500-step promotion unless a Step133 250-step row clears the explicit
  relaxed triage gates below.

## Controller Formula

Keep the Step131/Step132 plane-integrated flux controller as the base:

```text
target_outlet_flux = inlet_flux_plane
measured_outlet_flux = outlet_flux_plane
raw_error = target_outlet_flux - measured_outlet_flux
filtered_error = low_pass(raw_error)
requested_u_feedback = gain_u * filtered_error / outlet_fluid_area
bounded_u_feedback = clamp(requested_u_feedback, -cap_u, cap_u)
```

Add stationarity damping:

```text
previous_feedback = controller_u_feedback_previous
bounded_feedback = clamp(requested_feedback, -cap_u, cap_u)

if delta_cap_u > 0:
    delta_limited_feedback = previous_feedback + clamp(
        bounded_feedback - previous_feedback,
        -delta_cap_u,
        +delta_cap_u
    )
else:
    delta_limited_feedback = bounded_feedback

final_feedback = previous_feedback + slew_alpha * (
    delta_limited_feedback - previous_feedback
)
```

Default behavior must preserve Step131/Step132 when the new fields are left at
defaults:

```text
open_boundary_flux_feedback_delta_cap_u = 0.0
open_boundary_flux_feedback_slew_alpha = 1.0
```

Add slow density feedback using existing `gain_rho`:

```text
requested_rho_feedback = gain_rho * filtered_error / outlet_fluid_area
density_feedback = clamp(requested_rho_feedback, -0.01, +0.01)
repaired_rho = outlet_target_rho + density_feedback
```

This density channel is intentionally slow. It is a bounded mass-coupling probe,
not a hidden pressure shortcut.

## Candidate Rows

Use row role:

```text
plane_flux_control_candidate_48
```

Use phase:

```text
planeflux_mass_damped48
```

Use row names or manifest metadata that encode `gain_rho`, `filter_alpha`,
`delta_cap_u`, and `slew_alpha`.

Initial max-six-row plan:

```text
1. regularized gain_u=0.25 cap_u=0.005 gain_rho=0.0005 alpha=0.02
   delta_cap_u=0.0005 slew_alpha=0.50

2. regularized gain_u=0.25 cap_u=0.005 gain_rho=0.0010 alpha=0.02
   delta_cap_u=0.0005 slew_alpha=0.50

3. regularized gain_u=0.25 cap_u=0.005 gain_rho=0.0020 alpha=0.02
   delta_cap_u=0.0005 slew_alpha=0.50

4. regularized gain_u=0.25 cap_u=0.005 gain_rho=0.0010 alpha=0.01
   delta_cap_u=0.00025 slew_alpha=0.50

5. regularized gain_u=0.25 cap_u=0.005 gain_rho=0.0010 alpha=0.005
   delta_cap_u=0.00025 slew_alpha=0.25

6. convective gain_u=0.10 cap_u=0.002 gain_rho=0.0010 alpha=0.02
   delta_cap_u=0.0005 slew_alpha=0.50 diagnostic-only comparator
```

The convective row is diagnostic-only. The regularized surface remains the
primary Step133 repair candidate unless evidence says otherwise.

## Required Diagnostics

Add these bounded diagnostics to the flow-development summary surface:

```text
mass_drift_tail_mean
mass_drift_tail_slope
density_feedback_tail_mean
density_feedback_tail_abs_max
rho_outlet_tail_mean
rho_outlet_tail_std
controller_u_feedback_tail_std
controller_feedback_sign_change_count_tail
outlet_flux_tail_cv
outlet_flux_tail_slope
```

Per-record diagnostics should include:

```text
step133_mass_damped_candidate
controller_density_feedback
controller_density_feedback_abs
controller_delta_cap_u
controller_slew_alpha
outlet_plane_rho_mean
outlet_plane_rho_std
```

The CSV/JSON artifacts must stay bounded-size and report-only:

```text
validation_claim_allowed = false
selected96_claim_allowed = false
```

## Step133 Tests

Create:

```text
tests/test_step133_mass_damped_plane_flux_contract.py
```

Required coverage:

1. `planeflux_mass_damped48` exists and is separate from
   `planeflux_sweep48`.
2. The sweep rows encode `gain_rho` and damping params in row names or manifest
   metadata.
3. `open_boundary_flux_feedback_gain_rho`,
   `open_boundary_flux_feedback_delta_cap_u`, and
   `open_boundary_flux_feedback_slew_alpha` enter `solver_state_hash`.
4. Stale Step132 rows cannot be reused as Step133 rows.
5. Rows remain non-selected96 triage rows.
6. Density feedback diagnostics exist in per-record and summary surfaces.
7. Authority diagnostics remain bounded-size.
8. No selected96 spec can be created from Step133 triage rows.

Use TDD: add the failing Step133 contract first, then implement the minimal
code surface to pass it.

## Tiny Smoke

Before 48^3, run a tiny real smoke:

```text
nx = 8
ny = 6
nz = 6
n_steps = 20
semantics = regularized_plane_flux_controlled_pressure_outlet
gain_u = 0.25
cap_u = 0.005
gain_rho = 0.001
filter_alpha = 0.01
delta_cap_u = 0.0005
slew_alpha = 0.50
```

Expected smoke checks:

```text
requested_window_completed = true
finite_pass = true
first_failure_step = null
abs(controller_u_feedback) <= cap_u
abs(controller_density_feedback) <= 0.01
flow_development_diagnostics_summary.step = 133
validation_claim_allowed = false
selected96_claim_allowed = false
```

If the tiny smoke fails, stop and report honestly. Do not hide failure by
relaxing gates.

## Bounded 48^3 Triage Run

Run only after tests and tiny smoke pass:

```powershell
& 'D:\working\taichi\env\python.exe' -m `
  experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_mass_damped48 `
  --allow-large-real-rows `
  --output-interval 25
```

Do not use `--force` by default. If stale artifacts require `--force`, explain
why in the report.

## Relaxed Triage Gate for Possible Later 500-Step Promotion

A Step133 row may be considered for a later 500-step 48^3 final row only if it
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
0.10 <= controller_authority_ratio_tail_mean <= 0.95
controller_saturation_fraction_tail < 0.80
```

If no row passes, stop triage. Do not run 500-step final evidence. Do not run
selected 96^3.

## Required Step133 Report

Create:

```text
docs/campaigns/fluent_duct_flap/steps/133/report.md
```

The report must include:

```text
- Step132 accepted baseline and exact starting row.
- Phase 0 docs-fix summary.
- Exact Step133 code/config/test surface.
- Tiny smoke command and result.
- 48^3 triage command and force/no-force status.
- Per-row parameter table:
  semantics, gain_u, cap_u, gain_rho, alpha, delta_cap_u, slew_alpha.
- Per-row outcome table:
  completed steps, first failure, mass acceptance, flux ratios, flux imbalance,
  outlet CV, density feedback, outlet rho mean/std, controller feedback std,
  sign-change count, saturation fraction.
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
  tests\test_step133_mass_damped_plane_flux_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step133-focused `
  tests\test_step133_mass_damped_plane_flux_contract.py `
  tests\test_step132_plane_flux_authority_sweep_contract.py `
  tests\test_step131_plane_flux_controller_contract.py `
  tests\test_step130_flow_development_diagnostics_contract.py
```

Run the full suite before push:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step133-final-all

git diff --check
```

## Recommended Commit Structure

Prefer:

```text
docs: update Step132 active campaign reading order
docs: add Step133 mass damped plane flux goal
feat/test: add Step133 slow density feedback and stationarity diagnostics
test: run Step133 mass damped plane flux 48 triage
```

Combining adjacent docs commits is acceptable if the final history remains
clear and the report is exact.

## Completion Definition

Step133 is complete only when:

```text
- This detailed goal file is checked in and the active goal references it.
- Current docs point to Step132 goal/report before Step133 work is claimed.
- Step133 contract tests are added and pass.
- Slow density feedback and stationarity damping are implemented through
  bounded config fields and solver-state hash identity.
- Tiny smoke is run and recorded.
- Step133 48^3 / 250-step triage is run only after tests/smoke pass.
- Step133 report records exact outcomes and claim boundaries.
- Current docs are updated with the Step133 outcome.
- Full verification passes or any failure is explicitly reported.
- Final code/docs/artifacts are committed and pushed to origin/main.
- Final response reports final commit hash, branch/remote proof, pass counts,
  and whether selected 96^3 remains blocked.
```
