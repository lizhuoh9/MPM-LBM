# Step 30 Controlled Squid Proxy Region Geometry Report

Step 30 is controlled squid proxy region geometry.
Step 30 defines squid-like region semantics only.
Step 30 is not real squid validation.
Step 30 does not implement squid actuation.
Step 30 does not implement squid swimming.
Step 30 does not implement mantle contraction.
Step 30 does not implement funnel actuation.
Step 30 does not implement new FSI physics.
The default quality_check_enabled remains false.
The default quality_check_strict remains false.
The default reaction_transfer_mode remains engineering.
The moving bounce-back formula is unchanged.
PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.

No FSI, LBM, MPM, moving bounce-back, link-area, or projection formula files were edited.

## 1. Goal

Step 30 adds a controlled static region contract for the procedural `squid_proxy` geometry. It defines stable squid-like proxy region IDs, a body frame convention, allowed semantic overlaps, deterministic mask diagnostics, quality checks, and projection-only region accumulation.

Step 30 deliberately stops before actuation, swimming, new coupling behavior, or real squid validation.

## 2. Files Created And Updated

Created:

- `STEP30_CONTROLLED_SQUID_PROXY_REGION_GEOMETRY_GOAL.md`
- `STEP30_CONTROLLED_SQUID_PROXY_REGION_GEOMETRY_REPORT.md`
- `docs/30_controlled_squid_proxy_region_geometry.md`
- `src/squid_region_config.py`
- `src/squid_proxy_regions.py`
- `src/squid_region_quality.py`
- `src/squid_region_projection.py`
- `configs/step30_squid_proxy_geometry.json`
- `configs/step30_squid_proxy_region_config.json`
- `baseline_tests/step30_common.py`
- `baseline_tests/run_step30_region_schema_validation.py`
- `baseline_tests/run_step30_region_mask_sampling.py`
- `baseline_tests/run_step30_region_quality.py`
- `baseline_tests/run_step30_region_overlap_diagnostics.py`
- `baseline_tests/run_step30_region_projection_smoke.py`
- `baseline_tests/run_step30_step29_regression_guard.py`
- `baseline_tests/run_step30_artifact_manifest.py`
- `tests/test_step30_squid_proxy_region_geometry_contract.py`

Updated:

- `README.md`
- `docs/08_roadmap.md`
- `docs/09_api_reference.md`
- `docs/11_artifact_policy.md`
- `docs/12_geometry_ingestion.md`
- `docs/29_controlled_real_geometry_64_stability_envelope.md`
- `src/__init__.py`

Generated artifacts:

- `outputs/step30_region_schema_validation/region_schema_validation.csv`
- `outputs/step30_region_schema_validation/region_schema_validation.json`
- `outputs/step30_region_mask_sampling/region_mask_summary.csv`
- `outputs/step30_region_mask_sampling/region_mask_summary.json`
- `outputs/step30_region_quality/region_quality.csv`
- `outputs/step30_region_quality/region_quality.json`
- `outputs/step30_region_overlap_diagnostics/region_overlap_matrix.csv`
- `outputs/step30_region_overlap_diagnostics/region_overlap_summary.json`
- `outputs/step30_region_projection_smoke/region_projection_results.csv`
- `outputs/step30_region_projection_smoke/region_projection_results.json`
- `outputs/step30_step29_regression_guard/step29_regression_guard.csv`
- `outputs/step30_step29_regression_guard/step29_regression_guard.json`
- `outputs/step30_artifact_manifest/artifact_manifest.csv`
- `outputs/step30_artifact_manifest/artifact_summary.csv`
- `outputs/step30_artifact_manifest/artifact_summary.json`
- `logs/step30_*.log`

## 3. Explicit Non-Goals

Step 30 does not add prescribed motion, mantle volume change, funnel motion, jetting, free-body motion, new FSI physics, production mesh repair, automatic remeshing, real squid validation, or final readiness claims.

The mantle cavity proxy is a static semantic region. The funnel outlet proxy is a static semantic region. Neither is used as an internal fluid cavity, an aperture controller, a jet model, or a driver input.

## 4. Region Schema Validation

Runner:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_schema_validation.py
```

Result:

- required region count: 7
- present required region count: 7
- body axis: `+y`
- reference length: `1.0`
- body-frame origin finite: true
- all region IDs unique: true
- all regions have `active_for_actuation = false`
- schema pass: true

Required regions:

- `mantle_outer`
- `mantle_cavity_proxy`
- `funnel_outlet_proxy`
- `head_proxy`
- `arms_proxy`
- `left_fin_proxy`
- `right_fin_proxy`

## 5. Region Mask Sampling

Runner:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_mask_sampling.py
```

Result:

| region_id | count | estimated_volume |
| --- | ---: | ---: |
| mantle_outer | 648 | 0.019775390625 |
| mantle_cavity_proxy | 100 | 0.0030517578125 |
| funnel_outlet_proxy | 8 | 0.000244140625 |
| head_proxy | 136 | 0.004150390625 |
| arms_proxy | 34 | 0.00103759765625 |
| left_fin_proxy | 18 | 0.00054931640625 |
| right_fin_proxy | 18 | 0.00054931640625 |

Deterministic sample count: 32768.

Sampled position hash:

```text
987cd215a4766383f4d396989265a1ca3ec0aa89b00fcb60b42130823ea6a9de
```

Region assignment hash:

```text
d2c6519395ad7c789a729511e37124f0dc65f3f79f9a0203ffc8b1cd023be0d9
```

Both hashes repeated exactly across the second run.

## 6. Region Quality

Runner:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_quality.py
```

Result:

- quality row count: 11
- pass count: 11
- missing required region count: 0
- forbidden claim count: 0
- mantle cavity inside mantle condition: recorded
- funnel outlet near mantle boundary condition: recorded
- region quality pass: true

## 7. Region Overlap Diagnostics

Runner:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_overlap_diagnostics.py
```

Result:

- matrix rows: 49
- matrix finite: true
- diagonal match count: 7
- diagonal mismatch count: 0
- intentional overlap count: 14
- unintended overlap count: 0
- overlap pass: true

Intentional overlaps are documented in `configs/step30_squid_proxy_region_config.json`.

## 8. Region Projection Smoke

Runner:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_projection_smoke.py
```

Result:

- grid sizes: 32 and 48
- row count: 14
- pass count: 14
- projected mass total: 0.0587158203125
- active cell count total: 1924
- NaN count: 0
- Inf count: 0
- projection pass: true

This is projection-only. It does not run `FSIDriver3D`.

## 9. Step 29 Regression Guard

Runner:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_step29_regression_guard.py
```

Result:

- guard row count: 7
- pass count: 7
- Step 29 driver row count: 4
- Step 29 stable count: 4
- Step 29 quality report count: 4
- Step 29 quality pass count: 4
- Step 29 large file count: 0
- Step 29 raw candidate large file count: 0
- Step 29 scan data file count: 0

## 10. Artifact Manifest Summary

The final artifact manifest is generated by:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_artifact_manifest.py
```

Acceptance policy:

- `large_file_count == 0`
- `step30_total_size_mb < 5`
- repository `total_size_mb < 180`
- no Step 30 `.vtr`
- no Step 30 particle `.npy`
- no raw candidate large files
- no scan data
- no private absolute paths

The committed manifest files are:

- `outputs/step30_artifact_manifest/artifact_manifest.csv`
- `outputs/step30_artifact_manifest/artifact_summary.csv`
- `outputs/step30_artifact_manifest/artifact_summary.json`

## 11. Verification Commands

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile src\squid_region_config.py src\squid_proxy_regions.py src\squid_region_quality.py src\squid_region_projection.py baseline_tests\step30_common.py baseline_tests\run_step30_region_schema_validation.py baseline_tests\run_step30_region_mask_sampling.py baseline_tests\run_step30_region_quality.py baseline_tests\run_step30_region_overlap_diagnostics.py baseline_tests\run_step30_region_projection_smoke.py baseline_tests\run_step30_step29_regression_guard.py baseline_tests\run_step30_artifact_manifest.py tests\test_step30_squid_proxy_region_geometry_contract.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_schema_validation.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_mask_sampling.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_quality.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_overlap_diagnostics.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_region_projection_smoke.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_step29_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step30_artifact_manifest.py
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step30_squid_proxy_region_geometry_contract.py -q
pytest -q
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

`logs/step30_pytest.log` records the full pytest result.

## 12. GitHub Sync Information

The user approved push after Step 30 modifications. The final commit hash and remote `origin/main` confirmation are reported in the Codex final response after the approved push completes.

## 13. Acceptance Checklist

- [x] region schema validation passes
- [x] required squid proxy regions exist
- [x] region IDs are unique
- [x] body axis is defined
- [x] reference length is positive
- [x] body-frame origin is finite
- [x] mantle_outer region exists
- [x] mantle_cavity_proxy region exists
- [x] funnel_outlet_proxy region exists
- [x] head_proxy region exists
- [x] arms_proxy region exists
- [x] fin proxy regions exist or are explicitly disabled
- [x] region mask sampling is deterministic
- [x] region-assignment hash is repeatable
- [x] sampled-position hash is repeatable
- [x] every required region has finite diagnostics
- [x] solid regions have positive count
- [x] cavity proxy has positive count
- [x] funnel outlet proxy has positive count
- [x] region overlap diagnostics pass
- [x] intentional overlaps are documented
- [x] projection-only smoke passes at 32^3
- [x] projection-only smoke passes at 48^3
- [x] region projected mass is finite
- [x] region active cell count is finite
- [x] no NaN
- [x] no Inf
- [x] Step 29 regression guard passes
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
- [x] no Step 30 .vtr outputs
- [x] no Step 30 particle .npy outputs
- [x] artifact large_file_count == 0
- [x] Step 30 output total-size budget passes
- [x] repo artifact summary total_size_mb < 180
- [x] logs/step30_pytest.log exists
- [x] full pytest passes
- [x] Step 30 contract test passes
- [x] git diff --check passes
- [x] staged whitespace check passes
- [x] pre-push hook passes
- [x] Step 30 artifacts are pushed to origin/main

## 14. Decision For Step 31

Step 31 should be `Controlled Squid Proxy Region Projection And Static Driver Smoke`.

The next step can add region-aware static driver diagnostics and a short 48^3 static moving-boundary smoke. It should still avoid actuation. Prescribed mantle or funnel kinematics should remain a later step after region-aware projection and static-driver evidence are stable.
