# Step 58 Canonical FSIDriver Implementation Migration Wave 3 Report

## Summary

Step 58 moves the real `FSIDriver3D` implementation into `src/mpm_lbm/sim/drivers/fsi_driver.py`.

The legacy `src/fsi_driver.py` file is now a compatibility shim that imports from the canonical module. Existing `src.fsi_driver` imports therefore continue to resolve to the same `FSIDriver3D` object and the same `DIAGNOSTIC_FIELDS` value.

## Migrated Implementation Owner

| Canonical implementation | Legacy compatibility shim |
| --- | --- |
| `src/mpm_lbm/sim/drivers/fsi_driver.py` | `src/fsi_driver.py` |

`src.__init__` now resolves `FSIDriver3D` through `src.mpm_lbm.sim.drivers.fsi_driver`.

## Temporary Optional Bridges

The driver still has optional hooks whose real implementations are intentionally outside Step 58. To keep canonical driver imports self-contained, Step 58 adds temporary bridge surfaces:

| Canonical bridge | Legacy implementation |
| --- | --- |
| `src/mpm_lbm/sim/motion/boundary_motion_interface.py` | `src/boundary_motion_interface.py` |
| `src/mpm_lbm/sim/motion/geometry_motion_interface.py` | `src/geometry_motion_interface.py` |
| `src/mpm_lbm/sim/wall_velocity/application.py` | `src/wall_velocity_application.py` |

These bridges are marked temporary until Step 59 and use `legacy_getattr`. They are not real implementation migrations.

## Intentionally Unmigrated

The following areas remain outside Step 58:

- boundary-motion implementation modules
- wall-velocity implementation modules
- runtime geometry, diagnostic geometry, geometry displacement, intake, candidate, fingerprint, normalization, and real-geometry modules
- squid proxy modules
- `external/taichi_LBM3D`
- `data/real_geometry_candidates`

## Evidence Artifacts

- `outputs/step58_fsidriver_migration_audit/fsidriver_migration_audit.json`
- `outputs/step58_import_execution_audit/import_execution_audit.json`
- `outputs/step58_legacy_shim_audit/legacy_shim_audit.json`
- `outputs/step58_optional_bridge_audit/optional_bridge_audit.json`
- `outputs/step58_behavior_preservation_audit/behavior_preservation_audit.json`
- `outputs/step58_step57_regression_guard/step57_regression_guard.json`
- `outputs/step58_artifact_manifest/artifact_summary.json`

## Boundary

Step 58 does not change default solver behavior, add a larger physics run, activate runtime geometry, expand moving-wall velocity behavior, validate jet propulsion, implement squid swimming, prove grid convergence, or claim production readiness.

The Step 56 behavior-preservation audit still records its original protected-path assumption. Step 58 therefore extends the regression supersession to allow the policy-listed `src/fsi_driver.py` migration while keeping unrelated Step 56 failures blocking.

## Validation

The Step 58 validation commands are:

```powershell
D:\working\taichi\env\python.exe baseline_tests/run_step58_fsidriver_migration_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step58_import_execution_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step58_legacy_shim_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step58_optional_bridge_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step58_behavior_preservation_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step58_step57_regression_guard.py
D:\working\taichi\env\python.exe baseline_tests/run_step58_artifact_manifest.py
D:\working\taichi\env\python.exe -m pytest -q tests/test_step58_fsidriver_migration_contract.py tests/test_step58_import_execution_contract.py tests/test_step58_legacy_shim_contract.py tests/test_step58_optional_bridge_contract.py tests/test_step58_behavior_preservation_contract.py tests/test_step58_step57_regression_contract.py
D:\working\taichi\env\python.exe -m pytest -q
D:\TOOL\Anaconda\python.exe -m pytest -q
```

## Acceptance Checklist

- [x] `FSIDriver3D` real implementation lives in `src/mpm_lbm/sim/drivers/fsi_driver.py`.
- [x] `src/fsi_driver.py` is a thin compatibility shim.
- [x] Canonical driver source has no root `src.fsi_driver` reverse dependency.
- [x] Canonical driver source does not use `legacy_getattr`.
- [x] Optional motion and wall-velocity bridge surfaces are explicitly temporary until Step 59.
- [x] Constructor-only behavior preservation check does not create an output directory.
- [x] Step 57 regression guard passes with Step 58 supersession.
- [x] Artifact manifest reports no large Step 58 files, `.vtr` files, particle `.npy` files, external solver edits, or real-geometry candidate edits.
- [x] Step 58 artifacts are pushed to GitHub origin/main.
