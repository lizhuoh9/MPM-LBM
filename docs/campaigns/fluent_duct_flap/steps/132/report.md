# Step132 Plane-Flux Controller Authority Calibration Report

## Result

Step132 calibrated the existing Step131 plane-flux controller authority by adding
a bounded `planeflux_sweep48` phase. The sweep reused the two Step131 boundary
semantics and varied only controller authority parameters:

- `regularized_plane_flux_controlled_pressure_outlet`
- `convective_plane_flux_controlled_damped_outlet`

All six 48^3 / 250-step LBM-only sweep rows completed 250/250, stayed finite,
and had no first-failure event. None passed both candidate mass acceptance and
flow-development hard gates. Therefore Step132 does not justify a 500-step
promotion, does not select a repaired 48^3 candidate, and does not unblock
selected 96^3.

This step does not claim selected 96^3 success, quasi-2D validation, FSI
validation, Fluent validation, or Figure 29.3 parity.

## Code Surface

Implemented and tested:

- New Step121 phase: `planeflux_sweep48`.
- Six bounded 48^3 / 250-step sweep specs that reuse Step131 plane-flux
  semantics and vary `open_boundary_flux_feedback_gain_u` and
  `open_boundary_flux_correction_cap_u`.
- Controller authority diagnostics in the bounded flow-development CSV/JSON
  surface:
  `controller_authority_ratio`,
  `step132_authority_sweep_candidate`,
  controller feedback tail mean/abs max/std,
  saturation tail fraction,
  raw/filtered error tail mean,
  target/measured outlet flux tail mean, and authority tail mean/max.
- Step132 contract tests covering phase separation, solver hash separation from
  Step131, stale Step131 manifest rejection, no selected96 enablement, and the
  new diagnostics summary fields.
- `docs/current/VALIDATION_GATES.md` now includes the Step131 planeflux triage
  evidence that was missing from the current gate surface.

## Artifacts

Tiny smoke root:
`outputs/step132_plane_flux_authority_calibration/tiny_smoke/tiny_step132_plane_flux_authority_smoke`

Sweep root:
`outputs/step132_plane_flux_authority_calibration/planeflux_sweep48`

Step132 summary:
`outputs/step132_plane_flux_authority_calibration/step132_authority_sweep_summary.json`

Runtime code commit for the tiny smoke and sweep rows:
`4e358d43ac86a5e520b82838f4f2e1a218ca3ef9`

## Tiny Smoke Evidence

The 8x6x6 / 2-step authority smoke completed 2/2 with:

- `finite_pass = true`
- `requested_window_completed = true`
- `first_failure_step = null`
- `flow_development_diagnostics_summary.step = 132`
- `selected96_claim_allowed = false`
- `controller_authority_ratio_tail_max = 0.025499983166810125`
- `controller_u_feedback_tail_abs_max = 5.099996633362025e-05`

The smoke is only a controller-authority and diagnostics check. It is not
validation evidence.

## 48^3 Sweep Evidence

All rows below are real LBM-only 48^3 / 250-step triage artifacts.

| Row | Gain | Cap | Mass abs | Flow gate | Flux mean | Flux max | Outlet ratio | Mid ratio | Outlet CV | Authority tail mean | Saturation tail |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `regularized gain0p05 cap0p002` | 0.05 | 0.002 | 0.02507971823051168 | false | 0.41377412921735246 | 0.46401271478262013 | 1.463913725219208 | 1.234307452180338 | 0.3790611140935099 | 0.3618667639481525 | 0.0 |
| `regularized gain0p10 cap0p002` | 0.10 | 0.002 | 0.021917770267537575 | false | 0.4205362760165438 | 0.4304513813339547 | 1.3308788194688899 | 1.1399716839113967 | 0.40487700715091 | 0.6418003079791864 | 0.0 |
| `regularized gain0p25 cap0p002` | 0.25 | 0.002 | 0.017047883043090316 | false | 0.41400434946719883 | 0.5616177301074178 | 1.1561859027472767 | 1.006558717450225 | 0.4387419991867708 | 1.0000000474974513 | 0.6504444444444444 |
| `regularized gain0p25 cap0p005` | 0.25 | 0.005 | 0.014016928659457415 | false | 0.39506523169401825 | 0.6458331484894854 | 1.0307369515412572 | 0.9160340533832297 | 0.46453328972807856 | 0.43761600585033494 | 0.0 |
| `convective gain0p05 cap0p002` | 0.05 | 0.002 | 0.025274681861652618 | false | 0.3407454353917416 | 0.4922055079263776 | 1.5626615520921288 | 1.4184664750217673 | 0.1775235596464611 | 0.35439183314641315 | 0.0 |
| `convective gain0p10 cap0p002` | 0.10 | 0.002 | 0.02197742027071526 | false | 0.26260675631911695 | 0.44876873369242576 | 1.4076835420515006 | 1.2354670381858301 | 0.20215625232941636 | 0.6114913655134538 | 0.0 |

Shared outcome:

- `row_count = 6`
- Every row completed 250/250.
- Every row had `finite_pass = true`.
- Every row had `first_failure_step = null` and `first_failure_reason = null`.
- Every row failed candidate mass acceptance because mass abs stayed above
  `0.005`.
- Every row failed flow development.
- `accepted_row_count = 0`.
- `promotion_to_500step_allowed = false`.
- `selected96_claim_allowed = false`.

Best observed mass row:
`duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005_250step_triage`
with `candidate_mass_acceptance_observed_abs = 0.014016928659457415`.

Best observed flux-imbalance row:
`duct_only_48_convective_plane_flux_controlled_damped_gain0p10_cap0p002_250step_triage`
with `flux_imbalance_rel_tail_mean = 0.26260675631911695`.

## Decision

Step132 is useful calibration evidence: increasing controller authority changed
mass drift and throughput metrics in the expected direction, especially for the
regularized gain 0.25 rows. However, it still did not produce an accepted 48^3
candidate.

The next step should remain bounded 48^3 LBM-only controller/formulation work.
It should not run selected 96^3, quasi-2D, FSI, Fluent parity, or Figure 29.3
work from these artifacts.

## Verification

Commands run with `D:\working\taichi\env\python.exe` unless otherwise noted:

```text
python -m pytest -q tests/test_step132_plane_flux_authority_sweep_contract.py --basetemp "$env:TEMP\pytest-step132-contract"
python -m pytest -q tests/test_step131_plane_flux_controller_contract.py -k "not tiny_real_controller_smoke" --basetemp "$env:TEMP\pytest-step131-contract"
python -m compileall -q experiments/steps/step120_lbm_boundary_repair_large_real_execution.py experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py src/mpm_lbm/sim/lbm/fluid.py tests/test_step132_plane_flux_authority_sweep_contract.py
python <inline Step132 tiny smoke runner>
python <inline per-row Step132 planeflux_sweep48 runner, rows 1 through 6>
python -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase summary --output-dir outputs\step132_plane_flux_authority_calibration\planeflux_sweep48
python -m pytest -q --basetemp "$env:TEMP\pytest-step132-final-all"
git diff --check
```

Verification results:

- Step132 contract tests: 5 passed.
- Step131 non-smoke plane-flux contract regression: 6 passed, 1 deselected.
- `compileall`: passed.
- Tiny authority smoke: completed 2/2, finite, Step132 diagnostics present.
- Step132 `planeflux_sweep48`: six 48^3 rows completed 250/250, finite, no
  first-failure event, but all failed promotion gates.
- Full suite: 1352 passed, 76 warnings.
- `git diff --check`: passed with only Windows line-ending warnings.
