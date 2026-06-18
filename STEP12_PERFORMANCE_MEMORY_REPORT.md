# Step 12 Performance, Memory, and Artifact Hygiene Report

## 1. Goal

Establish performance timing, memory estimates, artifact manifest, and no-physics regression checks for the Step 10 unified FSI driver.

Step 12 adds performance and artifact hygiene scaffolding.
Step 12 does not add new FSI physics.
Step 12 does not change solver behavior.

## 2. Files

Created:

- `src/performance.py`
- `src/artifact_utils.py`
- `docs/10_performance_memory.md`
- `docs/11_artifact_policy.md`
- `configs/step12_profile_none.json`
- `configs/step12_profile_penalty.json`
- `configs/step12_profile_moving_boundary.json`
- `baseline_tests/run_step12_memory_estimate.py`
- `baseline_tests/run_step12_driver_profile_matrix.py`
- `baseline_tests/run_step12_artifact_manifest.py`
- `baseline_tests/run_step12_no_physics_regression.py`
- `tests/test_step12_performance_memory_contract.py`
- `STEP12_PERFORMANCE_MEMORY_REPORT.md`

Updated:

- `README.md`
- `docs/08_roadmap.md`
- `.gitignore`

Generated:

- `logs/step12_memory_estimate.log`
- `logs/step12_profile_matrix.log`
- `logs/step12_artifact_manifest.log`
- `logs/step12_no_physics_regression.log`
- `logs/step12_pytest.log`
- `outputs/step12_memory_estimate/`
- `outputs/step12_profile_matrix/`
- `outputs/step12_artifact_manifest/`
- `outputs/step12_no_physics_regression/`

## 3. Explicit Non-Goals

Step 12 does not implement:

- new FSI physics
- two-phase flow
- contact angle physics
- squid geometry
- sparse storage
- ReducedSquidFSI
- external/taichi_LBM3D edits
- production-grade optimization

## 4. Memory Estimate Baseline

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step12_memory_estimate.py
```

Result:

| n_grid | n_particles | total_estimated_mb |
| -----: | ----------: | -----------------: |
| 32 | 4096 | 8.046875 |
| 64 | 32768 | 64.375000 |
| 96 | 110592 | 217.265625 |
| 128 | 262144 | 515.000000 |

## 5. Driver Profile Matrix

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step12_driver_profile_matrix.py
```

Result:

| mode | total_time | projection_time | coupling_time | lbm_step_time | mpm_substep_time |
| ---- | ---------: | --------------: | ------------: | ------------: | ---------------: |
| none | 6.917063930e+01 | 7.172903999e-01 | 0.000000000e+00 | 3.315308700e+00 | 2.560219300e+00 |
| penalty | 4.176673150e+01 | 7.542968001e-01 | 2.239187000e-01 | 3.341393600e+00 | 3.819050200e+00 |
| moving_boundary | 4.517759770e+01 | 7.380417000e-01 | 5.759623000e-01 | 4.187514900e+00 | 3.869418200e+00 |

## 6. Artifact Manifest

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step12_artifact_manifest.py
```

Result:

```text
file_count = 318
total_size_bytes = 80178232
total_size_mb = 76.463921
large_file_count = 0
```

## 7. No-Physics Regression

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step12_no_physics_regression.py
```

Result:

| mode | projection_zone_ux_final | cell_force_max_norm | hydro_force_max_norm | bb_link_count | rho_min | rho_max |
| ---- | -----------------------: | ------------------: | -------------------: | ------------: | ------: | ------: |
| none | 0.000000000e+00 | 0.000000000e+00 | 0.000000000e+00 | 0 | 1.000000358e+00 | 1.000000358e+00 |
| penalty | 2.196828973e-05 | 1.982891990e-05 | 1.982891990e-05 | 0 | 9.999848604e-01 | 1.000016212e+00 |
| moving_boundary | 1.271677669e-03 | 0.000000000e+00 | 4.022144675e-01 | 2322 | 9.684749842e-01 | 1.029817462e+00 |

Trend preserved:

```text
projection_zone_ux_final(moving_boundary) > projection_zone_ux_final(penalty) > projection_zone_ux_final(none)
```

## 8. Documentation Updates

- `README.md` links Step 12 performance and artifact docs.
- `docs/08_roadmap.md` marks Step 12 as completed and keeps Step 13 as geometry ingestion / squid proxy geometry.
- `docs/10_performance_memory.md` documents memory assumptions and profile scope.
- `docs/11_artifact_policy.md` documents committed, scratch, and heavy experiment artifacts.

## 9. Verification

RED evidence:

```text
pytest after adding tests/test_step12_performance_memory_contract.py:
9 failed, 55 passed
Failure reason: required Step 12 artifacts did not exist yet.
```

Final verification:

```text
& 'D:\working\taichi\env\python.exe' -m pytest -q
64 passed
```

## 10. GitHub Sync

Final commit hash:

```text
Recorded in final response after commit and push.
```

Remote branch:

```text
origin/main
```

## 11. Acceptance Checklist

- [x] main is on the Step 12 final commit
- [x] src/performance.py exists
- [x] src/artifact_utils.py exists
- [x] docs/10_performance_memory.md exists
- [x] docs/11_artifact_policy.md exists
- [x] .gitignore exists and ignores tmp/scratch/experiments
- [x] configs/step12_profile_none.json exists
- [x] configs/step12_profile_penalty.json exists
- [x] configs/step12_profile_moving_boundary.json exists
- [x] baseline_tests/run_step12_memory_estimate.py exists
- [x] baseline_tests/run_step12_driver_profile_matrix.py exists
- [x] baseline_tests/run_step12_artifact_manifest.py exists
- [x] baseline_tests/run_step12_no_physics_regression.py exists
- [x] memory_estimate.csv exists
- [x] memory_estimate.npz exists
- [x] memory estimate values are finite
- [x] memory estimate total increases monotonically with n_grid
- [x] profile_matrix.csv exists
- [x] profile_matrix.npz exists
- [x] none / penalty / moving_boundary profiles complete
- [x] artifact_manifest.csv exists
- [x] artifact_summary.json exists
- [x] no-physics regression passes
- [x] Step 10 mode trend is preserved
- [x] rho_min > 0.95
- [x] rho_max < 1.05
- [x] lbm_max_v < 0.1
- [x] mpm_min_J > 0
- [x] no NaN
- [x] no Inf
- [x] no new FSI physics
- [x] no two-phase flow
- [x] no contact angle physics
- [x] no ReducedSquidFSI
- [x] no external/taichi_LBM3D edits
- [x] README links Step 12 docs
- [x] docs/08_roadmap.md updated
- [x] STEP12_PERFORMANCE_MEMORY_REPORT.md complete
- [x] tests/test_step12_performance_memory_contract.py exists
- [x] pytest -q passes
- [x] logs/step12_pytest.log exists
- [x] Step 12 artifacts are committed
- [x] Step 12 artifacts are pushed to GitHub

## 12. Decision

Can proceed to Step 13?

- [x] Yes
- [ ] No
