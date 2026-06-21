# Step 54 Repository Evidence Integrity Repair Goal

## Short Goal Reference

Implement Step 54 exactly as this file specifies. Step 54 is a repository-wide
evidence integrity and semantic truthfulness repair. It must pause feature
expansion and repair evidence labels, proxy diagnostic labels, state guard
measurement metadata, test strength classification, evidence classification,
and LBM relaxation-parameter semantics. Step 54 must not run 48^3
`link_area_experimental`, must not run longer cycles, must not run 64^3, must
not change solver formulas, must not rewrite historical outputs with changed
physics, must not edit `external/taichi_LBM3D`, and must not make physical,
grid-convergence, production-readiness, real-jet, or squid-swimming claims.

## Background

Step 53 completed active-cell, applied-cell, and bounce-back support semantics
for accepted Step 51 and Step 52 artifacts. It did not repair the repository
wide evidence-integrity problem. Step 53 also ended with a local recommendation
that Step 54 may consider 48^3 `link_area_experimental`, but that expansion is
now explicitly paused.

The current priority is to make the repository honest about:

```text
LBM relaxation parameter semantics
proxy diagnostic records versus solver time integration
fixed-zero state guard fields
test strength and artifact-contract tests
evidence type for historical steps
claim boundaries in docs, reports, configs, tests, runners, and outputs
```

## Explicit Non-Goals

Step 54 must not implement or claim:

```text
48^3 link_area_experimental
longer cycle
64^3
real solver formula correction
standard viscosity migration
rerun all historical outputs with changed tau
delete old reports
delete old artifacts
external/taichi_LBM3D edit
data/real_geometry_candidates edit
real jet validation
jet propulsion validation
squid swimming
grid convergence validation
physical validation
production readiness
full solver validation for Step 50/51/52
standard physical viscosity validation
```

## Required LBM Relaxation Semantics Repair

Current `src/lbm_fluid.py` uses the legacy external solver formula:

```python
self.tau_f = self.niu / 3.0 + 0.5
```

`LBMConfig.niu` looks like viscosity but the formula is not the standard lattice
kinematic viscosity relation. Step 54 must not silently switch formulas. It must
name both formulas explicitly:

```python
def tau_from_legacy_external_solver_parameter(niu: float) -> float:
    return niu / 3.0 + 0.5

def tau_from_lattice_kinematic_viscosity(nu_lbm: float) -> float:
    return 3.0 * nu_lbm + 0.5
```

Then `LBMFluid3D.init_simulation()` must use the legacy helper instead of an
inline expression:

```python
from .lbm_relaxation_semantics import tau_from_legacy_external_solver_parameter

self.tau_f = tau_from_legacy_external_solver_parameter(self.niu)
```

The report must state:

```text
LBMConfig.niu is legacy_external_solver_relaxation_parameter, not yet validated as standard lattice kinematic viscosity.
```

The standard lattice viscosity formula must be documented and tested separately
but not made the default behavior in Step 54.

## Required Proxy Diagnostic Truthfulness Repair

Step 50, Step 51, and Step 52 matrix rows are proxy diagnostic records, not
real `FSIDriver3D.run()` time integration records. Their `completed_lbm_steps`
and `total_mpm_substeps` are declared from config. Density, velocity,
bounce-back, force, impulse, NaN, and Inf fields are generated from proxy
formulas or finite-input assumptions.

Step 54 must preserve existing fields but add explicit truthfulness metadata to
Step 50, Step 51, and Step 52 envelope row and step records:

```text
record_kind = proxy_diagnostic_record
solver_time_integration_run = false
completed_lbm_steps_source = config_declared_proxy_steps
total_mpm_substeps_source = config_declared_proxy_substeps
rho_velocity_source = proxy_formula
hydro_force_source = proxy_formula
nan_inf_source = finite_input_proxy_assumption
```

Files to update:

```text
src/runtime_geometry_wall_velocity_one_cycle_envelope.py
src/runtime_geometry_wall_velocity_transfer_envelope.py
src/runtime_geometry_wall_velocity_48_feasibility_envelope.py
```

Step 54 must add:

```text
docs/REPOSITORY_EVIDENCE_INTEGRITY_ERRATA.md
outputs/step54_proxy_diagnostic_label_audit/
```

Errata must state:

```text
Step 50/51/52 matrix rows are 40-phase proxy diagnostic records, not real 40-step solver time integration.
```

## Required State Guard Truthfulness Repair

State guards currently combine measured hash and artifact scans with fixed-zero
fields for state mutation counts. Step 54 must keep the values but add
measurement metadata:

```text
default_driver_state_mutation_count_method = not_applicable_proxy_no_driver_instance
default_lbm_state_mutation_count_method = not_applicable_proxy_no_lbm_instance
default_mpm_state_mutation_count_method = not_applicable_proxy_no_mpm_instance
default_projection_state_mutation_count_method = not_applicable_proxy_no_projection_instance
persistent_projected_state_count_method = config_and_artifact_guard
persistent_displaced_geometry_count_method = config_and_artifact_guard
persistent_lbm_solid_vel_count_method = config_and_artifact_guard
state_guard_kind = hash_plus_artifact_scan_plus_not_applicable_proxy_fields
fixed_zero_fields_disclosed = true
```

Files to update:

```text
src/runtime_geometry_wall_velocity_one_cycle_state_guard.py
src/runtime_geometry_wall_velocity_transfer_state_guard.py
src/runtime_geometry_wall_velocity_48_feasibility_state_guard.py
```

Acceptance:

```text
all fixed-zero state guard fields are disclosed
no fixed-zero field is described as directly measured
hash checks remain measured
forbidden output scans remain measured
```

## Required Test Strength Audit

Step 54 must classify test strength across `tests/test_step*.py` and
`baseline_tests/run_step*.py`. It must add:

```text
src/repository_test_strength_audit.py
baseline_tests/run_step54_test_strength_audit.py
outputs/step54_test_strength_audit/test_strength_audit.csv
outputs/step54_test_strength_audit/test_strength_audit.json
```

Each row must include:

```text
test_file
step
checks_file_existence
checks_log_marker
checks_report_text
checks_committed_artifact_json
checks_source_string
reruns_runner
reruns_solver
validates_formula
validates_numerical_benchmark
test_strength_level
```

Allowed `test_strength_level` values:

```text
artifact_contract
artifact_plus_source_contract
runner_reexecution_contract
proxy_diagnostic_contract
solver_smoke_contract
formula_unit_contract
numerical_benchmark_contract
```

Step 54 report must state:

```text
604/614 passed means contract/artifact/proxy tests passed unless explicitly classified otherwise.
```

The report must not say:

```text
full solver validation passed
```

## Required Repository Evidence Index

Step 54 must add:

```text
src/repository_evidence_index.py
baseline_tests/run_step54_repository_evidence_index.py
outputs/step54_repository_evidence_index/repository_evidence_index.csv
outputs/step54_repository_evidence_index/repository_evidence_index.json
docs/REPOSITORY_EVIDENCE_INDEX.md
```

Evidence classifications:

```text
real_solver_run
proxy_diagnostic
post_processing_audit
artifact_manifest
claim_guard
state_guard
report_only
log_only
```

Required classifications:

```text
Step 50 = proxy_diagnostic, not real solver time integration
Step 51 = proxy_diagnostic, not real solver time integration
Step 52 = proxy_diagnostic, not real solver time integration
Step 53 = post_processing_audit
Step 1/2 solver smoke baselines are separate from artifact contract tests
```

## Required Claim Guard

Step 54 must add a claim guard that scans Step 54 docs, report, configs,
runners, tests, outputs, and repository evidence docs. It must prevent positive
claims of:

```text
real jet validation
jet propulsion validation
squid swimming
grid convergence
production readiness
full solver validation for Step 50/51/52
standard viscosity validation
```

The guard should allow explicit negative statements such as:

```text
Step 54 does not validate real jets.
Step 50/51/52 are not full solver validation.
standard physical viscosity is not validated.
```

## Files To Add

Configs:

```text
configs/step54_repository_evidence_integrity_repair.json
configs/step54_lbm_relaxation_semantics_policy.json
configs/step54_evidence_classification_policy.json
```

Source:

```text
src/lbm_relaxation_semantics.py
src/repository_evidence_index.py
src/repository_test_strength_audit.py
src/proxy_diagnostic_truthfulness.py
src/state_guard_truthfulness.py
src/repository_evidence_integrity_claim_guard.py
```

Runners:

```text
baseline_tests/step54_common.py
baseline_tests/run_step54_lbm_relaxation_semantics_audit.py
baseline_tests/run_step54_proxy_diagnostic_truthfulness_audit.py
baseline_tests/run_step54_state_guard_truthfulness_audit.py
baseline_tests/run_step54_test_strength_audit.py
baseline_tests/run_step54_repository_evidence_index.py
baseline_tests/run_step54_claim_guard.py
baseline_tests/run_step54_step53_regression_guard.py
baseline_tests/run_step54_artifact_manifest.py
```

Tests:

```text
tests/test_step54_repository_evidence_integrity_repair_contract.py
tests/test_step54_lbm_relaxation_semantics_contract.py
```

Docs and reports:

```text
STEP54_REPOSITORY_EVIDENCE_INTEGRITY_REPAIR_REPORT.md
docs/54_repository_evidence_integrity_repair.md
docs/REPOSITORY_EVIDENCE_INDEX.md
docs/REPOSITORY_EVIDENCE_INTEGRITY_ERRATA.md
```

## Required Outputs

```text
outputs/step54_lbm_relaxation_semantics_audit/
outputs/step54_proxy_diagnostic_label_audit/
outputs/step54_state_guard_truthfulness_audit/
outputs/step54_test_strength_audit/
outputs/step54_repository_evidence_index/
outputs/step54_claim_guard/
outputs/step54_step53_regression_guard/
outputs/step54_artifact_manifest/
logs/step54_*.log
```

## Acceptance Criteria

All of the following must be true:

```text
Step 54 detailed goal exists
LBM relaxation semantics audit passes
legacy tau formula is explicitly named
standard lattice viscosity formula is documented separately
LBMFluid3D no longer hardcodes tau formula inline
no physical viscosity validation claim is made

proxy diagnostic truthfulness audit passes
Step 50/51/52 rows include record_kind = proxy_diagnostic_record
Step 50/51/52 rows include solver_time_integration_run = false
Step 50/51/52 reports/docs have errata or updated wording
no Step 50/51/52 artifact claims real 40-step solver integration

state guard truthfulness audit passes
fixed-zero fields are disclosed
fixed-zero fields are not described as directly measured
hash guards remain measured
artifact scan guards remain measured

test strength audit passes
all tests/test_step*.py files are classified
all baseline_tests/run_step*.py files are classified
artifact-only tests are not described as solver validation
runner-reexecution tests are distinguished from committed-output checks

repository evidence index exists
Step 50 is classified as proxy_diagnostic
Step 51 is classified as proxy_diagnostic
Step 52 is classified as proxy_diagnostic
Step 53 is classified as post_processing_audit
Step 1/2 solver smoke baselines are classified separately from artifact contract tests

claim guard passes
no real jet validation claim
no jet propulsion validation claim
no squid swimming claim
no grid convergence claim
no production readiness claim
no full solver validation claim for Step 50/51/52
no standard viscosity validation claim

Step 53 regression guard passes
artifact budget passes
repo total_size_mb < 400
large_file_count == 0
external/taichi_LBM3D unchanged
data/real_geometry_candidates unchanged
py_compile passes
Step 54 contract tests pass
full pytest passes
pre-push hook passes
git diff --check passes
```

## Verification Commands

Use the trusted interpreter:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\lbm_relaxation_semantics.py `
  src\repository_evidence_index.py `
  src\repository_test_strength_audit.py `
  src\proxy_diagnostic_truthfulness.py `
  src\state_guard_truthfulness.py `
  src\repository_evidence_integrity_claim_guard.py `
  baseline_tests\step54_common.py `
  baseline_tests\run_step54_lbm_relaxation_semantics_audit.py `
  baseline_tests\run_step54_proxy_diagnostic_truthfulness_audit.py `
  baseline_tests\run_step54_state_guard_truthfulness_audit.py `
  baseline_tests\run_step54_test_strength_audit.py `
  baseline_tests\run_step54_repository_evidence_index.py `
  baseline_tests\run_step54_claim_guard.py `
  baseline_tests\run_step54_step53_regression_guard.py `
  baseline_tests\run_step54_artifact_manifest.py `
  tests\test_step54_repository_evidence_integrity_repair_contract.py `
  tests\test_step54_lbm_relaxation_semantics_contract.py

& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step54_lbm_relaxation_semantics_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step54_proxy_diagnostic_truthfulness_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step54_state_guard_truthfulness_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step54_test_strength_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step54_repository_evidence_index.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step54_claim_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step54_step53_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step54_artifact_manifest.py

& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step54_repository_evidence_integrity_repair_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest tests\test_step54_lbm_relaxation_semantics_contract.py -q
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest -q

git diff --check
git diff --cached --check
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

## Decision For Step 55

Step 54 must end with this decision boundary:

```text
Step 54 repairs evidence integrity and semantic truthfulness.
It does not change solver formulas.
Step 55 must choose one path:
A. preserve legacy tau convention and rename/configure it permanently;
B. migrate to standard lattice viscosity tau = 3*nu + 0.5 and rerun affected solver baselines.
No link_area expansion or longer-cycle expansion should proceed before this decision.
```
