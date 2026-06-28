# Step141 Density-Feedback Isolation Diagnostic Report

## Decision

Step141 ran a bounded real 48^3 / 250-step LBM-only density-feedback isolation
diagnostic:

```text
planeflux_density_feedback_isolation48
```

The phase contains exactly four rows, all using:

```text
semantics = regularized_plane_flux_controlled_pressure_outlet
row_role = density_feedback_isolation_diagnostic_48
grid = 48^3
n_steps = 250
output_interval = 5
ramp_steps = 85
target_scale = 0.80
gain_u = 0.75
cap_u = 0.0075
alpha = 0.02
delta_cap_u = 0.0005
slew_alpha = 0.50
measure_offset = 2
guard_enabled = true
guard_min_ratio = 0.70
lbm_niu = 0.10
```

Only `gain_rho` varies:

```text
0.001
0.0
0.00025
0.0005
```

The audit decision is:

```text
decision_case = density_feedback_isolation_insufficient
step142_single_500step_final_evidence_proposal_allowed = false
selected96_execution_allowed = false
validation_claim_allowed = false
```

Lowering or removing density feedback did not improve the Step139/Step138
short-window baseline at 250 steps. The baseline repeat with `gain_rho =
0.001` had the lowest `candidate_mass_acceptance_observed_abs` in the
Step141 comparison. Step142 should therefore stay with a mass-neutral
plane-flux controller design proposal or further formulation diagnosis, not a
500-step final-evidence run.

## Source Provenance

Step141 links each row to the Step139 source row and Step140 summary:

```text
source_step = 140
source_step139_row_name = duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_500step_final
source_step139_solver_state_hash = 94f3ce3773430d8a8e851c6e8408b8a93a32405a09df1ff042022c5c0ddf9eab
source_step139_run_manifest_hash = 59139b253ba9dabdcbfb31c50a50f40ef146eada42068d19d6234037a6c446b6
source_step139_code_commit = 4e43162a641085e56a4ba72c8bc013e58cb08cc3
source_step140_summary_hash = a2cabe6f927750f161e892b8b625087193f2a43218ebe4c68a2e970d3817f7d8
source_step140_summary_path = outputs/step140_long_window_drift_forensics/step140_failure_mechanism_summary.json
source_step140_dominant_failure_mechanism = mass_accumulation_with_outlet_stationarity_drift
source_step140_mass_drift_mechanism = tail_mass_acceptance_failure
```

Step141 interprets the Step140 mass label as
`post_250_mass_excursion_with_tail_acceptance_failure`: the long-window mass
rose quickly after step 250, later partly relaxed, and still failed the
hard-tail candidate mass-acceptance gate.

## Artifacts

Step141 artifact root:

```text
outputs/step141_density_feedback_isolation
```

Phase root:

```text
outputs/step141_density_feedback_isolation/density_feedback_isolation48
```

Important files:

```text
outputs/step141_density_feedback_isolation/density_feedback_isolation48/campaign_manifest.json
outputs/step141_density_feedback_isolation/density_feedback_isolation48/step121_summary.json
outputs/step141_density_feedback_isolation/density_feedback_isolation48/step121_gate_report.json
outputs/step141_density_feedback_isolation/density_feedback_isolation48/step121_best_boundary_selection.json
outputs/step141_density_feedback_isolation/step141_density_feedback_comparison.json
outputs/step141_density_feedback_isolation/step141_density_feedback_comparison.csv
outputs/step141_density_feedback_isolation/step141_decision_summary.json
```

## Results

All four rows completed the bounded diagnostic window:

```text
requested_window_completed = true
finite_pass = true
density_gate_pass = true
population_gate_pass = true
mach_gate_pass = true
mass_drift_gate_pass = true
flow_development_gate_pass = true
first_failure_step = null
collapse_first_x = null
selected96_claim_allowed = false
validation_claim_allowed = false
```

Sorted audit comparison:

```text
gain_rho = 0.001
candidate_mass_acceptance_observed_abs = 0.003974863988826804
flux_imbalance_rel_tail_mean = 0.08826485542410979
outlet_flux_tail_cv = 0.09651149130583905
outlet_to_inlet_flux_ratio_tail_mean = 1.0589469344632336

gain_rho = 0.0005
candidate_mass_acceptance_observed_abs = 0.003977426612971523
flux_imbalance_rel_tail_mean = 0.08823144079765681
outlet_flux_tail_cv = 0.09651284032492045
outlet_to_inlet_flux_ratio_tail_mean = 1.0588559920832377

gain_rho = 0.00025
candidate_mass_acceptance_observed_abs = 0.003978707752511535
flux_imbalance_rel_tail_mean = 0.08821456045076578
outlet_flux_tail_cv = 0.09651300200390653
outlet_to_inlet_flux_ratio_tail_mean = 1.0588104243397933

gain_rho = 0.0
candidate_mass_acceptance_observed_abs = 0.003979989185473907
flux_imbalance_rel_tail_mean = 0.0881982312839506
outlet_flux_tail_cv = 0.09651379624841921
outlet_to_inlet_flux_ratio_tail_mean = 1.0587651535870601
```

The rows are nearly identical at the 250-step window. Removing density feedback
slightly reduces mean flux imbalance but slightly worsens mass acceptance and
outlet stationarity. This does not support density feedback as the dominant
cause of Step140's post-250 tail failure.

## Commands

Real phase:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction `
  --phase planeflux_density_feedback_isolation48 `
  --output-dir outputs\step141_density_feedback_isolation\density_feedback_isolation48 `
  --allow-large-real-rows `
  --output-interval 5 `
  --force `
  --no-resume
```

Audit:

```powershell
& 'D:\working\taichi\env\python.exe' -m experiments.steps.step141_density_feedback_isolation_audit `
  --phase-root outputs\step141_density_feedback_isolation\density_feedback_isolation48 `
  --step140-summary outputs\step140_long_window_drift_forensics\step140_failure_mechanism_summary.json `
  --output-dir outputs\step141_density_feedback_isolation `
  --force
```

## Gate State

Step141 does not change the selected-boundary state:

```text
selected96_execution_allowed = false
selected_static_execution_allowed = false
validation_claim_allowed = false
quasi2d_validation_claim_allowed = false
fsi_validation_claim_allowed = false
fluent_validation_claim_allowed = false
production_readiness_claim_allowed = false
```

Step141 did not run selected96, selected-static, 96^3, Fluent, FSI, or any
500-step row. It did not add selected-candidate semantics and did not relax
hard gates.
