# Step 69 Root src Final Implementation Cleanup Goal

## Step Name

Step69 Root src Final Implementation Cleanup

## Source Context

`origin/main` is expected to start from Step68 commit:

```text
2ff617d17ef2f715f8a396094a13898bb5df7d09
```

Step68 migrated the Step63 `step_specific_proxy_remaining` rows from root
`src/` into `experiments/steps/` and left root files as compatibility shims.
Step69 must not reinterpret Step63 inventory as the current post-Step68 root
state. Step69 must generate a new current root inventory and then finish the
remaining support migration and policy cleanup.

## Goal

Step69 closes the remaining root `src/*.py` implementation cleanup after
Step68. The expected final state is a root `src/` surface made of canonical
package implementations plus explicit compatibility shims or documented
approved legacy tooling. Step69 is a code-placement, import-boundary, and
evidence-integrity step. It is not a physics-activation step.

The work must:

1. Generate a new Step68-post current root inventory.
2. Prove root step-specific implementation count is zero.
3. Migrate the six Step63 `migration_required` support rows into canonical
   package locations.
4. Leave the six original root files as thin compatibility shims only.
5. Define which root `src/*.py` files are approved compatibility/legacy
   surfaces and which would require future migration.
6. Refresh the `src.__init__` export surface so it points to canonical modules
   where canonical modules exist.
7. Prove `import src` remains lazy and does not eagerly import heavy runtime
   dependencies.
8. Preserve Step68 evidence and guard it with a Step69 regression check.
9. Produce checked-in configs, evidence builders, runners, tests, logs,
   outputs, docs, and a Step69 report.
10. Commit and push the verified result to `origin/main`.

## Explicit Non-Goals

Step69 must not run or introduce:

```text
driver.run()
FSIDriver3D(...).run()
driver.initialize()
driver.step_once()
outputs/step69_driver_runs
runtime geometry activation
wall velocity activation
real geometry run
squid simulation
48^3 / 64^3 runs
VTR output
particle NPY output
tau convention migration
solver formula changes
physics validation claims
external/taichi_LBM3D edits
data/real_geometry_candidates edits
```

Step69 may import lightweight support modules for identity/audit checks, but
must not execute solver stepping or create driver-run artifacts.

## Required Support Migrations

The policy file must list exactly these six migrations. Public symbols must be
captured from the source files using AST inspection and verified by evidence.

### Squid Proxy Support

1. `src/squid_region_projection.py`
   - Canonical path:
     `src/mpm_lbm/sim/squid_proxy/region_projection.py`
   - Canonical module:
     `src.mpm_lbm.sim.squid_proxy.region_projection`
   - Legacy root module:
     `src.squid_region_projection`
   - Classification: `squid_proxy_support`

2. `src/squid_region_quality.py`
   - Canonical path:
     `src/mpm_lbm/sim/squid_proxy/region_quality.py`
   - Canonical module:
     `src.mpm_lbm.sim.squid_proxy.region_quality`
   - Legacy root module:
     `src.squid_region_quality`
   - Classification: `squid_proxy_support`

3. `src/squid_region_driver_diagnostics.py`
   - Canonical path:
     `src/mpm_lbm/diagnostics/squid_region_driver.py`
   - Canonical module:
     `src.mpm_lbm.diagnostics.squid_region_driver`
   - Legacy root module:
     `src.squid_region_driver_diagnostics`
   - Classification: `squid_region_diagnostics`
   - Decision: this is a diagnostics/report helper unless a runtime driver
     import proves otherwise. Default placement is diagnostics, not `sim/`.

### Wall Velocity Support

4. `src/wall_velocity_application_envelope.py`
   - Canonical path:
     `src/mpm_lbm/sim/wall_velocity/application_envelope.py`
   - Canonical module:
     `src.mpm_lbm.sim.wall_velocity.application_envelope`
   - Legacy root module:
     `src.wall_velocity_application_envelope`
   - Classification: `wall_velocity_support`

5. `src/wall_velocity_consistency.py`
   - Canonical path:
     `src/mpm_lbm/sim/wall_velocity/consistency.py`
   - Canonical module:
     `src.mpm_lbm.sim.wall_velocity.consistency`
   - Legacy root module:
     `src.wall_velocity_consistency`
   - Classification: `wall_velocity_support`

6. `src/wall_velocity_quality.py`
   - Canonical path:
     `src/mpm_lbm/sim/wall_velocity/quality.py`
   - Canonical module:
     `src.mpm_lbm.sim.wall_velocity.quality`
   - Legacy root module:
     `src.wall_velocity_quality`
   - Classification: `wall_velocity_support`

## Required Configs

Create or update:

```text
configs/step69_current_root_inventory_policy.json
configs/step69_remaining_support_migration_policy.json
configs/step69_root_src_approved_legacy_policy.json
configs/step69_src_init_export_policy.json
configs/step69_code_placement_policy.json
configs/step69_no_simulation_policy.json
```

The migration policy must include:

```text
policy_id = step69_remaining_support_migration_policy
step = 69
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = false
migration_count = 6
```

It must include `public_symbols` and `symbol_kinds` for each migration. These
must match AST-discovered top-level public functions/classes and public
constants in the original legacy files.

## Required Evidence Builders

Create or update:

```text
src/mpm_lbm/evidence/current_root_inventory_audit.py
src/mpm_lbm/evidence/remaining_support_migration_audit.py
src/mpm_lbm/evidence/root_src_final_cleanup_audit.py
src/mpm_lbm/evidence/src_init_export_refresh_audit.py
src/mpm_lbm/evidence/step69_code_placement_audit.py
src/mpm_lbm/evidence/step69_no_simulation_audit.py
src/mpm_lbm/evidence/step69_regression_guard.py
```

Evidence must use source inspection and committed artifacts where possible.
It must not depend on running a new driver simulation.

## Required Runners

Create:

```text
baseline_tests/step69_common.py
baseline_tests/run_step69_current_root_inventory_audit.py
baseline_tests/run_step69_remaining_support_migration_audit.py
baseline_tests/run_step69_import_execution_audit.py
baseline_tests/run_step69_legacy_shim_audit.py
baseline_tests/run_step69_root_src_final_cleanup_audit.py
baseline_tests/run_step69_src_init_export_audit.py
baseline_tests/run_step69_code_placement_audit.py
baseline_tests/run_step69_no_simulation_audit.py
baseline_tests/run_step69_step68_regression_guard.py
baseline_tests/run_step69_artifact_manifest.py
```

Runners must write JSON, CSV, summary CSV, and log artifacts under the Step69
output/log paths.

## Required Tests

Create:

```text
tests/test_step69_current_root_inventory_contract.py
tests/test_step69_remaining_support_migration_contract.py
tests/test_step69_import_execution_contract.py
tests/test_step69_legacy_shim_contract.py
tests/test_step69_root_src_final_cleanup_contract.py
tests/test_step69_src_init_export_contract.py
tests/test_step69_code_placement_contract.py
tests/test_step69_no_simulation_contract.py
tests/test_step69_step68_regression_contract.py
```

Tests must cover both builder behavior and committed artifacts. They should
avoid importing heavy runtime modules unless the tested contract explicitly
requires import identity checks for the six migrated support rows.

## Required Outputs

Generate and commit:

```text
outputs/step69_current_root_inventory_audit/
outputs/step69_remaining_support_migration_audit/
outputs/step69_import_execution_audit/
outputs/step69_legacy_shim_audit/
outputs/step69_root_src_final_cleanup_audit/
outputs/step69_src_init_export_audit/
outputs/step69_code_placement_audit/
outputs/step69_no_simulation_audit/
outputs/step69_step68_regression_guard/
outputs/step69_artifact_manifest/
logs/step69_*.log
```

## Required Docs and Reports

Create:

```text
STEP69_ROOT_SRC_FINAL_IMPLEMENTATION_CLEANUP_REPORT.md
docs/69_root_src_final_implementation_cleanup.md
docs/ROOT_SRC_COMPATIBILITY_POLICY.md
```

Update `README.md` so the implemented Step list includes Step69.

## Acceptance Criteria

All of these must be true:

```text
Step69 goal/report/docs exist
current_root_inventory_audit_pass == true
current_step_specific_proxy_remaining_count == 0
current_root_step_specific_implementation_count == 0
current_unknown_requires_review_count == 0

remaining_support_migration_audit_pass == true
migration_required_count_from_step63 == 6
migrated_support_count == 6
remaining_migration_required_count == 0

legacy_shim_count_for_six_support_rows == 6
legacy_implementation_body_count_for_six_support_rows == 0
canonical_imports_legacy_root_count == 0
same_object_count == public_symbol_count

src_init_export_audit_pass == true
no_stale_export_count == 0
heavy_import_during_src_import == false

code_placement_audit_pass == true
no_simulation_audit_pass == true
step68_regression_guard_pass == true
artifact_budget_pass == true
```

The repository must also pass focused Step69 tests and full pytest under the
trusted interpreter. If the Anaconda interpreter is available, run the full
pytest suite there too.

## Verification Commands

Use the trusted interpreter first:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\evidence\current_root_inventory_audit.py `
  src\mpm_lbm\evidence\remaining_support_migration_audit.py `
  src\mpm_lbm\evidence\root_src_final_cleanup_audit.py `
  src\mpm_lbm\evidence\src_init_export_refresh_audit.py `
  src\mpm_lbm\evidence\step69_code_placement_audit.py `
  src\mpm_lbm\evidence\step69_no_simulation_audit.py `
  src\mpm_lbm\evidence\step69_regression_guard.py `
  baseline_tests\step69_common.py `
  baseline_tests\run_step69_current_root_inventory_audit.py `
  baseline_tests\run_step69_remaining_support_migration_audit.py `
  baseline_tests\run_step69_import_execution_audit.py `
  baseline_tests\run_step69_legacy_shim_audit.py `
  baseline_tests\run_step69_root_src_final_cleanup_audit.py `
  baseline_tests\run_step69_src_init_export_audit.py `
  baseline_tests\run_step69_code_placement_audit.py `
  baseline_tests\run_step69_no_simulation_audit.py `
  baseline_tests\run_step69_step68_regression_guard.py `
  baseline_tests\run_step69_artifact_manifest.py
```

Run all Step69 runners:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step69_current_root_inventory_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step69_remaining_support_migration_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step69_import_execution_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step69_legacy_shim_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step69_root_src_final_cleanup_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step69_src_init_export_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step69_code_placement_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step69_no_simulation_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step69_step68_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step69_artifact_manifest.py
```

Run focused and full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step69_current_root_inventory_contract.py tests\test_step69_remaining_support_migration_contract.py tests\test_step69_import_execution_contract.py tests\test_step69_legacy_shim_contract.py tests\test_step69_root_src_final_cleanup_contract.py tests\test_step69_src_init_export_contract.py tests\test_step69_code_placement_contract.py tests\test_step69_no_simulation_contract.py tests\test_step69_step68_regression_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Before commit and push:

```powershell
git diff --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
git commit -m "test: add step69 root src final cleanup"
git push origin main
```
