# Step133 Slow Density Feedback and Outlet Stationarity Repair Report

## Decision

Step133 is bounded 48^3 LBM-only triage evidence. It does not select a
boundary, does not justify a 500-step promotion, and does not authorize any
selected 96^3 run.

The `planeflux_mass_damped48` phase completed six real 48^3 / 250-step rows.
All six rows completed the requested 250-step window, stayed finite, and had no
first-failure event. Accepted row count remained zero because every row still
failed the relaxed triage promotion gate.

Step133 makes no quasi-2D, FSI, Fluent validation, or Figure 29.3 parity claim.

## Step132 Baseline

Step133 started from the accepted Step132 authority-sweep evidence, not from a
selected boundary. The Step132 baseline row was:

```text
duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_250step_triage
semantics = regularized_plane_flux_controlled_pressure_outlet
gain_u = 0.25
cap_u = 0.005
filter_alpha = 0.02
convective_blend_weight = 0.02
gain_rho = 0.0
```

The Step132 row completed 250/250 with finite state and no first-failure
event, but still had `candidate_mass_acceptance_observed_abs =
0.014016928659457415` and `outlet_flux_tail_cv = 0.46453328972807856`.

## Phase 0 Docs Fix

Before Step133 implementation claims, the current read-first docs were updated
so Step132 goal/report appear before older campaign history:

```text
docs/current/ACTIVE_CAMPAIGN.json
docs/current/READING_ORDER.md
```

During final current-doc verification, `ACTIVE_CAMPAIGN.json` was compressed to
the Step124 contract limit of eight read-first entries and advanced to the
Step133 report/goal first, with Step132 retained as the immediate baseline.
The campaign-level manifest identity in
`outputs/step121_lbm_boundary_real_campaign_and_gate_correction/campaign_manifest.json`
was synchronized to the Step133 code commit. This does not alter earlier row
artifacts or their run-time `code_commit_at_run` evidence.

## Code Surface

Step133 added bounded stationarity damping around the existing Step131/Step132
plane-integrated flux controller:

```text
open_boundary_flux_feedback_delta_cap_u
open_boundary_flux_feedback_slew_alpha
```

Default values preserve Step131/Step132 behavior:

```text
open_boundary_flux_feedback_delta_cap_u = 0.0
open_boundary_flux_feedback_slew_alpha = 1.0
```

Step133 also uses the existing `open_boundary_flux_feedback_gain_rho` surface
as slow density feedback and records it in solver-state identity, metadata,
boundary reports, flow-development diagnostics, and summary rows. The density
feedback is clamped to `[-0.01, +0.01]`.

The new Step121 phase is:

```text
planeflux_mass_damped48
```

The phase rows remain `row_role = plane_flux_control_candidate_48` triage rows
and are not selected96-eligible rows.

## Tiny Smoke

Command shape:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step120_lbm_boundary_repair_large_real_execution `
  --tiny Step133 smoke via local Step120 row construction
```

Artifact root:

```text
outputs/step133_mass_damped_plane_flux_repair/tiny_smoke/tiny_step133_mass_damped_plane_flux_smoke
```

Tiny smoke result:

| field | value |
| --- | --- |
| code_commit_at_run | `f78bea27e6df28f0e99119658e2f349b4f1607c8` |
| requested_window_completed | `true` |
| steps_completed | `20` |
| finite_pass | `true` |
| first_failure_step | `null` |
| first_failure_reason | `null` |
| flow diagnostics step | `133` |
| controller_u_feedback_tail_abs_max | `0.0005706780939362943` |
| density_feedback_tail_abs_max | `2.381955255259527e-06` |
| rho_outlet_tail_mean | `0.9994498863816261` |
| rho_outlet_tail_std | `0.002418108284473419` |
| validation_claim_allowed | `false` |
| selected96_claim_allowed | `false` |

## 48^3 Triage Run

Final command:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_mass_damped48 `
  --output-dir outputs\step133_mass_damped_plane_flux_repair\planeflux_mass_damped48 `
  --allow-large-real-rows `
  --output-interval 25 `
  --force `
  --no-resume
```

`--force --no-resume` was used only for the final 48^3 artifact generation
after the Step133 code commit, so every final row records
`code_commit_at_run = f78bea27e6df28f0e99119658e2f349b4f1607c8` and no stale
checkpoint resume is mixed into the evidence.

Artifact roots:

```text
outputs/step133_mass_damped_plane_flux_repair/planeflux_mass_damped48
outputs/step133_mass_damped_plane_flux_repair/step133_mass_damped_summary.json
```

## Parameter Table

| row | semantics | gain_u | cap_u | gain_rho | alpha | delta_cap_u | slew_alpha |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| convective gain0p10 cap0p002 rho0p001 alpha0p02 du0p0005 slew0p50 | convective_plane_flux_controlled_damped_outlet | 0.10 | 0.002 | 0.0010 | 0.02 | 0.0005 | 0.50 |
| regularized rho0p0005 alpha0p02 du0p0005 slew0p50 | regularized_plane_flux_controlled_pressure_outlet | 0.25 | 0.005 | 0.0005 | 0.02 | 0.0005 | 0.50 |
| regularized rho0p001 alpha0p005 du0p00025 slew0p25 | regularized_plane_flux_controlled_pressure_outlet | 0.25 | 0.005 | 0.0010 | 0.005 | 0.00025 | 0.25 |
| regularized rho0p001 alpha0p01 du0p00025 slew0p50 | regularized_plane_flux_controlled_pressure_outlet | 0.25 | 0.005 | 0.0010 | 0.01 | 0.00025 | 0.50 |
| regularized rho0p001 alpha0p02 du0p0005 slew0p50 | regularized_plane_flux_controlled_pressure_outlet | 0.25 | 0.005 | 0.0010 | 0.02 | 0.0005 | 0.50 |
| regularized rho0p002 alpha0p02 du0p0005 slew0p50 | regularized_plane_flux_controlled_pressure_outlet | 0.25 | 0.005 | 0.0020 | 0.02 | 0.0005 | 0.50 |

## Outcome Table

| row | steps | first failure | mass abs | flux mean | flux max | outlet CV | outlet/inlet | mid/inlet | authority mean | saturation | density fb abs max | outlet rho mean/std | sign changes | rejection reasons |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- |
| convective gain0p10 cap0p002 rho0p001 alpha0p02 du0p0005 slew0p50 | 250 | null | 0.022125313054974453 | 0.2630888340905568 | 0.4495472815466084 | 0.20262416501645636 | 1.408879778823433 | 1.2372221853054948 | 0.6191853511457642 | 0.0 | 1.618947135284543e-05 | 1.0182004683259605 / 0.008815408173429158 | 0 | mass, flux max, flux mean, mid ratio, outlet CV, outlet ratio |
| regularized rho0p0005 alpha0p02 du0p0005 slew0p50 | 250 | null | 0.014184975814691638 | 0.3987696128026395 | 0.6558913031436817 | 0.47087164136218246 | 1.0280528796842723 | 0.9111280219154153 | 0.44773064243296784 | 0.0 | 5.405273896030849e-06 | 1.006934913829504 / 0.0014329189458766134 | 0 | mass, flux max, flux mean, outlet CV |
| regularized rho0p001 alpha0p005 du0p00025 slew0p25 | 250 | null | 0.024829462325527896 | 0.4483849557329607 | 0.4827290560098236 | 0.4361470854537922 | 1.3452237056170424 | 1.1533783978641838 | 0.27098464003453654 | 0.0 | 6.068346465326613e-06 | 1.003946693535488 / 0.0004536078080584434 | 0 | mass, flux max, flux mean, mid ratio, outlet CV, outlet ratio |
| regularized rho0p001 alpha0p01 du0p00025 slew0p50 | 250 | null | 0.01987675161739998 | 0.44222157136335255 | 0.6130067337699419 | 0.47363843292900576 | 1.1660274686186083 | 1.0164311276604172 | 0.42380990150074166 | 0.0 | 8.959964361565653e-06 | 1.0063964196474355 / 0.00040016715674497317 | 0 | mass, flux max, flux mean, outlet CV, outlet ratio |
| regularized rho0p001 alpha0p02 du0p0005 slew0p50 | 250 | null | 0.014192482589191811 | 0.3988279078914281 | 0.6557326488782265 | 0.47082283085466237 | 1.0283149713136532 | 0.9113304853742965 | 0.4479239461943507 | 0.0 | 1.0813455446623266e-05 | 1.0069332708896297 / 0.0014315805084057728 | 0 | mass, flux max, flux mean, outlet CV |
| regularized rho0p002 alpha0p02 du0p0005 slew0p50 | 250 | null | 0.014207528860067037 | 0.39894398327816094 | 0.6554137527895759 | 0.4707243350859428 | 1.0288399464133098 | 0.9117343966027068 | 0.4483108331138889 | 0.0 | 2.163855060643982e-05 | 1.0069299584187723 / 0.0014289163527029256 | 0 | mass, flux max, flux mean, outlet CV |

## Promotion Decision

```text
accepted_row_count = 0
promotion_to_500step_allowed = false
selected96_claim_allowed = false
```

The best mass row still had mass drift above the relaxed triage threshold:

```text
candidate_mass_acceptance_observed_abs = 0.014184975814691638
threshold = 0.01
```

The best flux-imbalance row still failed mass acceptance, outlet ratio,
midplane ratio, and outlet stationarity:

```text
flux_imbalance_rel_tail_mean = 0.2630888340905568
candidate_mass_acceptance_observed_abs = 0.022125313054974453
outlet_to_inlet_flux_ratio_tail_mean = 1.408879778823433
midplane_to_inlet_flux_ratio_tail_mean = 1.2372221853054948
outlet_flux_tail_cv = 0.20262416501645636
```

Step133 therefore stops at 48^3 triage evidence.

## Verification

Focused verification already completed before this report was written:

```text
Step133 TDD red: 5 failed, 1 passed before implementation.
Step133 focused test: 6 passed in 1.63 s.
py_compile: passed for Step133 touched modules/tests.
Step130-Step132 neighbor regression: 15 passed, 12 Taichi matrix warnings.
Step120 regression group: 13 passed, 28 Taichi matrix warnings in 354.32 s.
```

Full-suite attempt:

```text
& 'D:\working\taichi\env\python.exe' -m pytest -q --basetemp outputs\tmp\pytest-step133-final-all
```

This attempt timed out after 901 s while still in the early Step120/Step12x
region. A follow-up `-x -vv` attempt also timed out after 421 s before reaching
a failure. The heavy Step120 file group was then run separately and passed.

The Step121-Step129 group initially reported two current-doc/provenance
failures: `ACTIVE_CAMPAIGN.read_first` was over the Step124 limit while this
report file did not yet exist, and the old campaign manifest had not yet had
`git_commit` synchronized with `current_code_commit`. After the report/current
doc update, the same group passed:

```text
Step121-Step129 current/provenance regression: 52 passed, 16 Taichi matrix warnings in 188.53 s.
```
