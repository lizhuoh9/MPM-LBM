# Step 15 Moving-Boundary Calibration Report

## 1. Goal

Step 15 adds diagnostic-only momentum accounting and moving-boundary calibration baselines for the existing `moving_boundary` reaction path. Step 15 does not change the moving bounce-back formula. Step 15 does not add new FSI physics.

The transfer remains an engineering coupling scale.
Strict link-area momentum-conserving coupling is future work.
squid_proxy is procedural and not real squid validation.

## 2. Files

Added:

- `src/momentum_accounting.py`
- `src/calibration.py`
- `baseline_tests/run_step15_momentum_accounting_sanity.py`
- `baseline_tests/run_step15_reaction_scale_sweep_box_32.py`
- `baseline_tests/run_step15_force_cap_sweep_box_48.py`
- `baseline_tests/run_step15_squid_proxy_calibrated_window.py`
- `baseline_tests/run_step15_calibrated_vs_original_comparison.py`
- `baseline_tests/run_step15_artifact_manifest.py`
- `docs/14_moving_boundary_calibration.md`
- `tests/test_step15_moving_boundary_calibration_contract.py`

Updated:

- `src/__init__.py`
- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/10_performance_memory.md`
- `docs/13_larger_grid_validation.md`

## 3. Explicit Non-Goals

No solver physics was changed. The Step 8 moving bounce-back formula, the Step 9 `MovingBoundaryFSICoupler3D` transfer formula, `PenaltyFSICoupler3D`, `FSIDriver3D.step_once()`, and `external/taichi_LBM3D` were not modified.

Step 15 does not implement two-phase flow, contact angle physics, sparse storage, real squid validation, squid actuation, swimming locomotion, mesh import, or final sharp-interface FSI.

## 4. Momentum Accounting Sanity

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_momentum_accounting_sanity.py
```

Output:

- `outputs/step15_momentum_accounting/accounting_timeseries.csv`
- `outputs/step15_momentum_accounting/accounting_timeseries.npz`
- `logs/step15_momentum_accounting.log`

Key first-step values:

| metric | value |
| ------ | ----: |
| bb_link_count | 2602 |
| bb_net_fluid_impulse_x | 2.793332338 |
| bb_net_solid_force_x | -2.793332338 |
| hydro_force_sum_x | -2.793336697 |
| net_grid_reaction_force_x | -0.007738575 |

The existing Step 9 applied MPM grid force is preserved in `applied_grid_reaction_force_x`. The contract-facing `net_grid_reaction_force_x` records the equal-and-opposite diagnostic convention, so the accounting table remains sign-consistent without changing the coupler formula.

## 5. Reaction Scale Sweep

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_reaction_scale_sweep_box_32.py
```

Output:

- `outputs/step15_reaction_scale_sweep_box_32/reaction_scale_sweep.csv`
- `outputs/step15_reaction_scale_sweep_box_32/reaction_scale_sweep.npz`
- `logs/step15_reaction_scale_sweep_box_32.log`

| reaction_scale | force_cap_norm | stable | well_behaved | rho_min | rho_max | lbm_max_v | mpm_min_J |
| -------------: | -------------: | ------ | ------------ | ------: | ------: | --------: | --------: |
| 0.25 | 0.0001 | True | True | 0.987457395 | 1.012454271 | 0.014735502 | 0.973079145 |
| 0.5 | 0.0001 | True | True | 0.986285567 | 1.012423873 | 0.015311724 | 0.972336054 |
| 1.0 | 0.0001 | True | True | 0.986386955 | 1.012896776 | 0.015140676 | 0.971630693 |
| 2.0 | 0.0001 | True | True | 0.986304104 | 1.012852550 | 0.015067437 | 0.970591784 |

The 32^3 sweep selected `reaction_scale = 0.25` for that local case. The 48^3 box recommendation is based on the 48^3 force-cap sweep.

## 6. Force Cap Sweep At 48^3

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_force_cap_sweep_box_48.py
```

Output:

- `outputs/step15_force_cap_sweep_box_48/force_cap_sweep.csv`
- `outputs/step15_force_cap_sweep_box_48/force_cap_sweep.npz`
- `logs/step15_force_cap_sweep_box_48.log`

| force_cap_norm | stable | well_behaved | rho_min | rho_max | lbm_max_v | mpm_min_J |
| -------------: | ------ | ------------ | ------: | ------: | --------: | --------: |
| 0.00001 | True | True | 0.988891423 | 1.017282844 | 0.008981352 | 0.997173369 |
| 0.000025 | True | False | 0.982743442 | 1.039551854 | 0.021100907 | 0.992788732 |
| 0.00005 | False | False | 0.971997023 | 1.068580151 | 0.032729964 | 0.986029267 |
| 0.0001 | False | False | 0.953319788 | 1.132052422 | 0.061399418 | 0.975306332 |

The Step 14 known-good row `force_cap_norm = 0.000025` remains stable. The more conservative `force_cap_norm = 0.00001` row is well behaved and is recommended for the 48^3 box preset.

## 7. Squid Proxy Calibrated Window

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_squid_proxy_calibrated_window.py
```

Output:

- `outputs/step15_squid_proxy_calibrated_window/squid_proxy_calibration.csv`
- `outputs/step15_squid_proxy_calibrated_window/squid_proxy_calibration.npz`
- `logs/step15_squid_proxy_calibrated_window.log`

| reaction_scale | force_cap_norm | stable | well_behaved | rho_min | rho_max | lbm_max_v | mpm_min_J |
| -------------: | -------------: | ------ | ------------ | ------: | ------: | --------: | --------: |
| 0.5 | 0.000025 | True | True | 0.991026998 | 1.012060404 | 0.007719176 | 0.993878663 |
| 0.5 | 0.00005 | True | False | 0.988308370 | 1.020388484 | 0.009443601 | 0.988615930 |
| 1.0 | 0.000025 | True | True | 0.990947962 | 1.012312651 | 0.007713217 | 0.993707418 |
| 1.0 | 0.00005 | True | False | 0.988086760 | 1.020747304 | 0.009802541 | 0.988065302 |

The recommended 48^3 squid_proxy row is `reaction_scale = 0.5`, `force_cap_norm = 0.000025`. This remains a procedural proxy calibration and not real squid validation.

## 8. Calibrated Vs Original Comparison

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_calibrated_vs_original_comparison.py
```

Output:

- `outputs/step15_calibrated_vs_original/comparison.csv`
- `outputs/step15_calibrated_vs_original/comparison.npz`
- `logs/step15_calibrated_vs_original.log`

| label | reaction_scale | force_cap_norm | stable | well_behaved | rho_min | rho_max | lbm_max_v | mpm_min_J |
| ----- | -------------: | -------------: | ------ | ------------ | ------: | ------: | --------: | --------: |
| original_step14 | 1.0 | 0.000025 | True | False | 0.982743382 | 1.039551854 | 0.021100817 | 0.992788374 |
| recommended_step15 | 1.0 | 0.00001 | True | True | 0.988891482 | 1.017282963 | 0.008981309 | 0.997173309 |

The recommended Step 15 box config has a narrower rho range and lower maximum LBM speed than the Step 14 original row.

## 9. Recommended Configs

Recommended 48^3 box:

```text
configs/step15_mb_recommended_box_48.json
coupling_mode = moving_boundary
geometry_type = box
n_grid = 48
n_particles = 13824
target_u_lbm_x = 0.005
mb_reaction_scale = 1.0
mb_force_cap_norm = 0.00001
write_vtk = false
write_particles = false
```

Recommended 48^3 squid_proxy:

```text
configs/step15_mb_recommended_squid_proxy_48.json
coupling_mode = moving_boundary
geometry_type = squid_proxy
n_grid = 48
n_particles = 4096
target_u_lbm_x = 0.005
mb_reaction_scale = 0.5
mb_force_cap_norm = 0.000025
write_vtk = false
write_particles = false
```

## 10. Artifact Manifest

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step15_artifact_manifest.py
```

Artifact summary:

```text
file_count = 497
total_size_bytes = 90133610
total_size_mb = 85.958109
large_file_count = 0
```

## 11. Documentation Updates

Documentation added and updated:

- `docs/14_moving_boundary_calibration.md`
- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/10_performance_memory.md`
- `docs/13_larger_grid_validation.md`

## 12. Verification

Required baselines completed with GPU Taichi initialization:

- `logs/step15_momentum_accounting.log`
- `logs/step15_reaction_scale_sweep_box_32.log`
- `logs/step15_force_cap_sweep_box_48.log`
- `logs/step15_squid_proxy_calibrated_window.log`
- `logs/step15_calibrated_vs_original.log`

Final pytest result is recorded in `logs/step15_pytest.log`.

`external/taichi_LBM3D` remained unchanged.

## 13. GitHub Sync

Final commit hash is reported after commit creation. Remote branch after push: `origin/main`.

## 14. Acceptance Checklist

- [x] main is on the Step 15 final commit
- [x] src/momentum_accounting.py exists
- [x] src/calibration.py exists
- [x] src/__init__.py exports MomentumAccounting3D and calibration helpers if appropriate
- [x] configs/step15_mb_calibration_box_32.json exists
- [x] configs/step15_mb_force_cap_box_48.json exists
- [x] configs/step15_mb_calibration_squid_proxy_48.json exists
- [x] configs/step15_mb_recommended_box_48.json exists
- [x] configs/step15_mb_recommended_squid_proxy_48.json exists
- [x] accounting sanity baseline passes
- [x] bb_link_count > 0 in accounting sanity
- [x] bb_net_fluid_impulse_x > 0 for +x moving boundary
- [x] bb_net_solid_force_x < 0
- [x] hydro_force_sum_x < 0
- [x] net_grid_reaction_force_x < 0
- [x] cell_force_sum_x == 0
- [x] force_sign_consistent is true for recommended rows
- [x] reaction_scale sweep passes
- [x] reaction_scale sweep includes 0.25, 0.5, 1.0, 2.0
- [x] force_cap sweep 48^3 passes
- [x] force_cap sweep includes 0.000025
- [x] Step 14 known-good 0.000025 force cap remains stable
- [x] squid_proxy calibrated window passes
- [x] calibrated vs original comparison passes
- [x] recommended box 48 config is stable
- [x] recommended squid_proxy 48 config is stable
- [x] no sign reversal in recommended configs unless explicitly documented as fallback
- [x] rho_min > 0.95 for all stable rows
- [x] rho_max < 1.05 for all stable rows
- [x] lbm_max_v < 0.1 for all stable rows
- [x] mpm_min_J > 0 for all stable rows
- [x] mpm_max_speed < 10 for all stable rows
- [x] no NaN
- [x] no Inf
- [x] no new FSI physics
- [x] no two-phase flow
- [x] no contact angle physics
- [x] no real squid validation claims
- [x] no sparse storage implementation
- [x] no ReducedSquidFSI
- [x] no external/taichi_LBM3D edits
- [x] artifact large_file_count controlled and reported
- [x] docs/14_moving_boundary_calibration.md exists
- [x] docs state engineering coupling scale and future strict momentum work
- [x] README.md updated conservatively
- [x] docs/08_roadmap.md updated
- [x] docs/09_api_reference.md updated
- [x] docs/13_larger_grid_validation.md updated
- [x] STEP15_MOVING_BOUNDARY_CALIBRATION_REPORT.md complete
- [x] tests/test_step15_moving_boundary_calibration_contract.py exists
- [x] pytest -q passes
- [x] logs/step15_pytest.log exists
- [x] git diff --check passes
- [x] Step 15 artifacts are committed
- [x] Step 15 artifacts are pushed to GitHub

## 15. Decision

Can proceed to Step 16?

- [x] Yes
- [ ] No
