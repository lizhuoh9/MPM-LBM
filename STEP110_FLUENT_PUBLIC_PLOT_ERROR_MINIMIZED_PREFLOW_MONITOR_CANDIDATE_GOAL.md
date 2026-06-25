# Step110 Fluent Public-Plot Error-Minimized Candidate With Preflow and Monitor Alignment Goal

This goal starts from `origin/main` Step109 commit `b11f0cab00ead8c8a5e1cd103cf387db3d34fd31`. Step109 is accepted as a response-amplitude sensitivity matrix: it added a 9-row matrix, monitor sensitivity, force diagnostics, structural diagnostics, output guard, artifact manifest, docs, and tests without changing the underlying LBM, MPM, or coupling solver formulas.

Step109 showed that the moving-boundary force-cap envelope is a primary amplitude control parameter, but it did not identify `cap_1e-1_scale_10` as the next candidate solution. That row overshoots the Step107 public reference peak: `peak_solver_m = 0.0012614636`, `peak_reference_m = 0.000395`, `peak_ratio = 3.1936`, `peak_relative_error = 2.1936`, `normalized_rms_error = 1.2731`, and `shape_correlation = 0.0791`.

The closest Step109 candidate region is near `E_1e4` or `cap_1e-2`. The `E_1e4` row had `peak_solver_m = 0.0003403109`, `peak_ratio = 0.8615`, `peak_relative_error = 0.1385`, and `normalized_rms_error = 0.4604`, but its peak time remained late by `0.021 s` and its shape correlation remained only `0.0699`. Step110 must therefore move from peak-amplitude tuning to error minimization plus phase and curve-shape diagnosis.

## One-Sentence Goal

Introduce a proxy steady-preflow restart, add a Step110 public structural-point proxy monitor, score candidate runs against the Step107 public reference by composite error instead of maximum peak, and select the best bounded Step110 proxy candidate by normalized RMS, peak error, peak time, and shape correlation.

## Public Tutorial Scope

Use only public tutorial facts from the Ansys Fluent two-way FSI tutorial and already committed Step107 public-plot digitization:

- inlet speed: `10 m/s`
- official transient duration: `50` steps at `0.0005 s`, for `0.025 s`
- the tutorial initializes transient FSI after a steady fluid-flow simulation
- structural monitor name: `structural-point-flap`
- structural monitor point: `x = 0.0505 m`, `y = 0.0095 m`
- reported structural quantity: Total Displacement vertex average
- structural model: Linear Elasticity

Do not download, commit, or depend on official Fluent case, mesh, journal, data, private CSV, screenshots, or image payloads.

## Allowed Statement

The final Step110 report may claim only:

```text
A Step110 public-plot error-minimized proxy candidate was selected using proxy preflow, public structural-point monitor alignment, and Step107 public-reference error metrics.
```

## Forbidden Statements

The final Step110 report, docs, logs, configs, and artifacts must not claim:

```text
Fluent validation passed
Fluent equivalence achieved
official Fluent mesh/case/data reproduced
official steady-preflow exactly reproduced
official structural-point monitor exactly reproduced
production ready
```

## Why Step110 Is Needed

Step109 proved four things that define the Step110 scope:

1. Displacement amplitude can be pushed into the public Fluent plot range with `mb_force_cap_norm` and equivalent stiffness changes.
2. Selecting the largest peak is wrong because `cap_1e-1_scale_10` overshoots the public reference and has poor RMS and shape correlation.
3. Current solver curves still peak at the final time `0.025 s`, while the Step107 digitized public reference has early peak structure, including the first peak near `0.004 s`.
4. Monitor sensitivity changes values by a bounded amount but does not explain the full amplitude and phase mismatch.

Step110 must answer two concrete questions:

```text
1. phase/shape: why does the proxy solver peak at the end while the public reference peaks early?
2. candidate selection: which bounded candidate minimizes normalized RMS, peak error, peak time error, and shape mismatch?
```

## Scope Boundary

Step110 is an error-minimized proxy-candidate and evidence step.

Allowed:

- Add Step110 configs, evidence modules, runners, docs, reports, tests, logs, and artifacts.
- Add an LBM restart save/load helper for Step110 preflow artifacts.
- Add `FSIDriverConfig` fields for loading an LBM restart during initialization.
- Load a Step110 proxy preflow restart after LBM initialization when explicitly configured.
- Reuse Step107 public-reference error metrics and Step109 monitor/error evidence patterns.
- Generate bounded candidate rows around the Step109 useful region.
- Compute public structural-point proxy monitor variants from committed run data.
- Select the best candidate by composite error score.

Forbidden:

- Do not change LBM collision, tau convention, inlet/outlet formula, bounce-back, or moving-boundary formula.
- Do not change moving-boundary reaction-transfer formula.
- Do not change MPM stress/update formula.
- Do not change `external/taichi_LBM3D/**`.
- Do not change `data/real_geometry_candidates/**`.
- Do not claim official Fluent validation, official preflow reproduction, or official monitor equivalence.
- Do not select a candidate by maximum peak displacement.

## Fixed Baseline

Every Step110 runtime candidate must preserve the Step108/Step109 official-speed low-Mach structure:

```text
n_grid = 48
official_fsi_steps = 50
official_fsi_dt_s = 0.0005
lbm_substeps_per_fsi_step = 120
total_lbm_substeps = 6000
lbm_dt_phys_s = 4.166666666666667e-6
target_u_lbm = [0.02, 0.0, 0.0]
target_inlet_velocity_mps = 10.0
lbm_boundary_condition_mode = duct_velocity_inlet_pressure_outlet
wall_velocity_application_mode = disabled
fsi_exchange_mode = lbm_subcycled_per_fsi_step
```

The Step109 comparison anchors are:

```text
step109_E_1e4_normalized_rms_error = 0.460371
step109_E_1e4_peak_time_error_s = 0.021
step109_E_1e4_shape_correlation = 0.0699
step109_cap_1e-1_scale_10_normalized_rms_error = 1.2731
step109_cap_1e-1_scale_10_peak_relative_error = 2.1936
step107_public_reference_peak_m = 0.000395
```

## Work Package A: Proxy Steady-Preflow Restart

### Objective

Transient FSI should no longer start only from a quiescent LBM field. Step110 must create a proxy duct-only developed-flow restart that approximates the public tutorial's steady-fluid-flow-before-transient sequence while clearly marking it as a proxy, not an official Fluent steady solution.

### Required Configs

- `configs/step110_proxy_preflow_policy.json`
- `configs/step110_proxy_preflow_48_low_mach.json`

The 48 low-Mach config must include:

```json
{
  "n_grid": 48,
  "official_steps": 50,
  "lbm_substeps_per_fsi_step": 120,
  "total_lbm_substeps": 6000,
  "target_u_lbm": [0.02, 0.0, 0.0],
  "target_inlet_velocity_mps": 10.0,
  "lbm_dt_phys_s": 4.166666666666667e-6,
  "duct_static_geometry": "step104",
  "write_restart": true
}
```

### Required Outputs

- `outputs/step110_proxy_preflow/lbm_preflow_restart.npz`
- `outputs/step110_proxy_preflow/preflow_report.json`
- `outputs/step110_proxy_preflow/preflow_plane_timeseries.csv`
- `outputs/step110_proxy_preflow/restart_reload_report.json`

### Acceptance Criteria

```text
preflow_completed_lbm_substeps = 6000
inlet_plane_mean_ux_final in [0.019, 0.021]
mid_duct_plane_mean_ux_final > 0.005
outlet_plane_mean_ux_final > 0.005
rho_min > 0.95
rho_max < 1.10
has_nan = false
has_inf = false
restart_npz_exists = true
restart_reload_stats_match = true
validation_claim_allowed = false
```

## Work Package B: Driver LBM Restart Load

### Objective

Allow `FSIDriver3D` to load the Step110 proxy preflow field after LBM initialization when explicitly configured:

```text
lbm_restart_path = outputs/step110_proxy_preflow/lbm_preflow_restart.npz
```

### Allowed Source Changes

- `src/mpm_lbm/sim/lbm/restart.py`
- `src/mpm_lbm/sim/drivers/fsi_config.py`
- `src/mpm_lbm/sim/drivers/fsi_driver.py`

### Required Config Fields

```python
lbm_restart_path: Optional[str] = None
lbm_restart_required: bool = False
lbm_restart_scope: str = "rho_velocity_populations"
```

### Restart Contents

The first version must save and restore at least:

```text
rho
v
f
F
solid/static_solid geometry consistency metadata
n_grid
target_u_lbm
lbm_boundary_condition_mode
```

### Restart Guard

```text
restart_n_grid_matches = true
restart_lbm_boundary_condition_mode_matches = true
restart_target_u_lbm_matches = true
restart_loaded = true
```

If `lbm_restart_required = true` and the restart is missing, incompatible, or fails to load, initialization must fail fast with a clear error.

## Work Package C: Public Structural-Point Proxy Monitor Alignment

### Objective

Do not use only `free_tip_proxy_mean` for error comparison. Add public monitor proxy variants based on the public structural point `x = 0.0505 m`, `y = 0.0095 m`, with `monitor_equivalence = false`.

### Required Config

- `configs/step110_monitor_alignment_policy.json`

Required values:

```json
{
  "public_monitor_x_m": 0.0505,
  "public_monitor_y_m": 0.0095,
  "duct_length_m": 0.1,
  "duct_height_m": 0.04,
  "normalized_monitor_point": [0.505, 0.395, 0.5],
  "monitor_equivalence": false,
  "required_monitor_names": [
    "free_tip_proxy_mean",
    "nearest_public_monitor_point",
    "top_5_nearest_public_monitor_mean",
    "radius_public_monitor_mean"
  ]
}
```

### Required Outputs

- `outputs/step110_monitor_alignment/monitor_definition_report.json`
- `outputs/step110_monitor_alignment/monitor_timeseries_nearest_public_monitor_point.csv`
- `outputs/step110_monitor_alignment/monitor_timeseries_top_5_nearest_public_monitor_mean.csv`
- `outputs/step110_monitor_alignment/monitor_timeseries_radius_public_monitor_mean.csv`

## Work Package D: Error-Minimized Candidate Matrix

### Objective

Step110 must not select the largest peak. It must select the lowest composite error score.

Required score:

```text
score =
  0.45 * normalized_rms_error
+ 0.25 * abs(log(peak_solver / peak_reference))
+ 0.20 * normalized_peak_time_error
+ 0.10 * (1 - max(shape_correlation, 0))
```

If a non-log implementation is used for the first version, it must still include:

```text
normalized_rms_error
peak_relative_error
peak_time_error_s
shape_correlation
```

### Candidate Rows

Keep the matrix bounded around Step109's useful region and run no more than 12 rows:

```text
cap_3e-2_E_1e6
cap_5e-2_E_1e6
cap_7e-2_E_1e6
cap_1e-2_E_5e4
cap_1e-2_E_2e4
cap_1e-2_E_1e4
cap_2e-2_E_5e4
cap_2e-2_E_2e4
cap_3e-2_E_5e4
cap_3e-2_E_2e4
replay_E_1e4
replay_cap_1e-2
```

Each candidate must run or replay a Step110-compatible evidence row with:

```text
50 official FSI steps
6000 LBM substeps
preflow restart loaded
monitor variants captured
Step107 public reference error comparison
```

### Required Outputs

- `outputs/step110_error_minimized_candidate_matrix/candidate_matrix_report.json`
- `outputs/step110_error_minimized_candidate_matrix/candidate_matrix_report.csv`
- `outputs/step110_error_minimized_candidate_matrix/best_candidate_error_report.json`
- `outputs/step110_error_minimized_candidate_matrix/best_candidate_monitor_timeseries.csv`

### Candidate Hard Rules

```text
stable = true
has_nan = false
has_inf = false
sample_count = 51
solver_curve_time_end_s = 0.025
validation_claim_allowed = false
direct_quantitative_equivalence_allowed = false
```

Candidate ordering:

```text
primary: lowest composite score
secondary: normalized_rms_error
tertiary: peak_time_error_s
```

### Minimum Step110 Success Threshold

```text
candidate_matrix_row_count >= 8
successful_candidate_rows >= 6
best_candidate_selected = true
best_candidate_normalized_rms_error < 0.460371
best_candidate_peak_time_error_s < 0.021
best_candidate_peak_relative_error < 0.5
best_candidate_shape_correlation > 0.10
```

These thresholds are the minimum evidence for moving toward controllable public-plot error. They are not validation thresholds.

## Work Package E: Curve Shape Diagnostics

Each candidate must report:

```text
first_peak_time_s
first_peak_m
final_displacement_m
monotonic_increasing_fraction
reference_peak_time_s
solver_peak_time_s
peak_time_error_s
early_window_rms_error_0_to_0p008
mid_window_rms_error_0p008_to_0p017
late_window_rms_error_0p017_to_0p025
```

Step109's largest remaining issue is that solver curves continue increasing to `0.025 s` while the public reference has peak structure near `0.004 s`, `0.013 s`, and `0.022 s`. Step110 must identify whether error is dominated by early, mid, or late time windows.

### Required Outputs

- `outputs/step110_curve_shape_diagnostics/curve_shape_diagnostics_report.json`
- `outputs/step110_curve_shape_diagnostics/curve_shape_diagnostics_report.csv`

## Required Files

Goal, docs, report:

- `STEP110_FLUENT_PUBLIC_PLOT_ERROR_MINIMIZED_PREFLOW_MONITOR_CANDIDATE_GOAL.md`
- `STEP110_FLUENT_PUBLIC_PLOT_ERROR_MINIMIZED_PREFLOW_MONITOR_CANDIDATE_REPORT.md`
- `docs/110_fluent_public_plot_error_minimized_preflow_monitor_candidate.md`

Configs:

- `configs/step110_proxy_preflow_policy.json`
- `configs/step110_proxy_preflow_48_low_mach.json`
- `configs/step110_monitor_alignment_policy.json`
- `configs/step110_candidate_matrix_policy.json`
- `configs/step110_output_guard_policy.json`
- `configs/step110_artifact_manifest_policy.json`
- `configs/step110_candidates/cap_3e-2_E_1e6.json`
- `configs/step110_candidates/cap_5e-2_E_1e6.json`
- `configs/step110_candidates/cap_7e-2_E_1e6.json`
- `configs/step110_candidates/cap_1e-2_E_5e4.json`
- `configs/step110_candidates/cap_1e-2_E_2e4.json`
- `configs/step110_candidates/cap_1e-2_E_1e4.json`
- `configs/step110_candidates/cap_2e-2_E_5e4.json`
- `configs/step110_candidates/cap_2e-2_E_2e4.json`
- `configs/step110_candidates/cap_3e-2_E_5e4.json`
- `configs/step110_candidates/cap_3e-2_E_2e4.json`
- `configs/step110_candidates/replay_E_1e4.json`
- `configs/step110_candidates/replay_cap_1e-2.json`

Source:

- `src/mpm_lbm/sim/lbm/restart.py`
- `src/mpm_lbm/evidence/step110_common.py`
- `src/mpm_lbm/evidence/step110_proxy_preflow_runner.py`
- `src/mpm_lbm/evidence/step110_monitor_alignment.py`
- `src/mpm_lbm/evidence/step110_candidate_matrix_runner.py`
- `src/mpm_lbm/evidence/step110_curve_shape_diagnostics.py`
- `src/mpm_lbm/evidence/step110_error_scoring.py`
- `src/mpm_lbm/evidence/step110_output_guard.py`

Baseline runners:

- `baseline_tests/run_step110_proxy_preflow.py`
- `baseline_tests/run_step110_monitor_alignment.py`
- `baseline_tests/run_step110_candidate_matrix.py`
- `baseline_tests/run_step110_curve_shape_diagnostics.py`
- `baseline_tests/run_step110_output_guard.py`
- `baseline_tests/run_step110_artifact_manifest.py`

Tests:

- `tests/test_step110_proxy_preflow_contract.py`
- `tests/test_step110_monitor_alignment_contract.py`
- `tests/test_step110_candidate_matrix_contract.py`
- `tests/test_step110_curve_shape_diagnostics_contract.py`
- `tests/test_step110_output_guard_contract.py`

README must receive one concise Step110 bullet in the implemented-step list.

## Required Outputs

- `outputs/step110_proxy_preflow/lbm_preflow_restart.npz`
- `outputs/step110_proxy_preflow/preflow_report.json`
- `outputs/step110_proxy_preflow/preflow_plane_timeseries.csv`
- `outputs/step110_proxy_preflow/restart_reload_report.json`
- `outputs/step110_monitor_alignment/monitor_definition_report.json`
- `outputs/step110_monitor_alignment/monitor_timeseries_nearest_public_monitor_point.csv`
- `outputs/step110_monitor_alignment/monitor_timeseries_top_5_nearest_public_monitor_mean.csv`
- `outputs/step110_monitor_alignment/monitor_timeseries_radius_public_monitor_mean.csv`
- `outputs/step110_error_minimized_candidate_matrix/candidate_matrix_report.json`
- `outputs/step110_error_minimized_candidate_matrix/candidate_matrix_report.csv`
- `outputs/step110_error_minimized_candidate_matrix/best_candidate_error_report.json`
- `outputs/step110_error_minimized_candidate_matrix/best_candidate_monitor_timeseries.csv`
- `outputs/step110_curve_shape_diagnostics/curve_shape_diagnostics_report.json`
- `outputs/step110_curve_shape_diagnostics/curve_shape_diagnostics_report.csv`
- `outputs/step110_output_guard/output_guard_report.json`
- `outputs/step110_output_guard/output_guard_report.csv`
- `outputs/step110_artifact_manifest/artifact_manifest.json`
- `outputs/step110_artifact_manifest/artifact_manifest.csv`

## RED/GREEN Workflow

RED first:

```text
test_step110_preflow_restart_exists_and_reloads
test_step110_driver_can_load_lbm_restart
test_step110_monitor_alignment_uses_public_structural_point_proxy
test_step110_candidate_matrix_scores_by_error_not_peak
test_step110_best_candidate_improves_rms_peak_time_and_correlation
test_step110_curve_shape_diagnostics_reports_windows
test_step110_output_guard_blocks_official_payloads_and_validation_claims
```

Expected initial failures:

```text
missing restart module
missing preflow restart
missing monitor alignment report
missing candidate scoring report
missing best candidate
missing curve-shape diagnostics
```

GREEN:

```text
add restart save/load helper
add driver restart config/load guard
add Step110 explicit configs
add proxy preflow runner
add monitor alignment artifact builder
add candidate matrix runner and composite scoring
add curve-shape diagnostics
add output guard and artifact manifest
generate Step110 artifacts
```

REFACTOR:

```text
reuse Step109 monitor helpers where practical
reuse Step107 public-reference error metrics
avoid duplicating generic JSON/CSV helpers
keep all solver formula files unchanged
```

## Required Verification Commands

Use the trusted interpreter first:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\lbm\restart.py `
  src\mpm_lbm\sim\drivers\fsi_config.py `
  src\mpm_lbm\sim\drivers\fsi_driver.py `
  src\mpm_lbm\evidence\step110_common.py `
  src\mpm_lbm\evidence\step110_proxy_preflow_runner.py `
  src\mpm_lbm\evidence\step110_monitor_alignment.py `
  src\mpm_lbm\evidence\step110_candidate_matrix_runner.py `
  src\mpm_lbm\evidence\step110_curve_shape_diagnostics.py `
  src\mpm_lbm\evidence\step110_error_scoring.py `
  src\mpm_lbm\evidence\step110_output_guard.py

& 'D:\working\taichi\env\python.exe' baseline_tests\run_step110_proxy_preflow.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step110_monitor_alignment.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step110_candidate_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step110_curve_shape_diagnostics.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step110_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step110_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step110_proxy_preflow_contract.py `
  tests\test_step110_monitor_alignment_contract.py `
  tests\test_step110_candidate_matrix_contract.py `
  tests\test_step110_curve_shape_diagnostics_contract.py `
  tests\test_step110_output_guard_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -m pytest -q
pytest -q
git diff --check
```

## Completion Criteria

Step110 is complete only when:

```text
preflow_completed_lbm_substeps = 6000
restart_npz_exists = true
restart_reload_stats_match = true
driver_restart_guard_pass = true
monitor_definition_report exists and passes
candidate_matrix_row_count >= 8
successful_candidate_rows >= 6
best_candidate_selected = true
best_candidate_normalized_rms_error < 0.460371
best_candidate_peak_time_error_s < 0.021
best_candidate_peak_relative_error < 0.5
best_candidate_shape_correlation > 0.10
curve_shape_diagnostics_report exists and passes
official case/mesh/journal/data/image count = 0
private Fluent CSV committed count = 0
validation_claim_allowed = false
direct_quantitative_equivalence_allowed = false
focused Step110 tests pass
full pytest passes with the trusted interpreter
Anaconda pytest and default pytest are attempted and reported honestly
git diff --check passes
```

## Step111 Decision Rule

Step110 may recommend proceeding to Step111 only if:

```text
best_candidate_normalized_rms_error < 0.35
best_candidate_peak_relative_error < 0.35
best_candidate_peak_time_error_s < 0.010
best_candidate_shape_correlation > 0.20
best candidate stable
no NaN/Inf
official payload count = 0
validation_claim_allowed = false
```

If Step110 cannot meet these Step111-entry thresholds but amplitude is controlled, the next step should not be a larger run. It should branch toward structural dynamics repair, such as a small-strain linear elastic structural path, restoring-force/damping correction, or surface/link-area reaction transfer replacement.

When implementation and verification are complete, commit all relevant code, configs, docs, reports, logs, and generated artifacts, then push `main` to the configured GitHub remote. The final response must report the commit hash, remote branch, key pass counts, and the artifact-manifest summary.
