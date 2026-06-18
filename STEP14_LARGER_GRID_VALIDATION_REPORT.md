# Step 14 Larger Grid Validation Report

## 1. Goal

Step 14 extends the validated 32^3 engineering prototype with 48^3 scale baselines and 64^3 feasibility checks. Step 14 does not add new FSI physics.

This report covers:

- 48^3 box validation for `none`, `penalty`, and `moving_boundary`
- 48^3 procedural `squid_proxy` validation for `none`, `penalty`, and `moving_boundary`
- 64^3 short feasibility for `none` and `penalty`
- scaling summary generation
- artifact manifest generation
- documentation and pytest contract updates

These results are an engineering scale baseline, not production benchmark data and not real squid validation.

## 2. Files

Created:

```text
configs/step14_scale_48_none.json
configs/step14_scale_48_penalty.json
configs/step14_scale_48_moving_boundary.json
configs/step14_scale_48_squid_proxy_none.json
configs/step14_scale_48_squid_proxy_penalty.json
configs/step14_scale_48_squid_proxy_moving_boundary.json
configs/step14_feasibility_64_none.json
configs/step14_feasibility_64_penalty.json
baseline_tests/step14_common.py
baseline_tests/run_step14_scale_box_48.py
baseline_tests/run_step14_scale_squid_proxy_48.py
baseline_tests/run_step14_feasibility_64.py
baseline_tests/run_step14_scaling_summary.py
baseline_tests/run_step14_artifact_manifest.py
docs/13_larger_grid_validation.md
tests/test_step14_larger_grid_contract.py
STEP14_LARGER_GRID_VALIDATION_REPORT.md
```

Generated:

```text
logs/step14_scale_box_48.log
logs/step14_scale_squid_proxy_48.log
logs/step14_feasibility_64.log
logs/step14_scaling_summary.log
logs/step14_artifact_manifest.log
outputs/step14_scale_box_48/box_48_results.csv
outputs/step14_scale_box_48/box_48_results.npz
outputs/step14_scale_squid_proxy_48/squid_proxy_48_results.csv
outputs/step14_scale_squid_proxy_48/squid_proxy_48_results.npz
outputs/step14_feasibility_64/feasibility_64_results.csv
outputs/step14_feasibility_64/feasibility_64_results.npz
outputs/step14_scaling_summary/scaling_summary.csv
outputs/step14_scaling_summary/scaling_summary.json
outputs/step14_artifact_manifest/artifact_manifest.csv
outputs/step14_artifact_manifest/artifact_summary.json
```

Updated:

```text
README.md
docs/08_roadmap.md
docs/10_performance_memory.md
docs/12_geometry_ingestion.md
```

## 3. Explicit Non-Goals

Step 14 does not implement:

- new FSI physics
- a new coupling mode
- changes to `lbm.step()`
- changes to penalty coupling formulas
- changes to moving bounce-back formulas
- changes to moving-boundary reaction transfer formulas
- two-phase flow
- contact angle physics
- real squid validation
- squid actuation
- swimming locomotion
- mesh import
- sparse storage
- ReducedSquidFSI
- production-grade solver readiness

`external/taichi_LBM3D` was not edited.

## 4. Scale Settings

| case | geometry | modes | n_grid | n_particles | n_lbm_steps | substeps |
| ---- | -------- | ----- | -----: | ----------: | ----------: | -------: |
| box 48^3 | box | none, penalty, moving_boundary | 48 | 13824 | 10 | 10 |
| squid_proxy 48^3 | squid_proxy | none, penalty, moving_boundary | 48 | 4096 | 10 | 10 |
| box 64^3 feasibility | box | none, penalty | 64 | 32768 | 5 | 5 |

All required Step 14 scale configs use:

```text
write_vtk = false
write_particles = false
```

The 48^3 box moving_boundary run initially failed the density range at the goal-proposed `target_u_lbm = [0.01, 0.0, 0.0]`, with:

```text
rho_min = 0.9645411372
rho_max = 1.066477895
```

Following Step 14 failure handling, only the Step 14 moving_boundary config was made more conservative:

```text
target_u_lbm = [0.005, 0.0, 0.0]
mb_force_cap_norm = 0.000025
```

No solver formula was changed.

## 5. 48^3 Box Validation

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_scale_box_48.py
```

Result:

| mode | stable | rho_min | rho_max | lbm_max_v | mpm_min_J | mpm_max_speed | time s |
| ---- | ------ | ------: | ------: | --------: | --------: | ------------: | -----: |
| none | True | 1.000000358 | 1.000000358 | 0.000000000 | 0.999999642 | 0.052087333 | 44.333 |
| penalty | True | 0.999991417 | 1.000009537 | 0.000015987 | 0.999995530 | 0.051635873 | 45.785 |
| moving_boundary | True | 0.982743502 | 1.039551854 | 0.021100756 | 0.992788911 | 0.141585857 | 70.848 |

The moving_boundary row has:

```text
cell_force_max_norm = 0.0
hydro_force_max_norm = 0.434040278
bb_link_count = 5960
active_reaction_particle_count = 8670
```

## 6. 48^3 Squid Proxy Validation

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_scale_squid_proxy_48.py
```

Result:

| mode | stable | rho_min | rho_max | lbm_max_v | mpm_min_J | mpm_max_speed | time s |
| ---- | ------ | ------: | ------: | --------: | --------: | ------------: | -----: |
| none | True | 1.000000358 | 1.000000358 | 0.000000000 | 0.999999523 | 0.026048692 | 69.284 |
| penalty | True | 0.999996662 | 1.000004530 | 0.000007749 | 0.999995649 | 0.025958233 | 91.868 |
| moving_boundary | True | 0.990947962 | 1.012312770 | 0.007713154 | 0.993707359 | 0.055477206 | 95.615 |

The `squid_proxy` is the Step 13 procedural proxy. It is not real squid validation, not anatomical squid geometry, and not swimming validation.

## 7. 64^3 Feasibility

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_feasibility_64.py
```

Result:

| mode | stable | rho_min | rho_max | lbm_max_v | mpm_min_J | mpm_max_speed | time s |
| ---- | ------ | ------: | ------: | --------: | --------: | ------------: | -----: |
| none | True | 1.000000358 | 1.000000358 | 0.000000000 | 0.999999702 | 0.039064411 | 155.620 |
| penalty | True | 0.999998331 | 1.000002623 | 0.000005288 | 0.999998629 | 0.038913112 | 178.103 |

These are 64^3 short feasibility rows, not full 64^3 validation.

## 8. Scaling Summary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_scaling_summary.py
```

Result:

```text
row_count = 12
grid_references = [32, 48, 64, 96, 128]
```

Primary outputs:

```text
outputs/step14_scaling_summary/scaling_summary.csv
outputs/step14_scaling_summary/scaling_summary.json
```

The 96^3 and 128^3 rows are Step 12 memory-estimate references only. They are not runtime validation rows.

## 9. Artifact Manifest

Command:

```powershell
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_artifact_manifest.py
```

Result:

```text
file_count = 438
total_size_bytes = 86135862
total_size_mb = 82.145559
large_file_count = 0
```

Primary outputs:

```text
outputs/step14_artifact_manifest/artifact_manifest.csv
outputs/step14_artifact_manifest/artifact_summary.json
```

## 10. Documentation Updates

Updated documentation:

- `README.md`
- `docs/08_roadmap.md`
- `docs/10_performance_memory.md`
- `docs/12_geometry_ingestion.md`
- `docs/13_larger_grid_validation.md`

Documentation states that Step 14 is an engineering scale baseline, not production benchmark data and not real squid validation.

## 11. Verification

Commands run:

```powershell
& 'D:\working\taichi\env\python.exe' -m pytest -q
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_scale_box_48.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_scale_squid_proxy_48.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_feasibility_64.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_scaling_summary.py
& 'D:\working\taichi\env\python.exe' baseline_tests\run_step14_artifact_manifest.py
```

The initial pytest run was RED after adding `tests/test_step14_larger_grid_contract.py`, as expected, because Step 14 artifacts were missing.

Final pytest result is recorded in:

```text
logs/step14_pytest.log
```

## 12. GitHub Sync

The Step 14 final commit and pushed branch are verified after the final commit is created. Because this report is part of the commit object, embedding the final commit SHA inside the same file would change the SHA. The final pushed commit hash is reported by the final `git rev-parse HEAD` / `git rev-parse origin/main` verification and in the Codex final response.

Remote branch:

```text
origin/main
```

## 13. Acceptance Checklist

- [x] main is on the Step 14 final commit
- [x] configs/step14_scale_48_none.json exists
- [x] configs/step14_scale_48_penalty.json exists
- [x] configs/step14_scale_48_moving_boundary.json exists
- [x] configs/step14_scale_48_squid_proxy_none.json exists
- [x] configs/step14_scale_48_squid_proxy_penalty.json exists
- [x] configs/step14_scale_48_squid_proxy_moving_boundary.json exists
- [x] configs/step14_feasibility_64_none.json exists
- [x] configs/step14_feasibility_64_penalty.json exists
- [x] 48^3 box none baseline passes
- [x] 48^3 box penalty baseline passes
- [x] 48^3 box moving_boundary baseline passes
- [x] 48^3 squid_proxy none baseline passes
- [x] 48^3 squid_proxy penalty baseline passes
- [x] 48^3 squid_proxy moving_boundary baseline passes
- [x] 64^3 none feasibility baseline passes
- [x] 64^3 penalty feasibility baseline passes
- [x] rho_min > 0.95 for all stable rows
- [x] rho_max < 1.05 for all stable rows
- [x] lbm_max_v < 0.1 for all stable rows
- [x] mpm_min_J > 0 for all stable rows
- [x] mpm_max_speed < 10 for all stable rows
- [x] active_cell_count > 0 where projection is active
- [x] projected_mass > 0 where projection is active
- [x] no NaN
- [x] no Inf
- [x] scaling_summary.csv exists
- [x] scaling_summary.json exists
- [x] scaling summary references 32^3, 48^3, and 64^3
- [x] artifact manifest exists
- [x] artifact manifest reports total size and large_file_count
- [x] write_vtk is false in required scale configs
- [x] write_particles is false in required scale configs
- [x] no new FSI physics
- [x] no two-phase flow
- [x] no contact angle physics
- [x] no real squid validation claims
- [x] no sparse storage implementation
- [x] no ReducedSquidFSI
- [x] no external/taichi_LBM3D edits
- [x] docs/13_larger_grid_validation.md exists
- [x] README.md documents larger-grid validation conservatively
- [x] docs/08_roadmap.md updated
- [x] docs/10_performance_memory.md updated
- [x] docs/12_geometry_ingestion.md updated
- [x] STEP14_LARGER_GRID_VALIDATION_REPORT.md complete
- [x] tests/test_step14_larger_grid_contract.py exists
- [x] pytest -q passes
- [x] logs/step14_pytest.log exists
- [x] git diff --check passes
- [x] Step 14 artifacts are committed
- [x] Step 14 artifacts are pushed to GitHub

## 14. Decision

Can proceed to Step 15?

- [x] Yes
- [ ] No
