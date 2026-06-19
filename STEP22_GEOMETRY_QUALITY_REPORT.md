# Step 22 Geometry Quality Report

## 1. Goal

Step 22 adds diagnostic quality checks for imported mesh and voxel geometry.
Step 22 is a geometry QA and import robustness layer, not real squid validation.

The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Imported geometry remains limited to small synthetic voxel and mesh fixtures.
The Step 22 mesh path is not production mesh repair or automatic remeshing.

The implementation adds mesh quality diagnostics, voxel quality diagnostics, a geometry quality aggregator, an optional quality gate, expected-failure fixtures, sampling sensitivity diagnostics, and optional `FSIDriver3D` quality report output.

## 2. Files Created And Updated

Created:

- `src/mesh_quality.py`
- `src/voxel_quality.py`
- `src/geometry_quality.py`
- `data/geometry_fixtures/bad_nonwatertight.obj`
- `data/geometry_fixtures/bad_degenerate.obj`
- `data/geometry_fixtures/bad_empty_voxel.npy`
- `data/geometry_fixtures/bad_empty_voxel_metadata.json`
- `configs/step22_quality_*.json`
- `configs/step22_resolution_sweep_*.json`
- `configs/step22_driver_quality_gate_*.json`
- `baseline_tests/step22_common.py`
- `baseline_tests/run_step22_mesh_quality_sanity.py`
- `baseline_tests/run_step22_voxel_quality_sanity.py`
- `baseline_tests/run_step22_bad_geometry_failure_checks.py`
- `baseline_tests/run_step22_sampling_resolution_sensitivity.py`
- `baseline_tests/run_step22_driver_quality_gate_smoke.py`
- `baseline_tests/run_step22_artifact_manifest.py`
- `docs/21_geometry_quality_checks.md`
- `tests/test_step22_geometry_quality_contract.py`

Updated:

- `src/geometry_config.py`
- `src/fsi_config.py`
- `src/fsi_driver.py`
- `src/__init__.py`
- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/12_geometry_ingestion.md`
- `docs/19_geometry_import_pipeline.md`
- `docs/20_imported_geometry_scale_validation.md`

## 3. Explicit Non-Goals

- No new FSI physics.
- No change to `PenaltyFSICoupler3D`.
- No change to `MovingBoundaryFSICoupler3D`.
- No change to `LinkAreaMovingBoundaryCoupler3D`.
- No change to the moving bounce-back formula.
- No change to LBM step formulas.
- No change to default `reaction_transfer_mode = "engineering"`.
- No squid actuation or swimming validation.
- No real squid validation.
- No production mesh repair.
- No automatic remeshing.
- No sparse storage.
- No `ReducedSquidFSI`.
- No edits to `external/taichi_LBM3D`.

## 4. Mesh Quality Sanity

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_mesh_quality_sanity.py
```

Artifact: `outputs/step22_mesh_quality_sanity/mesh_quality_results.csv`.

| case | geometry_type | quality_kind | strict | pass | severity | boundary_edge_count | degenerate_face_count | volume_abs | stable |
| ---- | ------------- | ------------ | ------ | ---- | -------- | ------------------: | --------------------: | ---------: | ------ |
| mesh_cube | mesh | mesh | false | true | ok | 0 | 0 | 0.810000000 | true |
| mesh_ellipsoid | mesh | mesh | false | true | ok | 0 | 0 | 0.219916728 | true |

Both small synthetic mesh fixtures have finite vertices, valid face indices, no boundary edges, no nonmanifold edges, and positive absolute volume proxy.

## 5. Voxel Quality Sanity

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_voxel_quality_sanity.py
```

Artifact: `outputs/step22_voxel_quality_sanity/voxel_quality_results.csv`.

| case | geometry_type | quality_kind | strict | pass | severity | occupied_count | connected_component_count | largest_component_fraction | stable |
| ---- | ------------- | ------------ | ------ | ---- | -------- | -------------: | ------------------------: | -------------------------: | ------ |
| voxel_sphere | voxel | voxel | false | true | ok | 3016 | 1 | 1.000000000 | true |

The voxel sphere fixture is non-empty, connected, does not touch the domain boundary, and has both surface and interior voxels.

## 6. Bad Geometry Failure Checks

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_bad_geometry_failure_checks.py
```

Artifact: `outputs/step22_bad_geometry_failure_checks/bad_geometry_results.csv`.

| case | geometry_type | quality_kind | strict | pass | severity | boundary_edge_count | nonmanifold_edge_count | degenerate_face_count | occupied_count | connected_component_count | expected_failure |
| ---- | ------------- | ------------ | ------ | ---- | -------- | ------------------: | ---------------------: | --------------------: | -------------: | ------------------------: | ---------------- |
| bad_nonwatertight | mesh | mesh | true | false | error | 4 | 0 | 0 | 0 | 0 | true |
| bad_degenerate | mesh | mesh | true | false | error | 3 | 1 | 1 | 0 | 0 | true |
| bad_empty_voxel | voxel | voxel | true | false | error | 0 | 0 | 0 | 0 | 0 | true |

These are intentional small bad fixtures. The strict quality gate rejects them and records the expected failures instead of weakening the checks.

## 7. Sampling Resolution Sensitivity

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_sampling_resolution_sensitivity.py
```

Artifact: `outputs/step22_sampling_resolution_sensitivity/resolution_sensitivity.csv`.

| case | geometry_type | quality_kind | strict | pass | severity | particles_per_axis_hint | mesh_voxel_resolution | geometry_volume | projected_mass | relative_mass_error | active_cell_count | stable |
| ---- | ------------- | ------------ | ------ | ---- | -------- | ----------------------: | --------------------: | --------------: | -------------: | ------------------: | ----------------: | ------ |
| voxel_sphere | voxel | voxel | false | true | ok | 24 | 32 | 0.099441056 | 0.099441066 | 0.000000075 | 5286 | true |
| voxel_sphere | voxel | voxel | false | true | ok | 32 | 32 | 0.099441056 | 0.099441119 | 0.000000599 | 5286 | true |
| voxel_sphere | voxel | voxel | false | true | ok | 40 | 32 | 0.099441056 | 0.099441111 | 0.000000524 | 5286 | true |
| mesh_ellipsoid | mesh | mesh | false | true | ok | 24 | 24 | 0.133917160 | 0.133916989 | 0.000001224 | 6415 | true |
| mesh_ellipsoid | mesh | mesh | false | true | ok | 32 | 32 | 0.133917160 | 0.133917034 | 0.000000890 | 6415 | true |
| mesh_ellipsoid | mesh | mesh | false | true | ok | 40 | 48 | 0.133917160 | 0.133917123 | 0.000000223 | 6415 | true |

All rows have finite projected mass, positive active cell count, and stable status.

## 8. Driver Quality Gate Smoke

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_driver_quality_gate_smoke.py
```

Artifacts:

- `outputs/step22_driver_quality_gate_smoke/quality_gate_driver_results.csv`
- `outputs/step22_driver_quality_gate_smoke/voxel_sphere_penalty/geometry_quality_report.json`
- `outputs/step22_driver_quality_gate_smoke/mesh_cube_moving_boundary/geometry_quality_report.json`

| case | geometry_type | quality_kind | strict | pass | severity | mode | reaction_transfer_mode | rho_min | rho_max | lbm_max_v | mpm_min_J | projected_mass | active_cell_count | stable |
| ---- | ------------- | ------------ | ------ | ---- | -------- | ---- | ---------------------- | ------: | ------: | --------: | --------: | -------------: | ----------------: | ------ |
| voxel_sphere | voxel | voxel | false | true | ok | penalty | engineering | 0.999998152 | 1.000002742 | 0.000005304 | 0.999995947 | 0.099441066 | 5294 | true |
| mesh_cube | mesh | mesh | false | true | ok | moving_boundary | engineering | 0.995754659 | 1.005024076 | 0.004645086 | 0.995930254 | 0.747852743 | 28648 | true |

The driver quality gate is opt-in and non-strict for these good smoke cases. It writes `geometry_quality_report.json` before imported-geometry sampling and leaves the FSI mode behavior unchanged.

## 9. Artifact Manifest Summary

The final artifact manifest is generated after pytest so it includes `logs/step22_pytest.log`. The authoritative artifact counts are in `outputs/step22_artifact_manifest/artifact_summary.json`.

| metric | value |
| ------ | ----: |
| large_file_count | 0 |

## 10. Verification Commands

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_mesh_quality_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_voxel_quality_sanity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_bad_geometry_failure_checks.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_sampling_resolution_sensitivity.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_driver_quality_gate_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step22_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step22_geometry_quality_contract.py -q
git diff --check
```

## 11. GitHub Sync Information

Target branch: `origin/main`.

This report is part of the Step 22 commit pushed after verification. The final commit hash is reported in the completion message.

## 12. Acceptance Checklist

- [x] mesh quality sanity passes
- [x] voxel quality sanity passes
- [x] bad geometry failure checks pass
- [x] sampling resolution sensitivity passes
- [x] driver quality gate smoke passes
- [x] GeometryConfig quality_check_enabled defaults to false
- [x] FSIDriver3D default behavior unchanged when quality_check_enabled is false
- [x] no FSI formula changes
- [x] default reaction_transfer_mode remains engineering
- [x] no production mesh repair claims
- [x] no automatic remeshing claims
- [x] no real squid validation claims
- [x] no external/taichi_LBM3D edits
- [x] artifact large_file_count == 0
- [x] logs/step22_pytest.log exists
- [x] pytest -q passes
- [x] Git pre-push pytest hook passes
- [x] git diff --check passes
- [x] Step 22 artifacts are pushed to GitHub origin/main

## 13. Decision For Step 23

Step 22 supports proceeding to Step 23 planning with the same constraints: keep imported geometry quality checks diagnostic, keep real squid validation out of scope until a separate goal introduces controlled real geometry, and do not replace the existing coupling paths without explicit regression evidence.
