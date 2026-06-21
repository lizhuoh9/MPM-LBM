# Step 62 Controlled Canonical 32 Moving-Boundary 3-Step Duration

Step 62 is a controlled canonical 32^3 moving-boundary engineering 3-step duration probe.

It calls the canonical runtime driver:

```python
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D
driver.run()
```

The required row is:

```text
canonical_driver_moving_boundary_engineering_32_3step
```

It uses:

```text
n_grid = 32
n_particles = 1024
n_lbm_steps = 3
mpm_substeps_per_lbm_step = 1
coupling_mode = moving_boundary
reaction_transfer_mode = engineering
geometry_type = box
write_vtk = false
write_particles = false
boundary_motion_mode = static
wall_velocity_application_mode = disabled
geometry_motion_mode = static
geometry_motion_application_mode = disabled
```

Step 62 keeps runtime solver code unchanged and keeps optional penalty 3-step and moving-boundary 5-step rows disabled by default.

Step 62 also repairs the Step 61 report Output Guard size mismatch and adds a report consistency guard for Step 61 and Step 62 report size rows.

The Step 62 row completed 3 LBM steps with 4 diagnostics rows and stayed finite/bounded under the Step 62 policy. This is a finite/bounded duration feasibility smoke, not real squid validation, not propulsion validation, not grid convergence, and not production-readiness evidence.

Primary artifacts:

```text
outputs/step62_driver_runs/canonical_driver_moving_boundary_engineering_32_3step/
outputs/step62_32_duration_matrix/
outputs/step62_32_duration_quality/
outputs/step62_output_guard/
outputs/step62_report_consistency_guard/
outputs/step62_step61_regression_guard/
outputs/step62_artifact_manifest/
```

Report:

```text
STEP62_CONTROLLED_CANONICAL_32_MOVING_BOUNDARY_3STEP_DURATION_REPORT.md
```
