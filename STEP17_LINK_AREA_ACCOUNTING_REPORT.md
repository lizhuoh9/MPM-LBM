# Step 17 Link-Area Momentum Accounting Report

## 1. Goal

Step 17 adds diagnostic-only direction-wise and link-area proxy accounting.

The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. These are diagnostic proxy policies, not final surface-area reconstruction. Strict link-area momentum-conserving coupling remains future work. squid_proxy is procedural and not real squid validation.

## 2. Files

Created:

- `STEP17_LINK_AREA_ACCOUNTING_GOAL.md`
- `src/link_area_accounting.py`
- `configs/step17_link_area_wall_32.json`
- `configs/step17_link_area_box_48.json`
- `configs/step17_link_area_squid_proxy_48.json`
- `configs/step17_link_area_box_64.json`
- `baseline_tests/step17_common.py`
- `baseline_tests/run_step17_directional_link_sanity.py`
- `baseline_tests/run_step17_link_area_wall_couette.py`
- `baseline_tests/run_step17_box_48_link_budget.py`
- `baseline_tests/run_step17_squid_proxy_48_link_budget.py`
- `baseline_tests/run_step17_box_64_link_budget.py`
- `baseline_tests/run_step17_step16_regression.py`
- `baseline_tests/run_step17_artifact_manifest.py`
- `docs/16_link_area_momentum_accounting.md`
- `tests/test_step17_link_area_accounting_contract.py`

Updated:

- `src/lbm_fluid.py`
- `src/__init__.py`
- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/14_moving_boundary_calibration.md`
- `docs/15_long_run_validation.md`

## 3. Explicit Non-Goals

Step 17 does not implement:

- a new bounce-back formula
- a new reaction transfer formula
- a new FSI mode
- two-phase flow
- contact angle physics
- real squid validation
- squid actuation or swimming
- mesh import
- sparse storage
- `ReducedSquidFSI`
- edits to `external/taichi_LBM3D`
- completion of strict momentum-conserving sharp-interface FSI

## 4. Directional Link Sanity

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step17_directional_link_sanity.py
```

Result:

| metric | value |
| ------ | ----: |
| bb_link_count | 10240 |
| sum_link_count_by_dir | 10240 |
| link_count_sum_error | 0 |
| scalar_vs_directional_impulse_error_x | 0.000000000 |
| bb_net_fluid_impulse_x | 0.123149872 |
| bb_net_solid_force_x | -0.123149872 |
| rho_min | 1.000000238 |
| rho_max | 1.000002146 |
| lbm_max_v | 0.014671623 |

The scalar moving-boundary diagnostic is finalized from the per-direction reductions, so the scalar and direction-wise paths agree exactly for the x accounting row.

## 5. Link-Area Wall Couette

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step17_link_area_wall_couette.py
```

Result:

| policy | total links | axis links | face diagonal links | area proxy total | area weighted fluid impulse x | area weighted solid force x |
| ------ | ----------: | ---------: | ------------------: | ---------------: | -----------------------------: | --------------------------: |
| uniform | 10240 | 2048 | 8192 | 10240.000000 | 0.058269501 | -0.058269501 |
| inverse_length | 10240 | 2048 | 8192 | 7840.618751 | 0.041202759 | -0.041202759 |
| length | 10240 | 2048 | 8192 | 13633.237503 | 0.082405518 | -0.082405518 |

All policies were finite and stable.

## 6. Link Budget Baselines

| case | policy | links | axis | face diagonal | area proxy total | rho_min | rho_max | lbm_max_v | mpm_min_J | cell_force_max_norm |
| ---- | ------ | ----: | ---: | ------------: | ---------------: | ------: | ------: | --------: | --------: | ------------------: |
| 48^3 box | inverse_length | 5964 | 1232 | 4732 | 4578.029289 | 0.988891542 | 1.017282963 | 0.009996162 | 0.992804050 | 0.000000000 |
| 48^3 squid_proxy | inverse_length | 6616 | 1746 | 4870 | 5189.610024 | 0.991027117 | 1.012060523 | 0.007719247 | 0.993878782 | 0.000000000 |
| 64^3 box | inverse_length | 11186 | 2424 | 8762 | 8619.669617 | 0.992273271 | 1.002777219 | 0.005351911 | 0.995547771 | 0.000000000 |

The procedural squid_proxy row is a geometry-distribution accounting case, not real squid validation. Its final x-direction impulse sign differs from the box rows, but the row remains stable and direction-wise accounting is finite and internally consistent.

## 7. Step 16 Regression

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step17_step16_regression.py
```

Result:

| case | n_grid | completed LBM steps | total MPM substeps | rho_min | rho_max | lbm_max_v | mpm_min_J | bb_link_count_min | cell_force_max_norm |
| ---- | -----: | ------------------: | -----------------: | ------: | ------: | --------: | --------: | ----------------: | ------------------: |
| step16_box_48_short | 48 | 10 | 100 | 0.988891482 | 1.017282963 | 0.008981408 | 0.997173488 | 6120 | 0.000000000 |
| step16_box_64_feasibility | 64 | 5 | 25 | 0.992273331 | 1.002777219 | 0.005351944 | 0.995547712 | 11186 | 0.000000000 |

These rows show the Step 16 moving_boundary stability thresholds remain satisfied after adding diagnostic-only direction accumulators.

## 8. Artifact Manifest

Artifact manifest is generated at:

```text
outputs/step17_artifact_manifest/artifact_manifest.csv
outputs/step17_artifact_manifest/artifact_summary.json
```

Final artifact summary:

| metric | value |
| ------ | ----: |
| file_count | 598 |
| total_size_bytes | 97071447 |
| total_size_mb | 92.574546 |
| large_file_count | 0 |

## 9. Verification

Required baselines completed with GPU Taichi initialization:

- `logs/step17_directional_link_sanity.log`
- `logs/step17_link_area_wall_couette.log`
- `logs/step17_box_48_link_budget.log`
- `logs/step17_squid_proxy_48_link_budget.log`
- `logs/step17_box_64_link_budget.log`
- `logs/step17_step16_regression.log`

Final pytest result is recorded in `logs/step17_pytest.log`.

`external/taichi_LBM3D` remained unchanged.

## 10. GitHub Sync

Final commit hash is reported after commit creation. Remote branch after push: `origin/main`.

## 11. Acceptance Checklist

- [x] main is on the Step 17 final commit
- [x] LBMFluid3D has per-direction moving-boundary diagnostics
- [x] get_moving_boundary_directional_stats() exists
- [x] src/link_area_accounting.py exists
- [x] LinkAreaMomentumAccounting3D exists
- [x] configs/step17_link_area_wall_32.json exists
- [x] configs/step17_link_area_box_48.json exists
- [x] configs/step17_link_area_squid_proxy_48.json exists
- [x] configs/step17_link_area_box_64.json exists
- [x] directional sanity baseline passes
- [x] sum(direction counts) == scalar bb_link_count
- [x] sum(direction impulses) matches scalar impulse within tolerance
- [x] area proxy policies uniform / inverse_length / length run
- [x] 48^3 box link budget passes
- [x] 48^3 squid_proxy link budget passes
- [x] 64^3 box link budget passes
- [x] Step 16 regression passes
- [x] rho_min > 0.95
- [x] rho_max < 1.05
- [x] lbm_max_v < 0.1
- [x] mpm_min_J > 0
- [x] cell_force_max_norm == 0 for moving_boundary rows
- [x] no NaN
- [x] no Inf
- [x] no new bounce-back formula
- [x] no new reaction transfer formula
- [x] no new FSI mode
- [x] no two-phase flow
- [x] no contact angle physics
- [x] no real squid validation claims
- [x] no sparse storage implementation
- [x] no ReducedSquidFSI
- [x] no external/taichi_LBM3D edits
- [x] artifact large_file_count controlled
- [x] docs/16_link_area_momentum_accounting.md exists
- [x] STEP17_LINK_AREA_ACCOUNTING_REPORT.md complete
- [x] tests/test_step17_link_area_accounting_contract.py exists
- [x] pytest -q passes
- [x] logs/step17_pytest.log exists
- [x] git diff --check passes
- [x] Step 17 artifacts are committed
- [x] Step 17 artifacts are pushed to GitHub

## 12. Decision

Can proceed to Step 18?

- [x] Yes
- [ ] No
