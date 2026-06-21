# Step 56 Goal: Canonical Runtime Implementation Migration Wave 1

## Source Of Truth

This file is the detailed Step 56 goal. The short active Codex goal should reference this file instead of duplicating the full contract.

Step 56 starts from remote `origin/main` at the accepted Step 55 state:

- Repository: `lizhuoh9/MPM-LBM`
- Branch: `main`
- Accepted Step 55 commit: `b5564c56279edf8aaaf1befe5e2c49b3e42adaea`
- Step 55 meaning: package boundary and audit system are accepted, but runtime implementations are not yet migrated into canonical package files.

## Step Name

`Step 56 Canonical Runtime Implementation Migration Wave 1`

## Commit Message

`test: add step56 canonical runtime implementation migration wave1`

## Primary Objective

Move the first leaf batch of runtime implementations from legacy root modules into canonical package modules under `src/mpm_lbm/sim/...`, then turn the corresponding legacy root modules into thin compatibility shims.

After this step, the required dependency direction is:

```text
canonical package module -> real implementation
legacy root module -> compatibility shim -> canonical package module
```

The forbidden direction is:

```text
canonical package module -> lazy wrapper -> legacy root implementation
```

This step must make the migration real for the listed Wave 1 files. It must not be a source-text-only audit improvement.

## Files To Migrate

The canonical files below must contain the real implementations after Step 56:

| Canonical file | Legacy shim file |
| --- | --- |
| `src/mpm_lbm/sim/lbm/config.py` | `src/lbm_config.py` |
| `src/mpm_lbm/sim/lbm/relaxation_semantics.py` | `src/lbm_relaxation_semantics.py` |
| `src/mpm_lbm/sim/lbm/fluid.py` | `src/lbm_fluid.py` |
| `src/mpm_lbm/sim/mpm/config.py` | `src/mpm_config.py` |
| `src/mpm_lbm/sim/mpm/solid.py` | `src/mpm_solid.py` |
| `src/mpm_lbm/sim/units/mapper.py` | `src/units.py` |
| `src/mpm_lbm/sim/coupling/projection.py` | `src/projection.py` |
| `src/mpm_lbm/sim/coupling/penalty.py` | `src/coupling.py` |
| `src/mpm_lbm/sim/coupling/moving_boundary.py` | `src/moving_boundary_coupling.py` |

Each legacy shim should follow this shape:

```python
"""Compatibility shim. Canonical implementation lives in src.mpm_lbm.sim.<...>."""

from .mpm_lbm.sim.<...> import *
```

The exact canonical path in the docstring and import must match the corresponding migrated module.

## Explicit Non-Goals

Do not migrate or refactor these modules in Step 56:

- `src/fsi_config.py`
- `src/fsi_driver.py`
- `src/sim_config.py`
- `src/link_area_coupling.py`
- `src/link_area_accounting.py`
- `src/momentum_accounting.py`
- `src/geometry*.py`
- `src/squid*.py`
- `src/wall_velocity*.py`
- `src/runtime_geometry_*.py`
- `src/diagnostic_geometry_*.py`

Do not do any of the following:

- No `48^3` `link_area_experimental` run.
- No longer cycle.
- No `64^3` run.
- No LBM tau migration.
- No historical physics rerun with changed formulas.
- No default solver behavior change.
- No edits under `external/taichi_LBM3D`.
- No edits under `data/real_geometry_candidates`.

## Required New Configs

Add these policy files:

- `configs/step56_canonical_runtime_migration_policy.json`
- `configs/step56_import_execution_policy.json`
- `configs/step56_legacy_shim_policy.json`
- `configs/step56_behavior_preservation_policy.json`

The configs must be data-driven enough for tests and runners to load the contract instead of duplicating all path lists inline.

## Required Evidence Tools

Add these audit modules:

- `src/mpm_lbm/evidence/canonical_runtime_migration_audit.py`
- `src/mpm_lbm/evidence/import_execution_audit.py`
- `src/mpm_lbm/evidence/legacy_shim_audit.py`
- `src/mpm_lbm/evidence/behavior_preservation_audit.py`

The audit tools must produce deterministic JSON-compatible dictionaries and avoid running the solver.

## Required Baseline Runners

Add these runners:

- `baseline_tests/step56_common.py`
- `baseline_tests/run_step56_canonical_runtime_migration_audit.py`
- `baseline_tests/run_step56_import_execution_audit.py`
- `baseline_tests/run_step56_legacy_shim_audit.py`
- `baseline_tests/run_step56_behavior_preservation_audit.py`
- `baseline_tests/run_step56_step55_regression_guard.py`
- `baseline_tests/run_step56_artifact_manifest.py`

The runners must write JSON artifacts under `outputs/step56_*` and logs under `logs/step56_*.log`.

## Required Tests

Add these tests:

- `tests/test_step56_canonical_runtime_migration_contract.py`
- `tests/test_step56_import_execution_contract.py`
- `tests/test_step56_legacy_shim_contract.py`
- `tests/test_step56_behavior_preservation_contract.py`

The tests must verify both source structure and execution behavior. They must not rely only on file names or comments.

## Required Outputs

Generate and commit artifacts under:

- `outputs/step56_canonical_runtime_migration_audit/`
- `outputs/step56_import_execution_audit/`
- `outputs/step56_legacy_shim_audit/`
- `outputs/step56_behavior_preservation_audit/`
- `outputs/step56_step55_regression_guard/`
- `outputs/step56_artifact_manifest/`
- `logs/step56_*.log`

## Canonical Runtime Migration Audit Contract

For every migrated file pair, the audit result must include:

- `canonical_path`
- `legacy_path`
- `migration_status`
- `canonical_contains_real_implementation`
- `canonical_uses_legacy_getattr`
- `legacy_is_shim`
- `legacy_imports_canonical`
- `forbidden_reverse_dependency`
- `pass`

Acceptance criteria:

- `canonical_contains_real_implementation == true`
- `canonical_uses_legacy_getattr == false`
- `legacy_is_shim == true`
- `legacy_imports_canonical == true`
- `forbidden_reverse_dependency == false`
- `pass == true`

Specific examples:

- `src/mpm_lbm/sim/lbm/fluid.py` must not contain `_LEGACY_MODULE` or `legacy_getattr`.
- `src/lbm_fluid.py` must contain the compatibility shim docstring and import from `src.mpm_lbm.sim.lbm.fluid`.

## Import Execution Audit Contract

The audit must actually import all migrated canonical symbols:

```python
from src.mpm_lbm.sim.lbm.config import LBMConfig
from src.mpm_lbm.sim.lbm.relaxation_semantics import tau_from_legacy_external_solver_parameter
from src.mpm_lbm.sim.lbm.fluid import LBMFluid3D
from src.mpm_lbm.sim.mpm.config import MPMConfig
from src.mpm_lbm.sim.mpm.solid import MPMSolid3D
from src.mpm_lbm.sim.units.mapper import GridUnitMapper
from src.mpm_lbm.sim.coupling.projection import MPMToLBMProjector3D
from src.mpm_lbm.sim.coupling.penalty import PenaltyFSICoupler3D
from src.mpm_lbm.sim.coupling.moving_boundary import MovingBoundaryFSICoupler3D
```

The audit must also actually import the compatibility legacy symbols:

```python
from src.lbm_config import LBMConfig
from src.lbm_fluid import LBMFluid3D
from src.mpm_config import MPMConfig
from src.mpm_solid import MPMSolid3D
from src.units import GridUnitMapper
from src.projection import MPMToLBMProjector3D
from src.coupling import PenaltyFSICoupler3D
from src.moving_boundary_coupling import MovingBoundaryFSICoupler3D
```

Acceptance criteria:

- Every canonical import succeeds.
- Every legacy import succeeds.
- Canonical and legacy exported symbols are the same object where applicable.
- Imports do not write output artifacts.
- Imports do not run the solver.

## Legacy Shim Audit Contract

For all nine legacy files, verify:

- The file is a thin compatibility shim.
- It imports from the matching canonical package path.
- It no longer contains the migrated implementation body.
- It does not import from another legacy migrated root module.

## Behavior Preservation Audit Contract

This audit is lightweight and semantic. It must not run heavy physics.

Required checks:

- `LBMConfig` default fields remain unchanged.
- `MPMConfig` default fields remain unchanged.
- `GridUnitMapper` conversions remain unchanged.
- `tau_from_legacy_external_solver_parameter(0.1) == 0.5333333333333333`
- `tau_from_lattice_kinematic_viscosity(0.1) == 0.8`
- `UnifiedSimConfig` and unmigrated drivers are not changed by this step.
- `solver_behavior_changed == false`
- `physics_feature_expansion == false`
- Constructing `LBMFluid3D` and `MPMSolid3D` is not required.

## Step 55 Regression Guard

Step 56 must keep the accepted Step 55 layout/boundary evidence green or explicitly superseded by Step 56's stronger execution audit.

The Step 56 regression guard must check:

- Step 55 code layout audit is green.
- Step 55 import boundary audit is green.
- Step 55 compatibility shim audit is green or superseded by Step 56 execution audit.
- Step 55 test strength enum audit is green.
- Step 55 artifact manifest is green.
- README/docs still contain the Step 55 layout boundary.

## Documentation Requirements

Add:

- `STEP56_CANONICAL_RUNTIME_IMPLEMENTATION_MIGRATION_WAVE1_REPORT.md`
- `docs/56_canonical_runtime_implementation_migration_wave1.md`

Update README/progress documentation so Step 56 is discoverable and its scope is not confused with a physics validation step.

The report must include:

- What was migrated.
- What remained intentionally unmigrated.
- Evidence artifact paths.
- Commands used for validation.
- Confirmation that the step did not run large physics cases.
- Confirmation that canonical files are no longer lazy wrappers for the migrated batch.

## Validation Commands

Use `D:\working\taichi\env\python.exe` as the primary validation interpreter.

Required focused validation:

```powershell
D:\working\taichi\env\python.exe -m pytest -q tests/test_step56_canonical_runtime_migration_contract.py tests/test_step56_import_execution_contract.py tests/test_step56_legacy_shim_contract.py tests/test_step56_behavior_preservation_contract.py
D:\working\taichi\env\python.exe -m pytest -q tests/test_step55_code_layout_contract.py tests/test_step55_import_boundary_contract.py tests/test_step55_compatibility_shim_contract.py tests/test_step55_test_strength_contract.py tests/test_step55_artifact_manifest_contract.py
```

Required artifact generation:

```powershell
D:\working\taichi\env\python.exe baseline_tests/run_step56_canonical_runtime_migration_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step56_import_execution_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step56_legacy_shim_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step56_behavior_preservation_audit.py
D:\working\taichi\env\python.exe baseline_tests/run_step56_step55_regression_guard.py
D:\working\taichi\env\python.exe baseline_tests/run_step56_artifact_manifest.py
```

Required broad validation:

```powershell
D:\working\taichi\env\python.exe -m pytest -q
D:\TOOL\Anaconda\python.exe -m pytest -q
```

If the Anaconda run exposes an optional dependency import-time failure, fix the import boundary so imports are lightweight and optional functionality fails only when the optional feature is invoked.

## Push Requirement

After implementation, tests, artifacts, and documentation are complete:

1. Review `git diff`.
2. Commit all relevant changes with `test: add step56 canonical runtime implementation migration wave1`.
3. Push to `origin/main`.
4. Report the final commit hash and pushed branch.

