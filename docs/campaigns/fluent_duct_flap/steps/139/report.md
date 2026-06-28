# Step139 Plane-Flux Final48 Report

## Decision

Step139 ran the exact Step138 passing row as a single real 48^3 / 500-step
LBM-only final-evidence row:

```text
planeflux_final48
```

Final Step139 hard gate result:

```text
Step139 final hard gate pass = false
```

The row completed 500 / 500 steps, stayed finite, had no first-failure event,
and kept the outlet and midplane flux ratios inside the allowed range. It did
not pass the full final hard gate because the 500-step tail failed candidate
mass acceptance, flux-imbalance mean, and outlet stationarity.

No selected boundary is selected. No selected96, selected-static, 96^3,
quasi-2D validation, FSI validation, Fluent validation, Figure 29.3 parity, or
production-readiness claim is allowed.

Step140 promotion proposal was skipped because Step139 did not pass.

## Code Surface

Step139 added a bounded Step121 phase:

```text
planeflux_final48
```

The phase contains exactly one row:

```text
duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_500step_final
```

The row uses:

```text
semantics = regularized_plane_flux_controlled_pressure_outlet
row_role = final_evidence_candidate_48
grid = 48^3
n_steps = 500
ramp_steps = 85
target_scale = 0.80
gain_u = 0.75
cap_u = 0.0075
gain_rho = 0.001
alpha = 0.02
delta_cap_u = 0.0005
slew_alpha = 0.50
measure_offset = 2
guard_enabled = true
guard_min_ratio = 0.70
lbm_niu = 0.10
```

Step139 did not add the plane-flux semantics to `CANDIDATE_SEMANTICS` or
`REPAIRED_CANDIDATE_SEMANTICS`. The row is final-evidence only and cannot
enable selected96.

## Provenance

Step139 preserves the Step138 source row:

```text
source_step = 138
source_row_name = duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_out5_250step_high_authority
source_solver_state_hash = 34437ee966ac063d03d80bd4a9c9dea30961897cbb87d41cc5c7de1571ef3ed8
source_run_manifest_hash = e689ad17b0de0f478d57ef9d419e2ed10579692cfb94866dbc1095b5c7239969
source_code_commit = f0284d3f6207eb1c9341dfc9906293b651c6b0f7
code_commit_at_run = 4e43162a641085e56a4ba72c8bc013e58cb08cc3
repository_head_at_report = b83c1514e325c3bb5f29d73f8adeab13f6ac623d
```

The source provenance is recorded in the Step139 finite report, run metadata,
boundary report, flow diagnostics, and campaign manifest expected row.
`code_commit_at_run` identifies the code commit used to execute Step139;
`repository_head_at_report` identifies the final Step139 report/docs commit
that also added guard documentation and tests.

## Artifacts

Step139 artifact root:

```text
outputs/step139_planeflux_final48
```

Important files:

```text
outputs/step139_planeflux_final48/planeflux_final48/campaign_manifest.json
outputs/step139_planeflux_final48/planeflux_final48/step121_summary.json
outputs/step139_planeflux_final48/planeflux_final48/step121_gate_report.json
outputs/step139_planeflux_final48/planeflux_final48/step121_best_boundary_selection.json
outputs/step139_planeflux_final48/planeflux_final48/duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_500step_final/finite_stability_report.json
outputs/step139_planeflux_final48/planeflux_final48/duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_500step_final/flow_development_diagnostics_summary.json
outputs/step139_planeflux_final48/step139_long_window_comparison.json
outputs/step139_planeflux_final48/step139_long_window_comparison.csv
outputs/step139_planeflux_final48/step139_failure_forensics.json
outputs/step139_planeflux_final48/step139_failure_forensics.md
```

## Command

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_final48 `
  --output-dir outputs\step139_planeflux_final48\planeflux_final48 `
  --allow-large-real-rows `
  --output-interval 10 `
  --force `
  --no-resume
```

## Results

The row completed the requested long window:

```text
steps_completed = 500
requested_window_completed = true
simulation_backed_artifact = true
finite_pass = true
density_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
mass_drift_gate_pass = true
first_failure_step = null
first_failure_reason = null
limiter_activation_fraction = 0.0
collapse_first_x = null
collapse_first_step = null
selected96_claim_allowed = false
validation_claim_allowed = false
```

The final hard gate failed:

```text
candidate_mass_acceptance_gate_pass = false
candidate_mass_acceptance_observed_abs = 0.008321150189010917
flow_development_gate_pass = false
flux_imbalance_rel_tail_mean = 0.10270018561574665
outlet_flux_tail_cv = 0.11556697847525366
```

The ratio and max-imbalance checks stayed within their hard ranges:

```text
outlet_to_inlet_flux_ratio_tail_mean = 1.0372606489398013
midplane_to_inlet_flux_ratio_tail_mean = 0.9995829419859176
flux_imbalance_rel_tail_max = 0.16810119026843742
```

Controller telemetry:

```text
controller_authority_ratio_tail_mean = 0.5527449179102074
controller_saturation_fraction_tail = 0.0
```

## Long-Window Comparison

Step138 250-step source row:

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

Step139 500-step final row:

```text
candidate_mass_acceptance_observed_abs = 0.008321150189010917
outlet_to_inlet_flux_ratio_tail_mean = 1.0372606489398013
midplane_to_inlet_flux_ratio_tail_mean = 0.9995829419859176
flux_imbalance_rel_tail_mean = 0.10270018561574665
flux_imbalance_rel_tail_max = 0.16810119026843742
outlet_flux_tail_cv = 0.11556697847525366
collapse_first_x = null
collapse_first_step = null
```

Interpretation:

```text
Step139 falsifies the Step138 short-window promotion candidate.
No selected boundary.
No selected96.
Next step should analyze first failure or long-window flow-development drift.
```

## Failure Forensics

First failed gate:

```text
candidate_mass_acceptance_gate_pass
```

Failed gates:

```text
candidate_mass_acceptance_gate_pass
flow_development_gate_pass
flux_imbalance_rel_tail_mean
outlet_flux_tail_cv
```

Failure classes:

```text
mass_acceptance_failed_after_250
flux_mean_or_max_drift
outlet_cv_drift
```

The source Step138 250-step row passed the full final hard gate. Step139 stayed
finite through 500 steps but failed final 500-step gates. The long-window drift
did not create compact x-profile collapse and did not saturate the controller,
but it did move mass acceptance, mean flux imbalance, and outlet stationarity
outside the hard limits.

Suggested next diagnostic:

```text
Analyze long-window mass drift and outlet stationarity around steps 250-500
without changing Step139 parameters and without running selected96.
```

## Conditional Tasks

Step140 promotion proposal was skipped because Step139 failed the final hard
gate.

Failure forensics was executed because Step139 failed the final hard gate.

## Architecture Contract

Task5 added a static generic solver architecture contract:

```text
docs/GENERIC_SOLVER_ARCHITECTURE_CONTRACT.md
tests/test_step139_generic_solver_architecture_contract.py
```

The contract keeps solver-core packages benchmark-agnostic, keeps benchmark
adapters outside solver equations, and keeps official Fluent payloads outside
the repository. The guard is static only and does not run a simulation.

## Fluent Official Local-Execution Guard

Task6 added Fluent official local-execution prep artifacts:

```text
docs/campaigns/fluent_duct_flap/fluent_official_local_execution_guard.md
configs/fluent_official_2way_fsi_local_execution_schema.json
configs/fluent_official_monitor_export_schema.json
outputs/fluent_official_local_execution_prep/guard_report.json
tests/test_fluent_official_local_execution_guard.py
```

The guard report records:

```text
fluent_run_executed = false
external_action_taken = false
official_payload_committed = false
validation_claim_allowed = false
gap_only_comparison_readiness = true
```

No Fluent official file is committed and no Fluent validation claim is allowed.

## Verification

Initial red-to-green and phase verification:

```text
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step139-red tests\test_step139_planeflux_final48_contract.py
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step139-green tests\test_step139_planeflux_final48_contract.py
D:\working\taichi\env\python.exe -m py_compile experiments\steps\step120_lbm_boundary_repair_large_real_execution.py experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py src\mpm_lbm\sim\lbm\config.py src\mpm_lbm\sim\lbm\fluid.py
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step139-phase tests\test_step139_planeflux_final48_contract.py tests\test_step138_high_authority_outlet_contract.py tests\test_step137_ramp_target_refinement_contract.py
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step139-arch-red2 tests\test_step139_generic_solver_architecture_contract.py
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step139-arch-green tests\test_step139_generic_solver_architecture_contract.py
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-fluent-official-guard-red tests\test_fluent_official_local_execution_guard.py
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-fluent-official-guard-green tests\test_fluent_official_local_execution_guard.py
```

Results:

```text
Step139 contract red test: 2 failed / 2 passed before implementation
Step139 contract green test: 4 passed
Step139 + Step138 + Step137 focused phase tests: 12 passed
Generic solver architecture contract red test: 1 failed / 3 passed before contract doc
Generic solver architecture contract green test: 4 passed
Fluent official local-execution guard red test: 4 failed / 1 passed before guard artifacts
Fluent official local-execution guard green test: 5 passed
py_compile: passed
Step139 real 48^3 / 500-step run: completed 500/500, finite, final hard gate failed
```

Final verification after Task5/Task6 and current-doc updates:

```text
D:\working\taichi\env\python.exe -m py_compile experiments\steps\step120_lbm_boundary_repair_large_real_execution.py experiments\steps\step121_lbm_boundary_real_campaign_and_gate_correction.py src\mpm_lbm\sim\diagnostics\lbm_boundary_diagnostics.py src\mpm_lbm\sim\lbm\config.py src\mpm_lbm\sim\lbm\fluid.py tests\test_step139_generic_solver_architecture_contract.py tests\test_fluent_official_local_execution_guard.py
D:\working\taichi\env\python.exe -c "<json load check for current/guard/Step139 artifacts>"
git diff --check
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step139-final-focused-rerun tests\test_step139_planeflux_final48_contract.py tests\test_step138_high_authority_outlet_contract.py tests\test_step137_ramp_target_refinement_contract.py tests\test_step136_ramped_throughput_calibration_contract.py tests\test_step135_interior_reflection_diagnostics_contract.py tests\test_step134_outlet_stationarity_contract.py tests\test_step133_mass_damped_plane_flux_contract.py tests\test_step132_plane_flux_authority_sweep_contract.py tests\test_step131_plane_flux_controller_contract.py
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step139-campaign-provenance-rerun tests\test_step130_flow_development_repair_contract.py tests\test_step130_flow_development_diagnostics_contract.py tests\test_step129_repair_checkpoint_counter_contract.py tests\test_step128_boundary_formulation_repair_contract.py tests\test_step125_campaign_provenance_identity_contract.py tests\test_step124_boundary_campaign_execution_contract.py tests\test_step123_boundary_campaign_execution_decision_contract.py
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step139-policy-guards tests\test_step56_behavior_preservation_contract.py tests\test_step56_canonical_runtime_migration_contract.py tests\test_step56_import_execution_contract.py tests\test_step56_legacy_shim_contract.py tests\test_step57_behavior_preservation_contract.py tests\test_step57_driver_support_migration_contract.py tests\test_step57_import_execution_contract.py tests\test_step57_legacy_shim_contract.py tests\test_step57_src_init_export_contract.py tests\test_step57_step56_regression_contract.py tests\test_step58_behavior_preservation_contract.py tests\test_step58_fsidriver_migration_contract.py tests\test_step58_import_execution_contract.py tests\test_step58_legacy_shim_contract.py tests\test_step58_optional_bridge_contract.py tests\test_step58_step57_regression_contract.py
D:\working\taichi\env\python.exe -m pytest -q --basetemp outputs\tmp\pytest-step139-new-guards-final tests\test_step139_planeflux_final48_contract.py tests\test_step139_generic_solver_architecture_contract.py tests\test_fluent_official_local_execution_guard.py
```

Final verification results:

```text
py_compile: passed
json load check: passed for 6 JSON files
Step139 artifact selected/96 name scan: empty
git diff --check: passed with CRLF warnings only
Step139-Step131 focused contracts: 48 passed, 8 Taichi matrix-size warnings
Step130/129/128/125/124/123 campaign/provenance contracts: 44 passed, 20 Taichi matrix-size warnings
Step56-Step58 policy guard contracts: 50 passed
Step139 + generic architecture + Fluent local guard contracts: 13 passed
```

One earlier Step139 focused pytest attempt and one earlier campaign/provenance
pytest attempt hit command timeouts before completion; both groups were rerun
with longer timeouts and passed as recorded above.
