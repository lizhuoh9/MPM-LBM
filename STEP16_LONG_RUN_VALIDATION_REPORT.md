# Step 16 Long-Run Validation Report

## 1. Goal

Step 16 does not add new FSI physics. It uses the Step 15 calibrated moving_boundary settings to run longer 48^3 stability baselines and a conservative 64^3 moving_boundary feasibility baseline.

The 64^3 moving_boundary row is a feasibility baseline. squid_proxy is procedural and not real squid validation. Strict link-area momentum-conserving coupling remains future work.

## 2. Files

Added:

- `configs/step16_long_box_48_moving_boundary.json`
- `configs/step16_long_squid_proxy_48_moving_boundary.json`
- `configs/step16_feasibility_64_moving_boundary_box.json`
- `configs/step16_compare_64_modes.json`
- `baseline_tests/step16_common.py`
- `baseline_tests/run_step16_long_box_48_moving_boundary.py`
- `baseline_tests/run_step16_long_squid_proxy_48_moving_boundary.py`
- `baseline_tests/run_step16_feasibility_64_moving_boundary.py`
- `baseline_tests/run_step16_64_mode_comparison.py`
- `baseline_tests/run_step16_long_run_summary.py`
- `baseline_tests/run_step16_artifact_manifest.py`
- `docs/15_long_run_validation.md`
- `tests/test_step16_long_run_validation_contract.py`

Updated:

- `README.md`
- `docs/08_roadmap.md`
- `docs/10_performance_memory.md`
- `docs/13_larger_grid_validation.md`
- `docs/14_moving_boundary_calibration.md`

## 3. Explicit Non-Goals

No solver physics was changed. Step 16 does not change the Step 8 moving bounce-back formula, Step 9 moving-boundary reaction transfer, `PenaltyFSICoupler3D`, `MovingBoundaryFSICoupler3D`, `FSIDriver3D.step_once()`, or `external/taichi_LBM3D`.

Step 16 does not implement two-phase flow, contact angle physics, sparse storage, real squid validation, squid actuation, swimming locomotion, mesh import, or final sharp-interface FSI.

## 4. Baseline Results

| case | mode | n_grid | particles | LBM steps | MPM substeps | rho_min | rho_max | lbm_max_v | mpm_min_J | cell_force_max_norm | bb_link_count_min |
| ---- | ---- | -----: | --------: | --------: | -----------: | ------: | ------: | --------: | --------: | ------------------: | ----------------: |
| long box 48 | moving_boundary | 48 | 13824 | 50 | 500 | 0.988891482 | 1.017282963 | 0.012052457 | 0.992399573 | 0.000000000 | 5964 |
| long squid_proxy 48 | moving_boundary | 48 | 4096 | 30 | 300 | 0.991026938 | 1.012060523 | 0.007719210 | 0.993878663 | 0.000000000 | 6616 |
| feasibility box 64 | moving_boundary | 64 | 32768 | 5 | 25 | 0.992273271 | 1.002777219 | 0.005351932 | 0.995547831 | 0.000000000 | 11186 |
| mode compare 64 | none | 64 | 32768 | 5 | 25 | 1.000000000 | 1.000000358 | 0.000000000 | 0.999999702 | 0.000000000 | 0 |
| mode compare 64 | penalty | 64 | 32768 | 5 | 25 | 0.999999285 | 1.000001550 | 0.000002630 | 0.999998987 | 0.000002490 | 0 |
| mode compare 64 | moving_boundary | 64 | 32768 | 5 | 25 | 0.992273331 | 1.002777338 | 0.005351928 | 0.995547831 | 0.000000000 | 11186 |

All rows passed the Step 16 stability thresholds:

```text
rho_min_global > 0.95
rho_max_global < 1.05
lbm_max_v_global < 0.1
mpm_min_J_global > 0
mpm_max_speed_global < 10
```

## 5. Commands

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step16_long_box_48_moving_boundary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step16_long_squid_proxy_48_moving_boundary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step16_feasibility_64_moving_boundary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step16_64_mode_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step16_long_run_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step16_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
```

## 6. Outputs

Main outputs:

- `outputs/step16_long_box_48_moving_boundary/long_run_summary.json`
- `outputs/step16_long_squid_proxy_48_moving_boundary/long_run_summary.json`
- `outputs/step16_feasibility_64_moving_boundary/long_run_summary.json`
- `outputs/step16_feasibility_64_moving_boundary/box_64_moving_boundary_results.csv`
- `outputs/step16_64_mode_comparison/mode_64_results.csv`
- `outputs/step16_long_run_summary/step16_summary.csv`
- `outputs/step16_long_run_summary/step16_summary.json`

## 7. Artifact Manifest

Artifact manifest is generated at:

```text
outputs/step16_artifact_manifest/artifact_manifest.csv
outputs/step16_artifact_manifest/artifact_summary.json
```

The final artifact counts are recorded after the manifest script is rerun.

Artifact summary:

```text
file_count = 545
total_size_bytes = 94122877
total_size_mb = 89.762570
large_file_count = 0
```

## 8. Verification

Required baselines completed with GPU Taichi initialization:

- `logs/step16_long_box_48_moving_boundary.log`
- `logs/step16_long_squid_proxy_48_moving_boundary.log`
- `logs/step16_feasibility_64_moving_boundary.log`
- `logs/step16_64_mode_comparison.log`
- `logs/step16_long_run_summary.log`

Final pytest result is recorded in `logs/step16_pytest.log`.

`external/taichi_LBM3D` remained unchanged.

## 9. GitHub Sync

Final commit hash is reported after commit creation. Remote branch after push: `origin/main`.

## 10. Acceptance Checklist

- [x] main is on the Step 16 final commit
- [x] configs/step16_long_box_48_moving_boundary.json exists
- [x] configs/step16_long_squid_proxy_48_moving_boundary.json exists
- [x] configs/step16_feasibility_64_moving_boundary_box.json exists
- [x] configs/step16_compare_64_modes.json exists
- [x] baseline_tests/step16_common.py exists
- [x] 48^3 box moving_boundary long-run passes
- [x] 48^3 squid_proxy moving_boundary long-run passes
- [x] 64^3 moving_boundary feasibility passes
- [x] 64^3 mode comparison passes
- [x] step16_summary.csv exists
- [x] step16_summary.json exists
- [x] artifact manifest exists
- [x] rho_min_global > 0.95 for all stable rows
- [x] rho_max_global < 1.05 for all stable rows
- [x] lbm_max_v_global < 0.1 for all stable rows
- [x] mpm_min_J_global > 0 for all stable rows
- [x] mpm_max_speed_global < 10 for all stable rows
- [x] moving_boundary rows have bb_link_count_min > 0
- [x] moving_boundary rows keep cell_force_max_norm == 0
- [x] no NaN
- [x] no Inf
- [x] write_vtk is false in required Step 16 configs
- [x] write_particles is false in required Step 16 configs
- [x] no new FSI physics
- [x] no two-phase flow
- [x] no contact angle physics
- [x] no real squid validation claims
- [x] no sparse storage implementation
- [x] no ReducedSquidFSI
- [x] no external/taichi_LBM3D edits
- [x] docs/15_long_run_validation.md exists
- [x] README.md updated conservatively
- [x] docs/08_roadmap.md updated
- [x] docs/10_performance_memory.md updated
- [x] docs/13_larger_grid_validation.md updated
- [x] docs/14_moving_boundary_calibration.md updated
- [x] STEP16_LONG_RUN_VALIDATION_REPORT.md complete
- [x] tests/test_step16_long_run_validation_contract.py exists
- [x] pytest -q passes
- [x] logs/step16_pytest.log exists
- [x] git diff --check passes
- [x] Step 16 artifacts are committed
- [x] Step 16 artifacts are pushed to GitHub

## 11. Decision

Can proceed to the next step?

- [x] Yes
- [ ] No
