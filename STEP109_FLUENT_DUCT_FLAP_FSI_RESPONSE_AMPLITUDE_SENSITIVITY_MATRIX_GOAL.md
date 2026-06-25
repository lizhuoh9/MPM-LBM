# Step109 Fluent Duct-Flap FSI Response Amplitude Sensitivity Matrix Goal

This goal starts from `origin/main` Step108 commit `69331ef6c5ef71b3715fdd42ea00c69e80490293`. Step108 is accepted: it mapped the public Fluent tutorial `10 m/s` inlet to low-Mach `u_lbm = 0.02`, ran `50` official FSI steps with `120` LBM substeps per official step, covered `0.025 s`, and compared the resulting proxy displacement curve against the Step107 public-plot reference.

Step108 did not materially reduce the displacement error. The Step108 proxy peak is `1.2332112646618043e-6 m`, while the Step107 public reference peak is `0.000395 m`; the solver remains roughly `320x` low in amplitude. Step109 must therefore diagnose the response-amplitude bottleneck with an explicit sensitivity matrix rather than continuing with gap-only or preflow-only documentation.

## One-Sentence Goal

Run a bounded response-amplitude sensitivity matrix around the Step108 official-speed low-Mach setup, compare each successful candidate with the Step107 public Fluent plot reference, and identify whether reaction cap/scale, structural proxy stiffness/mass, or monitor definition is the dominant reason the proxy displacement is still hundreds of times too small.

## Public Tutorial Scope

Use only public tutorial facts from the Ansys Fluent two-way FSI tutorial and the already committed Step107 public-plot digitization:

- inlet speed: `10 m/s`
- duct length: `0.10 m`
- official transient: `50` steps at `0.0005 s`
- silicone-rubber material reference: density `1600`, Young's modulus `1e6`, Poisson ratio `0.47`
- public structural monitor name: `structural-point-flap`
- public structural monitor location: `x = 0.0505 m`, `y = 0.0095 m`
- report quantity: vertex-average total displacement

Do not download, commit, or depend on official Fluent case, mesh, journal, data, private CSV, or image payloads.

## Allowed Statement

The final Step109 report may claim only:

```text
A response-amplitude sensitivity matrix was run against the Step107 public Fluent plot reference, and the dominant proxy parameters controlling displacement amplitude were identified.
```

## Forbidden Statements

The final Step109 report, docs, logs, configs, and artifacts must not claim:

```text
Fluent validation passed
Fluent equivalence achieved
official Fluent mesh reproduced
official dynamic mesh reproduced
official structural-point monitor exactly matched
production ready
```

## Why Step109 Is Not First a Steady-Preflow Step

The public tutorial does run steady fluid flow before transient FSI. Step108 already showed that the low-Mach official-speed duct flow is stable and propagates through the duct: final duct-only inlet mean `ux = 0.0200000070`, mid-duct mean `ux = 0.0123139098`, and outlet mean `ux = 0.0124071455`. The current problem is not absence of flow; it is that the structural response remains roughly two to three orders of magnitude too small.

Step109 must answer four concrete questions:

1. Is `mb_force_cap_norm` clipping the reaction transfer too aggressively?
2. Is `mb_reaction_scale` the dominant amplitude knob?
3. Does the current MPM proxy stiffness/mass mapping make the flap too stiff or too heavy relative to the public 2D linear-elastic tutorial behavior?
4. Does the current `free_tip_proxy_mean` monitor significantly under-report a local/public-monitor-like displacement?

## Scope Boundary

Step109 is a diagnostic and sensitivity step.

Allowed:

- Add Step109 configs, tests, evidence modules, runners, docs, reports, logs, and artifacts.
- Reuse the Step108 official-speed low-Mach `FSIDriverConfig` setup.
- Run bounded matrix cases by changing config-level `mb_force_cap_norm`, `mb_reaction_scale`, and generated material-reference variants.
- Compute monitor variants from existing driver particle states and initial positions.
- Compute force/cap diagnostics from committed diagnostics rows.

Forbidden:

- Do not change LBM collision, tau convention, inlet/outlet formula, or moving bounce-back formula.
- Do not change moving-boundary reaction-transfer formula.
- Do not change MPM stress/update formula.
- Do not change `external/taichi_LBM3D/**`.
- Do not change `data/real_geometry_candidates/**`.
- Do not tune one parameter to match peak and then claim validation.

## Fixed Baseline

Every Step109 matrix case must inherit the Step108 official-speed low-Mach setup:

```text
n_grid = 48
n_particles = 1024
official_fsi_steps = 50
official_fsi_dt_s = 0.0005
lbm_substeps_per_fsi_step = 120
lbm_dt_phys_s = 4.166666666666667e-6
target_u_lbm = [0.02, 0.0, 0.0]
target_inlet_velocity_mps = 10.0
lbm_boundary_condition_mode = duct_velocity_inlet_pressure_outlet
wall_velocity_application_mode = disabled
fsi_exchange_mode = lbm_subcycled_per_fsi_step
```

The Step108 baseline reference values are:

```text
step108_peak_solver_m = 1.2332112646618043e-6
step108_normalized_rms_error = 0.616126763475836
step108_shape_correlation = 0.07866350821657236
step108_peak_reference_m = 0.000395
```

## Matrix 1: Reaction Cap / Scale

Add and run these config rows:

```text
configs/step109_response_matrix_base.json
configs/step109_response_matrix_cap_1e-4_scale_1.json
configs/step109_response_matrix_cap_1e-3_scale_1.json
configs/step109_response_matrix_cap_1e-2_scale_1.json
configs/step109_response_matrix_cap_1e-1_scale_1.json
configs/step109_response_matrix_cap_1e-2_scale_10.json
configs/step109_response_matrix_cap_1e-1_scale_10.json
```

Each successful row must record:

```text
row_name
matrix_family
mb_force_cap_norm
mb_reaction_scale
youngs_modulus
density
completed_official_fsi_steps
completed_lbm_substeps
flap_tip_timeseries_row_count
solver_curve_time_end_s
hydro_force_max_norm_max
max_grid_reaction_norm_max
active_reaction_particle_count_final
peak_solver_m
peak_reference_m
peak_ratio
normalized_rms_error
shape_correlation
peak_time_error_s
has_nan
has_inf
stable
validation_claim_allowed
direct_quantitative_equivalence_allowed
```

Hard acceptance for this matrix:

```text
response_matrix_row_count >= 6
successful_response_matrix_rows >= 5
every successful row has 51 solver samples from 0.0 to 0.025 s
all successful rows have finite error metrics
at least one successful row has peak_solver_m > Step108 peak_solver_m
at least one successful row has peak_solver_m > 1e-5 m
best_candidate_selected = true
best_candidate_validation_claim_allowed = false
best_candidate_direct_quantitative_equivalence_allowed = false
```

If no reaction cap/scale row increases displacement, the report must state that reaction cap/scale is not the dominant bottleneck under this matrix.

## Matrix 2: Structural Stiffness / Mass Sanity Sweep

The official public material reference remains silicone rubber with density `1600`, Young's modulus `1e6`, and Poisson ratio `0.47`. Step109 may run proxy sensitivity variants only; it must not claim these are official material replacements.

Add and run at least:

```text
configs/step109_response_matrix_E_1e5.json
configs/step109_response_matrix_E_1e4.json
```

Optionally include density variants if runtime remains reasonable:

```text
configs/step109_response_matrix_density_160.json
```

Purpose:

- If reducing proxy stiffness by `10x` or `100x` moves the peak toward the public reference, structural model/thickness/2D-3D proxy mapping is likely dominant.
- If stiffness/mass changes have small effect, force transfer or monitor definition is more likely dominant.

## Matrix 3: Monitor Definition Sensitivity

Step107 and Step108 use `free_tip_proxy_mean` and explicitly mark `monitor_equivalence = false`. Step109 must compute monitor variants from the same Step109 best candidate or baseline run:

```text
free_tip_proxy_mean
free_tip_proxy_max_total_displacement
nearest_public_monitor_point
top_5_nearest_public_monitor_mean
free_tip_x_displacement_mean
free_tip_y_displacement_mean
```

The public monitor proxy point must be mapped from the public tutorial coordinates:

```text
public_monitor_x_m = 0.0505
public_monitor_y_m = 0.0095
duct_length_m = 0.1
duct_height_m = 0.04
normalized_x = 0.505
normalized_y = duct_y_min + (0.0095 / 0.04) * (duct_y_max - duct_y_min)
normalized_z = duct z center
```

Required monitor outputs:

```text
outputs/step109_monitor_sensitivity/monitor_sensitivity_report.json
outputs/step109_monitor_sensitivity/monitor_sensitivity_report.csv
outputs/step109_monitor_sensitivity/monitor_timeseries_free_tip_proxy_mean.csv
outputs/step109_monitor_sensitivity/monitor_timeseries_free_tip_proxy_max_total_displacement.csv
outputs/step109_monitor_sensitivity/monitor_timeseries_nearest_public_monitor_point.csv
outputs/step109_monitor_sensitivity/monitor_timeseries_top_5_nearest_public_monitor_mean.csv
```

Hard acceptance:

```text
monitor_count >= 4
all monitor timeseries have 51 rows
all monitor timeseries end at 0.025 s
monitor_equivalence = false for all rows
all monitor metrics finite
```

If max/nearest monitor is more than `10x` the mean monitor, Step110 should prioritize a public structural-point proxy monitor. If all monitors remain near `1e-6 m`, the amplitude bottleneck is not mainly monitor averaging.

## Force / Cap Diagnostics

Step109 must produce:

```text
outputs/step109_diagnostics/force_cap_diagnostics_report.json
outputs/step109_diagnostics/force_cap_diagnostics_report.csv
outputs/step109_diagnostics/structural_sensitivity_report.json
outputs/step109_diagnostics/structural_sensitivity_report.csv
```

The force diagnostics report must summarize, per response-matrix row:

```text
mb_force_cap_norm
mb_reaction_scale
hydro_force_max_norm_max
max_grid_reaction_norm_max
max_grid_reaction_to_cap_ratio
active_reaction_particle_count_final
peak_solver_m
peak_ratio
stable
```

The structural report must summarize the stiffness/density sensitivity rows and whether a `10x` or `100x` stiffness change caused an order-of-magnitude displacement increase.

## Required Files

Goal, docs, report:

- `STEP109_FLUENT_DUCT_FLAP_FSI_RESPONSE_AMPLITUDE_SENSITIVITY_MATRIX_GOAL.md`
- `STEP109_FLUENT_DUCT_FLAP_FSI_RESPONSE_AMPLITUDE_SENSITIVITY_MATRIX_REPORT.md`
- `docs/109_fluent_duct_flap_fsi_response_amplitude_sensitivity_matrix.md`

Configs:

- `configs/step109_response_matrix_policy.json`
- `configs/step109_response_matrix_base.json`
- `configs/step109_response_matrix_cap_1e-4_scale_1.json`
- `configs/step109_response_matrix_cap_1e-3_scale_1.json`
- `configs/step109_response_matrix_cap_1e-2_scale_1.json`
- `configs/step109_response_matrix_cap_1e-1_scale_1.json`
- `configs/step109_response_matrix_cap_1e-2_scale_10.json`
- `configs/step109_response_matrix_cap_1e-1_scale_10.json`
- `configs/step109_response_matrix_E_1e5.json`
- `configs/step109_response_matrix_E_1e4.json`
- `configs/step109_monitor_sensitivity_policy.json`
- `configs/step109_output_guard_policy.json`
- `configs/step109_artifact_manifest_policy.json`

Source:

- `src/mpm_lbm/evidence/step109_common.py`
- `src/mpm_lbm/evidence/step109_response_sensitivity_matrix_runner.py`
- `src/mpm_lbm/evidence/step109_monitor_sensitivity.py`
- `src/mpm_lbm/evidence/step109_force_diagnostics.py`
- `src/mpm_lbm/evidence/step109_error_comparison.py`
- `src/mpm_lbm/evidence/step109_output_guard.py`

Baseline runners:

- `baseline_tests/run_step109_response_sensitivity_matrix.py`
- `baseline_tests/run_step109_monitor_sensitivity.py`
- `baseline_tests/run_step109_force_diagnostics.py`
- `baseline_tests/run_step109_output_guard.py`
- `baseline_tests/run_step109_artifact_manifest.py`

Tests:

- `tests/test_step109_response_sensitivity_matrix_contract.py`
- `tests/test_step109_monitor_sensitivity_contract.py`
- `tests/test_step109_output_guard_contract.py`

README must receive one concise Step109 bullet in the implemented-step list.

## Required Outputs

Response matrix:

- `outputs/step109_response_sensitivity_matrix/response_matrix_report.json`
- `outputs/step109_response_sensitivity_matrix/response_matrix_report.csv`
- `outputs/step109_response_sensitivity_matrix/response_matrix_summary.csv`
- `outputs/step109_response_sensitivity_matrix/best_candidate_error_report.json`
- `outputs/step109_response_sensitivity_matrix/best_candidate_flap_tip_displacement_timeseries.csv`

Monitor sensitivity:

- `outputs/step109_monitor_sensitivity/monitor_sensitivity_report.json`
- `outputs/step109_monitor_sensitivity/monitor_sensitivity_report.csv`
- `outputs/step109_monitor_sensitivity/monitor_sensitivity_summary.csv`
- `outputs/step109_monitor_sensitivity/monitor_timeseries_<monitor>.csv`

Diagnostics:

- `outputs/step109_diagnostics/force_cap_diagnostics_report.json`
- `outputs/step109_diagnostics/force_cap_diagnostics_report.csv`
- `outputs/step109_diagnostics/structural_sensitivity_report.json`
- `outputs/step109_diagnostics/structural_sensitivity_report.csv`

Guards:

- `outputs/step109_output_guard/output_guard_report.json`
- `outputs/step109_output_guard/output_guard_report.csv`
- `outputs/step109_artifact_manifest/artifact_manifest.json`
- `outputs/step109_artifact_manifest/artifact_manifest.csv`

Logs:

- `logs/step109_response_sensitivity_matrix.log`
- `logs/step109_monitor_sensitivity.log`
- `logs/step109_force_diagnostics.log`
- `logs/step109_output_guard.log`
- `logs/step109_artifact_manifest.log`

## RED/GREEN Workflow

RED first:

```text
test_step109_response_matrix_contains_required_cap_scale_rows
test_step109_response_matrix_runs_step108_baseline_and_at_least_five_variants
test_step109_reports_peak_ratio_and_error_metrics
test_step109_identifies_best_candidate_without_validation_claim
test_step109_monitor_sensitivity_reports_mean_max_nearest_monitors
test_step109_output_guard_blocks_official_payloads_and_validation_claims
```

Initial failure should be missing Step109 configs and artifacts.

GREEN:

```text
add Step109 explicit configs
add response matrix runner
add public-reference error wrapper reuse
add monitor sensitivity artifact builder
add force/cap diagnostics artifact builder
add output guard and artifact manifest
generate Step109 artifacts
```

REFACTOR:

```text
avoid duplicated error-metric logic
reuse Step107/Step108 public-reference harness behavior
keep all solver formula files unchanged
```

## Branch Interpretation Rules

The final report must classify the likely next Step110 direction:

### Branch A

If cap/scale increases peak to `1e-4 m` scale, Step110 should prioritize dimensional reaction-transfer calibration.

### Branch B

If stiffness reduction increases peak to `1e-4 m` scale while cap/scale does not, Step110 should prioritize structural model / equivalent stiffness / 2D-3D proxy mapping.

### Branch C

If max or nearest monitor is more than `10x` the mean monitor, Step110 should prioritize a public structural-point proxy monitor.

### Branch D

If all sweeps remain near `1e-6 m`, Step110 should prioritize surface/link-area reaction transfer repair rather than scalar cap/scale tuning.

## Required Verification Commands

Use the trusted interpreter first:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\evidence\step109_common.py `
  src\mpm_lbm\evidence\step109_response_sensitivity_matrix_runner.py `
  src\mpm_lbm\evidence\step109_monitor_sensitivity.py `
  src\mpm_lbm\evidence\step109_force_diagnostics.py `
  src\mpm_lbm\evidence\step109_error_comparison.py `
  src\mpm_lbm\evidence\step109_output_guard.py `
  baseline_tests\run_step109_response_sensitivity_matrix.py `
  baseline_tests\run_step109_monitor_sensitivity.py `
  baseline_tests\run_step109_force_diagnostics.py `
  baseline_tests\run_step109_output_guard.py `
  baseline_tests\run_step109_artifact_manifest.py `
  tests\test_step109_response_sensitivity_matrix_contract.py `
  tests\test_step109_monitor_sensitivity_contract.py `
  tests\test_step109_output_guard_contract.py

& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_response_sensitivity_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_monitor_sensitivity.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_force_diagnostics.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step109_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step109_response_sensitivity_matrix_contract.py `
  tests\test_step109_monitor_sensitivity_contract.py `
  tests\test_step109_output_guard_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -m pytest -q
pytest -q
git diff --check
```

## Completion Criteria

Step109 is complete only when:

```text
response_matrix_row_count >= 6
successful_response_matrix_rows >= 5
at least one successful row has peak_solver_m > Step108 peak_solver_m
at least one successful row has peak_solver_m > 1e-5 m
best_candidate_selected = true
monitor_sensitivity_report exists and passes
force_cap_diagnostics_report exists and passes
structural_sensitivity_report exists and passes
official case/mesh/journal/data/image count = 0
private Fluent CSV committed count = 0
validation_claim_allowed = false
direct_quantitative_equivalence_allowed = false
focused Step109 tests pass
full pytest passes with the trusted interpreter
Anaconda pytest and default pytest are attempted and reported honestly
git diff --check passes
```

When implementation and verification are complete, commit all relevant code, configs, docs, reports, logs, and generated artifacts, then push `main` to the configured GitHub remote. The final response must report the commit hash, remote branch, key artifacts, pass counts, and the Step110 branch recommendation.
