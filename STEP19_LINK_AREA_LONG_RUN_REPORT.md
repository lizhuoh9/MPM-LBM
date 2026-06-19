# Step 19 Link-Area Long-Run Report

## 1. Goal

Step 19 validates the opt-in link_area_experimental transfer over longer windows and 64^3 feasibility.

The default reaction_transfer_mode remains engineering. The moving bounce-back formula is unchanged. LinkAreaMovingBoundaryCoupler3D formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. The link-area transfer remains experimental and uses a bounded global area_scale. This is not final strict momentum-conserving sharp-interface FSI. squid_proxy is procedural and not real squid validation.

Step 19 does not change the Step 18 transfer formula. The link-area transfer remains experimental.

## 2. Files Created And Updated

Created:

- `configs/step19_long_box_48_link_area.json`
- `configs/step19_long_squid_proxy_48_link_area.json`
- `configs/step19_feasibility_64_link_area_box.json`
- `configs/step19_compare_64_engineering_vs_link_area.json`
- `configs/step19_compare_48_long_engineering_vs_link_area.json`
- `baseline_tests/step19_common.py`
- `baseline_tests/run_step19_long_box_48_link_area.py`
- `baseline_tests/run_step19_long_squid_proxy_48_link_area.py`
- `baseline_tests/run_step19_feasibility_64_link_area.py`
- `baseline_tests/run_step19_compare_64_engineering_vs_link_area.py`
- `baseline_tests/run_step19_compare_48_long_engineering_vs_link_area.py`
- `baseline_tests/run_step19_regression_step18.py`
- `baseline_tests/run_step19_long_run_summary.py`
- `baseline_tests/run_step19_artifact_manifest.py`
- `tests/test_step19_link_area_long_run_contract.py`
- `docs/18_link_area_long_run.md`
- `outputs/step19_*`
- `logs/step19_*`

Updated:

- `README.md`
- `docs/08_roadmap.md`
- `docs/10_performance_memory.md`
- `docs/16_link_area_momentum_accounting.md`
- `docs/17_experimental_link_area_transfer.md`

## 3. Explicit Non-Goals

Step 19 does not add new FSI physics, does not add a new transfer formula, does not change the moving bounce-back formula, does not change LinkAreaMovingBoundaryCoupler3D formula, does not change MovingBoundaryFSICoupler3D, does not change PenaltyFSICoupler3D, does not change the default reaction_transfer_mode, and does not edit `external/taichi_LBM3D`.

It also does not implement two-phase flow, contact angle physics, real squid validation, squid swimming, mesh import, sparse storage, ReducedSquidFSI, or final strict momentum-conserving sharp-interface FSI.

## 4. 48^3 Box Link-Area Long-Run Result

| completed_lbm_steps | total_mpm_substeps | area_scale_initial | area_scale_final | area_scale_min | area_scale_max | rho_min_global | rho_max_global | lbm_max_v_global | mpm_min_J_global | cell_force_max_norm | stable |
| ------------------: | -----------------: | -----------------: | ---------------: | -------------: | -------------: | -------------: | -------------: | ---------------: | ---------------: | ------------------: | ------ |
| 50 | 500 | 1.000000000 | 0.853882253 | 0.417903900 | 1.000000000 | 0.988891423 | 1.017294407 | 0.011978018 | 0.992365003 | 0.000000000 | true |

The 48^3 box link-area long-run passed. `area_scale` did not sit continuously on the configured minimum or maximum bound.

## 5. 48^3 Procedural Squid Proxy Link-Area Long-Run Result

| completed_lbm_steps | total_mpm_substeps | area_scale_initial | area_scale_final | area_scale_min | area_scale_max | rho_min_global | rho_max_global | lbm_max_v_global | mpm_min_J_global | cell_force_max_norm | stable |
| ------------------: | -----------------: | -----------------: | ---------------: | -------------: | -------------: | -------------: | -------------: | ---------------: | ---------------: | ------------------: | ------ |
| 30 | 300 | 1.000000000 | 0.808569014 | 0.784083664 | 1.000000000 | 0.991046309 | 1.012029171 | 0.007718042 | 0.993962169 | 0.000000000 | true |

The procedural squid_proxy long-run passed. squid_proxy is procedural and not real squid validation.

## 6. 64^3 Link-Area Feasibility Result

| completed_lbm_steps | total_mpm_substeps | area_scale_initial | area_scale_final | area_scale_min | area_scale_max | rho_min_global | rho_max_global | lbm_max_v_global | mpm_min_J_global | cell_force_max_norm | stable |
| ------------------: | -----------------: | -----------------: | ---------------: | -------------: | -------------: | -------------: | -------------: | ---------------: | ---------------: | ------------------: | ------ |
| 5 | 25 | 1.000000000 | 0.777285635 | 0.777285635 | 1.000000000 | 0.992273211 | 1.002777219 | 0.005351947 | 0.995547712 | 0.000000000 | true |

The 64^3 row is a conservative feasibility baseline, not a full validation claim.

## 7. 64^3 Engineering Vs Link-Area Comparison Result

| case | transfer | completed_lbm_steps | total_mpm_substeps | area_scale_final | area_scale_min | area_scale_max | rho_min_global | rho_max_global | lbm_max_v_global | mpm_min_J_global | cell_force_max_norm | stable |
| ---- | -------- | ------------------: | -----------------: | ---------------: | -------------: | -------------: | -------------: | -------------: | ---------------: | ---------------: | ------------------: | ------ |
| box_64 | engineering | 5 | 25 | 1.000000000 | 1.000000000 | 1.000000000 | 0.992273271 | 1.002777219 | 0.005351898 | 0.995547831 | 0.000000000 | true |
| box_64 | link_area_experimental | 5 | 25 | 0.777285695 | 0.777285695 | 1.000000000 | 0.992273271 | 1.002777338 | 0.005351908 | 0.995547652 | 0.000000000 | true |

Both rows passed. The comparison does not require link_area_experimental to outperform engineering.

## 8. 48^3 Long Engineering Vs Link-Area Comparison Result

| case | transfer | completed_lbm_steps | total_mpm_substeps | area_scale_final | area_scale_min | area_scale_max | rho_min_global | rho_max_global | lbm_max_v_global | mpm_min_J_global | cell_force_max_norm | stable |
| ---- | -------- | ------------------: | -----------------: | ---------------: | -------------: | -------------: | -------------: | -------------: | ---------------: | ---------------: | ------------------: | ------ |
| box_48 | engineering | 30 | 300 | 1.000000000 | 1.000000000 | 1.000000000 | 0.988891482 | 1.017282844 | 0.011355299 | 0.992399752 | 0.000000000 | true |
| box_48 | link_area_experimental | 30 | 300 | 0.702269793 | 0.417994887 | 1.000000000 | 0.988891542 | 1.017294168 | 0.011393997 | 0.992364883 | 0.000000000 | true |
| squid_proxy_48 | engineering | 20 | 200 | 1.000000000 | 1.000000000 | 1.000000000 | 0.991026998 | 1.012060404 | 0.007719149 | 0.993878603 | 0.000000000 | true |
| squid_proxy_48 | link_area_experimental | 20 | 200 | 0.799404085 | 0.784088552 | 1.000000000 | 0.991046131 | 1.012029290 | 0.007718053 | 0.993962228 | 0.000000000 | true |

All four rows passed. The engineering rows keep `area_scale = 1.0`.

## 9. Step 18 Regression Result

| case | transfer | completed_lbm_steps | total_mpm_substeps | area_scale_final | area_scale_min | area_scale_max | rho_min_global | rho_max_global | lbm_max_v_global | mpm_min_J_global | cell_force_max_norm | stable |
| ---- | -------- | ------------------: | -----------------: | ---------------: | -------------: | -------------: | -------------: | -------------: | ---------------: | ---------------: | ------------------: | ------ |
| step18_sanity_regression | link_area_experimental | 5 | 25 | 0.776304126 | 0.715170085 | 1.000000000 | 0.976838350 | 1.018712997 | 0.013707758 | 0.998373866 | 0.000000000 | true |
| step18_box_48_experimental_regression | link_area_experimental | 10 | 100 | 0.417895973 | 0.417895973 | 1.000000000 | 0.988891482 | 1.017294407 | 0.008986835 | 0.997175097 | 0.000000000 | true |
| engineering_default_regression | engineering | 5 | 25 | 1.000000000 | 1.000000000 | 1.000000000 | 0.987000704 | 1.009115219 | 0.007159951 | 0.998374045 | 0.000000000 | true |

The default `reaction_transfer_mode` remains engineering.

## 10. Long-Run Summary Result

| summary_case | row_count | stable | rho_min_global | rho_max_global | area_scale_min | area_scale_max |
| ------------ | --------: | ------ | -------------: | -------------: | -------------: | -------------: |
| box_48_link_area_long | 1 | true | 0.988891423 | 1.017294407 | 0.417903900 | 1.000000000 |
| squid_proxy_48_link_area_long | 1 | true | 0.991046309 | 1.012029171 | 0.784083664 | 1.000000000 |
| box_64_link_area_feasibility | 1 | true | 0.992273211 | 1.002777219 | 0.777285635 | 1.000000000 |
| engineering_vs_link_area_64 | 2 | true | 0.992273271 | 1.002777338 | 0.777285695 | 1.000000000 |
| engineering_vs_link_area_48 | 4 | true | 0.988891482 | 1.017294168 | 0.417994887 | 1.000000000 |
| step18_regression | 3 | true | 0.976838350 | 1.018712997 | 0.417895973 | 1.000000000 |

No experimental row sat continuously on the configured minimum or maximum area_scale bound.

## 11. Artifact Manifest Summary

Final artifact manifest:

| file_count | total_size_bytes | total_size_mb | large_file_count |
| ---------: | ---------------: | ------------: | ---------------: |
| 784 | 105807542 | 100.905935 | 0 |

The final manifest includes `logs/step19_pytest.log` and the Step 19 documentation/report artifacts.

## 12. Verification Commands

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_long_box_48_link_area.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_long_squid_proxy_48_link_area.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_feasibility_64_link_area.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_compare_64_engineering_vs_link_area.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_compare_48_long_engineering_vs_link_area.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_regression_step18.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_long_run_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step19_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
git diff --check
git status --short external/taichi_LBM3D
```

## 13. GitHub Sync Information

Target branch: `origin/main`.

The final Step 19 commit is pushed after the final pytest run, Git pre-push pytest hook, `git diff --check`, and external cleanliness check pass.

## 14. Acceptance Checklist

- [x] 48^3 box link_area_experimental long-run completes
- [x] 48^3 box long-run completed_lbm_steps >= 50
- [x] 48^3 box long-run total_mpm_substeps >= 500
- [x] 48^3 squid_proxy link_area_experimental long-run completes
- [x] 48^3 squid_proxy long-run completed_lbm_steps >= 30
- [x] 48^3 squid_proxy long-run total_mpm_substeps >= 300
- [x] 64^3 link_area_experimental feasibility completes
- [x] 64^3 link-area feasibility completed_lbm_steps >= 5
- [x] 64^3 engineering vs link-area comparison completes
- [x] 48^3 long engineering vs link-area comparison completes
- [x] Step 18 regression completes
- [x] long-run summary completes
- [x] area_scale is finite for all experimental rows
- [x] area_scale stays within configured bounds
- [x] rho_min_global > 0.95 for required stable rows
- [x] rho_max_global < 1.05 for required stable rows
- [x] lbm_max_v_global < 0.1 for required stable rows
- [x] mpm_min_J_global > 0 for required stable rows
- [x] mpm_max_speed_global < 10 for required stable rows
- [x] cell_force_max_norm == 0 for moving_boundary rows
- [x] bb_link_count_min > 0 for moving_boundary rows
- [x] active_reaction_particle_count_min > 0 for required experimental rows
- [x] engineering transfer remains available
- [x] default reaction_transfer_mode remains engineering
- [x] link_area_experimental remains opt-in
- [x] no moving bounce-back formula changes
- [x] no LinkAreaMovingBoundaryCoupler3D formula changes
- [x] no MovingBoundaryFSICoupler3D changes
- [x] no PenaltyFSICoupler3D changes
- [x] no two-phase flow
- [x] no contact angle physics
- [x] no real squid validation claims
- [x] no squid swimming validation claims
- [x] no mesh import
- [x] no sparse storage implementation
- [x] no ReducedSquidFSI
- [x] no external/taichi_LBM3D edits
- [x] artifact large_file_count == 0
- [x] docs/18_link_area_long_run.md exists
- [x] STEP19_LINK_AREA_LONG_RUN_REPORT.md complete
- [x] tests/test_step19_link_area_long_run_contract.py exists
- [x] logs/step19_pytest.log exists
- [x] pytest -q passes
- [x] Git pre-push pytest hook passes
- [x] git diff --check passes
- [x] Step 19 artifacts are committed
- [x] Step 19 artifacts are pushed to GitHub origin/main

## 15. Decision For Step 20

Step 19 supports proceeding to Step 20: Mesh/voxel geometry import pipeline.

Reason: after Step 19, the project has engineering moving_boundary long-run evidence, link_area_experimental short-run evidence, link_area_experimental long-run evidence, 64^3 link_area_experimental feasibility, and direct engineering-vs-link-area comparison. The next bottleneck is geometry ingestion, not claiming final strict momentum-conserving sharp-interface FSI.
