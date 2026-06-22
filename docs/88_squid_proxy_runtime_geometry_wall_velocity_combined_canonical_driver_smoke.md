# Step88 Squid Proxy Runtime Geometry Wall Velocity Combined Canonical Driver Smoke

Step88 executes exactly one canonical driver row:

```text
canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

The row is 32^3, 1024 particles, three LBM steps, one MPM substep per LBM step,
`moving_boundary`, and engineering transfer. It uses procedural `squid_proxy`
geometry with `configs/step85_squid_proxy_geometry_1024.json`, runtime geometry
`diagnostic_only` reporting, wall velocity `solid_vel_experimental` reporting,
and row-local `target_u_lbm = [0.0, 0.0, 0.0]`.

## Evidence

Step88 records:

- smoke matrix evidence in `outputs/step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix/`;
- quality evidence in `outputs/step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality/`;
- activation guard evidence in `outputs/step88_activation_guard/`;
- output guard evidence in `outputs/step88_output_guard/`;
- Step87, Step86, Step84, Step82, and Step80 regression evidence in `outputs/step88_step*_regression_guard/`;
- artifact budget evidence in `outputs/step88_artifact_manifest/`.

The required driver run directory is:

```text
outputs/step88_driver_runs/canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke
```

## Boundaries

Step88 does not mutate geometry, displace MPM particles through runtime
geometry, update LBM `solid_phi` through runtime geometry, write LBM populations
through wall velocity, modify moving bounce-back formulas, directly update MPM
or projector state through wall velocity, enable real geometry candidate data,
enable link-area transfer, add 48^3 or 64^3 rows, or write VTR/particle NPY
outputs.

The only positive Step88 claim is that the bounded three-feature combined
canonical driver 3-step smoke passed. Step88 does not validate squid swimming,
real squid geometry, physical correctness, grid convergence, or production
readiness.
