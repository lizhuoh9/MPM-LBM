# Step138 High-Authority Outlet Diagnostic Goal

## Source Review

Step138 starts from the post-Step137 review conclusion:

```text
origin/main contains final commit:
e273825e9e68480218510bfdd2dd47d7c5949dcd
test: record Step137 ramp-target refinement diagnostics
```

Step137 is accepted only as bounded real 48^3 / 250-step LBM-only
diagnostic evidence for:

```text
phase = planeflux_ramp_refined48
semantics = regularized_plane_flux_controlled_pressure_outlet
row_role = interior_reflection_diagnostic_48
```

The accepted Step137 evidence is narrow:

```text
6 / 6 real 48^3 rows completed 250 / 250.
All rows stayed finite.
All rows had first_failure_step = null and first_failure_reason = null.
6 / 6 rows passed candidate mass acceptance.
6 / 6 rows avoided the compact x-profile collapse label.
0 / 6 rows passed the final hard flow-development gate.
No 500-step promotion row was run.
No selected 96^3 run is allowed.
No quasi-2D, FSI, Fluent, or Figure 29.3 parity claim is allowed.
```

The best Step137 outlet-ratio row was:

```text
ramp_steps = 85
target_scale = 0.85
gain_u = 0.50
cap_u = 0.005
outlet_to_inlet_flux_ratio_tail_mean = 1.246561166160358
midplane_to_inlet_flux_ratio_tail_mean = 1.1418110718950278
flux_imbalance_rel_tail_mean = 0.19102045308771165
flux_imbalance_rel_tail_max = 0.29227885610916315
outlet_flux_tail_cv = 0.09162197337437686
controller_authority_ratio_tail_mean = 0.952345
```

The best Step137 mass row was:

```text
ramp_steps = 90
target_scale = 0.80
gain_u = 0.50
cap_u = 0.005
candidate_mass_acceptance_observed_abs = 0.0006162400457775661
outlet_to_inlet_flux_ratio_tail_mean = 1.2636158741752672
midplane_to_inlet_flux_ratio_tail_mean = 1.170339464016481
flux_imbalance_rel_tail_mean = 0.20201121638125025
```

Interpretation:

```text
Step137 moved mass acceptance, outlet stationarity, and compact-collapse
diagnostics into a much better regime, but outlet over-throughput and flux
imbalance still failed the final hard gates.

Lower target scale alone was not sufficient. The best outlet-ratio row had
controller authority near the existing cap, so Step138 must test whether higher
feedback authority and higher correction cap can reduce outlet ratio and flux
imbalance without reintroducing compact collapse or numerical failure.
```

Step138 must not reinterpret Step137 as repaired-candidate success. Step137
does not justify a 48^3 / 500-step final-evidence run, and it does not justify
selected 96^3.

## Step138 Objective

Implement and run a bounded 48^3 / 250-step LBM-only diagnostic phase named:

```text
planeflux_high_authority48
```

The objective is to answer one narrow question:

```text
Does higher plane-flux feedback gain or correction cap bring outlet ratio and
flux-imbalance metrics inside the final hard gates, while preserving Step137's
finite state, candidate mass acceptance, and no-compact-collapse behavior?
```

Step138 must distinguish these possibilities:

1. Higher gain at the same cap improves ratio and imbalance.
2. Higher cap is required because the Step137 best row was near the authority
   ceiling.
3. Lower target scale only helps when paired with higher authority.
4. Higher authority reintroduces compact collapse or instability.
5. The scalar plane-flux controller remains insufficient even with higher gain
   and cap, implying a later ratio-coupled or pressure-coupled formulation is
   needed.

Step138 is still diagnostic-only. It may recommend a later Step139 single-row
48^3 / 500-step final-evidence run only if a Step138 row passes the final hard
gates listed below. Step138 itself must not run 500 steps and must not enable
selected 96^3.

## Non-Negotiable Scope Boundaries

Step138 must stay inside this envelope:

- Real 48^3 LBM-only rows.
- Maximum 250 steps per 48^3 row.
- Maximum six real 48^3 rows.
- Tiny smoke is allowed before real 48^3 execution.
- No selected 96^3 execution.
- No selected-candidate row semantics.
- No 500-step execution.
- No quasi-2D validation claim.
- No FSI validation claim.
- No Fluent validation claim.
- No Figure 29.3 parity claim.
- No gate relaxation.
- No dense-grid dumps or large checkpoint artifacts.
- No hardcoded pressure, velocity, displacement, or flow shortcut that fakes a
  successful jet.
- No stale Step137 or earlier artifact reuse as Step138 evidence.
- No claim that GitHub Actions validated the run unless actions actually ran.

If all six Step138 rows fail the final hard gates, the correct conclusion is
continued selected-boundary blocked state, not promotion.

## Boundary Semantics

Reuse the existing diagnostic boundary semantics:

```text
semantics = regularized_plane_flux_controlled_pressure_outlet
row_role = interior_reflection_diagnostic_48
```

Do not add Step138 rows to:

```text
CANDIDATE_SEMANTICS
REPAIRED_CANDIDATE_SEMANTICS
```

Do not alter selected-chain logic except for tests proving Step138 rows remain
blocked from selected 96^3 claims even when mocked metrics pass.

## Required Six-Row 48^3 Phase

Add:

```text
phase = planeflux_high_authority48
row_role = interior_reflection_diagnostic_48
```

The phase must contain exactly these six real 48^3 rows:

1. `ramp85 target0.85 gain0.75 cap0.0050`,
2. `ramp85 target0.85 gain0.75 cap0.0075`,
3. `ramp85 target0.85 gain1.00 cap0.0075`,
4. `ramp85 target0.85 gain1.00 cap0.0100`,
5. `ramp85 target0.80 gain0.75 cap0.0075`,
6. `ramp90 target0.80 gain0.75 cap0.0075`.

All rows must use:

```text
grid = 48^3
n_steps = 250
output_interval = 5
lbm_niu = 0.10
target semantics = regularized_plane_flux_controlled_pressure_outlet
measure_offset = 2
guard_enabled = true
guard_min_ratio = 0.70
ramp_profile = linear
gain_rho = 0.001
alpha = 0.02
delta_cap_u = 0.0005
slew_alpha = 0.50
```

Row rationale:

```text
Rows 1-2 isolate cap effect at gain0.75 for the Step137 best outlet-ratio
baseline.

Rows 3-4 test whether stronger gain plus higher cap can move outlet ratio and
flux imbalance across final hard gates.

Row 5 tests whether the Step137 lower-target mass win becomes useful only when
paired with higher authority.

Row 6 keeps the Step137 best mass ramp/target pair and raises authority for a
ramp90 comparison.
```

Suggested row-name tokens:

```text
ramp85_target0p85_gain0p75_cap0p005
ramp85_target0p85_gain0p75_cap0p0075
ramp85_target0p85_gain1p00_cap0p0075
ramp85_target0p85_gain1p00_cap0p0100
ramp85_target0p80_gain0p75_cap0p0075
ramp90_target0p80_gain0p75_cap0p0075
```

No row in this phase may set selected-candidate semantics. No Step138 row may
enter the selected 96^3 candidate set.

## Ratio-Coupled Control Boundary

Step138 should not introduce a new ratio-coupled control law unless the
implementation needs a report-visible placeholder to reserve the future
interface. The first Step138 run should prioritize the cleaner high-authority
gain/cap sweep because Step137 already showed near-cap authority on the best
row.

If a placeholder is added, it must be disabled by default:

```text
open_boundary_flux_control_ratio_feedback_enabled = false
open_boundary_flux_control_ratio_gain = 0.0
```

When disabled, it must not change solver behavior, hashes except where the
existing identity policy records config surface, diagnostics, or gates. Any
activated ratio-coupled law belongs to a later explicitly authorized step.

## Final Hard Gate Handling

Step138 must evaluate every row against the final hard flow-development gate:

```text
requested_window_completed = true
finite_pass = true
density_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
first_failure_step = null
hard_stop_mass_drift_gate_pass = true
candidate_mass_acceptance_observed_abs < 0.005
0.80 <= abs(outlet_to_inlet_flux_ratio_tail_mean) <= 1.20
0.80 <= abs(midplane_to_inlet_flux_ratio_tail_mean) <= 1.20
flux_imbalance_rel_tail_mean < 0.10
flux_imbalance_rel_tail_max < 0.20
outlet_flux_tail_cv < 0.10
collapse_first_x = null
collapse_first_step = null
```

The report may show relaxed diagnostic observations for interpretation, but a
relaxed gate is not promotion evidence. If only outlet ratio enters gate while
flux mean or flux max still fails, Step138 must not recommend 500-step final
evidence.

If one row passes every final hard gate, Step138 may recommend:

```text
Step139: single 48^3 / 500-step final evidence row.
```

Even in that case, Step138 must not run the 500-step row and must not enable
selected 96^3.

## Tiny Smoke Requirement

Before real 48^3 execution, run a tiny smoke using the Step138 phase:

```text
shape = 8 x 6 x 6
n_steps = 20
ramp_steps = 10
target_scale = 0.85
gain_u = 0.75
cap_u = 0.0075
```

Smoke artifacts must prove:

- `finite_pass = true`,
- `first_failure_step = null`,
- target scale appears in diagnostics / metadata,
- gain and cap appear in diagnostics / metadata,
- `selected96_claim_allowed = false`,
- `validation_claim_allowed = false`,
- the Step138 phase does not reuse Step137 artifacts.

## Test Requirements

Add a focused contract test file:

```text
tests/test_step138_high_authority_outlet_contract.py
```

The tests must cover:

- `planeflux_high_authority48` exists and is distinct from Step137
  `planeflux_ramp_refined48`.
- The phase contains exactly, and no more than, six rows.
- All Step138 rows are 48^3 / 250-step diagnostic rows.
- All Step138 rows use `row_role = interior_reflection_diagnostic_48`.
- Row names / manifest expectations encode `ramp_steps`, target scale,
  `gain_u`, and `cap_u`.
- The expected rows are precisely the six Step138 high-authority combinations.
- `gain_u` and `cap_u` changes alter solver-state hash / run-manifest identity.
- Stale Step137 rows cannot be reused for Step138.
- Step138 diagnostic rows cannot enable selected 96^3 even if mocked metrics
  pass.
- Step138 semantics are not added to `CANDIDATE_SEMANTICS` or
  `REPAIRED_CANDIDATE_SEMANTICS`.
- Tiny smoke phase exists and uses the high-authority parameters.
- Compact x-profile diagnostics remain bounded and schema-stable.

## Implementation Requirements

The implementation must stay narrow:

- Reuse existing Step120 / Step121 campaign and artifact machinery.
- Reuse existing plane-flux controller parameters.
- Keep default behavior unchanged for existing phases.
- Keep solver behavior changes limited to the Step138 gain/cap row specs and
  report-visible diagnostics.
- Keep compact x-profile diagnostics from Step135 through Step137.
- Include Step138 fields in solver identity where they affect artifacts or
  behavior.
- Keep row names, metadata, and manifests explicit and reproducible.
- Keep tiny-smoke support.
- Keep selected-chain logic unchanged except for tests proving Step138 rows are
  ignored by selection.

Required command surface:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_high_authority48 `
  --output-dir outputs\step138_high_authority_outlet_diagnostic\planeflux_high_authority48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume
```

Use `--force --no-resume` for final provenance generation after the
implementation commit.

## Artifact Requirements

Required tiny smoke artifact root:

```text
outputs/step138_high_authority_outlet_diagnostic/tiny_smoke
```

Required 48^3 artifact root:

```text
outputs/step138_high_authority_outlet_diagnostic/planeflux_high_authority48
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
docs/campaigns/fluent_duct_flap/steps/138/report.md
```

The report must answer:

1. Did higher `gain_u` reduce outlet ratio to `<= 1.20`?
2. Did higher `cap_u` reduce outlet ratio or flux imbalance when Step137 was
   near the authority ceiling?
3. If outlet ratio improved, did `flux_imbalance_rel_tail_mean` and
   `flux_imbalance_rel_tail_max` also pass the final hard gates?
4. Did higher authority reintroduce compact x-profile collapse?
5. Did higher authority trigger density, population, Mach, or first-failure
   instability?
6. Did controller saturation / authority telemetry show that the new cap was
   still exhausted?
7. Is a later Step139 48^3 / 500-step final-evidence row justified?
8. Is selected 96^3 still blocked?

The report table must include at minimum:

- row name,
- ramp steps,
- target scale,
- gain,
- cap,
- `candidate_mass_acceptance_observed_abs`,
- `outlet_to_inlet_flux_ratio_tail_mean`,
- `midplane_to_inlet_flux_ratio_tail_mean`,
- `flux_imbalance_rel_tail_mean`,
- `flux_imbalance_rel_tail_max`,
- `outlet_flux_tail_cv`,
- `collapse_first_x`,
- `collapse_first_step`,
- key x-profile tail CV values, especially x24, x36, and x47,
- controller authority / feedback tail behavior when available,
- controller saturation fraction when available,
- limiter activation fraction when available,
- density / population / Mach / first-failure status,
- selected 96^3 claim allowed flag.

Possible report conclusions:

```text
Case A:
One row passes all final hard gates.
Next step may be Step139 single 48^3 / 500-step final evidence.
No selected 96^3 yet.

Case B:
Outlet ratio enters gate, but flux mean or flux max remains outside hard gates.
Continue 250-step formulation tuning.
No 500-step evidence yet.

Case C:
Higher authority reintroduces compact collapse or instability.
Return to lower authority and repair ramp profile, outlet reconstruction, or
inlet/outlet coupling.
No 500-step evidence yet.

Case D:
Higher cap/gain barely moves ratios.
The scalar plane-flux controller is insufficient.
Next step should introduce a distinct ratio-coupled or pressure-coupled outlet
formulation, still bounded at 48^3 / 250 steps.
No 500-step evidence yet.
```

The conclusion must be artifact-bounded. If evidence remains inconclusive, say
so and recommend the next bounded diagnostic rather than promoting.

## Current Documentation Requirements

After the run, update the current campaign status documents so they state:

- Step137 remains accepted only as bounded 48^3 / 250-step diagnostic evidence.
- Step138 adds bounded high-authority outlet diagnostics.
- Whether Step138 supports a later Step139 48^3 / 500-step final-evidence run.
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

Focused contract verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
  --basetemp outputs\tmp\pytest-step138-focused `
  tests\test_step138_high_authority_outlet_contract.py `
  tests\test_step137_ramp_target_refinement_contract.py `
  tests\test_step136_ramped_throughput_calibration_contract.py `
  tests\test_step135_interior_reflection_diagnostics_contract.py `
  tests\test_step134_outlet_stationarity_contract.py `
  tests\test_step133_mass_damped_plane_flux_contract.py `
  tests\test_step132_plane_flux_authority_sweep_contract.py `
  tests\test_step131_plane_flux_controller_contract.py
```

Campaign / provenance verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q `
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
  src\mpm_lbm\sim\lbm\config.py `
  src\mpm_lbm\sim\lbm\fluid.py
```

Artifact verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_high_authority48 `
  --output-dir outputs\step138_high_authority_outlet_diagnostic\tiny_smoke `
  --tiny-smoke `
  --force `
  --no-resume

& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_high_authority48 `
  --output-dir outputs\step138_high_authority_outlet_diagnostic\planeflux_high_authority48 `
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
docs: add Step138 high-authority outlet diagnostic goal
feat: add Step138 high-authority outlet diagnostic phase
test: record Step138 high-authority outlet diagnostics
```

Before the final push:

- inspect `git status --short`,
- inspect staged file names,
- ensure generated artifacts and docs match the code commit that produced them,
- ensure no selected 96^3 artifact was created,
- ensure no 500-step Step138 artifact was created,
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
