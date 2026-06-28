# Step137 Refined Ramp-Target Throughput Window Goal

## Source Review

Step137 starts from the post-Step136 review conclusion:

```text
origin/main contains final commit:
998e621db1e4759c1444fa9268b06b05f36f35e9
test: record Step136 ramped throughput calibration diagnostics
```

Step136 is accepted only as bounded real 48^3 / 250-step LBM-only
ramped-throughput calibration evidence:

```text
6 / 6 planeflux_ramp_tuned48 rows completed 250 / 250.
All rows stayed finite.
All rows had first_failure_step = null and first_failure_reason = null.
0 / 6 rows passed the flow-development promotion gate.
No 500-step promotion row was run.
No selected 96^3 run is allowed.
No quasi-2D, FSI, Fluent, or Figure 29.3 parity claim is allowed.
```

Step136 is useful because it narrowed the failure rather than promoting a
candidate. The best mass / stationarity row and the best flux-imbalance row
pulled in different directions:

```text
Best mass row:
  ramp_steps = 100
  gain_u = 0.50
  cap_u = 0.005
  target_scale = 0.90
  candidate_mass_acceptance_observed_abs = 0.0027411073257309804
  flux_imbalance_rel_tail_mean = 0.22888777098124222
  outlet_to_inlet_flux_ratio_tail_mean = 1.3064291443826772
  midplane_to_inlet_flux_ratio_tail_mean = 1.228018341923524
  outlet_flux_tail_cv = 0.08653967735783066
  collapse_first_x = null
  collapse_first_step = null

Best flux-imbalance row:
  ramp_steps = 75
  gain_u = 0.50
  cap_u = 0.005
  target_scale = 1.00
  candidate_mass_acceptance_observed_abs = 0.0065664103097401475
  flux_imbalance_rel_tail_mean = 0.17995040672859994
  outlet_to_inlet_flux_ratio_tail_mean = 1.2300496083019266
  midplane_to_inlet_flux_ratio_tail_mean = 1.0789222122987672
  outlet_flux_tail_cv = 0.11151179601758945
  collapse_first_x = 24
  collapse_first_step = 250
```

Interpretation:

```text
target_scale 0.90 / 0.95 with ramp100 gives good mass, good outlet CV, and no
compact collapse, but outlet and midplane ratios remain too high.

ramp75 improves flux imbalance and midplane ratio, but outlet ratio remains too
high and the compact x-profile collapse returns at x = 24.
```

Step137 must stay in this narrowed diagnostic envelope. It must test whether
intermediate ramp duration and lower target scale can combine the stable
ramp100 / target0.90 behavior with the lower-imbalance ramp75 behavior.

## Step137 Objective

Implement and run a bounded 48^3 LBM-only diagnostic phase named:

```text
planeflux_ramp_refined48
```

The objective is to evaluate a refined ramp-target window:

```text
ramp_steps in the 80-95 neighborhood
target_scale in the 0.80-0.90 neighborhood
gain_u = 0.50
cap_u = 0.005
```

Step137 must answer:

1. Does `target_scale = 0.85` or `target_scale = 0.80` reduce
   `outlet_to_inlet_flux_ratio_tail_mean` below `1.20`?
2. Does `ramp_steps = 85` or `ramp_steps = 90` avoid the ramp75 compact
   collapse while improving flux imbalance?
3. Does any row pass the final hard flow-development gates?
4. Is a later Step138 single 48^3 / 500-step final evidence run justified?
5. Is selected 96^3 still blocked?

Step137 remains diagnostic. It may justify a later Step138 48^3 / 500-step
final-evidence proposal only if a row passes the final hard gates below.
Step137 itself must not run 500 steps and must not enable selected 96^3.

## Non-Negotiable Scope Boundaries

Step137 must stay inside this envelope:

- Real 48^3 LBM-only rows.
- Maximum 250 steps per 48^3 row.
- Maximum six 48^3 rows.
- Tiny smoke is allowed before real 48^3 execution.
- No selected 96^3 execution.
- No selected-candidate row semantics.
- No 500-step execution.
- No quasi-2D, FSI, Fluent, or Figure 29.3 parity claim.
- No gate relaxation.
- No dense-grid dumps or large checkpoint artifacts.
- No hardcoded pressure, velocity, displacement, or flow shortcut that fakes a
  successful jet.
- No stale Step136 or earlier artifact reuse as Step137 evidence.
- No claim that GitHub Actions validated the run unless actions actually ran.

## Boundary Semantics

Reuse the existing diagnostic boundary semantics:

```text
semantics = regularized_plane_flux_controlled_pressure_outlet
row_role = interior_reflection_diagnostic_48
```

Do not add Step137 rows to:

```text
CANDIDATE_SEMANTICS
REPAIRED_CANDIDATE_SEMANTICS
```

Do not alter selected-chain logic except for tests proving Step137 rows remain
blocked from selected 96^3 claims even when mocked metrics pass.

## Required Six-Row 48^3 Phase

Use:

```text
phase = planeflux_ramp_refined48
row_role = interior_reflection_diagnostic_48
```

The phase must contain exactly these six real 48^3 rows:

1. `ramp90 target0.90 gain0.50 cap0.005`,
2. `ramp90 target0.85 gain0.50 cap0.005`,
3. `ramp90 target0.80 gain0.50 cap0.005`,
4. `ramp85 target0.90 gain0.50 cap0.005`,
5. `ramp85 target0.85 gain0.50 cap0.005`,
6. `ramp100 target0.85 gain0.50 cap0.005`.

All rows should use:

```text
grid = 48^3
n_steps = 250
output_interval = 5
lbm_niu = 0.10
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
Rows 1-3 test target scale 0.90 / 0.85 / 0.80 at ramp90.
Rows 4-5 test whether ramp85 preserves the ramp75 imbalance benefit without
compact collapse.
Row 6 holds ramp100 while lowering target scale to 0.85, to separate target
effect from ramp-duration effect.
```

No row in this phase may set selected-candidate semantics. No Step137 row may
enter the selected 96^3 candidate set.

## Optional Report-Only Diagnostics

Step137 may add report-only summary fields to make sorting and diagnosis
clearer:

```text
ratio_overdrive_tail_mean = max(
  outlet_to_inlet_flux_ratio_tail_mean - 1.0,
  midplane_to_inlet_flux_ratio_tail_mean - 1.0
)

promotion_margin_score = report-only scalar summarizing remaining distance
from the final hard gates
```

These fields must not relax any gate and must not enable promotion by
themselves. If implemented, they must be visible in per-row diagnostics and
summary JSON; if omitted, the report must still present the raw final hard-gate
metrics listed below.

## Final Hard Gate Handling

Step137 must evaluate rows against the final hard flow-development gate:

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

If a row passes only a relaxed diagnostic threshold, the report must still show
the final hard-gate failure. Step137 cannot use a relaxed gate alone to justify
Step138 or selected 96^3.

If a row passes the final hard gate, Step137 may recommend Step138 as a single
48^3 / 500-step final evidence row. Step137 still must not run that row.
Selected 96^3 remains blocked unless a later explicitly authorized step
changes the selected-candidate contract with artifact-backed evidence.

## Tiny Smoke Requirement

Before real 48^3 execution, run a tiny smoke using the Step137 phase:

```text
shape = 8 x 6 x 6
n_steps = 20
ramp_steps = 10 or 20
target_scale = 0.85
gain_u = 0.50
cap_u = 0.005
```

Smoke artifacts must prove:

- `finite_pass = true`,
- `selected96_claim_allowed = false`,
- target scale appears in diagnostics / metadata,
- ramp settings appear in diagnostics / metadata,
- the Step137 phase does not reuse Step136 artifacts,
- validation / promotion remains false for the tiny row.

## Test Requirements

Add a focused contract test file:

```text
tests/test_step137_ramp_target_refinement_contract.py
```

The tests must cover:

- `planeflux_ramp_refined48` exists and is distinct from Step136
  `planeflux_ramp_tuned48`.
- The phase contains exactly, and no more than, six rows.
- All Step137 rows are 48^3 / 250-step diagnostic rows.
- All Step137 rows use `row_role = interior_reflection_diagnostic_48`.
- Row names / manifest expectations encode `ramp_steps` and
  `open_boundary_flux_control_target_scale`.
- The expected rows are precisely the six Step137 ramp-target combinations.
- `open_boundary_flux_control_target_scale` defaults to `1.0` and preserves
  Step136 / earlier default behavior.
- Target scale and ramp settings enter solver-state hash / run-manifest
  identity.
- Stale Step136 rows cannot be reused for Step137.
- Step137 diagnostic rows cannot enable selected 96^3 even if mocked metrics
  pass.
- Compact x-profile diagnostics remain bounded and schema-stable.

## Implementation Requirements

The implementation must stay narrow:

- Reuse existing Step120 / Step121 campaign and artifact machinery.
- Keep default behavior unchanged when target scale is `1.0`.
- Keep solver behavior changes limited to already-visible ramp / target-scale
  control surfaces and optional report-only diagnostics.
- Keep compact x-profile diagnostics from Step135 / Step136.
- Include new Step137 fields in solver identity where they affect artifacts or
  behavior.
- Keep row names, metadata, and manifests explicit and reproducible.
- Keep tiny-smoke support.
- Keep selected-chain logic unchanged except for tests proving Step137 rows are
  ignored by selection.

Required command surface:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_ramp_refined48 `
  --output-dir outputs\step137_ramp_target_refinement\planeflux_ramp_refined48 `
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
outputs/step137_ramp_target_refinement/tiny_smoke
```

Required 48^3 artifact root:

```text
outputs/step137_ramp_target_refinement/planeflux_ramp_refined48
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
docs/campaigns/fluent_duct_flap/steps/137/report.md
```

The report must answer:

1. Did `target_scale = 0.85` or `target_scale = 0.80` reduce outlet ratio below
   `1.20`?
2. Did `ramp_steps = 85` or `ramp_steps = 90` avoid the ramp75 compact collapse
   while improving flux imbalance?
3. Did any row pass the final hard flow-development gates?
4. Is Step138 48^3 / 500-step final evidence justified?
5. Is selected 96^3 still blocked?

The report table must include at minimum:

- row name,
- ramp steps,
- target scale,
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
- limiter activation fraction when available,
- selected 96^3 claim allowed flag.

Possible report conclusions:

```text
Case A:
One row passes the final hard gates.
Next step may be Step138 single 48^3 / 500-step final evidence.
No selected 96^3 yet.

Case B:
One row passes relaxed diagnostic expectations but not final hard gates.
Continue 250-step refinement.
No 500-step evidence yet.

Case C:
target_scale 0.80 / 0.85 fixes ratios but reintroduces compact collapse.
Next step should repair ramp profile or bulk development, such as smoothstep
ramping, still at 250 steps.

Case D:
All rows keep outlet or midplane ratio above 1.20.
Target scale alone is insufficient; revisit open-boundary formulation or
inlet/outlet coupling before any longer run.
```

The conclusion must be artifact-bounded. If evidence remains inconclusive, say
so and recommend the next bounded diagnostic rather than promoting.

## Current Documentation Requirements

After the run, update the current campaign status documents so they state:

- Step136 remains accepted only as bounded 48^3 / 250-step ramped-throughput
  calibration evidence.
- Step137 adds bounded refined ramp-target throughput-window diagnostics.
- Whether Step137 supports a later Step138 48^3 / 500-step final-evidence run.
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
  --basetemp outputs\tmp\pytest-step137-focused `
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
  --phase planeflux_ramp_refined48 `
  --output-dir outputs\step137_ramp_target_refinement\tiny_smoke `
  --tiny-smoke `
  --force `
  --no-resume

& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_ramp_refined48 `
  --output-dir outputs\step137_ramp_target_refinement\planeflux_ramp_refined48 `
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
docs: add Step137 ramp-target refinement goal
feat: add Step137 ramp-target refinement phase
test: record Step137 ramp-target refinement diagnostics
```

Before the final push:

- inspect `git status --short`,
- inspect staged file names,
- ensure generated artifacts and docs match the code commit that produced them,
- ensure no selected 96^3 artifact was created,
- ensure no 500-step Step137 artifact was created,
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
