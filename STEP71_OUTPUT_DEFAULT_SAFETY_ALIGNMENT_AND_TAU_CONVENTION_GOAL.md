# Step 71 Output Default Safety Alignment And LBM Tau Convention Decision Goal

## Source And Base State

User-provided Step71 direction:

```text
C:\Users\lizhu\.codex\attachments\6a15e422-ef1e-4204-94f4-bf5bf7861583\pasted-text.txt
```

Base commit:

```text
0851d7ba01fae4bf055c8d4b9cc8ed09ce936410
test: add step70 api config freeze
```

Step70 is accepted as the API/config/compatibility/activation/output/report
freeze step. Step70 evidence says public API, compatibility, config schema,
activation preconditions, output artifact policy, Step69 regression, and
report consistency are green. Step70 also intentionally did not run a driver,
activate runtime geometry, activate wall velocity, run real geometry, validate
squid behavior, change solver formulas, or migrate tau convention.

Step71 exists because Step70 froze an output safety policy that conflicts with
the current runtime defaults:

```text
Step70 output policy:
  default_write_vtk_allowed = false
  default_write_particles_allowed = false
  vtr_default_allowed = false
  particle_npy_default_allowed = false

Current FSIDriverConfig defaults:
  write_vtk = True
  write_particles = True
```

This is not a Step70 failure. Step70 froze the state. Step71 must now align the
runtime output defaults with the frozen output safety policy before later
activation readiness work.

## Step Name

```text
Step71 Output Default Safety Alignment And LBM Tau Convention Decision
```

## Core Objectives

Step71 must complete two bounded decisions and add evidence guards for both:

1. Align `FSIDriverConfig` runtime output defaults with Step70 output safety
   policy.
2. Freeze the LBM tau/`niu` convention decision without changing the current
   solver numerical tau formula.

Step71 is a safety/default and semantics step. It is not a simulation,
activation, physical validation, production readiness, or tau migration step.

## Decision A: Safe-By-Default Driver Outputs

Change:

```python
FSIDriverConfig.write_vtk = True
FSIDriverConfig.write_particles = True
```

to:

```python
FSIDriverConfig.write_vtk = False
FSIDriverConfig.write_particles = False
```

Required runtime semantics:

```text
FSIDriverConfig().write_vtk == False
FSIDriverConfig().write_particles == False
FSIDriverConfig.from_json(config_with_write_vtk_true).write_vtk == True
FSIDriverConfig.from_json(config_with_write_particles_true).write_particles == True
FSIDriverConfig.from_json(config_with_write_vtk_false).write_vtk == False
FSIDriverConfig.from_json(config_with_write_particles_false).write_particles == False
```

Policy meaning:

```text
runtime_output_default_changed = true
solver_numerical_behavior_changed = false
physics_feature_expansion = false
explicit_opt_in_remains_allowed = true
```

This change is intentionally limited to default output persistence behavior.
It must not change coupling formulas, LBM formulas, MPM formulas, projection,
runtime geometry activation, wall velocity activation, or driver stepping.

## Decision B: Tau Convention Decision Without Formula Migration

Current code already separates two formulas:

```python
tau_from_legacy_external_solver_parameter(niu) = niu / 3.0 + 0.5
tau_from_lattice_kinematic_viscosity(nu_lbm) = 3.0 * nu_lbm + 0.5
```

Step71 must preserve current solver numerical behavior:

```text
LBMFluid3D.init_simulation uses tau_from_legacy_external_solver_parameter.
LBMConfig.niu remains present.
LBMConfig.niu remains the legacy external solver relaxation parameter.
The standard lattice viscosity formula remains available but is not default.
No physical viscosity validation claim is made.
Future standard tau migration requires a separate baseline rerun campaign.
```

Required policy values:

```text
tau_convention_decision = preserve_legacy_external_solver_parameter_for_now
default_solver_tau_formula = tau_from_legacy_external_solver_parameter
standard_lattice_viscosity_formula_available = true
standard_lattice_viscosity_formula_default = false
physical_viscosity_validation_claim = false
future_standard_tau_migration_requires_baseline_rerun = true
solver_numerical_behavior_changed = false
```

Step71 may add explicit constants to `relaxation_semantics.py` if useful:

```python
LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER
STANDARD_LATTICE_KINEMATIC_VISCOSITY
DEFAULT_TAU_CONVENTION
```

Step71 must not change the tau formula used by `LBMFluid3D`.

## Non-Goals And Forbidden Work

Step71 must not do any of the following:

```text
driver.run()
FSIDriver3D(...).run()
driver.initialize()
driver.step_once()
outputs/step71_driver_runs
runtime geometry activation
wall velocity activation
real geometry run
squid simulation
VTR output
particle NPY output
LBM tau numerical migration
standard viscosity migration
historical baseline rerun
physics validation claim
grid convergence claim
production readiness claim
external/taichi_LBM3D edit
data/real_geometry_candidates edit
```

## Required Runtime Code Changes

Modify:

```text
src/mpm_lbm/sim/drivers/fsi_config.py
```

Required change:

```text
FSIDriverConfig.write_vtk default True -> False
FSIDriverConfig.write_particles default True -> False
```

Inspect but do not numerically change:

```text
src/mpm_lbm/sim/lbm/relaxation_semantics.py
src/mpm_lbm/sim/lbm/fluid.py
src/mpm_lbm/sim/lbm/config.py
```

Allowed semantic-only addition:

```text
Add tau convention constants and include them in relaxation_semantics_summary.
```

Protected numerical behavior:

```text
tau_from_legacy_external_solver_parameter(0.1) == 0.5333333333333333
tau_from_lattice_kinematic_viscosity(0.1) == 0.8
LBMFluid3D source still calls tau_from_legacy_external_solver_parameter
LBMFluid3D source does not use tau_from_lattice_kinematic_viscosity by default
```

## Required Config Files

Create:

```text
configs/step71_output_default_alignment_policy.json
configs/step71_tau_convention_decision_policy.json
configs/step71_config_schema_delta_policy.json
configs/step71_no_simulation_policy.json
configs/step71_step70_regression_policy.json
```

`step71_output_default_alignment_policy.json` must include:

```json
{
  "policy_id": "step71_output_default_alignment_policy",
  "step": 71,
  "recommended_action": "safe_by_default_outputs",
  "runtime_output_default_changed": true,
  "solver_numerical_behavior_changed": false,
  "physics_feature_expansion": false,
  "required_defaults": {
    "FSIDriverConfig.write_vtk": false,
    "FSIDriverConfig.write_particles": false
  },
  "explicit_opt_in_remains_allowed": true,
  "vtr_output_allowed_by_default": false,
  "particle_npy_output_allowed_by_default": false
}
```

`step71_tau_convention_decision_policy.json` must include:

```json
{
  "policy_id": "step71_tau_convention_decision_policy",
  "step": 71,
  "tau_convention_decision": "preserve_legacy_external_solver_parameter_for_now",
  "default_solver_tau_formula": "tau_from_legacy_external_solver_parameter",
  "legacy_formula": "tau = niu / 3.0 + 0.5",
  "standard_lattice_viscosity_formula": "tau = 3.0 * nu_lbm + 0.5",
  "standard_lattice_viscosity_is_default": false,
  "physical_viscosity_validation_claim": false,
  "future_standard_tau_migration_requires_baseline_rerun": true,
  "solver_numerical_behavior_changed": false
}
```

`step71_config_schema_delta_policy.json` must require:

```text
expected_changed_schema_classes = ["FSIDriverConfig"]
expected_unchanged_schema_classes includes all other Step70 required config classes
```

## Required Evidence Modules

Create:

```text
src/mpm_lbm/evidence/output_default_alignment_audit.py
src/mpm_lbm/evidence/tau_convention_decision_audit.py
src/mpm_lbm/evidence/config_schema_delta_audit.py
src/mpm_lbm/evidence/step71_no_simulation_audit.py
src/mpm_lbm/evidence/step71_regression_guard.py
```

### Output Default Alignment Audit

Must check:

```text
FSIDriverConfig().write_vtk == false
FSIDriverConfig().write_particles == false
Step70 output policy default_write_vtk_allowed == false
Step70 output policy default_write_particles_allowed == false
explicit true remains accepted from JSON
explicit false remains accepted from JSON
runtime_output_default_changed == true
solver_numerical_behavior_changed == false
physics_feature_expansion == false
```

Outputs:

```text
outputs/step71_output_default_alignment_audit/output_default_alignment.json
outputs/step71_output_default_alignment_audit/output_default_alignment.csv
outputs/step71_output_default_alignment_audit/output_default_alignment_summary.csv
```

### Tau Convention Decision Audit

Must check:

```text
tau_from_legacy_external_solver_parameter(0.1) == 0.5333333333333333
tau_from_lattice_kinematic_viscosity(0.1) == 0.8
relaxation_semantics_summary()["default_solver_formula"] == "legacy_external_solver_parameter"
relaxation_semantics_summary()["standard_lattice_viscosity_is_default"] == false
LBMFluid3D source contains tau_from_legacy_external_solver_parameter
LBMFluid3D source does not directly hardcode self.niu / 3.0 + 0.5
LBMFluid3D source does not use tau_from_lattice_kinematic_viscosity by default
physical_viscosity_validation_claim == false
```

Outputs:

```text
outputs/step71_tau_convention_decision_audit/tau_convention_decision.json
outputs/step71_tau_convention_decision_audit/tau_convention_decision.csv
outputs/step71_tau_convention_decision_audit/tau_convention_decision_summary.csv
```

### Config Schema Delta Audit

Must compare Step70 schema freeze with the current Step71 schema snapshot.

Expected:

```text
changed_schema_classes == ["FSIDriverConfig"]
FSIDriverConfig write_vtk default True -> False
FSIDriverConfig write_particles default True -> False
LBMConfig schema unchanged
UnifiedSimConfig schema unchanged
MPMConfig schema unchanged
all non-FSIDriverConfig required schema hashes unchanged
```

Outputs:

```text
outputs/step71_config_schema_delta_audit/config_schema_delta.json
outputs/step71_config_schema_delta_audit/config_schema_delta.csv
outputs/step71_config_schema_delta_audit/config_schema_delta_summary.csv
```

### No Simulation Audit

Must check:

```text
no driver.run
no FSIDriver3D(...).run
no driver.initialize
no driver.step_once
no outputs/step71_driver_runs
no VTR
no particle NPY
no external edits
no real geometry candidate edits
```

### Step70 Regression Guard

Must check Step70 remains valid with the intentional schema-delta exception:

```text
Step70 public API audit remains green
Step70 compatibility surface audit remains green
Step70 activation preconditions remain green
Step70 output artifact policy remains green
Step70 artifact manifest remains green
Step70 report consistency remains green
Step70 config schema freeze is superseded by Step71 schema delta
```

## Required Runners

Create:

```text
baseline_tests/step71_common.py
baseline_tests/run_step71_output_default_alignment_audit.py
baseline_tests/run_step71_tau_convention_decision_audit.py
baseline_tests/run_step71_config_schema_delta_audit.py
baseline_tests/run_step71_no_simulation_audit.py
baseline_tests/run_step71_step70_regression_guard.py
baseline_tests/run_step71_artifact_manifest.py
```

Runners must be thin and deterministic. They must not run a driver or call
`driver.initialize`, `driver.step_once`, or `driver.run`.

## Required Tests

Create:

```text
tests/test_step71_output_default_alignment_contract.py
tests/test_step71_tau_convention_decision_contract.py
tests/test_step71_config_schema_delta_contract.py
tests/test_step71_no_simulation_contract.py
tests/test_step71_step70_regression_contract.py
```

Tests must verify both fresh audit computation and committed artifacts where
appropriate.

## Required Docs And Reports

Create:

```text
STEP71_OUTPUT_DEFAULT_SAFETY_ALIGNMENT_AND_TAU_CONVENTION_REPORT.md
docs/71_output_default_safety_alignment_and_tau_convention.md
docs/OUTPUT_DEFAULT_SAFETY_POLICY.md
docs/LBM_TAU_CONVENTION_DECISION.md
docs/LBM_RELAXATION_SEMANTICS.md
```

Update:

```text
README.md
docs/CONFIG_SCHEMA_FREEZE.md
docs/ACTIVATION_PRECONDITIONS.md
```

If `docs/00_project_status.md` exists, update it. If it does not exist, do not
create it only for Step71.

Docs must say:

```text
FSIDriverConfig is safe-by-default for file outputs.
VTR and particle output require explicit opt-in.
LBM niu remains the legacy external solver relaxation parameter.
Standard lattice viscosity formula exists but is not default.
No physical viscosity validation claim is made.
Changing to standard lattice tau requires a future baseline rerun campaign.
```

Docs must not say:

```text
viscosity validated
physical viscosity corrected
solver physically validated
production ready
```

## Required Outputs And Logs

Generate:

```text
outputs/step71_output_default_alignment_audit/
outputs/step71_tau_convention_decision_audit/
outputs/step71_config_schema_delta_audit/
outputs/step71_no_simulation_audit/
outputs/step71_step70_regression_guard/
outputs/step71_artifact_manifest/
logs/step71_*.log
```

The final artifact manifest must be refreshed after final pytest logs exist.

## Acceptance Criteria

Step71 is accepted only if all criteria pass:

```text
Step71 goal/report/docs exist.

Output default alignment:
  FSIDriverConfig().write_vtk == false
  FSIDriverConfig().write_particles == false
  explicit config opt-in write_vtk=true still works
  explicit config opt-in write_particles=true still works
  Step70 output policy remains false-by-default
  runtime_output_default_changed == true
  solver_numerical_behavior_changed == false
  physics_feature_expansion == false

Tau convention:
  tau_convention_decision == preserve_legacy_external_solver_parameter_for_now
  tau_from_legacy_external_solver_parameter(0.1) == 0.5333333333333333
  tau_from_lattice_kinematic_viscosity(0.1) == 0.8
  LBMFluid3D still uses legacy helper by default
  standard_lattice_viscosity_is_default == false
  physical_viscosity_validation_claim == false
  future_standard_tau_migration_requires_baseline_rerun == true

Config schema delta:
  changed_schema_classes == ["FSIDriverConfig"]
  FSIDriverConfig write_vtk default True -> False
  FSIDriverConfig write_particles default True -> False
  LBMConfig schema unchanged
  all non-FSIDriverConfig required schema hashes unchanged

No simulation:
  no driver.run
  no FSIDriver3D(...).run
  no outputs/step71_driver_runs
  no VTR
  no particle NPY
  no external/taichi_LBM3D edits
  no data/real_geometry_candidates edits

Regression:
  Step70 regression guard passes with schema-delta exception
  artifact manifest passes
  focused pytest passes
  full pytest passes under both Python environments
  pre-push hook passes
  git diff --check passes
```

## Verification Commands

Compile:

```powershell
& 'D:\working\taichi\env\python.exe' -m py_compile `
  src\mpm_lbm\sim\drivers\fsi_config.py `
  src\mpm_lbm\sim\lbm\relaxation_semantics.py `
  src\mpm_lbm\evidence\output_default_alignment_audit.py `
  src\mpm_lbm\evidence\tau_convention_decision_audit.py `
  src\mpm_lbm\evidence\config_schema_delta_audit.py `
  src\mpm_lbm\evidence\step71_no_simulation_audit.py `
  src\mpm_lbm\evidence\step71_regression_guard.py `
  baseline_tests\step71_common.py `
  baseline_tests\run_step71_output_default_alignment_audit.py `
  baseline_tests\run_step71_tau_convention_decision_audit.py `
  baseline_tests\run_step71_config_schema_delta_audit.py `
  baseline_tests\run_step71_no_simulation_audit.py `
  baseline_tests\run_step71_step70_regression_guard.py `
  baseline_tests\run_step71_artifact_manifest.py `
  tests\test_step71_output_default_alignment_contract.py `
  tests\test_step71_tau_convention_decision_contract.py `
  tests\test_step71_config_schema_delta_contract.py `
  tests\test_step71_no_simulation_contract.py `
  tests\test_step71_step70_regression_contract.py
```

Run audits:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step71_output_default_alignment_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step71_tau_convention_decision_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step71_config_schema_delta_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step71_no_simulation_audit.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step71_step70_regression_guard.py
& 'D:\working\taichi\env\python.exe' -W ignore baseline_tests\run_step71_artifact_manifest.py
```

Focused tests:

```powershell
& 'D:\working\taichi\env\python.exe' -W ignore -m pytest `
  tests\test_step71_output_default_alignment_contract.py `
  tests\test_step71_tau_convention_decision_contract.py `
  tests\test_step71_config_schema_delta_contract.py `
  tests\test_step71_no_simulation_contract.py `
  tests\test_step71_step70_regression_contract.py `
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
git status --short external/taichi_LBM3D
git status --short data/real_geometry_candidates
```

Commit and push:

```powershell
git status --short
git add .
git diff --cached --check
git commit -m "test: add step71 output defaults and tau convention decision"
git push origin main
```

## Expected Commit

```text
test: add step71 output defaults and tau convention decision
```

## Step72 Reserved Direction

After Step71, the next reserved direction is:

```text
Step72 Runtime Geometry Activation Readiness Audit
```

Step72 should remain a readiness audit and should not immediately resume
simulation campaigns. Step76 or later can resume post-gate simulation only
after readiness gates are explicitly passed.
