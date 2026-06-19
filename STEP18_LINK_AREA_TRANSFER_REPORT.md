# Step 18 Experimental Link-Area Reaction Transfer Report

## 1. Goal

Step 18 adds an opt-in experimental link-area reaction transfer mode.

The default moving_boundary reaction transfer remains engineering. The moving bounce-back formula is unchanged. MovingBoundaryFSICoupler3D is unchanged. The experimental transfer uses a bounded global area_scale from Step 17 link-area proxy accounting. This is not final strict momentum-conserving sharp-interface FSI. squid_proxy is procedural and not real squid validation.

## 2. Files

Created:

- `src/link_area_coupling.py`
- `configs/step18_link_area_transfer_sanity_32.json`
- `configs/step18_link_area_policy_sweep_box_32.json`
- `configs/step18_link_area_transfer_box_48.json`
- `configs/step18_link_area_transfer_squid_proxy_48.json`
- `configs/step18_compare_engineering_vs_link_area_box_48.json`
- `configs/step18_compare_engineering_vs_link_area_squid_proxy_48.json`
- `baseline_tests/step18_common.py`
- `baseline_tests/run_step18_link_area_transfer_sanity.py`
- `baseline_tests/run_step18_link_area_policy_sweep_box_32.py`
- `baseline_tests/run_step18_link_area_transfer_box_48.py`
- `baseline_tests/run_step18_link_area_transfer_squid_proxy_48.py`
- `baseline_tests/run_step18_compare_engineering_vs_link_area.py`
- `baseline_tests/run_step18_regression_existing_modes.py`
- `baseline_tests/run_step18_artifact_manifest.py`
- `docs/17_experimental_link_area_transfer.md`
- `tests/test_step18_link_area_transfer_contract.py`

Updated:

- `src/fsi_config.py`
- `src/fsi_driver.py`
- `src/__init__.py`
- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/16_link_area_momentum_accounting.md`

## 3. Explicit Non-Goals

Step 18 does not:

- replace engineering moving_boundary transfer
- change the moving bounce-back formula
- change `MovingBoundaryFSICoupler3D`
- change `PenaltyFSICoupler3D`
- make `link_area_experimental` the default
- implement two-phase flow
- implement contact angle physics
- validate a real squid simulation
- validate squid swimming
- import real squid meshes
- implement sparse storage
- implement `ReducedSquidFSI`
- complete strict link-area momentum-conserving sharp-interface FSI
- edit `external/taichi_LBM3D`

## 4. Experimental Transfer Formula

```text
area_scale = clip(
    |area_weighted_solid_force_x| / (|bb_net_solid_force_x| + eps),
    area_scale_min,
    area_scale_max
)

particle_force =
    sampled_hydro_lbm
    * force_density_scale_lbm_to_norm
    * particle_volume
    * reaction_scale
    * area_scale
```

This is a global proxy scale, not local surface-area reconstruction. The local spatial distribution still comes from `lbm.hydro_force`. The experimental transfer writes to `solid.grid_f_ext` and does not write to `lbm.cell_force`.

## 5. Sanity Baseline

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_link_area_transfer_sanity.py
```

| metric | value |
| ------ | ----: |
| step | 5 |
| area_scale | 0.776303947 |
| raw_area_scale | 0.776303947 |
| area_proxy_total | 1895.645020 |
| bb_link_count | 2458 |
| rho_min | 0.976838231 |
| rho_max | 1.018712997 |
| lbm_max_v | 0.013707759 |
| mpm_min_J | 0.998373866 |
| active_reaction_particle_count | 3520 |
| max_grid_reaction_norm | 0.000004095 |
| cell_force_max_norm | 0.000000000 |

## 6. Area Policy Sweep

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_link_area_policy_sweep_box_32.py
```

| policy | stable | area_scale | rho_min | rho_max | lbm_max_v | mpm_min_J | bb_link_count |
| ------ | ------ | ---------: | ------: | ------: | --------: | --------: | ------------: |
| uniform | True | 1.000000000 | 0.985451698 | 1.015292883 | 0.012824387 | 0.998647273 | 2458 |
| inverse_length | True | 0.751058698 | 0.985451281 | 1.015294671 | 0.012829683 | 0.998649180 | 2458 |
| length | True | 1.351855159 | 0.985452533 | 1.015290022 | 0.012816965 | 0.998646855 | 2458 |

## 7. 48^3 Box Experimental Transfer

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_link_area_transfer_box_48.py
```

| metric | value |
| ------ | ----: |
| area_scale | 0.787582099 |
| area_proxy_total | 4578.029297 |
| bb_link_count | 5964 |
| rho_min | 0.989737570 |
| rho_max | 1.014070630 |
| lbm_max_v | 0.009917610 |
| mpm_min_J | 0.992774725 |
| active_reaction_particle_count | 8622 |
| cell_force_max_norm | 0.000000000 |

## 8. 48^3 Procedural Squid Proxy Experimental Transfer

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_link_area_transfer_squid_proxy_48.py
```

| metric | value |
| ------ | ----: |
| area_scale | 0.799408257 |
| area_proxy_total | 5181.953125 |
| bb_link_count | 6606 |
| rho_min | 0.992144644 |
| rho_max | 1.010514975 |
| lbm_max_v | 0.006503166 |
| mpm_min_J | 0.994846642 |
| active_reaction_particle_count | 3299 |
| cell_force_max_norm | 0.000000000 |

The squid_proxy row is procedural and not real squid validation.

## 9. Engineering vs Link-Area Comparison

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_compare_engineering_vs_link_area.py
```

| case | transfer_mode | stable | area_scale | rho_min | rho_max | lbm_max_v | mpm_min_J | bb_link_count |
| ---- | ------------- | ------ | ---------: | ------: | ------: | --------: | --------: | ------------: |
| box_48 | engineering | True | 1.000000000 | 0.989750385 | 1.013995290 | 0.009996211 | 0.992804229 | 5964 |
| box_48 | link_area_experimental | True | 0.787572086 | 0.989737630 | 1.014070868 | 0.009917681 | 0.992774665 | 5964 |
| squid_proxy_48 | engineering | True | 1.000000000 | 0.991861343 | 1.010593176 | 0.006485941 | 0.994595468 | 6616 |
| squid_proxy_48 | link_area_experimental | True | 0.799397409 | 0.992144704 | 1.010515213 | 0.006503075 | 0.994846463 | 6606 |

This comparison is evidence that the experimental path runs stably beside the engineering path. It does not claim the experimental path is more accurate or more physical.

## 10. Existing Mode Regression

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step18_regression_existing_modes.py
```

| case | completed LBM steps | total MPM substeps | rho_min | rho_max | lbm_max_v | mpm_min_J | bb_link_count_min | cell_force_max_norm |
| ---- | ------------------: | -----------------: | ------: | ------: | --------: | --------: | ----------------: | ------------------: |
| engineering_box_48_regression | 10 | 100 | 0.988891482 | 1.017282844 | 0.008981327 | 0.997173488 | 6120 | 0.000000000 |
| step17_accounting_regression | 5 | 50 | 0.983584225 | 1.006649613 | 0.009175895 | 0.990767956 | 6148 | 0.000000000 |

## 11. Artifact Manifest

Generated at:

```text
outputs/step18_artifact_manifest/artifact_manifest.csv
outputs/step18_artifact_manifest/artifact_summary.json
```

Final artifact summary:

| metric | value |
| ------ | ----: |
| file_count | 676 |
| total_size_bytes | 100390766 |
| total_size_mb | 95.740095 |
| large_file_count | 0 |

## 12. Verification Commands

Required baseline logs:

- `logs/step18_link_area_transfer_sanity.log`
- `logs/step18_link_area_policy_sweep_box_32.log`
- `logs/step18_link_area_transfer_box_48.log`
- `logs/step18_link_area_transfer_squid_proxy_48.log`
- `logs/step18_compare_engineering_vs_link_area.log`
- `logs/step18_regression_existing_modes.log`
- `logs/step18_artifact_manifest.log`
- `logs/step18_pytest.log`

Final pytest result is recorded in `logs/step18_pytest.log`.

`external/taichi_LBM3D` remained unchanged.

## 13. GitHub Sync

Final commit hash is reported after commit creation. Remote branch after push: `origin/main`.

## 14. Acceptance Checklist

- [x] main is on the Step 18 final commit
- [x] src/link_area_coupling.py exists
- [x] LinkAreaMovingBoundaryCoupler3D exists
- [x] FSIDriverConfig has reaction_transfer_mode
- [x] FSIDriverConfig default reaction_transfer_mode == engineering
- [x] link_area_experimental is opt-in only
- [x] engineering moving_boundary path remains available
- [x] moving bounce-back formula unchanged
- [x] MovingBoundaryFSICoupler3D unchanged
- [x] PenaltyFSICoupler3D unchanged
- [x] LBMFluid3D.step() default behavior unchanged
- [x] experimental transfer writes MPM reaction through solid.grid_f_ext
- [x] experimental transfer does not use lbm.cell_force
- [x] area_scale is finite and bounded
- [x] sanity baseline passes
- [x] area policy sweep passes
- [x] 48^3 box experimental transfer passes
- [x] 48^3 procedural squid_proxy experimental transfer passes
- [x] engineering vs link-area comparison passes
- [x] existing-mode regression passes
- [x] rho_min > 0.95 for required stable rows
- [x] rho_max < 1.05 for required stable rows
- [x] lbm_max_v < 0.1 for required stable rows
- [x] mpm_min_J > 0 for required stable rows
- [x] cell_force_max_norm == 0 for moving_boundary rows
- [x] active_reaction_particle_count > 0 for experimental rows
- [x] no NaN
- [x] no Inf
- [x] no two-phase flow
- [x] no contact angle physics
- [x] no real squid validation claims
- [x] no squid swimming validation claims
- [x] no mesh import
- [x] no sparse storage implementation
- [x] no ReducedSquidFSI
- [x] no external/taichi_LBM3D edits
- [x] artifact large_file_count == 0
- [x] docs/17_experimental_link_area_transfer.md exists
- [x] STEP18_LINK_AREA_TRANSFER_REPORT.md complete
- [x] tests/test_step18_link_area_transfer_contract.py exists
- [x] logs/step18_pytest.log exists
- [x] pytest -q passes
- [x] git diff --check passes
- [x] Step 18 artifacts are committed
- [x] Step 18 artifacts are pushed to GitHub origin/main

## 15. Decision

Can proceed to Step 19?

- [x] Yes
- [ ] No
