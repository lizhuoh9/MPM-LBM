# Step 71 Output Default Safety Alignment And LBM Tau Convention Decision Report

## Scope

Step71 aligns runtime file-output defaults with the Step70 output policy and
records the LBM tau convention decision before activation-readiness work.

This step changes output persistence defaults only:

```text
FSIDriverConfig.write_vtk: True -> False
FSIDriverConfig.write_particles: True -> False
```

This step does not run a driver, activate runtime geometry, activate wall
velocity, run real geometry, run squid simulation, write VTR, write particle
NPY, change solver formulas, migrate tau convention, validate physical
viscosity, claim grid convergence, or claim production readiness.

Base commit:

```text
0851d7ba01fae4bf055c8d4b9cc8ed09ce936410
test: add step70 api config freeze
```

## Phase Summary

| Phase | Result |
| --- | --- |
| Output default alignment | pass, 14 checks, default VTR/particle outputs false, explicit opt-in preserved |
| Tau convention decision | pass, 15 checks, legacy tau `0.5333333333333333`, standard tau helper `0.8`, standard formula not default |
| Config schema delta | pass, changed schema classes `["FSIDriverConfig"]`, all other Step70 schema hashes unchanged |
| No-simulation guard | pass, 12 executable-surface checks, 0 forbidden calls, 0 VTR, 0 particle NPY |
| Step70 regression guard | pass, 7 checks, Step70 schema freeze superseded by Step71 delta |
| Artifact manifest | pass, 56 Step71 files, artifact budget pass, 0 large files, 0 VTR, 0 particle NPY |

## Decisions

Output defaults:

```text
FSIDriverConfig().write_vtk = false
FSIDriverConfig().write_particles = false
explicit opt-in write_vtk=true remains accepted
explicit opt-in write_particles=true remains accepted
```

Tau convention:

```text
tau_convention_decision = preserve_legacy_external_solver_parameter_for_now
default_solver_tau_formula = tau_from_legacy_external_solver_parameter
standard_lattice_viscosity_is_default = false
physical_viscosity_validation_claim = false
future_standard_tau_migration_requires_baseline_rerun = true
```

## Evidence

Step71 evidence artifacts:

```text
outputs/step71_output_default_alignment_audit/output_default_alignment.json
outputs/step71_tau_convention_decision_audit/tau_convention_decision.json
outputs/step71_config_schema_delta_audit/config_schema_delta.json
outputs/step71_no_simulation_audit/no_simulation.json
outputs/step71_step70_regression_guard/step70_regression_guard.json
outputs/step71_artifact_manifest/artifact_summary.json
```

## Verification

Final validation:

```text
D:\working\taichi\env\python.exe -m py_compile src\mpm_lbm\sim\drivers\fsi_config.py src\mpm_lbm\sim\lbm\relaxation_semantics.py src\mpm_lbm\evidence\output_default_alignment_audit.py src\mpm_lbm\evidence\tau_convention_decision_audit.py src\mpm_lbm\evidence\config_schema_delta_audit.py src\mpm_lbm\evidence\step71_no_simulation_audit.py src\mpm_lbm\evidence\step71_regression_guard.py baseline_tests\step71_common.py baseline_tests\run_step71_output_default_alignment_audit.py baseline_tests\run_step71_tau_convention_decision_audit.py baseline_tests\run_step71_config_schema_delta_audit.py baseline_tests\run_step71_no_simulation_audit.py baseline_tests\run_step71_step70_regression_guard.py baseline_tests\run_step71_artifact_manifest.py tests\test_step71_output_default_alignment_contract.py tests\test_step71_tau_convention_decision_contract.py tests\test_step71_config_schema_delta_contract.py tests\test_step71_no_simulation_contract.py tests\test_step71_step70_regression_contract.py
pass

D:\working\taichi\env\python.exe -W ignore -m pytest tests\test_step71_output_default_alignment_contract.py tests\test_step71_tau_convention_decision_contract.py tests\test_step71_config_schema_delta_contract.py tests\test_step71_no_simulation_contract.py tests\test_step71_step70_regression_contract.py -q
11 passed in 9.19s

D:\working\taichi\env\python.exe -W ignore -m pytest -q
846 passed in 76.80s (0:01:16)

D:\TOOL\Anaconda\python.exe -W ignore -m pytest -q
846 passed in 36.42s
```

The Anaconda validation required elevated execution because sandbox execution
returned `Access is denied` for `D:\TOOL\Anaconda\python.exe`.
