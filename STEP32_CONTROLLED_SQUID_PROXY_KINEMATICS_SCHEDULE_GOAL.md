# Step 32 Controlled Squid Proxy Prescribed Kinematics Schedule Goal

## 1. Name

Step 32 Controlled Squid Proxy Prescribed Kinematics Schedule Contract

Short scope statement:

Step 32 defines deterministic prescribed kinematics schedules for the accepted Step 30/31 static squid proxy regions. It creates and validates schedule math, schedule artifacts, region-mapping compatibility, repeatability, and envelope diagnostics only. Step 32 does not integrate kinematics into `FSIDriver3D`, does not apply moving wall velocity, does not drive mantle contraction or funnel actuation in simulation, and does not add new FSI physics.

## 2. Starting Point

Step 31 is accepted on GitHub. It provides:

- 32^3, 48^3, and 64^3 squid proxy region projection scale diagnostics;
- a four-row 48^3 static `FSIDriver3D` smoke matrix for none, penalty, moving_boundary engineering, and moving_boundary link-area transfer;
- strict quality report aggregation;
- Step 30 regression guard;
- artifact manifest evidence;
- explicit scope that Step 31 uses static region semantics only.

Step 31's decision says Step 32 should define:

- mantle radius schedule;
- mantle cavity volume proxy schedule;
- funnel aperture proxy schedule;
- cycle period;
- phase/ramp semantics;
- kinematic repeatability.

Step 31 also says Step 32 must not integrate kinematics into the driver. Driver integration must wait for Step 33 or later.

## 3. Non-Negotiable Boundaries

Step 32 must not implement or claim any of the following:

- driver integration;
- `FSIDriver3D` changes for actuation;
- mantle wall velocity applied to LBM;
- funnel boundary motion applied to LBM;
- jet model;
- free-body motion;
- squid swimming;
- implemented squid actuation;
- new FSI physics;
- new coupling formula;
- changes to moving bounce-back;
- changes to `PenaltyFSICoupler3D`;
- changes to `MovingBoundaryFSICoupler3D`;
- changes to `LinkAreaMovingBoundaryCoupler3D`;
- changes to LBM step formulas;
- changes to MPM constitutive formulas;
- changes to projection formulas;
- production sharp-interface FSI;
- real squid validation;
- production mesh repair;
- automatic remeshing;
- two-phase flow;
- contact-angle physics;
- sparse storage;
- edits to `external/taichi_LBM3D`;
- committed raw scan data;
- committed large raw real geometry.

Step 32 is allowed to implement:

- immutable kinematics config dataclass;
- schedule config validation;
- cycle phase samples;
- ramp and smoothstep functions;
- mantle radius scale schedule;
- mantle cavity volume proxy schedule;
- funnel aperture proxy schedule;
- first-derivative diagnostics;
- phase labels;
- schedule quality checks;
- deterministic schedule repeatability hashes;
- region mapping validation against Step 30 region semantics;
- schedule envelope summary;
- Step 31 regression guard;
- artifact manifest and small committed outputs;
- docs, report, logs, and contract tests.

## 4. Required Source Files

Create:

- `src/squid_kinematics_config.py`
- `src/squid_kinematics_schedule.py`
- `src/squid_kinematics_quality.py`
- `src/squid_kinematics_region_mapping.py`

These modules must be CPU/NumPy/Python postprocessing and schedule-definition utilities. They must not import or modify `FSIDriver3D`, LBM stepping, MPM stepping, penalty coupling, moving-boundary coupling, link-area transfer, or projection formulas.

### 4.1 `src/squid_kinematics_config.py`

Define an immutable dataclass:

```python
@dataclass(frozen=True)
class SquidKinematicsScheduleConfig:
    schedule_id: str
    region_config_path: str
    geometry_config_path: str
    cycle_period_steps: int
    sample_count: int
    contraction_start_phase: float
    contraction_end_phase: float
    refill_start_phase: float
    refill_end_phase: float
    ramp_fraction: float
    mantle_radius_scale_rest: float
    mantle_radius_scale_min: float
    cavity_volume_scale_rest: float
    cavity_volume_scale_min: float
    funnel_aperture_scale_rest: float
    funnel_aperture_scale_max: float
    funnel_open_phase_start: float
    funnel_open_phase_end: float
    deterministic: bool
    driver_integration_enabled: bool
    actuation_enabled: bool
    scope_note: str
```

Required functions:

- `SquidKinematicsScheduleConfig.from_json(path)`
- `SquidKinematicsScheduleConfig.to_dict()`
- `validate_kinematics_schedule_config(config, root=None) -> list[dict]`
- `summarize_config_validation(rows) -> dict`

Validation acceptance:

- config file exists;
- region config path exists;
- geometry config path exists;
- `cycle_period_steps > 0`;
- `sample_count >= cycle_period_steps + 1`;
- all phase values are finite and within `[0, 1]`;
- `contraction_start_phase < contraction_end_phase`;
- `refill_start_phase == contraction_end_phase`;
- `refill_start_phase < refill_end_phase`;
- `refill_end_phase == 1.0`;
- `0 <= ramp_fraction <= 0.5`;
- `0 < mantle_radius_scale_min <= mantle_radius_scale_rest`;
- `0 < cavity_volume_scale_min <= cavity_volume_scale_rest`;
- `0 <= funnel_aperture_scale_rest <= funnel_aperture_scale_max`;
- `funnel_open_phase_start < funnel_open_phase_end`;
- `deterministic is True`;
- `driver_integration_enabled is False`;
- `actuation_enabled is False`;
- `scope_note` includes `schedule contract only` and `no driver integration`.

### 4.2 `src/squid_kinematics_schedule.py`

Required functions:

- `phase_samples(config) -> np.ndarray`
- `smoothstep(x) -> np.ndarray`
- `window_weight(phase, start, end, ramp_fraction) -> np.ndarray`
- `mantle_radius_scale(phase, config) -> np.ndarray`
- `cavity_volume_scale(phase, config) -> np.ndarray`
- `funnel_aperture_scale(phase, config) -> np.ndarray`
- `schedule_rows(config) -> list[dict]`
- `summarize_schedule(rows) -> dict`
- `write_schedule_outputs(rows, csv_path, json_path, summary=None) -> None`

Output row fields:

- `sample_index`
- `phase`
- `cycle_time_fraction`
- `mantle_radius_scale`
- `mantle_radius_rate`
- `cavity_volume_scale`
- `cavity_volume_rate`
- `funnel_aperture_scale`
- `funnel_aperture_rate`
- `phase_label`
- `ramp_weight`
- `driver_integration_enabled`
- `actuation_enabled`
- `scope_note`

Required schedule semantics:

- phases sample `[0, 1]` inclusively;
- row count equals `sample_count`;
- endpoint values repeat rest state;
- contraction phase decreases mantle radius scale and cavity volume scale;
- refill phase returns mantle radius scale and cavity volume scale to rest;
- funnel aperture opens during configured funnel-open window and returns to rest;
- derivatives are finite first differences with respect to phase;
- the first and last rows have repeatable endpoint values.

### 4.3 `src/squid_kinematics_quality.py`

Required functions:

- `analyze_kinematics_schedule(rows, config) -> dict`
- `quality_rows_from_analysis(analysis) -> list[dict]`
- `assert_kinematics_schedule_quality(analysis) -> None`

Required quality checks:

- `finite_pass`;
- `bounds_pass`;
- `phase_monotonic_pass`;
- `endpoint_repeatability_pass`;
- `derivative_finite_pass`;
- `contraction_volume_rate_pass`;
- `refill_volume_rate_pass`;
- `funnel_aperture_bounds_pass`;
- `driver_integration_disabled_pass`;
- `actuation_disabled_pass`;
- `quality_pass`.

Acceptance:

- all numeric schedule fields finite;
- `mantle_radius_scale` remains within configured `[min, rest]`;
- `cavity_volume_scale` remains within configured `[min, rest]`;
- `funnel_aperture_scale` remains within configured `[rest, max]`;
- phase is monotonic nondecreasing;
- first and last mantle/cavity/funnel values match within `1e-12`;
- all derivative fields are finite;
- contraction window has non-positive cavity volume rate, allowing endpoint tolerance;
- refill window has non-negative cavity volume rate, allowing endpoint tolerance;
- driver integration and actuation flags are false in every row.

### 4.4 `src/squid_kinematics_region_mapping.py`

Required functions:

- `validate_kinematics_region_mapping(schedule_config, region_config) -> dict`
- `region_mapping_rows(mapping) -> list[dict]`
- `assert_region_mapping(mapping) -> None`

Required mapping checks:

- `mantle_outer` exists;
- `mantle_cavity_proxy` exists;
- `funnel_outlet_proxy` exists;
- all Step 30 required region IDs remain present;
- all Step 30 region `active_for_actuation` flags remain false;
- `driver_integration_enabled` is false;
- `actuation_enabled` is false;
- mapping notes say future mapping only;
- no region config mutation.

## 5. Required Config Files

Create:

- `configs/step32_squid_proxy_kinematics_schedule.json`
- `configs/step32_squid_proxy_kinematics_sampling.json`

The schedule config must include:

```json
{
  "schedule_id": "step32_squid_proxy_prescribed_cycle",
  "region_config_path": "configs/step30_squid_proxy_region_config.json",
  "geometry_config_path": "configs/step30_squid_proxy_geometry.json",
  "cycle_period_steps": 40,
  "sample_count": 81,
  "contraction_start_phase": 0.0,
  "contraction_end_phase": 0.35,
  "refill_start_phase": 0.35,
  "refill_end_phase": 1.0,
  "ramp_fraction": 0.10,
  "mantle_radius_scale_rest": 1.0,
  "mantle_radius_scale_min": 0.85,
  "cavity_volume_scale_rest": 1.0,
  "cavity_volume_scale_min": 0.60,
  "funnel_aperture_scale_rest": 0.35,
  "funnel_aperture_scale_max": 1.0,
  "funnel_open_phase_start": 0.05,
  "funnel_open_phase_end": 0.40,
  "deterministic": true,
  "driver_integration_enabled": false,
  "actuation_enabled": false,
  "scope_note": "schedule contract only; no driver integration"
}
```

The sampling config must reference the schedule config and must be artifact-only. It must not include driver, LBM, MPM, coupling, or moving-wall execution settings.

## 6. Required Baseline Runners

Create:

- `baseline_tests/step32_common.py`
- `baseline_tests/run_step32_schedule_config_validation.py`
- `baseline_tests/run_step32_generate_kinematics_schedule.py`
- `baseline_tests/run_step32_schedule_quality.py`
- `baseline_tests/run_step32_schedule_repeatability.py`
- `baseline_tests/run_step32_region_mapping_validation.py`
- `baseline_tests/run_step32_schedule_envelope_summary.py`
- `baseline_tests/run_step32_step31_regression_guard.py`
- `baseline_tests/run_step32_artifact_manifest.py`

All runners must write small committed artifacts under `outputs/step32_*` and logs under `logs/step32_*.log`.

### 6.1 Config Validation Runner

Output:

- `outputs/step32_schedule_config_validation/schedule_config_validation.csv`
- `outputs/step32_schedule_config_validation/schedule_config_validation.json`
- `logs/step32_schedule_config_validation.log`

Acceptance:

- all config validation rows pass;
- `validation_pass == true`;
- config paths exist;
- phase ranges valid;
- scale ranges valid;
- deterministic true;
- driver integration false;
- actuation false.

### 6.2 Schedule Generation Runner

Output:

- `outputs/step32_kinematics_schedule/kinematics_schedule.csv`
- `outputs/step32_kinematics_schedule/kinematics_schedule.json`
- `logs/step32_generate_kinematics_schedule.log`

Acceptance:

- `row_count == sample_count`;
- `phase_min == 0`;
- `phase_max == 1`;
- all schedule fields finite;
- mantle radius scale bounded;
- cavity volume scale bounded;
- funnel aperture scale bounded;
- endpoint repeatability passes.

### 6.3 Schedule Quality Runner

Output:

- `outputs/step32_schedule_quality/schedule_quality.csv`
- `outputs/step32_schedule_quality/schedule_quality.json`
- `logs/step32_schedule_quality.log`

Acceptance:

- `quality_pass == true`;
- `finite_pass == true`;
- `bounds_pass == true`;
- `phase_monotonic_pass == true`;
- `endpoint_repeatability_pass == true`;
- `derivative_finite_pass == true`;
- `contraction_volume_rate_pass == true`;
- `refill_volume_rate_pass == true`;
- `funnel_aperture_bounds_pass == true`;
- `driver_integration_disabled_pass == true`;
- `actuation_disabled_pass == true`.

### 6.4 Schedule Repeatability Runner

Generate the same schedule twice and compare hashes.

Output:

- `outputs/step32_schedule_repeatability/schedule_repeatability.csv`
- `outputs/step32_schedule_repeatability/schedule_repeatability.json`
- `logs/step32_schedule_repeatability.log`

Acceptance:

- `row_count_first == row_count_second`;
- `schedule_hash_first == schedule_hash_second`;
- `mantle_hash_first == mantle_hash_second`;
- `cavity_hash_first == cavity_hash_second`;
- `funnel_hash_first == funnel_hash_second`;
- `repeatability_pass == true`.

### 6.5 Region Mapping Validation Runner

Output:

- `outputs/step32_region_mapping_validation/region_mapping_validation.csv`
- `outputs/step32_region_mapping_validation/region_mapping_validation.json`
- `logs/step32_region_mapping_validation.log`

Acceptance:

- `mantle_outer` present;
- `mantle_cavity_proxy` present;
- `funnel_outlet_proxy` present;
- all Step 30 region IDs unchanged;
- `driver_integration_enabled == false`;
- `actuation_enabled == false`;
- `mapping_pass == true`.

### 6.6 Schedule Envelope Summary Runner

Output:

- `outputs/step32_schedule_envelope_summary/schedule_envelope_summary.csv`
- `outputs/step32_schedule_envelope_summary/schedule_envelope_summary.json`
- `logs/step32_schedule_envelope_summary.log`

Required fields:

- `mantle_radius_scale_min_observed`
- `mantle_radius_scale_max_observed`
- `cavity_volume_scale_min_observed`
- `cavity_volume_scale_max_observed`
- `funnel_aperture_scale_min_observed`
- `funnel_aperture_scale_max_observed`
- `max_abs_mantle_radius_rate`
- `max_abs_cavity_volume_rate`
- `max_abs_funnel_aperture_rate`
- `contraction_sample_count`
- `refill_sample_count`
- `funnel_open_sample_count`
- `envelope_pass`

Acceptance:

- all values finite;
- observed min/max within configured bounds;
- `contraction_sample_count > 0`;
- `refill_sample_count > 0`;
- `funnel_open_sample_count > 0`;
- `envelope_pass == true`.

### 6.7 Step 31 Regression Guard Runner

Output:

- `outputs/step32_step31_regression_guard/step31_regression_guard.csv`
- `outputs/step32_step31_regression_guard/step31_regression_guard.json`
- `logs/step32_step31_regression_guard.log`

Acceptance:

- Step 31 report exists;
- Step 31 region projection `row_count == 21`;
- Step 31 static driver `driver_row_count == 4`;
- Step 31 static driver `stable_count == 4`;
- Step 31 quality report count is 4;
- Step 31 artifact `large_file_count == 0`;
- Step 31 `step31_vtr_count == 0`;
- Step 31 `step31_particle_npy_count == 0`.

### 6.8 Artifact Manifest Runner

Output:

- `outputs/step32_artifact_manifest/artifact_manifest.csv`
- `outputs/step32_artifact_manifest/artifact_summary.csv`
- `outputs/step32_artifact_manifest/artifact_summary.json`
- `logs/step32_artifact_manifest.log`

Acceptance:

- `large_file_count == 0`;
- `step32_total_size_mb < 3`;
- repository `total_size_mb < 190`;
- `step32_vtr_count == 0`;
- `step32_particle_npy_count == 0`;
- `raw_candidate_large_file_count == 0`;
- `scan_data_file_count == 0`;
- `private_absolute_path_count == 0`.

The manifest runner must exclude local `__pycache__` and `.pyc` files.

## 7. Contract Test

Create:

- `tests/test_step32_squid_proxy_kinematics_schedule_contract.py`

Required tests:

- `test_step32_required_artifacts_exist`
- `test_step32_schedule_config_is_valid`
- `test_step32_kinematics_schedule_is_valid`
- `test_step32_schedule_quality_is_valid`
- `test_step32_schedule_repeatability_is_valid`
- `test_step32_region_mapping_validation_is_valid`
- `test_step32_schedule_envelope_summary_is_valid`
- `test_step32_step31_regression_guard_is_valid`
- `test_step32_default_modes_remain_unchanged`
- `test_step32_docs_scope_and_forbidden_claims_are_valid`
- `test_step32_artifact_budget_is_valid`
- `test_step32_report_acceptance_complete`
- `test_step32_no_driver_integration_claims`

Required scope phrases:

- `Step 32 is controlled squid proxy prescribed kinematics schedule.`
- `Step 32 defines kinematics schedules only.`
- `Step 32 does not integrate kinematics into FSIDriver3D.`
- `Step 32 does not apply moving wall velocity.`
- `Step 32 does not implement mantle contraction in the driver.`
- `Step 32 does not implement funnel actuation in the driver.`
- `Step 32 does not implement squid swimming.`
- `Step 32 does not implement new FSI physics.`
- `The default quality_check_enabled remains false.`
- `The default quality_check_strict remains false.`
- `The default reaction_transfer_mode remains engineering.`
- `The moving bounce-back formula is unchanged.`
- `PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.`

Forbidden claims:

- `mantle contraction is integrated into the driver`
- `funnel actuation is integrated into the driver`
- `squid actuation is implemented`
- `squid swimming is implemented`
- `real squid simulation is validated`
- `production-ready sharp-interface FSI`
- `final solver readiness`
- `jet model is implemented`
- `free-body motion is implemented`
- `moving wall velocity is applied`
- `strict momentum-conserving FSI is complete`
- `implements two_phase`
- `implements contact_angle`

## 8. Required Docs And Report

Create:

- `docs/32_controlled_squid_proxy_kinematics_schedule.md`
- `STEP32_CONTROLLED_SQUID_PROXY_KINEMATICS_SCHEDULE_REPORT.md`

Update:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/11_artifact_policy.md`
- `docs/12_geometry_ingestion.md`
- `docs/30_controlled_squid_proxy_region_geometry.md`
- `docs/31_controlled_squid_proxy_region_static_driver.md`

Report sections:

- Goal
- Files Created And Updated
- Explicit Non-Goals
- Schedule Config Validation
- Generated Kinematics Schedule
- Schedule Quality
- Schedule Repeatability
- Region Mapping Validation
- Schedule Envelope Summary
- Step 31 Regression Guard
- Artifact Manifest Summary
- Verification Commands
- GitHub Sync Information
- Acceptance Checklist
- Decision For Step 33

Decision for Step 33:

Step 33 should be `Controlled Squid Proxy Kinematics Mapping To Boundary-Motion Diagnostics`. It may map the accepted Step 32 schedule to region displacement and velocity proxies for diagnostics only. It must not integrate moving wall velocity into LBM, must not implement a jet model, and must not claim squid swimming. Real driver integration should wait for Step 34 or later.

## 9. Verification Commands

Run these commands before completion:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\squid_kinematics_config.py src\squid_kinematics_schedule.py src\squid_kinematics_quality.py src\squid_kinematics_region_mapping.py baseline_tests\step32_common.py baseline_tests\run_step32_schedule_config_validation.py baseline_tests\run_step32_generate_kinematics_schedule.py baseline_tests\run_step32_schedule_quality.py baseline_tests\run_step32_schedule_repeatability.py baseline_tests\run_step32_region_mapping_validation.py baseline_tests\run_step32_schedule_envelope_summary.py baseline_tests\run_step32_step31_regression_guard.py baseline_tests\run_step32_artifact_manifest.py tests\test_step32_squid_proxy_kinematics_schedule_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_schedule_config_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_generate_kinematics_schedule.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_schedule_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_schedule_repeatability.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_region_mapping_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_schedule_envelope_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_step31_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step32_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step32_squid_proxy_kinematics_schedule_contract.py -q
pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

If plain `pytest -q` fails because of the local shell/shim environment, rerun the same command with the trusted environment and document both the exact failure and the trusted pass. Do not ignore a real test failure.

## 10. Acceptance Checklist

- [ ] schedule config validation passes
- [ ] region config path exists
- [ ] geometry config path exists
- [ ] cycle period is positive
- [ ] sample count is sufficient
- [ ] phase ranges are valid
- [ ] scale ranges are valid
- [ ] generated kinematics schedule has expected row count
- [ ] phase samples are monotonic
- [ ] endpoint repeatability passes
- [ ] mantle radius scale is finite and bounded
- [ ] cavity volume scale is finite and bounded
- [ ] funnel aperture scale is finite and bounded
- [ ] mantle radius derivative is finite
- [ ] cavity volume derivative is finite
- [ ] funnel aperture derivative is finite
- [ ] contraction phase volume-rate check passes
- [ ] refill phase volume-rate check passes
- [ ] schedule repeatability hash passes
- [ ] mantle schedule hash repeats
- [ ] cavity schedule hash repeats
- [ ] funnel schedule hash repeats
- [ ] region mapping validation passes
- [ ] mantle_outer region is mapped
- [ ] mantle_cavity_proxy region is mapped
- [ ] funnel_outlet_proxy region is mapped
- [ ] driver integration flag is false
- [ ] actuation enabled flag is false
- [ ] schedule envelope summary passes
- [ ] Step 31 regression guard passes
- [ ] default quality_check_enabled remains false
- [ ] default quality_check_strict remains false
- [ ] default reaction_transfer_mode remains engineering
- [ ] no FSIDriver3D integration
- [ ] no moving wall velocity application
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
- [ ] no Step 32 .vtr outputs
- [ ] no Step 32 particle .npy outputs
- [ ] artifact large_file_count == 0
- [ ] Step 32 output total-size budget passes
- [ ] repo artifact summary total_size_mb < 190
- [ ] logs/step32_pytest.log exists
- [ ] pytest -q passes
- [ ] Step 32 contract test passes
- [ ] git diff --check passes
- [ ] staged whitespace check passes
- [ ] pre-push hook passes
- [ ] Step 32 artifacts are pushed to origin/main

## 11. Commit And Push

Use commit message:

```text
test: add step32 squid proxy kinematics schedule contract
```

After local verification, commit all relevant source, configs, tests, docs, reports, logs, and small outputs. Push to `origin/main` because the user explicitly approved push after modifications. Report the final commit hash, remote branch, and verification results.
