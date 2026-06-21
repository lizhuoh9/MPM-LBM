# Step 58 Canonical FSIDriver Implementation Migration Wave 3 Goal

## Source State

`origin/main` is accepted at Step 57 commit:

```text
973ef25295b75692ef794a7aed5b9bcf736adbb6
test: add step57 canonical driver support migration wave2
```

Step 57 migrated driver support, diagnostics, run utilities, link-area support, momentum accounting, and geometry support modules into canonical `src.mpm_lbm` package paths. It left `src/fsi_driver.py` intentionally unmigrated.

The current structural risk is that `src/mpm_lbm/sim/drivers/fsi_driver.py` is still a lazy canonical surface pointing at legacy `src.fsi_driver`, while `src/fsi_driver.py` still contains the real `FSIDriver3D` implementation and imports root-level legacy modules.

## Objective

Implement:

```text
Step 58 Canonical FSIDriver Implementation Migration Wave 3
```

Move the real `FSIDriver3D` implementation from:

```text
src/fsi_driver.py
```

to:

```text
src/mpm_lbm/sim/drivers/fsi_driver.py
```

Then turn:

```text
src/fsi_driver.py
```

into a thin compatibility shim that imports from the canonical driver path.

## Required Dependency Direction

After Step 58, the allowed direction is:

```text
src/fsi_driver.py
    -> compatibility shim
    -> src.mpm_lbm.sim.drivers.fsi_driver

src.mpm_lbm.sim.drivers.fsi_driver
    -> canonical runtime, driver support, geometry, diagnostics, coupling, IO modules
```

The forbidden direction is:

```text
src.mpm_lbm.sim.drivers.fsi_driver
    -> legacy src.fsi_driver
```

The canonical driver must not use:

```text
_LEGACY_MODULE
legacy_getattr
from ..._legacy import legacy_getattr
```

## Canonical Driver Imports

`src/mpm_lbm/sim/drivers/fsi_driver.py` must import through canonical package paths:

```python
from .fsi_config import FSIDriverConfig
from ..lbm.fluid import LBMFluid3D
from ..mpm.solid import MPMSolid3D
from ..coupling.projection import MPMToLBMProjector3D
from ..coupling.penalty import PenaltyFSICoupler3D
from ..coupling.moving_boundary import MovingBoundaryFSICoupler3D
from ..coupling.link_area import LinkAreaMovingBoundaryCoupler3D
from ..units.mapper import GridUnitMapper
from ..io.run_utils import (
    assert_no_nan_inf_array,
    ensure_output_dir,
    make_all_fluid_geo,
    save_csv_rows,
    save_json_config,
)
from ..geometry.config import GeometryConfig
from ..geometry.sampler import GeometrySampler3D
from ..geometry.quality import GeometryQualityGate, analyze_geometry_config
from ...diagnostics.fsi_diagnostics import FSIDiagnostics3D
```

It must not import root legacy driver dependencies such as:

```text
from .coupling
from .diagnostics
from .fsi_config
from .geometry_config
from .geometry
from .geometry_quality
from .lbm_fluid
from .link_area_coupling
from .moving_boundary_coupling
from .mpm_solid
from .projection
from .run_utils
from .units
from .boundary_motion_interface
from .geometry_motion_interface
from .wall_velocity_application
```

## Optional Hook Bridge Surfaces

Step 58 must not migrate the real wall-velocity or motion implementation chain. Instead, create temporary canonical bridge surfaces so the canonical driver does not directly import root legacy optional hook modules:

```text
src/mpm_lbm/sim/motion/__init__.py
src/mpm_lbm/sim/motion/boundary_motion_interface.py
src/mpm_lbm/sim/motion/geometry_motion_interface.py
src/mpm_lbm/sim/wall_velocity/__init__.py
src/mpm_lbm/sim/wall_velocity/application.py
```

These bridge files are explicitly temporary until Step 59. They may use `legacy_getattr` and must point at:

```text
src.boundary_motion_interface
src.geometry_motion_interface
src.wall_velocity_application
```

The canonical driver must import optional hook symbols from those bridge surfaces:

```python
from ..motion.boundary_motion_interface import write_static_boundary_motion_interface_report
from ..motion.boundary_motion_interface import write_boundary_motion_interface_report
from ..motion.geometry_motion_interface import write_geometry_motion_interface_report
from ..wall_velocity.application import apply_wall_velocity_application_to_lbm
```

## Legacy Driver Shim

`src/fsi_driver.py` must become:

```python
"""Compatibility shim. Canonical implementation lives in src.mpm_lbm.sim.drivers.fsi_driver."""

from src.mpm_lbm.sim.drivers.fsi_driver import *
```

The shim must contain no `class FSIDriver3D`, no `DIAGNOSTIC_FIELDS` implementation body, no `legacy_getattr`, and no Taichi/data-oriented implementation.

## Explicit Non-Goals

Step 58 must not do any of the following:

```text
48^3 link_area_experimental run
longer cycle run
64^3 run
LBM tau formula migration
standard viscosity migration
historical physics rerun
default solver behavior change
wall_velocity implementation migration
geometry_motion implementation migration
boundary_motion implementation migration
runtime_geometry proxy implementation migration
diagnostic_geometry implementation migration
squid kinematics or squid proxy implementation migration
real jet validation
jet propulsion validation
squid swimming
grid convergence claim
production readiness claim
external/taichi_LBM3D edit
data/real_geometry_candidates edit
```

## Required Config Files

Create:

```text
configs/step58_fsidriver_migration_policy.json
configs/step58_driver_import_execution_policy.json
configs/step58_legacy_shim_policy.json
configs/step58_optional_bridge_policy.json
configs/step58_behavior_preservation_policy.json
```

The migration policy must define the canonical and legacy driver paths, required symbols (`FSIDriver3D`, `DIAGNOSTIC_FIELDS`), forbidden root import tokens, and explicit `solver_behavior_changed=false`, `physics_feature_expansion=false`.

The optional bridge policy must define the three canonical bridge files, their legacy modules, exported symbols, and `bridge_is_temporary_until_step59=true`.

## Required Evidence Tools

Create:

```text
src/mpm_lbm/evidence/fsidriver_migration_audit.py
src/mpm_lbm/evidence/fsidriver_import_execution_audit.py
src/mpm_lbm/evidence/fsidriver_legacy_shim_audit.py
src/mpm_lbm/evidence/optional_bridge_audit.py
src/mpm_lbm/evidence/fsidriver_behavior_preservation_audit.py
```

## Required Baseline Runners

Create:

```text
baseline_tests/step58_common.py
baseline_tests/run_step58_fsidriver_migration_audit.py
baseline_tests/run_step58_import_execution_audit.py
baseline_tests/run_step58_legacy_shim_audit.py
baseline_tests/run_step58_optional_bridge_audit.py
baseline_tests/run_step58_behavior_preservation_audit.py
baseline_tests/run_step58_step57_regression_guard.py
baseline_tests/run_step58_artifact_manifest.py
```

## Required Tests

Create:

```text
tests/test_step58_fsidriver_migration_contract.py
tests/test_step58_import_execution_contract.py
tests/test_step58_legacy_shim_contract.py
tests/test_step58_optional_bridge_contract.py
tests/test_step58_behavior_preservation_contract.py
tests/test_step58_step57_regression_contract.py
```

## Required Documentation

Create:

```text
STEP58_CANONICAL_FSIDRIVER_IMPLEMENTATION_MIGRATION_WAVE3_REPORT.md
docs/58_canonical_fsidriver_implementation_migration_wave3.md
```

Update:

```text
README.md
docs/00_project_status.md
```

The documentation must explicitly say that Step 58 migrates `FSIDriver3D` ownership only. It must also say that optional motion and wall-velocity bridge files remain temporary wrappers until Step 59 and that no new physics validation or production-readiness claim is established.

## Audit Requirements

### FSIDriver Migration Audit

Must verify:

```text
canonical_path_exists == true
legacy_path_exists == true
canonical_contains_real_implementation == true
canonical_contains_class_FSIDriver3D == true
canonical_contains_DIAGNOSTIC_FIELDS == true
canonical_uses_legacy_getattr == false
canonical_imports_legacy_root == false
legacy_is_shim == true
legacy_imports_canonical == true
forbidden_reverse_dependency == false
solver_behavior_changed == false
physics_feature_expansion == false
```

### Import Execution Audit

Must import:

```python
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D, DIAGNOSTIC_FIELDS
from src.fsi_driver import FSIDriver3D as LegacyFSIDriver3D
```

Must verify:

```text
canonical import passes
legacy import passes
canonical FSIDriver3D is legacy FSIDriver3D
canonical DIAGNOSTIC_FIELDS equals legacy DIAGNOSTIC_FIELDS
import does not write outputs
import does not run solver
```

Also import the bridge symbols:

```python
from src.mpm_lbm.sim.motion.boundary_motion_interface import write_static_boundary_motion_interface_report
from src.mpm_lbm.sim.motion.geometry_motion_interface import write_geometry_motion_interface_report
from src.mpm_lbm.sim.wall_velocity.application import apply_wall_velocity_application_to_lbm
```

### Legacy Shim Audit

Must verify:

```text
src/fsi_driver.py is a shim
src/fsi_driver.py imports src.mpm_lbm.sim.drivers.fsi_driver
src/fsi_driver.py contains no class FSIDriver3D implementation
src/fsi_driver.py contains no DIAGNOSTIC_FIELDS implementation body
nonblank_line_count <= 4
```

### Optional Bridge Audit

Must verify:

```text
canonical bridge files exist
bridge files are explicitly temporary until Step 59
bridge files use legacy_getattr
bridge files point to the intended legacy modules
bridge imports pass
bridge files do not write outputs on import
bridge files do not run solver on import
```

### Behavior Preservation Audit

Must verify without calling `initialize()`, `run()`, or `step_once()`:

```text
FSIDriverConfig selected defaults unchanged
DIAGNOSTIC_FIELDS unchanged
FSIDriver3D constructor smoke passes
constructor does not write outputs
constructor leaves initialized == false
constructor leaves current_lbm_step == 0
constructor leaves total_mpm_substeps == 0
constructor preserves expected timing keys
solver_behavior_changed == false
physics_feature_expansion == false
```

The constructor smoke may use:

```python
config = FSIDriverConfig(n_lbm_steps=1, write_vtk=False, write_particles=False)
driver = FSIDriver3D(config, out_dir="outputs/step58_constructor_no_run_probe")
```

The audit must confirm that `outputs/step58_constructor_no_run_probe` does not exist after construction.

### Step 57 Regression Guard

Must verify:

```text
Step57 driver support migration audit green
Step57 import execution audit green
Step57 legacy shim audit green
Step57 src init export audit green
Step57 behavior preservation audit green
Step57 artifact manifest green
Step57 Step56 regression guard green
```

## Required Artifacts

Generate:

```text
outputs/step58_fsidriver_migration_audit/
outputs/step58_import_execution_audit/
outputs/step58_legacy_shim_audit/
outputs/step58_optional_bridge_audit/
outputs/step58_behavior_preservation_audit/
outputs/step58_step57_regression_guard/
outputs/step58_artifact_manifest/
logs/step58_*.log
```

The artifact manifest must verify:

```text
step58_total_size_mb < 5
large_file_count == 0
step58_vtr_count == 0
step58_particle_npy_count == 0
protected_external_taichi_lbm3d_step58_file_count == 0
protected_real_geometry_candidates_step58_file_count == 0
```

## Validation Commands

Use the trusted interpreter first:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step58_fsidriver_migration_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step58_import_execution_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step58_legacy_shim_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step58_optional_bridge_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step58_behavior_preservation_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step58_step57_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step58_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q tests\test_step58_fsidriver_migration_contract.py tests\test_step58_import_execution_contract.py tests\test_step58_legacy_shim_contract.py tests\test_step58_optional_bridge_contract.py tests\test_step58_behavior_preservation_contract.py tests\test_step58_step57_regression_contract.py
```

Full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Git checks:

```powershell
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## Commit And Push

Commit message must be:

```text
test: add step58 canonical fsidriver implementation migration wave3
```

Push to:

```text
origin/main
```

Final response must include:

```text
final commit hash
remote branch
key validation pass counts
artifact manifest summary
whether ECC pre-push passed
```

## Done Criteria

Step 58 is complete only when:

```text
the detailed Step58 goal exists and active goal references it
FSIDriver3D real implementation lives in canonical driver path
legacy src/fsi_driver.py is a thin shim
canonical driver has no direct root legacy imports
temporary optional bridge surfaces exist and are audited as temporary
canonical and legacy driver imports resolve to the same objects
constructor no-run behavior preservation audit passes
Step57 regression guard passes
artifact budget passes
external/taichi_LBM3D and data/real_geometry_candidates remain unchanged
Taichi full pytest passes
Anaconda full pytest passes
ECC pre-push hook passes
commit is pushed to origin/main
```
