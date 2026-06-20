# Step 33 Controlled Squid Proxy Kinematics Mapping Goal

## 1. Name

Step 33 Controlled Squid Proxy Kinematics Mapping To Boundary-Motion Diagnostics

Short scope statement:

Step 33 maps the accepted Step 32 prescribed kinematics schedule to squid proxy region displacement and velocity diagnostics only. Step 33 does not integrate kinematics into `FSIDriver3D`, does not apply moving wall velocity to LBM, does not implement a jet model, does not drive mantle contraction or funnel actuation in simulation, does not implement squid swimming, and does not add new FSI physics.

## 2. Starting Point

Step 32 is accepted on GitHub. It provides:

- a deterministic schedule config at `configs/step32_squid_proxy_kinematics_schedule.json`;
- 81 inclusive phase samples over `[0, 1]`;
- mantle radius scale range `[0.85, 1.0]`;
- mantle cavity volume proxy scale range `[0.6, 1.0]`;
- funnel aperture proxy scale range `[0.35, 1.0]`;
- finite first-derivative diagnostics;
- repeatability hashes for schedule, mantle, cavity, and funnel values;
- region mapping validation against the accepted Step 30 regions;
- a Step 31 regression guard;
- artifact manifest evidence with no large files, no `.vtr`, no particle `.npy`, no scan data, and no private absolute paths;
- explicit scope that schedule rows are diagnostics only and driver integration remains out of scope.

Step 33 should build the next bridge from schedule rows to region-level motion diagnostics:

- map `mantle_outer` to radial displacement and velocity proxy diagnostics;
- map `mantle_cavity_proxy` to volume scale and volume-rate proxy diagnostics;
- map `funnel_outlet_proxy` to aperture scale and aperture-rate proxy diagnostics;
- summarize motion proxy coverage at 32^3, 48^3, and 64^3 diagnostic grids;
- prove the motion rows remain consistent with the accepted Step 32 schedule;
- preserve all Step 32 and default-mode safety boundaries.

## 3. Non-Negotiable Boundaries

Step 33 must not implement or claim any of the following:

- `FSIDriver3D` integration;
- LBM moving wall velocity integration;
- moving wall velocity applied to LBM;
- boundary velocity applied to fluid;
- moving bounce-back formula changes;
- mantle contraction in the driver;
- funnel actuation in the driver;
- jet model;
- fluid forcing from kinematics;
- free-body motion;
- squid swimming;
- implemented squid actuation;
- real squid validation;
- new FSI physics;
- new coupling formula;
- changes to `PenaltyFSICoupler3D`;
- changes to `MovingBoundaryFSICoupler3D`;
- changes to `LinkAreaMovingBoundaryCoupler3D`;
- changes to LBM step formulas;
- changes to MPM constitutive formulas;
- changes to projection formulas;
- production sharp-interface FSI;
- final solver readiness;
- production mesh repair;
- automatic remeshing;
- two-phase flow;
- contact-angle physics;
- sparse storage;
- edits to `external/taichi_LBM3D`;
- committed raw scan data;
- committed large raw real geometry.

Step 33 is allowed to implement:

- immutable motion mapping config dataclass;
- motion mapping config validation;
- deterministic schedule-to-region diagnostic rows;
- mantle radial displacement and velocity proxies;
- cavity volume and volume-rate proxies;
- funnel aperture and aperture-rate proxies;
- motion quality checks;
- motion repeatability hashes;
- grid coverage diagnostics at 32^3, 48^3, and 64^3;
- schedule-motion consistency checks against Step 32;
- Step 32 regression guard;
- artifact manifest and small committed outputs;
- docs, report, logs, and contract tests.

## 4. Required Source Files

Create:

- `src/squid_motion_mapping_config.py`
- `src/squid_motion_mapping.py`
- `src/squid_motion_quality.py`
- `src/squid_motion_projection_diagnostics.py`

These modules must be CPU/NumPy/Python postprocessing and diagnostic utilities. They must not import or modify `FSIDriver3D`, LBM stepping, MPM stepping, penalty coupling, moving-boundary coupling, link-area transfer, or projection formulas.

### 4.1 `src/squid_motion_mapping_config.py`

Define an immutable dataclass:

```python
@dataclass(frozen=True)
class SquidMotionMappingConfig:
    mapping_id: str
    schedule_config_path: str
    region_config_path: str
    geometry_config_path: str
    sample_count: int
    grid_sizes: tuple[int, ...]
    tracked_regions: tuple[str, ...]
    mantle_motion_model: str
    cavity_motion_model: str
    funnel_motion_model: str
    driver_integration_enabled: bool
    lbm_wall_velocity_enabled: bool
    jet_model_enabled: bool
    actuation_enabled: bool
    deterministic: bool
    scope_note: str
```

Required functions:

- `SquidMotionMappingConfig.from_json(path)`
- `SquidMotionMappingConfig.to_dict()`
- `validate_motion_mapping_config(config, root=None) -> list[dict]`
- `summarize_motion_mapping_config_validation(rows) -> dict`

Validation acceptance:

- mapping ID is nonempty;
- schedule config path exists;
- region config path exists;
- geometry config path exists;
- sample count is positive;
- grid sizes are positive;
- grid sizes equal `[32, 48, 64]`;
- tracked regions include `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy`;
- mantle motion model equals `radial_scale_proxy`;
- cavity motion model equals `volume_scale_proxy`;
- funnel motion model equals `aperture_scale_proxy`;
- deterministic is true;
- `driver_integration_enabled` is false;
- `lbm_wall_velocity_enabled` is false;
- `jet_model_enabled` is false;
- `actuation_enabled` is false;
- scope note includes `motion diagnostics only` and `no driver integration`.

### 4.2 `src/squid_motion_mapping.py`

Required functions:

- `load_motion_mapping_inputs(mapping_config_path) -> dict`
- `compute_region_motion_rows(mapping_config, schedule_rows, geometry_config, region_config, points, masks) -> list[dict]`
- `mantle_displacement_proxy(points, mantle_center, mantle_radii, mantle_radius_scale) -> np.ndarray`
- `mantle_velocity_proxy(points, mantle_center, mantle_radii, mantle_radius_rate) -> np.ndarray`
- `cavity_volume_rate_proxy(cavity_volume_rate) -> float`
- `funnel_aperture_rate_proxy(funnel_aperture_rate) -> float`
- `summarize_motion_rows(rows) -> dict`
- `write_motion_rows(rows, csv_path, json_path, summary=None) -> None`

Output row fields:

- `sample_index`
- `phase`
- `region_id`
- `motion_model`
- `point_count`
- `displacement_norm_min`
- `displacement_norm_max`
- `displacement_norm_mean`
- `velocity_norm_min`
- `velocity_norm_max`
- `velocity_norm_mean`
- `mantle_radius_scale`
- `mantle_radius_rate`
- `volume_scale`
- `volume_rate`
- `aperture_scale`
- `aperture_rate`
- `finite_pass`
- `bounds_pass`
- `driver_integration_enabled`
- `lbm_wall_velocity_enabled`
- `jet_model_enabled`
- `actuation_enabled`
- `scope_note`

Required motion semantics:

- row count equals Step 32 schedule row count times 3 tracked regions;
- `mantle_outer` rows use `radial_scale_proxy`;
- `mantle_outer` displacement magnitude is derived from radial distance to the mantle center times `abs(1 - mantle_radius_scale)`;
- `mantle_outer` velocity magnitude is derived from radial distance to the mantle center times `abs(mantle_radius_rate)`;
- `mantle_cavity_proxy` rows use `volume_scale_proxy` and carry cavity volume scale/rate;
- `funnel_outlet_proxy` rows use `aperture_scale_proxy` and carry funnel aperture scale/rate;
- cavity/funnel rows may have zero displacement and velocity proxies unless a future diagnostic explicitly adds a spatial model;
- all numeric fields must be finite;
- all flags for driver integration, LBM wall velocity, jet model, and actuation must be false.

### 4.3 `src/squid_motion_quality.py`

Required functions:

- `analyze_motion_mapping(rows, mapping_config) -> dict`
- `quality_rows_from_motion_analysis(analysis) -> list[dict]`
- `assert_motion_mapping_quality(analysis) -> None`

Required quality checks:

- `row_count_pass`;
- `tracked_region_count_pass`;
- `finite_pass`;
- `bounds_pass`;
- `mantle_motion_pass`;
- `cavity_motion_pass`;
- `funnel_motion_pass`;
- `mantle_velocity_nonzero_during_cycle`;
- `cavity_volume_rate_nonzero_during_cycle`;
- `funnel_aperture_rate_nonzero_during_open_close`;
- `driver_integration_disabled_pass`;
- `lbm_wall_velocity_disabled_pass`;
- `jet_model_disabled_pass`;
- `actuation_disabled_pass`;
- `quality_pass`.

Acceptance:

- all numeric motion fields are finite;
- displacement and velocity proxy norms are nonnegative and bounded;
- all tracked regions appear for each schedule sample;
- mantle rows have nonzero velocity during non-rest schedule phases;
- cavity rows carry nonzero finite volume-rate diagnostics during the cycle;
- funnel rows carry nonzero finite aperture-rate diagnostics during open/close phases;
- every execution/integration flag remains false.

### 4.4 `src/squid_motion_projection_diagnostics.py`

Required functions:

- `summarize_motion_on_grids(points, masks, motion_rows, grid_sizes) -> list[dict]`
- `summarize_motion_grid_rows(rows) -> dict`
- `assert_motion_grid_diagnostics(summary) -> None`

Output row fields:

- `grid_size`
- `region_id`
- `active_cell_count`
- `sample_point_count`
- `max_velocity_norm`
- `mean_velocity_norm`
- `max_displacement_norm`
- `coverage_pass`
- `finite_pass`

Acceptance:

- row count is `3 grid sizes * 3 tracked regions = 9`;
- grid sizes are 32, 48, and 64;
- tracked regions are `mantle_outer`, `mantle_cavity_proxy`, and `funnel_outlet_proxy`;
- `active_cell_count > 0` for all rows;
- max velocity, mean velocity, and max displacement are finite and nonnegative;
- coverage pass is true for all rows.

## 5. Required Config Files

Create:

- `configs/step33_squid_proxy_motion_mapping.json`
- `configs/step33_squid_proxy_motion_sampling.json`

The motion mapping config must include:

```json
{
  "mapping_id": "step33_squid_proxy_boundary_motion_diagnostics",
  "schedule_config_path": "configs/step32_squid_proxy_kinematics_schedule.json",
  "region_config_path": "configs/step30_squid_proxy_region_config.json",
  "geometry_config_path": "configs/step30_squid_proxy_geometry.json",
  "sample_count": 32768,
  "grid_sizes": [32, 48, 64],
  "tracked_regions": [
    "mantle_outer",
    "mantle_cavity_proxy",
    "funnel_outlet_proxy"
  ],
  "mantle_motion_model": "radial_scale_proxy",
  "cavity_motion_model": "volume_scale_proxy",
  "funnel_motion_model": "aperture_scale_proxy",
  "driver_integration_enabled": false,
  "lbm_wall_velocity_enabled": false,
  "jet_model_enabled": false,
  "actuation_enabled": false,
  "deterministic": true,
  "scope_note": "motion diagnostics only; no driver integration"
}
```

The sampling config must reference the motion mapping config and must be artifact-only. It must not include driver, LBM, MPM, coupling, moving-wall execution, jet, or flow-forcing settings.

## 6. Required Baseline Runners

Create:

- `baseline_tests/step33_common.py`
- `baseline_tests/run_step33_motion_mapping_config_validation.py`
- `baseline_tests/run_step33_generate_motion_mapping.py`
- `baseline_tests/run_step33_motion_quality.py`
- `baseline_tests/run_step33_motion_repeatability.py`
- `baseline_tests/run_step33_motion_grid_diagnostics.py`
- `baseline_tests/run_step33_schedule_motion_consistency.py`
- `baseline_tests/run_step33_step32_regression_guard.py`
- `baseline_tests/run_step33_artifact_manifest.py`

All runners must write small committed artifacts under `outputs/step33_*` and logs under `logs/step33_*.log`.

### 6.1 Config Validation Runner

Output:

- `outputs/step33_motion_mapping_config_validation/motion_mapping_config_validation.csv`
- `outputs/step33_motion_mapping_config_validation/motion_mapping_config_validation.json`
- `logs/step33_motion_mapping_config_validation.log`

Acceptance:

- row count is at least 12;
- all config validation rows pass;
- `validation_pass == true`;
- schedule, region, and geometry config paths exist;
- sample count is positive;
- grid sizes equal `[32, 48, 64]`;
- tracked regions include the three required Step 33 regions;
- all integration, wall-velocity, jet, and actuation flags are false.

### 6.2 Generate Motion Mapping Runner

Output:

- `outputs/step33_motion_mapping/motion_mapping.csv`
- `outputs/step33_motion_mapping/motion_mapping.json`
- `logs/step33_generate_motion_mapping.log`

Acceptance:

- `row_count == 243`;
- `tracked_region_count == 3`;
- `schedule_sample_count == 81`;
- `finite_pass == true`;
- `bounds_pass == true`;
- `mantle_outer` has nonzero max velocity during contraction/refill phases;
- `mantle_cavity_proxy` volume-rate diagnostics are finite;
- `funnel_outlet_proxy` aperture-rate diagnostics are finite;
- integration, LBM wall velocity, jet model, and actuation enabled counts are zero.

### 6.3 Motion Quality Runner

Output:

- `outputs/step33_motion_quality/motion_quality.csv`
- `outputs/step33_motion_quality/motion_quality.json`
- `logs/step33_motion_quality.log`

Acceptance:

- `quality_pass == true`;
- `finite_pass == true`;
- `bounds_pass == true`;
- `mantle_motion_pass == true`;
- `cavity_motion_pass == true`;
- `funnel_motion_pass == true`;
- `driver_integration_disabled_pass == true`;
- `lbm_wall_velocity_disabled_pass == true`;
- `jet_model_disabled_pass == true`;
- `actuation_disabled_pass == true`.

### 6.4 Motion Repeatability Runner

Generate the same motion mapping twice and compare hashes.

Output:

- `outputs/step33_motion_repeatability/motion_repeatability.csv`
- `outputs/step33_motion_repeatability/motion_repeatability.json`
- `logs/step33_motion_repeatability.log`

Acceptance:

- `motion_hash_first == motion_hash_second`;
- `mantle_motion_hash_first == mantle_motion_hash_second`;
- `cavity_motion_hash_first == cavity_motion_hash_second`;
- `funnel_motion_hash_first == funnel_motion_hash_second`;
- `repeatability_pass == true`.

### 6.5 Motion Grid Diagnostics Runner

Output:

- `outputs/step33_motion_grid_diagnostics/motion_grid_diagnostics.csv`
- `outputs/step33_motion_grid_diagnostics/motion_grid_diagnostics.json`
- `logs/step33_motion_grid_diagnostics.log`

Acceptance:

- `row_count == 9`;
- `grid_size_count == 3`;
- `tracked_region_count == 3`;
- `active_cell_count > 0` for all rows;
- max velocity norm is finite;
- mean velocity norm is finite;
- max displacement norm is finite;
- `coverage_pass == true`.

### 6.6 Schedule-Motion Consistency Runner

Output:

- `outputs/step33_schedule_motion_consistency/schedule_motion_consistency.csv`
- `outputs/step33_schedule_motion_consistency/schedule_motion_consistency.json`
- `logs/step33_schedule_motion_consistency.log`

Acceptance:

- Step 32 schedule row count is 81;
- Step 33 motion sample count is 81;
- phase samples match;
- mantle scale/rate match schedule values;
- cavity scale/rate match schedule values;
- funnel scale/rate match schedule values;
- `consistency_pass == true`.

### 6.7 Step 32 Regression Guard Runner

Input:

- `STEP32_CONTROLLED_SQUID_PROXY_KINEMATICS_SCHEDULE_REPORT.md`
- `outputs/step32_kinematics_schedule/kinematics_schedule.json`
- `outputs/step32_schedule_quality/schedule_quality.json`
- `outputs/step32_schedule_repeatability/schedule_repeatability.json`
- `outputs/step32_region_mapping_validation/region_mapping_validation.json`
- `outputs/step32_artifact_manifest/artifact_summary.json`

Output:

- `outputs/step33_step32_regression_guard/step32_regression_guard.csv`
- `outputs/step33_step32_regression_guard/step32_regression_guard.json`
- `logs/step33_step32_regression_guard.log`

Acceptance:

- Step 32 report exists;
- Step 32 schedule `row_count == 81`;
- Step 32 schedule quality passes;
- Step 32 repeatability passes;
- Step 32 region mapping passes;
- Step 32 large file count is zero;
- Step 32 `.vtr` count is zero;
- Step 32 particle `.npy` count is zero.

### 6.8 Artifact Manifest Runner

Output:

- `outputs/step33_artifact_manifest/artifact_manifest.csv`
- `outputs/step33_artifact_manifest/artifact_summary.csv`
- `outputs/step33_artifact_manifest/artifact_summary.json`
- `logs/step33_artifact_manifest.log`

Acceptance:

- `large_file_count == 0`;
- `step33_total_size_mb < 5`;
- repository `total_size_mb < 195`;
- `step33_vtr_count == 0`;
- `step33_particle_npy_count == 0`;
- `raw_candidate_large_file_count == 0`;
- `scan_data_file_count == 0`;
- `private_absolute_path_count == 0`.

The manifest runner must exclude local `__pycache__` and `.pyc` files.

## 7. Contract Test

Create:

- `tests/test_step33_squid_proxy_kinematics_mapping_contract.py`

Required tests:

- `test_step33_required_artifacts_exist`
- `test_step33_motion_mapping_config_is_valid`
- `test_step33_motion_mapping_output_is_valid`
- `test_step33_motion_quality_is_valid`
- `test_step33_motion_repeatability_is_valid`
- `test_step33_motion_grid_diagnostics_is_valid`
- `test_step33_schedule_motion_consistency_is_valid`
- `test_step33_step32_regression_guard_is_valid`
- `test_step33_default_modes_remain_unchanged`
- `test_step33_docs_scope_and_forbidden_claims_are_valid`
- `test_step33_artifact_budget_is_valid`
- `test_step33_report_acceptance_complete`
- `test_step33_no_driver_integration_claims`

Required scope phrases:

- `Step 33 is controlled squid proxy kinematics mapping to boundary-motion diagnostics.`
- `Step 33 maps schedules to displacement and velocity proxies only.`
- `Step 33 does not integrate kinematics into FSIDriver3D.`
- `Step 33 does not apply moving wall velocity to LBM.`
- `Step 33 does not implement a jet model.`
- `Step 33 does not implement squid swimming.`
- `Step 33 does not implement new FSI physics.`
- `The default quality_check_enabled remains false.`
- `The default quality_check_strict remains false.`
- `The default reaction_transfer_mode remains engineering.`
- `The moving bounce-back formula is unchanged.`
- `PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.`

Forbidden claims:

- `moving wall velocity is applied to LBM`
- `kinematics are integrated into FSIDriver3D`
- `mantle contraction is implemented in the driver`
- `funnel actuation is implemented in the driver`
- `jet model is implemented`
- `squid actuation is implemented`
- `squid swimming is implemented`
- `real squid simulation is validated`
- `production-ready sharp-interface FSI`
- `final solver readiness`
- `strict momentum-conserving FSI is complete`
- `implements two_phase`
- `implements contact_angle`

## 8. Required Docs And Report

Create:

- `docs/33_controlled_squid_proxy_kinematics_mapping.md`
- `STEP33_CONTROLLED_SQUID_PROXY_KINEMATICS_MAPPING_REPORT.md`

Update:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/11_artifact_policy.md`
- `docs/12_geometry_ingestion.md`
- `docs/30_controlled_squid_proxy_region_geometry.md`
- `docs/31_controlled_squid_proxy_region_static_driver.md`
- `docs/32_controlled_squid_proxy_kinematics_schedule.md`

Report sections:

- Goal
- Files Created And Updated
- Explicit Non-Goals
- Motion Mapping Config Validation
- Generated Motion Mapping
- Motion Quality
- Motion Repeatability
- Motion Grid Diagnostics
- Schedule-Motion Consistency
- Step 32 Regression Guard
- Artifact Manifest Summary
- Verification Commands
- GitHub Sync Information
- Acceptance Checklist
- Decision For Step 34

Decision for Step 34:

Step 34 should be `Controlled Squid Proxy Boundary-Motion Driver Interface Contract`. It may define a config schema such as `boundary_motion_mode = "static" | "prescribed_kinematic"` and a guarded no-op/default behavior contract, but should still avoid applying moving wall velocity to LBM. Actual moving wall velocity application should wait until Step 35 or later.

## 9. Verification Commands

Run these commands before completion:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\squid_motion_mapping_config.py src\squid_motion_mapping.py src\squid_motion_quality.py src\squid_motion_projection_diagnostics.py baseline_tests\step33_common.py baseline_tests\run_step33_motion_mapping_config_validation.py baseline_tests\run_step33_generate_motion_mapping.py baseline_tests\run_step33_motion_quality.py baseline_tests\run_step33_motion_repeatability.py baseline_tests\run_step33_motion_grid_diagnostics.py baseline_tests\run_step33_schedule_motion_consistency.py baseline_tests\run_step33_step32_regression_guard.py baseline_tests\run_step33_artifact_manifest.py tests\test_step33_squid_proxy_kinematics_mapping_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_motion_mapping_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_generate_motion_mapping.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_motion_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_motion_repeatability.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_motion_grid_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_schedule_motion_consistency.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_step32_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step33_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step33_squid_proxy_kinematics_mapping_contract.py -q
pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

If plain `pytest -q` fails because of the local shell/shim environment, rerun the same command with the trusted environment and document both the exact failure and the trusted pass. Do not ignore a real test failure.

## 10. Acceptance Checklist

- [ ] motion mapping config validation passes
- [ ] schedule config path exists
- [ ] region config path exists
- [ ] geometry config path exists
- [ ] tracked regions include mantle_outer
- [ ] tracked regions include mantle_cavity_proxy
- [ ] tracked regions include funnel_outlet_proxy
- [ ] driver integration flag is false
- [ ] LBM wall velocity flag is false
- [ ] jet model flag is false
- [ ] actuation flag is false
- [ ] generated motion mapping has expected row count
- [ ] motion mapping fields are finite
- [ ] displacement proxy fields are bounded
- [ ] velocity proxy fields are bounded
- [ ] mantle_outer motion diagnostics pass
- [ ] mantle_cavity_proxy motion diagnostics pass
- [ ] funnel_outlet_proxy motion diagnostics pass
- [ ] motion quality passes
- [ ] motion repeatability hash passes
- [ ] mantle motion hash repeats
- [ ] cavity motion hash repeats
- [ ] funnel motion hash repeats
- [ ] motion grid diagnostics pass at 32^3
- [ ] motion grid diagnostics pass at 48^3
- [ ] motion grid diagnostics pass at 64^3
- [ ] schedule-motion consistency passes
- [ ] Step 32 regression guard passes
- [ ] default quality_check_enabled remains false
- [ ] default quality_check_strict remains false
- [ ] default reaction_transfer_mode remains engineering
- [ ] no FSIDriver3D integration
- [ ] no LBM moving wall velocity application
- [ ] no jet model
- [ ] no mantle contraction driver claim
- [ ] no funnel actuation driver claim
- [ ] no squid swimming claim
- [ ] no real squid validation claim
- [ ] no new FSI physics
- [ ] no moving bounce-back formula changes
- [ ] no LBM formula changes
- [ ] no MPM constitutive formula changes
- [ ] no projection formula changes
- [ ] no external/taichi_LBM3D edits
- [ ] no Step 33 .vtr outputs
- [ ] no Step 33 particle .npy outputs
- [ ] artifact large_file_count == 0
- [ ] Step 33 output total-size budget passes
- [ ] repo artifact summary total_size_mb < 195
- [ ] logs/step33_pytest.log exists
- [ ] pytest -q passes
- [ ] Step 33 contract test passes
- [ ] git diff --check passes
- [ ] staged whitespace check passes
- [ ] pre-push hook passes
- [ ] Step 33 artifacts are pushed to origin/main

## 11. Commit And Push

Use commit message:

```text
test: add step33 squid proxy kinematics mapping diagnostics
```

After local verification, commit all relevant source, configs, tests, docs, reports, logs, and small outputs. Push to `origin/main` because the user explicitly approved push after modifications. Report the final commit hash, remote branch, and verification results.
