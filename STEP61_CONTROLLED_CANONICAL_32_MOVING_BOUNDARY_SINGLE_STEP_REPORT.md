# Step 61 Controlled Canonical 32 Moving-Boundary Single-Step Report

## Goal

Step 61 expands exactly one dimension from Step 60:

```text
grid: 16^3 -> 32^3
duration: 1 LBM step
mode: moving_boundary engineering
```

The probe imports and runs the canonical driver implementation:

```python
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D
driver.run()
```

This is a controlled canonical 32^3 real-driver single-step probe and a finite/bounded feasibility smoke. It is not a broader solver validation campaign.

## Runtime Vs Diagnostic Boundary

Step 61 runs the existing canonical moving-boundary engineering path only. It does not change runtime solver code, stepping formulas, moving-boundary formulas, geometry motion behavior, wall-velocity behavior, or optional bridge ownership.

The matrix policy records:

| Flag | Value |
| --- | --- |
| `runtime_code_changed` | false |
| `solver_behavior_changed` | false |
| `physics_feature_expansion` | false |
| `run_optional_penalty_32_probe` | false |
| `run_optional_32_3step_probe` | false |

## Files Created And Updated

Created:

- `STEP61_CONTROLLED_CANONICAL_32_MOVING_BOUNDARY_SINGLE_STEP_GOAL.md`
- `STEP61_CONTROLLED_CANONICAL_32_MOVING_BOUNDARY_SINGLE_STEP_REPORT.md`
- `docs/61_controlled_canonical_32_moving_boundary_single_step.md`
- `configs/step61_*.json`
- `src/mpm_lbm/evidence/canonical_driver_32_probe_runner.py`
- `src/mpm_lbm/evidence/canonical_driver_32_probe_audit.py`
- `src/mpm_lbm/evidence/canonical_driver_32_probe_output_guard.py`
- `src/mpm_lbm/evidence/step61_regression_guard.py`
- `baseline_tests/step61_common.py`
- `baseline_tests/run_step61_*.py`
- `tests/test_step61_*.py`
- `outputs/step61_*/`
- `logs/step61_*.log`

Updated:

- `README.md`
- `docs/00_project_status.md`

## Explicit Non-Goals

Step 61 does not activate runtime geometry, wall-velocity application, geometry motion, prescribed boundary motion, 48^3 or 64^3 rows, required 3-step or 5-step rows, long-duration rows, required link-area rows, real geometry, propulsion validation, real squid behavior validation, grid-convergence proof, viscosity/tau migration, VTR output, particle NPY output, external solver edits, real-geometry candidate edits, runtime solver code changes, or deployment-readiness claims.

## Required Configs

Required row config:

- `configs/step61_canonical_driver_moving_boundary_engineering_32_1step.json`

Optional row configs, disabled by default:

- `configs/step61_canonical_driver_penalty_32_1step_optional.json`
- `configs/step61_canonical_driver_moving_boundary_engineering_32_3step_optional.json`

Policies:

- `configs/step61_controlled_canonical_32_moving_boundary_single_step.json`
- `configs/step61_single_step_acceptance_policy.json`
- `configs/step61_output_guard_policy.json`
- `configs/step61_runtime_budget_policy.json`

## 32^3 Single-Step Matrix

| Row | Mode | Grid | Particles | LBM steps | Diagnostics rows | Stable | Elapsed seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `canonical_driver_moving_boundary_engineering_32_1step` | `moving_boundary` | 32^3 | 1024 | 1 | 2 | true | 216.48096530001203 |

Matrix summary:

| Metric | Value |
| --- | --- |
| `probe_32_matrix_pass` | true |
| `required_stable_count` | 1 |
| `driver_run_called_count` | 1 |
| `legacy_driver_module_used_count` | 0 |
| `has_nan_count` | 0 |
| `has_inf_count` | 0 |
| `min_rho_min` | 0.980000376701355 |
| `max_rho_max` | 1.0200003385543823 |
| `max_lbm_max_v` | 0.020408157259225845 |
| `min_mpm_min_J` | 0.9999732971191406 |
| `bb_link_count_max` | 2272 |

## 32^3 Probe Quality

The quality audit confirms:

- the required 32^3 row is present
- the row used `src.mpm_lbm.sim.drivers.fsi_driver`
- the row called the real driver run path
- the row stayed finite under the Step 61 bounds
- the row produced `geo_all_fluid_32.dat`
- no legacy root driver implementation owns the run

The committed quality artifact is:

- `outputs/step61_32_probe_quality/probe_32_quality.json`

## Runtime Timing Summary

Measured runtime:

```text
216.48096530001203 seconds
```

Runtime warning count:

```text
0
```

The required 32^3 row stayed below the 3600-second soft warning threshold.

The Taichi run emitted offline-cache lock warnings after the successful matrix result. These warnings did not prevent the row from completing or artifacts from being written.

## Output Guard

The Step 61 output guard reports:

| Metric | Value |
| --- | --- |
| `output_guard_pass` | true |
| `step61_required_driver_run_dir_count` | 1 |
| `step61_optional_driver_run_dir_count` | 0 |
| `step61_vtr_count` | 0 |
| `step61_particle_npy_count` | 0 |
| `step61_large_file_count` | 0 |
| `step61_forbidden_file_count` | 0 |
| `private_absolute_path_count` | 0 |
| `external_edit_count` | 0 |
| `real_geometry_candidates_edit_count` | 0 |
| `step61_total_size_mb` | 0.11867237091064453 |

The required driver run directory contains only:

- `driver_config.json`
- `geo_all_fluid_32.dat`
- `diagnostics_timeseries.csv`
- `diagnostics_timeseries.npz`

## Step60 Regression Guard

The Step 61 regression guard confirms Step 60 remains green:

- Step 60 duration ramp matrix pass
- Step 60 duration ramp quality pass
- Step 60 output guard pass
- Step 60 Step 59 regression guard pass
- Step 60 artifact manifest pass
- Step 60 required rows still present
- Step 60 legacy driver implementation count remains 0
- Step 60 runtime code changed remains false
- Step 60 solver behavior changed remains false
- Step 60 physics feature expansion remains false

The committed regression artifact is:

- `outputs/step61_step60_regression_guard/step60_regression_guard.json`

## Artifact Manifest

The Step 61 artifact manifest is generated by:

```text
baseline_tests/run_step61_artifact_manifest.py
```

The committed manifest artifacts are:

- `outputs/step61_artifact_manifest/artifact_manifest.csv`
- `outputs/step61_artifact_manifest/artifact_summary.csv`
- `outputs/step61_artifact_manifest/artifact_summary.json`

Manifest summary:

| Metric | Value |
| --- | --- |
| `artifact_budget_pass` | true |
| `step61_file_count` | 45 |
| `step61_total_size_mb` | 0.5198221206665039 |
| `large_file_count` | 0 |
| `step61_vtr_count` | 0 |
| `step61_particle_npy_count` | 0 |
| `protected_external_taichi_lbm3d_step61_file_count` | 0 |
| `protected_real_geometry_candidates_step61_file_count` | 0 |

## Verification Commands

```powershell
D:\working\taichi\env\python.exe -m py_compile src\mpm_lbm\evidence\canonical_driver_32_probe_runner.py src\mpm_lbm\evidence\canonical_driver_32_probe_audit.py src\mpm_lbm\evidence\canonical_driver_32_probe_output_guard.py src\mpm_lbm\evidence\step61_regression_guard.py baseline_tests\step61_common.py baseline_tests\run_step61_32_probe_matrix.py baseline_tests\run_step61_32_probe_quality.py baseline_tests\run_step61_output_guard.py baseline_tests\run_step61_step60_regression_guard.py baseline_tests\run_step61_artifact_manifest.py tests\test_step61_32_probe_contract.py tests\test_step61_32_probe_quality_contract.py tests\test_step61_output_guard_contract.py tests\test_step61_step60_regression_contract.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step61_step60_regression_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step61_32_probe_matrix.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step61_32_probe_quality.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step61_output_guard.py
D:\working\taichi\env\python.exe -W ignore baseline_tests\run_step61_artifact_manifest.py
D:\working\taichi\env\python.exe -W ignore -m pytest -q tests/test_step61_32_probe_contract.py tests/test_step61_32_probe_quality_contract.py tests/test_step61_output_guard_contract.py tests/test_step61_step60_regression_contract.py
D:\working\taichi\env\python.exe -W ignore -m pytest -q
D:\TOOL\Anaconda\python.exe -W ignore -m pytest -q
```

## Acceptance Checklist

- [x] Detailed Step 61 goal file exists and the active goal references it.
- [x] Required configs are checked in.
- [x] Required 32^3 row calls the canonical `FSIDriver3D(...).run()` path.
- [x] Required row completes 1 LBM step with 2 diagnostics rows.
- [x] Required row is finite and bounded under Step 61 policy.
- [x] Runtime code remains unchanged.
- [x] Optional 32^3 rows are defined but disabled by default.
- [x] Output guard rejects heavy and private-path artifacts.
- [x] Step 60 regression guard passes.
- [x] External solver and real-geometry candidate directories remain unmodified.

## Decision For Step62

The Step 61 32^3 / 1-step moving-boundary row is stable and below the 3600-second runtime warning threshold. The conservative Step 62 direction is therefore a 32^3 canonical moving-boundary 3-step duration probe, provided it remains the only expansion dimension.

Step 62 should still avoid combining larger grid, runtime geometry, wall velocity, link-area comparison, and longer duration in one step.
