# Simulation Freeze Policy

Step 63-67 freeze new simulation execution while canonical ownership is completed.

## Frozen Actions

Batch A executable code must not add:

```text
FSIDriver3D run execution
driver run execution
driver step_once execution
driver initialize execution
Step63-67 driver output directories
VTR outputs
particle NPY outputs
write_vtk enabled configs
write_particles enabled configs
```

## Allowed Actions

Batch A may run:

```text
import checks
AST/source audits
symbol identity audits
legacy shim audits
configuration checks
small pure-function checks
existing Step62 regression checks
artifact manifest checks
```

## Evidence

The enforced audit is:

```text
src/mpm_lbm/evidence/simulation_freeze_audit.py
baseline_tests/run_step63_simulation_freeze_audit.py
outputs/step63_simulation_freeze_audit/audit.json
```

Current result:

```text
simulation_freeze_audit_pass = true
new_simulation_run_count = 0
new_driver_run_output_dir_count = 0
step63_67_vtr_count = 0
step63_67_particle_npy_count = 0
```
