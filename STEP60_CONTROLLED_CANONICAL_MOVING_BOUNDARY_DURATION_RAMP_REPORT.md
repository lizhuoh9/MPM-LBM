# Step 60 Controlled Canonical Moving-Boundary Duration Ramp Report

## Goal

Step 60 extends the Step 59 canonical-driver real smoke result from one LBM step to a short controlled duration ramp.

The duration ramp imports and runs the canonical driver implementation:

```python
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D
driver.run()
```

This is a controlled canonical real-driver duration ramp and a finite/bounded smoke extension. It is not a broader solver validation campaign.

## Runtime Vs Diagnostic Boundary

Step 60 runs existing driver modes only. It does not change runtime solver code, stepping formulas, moving-boundary formulas, geometry motion behavior, wall-velocity behavior, or optional bridge ownership.

The matrix policy records:

| Flag | Value |
| --- | --- |
| `runtime_code_changed` | false |
| `solver_behavior_changed` | false |
| `physics_feature_expansion` | false |
| `run_optional_32_probe` | false |

## Files Created And Updated

Created:

- `STEP60_CONTROLLED_CANONICAL_MOVING_BOUNDARY_DURATION_RAMP_GOAL.md`
- `STEP60_CONTROLLED_CANONICAL_MOVING_BOUNDARY_DURATION_RAMP_REPORT.md`
- `docs/60_controlled_canonical_moving_boundary_duration_ramp.md`
- `configs/step60_*.json`
- `src/mpm_lbm/evidence/canonical_driver_duration_ramp_runner.py`
- `src/mpm_lbm/evidence/canonical_driver_duration_ramp_audit.py`
- `src/mpm_lbm/evidence/canonical_driver_duration_ramp_output_guard.py`
- `src/mpm_lbm/evidence/step60_regression_guard.py`
- `baseline_tests/step60_common.py`
- `baseline_tests/run_step60_*.py`
- `tests/test_step60_*.py`
- `outputs/step60_*/`
- `logs/step60_*.log`

Updated:

- `README.md`
- `docs/00_project_status.md`

## Explicit Non-Goals

Step 60 does not activate runtime geometry, wall-velocity application, geometry motion, prescribed boundary motion, 48^3 or 64^3 rows, long-duration rows, required link-area rows, real geometry, propulsion validation, real squid behavior validation, mesh-convergence proof, viscosity/tau migration, VTR output, particle NPY output, external solver edits, real-geometry candidate edits, or deployment-readiness claims.

## Required Configs

Required row configs:

- `configs/step60_canonical_driver_moving_boundary_engineering_16_3step.json`
- `configs/step60_canonical_driver_moving_boundary_engineering_16_5step.json`
- `configs/step60_canonical_driver_penalty_16_5step.json`

Optional row config, disabled by default:

- `configs/step60_canonical_driver_moving_boundary_engineering_32_1step_optional.json`

Policies:

- `configs/step60_controlled_canonical_moving_boundary_duration_ramp.json`
- `configs/step60_duration_ramp_acceptance_policy.json`
- `configs/step60_output_guard_policy.json`

## Duration Ramp Matrix

| Row | Mode | Grid | Particles | LBM steps | Diagnostics rows | Stable | Elapsed seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `canonical_driver_moving_boundary_engineering_16_3step` | `moving_boundary` | 16^3 | 512 | 3 | 4 | true | 115.28821250000328 |
| `canonical_driver_moving_boundary_engineering_16_5step` | `moving_boundary` | 16^3 | 512 | 5 | 6 | true | 299.3498921999999 |
| `canonical_driver_penalty_16_5step` | `penalty` | 16^3 | 512 | 5 | 6 | true | 215.405316999997 |

Matrix summary:

| Metric | Value |
| --- | --- |
| `duration_ramp_matrix_pass` | true |
| `required_stable_count` | 3 |
| `driver_run_called_count` | 3 |
| `legacy_driver_module_used_count` | 0 |
| `has_nan_count` | 0 |
| `has_inf_count` | 0 |
| `min_rho_min` | 0.9671249985694885 |
| `max_rho_max` | 1.0341906547546387 |
| `max_lbm_max_v` | 0.027245832607150078 |
| `min_mpm_min_J` | 0.9998660087585449 |

## Duration Ramp Quality

The quality audit confirms:

- all required rows are present
- all rows used `src.mpm_lbm.sim.drivers.fsi_driver`
- all rows called the real driver run path
- all rows stayed finite under the Step 60 bounds
- no row used the legacy root driver implementation as owner

The committed quality artifact is:

- `outputs/step60_duration_ramp_quality/duration_ramp_quality.json`

## Runtime Timing Summary

Total measured row runtime:

```text
630.0434217000002 seconds
```

Slowest row:

```text
canonical_driver_moving_boundary_engineering_16_5step
299.3498921999999 seconds
```

Runtime warning count:

```text
0
```

The 5-step moving-boundary row stayed below the 1800-second soft warning threshold.

## Output Guard

The Step 60 output guard reports:

| Metric | Value |
| --- | --- |
| `output_guard_pass` | true |
| `step60_required_driver_run_dir_count` | 3 |
| `step60_optional_driver_run_dir_count` | 0 |
| `step60_vtr_count` | 0 |
| `step60_particle_npy_count` | 0 |
| `step60_large_file_count` | 0 |
| `step60_forbidden_file_count` | 0 |
| `private_absolute_path_count` | 0 |
| `external_edit_count` | 0 |
| `real_geometry_candidates_edit_count` | 0 |
| `step60_total_size_mb` | 0.09174537658691406 |

Each driver run directory contains only lightweight files:

- `driver_config.json`
- `geo_all_fluid_16.dat`
- `diagnostics_timeseries.csv`
- `diagnostics_timeseries.npz`

## Step59 Regression Guard

The Step 60 regression guard confirms Step 59 remains green:

- Step 59 smoke matrix pass
- Step 59 smoke quality pass
- Step 59 geo path naming pass
- Step 59 output guard pass
- Step 59 Step 58 regression guard pass
- Step 59 artifact manifest pass
- required Step 59 rows still present
- canonical driver module count remains 3
- legacy driver implementation count remains 0

The committed regression artifact is:

- `outputs/step60_step59_regression_guard/step59_regression_guard.json`

## Artifact Manifest

The Step 60 artifact manifest is generated by:

```text
baseline_tests/run_step60_artifact_manifest.py
```

The committed manifest artifacts are:

- `outputs/step60_artifact_manifest/artifact_manifest.csv`
- `outputs/step60_artifact_manifest/artifact_summary.csv`
- `outputs/step60_artifact_manifest/artifact_summary.json`

Manifest summary:

| Metric | Value |
| --- | --- |
| `artifact_budget_pass` | true |
| `step60_file_count` | 53 |
| `step60_total_size_mb` | 0.4922046661376953 |
| `large_file_count` | 0 |
| `step60_vtr_count` | 0 |
| `step60_particle_npy_count` | 0 |
| `protected_external_taichi_lbm3d_step60_file_count` | 0 |
| `protected_real_geometry_candidates_step60_file_count` | 0 |

## Verification Commands

```powershell
D:\working\taichi\env\python.exe -m py_compile src\mpm_lbm\evidence\canonical_driver_duration_ramp_runner.py src\mpm_lbm\evidence\canonical_driver_duration_ramp_audit.py src\mpm_lbm\evidence\canonical_driver_duration_ramp_output_guard.py src\mpm_lbm\evidence\step60_regression_guard.py baseline_tests\step60_common.py baseline_tests\run_step60_duration_ramp_matrix.py baseline_tests\run_step60_duration_ramp_quality.py baseline_tests\run_step60_output_guard.py baseline_tests\run_step60_step59_regression_guard.py baseline_tests\run_step60_artifact_manifest.py tests\test_step60_duration_ramp_contract.py tests\test_step60_duration_ramp_quality_contract.py tests\test_step60_output_guard_contract.py tests\test_step60_step59_regression_contract.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step60_step59_regression_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step60_duration_ramp_matrix.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step60_duration_ramp_quality.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step60_output_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step60_artifact_manifest.py
D:\working\taichi\env\python.exe -W ignore -m pytest -q tests/test_step60_duration_ramp_contract.py tests/test_step60_duration_ramp_quality_contract.py tests/test_step60_output_guard_contract.py tests/test_step60_step59_regression_contract.py
D:\working\taichi\env\python.exe -W ignore -m pytest -q
D:\TOOL\Anaconda\python.exe -W ignore -m pytest -q
```

## Acceptance Checklist

- [x] Detailed Step 60 goal file exists and the active goal references it.
- [x] Required configs are checked in.
- [x] Required duration ramp rows call the canonical `FSIDriver3D(...).run()` path.
- [x] Required rows complete 3/5 LBM steps with expected diagnostics row counts.
- [x] Required rows are finite and bounded under Step 60 policy.
- [x] Runtime code remains unchanged.
- [x] Optional 32^3 row is defined but disabled by default.
- [x] Output guard rejects heavy and private-path artifacts.
- [x] Step 59 regression guard passes.
- [x] External solver and real-geometry candidate directories remain unmodified.

## Decision For Step61

The Step 60 16^3 / 5-step moving-boundary row is stable and below the 1800-second runtime warning threshold. The conservative Step 61 direction is therefore a controlled 32^3 canonical moving-boundary short simulation, starting with 1 step and only expanding to 3 steps if the first row is stable and runtime remains manageable.

Step 61 should still avoid combining larger grid, runtime geometry, wall velocity, and longer duration in one step.
