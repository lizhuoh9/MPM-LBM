# LBM Relaxation Semantics

The LBM relaxation helpers distinguish the legacy external solver parameter
from standard lattice kinematic viscosity.

```text
LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER = legacy_external_solver_relaxation_parameter
STANDARD_LATTICE_KINEMATIC_VISCOSITY = standard_lattice_kinematic_viscosity
DEFAULT_TAU_CONVENTION = legacy_external_solver_relaxation_parameter
```

Probe values:

```text
tau_from_legacy_external_solver_parameter(0.1) = 0.5333333333333333
tau_from_lattice_kinematic_viscosity(0.1) = 0.8
```

`LBMFluid3D` still uses the legacy helper by default. The standard formula is
documented and test-covered, but not default. This is a semantics decision, not
a physical viscosity validation result.
