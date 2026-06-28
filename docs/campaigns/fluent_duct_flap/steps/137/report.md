# Step137 Refined Ramp-Target Throughput Window Report

## Decision

Step137 produced bounded real 48^3 / 250-step LBM-only diagnostic evidence for:

```text
planeflux_ramp_refined48
```

Final Step137 state:

- 6 / 6 real diagnostic rows completed 250 / 250.
- All rows stayed finite.
- All rows had `first_failure_step = null` and `first_failure_reason = null`.
- All rows passed candidate mass acceptance.
- All rows avoided the compact x-profile collapse label.
- 0 / 6 rows passed the final hard flow-development gate.
- No Step137 500-step promotion was run.
- No selected 96^3 run is allowed.
- No quasi-2D, FSI, Fluent, or Figure 29.3 parity claim is allowed.

Step137 answers the Step136 question narrowly: intermediate ramp duration
removes the ramp75 compact-collapse label, but lower target scale does not fix
the remaining throughput overdrive. Step138 48^3 / 500-step final evidence is
not justified from these artifacts.

## Code Surface

Step137 added a bounded Step121 phase:

```text
planeflux_ramp_refined48
```

The phase uses:

```text
semantics = regularized_plane_flux_controlled_pressure_outlet
row_role = interior_reflection_diagnostic_48
```

This role is not in the selected-candidate semantics set and cannot enable
selected 96^3. Step137 did not add rows to `CANDIDATE_SEMANTICS` or
`REPAIRED_CANDIDATE_SEMANTICS`.

Step137 also added a report/provenance flag:

```text
step137_ramp_target_refinement_candidate
```

The flag is written to finite reports, metadata, boundary reports, and
flow-development diagnostics for the 48^3 diagnostic rows. The hard
flow-development gate was not relaxed.

## Artifacts

Tiny smoke artifact:

```text
outputs/step137_ramp_target_refinement/tiny_smoke/tiny_step137_ramp_target_refinement_smoke
```

48^3 artifact root:

```text
outputs/step137_ramp_target_refinement/planeflux_ramp_refined48
```

Important artifact files:

```text
outputs/step137_ramp_target_refinement/tiny_smoke/campaign_manifest.json
outputs/step137_ramp_target_refinement/tiny_smoke/tiny_step137_ramp_target_refinement_smoke/finite_stability_report.json
outputs/step137_ramp_target_refinement/planeflux_ramp_refined48/campaign_manifest.json
outputs/step137_ramp_target_refinement/planeflux_ramp_refined48/step121_summary.json
outputs/step137_ramp_target_refinement/planeflux_ramp_refined48/step121_gate_report.json
outputs/step137_ramp_target_refinement/planeflux_ramp_refined48/step121_best_boundary_selection.json
outputs/step137_ramp_target_refinement/planeflux_ramp_refined48/duct_only_48_regularized_plane_flux_controlled_gain0p50_cap0p005_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p85_out5_250step_ramp_refined/flow_development_diagnostics_summary.json
```

Both campaign manifests and all row finite reports record:

```text
code_commit_at_run = 5cf3e4b2442d5239605d5506e81033fc376eb032
```

The Step121 selector wrapper reports `campaign_state = awaiting_48_references`
because Step137 rows are diagnostic rows, not selected-candidate rows. The
Step137 decision above is based on the six row-level finite and
flow-development reports.

## Commands

Tiny smoke:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_ramp_refined48 `
  --output-dir outputs\step137_ramp_target_refinement\tiny_smoke `
  --tiny-smoke `
  --force `
  --no-resume
```

48^3 diagnostic run:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_ramp_refined48 `
  --output-dir outputs\step137_ramp_target_refinement\planeflux_ramp_refined48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume
```

## Results

All rows completed 250 / 250 and had `validation_claim_allowed = false` and
`selected96_claim_allowed = false`.

| row | ramp | target | mass abs | out/in | mid/in | flux mean | flux max | outlet cv | collapse first | x24 cv | x36 cv | x47 cv | authority tail | limiter frac |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| ramp85 target0.85 | 85 | 0.85 | 0.002018 | 1.246561 | 1.141811 | 0.191020 | 0.292279 | 0.091622 | none | 0.211729 | 0.156850 | 0.091622 | 0.952345 | 0.0 |
| ramp85 target0.90 | 85 | 0.90 | 0.003449 | 1.255029 | 1.145251 | 0.196038 | 0.300637 | 0.094523 | none | 0.215257 | 0.160824 | 0.094523 | 0.888311 | 0.0 |
| ramp90 target0.80 | 90 | 0.80 | 0.000616 | 1.263616 | 1.170339 | 0.202011 | 0.294580 | 0.090650 | none | 0.192036 | 0.142755 | 0.090650 | 0.991588 | 0.0 |
| ramp90 target0.85 | 90 | 0.85 | 0.001813 | 1.262942 | 1.171400 | 0.202100 | 0.299558 | 0.087786 | none | 0.199245 | 0.153809 | 0.087786 | 0.951379 | 0.0 |
| ramp90 target0.90 | 90 | 0.90 | 0.003249 | 1.272712 | 1.175833 | 0.207776 | 0.307918 | 0.090931 | none | 0.202324 | 0.157321 | 0.090931 | 0.886720 | 0.0 |
| ramp100 target0.85 | 100 | 0.85 | 0.001321 | 1.295251 | 1.222135 | 0.222584 | 0.315621 | 0.083877 | none | 0.167266 | 0.149354 | 0.083877 | 0.937960 | 0.0 |

Hard-gate status:

```text
requested_window_completed = true for all six rows
finite_pass = true for all six rows
density_gate_pass = true for all six rows
population_gate_pass = true for all six rows
mach_gate_pass = true for all six rows
first_failure_step = null for all six rows
hard_stop_mass_drift_gate_pass = true for all six rows
candidate_mass_acceptance_observed_abs < 0.005 for all six rows
collapse_first_x = null for all six rows
collapse_first_step = null for all six rows
flow_development_gate_pass = false for all six rows
```

The best outlet ratio row was ramp85 / target0.85:

```text
outlet_to_inlet_flux_ratio_tail_mean = 1.246561166160358
midplane_to_inlet_flux_ratio_tail_mean = 1.1418110718950278
flux_imbalance_rel_tail_mean = 0.19102045308771165
flux_imbalance_rel_tail_max = 0.29227885610916315
outlet_flux_tail_cv = 0.09162197337437686
```

This is still outside the final hard gate because outlet ratio remains above
`1.20`, flux mean remains above `0.10`, and flux max remains above `0.20`.

The best mass row was ramp90 / target0.80:

```text
candidate_mass_acceptance_observed_abs = 0.0006162400457775661
outlet_to_inlet_flux_ratio_tail_mean = 1.2636158741752672
midplane_to_inlet_flux_ratio_tail_mean = 1.170339464016481
flux_imbalance_rel_tail_mean = 0.20201121638125025
```

It also fails the final hard flow-development gate.

## Required Answers

1. `target_scale = 0.85` or `target_scale = 0.80` did not reduce outlet ratio
   below `1.20`. The best outlet ratio in Step137 was `1.246561166160358`.
2. `ramp_steps = 85` and `ramp_steps = 90` avoided the Step136 ramp75 compact
   collapse label. All Step137 rows had `collapse_first_x = null` and
   `collapse_first_step = null`.
3. No row passed the final hard flow-development gates.
4. Step138 48^3 / 500-step final evidence is not justified from Step137.
5. selected 96^3 remains blocked.

## Interpretation

Step137 improves the collapse part of the Step136 tradeoff: intermediate ramps
avoid the ramp75 compact-collapse label while keeping candidate mass acceptance
below `0.005`.

That improvement is not enough. Lowering target scale into the `0.80` to `0.90`
window did not bring outlet ratio inside the final hard gate, and all rows
still fail the flux-imbalance gates. The best outlet ratio remains above
`1.20`, and the best flux-imbalance mean remains above `0.10`.

The failure is therefore no longer a compact-collapse-only diagnosis. Step137
points to a remaining open-boundary formulation or inlet/outlet coupling issue:
the controller can keep finite mass/stationarity behavior, but the developed
flow remains overdriven relative to inlet and midplane checks.

The next step should not be 500-step evidence. A later step should either
change the ramp profile / bulk-development formulation at 48^3 / 250 steps or
revisit the open-boundary coupling itself. selected 96^3 remains blocked until
a later explicitly authorized selected-candidate contract changes that with
artifact-backed evidence.

## Verification

Focused verification and artifact generation:

```text
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step137-initial tests\test_step137_ramp_target_refinement_contract.py
D:\working\taichi\env\python.exe -m py_compile experiments\steps\step120_lbm_boundary_repair_large_real_execution.py experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py src\mpm_lbm\sim\lbm\config.py src\mpm_lbm\sim\lbm\fluid.py
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step137-focused tests\test_step137_ramp_target_refinement_contract.py tests\test_step136_ramped_throughput_calibration_contract.py tests\test_step135_interior_reflection_diagnostics_contract.py tests\test_step134_outlet_stationarity_contract.py tests\test_step133_mass_damped_plane_flux_contract.py tests\test_step132_plane_flux_authority_sweep_contract.py tests\test_step131_plane_flux_controller_contract.py
D:\working\taichi\env\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase planeflux_ramp_refined48 --output-dir outputs\step137_ramp_target_refinement\tiny_smoke --tiny-smoke --force --no-resume
D:\working\taichi\env\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase planeflux_ramp_refined48 --output-dir outputs\step137_ramp_target_refinement\planeflux_ramp_refined48 --allow-large-real-rows --output-interval 5 --force --no-resume
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step137-step128-130-long tests\test_step130_flow_development_diagnostics_contract.py tests\test_step129_repair_checkpoint_counter_contract.py tests\test_step128_boundary_formulation_repair_contract.py
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step137-step123-125 tests\test_step125_campaign_provenance_identity_contract.py tests\test_step124_boundary_campaign_execution_contract.py tests\test_step123_boundary_campaign_execution_decision_contract.py
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step137-policy tests\test_step56_behavior_preservation_contract.py tests\test_step57_step56_regression_contract.py tests\test_step58_step57_regression_contract.py
```

Results:

```text
tests/test_step137_ramp_target_refinement_contract.py: 4 passed
py_compile: passed
Step131-Step137 focused contract group: 40 passed, 8 Taichi matrix-size warnings
Step137 tiny smoke: completed 20/20, finite_pass = true, selected96_claim_allowed = false
Step137 48^3 diagnostic run: 6/6 rows completed 250/250
Step128-Step130 contract group: 17 passed, 12 Taichi matrix-size warnings
Step123-Step125 campaign/provenance group: 22 passed, 8 Taichi matrix-size warnings
Step56-Step58 policy group: 10 passed
```

The initial combined Step123-Step130 command exceeded a 240-second timeout, and
the first shorter Step128-Step130 retry exceeded a 180-second timeout. The same
coverage was rerun as longer/smaller groups and passed as recorded above.
