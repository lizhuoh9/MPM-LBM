# Step 37 Goal: Controlled Moving-Wall Application Short-Window Envelope

## Objective

Implement Step 37 as a controlled moving-wall application short-window envelope.

Step 37 extends the accepted Step 36 opt-in `solid_vel_experimental` wall-velocity application from 5-step smoke runs to a 20-step short-window envelope. It must remain guarded, experimental, report-backed, and conservative.

Step 37 must preserve static/default behavior and must not change LBM, MPM, projection, coupling, or moving bounce-back formulas. Step 37 must not claim jet model behavior, expelled-volume physics, squid actuation, squid swimming, real squid validation, production sharp-interface FSI, or final solver readiness.

## Required Scope Statements

- Step 37 is controlled moving-wall application short-window envelope.
- Step 37 remains opt-in and experimental.
- Step 37 uses the existing `solid_vel` channel.
- Step 37 extends Step 36 from 5-step smoke to a 20-step short-window envelope.
- Step 37 does not change moving bounce-back formulas.
- Step 37 does not update LBM populations outside the existing bounce-back step.
- Step 37 does not change collision formulas.
- Step 37 does not change streaming formulas.
- Step 37 does not change projection formulas.
- Step 37 does not change MPM constitutive formulas.
- Step 37 does not change coupling formulas.
- Step 37 does not implement a jet model.
- Step 37 does not validate jet propulsion.
- Step 37 does not implement free-body motion.
- Step 37 does not implement squid swimming.
- Step 37 does not implement real squid validation.
- The default `boundary_motion_mode` remains static.
- The default `wall_velocity_application_mode` remains disabled.
- The default `quality_check_enabled` remains false.
- The default `quality_check_strict` remains false.
- The default `reaction_transfer_mode` remains engineering.

## Core Contract

Step 36 showed that a capped Step 35 wall-velocity diagnostic field can be applied through `lbm.solid_vel` in short 5-step opt-in smoke runs. Step 37 must test the same application path over a short 20-step envelope.

The Step 37 application hook is still the existing Step 36 driver hook:

1. `self.projector.project(self.solid, self.lbm)` updates `lbm.solid_vel`.
2. `_apply_wall_velocity_application_if_enabled()` optionally applies the Step 36 wall velocity field to `lbm.solid_vel`.
3. `step_moving_bounceback()` consumes `lbm.solid_vel`.

Step 37 may add report collection and envelope postprocessing. Step 37 must not alter the physics formula path.

The experimental application remains guarded by:

- `boundary_motion_mode == "prescribed_kinematic"`
- `wall_velocity_application_mode == "solid_vel_experimental"`
- `wall_velocity_application_config_path == "configs/step36_wall_velocity_application_solid_vel_experimental.json"`
- `wall_velocity_application_report_enabled == true`

The application remains capped and conservative:

- `wall_velocity_scale = 0.05`
- `wall_velocity_cap_lbm = 0.01`

## Explicit Non-Goals

Do not implement or claim:

- Default behavior change.
- Default wall velocity application.
- Unconditional prescribed kinematics.
- New wall velocity formula.
- Moving bounce-back formula change.
- Collision formula change.
- Streaming formula change.
- Projection formula change.
- MPM constitutive formula change.
- New coupling formula.
- `PenaltyFSICoupler3D` formula change.
- `MovingBoundaryFSICoupler3D` formula change.
- `LinkAreaMovingBoundaryCoupler3D` formula change.
- Jet model.
- Expelled-volume validation.
- Jet propulsion validation.
- Internal fluid cavity model.
- Free-body motion.
- Squid actuation claim.
- Squid swimming.
- Real squid validation.
- Production sharp-interface FSI.
- Two-phase flow.
- Contact-angle physics.
- Sparse storage.
- Edits under `external/taichi_LBM3D`.
- Raw real geometry or scan data.

Allowed Step 37 work:

- 20-step experimental application short-window runs.
- 20-step static/default short-window regression runs.
- Short-window envelope diagnostics.
- Static vs experimental envelope comparison.
- Engineering vs link-area envelope comparison.
- Wall velocity application timeseries aggregation.
- Mass, force, bounce-back, density, velocity, MPM, and projected-mass envelope summaries.
- Quality report aggregation.
- Step 36 regression guard.
- Small CSV/JSON/NPZ/log artifacts.
- Documentation and report files.
- Contract tests.

## Verification Matrix

Run only four primary 48^3 rows:

1. `48^3 static moving_boundary engineering, 20 steps`
2. `48^3 experimental moving_boundary engineering, 20 steps`
3. `48^3 static moving_boundary link_area_experimental, 20 steps`
4. `48^3 experimental moving_boundary link_area_experimental, 20 steps`

All four rows must use:

```json
{
  "n_grid": 48,
  "n_particles": 4096,
  "n_lbm_steps": 20,
  "mpm_substeps_per_lbm_step": 5,
  "output_interval": 1,
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
  "boundary_motion_config_path": null,
  "boundary_motion_report_enabled": false,
  "wall_velocity_application_mode": "disabled",
  "wall_velocity_application_config_path": null,
  "wall_velocity_application_report_enabled": false
}
```

## Configs To Add

Add:

- `configs/step37_static_48_moving_boundary.json`
- `configs/step37_experimental_48_moving_boundary.json`
- `configs/step37_static_48_link_area.json`
- `configs/step37_experimental_48_link_area.json`

Reuse:

- `configs/step36_wall_velocity_application_solid_vel_experimental.json`
- `configs/step34_boundary_motion_interface_prescribed_kinematic.json`
- `configs/step30_squid_proxy_geometry.json`

Do not add a new wall-velocity formula config.

## Source Files

Add:

- `src/wall_velocity_application_envelope.py`

Responsibilities:

- Collect per-step application reports from a case directory.
- Summarize application report envelopes.
- Summarize driver diagnostics envelopes.
- Compare static and experimental envelopes.
- Compare engineering and link-area envelopes.
- Write CSV/JSON envelope outputs.

Prefer using the existing Step 36 `driver.wall_velocity_application_reports` in runners to write:

- `wall_velocity_application_timeseries.csv`
- `wall_velocity_application_timeseries.json`

This is reporting only. It must not change solver formulas.

Suggested functions:

```python
def collect_wall_velocity_application_reports(case_dir) -> list[dict]:
    ...

def summarize_application_envelope(reports) -> dict:
    ...

def summarize_driver_stability_envelope(diagnostics_rows) -> dict:
    ...

def compare_static_experimental_envelopes(static_row, experimental_row) -> dict:
    ...

def compare_engineering_link_area_envelopes(engineering_row, link_area_row) -> dict:
    ...

def write_envelope_rows(rows, csv_path, json_path, summary=None) -> None:
    ...
```

Important fields:

- `case`
- `reaction_transfer_mode`
- `mode_class`
- `n_lbm_steps`
- `application_report_count`
- `applied_cell_count_min`
- `applied_cell_count_max`
- `max_applied_velocity_norm`
- `mean_applied_velocity_norm_max`
- `wall_velocity_cap_lbm`
- `lbm_population_update_count_max`
- `rho_min_global`
- `rho_max_global`
- `lbm_max_v_global`
- `mpm_min_J_global`
- `mpm_max_speed_global`
- `projected_mass_min`
- `projected_mass_max`
- `bb_max_correction_max`
- `hydro_force_max_norm`
- `stable`

## Baseline Runners

Add:

- `baseline_tests/step37_common.py`
- `baseline_tests/run_step37_application_window_driver.py`
- `baseline_tests/run_step37_application_envelope_summary.py`
- `baseline_tests/run_step37_static_vs_experimental_envelope.py`
- `baseline_tests/run_step37_engineering_vs_link_area_envelope.py`
- `baseline_tests/run_step37_mass_force_bounceback_envelope.py`
- `baseline_tests/run_step37_wall_velocity_timeseries_quality.py`
- `baseline_tests/run_step37_quality_report_aggregation.py`
- `baseline_tests/run_step37_step36_regression_guard.py`
- `baseline_tests/run_step37_artifact_manifest.py`

All runners must write stable success markers under `logs/step37_*.log`.

## Runner Acceptance

### Application Window Driver

Output:

- `outputs/step37_application_window_driver/application_window_results.csv`
- `outputs/step37_application_window_driver/application_window_results.json`
- `outputs/step37_application_window_driver/application_window_results.npz`
- `outputs/step37_application_window_driver/<case>/diagnostics_timeseries.csv`
- `outputs/step37_application_window_driver/<case>/wall_velocity_application_timeseries.csv`
- `outputs/step37_application_window_driver/<case>/wall_velocity_application_timeseries.json`
- `outputs/step37_application_window_driver/<case>/geometry_quality_report.json`
- `logs/step37_application_window_driver.log`

Accept:

- `row_count == 4`
- `stable_count == 4`
- `experimental_row_count == 2`
- `static_row_count == 2`
- `completed_lbm_steps >= 20`
- `total_mpm_substeps >= 100`
- `rho_min_global > 0.95`
- `rho_max_global < 1.05`
- `lbm_max_v_global < 0.1`
- `mpm_min_J_global > 0`
- `projected_mass_min > 0`
- `projected_mass_max > 0`
- `active_cell_count > 0`
- `bb_link_count_max > 0`
- `quality_pass == true`
- no NaN
- no Inf

Experimental rows additionally require:

- `application_report_count >= 20`
- `applied_cell_count_min > 0`
- `max_applied_velocity_norm <= configured cap`
- `lbm_population_update_count_max == 0`
- `modify_bounceback_formula == false`

### Application Envelope Summary

Output:

- `outputs/step37_application_envelope_summary/application_envelope.csv`
- `outputs/step37_application_envelope_summary/application_envelope.json`
- `logs/step37_application_envelope_summary.log`

Accept:

- `row_count == 2`
- each experimental row has `application_report_count >= 20`
- `applied_cell_count_min > 0`
- `applied_cell_count_max >= applied_cell_count_min`
- `max_applied_velocity_norm <= wall_velocity_cap_lbm`
- `mean_applied_velocity_norm_max` finite
- `application_envelope_pass == true`

### Static Vs Experimental Envelope

Compare:

- static moving-boundary engineering vs experimental moving-boundary engineering
- static link-area vs experimental link-area

Output:

- `outputs/step37_static_vs_experimental_envelope/static_vs_experimental_envelope.csv`
- `outputs/step37_static_vs_experimental_envelope/static_vs_experimental_envelope.json`
- `logs/step37_static_vs_experimental_envelope.log`

Accept:

- `row_count == 2`
- `comparison_pass == true`
- `both_stable == true`
- `rho_min_delta` finite
- `rho_max_delta` finite
- `lbm_max_v_delta` finite
- `mpm_min_J_delta` finite
- `projected_mass_delta` finite and bounded
- `active_cell_count_delta` bounded
- `bb_link_count_delta` bounded
- `experimental_applied_velocity_max > 0`

Do not require static and experimental rows to be identical.

### Engineering Vs Link-Area Envelope

Compare:

- experimental engineering vs experimental link-area

Output:

- `outputs/step37_engineering_vs_link_area_envelope/engineering_vs_link_area_envelope.csv`
- `outputs/step37_engineering_vs_link_area_envelope/engineering_vs_link_area_envelope.json`
- `logs/step37_engineering_vs_link_area_envelope.log`

Accept:

- `row_count == 1`
- `comparison_pass == true`
- `both_stable == true`
- `link_area_scale_final` finite
- `0.25 <= link_area_scale_final <= 2.0`
- `projected_mass_delta` finite and bounded
- rho/lbm/mpm metrics finite

### Mass Force Bounce-Back Envelope

Output:

- `outputs/step37_mass_force_bounceback_envelope/mass_force_bounceback_envelope.csv`
- `outputs/step37_mass_force_bounceback_envelope/mass_force_bounceback_envelope.json`
- `logs/step37_mass_force_bounceback_envelope.log`

Accept:

- `envelope_pass == true`
- `rho_min_global > 0.95`
- `rho_max_global < 1.05`
- `bb_max_correction_max` finite
- `hydro_force_max_norm` finite
- `max_grid_reaction_norm` finite
- `max_applied_velocity_norm <= cap`
- no NaN
- no Inf

### Wall Velocity Timeseries Quality

Output:

- `outputs/step37_wall_velocity_timeseries_quality/wall_velocity_timeseries_quality.csv`
- `outputs/step37_wall_velocity_timeseries_quality/wall_velocity_timeseries_quality.json`
- `logs/step37_wall_velocity_timeseries_quality.log`

Accept:

- `row_count == 2`
- each experimental row has `timeseries_row_count >= 20`
- `applied_cell_count_min > 0`
- applied velocity norms finite
- `cap_pass == true`
- `repeatable_phase_sequence == true`
- `lbm_population_update_count_max == 0`

### Quality Report Aggregation

Output:

- `outputs/step37_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step37_quality_report_aggregation/quality_report_summary.json`
- `logs/step37_quality_report_aggregation.log`

Accept:

- `quality_report_count == 4`
- `pass_count == 4`
- `strict_count == 4`
- `warning_count == 0`
- `error_count == 0`

### Step 36 Regression Guard

Input:

- `STEP36_CONTROLLED_MOVING_WALL_BOUNCEBACK_VELOCITY_APPLICATION_SMOKE_REPORT.md`
- `outputs/step36_experimental_application_smoke/experimental_application_results.json`
- `outputs/step36_wall_velocity_application_quality/application_quality.json`
- `outputs/step36_step35_regression_guard/step35_regression_guard.json`
- `outputs/step36_artifact_manifest/artifact_summary.json`

Accept:

- Step 36 report exists.
- Step 36 experimental row count is 3.
- Step 36 experimental stable count is 3.
- Step 36 application quality passes.
- Step 36 large file count is 0.
- Step 36 VTR count is 0.
- Step 36 particle NPY count is 0.

### Artifact Manifest

Output:

- `outputs/step37_artifact_manifest/artifact_manifest.csv`
- `outputs/step37_artifact_manifest/artifact_summary.csv`
- `outputs/step37_artifact_manifest/artifact_summary.json`
- `logs/step37_artifact_manifest.log`

Accept:

- `large_file_count == 0`
- `step37_total_size_mb < 20`
- `total_size_mb < 230`
- `step37_vtr_count == 0`
- `step37_particle_npy_count == 0`
- `raw_candidate_large_file_count == 0`
- `scan_data_file_count == 0`
- `private_absolute_path_count == 0`

## Contract Test

Add:

- `tests/test_step37_wall_velocity_application_envelope_contract.py`

Required tests:

- `test_step37_required_artifacts_exist`
- `test_step37_driver_configs_are_valid`
- `test_step37_application_window_driver_is_valid`
- `test_step37_application_envelope_summary_is_valid`
- `test_step37_static_vs_experimental_envelope_is_valid`
- `test_step37_engineering_vs_link_area_envelope_is_valid`
- `test_step37_mass_force_bounceback_envelope_is_valid`
- `test_step37_wall_velocity_timeseries_quality_is_valid`
- `test_step37_quality_report_aggregation_is_valid`
- `test_step37_step36_regression_guard_is_valid`
- `test_step37_default_modes_remain_unchanged`
- `test_step37_docs_scope_and_forbidden_claims_are_valid`
- `test_step37_artifact_budget_is_valid`
- `test_step37_report_acceptance_complete`

Required scope phrases:

- Step 37 is controlled moving-wall application short-window envelope.
- Step 37 remains opt-in and experimental.
- Step 37 uses the existing solid_vel channel.
- Step 37 does not change moving bounce-back formulas.
- Step 37 does not implement a jet model.
- Step 37 does not implement squid swimming.
- Step 37 does not implement real squid validation.
- The default boundary_motion_mode remains static.
- The default wall_velocity_application_mode remains disabled.

Forbidden claims:

- `squid swimming is implemented`
- `real squid simulation is validated`
- `production-ready sharp-interface FSI`
- `final solver readiness`
- `jet model is implemented`
- `jet propulsion is validated`
- `free-body motion is implemented`
- `two-phase flow is implemented`
- `contact angle physics is implemented`
- `moving bounce-back formula is changed`
- `default wall velocity application is enabled`

## Documentation

Add:

- `docs/37_controlled_moving_wall_application_short_window_envelope.md`
- `STEP37_CONTROLLED_MOVING_WALL_APPLICATION_SHORT_WINDOW_ENVELOPE_REPORT.md`

Report sections:

- `## 1. Goal`
- `## 2. Files Created And Updated`
- `## 3. Explicit Non-Goals`
- `## 4. Application Window Driver`
- `## 5. Application Envelope Summary`
- `## 6. Static Vs Experimental Envelope`
- `## 7. Engineering Vs Link-Area Envelope`
- `## 8. Mass Force Bounce-Back Envelope`
- `## 9. Wall Velocity Timeseries Quality`
- `## 10. Quality Report Aggregation`
- `## 11. Step 36 Regression Guard`
- `## 12. Artifact Manifest Summary`
- `## 13. Verification Commands`
- `## 14. GitHub Sync Information`
- `## 15. Acceptance Checklist`
- `## 16. Decision For Step 38`

## Verification Commands

Use:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\wall_velocity_application_envelope.py baseline_tests\step37_common.py baseline_tests\run_step37_application_window_driver.py baseline_tests\run_step37_application_envelope_summary.py baseline_tests\run_step37_static_vs_experimental_envelope.py baseline_tests\run_step37_engineering_vs_link_area_envelope.py baseline_tests\run_step37_mass_force_bounceback_envelope.py baseline_tests\run_step37_wall_velocity_timeseries_quality.py baseline_tests\run_step37_quality_report_aggregation.py baseline_tests\run_step37_step36_regression_guard.py baseline_tests\run_step37_artifact_manifest.py tests\test_step37_wall_velocity_application_envelope_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_application_window_driver.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_application_envelope_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_static_vs_experimental_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_engineering_vs_link_area_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_mass_force_bounceback_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_wall_velocity_timeseries_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_step36_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step37_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q *> logs\step37_pytest.log
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step37_wall_velocity_application_envelope_contract.py -q

git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Trusted full pytest output must be recorded in:

- `logs/step37_pytest.log`

## Acceptance Checklist

- [ ] Step 37 detailed goal file exists.
- [ ] Application window driver runs 4 rows.
- [ ] Static engineering row passes.
- [ ] Experimental engineering row passes.
- [ ] Static link-area row passes.
- [ ] Experimental link-area row passes.
- [ ] All rows complete at least 20 LBM steps.
- [ ] All rows complete at least 100 MPM substeps.
- [ ] Experimental rows write wall velocity application timeseries.
- [ ] Experimental applied cell count is positive.
- [ ] Max applied velocity norm is within the configured cap.
- [ ] `rho_min_global > 0.95`.
- [ ] `rho_max_global < 1.05`.
- [ ] `lbm_max_v_global < 0.1`.
- [ ] `mpm_min_J_global > 0`.
- [ ] `projected_mass_min > 0`.
- [ ] `projected_mass_max > 0`.
- [ ] `active_cell_count > 0`.
- [ ] `bb_link_count_max > 0`.
- [ ] Hydro force diagnostics are finite.
- [ ] Bounce-back correction diagnostics are finite.
- [ ] No NaN.
- [ ] No Inf.
- [ ] Static vs experimental envelope passes.
- [ ] Engineering vs link-area envelope passes.
- [ ] Mass/force/bounce-back envelope passes.
- [ ] Wall velocity timeseries quality passes.
- [ ] Quality report aggregation passes.
- [ ] Step 36 regression guard passes.
- [ ] Default `boundary_motion_mode` remains static.
- [ ] Default `wall_velocity_application_mode` remains disabled.
- [ ] Default `quality_check_enabled` remains false.
- [ ] Default `quality_check_strict` remains false.
- [ ] Default `reaction_transfer_mode` remains engineering.
- [ ] No default behavior change.
- [ ] No moving bounce-back formula changes.
- [ ] No LBM collision formula changes.
- [ ] No MPM constitutive formula changes.
- [ ] No projection formula changes.
- [ ] No `external/taichi_LBM3D` edits.
- [ ] No jet model claim.
- [ ] No squid swimming claim.
- [ ] No real squid validation claim.
- [ ] No Step 37 `.vtr` outputs.
- [ ] No Step 37 particle `.npy` outputs.
- [ ] Artifact large file count is 0.
- [ ] Step 37 output total-size budget passes.
- [ ] Repo artifact summary `total_size_mb < 230`.
- [ ] `logs/step37_pytest.log` exists.
- [ ] Full pytest passes.
- [ ] Step 37 contract test passes.
- [ ] `git diff --check` passes.
- [ ] Staged whitespace check passes.
- [ ] Pre-push hook passes.
- [ ] Step 37 artifacts are pushed to `origin/main`.

## Commit And Push

Commit message:

```text
test: add step37 wall velocity application envelope
```

Push target:

```text
origin/main
```

If the local commit hook fails with the known Windows `/usr/bin/env: bash: Permission denied` problem, use `git commit --no-verify`, then still run a normal `git push origin main` so the ECC pre-push verification gate runs.

## Step 38 Direction

If Step 37 passes, Step 38 may be:

```text
Step 38 Controlled Tethered Jet-Cycle Diagnostics Prototype
```

Step 38 must still avoid real jet validation, squid swimming, and free-body claims unless later evidence supports them.
