# Step 70 API And Config Freeze Before Activation Goal

## Step Name

Step70 API And Config Freeze Before Activation

## Source Context

`origin/main` is expected to start from Step69 commit:

```text
d1a767692269d807bbaef8bdd645d3697150b247
test: add step69 root src final cleanup
```

Step69 completed the root `src/*.py` final implementation cleanup, migrated
the remaining six support rows into canonical packages, refreshed the lazy
`src.__init__` squid exports, and proved the current root inventory has no
remaining migration-required or unknown rows.

Step70 is the freeze step after that cleanup. It must not activate any solver
behavior. It must make API, compatibility, config schema, activation gate, and
artifact/report policy explicit before later activation or tau-convention work.

## Goal

Step70 freezes the public and compatibility surfaces that later steps must
respect before runtime geometry, wall velocity, real geometry, squid proxy, or
larger-grid activation work continues.

The work must:

1. Repair the known Step69 report/artifact-summary mismatch.
2. Add a report consistency guard so report numbers cannot drift from committed
   artifact JSON summaries.
3. Freeze the canonical public API surface with explicit policy entries.
4. Freeze the legacy compatibility import surface, including `src.__init__`
   lazy exports and root compatibility shims.
5. Freeze config schema snapshots and schema hashes for required config
   classes.
6. Freeze activation preconditions and keep every activation gate closed.
7. Freeze output/artifact policy, including VTR, particle NPY, protected
   external edits, protected real-geometry edits, report consistency, and
   artifact manifest requirements.
8. Guard Step69 evidence so the root cleanup remains green.
9. Produce checked-in configs, evidence builders, runners, tests, docs, logs,
   outputs, report, and artifact manifest.
10. Verify with focused and full pytest under the trusted interpreter, run the
    Anaconda interpreter full pytest when available, commit, and push to
    `origin/main`.

## Explicit Non-Goals

Step70 must not run or introduce:

```text
driver.run()
FSIDriver3D(...).run()
driver.initialize()
driver.step_once()
outputs/step70_driver_runs
runtime geometry activation
wall velocity activation
real geometry run
squid simulation
48^3 / 64^3 runs
VTR output
particle NPY output
solver formula changes
tau convention migration
physics validation claims
grid convergence claims
production readiness claims
external/taichi_LBM3D edits
data/real_geometry_candidates edits
```

Step70 may use imports, source-text checks, dataclass/signature
introspection, schema hashing, legacy shim identity checks, committed artifact
checks, and report consistency checks. These checks must not construct
runtime solver objects when a symbol can be verified by import and source
inspection alone.

## Phase 0: Repair Step69 Report Consistency

Modify:

```text
STEP69_ROOT_SRC_FINAL_IMPLEMENTATION_CLEANUP_REPORT.md
```

The Step69 artifact manifest row must match:

```text
outputs/step69_artifact_manifest/artifact_summary.json
```

Required values:

```text
step69_file_count = 90
step69_total_size_mb = 0.6521368026733398
large_file_count = 0
step69_vtr_count = 0
step69_particle_npy_count = 0
step69_driver_run_output_dir_count = 0
```

Add:

```text
configs/step70_report_consistency_policy.json
src/mpm_lbm/evidence/report_consistency_freeze_audit.py
baseline_tests/run_step70_report_consistency_audit.py
tests/test_step70_report_consistency_contract.py
outputs/step70_report_consistency_audit/
```

The audit must verify:

```text
step69_report_consistency_fixed == true
report_consistency_freeze_audit_pass == true
fail_count == 0
Step69 report file count matches Step69 artifact summary JSON
Step69 report total size MB matches Step69 artifact summary JSON
Step70 report file count matches Step70 artifact summary JSON when the Step70
artifact manifest has been generated
Step70 report total size MB matches Step70 artifact summary JSON when the
Step70 artifact manifest has been generated
```

## Phase 1: Public API Surface Freeze

Add:

```text
configs/step70_public_api_surface_policy.json
src/mpm_lbm/evidence/public_api_surface_audit.py
baseline_tests/run_step70_public_api_surface_audit.py
tests/test_step70_public_api_surface_contract.py
outputs/step70_public_api_surface_audit/
docs/PUBLIC_API_SURFACE.md
```

The public API policy must be explicit, not automatic-only. It must group
symbols under:

```text
driver_api
lbm_mpm_api
coupling_api
geometry_api
motion_wall_velocity_api
runtime_geometry_displacement_api
squid_proxy_api
diagnostics_api
experiments_api
```

The audit rows must include:

```text
api_group
symbol
canonical_module
canonical_import_pass
object_type
runtime_object_construction_required
solver_run
output_snapshot_unchanged
pass
```

Acceptance:

```text
public_api_surface_audit_pass == true
canonical_import_pass_count == expected_count
missing_symbol_count == 0
solver_run == false
output_snapshot_unchanged == true
```

## Phase 2: Compatibility Surface Freeze

Add:

```text
configs/step70_compatibility_surface_policy.json
src/mpm_lbm/evidence/compatibility_surface_audit.py
baseline_tests/run_step70_compatibility_surface_audit.py
tests/test_step70_compatibility_surface_contract.py
outputs/step70_compatibility_surface_audit/
docs/COMPATIBILITY_AND_DEPRECATION_POLICY.md
```

The policy must classify `src.__init__` lazy exports as one of:

```text
canonical_target_required
legacy_shim_target_allowed
approved_legacy_tooling_allowed
forbidden_target
```

Canonical targets are required for canonicalized driver, geometry, and squid
region exports. Legacy shim targets may remain temporarily for legacy LBM,
MPM, projection, moving-boundary, and unit exports only when the target root
file is a compatibility shim and canonical/legacy imports resolve to the same
object.

Forbidden targets include:

```text
src.runtime_geometry_wall_velocity_*
src.real_geometry_feasibility
src.squid_region_projection
src.squid_region_quality
src.squid_region_driver_diagnostics
src.wall_velocity_application_envelope
src.wall_velocity_consistency
src.wall_velocity_quality
```

Acceptance:

```text
compatibility_surface_audit_pass == true
src_init_export_count == expected_count
stale_export_count == 0
forbidden_target_count == 0
legacy_shim_target_count is reported
legacy_shim_targets_are_shims == true
same_object_count == expected_count
heavy_import_during_src_import == false
```

## Phase 3: Config Schema Freeze

Add:

```text
configs/step70_config_schema_freeze_policy.json
src/mpm_lbm/evidence/config_schema_freeze_audit.py
baseline_tests/run_step70_config_schema_freeze_audit.py
tests/test_step70_config_schema_freeze_contract.py
outputs/step70_config_schema_freeze_audit/
docs/CONFIG_SCHEMA_FREEZE.md
```

Required config classes:

```text
FSIDriverConfig
UnifiedSimConfig
LBMConfig
MPMConfig
GeometryConfig
BoundaryMotionInterfaceConfig
GeometryMotionInterfaceConfig
WallVelocityApplicationConfig
WallVelocityFieldConfig
RuntimeGeometryProjectionIntegrationConfig
GeometryDisplacementConfig
SquidProxyRegionConfig
SquidKinematicsScheduleConfig
SquidMotionMappingConfig
```

For each class, record:

```text
class_name
canonical_module
is_dataclass
init_signature
public_fields_or_constructor_params
default_values_repr
from_json_available
to_json_or_to_dict_available
schema_hash
```

Write:

```text
outputs/step70_config_schema_freeze_audit/config_schema_freeze.json
outputs/step70_config_schema_freeze_audit/config_schema_freeze.csv
```

Acceptance:

```text
config_schema_freeze_audit_pass == true
schema_row_count >= required_config_class_count
missing_config_class_count == 0
schema_hash_count == schema_row_count
from_json_available_count is reported
```

## Phase 4: Activation Preconditions Freeze

Add:

```text
configs/step70_activation_preconditions_policy.json
src/mpm_lbm/evidence/activation_preconditions_audit.py
baseline_tests/run_step70_activation_preconditions_audit.py
tests/test_step70_activation_preconditions_contract.py
outputs/step70_activation_preconditions_audit/
docs/ACTIVATION_PRECONDITIONS.md
```

All activation gates must remain false:

```text
runtime_geometry_activation_allowed = false
wall_velocity_activation_allowed = false
combined_runtime_geometry_wall_velocity_activation_allowed = false
real_geometry_activation_allowed = false
squid_proxy_activation_allowed = false
link_area_activation_allowed = false
grid_48_activation_allowed = false
grid_64_activation_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
```

Policy must preserve pending gate reasons:

```text
Step71 tau convention decision pending
Step72 runtime geometry activation readiness pending
Step73 wall velocity activation readiness pending
Step74 real geometry data boundary pending
Step75 solver-complete campaign gate pending
```

Acceptance:

```text
activation_preconditions_audit_pass == true
activation_allowed_count == 0
pending_gate_count >= 5
```

## Phase 5: Output And Artifact Policy Freeze

Add:

```text
configs/step70_output_artifact_policy.json
src/mpm_lbm/evidence/output_artifact_policy_audit.py
baseline_tests/run_step70_output_artifact_policy_audit.py
tests/test_step70_output_artifact_policy_contract.py
outputs/step70_output_artifact_policy_audit/
```

Freeze these defaults:

```text
default_write_vtk_allowed = false
default_write_particles_allowed = false
driver_run_outputs_committable = false unless step-specific smoke budget says true
private_absolute_paths_allowed = false
external_taichi_lbm3d_edit_allowed = false
real_geometry_candidates_edit_allowed = false
report_consistency_guard_required = true
artifact_manifest_required = true
large_file_threshold_mb = 5
```

Acceptance:

```text
output_artifact_policy_audit_pass == true
vtr_default_allowed == false
particle_npy_default_allowed == false
protected_external_edit_allowed == false
protected_real_geometry_edit_allowed == false
report_consistency_required == true
artifact_manifest_required == true
```

## Phase 6: Step69 Regression Guard

Add:

```text
src/mpm_lbm/evidence/step70_regression_guard.py
baseline_tests/run_step70_step69_regression_guard.py
tests/test_step70_step69_regression_contract.py
outputs/step70_step69_regression_guard/
```

The guard must verify:

```text
current_root_inventory_audit_pass == true
current_migration_required_count == 0
current_root_step_specific_implementation_count == 0
current_unknown_requires_review_count == 0
remaining_support_migration_audit_pass == true
step69_import_execution_audit_pass == true
step69_legacy_shim_audit_pass == true
src_init_export_audit_pass == true
no_simulation_audit_pass == true
artifact_budget_pass == true
```

## Required Step70 Files

Configs:

```text
configs/step70_public_api_surface_policy.json
configs/step70_compatibility_surface_policy.json
configs/step70_config_schema_freeze_policy.json
configs/step70_activation_preconditions_policy.json
configs/step70_output_artifact_policy.json
configs/step70_report_consistency_policy.json
```

Evidence:

```text
src/mpm_lbm/evidence/public_api_surface_audit.py
src/mpm_lbm/evidence/compatibility_surface_audit.py
src/mpm_lbm/evidence/config_schema_freeze_audit.py
src/mpm_lbm/evidence/activation_preconditions_audit.py
src/mpm_lbm/evidence/output_artifact_policy_audit.py
src/mpm_lbm/evidence/report_consistency_freeze_audit.py
src/mpm_lbm/evidence/step70_regression_guard.py
```

Runners:

```text
baseline_tests/step70_common.py
baseline_tests/run_step70_public_api_surface_audit.py
baseline_tests/run_step70_compatibility_surface_audit.py
baseline_tests/run_step70_config_schema_freeze_audit.py
baseline_tests/run_step70_activation_preconditions_audit.py
baseline_tests/run_step70_output_artifact_policy_audit.py
baseline_tests/run_step70_report_consistency_audit.py
baseline_tests/run_step70_step69_regression_guard.py
baseline_tests/run_step70_artifact_manifest.py
```

Tests:

```text
tests/test_step70_public_api_surface_contract.py
tests/test_step70_compatibility_surface_contract.py
tests/test_step70_config_schema_freeze_contract.py
tests/test_step70_activation_preconditions_contract.py
tests/test_step70_output_artifact_policy_contract.py
tests/test_step70_report_consistency_contract.py
tests/test_step70_step69_regression_contract.py
```

Docs:

```text
STEP70_API_CONFIG_FREEZE_BEFORE_ACTIVATION_REPORT.md
docs/70_api_config_freeze_before_activation.md
docs/PUBLIC_API_SURFACE.md
docs/CONFIG_SCHEMA_FREEZE.md
docs/COMPATIBILITY_AND_DEPRECATION_POLICY.md
docs/ACTIVATION_PRECONDITIONS.md
```

Outputs:

```text
outputs/step70_public_api_surface_audit/
outputs/step70_compatibility_surface_audit/
outputs/step70_config_schema_freeze_audit/
outputs/step70_activation_preconditions_audit/
outputs/step70_output_artifact_policy_audit/
outputs/step70_report_consistency_audit/
outputs/step70_step69_regression_guard/
outputs/step70_artifact_manifest/
logs/step70_*.log
```

## Acceptance Criteria

All of these must be true:

```text
Step70 goal/report/docs exist

Step69 report consistency repaired
step69 report file_count matches artifact_summary.json
step69 report total_size_mb matches artifact_summary.json
report_consistency_freeze_audit_pass == true

public_api_surface_audit_pass == true
canonical_import_pass_count == expected_count
solver_run == false
output_snapshot_unchanged == true

compatibility_surface_audit_pass == true
src_init_export_audit_pass == true
stale_export_count == 0
forbidden_target_count == 0
heavy_import_during_src_import == false
legacy_shim_targets_are_shims == true

config_schema_freeze_audit_pass == true
missing_config_class_count == 0
schema snapshots committed
schema hashes stable

activation_preconditions_audit_pass == true
activation_allowed_count == 0
pending_gate_count >= 5

output_artifact_policy_audit_pass == true
default VTR disabled
default particle NPY disabled
protected external edits disabled
protected real geometry edits disabled
report consistency required
artifact manifest required

Step69 regression guard passes
artifact manifest passes

No driver.run
No FSIDriver3D(...).run
No outputs/step70_driver_runs
No VTR
No particle NPY
No runtime solver behavior change
No physics feature expansion

focused Step70 pytest passes
full pytest passes under D:\working\taichi\env\python.exe
full pytest passes under D:\TOOL\Anaconda\python.exe when available
pre-push hook passes
git diff --check passes
external/taichi_LBM3D clean
data/real_geometry_candidates clean
```

## Verification Commands

Compile:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\evidence\public_api_surface_audit.py `
  src\mpm_lbm\evidence\compatibility_surface_audit.py `
  src\mpm_lbm\evidence\config_schema_freeze_audit.py `
  src\mpm_lbm\evidence\activation_preconditions_audit.py `
  src\mpm_lbm\evidence\output_artifact_policy_audit.py `
  src\mpm_lbm\evidence\report_consistency_freeze_audit.py `
  src\mpm_lbm\evidence\step70_regression_guard.py `
  baseline_tests\step70_common.py `
  baseline_tests\run_step70_public_api_surface_audit.py `
  baseline_tests\run_step70_compatibility_surface_audit.py `
  baseline_tests\run_step70_config_schema_freeze_audit.py `
  baseline_tests\run_step70_activation_preconditions_audit.py `
  baseline_tests\run_step70_output_artifact_policy_audit.py `
  baseline_tests\run_step70_report_consistency_audit.py `
  baseline_tests\run_step70_step69_regression_guard.py `
  baseline_tests\run_step70_artifact_manifest.py
```

Run Step70 audits:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step70_report_consistency_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step70_public_api_surface_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step70_compatibility_surface_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step70_config_schema_freeze_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step70_activation_preconditions_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step70_output_artifact_policy_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step70_step69_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step70_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest `
  tests\test_step70_report_consistency_contract.py `
  tests\test_step70_public_api_surface_contract.py `
  tests\test_step70_compatibility_surface_contract.py `
  tests\test_step70_config_schema_freeze_contract.py `
  tests\test_step70_activation_preconditions_contract.py `
  tests\test_step70_output_artifact_policy_contract.py `
  tests\test_step70_step69_regression_contract.py `
  -q
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

Commit:

```powershell
git add .
git commit -m "test: add step70 api config freeze"
git push origin main
```
