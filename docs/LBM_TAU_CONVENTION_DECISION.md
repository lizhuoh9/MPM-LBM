# LBM Tau Convention Decision

Step71 decision:

```text
tau_convention_decision = preserve_legacy_external_solver_parameter_for_now
default_solver_tau_formula = tau_from_legacy_external_solver_parameter
standard_lattice_viscosity_is_default = false
physical_viscosity_validation_claim = false
future_standard_tau_migration_requires_baseline_rerun = true
```

The current default solver formula remains:

```text
tau_from_legacy_external_solver_parameter(niu) = niu / 3.0 + 0.5
```

The standard lattice kinematic viscosity formula exists:

```text
tau_from_lattice_kinematic_viscosity(nu_lbm) = 3.0 * nu_lbm + 0.5
```

Step71 does not migrate the solver to the standard formula. That would change
solver numerical behavior and must be handled as a future step with baseline
reruns.
