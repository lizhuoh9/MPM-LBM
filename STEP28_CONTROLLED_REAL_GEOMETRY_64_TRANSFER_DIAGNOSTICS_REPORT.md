# Step 28 Controlled Real Geometry 64 Transfer Diagnostics Report

## 1. Goal

Step 28 is controlled real geometry 64^3 transfer diagnostics.
Step 28 compares engineering and link_area_experimental transfer diagnostically.
Step 28 is not real squid validation.
Step 28 does not implement squid actuation.
Step 28 does not implement squid swimming.
Step 28 does not implement new FSI physics.
Step 28 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 28 compares the accepted mesh and voxel smoke candidates with four 64^3 moving_boundary rows: engineering and link_area_experimental transfer for each candidate. The run window is 10 LBM steps with 5 MPM substeps per LBM step and per-step diagnostics.

## 2. Files Created And Updated

Created:

- `STEP28_CONTROLLED_REAL_GEOMETRY_64_TRANSFER_DIAGNOSTICS_GOAL.md`
- `STEP28_CONTROLLED_REAL_GEOMETRY_64_TRANSFER_DIAGNOSTICS_REPORT.md`
- `docs/28_controlled_real_geometry_64_transfer_diagnostics.md`
- `configs/step28_compare_real_candidate_smoke_mesh_64_moving_boundary.json`
- `configs/step28_compare_real_candidate_smoke_mesh_64_link_area.json`
- `configs/step28_compare_real_candidate_smoke_voxel_64_moving_boundary.json`
- `configs/step28_compare_real_candidate_smoke_voxel_64_link_area.json`
- `baseline_tests/step28_common.py`
- `baseline_tests/run_step28_candidate_fingerprint_guard.py`
- `baseline_tests/run_step28_64_transfer_pair_driver.py`
- `baseline_tests/run_step28_engineering_vs_link_area_comparison.py`
- `baseline_tests/run_step28_force_reaction_diagnostics.py`
- `baseline_tests/run_step28_area_scale_envelope.py`
- `baseline_tests/run_step28_step27_prefix_regression.py`
- `baseline_tests/run_step28_quality_report_aggregation.py`
- `baseline_tests/run_step28_step27_regression_guard.py`
- `baseline_tests/run_step28_artifact_manifest.py`
- `tests/test_step28_controlled_real_geometry_64_transfer_diagnostics_contract.py`

Updated:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/11_artifact_policy.md`
- `docs/12_geometry_ingestion.md`
- `docs/19_geometry_import_pipeline.md`
- `docs/24_controlled_real_geometry_intake.md`
- `docs/25_real_geometry_candidate_policy.md`
- `docs/26_controlled_real_geometry_short_feasibility.md`
- `docs/27_controlled_real_geometry_64_short_driver.md`

## 3. Explicit Non-Goals

Step 28 does not add actuation, swimming, new coupling formulas, LBM formula changes, MPM constitutive changes, projection formula changes, mesh repair behavior, remeshing behavior, sparse storage, two-phase flow, contact-angle physics, or edits to `external/taichi_LBM3D`.

## 4. Candidate Fingerprint Guard

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_candidate_fingerprint_guard.py
```

Artifacts:

- `outputs/step28_candidate_fingerprint_guard/fingerprint_guard.csv`
- `outputs/step28_candidate_fingerprint_guard/fingerprint_guard.json`
- `logs/step28_candidate_fingerprint_guard.log`

Result:

- `row_count = 2`
- `pass_count = 2`
- mesh SHA-256: `d5a3dd8a698a81951052c6fc3aeb1dd37f7a3c205c07b23d514a3b6a77c2c126`
- voxel SHA-256: `7df9048eb5967888f0788817414b05235fe4a67367198ad82fdb571d92e3b01f`
- both descriptor fingerprints and sizes match the Step 25 manifest
- both Step 26 generated GeometryConfig files remain strict quality-enabled

## 5. 64^3 Transfer Pair Driver

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_64_transfer_pair_driver.py
```

Artifacts:

- `outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.csv`
- `outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.npz`
- `outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.json`
- `logs/step28_64_transfer_pair_driver.log`

Summary:

- `driver_row_count = 4`
- `candidate_count = 2`
- `mesh_row_count = 2`
- `voxel_row_count = 2`
- `engineering_row_count = 2`
- `link_area_row_count = 2`
- `stable_count = 4`
- `quality_report_count = 4`
- `quality_pass_count = 4`
- `strict_count = 4`
- `min_rho_min_global = 0.9925969839096069`
- `max_rho_max_global = 1.008886456489563`
- `max_lbm_max_v_global = 0.006151682231575251`
- `min_mpm_min_J_global = 0.9997254014015198`
- `max_mpm_max_speed_global = 0.027336400002241135`
- `min_projected_mass = 0.09944119304418564`
- `min_active_cell_count = 31116`
- `min_bb_link_count_min = 101890`
- `max_hydro_force_max_norm = 0.41878199577331543`
- `max_driver_total_time = 277.19025119999424`

Rows:

| candidate | transfer | rho_min | rho_max | lbm_max_v | mpm_min_J | projected_mass | hydro_force_max_norm | bb_link_count_min | bb_link_count_max | area_scale_final |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mesh | engineering | 0.9956843852996826 | 1.0041377544403076 | 0.005641019903123379 | 0.9999977350234985 | 0.605825662612915 | 0.4173511266708374 | 498554 | 498714 | 1.0 |
| mesh | link_area_experimental | 0.9956842660903931 | 1.0041377544403076 | 0.005641019903123379 | 0.9999977350234985 | 0.6058269143104553 | 0.4173510670661926 | 498554 | 498714 | 0.7903904318809509 |
| voxel | engineering | 0.9925971627235413 | 1.008886456489563 | 0.006151681300252676 | 0.9997254014015198 | 0.09944126754999161 | 0.41878190636634827 | 101890 | 102144 | 1.0 |
| voxel | link_area_experimental | 0.9925969839096069 | 1.008886456489563 | 0.006151682231575251 | 0.9997256398200989 | 0.09944119304418564 | 0.41878199577331543 | 101890 | 102144 | 0.7920417189598083 |

Every row completed 10 LBM steps and 50 MPM substeps with `cell_force_max_norm = 0`, no NaN, no Inf, and a strict quality report.

## 6. Engineering Vs Link-Area Comparison

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_engineering_vs_link_area_comparison.py
```

Artifacts:

- `outputs/step28_engineering_vs_link_area_comparison/engineering_vs_link_area.csv`
- `outputs/step28_engineering_vs_link_area_comparison/engineering_vs_link_area.json`
- `logs/step28_engineering_vs_link_area_comparison.log`

Result:

- `row_count = 2`
- `pass_count = 2`

Comparison deltas:

| candidate | rho_min_delta | rho_max_delta | lbm_max_v_delta | mpm_min_J_delta | projected_mass_delta | hydro_force_max_norm_delta | link_area_area_scale_final |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mesh | -1.1920928955078125e-07 | 0.0 | 0.0 | 0.0 | 1.2516975402832031e-06 | -5.960464477539063e-08 | 0.7903904318809509 |
| voxel | -1.7881393432617188e-07 | 0.0 | 9.313225746154785e-10 | 2.384185791015625e-07 | -7.450580596923828e-08 | 8.940696716308594e-08 | 0.7920417189598083 |

The comparison is diagnostic and bounded only.

## 7. Force And Reaction Diagnostics

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_force_reaction_diagnostics.py
```

Artifacts:

- `outputs/step28_force_reaction_diagnostics/force_reaction_diagnostics.csv`
- `outputs/step28_force_reaction_diagnostics/force_reaction_diagnostics.json`
- `logs/step28_force_reaction_diagnostics.log`

Result:

- `row_count = 4`
- `pass_count = 4`
- every row has 11 time-series rows including step 0
- every row has 10 post-step positive diagnostic rows

Force and reaction envelope:

| candidate | transfer | hydro_force_min | hydro_force_max | hydro_force_final | max_grid_reaction_min | max_grid_reaction_max | active_reaction_particles | bb_link_min | bb_link_max |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mesh | engineering | 0.4164714515209198 | 0.4173511266708374 | 0.4164714515209198 | 4.216282377456082e-06 | 4.2173896872554906e-06 | 4096 | 498554 | 498714 |
| mesh | link_area_experimental | 0.4164714813232422 | 0.4173510670661926 | 0.4164714813232422 | 4.216282832203433e-06 | 4.21738923250814e-06 | 4096 | 498554 | 498714 |
| voxel | engineering | 0.4175855219364166 | 0.41878190636634827 | 0.41801777482032776 | 4.217123205307871e-06 | 4.21744061895879e-06 | 4096 | 101890 | 102144 |
| voxel | link_area_experimental | 0.4175856113433838 | 0.41878199577331543 | 0.4180176854133606 | 4.21712275056052e-06 | 4.2174419832008425e-06 | 4096 | 101890 | 102144 |

All rows have finite force/reaction diagnostics and `diagnostic_pass = true`.

## 8. Area-Scale Envelope

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_area_scale_envelope.py
```

Artifacts:

- `outputs/step28_area_scale_envelope/area_scale_envelope.csv`
- `outputs/step28_area_scale_envelope/area_scale_envelope.json`
- `logs/step28_area_scale_envelope.log`

Result:

- `row_count = 2`
- `pass_count = 2`

Envelope:

| candidate | area_scale_initial | area_scale_min_observed | area_scale_max_observed | area_scale_final | raw_area_scale_min | raw_area_scale_max | hit_lower_bound | hit_upper_bound |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| mesh | 1.0 | 0.7903904318809509 | 1.0 | 0.7903904318809509 | 0.7903904318809509 | 1.0 | false | false |
| voxel | 1.0 | 0.7920417189598083 | 1.0 | 0.7920417189598083 | 0.7920417189598083 | 1.0 | false | false |

The area-scale script uses the current exposed final area scale plus the configured initialization baseline. It does not change solver or coupler formulas.

## 9. Step 27 Prefix Regression

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_step27_prefix_regression.py
```

Artifacts:

- `outputs/step28_step27_prefix_regression/step27_prefix_regression.csv`
- `outputs/step28_step27_prefix_regression/step27_prefix_regression.json`
- `logs/step28_step27_prefix_regression.log`

Result:

- `row_count = 4`
- `pass_count = 4`

Prefix deltas at step 5:

| candidate | transfer | rho_min_delta | rho_max_delta | lbm_max_v_delta | mpm_min_J_delta | projected_mass_delta | active_cell_count_delta | bb_link_count_delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mesh | engineering | 0.0 | 0.0 | 0.0 | 1.1920928955078125e-07 | 4.76837158203125e-07 | 0 | 0 |
| mesh | link_area_experimental | 0.0 | 0.0 | 0.0 | -5.960464477539063e-08 | -3.5762786865234375e-07 | 0 | 0 |
| voxel | engineering | -5.960464477539063e-08 | 1.1920928955078125e-07 | -7.916241884231567e-08 | 5.960464477539063e-08 | 1.4901161193847656e-08 | 0 | 0 |
| voxel | link_area_experimental | -5.960464477539063e-08 | 1.1920928955078125e-07 | -6.28642737865448e-08 | 1.7881393432617188e-07 | 4.470348358154297e-08 | 0 | 0 |

The final Step 27 summary rows were compared with Step 28 `diagnostics_timeseries.csv` rows at `step = 5` using semantically matching fields.

## 10. Quality Report Aggregation

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_quality_report_aggregation.py
```

Artifacts:

- `outputs/step28_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step28_quality_report_aggregation/quality_report_summary.json`
- `logs/step28_quality_report_aggregation.log`

Summary:

- `quality_report_count = 4`
- `pass_count = 4`
- `strict_count = 4`
- `error_count = 0`
- `warning_count = 0`
- `mesh_row_count = 2`
- `voxel_row_count = 2`
- `quality_report_total_size_bytes = 4742`
- `quality_report_max_size_bytes = 1294`

## 11. Step 27 Regression Guard

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_step27_regression_guard.py
```

Artifacts:

- `outputs/step28_step27_regression_guard/step27_regression_guard.csv`
- `outputs/step28_step27_regression_guard/step27_regression_guard.json`
- `logs/step28_step27_regression_guard.log`

Summary:

- `row_count = 7`
- `pass_count = 7`
- `step27_driver_row_count = 6`
- `step27_stable_count = 6`
- `step27_quality_report_count = 6`
- `step27_quality_pass_count = 6`
- `step27_large_file_count = 0`

## 12. Artifact Manifest Summary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_artifact_manifest.py
```

Artifacts:

- `outputs/step28_artifact_manifest/artifact_manifest.csv`
- `outputs/step28_artifact_manifest/artifact_summary.csv`
- `outputs/step28_artifact_manifest/artifact_summary.json`
- `logs/step28_artifact_manifest.log`

Summary:

- `file_count = 1694`
- `large_file_count = 0`
- `raw_candidate_large_file_count = 0`
- `scan_data_file_count = 0`
- `private_absolute_path_count = 0`
- `step28_driver_config_count = 4`
- `step28_file_count = 59`
- `step28_particle_npy_count = 0`
- `step28_quality_report_count = 4`
- `step28_total_size_bytes = 3353947`
- `step28_total_size_mb = 3.198573112487793`
- `step28_vtr_count = 0`
- `total_size_bytes = 145433361`
- `total_size_mb = 138.69606113433838`

## 13. Verification Commands

Commands used:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile baseline_tests\step28_common.py baseline_tests\run_step28_candidate_fingerprint_guard.py baseline_tests\run_step28_64_transfer_pair_driver.py baseline_tests\run_step28_engineering_vs_link_area_comparison.py baseline_tests\run_step28_force_reaction_diagnostics.py baseline_tests\run_step28_area_scale_envelope.py baseline_tests\run_step28_step27_prefix_regression.py baseline_tests\run_step28_quality_report_aggregation.py baseline_tests\run_step28_step27_regression_guard.py baseline_tests\run_step28_artifact_manifest.py tests\test_step28_controlled_real_geometry_64_transfer_diagnostics_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_candidate_fingerprint_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_64_transfer_pair_driver.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_engineering_vs_link_area_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_force_reaction_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_area_scale_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_step27_prefix_regression.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_step27_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step28_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step28_controlled_real_geometry_64_transfer_diagnostics_contract.py -q
pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Full pytest output is stored in `logs/step28_pytest.log`.

## 14. GitHub Sync Information

- target branch: `origin/main`
- commit message: `test: add step28 controlled real geometry 64 transfer diagnostics`
- final commit hash: reported in the completion message after push

## 15. Acceptance Checklist

- [x] candidate fingerprint guard passes
- [x] Step 25 manifest fingerprints match current candidate files
- [x] Step 26 generated GeometryConfig files remain valid
- [x] mesh 64^3 moving_boundary engineering 10-step row passes
- [x] mesh 64^3 moving_boundary link_area 10-step row passes
- [x] voxel 64^3 moving_boundary engineering 10-step row passes
- [x] voxel 64^3 moving_boundary link_area 10-step row passes
- [x] every Step 28 driver row writes geometry_quality_report.json
- [x] every Step 28 quality gate is strict
- [x] every Step 28 quality report passes
- [x] quality warning count == 0
- [x] quality error count == 0
- [x] all driver rows have completed_lbm_steps >= 10
- [x] all driver rows have total_mpm_substeps >= 50
- [x] rho_min > 0.95
- [x] rho_max < 1.05
- [x] lbm_max_v < 0.1
- [x] mpm_min_J > 0
- [x] mpm_max_speed < 10
- [x] projected_mass > 0
- [x] active_cell_count > 0
- [x] no NaN
- [x] no Inf
- [x] moving_boundary rows keep cell_force_max_norm == 0
- [x] moving_boundary rows have bb_link_count > 0
- [x] moving_boundary rows have active_reaction_particle_count_max > 0
- [x] hydro_force_max_norm is finite and positive after nonzero steps
- [x] max_grid_reaction_norm is finite
- [x] engineering vs link_area comparison passes for mesh
- [x] engineering vs link_area comparison passes for voxel
- [x] link_area rows have finite bounded area_scale
- [x] area_scale envelope summary passes
- [x] Step 27 prefix regression passes at step=5
- [x] Step 27 regression guard passes
- [x] default quality_check_enabled remains false
- [x] default quality_check_strict remains false
- [x] default reaction_transfer_mode remains engineering
- [x] no FSI formula changes
- [x] no moving bounce-back formula changes
- [x] no LBM formula changes
- [x] no MPM constitutive formula changes
- [x] no projection formula changes
- [x] no production mesh repair claims
- [x] no automatic remeshing claims
- [x] no real squid validation claims
- [x] no squid swimming claims
- [x] no squid actuation claims
- [x] no production sharp-interface FSI claims
- [x] no final readiness claims
- [x] no external/taichi_LBM3D edits
- [x] no committed large raw real geometry
- [x] no committed scan data
- [x] no private absolute paths in committed outputs
- [x] no Step 28 .vtr outputs
- [x] no Step 28 particle .npy outputs
- [x] artifact large_file_count == 0
- [x] Step 28 output total size budget passes
- [x] repo artifact_summary total_size_mb < 165
- [x] logs/step28_pytest.log exists
- [x] pytest -q passes
- [x] Step 28 contract test passes
- [x] git diff --check passes
- [x] staged whitespace check passes
- [x] pre-push hook passes
- [x] Step 28 artifacts are pushed to origin/main

## 16. Decision For Step 29

If Step 28 passes, Step 29 should stay conservative and expand only short-window stability diagnostics for the same accepted real-geometry smoke candidates. It should continue to avoid actuation, swimming, production sharp-interface FSI claims, final readiness claims, production mesh repair, automatic remeshing, and solver formula changes.
