# Step138 High-Authority Outlet Diagnostic Report

## Decision

Step138 produced bounded real 48^3 / 250-step LBM-only diagnostic evidence for:

```text
planeflux_high_authority48
```

Final Step138 state:

- 6 / 6 real diagnostic rows completed 250 / 250.
- All rows stayed finite.
- All rows had `first_failure_step = null` and `first_failure_reason = null`.
- All rows passed density, population, and Mach stability gates.
- 4 / 6 rows passed candidate mass acceptance.
- 3 / 6 rows avoided the compact x-profile collapse label.
- 2 / 6 rows passed the raw flow-development gate.
- 1 / 6 rows passed the full final hard gate, including mass acceptance and
  no compact-collapse label.
- No Step138 500-step promotion was run.
- No selected 96^3 run is allowed.
- No quasi-2D, FSI, Fluent, or Figure 29.3 parity claim is allowed.

The passing final-hard-gate row is:

```text
ramp85 target0.80 gain0.75 cap0.0075
```

This row justifies a later Step139 proposal for a single 48^3 / 500-step
final-evidence run. Step138 itself remains diagnostic-only and does not enable
selected 96^3.

## Code Surface

Step138 added a bounded Step121 phase:

```text
planeflux_high_authority48
```

The phase uses:

```text
semantics = regularized_plane_flux_controlled_pressure_outlet
row_role = interior_reflection_diagnostic_48
```

This role is not in the selected-candidate semantics set and cannot enable
selected 96^3. Step138 did not add rows to `CANDIDATE_SEMANTICS` or
`REPAIRED_CANDIDATE_SEMANTICS`.

Step138 also added a report/provenance flag:

```text
step138_high_authority_outlet_candidate
```

The flag is written to finite reports, metadata, boundary reports, and
flow-development diagnostics for the 48^3 diagnostic rows. The hard
flow-development gate was not relaxed.

## Artifacts

Tiny smoke artifact:

```text
outputs/step138_high_authority_outlet_diagnostic/tiny_smoke/tiny_step138_high_authority_outlet_smoke
```

48^3 artifact root:

```text
outputs/step138_high_authority_outlet_diagnostic/planeflux_high_authority48
```

Important artifact files:

```text
outputs/step138_high_authority_outlet_diagnostic/tiny_smoke/campaign_manifest.json
outputs/step138_high_authority_outlet_diagnostic/tiny_smoke/tiny_step138_high_authority_outlet_smoke/finite_stability_report.json
outputs/step138_high_authority_outlet_diagnostic/planeflux_high_authority48/campaign_manifest.json
outputs/step138_high_authority_outlet_diagnostic/planeflux_high_authority48/step121_summary.json
outputs/step138_high_authority_outlet_diagnostic/planeflux_high_authority48/step121_gate_report.json
outputs/step138_high_authority_outlet_diagnostic/planeflux_high_authority48/step121_best_boundary_selection.json
outputs/step138_high_authority_outlet_diagnostic/planeflux_high_authority48/duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_out5_250step_high_authority/flow_development_diagnostics_summary.json
```

Both campaign manifests record:

```text
code_commit_at_run = f0284d3f6207eb1c9341dfc9906293b651c6b0f7
```

The Step121 selector wrapper reports `campaign_state = awaiting_48_references`
for this artifact root because Step138 rows are diagnostic rows, not
selected-candidate rows. That selector state is expected and is not a selected
96^3 claim.

## Commands

Tiny smoke:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_high_authority48 `
  --output-dir outputs\step138_high_authority_outlet_diagnostic\tiny_smoke `
  --tiny-smoke `
  --force `
  --no-resume
```

48^3 diagnostic run:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_high_authority48 `
  --output-dir outputs\step138_high_authority_outlet_diagnostic\planeflux_high_authority48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume
```

## Results

All rows completed 250 / 250 and had `validation_claim_allowed = false` and
`selected96_claim_allowed = false`.

| row | ramp | target | gain | cap | mass abs | out/in | mid/in | flux mean | flux max | outlet cv | collapse first | authority tail | saturation tail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| ramp85 target0.80 gain0.75 cap0.0075 | 85 | 0.80 | 0.75 | 0.0075 | 0.003975 | 1.058947 | 0.937216 | 0.088265 | 0.180880 | 0.096511 | none | 0.784361 | 0.000000 |
| ramp90 target0.80 gain0.75 cap0.0075 | 90 | 0.80 | 0.75 | 0.0075 | 0.003963 | 1.076808 | 0.972666 | 0.091996 | 0.191360 | 0.092654 | x30 step250 | 0.790016 | 0.000000 |
| ramp85 target0.85 gain0.75 cap0.0075 | 85 | 0.85 | 0.75 | 0.0075 | 0.002138 | 1.070071 | 0.939970 | 0.094742 | 0.193898 | 0.100405 | x24 step250 | 0.726330 | 0.000000 |
| ramp85 target0.85 gain0.75 cap0.0050 | 85 | 0.85 | 0.75 | 0.0050 | 0.000343 | 1.113990 | 0.999404 | 0.142009 | 0.261678 | 0.147609 | x36 step250 | 0.994469 | 0.238862 |
| ramp85 target0.85 gain1.00 cap0.0075 | 85 | 0.85 | 1.00 | 0.0075 | 0.005120 | 0.962889 | 0.792322 | 0.083829 | 0.210959 | 0.097387 | none | 0.742410 | 0.000000 |
| ramp85 target0.85 gain1.00 cap0.0100 | 85 | 0.85 | 1.00 | 0.0100 | 0.005120 | 0.962889 | 0.792322 | 0.083829 | 0.210959 | 0.097387 | none | 0.556807 | 0.000000 |

Hard-gate status:

```text
requested_window_completed = true for all six rows
finite_pass = true for all six rows
density_gate_pass = true for all six rows
population_gate_pass = true for all six rows
mach_gate_pass = true for all six rows
first_failure_step = null for all six rows
candidate_mass_acceptance_observed_abs < 0.005 for four rows
collapse_first_x = null for three rows
flow_development_gate_pass = true for two rows
full final hard gate pass = true for one row
```

The full final-hard-gate passing row was ramp85 / target0.80 / gain0.75 /
cap0.0075:

```text
candidate_mass_acceptance_observed_abs = 0.003974863988826804
outlet_to_inlet_flux_ratio_tail_mean = 1.0589469344632336
midplane_to_inlet_flux_ratio_tail_mean = 0.9372161279428126
flux_imbalance_rel_tail_mean = 0.08826485542410979
flux_imbalance_rel_tail_max = 0.18087974336724078
outlet_flux_tail_cv = 0.09651149130583905
collapse_first_x = null
collapse_first_step = null
```

The ramp90 / target0.80 / gain0.75 / cap0.0075 row passed the raw ratio,
imbalance, and outlet-CV flow metrics, but it carried a compact-collapse label:

```text
collapse_first_x = 30
collapse_first_step = 250
```

It therefore cannot be promoted as final hard-gate evidence.

The gain1.00 rows reduced outlet ratio below 1.0 but failed other hard gates:

```text
candidate_mass_acceptance_observed_abs = 0.005120382544472485
midplane_to_inlet_flux_ratio_tail_mean = 0.792321699367552
flux_imbalance_rel_tail_max = 0.21095864702906178
```

They do not justify promotion.

## Required Answers

1. Higher `gain_u` and `cap_u` did reduce outlet ratio into the hard-gate range
   for multiple rows.
2. Higher `cap_u` mattered: gain0.75 / cap0.0050 remained close to cap with
   `controller_authority_ratio_tail_mean = 0.9944693608717485` and failed
   flux/outlet-CV/collapse gates, while gain0.75 / cap0.0075 allowed the
   ramp85 / target0.80 row to pass the full final hard gate.
3. The passing ramp85 / target0.80 row also passed flux mean/max and outlet CV.
4. Higher authority reintroduced compact-collapse labels in three rows, so the
   passing row must be selected by the full hard gate, not by ratio alone.
5. Higher authority did not trigger density, population, Mach, or
   first-failure instability in these 250-step rows.
6. The new cap was not exhausted for the passing row:
   `controller_authority_ratio_tail_mean = 0.7843610576607964` and
   `controller_saturation_fraction_tail = 0.0`.
7. A later Step139 single 48^3 / 500-step final-evidence run is justified for
   the ramp85 / target0.80 / gain0.75 / cap0.0075 row.
8. selected 96^3 remains blocked.

## Interpretation

Step138 converts the Step137 near-miss into one bounded 250-step diagnostic row
that passes the full final hard gate. The useful change was not higher gain
alone; the cleaner passing point combined lower target scale with higher
authority:

```text
ramp_steps = 85
target_scale = 0.80
gain_u = 0.75
cap_u = 0.0075
```

This evidence is enough to propose a later single-row 48^3 / 500-step final
evidence run, but not enough to select a boundary or run selected 96^3. The
remaining promotion path must stay bounded: first prove that the same row
survives 500 steps at 48^3, then revisit selected-candidate semantics only in a
later explicitly authorized step.

## Verification

Focused verification and artifact generation:

```text
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step138-initial tests\test_step138_high_authority_outlet_contract.py
D:\working\taichi\env\python.exe -m py_compile experiments\steps\step120_lbm_boundary_repair_large_real_execution.py experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py src\mpm_lbm\sim\lbm\config.py src\mpm_lbm\sim\lbm\fluid.py
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step138-focused tests\test_step138_high_authority_outlet_contract.py tests\test_step137_ramp_target_refinement_contract.py tests\test_step136_ramped_throughput_calibration_contract.py tests\test_step135_interior_reflection_diagnostics_contract.py tests\test_step134_outlet_stationarity_contract.py tests\test_step133_mass_damped_plane_flux_contract.py tests\test_step132_plane_flux_authority_sweep_contract.py tests\test_step131_plane_flux_controller_contract.py
D:\working\taichi\env\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase planeflux_high_authority48 --output-dir outputs\step138_high_authority_outlet_diagnostic\tiny_smoke --tiny-smoke --force --no-resume
D:\working\taichi\env\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase planeflux_high_authority48 --output-dir outputs\step138_high_authority_outlet_diagnostic\planeflux_high_authority48 --allow-large-real-rows --output-interval 5 --force --no-resume
```

Results:

```text
tests/test_step138_high_authority_outlet_contract.py: 4 passed
py_compile: passed
Step131-Step138 focused contract group: 44 passed, 8 Taichi matrix-size warnings
Step138 tiny smoke: completed 20/20, finite_pass = true, selected96_claim_allowed = false
Step138 48^3 diagnostic run: 6/6 rows completed 250/250
Step138 full final hard gate: 1/6 rows passed
```
