# Step 57 Goal: Canonical Driver Support Migration Wave 2

## Source Of Truth

This file is the detailed Step 57 goal. The short active Codex goal should reference this file instead of duplicating the full contract.

Step 57 starts from the accepted Step 56 state:

- Repository: `lizhuoh9/MPM-LBM`
- Branch: `main`
- Accepted Step 56 commit: `354cccacc4610aae82427dd28c658e35eb26c62d`
- Step 56 meaning: Wave 1 runtime leaf implementations are now real canonical implementations, and corresponding root modules are compatibility shims.

GitHub Actions still has no remote workflow-run evidence for this repository, so local artifacts, logs, and the ECC pre-push hook are the authoritative validation proof.

## Step Name

`Step 57 Canonical Driver Support Migration Wave 2`

## Commit Message

`test: add step57 canonical driver support migration wave2`

## Primary Objective

Migrate the direct support layer needed before full `FSIDriver3D` migration. Step 57 must not migrate the full driver. It prepares Step 58 by moving driver config, unified sim config, IO utilities, FSI diagnostics, link-area/momentum support, and core geometry support into canonical package modules.

After this step, the required dependency direction for migrated modules is:

```text
canonical support module -> real implementation
legacy root module -> thin compatibility shim -> canonical support module
```

The forbidden direction is:

```text
canonical support module -> lazy wrapper -> legacy root implementation
```

## Explicit Non-Goals

Do not do any of the following in Step 57:

- No `48^3` `link_area_experimental` run.
- No longer cycle.
- No `64^3` run.
- No LBM tau formula migration.
- No standard viscosity migration.
- No historical physics rerun.
- No default solver behavior change.
- No full `FSIDriver3D` migration.
- No full wall-velocity application migration.
- No runtime-geometry proxy implementation migration.
- No Step 50/51/52 physics artifact regeneration beyond necessary path/metadata guards.
- No edits under `external/taichi_LBM3D`.
- No edits under `data/real_geometry_candidates`.
- No real jet validation.
- No jet propulsion validation.
- No squid swimming.
- No grid convergence claim.
- No production-readiness claim.

## Files To Migrate

### Driver Config / Sim Config

The canonical files must contain the real implementations after Step 57:

| Canonical file | Legacy shim file | Symbols |
| --- | --- | --- |
| `src/mpm_lbm/sim/drivers/sim_config.py` | `src/sim_config.py` | `UnifiedSimConfig` |
| `src/mpm_lbm/sim/drivers/fsi_config.py` | `src/fsi_config.py` | `FSIDriverConfig` |

Required dependency rewiring:

- `src/mpm_lbm/sim/drivers/sim_config.py` imports `src.mpm_lbm.sim.lbm.config.LBMConfig`.
- `src/mpm_lbm/sim/drivers/sim_config.py` imports `src.mpm_lbm.sim.mpm.config.MPMConfig`.
- `src/mpm_lbm/sim/drivers/fsi_config.py` imports `src.mpm_lbm.sim.drivers.sim_config.UnifiedSimConfig`.
- `src/mpm_lbm/sim/drivers/fsi_config.py` imports `src.mpm_lbm.sim.geometry.config.VALID_GEOMETRY_TYPES`.
- Canonical driver config modules must not import legacy root `src.sim_config`, `src.fsi_config`, or `src.geometry_config`.

### Driver IO Utilities

| Canonical file | Legacy shim file |
| --- | --- |
| `src/mpm_lbm/sim/io/run_utils.py` | `src/run_utils.py` |

### FSI Diagnostics

| Canonical file | Legacy shim file | Symbols |
| --- | --- | --- |
| `src/mpm_lbm/diagnostics/fsi_diagnostics.py` | `src/diagnostics.py` | `FSIDiagnostics3D` |

`src/mpm_lbm/diagnostics/__init__.py` must explicitly export `FSIDiagnostics3D`.

### Link-Area And Momentum Support

| Canonical file | Legacy shim file | Symbols |
| --- | --- | --- |
| `src/mpm_lbm/sim/coupling/link_area_accounting.py` | `src/link_area_accounting.py` | `LinkAreaMomentumAccounting3D`, `direction_metadata`, `summarize_link_accounting` |
| `src/mpm_lbm/sim/coupling/link_area.py` | `src/link_area_coupling.py` | `LinkAreaMovingBoundaryCoupler3D` |
| `src/mpm_lbm/sim/coupling/momentum_accounting.py` | `src/momentum_accounting.py` | `MomentumAccounting3D` |

Required dependency rewiring:

- `src/mpm_lbm/sim/coupling/link_area.py` imports canonical `src.mpm_lbm.sim.coupling.link_area_accounting`.
- Canonical link-area modules must not import root `src.link_area_accounting`, `src.link_area_coupling`, or `src.momentum_accounting`.

### Geometry Core Support

Create package:

```text
src/mpm_lbm/sim/geometry/
```

The canonical files must contain real implementations after Step 57:

| Canonical file | Legacy shim file | Primary symbols |
| --- | --- | --- |
| `src/mpm_lbm/sim/geometry/config.py` | `src/geometry_config.py` | `GeometryConfig`, `VALID_GEOMETRY_TYPES` |
| `src/mpm_lbm/sim/geometry/utils.py` | `src/geometry_utils.py` | geometry utility helpers |
| `src/mpm_lbm/sim/geometry/mesh_io.py` | `src/mesh_io.py` | `load_obj`, `write_obj`, `mesh_bounds`, `normalize_vertices` |
| `src/mpm_lbm/sim/geometry/mesh_quality.py` | `src/mesh_quality.py` | `analyze_mesh` |
| `src/mpm_lbm/sim/geometry/voxel_io.py` | `src/voxel_io.py` | `VoxelGeometry`, `load_voxel_geometry`, `save_voxel_geometry`, `voxel_centers_to_points` |
| `src/mpm_lbm/sim/geometry/voxel_quality.py` | `src/voxel_quality.py` | `analyze_voxel_occupancy` |
| `src/mpm_lbm/sim/geometry/importers.py` | `src/geometry_import.py` | `ImportedGeometrySampler3D` |
| `src/mpm_lbm/sim/geometry/sampler.py` | `src/geometry.py` | `GeometrySampler3D` |
| `src/mpm_lbm/sim/geometry/quality.py` | `src/geometry_quality.py` | `GeometryQualityGate`, `analyze_geometry_config` |

Required dependency rewiring:

- `src/mpm_lbm/sim/geometry/sampler.py` imports canonical `config`, `importers`, and `utils`.
- `src/mpm_lbm/sim/geometry/importers.py` imports canonical `mesh_io` and `voxel_io`.
- Canonical geometry modules must not import root `src.geometry`, `src.geometry_config`, `src.geometry_import`, `src.mesh_io`, `src.voxel_io`, or other migrated root geometry modules.

## Files Explicitly Deferred To Step 58+

Do not migrate:

- `src/fsi_driver.py`
- `src/boundary_motion_*.py`
- `src/geometry_motion_*.py`
- `src/wall_velocity_*.py`
- `src/squid_*.py`
- `src/runtime_geometry_*.py`
- `src/diagnostic_geometry_*.py`
- `src/geometry_displacement_*.py`
- `src/geometry_intake.py`
- `src/geometry_candidate_manifest.py`
- `src/geometry_fingerprint.py`
- `src/geometry_normalization.py`
- `src/real_geometry_feasibility.py`

Step 57 must not mix in the motion/wall/runtime proxy chain.

## Legacy Shim Shape

Each migrated legacy file should become a thin shim shaped like:

```python
"""Compatibility shim. Canonical implementation lives in src.mpm_lbm.<...>."""

from .mpm_lbm.<...> import *
```

The shim docstring and import must match the canonical package path.

## Required New Configs

Add:

- `configs/step57_driver_support_migration_policy.json`
- `configs/step57_import_execution_policy.json`
- `configs/step57_legacy_shim_policy.json`
- `configs/step57_src_init_export_policy.json`
- `configs/step57_behavior_preservation_policy.json`

The configs must be data-driven enough for tests and runners to load the migration contract rather than duplicating the full path list inline.

## Required Evidence Tools

Add:

- `src/mpm_lbm/evidence/driver_support_migration_audit.py`
- `src/mpm_lbm/evidence/driver_support_import_execution_audit.py`
- `src/mpm_lbm/evidence/driver_support_legacy_shim_audit.py`
- `src/mpm_lbm/evidence/src_init_export_audit.py`
- `src/mpm_lbm/evidence/driver_support_behavior_preservation_audit.py`

The audit tools must produce deterministic JSON-compatible dictionaries and avoid running the solver.

## Required Baseline Runners

Add:

- `baseline_tests/step57_common.py`
- `baseline_tests/run_step57_driver_support_migration_audit.py`
- `baseline_tests/run_step57_import_execution_audit.py`
- `baseline_tests/run_step57_legacy_shim_audit.py`
- `baseline_tests/run_step57_src_init_export_audit.py`
- `baseline_tests/run_step57_behavior_preservation_audit.py`
- `baseline_tests/run_step57_step56_regression_guard.py`
- `baseline_tests/run_step57_artifact_manifest.py`

The runners must write JSON/CSV artifacts under `outputs/step57_*` and logs under `logs/step57_*.log`.

## Required Tests

Add:

- `tests/test_step57_driver_support_migration_contract.py`
- `tests/test_step57_import_execution_contract.py`
- `tests/test_step57_legacy_shim_contract.py`
- `tests/test_step57_src_init_export_contract.py`
- `tests/test_step57_behavior_preservation_contract.py`
- `tests/test_step57_step56_regression_contract.py`

The tests must verify both source structure and execution behavior. They must not rely only on file names or comments.

## Required Outputs

Generate and commit:

- `outputs/step57_driver_support_migration_audit/driver_support_migration_audit.csv`
- `outputs/step57_driver_support_migration_audit/driver_support_migration_audit.json`
- `outputs/step57_driver_support_migration_audit/driver_support_migration_audit_summary.csv`
- `outputs/step57_import_execution_audit/import_execution_audit.csv`
- `outputs/step57_import_execution_audit/import_execution_audit.json`
- `outputs/step57_import_execution_audit/import_execution_audit_summary.csv`
- `outputs/step57_legacy_shim_audit/legacy_shim_audit.csv`
- `outputs/step57_legacy_shim_audit/legacy_shim_audit.json`
- `outputs/step57_legacy_shim_audit/legacy_shim_audit_summary.csv`
- `outputs/step57_src_init_export_audit/src_init_export_audit.csv`
- `outputs/step57_src_init_export_audit/src_init_export_audit.json`
- `outputs/step57_src_init_export_audit/src_init_export_audit_summary.csv`
- `outputs/step57_behavior_preservation_audit/behavior_preservation_audit.csv`
- `outputs/step57_behavior_preservation_audit/behavior_preservation_audit.json`
- `outputs/step57_behavior_preservation_audit/behavior_preservation_audit_summary.csv`
- `outputs/step57_step56_regression_guard/step56_regression_guard.csv`
- `outputs/step57_step56_regression_guard/step56_regression_guard.json`
- `outputs/step57_step56_regression_guard/step56_regression_guard_summary.csv`
- `outputs/step57_artifact_manifest/artifact_manifest.csv`
- `outputs/step57_artifact_manifest/artifact_summary.csv`
- `outputs/step57_artifact_manifest/artifact_summary.json`
- `logs/step57_*.log`

## Driver Support Migration Audit Contract

For every migrated file pair, verify:

- `canonical_path_exists == true`
- `legacy_path_exists == true`
- `canonical_contains_real_implementation == true`
- `canonical_uses_legacy_getattr == false`
- `canonical_imports_legacy_root == false`
- `legacy_is_shim == true`
- `legacy_imports_canonical == true`
- `forbidden_reverse_dependency == false`
- `pass == true`

Special checks:

- `src/mpm_lbm/sim/drivers/fsi_config.py` must not import `src.fsi_config`.
- `src/mpm_lbm/sim/drivers/sim_config.py` must not import `src.sim_config`.
- `src/mpm_lbm/sim/geometry/sampler.py` must not import `src.geometry`.
- `src/mpm_lbm/sim/coupling/link_area.py` must not import `src.link_area_coupling`.

## Import Execution Audit Contract

The audit must actually import canonical symbols:

```python
from src.mpm_lbm.sim.drivers.sim_config import UnifiedSimConfig
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.io.run_utils import assert_no_nan_inf_array
from src.mpm_lbm.diagnostics.fsi_diagnostics import FSIDiagnostics3D
from src.mpm_lbm.sim.coupling.link_area_accounting import LinkAreaMomentumAccounting3D
from src.mpm_lbm.sim.coupling.link_area import LinkAreaMovingBoundaryCoupler3D
from src.mpm_lbm.sim.coupling.momentum_accounting import MomentumAccounting3D
from src.mpm_lbm.sim.geometry.config import GeometryConfig
from src.mpm_lbm.sim.geometry.sampler import GeometrySampler3D
from src.mpm_lbm.sim.geometry.importers import ImportedGeometrySampler3D
from src.mpm_lbm.sim.geometry.quality import GeometryQualityGate, analyze_geometry_config
from src.mpm_lbm.sim.geometry.mesh_io import load_obj
from src.mpm_lbm.sim.geometry.voxel_io import load_voxel_geometry
```

The audit must also actually import legacy symbols:

```python
from src.fsi_config import FSIDriverConfig
from src.sim_config import UnifiedSimConfig
from src.geometry_config import GeometryConfig
from src.geometry import GeometrySampler3D
from src.geometry_import import ImportedGeometrySampler3D
from src.geometry_quality import GeometryQualityGate
from src.link_area_coupling import LinkAreaMovingBoundaryCoupler3D
```

Acceptance criteria:

- Every canonical import succeeds.
- Every legacy import succeeds.
- Canonical and legacy exported symbols are the same object where applicable.
- Imports do not write output artifacts.
- Imports do not run the solver.

## `src.__init__` Export Audit Contract

Audit `_EXPORT_MODULES` in `src/__init__.py`:

- All target modules exist.
- All exported symbols exist or lazy import resolves.
- No target points to missing `src.calibration`.
- Migrated Step 57 symbols point to canonical paths where practical.
- Lazy import remains enabled.
- Importing `src` does not construct heavy solver objects.

Resolve the stale calibration risk by removing these exports unless a tested `src/calibration.py` is added:

- `classify_calibration_row`
- `choose_recommended_row`
- `write_calibration_summary`

Preferred resolution for Step 57: remove stale exports because calibration is not part of the Step 57 migration target.

## Behavior Preservation Audit Contract

Use lightweight semantic checks only. Do not run large drivers, write VTR files, or write particle NPY outputs.

Required checks:

- `UnifiedSimConfig` defaults unchanged.
- `FSIDriverConfig` defaults unchanged.
- `GeometryConfig` defaults unchanged.
- `GeometrySampler3D` deterministic behavior for a small box sample unchanged.
- `GeometryQualityGate` strict/non-strict behavior unchanged.
- Link-area policy constants unchanged.
- `VALID_COUPLING_MODES` unchanged.
- `VALID_REACTION_TRANSFER_MODES` unchanged.
- `VALID_GEOMETRY_TYPES` unchanged.
- `solver_behavior_changed == false`
- `physics_feature_expansion == false`

## Step 56 Regression Guard

The Step 57 regression guard must keep:

- Step 56 canonical runtime migration audit green.
- Step 56 import execution audit green.
- Step 56 legacy shim audit green.
- Step 56 behavior preservation audit green.
- Step 56 artifact manifest green.
- Step 55 regression still green.

## Documentation Requirements

Add:

- `STEP57_CANONICAL_DRIVER_SUPPORT_MIGRATION_WAVE2_REPORT.md`
- `docs/57_canonical_driver_support_migration_wave2.md`

Update README/progress docs so Step 57 is discoverable and its scope is not confused with a physics validation step.

The report must include:

- What was migrated.
- What remained intentionally unmigrated.
- Evidence artifact paths.
- Commands used for validation.
- Confirmation that Step 57 did not run large physics cases.
- Confirmation that canonical support files are no longer lazy wrappers for the migrated batch.

## Validation Commands

Use `D:\working\taichi\env\python.exe` as the primary validation interpreter.

Required compile check:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\drivers\sim_config.py `
  src\mpm_lbm\sim\drivers\fsi_config.py `
  src\mpm_lbm\sim\io\run_utils.py `
  src\mpm_lbm\diagnostics\fsi_diagnostics.py `
  src\mpm_lbm\sim\coupling\link_area_accounting.py `
  src\mpm_lbm\sim\coupling\link_area.py `
  src\mpm_lbm\sim\coupling\momentum_accounting.py `
  src\mpm_lbm\sim\geometry\config.py `
  src\mpm_lbm\sim\geometry\utils.py `
  src\mpm_lbm\sim\geometry\mesh_io.py `
  src\mpm_lbm\sim\geometry\mesh_quality.py `
  src\mpm_lbm\sim\geometry\voxel_io.py `
  src\mpm_lbm\sim\geometry\voxel_quality.py `
  src\mpm_lbm\sim\geometry\importers.py `
  src\mpm_lbm\sim\geometry\sampler.py `
  src\mpm_lbm\sim\geometry\quality.py `
  src\mpm_lbm\evidence\driver_support_migration_audit.py `
  src\mpm_lbm\evidence\driver_support_import_execution_audit.py `
  src\mpm_lbm\evidence\driver_support_legacy_shim_audit.py `
  src\mpm_lbm\evidence\src_init_export_audit.py `
  src\mpm_lbm\evidence\driver_support_behavior_preservation_audit.py `
  baseline_tests\step57_common.py `
  baseline_tests\run_step57_driver_support_migration_audit.py `
  baseline_tests\run_step57_import_execution_audit.py `
  baseline_tests\run_step57_legacy_shim_audit.py `
  baseline_tests\run_step57_src_init_export_audit.py `
  baseline_tests\run_step57_behavior_preservation_audit.py `
  baseline_tests\run_step57_step56_regression_guard.py `
  baseline_tests\run_step57_artifact_manifest.py `
  tests\test_step57_driver_support_migration_contract.py `
  tests\test_step57_import_execution_contract.py `
  tests\test_step57_legacy_shim_contract.py `
  tests\test_step57_src_init_export_contract.py `
  tests\test_step57_behavior_preservation_contract.py `
  tests\test_step57_step56_regression_contract.py
```

Required audit generation:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step57_driver_support_migration_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step57_import_execution_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step57_legacy_shim_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step57_src_init_export_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step57_behavior_preservation_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step57_step56_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step57_artifact_manifest.py
```

Required focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step57_driver_support_migration_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step57_import_execution_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step57_legacy_shim_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step57_src_init_export_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step57_behavior_preservation_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step57_step56_regression_contract.py -q
```

Required broad validation:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Required git checks:

```powershell
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## Push Requirement

After implementation, tests, artifacts, and documentation are complete:

1. Review `git diff`.
2. Commit all relevant changes with `test: add step57 canonical driver support migration wave2`.
3. Push to `origin/main`.
4. Report the final commit hash and pushed branch.

## Step 58 Reserved Direction

Step 58 should be:

```text
Step 58 Canonical FSIDriver Implementation Migration Wave 3
```

Step 58 should migrate:

```text
src/fsi_driver.py -> src/mpm_lbm/sim/drivers/fsi_driver.py
```

Step 58 must handle driver-internal lazy imports for `boundary_motion_interface`, `geometry_motion_interface`, and `wall_velocity_application`. Step 57 must complete driver support, geometry, diagnostics, and link-area/momentum canonicalization first so that `FSIDriver3D` does not continue to depend on root legacy namespace after its own migration.
