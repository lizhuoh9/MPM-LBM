# Step75 Solver-Complete Simulation Campaign Readiness Gate Report

Step75 is a gate-only aggregation step. It reads committed Step71, Step72,
Step73, and Step74 evidence, confirms that all activation gates remain closed,
and records that the repository is ready for one narrowly scoped Step76
minimal safe rebaseline proposal.

Step75 does not run `FSIDriver3D`, initialize a driver, step a driver, execute
projection smoke, activate runtime geometry, activate wall velocity, activate
real geometry, run a squid proxy, write VTR files, write particle NPY files,
or edit protected external or real-geometry candidate directories.

## Evidence

- `outputs/step75_precondition_artifact_audit/precondition_artifact.json`
- `outputs/step75_activation_gate_closure_audit/activation_gate_closure.json`
- `outputs/step75_post_gate_campaign_policy_audit/post_gate_campaign_policy.json`
- `outputs/step75_solver_complete_gate_audit/solver_complete_gate.json`
- `outputs/step75_no_simulation_audit/no_simulation.json`
- `outputs/step75_output_artifact_policy_audit/output_artifact_policy.json`
- `outputs/step75_step74_regression_guard/step74_regression_guard.json`
- `outputs/step75_artifact_manifest/artifact_summary.json`

## Result

The Step75 readiness gate passes only as a bounded campaign gate:

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

The `post_gate_simulation_allowed` field is intentionally narrow. It allows
only a later Step76 minimal rebaseline campaign proposal. It does not open
runtime geometry, wall velocity, real geometry, squid proxy, 48^3, 64^3, VTR,
particle NPY, tau migration, or production-readiness work.

## Preconditions

Step75 requires 35 green artifacts from Step71 through Step74:

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

Step71 extra checks keep output safety and tau semantics explicit:

```text
fsidriver_default_write_vtk = false
fsidriver_default_write_particles = false
tau_convention_decision = preserve_legacy_external_solver_parameter_for_now
default_solver_tau_formula = tau_from_legacy_external_solver_parameter
physical_viscosity_validation_claim = false
future_standard_tau_migration_requires_baseline_rerun = true
```

## Activation Gate Closure

All Step70 activation gates remain closed after Step75:

```text
activation_gate_closure_audit_pass = true
required_gate_count = 10
closed_gate_count = 10
activation_allowed_count = 0
latest_step_checked = Step75
```

Closed gates include runtime geometry, wall velocity, combined runtime
geometry plus wall velocity, real geometry, squid proxy, link-area activation,
48^3, 64^3, VTR output, and particle NPY output.

## Step76 Campaign Proposal

The only allowed post-gate campaign proposal is inactive until Step76:

```text
campaign_id = step76_minimal_post_gate_real_driver_rebaseline
row_id = canonical_driver_moving_boundary_engineering_32_1step_rebaseline
n_grid = 32
n_lbm_steps = 1
required = true
```

The optional three-step row remains disabled by default:

```text
row_id = canonical_driver_moving_boundary_engineering_32_3step_rebaseline_optional
required = false
run_by_default = false
```

The proposal keeps every advanced feature disabled:

```text
runtime_geometry_enabled = false
wall_velocity_enabled = false
real_geometry_enabled = false
squid_proxy_enabled = false
write_vtk = false
write_particles = false
activation_feature_count_in_first_campaign = 0
```

## No-Simulation And Output Policy

Step75 verifies that it did not introduce a runtime path:

```text
no_simulation_audit_pass = true
forbidden_python_call_count = 0
forbidden_output_directory_count = 0
step75_vtr_count = 0
step75_particle_npy_count = 0
protected_step75_file_count = 0
```

Step75 also verifies that report artifacts exist and no forbidden output was
created:

```text
output_artifact_policy_audit_pass = true
large_file_count = 0
private_absolute_path_count = 0
protected_external_edit_count = 0
protected_real_geometry_candidate_edit_count = 0
report_missing_count = 0
step75_driver_run_output_dir_count = 0
step75_vtr_count = 0
step75_particle_npy_count = 0
```

## Regression Guard

Step75 keeps Step74 evidence green and preserves the closed activation gates:

```text
step75_step74_regression_guard_pass = true
step74_artifact_check_count = 10
step74_artifact_pass_count = 10
closed_gate_pass_count = required_closed_gate_count
```

## Validation

Completed validation:

```text
D:\working\taichi\env\python.exe -m py_compile <Step75 Python files>
D:\working\taichi\env\python.exe baseline_tests\run_step75_precondition_artifact_audit.py
D:\working\taichi\env\python.exe baseline_tests\run_step75_activation_gate_closure_audit.py
D:\working\taichi\env\python.exe baseline_tests\run_step75_post_gate_campaign_policy_audit.py
D:\working\taichi\env\python.exe baseline_tests\run_step75_solver_complete_gate_audit.py
D:\working\taichi\env\python.exe baseline_tests\run_step75_no_simulation_audit.py
D:\working\taichi\env\python.exe baseline_tests\run_step75_output_artifact_policy_audit.py
D:\working\taichi\env\python.exe baseline_tests\run_step75_step74_regression_guard.py
D:\working\taichi\env\python.exe baseline_tests\run_step75_artifact_manifest.py
D:\working\taichi\env\python.exe -W ignore -m pytest <Step75 focused tests> -q
14 passed

D:\working\taichi\env\python.exe -W ignore -m pytest -q
915 passed

D:\TOOL\Anaconda\python.exe -W ignore -m pytest -q
915 passed
```

Final Step75 artifact budget:

```text
artifact_budget_pass = true
step75_file_count = 64
step75_total_size_mb = 0.18829059600830078
large_file_count = 0
private_absolute_path_count = 0
protected_external_taichi_lbm3d_step75_file_count = 0
protected_real_geometry_candidates_step75_file_count = 0
raw_output_file_count = 0
step75_driver_run_output_dir_count = 0
step75_particle_npy_count = 0
step75_vtr_count = 0
```

Step75 records solver-complete campaign readiness only for Step76 minimal
rebaseline planning. It is not production readiness, not physical validation,
and not real squid validation.
