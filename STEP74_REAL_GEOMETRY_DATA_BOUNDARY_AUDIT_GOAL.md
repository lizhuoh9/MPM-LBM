# Step74 Real Geometry Data Boundary Audit Goal

## Repository And Baseline

Repository root:

```text
D:\working\squid robot\LBM\MPM-LBM
```

Current accepted baseline before Step74:

```text
origin/main = 75e5bbaf66bc6861628868dbfe6c2eacb97c25d4
test: add step73 wall velocity activation readiness audit
```

Step73 is accepted as an audit-only readiness layer. Runtime geometry activation,
wall velocity activation, combined activation, real geometry activation, squid
proxy activation, link-area activation, 48^3 activation, 64^3 activation, VTR
output, and particle NPY output all remain closed. Step74 must preserve that
state.

## Step Name

```text
Step74 Real Geometry Data Boundary Audit
```

Required commit message:

```text
test: add step74 real geometry data boundary audit
```

## Core Objective

Step74 adds a real geometry data boundary audit. It is not real geometry
activation, not a driver run, not a projection smoke execution, and not physical
validation. It answers only these boundary questions:

1. The canonical real geometry support API can be imported without running a
   solver or writing outputs.
2. Candidate descriptors, manifests, fingerprints, and normalization policy keep
   safe commit boundaries.
3. `data/real_geometry_candidates` remains protected and unchanged.
4. No raw scan data, large files, VTR outputs, particle NPY outputs, private
   absolute paths, or protected external edits are introduced.
5. `experiments.steps.real_geometry_feasibility` remains a quarantined
   experiment helper and is not promoted into runtime solver API.
6. `real_geometry_activation_allowed` and every other Step70 activation gate
   remain closed.

The accepted final Step74 claim is:

```text
real_geometry_boundary_audit_ready_for_later_data_decision_only
```

Step74 must not claim solver completion, production readiness, real squid
validation, real squid geometry readiness, jet validation, swimming validation,
grid convergence, or physical validation.

## Explicit Non-Goals And Forbidden Actions

Do not execute, add, enable, or imply any of the following:

```text
driver.run()
FSIDriver3D(...).run()
driver.initialize()
driver.step_once()
outputs/step74_driver_runs
real geometry run
real geometry activation
runtime geometry activation
wall velocity activation
combined activation
squid simulation
48^3 simulation
64^3 simulation
VTR output
particle NPY output
new raw geometry data
new real geometry candidate data
external/taichi_LBM3D edits
data/real_geometry_candidates edits
private absolute path commits
large raw scan files
LBM formula changes
MPM formula changes
projector formula changes
moving bounce-back formula changes
tau convention migration
physics validation claim
real squid validation claim
grid convergence claim
production readiness claim
```

Step74 may import symbols, inspect source text, validate synthetic in-memory
descriptors, create small JSON/CSV/log audit artifacts, and optionally create
small synthetic fixtures only under Step74-controlled output paths. It must not
place new files under `data/real_geometry_candidates`.

## Real Geometry Support Surface

Step74 must audit the canonical real geometry support surface:

```text
src/mpm_lbm/sim/geometry/intake.py
src/mpm_lbm/sim/geometry/candidate_manifest.py
src/mpm_lbm/sim/geometry/fingerprint.py
src/mpm_lbm/sim/geometry/normalization.py
experiments/steps/real_geometry_feasibility/feasibility.py
```

`src/mpm_lbm/sim/geometry/intake.py` contains
`run_candidate_projection_smoke()`. That helper imports Taichi, LBM, MPM, and the
projector, creates output files, and performs a projection smoke path. Step74 may
confirm that this symbol exists, but must not call it. Any execution of
projection smoke must remain reserved for a later explicitly authorized
post-gate step.

`experiments/steps/real_geometry_feasibility/feasibility.py` contains
driver-related historical feasibility helpers. Step74 must keep this code
quarantined under `experiments/steps` and must not execute driver helpers from
that module.

## Required Config Files

Add these checked-in policy files:

```text
configs/step74_real_geometry_data_boundary_policy.json
configs/step74_real_geometry_api_policy.json
configs/step74_candidate_descriptor_schema_policy.json
configs/step74_candidate_manifest_policy.json
configs/step74_real_geometry_quarantine_policy.json
configs/step74_real_geometry_output_policy.json
configs/step74_full_activation_gate_coverage_policy.json
configs/step74_no_simulation_policy.json
configs/step74_step73_regression_policy.json
```

The configs must be explicit enough that the tests and runners derive their
expected symbols, gates, protected prefixes, forbidden paths, invalid descriptor
cases, and regression artifacts from checked-in policy rather than hidden test
assumptions.

## Required Evidence Modules

Add these modules:

```text
src/mpm_lbm/evidence/real_geometry_data_boundary_audit.py
src/mpm_lbm/evidence/real_geometry_api_audit.py
src/mpm_lbm/evidence/candidate_descriptor_schema_audit.py
src/mpm_lbm/evidence/candidate_manifest_policy_audit.py
src/mpm_lbm/evidence/real_geometry_quarantine_audit.py
src/mpm_lbm/evidence/real_geometry_output_policy_audit.py
src/mpm_lbm/evidence/step74_full_activation_gate_coverage_audit.py
src/mpm_lbm/evidence/step74_no_simulation_audit.py
src/mpm_lbm/evidence/step74_regression_guard.py
```

The evidence modules must be audit-only. They must not run a driver, initialize a
driver, step a driver, execute projection smoke, mutate solver state, or write
outside their Step74 artifact/log paths.

## Required Baseline Runners

Add these thin runners:

```text
baseline_tests/step74_common.py
baseline_tests/run_step74_real_geometry_api_audit.py
baseline_tests/run_step74_candidate_descriptor_schema_audit.py
baseline_tests/run_step74_candidate_manifest_policy_audit.py
baseline_tests/run_step74_real_geometry_quarantine_audit.py
baseline_tests/run_step74_real_geometry_output_policy_audit.py
baseline_tests/run_step74_full_activation_gate_coverage_audit.py
baseline_tests/run_step74_real_geometry_data_boundary_audit.py
baseline_tests/run_step74_no_simulation_audit.py
baseline_tests/run_step74_step73_regression_guard.py
baseline_tests/run_step74_artifact_manifest.py
```

Each runner must write CSV, JSON, and log evidence in the existing Step pattern.

## Required Tests

Add focused contract tests:

```text
tests/test_step74_real_geometry_api_contract.py
tests/test_step74_candidate_descriptor_schema_contract.py
tests/test_step74_candidate_manifest_policy_contract.py
tests/test_step74_real_geometry_quarantine_contract.py
tests/test_step74_real_geometry_output_policy_contract.py
tests/test_step74_full_activation_gate_coverage_contract.py
tests/test_step74_real_geometry_data_boundary_contract.py
tests/test_step74_no_simulation_contract.py
tests/test_step74_step73_regression_contract.py
```

The tests must verify committed artifacts and the audit functions. They should
avoid importing the full package in ways that make pre-push hooks fragile.

## Required Docs And Report

Add:

```text
STEP74_REAL_GEOMETRY_DATA_BOUNDARY_AUDIT_REPORT.md
docs/74_real_geometry_data_boundary_audit.md
docs/REAL_GEOMETRY_DATA_BOUNDARY.md
docs/REAL_GEOMETRY_CANDIDATE_POLICY.md
```

Update:

```text
README.md
docs/00_project_status.md
docs/ACTIVATION_PRECONDITIONS.md
```

The docs must clearly state:

```text
real_geometry_activation_allowed remains false
data/real_geometry_candidates remains protected
no real geometry data was added
real_geometry_feasibility remains quarantined experiment code
Step74 does not execute projection smoke
Step74 does not execute FSIDriver3D
Step74 records a later data-decision readiness boundary only
```

## Required Outputs And Logs

Generate and commit:

```text
outputs/step74_real_geometry_api_audit/
outputs/step74_candidate_descriptor_schema_audit/
outputs/step74_candidate_manifest_policy_audit/
outputs/step74_real_geometry_quarantine_audit/
outputs/step74_real_geometry_output_policy_audit/
outputs/step74_full_activation_gate_coverage_audit/
outputs/step74_real_geometry_data_boundary_audit/
outputs/step74_no_simulation_audit/
outputs/step74_step73_regression_guard/
outputs/step74_artifact_manifest/
logs/step74_*.log
```

The artifact manifest must prove that Step74 stays small and contains no
forbidden output formats, driver-run directories, protected data edits, protected
external edits, or private absolute paths.

## Phase 1: Real Geometry API Audit

Audit required symbols by import only:

```text
src.mpm_lbm.sim.geometry.intake.run_candidate_intake
src.mpm_lbm.sim.geometry.intake.run_candidate_quality_check
src.mpm_lbm.sim.geometry.intake.run_candidate_sampling_reproducibility
src.mpm_lbm.sim.geometry.intake.run_candidate_projection_smoke
src.mpm_lbm.sim.geometry.candidate_manifest.validate_candidate_descriptor
src.mpm_lbm.sim.geometry.candidate_manifest.candidate_manifest_row
src.mpm_lbm.sim.geometry.candidate_manifest.write_candidate_manifest
src.mpm_lbm.sim.geometry.candidate_manifest.VALID_COMMIT_POLICIES
src.mpm_lbm.sim.geometry.candidate_manifest.VALIDATION_SCOPE
src.mpm_lbm.sim.geometry.fingerprint.fingerprint_geometry_file
src.mpm_lbm.sim.geometry.fingerprint.sha256_file
src.mpm_lbm.sim.geometry.fingerprint.file_size_bytes
src.mpm_lbm.sim.geometry.normalization.geometry_config_from_descriptor
src.mpm_lbm.sim.geometry.normalization.normalize_mesh_candidate
src.mpm_lbm.sim.geometry.normalization.normalize_voxel_candidate
src.mpm_lbm.sim.geometry.normalization.write_normalization_report
experiments.steps.real_geometry_feasibility.feasibility.run_projection_only_scale_case
experiments.steps.real_geometry_feasibility.feasibility.run_short_driver_case
```

Required summary:

```text
real_geometry_api_audit_pass = true
required_symbol_count = 18
canonical_import_pass_count = 18
missing_symbol_count = 0
output_snapshot_unchanged = true
projection_smoke_imported_but_not_executed = true
driver_constructed = false
solver_run = false
```

## Phase 2: Candidate Descriptor Schema Audit

Use synthetic in-memory descriptors. Do not use real geometry data.

Required descriptor fields:

```text
candidate_id
geometry_type
source_file
source_policy
license_status
commit_policy
normalize_to_domain
preserve_aspect_ratio
padding
n_particles
quality_check_enabled
quality_check_strict
artifact_policy
validation_scope
```

The valid synthetic descriptor must be accepted. Invalid descriptors must be
rejected for:

```text
candidate_id contains validated
candidate_id contains swimming
candidate_id contains actuation
candidate_id contains anatomical
unknown geometry_type
invalid commit_policy
quality_check_enabled = false
quality_check_strict = false
wrong validation_scope
absolute private source path without local_candidate_only
source_file under external/taichi_LBM3D
```

Required summary:

```text
candidate_descriptor_schema_audit_pass = true
valid_descriptor_pass_count = 1
invalid_descriptor_rejected_count = 11
private_absolute_path_policy_enforced = true
external_path_rejected = true
identity_claim_terms_rejected = true
```

## Phase 3: Candidate Manifest Policy Audit

Use only a tiny synthetic fixture under Step74 output paths. Do not create files
under `data/real_geometry_candidates`.

Required checks:

```text
candidate_manifest_row redacts absolute private source path
large file + small_controlled_fixture_allowed is rejected
source_available=false requires local_candidate_only or do_not_commit_large_raw_geometry
duplicate candidate_id is rejected by write_candidate_manifest
valid small synthetic fixture manifest passes
```

Required summary:

```text
candidate_manifest_policy_audit_pass = true
absolute_path_redaction_pass = true
large_file_policy_enforced = true
unavailable_source_policy_enforced = true
duplicate_candidate_id_rejected = true
synthetic_fixture_count <= 1
real_geometry_candidate_edit_count = 0
```

## Phase 4: Real Geometry Quarantine Audit

Confirm the historical feasibility helper remains quarantined:

```text
experiments/steps/real_geometry_feasibility/feasibility.py exists
path is under experiments/steps
path is not under src/mpm_lbm/sim
driver helper functions are detected
projection and short-driver helpers are not executed
solver_run = false
```

Required summary:

```text
real_geometry_quarantine_audit_pass = true
quarantined_experiment_path_exists = true
under_sim_package = false
driver_helper_detected = true
driver_helper_executed = false
solver_run = false
```

## Phase 5: Real Geometry Output Policy Audit

Required checks:

```text
data/real_geometry_candidates unchanged
no Step74 files under data/real_geometry_candidates
no Step74 files under external/taichi_LBM3D
no outputs/step74_driver_runs
no VTR outputs
no particle NPY outputs
no unapproved raw geometry outputs
no private absolute paths in Step74 outputs/logs
no large Step74 files
```

Small JSON, CSV, markdown, Python, and log audit artifacts are allowed. An
optional tiny synthetic text fixture is allowed only under
`outputs/step74_synthetic_geometry_fixture/` and must be recorded as synthetic.

Required summary:

```text
real_geometry_output_policy_audit_pass = true
protected_real_geometry_candidate_edit_count = 0
external_taichi_lbm3d_edit_count = 0
forbidden_output_directory_count = 0
raw_geometry_file_count = 0
synthetic_fixture_count <= 1
private_absolute_path_count = 0
large_file_count = 0
```

## Phase 6: Full Activation Gate Coverage Audit

Reuse the Step70 activation policy and require all 10 gates to remain closed:

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
full_activation_gate_coverage_audit_pass = true
required_gate_count = 10
step70_gate_count = 10
closed_gate_count = 10
activation_allowed_count = 0
```

## Phase 7: Aggregate Real Geometry Data Boundary Audit

Aggregate these six required audits:

```text
real_geometry_api_audit
candidate_descriptor_schema_audit
candidate_manifest_policy_audit
real_geometry_quarantine_audit
real_geometry_output_policy_audit
full_activation_gate_coverage_audit
```

Required summary:

```text
real_geometry_data_boundary_audit_pass = true
required_audit_count = 6
required_audit_pass_count = 6
activation_allowed_after_step74 = false
readiness_claim = real_geometry_boundary_audit_ready_for_later_data_decision_only
```

## Phase 8: No Simulation Audit

Search Step74 executable files for forbidden calls and outputs:

```text
driver.run(
FSIDriver3D(...).run(
driver.initialize(
driver.step_once(
run_candidate_projection_smoke(
outputs/step74_driver_runs
write_vtk=True
write_particles=True
```

Required summary:

```text
no_simulation_audit_pass = true
forbidden_python_call_count = 0
forbidden_output_directory_count = 0
step74_vtr_count = 0
step74_particle_npy_count = 0
protected_step74_file_count = 0
```

## Phase 9: Step73 Regression Guard

Confirm Step73 remains green:

```text
Step73 wall velocity readiness pass
Step73 API audit pass
Step73 config schema audit pass
Step73 driver gate audit pass
Step73 application safety audit pass
Step73 output policy audit pass
Step73 full activation gate coverage pass
Step73 no simulation pass
Step73 Step72 regression pass
Step73 artifact manifest pass
```

Also confirm the key activation gates remain closed.

## Acceptance Criteria

Step74 is complete only if:

```text
Step74 goal/report/docs exist
all Step74 audit runners generate committed JSON/CSV/log artifacts
real_geometry_api_audit_pass == true
candidate_descriptor_schema_audit_pass == true
candidate_manifest_policy_audit_pass == true
real_geometry_quarantine_audit_pass == true
real_geometry_output_policy_audit_pass == true
full_activation_gate_coverage_audit_pass == true
real_geometry_data_boundary_audit_pass == true
no_simulation_audit_pass == true
step74_step73_regression_guard_pass == true
artifact_budget_pass == true
real_geometry_activation_allowed remains false
activation_allowed_count == 0
data/real_geometry_candidates remains clean
external/taichi_LBM3D remains clean
no private absolute paths are committed in Step74 outputs/logs
no VTR or particle NPY outputs are added
no driver-run directory is created
focused Step74 pytest passes
full pytest passes under D:\working\taichi\env\python.exe
full pytest passes under D:\TOOL\Anaconda\python.exe when accessible
pre-push hook passes
git diff --check passes
Step74 is committed and pushed to origin/main
```

## Verification Commands

Compile:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\evidence\real_geometry_data_boundary_audit.py `
  src\mpm_lbm\evidence\real_geometry_api_audit.py `
  src\mpm_lbm\evidence\candidate_descriptor_schema_audit.py `
  src\mpm_lbm\evidence\candidate_manifest_policy_audit.py `
  src\mpm_lbm\evidence\real_geometry_quarantine_audit.py `
  src\mpm_lbm\evidence\real_geometry_output_policy_audit.py `
  src\mpm_lbm\evidence\step74_full_activation_gate_coverage_audit.py `
  src\mpm_lbm\evidence\step74_no_simulation_audit.py `
  src\mpm_lbm\evidence\step74_regression_guard.py `
  baseline_tests\step74_common.py `
  baseline_tests\run_step74_real_geometry_api_audit.py `
  baseline_tests\run_step74_candidate_descriptor_schema_audit.py `
  baseline_tests\run_step74_candidate_manifest_policy_audit.py `
  baseline_tests\run_step74_real_geometry_quarantine_audit.py `
  baseline_tests\run_step74_real_geometry_output_policy_audit.py `
  baseline_tests\run_step74_full_activation_gate_coverage_audit.py `
  baseline_tests\run_step74_real_geometry_data_boundary_audit.py `
  baseline_tests\run_step74_no_simulation_audit.py `
  baseline_tests\run_step74_step73_regression_guard.py `
  baseline_tests\run_step74_artifact_manifest.py `
  tests\test_step74_real_geometry_api_contract.py `
  tests\test_step74_candidate_descriptor_schema_contract.py `
  tests\test_step74_candidate_manifest_policy_contract.py `
  tests\test_step74_real_geometry_quarantine_contract.py `
  tests\test_step74_real_geometry_output_policy_contract.py `
  tests\test_step74_full_activation_gate_coverage_contract.py `
  tests\test_step74_real_geometry_data_boundary_contract.py `
  tests\test_step74_no_simulation_contract.py `
  tests\test_step74_step73_regression_contract.py
```

Run audits:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step74_real_geometry_api_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step74_candidate_descriptor_schema_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step74_candidate_manifest_policy_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step74_real_geometry_quarantine_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step74_real_geometry_output_policy_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step74_full_activation_gate_coverage_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step74_real_geometry_data_boundary_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step74_no_simulation_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step74_step73_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step74_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest `
  tests\test_step74_real_geometry_api_contract.py `
  tests\test_step74_candidate_descriptor_schema_contract.py `
  tests\test_step74_candidate_manifest_policy_contract.py `
  tests\test_step74_real_geometry_quarantine_contract.py `
  tests\test_step74_real_geometry_output_policy_contract.py `
  tests\test_step74_full_activation_gate_coverage_contract.py `
  tests\test_step74_real_geometry_data_boundary_contract.py `
  tests\test_step74_no_simulation_contract.py `
  tests\test_step74_step73_regression_contract.py `
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
git add <Step74 files>
git diff --cached --check
git commit -m "test: add step74 real geometry data boundary audit"
git fetch origin main
git push origin main
```
