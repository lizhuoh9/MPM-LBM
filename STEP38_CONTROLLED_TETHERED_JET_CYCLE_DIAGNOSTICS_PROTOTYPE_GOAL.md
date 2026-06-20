# Step 38 Controlled Tethered Jet-Cycle Diagnostics Prototype Goal

## Objective

Implement Step 38 as a controlled tethered jet-cycle diagnostics prototype for the squid proxy workflow. Step 38 must run one prescribed 40-step kinematic cycle through the accepted opt-in wall-velocity application path and summarize cavity-volume, funnel-aperture, wall-velocity, force, bounce-back, and impulse-proxy diagnostics.

Step 38 is diagnostic-only. It must not claim real jet validation, jet propulsion validation, free-body swimming, production sharp-interface FSI readiness, or real squid validation.

The compact active goal for this work is:

```text
Implement Step 38 from STEP38_CONTROLLED_TETHERED_JET_CYCLE_DIAGNOSTICS_PROTOTYPE_GOAL.md: add explicit 48^3/40-step tethered cycle configs, proxy diagnostics, baseline runners, contract tests, report/docs, verification artifacts, and push to origin/main. Preserve default static/disabled modes, preserve solver formulas, preserve moving bounce-back formulas, preserve projection/coupling/MPM/LBM formulas, and do not edit external/taichi_LBM3D.
```

## Scope

Step 37 accepted a 48^3, 20-step wall-velocity application envelope. Step 38 extends that controlled surface to one full prescribed cycle:

```text
cycle_period_steps = 40
```

The implementation must demonstrate that:

1. A 48^3 run can complete one prescribed 40-step cycle for all four matrix rows.
2. Experimental wall-velocity application rows write one application report per step.
3. Wall-velocity application remains finite and capped.
4. The cavity-volume proxy completes a closed schedule-derived cycle.
5. The funnel-aperture proxy completes an opening/closing schedule-derived cycle.
6. Existing bounce-back and hydro-force diagnostics can be summarized into bounded force and impulse proxies.
7. Static and experimental rows remain bounded relative to each other.
8. Engineering and link-area transfer rows remain bounded relative to each other.
9. The workflow remains tethered: no free-body state, no rigid-body swimming integration, and no displacement or propulsion claim.
10. Step 37 artifacts still satisfy their previous acceptance guard.

## Hard Boundaries

Do not implement or claim:

- real jet validation
- jet propulsion validation
- free-body motion
- squid swimming
- real squid validation
- production sharp-interface FSI
- two-phase flow
- contact-angle physics
- a new coupling formula
- a moving bounce-back formula change
- an LBM collision or streaming formula change
- an MPM constitutive formula change
- a projection formula change
- a default wall-velocity application change
- a default `boundary_motion_mode` change
- edits under `external/taichi_LBM3D`
- raw real geometry or scan-data ingestion

Allowed work:

- explicit 40-step Step 38 driver configs
- schedule-derived cavity-volume proxy diagnostics
- schedule-derived funnel-aperture proxy diagnostics
- wall-velocity application timeseries summaries
- existing-diagnostics force and bounce-back envelopes
- impulse-norm proxy summaries from existing diagnostics
- static versus experimental comparisons
- engineering versus link-area comparisons
- no-free-body guard artifacts
- Step 37 regression guard
- small CSV/JSON/NPZ/log artifacts

## Validation Matrix

Add exactly four 48^3 driver configs:

```text
configs/step38_cycle_static_48_moving_boundary.json
configs/step38_cycle_experimental_48_moving_boundary.json
configs/step38_cycle_static_48_link_area.json
configs/step38_cycle_experimental_48_link_area.json
```

The four rows are:

```text
48^3 static moving_boundary engineering, 40 steps
48^3 experimental moving_boundary engineering, 40 steps
48^3 static moving_boundary link_area_experimental, 40 steps
48^3 experimental moving_boundary link_area_experimental, 40 steps
```

Required driver settings:

```json
{
  "n_grid": 48,
  "n_particles": 4096,
  "n_lbm_steps": 40,
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
src/jet_cycle_proxy_diagnostics.py
src/tethered_cycle_diagnostics.py
```

`src/jet_cycle_proxy_diagnostics.py` should expose focused helpers for:

- loading the Step 32 kinematic schedule
- extracting cycle-period and phase alignment
- computing schedule-derived cavity-volume cycle proxies
- computing schedule-derived funnel-aperture cycle proxies
- summarizing wall-velocity application cycle quality
- summarizing force and impulse proxies from existing diagnostics rows
- writing small CSV/JSON outputs

The cavity-volume proxy is schedule-derived only. It is not an internal-fluid volume solver. Expected fields include:

```text
cavity_volume_scale_min
cavity_volume_scale_max
contraction_sample_count
refill_sample_count
expelled_volume_proxy
refill_volume_proxy
net_cycle_volume_proxy
closed_cycle_pass
```

The funnel-aperture proxy is schedule-derived only. Expected fields include:

```text
funnel_aperture_min
funnel_aperture_max
funnel_open_sample_count
funnel_closed_or_rest_sample_count
aperture_cycle_pass
```

The impulse proxy uses existing diagnostics only. Expected fields include:

```text
hydro_force_max_norm_integral_proxy
bb_correction_integral_proxy
bb_link_count_integral_proxy
impulse_proxy_finite_pass
```

`src/tethered_cycle_diagnostics.py` should expose helpers that prove the Step 38 workflow did not add a free-body swimming state:

```text
free_body_state_file_count == 0
rigid_body_integrator_enabled == false
body_position_state_enabled == false
swimming_displacement_claim_enabled == false
target_u_lbm_zero_for_cycle_configs == true
```

Optional centroid diagnostics may be reported only as diagnostic-only quantities, never as swimming displacement.

## Baseline Runners

Add:

```text
baseline_tests/step38_common.py
baseline_tests/run_step38_cycle_driver.py
baseline_tests/run_step38_cycle_proxy_diagnostics.py
baseline_tests/run_step38_static_vs_experimental_cycle_comparison.py
baseline_tests/run_step38_engineering_vs_link_area_cycle_comparison.py
baseline_tests/run_step38_wall_velocity_cycle_quality.py
baseline_tests/run_step38_force_impulse_proxy_summary.py
baseline_tests/run_step38_tethered_no_free_body_guard.py
baseline_tests/run_step38_quality_report_aggregation.py
baseline_tests/run_step38_step37_regression_guard.py
baseline_tests/run_step38_artifact_manifest.py
```

## Required Outputs

Cycle driver:

```text
outputs/step38_cycle_driver/cycle_driver_results.csv
outputs/step38_cycle_driver/cycle_driver_results.json
outputs/step38_cycle_driver/cycle_driver_results.npz
outputs/step38_cycle_driver/<case>/diagnostics_timeseries.csv
outputs/step38_cycle_driver/<case>/wall_velocity_application_timeseries.csv
outputs/step38_cycle_driver/<case>/wall_velocity_application_timeseries.json
outputs/step38_cycle_driver/<case>/geometry_quality_report.json
logs/step38_cycle_driver.log
```

Cycle proxy diagnostics:

```text
outputs/step38_cycle_proxy_diagnostics/cycle_proxy_diagnostics.csv
outputs/step38_cycle_proxy_diagnostics/cycle_proxy_diagnostics.json
logs/step38_cycle_proxy_diagnostics.log
```

Static versus experimental comparison:

```text
outputs/step38_static_vs_experimental_cycle_comparison/static_vs_experimental_cycle.csv
outputs/step38_static_vs_experimental_cycle_comparison/static_vs_experimental_cycle.json
logs/step38_static_vs_experimental_cycle_comparison.log
```

Engineering versus link-area comparison:

```text
outputs/step38_engineering_vs_link_area_cycle_comparison/engineering_vs_link_area_cycle.csv
outputs/step38_engineering_vs_link_area_cycle_comparison/engineering_vs_link_area_cycle.json
logs/step38_engineering_vs_link_area_cycle_comparison.log
```

Wall-velocity cycle quality:

```text
outputs/step38_wall_velocity_cycle_quality/wall_velocity_cycle_quality.csv
outputs/step38_wall_velocity_cycle_quality/wall_velocity_cycle_quality.json
logs/step38_wall_velocity_cycle_quality.log
```

Force and impulse proxy summary:

```text
outputs/step38_force_impulse_proxy_summary/force_impulse_proxy_summary.csv
outputs/step38_force_impulse_proxy_summary/force_impulse_proxy_summary.json
logs/step38_force_impulse_proxy_summary.log
```

Tethered no-free-body guard:

```text
outputs/step38_tethered_no_free_body_guard/tethered_no_free_body_guard.csv
outputs/step38_tethered_no_free_body_guard/tethered_no_free_body_guard.json
logs/step38_tethered_no_free_body_guard.log
```

Quality report aggregation:

```text
outputs/step38_quality_report_aggregation/quality_report_summary.csv
outputs/step38_quality_report_aggregation/quality_report_summary.json
logs/step38_quality_report_aggregation.log
```

Step 37 regression guard:

```text
outputs/step38_step37_regression_guard/step37_regression_guard.csv
outputs/step38_step37_regression_guard/step37_regression_guard.json
logs/step38_step37_regression_guard.log
```

Artifact manifest:

```text
outputs/step38_artifact_manifest/artifact_manifest.csv
outputs/step38_artifact_manifest/artifact_summary.csv
outputs/step38_artifact_manifest/artifact_summary.json
logs/step38_artifact_manifest.log
```

Documentation and report:

```text
docs/38_controlled_tethered_jet_cycle_diagnostics_prototype.md
STEP38_CONTROLLED_TETHERED_JET_CYCLE_DIAGNOSTICS_PROTOTYPE_REPORT.md
```

## Acceptance Conditions

Cycle driver:

- `row_count == 4`
- `stable_count == 4`
- `experimental_row_count == 2`
- `static_row_count == 2`
- `completed_lbm_steps >= 40`
- `total_mpm_substeps >= 200`
- `rho_min > 0.95`
- `rho_max < 1.05`
- `lbm_max_v < 0.1`
- `mpm_min_J > 0`
- `projected_mass > 0`
- `active_cell_count > 0`
- `bb_link_count > 0`
- `quality_pass == true`
- no NaN
- no Inf

Experimental rows:

- `application_report_count >= 40`
- `applied_cell_count_min > 0`
- `max_applied_velocity_norm <= configured cap`
- `lbm_population_update_count == 0`
- `modify_bounceback_formula == false`

Cycle proxy diagnostics:

- `cycle_period_steps == 40`
- `schedule_row_count == 81`
- `phase_alignment_pass == true`
- `cavity_volume_cycle_pass == true`
- `funnel_aperture_cycle_pass == true`
- `expelled_volume_proxy > 0`
- `refill_volume_proxy > 0`
- `abs(net_cycle_volume_proxy) <= max(1e-8, 1e-6 * cavity_rest_volume)`
- `funnel_aperture_max > funnel_aperture_min`

Comparisons:

- static versus experimental produces two passing rows
- engineering versus link-area produces one passing row
- comparison deltas are finite
- `0.25 <= link_area_scale_final <= 2.0`

Wall-velocity cycle quality:

- two experimental rows pass
- each experimental row has at least 40 timeseries rows
- phase sequence covers the full cycle
- applied cell count is positive
- velocity cap passes
- LBM population update count remains zero

Force and impulse proxy summary:

- four rows pass
- hydro-force, bounce-back correction, and bounce-back link-count integrals are finite
- bounce-back link-count integral is positive
- output language remains proxy-only

Tethered guard:

- no free-body state files
- no rigid-body integrator state
- no body-position swimming state
- no swimming displacement claim
- all Step 38 cycle configs use zero `target_u_lbm`

Artifact and repo hygiene:

- Step 37 regression guard passes
- four Step 38 quality reports pass strictly
- no Step 38 VTR outputs
- no Step 38 particle NPY outputs
- no large files
- `step38_total_size_mb < 25`
- repo total size remains below 240 MB
- no raw scan data
- no private absolute paths in Step 38 outputs
- `external/taichi_LBM3D` remains untouched

## Contract Test

Add:

```text
tests/test_step38_tethered_jet_cycle_diagnostics_contract.py
```

Required test cases:

```text
test_step38_required_artifacts_exist
test_step38_driver_configs_are_valid
test_step38_cycle_driver_is_valid
test_step38_cycle_proxy_diagnostics_are_valid
test_step38_static_vs_experimental_cycle_comparison_is_valid
test_step38_engineering_vs_link_area_cycle_comparison_is_valid
test_step38_wall_velocity_cycle_quality_is_valid
test_step38_force_impulse_proxy_summary_is_valid
test_step38_tethered_no_free_body_guard_is_valid
test_step38_quality_report_aggregation_is_valid
test_step38_step37_regression_guard_is_valid
test_step38_default_modes_remain_unchanged
test_step38_docs_scope_and_forbidden_claims_are_valid
test_step38_artifact_budget_is_valid
test_step38_report_acceptance_complete
```

Required scope phrases:

```text
Step 38 is controlled tethered jet-cycle diagnostics prototype.
Step 38 uses proxy cavity-volume and funnel-aperture diagnostics only.
Step 38 does not validate a real jet.
Step 38 does not implement free-body motion.
Step 38 does not implement squid swimming.
Step 38 does not implement real squid validation.
Step 38 does not change moving bounce-back formulas.
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
& 'D:\working\taichi\env\python.exe' -m py_compile src\jet_cycle_proxy_diagnostics.py src\tethered_cycle_diagnostics.py baseline_tests\step38_common.py baseline_tests\run_step38_cycle_driver.py baseline_tests\run_step38_cycle_proxy_diagnostics.py baseline_tests\run_step38_static_vs_experimental_cycle_comparison.py baseline_tests\run_step38_engineering_vs_link_area_cycle_comparison.py baseline_tests\run_step38_wall_velocity_cycle_quality.py baseline_tests\run_step38_force_impulse_proxy_summary.py baseline_tests\run_step38_tethered_no_free_body_guard.py baseline_tests\run_step38_quality_report_aggregation.py baseline_tests\run_step38_step37_regression_guard.py baseline_tests\run_step38_artifact_manifest.py tests\test_step38_tethered_jet_cycle_diagnostics_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_cycle_driver.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_cycle_proxy_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_static_vs_experimental_cycle_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_engineering_vs_link_area_cycle_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_wall_velocity_cycle_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_force_impulse_proxy_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_tethered_no_free_body_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_step37_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step38_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step38_tethered_jet_cycle_diagnostics_contract.py -q
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
test: add step38 tethered jet cycle diagnostics
```

## Step 39 Candidate

If Step 38 passes, Step 39 should be:

```text
Step 39 Controlled Jet-Cycle Proxy Multi-Cycle Stability Envelope
```

Step 39 would extend the Step 38 one-cycle diagnostic prototype to two or three cycles and check per-cycle drift of cavity/funnel/wall-velocity/force/impulse proxies. Step 39 must still avoid free-body swimming and real jet validation claims.
