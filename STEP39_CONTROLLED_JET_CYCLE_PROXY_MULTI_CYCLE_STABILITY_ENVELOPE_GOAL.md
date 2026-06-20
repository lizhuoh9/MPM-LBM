# Step 39 Controlled Jet-Cycle Proxy Multi-Cycle Stability Envelope Goal

## Objective

Implement Step 39 as a controlled jet-cycle proxy multi-cycle stability envelope. Step 39 must extend the accepted Step 38 tethered one-cycle proxy diagnostics to a two-cycle, 80-step stability envelope and summarize cycle-to-cycle drift in cavity-volume proxy, funnel-aperture proxy, wall-velocity application, force, bounce-back, and impulse-proxy diagnostics.

Step 39 is still a tethered proxy-diagnostic step. It must not add free-body motion, body trajectory integration, squid swimming, real jet validation, jet propulsion validation, production sharp-interface FSI readiness, or real squid validation.

The compact active goal for this work is:

```text
Implement Step 39 from STEP39_CONTROLLED_JET_CYCLE_PROXY_MULTI_CYCLE_STABILITY_ENVELOPE_GOAL.md: add explicit 48^3/80-step two-cycle configs, multicycle proxy diagnostics, drift summaries, baseline runners, contract tests, docs/report, verification artifacts, then commit and push to origin/main. Preserve default static/disabled modes, preserve solver/moving-bounceback/projection/coupling/MPM/LBM formulas, and do not edit external/taichi_LBM3D.
```

## Scope

Step 38 demonstrated one prescribed 40-step cycle. Step 39 must verify that the same tethered proxy diagnostics remain stable over two consecutive cycles:

```text
cycle_period_steps = 40
cycle_count = 2
n_lbm_steps = 80
mpm_substeps_per_lbm_step = 5
total_mpm_substeps = 400
```

The implementation must demonstrate that:

1. The same 48^3 static/experimental by engineering/link-area matrix completes two cycles.
2. Each row completes at least 80 LBM steps and 400 MPM substeps.
3. Each experimental row writes at least 80 wall-velocity application reports.
4. Cavity-volume proxy closes in cycle 1 and cycle 2.
5. Funnel-aperture proxy opens and closes in cycle 1 and cycle 2.
6. Expelled/refill volume proxy drift from cycle 1 to cycle 2 is bounded.
7. Force, bounce-back, and impulse proxy drift from cycle 1 to cycle 2 is bounded.
8. Experimental rows remain bounded relative to static rows.
9. Link-area transfer remains bounded relative to engineering transfer.
10. No free-body state, body trajectory, or swimming-displacement state is written.
11. Step 38 artifacts still satisfy their regression guard.
12. Step 39 artifacts remain small and avoid VTR or particle NPY outputs.

## Hard Boundaries

Do not implement or claim:

- real jet validation
- jet propulsion validation
- free-body motion
- rigid-body integration
- body trajectory integration
- squid swimming
- swimming displacement claim
- real squid validation
- production sharp-interface FSI
- two-phase flow
- contact-angle physics
- a new coupling formula
- a moving bounce-back formula change
- an LBM collision formula change
- an LBM streaming formula change
- an MPM constitutive formula change
- a projection formula change
- a default wall-velocity application change
- a default boundary-motion change
- edits under `external/taichi_LBM3D`
- raw real geometry or scan-data ingestion

Allowed work:

- explicit 80-step Step 39 driver configs
- two-cycle cavity-volume proxy diagnostics
- two-cycle funnel-aperture proxy diagnostics
- per-cycle wall-velocity application summaries
- per-cycle force and bounce-back envelopes
- impulse-norm proxy summaries from existing diagnostics
- cycle-to-cycle drift summaries
- static versus experimental multicycle comparisons
- engineering versus link-area multicycle comparisons
- no-free-body guard artifacts
- Step 38 regression guard
- small CSV/JSON/NPZ/log artifacts

## Validation Matrix

Add exactly four 48^3 driver configs:

```text
configs/step39_multicycle_static_48_moving_boundary.json
configs/step39_multicycle_experimental_48_moving_boundary.json
configs/step39_multicycle_static_48_link_area.json
configs/step39_multicycle_experimental_48_link_area.json
```

The four rows are:

```text
48^3 static moving_boundary engineering, 80 steps
48^3 experimental moving_boundary engineering, 80 steps
48^3 static moving_boundary link_area_experimental, 80 steps
48^3 experimental moving_boundary link_area_experimental, 80 steps
```

Required driver settings:

```json
{
  "n_grid": 48,
  "n_particles": 4096,
  "n_lbm_steps": 80,
  "mpm_substeps_per_lbm_step": 5,
  "output_interval": 1,
  "target_u_lbm": [0.0, 0.0, 0.0],
  "coupling_mode": "moving_boundary",
  "geometry_type": "squid_proxy",
  "geometry_config_path": "configs/step30_squid_proxy_geometry.json",
  "quality_check_enabled": true,
  "quality_check_strict": true,
  "write_vtk": false,
  "write_particles": false
}
```

Experimental rows must use:

```json
{
  "boundary_motion_mode": "prescribed_kinematic",
  "boundary_motion_config_path": "configs/step34_boundary_motion_interface_prescribed_kinematic.json",
  "boundary_motion_report_enabled": true,
  "wall_velocity_application_mode": "solid_vel_experimental",
  "wall_velocity_application_config_path": "configs/step36_wall_velocity_application_solid_vel_experimental.json",
  "wall_velocity_application_report_enabled": true
}
```

Static rows must use:

```json
{
  "boundary_motion_mode": "static",
  "wall_velocity_application_mode": "disabled",
  "wall_velocity_application_config_path": null,
  "wall_velocity_application_report_enabled": false
}
```

## Source Files

Add:

```text
src/multicycle_proxy_diagnostics.py
```

Extend, if needed:

```text
src/jet_cycle_proxy_diagnostics.py
src/tethered_cycle_diagnostics.py
```

`src/multicycle_proxy_diagnostics.py` must expose focused helpers for:

- assigning a driver step to a cycle index
- splitting diagnostics rows by cycle
- summarizing per-cycle stability envelopes
- summarizing cycle-to-cycle drift
- summarizing per-cycle force and impulse proxies
- summarizing per-cycle wall-velocity application quality
- writing small CSV/JSON outputs

Expected per-cycle stability fields:

```text
case
cycle_index
step_min
step_max
row_count
rho_min
rho_max
lbm_max_v
mpm_min_J
mpm_max_speed
projected_mass_min
projected_mass_max
bb_link_count_min
bb_link_count_max
bb_max_correction_max
hydro_force_max_norm
cycle_stable
```

Expected drift fields:

```text
case
rho_min_drift_cycle2_minus_cycle1
rho_max_drift_cycle2_minus_cycle1
lbm_max_v_drift
mpm_min_J_drift
projected_mass_drift
hydro_force_max_norm_drift
bb_max_correction_drift
drift_pass
```

Drift acceptance:

```text
abs(projected_mass_drift) <= 1e-3
abs(lbm_max_v_drift) <= 5e-3
abs(rho_min_drift_cycle2_minus_cycle1) <= 5e-3
abs(rho_max_drift_cycle2_minus_cycle1) <= 5e-3
all drift values finite
```

`src/jet_cycle_proxy_diagnostics.py` may be extended with helpers for:

```text
summarize_cavity_proxy_by_cycle
summarize_funnel_proxy_by_cycle
summarize_impulse_proxy_by_cycle
summarize_wall_velocity_proxy_by_cycle
```

`src/tethered_cycle_diagnostics.py` may be extended with:

```text
summarize_multicycle_tethered_guard
```

It must continue to prove:

```text
free_body_state_file_count == 0
rigid_body_integrator_enabled == false
body_position_state_enabled == false
swimming_displacement_claim_enabled == false
target_u_lbm_zero_for_cycle_configs == true
body_trajectory_output_count == 0
```

## Baseline Runners

Add:

```text
baseline_tests/step39_common.py
baseline_tests/run_step39_multicycle_driver.py
baseline_tests/run_step39_multicycle_proxy_diagnostics.py
baseline_tests/run_step39_cycle_to_cycle_drift_summary.py
baseline_tests/run_step39_wall_velocity_multicycle_quality.py
baseline_tests/run_step39_static_vs_experimental_multicycle_comparison.py
baseline_tests/run_step39_engineering_vs_link_area_multicycle_comparison.py
baseline_tests/run_step39_force_impulse_multicycle_summary.py
baseline_tests/run_step39_tethered_no_free_body_guard.py
baseline_tests/run_step39_quality_report_aggregation.py
baseline_tests/run_step39_step38_regression_guard.py
baseline_tests/run_step39_artifact_manifest.py
```

## Required Outputs

Multi-cycle driver:

```text
outputs/step39_multicycle_driver/multicycle_driver_results.csv
outputs/step39_multicycle_driver/multicycle_driver_results.json
outputs/step39_multicycle_driver/multicycle_driver_results.npz
outputs/step39_multicycle_driver/<case>/diagnostics_timeseries.csv
outputs/step39_multicycle_driver/<case>/wall_velocity_application_timeseries.csv
outputs/step39_multicycle_driver/<case>/wall_velocity_application_timeseries.json
outputs/step39_multicycle_driver/<case>/geometry_quality_report.json
logs/step39_multicycle_driver.log
```

Multi-cycle proxy diagnostics:

```text
outputs/step39_multicycle_proxy_diagnostics/multicycle_proxy_diagnostics.csv
outputs/step39_multicycle_proxy_diagnostics/multicycle_proxy_diagnostics.json
logs/step39_multicycle_proxy_diagnostics.log
```

Cycle-to-cycle drift summary:

```text
outputs/step39_cycle_to_cycle_drift_summary/cycle_to_cycle_drift.csv
outputs/step39_cycle_to_cycle_drift_summary/cycle_to_cycle_drift.json
logs/step39_cycle_to_cycle_drift_summary.log
```

Wall-velocity multicycle quality:

```text
outputs/step39_wall_velocity_multicycle_quality/wall_velocity_multicycle_quality.csv
outputs/step39_wall_velocity_multicycle_quality/wall_velocity_multicycle_quality.json
logs/step39_wall_velocity_multicycle_quality.log
```

Static versus experimental multicycle comparison:

```text
outputs/step39_static_vs_experimental_multicycle_comparison/static_vs_experimental_multicycle.csv
outputs/step39_static_vs_experimental_multicycle_comparison/static_vs_experimental_multicycle.json
logs/step39_static_vs_experimental_multicycle_comparison.log
```

Engineering versus link-area multicycle comparison:

```text
outputs/step39_engineering_vs_link_area_multicycle_comparison/engineering_vs_link_area_multicycle.csv
outputs/step39_engineering_vs_link_area_multicycle_comparison/engineering_vs_link_area_multicycle.json
logs/step39_engineering_vs_link_area_multicycle_comparison.log
```

Force and impulse multicycle summary:

```text
outputs/step39_force_impulse_multicycle_summary/force_impulse_multicycle_summary.csv
outputs/step39_force_impulse_multicycle_summary/force_impulse_multicycle_summary.json
logs/step39_force_impulse_multicycle_summary.log
```

Tethered no-free-body guard:

```text
outputs/step39_tethered_no_free_body_guard/tethered_no_free_body_guard.csv
outputs/step39_tethered_no_free_body_guard/tethered_no_free_body_guard.json
logs/step39_tethered_no_free_body_guard.log
```

Quality report aggregation:

```text
outputs/step39_quality_report_aggregation/quality_report_summary.csv
outputs/step39_quality_report_aggregation/quality_report_summary.json
logs/step39_quality_report_aggregation.log
```

Step 38 regression guard:

```text
outputs/step39_step38_regression_guard/step38_regression_guard.csv
outputs/step39_step38_regression_guard/step38_regression_guard.json
logs/step39_step38_regression_guard.log
```

Artifact manifest:

```text
outputs/step39_artifact_manifest/artifact_manifest.csv
outputs/step39_artifact_manifest/artifact_summary.csv
outputs/step39_artifact_manifest/artifact_summary.json
logs/step39_artifact_manifest.log
```

Documentation and report:

```text
docs/39_controlled_jet_cycle_proxy_multi_cycle_stability_envelope.md
STEP39_CONTROLLED_JET_CYCLE_PROXY_MULTI_CYCLE_STABILITY_ENVELOPE_REPORT.md
```

## Acceptance Conditions

Multi-cycle driver:

- `row_count == 4`
- `stable_count == 4`
- `static_row_count == 2`
- `experimental_row_count == 2`
- `completed_lbm_steps >= 80`
- `total_mpm_substeps >= 400`
- `rho_min > 0.95`
- `rho_max < 1.05`
- `lbm_max_v < 0.1`
- `mpm_min_J > 0`
- `projected_mass > 0`
- `active_cell_count > 0`
- `bb_link_count > 0`
- no NaN
- no Inf

Experimental rows:

- `wall_velocity_application_report_count >= 80`
- `max_applied_velocity_norm <= 0.01`
- `lbm_population_update_count == 0`

Multi-cycle proxy diagnostics:

- `cycle_count == 2`
- `cycle_period_steps == 40`
- phase alignment passes for cycle 1 and cycle 2
- cavity volume proxy closes in both cycles
- funnel aperture proxy opens and closes in both cycles
- expelled volume proxy is positive in both cycles
- refill volume proxy is positive in both cycles
- wall velocity cycle pass is true for experimental rows

Cycle-to-cycle drift:

- four rows pass
- all drift values are finite
- `abs(projected_mass_drift) <= 1e-3`
- `abs(lbm_max_v_drift) <= 5e-3`
- `abs(rho_min_drift_cycle2_minus_cycle1) <= 5e-3`
- `abs(rho_max_drift_cycle2_minus_cycle1) <= 5e-3`

Comparisons:

- static versus experimental produces two passing rows
- engineering versus link-area produces one passing row
- comparison deltas are finite
- `0.25 <= link_area_scale_final <= 2.0`

Force and impulse multicycle summary:

- eight rows pass
- all proxy integrals are finite
- bounce-back link-count integral is positive for every row
- output language remains proxy-only

Tethered guard:

- no free-body state files
- no body trajectory output
- no rigid-body integrator state
- no body-position swimming state
- no swimming displacement claim
- all Step 39 cycle configs use zero `target_u_lbm`

Artifact and repo hygiene:

- Step 38 regression guard passes
- four Step 39 quality reports pass strictly
- no Step 39 VTR outputs
- no Step 39 particle NPY outputs
- no large files
- `step39_total_size_mb < 35`
- repo total size remains below 260 MB
- no raw scan data
- no private absolute paths in Step 39 outputs
- `external/taichi_LBM3D` remains untouched

## Contract Test

Add:

```text
tests/test_step39_multicycle_jet_proxy_stability_contract.py
```

Required test cases:

```text
test_step39_required_artifacts_exist
test_step39_driver_configs_are_valid
test_step39_multicycle_driver_is_valid
test_step39_multicycle_proxy_diagnostics_are_valid
test_step39_cycle_to_cycle_drift_summary_is_valid
test_step39_wall_velocity_multicycle_quality_is_valid
test_step39_static_vs_experimental_multicycle_comparison_is_valid
test_step39_engineering_vs_link_area_multicycle_comparison_is_valid
test_step39_force_impulse_multicycle_summary_is_valid
test_step39_tethered_no_free_body_guard_is_valid
test_step39_quality_report_aggregation_is_valid
test_step39_step38_regression_guard_is_valid
test_step39_default_modes_remain_unchanged
test_step39_docs_scope_and_forbidden_claims_are_valid
test_step39_artifact_budget_is_valid
test_step39_report_acceptance_complete
```

Required scope phrases:

```text
Step 39 is controlled jet-cycle proxy multi-cycle stability envelope.
Step 39 repeats tethered proxy diagnostics over two cycles.
Step 39 does not validate a real jet.
Step 39 does not implement free-body motion.
Step 39 does not implement squid swimming.
Step 39 does not implement real squid validation.
Step 39 does not change moving bounce-back formulas.
The default boundary_motion_mode remains static.
The default wall_velocity_application_mode remains disabled.
```

Forbidden claims:

```text
real jet validation
jet propulsion is validated
squid swimming is implemented
free-body motion is implemented
real squid simulation is validated
production-ready sharp-interface FSI
final solver readiness
two-phase flow is implemented
contact angle physics is implemented
moving bounce-back formula is changed
default wall velocity application is enabled
```

## Verification Commands

Use `D:\working\taichi\env\python.exe`:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\multicycle_proxy_diagnostics.py src\jet_cycle_proxy_diagnostics.py src\tethered_cycle_diagnostics.py baseline_tests\step39_common.py baseline_tests\run_step39_multicycle_driver.py baseline_tests\run_step39_multicycle_proxy_diagnostics.py baseline_tests\run_step39_cycle_to_cycle_drift_summary.py baseline_tests\run_step39_wall_velocity_multicycle_quality.py baseline_tests\run_step39_static_vs_experimental_multicycle_comparison.py baseline_tests\run_step39_engineering_vs_link_area_multicycle_comparison.py baseline_tests\run_step39_force_impulse_multicycle_summary.py baseline_tests\run_step39_tethered_no_free_body_guard.py baseline_tests\run_step39_quality_report_aggregation.py baseline_tests\run_step39_step38_regression_guard.py baseline_tests\run_step39_artifact_manifest.py tests\test_step39_multicycle_jet_proxy_stability_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_multicycle_driver.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_multicycle_proxy_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_cycle_to_cycle_drift_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_wall_velocity_multicycle_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_static_vs_experimental_multicycle_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_engineering_vs_link_area_multicycle_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_force_impulse_multicycle_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_tethered_no_free_body_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_step38_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step39_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step39_multicycle_jet_proxy_stability_contract.py -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## Final Delivery

Finish only after:

- code and artifacts are committed
- the push to `origin/main` completes
- the final answer reports the commit hash, branch, and verification results

Recommended commit message:

```text
test: add step39 multicycle jet proxy stability envelope
```

## Step 40 Candidate

If Step 39 passes, Step 40 should be:

```text
Step 40 Controlled Jet-Cycle Proxy Parameter Sensitivity Smoke
```

Step 40 should remain tethered and should test a small parameter set without adding free-body motion, swimming claims, or real propulsion claims.
