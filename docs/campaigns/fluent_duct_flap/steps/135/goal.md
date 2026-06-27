# Step135 Interior Reflection and Bulk-Dynamics Diagnosis Goal

## Source Review

Step135 starts from the post-Step134 review conclusion:

```text
origin/main contains final commit:
cdc91f658066f54a24e374a59bc8ec7e6540750d
test: record Step134 outlet stationarity triage
```

Step134 is accepted only as bounded real 48^3 / 250-step LBM-only outlet
stationarity triage evidence:

```text
6 / 6 planeflux_stationarity48 rows completed 250 / 250.
All rows stayed finite.
All rows had first_failure_step = null and first_failure_reason = null.
accepted_row_count = 0.
No 500-step Step134 promotion was run.
No selected 96^3 run is allowed.
No quasi-2D, FSI, Fluent, or Figure 29.3 parity claim is allowed.
```

Step135 must continue the real 48^3 boundary-repair loop. It must not convert
Step134 into selection evidence, and it must not bypass the unresolved tail
stationarity failure by relaxing gates, changing claim language, or reusing stale
artifacts.

## Step134 Technical Finding

Step134 tested near-outlet control-plane measurement offsets and an outlet drop
guard. The best regularized row was:

```text
duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_rho0p0005_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_250step_triage
candidate_mass_acceptance_observed_abs = 0.014007222184954796
flux_imbalance_rel_tail_mean = 0.39347561119048463
flux_imbalance_rel_tail_max = 0.6463693210369579
outlet_to_inlet_flux_ratio_tail_mean = 1.0272119275600675
midplane_to_inlet_flux_ratio_tail_mean = 0.9077078805411898
outlet_flux_tail_cv = 0.46403458232245004
near_outlet_to_outlet_flux_ratio_tail_mean = 0.9913981762897958
drop_guard_activation_count_tail = 0
```

The best convective diagnostic comparator was:

```text
duct_only_48_convective_plane_flux_controlled_damped_gain0p10_cap0p002_rho0p001_alpha0p02_du0p0005_slew0p50_offset1_guard_on_min0p70_250step_triage
candidate_mass_acceptance_observed_abs = 0.022051240592753655
flux_imbalance_rel_tail_mean = 0.2598977291666475
flux_imbalance_rel_tail_max = 0.44625889115432205
outlet_to_inlet_flux_ratio_tail_mean = 1.4026043007528752
midplane_to_inlet_flux_ratio_tail_mean = 1.240713111991833
outlet_flux_tail_cv = 0.20179832248145668
near_outlet_to_outlet_flux_ratio_tail_mean ~= 0.998
```

Interpretation:

```text
The late outlet collapse is not explained by measuring the controller one or
two cells upstream of the outlet.

For the regularized branch, x = nx - 2 / nx - 3 and x = nx - 1 collapse
together. The tail failure therefore appears to be a broader interior or
bulk-dynamics phenomenon rather than a one-cell outlet readout artifact.

For the convective comparator, flux imbalance improves but mass acceptance and
mean ratios move away from the regularized candidate branch. It remains
diagnostic only.
```

## Step135 Objective

Implement and test a bounded 48^3 LBM-only diagnostic phase named:

```text
planeflux_interior_diag48
```

The purpose is to diagnose whether the remaining Step134 tail failure is caused
by:

1. outlet-local numerical reflection,
2. an interior flow-development wave or startup transient,
3. controller feedback response to a bulk transient,
4. excessive or insufficient LBM relaxation / viscosity, or
5. another artifact visible in compact x-profile time diagnostics.

Step135 is diagnostic. It is not a selected-boundary phase and it must not
enable selected 96^3 work. The final report may recommend the next Step136
direction, but it must not claim quasi-2D, FSI, Fluent, or Figure 29.3 readiness.

## Non-Negotiable Scope Boundaries

Step135 must stay inside this envelope:

- Real 48^3 LBM-only rows.
- Maximum 250 steps per diagnostic row.
- Maximum six 48^3 rows.
- No selected 96^3 execution.
- No 500-step execution unless a later explicit step authorizes it from
  artifact-backed relaxed-gate evidence.
- No quasi-2D, FSI, Fluent, or Figure 29.3 parity claim.
- No dense-grid dump artifacts that would bloat the repo.
- No hardcoded pressure, velocity, displacement, or flow shortcut that fakes a
  successful jet.
- No relaxation of promotion gates inside Step135.
- No use of Step135 diagnostic rows as selected-candidate rows.
- No stale Step134 or earlier artifacts may be counted as Step135 evidence.

## Diagnostic Surface

Step135 must add compact, bounded x-profile diagnostics that can be stored in
CSV and JSON artifacts without saving full 3D fields.

Required per-sample diagnostics:

- `x_profile_flux_samples`
- `x_profile_ux_mean_samples`
- `x_profile_rho_mean_samples`
- `sampled_x_profile_flux`
- `inlet_flux`
- `midplane_flux`
- `near_outlet_flux_xminus3`
- `near_outlet_flux_xminus2`
- `near_outlet_flux_xminus1`
- `outlet_flux`
- controller target, measured flux, delta, feedback, cap, and limiter state
- mass drift / mass acceptance fields already used by Step121-Step134

For 48^3 rows, the x-profile sample stations should include the inlet,
quarter/interior stations, near-outlet stations, and true outlet:

```text
x = 0, 6, 12, 18, 24, 30, 36, 42, 45, 46, 47
```

The implementation must clamp and deduplicate indices for tiny smoke shapes so
the same code path works on small domains.

Required per-row summary diagnostics:

- `x_profile_flux_tail_values_by_x`
- `x_profile_flux_tail_slope_by_x`
- `x_profile_flux_tail_cv_by_x`
- `x_profile_flux_last_to_mean_ratio_by_x`
- `x_profile_flux_phase_lag_proxy`
- `collapse_first_x`
- `collapse_first_step`
- `step135_interior_reflection_candidate`
- `open_boundary_inlet_ramp_steps`
- `open_boundary_inlet_ramp_profile`

`collapse_first_x` and `collapse_first_step` are diagnostic labels only. They
must be computed from recorded compact samples and must not become a promotion
gate in this step.

## High-Frequency Tail Sampling

Step135 must include high-frequency tail sampling for the baseline regularized
Step134 best row:

```text
semantics = regularized_plane_flux_controlled_pressure_outlet
open_boundary_flux_control_measure_plane_offset = 2
open_boundary_outlet_flux_drop_guard_enabled = true
open_boundary_outlet_flux_drop_guard_min_ratio = 0.70
output_interval = 5
n_steps = 250
```

The goal is to observe the 150-250 step tail evolution at 5-step resolution.
The report must state whether the collapse first appears near the outlet, in the
interior, at the inlet, or across the profile at nearly the same time.

This row is not promotion evidence even if it looks better than Step134.

## Inlet Ramp / Startup Transient Probes

Step135 must test whether the late tail collapse is a delayed startup transient
or reflection seeded by the abrupt inlet boundary.

Add a bounded diagnostic inlet-ramp surface, default off:

```text
open_boundary_inlet_ramp_steps = 0
open_boundary_inlet_ramp_profile = linear
```

When `open_boundary_inlet_ramp_steps > 0`, the effective inlet velocity used by
the Step120 real-run row should be:

```text
effective_inlet_u_lbm(step) =
    inlet_u_lbm * min(1.0, step / open_boundary_inlet_ramp_steps)
```

The exact implementation may live in the runner or LBM config, but it must be
artifact-visible and included in solver identity:

- run metadata,
- diagnostics CSV / JSON,
- manifest expected rows,
- solver state hash fields,
- stale-artifact rejection.

Required diagnostic ramp probes:

- ramp 50 steps on the regularized Step134 best row,
- ramp 100 steps on the regularized Step134 best row.

These probes are diagnostic only. They must not be selected-candidate rows.

## Relaxation / Niu Sensitivity Probes

Step135 must include bounded relaxation sensitivity probes to determine whether
the collapse is tied to LBM viscosity / relaxation.

Required probes on the regularized Step134 best row:

```text
lbm_niu = 0.08
lbm_niu = 0.12
```

The final report must compare these to the baseline `lbm_niu = 0.10` behavior.
The comparison must stay diagnostic and must not claim physical validation.

## Required Six-Row 48^3 Phase

The `planeflux_interior_diag48` phase should run no more than these six rows:

1. regularized offset2 guard_on min0p70, high-frequency output interval 5,
2. regularized offset2 guard_on min0p70, inlet ramp 50,
3. regularized offset2 guard_on min0p70, inlet ramp 100,
4. regularized offset2 guard_on min0p70, `lbm_niu = 0.08`,
5. regularized offset2 guard_on min0p70, `lbm_niu = 0.12`,
6. convective offset1 guard_on min0p70, high-frequency output interval 5.

All six rows must use a diagnostic row role, for example:

```text
row_role = interior_reflection_diagnostic_48
```

No row in this phase may set selected-candidate semantics. No Step135 row may
enter the selected 96^3 candidate set.

## Promotion Gate Handling

Step135 must preserve the existing promotion gate contract.

If the implementation computes relaxed diagnostic gate status for reporting, it
must use the existing bounded gate values and label them diagnostic:

```text
candidate_mass_acceptance_observed_abs < 0.01
outlet_to_inlet_flux_ratio_tail_mean in [0.85, 1.15]
midplane_to_inlet_flux_ratio_tail_mean in [0.85, 1.15]
flux_imbalance_rel_tail_mean < 0.20
flux_imbalance_rel_tail_max < 0.35
outlet_flux_tail_cv < 0.20
outlet_flux_last_to_tail_mean_ratio >= 0.70
finite_pass = true
first_failure_step = null
population and density bounds pass
Mach bounds pass
```

Even if a row passes these diagnostic gates, Step135 should report that the next
step must explicitly decide whether to run any longer promotion. Step135 itself
should not start a 500-step or selected 96^3 job.

## Test Requirements

Add a focused contract test file:

```text
tests/test_step135_interior_reflection_diagnostics_contract.py
```

The tests must cover:

- `planeflux_interior_diag48` exists and is distinct from Step134
  `planeflux_stationarity48`.
- The phase contains no more than six rows.
- The phase uses `row_role = interior_reflection_diagnostic_48` or equivalent
  diagnostic role.
- Step135 rows cannot enable selected 96^3 candidate selection.
- High-frequency output interval is encoded in row identity / run metadata.
- Inlet ramp fields are default-off, bounded, artifact-visible, and included in
  the solver state hash.
- `lbm_niu = 0.08` and `lbm_niu = 0.12` probes are present and included in row
  identity / manifest expectations.
- The new x-profile diagnostics are bounded and work on small smoke shapes.
- Stale Step134 artifacts are rejected for Step135 manifests.
- Step135 diagnostic row roles are ignored by selected-boundary best-row
  selection.
- Existing Step134, Step133, Step132, and Step131 contracts remain green.

If the inlet-ramp defaults are added to `LBMConfig`, update the Step56 behavior
policy tests so default-off behavior is explicit and older runs do not silently
change.

## Implementation Requirements

The implementation must stay narrow:

- Reuse existing Step120 / Step121 campaign and artifact machinery.
- Keep solver behavior in core LBM or the real-run runner, not hidden in case
  code.
- Add only compact per-sample and per-row diagnostics.
- Keep tiny-smoke support.
- Keep defaults preserving Step121-Step134 behavior.
- Include new Step135 fields in solver identity where they affect artifacts or
  behavior.
- Keep manifest commands explicit and reproducible.

Required command surface:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_interior_diag48 `
  --output-dir outputs\step135_interior_reflection_diagnostics\planeflux_interior_diag48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume
```

## Artifact Requirements

Required tiny smoke artifact:

```text
outputs/step135_interior_reflection_diagnostics/tiny_smoke/tiny_step135_interior_reflection_smoke
```

Required 48^3 artifact root:

```text
outputs/step135_interior_reflection_diagnostics/planeflux_interior_diag48
```

The final report must cite concrete files, including:

- campaign manifest,
- campaign summary,
- per-row diagnostics CSV,
- at least one per-row summary JSON,
- tiny smoke metadata,
- 48^3 metadata.

The report must not rely on console output alone.

## Report Requirements

Create:

```text
docs/campaigns/fluent_duct_flap/steps/135/report.md
```

The report must answer:

1. Did the tail collapse first appear at the outlet, near-outlet, interior, or
   broadly across x?
2. Did inlet ramping delay, remove, or amplify the collapse?
3. Did changing `lbm_niu` materially alter the collapse timing or stationarity?
4. Did the controller feedback cause the collapse, or did it respond to a bulk
   transient that was already visible elsewhere?
5. Did any diagnostic row pass the relaxed reporting gates?
6. Is a Step136 500-step promotion justified, blocked, or still premature?

The report table must include at minimum:

- row name,
- completed steps,
- finite / first-failure status,
- `candidate_mass_acceptance_observed_abs`,
- `flux_imbalance_rel_tail_mean`,
- `flux_imbalance_rel_tail_max`,
- `outlet_to_inlet_flux_ratio_tail_mean`,
- `midplane_to_inlet_flux_ratio_tail_mean`,
- `outlet_flux_tail_cv`,
- `outlet_flux_last_to_tail_mean_ratio`,
- `x_profile_flux_tail_cv_by_x` for key stations `36`, `42`, `46`, and `47`,
- `collapse_first_x`,
- `collapse_first_step`,
- controller feedback tail behavior,
- selected 96^3 claim allowed flag.

The conclusion must be artifact-bounded. If evidence remains inconclusive, say
so and recommend the next bounded diagnostic rather than promoting.

## Current Documentation Requirements

After the run, update the current campaign status document used by prior steps
so it states:

- Step134 remains accepted only as bounded 48^3 outlet stationarity triage.
- Step135 adds bounded interior reflection / bulk-dynamics diagnostics.
- Whether Step135 supports or blocks a later Step136 promotion.
- selected 96^3 remains blocked unless a later step explicitly changes that
  with artifact-backed evidence.

## Verification Commands

Use the trusted Taichi interpreter:

```text
D:\working\taichi\env\python.exe
```

Minimum local verification before implementation commit:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q tests/test_step135_interior_reflection_diagnostics_contract.py
& 'D:\working\taichi\env\python.exe' -m pytest -q tests/test_step134_outlet_stationarity_contract.py tests/test_step133_mass_damped_planeflux_contract.py tests/test_step132_boundary_authority_sweep_contract.py tests/test_step131_boundary_selected_candidate_contract.py
& 'D:\working\taichi\env\python.exe' -m pytest -q tests/test_step56_behavior_policy.py tests/test_step57_step56_large_probe_contract.py tests/test_step58_step56_campaign_contract.py
& 'D:\working\taichi\env\python.exe' -m py_compile experiments/steps/step120_lbm_boundary_repair_large_real_execution.py experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py src/mpm_lbm/sim/diagnostics/lbm_boundary_diagnostics.py
```

Minimum artifact verification:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_interior_diag48 `
  --output-dir outputs\step135_interior_reflection_diagnostics\tiny_smoke `
  --tiny-smoke `
  --force `
  --no-resume

& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_interior_diag48 `
  --output-dir outputs\step135_interior_reflection_diagnostics\planeflux_interior_diag48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume
```

If any verification is too expensive or times out, report the exact command,
timeout, and last artifact state. Do not replace it with a readiness claim.

## Commit and Push Requirements

Use staged commits that preserve reviewability:

```text
docs: add Step135 interior reflection diagnostic goal
feat: add Step135 interior reflection diagnostic phase
test: record Step135 interior reflection diagnostics
```

Before the final push:

- inspect `git diff --cached` and `git status --short`,
- ensure generated artifacts and docs match the code commit that produced them,
- ensure no selected 96^3 artifact was created,
- ensure no 500-step Step135 artifact was created,
- ensure no secrets are staged.

After verification, push to:

```text
origin main
```

The final response must include:

- final commit hash,
- remote branch,
- verification commands run,
- artifact roots,
- explicit statement that selected 96^3 and 500-step execution remain blocked
  unless a later step authorizes them.
