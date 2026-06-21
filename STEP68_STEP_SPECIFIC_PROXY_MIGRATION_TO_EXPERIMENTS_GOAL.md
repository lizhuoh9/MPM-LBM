# Step 68 Step-Specific Proxy Migration To experiments/steps Goal

## Source Context

This goal follows the GitHub review note in:

```text
C:\Users\lizhu\.codex\attachments\5e74bde5-6629-4229-ac8b-40548ceffbaa\pasted-text.txt
```

The current base commit is:

```text
f28cfc8fb3a3811220c6d98472198a3187ebda41
test: add steps63-67 solver completion batch a
```

Step 63-67 Solver Completion Batch A established canonical solver ownership, retired temporary Step58 bridge surfaces, and produced a remaining solver inventory. Step68 must now move step-specific proxy implementations out of root `src/` and into `experiments/steps/` without activating new solver behavior.

## Step Name

```text
Step68 Step-Specific Proxy Migration To experiments/steps
```

## Required Files

Goal:

```text
STEP68_STEP_SPECIFIC_PROXY_MIGRATION_TO_EXPERIMENTS_GOAL.md
```

Report:

```text
STEP68_STEP_SPECIFIC_PROXY_MIGRATION_TO_EXPERIMENTS_REPORT.md
```

Documentation:

```text
docs/68_step_specific_proxy_migration_to_experiments.md
```

Commit message:

```text
test: add step68 step-specific proxy migration
```

## Primary Objective

Migrate every file that Step63 inventory classified as:

```text
classification == step_specific_proxy_remaining
target_owner == experiments/steps
recommended_step == Step68
```

out of root `src/` and into `experiments/steps/`.

The Step63 committed inventory currently reports:

```text
step_specific_proxy_remaining_count = 34
```

Step68 must prove that:

```text
policy_migration_count == 34
missing_inventory_paths == []
extra_policy_paths == []
root src step-specific implementation count == 0
all migrated root files are thin shims
experiment package imports work
legacy root imports still work
canonical and legacy public symbols are identical objects
```

## Explicit Non-Goals

Step68 does not run or add any new solver simulation.

Step68 does not activate runtime geometry, wall velocity, squid behavior, real geometry, or any combined solver path.

Step68 does not change solver formulas.

Step68 does not claim physical validation, real squid validation, production solver readiness, or new stability evidence.

Step68 does not perform Step69 remaining support cleanup or Step70 API/config freeze.

## Hard Runtime Boundary

The Step68 implementation, runners, tests, and generated evidence must not add or execute:

```text
FSIDriver3D(...).run()
driver.run()
driver.initialize()
driver.step_once()
outputs/step68_driver_runs
write_vtk = true
write_particles = true
```

Exception and required reporting:

```text
experiments/steps/real_geometry_feasibility/feasibility.py may contain the pre-existing historical short-driver helper moved from src/real_geometry_feasibility.py.
That helper must be classified as quarantined historical experiment code.
Step68 must not execute it.
Step68 runners/tests/evidence must not call it.
It must not be placed under src/mpm_lbm/sim.
The experiment boundary audit must report quarantined_driver_helper_count separately from Step68 executable driver calls.
```

Step68 must also prove:

```text
No VTR
No particle NPY
No runtime solver behavior change
No physics feature expansion
No external/taichi_LBM3D edit
No data/real_geometry_candidates edit
```

Allowed checks:

```text
AST/source audits
policy-vs-inventory audits
import execution audits
legacy shim audits
experiment boundary audits
source-text driver-call guards
artifact manifest checks
Step63-67 regression checks
pytest contract tests
```

## Directory Ownership Rules

Step68 implementation owners:

```text
experiments/steps/real_geometry_feasibility/
experiments/steps/runtime_geometry_wall_velocity_shared/
experiments/steps/step48_10step_proxy/
experiments/steps/step49_20step_proxy/
experiments/steps/step50_one_cycle_proxy/
experiments/steps/step51_transfer_comparison_proxy/
experiments/steps/step52_48_feasibility_proxy/
experiments/steps/step53_support_scaling_audit/
```

Compatibility shims:

```text
src/real_geometry_feasibility.py
src/runtime_geometry_wall_velocity_*.py
```

Evidence:

```text
src/mpm_lbm/evidence/
```

Runners:

```text
baseline_tests/
```

Contracts:

```text
tests/
```

Outputs:

```text
outputs/step68_*/
logs/step68_*.log
```

Forbidden placement:

```text
Do not place step-specific proxy implementation in src/mpm_lbm/sim/
Do not place step-specific proxy implementation in src/mpm_lbm/diagnostics/
Do not place reusable solver runtime implementation in experiments/steps/
Do not put runner logic in tests/
Do not put reusable audit logic in baseline_tests/
```

## Migration Groups

### A. Real Geometry Feasibility Experiment

Migrate:

```text
src/real_geometry_feasibility.py
  -> experiments/steps/real_geometry_feasibility/feasibility.py
```

Add:

```text
experiments/steps/real_geometry_feasibility/__init__.py
```

Root shim:

```text
src/real_geometry_feasibility.py
```

Acceptance:

```text
real_geometry_feasibility is not under src/mpm_lbm/sim
real_geometry_feasibility is not executed
no data/real_geometry_candidates edit
legacy import src.real_geometry_feasibility still works
experiment import experiments.steps.real_geometry_feasibility.feasibility works
public symbols are identical objects through the shim
```

### B. Shared Runtime Geometry Wall Velocity Proxy Package

Target package:

```text
experiments/steps/runtime_geometry_wall_velocity_shared/
```

Migrate:

```text
src/runtime_geometry_wall_velocity_coupling.py
  -> experiments/steps/runtime_geometry_wall_velocity_shared/coupling.py

src/runtime_geometry_wall_velocity_coupling_config.py
  -> experiments/steps/runtime_geometry_wall_velocity_shared/coupling_config.py

src/runtime_geometry_wall_velocity_diagnostics.py
  -> experiments/steps/runtime_geometry_wall_velocity_shared/diagnostics.py

src/runtime_geometry_wall_velocity_envelope.py
  -> experiments/steps/runtime_geometry_wall_velocity_shared/envelope.py

src/runtime_geometry_wall_velocity_envelope_config.py
  -> experiments/steps/runtime_geometry_wall_velocity_shared/envelope_config.py

src/runtime_geometry_wall_velocity_envelope_diagnostics.py
  -> experiments/steps/runtime_geometry_wall_velocity_shared/envelope_diagnostics.py

src/runtime_geometry_wall_velocity_envelope_state_guard.py
  -> experiments/steps/runtime_geometry_wall_velocity_shared/envelope_state_guard.py

src/runtime_geometry_wall_velocity_state_guard.py
  -> experiments/steps/runtime_geometry_wall_velocity_shared/state_guard.py
```

Root files must become thin shims.

Canonical experiment files must import other migrated proxy helpers through `experiments.steps.runtime_geometry_wall_velocity_shared.*`, not through root `src.runtime_geometry_wall_velocity_*`.

### C. Step47 Short-Step Proxy Handling

Step63 inventory may not include independent `step47_*` files. If no independent Step47 root files exist, Step68 must record this as:

```text
step47_supported_by = experiments/steps/runtime_geometry_wall_velocity_shared
```

Do not invent new Step47 implementation files unless the current inventory requires them.

### D. Step48 10-Step Proxy Package

Target package:

```text
experiments/steps/step48_10step_proxy/
```

Migrate:

```text
src/runtime_geometry_wall_velocity_10step_config.py
  -> experiments/steps/step48_10step_proxy/config.py

src/runtime_geometry_wall_velocity_10step_diagnostics.py
  -> experiments/steps/step48_10step_proxy/diagnostics.py

src/runtime_geometry_wall_velocity_10step_envelope.py
  -> experiments/steps/step48_10step_proxy/envelope.py

src/runtime_geometry_wall_velocity_10step_state_guard.py
  -> experiments/steps/step48_10step_proxy/state_guard.py
```

### E. Step49 20-Step Proxy Package

Target package:

```text
experiments/steps/step49_20step_proxy/
```

Migrate:

```text
src/runtime_geometry_wall_velocity_20step_config.py
  -> experiments/steps/step49_20step_proxy/config.py

src/runtime_geometry_wall_velocity_20step_diagnostics.py
  -> experiments/steps/step49_20step_proxy/diagnostics.py

src/runtime_geometry_wall_velocity_20step_envelope.py
  -> experiments/steps/step49_20step_proxy/envelope.py

src/runtime_geometry_wall_velocity_20step_state_guard.py
  -> experiments/steps/step49_20step_proxy/state_guard.py
```

### F. Step50 One-Cycle Proxy Package

Target package:

```text
experiments/steps/step50_one_cycle_proxy/
```

Migrate and replace any existing lazy wrapper with real implementation:

```text
src/runtime_geometry_wall_velocity_one_cycle_config.py
  -> experiments/steps/step50_one_cycle_proxy/config.py

src/runtime_geometry_wall_velocity_one_cycle_diagnostics.py
  -> experiments/steps/step50_one_cycle_proxy/diagnostics.py

src/runtime_geometry_wall_velocity_one_cycle_envelope.py
  -> experiments/steps/step50_one_cycle_proxy/envelope.py

src/runtime_geometry_wall_velocity_one_cycle_state_guard.py
  -> experiments/steps/step50_one_cycle_proxy/state_guard.py
```

Acceptance:

```text
experiments/steps/step50_one_cycle_proxy/envelope.py contains real implementation
no legacy_getattr in experiment implementation
root Step50 one-cycle files are thin shims
```

### G. Step51 Transfer Comparison Proxy Package

Target package:

```text
experiments/steps/step51_transfer_comparison_proxy/
```

Migrate:

```text
src/runtime_geometry_wall_velocity_transfer_config.py
  -> experiments/steps/step51_transfer_comparison_proxy/config.py

src/runtime_geometry_wall_velocity_transfer_diagnostics.py
  -> experiments/steps/step51_transfer_comparison_proxy/diagnostics.py

src/runtime_geometry_wall_velocity_transfer_envelope.py
  -> experiments/steps/step51_transfer_comparison_proxy/envelope.py

src/runtime_geometry_wall_velocity_transfer_state_guard.py
  -> experiments/steps/step51_transfer_comparison_proxy/state_guard.py
```

### H. Step52 48 Feasibility Proxy Package

Target package:

```text
experiments/steps/step52_48_feasibility_proxy/
```

Migrate and replace any existing lazy wrapper with real implementation:

```text
src/runtime_geometry_wall_velocity_48_feasibility_config.py
  -> experiments/steps/step52_48_feasibility_proxy/config.py

src/runtime_geometry_wall_velocity_48_feasibility_diagnostics.py
  -> experiments/steps/step52_48_feasibility_proxy/diagnostics.py

src/runtime_geometry_wall_velocity_48_feasibility_envelope.py
  -> experiments/steps/step52_48_feasibility_proxy/envelope.py

src/runtime_geometry_wall_velocity_48_feasibility_state_guard.py
  -> experiments/steps/step52_48_feasibility_proxy/state_guard.py
```

Acceptance:

```text
experiments/steps/step52_48_feasibility_proxy/envelope.py contains real implementation
no legacy_getattr in experiment implementation
canonical experiment files do not import root src.runtime_geometry_wall_velocity_48_feasibility_*
root Step52 files are thin shims
```

### I. Step53 Support-Scaling Audit Package

Target package:

```text
experiments/steps/step53_support_scaling_audit/
```

Migrate:

```text
src/runtime_geometry_wall_velocity_support_scaling_config.py
  -> experiments/steps/step53_support_scaling_audit/config.py

src/runtime_geometry_wall_velocity_support_scaling_audit.py
  -> experiments/steps/step53_support_scaling_audit/audit.py

src/runtime_geometry_wall_velocity_support_scaling_diagnostics.py
  -> experiments/steps/step53_support_scaling_audit/diagnostics.py

src/runtime_geometry_wall_velocity_support_scaling_claim_guard.py
  -> experiments/steps/step53_support_scaling_audit/claim_guard.py

src/runtime_geometry_wall_velocity_support_scaling_artifact_guard.py
  -> experiments/steps/step53_support_scaling_audit/artifact_guard.py
```

## Required Configs

```text
configs/step68_step_specific_proxy_migration_policy.json
configs/step68_import_execution_policy.json
configs/step68_legacy_shim_policy.json
configs/step68_experiment_boundary_policy.json
configs/step68_step63_67_regression_policy.json
```

`step68_step_specific_proxy_migration_policy.json` must be derived from or checked against the Step63 inventory artifact:

```text
outputs/step63_remaining_solver_inventory_audit/audit.json
```

The policy must include:

```text
policy_id
step
batch/base_commit
runtime_code_changed = false
solver_behavior_changed = false
physics_feature_expansion = false
inventory_source
expected_inventory_count
migrations[]
```

Each migration row must include:

```text
legacy_path
experiment_path
legacy_module
experiment_module
package
classification
public_symbols
required_tokens
source_inventory_classification
root_shim_required
simulation_required_for_migration = false
```

## Required Evidence Modules

Add:

```text
src/mpm_lbm/evidence/step_specific_proxy_policy_audit.py
src/mpm_lbm/evidence/step_specific_proxy_migration_audit.py
src/mpm_lbm/evidence/step_specific_proxy_import_execution_audit.py
src/mpm_lbm/evidence/step_specific_proxy_legacy_shim_audit.py
src/mpm_lbm/evidence/experiment_boundary_audit.py
src/mpm_lbm/evidence/step68_regression_guard.py
```

### `step_specific_proxy_policy_audit.py`

Purpose:

```text
Compare Step68 migration policy against Step63 inventory.
```

Required checks:

```text
policy_migration_count == Step63 inventory step_specific_proxy_remaining_count
missing_inventory_paths == []
extra_policy_paths == []
all policy paths have target_owner == experiments/steps in inventory
all policy paths have recommended_step == Step68 in inventory
```

Required summary:

```text
step68_proxy_policy_audit_pass
inventory_step_specific_proxy_remaining_count
policy_migration_count
missing_inventory_path_count
extra_policy_path_count
```

### `step_specific_proxy_migration_audit.py`

Purpose:

```text
Check migrated experiment implementation ownership.
```

Required row fields:

```text
legacy_path
experiment_path
legacy_file_exists
experiment_file_exists
experiment_contains_real_implementation
experiment_uses_legacy_getattr
experiment_imports_root_proxy
legacy_is_shim
legacy_imports_experiment
pass
```

Required summary:

```text
step68_proxy_migration_audit_pass
experiment_real_implementation_count
experiment_legacy_getattr_count
experiment_root_proxy_import_count
legacy_shim_count
```

### `step_specific_proxy_import_execution_audit.py`

Purpose:

```text
Import all public symbols from experiment modules and legacy root shims and compare object identity.
```

Required row fields:

```text
symbol
experiment_module
legacy_module
experiment_import_pass
legacy_import_pass
same_object
pass
error
```

Required summary:

```text
step68_import_execution_audit_pass
symbol_count
experiment_import_pass_count
legacy_import_pass_count
same_object_count
output_snapshot_unchanged
solver_run = false
```

### `step_specific_proxy_legacy_shim_audit.py`

Purpose:

```text
Ensure migrated root files no longer contain implementation bodies.
```

Required row fields:

```text
legacy_path
experiment_path
legacy_is_shim
legacy_imports_experiment
legacy_contains_implementation_body
nonblank_line_count
pass
```

Required summary:

```text
step68_legacy_shim_audit_pass
legacy_shim_count
legacy_implementation_body_count
```

### `experiment_boundary_audit.py`

Purpose:

```text
Prove Step68 experiment packages do not execute simulations or violate placement/protected-directory boundaries.
```

Required checks:

```text
No FSIDriver3D(...).run() in Step68 runners/tests/evidence
No driver.run() in Step68 runners/tests/evidence
No driver.initialize() in Step68 runners/tests/evidence
No driver.step_once() in Step68 runners/tests/evidence
quarantined real_geometry_feasibility driver helper is not executed
No outputs/step68_driver_runs
No VTR
No particle NPY
No external/taichi_LBM3D edit
No data/real_geometry_candidates edit
real_geometry_feasibility not under src/mpm_lbm/sim
runtime solver code not placed under experiments/steps
```

Required summary:

```text
experiment_boundary_audit_pass
driver_run_call_count
driver_initialize_call_count
driver_step_once_call_count
quarantined_driver_helper_count
step68_driver_run_output_dir_count
step68_vtr_count
step68_particle_npy_count
protected_external_edit_count
protected_real_geometry_candidate_edit_count
```

### `step68_regression_guard.py`

Purpose:

```text
Prove Step63-67 Batch A evidence remains green after Step68 migration.
```

Required source artifacts:

```text
outputs/step63_simulation_freeze_audit/audit.json
outputs/step63_remaining_solver_inventory_audit/audit.json
outputs/step64_motion_wall_velocity_migration_audit/audit.json
outputs/step65_runtime_geometry_migration_audit/audit.json
outputs/step66_diagnostic_geometry_displacement_migration_audit/audit.json
outputs/step67_squid_proxy_real_geometry_migration_audit/audit.json
outputs/step63_67_step62_regression_guard/audit.json
outputs/step63_67_artifact_manifest/artifact_summary.json
```

Required summary:

```text
step68_regression_guard_pass
step63_67_required_artifact_count
step63_67_pass_count
volatile_size_snapshot_embedded = false
```

## Required Runners

Add:

```text
baseline_tests/step68_common.py
baseline_tests/run_step68_step_specific_proxy_policy_audit.py
baseline_tests/run_step68_step_specific_proxy_migration_audit.py
baseline_tests/run_step68_import_execution_audit.py
baseline_tests/run_step68_legacy_shim_audit.py
baseline_tests/run_step68_experiment_boundary_audit.py
baseline_tests/run_step68_step63_67_regression_guard.py
baseline_tests/run_step68_artifact_manifest.py
```

Runners must:

```text
run from repo root
write CSV rows
write CSV summary
write JSON artifact
write log marker
raise RuntimeError if the pass key is false
not call driver.run or any simulation step
```

## Required Tests

Add:

```text
tests/test_step68_step_specific_proxy_policy_contract.py
tests/test_step68_step_specific_proxy_migration_contract.py
tests/test_step68_import_execution_contract.py
tests/test_step68_legacy_shim_contract.py
tests/test_step68_experiment_boundary_contract.py
tests/test_step68_step63_67_regression_contract.py
```

Each test must check:

```text
the build_* function returns pass
the committed output artifact returns pass
required nonzero row/symbol counts are present
the relevant no-driver/no-output boundary counters are zero
```

## Required Outputs

Generate:

```text
outputs/step68_step_specific_proxy_policy_audit/
outputs/step68_step_specific_proxy_migration_audit/
outputs/step68_import_execution_audit/
outputs/step68_legacy_shim_audit/
outputs/step68_experiment_boundary_audit/
outputs/step68_step63_67_regression_guard/
outputs/step68_artifact_manifest/
logs/step68_*.log
```

## Required Report

Add:

```text
STEP68_STEP_SPECIFIC_PROXY_MIGRATION_TO_EXPERIMENTS_REPORT.md
```

The report must state:

```text
base commit
policy migration count
inventory count
all migration groups
that root files became shims
that experiment packages own real implementation
that Step68 did not run new simulations
that protected directories remained clean
that Step63-67 regression remained green
verification commands and pass counts
artifact manifest summary
commit hash after commit
```

Do not claim:

```text
new physics validation
runtime geometry activation
wall velocity activation
real squid validation
real geometry feasibility execution
production readiness
```

## Required Documentation

Add:

```text
docs/68_step_specific_proxy_migration_to_experiments.md
```

Update README if needed so the implemented list and Step boundary text acknowledge Step68 without overstating scope.

README wording must preserve:

```text
engineering prototype
not production ready
not real squid validation
not final sharp-interface FSI
```

## Artifact Manifest Requirements

`outputs/step68_artifact_manifest/artifact_summary.json` must prove:

```text
artifact_budget_pass = true
step68_driver_run_output_dir_count = 0
step68_vtr_count = 0
step68_particle_npy_count = 0
protected_external_taichi_lbm3d_step68_file_count = 0
protected_real_geometry_candidates_step68_file_count = 0
large_file_count = 0
```

## Verification Commands

Run Step68 audits:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step68_step_specific_proxy_policy_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step68_step_specific_proxy_migration_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step68_import_execution_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step68_legacy_shim_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step68_experiment_boundary_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step68_step63_67_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step68_artifact_manifest.py
```

Run focused Step68 tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest `
  tests\test_step68_step_specific_proxy_policy_contract.py `
  tests\test_step68_step_specific_proxy_migration_contract.py `
  tests\test_step68_import_execution_contract.py `
  tests\test_step68_legacy_shim_contract.py `
  tests\test_step68_experiment_boundary_contract.py `
  tests\test_step68_step63_67_regression_contract.py `
  -q
```

Run full tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q
& 'D:\TOOL\Anaconda\python.exe' -W ignore -m pytest -q
```

Run git/protection checks:

```powershell
git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Commit and push:

```powershell
git add .
git diff --cached --check
git commit -m "test: add step68 step-specific proxy migration"
git push origin main
```

## Final Acceptance Criteria

Step68 is complete only when all are true:

```text
STEP68_STEP_SPECIFIC_PROXY_MIGRATION_TO_EXPERIMENTS_GOAL.md exists
STEP68_STEP_SPECIFIC_PROXY_MIGRATION_TO_EXPERIMENTS_REPORT.md exists
docs/68_step_specific_proxy_migration_to_experiments.md exists

policy_migration_count == Step63 inventory step_specific_proxy_remaining_count
policy_migration_count == 34
missing_inventory_paths == []
extra_policy_paths == []

all step_specific_proxy_remaining files moved to experiments/steps
root src step-specific implementation count == 0
all migrated root files are thin shims
experiment files contain real implementation
experiment files do not use legacy_getattr
experiment files do not import root src.runtime_geometry_wall_velocity_* modules
legacy imports still work
experiment imports work
same_object_count == public_symbol_count

experiment_boundary_audit_pass == true
driver_run_call_count == 0
driver_initialize_call_count == 0
driver_step_once_call_count == 0
quarantined_driver_helper_count is reported
step68_driver_run_output_dir_count == 0
step68_vtr_count == 0
step68_particle_npy_count == 0
protected_external_edit_count == 0
protected_real_geometry_candidate_edit_count == 0

Step63-67 regression guard passes
Step68 artifact manifest passes
focused Step68 pytest passes
full pytest passes under D:\working\taichi\env\python.exe
full pytest passes under D:\TOOL\Anaconda\python.exe
pre-push hook passes
git diff --check passes
push to origin/main succeeds
```

## Deferred Work

Step69 remains separate:

```text
Root src final implementation cleanup
Migrate or explicitly approve the six migration-required support rows:
src/squid_region_driver_diagnostics.py
src/squid_region_projection.py
src/squid_region_quality.py
src/wall_velocity_application_envelope.py
src/wall_velocity_consistency.py
src/wall_velocity_quality.py
```

Step70 remains separate:

```text
API and config freeze before activation
```
