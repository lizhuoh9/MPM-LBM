# Step112 Fluent Public-Plot Real Solver Dynamics Repair Matrix Goal

## Source Review

This goal is based on the review of `origin/main` Step111 commit `48ec2e2`.
Step111 correctly replaced Step110 replay/synthetic scoring with a real LBM preflow restart, a real
`FSIDriver3D` candidate run, real particle monitor extraction, a real Step107 public-plot comparison,
and an anti-synthetic output guard.

Step111 also correctly recorded failure:

- `error_source=real_solver_monitor_timeseries`
- `peak_solver_m=0.0007980134848`
- `peak_reference_m=0.000395`
- `normalized_rms_error=0.7131889377`
- `shape_correlation=0.0704327582`
- `time_of_peak_solver_s=0.025`
- `time_of_peak_reference_s=0.004`
- `step111_error_comparison_pass=false`

The Step111 real curve is almost monotonic through the public tutorial window. It has adequate or excessive
amplitude, but wrong timing and wrong shape. The next step must repair and diagnose real solver dynamics,
not repackage candidates or generate reference-derived curves.

## Objective

Implement Step112 as a bounded real-solver dynamics repair matrix:

> Use real `FSIDriver3D` runs to diagnose and repair the Step111 real dynamics failure: late monotonic
> growth, peak-time mismatch, possible out-of-plane monitor contamination, and excessive final displacement.
> Produce a real solver candidate matrix over cap/E/planar-lock/damping controls, score only real solver
> particle curves against the Step107 public-plot digitization, and report honestly whether the best real
> candidate beats Step111 and Step108.

## Allowed Claim

Only this class of claim is allowed:

```text
A real-solver dynamics repair matrix was run, and the best real FSIDriver3D candidate improved public-plot comparison metrics without synthetic/replay curves.
```

If the best candidate does not pass the hard gate, the report must say so directly.

## Forbidden Claims

Do not claim any of the following:

```text
Fluent validation passed
Fluent equivalence achieved
official Fluent mesh/case/data reproduced
official dynamic mesh reproduced
official structural-point monitor exactly reproduced
production ready
```

## Core Red Lines

Every Step112 candidate curve must come from the real solver path:

```text
FSIDriver3D.initialize()
FSIDriver3D.step_once()
real LBM restart
real MPM particle displacement
real monitor extraction
```

Hard forbidden:

```text
synthesize_candidate_curve
reference-derived solver curves
proxy_curve_replay evidence mode
manual displacement curve injection
```

The Step107 public reference may be used only for error metrics, not to generate or shape any solver curve.

## Work Package A: Real Dynamics Diagnostics

Before changing solver behavior, add diagnostics that decompose Step111 failure into measurable components.

Required outputs:

```text
outputs/step112_real_dynamics_diagnostics/component_monitor_report.json
outputs/step112_real_dynamics_diagnostics/force_displacement_phase_report.json
outputs/step112_real_dynamics_diagnostics/structural_state_report.json
```

Required fields:

```text
diagnostics_source
nearest_monitor_peak_total_m
nearest_monitor_peak_x_m
nearest_monitor_peak_y_m
nearest_monitor_peak_z_m
z_to_total_peak_ratio
y_to_total_peak_ratio
final_total_m
final_x_m
final_y_m
final_z_m
time_of_peak_total_s
time_of_peak_x_s
time_of_peak_y_s
time_of_peak_z_s
monotonic_increasing_fraction
mpm_min_J_min
mpm_max_speed_max
solid_mean_velocity_norm_max
hydro_force_max_norm_max
max_grid_reaction_norm_max
force_to_displacement_lag_s
all_metrics_finite
validation_claim_allowed
direct_quantitative_equivalence_allowed
```

Acceptance:

- `diagnostics_source=real_solver_particles`
- all metrics finite
- z/total and y/total ratios recorded
- monotonic growth fraction recorded
- no validation or equivalence claims

## Work Package B: Opt-In Planar Structural Constraint

Add a strictly opt-in planar proxy constraint for duct-flap structural particles. It is for Step112 dynamics
diagnosis only, not a broad default behavior change.

Add `FSIDriverConfig` fields:

```python
mpm_planar_constraint_mode: str = "disabled"  # disabled | lock_z
mpm_planar_constraint_axis: str = "z"
```

Propagate to MPM config/state and implement the constraint after G2P velocity/position update and near the
existing fixed-particle constraint surface:

```text
if mpm_planar_constraint_mode == lock_z:
    x[p].z = initial_x[p].z
    v[p].z = 0
    C z row/col entries are constrained
    F z coupling terms are constrained or reset
```

Acceptance:

- default is disabled and existing configs preserve current behavior
- lock-z keeps z displacement numerically zero for unconstrained dynamic flap particles
- fixed base remains exact with planar lock enabled
- tests cover default-disabled, opt-in active, and fixed-base compatibility

## Work Package C: Opt-In Real Solver Damping

Add an opt-in proxy dynamics damping control. This is not a physical material validation claim; it is a
bounded repair control to diagnose late monotonic growth.

Add config fields:

```python
mpm_velocity_damping: float = 0.0
mpm_damping_application: str = "disabled"  # disabled | particle_velocity_post_g2p
```

Implement after G2P velocity update:

```text
if enabled:
    v[p] *= max(0, 1 - damping * dt)
```

Acceptance:

- default damping is zero/disabled
- enabled damping reduces dynamic-particle velocity norm in a deterministic unit contract
- fixed base and planar lock constraints still run after damping or are otherwise preserved exactly

## Work Package D: Real Candidate Matrix

Run a bounded matrix using real solver outputs only. It must reuse the Step111 real LBM restart and run each row
for 50 official FSI steps / 6000 LBM substeps.

Target candidate rows, bounded to 16 or fewer:

```text
cap_5e-3_E_2e4
cap_7e-3_E_2e4
cap_1e-2_E_2e4
cap_1e-2_E_5e4
cap_5e-3_E_2e4_lock_z
cap_7e-3_E_2e4_lock_z
cap_1e-2_E_2e4_lock_z
cap_1e-2_E_5e4_lock_z
cap_7e-3_E_2e4_lock_z_damp_20
cap_7e-3_E_2e4_lock_z_damp_50
cap_1e-2_E_2e4_lock_z_damp_20
cap_1e-2_E_2e4_lock_z_damp_50
cap_1e-2_E_1e5_lock_z
cap_2e-2_E_1e5_lock_z
step111_cap_2e-2_E_2e4_real_replay
```

Every row must record:

```text
row_name
evidence_mode=real_solver_particles
driver_run_called
restart_loaded
preflow_source=real_lbm_simulation
completed_official_fsi_steps
completed_lbm_substeps
diagnostics_row_count
monitor_timeseries_row_count
monitor_source=real_solver_particles
peak_solver_m
peak_reference_m
peak_relative_error
normalized_rms_error
shape_correlation
peak_time_error_s
normalized_peak_time_error
composite_error_score
fixed_base_max_displacement_norm
fixed_base_max_velocity_norm
z_to_total_peak_ratio
monotonic_increasing_fraction
has_nan
has_inf
validation_claim_allowed
direct_quantitative_equivalence_allowed
stable
```

The matrix may honestly fail the hard gate if no real candidate repairs shape/timing enough. If it fails, the
report must preserve all real rows and state the next repair direction.

## Work Package E: Real Scoring

Score candidates only from real solver metrics:

```text
score =
  0.35 * normalized_rms_error
+ 0.25 * peak_relative_error
+ 0.25 * normalized_peak_time_error
+ 0.15 * (1 - max(shape_correlation, 0))
```

Step111 baseline:

```text
normalized_rms_error = 0.7131889376595728
peak_relative_error = 1.0202873032239297
peak_time_error_s = 0.021
shape_correlation = 0.07043275817678035
```

Step108 baseline:

```text
normalized_rms_error = 0.616126763475836
shape_correlation = 0.07866350821657236
```

Hard gate:

```text
candidate_matrix_row_count >= 10
successful_real_rows >= 8
all rows evidence_mode = real_solver_particles
synthetic/replay count = 0
best_normalized_rms_error < 0.616126763475836
best_peak_relative_error < 0.75
best_shape_correlation > 0.10
best_peak_time_error_s <= 0.021
```

Stretch gate:

```text
best_normalized_rms_error < 0.35
best_peak_relative_error < 0.35
best_shape_correlation > 0.30
best_peak_time_error_s < 0.015
```

## Work Package F: Output Guard

The Step112 guard must inherit Step111 anti-synthetic checks and add real-matrix checks:

```text
all_candidate_curves_real_solver = true
real_driver_run_called_count >= successful_real_rows
real_monitor_source_count == successful_real_rows
synthetic_candidate_curve_count = 0
proxy_curve_replay_evidence_mode_count = 0
solver_curve_generated_from_reference_count = 0
reference_curve_used_only_for_error_metrics = true
official_case_file_count = 0
official_mesh_file_count = 0
official_journal_file_count = 0
official_case_data_h5_count = 0
validation_claim_count = 0
direct_equivalence_claim_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
private_absolute_path_count = 0
```

## Required Output Directories

```text
outputs/step112_real_dynamics_diagnostics/
outputs/step112_real_candidate_matrix/
outputs/step112_real_candidate_matrix/curves/
outputs/step112_real_candidate_matrix/driver_runs/
outputs/step112_error_comparison/
outputs/step112_output_guard/
outputs/step112_artifact_manifest/
```

## Required Files

Goal, docs, report:

```text
STEP112_FLUENT_PUBLIC_PLOT_REAL_SOLVER_DYNAMICS_REPAIR_MATRIX_GOAL.md
STEP112_FLUENT_PUBLIC_PLOT_REAL_SOLVER_DYNAMICS_REPAIR_MATRIX_REPORT.md
docs/112_fluent_public_plot_real_solver_dynamics_repair_matrix.md
```

Configs:

```text
configs/step112_real_dynamics_matrix_policy.json
configs/step112_output_guard_policy.json
configs/step112_artifact_manifest_policy.json
configs/step112_candidates/*.json
```

Source:

```text
src/mpm_lbm/evidence/step112_common.py
src/mpm_lbm/evidence/step112_real_dynamics_diagnostics.py
src/mpm_lbm/evidence/step112_real_candidate_matrix_runner.py
src/mpm_lbm/evidence/step112_error_scoring.py
src/mpm_lbm/evidence/step112_output_guard.py
src/mpm_lbm/sim/drivers/fsi_config.py
src/mpm_lbm/sim/mpm/config.py
src/mpm_lbm/sim/mpm/solid.py
```

Baseline runners:

```text
baseline_tests/run_step112_real_dynamics_diagnostics.py
baseline_tests/run_step112_real_candidate_matrix.py
baseline_tests/run_step112_output_guard.py
baseline_tests/run_step112_artifact_manifest.py
```

Tests:

```text
tests/test_step112_real_dynamics_diagnostics_contract.py
tests/test_step112_real_candidate_matrix_contract.py
tests/test_step112_planar_constraint_contract.py
tests/test_step112_output_guard_contract.py
```

## Red/Green Flow

RED:

- write Step112 contract tests before generating Step112 artifacts
- confirm diagnostics/report tests fail due missing outputs
- confirm planar constraint tests fail before new config/control exists
- confirm matrix/guard tests fail before real rows are generated

GREEN:

1. implement diagnostics from existing Step111 real artifacts
2. implement opt-in planar lock and damping with default-disabled behavior
3. run a bounded real candidate matrix
4. generate real error reports and scoring
5. generate output guard and artifact manifest

REFACTOR:

- reuse Step111 real monitor extraction where practical
- do not import or copy Step110 synthetic curve generation
- keep solver changes opt-in and bounded to Step112 config fields

## Verification Commands

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\evidence\step112_common.py `
  src\mpm_lbm\evidence\step112_real_dynamics_diagnostics.py `
  src\mpm_lbm\evidence\step112_real_candidate_matrix_runner.py `
  src\mpm_lbm\evidence\step112_error_scoring.py `
  src\mpm_lbm\evidence\step112_output_guard.py `
  src\mpm_lbm\sim\drivers\fsi_config.py `
  src\mpm_lbm\sim\mpm\config.py `
  src\mpm_lbm\sim\mpm\solid.py

& 'D:\working\taichi\env\python.exe' baseline_tests\run_step112_real_dynamics_diagnostics.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step112_real_candidate_matrix.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step112_output_guard.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step112_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -m pytest -q `
  tests\test_step112_real_dynamics_diagnostics_contract.py `
  tests\test_step112_real_candidate_matrix_contract.py `
  tests\test_step112_planar_constraint_contract.py `
  tests\test_step112_output_guard_contract.py

& 'D:\working\taichi\env\python.exe' -m pytest -q
git diff --check
```

Plain `pytest -q` or Anaconda may be attempted for parity but is not a hard gate if the environment blocks it.

## Completion Criteria

Step112 is complete when:

- the detailed goal file exists and is referenced by the active goal
- diagnostics decompose the Step111 real failure with finite real metrics
- planar lock and damping are opt-in, default-disabled, and contract-tested
- candidate matrix rows are real solver runs only
- output guard reports zero synthetic/replay/reference-derived curve counts
- docs/report state whether the hard gate passed or failed without overclaiming
- focused Step112 tests pass
- full trusted pytest passes
- `git diff --check` passes or only reports known non-content line-ending warnings
- code, configs, tests, docs, logs, and artifacts are committed and pushed to `origin/main`

## Step113 Routing

After Step112:

- If Step112 only reduces amplitude but shape remains poor, Step113 should repair structural dynamics or reaction-transfer physics.
- If lock-z improves RMS/shape, Step113 should refine 2D proxy consistency: fixed-z constraint, 2D monitor, and force-area weighting.
- If damping improves peak timing/shape, Step113 should do damping convergence and stability checks without claiming physical material validation.
- If Step112 reaches the stretch gate, Step113 may proceed to resolution/particle refinement (`n_particles 1024 -> 4096`, possibly `n_grid 48 -> 64`), still real solver only.
