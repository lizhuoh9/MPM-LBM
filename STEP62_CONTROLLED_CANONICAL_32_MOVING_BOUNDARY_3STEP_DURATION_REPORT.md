# Step 62 Controlled Canonical 32 Moving-Boundary 3-Step Duration Report

## Goal

Step 62 expands exactly one dimension from Step 61:

```text
duration: 1 LBM step -> 3 LBM steps
grid: 32^3
mode: moving_boundary engineering
```

The probe imports and runs the canonical driver implementation:

```python
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D
driver.run()
```

This is a controlled canonical 32^3 moving-boundary 3-step duration probe and a finite/bounded duration feasibility smoke. It is not a broader solver validation campaign.

## Runtime Vs Diagnostic Boundary

Step 62 runs the existing canonical moving-boundary engineering path only. It does not change runtime solver code, stepping formulas, moving-boundary formulas, geometry motion behavior, wall-velocity behavior, or optional bridge ownership.

The matrix policy records:

| Flag | Value |
| --- | --- |
| `runtime_code_changed` | false |
| `solver_behavior_changed` | false |
| `physics_feature_expansion` | false |
| `run_optional_penalty_32_3step` | false |
| `run_optional_32_5step` | false |

## Step61 Report Consistency Repair

Step 62 repairs the Step 61 report Output Guard size value. The Step 61 report now matches:

```text
outputs/step61_output_guard/output_guard.json
summary.step61_total_size_mb = 0.46668243408203125
```

The Step 61 artifact manifest value remains:

```text
outputs/step61_artifact_manifest/artifact_summary.json
step61_total_size_mb = 0.5198221206665039
```

Step 62 also adds a report consistency guard so Step 61 and Step 62 report size rows are checked against their JSON artifacts.

## Files Created And Updated

Created:

- `STEP62_CONTROLLED_CANONICAL_32_MOVING_BOUNDARY_3STEP_DURATION_GOAL.md`
- `STEP62_CONTROLLED_CANONICAL_32_MOVING_BOUNDARY_3STEP_DURATION_REPORT.md`
- `docs/62_controlled_canonical_32_moving_boundary_3step_duration.md`
- `configs/step62_*.json`
- `src/mpm_lbm/evidence/canonical_driver_32_duration_runner.py`
- `src/mpm_lbm/evidence/canonical_driver_32_duration_audit.py`
- `src/mpm_lbm/evidence/canonical_driver_32_duration_output_guard.py`
- `src/mpm_lbm/evidence/report_consistency_guard.py`
- `src/mpm_lbm/evidence/step62_regression_guard.py`
- `baseline_tests/step62_common.py`
- `baseline_tests/run_step62_*.py`
- `tests/test_step62_*.py`
- `outputs/step62_*/`
- `logs/step62_*.log`

Updated:

- `STEP61_CONTROLLED_CANONICAL_32_MOVING_BOUNDARY_SINGLE_STEP_REPORT.md`
- `README.md`
- `docs/00_project_status.md`

## Explicit Non-Goals

Step 62 does not activate runtime geometry, wall-velocity application, geometry motion, prescribed boundary motion, 48^3 or 64^3 rows, required 5-step rows, long-duration rows, required link-area rows, real geometry, propulsion validation, real squid behavior validation, grid-convergence proof, viscosity/tau migration, VTR output, particle NPY output, external solver edits, real-geometry candidate edits, runtime solver code changes, or deployment-readiness claims.

## Required Configs

Required row config:

- `configs/step62_canonical_driver_moving_boundary_engineering_32_3step.json`

Optional row configs, disabled by default:

- `configs/step62_canonical_driver_penalty_32_3step_optional.json`
- `configs/step62_canonical_driver_moving_boundary_engineering_32_5step_optional.json`

Policies:

- `configs/step62_controlled_canonical_32_moving_boundary_3step_duration.json`
- `configs/step62_duration_acceptance_policy.json`
- `configs/step62_output_guard_policy.json`
- `configs/step62_runtime_budget_policy.json`
- `configs/step62_report_consistency_policy.json`

## 32^3 3-Step Duration Matrix

| Row | Mode | Grid | Particles | LBM steps | Diagnostics rows | Stable | Elapsed seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `canonical_driver_moving_boundary_engineering_32_3step` | `moving_boundary` | 32^3 | 1024 | 3 | 4 | true | 238.40363110000908 |

Matrix summary:

| Metric | Value |
| --- | --- |
| `duration_32_matrix_pass` | true |
| `required_stable_count` | 1 |
| `driver_run_called_count` | 1 |
| `legacy_driver_module_used_count` | 0 |
| `has_nan_count` | 0 |
| `has_inf_count` | 0 |
| `runtime_warning_count` | 0 |
| `runtime_hard_limit_exceeded_count` | 0 |
| `min_rho_min` | 0.9631504416465759 |
| `max_rho_max` | 1.037545919418335 |
| `max_lbm_max_v` | 0.028745334595441818 |
| `min_mpm_min_J` | 0.9998476505279541 |
| `bb_link_count_max` | 2272 |

## 32^3 Duration Quality

The quality audit confirms:

- the required 32^3 / 3-step row is present
- the row used `src.mpm_lbm.sim.drivers.fsi_driver`
- the row called the real driver run path
- the row stayed finite under the Step 62 bounds
- the row produced `geo_all_fluid_32.dat`
- no legacy root driver implementation owns the run

The committed quality artifact is:

- `outputs/step62_32_duration_quality/duration_32_quality.json`

## Runtime Timing Summary

Measured runtime:

```text
238.40363110000908 seconds
```

Runtime warning count:

```text
0
```

Runtime hard-limit exceeded count:

```text
0
```

The required 32^3 / 3-step row stayed below the 3600-second soft warning threshold and the 7200-second hard limit.

The Taichi run emitted offline-cache lock warnings after the successful matrix result. These warnings did not prevent the row from completing or artifacts from being written.

## Output Guard

The Step 62 output guard reports:

| Metric | Value |
| --- | --- |
| `output_guard_pass` | true |
| `step62_required_driver_run_dir_count` | 1 |
| `step62_optional_driver_run_dir_count` | 0 |
| `step62_vtr_count` | 0 |
| `step62_particle_npy_count` | 0 |
| `step62_large_file_count` | 0 |
| `step62_forbidden_file_count` | 0 |
| `private_absolute_path_count` | 0 |
| `external_edit_count` | 0 |
| `real_geometry_candidates_edit_count` | 0 |
| `step62_total_size_mb` | 0.4743785858154297 |

The required driver run directory contains only:

- `driver_config.json`
- `geo_all_fluid_32.dat`
- `diagnostics_timeseries.csv`
- `diagnostics_timeseries.npz`

## Report Consistency Guard

The Step 62 report consistency guard checks:

- Step 61 report Output Guard size against `outputs/step61_output_guard/output_guard.json`
- Step 61 report Artifact Manifest size against `outputs/step61_artifact_manifest/artifact_summary.json`
- Step 62 report Output Guard size against `outputs/step62_output_guard/output_guard.json`
- Step 62 report Artifact Manifest size against `outputs/step62_artifact_manifest/artifact_summary.json`

The committed consistency artifact is:

- `outputs/step62_report_consistency_guard/report_consistency_guard.json`

## Step61 Regression Guard

The Step 62 regression guard confirms Step 61 remains green:

- Step 61 32 probe matrix pass
- Step 61 32 probe quality pass
- Step 61 output guard pass
- Step 61 Step 60 regression guard pass
- Step 61 artifact manifest pass
- Step 61 required row still present
- Step 61 optional rows remain disabled
- Step 61 legacy driver implementation count remains 0
- Step 61 runtime code changed remains false
- Step 61 solver behavior changed remains false
- Step 61 physics feature expansion remains false
- Step 61 report consistency issue fixed

The committed regression artifact is:

- `outputs/step62_step61_regression_guard/step61_regression_guard.json`

## Artifact Manifest

The Step 62 artifact manifest is generated by:

```text
baseline_tests/run_step62_artifact_manifest.py
```

The committed manifest artifacts are:

- `outputs/step62_artifact_manifest/artifact_manifest.csv`
- `outputs/step62_artifact_manifest/artifact_summary.csv`
- `outputs/step62_artifact_manifest/artifact_summary.json`

Manifest summary:

| Metric | Value |
| --- | --- |
| `artifact_budget_pass` | true |
| `step62_file_count` | 52 |
| `step62_total_size_mb` | 0.5418987274169922 |
| `large_file_count` | 0 |
| `step62_vtr_count` | 0 |
| `step62_particle_npy_count` | 0 |
| `protected_external_taichi_lbm3d_step62_file_count` | 0 |
| `protected_real_geometry_candidates_step62_file_count` | 0 |

## Verification Commands

```powershell
D:\working\taichi\env\python.exe -m py_compile src\mpm_lbm\evidence\canonical_driver_32_duration_runner.py src\mpm_lbm\evidence\canonical_driver_32_duration_audit.py src\mpm_lbm\evidence\canonical_driver_32_duration_output_guard.py src\mpm_lbm\evidence\report_consistency_guard.py src\mpm_lbm\evidence\step62_regression_guard.py baseline_tests\step62_common.py baseline_tests\run_step62_32_duration_matrix.py baseline_tests\run_step62_32_duration_quality.py baseline_tests\run_step62_output_guard.py baseline_tests\run_step62_report_consistency_guard.py baseline_tests\run_step62_step61_regression_guard.py baseline_tests\run_step62_artifact_manifest.py tests\test_step62_32_duration_contract.py tests\test_step62_32_duration_quality_contract.py tests\test_step62_output_guard_contract.py tests\test_step62_report_consistency_contract.py tests\test_step62_step61_regression_contract.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step62_32_duration_matrix.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step62_32_duration_quality.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step62_output_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step62_report_consistency_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step62_step61_regression_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step62_artifact_manifest.py
D:\working\taichi\env\python.exe -W ignore -m pytest -q tests/test_step62_32_duration_contract.py tests/test_step62_32_duration_quality_contract.py tests/test_step62_output_guard_contract.py tests/test_step62_report_consistency_contract.py tests/test_step62_step61_regression_contract.py
D:\working\taichi\env\python.exe -W ignore -m pytest -q
D:\TOOL\Anaconda\python.exe -W ignore -m pytest -q
```

## Acceptance Checklist

- [x] Detailed Step 62 goal file exists and the active goal references it.
- [x] Step 61 report output-guard size mismatch is repaired.
- [x] Required configs are checked in.
- [x] Required 32^3 / 3-step row calls the canonical `FSIDriver3D(...).run()` path.
- [x] Required row completes 3 LBM steps with 4 diagnostics rows.
- [x] Required row is finite and bounded under Step 62 policy.
- [x] Runtime code remains unchanged.
- [x] Optional 32^3 rows are defined but disabled by default.
- [x] Output guard rejects heavy and private-path artifacts.
- [x] Report consistency guard passes.
- [x] Step 61 regression guard passes.
- [x] External solver and real-geometry candidate directories remain unmodified.

## Decision For Step63

The Step 62 32^3 / 3-step moving-boundary row is stable and below the 3600-second runtime warning threshold. The conservative Step 63 direction is one dimension only:

```text
32^3 moving_boundary engineering 5-step duration probe
```

An alternative Step 63 is a 32^3 moving-boundary link-area 1-step comparison, but it should not be combined with a longer duration in the same step.
