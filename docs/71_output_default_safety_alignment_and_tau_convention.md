# Step 71 Output Default Safety Alignment And Tau Convention

Step71 aligns runtime file-output defaults with the Step70 output safety
policy and records the LBM tau convention decision.

## Output Defaults

`FSIDriverConfig` is now safe-by-default for file outputs:

```text
write_vtk = false
write_particles = false
```

VTR output and particle NPY output require explicit opt-in in a config file or
constructor call. Explicit opt-in remains allowed for diagnostic cases that are
inside a bounded step contract.

## Tau Convention

`LBMConfig.niu` remains the legacy external solver relaxation parameter. The
default solver formula remains:

```text
tau = niu / 3.0 + 0.5
```

The standard lattice kinematic viscosity formula is available as a named helper:

```text
tau = 3.0 * nu_lbm + 0.5
```

That standard formula is not the default in Step71. No physical viscosity
validation claim is made. Any future migration to the standard lattice formula
requires a separate baseline rerun campaign.

## Boundaries

Step71 does not run a driver, activate runtime geometry, activate wall
velocity, run real geometry, run squid simulation, write VTR, write particle
NPY, change LBM tau numerical behavior, or edit vendored external code.
