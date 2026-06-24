# Step93 VTR Output Enablement Plan And Guard Report

Step93 accepted.

Step93 is a plan-and-guard step only.
Step93 does not run FSIDriver3D.
Step93 does not call driver.run().
Step93 does not execute simulation.
Step93 does not write VTR output.

Step93 only plans and guards Step94:

```text
first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_vtr_smoke
```

Step94 may run exactly one 32^3 / 1024-particle / 1-step /
moving_boundary / engineering row with:

```text
geometry_type = squid_proxy
geometry_motion_application_mode = diagnostic_only
wall_velocity_application_mode = solid_vel_experimental
target_lbm_field = solid_vel
target_u_lbm = [0.0, 0.0, 0.0]
write_vtk = true
write_particles = false
```

The only new feature from Step92 to Step94 is:

```text
write_vtk = false -> true
```

The duration reduction from 10 steps to 1 step is intentional VTR-output smoke
isolation.

Step94 must not enable real geometry candidate data, link-area transfer, 48^3,
64^3, particle NPY, solver formula changes, tau migration, physical validation
claims, squid swimming claims, real squid validation claims, squid actuation
claims, visualization-campaign readiness claims, or production readiness claims.

## Verification

Step93 evidence includes:

- VTR output enablement plan pass;
- VTR output enablement guard pass;
- Step92 regression guard pass;
- Step91 regression guard pass;
- Step90 regression guard pass;
- Step93 output guard pass;
- Step93 artifact manifest pass;
- focused Step93 pytest pass;
- full trusted Taichi pytest pass;
- full Anaconda pytest pass.

The authoritative artifact counts and byte totals are in:

```text
outputs/step93_artifact_manifest/artifact_summary.json
```
