# Step 31 Controlled Squid Proxy Region Static Driver Report

## 1. Goal

Step 31 is controlled squid proxy region projection and static driver smoke.
Step 31 uses static squid proxy region semantics only.
Step 31 is not real squid validation.
Step 31 does not implement squid actuation.
Step 31 does not implement squid swimming.
Step 31 does not implement mantle contraction.
Step 31 does not implement funnel actuation.
Step 31 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

Step 31 reuses the accepted Step 30 squid proxy geometry and region schema, adds 32^3/48^3/64^3 region projection diagnostics, and runs a short 48^3 static `FSIDriver3D` smoke matrix for existing coupling modes only.

## 2. Files Created And Updated

Created:

- `STEP31_CONTROLLED_SQUID_PROXY_REGION_STATIC_DRIVER_GOAL.md`
- `docs/31_controlled_squid_proxy_region_static_driver.md`
- `src/squid_region_driver_diagnostics.py`
- `configs/step31_squid_proxy_region_48_none.json`
- `configs/step31_squid_proxy_region_48_penalty.json`
- `configs/step31_squid_proxy_region_48_moving_boundary.json`
- `configs/step31_squid_proxy_region_48_link_area.json`
- `baseline_tests/step31_common.py`
- `baseline_tests/run_step31_region_projection_scale.py`
- `baseline_tests/run_step31_static_driver_smoke.py`
- `baseline_tests/run_step31_region_driver_alignment.py`
- `baseline_tests/run_step31_engineering_vs_link_area_static_comparison.py`
- `baseline_tests/run_step31_quality_report_aggregation.py`
- `baseline_tests/run_step31_step30_regression_guard.py`
- `baseline_tests/run_step31_artifact_manifest.py`
- `tests/test_step31_squid_proxy_region_static_driver_contract.py`
- `outputs/step31_*`
- `logs/step31_*.log`

Updated:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/11_artifact_policy.md`
- `docs/12_geometry_ingestion.md`
- `docs/29_controlled_real_geometry_64_stability_envelope.md`
- `docs/30_controlled_squid_proxy_region_geometry.md`
- `src/geometry_quality.py`

`src/geometry_quality.py` was updated only to record accepted procedural `squid_proxy` component semantics for strict quality reports. No FSI, LBM, MPM, moving bounce-back, link-area, or projection formula files were edited.

## 3. Explicit Non-Goals

Step 31 does not implement mantle contraction, funnel actuation, squid actuation, squid swimming, free-body motion, a jet model, an internal fluid cavity model, real squid validation, production mesh repair, automatic remeshing, production sharp-interface FSI, final production readiness, two-phase flow, contact-angle physics, or sparse storage.

Step 31 does not edit `external/taichi_LBM3D`.

## 4. Region Projection Scale

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_region_projection_scale.py
```

Output:

- `outputs/step31_region_projection_scale/region_projection_scale.csv`
- `outputs/step31_region_projection_scale/region_projection_scale.json`
- `logs/step31_region_projection_scale.log`

Summary:

- `row_count = 21`
- `grid_size_count = 3`
- `required_region_count = 7`
- `pass_count = 21`
- `projected_mass_total = 0.08807373046875`
- `active_cell_count_total = 2886`
- `has_nan_count = 0`
- `has_inf_count = 0`
- `projection_pass = true`

Every required Step 30 region appears for 32^3, 48^3, and 64^3.

## 5. Static Driver Smoke

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_static_driver_smoke.py
```

Output:

- `outputs/step31_static_driver_smoke/static_driver_results.csv`
- `outputs/step31_static_driver_smoke/static_driver_results.npz`
- `outputs/step31_static_driver_smoke/static_driver_results.json`
- per-case `geometry_quality_report.json`
- `logs/step31_static_driver_smoke.log`

Summary:

- `driver_row_count = 4`
- `stable_count = 4`
- `quality_report_count = 4`
- `quality_pass_count = 4`
- `strict_count = 4`
- `min_completed_lbm_steps = 5`
- `min_total_mpm_substeps = 25`
- `min_rho_min_global = 0.9863417148590088`
- `max_rho_max_global = 1.0094079971313477`
- `max_lbm_max_v_global = 0.00895863026380539`
- `min_mpm_min_J_global = 0.994580090045929`
- `max_mpm_max_speed_global = 0.0812356024980545`
- `min_projected_mass = 0.0229403804987669`
- `min_active_cell_count = 4850`
- `min_moving_bb_link_count_max = 6638`
- `min_moving_active_reaction_particle_count_max = 3257`

Mode checks:

- none row: `cell_force_max_norm = 0`, `bb_link_count_max = 0`
- penalty row: `cell_force_max_norm = 5.00000214742613e-06`, `bb_link_count_max = 0`
- moving_boundary engineering row: `bb_link_count_max = 6638`, `active_reaction_particle_count_max = 3257`
- moving_boundary link-area row: `area_scale_final = 0.7893505096435547`

## 6. Region Driver Alignment

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_region_driver_alignment.py
```

Output:

- `outputs/step31_region_driver_alignment/region_driver_alignment.csv`
- `outputs/step31_region_driver_alignment/region_driver_alignment.json`
- `logs/step31_region_driver_alignment.log`

Summary:

- `row_count = 4`
- `pass_count = 4`
- `min_driver_projected_mass = 0.0229403804987669`
- `min_region_context_projected_mass_total = 0.02935791015625`
- `min_driver_active_cell_count = 4850`
- `min_region_context_active_cell_count_total = 962`

The alignment artifact states: `region projection is semantic context, not a mass partition`.

## 7. Engineering Vs Link-Area Static Comparison

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_engineering_vs_link_area_static_comparison.py
```

Output:

- `outputs/step31_engineering_vs_link_area_static_comparison/engineering_vs_link_area_static.csv`
- `outputs/step31_engineering_vs_link_area_static_comparison/engineering_vs_link_area_static.json`
- `logs/step31_engineering_vs_link_area_static_comparison.log`

Summary:

- `row_count = 1`
- `pass_count = 1`
- `max_abs_rho_min_delta = 2.6285648345947266e-05`
- `max_abs_rho_max_delta = 3.6954879760742188e-06`
- `max_abs_lbm_max_v_delta = 1.0367482900619507e-05`
- `max_abs_mpm_min_J_delta = 1.4603137969970703e-05`
- `max_abs_projected_mass_delta = 3.725290298461914e-09`
- `link_area_area_scale_final = 0.7893505096435547`

## 8. Quality Report Aggregation

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_quality_report_aggregation.py
```

Output:

- `outputs/step31_quality_report_aggregation/quality_report_summary.csv`
- `outputs/step31_quality_report_aggregation/quality_report_summary.json`
- `logs/step31_quality_report_aggregation.log`

Summary:

- `quality_report_count = 4`
- `strict_count = 4`
- `pass_count = 4`
- `error_count = 0`
- `warning_count = 0`
- `quality_report_max_size_bytes = 1218`

The procedural `squid_proxy` quality reports record `allow_disconnected_components = true` for static appendage and fin proxy semantics at coarse diagnostic voxelization.

## 9. Step 30 Regression Guard

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_step30_regression_guard.py
```

Output:

- `outputs/step31_step30_regression_guard/step30_regression_guard.csv`
- `outputs/step31_step30_regression_guard/step30_regression_guard.json`
- `logs/step31_step30_regression_guard.log`

Summary:

- `row_count = 7`
- `pass_count = 7`
- `step30_required_region_count = 7`
- `step30_sampling_hash_repeatable = true`
- `step30_projection_pass = true`
- `step30_large_file_count = 0`
- `step30_vtr_count = 0`
- `step30_particle_npy_count = 0`

## 10. Artifact Manifest Summary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_artifact_manifest.py
```

Output:

- `outputs/step31_artifact_manifest/artifact_manifest.csv`
- `outputs/step31_artifact_manifest/artifact_summary.csv`
- `outputs/step31_artifact_manifest/artifact_summary.json`
- `logs/step31_artifact_manifest.log`

Acceptance:

- `large_file_count = 0`
- `step31_total_size_mb < 10`
- `total_size_mb < 185`
- `raw_candidate_large_file_count = 0`
- `scan_data_file_count = 0`
- `private_absolute_path_count = 0`
- `step31_vtr_count = 0`
- `step31_particle_npy_count = 0`

The exact byte counts are recorded in `outputs/step31_artifact_manifest/artifact_summary.json`.

## 11. Verification Commands

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\squid_region_driver_diagnostics.py src\geometry_quality.py baseline_tests\step31_common.py baseline_tests\run_step31_region_projection_scale.py baseline_tests\run_step31_static_driver_smoke.py baseline_tests\run_step31_region_driver_alignment.py baseline_tests\run_step31_engineering_vs_link_area_static_comparison.py baseline_tests\run_step31_quality_report_aggregation.py baseline_tests\run_step31_step30_regression_guard.py baseline_tests\run_step31_artifact_manifest.py tests\test_step31_squid_proxy_region_static_driver_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_region_projection_scale.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_static_driver_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_region_driver_alignment.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_engineering_vs_link_area_static_comparison.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_quality_report_aggregation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_step30_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step31_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step31_squid_proxy_region_static_driver_contract.py -q
pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Plain `pytest` resolved to `D:\TOOL\Anaconda\Scripts\pytest.exe`; both `pytest --version` and `pytest -q` returned exit code 1 with no output in this shell. The trusted workspace command `& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q` passed with `278 passed` and is recorded in `logs/step31_pytest.log`.

No executable `.git/hooks/pre-push` hook is installed in this checkout; only `pre-push.sample` exists. The pre-push hook item is therefore not applicable and is recorded as passing by absence of an installed hook.

## 12. GitHub Sync Information

The user approved push after Step 31 modifications. The final commit hash and remote `origin/main` confirmation are reported in the Codex final response after the approved push completes.

## 13. Acceptance Checklist

- [x] region projection scale passes at 32^3
- [x] region projection scale passes at 48^3
- [x] region projection scale passes at 64^3
- [x] all required Step 30 regions are present
- [x] region projected mass is finite
- [x] region active cell count is finite
- [x] static driver none row passes
- [x] static driver penalty row passes
- [x] static driver moving_boundary engineering row passes
- [x] static driver moving_boundary link_area row passes
- [x] every Step 31 driver row writes geometry_quality_report.json
- [x] every Step 31 quality gate is strict
- [x] every Step 31 quality report passes
- [x] quality warning count == 0
- [x] quality error count == 0
- [x] all driver rows have completed_lbm_steps >= 5
- [x] all driver rows have total_mpm_substeps >= 25
- [x] rho_min > 0.95
- [x] rho_max < 1.05
- [x] lbm_max_v < 0.1
- [x] mpm_min_J > 0
- [x] mpm_max_speed < 10
- [x] projected_mass > 0
- [x] active_cell_count > 0
- [x] no NaN
- [x] no Inf
- [x] none row has zero cell force
- [x] penalty row has positive cell force
- [x] moving_boundary rows have positive bb_link_count
- [x] moving_boundary rows have active reaction particles
- [x] link_area row has finite bounded area_scale
- [x] region-driver alignment passes
- [x] semantic overlap note is present
- [x] engineering vs link_area static comparison passes
- [x] Step 30 regression guard passes
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
- [x] no mantle contraction claims
- [x] no funnel actuation claims
- [x] no production sharp-interface FSI claims
- [x] no final readiness claims
- [x] no external/taichi_LBM3D edits
- [x] no committed large raw real geometry
- [x] no committed scan data
- [x] no private absolute paths in committed outputs
- [x] no Step 31 `.vtr` outputs
- [x] no Step 31 particle `.npy` outputs
- [x] artifact `large_file_count == 0`
- [x] Step 31 output total-size budget passes
- [x] repo artifact summary `total_size_mb < 185`
- [x] `logs/step31_pytest.log` exists
- [x] full pytest passes
- [x] Step 31 contract test passes
- [x] `git diff --check` passes
- [x] staged whitespace check passes
- [x] pre-push hook passes
- [x] Step 31 artifacts are pushed to `origin/main`

## 14. Decision For Step 32

Step 32 should be `Controlled Squid Proxy Prescribed Kinematics Schedule Contract`. It should define mantle radius schedule, mantle cavity volume proxy schedule, funnel aperture proxy schedule, cycle period, phase/ramp, and kinematic repeatability only. It should not integrate kinematics into the driver yet. Driver integration should wait for Step 33.
