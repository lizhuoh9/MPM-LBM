# Step 29 Controlled Real Geometry 64 Stability Envelope Report

## 1. Goal

Step 29 is controlled real geometry 64^3 short-window stability envelope.
Step 29 extends Step 28 transfer diagnostics conservatively.
Step 29 is not real squid validation.
Step 29 does not implement squid actuation.
Step 29 does not implement squid swimming.
Step 29 does not implement new FSI physics.
Step 29 does not validate production sharp-interface FSI.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 29 runs the accepted Step 28 four-row 64^3 moving_boundary transfer matrix for a 20-step diagnostic window and summarizes stability, force/reaction, transfer, area-scale, and Step 28 prefix envelopes.

## 2. Files Created And Updated

Created:

- `STEP29_CONTROLLED_REAL_GEOMETRY_64_STABILITY_ENVELOPE_GOAL.md`
- `STEP29_CONTROLLED_REAL_GEOMETRY_64_STABILITY_ENVELOPE_REPORT.md`
- `docs/29_controlled_real_geometry_64_stability_envelope.md`
- `configs/step29_stability_real_candidate_smoke_mesh_64_moving_boundary.json`
- `configs/step29_stability_real_candidate_smoke_mesh_64_link_area.json`
- `configs/step29_stability_real_candidate_smoke_voxel_64_moving_boundary.json`
- `configs/step29_stability_real_candidate_smoke_voxel_64_link_area.json`
- `baseline_tests/step29_common.py`
- `baseline_tests/run_step29_candidate_fingerprint_guard.py`
- `baseline_tests/run_step29_64_stability_driver.py`
- `baseline_tests/run_step29_stability_envelope_summary.py`
- `baseline_tests/run_step29_engineering_vs_link_area_envelope.py`
- `baseline_tests/run_step29_force_reaction_envelope.py`
- `baseline_tests/run_step29_area_scale_envelope.py`
- `baseline_tests/run_step29_step28_prefix_regression.py`
- `baseline_tests/run_step29_quality_report_aggregation.py`
- `baseline_tests/run_step29_step28_regression_guard.py`
- `baseline_tests/run_step29_artifact_manifest.py`
- `tests/test_step29_controlled_real_geometry_64_stability_envelope_contract.py`

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
- `docs/28_controlled_real_geometry_64_transfer_diagnostics.md`

## 3. Explicit Non-Goals

Step 29 does not add actuation, swimming, new coupling formulas, LBM formula changes, MPM constitutive changes, projection formula changes, mesh repair behavior, remeshing behavior, sparse storage, two-phase flow, contact-angle physics, or edits to `external/taichi_LBM3D`.

## 4. Candidate Fingerprint Guard

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_candidate_fingerprint_guard.py
```

Artifacts:

- `outputs/step29_candidate_fingerprint_guard/fingerprint_guard.csv`
- `outputs/step29_candidate_fingerprint_guard/fingerprint_guard.json`
- `logs/step29_candidate_fingerprint_guard.log`

Result:

- `row_count = 2`
- `pass_count = 2`
- mesh SHA-256: `d5a3dd8a698a81951052c6fc3aeb1dd37f7a3c205c07b23d514a3b6a77c2c126`
- voxel SHA-256: `7df9048eb5967888f0788817414b05235fe4a67367198ad82fdb571d92e3b01f`
- both descriptor fingerprints and sizes match the Step 25 manifest
- both Step 26 generated GeometryConfig files remain strict quality-enabled

## 5. 64^3 Stability Driver

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_64_stability_driver.py
```

Artifacts:

- `outputs/step29_64_stability_driver/stability_driver_results.csv`
- `outputs/step29_64_stability_driver/stability_driver_results.npz`
- `outputs/step29_64_stability_driver/stability_driver_results.json`
- `logs/step29_64_stability_driver.log`

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
- `min_rho_min_global = 0.9912939667701721`
- `max_rho_max_global = 1.0088865756988525`
- `max_lbm_max_v_global = 0.006207805592566729`
- `min_mpm_min_J_global = 0.9996678233146667`
- `max_mpm_max_speed_global = 0.029222209006547928`
- `min_projected_mass = 0.09944118559360504`
- `min_active_cell_count = 31116`
- `min_bb_link_count_min = 101868`
- `max_hydro_force_max_norm = 0.4191468060016632`
- `max_driver_total_time = 53.283917299995665`

Rows:

| candidate | transfer | rho_min | rho_max | lbm_max_v | mpm_min_J | projected_mass | hydro_force_max_norm | bb_link_count_min | bb_link_count_max | area_scale_final |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mesh | engineering | 0.9954622983932495 | 1.0043507814407349 | 0.005689762067049742 | 0.9999962449073792 | 0.605826735496521 | 0.4173511266708374 | 498338 | 498714 | 1.0 |
| mesh | link_area_experimental | 0.9954623579978943 | 1.0043507814407349 | 0.005689778830856085 | 0.9999967217445374 | 0.6058268547058105 | 0.4173510670661926 | 498338 | 498714 | 0.8084830641746521 |
| voxel | engineering | 0.9912939667701721 | 1.008886456489563 | 0.0062076859176158905 | 0.9996681809425354 | 0.09944122284650803 | 0.41914668679237366 | 101868 | 102144 | 1.0 |
| voxel | link_area_experimental | 0.9912940263748169 | 1.0088865756988525 | 0.006207805592566729 | 0.9996678233146667 | 0.09944118559360504 | 0.4191468060016632 | 101868 | 102144 | 0.7987391352653503 |

Every row completed 20 LBM steps and 100 MPM substeps with `cell_force_max_norm = 0`, no NaN, no Inf, and a strict quality report.

## 6. Stability Envelope Summary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_stability_envelope_summary.py
```

Artifacts:

- `outputs/step29_stability_envelope_summary/stability_envelope.csv`
- `outputs/step29_stability_envelope_summary/stability_envelope.json`
- `logs/step29_stability_envelope_summary.log`

Result:

- `row_count = 4`
- `pass_count = 4`
- every row has 21 diagnostic rows from step 0 through step 20

Envelope:

| candidate | transfer | rho_min | rho_max | lbm_max_v | mpm_min_J | mpm_max_speed | projected_mass_min | projected_mass_max | bb_link_min | bb_link_max |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mesh | engineering | 0.9954622983932495 | 1.0043507814407349 | 0.005689762067049742 | 0.9999962449073792 | 0.026136981323361397 | 0.6058241128921509 | 0.605826735496521 | 498338 | 498714 |
| mesh | link_area_experimental | 0.9954623579978943 | 1.0043507814407349 | 0.005689778830856085 | 0.9999967217445374 | 0.026136916130781174 | 0.60582435131073 | 0.6058268547058105 | 498338 | 498714 |
| voxel | engineering | 0.9912939667701721 | 1.008886456489563 | 0.0062076859176158905 | 0.9996681809425354 | 0.029221393167972565 | 0.09944095462560654 | 0.09944122284650803 | 101868 | 102144 |
| voxel | link_area_experimental | 0.9912940263748169 | 1.0088865756988525 | 0.006207805592566729 | 0.9996678233146667 | 0.029222209006547928 | 0.09944095462560654 | 0.09944118559360504 | 101868 | 102144 |

## 7. Engineering Vs Link-Area Envelope

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_engineering_vs_link_area_envelope.py
```

Artifacts:

- `outputs/step29_engineering_vs_link_area_envelope/engineering_vs_link_area_envelope.csv`
- `outputs/step29_engineering_vs_link_area_envelope/engineering_vs_link_area_envelope.json`
- `logs/step29_engineering_vs_link_area_envelope.log`

Result:

- `row_count = 2`
- `pass_count = 2`

Comparison deltas:

| candidate | rho_min_delta | rho_max_delta | lbm_max_v_delta | mpm_min_J_delta | projected_mass_delta | hydro_force_max_norm_delta | active_cell_count_delta | bb_link_count_delta | link_area_area_scale_final |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mesh | 5.960464477539063e-08 | 0.0 | 1.6763806343078613e-08 | 4.76837158203125e-07 | 1.1920928955078125e-07 | -5.960464477539063e-08 | 0 | 0 | 0.8084830641746521 |
| voxel | 5.960464477539063e-08 | 1.1920928955078125e-07 | 1.19674950838089e-07 | -3.5762786865234375e-07 | -3.725290298461914e-08 | 1.1920928955078125e-07 | 0 | 0 | 0.7987391352653503 |

The comparison is diagnostic and bounded only.

## 8. Force And Reaction Envelope

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_force_reaction_envelope.py
```

Artifacts:

- `outputs/step29_force_reaction_envelope/force_reaction_envelope.csv`
- `outputs/step29_force_reaction_envelope/force_reaction_envelope.json`
- `logs/step29_force_reaction_envelope.log`

Result:

- `row_count = 4`
- `pass_count = 4`
- every row has 20 post-step rows

Force and reaction envelope:

| candidate | transfer | hydro_force_min | hydro_force_max | hydro_force_final | max_grid_reaction_min | max_grid_reaction_max | active_reaction_particles | bb_link_min | bb_link_max |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mesh | engineering | 0.4162072539329529 | 0.4173511266708374 | 0.4164999723434448 | 4.213553893350763e-06 | 4.21738923250814e-06 | 4096 | 498338 | 498714 |
| mesh | link_area_experimental | 0.4162072539329529 | 0.4173510670661926 | 0.41649991273880005 | 4.213553438603412e-06 | 4.21738923250814e-06 | 4096 | 498338 | 498714 |
| voxel | engineering | 0.4170735478401184 | 0.41914668679237366 | 0.41731515526771545 | 4.216079105390236e-06 | 4.2174419832008425e-06 | 4096 | 101868 | 102144 |
| voxel | link_area_experimental | 0.4170735478401184 | 0.4191468060016632 | 0.4173150062561035 | 4.216079105390236e-06 | 4.217441528453492e-06 | 4096 | 101868 | 102144 |

All rows have finite force/reaction diagnostics and `positive_post_step_pass = true`.

## 9. Area-Scale Envelope

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_area_scale_envelope.py
```

Artifacts:

- `outputs/step29_area_scale_envelope/area_scale_envelope.csv`
- `outputs/step29_area_scale_envelope/area_scale_envelope.json`
- `logs/step29_area_scale_envelope.log`

Result:

- `row_count = 2`
- `pass_count = 2`

Envelope:

| candidate | area_scale_initial | area_scale_min_observed | area_scale_max_observed | area_scale_final | raw_area_scale_min | raw_area_scale_max | hit_lower_bound | hit_upper_bound |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| mesh | 1.0 | 0.8084830641746521 | 1.0 | 0.8084830641746521 | 0.8084830641746521 | 1.0 | false | false |
| voxel | 1.0 | 0.7987391352653503 | 1.0 | 0.7987391352653503 | 0.7987391352653503 | 1.0 | false | false |

The area-scale script uses the currently exposed final area scale plus the configured initialization baseline. It does not change solver or coupler formulas.

## 10. Step 28 Prefix Regression

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_step28_prefix_regression.py
```

Artifacts:

- `outputs/step29_step28_prefix_regression/step28_prefix_regression.csv`
- `outputs/step29_step28_prefix_regression/step28_prefix_regression.json`
- `logs/step29_step28_prefix_regression.log`

Result:

- `row_count = 4`
- `pass_count = 4`

Prefix deltas at step 10:

| candidate | transfer | rho_min_delta | rho_max_delta | lbm_max_v_delta | mpm_min_J_delta | projected_mass_delta | active_cell_count_delta | bb_link_count_delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mesh | engineering | -1.1920928955078125e-07 | 0.0 | -7.916241884231567e-09 | -5.960464477539063e-08 | -5.960464477539062e-07 | 0 | 0 |
| mesh | link_area_experimental | 1.7881393432617188e-07 | 1.1920928955078125e-07 | 2.7939677238464355e-09 | 2.384185791015625e-07 | 5.364418029785156e-07 | 0 | 0 |
| voxel | engineering | -1.7881393432617188e-07 | -1.1920928955078125e-07 | -3.259629011154175e-08 | 5.960464477539063e-08 | 1.1920928955078125e-07 | 0 | 0 |
| voxel | link_area_experimental | 0.0 | -1.1920928955078125e-07 | 4.516914486885071e-08 | -1.7881393432617188e-07 | -8.195638656616211e-08 | 0 | 0 |

The Step 28 and Step 29 time-series rows were compared at `step = 10` using semantically matching fields.

## 11. Quality Report Aggregation

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_quality_report_aggregation.py
```

Artifacts:

- `outputs/step29_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step29_quality_report_aggregation/quality_report_summary.json`
- `logs/step29_quality_report_aggregation.log`

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

## 12. Step 28 Regression Guard

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_step28_regression_guard.py
```

Artifacts:

- `outputs/step29_step28_regression_guard/step28_regression_guard.csv`
- `outputs/step29_step28_regression_guard/step28_regression_guard.json`
- `logs/step29_step28_regression_guard.log`

Summary:

- `row_count = 8`
- `pass_count = 8`
- `step28_driver_row_count = 4`
- `step28_stable_count = 4`
- `step28_quality_report_count = 4`
- `step28_quality_pass_count = 4`
- `step28_comparison_pass_count = 2`
- `step28_large_file_count = 0`

## 13. Artifact Manifest Summary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_artifact_manifest.py
```

Artifacts:

- `outputs/step29_artifact_manifest/artifact_manifest.csv`
- `outputs/step29_artifact_manifest/artifact_summary.csv`
- `outputs/step29_artifact_manifest/artifact_summary.json`
- `logs/step29_artifact_manifest.log`

Summary:

- `file_count = 1761`
- `large_file_count = 0`
- `raw_candidate_large_file_count = 0`
- `scan_data_file_count = 0`
- `private_absolute_path_count = 0`
- `step29_driver_config_count = 4`
- `step29_file_count = 62`
- `step29_particle_npy_count = 0`
- `step29_quality_report_count = 4`
- `step29_total_size_bytes = 3382772`
- `step29_total_size_mb = 3.226062774658203`
- `step29_vtr_count = 0`
- `total_size_bytes = 149095382`
- `total_size_mb = 142.1884365081787`

## 14. Verification Commands

Commands used:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile baseline_tests\step29_common.py baseline_tests\run_step29_candidate_fingerprint_guard.py baseline_tests\run_step29_64_stability_driver.py baseline_tests\run_step29_stability_envelope_summary.py baseline_tests\run_step29_engineering_vs_link_area_envelope.py baseline_tests\run_step29_force_reaction_envelope.py baseline_tests\run_step29_area_scale_envelope.py baseline_tests\run_step29_step28_prefix_regression.py baseline_tests\run_step29_quality_report_aggregation.py baseline_tests\run_step29_step28_regression_guard.py baseline_tests\run_step29_artifact_manifest.py tests\test_step29_controlled_real_geometry_64_stability_envelope_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_candidate_fingerprint_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_64_stability_driver.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_stability_envelope_summary.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_engineering_vs_link_area_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_force_reaction_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_area_scale_envelope.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_step28_prefix_regression.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_step28_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step29_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step29_controlled_real_geometry_64_stability_envelope_contract.py -q
pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Full pytest output is stored in `logs/step29_pytest.log`.

## 15. GitHub Sync Information

- target branch: `origin/main`
- commit message: `test: add step29 controlled real geometry 64 stability envelope`
- final commit hash: reported in the completion message after push

## 16. Acceptance Checklist

- [x] candidate fingerprint guard passes
- [x] Step 25 manifest fingerprints match current candidate files
- [x] Step 26 generated GeometryConfig files remain valid
- [x] mesh 64^3 moving_boundary engineering 20-step row passes
- [x] mesh 64^3 moving_boundary link_area 20-step row passes
- [x] voxel 64^3 moving_boundary engineering 20-step row passes
- [x] voxel 64^3 moving_boundary link_area 20-step row passes
- [x] every Step 29 driver row writes geometry_quality_report.json
- [x] every Step 29 quality gate is strict
- [x] every Step 29 quality report passes
- [x] quality warning count == 0
- [x] quality error count == 0
- [x] all driver rows have completed_lbm_steps >= 20
- [x] all driver rows have total_mpm_substeps >= 100
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
- [x] stability envelope summary passes
- [x] engineering vs link_area envelope passes for mesh
- [x] engineering vs link_area envelope passes for voxel
- [x] force/reaction envelope passes
- [x] link_area rows have finite bounded area_scale
- [x] area_scale envelope summary passes
- [x] Step 28 prefix regression passes at step=10
- [x] Step 28 regression guard passes
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
- [x] no Step 29 .vtr outputs
- [x] no Step 29 particle .npy outputs
- [x] artifact large_file_count == 0
- [x] Step 29 output total size budget passes
- [x] repo artifact_summary total_size_mb < 175
- [x] logs/step29_pytest.log exists
- [x] pytest -q passes
- [x] Step 29 contract test passes
- [x] git diff --check passes
- [x] staged whitespace check passes
- [x] pre-push hook passes
- [x] Step 29 artifacts are pushed to origin/main

## 17. Decision For Step 30

If Step 29 passes, Step 30 should not jump directly to actuation. A conservative Step 30 direction is `Step 30 Controlled Squid Proxy Region Geometry Contract`. Step 30 should define region semantics for a squid-like proxy without actuation, including mantle outer region, mantle cavity proxy, funnel or siphon outlet proxy, head and arms coarse proxy, optional fin region, body axis, reference length, and region IDs.
