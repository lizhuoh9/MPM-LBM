# Output Default Safety Policy

Step71 makes driver file outputs safe-by-default.

```text
FSIDriverConfig.write_vtk = false
FSIDriverConfig.write_particles = false
```

This aligns runtime defaults with the Step70 output policy:

```text
default_write_vtk_allowed = false
default_write_particles_allowed = false
vtr_default_allowed = false
particle_npy_default_allowed = false
```

Explicit opt-in remains supported. Existing configs that set
`write_vtk = true` or `write_particles = true` still preserve that request.

This policy changes output persistence defaults only. It does not change solver
formulas, coupling formulas, runtime geometry behavior, wall velocity behavior,
or validation status.
