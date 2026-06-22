# Step75 Solver-Complete Simulation Campaign Readiness Gate Goal

## Repository And Baseline

Repository root:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Accepted baseline before Step75:

```text
origin/main = 19ce67838923197046763bc77a8468d2de5d2535
test: add step74 real geometry data boundary audit
```

Step75 assumes Step74 is accepted and retained. If Step74 were not intended, the
workflow must stop before Step75. This goal treats Step74 as the current
accepted upstream state.

## Step Name

```text
Step75 Solver-Complete Simulation Campaign Readiness Gate
```

Required commit message:

```text
test: add step75 solver complete readiness gate
```

## Core Objective

Step75 is a gate step. It is not a simulation step.

Step75 must aggregate the accepted Step71, Step72, Step73, and Step74 committed
evidence and decide whether the repository is ready for a later Step76 minimal
post-gate canonical-driver rebaseline. It may allow a later baseline simulation
campaign in principle, but Step75 itself must not run any simulation and must not
open any advanced activation feature.

Step75 must answer:

1. Output defaults are safe and explicit opt-in still exists.
2. Tau convention is decided and frozen for now.
3. Runtime geometry readiness is green, while activation remains closed.
4. Wall velocity readiness is green, while activation remains closed.
5. Real geometry data boundary is green, while activation remains closed.
6. All 10 Step70 activation gates remain closed.
7. Step76 may be planned as a minimal safe rebaseline only.
8. Step76's first campaign must not enable runtime geometry, wall velocity, real
   geometry, squid proxy, VTR output, particle NPY output, 48^3, 64^3, or long
   duration.

The accepted gate status is:

```text
ready_for_step76_rebaseline_only
```

The accepted next-step claim is:

```text
Step76 may run a minimal safe canonical-driver rebaseline only.
```

Step75 must not claim:

```text
ready_for_full_target_simulation
ready_for_real_geometry
ready_for_runtime_geometry_wall_velocity_combined
production_ready
physical_validation_complete
grid_convergence_complete
real_squid_validation_complete
```

## Explicit Non-Goals And Forbidden Actions

Step75 must not execute, add, enable, or imply any of the following:

```text
driver.run()
FSIDriver3D(...).run()
driver.initialize()
driver.step_once()
outputs/step75_driver_runs
runtime geometry activation
wall velocity activation
combined activation
real geometry run
real geometry activation
squid simulation
squid proxy activation
48^3 run
64^3 run
VTR output
particle NPY output
new raw geometry data
new data/real_geometry_candidates content
external/taichi_LBM3D edits
data/real_geometry_candidates edits
tau formula migration
LBM formula changes
MPM formula changes
projection formula changes
moving bounce-back formula changes
physical validation claim
grid convergence claim
production readiness claim
real squid validation claim
```

Step75 may:

```text
read committed Step71-74 artifacts
read activation policies
import lightweight public APIs if needed
generate readiness summaries
generate inactive Step76 campaign policy proposals
generate no-simulation guards
generate output/artifact policy guards
generate artifact manifest
update docs and README
commit and push the audit-only evidence
```

## Required Config Files

Add these checked-in policy files:

```text
configs/step75_solver_complete_gate_policy.json
configs/step75_precondition_artifact_policy.json
configs/step75_activation_gate_policy.json
configs/step75_post_gate_campaign_policy.json
configs/step75_no_simulation_policy.json
configs/step75_output_artifact_policy.json
configs/step75_step74_regression_policy.json
```

The configs must make the Step75 contract explicit: artifact paths, summary
keys, activation gates, allowed Step76 campaign proposal rows, forbidden campaign
items, protected prefixes, and output policies should be checked from committed
policy data rather than hidden in tests.

## Required Evidence Modules

Add these modules:

```text
src/mpm_lbm/evidence/solver_complete_gate_audit.py
src/mpm_lbm/evidence/precondition_artifact_audit.py
src/mpm_lbm/evidence/activation_gate_closure_audit.py
src/mpm_lbm/evidence/post_gate_campaign_policy_audit.py
src/mpm_lbm/evidence/step75_no_simulation_audit.py
src/mpm_lbm/evidence/step75_output_artifact_policy_audit.py
src/mpm_lbm/evidence/step75_regression_guard.py
```

These evidence modules must be audit-only. They must not construct a driver, run
a driver, initialize a driver, step a driver, mutate solver state, or write
outside Step75 output/log/report paths.

## Required Baseline Runners

Add these thin runners:

```text
baseline_tests/step75_common.py
baseline_tests/run_step75_precondition_artifact_audit.py
baseline_tests/run_step75_activation_gate_closure_audit.py
baseline_tests/run_step75_post_gate_campaign_policy_audit.py
baseline_tests/run_step75_solver_complete_gate_audit.py
baseline_tests/run_step75_no_simulation_audit.py
baseline_tests/run_step75_output_artifact_policy_audit.py
baseline_tests/run_step75_step74_regression_guard.py
baseline_tests/run_step75_artifact_manifest.py
```

Each runner must write CSV, JSON, and log evidence in the existing Step pattern.

## Required Tests

Add focused contract tests:

```text
tests/test_step75_precondition_artifact_contract.py
tests/test_step75_activation_gate_closure_contract.py
tests/test_step75_post_gate_campaign_policy_contract.py
tests/test_step75_solver_complete_gate_contract.py
tests/test_step75_no_simulation_contract.py
tests/test_step75_output_artifact_policy_contract.py
tests/test_step75_step74_regression_contract.py
```

The tests must verify both direct builder output and committed artifact output.
They should avoid importing the full runtime package in a way that makes the
pre-push hook fragile.

## Required Docs And Report

Add:

```text
STEP75_SOLVER_COMPLETE_SIMULATION_CAMPAIGN_READINESS_GATE_REPORT.md
docs/75_solver_complete_simulation_campaign_readiness_gate.md
docs/SOLVER_COMPLETE_READINESS_GATE.md
docs/POST_GATE_SIMULATION_CAMPAIGN_PLAN.md
```

Update:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
```

Docs must say:

```text
Step75 is a gate-only audit
Step75 does not run FSIDriver3D
Step75 does not open any Step70 activation gate
Step75 allows only Step76 minimal safe rebaseline planning
Step76 first campaign must keep advanced activation features disabled
Step75 is not physical validation, real squid validation, grid convergence, or production readiness
```

## Required Outputs And Logs

Generate and commit:

```text
outputs/step75_precondition_artifact_audit/
outputs/step75_activation_gate_closure_audit/
outputs/step75_post_gate_campaign_policy_audit/
outputs/step75_solver_complete_gate_audit/
outputs/step75_no_simulation_audit/
outputs/step75_output_artifact_policy_audit/
outputs/step75_step74_regression_guard/
outputs/step75_artifact_manifest/
logs/step75_*.log
```

The artifact manifest must prove Step75 stays small and contains no forbidden
driver-run directories, VTR output, particle NPY output, large files, private
absolute paths, protected external edits, or protected real-geometry candidate
edits.

## Phase 1: Precondition Artifact Audit

Read committed Step71-74 artifacts and verify they are present and green.

Step71 required artifacts:

```text
outputs/step71_output_default_alignment_audit/output_default_alignment.json
outputs/step71_tau_convention_decision_audit/tau_convention_decision.json
outputs/step71_config_schema_delta_audit/config_schema_delta.json
outputs/step71_no_simulation_audit/no_simulation.json
outputs/step71_step70_regression_guard/step70_regression_guard.json
outputs/step71_artifact_manifest/artifact_summary.json
```

Step72 required artifacts:

```text
outputs/step72_runtime_geometry_readiness_audit/runtime_geometry_readiness.json
outputs/step72_runtime_geometry_api_audit/runtime_geometry_api.json
outputs/step72_runtime_geometry_config_schema_audit/runtime_geometry_config_schema.json
outputs/step72_runtime_geometry_driver_gate_audit/runtime_geometry_driver_gate.json
outputs/step72_runtime_geometry_state_guard_audit/runtime_geometry_state_guard.json
outputs/step72_runtime_geometry_output_policy_audit/runtime_geometry_output_policy.json
outputs/step72_no_simulation_audit/no_simulation.json
outputs/step72_step71_regression_guard/step71_regression_guard.json
outputs/step72_artifact_manifest/artifact_summary.json
```

Step73 required artifacts:

```text
outputs/step73_wall_velocity_readiness_audit/wall_velocity_readiness.json
outputs/step73_wall_velocity_api_audit/wall_velocity_api.json
outputs/step73_wall_velocity_config_schema_audit/wall_velocity_config_schema.json
outputs/step73_wall_velocity_driver_gate_audit/wall_velocity_driver_gate.json
outputs/step73_wall_velocity_application_safety_audit/wall_velocity_application_safety.json
outputs/step73_wall_velocity_output_policy_audit/wall_velocity_output_policy.json
outputs/step73_full_activation_gate_coverage_audit/full_activation_gate_coverage.json
outputs/step73_no_simulation_audit/no_simulation.json
outputs/step73_step72_regression_guard/step72_regression_guard.json
outputs/step73_artifact_manifest/artifact_summary.json
```

Step74 required artifacts:

```text
outputs/step74_real_geometry_data_boundary_audit/real_geometry_data_boundary.json
outputs/step74_real_geometry_api_audit/real_geometry_api.json
outputs/step74_candidate_descriptor_schema_audit/candidate_descriptor_schema.json
outputs/step74_candidate_manifest_policy_audit/candidate_manifest_policy.json
outputs/step74_real_geometry_quarantine_audit/real_geometry_quarantine.json
outputs/step74_real_geometry_output_policy_audit/real_geometry_output_policy.json
outputs/step74_full_activation_gate_coverage_audit/full_activation_gate_coverage.json
outputs/step74_no_simulation_audit/no_simulation.json
outputs/step74_step73_regression_guard/step73_regression_guard.json
outputs/step74_artifact_manifest/artifact_summary.json
```

Required summary:

```text
precondition_artifact_audit_pass = true
required_artifact_count = 35
present_artifact_count = 35
green_artifact_count = 35
missing_artifact_count = 0
failed_artifact_count = 0
step71_pass = true
step72_pass = true
step73_pass = true
step74_pass = true
```

Step71 must additionally confirm:

```text
fsidriver_default_write_vtk = false
fsidriver_default_write_particles = false
explicit opt-in remains allowed
tau_convention_decision = preserve_legacy_external_solver_parameter_for_now
default_solver_tau_formula = tau_from_legacy_external_solver_parameter
standard_lattice_viscosity_is_default = false
physical_viscosity_validation_claim = false
future_standard_tau_migration_requires_baseline_rerun = true
```

## Phase 2: Activation Gate Closure Audit

Read `configs/step70_activation_preconditions_policy.json` and require all 10
activation gates to remain closed:

```text
runtime_geometry_activation_allowed
wall_velocity_activation_allowed
combined_runtime_geometry_wall_velocity_activation_allowed
real_geometry_activation_allowed
squid_proxy_activation_allowed
link_area_activation_allowed
grid_48_activation_allowed
grid_64_activation_allowed
vtr_output_allowed
particle_npy_output_allowed
```

Required summary:

```text
activation_gate_closure_audit_pass = true
required_gate_count = 10
closed_gate_count = 10
activation_allowed_count = 0
gate_source_policy = configs/step70_activation_preconditions_policy.json
latest_step_checked = Step74
```

## Phase 3: Post-Gate Campaign Policy Audit

Generate an inactive Step76 campaign proposal. This is a policy artifact only,
not an executable run config and not a simulation.

Recommended allowed campaign:

```text
campaign_id = step76_minimal_post_gate_real_driver_rebaseline
row_1 = canonical_driver_moving_boundary_engineering_32_1step_rebaseline
row_2 = canonical_driver_moving_boundary_engineering_32_3step_rebaseline_optional
```

Required campaign defaults:

```text
run_optional_32_3step = false
runtime_geometry_enabled = false
wall_velocity_enabled = false
real_geometry_enabled = false
squid_proxy_enabled = false
write_vtk = false
write_particles = false
```

Forbidden Step76 campaign items:

```text
runtime geometry plus wall velocity combined
real geometry candidate
squid motion
48^3
64^3
VTR
particle NPY
required link_area row
long duration
```

Required summary:

```text
post_gate_campaign_policy_audit_pass = true
allowed_campaign_count >= 1
forbidden_campaign_count >= 1
first_campaign_is_rebaseline_only = true
activation_feature_count_in_first_campaign = 0
runtime_geometry_enabled = false
wall_velocity_enabled = false
real_geometry_enabled = false
squid_proxy_enabled = false
write_vtk = false
write_particles = false
```

## Phase 4: Solver-Complete Gate Audit

Aggregate the Step75 evidence into one gate decision.

Required decision:

```text
solver_complete_gate_audit_pass = true
gate_status = ready_for_step76_rebaseline_only
post_gate_simulation_allowed = true
allowed_next_step = Step76
allowed_next_step_scope = minimal safe rebaseline only
activation_features_allowed_in_next_step = []
runtime_geometry_activation_allowed = false
wall_velocity_activation_allowed = false
real_geometry_activation_allowed = false
squid_proxy_activation_allowed = false
vtr_output_allowed = false
particle_npy_output_allowed = false
production_readiness_claim = false
physical_validation_claim = false
```

This resolves the intended nuance: Step75 may allow Step76 to run a minimal
baseline simulation again, but it does not open runtime geometry, wall velocity,
real geometry, squid proxy, VTR, or particle persistence.

## Phase 5: No-Simulation Audit

Scan Step75 executable files for:

```text
driver.run(
FSIDriver3D(...).run(
driver.initialize(
driver.step_once(
outputs/step75_driver_runs
write_vtk=True
write_particles=True
```

Required summary:

```text
no_simulation_audit_pass = true
forbidden_python_call_count = 0
forbidden_output_directory_count = 0
step75_vtr_count = 0
step75_particle_npy_count = 0
protected_step75_file_count = 0
```

## Phase 6: Output And Artifact Policy Audit

Required checks:

```text
no outputs/step75_driver_runs
no VTR
no particle NPY
no large files
no private absolute paths
no protected external edits
no protected real geometry candidate edits
artifact manifest required
report consistency required
```

Required summary:

```text
output_artifact_policy_audit_pass = true
large_file_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
step75_driver_run_output_dir_count = 0
step75_vtr_count = 0
step75_particle_npy_count = 0
```

## Phase 7: Step74 Regression Guard

Confirm Step74 remains green:

```text
Step74 real geometry data boundary pass
Step74 real geometry API pass
Step74 candidate descriptor schema pass
Step74 candidate manifest policy pass
Step74 quarantine pass
Step74 output policy pass
Step74 full activation gate coverage pass
Step74 no simulation pass
Step74 Step73 regression pass
Step74 artifact manifest pass
```

Required summary:

```text
step75_step74_regression_guard_pass = true
step74_artifact_check_count = 10
step74_artifact_pass_count = 10
closed_gate_pass_count = required_closed_gate_count
```

## Acceptance Criteria

Step75 is complete only when all pass:

```text
Step75 goal/report/docs exist

Preconditions:
  precondition_artifact_audit_pass == true
  step71_pass == true
  step72_pass == true
  step73_pass == true
  step74_pass == true
  missing_artifact_count == 0
  failed_artifact_count == 0

Activation gates:
  activation_gate_closure_audit_pass == true
  required_gate_count == 10
  closed_gate_count == 10
  activation_allowed_count == 0

Post-gate campaign policy:
  post_gate_campaign_policy_audit_pass == true
  first_campaign_is_rebaseline_only == true
  activation_feature_count_in_first_campaign == 0
  runtime_geometry_enabled == false
  wall_velocity_enabled == false
  real_geometry_enabled == false
  squid_proxy_enabled == false
  write_vtk == false
  write_particles == false

Solver-complete gate:
  solver_complete_gate_audit_pass == true
  gate_status == ready_for_step76_rebaseline_only
  post_gate_simulation_allowed == true
  allowed_next_step == Step76
  allowed_next_step_scope == minimal safe rebaseline only
  production_readiness_claim == false
  physical_validation_claim == false

No simulation in Step75:
  no_simulation_audit_pass == true
  no driver.run
  no FSIDriver3D(...).run
  no driver.initialize
  no driver.step_once
  no outputs/step75_driver_runs
  no VTR
  no particle NPY

Output/artifact:
  output_artifact_policy_audit_pass == true
  artifact_budget_pass == true
  large_file_count == 0
  private_absolute_path_count == 0
  protected_external_edit_count == 0
  protected_real_geometry_candidate_edit_count == 0

Regression:
  Step74 regression guard passes
  artifact manifest passes

Validation:
  focused Step75 pytest passes
  full pytest passes under D:\working\taichi\env\python.exe
  full pytest passes under D:\TOOL\Anaconda\python.exe when accessible
  pre-push hook passes
  git diff --check passes
  external/taichi_LBM3D clean
  data/real_geometry_candidates clean
```

## Verification Commands

Compile:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\evidence\solver_complete_gate_audit.py `
  src\mpm_lbm\evidence\precondition_artifact_audit.py `
  src\mpm_lbm\evidence\activation_gate_closure_audit.py `
  src\mpm_lbm\evidence\post_gate_campaign_policy_audit.py `
  src\mpm_lbm\evidence\step75_no_simulation_audit.py `
  src\mpm_lbm\evidence\step75_output_artifact_policy_audit.py `
  src\mpm_lbm\evidence\step75_regression_guard.py `
  baseline_tests\step75_common.py `
  baseline_tests\run_step75_precondition_artifact_audit.py `
  baseline_tests\run_step75_activation_gate_closure_audit.py `
  baseline_tests\run_step75_post_gate_campaign_policy_audit.py `
  baseline_tests\run_step75_solver_complete_gate_audit.py `
  baseline_tests\run_step75_no_simulation_audit.py `
  baseline_tests\run_step75_output_artifact_policy_audit.py `
  baseline_tests\run_step75_step74_regression_guard.py `
  baseline_tests\run_step75_artifact_manifest.py `
  tests\test_step75_precondition_artifact_contract.py `
  tests\test_step75_activation_gate_closure_contract.py `
  tests\test_step75_post_gate_campaign_policy_contract.py `
  tests\test_step75_solver_complete_gate_contract.py `
  tests\test_step75_no_simulation_contract.py `
  tests\test_step75_output_artifact_policy_contract.py `
  tests\test_step75_step74_regression_contract.py
```

Run audits:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step75_precondition_artifact_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step75_activation_gate_closure_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step75_post_gate_campaign_policy_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step75_solver_complete_gate_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step75_no_simulation_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step75_output_artifact_policy_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step75_step74_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step75_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest `
  tests\test_step75_precondition_artifact_contract.py `
  tests\test_step75_activation_gate_closure_contract.py `
  tests\test_step75_post_gate_campaign_policy_contract.py `
  tests\test_step75_solver_complete_gate_contract.py `
  tests\test_step75_no_simulation_contract.py `
  tests\test_step75_output_artifact_policy_contract.py `
  tests\test_step75_step74_regression_contract.py `
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

Commit and push:

```powershell
git status --short
git add <Step75 files>
git diff --cached --check
git commit -m "test: add step75 solver complete readiness gate"
git fetch origin main
git push origin main
```

## Step76 Reserved Direction

If Step75 passes, Step76 may be:

```text
Step76 Minimal Post-Gate Canonical Driver Rebaseline
```

The first Step76 row should be:

```text
canonical_driver_moving_boundary_engineering_32_1step_rebaseline
```

Required Step76 feature defaults:

```text
runtime_geometry_enabled = false
wall_velocity_enabled = false
real_geometry_enabled = false
squid_proxy_enabled = false
write_vtk = false
write_particles = false
```

Step76 should rebaseline post-freeze safe defaults and canonical public API
before opening any single advanced activation feature gate.
