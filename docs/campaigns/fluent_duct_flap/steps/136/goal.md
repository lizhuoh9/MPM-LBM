# Step136 Ramped-Inlet Throughput Calibration Goal

## Source Review

Step136 starts from the post-Step135 review conclusion:

```text
origin/main contains final commit:
c3082cdb8b024bef26833a334dfd5144c469b167
test: record Step135 interior reflection diagnostics
```

Step135 is accepted as bounded real 48^3 / 250-step LBM-only
interior-reflection and bulk-dynamics diagnostic evidence:

```text
6 / 6 planeflux_interior_diag48 rows completed 250 / 250.
All rows stayed finite.
All rows had first_failure_step = null and first_failure_reason = null.
0 / 6 rows passed the relaxed reporting gates.
No Step135 500-step promotion was run.
No selected 96^3 run is allowed.
No quasi-2D, FSI, Fluent, or Figure 29.3 parity claim is allowed.
```

Step135 materially changed the diagnosis. The remaining failure should no
longer be treated as a single outlet-cell readout artifact. The best ramped
branch shows that inlet ramping can remove the compact collapse label and
improve mass / stationarity proxies, but the same branch overdrives
throughput.

Step136 must continue from that evidence without converting diagnostic rows
into selection evidence and without starting selected 96^3 or 500-step work.

## Step135 Technical Finding

The baseline high-frequency regularized Step135 row showed an interior collapse:

```text
collapse_first_x = 24
collapse_first_step = 220
outlet_flux_tail_last_to_mean_ratio = 0.29775218971678935
outlet_flux_tail_slope = -43.49 approximately
x_profile_flux_phase_lag_proxy.collapsed_x includes 24, 30, 36, 42, 45, 46, 47
```

The final profile showed downstream deformation rather than a single outlet
readout collapse:

```text
inlet flux ~= 41.6
midplane flux ~= 29.55
x = 36 flux ~= 24.45
x = 42 flux ~= 14.18
outlet flux ~= 14.71
```

The ramp100 regularized row changed the failure mode:

```text
collapse_first_x = null
collapse_first_step = null
candidate_mass_acceptance_observed_abs = 0.008563736649658519
outlet_flux_tail_cv = 0.06249631177635149
outlet_flux_last_to_tail_mean_ratio = 0.8788833236281177
outlet_to_inlet_flux_ratio_tail_mean = 1.5815747922655192
midplane_to_inlet_flux_ratio_tail_mean = 1.4639728217023902
flux_imbalance_rel_tail_mean = 0.36544508198725295
flux_imbalance_rel_tail_max = 0.4148086159154826
```

Interpretation:

```text
The ramp100 branch removes the compact collapse label and gets mass /
stationarity close, but it fails because the outlet and midplane throughput are
too high relative to inlet and relaxed gate expectations.
```

The niu sensitivity rows do not identify viscosity / relaxation as the primary
fix. `lbm_niu = 0.08` and `lbm_niu = 0.12` both retain the interior collapse at
`x = 24`, step 220, with mass above `0.01` and outlet CV near `0.25`.

## Step136 Objective

Implement and test a bounded 48^3 LBM-only diagnostic phase named:

```text
planeflux_ramp_tuned48
```

The purpose is to calibrate the ramped-inlet branch's throughput behavior while
preserving the stability improvements seen in Step135 ramp100.

Step136 must answer:

1. Does stronger controller feedback reduce outlet/inlet and midplane/inlet
   ratios while preserving mass and stationarity?
2. Does a visible target flux scale reduce flux imbalance without reintroducing
   compact x-profile collapse?
3. Does a shorter ramp, especially ramp75, reduce overdrive while preserving
   the ramp100 stationarity improvement?
4. Does any row pass the relaxed diagnostic reporting gates?
5. Is a later Step137 single 48^3 / 500-step final evidence row justified, or
   does 500-step evidence remain blocked?

Step136 is still diagnostic. A passing row may justify proposing Step137, but
Step136 itself must not run the 500-step row and must not enable selected 96^3.

## Non-Negotiable Scope Boundaries

Step136 must stay inside this envelope:

- Real 48^3 LBM-only rows.
- Maximum 250 steps per 48^3 row.
- Maximum six 48^3 rows.
- Tiny smoke is allowed before real 48^3 execution.
- No selected 96^3 execution.
- No selected-candidate row semantics.
- No 500-step execution.
- No quasi-2D, FSI, Fluent, or Figure 29.3 parity claim.
- No dense-grid dumps or large checkpoint artifacts.
- No hardcoded pressure, velocity, displacement, or flow shortcut that fakes a
  successful jet.
- No relaxation of existing promotion gates.
- No stale Step135 or earlier artifact reuse as Step136 evidence.
- No claim that GitHub Actions validated the run unless actions actually ran.

## Primary Branch

Use the Step135 ramp100 regularized row as the primary branch:

```text
semantics = regularized_plane_flux_controlled_pressure_outlet
ramp_steps = 100
ramp_profile = linear
lbm_niu = 0.10
measure_offset = 2
guard_enabled = true
guard_min_ratio = 0.70
gain_u = 0.25
cap_u = 0.005
gain_rho = 0.001
alpha = 0.02
delta_cap_u = 0.0005
slew_alpha = 0.50
```

This branch is the only observed branch that removes the compact collapse label
and brings mass below `0.01`. The remaining issue is throughput overdrive, not
basic finite stability.

## Controller Authority Sweep

Ramp100 still had controller authority available. Step136 must test whether
stronger negative feedback can bring outlet and midplane ratios back toward the
gate interval while preserving mass and outlet stationarity.

Required bounded controller-authority probes:

```text
gain_u = 0.35, cap_u = 0.005, target_scale = 1.00
gain_u = 0.50, cap_u = 0.005, target_scale = 1.00
gain_u = 0.50, cap_u = 0.0075, target_scale = 1.00
```

Keep these fixed unless the row plan explicitly says otherwise:

```text
ramp_steps = 100
ramp_profile = linear
alpha = 0.02
gain_rho = 0.001
measure_offset = 2
guard_enabled = true
guard_min_ratio = 0.70
lbm_niu = 0.10
```

## Target Flux Scale Surface

Step136 must add a report-visible optional diagnostic parameter:

```text
open_boundary_flux_control_target_scale
```

Default:

```text
1.0
```

When plane-flux outlet control computes the target outlet flux from the inlet
plane, the target must become:

```text
target_outlet_flux = open_boundary_flux_control_target_scale * inlet_flux_plane
```

This is diagnostic only and must be fully visible. It is acceptable because it
tests whether the ramped branch is overdriving the controller target; it must
not be hidden as a success shortcut.

Implementation requirements for target scale:

- Default `1.0` must preserve Step121-Step135 behavior.
- Include the field in solver-state hash / run-manifest identity.
- Include the field in per-row metadata, manifest expected rows, and summary
  diagnostics.
- Include the field in controller diagnostics where target flux is recorded.
- Include tests proving stale Step135 rows cannot be reused as Step136 rows.
- Include tests proving Step136 target-scale rows cannot enable selected 96^3.

Step136 should test bounded target-scale values only:

```text
target_scale = 0.95
target_scale = 0.90
```

`target_scale = 0.85` may remain a later option, but Step136's six-row cap must
not be exceeded.

## Required Six-Row 48^3 Phase

Use:

```text
phase = planeflux_ramp_tuned48
row_role = interior_reflection_diagnostic_48
```

The phase must contain no more than these six real 48^3 rows:

1. ramp100 gain0p35 cap0p005 target1p00,
2. ramp100 gain0p50 cap0p005 target1p00,
3. ramp100 gain0p50 cap0p0075 target1p00,
4. ramp100 gain0p50 cap0p005 target0p95,
5. ramp100 gain0p50 cap0p005 target0p90,
6. ramp75 gain0p50 cap0p005 target1p00.

All rows should use:

```text
grid = 48^3
n_steps = 250
output_interval = 5
lbm_niu = 0.10
measure_offset = 2
guard_enabled = true
guard_min_ratio = 0.70
alpha = 0.02
gain_rho = 0.001
delta_cap_u = 0.0005
slew_alpha = 0.50
```

Row rationale:

```text
Rows 1-3 test controller authority under ramp100.
Rows 4-5 test whether target scaling fixes ratio / imbalance without
reintroducing compact collapse.
Row 6 tests whether a shorter ramp reduces overdrive while preserving
stationarity.
```

No row in this phase may set selected-candidate semantics. No Step136 row may
enter the selected 96^3 candidate set.

## Promotion Gate Handling

Step136 must preserve the existing relaxed diagnostic reporting gates:

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
outlet_flux_last_to_tail_mean_ratio >= 0.70
collapse_first_x = null or collapse_first_step = null
```

If a row passes these gates, Step136 may report it as a candidate for a later
Step137 48^3 / 500-step final evidence row. Step136 itself must not start that
500-step row. Selected 96^3 remains blocked.

## Tiny Smoke Requirement

Before real 48^3 execution, run a tiny smoke using the same Step136 phase:

```text
shape = 8 x 6 x 6
n_steps = 20
ramp_steps = 10 preferred for tiny smoke
gain_u = 0.50
cap_u = 0.005
target_scale = 0.95
```

Smoke artifacts must prove:

- `finite_pass = true`,
- `selected96_claim_allowed = false`,
- target scale appears in diagnostics / metadata,
- ramp settings appear in diagnostics / metadata,
- the Step136 phase does not reuse Step135 artifacts.

## Test Requirements

Add a focused contract test file:

```text
tests/test_step136_ramped_throughput_calibration_contract.py
```

The tests must cover:

- `planeflux_ramp_tuned48` exists and is distinct from Step135
  `planeflux_interior_diag48`.
- The phase contains no more than six rows.
- All Step136 rows are 48^3 / 250-step diagnostic rows.
- All Step136 rows use `row_role = interior_reflection_diagnostic_48`.
- Row identity / manifest expectations encode ramp steps, `gain_u`, `cap_u`,
  and `open_boundary_flux_control_target_scale`.
- `open_boundary_flux_control_target_scale` defaults to `1.0` and preserves
  Step135 / earlier behavior.
- Target scale enters solver-state hash / run-manifest identity.
- Stale Step135 rows cannot be reused for Step136.
- Step136 diagnostic rows cannot enable selected 96^3 even if mocked metrics
  pass.
- Compact x-profile diagnostics remain bounded and schema-stable.
- If target scale is added to `LBMConfig`, Step56 / Step57 / Step58 policy
  guards are updated for default-off or default-neutral behavior.

## Implementation Requirements

The implementation must stay narrow:

- Reuse existing Step120 / Step121 campaign and artifact machinery.
- Keep default behavior unchanged when target scale is `1.0`.
- Keep solver behavior changes limited to the explicit Step136 diagnostic
  target-scale surface and the existing Step135 ramp surface.
- Keep compact x-profile diagnostics from Step135.
- Include new Step136 fields in solver identity where they affect artifacts or
  behavior.
- Keep row names, metadata, and manifests explicit and reproducible.
- Keep tiny-smoke support.
- Keep selected-chain logic unchanged except for tests proving Step136 rows are
  ignored by selection.

Required command surface:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_ramp_tuned48 `
  --output-dir outputs\step136_ramped_throughput_calibration\planeflux_ramp_tuned48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume
```

Use `--force --no-resume` for final provenance generation after the
implementation commit, as in Step134 and Step135.

## Artifact Requirements

Required tiny smoke artifact root:

```text
outputs/step136_ramped_throughput_calibration/tiny_smoke
```

Required 48^3 artifact root:

```text
outputs/step136_ramped_throughput_calibration/planeflux_ramp_tuned48
```

The final report must cite concrete files, including:

- tiny smoke campaign manifest,
- tiny smoke per-row finite report,
- 48^3 campaign manifest,
- 48^3 step summary,
- gate report,
- best-boundary / selection report,
- per-row `flow_development_diagnostics_summary.json`,
- per-row CSV diagnostics where needed.

The report must not rely on console output alone.

## Report Requirements

Create:

```text
docs/campaigns/fluent_duct_flap/steps/136/report.md
```

The report must answer:

1. Did stronger feedback reduce outlet/inlet and midplane/inlet ratios?
2. Did target scale reduce flux imbalance without reintroducing collapse?
3. Did ramp75 reduce overdrive while preserving stationarity?
4. Did any row pass the relaxed diagnostic gates?
5. Is Step137 48^3 / 500-step final evidence justified or still blocked?

The report table must include at minimum:

- row name,
- ramp steps,
- `gain_u`,
- `cap_u`,
- target scale,
- completed steps,
- finite / first-failure status,
- `candidate_mass_acceptance_observed_abs`,
- `outlet_to_inlet_flux_ratio_tail_mean`,
- `midplane_to_inlet_flux_ratio_tail_mean`,
- `flux_imbalance_rel_tail_mean`,
- `flux_imbalance_rel_tail_max`,
- `outlet_flux_tail_cv`,
- `outlet_flux_last_to_tail_mean_ratio`,
- `collapse_first_x`,
- `collapse_first_step`,
- key x-profile tail CV values, especially x24, x36, and x47,
- controller authority / feedback tail behavior when available,
- selected 96^3 claim allowed flag.

Possible report conclusions:

```text
Case A:
gain0.50 / cap0.005 fixes ratios and keeps mass / CV good.
Next step may be Step137 single 48^3 / 500-step final evidence row.
No selected 96^3 yet.

Case B:
target_scale 0.90 or 0.95 fixes ratios and keeps stationarity.
Next step may be Step137 48^3 / 500-step row with target scale documented.

Case C:
all tuned rows reintroduce collapse or remain overdriven.
Step137 should not be 500-step; inspect inlet formulation or bulk
initialization.

Case D:
ramp75 improves ratios but leaves mild stationarity failure.
Next step may sweep ramp duration 75-125 with refined feedback, still
250-step.
```

The conclusion must be artifact-bounded. If evidence remains inconclusive, say
so and recommend the next bounded diagnostic rather than promoting.

## Current Documentation Requirements

After the run, update the current campaign status documents so they state:

- Step135 remains accepted only as bounded 48^3 / 250-step interior reflection
  and bulk-dynamics diagnostic evidence.
- Step136 adds bounded ramped-inlet throughput calibration.
- Whether Step136 supports a later Step137 48^3 / 500-step run.
- selected 96^3 remains blocked unless a later step explicitly changes that
  with artifact-backed evidence.
- GitHub Actions status is not evidence unless actual workflow runs exist.

Files expected to be updated:

```text
docs/current/ACTIVE_CAMPAIGN.json
docs/current/READING_ORDER.md
docs/current/STATUS.md
docs/current/VALIDATION_GATES.md
```

## Verification Commands

Use the trusted Taichi interpreter:

```text
D:\working\taichi\env\python.exe
```

Focused contract and regression verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step136-focused `
  tests\test_step136_ramped_throughput_calibration_contract.py `
  tests\test_step135_interior_reflection_diagnostics_contract.py `
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
```

Policy-guard verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step136-policy `
  tests\test_step56_behavior_preservation_contract.py `
  tests\test_step57_step56_regression_contract.py `
  tests\test_step58_step57_regression_contract.py
```

Compile verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  experiments\steps\step120_lbm_boundary_repair_large_real_execution.py `
  experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py `
  src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py `
  src\mpm_lbm\sim\lbm\fluid.py
```

Artifact verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_ramp_tuned48 `
  --output-dir outputs\step136_ramped_throughput_calibration\tiny_smoke `
  --tiny-smoke `
  --force `
  --no-resume

& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_ramp_tuned48 `
  --output-dir outputs\step136_ramped_throughput_calibration\planeflux_ramp_tuned48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume
```

Final local checks:

```powershell
git diff --check
git diff --cached --check
```

Given repeated full-suite cost in this repo, decomposed verification is
acceptable if reported honestly with exact commands and pass counts.

## Commit and Push Requirements

Use staged commits that preserve reviewability:

```text
docs: add Step136 ramped throughput calibration goal
feat: add Step136 ramp target-scale and throughput calibration phase
test: record Step136 ramped throughput calibration diagnostics
```

Before the final push:

- inspect `git status --short`,
- inspect staged file names,
- ensure generated artifacts and docs match the code commit that produced them,
- ensure no selected 96^3 artifact was created,
- ensure no 500-step Step136 artifact was created,
- ensure no secrets are staged,
- run `git diff --check` / `git diff --cached --check`.

After verification, push to:

```text
origin main
```

The final response must include:

- final commit hash,
- remote branch,
- verification commands and pass counts,
- artifact roots,
- explicit statement that selected 96^3 and 500-step execution remain blocked
  unless a later step authorizes them.
