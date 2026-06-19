# Step 25 Controlled Real Geometry Intake Report

## 1. Goal

Step 25 is controlled real geometry intake, not real squid validation.
Step 25 performs geometry QA, normalization, fingerprinting, sampling reproducibility, and projection-only smoke diagnostics.
Step 25 does not implement squid swimming.
Step 25 does not implement squid actuation.
Step 25 does not implement new FSI physics.
Step 25 does not validate production sharp-interface FSI.

The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.
Candidate intake does not perform production mesh repair or automatic remeshing.
Raw large real geometry files and scan data are not committed.

Step 25 adds a descriptor-driven candidate intake contract with file fingerprinting, manifest output, strict mesh/voxel QA, normalization reports, deterministic sampling checks, and projection-only diagnostics.

## 2. Files Created And Updated

Created:

- `STEP25_CONTROLLED_REAL_GEOMETRY_INTAKE_GOAL.md`
- `STEP25_CONTROLLED_REAL_GEOMETRY_INTAKE_REPORT.md`
- `src/geometry_fingerprint.py`
- `src/geometry_candidate_manifest.py`
- `src/geometry_normalization.py`
- `src/geometry_intake.py`
- `configs/step25_candidate_smoke_mesh_descriptor.json`
- `configs/step25_candidate_smoke_voxel_descriptor.json`
- `configs/step25_intake_policy.json`
- `data/geometry_fixtures/step25_real_candidate_smoke_mesh.obj`
- `data/real_geometry_candidates/README.md`
- `data/real_geometry_candidates/.gitkeep`
- `baseline_tests/step25_common.py`
- `baseline_tests/run_step25_candidate_manifest.py`
- `baseline_tests/run_step25_real_geometry_intake_smoke.py`
- `baseline_tests/run_step25_mesh_candidate_quality.py`
- `baseline_tests/run_step25_voxel_candidate_quality.py`
- `baseline_tests/run_step25_normalization_reports.py`
- `baseline_tests/run_step25_sampling_reproducibility.py`
- `baseline_tests/run_step25_projection_smoke.py`
- `baseline_tests/run_step25_step24_regression_guard.py`
- `baseline_tests/run_step25_artifact_manifest.py`
- `docs/24_controlled_real_geometry_intake.md`
- `docs/25_real_geometry_candidate_policy.md`
- `tests/test_step25_controlled_real_geometry_intake_contract.py`

Updated:

- `.gitignore`
- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/11_artifact_policy.md`
- `docs/12_geometry_ingestion.md`
- `docs/19_geometry_import_pipeline.md`
- `docs/21_geometry_quality_checks.md`
- `docs/22_quality_gated_imported_geometry_validation.md`
- `docs/23_strict_quality_gated_imported_geometry_long_run.md`

## 3. Explicit Non-Goals

- No squid swimming.
- No squid actuation.
- No new FSI physics.
- No production sharp-interface FSI validation.
- No change to `PenaltyFSICoupler3D`.
- No change to `MovingBoundaryFSICoupler3D`.
- No change to `LinkAreaMovingBoundaryCoupler3D`.
- No change to the moving bounce-back formula.
- No change to LBM step formulas.
- No change to MPM constitutive formulas.
- No change to projection formulas.
- No production mesh repair.
- No automatic remeshing.
- No two-phase flow.
- No contact angle physics.
- No sparse storage.
- No edits to `external/taichi_LBM3D`.
- No committed raw large real geometry or scan data.

## 4. Candidate Manifest

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_candidate_manifest.py
```

Artifacts:

- `outputs/step25_candidate_manifest/candidate_manifest.csv`
- `outputs/step25_candidate_manifest/candidate_manifest.json`
- `logs/step25_candidate_manifest.log`

Results:

| candidate_id | type | size_bytes | sha256 | pass |
| ------------ | ---- | ---------: | ------ | ---- |
| real_candidate_smoke_mesh | mesh | 323 | d5a3dd8a698a81951052c6fc3aeb1dd37f7a3c205c07b23d514a3b6a77c2c126 | true |
| real_candidate_smoke_voxel | voxel | 32896 | 7df9048eb5967888f0788817414b05235fe4a67367198ad82fdb571d92e3b01f | true |

Row count: 2. Candidate IDs are unique. Both descriptors use `validation_scope = intake_qa_normalization_sampling_projection_only`, `quality_check_enabled = true`, and `quality_check_strict = true`.

## 5. Intake Smoke

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_real_geometry_intake_smoke.py
```

Artifacts:

- `outputs/step25_real_geometry_intake_smoke/intake_smoke_summary.csv`
- `outputs/step25_real_geometry_intake_smoke/intake_smoke_summary.json`
- `logs/step25_real_geometry_intake_smoke.log`

Results:

| candidate_id | type | manifest_pass | quality_pass | normalization_pass | severity |
| ------------ | ---- | ------------- | ------------ | ------------------ | -------- |
| real_candidate_smoke_mesh | mesh | true | true | true | ok |
| real_candidate_smoke_voxel | voxel | true | true | true | ok |

Row count: 2. This smoke path is descriptor, fingerprint, load, QA, normalization, and manifest only.

## 6. Mesh Candidate Quality

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_mesh_candidate_quality.py
```

Artifacts:

- `outputs/step25_mesh_candidate_quality/mesh_candidate_quality.csv`
- `outputs/step25_mesh_candidate_quality/mesh_candidate_quality.json`
- `outputs/step25_mesh_candidate_quality/real_candidate_smoke_mesh/geometry_quality_report.json`
- `logs/step25_mesh_candidate_quality.log`

Result: 1 row. `real_candidate_smoke_mesh` has 8 vertices, 12 faces, valid face indices, 0 degenerate faces, 0 boundary edges, 0 nonmanifold edges, `quality_pass = true`, and `quality_severity = ok`.

## 7. Voxel Candidate Quality

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_voxel_candidate_quality.py
```

Artifacts:

- `outputs/step25_voxel_candidate_quality/voxel_candidate_quality.csv`
- `outputs/step25_voxel_candidate_quality/voxel_candidate_quality.json`
- `outputs/step25_voxel_candidate_quality/real_candidate_smoke_voxel/geometry_quality_report.json`
- `logs/step25_voxel_candidate_quality.log`

Result: 1 row. `real_candidate_smoke_voxel` has 3016 occupied voxels, 1 connected component, largest component fraction 1.0, `quality_pass = true`, and `quality_severity = ok`.

## 8. Normalization Reports

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_normalization_reports.py
```

Artifacts:

- `outputs/step25_normalization_reports/normalization_summary.csv`
- `outputs/step25_normalization_reports/normalization_summary.json`
- `outputs/step25_normalization_reports/real_candidate_smoke_mesh/normalization_report.json`
- `outputs/step25_normalization_reports/real_candidate_smoke_voxel/normalization_report.json`
- `logs/step25_normalization_reports.log`

Results:

| candidate_id | type | inside_domain | scale_factor | translation | source_modified | repair | remeshing |
| ------------ | ---- | ------------- | -----------: | ----------- | --------------- | ------ | --------- |
| real_candidate_smoke_mesh | mesh | true | 0.840000000 | [0.5, 0.5, 0.5] | false | false | false |
| real_candidate_smoke_voxel | voxel | true | 1.000000000 | [0.0, 0.0, 0.0] | false | false | false |

Normalization is report-only for Step 25. Source files are unchanged.

## 9. Sampling Reproducibility

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_sampling_reproducibility.py
```

Artifacts:

- `outputs/step25_sampling_reproducibility/sampling_reproducibility.csv`
- `outputs/step25_sampling_reproducibility/sampling_reproducibility.json`
- `logs/step25_sampling_reproducibility.log`

Results:

| candidate_id | particles | geometry_volume | mass_sum | position_hash_repeat | vol0_hash_repeat | mass_hash_repeat |
| ------------ | --------: | --------------: | -------: | -------------------- | ---------------- | ---------------- |
| real_candidate_smoke_mesh | 4096 | 0.605826126536 | 0.605826258659 | true | true | true |
| real_candidate_smoke_voxel | 4096 | 0.099441055985 | 0.099441058934 | true | true | true |

Both candidates have `relative_mass_error = 0.0` and `reproducibility_pass = true`.

## 10. Projection Smoke

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_projection_smoke.py
```

Artifacts:

- `outputs/step25_projection_smoke/projection_smoke_results.csv`
- `outputs/step25_projection_smoke/projection_smoke_results.json`
- `logs/step25_projection_smoke.log`

Results:

| candidate_id | projected_mass | active_cell_count | solid_phi_min | solid_phi_max | has_nan | has_inf | pass |
| ------------ | -------------: | ----------------: | ------------: | ------------: | ------- | ------- | ---- |
| real_candidate_smoke_mesh | 0.605826199055 | 23961 | 0.0 | 1.0 | false | false | true |
| real_candidate_smoke_voxel | 0.099441058934 | 5286 | 0.0 | 1.0 | false | false | true |

Projection smoke initializes the projection path only. It is not an FSI driver validation matrix.

## 11. Step 24 Regression Guard

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_step24_regression_guard.py
```

Artifacts:

- `outputs/step25_step24_regression_guard/step24_regression_guard.csv`
- `outputs/step25_step24_regression_guard/step24_regression_guard.json`
- `logs/step25_step24_regression_guard.log`

Results: 6 guard rows, 6 pass. Step 24 quality report count remains 9 and Step 24 large file count remains 0.

## 12. Artifact Manifest Summary

Command:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_artifact_manifest.py
```

Artifacts:

- `outputs/step25_artifact_manifest/artifact_manifest.csv`
- `outputs/step25_artifact_manifest/artifact_summary.csv`
- `outputs/step25_artifact_manifest/artifact_summary.json`
- `logs/step25_artifact_manifest.log`

Final manifest summary after baseline generation, report writing, and `logs/step25_pytest.log` generation:

| metric | value |
| ------ | ----: |
| file_count | 1435 |
| total_size_bytes | 130614774 |
| total_size_mb | 124.563955 |
| large_file_count | 0 |
| step25_file_count | 47 |
| step25_total_size_bytes | 430667 |
| step25_total_size_mb | 0.410716 |
| step25_vtr_count | 0 |
| step25_particle_npy_count | 0 |
| raw_candidate_large_file_count | 0 |
| scan_data_file_count | 0 |
| step25_descriptor_count | 2 |
| step25_policy_doc_count | 2 |

The final manifest was regenerated after this report and `logs/step25_pytest.log` were present.

## 13. Verification Commands

Executed or required in this order:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\geometry_intake.py src\geometry_fingerprint.py src\geometry_normalization.py src\geometry_candidate_manifest.py baseline_tests\step25_common.py baseline_tests\run_step25_candidate_manifest.py baseline_tests\run_step25_real_geometry_intake_smoke.py baseline_tests\run_step25_mesh_candidate_quality.py baseline_tests\run_step25_voxel_candidate_quality.py baseline_tests\run_step25_normalization_reports.py baseline_tests\run_step25_sampling_reproducibility.py baseline_tests\run_step25_projection_smoke.py baseline_tests\run_step25_step24_regression_guard.py baseline_tests\run_step25_artifact_manifest.py tests\test_step25_controlled_real_geometry_intake_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_candidate_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_real_geometry_intake_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_mesh_candidate_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_voxel_candidate_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_normalization_reports.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_sampling_reproducibility.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_projection_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_step24_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step25_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step25_controlled_real_geometry_intake_contract.py -q
git diff --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

The full pytest output is written to `logs/step25_pytest.log`.

## 14. GitHub Sync Information

Target remote branch: `origin/main`.

This report is part of the Step 25 commit. The final pushed commit hash is reported in the completion message because a git commit cannot embed its own final hash without changing that hash.

## 15. Acceptance Checklist

- [x] candidate manifest generation passes
- [x] candidate descriptors are valid
- [x] candidate IDs are unique
- [x] raw candidate geometry commit policy is enforced
- [x] mesh candidate strict quality report passes
- [x] voxel candidate strict quality report passes
- [x] normalization reports are finite and domain-bounded
- [x] normalization does not perform repair
- [x] normalization does not perform remeshing
- [x] original candidate files are not modified
- [x] deterministic sampling reproducibility passes
- [x] sampled_position_hash is repeatable
- [x] particle mass hash is repeatable
- [x] particle volume hash is repeatable
- [x] projection smoke passes
- [x] projected_mass > 0
- [x] active_cell_count > 0
- [x] projection smoke has no NaN
- [x] projection smoke has no Inf
- [x] projection smoke is not reported as FSI validation
- [x] Step 24 regression guard passes
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
- [x] no private absolute geometry paths in committed manifest outputs
- [x] no Step 25 .vtr outputs
- [x] no Step 25 particle .npy outputs
- [x] artifact large_file_count == 0
- [x] Step 25 output total size budget passes
- [x] repo artifact_summary total_size_mb < 160
- [x] logs/step25_pytest.log exists
- [x] pytest -q passes
- [x] Step 25 contract test passes
- [x] git diff --check passes
- [x] pre-push hook passes if push is performed
- [x] Step 25 artifacts are pushed to GitHub origin/main unless user explicitly says not to push

## 16. Decision For Step 26

Step 26 should be Controlled Real Geometry Projection-Only And Short Driver Feasibility.

It should start from Step 25 candidate intake artifacts and remain conservative:

- controlled real geometry projection-only diagnostics;
- optional very short driver feasibility;
- no squid actuation;
- no swimming;
- no production sharp-interface FSI claim;
- no final readiness claim.
