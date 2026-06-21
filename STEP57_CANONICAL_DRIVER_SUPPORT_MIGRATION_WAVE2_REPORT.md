# Step 57 Canonical Driver Support Migration Wave 2 Report

## Summary

Step 57 migrates the second ownership batch into canonical package modules. This batch covers driver support, diagnostics, run utilities, link-area and momentum-accounting support, and geometry support modules.

The legacy root files remain compatibility shims, so existing imports such as `from src.geometry import GeometrySampler3D` continue to resolve to the same object as the canonical import.

## Migrated Implementation Owners

| Canonical implementation | Legacy compatibility shim |
| --- | --- |
| `src/mpm_lbm/sim/drivers/sim_config.py` | `src/sim_config.py` |
| `src/mpm_lbm/sim/drivers/fsi_config.py` | `src/fsi_config.py` |
| `src/mpm_lbm/sim/io/run_utils.py` | `src/run_utils.py` |
| `src/mpm_lbm/diagnostics/fsi_diagnostics.py` | `src/diagnostics.py` |
| `src/mpm_lbm/sim/coupling/link_area_accounting.py` | `src/link_area_accounting.py` |
| `src/mpm_lbm/sim/coupling/link_area.py` | `src/link_area_coupling.py` |
| `src/mpm_lbm/sim/coupling/momentum_accounting.py` | `src/momentum_accounting.py` |
| `src/mpm_lbm/sim/geometry/config.py` | `src/geometry_config.py` |
| `src/mpm_lbm/sim/geometry/utils.py` | `src/geometry_utils.py` |
| `src/mpm_lbm/sim/geometry/mesh_io.py` | `src/mesh_io.py` |
| `src/mpm_lbm/sim/geometry/mesh_quality.py` | `src/mesh_quality.py` |
| `src/mpm_lbm/sim/geometry/voxel_io.py` | `src/voxel_io.py` |
| `src/mpm_lbm/sim/geometry/voxel_quality.py` | `src/voxel_quality.py` |
| `src/mpm_lbm/sim/geometry/importers.py` | `src/geometry_import.py` |
| `src/mpm_lbm/sim/geometry/sampler.py` | `src/geometry.py` |
| `src/mpm_lbm/sim/geometry/quality.py` | `src/geometry_quality.py` |

## `src.__init__` Export Repair

Step 57 updates lazy `from src import ...` exports for the migrated symbols so they point at canonical package modules where practical.

The export audit also verifies that the existing `src.calibration` targets resolve, so calibration exports are preserved rather than removed.

## Intentionally Unmigrated

The following areas remain outside Step 57:

- `src/fsi_driver.py`
- boundary motion, wall velocity, runtime geometry, diagnostic geometry, geometry displacement, intake, candidate, fingerprint, normalization, and real-geometry modules
- squid proxy modules
- `external/taichi_LBM3D`
- `data/real_geometry_candidates`

## Evidence Artifacts

- `outputs/step57_driver_support_migration_audit/driver_support_migration_audit.json`
- `outputs/step57_import_execution_audit/import_execution_audit.json`
- `outputs/step57_legacy_shim_audit/legacy_shim_audit.json`
- `outputs/step57_src_init_export_audit/src_init_export_audit.json`
- `outputs/step57_behavior_preservation_audit/behavior_preservation_audit.json`
- `outputs/step57_step56_regression_guard/step56_regression_guard.json`
- `outputs/step57_artifact_manifest/artifact_summary.json`

## Boundary

Step 57 does not change default solver behavior, migrate `FSIDriver3D`, add a larger physics run, validate jet propulsion, implement squid swimming, prove grid convergence, or claim production readiness.

The Step 56 behavior-preservation audit still records its original protected-path assumption. Step 57 therefore adds a regression guard that allows only the Step 57 policy-listed support-layer paths to supersede that Step 56 assumption; other Step 56 failures remain blocking.

## Validation

The Step 57 validation commands are:

```powershell
D:\working\taichi\env\python.exe baseline_tests/run_step57_driver_support_migration_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step57_import_execution_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step57_legacy_shim_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step57_src_init_export_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step57_behavior_preservation_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step57_step56_regression_guard.py
D:\working\taichi\env\python.exe baseline_tests/run_step57_artifact_manifest.py
D:\working\taichi\env\python.exe -m pytest -q tests/test_step57_driver_support_migration_contract.py tests/test_step57_import_execution_contract.py tests/test_step57_legacy_shim_contract.py tests/test_step57_src_init_export_contract.py tests/test_step57_behavior_preservation_contract.py tests/test_step57_step56_regression_contract.py
D:\working\taichi\env\python.exe -m pytest -q
D:\TOOL\Anaconda\python.exe -m pytest -q
```

Final pass counts are recorded in the committed logs and command output after validation.
