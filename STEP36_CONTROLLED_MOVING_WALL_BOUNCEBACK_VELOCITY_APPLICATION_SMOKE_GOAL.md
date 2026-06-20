# Step 36 Goal: Controlled Moving-Wall Bounce-Back Velocity Application Smoke

## Objective

Implement Step 36 as a controlled moving-wall bounce-back velocity application smoke. Step 36 is the first opt-in bridge from the accepted Step 35 moving-wall velocity diagnostics into the existing LBM `solid_vel` wall-velocity channel. It must remain guarded, experimental, short-step, and artifact-backed.

Step 36 applies wall velocity only through the existing `solid_vel` channel. Step 36 does not change moving bounce-back formulas, collision formulas, streaming formulas, projection formulas, MPM constitutive formulas, or FSI coupler formulas. Step 36 must preserve static/default behavior and must not claim jet model, actuation, squid swimming, real squid validation, production readiness, or final solver readiness.

## Required Scope Statements

- Step 36 is controlled moving-wall bounce-back velocity application smoke.
- Step 36 is opt-in and experimental.
- Step 36 applies wall velocity only through the existing solid_vel channel.
- Step 36 does not change moving bounce-back formulas.
- Step 36 does not update LBM populations outside the existing bounce-back step.
- Step 36 does not implement a jet model.
- Step 36 does not implement squid swimming.
- Step 36 does not implement real squid validation.
- The default boundary_motion_mode remains static.
- The default wall_velocity_application_mode remains disabled.
- The default quality_check_enabled remains false.
- The default quality_check_strict remains false.
- The default reaction_transfer_mode remains engineering.

## Core Contract

Step 35 proved that moving-wall velocity diagnostics can be generated without application. Step 36 may apply those diagnostics only when all opt-in guards are enabled:

- `boundary_motion_mode == "prescribed_kinematic"`
- `wall_velocity_application_mode == "solid_vel_experimental"`
- `wall_velocity_application_config_path` points to a valid Step 36 application config
- `wall_velocity_application_report_enabled == true`

The application hook must run after projection updates `lbm.solid_vel` and before `step_moving_bounceback()` consumes `lbm.solid_vel`.

The application must be capped and conservative:

- `wall_velocity_scale = 0.05`
- `wall_velocity_cap_lbm = 0.01`

The purpose is to verify the application path is stable and measurable. It is not a propulsion model.

## Explicit Non-Goals

Do not implement or claim:

- Default behavior change.
- Unconditional wall velocity application.
- Moving bounce-back formula change.
- Collision formula change.
- Streaming formula change.
- New coupling formula.
- `PenaltyFSICoupler3D` formula change.
- `MovingBoundaryFSICoupler3D` formula change.
- `LinkAreaMovingBoundaryCoupler3D` formula change.
- MPM constitutive formula change.
- Projection formula change.
- Jet model.
- Internal fluid cavity model.
- Free-body motion.
- Squid swimming.
- Real squid validation.
- Production sharp-interface FSI.
- Two-phase flow.
- Contact-angle physics.
- Sparse storage.
- Edits under `external/taichi_LBM3D`.
- Raw real geometry or scan data.

Allowed Step 36 work:

- Opt-in `wall_velocity_application_mode` config fields.
- Experimental write into `lbm.solid_vel`.
- Wall velocity application config validation.
- Wall velocity application report generation.
- Short 32^3 and 48^3 moving-boundary smoke baselines.
- Static/no-op regression comparisons.
- Bounce-back correction, force, mass, density, velocity, and stability diagnostics.
- Quality report aggregation.
- Step 35 regression guard.
- Small CSV/JSON/NPZ/log artifacts.

## Source Changes

### `src/fsi_config.py`

Add:

```python
VALID_WALL_VELOCITY_APPLICATION_MODES = (
    "disabled",
    "solid_vel_experimental",
)

wall_velocity_application_mode: str = "disabled"
wall_velocity_application_config_path: Optional[str] = None
wall_velocity_application_report_enabled: bool = False
```

Validation rules:

- `wall_velocity_application_mode` must be one of the valid modes.
- Disabled mode must require `wall_velocity_application_config_path is None`.
- `solid_vel_experimental` mode must require `boundary_motion_mode == "prescribed_kinematic"`.
- `solid_vel_experimental` mode must require `wall_velocity_application_config_path` to be present.
- Default `boundary_motion_mode` remains `"static"`.
- Default `wall_velocity_application_mode` remains `"disabled"`.
- Default quality and reaction-transfer fields remain unchanged.

### `src/wall_velocity_application_config.py`

Add an immutable config object:

```python
@dataclass(frozen=True)
class WallVelocityApplicationConfig:
    application_id: str
    wall_velocity_config_path: str
    boundary_motion_config_path: str
    geometry_config_path: str
    region_config_path: str
    application_mode: str = "solid_vel_experimental"
    target_lbm_field: str = "solid_vel"
    application_policy: str = "additive_capped"
    wall_velocity_scale: float = 0.05
    wall_velocity_cap_lbm: float = 0.01
    apply_to_lbm_solid_vel: bool = True
    apply_to_lbm_populations: bool = False
    apply_to_mpm: bool = False
    apply_to_projector: bool = False
    modify_bounceback_formula: bool = False
    jet_model_enabled: bool = False
    actuation_claim_enabled: bool = False
    diagnostic_report_enabled: bool = True
```

Validation requirements:

- Required source paths exist.
- `application_mode == "solid_vel_experimental"`.
- `target_lbm_field == "solid_vel"`.
- `application_policy in {"additive_capped", "replace_capped"}`.
- `0 < wall_velocity_scale <= 1`.
- `0 < wall_velocity_cap_lbm <= 0.05`.
- `apply_to_lbm_solid_vel == true`.
- `apply_to_lbm_populations == false`.
- `apply_to_mpm == false`.
- `apply_to_projector == false`.
- `modify_bounceback_formula == false`.
- `jet_model_enabled == false`.
- `actuation_claim_enabled == false`.
- `diagnostic_report_enabled == true`.

### `src/wall_velocity_application.py`

Responsibilities:

- Load and validate Step 36 application config.
- Reuse Step 35 wall velocity generation.
- Build a grid-shaped wall velocity array for a requested `n_grid` and phase.
- Apply capped velocity to `lbm.solid_vel` only.
- Preserve all LBM populations outside the existing bounce-back step.
- Write an application report.

Suggested functions:

```python
def load_wall_velocity_application_config(path) -> WallVelocityApplicationConfig:
    ...

def build_wall_velocity_grid(application_config, n_grid, phase) -> np.ndarray:
    ...

def apply_wall_velocity_to_lbm_solid_vel(lbm, velocity_grid, scale, cap) -> dict:
    ...

def summarize_wall_velocity_application(lbm, velocity_grid, before_solid_vel_stats, after_solid_vel_stats) -> dict:
    ...

def write_wall_velocity_application_report(report, path) -> None:
    ...
```

Implementation strategy:

1. Read Step 35 wall velocity rows or regenerate them from Step 35 config.
2. Choose the nearest available Step 35 phase for the current driver phase.
3. Build a deterministic grid velocity field using the same Step 30 region masks.
4. Apply `wall_velocity_scale` and cap `||u_wall|| <= wall_velocity_cap_lbm`.
5. Apply to `lbm.solid_vel` using `application_policy`.
6. Record before/after stats, applied cell count, max applied norm, cap pass, and forbidden flags.

### `src/fsi_driver.py`

Add a guarded hook after projection and before moving bounce-back:

```python
def _project(self):
    ...
    self.projector.project(self.solid, self.lbm)
    self._apply_wall_velocity_application_if_enabled()
```

The hook must be no-op unless:

- `boundary_motion_mode == "prescribed_kinematic"`
- `wall_velocity_application_mode == "solid_vel_experimental"`

When enabled, it must write `wall_velocity_application_report.json` if reporting is enabled.

### Formula Boundaries

Do not modify the moving bounce-back correction formula. Step 36 must reuse the existing path where moving bounce-back reads `self.solid_vel[ip]`.

## Config Files

Add:

- `configs/step36_wall_velocity_application_solid_vel_experimental.json`
- `configs/step36_static_32_moving_boundary.json`
- `configs/step36_experimental_32_moving_boundary.json`
- `configs/step36_static_48_moving_boundary.json`
- `configs/step36_experimental_48_moving_boundary.json`
- `configs/step36_static_48_link_area.json`
- `configs/step36_experimental_48_link_area.json`

Application config:

```json
{
  "application_id": "step36_wall_velocity_solid_vel_experimental",
  "wall_velocity_config_path": "configs/step35_squid_proxy_wall_velocity_field.json",
  "boundary_motion_config_path": "configs/step34_boundary_motion_interface_prescribed_kinematic.json",
  "geometry_config_path": "configs/step30_squid_proxy_geometry.json",
  "region_config_path": "configs/step30_squid_proxy_region_config.json",
  "application_mode": "solid_vel_experimental",
  "target_lbm_field": "solid_vel",
  "application_policy": "additive_capped",
  "wall_velocity_scale": 0.05,
  "wall_velocity_cap_lbm": 0.01,
  "apply_to_lbm_solid_vel": true,
  "apply_to_lbm_populations": false,
  "apply_to_mpm": false,
  "apply_to_projector": false,
  "modify_bounceback_formula": false,
  "jet_model_enabled": false,
  "actuation_claim_enabled": false,
  "diagnostic_report_enabled": true,
  "scope_note": "Step 36 opt-in experimental solid_vel application smoke only"
}
```

Driver config constraints:

- `geometry_type = "squid_proxy"`.
- `geometry_config_path = "configs/step30_squid_proxy_geometry.json"`.
- `coupling_mode = "moving_boundary"`.
- `n_particles = 4096`.
- `n_lbm_steps = 5`.
- `mpm_substeps_per_lbm_step = 5`.
- `output_interval = 1`.
- `quality_check_enabled = true`.
- `quality_check_strict = true`.
- `write_vtk = false`.
- `write_particles = false`.

Static rows:

- `boundary_motion_mode = "static"`.
- `wall_velocity_application_mode = "disabled"`.
- `wall_velocity_application_config_path = null`.
- `wall_velocity_application_report_enabled = false`.

Experimental rows:

- `boundary_motion_mode = "prescribed_kinematic"`.
- `boundary_motion_config_path = "configs/step34_boundary_motion_interface_prescribed_kinematic.json"`.
- `boundary_motion_report_enabled = true`.
- `wall_velocity_application_mode = "solid_vel_experimental"`.
- `wall_velocity_application_config_path = "configs/step36_wall_velocity_application_solid_vel_experimental.json"`.
- `wall_velocity_application_report_enabled = true`.

## Baseline Runner Contract

Add:

- `baseline_tests/step36_common.py`
- `baseline_tests/run_step36_wall_velocity_application_config_validation.py`
- `baseline_tests/run_step36_wall_velocity_application_report.py`
- `baseline_tests/run_step36_static_regression_smoke.py`
- `baseline_tests/run_step36_experimental_application_smoke.py`
- `baseline_tests/run_step36_static_vs_experimental_comparison.py`
- `baseline_tests/run_step36_mass_force_stability_diagnostics.py`
- `baseline_tests/run_step36_wall_velocity_application_quality.py`
- `baseline_tests/run_step36_quality_report_aggregation.py`
- `baseline_tests/run_step36_step35_regression_guard.py`
- `baseline_tests/run_step36_artifact_manifest.py`

All runners must write stable success markers under `logs/step36_*.log`.

### Application Config Validation

Outputs:

- `outputs/step36_wall_velocity_application_config_validation/application_config_validation.csv`
- `outputs/step36_wall_velocity_application_config_validation/application_config_validation.json`
- `logs/step36_wall_velocity_application_config_validation.log`

Acceptance:

- `validation_pass == true`
- `application_mode == "solid_vel_experimental"`
- `target_lbm_field == "solid_vel"`
- `application_policy == "additive_capped"`
- `0 < wall_velocity_scale <= 1`
- `0 < wall_velocity_cap_lbm <= 0.05`
- `apply_to_lbm_solid_vel == true`
- `apply_to_lbm_populations == false`
- `apply_to_mpm == false`
- `apply_to_projector == false`
- `modify_bounceback_formula == false`
- `jet_model_enabled == false`
- `actuation_claim_enabled == false`

### Application Report

Outputs:

- `outputs/step36_wall_velocity_application_report/application_report.json`
- `outputs/step36_wall_velocity_application_report/application_report_summary.csv`
- `logs/step36_wall_velocity_application_report.log`

Acceptance:

- Report exists.
- `wall_velocity_row_count == 63`
- `grid_size_count == 3`
- `phase_sample_count == 7`
- Application scale is finite.
- Velocity cap is finite.
- Uncapped velocity norm is finite.
- Capped velocity norm is `<= wall_velocity_cap_lbm`.
- `lbm_population_update_enabled == false`
- `modify_bounceback_formula == false`

### Static Regression Smoke

Runs:

- 32 moving-boundary engineering static.
- 48 moving-boundary engineering static.
- 48 moving-boundary link-area static.

Outputs:

- `outputs/step36_static_regression_smoke/static_regression_results.csv`
- `outputs/step36_static_regression_smoke/static_regression_results.json`
- `outputs/step36_static_regression_smoke/static_regression_results.npz`
- `logs/step36_static_regression_smoke.log`

Acceptance:

- `row_count == 3`
- `stable_count == 3`
- `wall_velocity_application_mode == "disabled"`
- `rho_min > 0.95`
- `rho_max < 1.05`
- `lbm_max_v < 0.1`
- `mpm_min_J > 0`
- `projected_mass > 0`
- `active_cell_count > 0`
- `quality_pass == true`

### Experimental Application Smoke

Runs:

- 32 moving-boundary engineering experimental.
- 48 moving-boundary engineering experimental.
- 48 moving-boundary link-area experimental.

Outputs:

- `outputs/step36_experimental_application_smoke/experimental_application_results.csv`
- `outputs/step36_experimental_application_smoke/experimental_application_results.json`
- `outputs/step36_experimental_application_smoke/experimental_application_results.npz`
- `outputs/step36_experimental_application_smoke/<case>/wall_velocity_application_report.json`
- `logs/step36_experimental_application_smoke.log`

Acceptance:

- `row_count == 3`
- `stable_count == 3`
- `wall_velocity_application_mode == "solid_vel_experimental"`
- `application_report_count == 3`
- `applied_cell_count > 0`
- `max_applied_velocity_norm <= wall_velocity_cap_lbm`
- `lbm_population_update_count == 0`
- `modify_bounceback_formula == false`
- `rho_min > 0.95`
- `rho_max < 1.05`
- `lbm_max_v < 0.1`
- `mpm_min_J > 0`
- `projected_mass > 0`
- `active_cell_count > 0`
- no NaN
- no Inf

### Static Vs Experimental Comparison

Outputs:

- `outputs/step36_static_vs_experimental_comparison/static_vs_experimental.csv`
- `outputs/step36_static_vs_experimental_comparison/static_vs_experimental.json`
- `logs/step36_static_vs_experimental_comparison.log`

Acceptance:

- `row_count == 3`
- `comparison_pass == true`
- `both_stable == true`
- density, velocity, MPM, and force diagnostics finite
- experimental differs in at least one wall-velocity diagnostic
- `active_cell_count_delta == 0`
- `projected_mass_delta <= 1e-4`
- `bb_link_count_delta <= 1024`
- `max_applied_velocity_norm > 0`

### Mass And Force Stability Diagnostics

Outputs:

- `outputs/step36_mass_force_stability_diagnostics/mass_force_stability.csv`
- `outputs/step36_mass_force_stability_diagnostics/mass_force_stability.json`
- `logs/step36_mass_force_stability_diagnostics.log`

Acceptance:

- `diagnostic_pass == true`
- `rho_min_global > 0.95`
- `rho_max_global < 1.05`
- hydro force diagnostics finite
- bounce-back correction diagnostics finite
- `bb_link_count > 0`
- `max_applied_velocity_norm <= cap`
- no NaN
- no Inf

### Wall Velocity Application Quality

Outputs:

- `outputs/step36_wall_velocity_application_quality/application_quality.csv`
- `outputs/step36_wall_velocity_application_quality/application_quality.json`
- `logs/step36_wall_velocity_application_quality.log`

Acceptance:

- `application_report_count == 3`
- `applied_cell_count_min > 0`
- `max_applied_velocity_norm <= cap`
- uncapped velocity norm finite
- capped velocity norm finite
- `application_quality_pass == true`

### Quality Report Aggregation

Outputs:

- `outputs/step36_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step36_quality_report_aggregation/quality_report_summary.json`
- `logs/step36_quality_report_aggregation.log`

Acceptance:

- `quality_report_count == 6`
- `pass_count == 6`
- `strict_count == 6`
- `warning_count == 0`
- `error_count == 0`

### Step 35 Regression Guard

Inputs:

- `STEP35_CONTROLLED_SQUID_PROXY_MOVING_WALL_VELOCITY_FIELD_DIAGNOSTIC_REPORT.md`
- `outputs/step35_wall_velocity_field/wall_velocity_field.json`
- `outputs/step35_no_lbm_update_guard/no_lbm_update_guard.json`
- `outputs/step35_artifact_manifest/artifact_summary.json`

Acceptance:

- Step 35 report exists.
- Step 35 wall velocity `row_count == 63`.
- Step 35 no-LBM-update guard passes.
- Step 35 `large_file_count == 0`.
- Step 35 `.vtr` count is `0`.
- Step 35 particle `.npy` count is `0`.

### Artifact Manifest

Acceptance:

- `large_file_count == 0`
- `step36_total_size_mb < 15`
- `total_size_mb < 220`
- `step36_vtr_count == 0`
- `step36_particle_npy_count == 0`
- `raw_candidate_large_file_count == 0`
- `scan_data_file_count == 0`
- `private_absolute_path_count == 0`

## Test Contract

Add `tests/test_step36_moving_wall_bounceback_application_contract.py` with:

- `test_step36_required_artifacts_exist`
- `test_step36_config_defaults_are_safe`
- `test_step36_application_config_validation_is_valid`
- `test_step36_application_report_is_valid`
- `test_step36_static_regression_smoke_is_valid`
- `test_step36_experimental_application_smoke_is_valid`
- `test_step36_static_vs_experimental_comparison_is_valid`
- `test_step36_mass_force_stability_diagnostics_are_valid`
- `test_step36_wall_velocity_application_quality_is_valid`
- `test_step36_quality_report_aggregation_is_valid`
- `test_step36_step35_regression_guard_is_valid`
- `test_step36_default_modes_remain_unchanged`
- `test_step36_docs_scope_and_forbidden_claims_are_valid`
- `test_step36_artifact_budget_is_valid`
- `test_step36_report_acceptance_complete`

Forbidden claims:

- `squid swimming is implemented`
- `real squid simulation is validated`
- `production-ready sharp-interface FSI`
- `final solver readiness`
- `jet model is validated`
- `free-body motion is implemented`
- `two-phase flow is implemented`
- `contact angle physics is implemented`
- `moving bounce-back formula is changed`
- `default wall velocity application is enabled`

Required scope phrases:

- `Step 36 is controlled moving-wall bounce-back velocity application smoke.`
- `Step 36 is opt-in and experimental.`
- `Step 36 applies wall velocity only through the existing solid_vel channel.`
- `Step 36 does not change moving bounce-back formulas.`
- `Step 36 does not update LBM populations outside the existing bounce-back step.`
- `Step 36 does not implement a jet model.`
- `Step 36 does not implement squid swimming.`
- `Step 36 does not implement real squid validation.`
- `The default boundary_motion_mode remains static.`
- `The default wall_velocity_application_mode remains disabled.`

## Documentation And Report Contract

Add:

- `docs/36_controlled_moving_wall_bounceback_velocity_application_smoke.md`
- `STEP36_CONTROLLED_MOVING_WALL_BOUNCEBACK_VELOCITY_APPLICATION_SMOKE_REPORT.md`

The report must contain:

1. Goal
2. Files Created And Updated
3. Explicit Non-Goals
4. Wall Velocity Application Config Validation
5. Wall Velocity Application Report
6. Static Regression Smoke
7. Experimental Application Smoke
8. Static Vs Experimental Comparison
9. Mass And Force Stability Diagnostics
10. Wall Velocity Application Quality
11. Quality Report Aggregation
12. Step 35 Regression Guard
13. Artifact Manifest Summary
14. Verification Commands
15. GitHub Sync Information
16. Acceptance Checklist
17. Decision For Step 37

## Verification Contract

Run and capture:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\wall_velocity_application_config.py src\wall_velocity_application.py src\fsi_config.py src\fsi_driver.py baseline_tests\step36_common.py baseline_tests\run_step36_wall_velocity_application_config_validation.py baseline_tests\run_step36_wall_velocity_application_report.py baseline_tests\run_step36_static_regression_smoke.py baseline_tests\run_step36_experimental_application_smoke.py baseline_tests\run_step36_static_vs_experimental_comparison.py baseline_tests\run_step36_mass_force_stability_diagnostics.py baseline_tests\run_step36_wall_velocity_application_quality.py baseline_tests\run_step36_quality_report_aggregation.py baseline_tests\run_step36_step35_regression_guard.py baseline_tests\run_step36_artifact_manifest.py tests\test_step36_moving_wall_bounceback_application_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_wall_velocity_application_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_wall_velocity_application_report.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_static_regression_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_experimental_application_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_static_vs_experimental_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_mass_force_stability_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_wall_velocity_application_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_step35_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step36_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q *> logs\step36_pytest.log
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step36_moving_wall_bounceback_application_contract.py -q

git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

The trusted full pytest result must be recorded in `logs/step36_pytest.log`.

## Acceptance Checklist

- [ ] Wall velocity application config validation passes.
- [ ] Default `wall_velocity_application_mode` is disabled.
- [ ] Application mode is opt-in experimental.
- [ ] Target field is `solid_vel`.
- [ ] Application policy is capped.
- [ ] Velocity cap is finite and conservative.
- [ ] `apply_to_lbm_solid_vel` is true only in experimental config.
- [ ] `apply_to_lbm_populations` is false.
- [ ] `apply_to_mpm` is false.
- [ ] `apply_to_projector` is false.
- [ ] `modify_bounceback_formula` is false.
- [ ] `jet_model_enabled` is false.
- [ ] Static regression smoke passes.
- [ ] Experimental application smoke passes.
- [ ] Every experimental row writes `wall_velocity_application_report.json`.
- [ ] Applied cell count is positive.
- [ ] Max applied velocity norm is `<=` configured cap.
- [ ] Static vs experimental comparison passes.
- [ ] Experimental rows remain stable.
- [ ] `rho_min > 0.95`.
- [ ] `rho_max < 1.05`.
- [ ] `lbm_max_v < 0.1`.
- [ ] `mpm_min_J > 0`.
- [ ] `projected_mass > 0`.
- [ ] `active_cell_count > 0`.
- [ ] Hydro force diagnostics are finite.
- [ ] `bb_max_correction` is finite.
- [ ] `bb_link_count > 0`.
- [ ] No NaN.
- [ ] No Inf.
- [ ] Quality report aggregation passes.
- [ ] Step 35 regression guard passes.
- [ ] Default `boundary_motion_mode` remains static.
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
- [ ] No Step 36 `.vtr` outputs.
- [ ] No Step 36 particle `.npy` outputs.
- [ ] Artifact `large_file_count == 0`.
- [ ] Step 36 output total-size budget passes.
- [ ] Repo artifact summary `total_size_mb < 220`.
- [ ] `logs/step36_pytest.log` exists.
- [ ] Full pytest passes.
- [ ] Step 36 contract test passes.
- [ ] `git diff --check` passes.
- [ ] Staged whitespace check passes.
- [ ] Pre-push hook passes.
- [ ] Step 36 artifacts are pushed to `origin/main`.

## Commit Contract

Use:

```text
test: add step36 moving wall bounceback application smoke
```

Push target:

```text
origin/main
```

## Step 37 Direction

If Step 36 is stable, Step 37 may be `Controlled Moving-Wall Application Short-Window Envelope`: extend the Step 36 5-step smoke to a 10-20 step envelope, still focused on stability and force diagnostics. Do not claim jet model or swimming.
