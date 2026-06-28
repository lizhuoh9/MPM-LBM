# Step136 Ramped-Inlet Throughput Calibration Report

## Decision

Step136 produced bounded real 48^3 / 250-step LBM-only calibration evidence for
`planeflux_ramp_tuned48`.

Final Step136 state:

- 6 / 6 real calibration rows completed 250 / 250.
- All rows stayed finite.
- All rows had `first_failure_step = null` and `first_failure_reason = null`.
- 2 / 6 rows passed candidate mass acceptance.
- 0 / 6 rows passed the flow-development gate.
- No Step136 500-step promotion was run.
- No selected 96^3 run is allowed.
- No quasi-2D, FSI, Fluent, or Figure 29.3 parity claim is allowed.

The evidence supports the Step135 diagnosis that ramped inlet startup can remove
or delay compact-collapse labels and improve mass behavior, but the calibrated
rows still overdrive throughput or retain flow-development failure. Step136 is
therefore report-only calibration evidence, not boundary selection.

## Code Surface

Step136 added a bounded Step121 phase:

```text
planeflux_ramp_tuned48
```

The phase uses:

```text
row_role = interior_reflection_diagnostic_48
```

This role is not in the selected-candidate semantics set and cannot enable
selected 96^3.

Step136 added a report-visible LBM configuration field:

```text
open_boundary_flux_control_target_scale = 1.0
```

The default is `1.0`, so existing controller behavior is unchanged unless a row
explicitly opts into a different target scale. The plane-flux controller target
is now:

```text
target_outlet_flux = open_boundary_flux_control_target_scale * inlet_flux_plane
```

The field is written to solver-state hashes, Step121 manifests, Step120 run
metadata, finite reports, boundary reports, flow-development diagnostics, and
limiter summaries.

## Artifacts

Tiny smoke artifact:

```text
outputs/step136_ramped_throughput_calibration/tiny_smoke/tiny_step136_ramped_throughput_calibration_smoke
```

48^3 artifact root:

```text
outputs/step136_ramped_throughput_calibration/planeflux_ramp_tuned48
```

Important artifact files:

```text
outputs/step136_ramped_throughput_calibration/tiny_smoke/campaign_manifest.json
outputs/step136_ramped_throughput_calibration/tiny_smoke/tiny_step136_ramped_throughput_calibration_smoke/finite_stability_report.json
outputs/step136_ramped_throughput_calibration/planeflux_ramp_tuned48/campaign_manifest.json
outputs/step136_ramped_throughput_calibration/planeflux_ramp_tuned48/step121_summary.json
outputs/step136_ramped_throughput_calibration/planeflux_ramp_tuned48/step121_best_boundary_selection.json
outputs/step136_ramped_throughput_calibration/planeflux_ramp_tuned48/duct_only_48_regularized_plane_flux_controlled_gain0p50_cap0p005_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp100_target0p90_out5_250step_ramp_tuned/flow_development_diagnostics_summary.json
```

Both campaign manifests and all row finite reports record:

```text
code_commit_at_run = e46ad23e361341567b92b8e114711f87d3f565f3
```

The Step121 campaign selector wrapper still reports
`campaign_state = awaiting_48_references` because Step136 rows are diagnostic /
calibration rows, not selected-candidate rows. The Step136 decision above is
based on the six row-level finite and flow-development reports.

## Commands

Tiny smoke:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_ramp_tuned48 `
  --output-dir outputs\step136_ramped_throughput_calibration\tiny_smoke `
  --tiny-smoke `
  --force `
  --no-resume
```

48^3 calibration run:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_ramp_tuned48 `
  --output-dir outputs\step136_ramped_throughput_calibration\planeflux_ramp_tuned48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume
```

## Results

All rows completed 250 / 250 and had `validation_claim_allowed = false`.

| row | ramp | gain | cap | target | mass abs | mass gate | flux mean | out/in | mid/in | outlet cv | collapse first |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |
| gain0.35 cap0.005 target1.00 | 100 | 0.35 | 0.005 | 1.00 | 0.007327 | false | 0.314839 | 1.467821 | 1.369278 | 0.077056 | none |
| gain0.50 cap0.005 target0.90 | 100 | 0.50 | 0.005 | 0.90 | 0.002741 | true | 0.228888 | 1.306429 | 1.228018 | 0.086540 | none |
| gain0.50 cap0.005 target0.95 | 100 | 0.50 | 0.005 | 0.95 | 0.004158 | true | 0.235060 | 1.317577 | 1.233894 | 0.089170 | none |
| gain0.50 cap0.005 target1.00 | 100 | 0.50 | 0.005 | 1.00 | 0.005572 | false | 0.241105 | 1.328695 | 1.239761 | 0.091770 | none |
| gain0.50 cap0.005 target1.00 | 75 | 0.50 | 0.005 | 1.00 | 0.006566 | false | 0.179950 | 1.230050 | 1.078922 | 0.111512 | x=24 step=250 |
| gain0.50 cap0.0075 target1.00 | 100 | 0.50 | 0.0075 | 1.00 | 0.005572 | false | 0.241105 | 1.328695 | 1.239761 | 0.091770 | none |

The best mass row was the ramp100 / gain0.50 / cap0.005 / target0.90 row:

```text
candidate_mass_acceptance_observed_abs = 0.0027411073257309804
flux_imbalance_rel_tail_mean = 0.22888777098124222
outlet_to_inlet_flux_ratio_tail_mean = 1.3064291443826772
midplane_to_inlet_flux_ratio_tail_mean = 1.228018341923524
outlet_flux_tail_cv = 0.08653967735783066
```

The best flux-imbalance row was the ramp75 / gain0.50 / cap0.005 /
target1.00 row:

```text
candidate_mass_acceptance_observed_abs = 0.0065664103097401475
flux_imbalance_rel_tail_mean = 0.17995040672859994
outlet_to_inlet_flux_ratio_tail_mean = 1.2300496083019266
midplane_to_inlet_flux_ratio_tail_mean = 1.0789222122987672
outlet_flux_tail_cv = 0.11151179601758945
collapse_first_x = 24
collapse_first_step = 250
```

No row passed the flow-development gate. The target0.90 and target0.95 rows
passed mass acceptance, but their outlet and midplane ratios remained above the
acceptable range. The ramp75 row reduced flux imbalance and midplane ratio, but
it reintroduced an interior compact-collapse label at `x = 24`, step 250.

Controller saturation did not explain the failure. All six rows had
`controller_saturation_fraction_tail = 0.0` and `limiter_activation_fraction =
0.0`; the failure is in the developed flow metrics, not limiter clipping.

## Interpretation

Step136 confirms that the ramp100 branch from Step135 is the right bounded
surface for throughput calibration: it removes the compact-collapse label in the
five ramp100 rows and lowers mass error enough that target0.90 and target0.95
pass candidate mass acceptance.

Target scaling is useful but not sufficient. Lowering the target from 1.00 to
0.90 improves mass and reduces overdrive, but the row still reports
`outlet_to_inlet_flux_ratio_tail_mean = 1.3064291443826772` and
`midplane_to_inlet_flux_ratio_tail_mean = 1.228018341923524`. That remains a
flow-development failure.

Increasing `open_boundary_flux_correction_cap_u` from 0.005 to 0.0075 did not
change the observed tail metrics for the gain0.50 / ramp100 / target1.00 row.
In this bounded window the cap is not the active bottleneck.

Shortening the ramp to 75 steps gives the best flux-imbalance number, but it
reintroduces a compact-collapse label at the interior `x = 24` sample at the
final step. That does not justify promotion.

Step136 therefore keeps selected 96^3 blocked. A later step should remain
bounded at 48^3 and either continue target-scaling around the target0.90 branch
with additional interior-profile controls or explicitly change the open-boundary
formulation. It should not run selected 96^3 or claim Fluent/FSI readiness from
these artifacts.

## Verification

Focused verification run before and during artifact generation:

```text
D:\working\taichi\env\python.exe -m pytest -q tests\test_step136_ramped_throughput_calibration_contract.py --basetemp=outputs\tmp\pytest-step136-contract
D:\working\taichi\env\python.exe -m py_compile experiments\steps\step118_lbm_open_boundary_stability_repair.py experiments\steps\step120_lbm_boundary_repair_large_real_execution.py experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py src\mpm_lbm\sim\lbm\config.py src\mpm_lbm\sim\lbm\fluid.py tests\test_step136_ramped_throughput_calibration_contract.py
D:\working\taichi\env\python.exe -m pytest -q tests\test_step135_interior_reflection_diagnostics_contract.py tests\test_step134_outlet_stationarity_contract.py tests\test_step133_mass_damped_plane_flux_contract.py tests\test_step132_plane_flux_authority_sweep_contract.py tests\test_step131_plane_flux_controller_contract.py --basetemp=outputs\tmp\pytest-step131-135-after-step136
D:\working\taichi\env\python.exe -m pytest -q tests\test_step130_flow_development_diagnostics_contract.py tests\test_step129_repair_checkpoint_counter_contract.py tests\test_step128_boundary_formulation_repair_contract.py --basetemp=outputs\tmp\pytest-step128-130-after-step136
D:\working\taichi\env\python.exe -m pytest -q tests\test_step56_behavior_preservation_contract.py tests\test_step57_step56_regression_contract.py tests\test_step58_step57_regression_contract.py --basetemp=outputs\tmp\pytest-step136-policy-rerun
D:\working\taichi\env\python.exe -m pytest -q tests\test_step125_campaign_provenance_identity_contract.py tests\test_step124_boundary_campaign_execution_contract.py tests\test_step123_boundary_campaign_execution_decision_contract.py --basetemp=outputs\tmp\pytest-step123-125-after-step136-rerun
git diff --check
```

Results:

```text
tests/test_step136_ramped_throughput_calibration_contract.py: 6 passed
py_compile: passed
Step131-Step135 contract group: 30 passed, 8 Taichi matrix-size warnings
Step128-Step130 contract group: 17 passed, 12 Taichi matrix-size warnings
Step56-Step58 policy group: 10 passed
Step123-Step125 campaign/provenance group: 22 passed, 8 Taichi matrix-size warnings
git diff --check: passed
```

The initial combined Step123-Step130 command exceeded a 180-second timeout after
eight passing tests, so the same coverage was rerun as two smaller groups.
