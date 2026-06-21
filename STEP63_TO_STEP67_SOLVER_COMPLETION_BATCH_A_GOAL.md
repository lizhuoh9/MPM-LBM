# Step 63-67 Solver Completion Batch A Goal

## 1. Batch Name

Step 63-67 Solver Completion Batch A.

## 2. Starting Point

The repository starts from Step 62:

```text
61b3e25cc2dcbb34060f5bdebacfb029ac2ee002
test: add step62 canonical 32 moving boundary 3step duration
```

Step 62 proved that the canonical `FSIDriver3D.run()` path can execute:

```text
32^3 / 1024 particles / moving_boundary / engineering / 3 LBM steps
```

The accepted Step 62 result was finite and bounded, with no NaN/Inf, no legacy driver owner, no runtime code change, and no activation of runtime geometry, wall velocity, link-area comparison, real geometry, or squid behavior.

Batch A must pause new simulation rows and complete solver-package ownership work.

## 3. Batch A Core Objective

Batch A must:

```text
1. Freeze new simulation rows for Steps 63-67.
2. Produce the remaining root implementation inventory and Step68+ roadmap.
3. Migrate motion, wall velocity, runtime geometry, diagnostic geometry, geometry displacement, squid proxy, and real geometry support to canonical packages.
4. Convert the migrated root src/*.py files into thin compatibility shims.
5. Retire Step58 temporary bridges for the migrated surfaces.
6. Add batch-wide audits, runners, tests, docs, report, logs, and artifact manifest.
7. Prove there are no new driver.run simulations, no VTR, no particle NPY, no external solver edits, and no real geometry candidate edits.
```

Batch A is implementation ownership and audit work. It is not a solver validation campaign and must not add new runtime behavior.

## 4. Global Hard Boundaries

Batch A executable source, runners, and tests must not add or execute:

```text
FSIDriver3D(...).run()
driver.run()
driver.step_once()
driver.initialize()
outputs/step63_driver_runs
outputs/step64_driver_runs
outputs/step65_driver_runs
outputs/step66_driver_runs
outputs/step67_driver_runs
write_vtk = true
write_particles = true
```

Allowed Batch A activity:

```text
import checks
constructor-free import checks
AST/source audits
symbol-resolution audits
unit-level pure function tests
legacy shim tests
config validation
existing Step59-62 artifact regression checks
```

Simulation freeze audits must scan executable files only. Markdown/docs may contain explanatory forbidden tokens and must not be counted as executable violations.

## 5. Directory Placement Rules

Canonical placement:

```text
runtime solver code: src/mpm_lbm/sim/
diagnostics: src/mpm_lbm/diagnostics/
evidence / audit: src/mpm_lbm/evidence/
step-specific experiment / proxy: experiments/steps/
runners: baseline_tests/
pytest contracts: tests/
outputs: outputs/stepXX_*/
logs: logs/stepXX_*.log
```

Forbidden placement:

```text
new real implementation in root src/*.py
evidence/audit code in src/mpm_lbm/sim/
solver runtime code in src/mpm_lbm/evidence/
step-specific proxy code in src/mpm_lbm/sim/
reusable solver module in baseline_tests/
runner implementation in tests/
```

## 6. Step 63 Scope

Step 63 is the freeze, inventory, roadmap, and policy layer. It must not migrate concrete solver modules.

Step 63 must:

```text
1. Formally freeze new Step63-67 simulations.
2. Inventory remaining root src/*.py real implementations.
3. Inventory Step58 temporary bridge surfaces.
4. Inventory step-specific proxy code.
5. Generate the Step68+ solver completion roadmap.
6. Check UTF-8 encoding and remove any UTF-8 BOM from Python source.
7. Check regression snapshot consistency.
8. Confirm Step62 regression remains green.
```

Step 63 must not:

```text
run driver.run()
create driver output dirs
change runtime solver behavior
activate physics features
```

Step 63 configs:

```text
configs/step63_simulation_freeze_policy.json
configs/step63_remaining_solver_inventory_policy.json
configs/step63_solver_completion_roadmap_policy.json
configs/step63_code_placement_policy.json
configs/step63_encoding_policy.json
configs/step63_regression_snapshot_policy.json
```

Step 63 evidence source:

```text
src/mpm_lbm/evidence/simulation_freeze_audit.py
src/mpm_lbm/evidence/remaining_solver_inventory_audit.py
src/mpm_lbm/evidence/solver_completion_roadmap_audit.py
src/mpm_lbm/evidence/code_placement_freeze_audit.py
src/mpm_lbm/evidence/encoding_policy_audit.py
src/mpm_lbm/evidence/regression_snapshot_consistency_audit.py
```

Step 63 runners:

```text
baseline_tests/run_step63_simulation_freeze_audit.py
baseline_tests/run_step63_remaining_solver_inventory_audit.py
baseline_tests/run_step63_solver_completion_roadmap_audit.py
baseline_tests/run_step63_code_placement_freeze_audit.py
baseline_tests/run_step63_encoding_policy_audit.py
baseline_tests/run_step63_regression_snapshot_consistency_audit.py
```

Step 63 tests:

```text
tests/test_step63_simulation_freeze_contract.py
tests/test_step63_remaining_solver_inventory_contract.py
tests/test_step63_solver_completion_roadmap_contract.py
tests/test_step63_code_placement_freeze_contract.py
tests/test_step63_encoding_policy_contract.py
tests/test_step63_regression_snapshot_consistency_contract.py
```

Step 63 outputs:

```text
outputs/step63_simulation_freeze_audit/
outputs/step63_remaining_solver_inventory_audit/
outputs/step63_solver_completion_roadmap_audit/
outputs/step63_code_placement_freeze_audit/
outputs/step63_encoding_policy_audit/
outputs/step63_regression_snapshot_consistency_audit/
logs/step63_*.log
```

Step 63 acceptance:

```text
simulation_freeze_audit_pass == true
new_simulation_run_count == 0
new_driver_run_output_dir_count == 0
runtime_code_changed == false
solver_behavior_changed == false
physics_feature_expansion == false
remaining_solver_inventory_pass == true
unknown_requires_review_count == 0
temporary_bridge_count is reported
migration_required_count is reported
solver_completion_roadmap_pass == true
Step68-Step76 roadmap exists
code_placement_freeze_pass == true
encoding_policy_audit_pass == true
utf8_bom_count == 0
regression_snapshot_consistency_pass == true
```

## 7. Step 64 Scope

Step 64 migrates motion and wall velocity implementation from temporary bridge or root ownership into canonical packages.

Step 64 migrations:

```text
src/boundary_motion_interface.py -> src/mpm_lbm/sim/motion/boundary_motion_interface.py
src/geometry_motion_interface.py -> src/mpm_lbm/sim/motion/geometry_motion_interface.py
src/wall_velocity_application.py -> src/mpm_lbm/sim/wall_velocity/application.py
src/wall_velocity_application_config.py -> src/mpm_lbm/sim/wall_velocity/application_config.py
src/wall_velocity_config.py -> src/mpm_lbm/sim/wall_velocity/config.py
src/wall_velocity_field.py -> src/mpm_lbm/sim/wall_velocity/field.py
```

Root files must become thin shims:

```text
src/boundary_motion_interface.py
src/geometry_motion_interface.py
src/wall_velocity_application.py
src/wall_velocity_application_config.py
src/wall_velocity_config.py
src/wall_velocity_field.py
```

Shim format:

```python
"""Compatibility shim. Canonical implementation lives in src.mpm_lbm.sim.wall_velocity.application."""

from src.mpm_lbm.sim.wall_velocity.application import *
```

Canonical Step 64 files must not import root legacy modules:

```text
src.boundary_motion_interface
src.geometry_motion_interface
src.wall_velocity_application
src.wall_velocity_application_config
src.wall_velocity_config
src.wall_velocity_field
```

Step 64 must retire temporary bridge tokens from canonical files:

```text
legacy_getattr
_LEGACY_MODULE
BRIDGE_IS_TEMPORARY_UNTIL_STEP59
Implementation remains legacy
```

Step 64 config:

```text
configs/step64_motion_wall_velocity_migration_policy.json
```

Step 64 outputs:

```text
outputs/step64_motion_wall_velocity_migration_audit/
outputs/step64_import_execution_audit/
outputs/step64_legacy_shim_audit/
outputs/step64_bridge_retirement_audit/
outputs/step64_behavior_preservation_audit/
```

Step 64 tests:

```text
tests/test_step64_motion_wall_velocity_migration_contract.py
tests/test_step64_import_execution_contract.py
tests/test_step64_legacy_shim_contract.py
tests/test_step64_bridge_retirement_contract.py
tests/test_step64_behavior_preservation_contract.py
```

Step 64 acceptance:

```text
step64_motion_wall_velocity_migration_pass == true
canonical_path_exists == true for all Step64 files
canonical_contains_real_implementation == true
canonical_uses_legacy_getattr == false
canonical_imports_legacy_root == false
temporary_bridge_count_for_step64_files == 0
legacy_root_files_are_shims == true
legacy_implementation_body_count == 0
canonical_import_pass_count == expected_count
legacy_import_pass_count == expected_count
same_object_count == expected_count
no driver.run()
no output files created by imports
no runtime solver behavior change
```

## 8. Step 65 Scope

Step 65 migrates runtime geometry core implementation into canonical runtime geometry package.

Step 65 migrations:

```text
src/runtime_geometry_projection.py -> src/mpm_lbm/sim/runtime_geometry/projection.py
src/runtime_geometry_projection_config.py -> src/mpm_lbm/sim/runtime_geometry/projection_config.py
src/runtime_geometry_projection_quality.py -> src/mpm_lbm/sim/runtime_geometry/projection_quality.py
src/runtime_geometry_projection_consistency.py -> src/mpm_lbm/sim/runtime_geometry/projection_consistency.py
src/runtime_geometry_projection_state_guard.py -> src/mpm_lbm/sim/runtime_geometry/state_guard.py
```

Add:

```text
src/mpm_lbm/sim/runtime_geometry/__init__.py
```

Root files must become thin shims:

```text
src/runtime_geometry_projection.py
src/runtime_geometry_projection_config.py
src/runtime_geometry_projection_quality.py
src/runtime_geometry_projection_consistency.py
src/runtime_geometry_projection_state_guard.py
```

Step 65 must not migrate these step-specific proxy files into `src/mpm_lbm/sim/runtime_geometry/`:

```text
src/runtime_geometry_wall_velocity_one_cycle_*.py
src/runtime_geometry_wall_velocity_transfer_*.py
src/runtime_geometry_wall_velocity_48_feasibility_*.py
src/runtime_geometry_wall_velocity_support_scaling_*.py
```

Those remain Step68 candidates for `experiments/steps/`.

Step 65 config:

```text
configs/step65_runtime_geometry_migration_policy.json
```

Step 65 outputs:

```text
outputs/step65_runtime_geometry_migration_audit/
outputs/step65_import_execution_audit/
outputs/step65_legacy_shim_audit/
outputs/step65_behavior_preservation_audit/
```

Step 65 tests:

```text
tests/test_step65_runtime_geometry_migration_contract.py
tests/test_step65_import_execution_contract.py
tests/test_step65_legacy_shim_contract.py
tests/test_step65_behavior_preservation_contract.py
```

Step 65 acceptance:

```text
step65_runtime_geometry_migration_pass == true
canonical runtime_geometry package exists
all Step65 canonical files contain real implementation
all Step65 root files are thin shims
canonical imports no legacy root modules
runtime_geometry_wall_velocity_* files are not placed in sim/runtime_geometry
step-specific proxy remaining count is reported
import execution passes
behavior preservation passes
no driver.run()
no output driver runs
```

## 9. Step 66 Scope

Step 66 separates diagnostic geometry and geometry displacement ownership.

Step 66 diagnostic geometry migrations:

```text
src/diagnostic_geometry_update.py -> src/mpm_lbm/diagnostics/geometry_update.py
src/diagnostic_geometry_projection.py -> src/mpm_lbm/diagnostics/geometry_projection.py
src/diagnostic_geometry_state_guard.py -> src/mpm_lbm/diagnostics/geometry_state_guard.py
```

Step 66 geometry displacement runtime support migrations:

```text
src/geometry_displacement_config.py -> src/mpm_lbm/sim/geometry_displacement/config.py
src/geometry_displacement_field.py -> src/mpm_lbm/sim/geometry_displacement/field.py
src/geometry_displacement_quality.py -> src/mpm_lbm/sim/geometry_displacement/quality.py
src/geometry_displacement_consistency.py -> src/mpm_lbm/sim/geometry_displacement/consistency.py
```

Step 66 geometry displacement diagnostics migration:

```text
src/geometry_displacement_grid_diagnostics.py -> src/mpm_lbm/diagnostics/geometry_displacement_grid.py
```

Add:

```text
src/mpm_lbm/sim/geometry_displacement/__init__.py
```

Root files must become thin shims:

```text
src/diagnostic_geometry_update.py
src/diagnostic_geometry_projection.py
src/diagnostic_geometry_state_guard.py
src/geometry_displacement_config.py
src/geometry_displacement_field.py
src/geometry_displacement_quality.py
src/geometry_displacement_consistency.py
src/geometry_displacement_grid_diagnostics.py
```

Step 66 config:

```text
configs/step66_diagnostic_geometry_displacement_migration_policy.json
```

Step 66 outputs:

```text
outputs/step66_diagnostic_geometry_displacement_migration_audit/
outputs/step66_import_execution_audit/
outputs/step66_legacy_shim_audit/
outputs/step66_behavior_preservation_audit/
```

Step 66 tests:

```text
tests/test_step66_diagnostic_geometry_displacement_migration_contract.py
tests/test_step66_import_execution_contract.py
tests/test_step66_legacy_shim_contract.py
tests/test_step66_behavior_preservation_contract.py
```

Step 66 acceptance:

```text
step66_diagnostic_geometry_displacement_migration_pass == true
diagnostic files are under src/mpm_lbm/diagnostics
runtime displacement files are under src/mpm_lbm/sim/geometry_displacement
root legacy files are shims
canonical files do not import root legacy modules
import execution passes
small-array behavior preservation passes
no driver.run()
no VTR
no particle NPY
```

## 10. Step 67 Scope

Step 67 migrates squid proxy and pure real geometry support. It must not run squid, run real geometry, or add real data.

Step 67 squid proxy migrations:

```text
src/squid_region_config.py -> src/mpm_lbm/sim/squid_proxy/region_config.py
src/squid_proxy_regions.py -> src/mpm_lbm/sim/squid_proxy/regions.py
src/squid_kinematics_config.py -> src/mpm_lbm/sim/squid_proxy/kinematics_config.py
src/squid_kinematics_schedule.py -> src/mpm_lbm/sim/squid_proxy/kinematics_schedule.py
src/squid_kinematics_quality.py -> src/mpm_lbm/sim/squid_proxy/kinematics_quality.py
src/squid_kinematics_region_mapping.py -> src/mpm_lbm/sim/squid_proxy/region_mapping.py
src/squid_motion_mapping.py -> src/mpm_lbm/sim/squid_proxy/motion_mapping.py
src/squid_motion_mapping_config.py -> src/mpm_lbm/sim/squid_proxy/motion_mapping_config.py
src/squid_motion_quality.py -> src/mpm_lbm/sim/squid_proxy/motion_quality.py
```

Step 67 squid diagnostics migration:

```text
src/squid_motion_projection_diagnostics.py -> src/mpm_lbm/diagnostics/squid_motion_projection.py
```

Add:

```text
src/mpm_lbm/sim/squid_proxy/__init__.py
```

Step 67 real geometry support migrations:

```text
src/geometry_intake.py -> src/mpm_lbm/sim/geometry/intake.py
src/geometry_candidate_manifest.py -> src/mpm_lbm/sim/geometry/candidate_manifest.py
src/geometry_fingerprint.py -> src/mpm_lbm/sim/geometry/fingerprint.py
src/geometry_normalization.py -> src/mpm_lbm/sim/geometry/normalization.py
```

Step 67 must classify `src/real_geometry_feasibility.py` before moving:

```text
If it contains FSIDriver3D, driver.run, write_vtk, write_particles, or outputs/step:
  classify as step_specific_or_experiment_runner
  target = experiments/steps/real_geometry_feasibility/
  do not place under src/mpm_lbm/sim/

If it is pure diagnostic helper:
  target = src/mpm_lbm/diagnostics/real_geometry_feasibility.py
```

Batch A must not execute `real_geometry_feasibility.py`.

Step 67 config:

```text
configs/step67_squid_proxy_real_geometry_migration_policy.json
```

Step 67 outputs:

```text
outputs/step67_squid_proxy_real_geometry_migration_audit/
outputs/step67_import_execution_audit/
outputs/step67_legacy_shim_audit/
outputs/step67_behavior_preservation_audit/
```

Step 67 tests:

```text
tests/test_step67_squid_proxy_real_geometry_migration_contract.py
tests/test_step67_import_execution_contract.py
tests/test_step67_legacy_shim_contract.py
tests/test_step67_behavior_preservation_contract.py
```

Step 67 acceptance:

```text
step67_squid_proxy_real_geometry_migration_pass == true
squid proxy canonical package exists
real geometry support canonical paths exist
root legacy files are shims
canonical files do not import root legacy modules
real_geometry_feasibility is correctly classified
no real geometry data added
data/real_geometry_candidates unchanged
no driver.run()
no real squid validation claim
no squid swimming claim
import execution passes
behavior preservation passes
```

## 11. Batch-Wide Generic Evidence Tools

Add reusable audit helpers:

```text
src/mpm_lbm/evidence/batch_migration_audit.py
src/mpm_lbm/evidence/batch_import_execution_audit.py
src/mpm_lbm/evidence/batch_legacy_shim_audit.py
src/mpm_lbm/evidence/batch_behavior_preservation_audit.py
```

`batch_migration_audit.py` checks:

```text
legacy_path
canonical_path
classification
canonical_path_exists
legacy_path_exists
canonical_contains_real_implementation
canonical_imports_legacy_root
canonical_uses_legacy_getattr
legacy_is_shim
legacy_imports_canonical
pass
```

`batch_import_execution_audit.py` checks:

```text
symbol
canonical_module
legacy_module
canonical_import_pass
legacy_import_pass
same_object
pass
```

`batch_legacy_shim_audit.py` checks:

```text
legacy_path
canonical_path
nonblank_line_count
legacy_contains_implementation_body
legacy_imports_canonical
legacy_is_shim
pass
```

`batch_behavior_preservation_audit.py` must run only pure function, config, and small-array checks. It must not call `driver.run()`.

## 12. Batch-Wide Configs

Add:

```text
configs/step64_motion_wall_velocity_migration_policy.json
configs/step65_runtime_geometry_migration_policy.json
configs/step66_diagnostic_geometry_displacement_migration_policy.json
configs/step67_squid_proxy_real_geometry_migration_policy.json
```

Each migration policy should follow this shape:

```json
{
  "policy_id": "step64_motion_wall_velocity_migration_policy",
  "step": 64,
  "runtime_code_changed": false,
  "solver_behavior_changed": false,
  "physics_feature_expansion": false,
  "migrations": [
    {
      "legacy_path": "src/wall_velocity_application.py",
      "canonical_path": "src/mpm_lbm/sim/wall_velocity/application.py",
      "legacy_module": "src.wall_velocity_application",
      "canonical_module": "src.mpm_lbm.sim.wall_velocity.application",
      "classification": "wall_velocity_runtime",
      "symbols": ["apply_wall_velocity_application_to_lbm"],
      "required_tokens": ["def apply_wall_velocity_application_to_lbm"]
    }
  ]
}
```

## 13. Batch-Wide Runners

Add:

```text
baseline_tests/step63_67_common.py

baseline_tests/run_step63_simulation_freeze_audit.py
baseline_tests/run_step63_remaining_solver_inventory_audit.py
baseline_tests/run_step63_solver_completion_roadmap_audit.py
baseline_tests/run_step63_code_placement_freeze_audit.py
baseline_tests/run_step63_encoding_policy_audit.py
baseline_tests/run_step63_regression_snapshot_consistency_audit.py

baseline_tests/run_step64_motion_wall_velocity_migration_audit.py
baseline_tests/run_step64_import_execution_audit.py
baseline_tests/run_step64_legacy_shim_audit.py
baseline_tests/run_step64_bridge_retirement_audit.py
baseline_tests/run_step64_behavior_preservation_audit.py

baseline_tests/run_step65_runtime_geometry_migration_audit.py
baseline_tests/run_step65_import_execution_audit.py
baseline_tests/run_step65_legacy_shim_audit.py
baseline_tests/run_step65_behavior_preservation_audit.py

baseline_tests/run_step66_diagnostic_geometry_displacement_migration_audit.py
baseline_tests/run_step66_import_execution_audit.py
baseline_tests/run_step66_legacy_shim_audit.py
baseline_tests/run_step66_behavior_preservation_audit.py

baseline_tests/run_step67_squid_proxy_real_geometry_migration_audit.py
baseline_tests/run_step67_import_execution_audit.py
baseline_tests/run_step67_legacy_shim_audit.py
baseline_tests/run_step67_behavior_preservation_audit.py

baseline_tests/run_step63_67_step62_regression_guard.py
baseline_tests/run_step63_67_artifact_manifest.py
```

## 14. Batch-Wide Tests

Add:

```text
tests/test_step63_simulation_freeze_contract.py
tests/test_step63_remaining_solver_inventory_contract.py
tests/test_step63_solver_completion_roadmap_contract.py
tests/test_step63_code_placement_freeze_contract.py
tests/test_step63_encoding_policy_contract.py
tests/test_step63_regression_snapshot_consistency_contract.py

tests/test_step64_motion_wall_velocity_migration_contract.py
tests/test_step64_import_execution_contract.py
tests/test_step64_legacy_shim_contract.py
tests/test_step64_bridge_retirement_contract.py
tests/test_step64_behavior_preservation_contract.py

tests/test_step65_runtime_geometry_migration_contract.py
tests/test_step65_import_execution_contract.py
tests/test_step65_legacy_shim_contract.py
tests/test_step65_behavior_preservation_contract.py

tests/test_step66_diagnostic_geometry_displacement_migration_contract.py
tests/test_step66_import_execution_contract.py
tests/test_step66_legacy_shim_contract.py
tests/test_step66_behavior_preservation_contract.py

tests/test_step67_squid_proxy_real_geometry_migration_contract.py
tests/test_step67_import_execution_contract.py
tests/test_step67_legacy_shim_contract.py
tests/test_step67_behavior_preservation_contract.py

tests/test_step63_67_step62_regression_contract.py
```

## 15. Batch-Wide Outputs

Generate and commit:

```text
outputs/step63_simulation_freeze_audit/
outputs/step63_remaining_solver_inventory_audit/
outputs/step63_solver_completion_roadmap_audit/
outputs/step63_code_placement_freeze_audit/
outputs/step63_encoding_policy_audit/
outputs/step63_regression_snapshot_consistency_audit/

outputs/step64_motion_wall_velocity_migration_audit/
outputs/step64_import_execution_audit/
outputs/step64_legacy_shim_audit/
outputs/step64_bridge_retirement_audit/
outputs/step64_behavior_preservation_audit/

outputs/step65_runtime_geometry_migration_audit/
outputs/step65_import_execution_audit/
outputs/step65_legacy_shim_audit/
outputs/step65_behavior_preservation_audit/

outputs/step66_diagnostic_geometry_displacement_migration_audit/
outputs/step66_import_execution_audit/
outputs/step66_legacy_shim_audit/
outputs/step66_behavior_preservation_audit/

outputs/step67_squid_proxy_real_geometry_migration_audit/
outputs/step67_import_execution_audit/
outputs/step67_legacy_shim_audit/
outputs/step67_behavior_preservation_audit/

outputs/step63_67_step62_regression_guard/
outputs/step63_67_artifact_manifest/

logs/step63_*.log
logs/step64_*.log
logs/step65_*.log
logs/step66_*.log
logs/step67_*.log
```

## 16. Batch-Wide Docs And Report

Add:

```text
STEP63_TO_STEP67_SOLVER_COMPLETION_BATCH_A_REPORT.md
docs/63_67_solver_completion_batch_a.md
docs/SIMULATION_FREEZE_POLICY.md
docs/SOLVER_COMPLETION_ROADMAP.md
docs/REMAINING_SOLVER_INVENTORY.md
```

Update:

```text
README.md
docs/00_project_status.md
```

Docs and report must avoid:

```text
validated propulsion
real squid validation
squid swimming
grid convergence
production ready
physical validation
```

Preferred wording:

```text
solver completion batch
simulation-free canonical ownership migration
artifact-backed audit
no new driver rows
```

## 17. Batch-Wide Acceptance Criteria

Batch A is complete only when:

```text
STEP63_TO_STEP67_SOLVER_COMPLETION_BATCH_A_GOAL.md exists
STEP63_TO_STEP67_SOLVER_COMPLETION_BATCH_A_REPORT.md exists
docs/63_67_solver_completion_batch_a.md exists
docs/SIMULATION_FREEZE_POLICY.md exists
docs/SOLVER_COMPLETION_ROADMAP.md exists
docs/REMAINING_SOLVER_INVENTORY.md exists

No new driver.run execution
No outputs/step63_driver_runs
No outputs/step64_driver_runs
No outputs/step65_driver_runs
No outputs/step66_driver_runs
No outputs/step67_driver_runs
No VTR
No particle NPY
No runtime solver behavior change
No physics feature expansion
No external/taichi_LBM3D edit
No data/real_geometry_candidates edit

Step63 freeze/inventory/roadmap/code-placement/encoding/snapshot audits pass
Step64 motion/wall_velocity migration/import/shim/bridge-retirement/behavior audits pass
Step65 runtime_geometry migration/import/shim/behavior audits pass
Step66 diagnostic geometry/displacement migration/import/shim/behavior audits pass
Step67 squid proxy/real geometry support migration/import/shim/behavior audits pass

Step62 regression guard passes
artifact manifest passes
full pytest passes under D:\working\taichi\env\python.exe
full pytest passes under D:\TOOL\Anaconda\python.exe
pre-push hook passes
git diff --check passes
```

## 18. Verification Commands

Compile:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\evidence\batch_migration_audit.py `
  src\mpm_lbm\evidence\batch_import_execution_audit.py `
  src\mpm_lbm\evidence\batch_legacy_shim_audit.py `
  src\mpm_lbm\evidence\batch_behavior_preservation_audit.py `
  src\mpm_lbm\evidence\simulation_freeze_audit.py `
  src\mpm_lbm\evidence\remaining_solver_inventory_audit.py `
  src\mpm_lbm\evidence\solver_completion_roadmap_audit.py `
  src\mpm_lbm\evidence\code_placement_freeze_audit.py `
  src\mpm_lbm\evidence\encoding_policy_audit.py `
  src\mpm_lbm\evidence\regression_snapshot_consistency_audit.py `
  src\mpm_lbm\evidence\step63_67_regression_guard.py
```

Run all Step63-67 audit runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step63_simulation_freeze_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step63_remaining_solver_inventory_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step63_solver_completion_roadmap_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step63_code_placement_freeze_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step63_encoding_policy_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step63_regression_snapshot_consistency_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step64_motion_wall_velocity_migration_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step64_import_execution_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step64_legacy_shim_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step64_bridge_retirement_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step64_behavior_preservation_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step65_runtime_geometry_migration_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step65_import_execution_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step65_legacy_shim_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step65_behavior_preservation_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step66_diagnostic_geometry_displacement_migration_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step66_import_execution_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step66_legacy_shim_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step66_behavior_preservation_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step67_squid_proxy_real_geometry_migration_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step67_import_execution_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step67_legacy_shim_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step67_behavior_preservation_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step63_67_step62_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step63_67_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests/test_step63_simulation_freeze_contract.py tests/test_step63_remaining_solver_inventory_contract.py tests/test_step63_solver_completion_roadmap_contract.py tests/test_step63_code_placement_freeze_contract.py tests/test_step63_encoding_policy_contract.py tests/test_step63_regression_snapshot_consistency_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests/test_step64_motion_wall_velocity_migration_contract.py tests/test_step64_import_execution_contract.py tests/test_step64_legacy_shim_contract.py tests/test_step64_bridge_retirement_contract.py tests/test_step64_behavior_preservation_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests/test_step65_runtime_geometry_migration_contract.py tests/test_step65_import_execution_contract.py tests/test_step65_legacy_shim_contract.py tests/test_step65_behavior_preservation_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests/test_step66_diagnostic_geometry_displacement_migration_contract.py tests/test_step66_import_execution_contract.py tests/test_step66_legacy_shim_contract.py tests/test_step66_behavior_preservation_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests/test_step67_squid_proxy_real_geometry_migration_contract.py tests/test_step67_import_execution_contract.py tests/test_step67_legacy_shim_contract.py tests/test_step67_behavior_preservation_contract.py tests/test_step63_67_step62_regression_contract.py -q
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
git diff --check HEAD~1 HEAD
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Commit and push:

```powershell
git status --short
git add .
git diff --cached --check
git commit -m "test: add steps63-67 solver completion batch a"
git push origin main
```

## 19. Step 68 Reserved Direction

After Batch A, Step 68 should remain simulation-free:

```text
Step68 Step-Specific Proxy Migration To experiments/steps
```

Step 68 should migrate:

```text
src/runtime_geometry_wall_velocity_one_cycle_*
src/runtime_geometry_wall_velocity_transfer_*
src/runtime_geometry_wall_velocity_48_feasibility_*
src/runtime_geometry_wall_velocity_support_scaling_*
```

The Step68 target:

```text
root src step-specific implementation count == 0
```

Step 69 can then perform root `src/*.py` final cleanup. Step 70 can perform API/config freeze. Step 71 can handle the tau convention decision. Step 75 or later can resume solver-complete simulation campaigns.

## 20. Done Criteria

Batch A is done only when:

```text
Detailed goal file exists and active goal references it.
All Step63-67 required configs, canonical packages, shims, audit modules, runners, tests, docs, report, logs, and artifacts are committed.
No new driver.run simulation exists in Batch A executable files.
No Step63-67 driver output directory exists.
All migration audits pass.
All import execution audits pass.
All legacy shim audits pass.
All behavior preservation audits pass.
Step62 regression guard passes.
Artifact manifest passes.
Focused Batch A tests pass.
Full Taichi pytest passes.
Full Anaconda pytest passes.
Git checks pass.
Commit uses: test: add steps63-67 solver completion batch a
Commit is pushed to origin/main.
Final response reports commit hash, remote branch, validation pass counts, audit pass status, artifact summary, and no-simulation proof.
```
