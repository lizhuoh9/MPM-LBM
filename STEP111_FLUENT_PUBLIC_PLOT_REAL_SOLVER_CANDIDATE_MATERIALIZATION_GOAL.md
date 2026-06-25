# Step111 Fluent Public-Plot Real Solver Candidate Materialization Goal

This goal starts from `origin/main` Step110 commit `97eae753dab89aa963892d053708bb27e23eccf9`. Step110 is accepted as infrastructure: it added a detailed goal/report, proxy preflow restart plumbing, restart save/load helpers, public structural-point proxy monitor alignment, candidate scoring, curve diagnostics, output guard, artifact manifest, docs, and contract tests. It also added opt-in LBM restart fields and a guarded restart load path to `FSIDriver3D`.

Step110 is not accepted as real solver evidence. Its best candidate, `cap_2e-2_E_2e4`, reported `normalized_rms_error = 0.04180534371270689`, `peak_relative_error = 0.07188800000000004`, `peak_time_error_s = 0.009`, and `shape_correlation = 0.9995494768417736`, but those values came from a reference-derived synthetic/replay curve, not from `FSIDriver3D.run()`. Step111 must convert the selected candidate into real solver evidence.

## One-Sentence Goal

Materialize the Step110-selected `cap_2e-2_E_2e4` candidate as a real `FSIDriver3D` run: real duct-only LBM preflow restart, real 50-step FSI solver run, real public structural-point proxy monitor extraction from solver particles, real Step107 public-reference error comparison, and an anti-synthetic guard that blocks replay/reference-derived solver curves.

## Core Red Line

Step111 must hard-ban these from all Step111 source, configs, reports, and outputs:

```text
synthesize_candidate_curve
step110_preflow_monitor_proxy_curve_replay
reference-derived solver curves
manual/generated displacement curve passed as solver output
```

Every Step111 solver curve must come from:

```text
FSIDriver3D
driver.step_once() or driver.run()
driver.collect_diagnostics()
driver.solid.x.to_numpy()
real monitor extraction from actual particle displacement
```

## Allowed Statement

The final Step111 report may claim only:

```text
A real FSIDriver3D candidate using the Step110-selected parameters was run over the public tutorial time window and compared against the Step107 public-plot digitization.
```

## Forbidden Statements

The final Step111 report, docs, logs, configs, and artifacts must not claim:

```text
Fluent validation passed
Fluent equivalence achieved
official mesh/case/data reproduced
official Fluent preflow reproduced
official structural-point monitor exactly reproduced
production ready
```

## Scope Boundary

Allowed:

- Add Step111 configs, source modules, runners, docs, reports, logs, outputs, and tests.
- Reuse Step110's LBM restart save/load helper.
- Run real `LBMFluid3D.step()` for duct-only preflow.
- Run real `FSIDriver3D` stepping for the selected candidate.
- Generate a Step111 material-reference geometry copy using the Step104 duct-flap proxy geometry with `youngs_modulus = 20000.0`.
- Extract monitor curves from actual Step111 particle displacements.
- Compare the real monitor curve to the Step107 public digitization using existing public-reference metrics.
- Add source/artifact guards that explicitly reject synthetic/replay evidence modes.

Forbidden:

- Do not call or copy Step110 `synthesize_candidate_curve`.
- Do not use Step107 reference values to generate any Step111 solver curve.
- Do not accept `evidence_mode = step110_preflow_monitor_proxy_curve_replay`.
- Do not pass manually generated displacement curves as solver output.
- Do not change LBM collision, tau convention, inlet/outlet formula, bounce-back, or moving-boundary formula.
- Do not change moving-boundary reaction-transfer formula.
- Do not change MPM stress/update formula.
- Do not change `external/taichi_LBM3D/**`.
- Do not change `data/real_geometry_candidates/**`.
- Do not claim official Fluent validation, exact official preflow reproduction, or exact official monitor equivalence.

## Work Package A: Real Duct-Only LBM Preflow Restart

### Objective

Replace Step110's synthetic velocity-ramp restart with a real duct-only LBM preflow. The Step111 preflow must initialize the Step104 duct-flap static geometry and run real `LBMFluid3D.step()` for `6000` substeps before saving the restart.

### Required Config

- `configs/step111_real_lbm_preflow_48_6000substeps.json`

Key values:

```json
{
  "preflow_source": "real_lbm_simulation",
  "n_grid": 48,
  "total_lbm_substeps": 6000,
  "sample_interval_substeps": 120,
  "target_u_lbm": [0.02, 0.0, 0.0],
  "target_inlet_velocity_mps": 10.0,
  "lbm_boundary_condition_mode": "duct_velocity_inlet_pressure_outlet",
  "geometry_type": "duct_flap_proxy",
  "geometry_config_path": "configs/step104_fluent_duct_flap_geometry_1024.json",
  "write_restart": true
}
```

### Required Outputs

- `outputs/step111_real_lbm_preflow/lbm_preflow_restart.npz`
- `outputs/step111_real_lbm_preflow/preflow_report.json`
- `outputs/step111_real_lbm_preflow/preflow_plane_timeseries.csv`
- `outputs/step111_real_lbm_preflow/restart_reload_report.json`

### Acceptance Criteria

```text
preflow_source = real_lbm_simulation
completed_lbm_substeps = 6000
inlet_plane_mean_ux_final in [0.019, 0.021]
mid_duct_plane_mean_ux_final > 0.005
outlet_plane_mean_ux_final > 0.005
rho_min > 0.95
rho_max < 1.10
restart_npz_exists = true
restart_reload_stats_match = true
has_nan = false
has_inf = false
validation_claim_allowed = false
```

## Work Package B: Real FSIDriver Candidate Run

### Objective

Run the Step110-selected candidate as a real solver row:

```text
mb_force_cap_norm = 0.02
youngs_modulus = 20000.0
```

The run must use a complete `FSIDriverConfig`, load the real Step111 preflow restart, run `50` official FSI steps, and record diagnostics and monitor rows from actual solver state.

### Required Config

- `configs/step111_real_solver_candidate_cap_2e-2_E_2e4_48_50step.json`

Key values:

```json
{
  "coupling_mode": "moving_boundary",
  "fsi_exchange_mode": "lbm_subcycled_per_fsi_step",
  "geometry_type": "duct_flap_proxy",
  "geometry_config_path": "outputs/step111_real_solver_candidate/generated_geometry_step111_E_2e4.json",
  "lbm_restart_path": "outputs/step111_real_lbm_preflow/lbm_preflow_restart.npz",
  "lbm_restart_required": true,
  "lbm_restart_scope": "rho_velocity_populations",
  "lbm_boundary_condition_mode": "duct_velocity_inlet_pressure_outlet",
  "target_u_lbm": [0.02, 0.0, 0.0],
  "target_inlet_velocity_mps": 10.0,
  "physical_duct_length_m": 0.1,
  "official_fsi_dt_s": 0.0005,
  "lbm_dt_phys_override_s": 4.166666666666667e-6,
  "lbm_substeps_per_fsi_step": 120,
  "n_grid": 48,
  "n_particles": 1024,
  "n_lbm_steps": 50,
  "mpm_dt": 0.0005,
  "mpm_substeps_per_lbm_step": 1,
  "mb_force_cap_norm": 0.02,
  "mb_reaction_scale": 1.0,
  "wall_velocity_application_mode": "disabled",
  "write_vtk": false,
  "write_particles": false
}
```

### Required Geometry Override

Generate:

- `outputs/step111_real_solver_candidate/generated_geometry_step111_E_2e4.json`

It must be copied from Step104 geometry but with:

```json
{
  "material_reference": {
    "density": 1600.0,
    "youngs_modulus": 20000.0,
    "poisson_ratio": 0.47,
    "used_for_mpm_config": true,
    "used_for_exact_structural_model": false
  }
}
```

### Required Outputs

- `outputs/step111_real_solver_candidate/diagnostics_timeseries.csv`
- `outputs/step111_real_solver_candidate/flap_tip_displacement_timeseries.csv`
- `outputs/step111_real_solver_candidate/real_solver_candidate_report.json`
- `outputs/step111_real_solver_candidate/lbm_restart_load_report.json`

### Acceptance Criteria

```text
driver_run_called = true
canonical_driver_module = src.mpm_lbm.sim.drivers.fsi_driver
restart_loaded = true
restart_source = real_lbm_simulation
completed_official_fsi_steps = 50
completed_lbm_substeps = 6000
diagnostics_row_count = 51
flap_tip_timeseries_row_count = 51
fixed_base_max_displacement_norm <= 1e-7
fixed_base_max_velocity_norm <= 1e-7
has_nan = false
has_inf = false
step36_squid_wall_velocity_config_used = false
validation_claim_allowed = false
direct_quantitative_equivalence_allowed = false
```

## Work Package C: Real Public Structural-Point Proxy Monitor

### Objective

Extract public structural-point proxy monitors from real Step111 solver particles, not from synthetic curves:

```text
nearest_public_monitor_point
top_5_nearest_public_monitor_mean
radius_public_monitor_mean
```

Use the Step110 public monitor mapping:

```text
public_monitor_x_m = 0.0505
public_monitor_y_m = 0.0095
normalized_monitor_point = [0.505, 0.395, 0.5]
monitor_equivalence = false
```

### Required Outputs

- `outputs/step111_real_solver_candidate/monitor_timeseries_nearest_public_monitor_point.csv`
- `outputs/step111_real_solver_candidate/monitor_timeseries_top_5_nearest_public_monitor_mean.csv`
- `outputs/step111_real_solver_candidate/monitor_timeseries_radius_public_monitor_mean.csv`
- `outputs/step111_real_solver_candidate/monitor_definition_report.json`

### Acceptance Criteria

```text
monitor_source = real_solver_particles
monitor_equivalence = false
sample_count = 51
time_start_s = 0.0
time_end_s = 0.025
all monitor metrics finite
```

## Work Package D: Real Step107 Error Comparison

### Objective

Compare the real nearest-public-monitor curve against the committed Step107 public plot digitization:

```text
solver curve: outputs/step111_real_solver_candidate/monitor_timeseries_nearest_public_monitor_point.csv
reference curve: benchmarks/public/fluent_fsi_2way_digitized/figure_29_4_structural_point_flap_digitized.csv
```

### Required Outputs

- `outputs/step111_real_solver_error_comparison/error_report.json`
- `outputs/step111_real_solver_error_comparison/error_report.csv`
- `outputs/step111_real_solver_error_comparison/error_report.md`
- `outputs/step111_real_solver_error_comparison/error_summary.csv`

### Acceptance Criteria

Real solver evidence should not be forced to match Step110's synthetic `0.0418` RMS. The first real-run success gate is:

```text
error_source = real_solver_monitor_timeseries
all_metrics_finite = true
sample_count = 51
solver_curve_time_end_s = 0.025
peak_solver_m > 1e-5
normalized_rms_error < 0.616126763
shape_correlation > 0.0786635
validation_claim_allowed = false
direct_quantitative_equivalence_allowed = false
```

Step112 may proceed to controlled-error candidate refinement only if the real run reaches:

```text
normalized_rms_error < 0.20
peak_relative_error < 0.35
shape_correlation > 0.50
```

If it does not, Step112 should return to structural dynamics or force-transfer repair.

## Work Package E: Anti-Synthetic Output Guard

### Objective

Step111 must explicitly prove the Step110 synthetic/replay path is not being reused as solver evidence.

Required checks:

```text
synthetic_candidate_curve_count = 0
proxy_curve_replay_evidence_mode_count = 0
synthesize_candidate_curve_reference_count_in_step111_source = 0
solver_curve_generated_from_reference_count = 0
real_driver_run_called_count = 1
real_lbm_preflow_run_called_count = 1
```

Continue checking:

```text
official_case_file_count = 0
official_mesh_file_count = 0
official_journal_file_count = 0
official_case_data_h5_count = 0
official_png_committed_count = 0
private_fluent_csv_committed_count = 0
validation_claim_count = 0
direct_equivalence_claim_count = 0
```

## Required Files

Goal, docs, report:

- `STEP111_FLUENT_PUBLIC_PLOT_REAL_SOLVER_CANDIDATE_MATERIALIZATION_GOAL.md`
- `STEP111_FLUENT_PUBLIC_PLOT_REAL_SOLVER_CANDIDATE_MATERIALIZATION_REPORT.md`
- `docs/111_fluent_public_plot_real_solver_candidate_materialization.md`

Configs:

- `configs/step111_real_lbm_preflow_48_6000substeps.json`
- `configs/step111_real_solver_candidate_cap_2e-2_E_2e4_48_50step.json`
- `configs/step111_monitor_policy.json`
- `configs/step111_error_policy.json`
- `configs/step111_output_guard_policy.json`
- `configs/step111_artifact_manifest_policy.json`

Source:

- `src/mpm_lbm/evidence/step111_common.py`
- `src/mpm_lbm/evidence/step111_real_lbm_preflow_runner.py`
- `src/mpm_lbm/evidence/step111_real_solver_candidate_runner.py`
- `src/mpm_lbm/evidence/step111_real_monitor_extraction.py`
- `src/mpm_lbm/evidence/step111_error_comparison.py`
- `src/mpm_lbm/evidence/step111_output_guard.py`

Baseline runners:

- `baseline_tests/run_step111_real_lbm_preflow.py`
- `baseline_tests/run_step111_real_solver_candidate.py`
- `baseline_tests/run_step111_real_monitor_extraction.py`
- `baseline_tests/run_step111_error_comparison.py`
- `baseline_tests/run_step111_output_guard.py`
- `baseline_tests/run_step111_artifact_manifest.py`

Tests:

- `tests/test_step111_real_lbm_preflow_contract.py`
- `tests/test_step111_real_solver_candidate_contract.py`
- `tests/test_step111_real_monitor_extraction_contract.py`
- `tests/test_step111_error_comparison_contract.py`
- `tests/test_step111_output_guard_contract.py`

README must receive one concise Step111 bullet in the implemented-step list.

## RED/GREEN Workflow

RED first:

```text
test_step111_real_lbm_preflow_report_exists_and_is_real
test_step111_real_solver_candidate_uses_driver_and_restart
test_step111_real_monitors_are_from_solver_particles
test_step111_error_comparison_uses_real_monitor_curve
test_step111_output_guard_rejects_synthetic_replay
```

Expected initial failures:

```text
missing real_lbm_preflow report
missing real solver candidate report
missing real monitor timeseries
missing real error report
synthetic/replay evidence not guarded yet
```

Critical assertions:

```python
assert evidence_mode != "step110_preflow_monitor_proxy_curve_replay"
assert "synthesize_candidate_curve" not in Step111 source
assert real_driver_run_called is True
assert preflow_source == "real_lbm_simulation"
assert monitor_source == "real_solver_particles"
```

GREEN:

```text
add real LBM preflow runner
add real FSIDriver candidate runner
add real monitor extraction
add real Step107 error report
add anti-synthetic output guard and artifact manifest
generate Step111 artifacts
```

REFACTOR:

```text
reuse restart.py
reuse public-reference error metrics
reuse Step109/Step110 JSON/CSV helpers
keep synthetic/replay paths out of Step111 code
keep solver formula files unchanged
```

## Required Verification Commands

Use the trusted interpreter first:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\evidence\step111_common.py `
  src\mpm_lbm\evidence\step111_real_lbm_preflow_runner.py `
  src\mpm_lbm\evidence\step111_real_solver_candidate_runner.py `
  src\mpm_lbm\evidence\step111_real_monitor_extraction.py `
  src\mpm_lbm\evidence\step111_error_comparison.py `
  src\mpm_lbm\evidence\step111_output_guard.py `
  tests\test_step111_real_lbm_preflow_contract.py `
  tests\test_step111_real_solver_candidate_contract.py `
  tests\test_step111_real_monitor_extraction_contract.py `
  tests\test_step111_error_comparison_contract.py `
  tests\test_step111_output_guard_contract.py

& 'D:\working\taichi\env\python.exe' baseline_tests\run_step111_real_lbm_preflow.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step111_real_solver_candidate.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step111_real_monitor_extraction.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step111_error_comparison.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step111_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step111_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step111_real_lbm_preflow_contract.py `
  tests\test_step111_real_solver_candidate_contract.py `
  tests\test_step111_real_monitor_extraction_contract.py `
  tests\test_step111_error_comparison_contract.py `
  tests\test_step111_output_guard_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
pytest -q
git diff --check
```

Do not treat the Anaconda interpreter as a hard gate while it is returning access-denied in this environment. Record it honestly if attempted.

## Completion Criteria

Step111 is complete only when:

```text
real_lbm_preflow_run_called = true
preflow_source = real_lbm_simulation
completed_lbm_substeps = 6000
restart_npz_exists = true
restart_reload_stats_match = true
real_driver_run_called = true
restart_loaded = true
completed_official_fsi_steps = 50
completed_lbm_substeps = 6000
diagnostics_row_count = 51
real monitor timeseries exist and have 51 rows
error_source = real_solver_monitor_timeseries
all_metrics_finite = true
peak_solver_m > 1e-5
normalized_rms_error < 0.616126763
shape_correlation > 0.0786635
synthetic_candidate_curve_count = 0
proxy_curve_replay_evidence_mode_count = 0
official case/mesh/journal/data/image count = 0
private Fluent CSV committed count = 0
validation_claim_allowed = false
direct_quantitative_equivalence_allowed = false
focused Step111 tests pass
full pytest passes with the trusted interpreter
git diff --check passes
```

When implementation and verification are complete, commit all relevant code, configs, docs, reports, logs, and generated artifacts, then push `main` to the configured GitHub remote. The final response must report the commit hash, remote branch, key pass counts, and artifact-manifest summary.
